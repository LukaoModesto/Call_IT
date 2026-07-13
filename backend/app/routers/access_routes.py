from fastapi import APIRouter, Depends

from app.core.dependencies import (
    get_current_administrator,
    get_current_any_user,
    get_current_requester,
    get_current_support_member,
    get_current_technician,
)
from app.models.user_model import User


router = APIRouter(
    prefix="/access",
    tags=["Access Control"],
)


@router.get("/authenticated")
def authenticated_access(
    current_user: User = Depends(get_current_any_user),
) -> dict[str, str]:
    return {
        "message": "Authenticated access granted",
        "user": current_user.email,
        "role": current_user.role.value,
    }


@router.get("/requester")
def requester_access(
    current_user: User = Depends(get_current_requester),
) -> dict[str, str]:
    return {
        "message": "Requester access granted",
        "user": current_user.email,
    }


@router.get("/technician")
def technician_access(
    current_user: User = Depends(get_current_technician),
) -> dict[str, str]:
    return {
        "message": "Technician access granted",
        "user": current_user.email,
    }


@router.get("/support")
def support_access(
    current_user: User = Depends(get_current_support_member),
) -> dict[str, str]:
    return {
        "message": "Support access granted",
        "user": current_user.email,
        "role": current_user.role.value,
    }


@router.get("/administrator")
def administrator_access(
    current_user: User = Depends(get_current_administrator),
) -> dict[str, str]:
    return {
        "message": "Administrator access granted",
        "user": current_user.email,
    }