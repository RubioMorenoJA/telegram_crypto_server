"""
Used to compute plot settings
"""
import numpy as np
from app_lib.utils.num_str_utils import float_to_string


def get_x_ticks_and_labels(labels_array: np.array, quantity: int) -> tuple:
    """
    Given an array of data the function selects the quantity number of array elements which will be
    the x labels for a plot
    :param labels_array:
    :param quantity:
    :return:
    """
    labels_length = labels_array.shape[0]-1
    quantity = 2 if quantity == 1 else quantity
    x_ticks = np.linspace(0, 1, quantity)
    x_labels = [labels_array[round(item*labels_length/(quantity-1))] for item in range(quantity)]
    return x_ticks, x_labels


def get_labels_from_y_ticks(y_ticks: np.array):
    """
    Given the y ticks in a plot we transform them into a short scientific string
    :param y_ticks:
    :return:
    """
    def delete_non_sense_zeros(str_number: str):
        str_number_split = str_number.split('.')
        last_zero = -1
        while str_number_split[1][last_zero] == '0':
            last_zero -= 1
        return str_number_split[0] + '.' + str_number_split[1][:last_zero+1]

    def transform(tick: float):
        if abs(tick) >= 1e3:
            tick_elems = "{:.2E}".format(tick).split('E')
            scale = int(tick_elems[1]) - 3
            new_int_tick = float(tick_elems[0]) * pow(10, scale)
            new_str_tick = float_to_string(new_int_tick, scale + 1 if scale > 0 else 2) + 'k'
        elif abs(tick) < 1:
            tick_elems = "{:.2E}".format(tick).split('E')
            scale = abs(int(tick_elems[1]) - 2)
            new_str_tick = str("{0:"+".{scale}f".format(scale=scale)+"}").format(tick)
            if new_str_tick == '0.00':
                new_str_tick = '0'
            else:
                new_str_tick = delete_non_sense_zeros(new_str_tick)
        else:
            new_str_tick = float_to_string(tick, 3)
        return new_str_tick
    return list(map(transform, y_ticks))


def get_saved_name_by_size(filename: str, size: tuple):
    """
    Adds the size in tuple, multiplied by 100, to the filename
    :param filename:
    :param size:
    :return:
    """
    name_list = filename.split('.')
    sizes = (int(round(size[0] * 100)), int(round(size[1] * 100)))
    return str(name_list[0] + '_{0}_{1}'.format(*sizes) if sizes[0] != 640 else filename) + '.png'
