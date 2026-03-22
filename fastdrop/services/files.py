import shutil
import os
import uuid
from zoneinfo import ZoneInfo

from fastapi import UploadFile, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlmodel import Session
import jwt
from pydantic import ValidationError

from fastdrop.models import User, FilePublic, File, DeletionToken
from fastdrop.utils import get_datetime_utc, get_datetime_utc_delta, create_delete_token, decode_token
from fastdrop.config import UPLOAD_BASE_DIR

def create_file_record(
        file: UploadFile,
        expire: int, 
        user: User | None, 
        session: Session) -> File:
    if not user:
        expire = 30
    if file.filename is not None:
        filename, extention = os.path.splitext(file.filename)
    else:
        filename = ""
        extention = ""
    file_record = File(
        name=filename, 
        extension=extention, 
        mime_type=file.content_type or "type/unknown",  
        expires_at=get_datetime_utc_delta(expire if expire > 0 else 1),
        user=user
        )
    session.add(file_record)
    session.flush()
    return file_record

async def upload_file(in_file: UploadFile, expire: int, session: Session, user: User | None):
    file = create_file_record(in_file, expire, user, session)
    uploaded_at = get_datetime_utc()
    
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


async def download_file(file_id: uuid.UUID, session: Session, user: User | None):
    file = session.get(File, file_id)
    if file is None :
        raise HTTPException(status_code=404, detail="File no found")
    
    # As we don't delete the file from the DB (just make is_deleted=True)
    # There is a possibility for the developer to delete it from the upload directory
    # but didn't mark it as deleted in DB which will execute the operation normally
    # This would raise exception as the file doesn't exist in the uploads directory (which happened in testing)
    # Note that normally this should never happen as normal users can't remove files form upload/
    stored_path = UPLOAD_BASE_DIR.absolute()/file.stored_path
    if not stored_path.exists():
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
    filename = f"{file.name}{file.extension}"
    return stored_path, file.mime_type, filename

async def delete_file(file_id: uuid.UUID, session: Session, user: User | None, deletion_token: str):
    file = session.get(File, file_id)
    if file is None :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File no found")
    
    if not user:
        try:
            deletion_token_decode: DeletionToken = DeletionToken(**decode_token(deletion_token))
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_410_GONE, detail="Deletion Token Expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Token")
        except ValidationError:  # From Pydantic if payload doesn't match DeletionToken
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Malformed token")
        if deletion_token_decode.file_id != file_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Token")
    else:
        if file.uploaded_by != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid File Ownership")
    file.is_active = False
    file.is_deleted = True
    session.add(file)
    session.commit()