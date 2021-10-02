from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.database import MongoDbWrapper
from src.dependencies import authenticate
from src.io_gateway.app import router as io_gateway_router
from src.logging_config import CONSOLE_LOGGING_CONFIG, FILE_LOGGING_CONFIG
from src.printing.app import router as printing_router
from src.video.app import router as video_router

# apply logging configuration
logger.configure(handlers=[CONSOLE_LOGGING_CONFIG, FILE_LOGGING_CONFIG])

# describe endpoint tags
tags = [
    {"name": "Video", "description": "Video cameras and record management"},
    {"name": "External IO", "description": "Everything related to IPFS and Pinata interaction"},
    {"name": "Printing", "description": "Printer and printing related operations"},
]

# set up an ASGI app
app = FastAPI(openapi_tags=tags, title="Feecc IO Gateway", description="https://github.com/NETMVAS/feecc-io-gateway")

# include routers
app.include_router(io_gateway_router, prefix="/io-gateway", dependencies=[Depends(authenticate)], tags=["External IO"])
app.include_router(printing_router, prefix="/printing", dependencies=[Depends(authenticate)], tags=["Printing"])
app.include_router(video_router, prefix="/video", tags=["Video"])

# allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
@logger.catch
def startup_event() -> None:
    """tasks to do at server startup"""
    MongoDbWrapper()
