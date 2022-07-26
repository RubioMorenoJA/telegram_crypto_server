"""
Users access and configuration
"""
import os
import traceback
from json import loads, dumps
from app_lib.configuration.tools.currencies_limits import del_user_limits
from app_lib.utils.files_utils import transform_path, save_dict_as_json
from app_lib.utils.telegram_bot_utils import check_user_name, check_user_exists, get_username_by_chat_id
from app_lib.log.log import get_log


ROOT = str(os.getcwd()).split('app_lib')[0]
FILE_NAME = ROOT + transform_path('/app_lib/configuration/json/users.json')
__logger__ = get_log('users')


def get_users() -> dict:
    """
    Reads users.json
    :return: dict with users if it is possible
    """
    users = {}
    try:
        with open(FILE_NAME, 'r') as file:
            users = loads(file.read())
    except IOError as ex:
        __logger__.error('IOError: %s\n%s', ex, traceback.format_exc())
    except Exception as ex:
        __logger__.error('Exception: %s\n%s', ex, traceback.format_exc())
    return users


def get_user(username) -> dict:
    """
    Returns the user with username if exists
    :param username:
    :return:
    """
    user = {}
    users = get_users()
    if users and username in users.keys():
        user = users[username]
    return user


def get_user_by_id(chat_id) -> str:
    """
    Returns the username by chat_id
    :param chat_id:
    :return:
    """
    user = ''
    users = get_users()
    if users:
        user = get_username_by_chat_id(users, chat_id)
    return user


def get_bot() -> dict:
    """
    Returns telegram_bot's token
    :return:
    """
    bot = get_user('bot')
    if bot:
        bot['token'] = f'{bot["token_1"]}:{bot["token_2"]}'
    else:
        bot['token'] = ''
    __logger__.debug('bot: %s', bot)
    return bot


def set_user(username, chat_id) -> str:
    """
    Tries to set a new user in users.json with username and chat_id
    :param username:
    :param chat_id:
    :return:
    """
    response = 'Unable to create user'
    users = get_users()
    username = check_user_name(username)
    if not check_user_exists(users, chat_id):
        users[username] = {'chat_id': chat_id}
        if save_dict_as_json(users, FILE_NAME):
            response = f'User "{username}" created'
    else:
        response = f'User "{username}" already exists'
    return response


def del_user(chat_id) -> str:
    """
    Deletes the selected user by chat_id in users.json
    :param chat_id:
    :return:
    """
    response = 'Unable to delete user'
    users = get_users()
    if check_user_exists(users, chat_id):
        username = get_username_by_chat_id(users, chat_id)
        if username:
            users.pop(username)
            if save_dict_as_json(users, FILE_NAME):
                response = f'User "{username}" deleted'
            response = response + '\n' + del_user_limits(username)
    else:
        response = 'User does not exist'
    return response
