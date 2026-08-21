from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.papers import router as papers_router
from app.routers.analysis import router as analysis_router
from app.routers.results import router as results_router
from app.routers.history import router as history_router
from app.routers.dashboard import router as dashboard_router
from app.routers.admin import router as admin_router
from app.routers.notifications import router as notifications_router

__all__ = [
    "auth_router", "users_router", "papers_router", "analysis_router",
    "results_router", "history_router", "dashboard_router", "admin_router",
    "notifications_router"
]
