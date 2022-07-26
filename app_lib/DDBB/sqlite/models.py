"""
Different models to use, each model has its own table in database
"""
from app_lib.DDBB.sqlite.connection import DataBase


def get_model(model_name: str):
    """
    Given a model name this function returns the selected model
    :param model_name:
    :return:
    """
    model = None
    if model_name == 'BTC':
        model = BTC()
    elif model_name == 'ETH':
        model = ETH()
    elif model_name == 'ADA':
        model = ADA()
    elif model_name == 'TRX':
        model = TRX()
    elif model_name == 'XLM':
        model = XLM()
    return model


class BTC(DataBase):
    """
    Class to manage BTC table
    """

    def __init__(self):
        super().__init__()
        self.table_name = "BTC"
        if not self.check_if_table_exists():
            self.create_table()


class ETH(DataBase):
    """
    Class to manage ETH table
    """

    def __init__(self):
        super().__init__()
        self.table_name = "ETH"
        if not self.check_if_table_exists():
            self.create_table()


class TRX(DataBase):
    """
    Class to manage TRX table
    """

    def __init__(self):
        super().__init__()
        self.table_name = "TRX"
        if not self.check_if_table_exists():
            self.create_table()


class ADA(DataBase):
    """
    Class to manage ADA table
    """

    def __init__(self):
        super().__init__()
        self.table_name = "ADA"
        if not self.check_if_table_exists():
            self.create_table()


class XLM(DataBase):
    """
    Class to manage XLM table
    """

    def __init__(self):
        super().__init__()
        self.table_name = "XLM"
        if not self.check_if_table_exists():
            self.create_table()
