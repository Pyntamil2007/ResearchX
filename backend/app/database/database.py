from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

db_url = settings.get_database_url()
is_sqlite = db_url.startswith("sqlite")
is_postgres = db_url.startswith("postgresql")

# If SQLite is used, ensure the target database directory exists
if is_sqlite:
    db_path_str = db_url.replace("sqlite:///", "").replace("sqlite://", "")
    if db_path_str and db_path_str != ":memory:":
        db_path = Path(db_path_str)
        if db_path.parent and str(db_path.parent) != ".":
            db_path.parent.mkdir(parents=True, exist_ok=True)

# Build engine with dialect-optimized connection settings
if is_sqlite:
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False}
    )
else:
    # Production-grade PostgreSQL connection pooling & connection health pre-ping
    engine = create_engine(
        db_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        pool_recycle=300
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency for obtaining a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
