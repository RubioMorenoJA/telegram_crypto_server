"""
File containing functions to transform dates
"""
import datetime


def historical_coin_date_to_int(str_date: str):
    """
    Transform date like "Jan 2, 2019" in "20190102"
    :param str_date:
    :return:
    """
    date = datetime.datetime.strptime(str_date, "%b %d, %Y")
    return date.strftime("%Y%m%d")


def float_coin_date_to_str(float_date, str_format_from: str, str_format_to: str):
    if isinstance(float_date, list):
        return list(map(lambda item: float_coin_date_to_str(item, str_format_from, str_format_to), float_date))
    elif isinstance(float_date, float) or isinstance(float_date, int):
        date = datetime.datetime.strptime(str(int(float_date)), str_format_from)
        return date.strftime(str_format_to)
    return None


def back_date_n_months(back_date, n_months: int):
    """
    Transform the given date going back the given number of months
    :param back_date:
    :param n_months:
    :return:
    """
    if not (
        isinstance(back_date, datetime.datetime) or
        isinstance(back_date, datetime.date)
    ):
        return back_date
    month_diff = back_date.month - n_months
    if month_diff > 0:
        new_date = back_date.replace(month=month_diff)
    else:
        month = month_diff % 12 + 1
        year = back_date.year - abs(month_diff // 12)
        # if month != 1:
        #     year -= 1
        new_date = back_date.replace(year=year, month=month)
    return new_date


def back_date_n_days(back_date, n_days: int):
    """
    Transform the given date going back the given number of days
    :param back_date:
    :param n_days:
    :return:
    """
    if not (
        isinstance(back_date, datetime.datetime) or
        isinstance(back_date, datetime.date)
    ):
        return back_date
    return back_date - datetime.timedelta(days=n_days)
