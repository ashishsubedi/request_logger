from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from request_logger.core.request_logger import RequestLogger
from request_logger.core.replayer import Replayer
from request_logger.core.storage.file import FileStorage

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")

# Set up templates
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

# Initialize storage and logger
storage = FileStorage(directory='request_logs')
logger = RequestLogger(storage=storage)
replayer = Replayer(storage=storage)
