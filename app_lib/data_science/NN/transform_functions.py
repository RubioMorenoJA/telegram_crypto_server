"""
Module containing transform functions to scale model data
"""
import numpy as np


def sigmoid(x: float) -> float:
    """
    Calculates and returns sigmoid image of x
    :param x:
    :return:
    """
    return 1 / (1 + np.exp(-x))
