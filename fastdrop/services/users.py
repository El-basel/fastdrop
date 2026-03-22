from typing import Any

from fastapi import HTTPException

from fastdrop.models import User, FilePublic
async def dashboard(user: User | None):
    if not user:
        raise HTTPException(status_code=403, detail="Please login first")
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