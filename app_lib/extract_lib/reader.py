"""
General Reader definition
"""


def parser(string) -> float:
    """
    Method used to parse big numbers as strings separated by commas
    :param string:
    :return:
    """
    if ',' in string:
        m_number = string.split(',')
        maximum = len(m_number)
        number = 0.0
        for item, exp in zip(m_number, range(maximum)):
            number += float(item) * pow(10, 3 * (maximum - exp - 1))
        return number
    return float(string)


class Reader:
    """
    Class used to inherit from other readers allowing them to use several methods
    to show the status of reading
    """
    __NOINIT = -1
    __BURIED = 0
    __RUNNING = 1
    __COMPLETE = 2

    def __init__(self, title: str = ''):
        self.__title = title
        self.operation = -1

    def set_operation(self, operation: int) -> None:
        """
        Sets operation status
        :param operation:
        :return:
        """
        self.operation = operation

    def get_operation(self) -> int:
        """
        Returns operation status
        :return:
        """
        return self.operation

    def set_title(self, title: str) -> None:
        """
        Sets title or name for a reader
        :param title:
        :return:
        """
        self.__title = title

    def get_title(self) -> str:
        """
        Returns own title or name from a reader
        :return:
        """
        return self.__title
