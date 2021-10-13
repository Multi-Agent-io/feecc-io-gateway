import os
import typing as tp

from fastapi import APIRouter, File, Form, UploadFile, status
from loguru import logger

from . import ipfs, pinata
from .models import GenericResponse, IpfsPublishResponse
from .utils import check_presence
from ..shared.config import config

router = APIRouter()


@router.post("/pinata", response_model=tp.Union[IpfsPublishResponse, GenericResponse])  # type: ignore
async def publish_file_to_pinata(
    filename: tp.Optional[str] = Form(None),
    file_data: tp.Optional[UploadFile] = File(None),
) -> tp.Union[IpfsPublishResponse, GenericResponse]:
    """
    publish a file into IPFS and Pinata

    a file can be provided EITHER as multipart form data OR a string path-like filename to it on the host machine
    """

    if filename is not None:
        check_presence(filename)
        file: bytes = open(filename, "rb").read()
        filename_: str = os.path.basename(filename)
    elif file_data is not None:
        file = await file_data.read()
        filename_ = file_data.filename
    else:
        raise ValueError("This operation accepts either one of its arguments but not both or none of them")

    try:
        response = await pinata.pin_file(file, filename_)
        cid = response.get("IpfsHash", "failed")
        uri = config.ipfs.gateway_address + cid
        message = f"File {filename_} pinned"
        logger.info(message)
        return IpfsPublishResponse(status=status.HTTP_200_OK, details=message, ipfs_cid=cid, ipfs_link=uri)

    except Exception as e:
        message = f"An error occurred while publishing file to Pinata: {e}"
        logger.error(message)
        return GenericResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, details=message)


@router.post("/ipfs", response_model=tp.Union[IpfsPublishResponse, GenericResponse])  # type: ignore
async def publish_file_to_ipfs(
    filename: tp.Optional[str] = Form(None),
    file_data: tp.Optional[UploadFile] = File(None),
) -> tp.Union[IpfsPublishResponse, GenericResponse]:
    """
    publish a file into IPFS

    a file can be provided EITHER as multipart form data OR a string path-like filename to it on the host machine
    """

    if filename is not None:
        check_presence(filename)

    try:
        cid, uri = ipfs.publish_to_ipfs(filename, await file_data.read() if file_data else None)
        message = f"File {filename or file_data.filename} published"
        logger.info(message)
        return IpfsPublishResponse(status=status.HTTP_200_OK, details=message, ipfs_cid=cid, ipfs_link=uri)

    except Exception as e:
        message = f"An error occurred while publishing file to IPFS: {e}"
        logger.error(message)
        return GenericResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, details=message)
