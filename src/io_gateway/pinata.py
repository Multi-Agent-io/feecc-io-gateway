import os
import typing as tp
from time import time

import httpx
from loguru import logger

from ..shared.config import config

PINATA_ENDPOINT: str = "https://api.pinata.cloud"
PINATA_API: str = config.pinata.pinata_api
PINATA_SECRET_API: str = config.pinata.pinata_secret_api
AUTH_HEADERS = {
    "pinata_api_key": PINATA_API,
    "pinata_secret_api_key": PINATA_SECRET_API,
}


@logger.catch(reraise=True)
async def pin_file(file: tp.Union[os.PathLike[tp.AnyStr], tp.IO[bytes]]) -> tp.Tuple[str, str]:
    logger.info("Pushing file to Pinata")
    t0 = time()

    files = {"file": open(file, "rb") if isinstance(file, os.PathLike) else file}
    async with httpx.AsyncClient(base_url=PINATA_ENDPOINT) as client:
        response = await client.post("/pinning/pinFileToIPFS", files=files, headers=AUTH_HEADERS)

    data = response.json()
    ipfs_hash: str = data["IpfsHash"]
    ipfs_link: str = config.ipfs.gateway_address + ipfs_hash
    logger.info("Published file to Pinata.")
    logger.debug(f"Push took {round(time() - t0, 3)} s.")
    logger.debug(data)
    return ipfs_hash, ipfs_link
