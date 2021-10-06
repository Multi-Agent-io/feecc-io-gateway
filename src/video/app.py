import asyncio
import typing as tp

from fastapi import APIRouter, Depends, status
from loguru import logger

from .camera import Camera, Recording, cameras, records
from .dependencies import get_camera_by_number, get_record_by_id
from .models import (
    CameraList,
    CameraModel,
    GenericResponse,
    RecordData,
    RecordList,
    StartRecordResponse,
    StopRecordResponse,
)
from .utils import end_stuck_records
from ..dependencies import authenticate

router = APIRouter()


@router.post(
    "/camera/{camera_number}/start",
    dependencies=[Depends(authenticate)],
    response_model=tp.Union[StartRecordResponse, GenericResponse],  # type: ignore
)
async def start_recording(
    camera: Camera = Depends(get_camera_by_number),
) -> tp.Union[StartRecordResponse, GenericResponse]:
    """start recording a video using specified camera"""
    record = Recording(camera.rtsp_stream_link)

    try:
        if not camera.is_up():
            raise BrokenPipeError(f"{camera} is unreachable")

        await record.start()
        records[record.record_id] = record

        message = f"Started recording video for recording {record.record_id}"
        logger.info(message)
        return StartRecordResponse(status=status.HTTP_200_OK, details=message, record_id=record.record_id)

    except Exception as e:
        message = f"Failed to start recording video for recording {record.record_id}: {e}"
        logger.error(message)
        return GenericResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, details=message)


@router.post(
    "/record/{record_id}/stop",
    dependencies=[Depends(authenticate)],
    response_model=tp.Union[StopRecordResponse, GenericResponse],  # type: ignore
)
async def end_recording(record: Recording = Depends(get_record_by_id)) -> tp.Union[StopRecordResponse, GenericResponse]:
    """finish recording a video"""
    try:
        if not record.is_ongoing:
            raise ValueError("Recording is not currently ongoing thus cannot be stopped")

        await record.stop()
        message = f"Stopped recording video for recording {record.record_id}"
        logger.info(message)
        return StopRecordResponse(status=status.HTTP_200_OK, details=message, filename=record.filename)

    except Exception as e:
        message = f"Failed to stop recording video for recording {record.record_id}: {e}"
        logger.error(message)
        return GenericResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, details=message)


@router.get("/cameras", response_model=CameraList)
def get_cameras() -> CameraList:
    """return a list of all connected cameras"""
    cameras_data = [
        CameraModel(number=camera.number, host=camera.host, is_up=camera.is_up()) for camera in cameras.values()
    ]
    message = f"Collected {len(cameras_data)} cameras"
    logger.info(message)

    return CameraList(status=status.HTTP_200_OK, details=message, cameras=cameras_data)


@router.get("/records", response_model=RecordList)
def get_records() -> RecordList:
    """return a list of all tracked records"""
    ongoing_records = []
    ended_records = []

    for record in records.values():
        record_data = RecordData(
            filename=record.filename,
            record_id=record.record_id,
            start_time=record.start_time,
            end_time=record.end_time,
        )

        if record.is_ongoing:
            ongoing_records.append(record_data)
        else:
            ended_records.append(record_data)

    message = f"Collected {len(ongoing_records)} ongoing and {len(ended_records)} ended records"
    logger.info(message)

    return RecordList(
        status=status.HTTP_200_OK, details=message, ongoing_records=ongoing_records, ended_records=ended_records
    )


@router.on_event("startup")
@logger.catch
def startup_event() -> None:
    """tasks to do at server startup"""
    asyncio.create_task(end_stuck_records())


@router.on_event("shutdown")
@logger.catch
async def shutdown_event() -> None:
    """tasks to do at server shutdown"""
    for rec in records.values():
        if rec.is_ongoing:
            await rec.stop()
            logger.warning(f"Recording {rec.record_id} was stopped due to server shutdown.")
