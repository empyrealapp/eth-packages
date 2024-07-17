import re
from datetime import datetime

import pytz


def convert_datetime_to_iso_8601(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def load_datetime_string(dt: str | int) -> datetime:
    if isinstance(dt, int):
        return datetime.fromtimestamp(int(dt), tz=pytz.UTC)
    elif re.fullmatch(r"^0x[0-9a-f]+$", dt):
        return datetime.fromtimestamp(int(dt, 16), tz=pytz.UTC)
    elif dt.replace(".", "", 1).isdigit():
        return datetime.fromtimestamp(int(dt), tz=pytz.UTC)
    return datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=pytz.UTC)
