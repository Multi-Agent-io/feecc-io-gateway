from __future__ import annotations

import asyncio
import os
import socket
import typing as tp
from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from loguru import logger

from ..shared.config import camera_config

MINIMAL_RECORD_DURATION_SEC = 3


@dataclass(frozen=True)
class Camera:
    """a wrapper for the video camera config"""

    ip: str
    port: int
    number: int
    rtsp_stream_link: str

    def __post_init__(self) -> None:
        self.is_up()

    def __str__(self) -> str:
        return f"Camera no.{self.number} host at {self.ip}:{self.port}"

    @property
    def host(self) -> str:
        return f"{self.ip}:{self.port}"

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
    process_ffmpeg: tp.Optional[asyncio.subprocess.Process] = None
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
        return f"{dir_}/{self.record_id}.mp4"

    @property
    def is_ongoing(self) -> bool:
        return self.start_time is not None and self.end_time is None

    async def start(self) -> None:
        """Execute ffmpeg command"""
        # ffmpeg -rtsp_transport tcp -i "rtsp://login:password@ip:port/Streaming/Channels/101" -c copy -map 0 vid.mp4
        command: str = f'ffmpeg -rtsp_transport tcp -i "{self.rtsp_steam}" -r 25 -c copy -map 0 {self.filename}'
        self.process_ffmpeg = await asyncio.subprocess.create_subprocess_shell(
            cmd=command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
        )
        self.start_time = datetime.now()
        logger.info(f"Started recording video '{self.filename}' using ffmpeg. {self.process_ffmpeg.pid=}")

    async def stop(self) -> None:
        """stop recording a video"""
        if self.process_ffmpeg is None:
            logger.error(f"Failed to stop record {self.record_id}")
            logger.debug(f"Operation ongoing: {self.is_ongoing}, ffmpeg process: {bool(self.process_ffmpeg)}")
            return

        if len(self) < MINIMAL_RECORD_DURATION_SEC:
            logger.warning(
                f"Recording {self.record_id} duration is below allowed minimum ({MINIMAL_RECORD_DURATION_SEC=}s). "
                "Waiting for it to reach it before stopping."
            )
            await asyncio.sleep(MINIMAL_RECORD_DURATION_SEC - len(self))

        logger.info(f"Trying to stop record {self.record_id} process {self.process_ffmpeg.pid=}")
        await self.process_ffmpeg.communicate(input=b"q")
        await self.process_ffmpeg.wait()
        self.process_ffmpeg = None
        self.end_time = datetime.now()
        logger.info(f"Finished recording video for record {self.record_id}")


cameras: tp.Dict[int, Camera] = {
    section.number: Camera(
        ip=section.ip,
        port=section.port,
        number=section.number,
        rtsp_stream_link=section.rtsp_stream_link,
    )
    for section in camera_config
}

logger.info(f"Initialized {len(cameras)} cameras")

records: tp.Dict[str, Recording] = {}
