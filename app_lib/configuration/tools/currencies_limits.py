"""
Currencies limits configuration
"""
import os
from json import loads, dumps, JSONDecodeError
import traceback
from app_lib.utils.files_utils import transform_path, save_dict_as_json
from app_lib.utils.dict_utils import update_dict_with_value, update_dict_delete_key, check_dict_value
from app_lib.utils.lists_utils import update_float_list
from app_lib.log.log import get_log


__logger__ = get_log('currencies_limits')
AVAILABLE_COINS_FILE = str(os.getcwd()).split('app_lib')[0] + transform_path('/app_lib/configuration/json/logos.json')
COIN_LIMITS_FILE = str(os.getcwd()).split('app_lib')[0] + transform_path('/app_lib/configuration/json/coin_limits.json')


def get_available_coins() -> list:
    """
    Returns a list with available coins in logos.json if it is possible
    :return: list
    """
    available_coins = []
    try:
        with open(AVAILABLE_COINS_FILE, 'r') as file:
            available_coins = list(loads(file.read()).values())
    except IOError as ex:
        __logger__.error('IOError: %s\n%s', ex, traceback.format_exc())
    except JSONDecodeError as ex:
        __logger__.error('JSONDecodeError: %s\n%s', ex, traceback.format_exc())
    except Exception as ex:
        __logger__.error('Exception: %s\n%s', ex, traceback.format_exc())
    return available_coins


def get_available_coins_structure() -> str:
    """
    Returns a string with available coins
    :return:
    """
    available_coins = get_available_coins()
    structure = ''
    if available_coins:
        structure = '\n'.join(available_coins)
        structure = 'Available coins:\n' + structure
    return structure


def get_coin_limits() -> dict:
    """
    Returns the whole file coin_limits.json if it is possible
    :return:
    """
    coin_limits = {}
    try:
        with open(COIN_LIMITS_FILE, 'r') as file:
            coin_limits = loads(file.read())
    except IOError as ex:
        __logger__.error('IOError: %s\n%s', ex, traceback.format_exc())
    except JSONDecodeError as ex:
        __logger__.error('JSONDecodeError: %s\n%s', ex, traceback.format_exc())
    except Exception as ex:
        __logger__.error('Exception: %s\n%s', ex, traceback.format_exc())
    return coin_limits


def get_user_limits(username) -> dict:
    """
    Returns the user's coin limits
    :param username:
    :return:
    """
    user_limits = {}
    coin_limits = get_coin_limits()
    __logger__.debug('get_user_limits: %s', coin_limits)
    if coin_limits and username in coin_limits:
        user_limits = coin_limits[username]
    return user_limits


def get_user_limits_structure(username) -> str:
    """
    Returns a string with user's coin limits
    :param username:
    :return:
    """
    user_limits = get_user_limits(username)
    if not user_limits:
        return f'{username} has no coins'
    response = f'{username} coins:\n'
    for coin in user_limits.keys():
        response = response + f'> {coin}\n'
        for limit in user_limits[coin]:
            response = response + f'-> {limit}\n'
            for value in user_limits[coin][limit]:
                response = response + f'--> {value}\n'
    return response


def get_user_and_coin_limits(username, coin_name) -> dict:
    """
    Returns the limits values of the selected coin for a given username
    :param username:
    :param coin_name:
    :return:
    """
    coin_limits = {}
    user_coins = get_user_limits(username)
    __logger__.debug('get_user_and_coin_limits: %s', user_coins)
    if user_coins and coin_name in user_coins:
        __logger__.debug('get_user_and_coin_limits: %s - %s', username, coin_name)
        coin_limits = user_coins[coin_name]
    return coin_limits


