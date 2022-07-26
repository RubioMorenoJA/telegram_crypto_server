"""
Definition of classes used to manage google drive excels
"""
import math
import os
import traceback
import pandas as pd
from json import loads
from pydrive.auth import GoogleAuth, AuthError, RefreshError
from pydrive.drive import GoogleDrive
from app_lib.utils.files_utils import transform_path, get_absolute_path
from app_lib.log.log import get_log


__logger__ = get_log('drive_api')


class Drive(GoogleDrive):
    """
    Google drive helper
    """

    def __init__(self):
        auth_settings = str(os.getcwd()).split('app_lib')[0] + transform_path(
            '/app_lib/configuration/yaml/settings.yaml')
        __logger__.debug(f'auth_settings: {auth_settings}')
        self.g_auth = GoogleAuth(auth_settings)
        self.check_token()
        super(Drive, self).__init__(self.g_auth)

    def check_token(self):
        """
        Checks if google token is expired, in that case the functions tries to refresh it
        :return:
        """
        self.g_auth.LoadCredentialsFile()
        if self.g_auth.access_token_expired:
            is_refreshed = False
            try:
                self.g_auth.Refresh()
                is_refreshed = True
            except RefreshError as ex:
                __logger__.error('RefreshError: %s\n%s', ex, traceback.format_exc())
            except Exception as ex:
                __logger__.error('Exception: %s\n%s', ex, traceback.format_exc())
            finally:
                if is_refreshed:
                    self.g_auth.SaveCredentialsFile()


class DriveFile:
    """
    Class used to manage google drive files
    """

    file = None
    folder_id = None

    def __init__(self, file_name: str):
        self.drive = Drive()
        self.set_folder_id()
        self.create_file_from_name(file_name)

    def set_folder_id(self):
        path = get_absolute_path('/app_lib/configuration/json/gdrive_folder.json')
        with open(path) as file:
            json_file = loads(file.read())
        if 'folder_id' in json_file:
            self.folder_id = json_file['folder_id']

    def create_file_from_name(self, file_name: str) -> None:
        """
        Creates a file from name to save the data
        :param file_name:
        :return:
        """
        if not self.download_file_from_name(file_name):
            __logger__.debug(f'Unable to download file "{file_name}"')
            if self.upload_file_from_name(file_name):
                __logger__.debug(f'File "{file_name}" created')

    def upload_file_from_name(self, file_name: str) -> bool:
        """
        Tries to upload the file to google drive and returns if success or not
        :param file_name:
        :return:
        """
        uploaded = False
        self.file = self.drive.CreateFile({'parents': [{'id': '{}'.format(self.folder_id)}]})
        try:
            self.file.SetContentFile(file_name)
            self.file.Upload()
            uploaded = True
        except IOError as ex:
            __logger__.error('IOError: %s\n%s', ex, traceback.format_exc())
        except Exception as ex:
            __logger__.error('Exception: %s\n%s', ex, traceback.format_exc())
        return uploaded

    def download_file_from_name(self, file_name: str) -> bool:
        """
        Tries to download and save the file from google drive and returns
        if success or not
        :param file_name:
        :return:
        """
        for file in self.drive.ListFile(
                {'q': "'{}' in parents and trashed=false".format(self.folder_id)}
        ).GetList():
            if file['title'] == file_name:
                self.file = self.drive.CreateFile({'id': file['id']})
                self.file.GetContentFile(file_name)
                return True
        return False

    def set_file(self, file_name: str) -> None:
        """
        Sets content in own file from filename
        :param file_name:
        :return:
        """
        self.file.SetContentFile(file_name)

    def get_file(self) -> str:
        """
        Returns current own file
        :return:
        """
        return self.file

    def upload(self) -> None:
        """
        Tries to upload the file if it exists
        :return:
        """
        if self.file:
            self.file.Upload()


