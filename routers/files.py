import shutil
import os
import uuid
from typing import Annotated
from zoneinfo import ZoneInfo

from sqlmodel import select

from fastapi import APIRouter, UploadFile, HTTPException, Body
from fastapi.responses import FileResponse
from fastapi.encoders import jsonable_encoder
import jwt
from pydantic import ValidationError

from ..utils import get_datetime_utc, get_datetime_utc_delta, create_delete_token, decode_token
from ..models import File, FilePublic, DeletionToken
from ..dependencies import SessionDep, GetUserDep
from ..config import UPLOAD_BASE_DIR

router = APIRouter(
    prefix="/file",
    tags=["file"]
)

@router.post("/", response_model=FilePublic)
async def uplode_file(in_file: UploadFile, session: SessionDep, user: GetUserDep):
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

@router.get("/{file_id}")
async def download_file(file_id: uuid.UUID, session: SessionDep, user: GetUserDep):
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
    
@router.delete("/{file_id}")
async def delete_file(file_id: uuid.UUID, deletion_token: Annotated[str, Body()], session: SessionDep, user: GetUserDep):
    file = session.exec(select(File).where(File.id == file_id)).one_or_none()
    if file is None :
        raise HTTPException(status_code=404, detail="File no found")
    
    try:
        deletion_token_decode: DeletionToken = DeletionToken(**decode_token(deletion_token))
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=410, detail="Deletion Token Expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid Token")
    except ValidationError:  # From Pydantic if payload doesn't match DeletionToken
        raise HTTPException(status_code=400, detail="Malformed token")
    if deletion_token_decode.file_id != file_id:
        raise HTTPException(status_code=400, detail="Invalid Token")
    file.is_active = False
    file.is_deleted = True
    session.add(file)
    session.commit()
    return {"message": "File deleted successfully"}