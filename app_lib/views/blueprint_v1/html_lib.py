"""
File containing html/css definitions for views
"""
import flask
from app_lib.configuration.tools.logos import get_logos
from app_lib.views.blueprint_v1.routes import blueprint
from app_lib.utils.num_str_utils import float_to_string


def add_methods_to_app(app: flask.Flask):
    @app.context_processor
    def utility_processor():
        return dict(
            get_arrow_class=get_arrow_class,
            get_warm_bar=get_warm_bar,
            float=float,
            get_indicator_value_as_str=get_indicator_value_as_str,
            get_arrow_style=get_arrow_style,
            get_indicator_name_information=get_indicator_name_information,
            get_image=get_image,
            get_route_from_logo=get_route_from_logo
        )


def get_indicator_name_information(key: str):
    info = ''
    if key in ['RSI']:
        info = 'https://es.cointelegraph.com/news/here-are-2-key-price-indicators-every-crypto-trader-should-know?utm_source=Telegram&utm_medium=social'
    elif key == 'EMA20 - SMA50':
        info = 'https://es.cointelegraph.com/news/3-ways-traders-use-moving-averages-to-read-market-momentum?utm_source=Telegram&utm_medium=social'
    elif key in ['Buy (macd)', 'Sell (macd)']:
        info = 'https://es.cointelegraph.com/news/here-s-5-ways-investors-can-use-the-macd-indicator-to-make-better-trades?utm_source=Telegram&utm_medium=social'
    return info


def get_arrow_class(key: str, value: float):
    if value is None:
        pass
    elif key == 'EMA20 - SMA50':
        return 'triangle-down-equilateral' if value < 0 else 'triangle-up-equilateral'
    else:  # key == 'RSI':
        if value < 30:
            return 'triangle-down-equilateral'
        elif value > 70:
            return 'triangle-up-equilateral'
    return 'thin_horizontal_rectangle'


def get_arrow_style(key: str, value: float):
    if key != 'EMA20 - SMA50' and 30 < value < 70:
        pass
    return ''


def get_warm_bar(key: str, value: float):
    return ''
    if key == 'EMA20 - SMA50':
        return 'triangle-down-equilateral' if value < 0 else 'triangle-up-equilateral'
    elif key == 'RSI':
        if value < 30:
            return 'triangle-down-equilateral'
        elif value > 70:
            return 'triangle-up-equilateral'
    return ''


def get_float_length_by_key(key):
    if key == 'EMA20 - SMA50':
        return 5
    elif key == 'RSI':
        return 2
    return 4


def get_indicator_value_as_str(key: str, number: float):
    value = '' if number is None else float_to_string(number, get_float_length_by_key(key))
    if key == 'EMA20 - SMA50':
        return value + '€'
    elif key == 'RSI':
        return value + ' points'
    elif key in ['Buy (macd)', 'Sell (macd)']:
        return value + '%'
    return value


def get_arrow_style_gradient_colour(value):
    pass


def get_image(coin_name: str, screen_size: str = ''):
    return coin_name + screen_size + '.png'


def get_route_from_logo(coin_logo: str):
    inverted_logos = dict(map(reversed, get_logos().items()))
    url_coin = blueprint.url_prefix
    if coin_logo in inverted_logos:
        return url_coin + '/' + inverted_logos[coin_logo]
    return '#'
