import os

from fastapi import HTTPException, status


def check_presence(path: str) -> None:
    """check if provided file exists"""
    if not os.path.exists(path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File {path} doesn't exist")