class Cryptocurrencies:
    """
    Class to manage the excel file with cryptocurrency data
    """

    TOTAL_STR_KEY = 'Total Invertido'
    COIN_COLUMN_NAME = 'Crypto'
    EUR_BUY_COLUMN_NAME = 'Compra (€)'
    MIN_PRICE_COLUMN_NAME = 'Minimo'
    MAX_PRICE_COLUMN_NAME = 'Maximo'
    PRICE_COLUMN_NAME = 'Precio'
    UNIT_QUANTITY_COLUMN_NAME = 'Cantidad (Unidad)'
    EUR_QUANTITY_COLUMN_NAME = 'Cantidad (€)'
    TAX_QUANTITY_COLUMN_NAME = 'Comisión (F)'
    EUR_PROFIT_COLUMN_NAME = 'Beneficio'
    EUR_PERCENT_PROFIT_COLUMN_NAME = 'Beneficio %'
    EUR_TOTAL_ROW = 7

    def __init__(self, file_name: str):
        self.crypto = pd.read_excel(file_name, usecols='A:M', nrows=35)
        self.styler = None
        self.__get_eur_total_row()

    def __get_eur_total_row(self) -> None:
        """
        Save the row number of 'TOTAL_STR_KEY'
        :return:
        """
        self.EUR_TOTAL_ROW = self.match_crypto_row(self.TOTAL_STR_KEY)

    def set_value(self, row: int, column_name: str, value: float) -> None:
        """
        Sets new value given the row number and column name
        :param row:
        :param column_name:
        :param value:
        :return:
        """
        self.crypto[column_name].iloc[row] = value

    def get_value(self, row: int, column_name: str):
        """
        Returns the value of cell given row number and column name
        :param row:
        :param column_name:
        :return:
        """
        return self.crypto[column_name].iloc[row]

    def get_excel_copy(self) -> pd.DataFrame:
        """
        Returns a copy of the current pandas dataframe with coin values
        :return:
        """
        return self.crypto.copy()

    def get_crypto_names(self) -> pd.DataFrame:
        """
        Returns the logo of every cryptocurrency in own crypto dataframe
        :return:
        """
        return self.crypto[self.COIN_COLUMN_NAME]

    def match_crypto_row(self, row_value):
        """
        Returns the index row where cryptocurrency logo is placed if it exists
        :param row_value:
        :return:
        """
        for index, value in zip(range(self.crypto[self.COIN_COLUMN_NAME].shape[0]), self.crypto[self.COIN_COLUMN_NAME]):
            if value == row_value:
                return index
        return None

    def get_total_eur_quantity(self) -> float:
        """
        Calculates the total amount of euros
        :return:
        """
        return self.crypto.loc[:self.EUR_TOTAL_ROW-1, self.EUR_QUANTITY_COLUMN_NAME].sum()

    def get_total_eur_profit(self) -> float:
        """
        Calculates the total amount of profits
        :return:
        """
        return self.crypto.loc[:self.EUR_TOTAL_ROW-1, self.EUR_PROFIT_COLUMN_NAME].sum()

    def get_total_eur_invested(self) -> float:
        """
        Calculates the total amount of the investment
        :return:
        """
        return self.crypto.loc[:self.EUR_TOTAL_ROW-1, self.EUR_BUY_COLUMN_NAME].sum()

    def highlight_by_value(self, column) -> None:
        """
        Highlight the given column painting in red or green every cell depending on the
        value: green if value is greater than zero red otherwise
        :param column:
        :return:
        """
        def highlight(value):
            if 'str' in str(type(value)) or math.isnan(value):
                return ''
            background_colour = '#64FF64' if value >= 0 else '#FF7878'
            return 'background-color: %s' % background_colour
        if column in self.crypto:
            self.crypto.style.applymap(highlight, subset=[column])

    def apply_styles(self) -> None:
        """
        Applies several styles and highlight to own dataframe
        :return:
        """
        def highlight_profit(value):
            if 'str' in str(type(value)) or math.isnan(value):
                return ''
            background_colour = '#64FF64' if value >= 0 else '#FF7878'
            return 'background-color: %s' % background_colour

        def highlight_price(column_values, comparative_values):
            def f(x):
                y = 155 * x + 100
                y = 255 if y > 255 else 100 if y < 100 else y
                return y
            return [
                'background-color: ' + "#" + ''.join("{:02x}".format(int(elem))
                                                     for elem in [64, f(value), f(1-value)])
                if not math.isnan(value) else '' for value in comparative_values
            ]

        def highlight_rows(rows):
            return [
                'background-color: #DCDCDC' if row_n % 2 == 0 else '' for row_n, row_v in zip(range(len(rows)), rows)
            ]

        def highlight_profit_percent(column):
            background_colour = 'background-color: {}'
            return [
                background_colour.format('#00FF00') if value >= 15
                else background_colour.format('#FFFF00') if value >= 10
                else '' for value in column
            ]

        comp_values = (self.crypto[self.PRICE_COLUMN_NAME] - self.crypto[self.MIN_PRICE_COLUMN_NAME]) \
                      / (self.crypto[self.MAX_PRICE_COLUMN_NAME] - self.crypto[self.MIN_PRICE_COLUMN_NAME])
        self.crypto = self.crypto.style.\
            apply(highlight_rows, axis=0).\
            applymap(highlight_profit, subset=[self.EUR_PROFIT_COLUMN_NAME]).\
            apply(highlight_price, subset=[self.PRICE_COLUMN_NAME], **{'comparative_values': comp_values}).\
            apply(highlight_profit_percent, subset=[self.EUR_PERCENT_PROFIT_COLUMN_NAME])

    def wide_cells(self, width=30) -> None:
        """
        Sets a width in every cell. It does not work
        :param width:
        :return:
        """
        self.crypto = self.crypto.style.set_table_styles(
            [
                dict(selector="td",
                     props=[('width', f'{width}px')]
                     )
            ]
        )

    def save_as_excel(self, file_name) -> None:
        """
        Saves the own cryptocurrencies dataframe to an excel file
        :param file_name:
        :return:
        """
        self.crypto.to_excel(file_name, index=False)
