import sys
import typing as tp

import yaml
from loguru import logger

from .Singleton import SingletonMeta
from .Types import CameraConfig, GlobalConfig


class Config(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.global_config: GlobalConfig = self._load_config("config.yaml")
        self.camera_config: CameraConfig = self._load_config("camera_config.yaml")

    @staticmethod
    def _load_config(config_path: str) -> tp.Any:
        """load up the config file"""
        logger.debug(f"Looking for config in {config_path}")

        try:
            with open(config_path) as f:
                content = f.read()
                return yaml.load(content, Loader=yaml.SafeLoader)

        except Exception as E:
            logger.error(f"Error parsing configuration file {config_path}: {E}")
            sys.exit(1)
