import io
import typing as tp
from time import time

import httpx
from loguru import logger

from ..shared.config import config

PINATA_ENDPOINT: str = "https://api.pinata.cloud"
PINATA_API: str = config.pinata.pinata_api
PINATA_SECRET_API: str = config.pinata.pinata_secret_api


async def pin_file(
    path_to_file: tp.Optional[str] = None,
    file_contents: tp.Optional[bytes] = None,
    options: tp.Optional[tp.Dict[str, tp.Any]] = None,
    session: tp.Optional[httpx.AsyncClient] = None,
) -> tp.Dict[str, tp.Any]:
    # make sure only one of the arguments is provided
    if bool(path_to_file) == bool(file_contents):
        raise ValueError("Publish to Pinata accepts either one of its arguments but not both or none of them")

    logger.info(f"Pushing file {path_to_file or ''} to Pinata")
    t0 = time()
    url: str = f"{PINATA_ENDPOINT}/pinning/pinFileToIPFS"
    files = {"file": open(path_to_file, "rb") if path_to_file else io.BytesIO(file_contents)}  # type: ignore
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

    if request.status_code == 200:
        return request.json()  # type: ignore

    logger.info(f"Published file {path_to_file or ''} to Pinata.")
    logger.debug(f"Push took {round(time() - t0, 3)} s.")
    return {"status_code": request.status_code, "text": request.text}
