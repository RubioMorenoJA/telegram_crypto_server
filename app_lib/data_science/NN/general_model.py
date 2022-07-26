"""
Module with general RNN model
"""
import traceback
from json import loads, dumps, JSONDecodeError
from abc import abstractmethod
import keras
import numpy as np
import pandas as pd
from keras import Sequential
from keras.models import model_from_json
from sklearn.preprocessing import FunctionTransformer, MinMaxScaler, MaxAbsScaler
from app_lib.DDBB.sqlite.connection import DataBase
from app_lib.utils.files_utils import get_absolute_path
from app_lib.log.log import get_log
from app_lib.data_science.indicators.moving_averages import exponential_moving_average, simple_moving_average, \
    mean_average_convergence_divergence
from app_lib.data_science.indicators.RSI import relative_strength_index_array


__logger__ = get_log('general_model')


def read_write_decorator(func):
    """
    Decorator used to read/write models
    :param func:
    """

    def impl(*args):
        """
        Used to manage read/write operations on the models
        """
        func_return = None
        try:
            func_return = func(*args)
        except IOError as ex:
            __logger__.error(f'IOError:\n{ex}\n{traceback.format_exc()}')
        except JSONDecodeError as ex:
            __logger__.error(f'JSONDecodeError:\n{ex}\n{traceback.format_exc()}')
        except ValueError as ex:
            __logger__.error(f'ValueError:\n{ex}\n{traceback.format_exc()}')
        except Exception as ex:
            __logger__.error(f'Exception:\n{ex}\n{traceback.format_exc()}')
        finally:
            return func_return

    return impl


def set_scaler_args(scaler, arguments) -> None:
    """
    Set save arguments from dictionary into the given scaler.

    When new scalers are introduced we should fill new conditional options in order
    to use new data

    :param scaler:
    :param arguments:
    """
    if not arguments:
        return scaler
    if isinstance(scaler, MinMaxScaler):
        scaler.min_ = np.array([arguments['min_']])
        scaler.scale_ = np.array([arguments['scale_']])
        scaler.data_min_ = np.array([arguments['data_min_']])
        scaler.data_max_ = np.array([arguments['data_max_']])
        scaler.data_range_ = np.array([arguments['data_range_']])
    elif isinstance(scaler, MaxAbsScaler):
        scaler.scale_ = np.array([arguments['scale_']])
        scaler.max_abs_ = np.array([arguments['max_abs_']])
    elif isinstance(scaler, FunctionTransformer):
        pass


def get_scaler_args(scaler) -> dict:
    """
    Get arguments from scaler to save into a dictionary

    When new scalers are introduced we should fill new conditional options in order
    to use new data

    :param scaler:
    """
    arguments = {}
    if isinstance(scaler, MinMaxScaler):
        arguments = {
            'min_': scaler.min_[0],
            'scale_': scaler.scale_[0],
            'data_min_': scaler.data_min_[0],
            'data_max_': scaler.data_max_[0],
            'data_range_': scaler.data_range_[0]
        }
    elif isinstance(scaler, MaxAbsScaler):
        arguments = {
            'scale_': scaler.scale_[0],
            'max_abs_': scaler.max_abs_[0]
        }
    elif isinstance(scaler, FunctionTransformer):
        pass
    return arguments


