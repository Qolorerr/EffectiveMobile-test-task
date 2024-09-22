import logging.config

import uvicorn
from fastapi import FastAPI

from src.config import LOGGER_CONFIG, DB_PATH
from src.routes import register_routes
from src.services import base_init

app = FastAPI()
register_routes(app)

logging.config.dictConfig(LOGGER_CONFIG)
logger = logging.getLogger("app")


if __name__ == "__main__":
    base_init(DB_PATH)
    uvicorn.run("main:app", port=8000, reload=False, log_level="info")
