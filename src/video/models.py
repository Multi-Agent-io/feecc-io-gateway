import typing as tp
from pydantic import BaseModel


class GenericResponse(BaseModel):
    status: int
    details: str


class StartRecordResponse(GenericResponse):
    record_id: str


class RecordList(GenericResponse):
    ongoing_records: tp.List[tp.Dict[str, tp.Any]]
    ended_records: tp.List[tp.Dict[str, tp.Any]]


class CameraList(GenericResponse):
    cameras: tp.List[tp.Dict[str, tp.Any]]
