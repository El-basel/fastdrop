from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo


def get_datetime_utc() -> datetime:
    return datetime.now(ZoneInfo("UTC")) 

def get_datetime_utc_delta(days=0) -> datetime:
    return datetime.now(ZoneInfo("UTC"))  + timedelta(days=days)