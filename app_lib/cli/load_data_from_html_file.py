"""
CLI module
"""
import traceback
import click
from app_lib.extract_lib.historical_data_extractor import load_historical_data_from_html
from app_lib.DDBB.sqlite.models import get_model


@click.command(name='load_data_from_html_file')
@click.option('--coin_logo', default=None, help='Logo of coin to insert. Ex: BTC.')
@click.option('--file_path', default=None, help='Filename and path where data is stored.')
@click.option('--price_transform', is_flag=True, default=False, help='Option to transform the price from USD to EUR.')
def load_data_from_html_file(coin_logo: str = None, file_path: str = None, price_transform: bool = False):
    """
    Loads and save coin_logo data in the database from file_path
    :param coin_logo:
    :param file_path:
    :param price_transform:
    """
    db_object = get_model(coin_logo)
    if db_object:
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    load_historical_data_from_html(db_object, file.read(), price_transform)
                return_str = f'Coin {coin_logo} data in {file_path} file was loaded successfully'
            except IOError as ex:
                return_str = f'Exception:\n{ex}\n{traceback.format_exc()}\n'
        else:
            return_str = f'File {file_path} does not exist.'
    else:
        return_str = f'Coin {coin_logo} does not have a database entry.'
    click.echo(return_str)


if __name__ == '__main__':
    load_data_from_html_file(coin_logo=None, file_path=None, price_transform=None)
