"""
Module to get all data related to webpage
"""
import traceback
from flask import render_template
import datetime as dt
import numpy as np
from app_lib.utils.files_utils import check_file_after_midnight, get_absolute_path
from app_lib.utils.date_utils import back_date_n_months, back_date_n_days
from app_lib.data_science.indicators.main import save_web_plots, get_ema, get_sma, get_rsi, get_macd, \
    get_macd_percentage
from app_lib.data_science.indicators.moving_averages import get_exponential_scaling_factors, weighted_average, \
    get_linear_scaling_factors
from app_lib.log.log import get_log


__logger__ = get_log('coin_data')
source_path = '/view/v1/{page}'
image_path = 'images/{image_name}'
combo_coins = ('BTC', 'ETH', 'ADA', 'TRX')
data_dict = {'coin_name': None, 'image_path': None, 'combo_coins': combo_coins,
             'indicators': {'RSI': None, 'EMA20 - SMA50': None, 'Buy (macd)': None, 'Sell (macd)': None}}
general_back_months = 6


def general_page(coin_logo: str, coin_name: str, image_name: str):
    """
    Prepare data for web page
    :param coin_logo:
    :param coin_name:
    :param image_name:
    :return:
    """
    data_dict['coin_name'] = coin_name
    # checks if there is an image created since midnight up to the moment using date as filename
    # save a plot with 6 months of data up today, got today date calculate 6 months back
    coin_image_path = get_absolute_path('/static/' + image_path.format(image_name=image_name))
    date_end = int(dt.datetime.today().strftime('%Y%m%d'))
    if not check_file_after_midnight(coin_image_path + '.png'):
        # date_init = today - (general_months + 2), +2 it's due to sma has 50 days and sma array is 50 shorter than date
        date_init = int(back_date_n_months(dt.datetime.today(), general_back_months+2).strftime('%Y%m%d'))
        save_web_plots(coin_logo, image_name, date_init=date_init, date_end=date_end)
    # search how to set images in flask html
    data_dict['image_path'] = image_path.format(image_name=image_name)
    data_dict['indicators']['EMA20 - SMA50'] = get_exp_sim_avg_diff(coin_logo, exp_length=20, sim_length=50)
    data_dict['indicators']['RSI'] = get_rsi(
        coin_logo=coin_logo,
        date_init=int(back_date_n_days(dt.datetime.today(), 15).strftime('%Y%m%d')),
        date_end=date_end
    )
    data_dict['indicators']['Buy (macd)'] = get_buy_macd_trend_percentage(coin_logo)
    data_dict['indicators']['Sell (macd)'] = get_sell_macd_trend_percentage(coin_logo)
    return render_template(source_path.format(page='coin_data.html'), **data_dict)


def get_exp_sim_avg_diff(coin_logo: str, exp_length: int, sim_length: int):
    """
    Given a coin name calculate the difference between exponential moving average with length exp_length and
    simple moving average with length sim_length
    :param coin_logo:
    :param exp_length:
    :param sim_length:
    :return:
    """
    date_end = int(dt.datetime.today().strftime('%Y%m%d'))
    exp = get_ema(
        coin_logo=coin_logo,
        date_init=int(back_date_n_days(dt.datetime.today(), exp_length).strftime('%Y%m%d')),
        date_end=date_end,
        length=exp_length
    )
    sim = get_sma(
        coin_logo=coin_logo,
        date_init=int(back_date_n_days(dt.datetime.today(), sim_length).strftime('%Y%m%d')),
        date_end=date_end,
        length=sim_length
    )
    diff = None
    try:
        diff = exp[0, 1] - sim[0, 1]
    except Exception as ex:
        __logger__.error(f'Exception:\n{ex}\n{traceback.format_exc()}')
    return diff


def get_buy_macd_trend_percentage(coin_logo: str):
    """

    :param save_image:
    :param coin_logo:
    :return:
    """
    date_end = int(dt.datetime.today().strftime('%Y%m%d'))
    date_init = int(back_date_n_days(dt.datetime.today(), 60).strftime('%Y%m%d'))
    macd, signal = get_macd(coin_logo, date_init, date_end, short_length=6, long_length=19)
    return round(100 * get_macd_percentage(macd, signal, operation='buy'), 2)  # check this


def get_sell_macd_trend_percentage(coin_logo: str):
    """

    :param save_image:
    :param coin_logo:
    :return:
    """
    date_end = int(dt.datetime.today().strftime('%Y%m%d'))
    date_init = int(back_date_n_days(dt.datetime.today(), 80).strftime('%Y%m%d'))
    macd, signal = get_macd(coin_logo, date_init, date_end, short_length=19, long_length=39)
    return round(100 * get_macd_percentage(macd, signal, operation='sell'), 2)  # check this
