import typing as tp
from time import time

import httpx
from loguru import logger

PINATA_ENDPOINT: str = "https://api.pinata.cloud"


async def pin_file(
    api_key: str,
    secret_api_key: str,
    path_to_file: str,
    options: tp.Optional[tp.Dict[str, tp.Any]] = None,
    session: tp.Optional[httpx.AsyncClient] = None,
) -> tp.Dict[str, tp.Any]:

    logger.info(f"Pushing file {path_to_file} to Pinata")
    t0 = time()
    url: str = f"{PINATA_ENDPOINT}/pinning/pinFileToIPFS"
    files = {"file": open(path_to_file, "rb")}
    headers = {
        "pinata_api_key": api_key,
        "pinata_secret_api_key": secret_api_key,
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

    logger.info(f"Published file {path_to_file} to Pinata.")
    logger.debug(f"Push took {round(time() - t0, 3)} s.")
    return {"status_code": request.status_code, "text": request.text}
