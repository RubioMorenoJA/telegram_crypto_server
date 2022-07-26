"""
App main module
"""
import time
import datetime
import traceback
from app_lib.extract_lib.extractor import run, min_max_extractor
from app_lib.log.log import get_log
from app_lib.telegram.telegram_bot import TelegramBot
from app_lib.configuration.tools.users import get_bot
from app_lib.utils.notification_utils import notify_telegram, notify_telegram_auth_error
from app_lib.gdrive.drive_update import update_drive_files, COIN_EXCEL_LIST_NAME, update_month_limits
from app_lib.gdrive.drive_api import AuthError
from app_lib.utils.notification_utils import avoid_network_error
from app_lib.extract_lib.historical_data_extractor import historical_data_extractor


__logger__ = get_log('app_main')


@avoid_network_error
def launch_telegram_server():
    """
    Launches telegram_bot server to listen to users
    :return:
    """
    bot = get_bot()
    if bot['token']:
        telegram_bot = TelegramBot(bot['token'])
        telegram_bot.set_methods()
        telegram_bot.launch_bot()
    else:
        telegram_bot = None
    return telegram_bot


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


def run_extractor(must_notify_telegram=True, must_save_data=True) -> None:
    """
    Main function in extractor app:
        - Extract data.
        - Notify users by telegram bot
        - Update Google drive excels with extracted data
    :param must_notify_telegram:
    :param must_save_data:
    :return:
    """
    __logger__.info('Running extractor')
    last_updated_time = None
    while True:
        telegram_bot = launch_telegram_server()
        try:
            while True:
                data = run()
                if must_notify_telegram:
                    notify_telegram(data)
                if must_save_data:
                    last_updated_time = update_limits(last_updated_time)
                    update_drive_files(data, COIN_EXCEL_LIST_NAME)
                time.sleep(30)
        except AuthError as ex:
            __logger__.error('%s\n%s', ex, traceback.format_exc())
            notify_telegram_auth_error()
            must_save_data = False
        except Exception as ex:
            __logger__.error('%s\n%s', ex, traceback.format_exc())
        finally:
            if telegram_bot:
                telegram_bot.stop()
                status = telegram_bot.stop_bot()
                __logger__.info('Telegram bot status: %s', status)
