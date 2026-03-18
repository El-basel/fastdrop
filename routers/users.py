from typing import Any

from fastapi import APIRouter

from ..models import UserPublic, FilePublic
from ..dependencies import GetUserDep

router = APIRouter(
    prefix="/user",
    tags=["user"]
)


@router.get("/me")
async def dashboard(user: GetUserDep):
    if not user:
        return {"error": "error"}
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