"""
Utils used in files IO
"""
import datetime
import os
import sys
import traceback
from json import dumps
from datetime import datetime as dt


def transform_path(path: str) -> str:
    """
    Given the current os (unix, windows) transform the path to get file changing '\' by '/'
    :param path:
    :return:
    """
    new_path = path
    if 'win' in sys.platform:
        new_path = '\\'.join(path.split('/'))
    return new_path


def save_dict_as_json(dict_to_json: dict, filename: str):
    """
    Save a dictionary as a json file
    :param dict_to_json:
    :param filename
    :return:
    """
    from app_lib.log.log import get_log
    __logger__ = get_log('files_utils')
    response = False
    try:
        with open(filename, 'w') as file:
            file.write(dumps(dict_to_json))
        response = True
    except IOError as ex:
        __logger__.error('IOError: %s\n%s', ex, traceback.format_exc())
    except Exception as ex:
        __logger__.error('Exception: %s\n%s', ex, traceback.format_exc())
    return response


def get_absolute_path(path: str) -> str:
    """
    Get total absolute path from path param
    :param path:
    :return:
    """
    return str(os.getcwd()).split('app_lib')[0] + transform_path(path)


def check_file_after_midnight(file_path: str):
    """
    Given a file path checks if file is newer than midnight
    :param file_path:
    :return:
    """
    return check_file_after_than(file_path,  dt.today())


def check_file_after_than(file_path: str, check_time: datetime.datetime):
    """
    Given a file path checks if file is newer than check_time. If file does not exist
    we consider file is created after time.
    :param file_path:
    :param check_time:
    :return:
    """
    from app_lib.log.log import get_log
    __logger__ = get_log('files_utils')
    is_file_after = False
    try:
        file_attr_time = os.path.getmtime(file_path)
        is_file_after = False \
            if (dt.fromtimestamp(file_attr_time).date()-check_time.date()).days < 0 \
            else True
    except IOError as ex:
        __logger__.error('IOError: %s\n%s', ex, traceback.format_exc())
    except Exception as ex:
        __logger__.error('Exception: %s\n%s', ex, traceback.format_exc())
    finally:
        return is_file_after
