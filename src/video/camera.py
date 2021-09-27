from __future__ import annotations

import asyncio.subprocess as subprocess
import os
import socket
import typing as tp
from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from loguru import logger


@dataclass(frozen=True)
class Camera:
    """a wrapper for the video camera config"""

    ip: str
    port: str
    login: str
    password: str
    number: int

    def __post_init__(self) -> None:
        self.is_up()

    def __str__(self) -> str:
        return f"Camera no.{self.number} host at {self.ip}:{self.port}"

    @property
    def host(self) -> str:
        return f"{self.ip}:{self.port}"

    @property
    def rtsp_stream_link(self) -> str:
        return f"rtsp://{self.login}:{self.password}@{self.ip}:{self.port}/Streaming/Channels/101"

    def is_up(self) -> bool:
        """check if camera is reachable on the specified port and ip"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.25)

        try:
            s.connect((self.ip, int(self.port)))
            is_up = True
            logger.debug(f"{self} is up")
        except socket.error:
            is_up = False
            logger.warning(f"{self} is unreachable")

        s.close()
        return is_up


@dataclass
class Recording:
    """a recording object represents one ongoing recording process"""

    rtsp_steam: str
    filename: tp.Optional[str] = None
    process_ffmpeg: tp.Optional[subprocess.Process] = None
    record_id: str = field(default_factory=lambda: uuid4().hex)
    start_time: tp.Optional[datetime] = None
    end_time: tp.Optional[datetime] = None

    def __post_init__(self) -> None:
        self.filename = self._get_video_filename()

    def __len__(self) -> int:
        """calculate recording duration in seconds"""
        if self.start_time is None:
            return 0

        if self.end_time is not None:
            duration = self.end_time - self.start_time
        else:
            duration = datetime.now() - self.start_time

        return int(duration.total_seconds())

    def _get_video_filename(self, dir_: str = "output/video") -> str:
        """determine a valid video name not to override an existing video"""
        if not os.path.isdir(dir_):
            os.makedirs(dir_)
        filename = f"{dir_}/{self.record_id}_video_1.mp4"
        cnt: int = 1
        while os.path.exists(filename):
            filename = filename.replace(f"video_{cnt}", f"video_{cnt + 1}")
            cnt += 1
        return filename

    @property
    def is_ongoing(self) -> bool:
        return self.start_time is not None and self.end_time is None

    async def start(self) -> None:
        """Execute ffmpeg command"""
        # ffmpeg -rtsp_transport tcp -i "rtsp://login:password@ip:port/Streaming/Channels/101" -c copy -map 0 vid.mp4
        command: str = f'ffmpeg -rtsp_transport tcp -i "{self.rtsp_steam}" -r 25 -c copy -map 0 {self.filename}'
        self.process_ffmpeg = await subprocess.create_subprocess_shell(
            cmd=command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        self.start_time = datetime.now()
        logger.info(f"Started recording video '{self.filename}' using ffmpeg")

    async def stop(self) -> None:
        """stop recording a video"""
        if self.process_ffmpeg is None:
            logger.error(f"Failed to stop record {self.record_id}")
            logger.debug(f"Operation ongoing: {self.is_ongoing}, ffmpeg process: {bool(self.process_ffmpeg)}")
            return

        self.process_ffmpeg.terminate()
        await self.process_ffmpeg.wait()
        self.process_ffmpeg = None
        self.end_time = datetime.now()
        logger.info(f"Finished recording video for record {self.record_id}")
