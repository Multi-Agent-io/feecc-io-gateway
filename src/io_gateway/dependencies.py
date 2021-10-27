from pathlib import Path

from fastapi import HTTPException, status

from .models import AbsolutePath


def get_file(absolute_path: AbsolutePath) -> Path:
    """check if provided file exists"""
    path = absolute_path.absolute_path
    file = Path(path)

    if not file.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File {path} doesn't exist")

    return file
