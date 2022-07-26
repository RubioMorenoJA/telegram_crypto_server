from app_lib.extract_lib.extractor import run, min_max_extractor, min_max_from_db
from app_lib.log.log import get_log
#from app_lib.utils.notification_utils import notify_telegram
from app_lib.gdrive.drive_update import update_drive_files, COIN_EXCEL_LIST_NAME, update_month_limits
import time
import datetime
from app_lib.extract_lib.historical_data_extractor import historical_data_extractor


NOTIFICATION_PERCENTAGE = 0.025
__logger__ = get_log('pruebas')


def run_extractor(must_notify_telegram=True, must_save_data=True):
    last_updated_time = None
    while True:
        try:
            __logger__.info('Running extractor')
            data = run()
            if must_notify_telegram:
                #notify_telegram(data)
                pass
            if must_save_data:
                last_updated_time = update_limits(last_updated_time)
                update_drive_files(data, COIN_EXCEL_LIST_NAME)
            time.sleep(30)
        except Exception as ex:
            __logger__.error(f'Exception: {ex}')


def update_limits(last_updated_time: datetime.datetime = None) -> datetime.datetime:
    """
    Updates currencies limits min and max daily
    :param last_updated_time:
    :return:
    """
    if not last_updated_time:
        last_updated_time = datetime.datetime.now() - datetime.timedelta(days=+1)
    current_time = datetime.datetime.now()
    if (current_time - last_updated_time).days > 0:
        __logger__.info('Updating limits')
        # getting last historical data and updating coin limits
        historical_data_extractor()
        min_max_data = min_max_extractor()
        update_month_limits(min_max_data, COIN_EXCEL_LIST_NAME)
        last_updated_time = current_time
    return last_updated_time


# run_extractor()
