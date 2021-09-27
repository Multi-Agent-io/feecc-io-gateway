from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from database import MongoDbWrapper
from dependencies import authenticate
from io_gateway.app import router as io_gateway_router
from logging_config import CONSOLE_LOGGING_CONFIG, FILE_LOGGING_CONFIG
from printing.app import router as printing_router
from shared.Config import Config
from video.app import router as video_router

# apply logging configuration
logger.configure(handlers=[CONSOLE_LOGGING_CONFIG, FILE_LOGGING_CONFIG])

# set up an ASGI app
app = FastAPI(dependencies=[Depends(authenticate)])

# include routers
app.include_router(io_gateway_router)
app.include_router(printing_router)
app.include_router(video_router)

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
    Config()
    MongoDbWrapper()
