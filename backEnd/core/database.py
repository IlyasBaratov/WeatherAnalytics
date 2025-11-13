from typing import Generator, Optional
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base

"""
Database URL configurable via env var. Default to a local SQLite file for easy development.
Default path: <project_root>/db/weather.db (two levels up from this file).
"""

# Resolve project root and ensure db directory exists
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_DB_DIR = os.path.join(_PROJECT_ROOT, "db")
os.makedirs(_DB_DIR, exist_ok=True)

# Build default SQLite URL to <project_root>/db/weather.db
DEFAULT_SQLITE_URL = "sqlite:///" + os.path.join(_DB_DIR, "weather.db")
DATABASE_URL: str = os.getenv("DATABASE_URL", DEFAULT_SQLITE_URL)

# For SQLite we need to pass connect_args to avoid thread check issues.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, class_=Session)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
	"""Dependency that provides a SQLAlchemy Session (sync).

	Use in FastAPI endpoints with Depends(get_db).
	"""
	db: Optional[Session] = None
	try:
		db = SessionLocal()
		yield db
	finally:
		if db:
			db.close()
