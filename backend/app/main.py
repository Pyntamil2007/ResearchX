from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.database.database import engine, Base, SessionLocal
from app.models.user import User
from app.services.demo_service import DemoService
from app.schemas.common import StandardResponse
from app.routers import (
    auth_router,
    users_router,
    papers_router,
    analysis_router,
    results_router,
    history_router,
    dashboard_router,
    admin_router,
    notifications_router
)

from sqlalchemy import inspect

def ensure_db_schema_columns(db_engine):
    """Safely migrate and add new columns to existing database tables (SQLite & PostgreSQL)."""
    try:
        inspector = inspect(db_engine)
        existing_tables = inspector.get_table_names()
        
        with db_engine.connect() as conn:
            # 1. research_papers table
            if "research_papers" in existing_tables:
                rp_cols = [c["name"] for c in inspector.get_columns("research_papers")]
                if "document_type" not in rp_cols:
                    conn.exec_driver_sql("ALTER TABLE research_papers ADD COLUMN document_type VARCHAR(100) DEFAULT 'Research Paper'")
            
            # 2. analyses table
            if "analyses" in existing_tables:
                an_cols = [c["name"] for c in inspector.get_columns("analyses")]
                if "document_type" not in an_cols:
                    conn.exec_driver_sql("ALTER TABLE analyses ADD COLUMN document_type VARCHAR(100) DEFAULT 'Research Paper'")
                if "recommended_domains" not in an_cols:
                    conn.exec_driver_sql("ALTER TABLE analyses ADD COLUMN recommended_domains TEXT")
                    
            # 3. users table
            if "users" in existing_tables:
                u_cols = [c["name"] for c in inspector.get_columns("users")]
                if "auth_provider" not in u_cols:
                    conn.exec_driver_sql("ALTER TABLE users ADD COLUMN auth_provider VARCHAR(20) DEFAULT 'local'")
                if "google_id" not in u_cols:
                    conn.exec_driver_sql("ALTER TABLE users ADD COLUMN google_id VARCHAR(100)")

            conn.commit()
    except Exception as e:
        print(f"Schema migration warning: {e}")

from app.core.security import get_password_hash, verify_password

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables
    Base.metadata.create_all(bind=engine)
    ensure_db_schema_columns(engine)
    
    # Ensure sample PDFs exist on disk for user experiments
    DemoService.ensure_demo_files()

    # Ensure admin@researchx.com exists with explicit role = 'ADMIN' and secure password
    db = SessionLocal()
    try:
        admin_email = (getattr(settings, "ADMIN_EMAIL", None) or "admin@researchx.com").lower().strip()
        admin_pwd = getattr(settings, "ADMIN_PASSWORD", None) or "Admin@2026"
        
        admin_user = db.query(User).filter(User.email == admin_email).first()
        if not admin_user:
            admin_user = User(
                name="System Administrator",
                email=admin_email,
                password_hash=get_password_hash(admin_pwd),
                role="ADMIN",
                status="active",
                auth_provider="local"
            )
            db.add(admin_user)
            db.commit()
            print(f"[ADMIN INIT] Created initial administrator account: {admin_email} (Role: ADMIN)")
        else:
            updated = False
            if admin_user.role != "ADMIN":
                admin_user.role = "ADMIN"
                updated = True
            if admin_user.status != "active":
                admin_user.status = "active"
                updated = True
            if admin_pwd and not verify_password(admin_pwd, admin_user.password_hash):
                admin_user.password_hash = get_password_hash(admin_pwd)
                updated = True
                print(f"[ADMIN INIT] Synchronized password hash for administrator: {admin_email}")
            
            if updated:
                db.commit()
    except Exception as e:
        print(f"Admin setup warning: {e}")
    finally:
        db.close()
        
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Web-based AI/NLP Research Paper Analyzer Full-Stack Application",
    lifespan=lifespan
)

# Configure CORS
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000"
]

if settings.FRONTEND_URL:
    clean_frontend = settings.FRONTEND_URL.strip().rstrip('/')
    if clean_frontend and clean_frontend not in allowed_origins:
        allowed_origins.append(clean_frontend)

if settings.CORS_ORIGINS:
    for origin in settings.CORS_ORIGINS.split(','):
        clean_o = origin.strip().rstrip('/')
        if clean_o and clean_o not in allowed_origins:
            allowed_origins.append(clean_o)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Exception Handlers for consistent API responses
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": str(exc.detail),
            "data": None
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = ".".join(str(loc) for loc in err.get("loc", []))
        msg = err.get("msg", "Invalid value")
        errors.append(f"{field}: {msg}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Input validation error. " + "; ".join(errors),
            "data": None
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": f"An unexpected error occurred: {str(exc)}",
            "data": None
        }
    )

# Include API Routers
app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(users_router, prefix=settings.API_PREFIX)
app.include_router(papers_router, prefix=settings.API_PREFIX)
app.include_router(analysis_router, prefix=settings.API_PREFIX)
app.include_router(results_router, prefix=settings.API_PREFIX)
app.include_router(history_router, prefix=settings.API_PREFIX)
app.include_router(dashboard_router, prefix=settings.API_PREFIX)
app.include_router(admin_router, prefix=settings.API_PREFIX)
app.include_router(notifications_router, prefix=settings.API_PREFIX)

@app.get("/")
def root_endpoint():
    return {
        "success": True,
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "version": settings.VERSION,
        "docs_url": "/docs"
    }

@app.get("/api/health")
def health_check():
    return {
        "success": True,
        "status": "healthy",
        "service": "ResearchX Backend",
        "version": settings.VERSION
    }
