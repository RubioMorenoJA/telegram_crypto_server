"""
Utils to notify by telegram
"""
import datetime as dt
from app_lib.utils.lists_utils import get_min, get_max
from app_lib.configuration.tools.currencies_limits import get_coin_limits
from app_lib.log.log import get_log
from app_lib.telegram.telegram_api import send_message, avoid_network_error
from app_lib.configuration.tools.users import get_users


global INTELLI_DICT
INTELLI_DICT = {}
NOTIFICATION_PERCENTAGE = 0.025
NOTIFICATION_TIME = 15 * 60  # min * 60s
__logger__ = get_log('notification_utils')


def notify_telegram(data: list, intelli_limit: bool = True) -> None:
    """
    Function used to notify by telegram if any coin match the limits
    :param data:
    :param intelli_limit:
    :return:
    """
    coin_limits = get_coin_limits()
    users = get_users()
    coin_values = {item['logo']: item['amount'] for item in data}
    for user in users:
        __logger__.info(f'User: {user}')
        if user in coin_limits:
            for coin_name, coin_limit_values in coin_limits[user].items():
                msg = None
                if intelli_limit:
                    low_case, high_case = check_intelligent_limits(user, coin_name, coin_limit_values, coin_values)
                else:
                    low_case, high_case = check_limits(coin_limit_values, coin_values, coin_name)
                __logger__.info(f'Coin: {coin_name}. High: {high_case}. '
                                f'Low: {low_case}. Value: {coin_values[coin_name]}')
                if low_case:
                    msg = f'{coin_name} is lower than {low_case}: '
                elif high_case:
                    msg = f'{coin_name} is higher than {high_case}: '
                if msg:
                    msg = msg + f'current value {coin_values[coin_name]}'
                    send_message(users[user]['chat_id'], msg)


def check_limits(coin_limit_values: dict, coin_values: dict, coin_name: str):
    """

    :param coin_limit_values: dictionary. Limits values of coins with two keys: low and high.
    :param coin_values: dictionary. Current values of every coin got from internet.
    :param coin_name: name of the coin to be evaluated
    :return:
    """
    low_case, high_case = None, None
    if coin_name in coin_values:
        if 'low' in coin_limit_values and len(coin_limit_values['low']) > 0:
            low_case = get_min(list(filter(lambda value: value if value > coin_values[coin_name] else None,
                                           coin_limit_values['low'])))
        if 'high' in coin_limit_values and len(coin_limit_values['high']) > 0:
            high_case = get_max(list(filter(lambda value: value if value < coin_values[coin_name] else None,
                                            coin_limit_values['high'])))
    return low_case, high_case


def check_intelligent_limits(user: str, coin: str, coin_limit_values: dict, coin_values: dict):
    """
    When the current price has passed our limits we must know if the user has to be notified using intelligent limits
    :param user:
    :param coin:
    :param coin_limit_values:
    :param coin_values:
    :return:
    """
    low_case, high_case = check_limits(coin_limit_values, coin_values, coin)
    if low_case:
        if not intelligent_limit(user, coin, 'low', low_case, coin_values[coin], INTELLI_DICT):
            low_case = None
    elif high_case:
        if not intelligent_limit(user, coin, 'high', high_case, coin_values[coin], INTELLI_DICT):
            high_case = None
    return low_case, high_case


def intelligent_limit(user: str, coin: str, limit_type: str, limit_value: float,
                      current_value: float, intelligent_dict: dict) -> bool:
    """
    This function is used to check last values of a coin limit to determine if we should notify the user that the
    expected coin has a "big" change. With this we avoid to over-notify the user.
    :param user:
    :param coin:
    :param limit_type: low or high
    :param limit_value:
    :param current_value:
    :param intelligent_dict: dictionary for keeping data
    :return: boolean to determine if we must notify the user
    """
    send_msg = True
    current_time = dt.datetime.now()
    if user not in intelligent_dict:
        intelligent_dict[user] = {
            coin: {limit_type: {'limit': limit_value, 'value': current_value, 'time': current_time}}
        }
    elif coin not in intelligent_dict[user]:
        intelligent_dict[user][coin] = \
            {limit_type: {'limit': limit_value, 'value': current_value, 'time': current_time}}
    elif limit_type not in intelligent_dict[user][coin]:
        intelligent_dict[user][coin][limit_type] = {'limit': limit_value, 'value': current_value, 'time': current_time}
    else:
        if intelligent_dict[user][coin][limit_type]['limit'] != limit_value \
                and (current_time - intelligent_dict[user][coin][limit_type]['time']).seconds > NOTIFICATION_TIME:
            intelligent_dict[user][coin][limit_type]['limit'] = limit_value
            intelligent_dict[user][coin][limit_type]['time'] = current_time
        elif intelligent_dict[user][coin][limit_type]['value'] > 0:
            percentage = abs(intelligent_dict[user][coin][limit_type]['value'] - current_value) \
                         / intelligent_dict[user][coin][limit_type]['value']
            if percentage > NOTIFICATION_PERCENTAGE:
                intelligent_dict[user][coin][limit_type]['value'] = current_value
            else:
                send_msg = False
    return send_msg


@avoid_network_error
def notify_telegram_auth_error() -> None:
    """
    Function used to notify by telegram about google auth error
    :return:
    """
    auth_error_msg = 'Google Auth Error has been thrown.'
    users = get_users()
    map(lambda user: send_message(user['chat_id'], auth_error_msg) if 'chat_id' in user else None, users)
