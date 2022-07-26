"""
Definition of functions used with telegram
"""
from requests import post
import traceback
from telegram.error import NetworkError
from app_lib.log.log import get_log
from app_lib.configuration.tools.users import get_bot


__logger__ = get_log('telegram_api')


def avoid_network_error(func):
    def inner(*args):
        return_value = None
        try:
            return_value = func(*args)
        except NetworkError as ex:
            __logger__.error('%s\n%s', ex, traceback.format_exc())
        except Exception as ex:
            __logger__.error('%s\n%s', ex, traceback.format_exc())
        finally:
            return return_value
    return inner


@avoid_network_error
def send_message(chat_id, message) -> str:
    """
    Sends a message to user with chat_id if telegram_bot's token exists
    :param chat_id:
    :param message:
    :return:
    """
    response = ''
    telegram_bot = get_bot()
    if telegram_bot['token']:
        url = 'https://api.telegram.org/bot{token}/sendMessage'.format(
            token=telegram_bot['token'])
        data = {'chat_id': chat_id, 'text': message}
        response = post(url, data)
        __logger__.debug('Response Status code: %s', response.status_code)
        __logger__.debug('Response content: %s', response.content)
    else:
        __logger__.error('Unable to get telegram_bot token')
    return response
