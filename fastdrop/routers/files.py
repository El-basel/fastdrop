import uuid
from typing import Annotated

from fastapi import APIRouter, UploadFile, Body, Form
from fastapi.responses import FileResponse

from fastdrop.models import FilePublic
from fastdrop.dependencies import SessionDep, GetUserDep
from fastdrop.services.files import upload_file, download_file, delete_file

router = APIRouter(
    prefix="/file",
    tags=["file"]
)

@router.post("/", response_model=FilePublic)
async def api_uplode_file(in_file: UploadFile, expire: Annotated[int, Form()], session: SessionDep, user: GetUserDep):
    return await upload_file(in_file, expire, session, user)

@router.get("/{file_id}")
async def api_download_file(file_id: uuid.UUID, session: SessionDep, user: GetUserDep):
    stored_path, mime_type, filename = await download_file(file_id, session, user)
    return FileResponse(
    stored_path,
    media_type=mime_type,
    filename=filename)
    
@router.delete("/{file_id}")
async def api_delete_file(file_id: uuid.UUID, session: SessionDep, user: GetUserDep, deletion_token: Annotated[str, Body()] = "token"):
    await delete_file(file_id, session, user, deletion_token)
    return {"message": "File deleted successfully"}