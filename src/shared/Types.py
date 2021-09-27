import typing as tp

CameraConfig = tp.List[tp.Dict[str, tp.Union[str, int, bool]]]
ConfigSection = tp.Dict[str, tp.Any]
GlobalConfig = tp.Dict[str, ConfigSection]
