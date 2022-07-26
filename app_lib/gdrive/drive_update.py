"""
Main file of google drive excel updating
"""
import math
from app_lib.gdrive.drive_api import DriveFile, Cryptocurrencies
from app_lib.utils.dict_utils import transform_coin_limits


COIN_EXCEL_FILE_NAME = 'cryptocurrencies.xlsx'
COIN_EXCEL_LIST_NAME = ['crypto_pope.xlsx', 'cryptocurrencies.xlsx', 'crypto_binance.xlsx']
DECIMAL_LENGTH = 4


def update_drive_files(coin_data, file_list) -> None:
    """
    Given extracted coin data updates every file in filenames list
    :param coin_data:
    :param file_list:
    :return:
    """
    for file in file_list:
        update_drive_excel(coin_data, file)


def update_month_limits(min_max_data, file_list) -> None:
    """
    Given minimum and maximum coin data updates every file in filenames list
    :param min_max_data:
    :param file_list:
    :return:
    """
    for file in file_list:
        update_drive_excel_limits(min_max_data, file)


def update_drive_excel(coin_data, file_name) -> None:
    """
    Main function for updating data of selecting file
    :param coin_data:
    :param file_name:
    :return:
    """
    driver_file = DriveFile(file_name)
    coin_excel = Cryptocurrencies(file_name)
    coin_values = {item['logo']: item['amount'] for item in coin_data}
    updated_coin_excel = False
    for coin_name in coin_excel.get_crypto_names():
        if coin_name in coin_values:
            index = coin_excel.match_crypto_row(coin_name)
            coin_excel.set_value(index, coin_excel.PRICE_COLUMN_NAME, coin_values[coin_name])
            eur_quant = calculate_eur_quantity(coin_excel, index, coin_values[coin_name])
            coin_excel.set_value(index, coin_excel.EUR_QUANTITY_COLUMN_NAME, eur_quant)
            eur_profit = calculate_eur_profit(coin_excel, index)
            coin_excel.set_value(index, coin_excel.EUR_PROFIT_COLUMN_NAME, eur_profit)
            eur_percent_profit = calculate_eur_percent_profit(coin_excel, index)
            coin_excel.set_value(index, coin_excel.EUR_PERCENT_PROFIT_COLUMN_NAME, eur_percent_profit)
            updated_coin_excel = True
    if updated_coin_excel:
        total = coin_excel.get_total_eur_quantity()
        coin_excel.set_value(coin_excel.EUR_TOTAL_ROW, coin_excel.EUR_QUANTITY_COLUMN_NAME, total)
        total_profit = coin_excel.get_total_eur_profit()
        coin_excel.set_value(coin_excel.EUR_TOTAL_ROW, coin_excel.EUR_PROFIT_COLUMN_NAME, total_profit)
        total_invest = coin_excel.get_total_eur_invested()
        coin_excel.set_value(coin_excel.EUR_TOTAL_ROW, coin_excel.EUR_BUY_COLUMN_NAME, total_invest)
        coin_excel.apply_styles()
        coin_excel.save_as_excel(file_name)
        driver_file.set_file(file_name)
        driver_file.upload()


def update_drive_excel_limits(min_max_data, file_name) -> None:
    """
    Main function for updating minimum and maximum data of selecting file
    :param min_max_data:
    :param file_name:
    :return:
    """
    driver_file = DriveFile(file_name)
    coin_excel = Cryptocurrencies(file_name)
    coin_limits = transform_coin_limits(min_max_data)
    for coin_name in coin_excel.get_crypto_names():
        if coin_name in coin_limits:
            index = coin_excel.match_crypto_row(coin_name)
            coin_excel.set_value(index, coin_excel.MIN_PRICE_COLUMN_NAME, coin_limits[coin_name]['min'])
            coin_excel.set_value(index, coin_excel.MAX_PRICE_COLUMN_NAME, coin_limits[coin_name]['max'])
    coin_excel.save_as_excel(file_name)
    driver_file.set_file(file_name)
    driver_file.upload()


def calculate_eur_quantity(coin_excel, index, value) -> float:
    """
    Calculates the current amount of euros multiplying the coin amount by the
    coin current price
    :param coin_excel:
    :param index:
    :param value:
    :return:
    """
    unit_quant = coin_excel.get_value(index, coin_excel.UNIT_QUANTITY_COLUMN_NAME)
    if not math.isnan(unit_quant):
        return round(unit_quant * value, DECIMAL_LENGTH)
    return 0.0


def calculate_eur_profit(coin_excel, index) -> float:
    """
    Calculates the current profit in euros given the earnings minus taxes and minus initial
    amount invested
    :param coin_excel:
    :param index:
    :return:
    """
    eur_init = coin_excel.get_value(index, coin_excel.EUR_BUY_COLUMN_NAME)
    eur_quant = coin_excel.get_value(index, coin_excel.EUR_QUANTITY_COLUMN_NAME)
    tax_quant = coin_excel.get_value(index, coin_excel.TAX_QUANTITY_COLUMN_NAME)
    tax_quant = tax_quant if not math.isnan(tax_quant) else 0
    if not math.isnan(eur_init) and not math.isnan(eur_quant):
        return round(eur_quant * (1-tax_quant) - eur_init, DECIMAL_LENGTH)
    return 0


def calculate_eur_percent_profit(coin_excel, index) -> float:
    """
    Calculates the current profit in percentage
    :param coin_excel:
    :param index:
    :return:
    """
    eur_init = coin_excel.get_value(index, coin_excel.EUR_BUY_COLUMN_NAME)
    eur_quant = coin_excel.get_value(index, coin_excel.EUR_QUANTITY_COLUMN_NAME)
    tax_quant = coin_excel.get_value(index, coin_excel.TAX_QUANTITY_COLUMN_NAME)
    tax_quant = tax_quant if not math.isnan(tax_quant) else 0
    if not math.isnan(eur_init) and eur_init > 0 and not math.isnan(eur_quant):
        return 100 * round((eur_quant * (1-tax_quant) / eur_init) - 1, DECIMAL_LENGTH)
    return 0
