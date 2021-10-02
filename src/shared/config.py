import typing as tp

import pydantic
import yaml
from loguru import logger

from .config_models import GlobalConfig, CameraConfigSection


@logger.catch
@tp.no_type_check
def _load_config(config_path: str, model) -> tp.Any:
    logger.debug(f"Looking for config in {config_path}")

    with open(config_path) as f:
        config_f = yaml.load(f.read(), Loader=yaml.SafeLoader)
        return pydantic.parse_obj_as(model, config_f)


config: GlobalConfig = _load_config("src/config.yaml", GlobalConfig)
camera_config: tp.List[CameraConfigSection] = _load_config("src/camera_config.yaml", tp.List[CameraConfigSection])
