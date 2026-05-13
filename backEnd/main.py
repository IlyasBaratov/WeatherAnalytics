import pathlib
import os

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from starlette.requests import Request

from backEnd.api.routers import weather, ski, pages
from backEnd.core.database import engine, Base
# --- paths ---
BASE_DIR = pathlib.Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

# Host both UI and API from the same container:
# - UI (static files): /
# - API:              /api/*
# - Swagger:          /api/docs
app = FastAPI(
    title="Weather Portal API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)


@app.middleware("http")
async def add_no_cache_headers(request: Request, call_next):
    response = await call_next(request)
    path = request.url.path
    if path == "/" or path.endswith(".html") or path.endswith(".css") or path.endswith(".js") or path == "/env.js":
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# Enable CORS so the frontEnd can call API independently
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace it with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(weather.router)
app.include_router(ski.router)


@app.get("/env.js", include_in_schema=False)
async def env_js() -> Response:
    api_base_url = os.getenv("API_BASE_URL")
    if not api_base_url:
        api_base_url = "/api/weather"
    payload = f"window.__ENV__ = {{ API_BASE_URL: {api_base_url!r} }};\n"
    return Response(content=payload, media_type="application/javascript")

@app.on_event("startup")
def on_startup():
    # create DB tables if they don't exist (local dev convenience)
    Base.metadata.create_all(bind=engine)
@app.on_event("shutdown")
async def on_shutdown():
    await ski.cleanup_ski_service()


@app.get("/api/health", tags=["health"])
async def health():
    return {"status": "ok"}


# Static UI from the repo folder: ./frontEnd
frontend_dir = PROJECT_DIR / "frontEnd"
frontend_html_dir = frontend_dir / "html"
frontend_css_dir = frontend_dir / "css"
frontend_js_dir = frontend_dir / "js"

if frontend_css_dir.exists():
    app.mount("/css", StaticFiles(directory=str(frontend_css_dir)), name="css")
if frontend_js_dir.exists():
    app.mount("/js", StaticFiles(directory=str(frontend_js_dir)), name="js")


@app.get("/", include_in_schema=False)
async def frontend_index() -> FileResponse:
    index_path = frontend_html_dir / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(str(index_path), media_type="text/html")


@app.get("/index.html", include_in_schema=False)
async def frontend_index_html() -> FileResponse:
    return await frontend_index()


@app.get("/ski_index.html", include_in_schema=False)
async def frontend_ski() -> FileResponse:
    ski_path = frontend_html_dir / "ski_index.html"
    if not ski_path.exists():
        raise HTTPException(status_code=404, detail="ski_index.html not found")
    return FileResponse(str(ski_path), media_type="text/html")
