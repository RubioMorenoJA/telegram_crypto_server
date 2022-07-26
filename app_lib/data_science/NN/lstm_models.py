"""
Module containing lstm models of cryptocurrencies
"""
import numpy as np
from sklearn.preprocessing import FunctionTransformer, MaxAbsScaler
from app_lib.data_science.NN.general_model import GeneralModel
from app_lib.data_science.NN.transform_functions import sigmoid


def function_transformer_with_min_max(data):
    """
    Transform data into a max abs scale and then apply sigmoid function
    """
    return FunctionTransformer(sigmoid, validate=True, check_inverse=True). \
        transform(MaxAbsScaler().fit_transform(data))


class BTC(GeneralModel):

    def set_model_scalers(self, model_scalers: dict = None) -> None:
        """
        Used to fill own model scalers
        """
        if model_scalers:
            self.model_scalers = model_scalers
        else:
            self.model_scalers = {
                'ema': FunctionTransformer(np.log1p, validate=True),
                'sma': FunctionTransformer(np.log1p, validate=True),
                'macd': MaxAbsScaler(),
                'signal': MaxAbsScaler(),
                'rsi': FunctionTransformer(lambda x: x/100, validate=True),
                'price': FunctionTransformer(np.log1p, validate=True)
            }
