from datetime import datetime
import time


def to_datetime(seconds: float | None = None) -> datetime:
    now = time.localtime(seconds)
    return datetime(
        now.tm_year,
        now.tm_mon,
        now.tm_mday,
        now.tm_hour,
        now.tm_min,
        now.tm_sec,
        0,
    )
