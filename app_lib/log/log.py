"""
Definition of general logger
"""
import logging
import os
from app_lib.utils.files_utils import transform_path


def get_log(log_name):
    """
    Returns set logger
    :param log_name:
    :return:
    """
    logging.basicConfig(
        level=logging.INFO,
        filename=str(os.getcwd()).split('app_lib')[0] + transform_path('/app_lib/log.txt'),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(log_name)
