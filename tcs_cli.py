"""
CLI main module
"""
import click
from app_lib.cli.add_historical_data import add_historical_data
from app_lib.cli.load_data_from_html_file import load_data_from_html_file


@click.group(name='tcs')
def tcs_cli_command() -> None:
    """
    Run telegram-crypto-server command line interface
    """


def tcs_entrypoint() -> None:
    """
    Add the cli modules
    """
    tcs_cli_command.add_command(add_historical_data)
    tcs_cli_command.add_command(load_data_from_html_file)
    tcs_cli_command()


if __name__ == '__main__':
    tcs_entrypoint()