def set_coin_limits(username, text) -> str:
    """
    Function used to add new coin limit value for a given username
    :param username:
    :param text:
    :return:
    """
    coin_data = text.split(' - ')
    __logger__.debug('Set coin limits text: %s', text)
    if len(coin_data) != 4:
        return 'Unable to set limit: wrong message'
    __logger__.debug('coin_data: %s', coin_data)
    response = 'Wrong coin limit value'
    if coin_data[1] in get_available_coins():
        if coin_data[2] in ('low', 'high'):
            try:
                value = float(coin_data[3])
                coin_limits = get_coin_limits()
                keys_list = [username] + coin_data[1:3]
                __logger__.debug('keys_list: %s', keys_list)
                current_limits = get_user_and_coin_limits(username, coin_data[1])
                __logger__.debug('current_limits: %s', current_limits)
                if current_limits and coin_data[2] in current_limits.keys():
                    value_to_set = current_limits[coin_data[2]] + [value] if value not in current_limits[coin_data[2]] \
                        else current_limits[coin_data[2]]
                    value_to_set.sort()
                else:
                    value_to_set = [value]
                __logger__.debug('list_to_set: %s', keys_list)
                __logger__.debug('value_to_set: %s', value_to_set)
                if current_limits == value_to_set:
                    response = 'New limit exists'
                else:
                    update_dict_with_value(coin_limits, keys_list, value_to_set)
                    __logger__.debug(f'New coin limits: {coin_limits}')
                    if save_dict_as_json(coin_limits, COIN_LIMITS_FILE):
                        response = f'New limit "{coin_data[1]}-{coin_data[2]}-{coin_data[3]}" created'
            except IOError as ex:
                __logger__.error('IOError: %s\n%s', ex, traceback.format_exc())
            except ValueError as ex:
                __logger__.error('ValueError: %s\n%s', ex, traceback.format_exc())
            except TypeError as ex:
                __logger__.error('TypeError: %s\n%s', ex, traceback.format_exc())
            except Exception as ex:
                __logger__.error('Exception: %s\n%s', ex, traceback.format_exc())
        else:
            response = 'Coin limit not defined (low/high)'
    else:
        response = 'Coin name not in available coins'
    return response


def del_coin_limit(username, text) -> str:
    """
    Function used to delete an existing coin limit value for a given username
    :param username:
    :param text:
    :return:
    """
    coin_data = text.split(' - ')
    __logger__.debug('Del coin limits text: %s', text)
    __logger__.debug('Del coin limits list: %s', coin_data)
    len_coin_data = len(coin_data)
    response = 'Unable to delete limit: wrong message'
    if len_coin_data == 1:
        return response
    save_new_limits = False
    coin_limits = get_coin_limits()
    if coin_data[1] in get_available_coins():
        if len_coin_data == 2:
            keys_list = [username] + [coin_data[1]]
            __logger__.debug('list_to_del: %s', keys_list)
            update_dict_delete_key(coin_limits, keys_list)
            __logger__.debug('Coin limits: %s', coin_limits)
            save_new_limits = True
        else:
            if coin_data[2] in ('low', 'high'):
                keys_list = [username] + coin_data[1:3]
                if len_coin_data == 3:
                    __logger__.debug('list_to_del: %s', keys_list)
                    update_dict_delete_key(coin_limits, keys_list)
                    __logger__.debug('Coin limits: %s', coin_limits)
                    save_new_limits = True
                else:
                    if len_coin_data == 4:
                        value = None
                        try:
                            value = float(coin_data[3])
                        except Exception as ex:
                            __logger__.error('Exception: %s\n%s', ex, traceback.format_exc())
                            response = 'Wrong coin limit value'
                        if value and isinstance(value, float):
                            __logger__.debug('list_to_del: %s', keys_list)
                            current_limits = get_user_and_coin_limits(username, coin_data[1])[coin_data[2]]
                            value_to_keep = update_float_list(current_limits, value)
                            __logger__.debug('value_to_del: %s', value_to_keep)
                            if len(value_to_keep) == 0:
                                keep_removing = True
                                while keep_removing:
                                    update_dict_delete_key(coin_limits, keys_list)
                                    keys_list.pop()
                                    if check_dict_value(coin_limits, keys_list):
                                        keep_removing = False
                                __logger__.debug('New coin_limits: %s', coin_limits)
                                save_new_limits = True
                            elif current_limits != value_to_keep:
                                update_dict_with_value(coin_limits, keys_list, value_to_keep)
                                __logger__.debug('New coin limits: %s', coin_limits)
                                save_new_limits = True
            else:
                response = 'Coin limit not defined (low/high)'
    else:
        response = 'Coin name not in available coins'
    if save_new_limits:
        if save_dict_as_json(coin_limits, COIN_LIMITS_FILE):
            new_limit = '-'.join(coin_data[1:])
            response = f'New limit "{new_limit}" deleted'
    return response


def del_user_limits(username) -> str:
    """
    Removes all limits from 'username' user
    :param username:
    :return:
    """
    response = 'Unable to delete limits'
    coin_limits = get_coin_limits()
    if coin_limits and username in coin_limits:
        coin_limits = update_dict_delete_key(coin_limits, [username])
        if save_dict_as_json(coin_limits, COIN_LIMITS_FILE):
            response = f'{username} limits have been removed'
    return response
