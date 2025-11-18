import pathlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backEnd.api.routers import weather
from backEnd.core.database import engine, Base

# --- paths ---
BASE_DIR = pathlib.Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

app = FastAPI(title="Weather API")

# Enable CORS so frontEnd can call API independently
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include only the API router (no template rendering)
app.include_router(weather.router)


@app.on_event("startup")
def on_startup():
    # create DB tables if they don't exist (local dev convenience)
    Base.metadata.create_all(bind=engine)

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "Weather API is running", "docs": "/docs"}
