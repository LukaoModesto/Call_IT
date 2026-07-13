from app.routers.access_routes import router as access_router
from app.routers.auth_routes import router as auth_router
from app.routers.health_routes import router as health_router
from app.routers.user_routes import router as user_router

__all__ = [
    "access_router",
    "auth_router",
    "health_router",
    "user_router",
]