import typing as tp

import ipfshttpclient
from loguru import logger

from ..shared.config import config


def _get_ipfs_client() -> tp.Optional[ipfshttpclient.Client]:
    if not config.ipfs.enable:
        logger.warning("IPFS capabilities are disabled in config-file")
        return None

    try:
        return ipfshttpclient.connect()
    except Exception as e:
        logger.error(f"An error occurred while getting IPFS client: {e}")
        return None


IPFS_CLIENT: tp.Optional[ipfshttpclient.Client] = _get_ipfs_client()


def publish_to_ipfs(file_path: str) -> tp.Tuple[str, str]:
    """publish file on IPFS"""
    logger.info(f"Publishing file {file_path} to IPFS")
    client = IPFS_CLIENT or _get_ipfs_client()

    if client is None:
        raise ConnectionError(f"Connection to IPFS node failed, cannot publish file {file_path}")

    result = client.add(file_path)
    ipfs_hash: str = result["Hash"]
    ipfs_link: str = config.ipfs.gateway_address + ipfs_hash
    logger.info(f"File {file_path} published to IPFS, hash: {ipfs_hash}")
    return ipfs_hash, ipfs_link
