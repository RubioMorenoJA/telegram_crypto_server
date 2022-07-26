"""
Logos configuration file.
logos.json file contains the coin names and the coin logo use in the app
"""
import os
from json import loads
import traceback
from app_lib.utils.files_utils import transform_path
from app_lib.log.log import get_log


__logger__ = get_log('logos')
LOGOS_PATH = str(os.getcwd()).split('app_lib')[0] + transform_path('/app_lib/configuration/json/logos.json')


def get_logos() -> dict:
    """
    Returns the whole logos.json file
    :return:
    """
    logos = {}
    try:
        with open(LOGOS_PATH, 'r') as file:
            logos = loads(file.read())
    except IOError as ex:
        __logger__.error('IOError: %s\n%s', ex, traceback.format_exc())
    return logos
