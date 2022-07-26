"""
Currencies configuration
"""
import os
from json import loads
from app_lib.utils.files_utils import transform_path
from app_lib.log.log import get_log


__logger__ = get_log('currencies_conf')


def get_currencies() -> list:
    """
    Reads logos.json and get the keys that they are name of the currencies
    :return: list with currencies if it is possible
    """
    currencies = []
    try:
        file_name = str(os.getcwd()).split('app_lib')[0] \
                    + transform_path('/app_lib/configuration/json/logos.json')
        with open(file_name) as file:
            currencies = list(loads(file.read()).keys())
    except IOError as ex:
        __logger__.error('IOError: %s', ex)
    except Exception as ex:
        __logger__.error('Exception: %s', ex)
    return currencies

# next version we should be able to add and delete currencies
# def add_new_currency():
# 	return False
#
# def get_currencies_file(type='r'):
# 	path = str(os.getcwd()).split('app/')[0] + 'app/configuration_tools/'
# 	file = open(path + 'use_currencies.txt', type)
