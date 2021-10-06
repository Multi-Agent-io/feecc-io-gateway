import typing as tp

import ipfshttpclient
from loguru import logger

from ..shared.config import config

IPFS_CLIENT: ipfshttpclient.Client = ipfshttpclient.connect()


def publish_to_ipfs(file_path: str) -> tp.Tuple[str, str]:
    """publish file on IPFS"""
    logger.info(f"Publishing file {file_path} to IPFS")
    result = IPFS_CLIENT.add(file_path)
    ipfs_hash: str = result["Hash"]
    ipfs_link: str = config.ipfs.gateway_address + ipfs_hash
    logger.info(f"File {file_path} published to IPFS, hash: {ipfs_hash}")
    return ipfs_hash, ipfs_link
