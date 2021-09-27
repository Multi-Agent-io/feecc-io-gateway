from pydantic import BaseModel
import typing as tp


class GenericResponse(BaseModel):
    status: int
    details: str


class PrintImageRequest(BaseModel):
    annotation: tp.Optional[str] = None
