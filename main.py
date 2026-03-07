import shutil
import os
import uuid
from pathlib import Path
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from typing import Annotated
from zoneinfo import ZoneInfo
from datetime import datetime

from sqlmodel import SQLModel, create_engine, Session, select

from fastapi import FastAPI, UploadFile, Depends, HTTPException, Response, status
from fastapi.responses import FileResponse
from fastapi.encoders import jsonable_encoder
import jwt
from jwt import InvalidTokenError

from .utils import *
from .models import *

UPLOAD_BASE_DIR = Path("uploads")
UPLOAD_BASE_DIR.mkdir(exist_ok=True)
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "")
engine = create_engine(DATABASE_URL, echo=False)
SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

def create_db_and_tables():
    # SQLModel.metadata.drop_all(engine)
    print("Creating Database and tables")
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting the app")
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

def get_session():
    with Session(engine) as session:
        yield session

def create_delete_token(data: dict, expire_delta: timedelta= timedelta(days=30)):
    to_encode = data.copy()
    expire = datetime.now(ZoneInfo("UTC")) + expire_delta
    to_encode.update({"exp": expire})
    deletion_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return deletion_token

SessionDep = Annotated[Session, Depends(get_session)]
@app.get("/")
async def hello_world():
    return {"response": "Hello world"}


@app.post("/file/", response_model=FilePublic)
async def uplode_file(in_file: UploadFile, session: SessionDep):
    if in_file.filename is not None:
        filename, extention = os.path.splitext(in_file.filename)
    else:
        filename = ""
        extention = ""
    uploaded_at = get_datetime_utc()
    file = File(
        name=filename, 
        extension=extention, 
        mime_type=in_file.content_type or "type/unknown",  
        expires_at=get_datetime_utc_delta(30))
    
    session.add(file)
    session.flush()
    
    upload_dir = UPLOAD_BASE_DIR/ f"{uploaded_at.year}_{uploaded_at.month:02d}"
    upload_dir.mkdir(exist_ok=True)
    file_path = upload_dir / f"{file.id}{file.extension}"
    try:
        with open(file_path, "wb+") as out_file:
            shutil.copyfileobj(in_file.file, out_file)
        file.size = os.path.getsize(file_path)
        
        session.commit()
        session.refresh(file)
        encoded_file_id = jsonable_encoder(file.id)
        deletion_token = create_delete_token({"file_id": encoded_file_id, "action": "delete"})
        file = FilePublic(**file.model_dump(), deletion_token=deletion_token)
        return file
    except Exception as e:
        print("Exception: ", e)
        session.rollback()
        if file_path.exists():
            os.remove(file_path)
        raise

@app.get("/file/{file_id}")
async def download_file(file_id: uuid.UUID, session: SessionDep):
    file = session.exec(select(File).where(File.id == file_id)).one_or_none()
    if file is None :
        raise HTTPException(status_code=404, detail="File no found")
    
    expiration_date_aware = file.expires_at.replace(tzinfo=ZoneInfo("UTC"))
    if expiration_date_aware < get_datetime_utc() or not file.is_active :
        if expiration_date_aware < get_datetime_utc() or file.is_active:
            file.is_active = False
            session.add(file)
            session.commit()
        raise HTTPException(status_code=410, detail="Link Expired")
    file.download_count += 1
    session.add(file)
    session.commit()
    return FileResponse(
    UPLOAD_BASE_DIR.absolute()/file.stored_path,
    media_type=file.mime_type,
    filename=f"{file.name}{file.extension}")
    