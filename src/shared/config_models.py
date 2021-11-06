from pydantic import BaseModel


class ConfigSection(BaseModel):
    pass


class ApiServer(ConfigSection):
    production_environment: bool


class MongoDB(ConfigSection):
    mongo_connection_url: str


class Pinata(ConfigSection):
    enable: bool
    pinata_api: str
    pinata_secret_api: str


class Ipfs(ConfigSection):
    enable: bool
    gateway_address: str


class Yourls(ConfigSection):
    server: str
    username: str
    password: str


class Printer(ConfigSection):
    printer_model: str
    paper_width: int
    enable: bool
    red: bool


class Video(ConfigSection):
    delete_after_publishing: bool


class GlobalConfig(BaseModel):
    api_server: ApiServer
    mongo_db: MongoDB
    pinata: Pinata
    ipfs: Ipfs
    yourls: Yourls
    printer: Printer
    video: Video


class CameraConfigSection(ConfigSection):
    number: int
    ip: str
    port: int
    rtsp_stream_link: str
