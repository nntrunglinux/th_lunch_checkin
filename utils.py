from datetime import datetime, timedelta
from constants import *


def convert_to_datetime_and_plus_7_hour(timestamp: str):
    timestamp = datetime.strptime(timestamp, YMDHMS_FORMAT)
    return timestamp + timedelta(hours=7)


def convert_to_str_and_minus_7_hour(timestamp: datetime):
    timestamp = timestamp - timedelta(hours=7)
    timestamp = timestamp.strftime(YMDHMS_FORMAT)
    return timestamp
