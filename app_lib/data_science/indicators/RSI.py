"""
File where we compute relative strength index (RSI)
"""
import numpy as np


def relative_strength_index(data: np.array, length: int = None):
    """
    Calculates RSI from data
    :param data: 2D array with dates and data
    :param length:
    :return:
    """
    if not length:
        length = 14 if 14 < data.shape[0]-1 else data.shape[0]-1
    averages = np.divide(data[:length, 1], data[1:length+1, 1])
    positive_avg = np.array(list(filter(lambda x: x > 1, averages))).mean() - 1
    negative_avg = np.array(list(filter(lambda x: x < 1, averages))).mean() - 1
    if negative_avg == 0:
        return 100
    return 100 - 100 / (1 - positive_avg/negative_avg)


