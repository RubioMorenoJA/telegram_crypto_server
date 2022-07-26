"""
File where we compute different moving averages
"""
import numpy as np


def exponential_moving_average(data: np.array, length: int = None):
    """
    Function used to compute the exponential moving average from data
    :param data: 2D array with dates and data
    :param length:
    :return:
    """
    if not length:
        length = 20 if 20 <= data.shape[0] else data.shape[0]
    scaling_factors = get_exponential_scaling_factors(length)
    exp_ma = np.array(
        [weighted_average(data[elem:elem+length, 1], scaling_factors) for elem in range(data.shape[0]-length+1)]
    )
    return np.array([data[:exp_ma.shape[0], 0], exp_ma]).transpose()


def simple_moving_average(data: np.array, length: int = None):
    """
    Function used to compute the simple moving average from data
    :param data:
    :param length:
    :return:
    """
    if not length:
        length = 50 if 50 < data.shape[0] else data.shape[0]
    sim_ma = np.array(
        [data[elem:elem+length, 1].mean() for elem in range(data.shape[0]-length+1)]
    )
    return np.array([data[:sim_ma.shape[0], 0], sim_ma]).transpose()


def weighted_average(feature1: np.array, feature2: np.array):
    """
    Function that computes the weighted average
    :param feature1: array with data
    :param feature2: array with weights
    :return:
    """
    if feature1.shape[0] > 0:
        return np.dot(feature1, feature2) / feature2.sum()
    return .0


def get_exponential_scaling_factors(length):
    """
    Calculates scaling exponential factors
    :param length:
    :return:
    """
    alpha = 2 / length
    return np.power(1. - alpha, np.arange(length))


def get_linear_scaling_factors(length):
    """
    Calculates scaling exponential factors
    :param length:
    :return:
    """
    alpha = 2 / length
    return np.array([1.-n*alpha for n in range(length)])
