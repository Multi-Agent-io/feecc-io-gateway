from pydantic import BaseModel


class GenericResponse(BaseModel):
    status: int
    details: str


class PublishFileRequest(BaseModel):
    filename: str
    background_processing: bool = True


class IpfsPublishResponse(GenericResponse):
    ipfs_cid: str
    ipfs_link: str
