from app.routers.health_routes import router as health_router
from app.routers.user_routes import router as user_router

__all__ = [
    "health_router",
    "user_router",
]