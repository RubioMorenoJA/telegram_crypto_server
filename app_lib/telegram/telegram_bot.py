"""
Definition of telegram bot and its functions
"""
from telegram.ext import Updater, CommandHandler
from app_lib.configuration.tools.users import set_user, del_user, get_user_by_id
from app_lib.configuration.tools.currencies_limits import get_user_limits_structure, set_coin_limits, del_coin_limit, \
    get_available_coins_structure
from app_lib.log.log import get_log


STOPPED = 0
RUNNING = 1
__logger__ = get_log('telegram_bot')


class TelegramBot(Updater):
    """
    Class to manage telegram bot
    """

    def __init__(self, token: str):
        self.status = STOPPED
        super().__init__(token=token, use_context=True)

    def set_methods(self) -> None:
        """
        Adds methods that telegram bot manages to interact with user by telegram app
        :return:
        """
        self.dispatcher.add_handler(CommandHandler('start', start))
        self.dispatcher.add_handler(CommandHandler('hello', hello))
        self.dispatcher.add_handler(CommandHandler('add_user', add_user))
        self.dispatcher.add_handler(CommandHandler('delete_user', delete_user))
        self.dispatcher.add_handler(CommandHandler('show', show))
        self.dispatcher.add_handler(CommandHandler('show_coins', show_coins))
        self.dispatcher.add_handler(CommandHandler('add_coin', add_coin))
        self.dispatcher.add_handler(CommandHandler('del_coin', del_coin))

    def launch_bot(self) -> int:
        """
        Launch bot and return status
        :return:
        """
        if self.status == STOPPED:
            self.start_polling()
            self.status = RUNNING
        return self.status

    def stop_bot(self) -> int:
        """
        Stops bot and returns status
        :return:
        """
        if self.status == RUNNING:
            self.stop()
            self.status = STOPPED
        return self.status


def start(update, context) -> None:
    """
    Start bot function
    :param update:
    :param context:
    :return:
    """
    start_msg = "Hello, I'm a bot to help you\n" \
                "To watch options send /hello"
    context.bot.send_message(chat_id=update.effective_chat.id, text=start_msg)


def hello(update, context) -> None:
    """
    Hello bot function that shows every function bot has
    :param update:
    :param context:
    :return:
    """
    hello_msg = 'Hello! Welcome to chat:\n' \
                'To add a new user send: /add_user - your_name\n' \
                '  > Example: /add_user - PopeBot\n' \
                'To delete user send: /delete_user\n' \
                'To show available coins send: /show\n' \
                'To show own coins send: /show_coins\n' \
                'To set new coin limit send: /add_coin - coin - limit - value\n' \
                '  > Example: /add_coin - BTC - low - 20000\n' \
                '  > Example: /add_coin - BTC - high - 26000\n' \
                'To delete coin send: /del_coin - coin - limit(optional) - value(optional)\n' \
                '  > Example: /del_coin - BTC - low - 26000\n' \
                '  > Example: /del_coin - ETH - high\n' \
                '  > Example: /del_coin - LTC'
    context.bot.send_message(chat_id=update.effective_chat.id, text=hello_msg)


def add_user(update, context) -> None:
    """
    Adds new user to bot
    :param update:
    :param context:
    :return:
    """
    msg = update.effective_message.text
    __logger__.debug(f"Message from {update.effective_user.username}: {msg}")
    response = set_user(update.effective_message.text, update.effective_chat.id)
    __logger__.debug(f"Set user response: {response}")
    context.bot.send_message(chat_id=update.effective_chat.id, text=response)


def delete_user(update, context) -> None:
    """
    Deletes a user from bot
    :param update:
    :param context:
    :return:
    """
    response = del_user(update.effective_chat.id)
    context.bot.send_message(chat_id=update.effective_chat.id, text=response)


def show(update, context) -> None:
    """
    Shows available coins in app
    :param update:
    :param context:
    :return:
    """
    available_coins = get_available_coins_structure()
    context.bot.send_message(chat_id=update.effective_chat.id, text=available_coins)


def show_coins(update, context) -> None:
    """
    Given a user show coins limits of the user
    :param update:
    :param context:
    :return:
    """
    user = get_user_by_id(update.effective_chat.id)
    response = get_user_limits_structure(user)
    context.bot.send_message(chat_id=update.effective_chat.id, text=response)


def add_coin(update, context) -> None:
    """
    Adds new coin limit to the user
    :param update:
    :param context:
    :return:
    """
    user = get_user_by_id(update.effective_chat.id)
    response = set_coin_limits(user, update.effective_message.text)
    context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    show_coins(update, context)


def del_coin(update, context):
    """
    Delete coin limit of the user
    :param update:
    :param context:
    :return:
    """
    user = get_user_by_id(update.effective_chat.id)
    __logger__.info(f"Delete coin user: {user}")
    response = del_coin_limit(user, update.effective_message.text)
    __logger__.info(f"Delete coin response: {response}")
    context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    show_coins(update, context)
