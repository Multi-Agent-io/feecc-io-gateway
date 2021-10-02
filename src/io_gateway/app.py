import typing as tp

from fastapi import APIRouter, BackgroundTasks, status
from loguru import logger

from . import ipfs, pinata
from .models import GenericResponse, IpfsPublishResponse, PublishFileRequest
from ..shared.config import config

router = APIRouter()


@router.post("/io-gateway/pinata", response_model=tp.Union[IpfsPublishResponse, GenericResponse])  # type: ignore
async def publish_file_to_pinata(
    publish_request: PublishFileRequest, background_tasks: BackgroundTasks
) -> tp.Union[IpfsPublishResponse, GenericResponse]:
    """publish a file into IPFS and Pinata"""
    filename = publish_request.filename
    pinata_api = config.pinata.pinata_api
    pinata_secret_api = config.pinata.pinata_secret_api

    try:

        if publish_request.background_processing:
            cid, uri = ipfs.publish_to_ipfs(filename)
            background_tasks.add_task(pinata.pin_file, pinata_api, pinata_secret_api, filename)
            message = f"Added background pinning task for file {filename}"
        else:
            response = await pinata.pin_file(pinata_api, pinata_secret_api, filename)
            cid = response["IpfsHash"]
            uri = f"https://gateway.ipfs.io/ipfs/{cid}"
            message = f"File {filename} pinned"

        logger.info(message)
        return IpfsPublishResponse(status=status.HTTP_200_OK, details=message, ipfs_cid=cid, ipfs_link=uri)

    except Exception as e:
        message = f"An error occurred while publishing file to Pinata: {e}"
        logger.error(message)
        return GenericResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, details=message)


@router.post("/io-gateway/ipfs", response_model=tp.Union[IpfsPublishResponse, GenericResponse])  # type: ignore
def publish_file_to_ipfs(
    publish_request: PublishFileRequest, background_tasks: BackgroundTasks
) -> tp.Union[IpfsPublishResponse, GenericResponse]:
    """publish a file into IPFS"""
    filename = publish_request.filename

    try:

        if publish_request.background_processing:
            background_tasks.add_task(ipfs.publish_to_ipfs, filename)
            message = f"Added background pinning task for file {filename}"
            logger.info(message)
            return GenericResponse(status=status.HTTP_202_ACCEPTED, details=message)

        else:
            cid, uri = ipfs.publish_to_ipfs(filename)
            message = f"File {filename} published"
            logger.info(message)
            return IpfsPublishResponse(status=status.HTTP_202_ACCEPTED, details=message, ipfs_cid=cid, ipfs_link=uri)

    except Exception as e:
        message = f"An error occurred while publishing file to IPFS: {e}"
        logger.error(message)
        return GenericResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, details=message)
