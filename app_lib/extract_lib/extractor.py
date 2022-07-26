#
# Extractor of cryptocurrency data from internet. Find, process and save the selected data.
#
import datetime as dt
import traceback
from app_lib.extract_lib.data_seeker import DataSeeker
from app_lib.extract_lib.html_reader import HtmlReader
from app_lib.extract_lib.json_reader import JsonReader
from app_lib.configuration.tools.currencies_conf import get_currencies
from app_lib.configuration.tools.logos import get_logos
# from app_lib.configuration.tools.currencies_limits import get_coin_limits
from app_lib.log.log import get_log
from app_lib.DDBB.sqlite.connection import DataBase
from app_lib.DDBB.sqlite.models import get_model
from app_lib.utils.date_utils import back_date_n_months


__logger__ = get_log('extractor')

urls = [
    lambda pair: "https://api.coinbase.com/v2/prices/{pair}/spot".format(pair=pair),
    lambda currency: "https://www.worldcoinindex.com/coin/{currency}".format(currency=currency),
    lambda currency: "https://www.worldcoinindex.com/coin/{currency}/historical".format(currency=currency)
]


def prepare_row(rowdata):
    if rowdata:
        data = {
            'currency': rowdata[0],
            'logo': rowdata[1],
            'amount': rowdata[2]
        }
    else:
        data = {
            'currency': None,
            'logo': None,
            'amount': 0
        }
    return data


def prepare_dict(currency) -> dict:
    rhtml = HtmlReader()
    mhtml = DataSeeker(urls[1](currency))
    htmldata = rhtml.get_exchange_table(mhtml.get_html_data())
    datadict = prepare_row(htmldata[0]) if htmldata else prepare_row([])
    return datadict


def compare_data(data1, data2):
    if len(data1) == len(data2):
        keys2 = data2.keys()
        for key in data1.keys():
            if not key in keys2 or \
                    data1[key] != data2[key]:
                return True
        return True
    else:
        return True


def transform_to_eur(data_from_exchange):
    new_data = data_from_exchange.copy()
    mjson = DataSeeker(urls[0]("EUR-USD"))
    coinbaseexch = JsonReader.get_row_data(JsonReader.read_json_data(mjson.get_json_data()))
    for item in new_data:
        if 'amount' in item:
            eur_amount = item['amount'] / coinbaseexch['amount']
            item['amount'] = eur_amount
    return new_data


def run():
    transformed_data = []
    try:
        currencies = get_currencies()
        __logger__.debug(f'currencies {currencies}')
        data = []
        for curr in currencies:
            coins = prepare_dict(curr)
            __logger__.debug(f'coins: {coins}')
            if coins:
                data.append(coins)
        transformed_data = transform_to_eur(data)
    except Exception as e:
        __logger__.error(f'Error extracting currencies: {e}')
    return transformed_data
    # if not compare_old_data or compare_data(compare_old_data, compare_new_data):
        # response = w.write_documents(new_data, True, True)
        # compare_old_data = compare_new_data
    # get_log(__name__).debug(response)
    # time.sleep(30)


def min_max_extractor() -> list:
    min_max_data = []
    try:
        currencies = get_currencies()
        logos = get_logos()
        __logger__.debug(f'min_max_extractor currencies {currencies}')
        data = []
        for curr in currencies:
            curr_limits = None
            if logos:
                curr_limits = prepare_min_max_dict(curr, logos)
            if curr_limits:
                data.append(curr_limits[0])
                data.append(curr_limits[1])
        min_max_data = transform_to_eur(data)
    except Exception as ex:
        __logger__.error('Error extracting min max: %s\n%s', ex, traceback.format_exc())
    return min_max_data


def get_min_max(currency):
    rhtml = HtmlReader()
    mhtml = DataSeeker(urls[2](currency))
    html_data = rhtml.get_historical_table(mhtml.get_html_data())
    max_price = max(map(lambda row: row[2], html_data))
    min_price = min(map(lambda row: row[3], html_data))
    return min_price, max_price


def prepare_min_max_dict(curr, logos) -> tuple:
    min_price, max_price = get_min_max(curr)
    min_dict = {}
    max_dict = {}
    if min_price or min_price == 0:
        min_dict = prepare_row([curr, logos[curr], min_price])
        min_dict['limit'] = 'min'
    if max_price == 0:
        max_price = 1
    if max_price:
        max_dict = prepare_row([curr, logos[curr], max_price])
        max_dict['limit'] = 'max'
    return min_dict, max_dict


def min_max_from_db() -> list:
    min_max_data = []
    try:
        logos = get_logos()
        data = []
        for coin_name, coin_logo in logos.items():
            db_obj = get_model(coin_logo)
            curr_limits = None
            if db_obj:
                curr_limits = prepare_min_max_dict_from_db(coin_name, coin_logo, db_obj)
            if curr_limits:
                data.append(curr_limits[0])
                data.append(curr_limits[1])
    except Exception as e:
        __logger__.error(f'Error getting min max from db: {e}')
    return min_max_data


def prepare_min_max_dict_from_db(coin_name: str, coin_logo: str, db_object: DataBase):
    min_dict = {}
    max_dict = {}
    if db_object:
        date_init = int(back_date_n_months(dt.datetime.today(), 1).strftime('%Y%m%d'))
        date_end = int(dt.datetime.today().strftime("%Y%m%d"))
        min_max_data = db_object.get_data(
            date_init=date_init,
            date_end=date_end,
            select_columns="max(MAXIMUM) as maximum, min(MINIMUM) as minimum"
        )[0]
        max_dict = {
            'currency': coin_name,
            'logo': coin_logo,
            'amount': min_max_data[0],
            'limit': 'max'
        }
        min_dict = {
            'currency': coin_name,
            'logo': coin_logo,
            'amount': min_max_data[1],
            'limit': 'min'
        }
    return min_dict, max_dict
