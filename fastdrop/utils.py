from fastdrop.config import SECRET_KEY, ALGORITHM
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Any

import jwt
from pwdlib import PasswordHash

password_hasher = PasswordHash.recommended()
def get_datetime_utc() -> datetime:
    return datetime.now(ZoneInfo("UTC")) 

def get_datetime_utc_delta(days=0) -> datetime:
    return datetime.now(ZoneInfo("UTC"))  + timedelta(days=days)

def create_token(data: dict, expire_delta: timedelta):
    expire = datetime.now(ZoneInfo("UTC")) + expire_delta
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(encoded_token: str) -> dict[str, Any]:
    decoded = jwt.decode(encoded_token, SECRET_KEY, [ALGORITHM])
    return decoded

def create_delete_token(data: dict, expire_delta: timedelta = timedelta(days=30)):
    return create_token(data, expire_delta)

def hash_password(plain_password: str) -> str:
    return password_hasher.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hasher.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    return create_token(data, timedelta(weeks=2))