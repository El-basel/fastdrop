from datetime import datetime, timezone, timedelta


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc) 

def get_datetime_utc_delta(days=0) -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=days)