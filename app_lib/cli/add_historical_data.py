"""
CLI module
"""
import click
from app_lib.extract_lib.historical_data_extractor import historical_data_extractor
from app_lib.utils.num_str_utils import str_to_int


@click.command(name='add_historical_data')
@click.option('--coin_name', default=None, help='Name of coin to insert. Ex: bitcoin.')
@click.option('--date_from', default=None, help='Initial date to get and insert. Ex: 20210101.')
@click.option('--date_to', default=None, help='Final date to get and insert. Ex: 20210131.')
def add_historical_data(coin_name: str = None, date_from: str = None, date_to: str = None) -> None:
    """
    Adds historical data extracted from the internet
    :param coin_name:
    :param date_from:
    :param date_to:
    """
    coins_name = None if not coin_name else [coin_name]
    date_from = str_to_int(date_from)
    date_to = str_to_int(date_to)
    hist_data_added = historical_data_extractor(coins_name=coins_name, date_init=date_from, date_end=date_to)
    click.echo(hist_data_added)


if __name__ == '__main__':
    add_historical_data()
