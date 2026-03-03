import shutil
import os
from pathlib import Path
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from typing import Annotated

from sqlmodel import SQLModel, create_engine, Session

from fastapi import FastAPI, UploadFile, Depends

from .utils import *
from .models import *

UPLOAD_BASE_DIR = Path("uploads")
UPLOAD_BASE_DIR.mkdir(exist_ok=True)
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "")
engine = create_engine(DATABASE_URL, echo=True)

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
        return file
    except Exception as e:
        print("Exception: ", e)
        session.rollback()
        if file_path.exists():
            os.remove(file_path)
        raise