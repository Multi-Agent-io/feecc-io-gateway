import typing as tp

from fastapi import APIRouter, BackgroundTasks, status
from loguru import logger

from . import ipfs, pinata
from .models import GenericResponse, IpfsPublishResponse, PublishFileRequest, PublishFileWBackground
from .utils import check_presence
from ..shared.config import config

router = APIRouter()


@router.post("/pinata", response_model=tp.Union[IpfsPublishResponse, GenericResponse])  # type: ignore
async def publish_file_to_pinata(
    publish_request: PublishFileWBackground, background_tasks: BackgroundTasks
) -> tp.Union[IpfsPublishResponse, GenericResponse]:
    """publish a file into IPFS and Pinata"""
    filename = publish_request.filename
    check_presence(filename)

    try:

        if publish_request.background_processing:
            cid, uri = ipfs.publish_to_ipfs(filename)
            background_tasks.add_task(pinata.pin_file, filename)
            message = f"Added background pinning task for file {filename}"
        else:
            response = await pinata.pin_file(filename)
            cid = response["IpfsHash"]
            uri = config.ipfs.gateway_address + cid
            message = f"File {filename} pinned"

        logger.info(message)
        return IpfsPublishResponse(status=status.HTTP_200_OK, details=message, ipfs_cid=cid, ipfs_link=uri)

    except Exception as e:
        message = f"An error occurred while publishing file to Pinata: {e}"
        logger.error(message)
        return GenericResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, details=message)


@router.post("/ipfs", response_model=tp.Union[IpfsPublishResponse, GenericResponse])  # type: ignore
def publish_file_to_ipfs(publish_request: PublishFileRequest) -> tp.Union[IpfsPublishResponse, GenericResponse]:
    """publish a file into IPFS"""
    filename = publish_request.filename
    check_presence(filename)

    try:
        cid, uri = ipfs.publish_to_ipfs(filename)
        message = f"File {filename} published"
        logger.info(message)
        return IpfsPublishResponse(status=status.HTTP_202_ACCEPTED, details=message, ipfs_cid=cid, ipfs_link=uri)

    except Exception as e:
        message = f"An error occurred while publishing file to IPFS: {e}"
        logger.error(message)
        return GenericResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, details=message)
