import os
import typing as tp

import ipfshttpclient
from loguru import logger

from ..shared.config import config

IS_DOCKERIZED: bool = os.environ.get("IS_DOCKERIZED", False)


def _get_ipfs_client() -> tp.Optional[ipfshttpclient.Client]:

    if not config.ipfs.enable:
        logger.warning("IPFS capabilities are disabled in config-file")
        return None

    try:
        node_address = f"/dns/{'ipfs-node' if IS_DOCKERIZED else 'localhost'}/tcp/5001/http"
        client = ipfshttpclient.connect(addr=node_address)
        logger.info(f"Successfully connected to the IPFS node at {node_address}")
        return client

    except Exception as e:
        logger.error(f"An error occurred while getting IPFS client: {e}")
        return None


IPFS_CLIENT: tp.Optional[ipfshttpclient.Client] = _get_ipfs_client()


@logger.catch
def publish_to_ipfs(file_path: tp.Optional[str] = None, file_contents: tp.Optional[bytes] = None) -> tp.Tuple[str, str]:
    """publish file on IPFS"""

    # make sure only one of the arguments is provided
    if bool(file_path) == bool(file_contents):
        raise ValueError("Publish to IPFS accepts either one of its arguments but not both or none of them")

    logger.info(f"Publishing file {file_path or ''} to IPFS")
    client = IPFS_CLIENT or _get_ipfs_client()

    if client is None:
        raise ConnectionError(f"Connection to IPFS node failed, cannot publish file {file_path or ''}")

    result = client.add(file_path or file_contents)
    ipfs_hash: str = result["Hash"]
    ipfs_link: str = config.ipfs.gateway_address + ipfs_hash
    logger.info(f"File {file_path or ''} published to IPFS, hash: {ipfs_hash}")
    return ipfs_hash, ipfs_link
