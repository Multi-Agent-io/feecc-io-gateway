import typing as tp

from fastapi import APIRouter, File, Form, status
from loguru import logger

from ._Printer import Printer
from .models import GenericResponse

router = APIRouter()


@router.post("/print_image", response_model=GenericResponse)
def print_image(image_file: bytes = File(...), annotation: tp.Optional[str] = Form(None)) -> GenericResponse:
    """Print an image using label printer and annotate if necessary"""
    try:
        Printer().print_image(image_file, annotation)
        message = "Task handled as expected"
        logger.info(message)
        return GenericResponse(status=status.HTTP_200_OK, details=message)

    except Exception as e:
        message = f"An error occurred while printing the image: {e}"
        logger.error(message)
        return GenericResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, details=message)


@router.on_event("startup")
@logger.catch
def startup_event() -> None:
    """tasks to do at server startup"""
    Printer()
    logger.info("Initialized printer")
