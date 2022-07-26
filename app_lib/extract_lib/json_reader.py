"""
JsonReader definition
"""
from app_lib.log.log import get_log
from app_lib.extract_lib.reader import Reader, parser


__logger__ = get_log('json_reader')


class JsonReader(Reader):
    """
    JsonReader is a class used to transform the data got from Coinbase
    """
    currencies = {
        'bitcoin': 'BTC',
        'ethereum': 'ETH',
        'litecoin': 'LTC'
    }

    @staticmethod
    def read_json_data(json_data, key='data') -> dict:
        """
        Reads json and gets the 'key' key data
        :param json_data:
        :param key:
        :return:
        """
        data = {}
        if json_data:
            data = json_data[key]
        return data

    @staticmethod
    def get_row_data(data) -> dict:
        """
        Returns a dictionary
        :param data:
        :return:
        """
        row_data = {}
        if data and 'currency' in data and 'amount' in data:
            row_data = {
                'currency': data['currency'],
                'logo': data['currency'],
                'amount': parser(data['amount'])
            }
        return row_data

    @staticmethod
    def get_amount(data, key='amount') -> str:
        """
        Returns the 'key' value in data
        :param data:
        :param key:
        :return:
        """
        amount = ''
        if data and key in data:
            amount = data[key]
        return amount

    def get_currencies(self) -> dict:
        """
        Returns self currencies
        :return:
        """
        return self.currencies

    def get_value(self, key) -> str:
        """
        Returns the 'key' value in self currencies
        :param key:
        :return:
        """
        if key in self.currencies:
            return self.currencies[key]
        return ''
