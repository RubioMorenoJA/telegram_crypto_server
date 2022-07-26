import datetime
import numpy as np


def get_username_by_chat_id(users, chat_id):
    for key, value in users.items():
        if 'chat_id' in value and value['chat_id'] == chat_id:
            return key
    return None


def update_float_list(list, pop_elem):
    list_copy = list.copy()
    for elem in list:
        if abs(pop_elem - elem) < 10e-5:
            list_copy.remove(elem)
    return list(filter(lambda elem: elem if abs(elem-pop_elem) > 1e-5 else None, list))


def update_dict_with_value(old_dict, keys_list, value):
    if isinstance(old_dict, list):
        keys_list[0] = int(keys_list[0])
        assert len(old_dict) > keys_list[0], f'Unable to update dict in "{__file__}": index is out of range'
    if keys_list[0] not in old_dict:
        old_dict[keys_list[0]] = {}
    old_dict[keys_list[0]] = \
        update_dict_with_value(old_dict[keys_list[0]], keys_list[1:], value) if len(keys_list) > 1 else value
    return old_dict


def update_dict_delete_key(old_dict: dict, keys_list: list):
    """
    Updates dictionary deleting the value by 'keys_list' key
    :param old_dict:
    :param keys_list: list that represents key as json type key: 'key0.key1' -> ['key0', 'key1']
    :return:
    """
    if isinstance(old_dict, list):
        keys_list[0] = int(keys_list[0])
        assert len(old_dict) > keys_list[0], f'Unable to update dict in "{__file__}": index is out of range'
    else:
        assert keys_list[0] in old_dict, f'Unable to update dict in "{__file__}": {keys_list[0]} is not in dict'
    if len(keys_list) > 1:
        old_dict[keys_list[0]] = update_dict_delete_key(old_dict[keys_list[0]], keys_list[1:])
    else:
        old_dict.pop(keys_list[0])
    return old_dict


def get_dict_value(my_dict, keys_list):
    if keys_list[0] in my_dict.keys():
        if len(keys_list) > 1:
            return get_dict_value(my_dict[keys_list[0]], keys_list[1:])
        else:
            return my_dict[keys_list[0]]
    else:
        raise IndexError


def check_dict_value(coin_limits, keys_list):
    dict_value = get_dict_value(coin_limits, keys_list)
    if not dict_value or len(dict_value) == 0:
        return False
    return True


def check_avail(coin_limits, keys_list):
    while not check_dict_value(coin_limits, keys_list):
        update_dict_delete_key(coin_limits, keys_list)
        keys_list.pop()
    return coin_limits


users = {
    "bot":
        {"token_1": "1207997712", "token_2": "AAEfLR6fMmJbL2FHQKiCURULRkt2a-QXsMo"},
    "Pope": {"chat_id": 88785478},
    "esthornudo": {"chat_id": 1099435927}
}
elem_list = [1,2,3,4,5]
limits = {
    "Pope": {
        "BTC": {
            "low": [23200.0, 26400.0, 33600.0, 44000.0, 49750.0],
            "high": [52500.0]
        },
        "ZIL": {
            "low": [0.05],
            "high": [0.165]
        },
        "IOT": {
            "high": [],
            "low": [0.8]
        },
        "DOGE": {
            "high": [],
            "low": [0.01]
        }
    }
}


# print(get_username_by_chat_id(users, 88785478))
# print(update_float_list(elem_list, 2))
# update_dict_with_value(limits, ["Pope", "BTC", "low"], [21000])
# update_dict_with_value(limits, ["Pope", "BTC", "high"], [21000])
# print(limits)
# new_limits = check_avail(limits, ['Pope', 'DOGE', 'high'])
# print(new_limits)

from app_lib.DDBB.sqlite.models import BTC, ETH
# from app_lib.extract_lib.data_seeker import DataSeeker
# from app_lib.extract_lib.html_reader import HtmlReader
from app_lib.utils.date_utils import historical_coin_date_to_int, back_date_n_months, back_date_n_days
from app_lib.data_science.indicators.plot_settings import get_labels_from_y_ticks
from app_lib.extract_lib.historical_data_extractor import load_historical_data_from_html, historical_data_extractor
from app_lib.data_science.indicators.main import get_ema, save_web_plots
from app_lib.views.blueprint_v1.coin_data import get_buy_macd_trend_percentage, get_sell_macd_trend_percentage

# html = HtmlReader()
# data_seeker = DataSeeker("https://www.worldcoinindex.com/coin/{currency}/historical".format(currency='bitcoin'))
# table = html.get_historical_table(data_seeker.get_html_data(), limit=1)
# table[0][0] = int(historical_coin_date_to_int(table[0][0]))
# btc_db = BTC()
# eth_db = ETH()
# btc_db.set_data(tuple(table[0]))
# db_data = btc_db.get_data()
# print(db_data)
# with open('C:\\Users\\jrubiomo\\Downloads\\TCS_data\\eth_table.html') as file:
#     # load_historical_data_from_html(btc_db, file.read())
#     load_historical_data_from_html(eth_db, file.read())
# get_ema('BTC', date_init=20210101, date_end=20210601)
#print(back_date_n_days(datetime.datetime.today(), 31).strftime('%Y%m%d'))
# print(back_date_n_months(datetime.datetime.today(), 32).strftime('%Y%m%d'))
# historical_data_extractor()
ticks = [-12 ** exp for exp in range(-5, 7)] + [12 ** exp for exp in range(-5, 7)]
labels = get_labels_from_y_ticks(np.array(ticks))
save_web_plots('BTC', 'bitcoin', date_init=20210101, date_end=20210601)
buy_perc = get_buy_macd_trend_percentage('BTC')
sell_perc = get_sell_macd_trend_percentage('BTC')
print(f'buy {buy_perc}, sell {sell_perc}')
