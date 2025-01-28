import html
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from request_logger.core.storage.file import FileStorage
from request_logger.core.request_logger import RequestLogger
from request_logger.core.replayer import Replayer
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi import HTTPException

from request_logger.core.util import RequestUtil

app = FastAPI()

# Mount static files
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Set up templates
templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# Initialize storage and logger
storage = FileStorage(directory='request_logs')
logger = RequestLogger(storage=storage)
replayer = Replayer(storage=storage)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # Retrieve list of request IDs
    request_ids = storage.list_requests()
    return templates.TemplateResponse("index.html", {"request": request, "request_ids": request_ids})


@app.get("/request/{request_id}", response_class=HTMLResponse)
async def request_detail(request: Request, request_id: str):
    try:
        request_data = storage.load_request(request_id)
        request_data.update(RequestUtil.parse_request_kwargs(request_data))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Request not found")
    return templates.TemplateResponse("request_detail.html", {"request": request, "request_data": request_data})


@app.post("/request/{request_id}/replay", response_class=HTMLResponse)
async def replay_request(request_id: str):
    try:
        response = replayer.replay_request(request_id)
        status_code = response.status_code
        content = html.escape(response.text)

        html_content = f"""
        <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative" role="alert">
          <strong class="font-bold">Replayed Successfully!</strong>
          <span class="block sm:inline">Status Code: {status_code}</span>
          <div class="mt-2">
            <p class="font-semibold">Response Body:</p>
            <pre class="bg-gray-100 p-4 rounded overflow-auto">{content}</pre>
          </div>
        </div>
        """
        return HTMLResponse(content=html_content)
    except Exception as e:
        error_message = html.escape(str(e))
        html_content = f"""
        <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong class="font-bold">Error:</strong>
          <span class="block sm:inline">{error_message}</span>
        </div>
        """
        return HTMLResponse(content=html_content, status_code=500)


@app.post("/request/{request_id}/modify_replay", response_class=HTMLResponse)
async def modify_and_replay(request: Request, request_id: str):
    form_data = await request.form()
    modifications = dict(form_data)
    try:
        response = replayer.replay_request(request_id, modifications=modifications)
        status_code = response.status_code
        content = f"<p>Modified request replayed successfully with status code: {status_code}</p>"
        return HTMLResponse(content=content)
    except Exception as e:
        content = f"<p>Error replaying modified request: {str(e)}</p>"
        return HTMLResponse(content=content, status_code=500)

@app.get("/request/{request_id}/modify_form", response_class=HTMLResponse)
async def get_modify_form(request: Request, request_id: str):
    try:
        request_data = storage.load_request(request_id)
        request_data.update(RequestUtil.parse_request_kwargs(request_data))

        return templates.TemplateResponse("modify_form.html", {"request": request, "request_data": request_data})
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Request not found")
