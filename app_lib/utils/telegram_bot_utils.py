"""
Utils for telegram bot
"""
import re
from app_lib.log.log import get_log


__logger__ = get_log('telegram_bot_utils')


def check_user_name(username) -> str:
    """
    Checks username and return if match the regex
    :param username:
    :return:
    """
    new_username = ''
    re_list = re.findall(r'[a-zA-Z\d]+[a-zA-Z\d\_\-]*$', username)
    if len(re_list) > 0:
        new_username = re_list[0]
    return new_username


def check_user_exists(users, chat_id) -> bool:
    """
    Checks if the new user with chat_id exists is already a user
    :param users:
    :param chat_id:
    :return:
    """
    return any(filter(lambda value: 'chat_id' in value and value['chat_id'] == chat_id, users.values()))


def get_username_by_chat_id(users, chat_id) -> str:
    """
    Returns the username given its chat_id value
    :param users:
    :param chat_id:
    :return:
    """
    for key, value in users.items():
        if 'chat_id' in value and value['chat_id'] == chat_id:
            return key
    return ''