class GeneralModel:
    """
    General NN model
    """

    model = None
    model_path = get_absolute_path('/app_lib/data_science/NN/models/') + '{name}'
    model_form = {
        'skeleton': [{'type': 'LSTM', 'input': None, 'output': 1, 'kwargs': None}],
        'compile': {'loss': 'mean_squared_error', 'optimizer': 'adam', 'metrics': ['accuracy']}
    }
    model_scalers = None

    def __init__(self, db_model: DataBase, name: str, **kwargs):
        self.db_model = db_model
        self.model_name = name
        self.__update_model_form(kwargs['model_form'] if 'model_form' in kwargs else None)
        self.set_model_scalers(kwargs['model_scalers'] if 'model_scalers' in kwargs else None)

    def __update_model_form(self, model_form: dict) -> None:
        """
        Initializes model form with given data. If data does not exist it takes the default data
        :param model_form:
        """
        if 'skeleton' in model_form:
            self.model_form['skeleton'] = model_form['skeleton']
        if 'compile' in model_form:
            self.model_form['compile']['loss'] = model_form['compile']['loss'] if \
                'loss' in model_form['compile'] else self.model_form['compile']['loss']
            self.model_form['compile']['optimizer'] = model_form['compile']['optimizer'] if \
                'optimizer' in model_form['compile'] else self.model_form['compile']['optimizer']
            self.model_form['compile']['metrics'] = model_form['compile']['metrics'] if \
                'metrics' in model_form['compile'] else self.model_form['compile']['metrics']

    @read_write_decorator
    def load_model(self) -> bool:
        """
        Tries to load previous saved model with full configuration
        :return:
        """
        with open(self.model_path.format(name=self.model_name + '_form.json'), 'r') as file:
            loaded_model_form = loads(file.read())
        with open(self.model_path.format(name=self.model_name + '.json'), 'r') as file:
            loaded_model_json = file.read()
        loaded_model = model_from_json(loaded_model_json)
        loaded_model.load_weights(self.model_path.format(name='{name}_weight.h5'.format(name=self.model_name)))
        loaded_model.compile(
            loss=loaded_model_form['compile']['loss'],
            optimizer=loaded_model_form['compile']['optimizer'],
            metrics=loaded_model_form['compile']['metrics']
        )
        self.model = loaded_model
        __logger__.info(f'Loaded {self.model_name} model from disk.')
        return True

    @read_write_decorator
    def save_model(self) -> bool:
        """
        Tries to save own model with full configuration
        """
        if self.model:
            with open(self.model_path.format(name='{name}.json'.format(name=self.model_name)), 'w') as file:
                file.write(self.model.to_json())
            self.model.save_weights(self.model_path.format(name='{name}_weight.h5'.format(name=self.model_name)))
            with open(self.model_path.format(name='{name}_form.json'.format(name=self.model_name)), 'w') as file:
                file.write(dumps(self.model_form))
            __logger__.debug(f'Saved {self.model_name} model to disk.')
            return True
        else:
            raise ValueError('Current model is empty or malformed')

    def create_model(self, train: bool = False, **kwargs) -> None:
        """
        Loads or creates a neural network model
        """
        if train or not self.load_model():
            train_x, train_y = self.prepare_data(self.load_data(), fit=True, **kwargs)
            # set input shape at first layer
            self.model_form['skeleton'][0]['input'] = train_x.shape[1:]
            self.model_form['skeleton'][-1]['output'] = train_y.shape[2]
            model = Sequential()
            for sk_layer in self.model_form['skeleton']:
                layer = self.__create_layer(sk_layer)
                model.add(layer)
            model.compile(
                loss=self.model_form['compile']['loss'],
                optimizer=self.model_form['compile']['optimizer'],
                metrics=self.model_form['compile']['metrics']
            )
            model.fit(
                train_x,
                train_y,
                epochs=1,
                batch_size=1,
                verbose=2
            )
            self.model = model
            self.save_model()

    @staticmethod
    def __create_layer(layer_info: dict):
        """
        Creates a keras layer from the layer_info
        :param layer_info:
        """
        layer = None
        str_layer = '{layer_type}({output_shape})'.format(
            layer_type=layer_info["type"],
            output_shape=str(layer_info["output"]) + ', {more}'
        )
        if 'input' in layer_info and layer_info['input']:
            str_layer = str_layer.format(more=f'input_shape={layer_info["input"]}' + ', {more}')
        if 'kwargs' in layer_info and layer_info['kwargs']:
            str_kwargs = ','.join([f'{key}={value}' for key, value in layer_info['kwargs'].items()])
            str_layer = str_layer.format(more=str_kwargs)
        str_layer = str_layer.replace(', {more}', '')
        _locals = locals()
        exec(f"layer = keras.layers.{str_layer}", globals(), _locals)
        layer = _locals['layer']
        return layer

    def predict(self, predict_x: np.array = None) -> np.array:
        """
        Predicts over last data
        """
        if predict_x is None:
            predict_x, _ = self.prepare_data()
        return self.model.predict(predict_x)

    def load_data(self, date_from: int = None, date_to: int = None) -> pd.DataFrame:
        """
        Loads data from DDBB with db_model
        Required to implement in child classes
        :param date_from:
        :param date_to:
        :return:
        """
        if self.db_model:
            ddbb_data = pd.DataFrame(
                self.db_model.get_data(date_init=date_from, date_end=date_to),
                columns=['date', 'price', 'maximum', 'minimum']
            )
            return ddbb_data
        return pd.DataFrame(None)

    def prepare_data(self, data: pd.DataFrame, fit: bool = False, **kwargs) -> tuple:
        """
        Prepare data to use in train/predict models
        Required to implement in child classes
        :param data:
        :param fit:
        :param kwargs:
        :return:
        """
        ema = exponential_moving_average(np.array(data.loc[:, ['date', 'price']]))
        sma = simple_moving_average(np.array(data.loc[:, ['date', 'price']]))
        macd, signal = mean_average_convergence_divergence(np.array(data.loc[:, ['date', 'price']]))
        rsi = relative_strength_index_array(np.array(data.loc[:, ['date', 'price']]))
        if 'look_back' in kwargs and kwargs['look_back'] > 1:
            look_back_array = np.concatenate(
                (
                    np.array([data.loc[:data.shape[0] - kwargs['look_back'] - 1, 'date']]).transpose(),
                    np.array(
                        [data.loc[i:i + kwargs['look_back'], 'price']
                         for i in range(data.shape[0] - kwargs['look_back'])]
                    )
                ), axis=1
            )
        else:
            look_back_array = np.array(data.loc[:, ['date', 'price']])
        look_forward_len = 1
        if 'look_forward' in kwargs and kwargs['look_forward'] > 1:
            look_forward_len = kwargs['look_forward']
            look_forward_array = np.concatenate(
                (
                    np.array([data.loc[:data.shape[0] - kwargs['look_forward'] - 1, 'date']]).transpose(),
                    np.array(
                        [data.loc[i:i + kwargs['look_forward'], 'price']
                         for i in range(data.shape[0] - kwargs['look_forward'])]
                    )
                ), axis=1
            )
        else:
            look_forward_array = np.array(data.loc[:, ['date', 'price']])
        min_len = min(ema.shape[0], sma.shape[0], macd.shape[0], rsi.shape[0],
                      look_back_array.shape[0], look_forward_array.shape[0])
        features = self.scale_data(
            pd.DataFrame(
                np.concatenate(
                    (
                        np.array([ema[:min_len, 1]]).transpose(),
                        np.array([sma[:min_len, 1]]).transpose(),
                        np.array([macd[:min_len, 1]]).transpose(),
                        np.array([signal[:min_len, 1]]).transpose(),
                        np.array([rsi[:min_len, 1]]).transpose(),
                        np.array(look_back_array[:min_len, 1:]),
                    ), axis=1
                ), columns=['ema', 'sma', 'macd', 'signal', 'rsi'] + \
                           [f'price t{-i}' for i in range(look_back_array.shape[1] - 1)]
            ),
            fit=fit
        )
        labels = np.array([])
        if fit:
            features = features[look_forward_len:, :]
            labels = self.scale_data(
                pd.DataFrame(
                    np.array(look_forward_array[:min_len - look_forward_len, 1:]),
                    columns=[f'price t+{i + 1}' for i in range(look_forward_array.shape[1] - 1)]
                ),
                fit=fit
            )
            labels = np.reshape(labels, (labels.shape[0], 1, labels.shape[1]))
        features = np.reshape(features, (features.shape[0], 1, features.shape[1]))
        return features, labels

    @abstractmethod
    def set_model_scalers(self, model_scalers: dict = None) -> None:
        """
        Used to fill own model scalers
        """
        pass

    def scale_data(self, data: pd.DataFrame, fit: bool = False) -> np.array:
        """
        Computes data scaling through own scalers. Due to we only use one scaler to price data
        we have to apply this to all prices data
        :param data:
        :param fit:
        :return:
        """
        fit_params = self.get_fit_params()
        if fit_params is None:
            fit_params = {}
        for label_name in data.columns:
            scaler = None
            transform_data = np.array(data.loc[:, label_name]).reshape(data.shape[0], 1)
            # if we use a different transformer for prices we must change this and we have to
            # transform all prices together, so we have to change prepare_data function too.
            if 'price' in label_name and 'price' in self.model_scalers:
                scaler = self.model_scalers['price']
            elif label_name in self.model_scalers:
                scaler = self.model_scalers[label_name]
            if scaler:
                if fit:
                    scaler.fit(transform_data)
                    fit_params.setdefault(label_name, get_scaler_args(scaler))
                else:
                    set_scaler_args(scaler, fit_params.get(label_name))
                data.loc[:, label_name] = scaler.transform(transform_data)
        if fit:
            self.save_fit_params(dumps(fit_params))
        return np.array(data)

    @read_write_decorator
    def save_fit_params(self, json_file: str) -> bool:
        """
        Save fit parameters got
        :param json_file:
        """
        with open(
                self.model_path.format(name='{name}_fit_params.json'.format(name=self.model_name)),
                'w',
                encoding='utf-8'
        ) as file:
            file.write(json_file)
        return True

    @read_write_decorator
    def get_fit_params(self) -> dict:
        """
        Get fit parameters
        :return:
        """
        fit_params = {}
        with open(
                self.model_path.format(name='{name}_fit_params.json'.format(name=self.model_name)),
                'r',
                encoding='utf-8'
        ) as file:
            fit_params = loads(file.read())
        return fit_params
