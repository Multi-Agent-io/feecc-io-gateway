from pydantic import BaseModel


class GenericResponse(BaseModel):
    status: int
    details: str


class IpfsPublishResponse(GenericResponse):
    ipfs_cid: str
    ipfs_link: str


class AbsolutePath(BaseModel):
    absolute_path: str
