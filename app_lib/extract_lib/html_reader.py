"""
HtmlReader definition
"""
import re
import traceback
from bs4 import BeautifulSoup as bs
from app_lib.extract_lib.reader import Reader, parser
from app_lib.log.log import get_log


__logger__ = get_log('html_reader')


class HtmlReader(Reader):
    """
    HtmlReader is used to get cryptocurrency data from WorldCoinIndex webpage
    """
    __NAME = 1
    __LOGO = 2
    __PRICE = 3
    __HIST_DATE = 0
    __HIST_CLOSE = 1
    __HIST_MAX = 2
    __HIST_MIN = 3

    def get_exchange_table(self, html) -> list:
        """
        Extracts data from exchange table
        :param html:
        :return:
        """
        table = []
        if html:
            try:
                soup = bs(html, 'html.parser')
                table = soup.find_all(lambda tag: tag.has_attr('id') and tag['id'] == 'market-table')[0]
                table = self.get_table_rows(table, 'data-symbol', re.compile('[a-zA-Z]+BTC$'))
                table = self.exchange_table(table)
            except Exception as ex:
                __logger__.error('Exception: %s\n%s', ex, traceback.format_exc())
        return table

    def get_table_rows(self, table, attr: str = '', expr: str = '') -> list:
        """
        Extracts rows from the given html table
        :param table: html data table
        :param attr: css attribute for searching
        :param expr: regular expression use to search
        :return: list
        """
        table_rows = []
        if table:
            if len(table) > 0:
                if not attr and not expr:
                    table_rows = table.find_all('tr')
                elif not expr:
                    table_rows = table.find_all(lambda tag: tag.has_attr(attr))
                elif str(type(expr)) == "<class \'re.Pattern\'>":  # expr is regular expression
                    table_rows = table.find_all(lambda tag: tag.has_attr(attr) and expr.match(tag.get(attr)))
        return table_rows

    def exchange_table(self, table) -> list:
        """
        Extracts name, logo and price from the exchange table as list and
        builds and returns the data as list
        :param table:
        :return:
        """
        data = []
        if table:
            try:
                for row in table:
                    rdata = []
                    c_elem = 0
                    for col in row.find_all('td'):
                        if c_elem == self.__NAME:
                            rdata.append(col.text.split('\n')[1])
                        elif c_elem == self.__LOGO:
                            rdata.append(col.text.split('\n')[2].split('/')[0].split(' ')[0])
                        elif c_elem == self.__PRICE:
                            rdata.append(parser(col.text.split('\n')[2]))
                        elif c_elem > self.__PRICE:
                            break
                        c_elem += 1
                    data.append(rdata)
            except Exception as ex:
                __logger__.error('Exception: %s\n%s', ex, traceback.format_exc())
        return data

    def get_historical_table(self, html, limit=None) -> list:
        """
        Extracts and returns historical data from any cryptocurrency. By the moment maximum
        and minimum price within the last month
        :param html:
        :param limit:
        :return:
        """
        table = []
        if html:
            try:
                soup = bs(html, 'html.parser')
                table = soup.find_all(
                    lambda tag: tag.name == 'tbody' and tag.parent.has_attr('id') and tag.parent['id'] == 'myTable'
                )[0]
                table = self.get_table_rows(table)
                table = self.historical_table(table, limit)
            except Exception as ex:
                __logger__.error('Exception: %s\n%s', ex, traceback.format_exc())
        return table

    def historical_table(self, table, limit=None) -> list:
        """
        Extracts date, maximun and minimum from every row
        :param table:
        :param limit:
        :return:
        """
        data = []
        if table:
            if limit and 0 < limit < len(table):
                table = table[0:limit]
            try:
                for row in table:
                    rdata = []
                    c_elem = 0
                    for col in row.find_all('td'):
                        if c_elem == self.__HIST_DATE:
                            rdata.append(col.text)
                        elif c_elem == self.__HIST_CLOSE:
                            rdata.append(parser(col.find_all('span')[1].text))
                        elif c_elem == self.__HIST_MAX:
                            rdata.append(parser(col.find_all('span')[1].text))
                        elif c_elem == self.__HIST_MIN:
                            rdata.append(parser(col.find_all('span')[1].text))
                        elif c_elem > self.__HIST_MIN:
                            break
                        c_elem += 1
                    data.append(rdata)
            except Exception as ex:
                __logger__.error('Exception: %s\n%s', ex, traceback.format_exc())
        return data
