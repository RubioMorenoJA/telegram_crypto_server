"""
DataSeeker definition
"""
import traceback
import requests
from app_lib.log.log import get_log


__logger__ = get_log('data_seeker')


class DataSeeker:
    """
    DataSeeker is a class used to get the data from internet given the URL
    """
    __OK = 200

    def __init__(self, url):
        """
        Constructor of DataSeeker
        :param url: url where data is seeked
        """
        self.url = url

    def get_html_data(self) -> str:
        """
        Returns data from url as html if it is possible
        :return:
        """
        content = ''
        try:
            response = requests.get(self.url)
            if response.status_code == self.__OK:
                content = response.content
            else:
                __logger__.debug('Error in response: status code %s', response.status_code)
        except ConnectionError as ex:
            __logger__.error('ConnectionError: %s\n%s', ex, traceback.format_exc())
        except Exception as ex:
            __logger__.error('Exception: %s\n%s', ex, traceback.format_exc())
        return content

    def get_json_data(self) -> dict:
        """
        Returns data from url as dictionary (json) if it
        is possible
        :return:
        """
        content = {}
        try:
            response = requests.get(self.url)
            if response.status_code == self.__OK:
                content = response.json()
            else:
                __logger__.debug('Error in response: status code %s', response.status_code)
        except ConnectionError as ex:
            __logger__.error('ConnectionError: %s\n%s', ex, traceback.format_exc())
        except Exception as ex:
            __logger__.error('Exception: %s\n%s', ex, traceback.format_exc())
        return content
