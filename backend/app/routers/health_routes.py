from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status

from app.database.session import get_db


router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("")
def health_check() -> dict[str, str]:
    return {
        "status": "online",
        "message": "CallIT API is running",
    }


@router.get("/database")
def database_health_check(
    database: Session = Depends(get_db),
) -> dict[str, str]:
    try:
        database.execute(text("SELECT 1"))

        return {
            "status": "online",
            "database": "connected",
        }

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed",
        ) from error