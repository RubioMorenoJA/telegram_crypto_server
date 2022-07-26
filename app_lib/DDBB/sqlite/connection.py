"""
SQLite managing class definition
"""
import sqlite3
import os
import traceback
from sqlite3 import Error, DatabaseError
from app_lib.utils.files_utils import transform_path


class DataBase:
    """
    Main class to manage SQLite database
    """

    insert_query = "INSERT INTO {table_name} VALUES (?, ? ,? ,?)"
    table_name = ''

    def __init__(self):
        db_location = str(os.getcwd()).split('app_lib')[0] + transform_path('/app_lib/DDBB/sqlite/crypto_database')
        self.connection = sqlite3.connect(db_location)
        self.cursor = self.connection.cursor()

    def close(self) -> None:
        """
        Close the current open connection
        :return:
        """
        self.connection.close()

    def create_table(self) -> None:
        """
        Create table if it does not exist
        :return:
        """
        self.cursor.execute(
            f"CREATE TABLE {self.table_name} (DATE INTEGER, CLOSE REAL, MAXIMUM REAL, MINIMUM REAL)"
        )

    def check_if_table_exists(self) -> bool:
        """
        Checks if selected table already exists
        :return:
        """
        self.cursor.execute(
            f"SELECT name FROM sqlite_master WHERE name == '{self.table_name}'"
        )
        db_result = self.cursor.fetchone()
        if db_result and self.table_name in db_result:
            return True
        return False

    def set_array_data(self, tuples_array: list) -> None:
        """
        Insert many rows into the database
        :param tuples_array:
        :return:
        """
        self.cursor.executemany(
            self.insert_query.format(table_name=self.table_name),
            tuples_array
        )
        self.connection.commit()

    def set_data(self, tuple_data: tuple) -> None:
        """
        Insert a row into the database
        :param tuple_data:
        :return:
        """
        self.cursor.execute(
            self.insert_query.format(table_name=self.table_name),
            tuple_data
        )
        self.connection.commit()

    def get_data(self, date_init: int = None, date_end: int = None, select_columns: str = '*'):
        """
        Search and return data between given dates
        :param date_init: integer with YYYYMMDD form
        :param date_end: integer with YYYYMMDD form
        :param select_columns: columns to select from database
        :return:
        """
        get_query = f"SELECT {select_columns} FROM {self.table_name}"
        if date_init or date_end:
            get_query = get_query + " WHERE "
            if date_init:
                get_query = get_query + f"date >= {date_init}"
            if date_end:
                if date_init:
                    get_query = get_query + " AND "
                get_query = get_query + f"date <= {date_end}"
        get_query += " ORDER BY DATE DESC"
        self.cursor.execute(get_query)
        return self.cursor.fetchall()

    def get_close_prices(self, date_init: int = None, date_end: int = None):
        return_data = []
        try:
            return_data = self.get_data(
                date_init=date_init, date_end=date_end, select_columns='DATE, CLOSE'
            )
        except Error as ex:
            print('%s\n%s', ex, traceback.format_exc())
        except Exception as ex:
            print('%s\n%s', ex, traceback.format_exc())
        finally:
            return return_data
