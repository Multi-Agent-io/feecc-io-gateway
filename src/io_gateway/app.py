import typing as tp

from fastapi import APIRouter, BackgroundTasks, File, Form, status
from loguru import logger

from . import ipfs, pinata
from .models import GenericResponse, IpfsPublishResponse
from .utils import check_presence
from ..shared.config import config

router = APIRouter()


@router.post("/pinata", response_model=tp.Union[IpfsPublishResponse, GenericResponse])  # type: ignore
async def publish_file_to_pinata(
    background_tasks: BackgroundTasks,
    filename: tp.Optional[str] = Form(None),
    file_data: tp.Optional[bytes] = File(None),
    background: bool = Form(True),
) -> tp.Union[IpfsPublishResponse, GenericResponse]:
    """
    publish a file into IPFS and Pinata

    a file can be provided EITHER as multipart form data OR a string path-like filename to it on the host machine
    """

    if filename is not None:
        check_presence(filename)

    try:
        if background:
            cid, uri = ipfs.publish_to_ipfs(file_path=filename, file_contents=file_data)
            background_tasks.add_task(pinata.pin_file, filename, file_data)
            message = f"Added background pinning task for file {filename or ''}"
        else:
            response = await pinata.pin_file(filename, file_data)
            cid = response["IpfsHash"]
            uri = config.ipfs.gateway_address + cid
            message = f"File {filename or ''} pinned"

        logger.info(message)
        return IpfsPublishResponse(status=status.HTTP_200_OK, details=message, ipfs_cid=cid, ipfs_link=uri)

    except Exception as e:
        message = f"An error occurred while publishing file to Pinata: {e}"
        logger.error(message)
        return GenericResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, details=message)


@router.post("/ipfs", response_model=tp.Union[IpfsPublishResponse, GenericResponse])  # type: ignore
def publish_file_to_ipfs(
    filename: tp.Optional[str] = Form(None),
    file_data: tp.Optional[bytes] = File(None),
) -> tp.Union[IpfsPublishResponse, GenericResponse]:
    """
    publish a file into IPFS

    a file can be provided EITHER as multipart form data OR a string path-like filename to it on the host machine
    """

    if filename is not None:
        check_presence(filename)

    try:
        cid, uri = ipfs.publish_to_ipfs(filename, file_data)
        message = f"File {filename or ''} published"
        logger.info(message)
        return IpfsPublishResponse(status=status.HTTP_202_ACCEPTED, details=message, ipfs_cid=cid, ipfs_link=uri)

    except Exception as e:
        message = f"An error occurred while publishing file to IPFS: {e}"
        logger.error(message)
        return GenericResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, details=message)
