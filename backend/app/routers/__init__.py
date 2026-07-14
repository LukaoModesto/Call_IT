from app.routers.access_routes import router as access_router
from app.routers.auth_routes import router as auth_router
from app.routers.health_routes import router as health_router
from app.routers.ticket_routes import router as ticket_router
from app.routers.user_routes import router as user_router
from app.routers.catalog_routes import router as catalog_router
from app.services.catalog_service import (
    create_category,
    create_department,
    get_active_category_by_id,
    get_categories,
    get_category_by_id,
    get_department_by_id,
    get_departments,
)

__all__ = [
    "access_router",
    "auth_router",
    "health_router",
    "ticket_router",
    "user_router",
    "catalog_router",
    "create_category",
    "create_department",
    "get_active_category_by_id",
    "get_categories",
    "get_category_by_id",
    "get_department_by_id",
    "get_departments",
]