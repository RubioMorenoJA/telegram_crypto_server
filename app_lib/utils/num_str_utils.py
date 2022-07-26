"""
File that contains number and string utils
"""


def float_to_string(number: float, total_length: int):
    """
    Convert the given number to a string with the given length
    :param number:
    :param total_length:
    :return:
    """
    if number < 0:
        total_length += 1
    int_part = '{0}'.format(int(number))
    float_length = total_length - len(int_part) if total_length - len(int_part) > 0 else 0
    float_part = str(number - int(number)).split('.')[-1][:float_length]
    return int_part + '.' + float_part if len(float_part) > 0 else int_part


def str_to_int(str_number: str):
    number = None
    try:
        number = int(str_number)
    except Exception:
        pass
    finally:
        return number
