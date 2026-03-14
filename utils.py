from .config import SECRET_KEY, ALGORITHM
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Any

import jwt


def get_datetime_utc() -> datetime:
    return datetime.now(ZoneInfo("UTC")) 

def get_datetime_utc_delta(days=0) -> datetime:
    return datetime.now(ZoneInfo("UTC"))  + timedelta(days=days)

def create_delete_token(data: dict, expire_delta: timedelta= timedelta(days=30)):
    to_encode = data.copy()
    expire = datetime.now(ZoneInfo("UTC")) + expire_delta
    to_encode.update({"exp": expire})
    deletion_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return deletion_token

def decode_token(encoded_token: str) -> dict[str, Any]:
    decoded = jwt.decode(encoded_token, SECRET_KEY, [ALGORITHM])
    return decoded