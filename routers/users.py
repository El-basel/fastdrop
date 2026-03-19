from typing import Any

from fastapi import APIRouter, HTTPException

from ..models import User, FilePublic
from ..dependencies import GetUserDep

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

async def dashboard(user: User | None):
    if not user:
        return HTTPException(status_code=403, detail="Please login first")
    files = user.files
    response: dict[str, Any] = {"name": user.full_name}
    response.update({"files": []})
    if files:
        uploaded_files: list[FilePublic] = list()
        for file in files:
            if not file.is_deleted:
                uploaded_files.append(FilePublic(**file.model_dump()))
        response["files"] = uploaded_files
    return response
@router.get("/me")
async def api_dashboard(user: GetUserDep):
    return await dashboard(user)