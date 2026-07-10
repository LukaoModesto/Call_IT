from fastapi import FastAPI

from app.core.config import settings
from app.routers.health_routes import router as health_router
from app.routers.user_routes import router as user_router


app = FastAPI(
    title=settings.app_name,
    description="Help desk API for ticket management.",
    version=settings.app_version,
    debug=settings.debug,
)

app.include_router(health_router)
app.include_router(user_router)


@app.get("/", tags=["Root"])
def root() -> dict[str, str]:
    return {
        "status": "online",
        "message": "Welcome to CallIT API",
    }