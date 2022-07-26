"""
Utils for lists
"""


def update_float_list(old_list: list, pop_elem: float) -> list:
    """
    Deletes the given value pop_elem of the given list
    :param old_list:
    :param pop_elem:
    :return:
    """
    return list(filter(lambda elem: elem if abs(elem-pop_elem) > 1e-5 else None, old_list))


def get_min(check_list: list):
    """
    Returns the minimum in the list
    :param check_list:
    :return:
    """
    if len(check_list) > 0:
        return min(check_list)
    return None


def get_max(check_list):
    """
    Returns the maximum in the list
    :param check_list:
    :return:
    """
    if len(check_list) > 0:
        return max(check_list)
    return None
