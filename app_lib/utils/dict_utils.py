"""
Utils for dictionaries
"""
from app_lib.log.log import get_log


__logger__ = get_log('dict_utils')


def update_dict_with_value(old_dict: dict, keys_list: list, value) -> dict:
    """
    Updates dictionaries with new value given 'key_list' key
    :param old_dict:
    :param keys_list: list that represents key as json type key: 'key0.key1' -> ['key0', 'key1']
    :param value:
    :return:
    """
    __logger__.debug(f'old_dict: {old_dict}')
    __logger__.debug(f'keys_list: {keys_list}')
    __logger__.debug(f'value: {value}')
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


def transform_coin_limits(old_coin_limits: list) -> dict:
    """
    Transforms coin limits dictionary list from [{logo, limit, amount}] to [{logo: {limit: amount}}]
    :param old_coin_limits:
    :return:
    """
    coin_limits = {}
    for item in old_coin_limits:
        if item['logo'] not in coin_limits:
            coin_limits[item['logo']] = {item['limit']: item['amount']}
        else:
            coin_limits[item['logo']][item['limit']] = item['amount']
    return coin_limits


def get_dict_value(my_dict, keys_list):
    """
    Returns the selected value by 'keys_list' key
    :param my_dict:
    :param keys_list:
    :return:
    """
    if keys_list[0] in my_dict.keys():
        if len(keys_list) > 1:
            return get_dict_value(my_dict[keys_list[0]], keys_list[1:])
        else:
            return my_dict[keys_list[0]]
    else:
        raise KeyError


def check_dict_value(my_dict, keys_list):
    """
    Checks if the selected value by 'keys_list' key is not None or an empty list or dict
    :param my_dict:
    :param keys_list:
    :return:
    """
    dict_value = get_dict_value(my_dict, keys_list)
    if not dict_value or len(dict_value) == 0:
        return False
    return True
