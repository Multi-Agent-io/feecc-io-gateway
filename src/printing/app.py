import os
from uuid import uuid4

from fastapi import APIRouter, File, status
from loguru import logger

from ._Printer import Printer
from .models import GenericResponse, PrintImageRequest

CACHE_DIR = "printing_cache"

router = APIRouter()


@router.post("/printing/print_image", response_model=GenericResponse)
def publish_file_to_pinata(print_request: PrintImageRequest, image_file: bytes = File(...)) -> GenericResponse:
    """Print an image using label printer and annotate if necessary"""

    # save image file to disk for later printing
    global CACHE_DIR
    image_path = f"{CACHE_DIR}/{uuid4().hex}.png"

    with open(image_path, "wb") as f:
        f.write(image_file)

    printer = Printer()

    try:
        printer.print_image(image_path, print_request.annotation)
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

    global CACHE_DIR
    if not os.path.exists(CACHE_DIR):
        os.mkdir(CACHE_DIR)
