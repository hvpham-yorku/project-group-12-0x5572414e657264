"""
Docstring for timeDiffCalculator

"""

from datetime import datetime, timedelta


def time_diff_hhmmss(t1: str, t2: str) -> str:
    """
    Docstring for time_diff_hhmmss

    :param t1: time 1 in time in HH:MM:SS format
    :type t1: str
    :param t2: time 2 in time in HH:MM:SS format
    :type t2: str
    :return: difference in time in HH:MM:SS format
    :rtype: str
    """
    fmt = "%H:%M:%S"
    time1 = datetime.strptime(t1, fmt)
    time2 = datetime.strptime(t2, fmt)

    # Handle crossing midnight
    if time2 < time1:
        time2 += timedelta(days=1)

    diff_seconds = int((time2 - time1).total_seconds())

    hours, remainder = divmod(diff_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


print(time_diff_hhmmss("14:25:00", "15:50:00"))
