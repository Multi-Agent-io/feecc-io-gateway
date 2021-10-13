import io
import typing as tp
from time import time

import httpx
from loguru import logger

from ..shared.config import config

PINATA_ENDPOINT: str = "https://api.pinata.cloud"
PINATA_API: str = config.pinata.pinata_api
PINATA_SECRET_API: str = config.pinata.pinata_secret_api


@logger.catch
async def pin_file(
    file_contents: bytes,
    filename: str,
    options: tp.Optional[tp.Dict[str, tp.Any]] = None,
    session: tp.Optional[httpx.AsyncClient] = None,
) -> tp.Dict[str, tp.Any]:
    # make sure only one of the arguments is provided
    logger.info(f"Pushing file {filename} to Pinata")
    t0 = time()
    url: str = f"{PINATA_ENDPOINT}/pinning/pinFileToIPFS"
    files = {"file": io.BytesIO(file_contents)}
    headers = {
        "pinata_api_key": PINATA_API,
        "pinata_secret_api_key": PINATA_SECRET_API,
    }

    if options is not None:
        if "pinataMetadata" in options:
            files["pinataMetadata"] = options["pinataMetadata"]
        if "pinataOptions" in options:
            files["pinataOptions"] = options["pinataOptions"]

    if session is None:
        async with httpx.AsyncClient() as client:
            request = await client.post(url, files=files, headers=headers)
    else:
        request = await session.post(url, files=files, headers=headers)

    logger.info(f"Published file {filename} to Pinata.")
    logger.debug(f"Push took {round(time() - t0, 3)} s.")

    if request.status_code != 200:
        raise ConnectionError(request.text)
    logger.debug(request.json())
    return request.json()  # type: ignore
