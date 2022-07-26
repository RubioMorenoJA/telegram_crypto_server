"""

"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import FormatStrFormatter
from sklearn.linear_model import LinearRegression
from app_lib.DDBB.sqlite.models import get_model
from app_lib.data_science.indicators.moving_averages import exponential_moving_average, simple_moving_average, \
    weighted_average, get_linear_scaling_factors, get_exponential_scaling_factors
from app_lib.data_science.indicators.RSI import relative_strength_index
from app_lib.utils.files_utils import get_absolute_path
from app_lib.utils.date_utils import float_coin_date_to_str
from app_lib.data_science.indicators.plot_settings import get_x_ticks_and_labels, get_saved_name_by_size, \
    get_labels_from_y_ticks


image_saving_path = get_absolute_path('/static/images/')


def get_ema(coin_logo: str, date_init: int = None, date_end: int = None, length: int = None):
    """
    Returns the exponential moving average from selected coin in the given date interval
    :param coin_logo:
    :param date_init:
    :param date_end:
    :param length:
    :return:
    """
    db_model = get_model(coin_logo)
    if db_model:
        close_prices = db_model.get_close_prices(date_init, date_end)
        ema = exponential_moving_average(np.array(close_prices), length)
        return ema
    return np.array([])


def get_sma(coin_logo: str, date_init: int = None, date_end: int = None, length: int = None):
    """
    Returns the simple moving average from selected coin in the given date interval
    :param coin_logo:
    :param date_init:
    :param date_end:
    :param length:
    :return:
    """
    db_model = get_model(coin_logo)
    if db_model:
        close_prices = db_model.get_close_prices(date_init, date_end)
        sma = simple_moving_average(np.array(close_prices), length)
        return sma
    return np.array([])


def save_ema_sma_plot(coin_logo: str, file_name, date_init: int = None, date_end: int = None):
    """
    Plot and save image with data, ema and sma
    :param coin_logo:
    :param file_name:
    :param date_init:
    :param date_end:
    :return:
    """
    db_model = get_model(coin_logo)
    if not db_model:
        return False
    close_prices = np.array(db_model.get_close_prices(date_init, date_end))
    ema = exponential_moving_average(close_prices)
    sma = simple_moving_average(close_prices)
    min_length = min([close_prices.shape[0], ema.shape[0], sma.shape[0]])
    close_prices = close_prices[:min_length]
    ema = ema[:min_length]
    sma = sma[:min_length]
    x_axis_values = np.linspace(0, 1, min_length)  # list(map(str, close_prices[:, 0][::-1]))  #
    fig, ax = plt.subplots()
    fig.set_tight_layout({"w_pad": .5, "h_pad": .5})
    ax.plot(x_axis_values, close_prices[:, 1][::-1], label='Close price', color='blue')
    ax.plot(x_axis_values, ema[:, 1][::-1], label='EMA 20', color='red')
    ax.plot(x_axis_values, sma[:, 1][::-1], label='SMA 50', color='black')
    x_ticks, x_labels = get_x_ticks_and_labels(close_prices[:, 0], 5)
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(float_coin_date_to_str(x_labels[::-1], '%Y%m%d', '%d-%m-%y'))
    ax.legend()
    # plt.savefig(image_saving_path + file_name)
    plt.show()


def save_web_plots(coin_logo: str, file_name, date_init: int = None, date_end: int = None):
    """
    Plot and save image with data, ema, sma, macd and signal
    :param coin_logo:
    :param file_name:
    :param date_init:
    :param date_end:
    :return:
    """
    db_model = get_model(coin_logo)
    if not db_model:
        return False
    close_prices = np.array(db_model.get_close_prices(date_init, date_end))
    ema = exponential_moving_average(close_prices)
    sma = simple_moving_average(close_prices)
    macd_short, signal_short = get_macd(coin_logo, date_init, date_end, short_length=6, long_length=19)
    macd_long, signal_long = get_macd(coin_logo, date_init, date_end, short_length=19, long_length=39)
    min_length = min(
        [
            close_prices.shape[0], ema.shape[0], sma.shape[0], macd_short.shape[0], macd_long.shape[0]
        ]
    )
    close_prices = close_prices[:min_length]
    ema = ema[:min_length]
    sma = sma[:min_length]
    macd_short = macd_short[:min_length]
    signal_short = signal_short[:min_length]
    macd_long = macd_long[:min_length]
    signal_long = signal_long[:min_length]
    x_axis_values = np.linspace(0, 1, min_length)  # list(map(str, close_prices[:, 0][::-1]))  #
    x_ticks, x_labels = get_x_ticks_and_labels(close_prices[:, 0], 5)
    x_labels = float_coin_date_to_str(x_labels[::-1], '%Y%m%d', '%d-%m-%y')
    for size in ((6.40, 4.80), (8.20, 6.15), (12., 9.)):
        fig = plt.figure(figsize=size, tight_layout={"w_pad": .5, "h_pad": .5})
        gs = gridspec.GridSpec(5, 1, figure=fig)
        ax = fig.add_subplot(gs[0:-2])
        ax.plot(x_axis_values, close_prices[:, 1][::-1], label='Close price', color='blue')
        ax.plot(x_axis_values, ema[:, 1][::-1], label='EMA 20', color='red')
        ax.plot(x_axis_values, sma[:, 1][::-1], label='SMA 50', color='black')
        ax.set_xticks(x_ticks)
        ax.set_xticklabels(x_labels)
        ax.set_yticklabels(get_labels_from_y_ticks(ax.get_yticks()))
        ax.legend()
        plt.grid(True, axis='both')
        ax1 = fig.add_subplot(gs[-2])
        ax1.plot(x_axis_values, macd_short[:, 1][::-1], label='macd short', color='blue')
        ax1.plot(x_axis_values, signal_short[:, 1][::-1], label='signal short', color='red')
        ax1.set_xticks(x_ticks)
        ax1.set_xticklabels(x_labels)
        ax1.set_yticklabels(get_labels_from_y_ticks(ax1.get_yticks()))
        ax1.legend(loc='lower left')
        plt.grid(True, axis='both')
        ax2 = fig.add_subplot(gs[-1])
        ax2.plot(x_axis_values, macd_long[:, 1][::-1], label='macd long', color='blue')
        ax2.plot(x_axis_values, signal_long[:, 1][::-1], label='signal long', color='red')
        ax2.set_xticks(x_ticks)
        ax2.set_xticklabels(x_labels)
        ax2.set_yticklabels(get_labels_from_y_ticks(ax2.get_yticks()))
        ax2.legend(loc='lower left')
        plt.grid(True, axis='both')
        save_name = get_saved_name_by_size(file_name, size)
        plt.savefig(image_saving_path + save_name)
        # plt.show()


def get_rsi(coin_logo: str, date_init: int = None, date_end: int = None, length: int = None):
    """
    Returns the relative strength index from selected coin in the given date interval
    :param coin_logo:
    :param date_init:
    :param date_end:
    :param length:
    :return:
    """
    db_model = get_model(coin_logo)
    if db_model:
        close_prices = db_model.get_close_prices(date_init, date_end)
        rsi = relative_strength_index(np.array(close_prices))
        return rsi
    return 50.


def get_macd(
        coin_logo: str, date_init: int = None, date_end: int = None,
        short_length: int = 12, long_length: int = 26, signal_length: int = 9
):
    """
    Returns the mean average convergence divergence and its signal from selected
    coin in the given date interval
    :param coin_logo:
    :param date_init:
    :param date_end:
    :param short_length:
    :param long_length:
    :param signal_length:
    :return:
    """
    db_model = get_model(coin_logo)
    if not db_model:
        return False
    close_prices = np.array(db_model.get_close_prices(date_init, date_end))
    short_ema = exponential_moving_average(close_prices, length=short_length)
    long_ema = exponential_moving_average(close_prices, length=long_length)
    min_length = min([short_ema.shape[0], long_ema.shape[0]])
    macd = np.array([short_ema[:min_length, 0], short_ema[:min_length, 1]-long_ema[:min_length, 1]]).transpose()
    signal = exponential_moving_average(macd, length=signal_length)
    min_length = min([macd.shape[0], signal.shape[0]])
    return macd[:min_length], signal[:min_length]


def get_macd_percentage(macd, signal, operation: str = 'buy'):
    """
    Calculates percentage of buy recommendation
    :param operation:
    :param macd:
    :param signal:
    :return:
    """
    cross_signal = 'positive' if operation == 'buy' else 'negative'
    percentage_indicators = []
    diff_array = macd[:, 1] - signal[:, 1]
    # save_macd_signal_plot(macd, signal, operation=operation)
    tend_length = diff_array.shape[0] - 1
    # tend_array = diff_array[:tend_length] - diff_array[1:tend_length+1]
    # tend_array /= max([max(tend_array), abs(min(tend_array))])
    diff_array /= max([max(diff_array), abs(min(diff_array))])
    diff_array = diff_array[:tend_length]
    percentage_indicators.append(get_cross_percentage(diff_array, cross_signal))
    # percentage_indicators.append(diff_array[0])
    # percentage_indicators.append(tend_array[0])
    # lin_tend_wa = weighted_average(tend_array, get_linear_scaling_factors(tend_length))
    # percentage_indicators.append(lin_tend_wa)
    macd_tend = macd[:tend_length, 1] - macd[1:tend_length+1, 1]
    macd_tend /= max([max(macd_tend), abs(min(macd_tend))])
    macd_tend_max_intervals = 4
    macd_tend_max = np.array([
        np.linspace(0, 2, macd_tend_max_intervals),
        [max(elem) for elem in np.array_split(macd_tend, macd_tend_max_intervals)][::-1]
    ]).transpose()
    reg = LinearRegression().fit(np.array([macd_tend_max[:, 0]]).transpose(),
                                 np.array([macd_tend_max[:, 1]]).transpose())
    percentage_indicators.append(reg.coef_[0, 0])
    # if cross_signal == 'negative':
    #     percentage_indicators[1:-1] *= -1
    percentage_indicators[1:] = linear_transformation(percentage_indicators[1:], np.array([-1, 1]))
    return weighted_average(
        np.array(percentage_indicators),
        np.array([1/len(percentage_indicators)] * len(percentage_indicators))
    )


def get_cross_percentage(array: np.array, cross_value: str = 'positive'):
    """
    Given an array we calculate the first cross value and returns 1 - n*1/array_length.
    If cross_value is 'positive' we search for the first change from negative to positive. In other way
    we search for the opposite change
    :param array: 1D array
    :param cross_value:
    :return:
    """
    def positive(item, next_item):
        return True if item >= 0 > next_item else False

    def negative(item, next_item):
        return True if item <= 0 < next_item else False

    search = positive if cross_value == 'positive' else negative
    elem = 0
    max_value = array.shape[0]
    while elem < max_value-1 and not search(array[elem], array[elem+1]):
        elem += 1
    return get_exponential_scaling_factors(max_value)[elem]


def save_macd_signal_plot(macd: np.array, signal: np.array, file_name: str = None, operation: str = ''):
    """

    :param operation:
    :param macd:
    :param signal:
    :param file_name:
    :return:
    """
    fig, ax = plt.subplots()
    x_axis_values = np.linspace(0, 1, macd.shape[0])
    ax.plot(x_axis_values, macd[:, 1][::-1], label=f'macd ({operation})', color='blue')
    ax.plot(x_axis_values, signal[:, 1][::-1], label='signal', color='red')
    ax.legend()
    # plt.show()
    plt.savefig(image_saving_path + file_name)


def linear_transformation(values, interval_from: np.array, interval_to: np.array = np.array([0, 1])):
    """

    :param values:
    :param interval_from:
    :param interval_to:
    :return:
    """
    def linear(x):
        return (x - interval_from[0]) * (interval_to[1] - interval_to[0]) / (interval_from[1] - interval_from[0]) \
               + interval_to[0]
    return [linear(x) for x in values]


def experiment_get_buy_macd_percentage(macd, signal):
    """
    Calculates percentage of buy recommendation
    :param macd:
    :param signal:
    :return:
    """
    diff_array = macd[:, 1] - signal[:, 1]
    clever_points = [diff_array[0], min(diff_array), diff_array[-1]]
    length = diff_array.shape[0] - 1
    tend_array = diff_array[:length] - diff_array[1:length+1]
    max_diff = max(tend_array)
    tend_array /= max_diff
    max_cp = max(diff_array)
    diff_array /= max_cp
    diff_array = diff_array[:length]
    scaling_factors = get_linear_scaling_factors(length)
    # possible first indicator
    lin_tend_wa = weighted_average(tend_array, scaling_factors)
    lin_diff_wa = weighted_average(diff_array, scaling_factors)
    scaling_factors = get_exponential_scaling_factors(length)
    exp_tend_wa = weighted_average(tend_array, scaling_factors)
    exp_diff_wa = weighted_average(diff_array, scaling_factors)
    # ------------------------------------
    import matplotlib.pyplot as plt
    import numpy as np
    fig, ax = plt.subplots()
    x_axis_values = np.linspace(0, 1, length+1)
    ax.plot(x_axis_values, macd[:, 1][::-1], label='macd', color='blue')
    ax.plot(x_axis_values, signal[:, 1][::-1], label='signal', color='red')
    ax.legend()
    plt.show()
    fig, ax = plt.subplots()
    x_axis_values = np.linspace(0, 1, length)
    ax.plot(x_axis_values, tend_array[:length][::-1], label='tend', color='red')
    ax.plot(x_axis_values, diff_array[:length][::-1], label='diff', color='blue')
    ax.legend()
    plt.grid(axis='y')
    plt.show()
    fig, ax = plt.subplots()
    length = macd.shape[0]
    macd_tend = macd[:length-1, 1] - macd[1:length, 1]
    macd_tend /= max(macd_tend)
    macd_tend_max_intervals = 4
    macd_tend_max = np.array([
        np.linspace(0, 1, macd_tend_max_intervals),
        [max(elem) for elem in np.array_split(macd_tend, macd_tend_max_intervals)][::-1]
    ]).transpose()
    from sklearn.linear_model import LinearRegression
    reg = LinearRegression().fit(np.array([macd_tend_max[:,0]]).transpose(), np.array([macd_tend_max[:,1]]).transpose())
    x_axis_values = np.linspace(0, 1, length-1)
    scaling_factors = get_linear_scaling_factors(length-1)
    lin_macd_tend_wa = weighted_average(macd_tend, scaling_factors)
    lin_macd_tend_a = macd_tend.mean()
    scaling_factors = get_exponential_scaling_factors(length-1)
    exp_macd_tend_wa = weighted_average(macd_tend, scaling_factors)
    ax.plot(x_axis_values, macd_tend[:][::-1], label='macd_tend', color='red')
    ax.plot(macd_tend_max[:, 0], reg.predict(np.array([macd_tend_max[:,0]]).transpose()), label='macd_tend_max', color='red', )
    ax.legend()
    plt.grid(axis='y')
    plt.show()
    # possible second indicator with transform
    reg_coef = reg.coef_[0, 0]
    # ------------------------------------