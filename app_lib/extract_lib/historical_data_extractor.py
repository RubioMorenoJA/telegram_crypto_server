"""
Definition and manage of historical data to save into database
"""
import traceback
import numpy as np
from app_lib.extract_lib.data_seeker import DataSeeker
from app_lib.extract_lib.html_reader import HtmlReader
from app_lib.extract_lib.json_reader import JsonReader
from app_lib.configuration.tools.currencies_conf import get_currencies
from app_lib.configuration.tools.logos import get_logos
from app_lib.log.log import get_log
from app_lib.DDBB.sqlite.models import get_model
from app_lib.extract_lib.extractor import urls
from app_lib.utils.date_utils import historical_coin_date_to_int


__logger__ = get_log('historical_extractor')


def historical_data_extractor(coins_name: list = None, date_init: int = None, date_end: int = None) -> str:
    """
    Main function to extract, process and save historical data.
    Historical data is composed by ['date', 'close price', 'min price', 'max price']
    :param coins_name:
    :param date_init:
    :param date_end:
    :return:
    """
    added_data = ''
    try:
        currencies = coins_name if coins_name else get_currencies()
        logos = get_logos()
        eur_usd_amount = get_eur_usd()
        for curr in currencies:
            if not date_init and not date_end:
                added_data += set_historical_day(curr, logos[curr], eur_usd_amount)
            else:
                added_data += set_historical_interval(curr, logos[curr], eur_usd_amount, date_init, date_end)
    except Exception as ex:
        exc_str = f'Exception:\n{ex}\n{traceback.format_exc()}\n'
        added_data += exc_str
        __logger__.error(exc_str)
    finally:
        if not added_data:
            added_data = 'No data added to database'
    return added_data


def set_historical_day(coin_name: str, coin_logo: str, eur_usd_amount: float) -> str:
    """
    Extracts and save the last 24h coin data
    :param coin_name:
    :param coin_logo:
    :param eur_usd_amount:
    :return:
    """
    added_data = ''
    hist_data = get_historical_data(coin_name, limit=1)[0]
    hist_data[1:] = data_price_transform(hist_data[1:], eur_usd_amount)
    db_object = get_model(coin_logo)
    if db_object is not None:
        current_day_data = db_object.get_data(date_init=hist_data[0])
        if len(current_day_data) == 0:
            db_object.set_data(tuple(hist_data))
            added_data += f'Added {coin_logo}:\n\t{hist_data}\n'
    return added_data


def set_historical_interval(coin_name: str, coin_logo: str, eur_usd_amount: float, date_init: int, date_end: int) -> str:
    """
    Extracts and save coin data from init to end
    :param coin_name:
    :param coin_logo:
    :param eur_usd_amount:
    :param date_init:
    :param date_end:
    :return:
    """
    def to_eur_historical_price(row):
        row[1:] = data_price_transform(row[1:], eur_usd_amount)

    def avoid_repeated_data(insert_data: list, got_dates: list) -> list:
        return list(
            filter(
                lambda row: row[0] not in got_dates and date_init <= row[0] <= date_end,
                insert_data
            )
        )

    added_data = ''
    hist_data = get_historical_data(coin_name)
    list(map(to_eur_historical_price, hist_data))
    db_object = get_model(coin_logo)
    if db_object is not None:
        current_data = db_object.get_data(date_init=date_init, date_end=date_end)
        current_dates = np.array(current_data, dtype=np.int)[:, 0] if len(current_data) > 0 else []
        hist_data = avoid_repeated_data(hist_data, current_dates)
        if len(hist_data) > 0:
            db_object.set_array_data(hist_data)
        added_data += f'Added {coin_logo}:\n\t' + '\n\t'.join([str(row) for row in hist_data]) + '\n'
    return added_data


def get_historical_data(currency: str, limit: int = None) -> list:
    """
    Extract 'currency' data from url (urls[2] in extractor.py) and returns all extracted data
    :param currency:
    :param limit:
    :return:
    """
    def to_int_historical_coin_date(row):
        row[0] = int(historical_coin_date_to_int(row[0]))
    html = HtmlReader()
    data_seeker = DataSeeker(urls[2](currency))
    hist_data = html.get_historical_table(data_seeker.get_html_data(), limit=limit)
    list(map(to_int_historical_coin_date, hist_data))
    return hist_data


def get_eur_usd() -> float:
    """
    Extracts pair value 'eur/usd' from url (urls[0] in extractor.py)
    :return:
    """
    mjson = DataSeeker(urls[0]("EUR-USD"))
    coinbaseexch = JsonReader.get_row_data(JsonReader.read_json_data(mjson.get_json_data()))
    return coinbaseexch['amount']


def data_price_transform(data: list, transform: float) -> list:
    """
    Given price data as $USD this function transforms it as €EUR
    :param data: price array
    :param transform: €/$ relation
    :return:
    """
    for elem, item_data in enumerate(data):
        data[elem] = item_data / transform
    return data


def load_historical_data_from_html(db_object, html_table: str, price_transform: bool = True) -> None:
    """
    Loads a local html file containing historical data in order to transform and save it
    into database
    :param db_object:
    :param html_table:
    :param price_transform:
    :return:
    """
    html = HtmlReader()
    load_data = html.get_historical_table(html_table)
    eur_usd_amount = get_eur_usd()
    for row in load_data:
        row[0] = int(historical_coin_date_to_int(row[0]))
        if price_transform:
            row[1:] = data_price_transform(row[1:], eur_usd_amount)
    db_object.set_array_data(list(map(tuple, load_data)))
