import uvicorn
from pathlib import Path

def run_app():
    uvicorn.run(
        "request_logger.web.app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=[str(Path(__file__).parent)],
    )
