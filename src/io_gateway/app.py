import asyncio
import os
import typing as tp
from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile, status
from loguru import logger

from . import ipfs, pinata
from .dependencies import get_file
from .models import GenericResponse, IpfsPublishResponse
from ..shared.config import config

router = APIRouter()


@router.post("/publish-to-ipfs/by-path", response_model=tp.Union[IpfsPublishResponse, GenericResponse])  # type: ignore
async def publish_file_to_ipfs_by_path(
    file: Path = Depends(get_file),
) -> tp.Union[IpfsPublishResponse, GenericResponse]:
    """
    Publish file to IPFS using local node (if enabled by config) and / or pin to Pinata pinning cloud (if enabled by config).

    File is accepted as an absolute path to the desired file on the host machine
    """
    try:
        cid, uri = await publish_file(file)
        message = f"File {file.name} published"
        logger.info(message)
        return IpfsPublishResponse(status=status.HTTP_200_OK, details=message, ipfs_cid=cid, ipfs_link=uri)

    except Exception as e:
        message = f"An error occurred while publishing file to IPFS: {e}"
        logger.error(message)
        return GenericResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, details=message)


@router.post("/publish-to-ipfs/upload-file", response_model=tp.Union[IpfsPublishResponse, GenericResponse])  # type: ignore
async def publish_file_to_ipfs_as_upload(
    file_data: UploadFile = File(...),
) -> tp.Union[IpfsPublishResponse, GenericResponse]:
    """
    Publish file to IPFS using local node (if enabled by config) and / or pin to Pinata pinning cloud (if enabled by config).

    File is accepted as an UploadFile (multipart form data)
    """
    try:
        # temporary fix using on disk caching, need to be reworked to work without saving data on the disk
        cache_dir = "cache"
        if not os.path.exists(cache_dir):
            os.mkdir(cache_dir)

        path = f"{cache_dir}/{file_data.filename}"
        with open(path, "wb") as f:
            f.write(file_data.file.read())

        cid, uri = await publish_file(Path(path))
        message = f"File {file_data.filename} published"
        logger.info(message)
        return IpfsPublishResponse(status=status.HTTP_200_OK, details=message, ipfs_cid=cid, ipfs_link=uri)

    except Exception as e:
        message = f"An error occurred while publishing file to IPFS: {e}"
        logger.error(message)
        return GenericResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, details=message)


async def publish_file(file: tp.Union[os.PathLike[tp.AnyStr], tp.IO[bytes]]) -> tp.Tuple[str, str]:
    if config.ipfs.enable and config.pinata.enable:
        cid, uri = ipfs.publish_to_ipfs(file)
        asyncio.create_task(pinata.pin_file(file))
    elif config.ipfs.enable:
        cid, uri = ipfs.publish_to_ipfs(file)
    elif config.pinata.enable:
        cid, uri = await pinata.pin_file(file)
    else:
        raise ValueError("Both IPFS and Pinata are disabled in config, cannot get CID")

    return cid, uri
