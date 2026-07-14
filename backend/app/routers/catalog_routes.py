import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_administrator,
    get_current_any_user,
)
from app.database.session import get_db
from app.models.category_model import Category
from app.models.department_model import Department
from app.models.user_model import User
from app.schemas.category_schema import CategoryCreate, CategoryResponse
from app.schemas.department_schema import DepartmentCreate, DepartmentResponse
from app.services.catalog_service import (
    create_category,
    create_department,
    get_categories,
    get_department_by_id,
    get_departments,
)


router = APIRouter(
    prefix="/catalog",
    tags=["Catalog"],
)


@router.post(
    "/departments",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_department(
    department_data: DepartmentCreate,
    database: Session = Depends(get_db),
    _: User = Depends(get_current_administrator),
) -> Department:
    return create_department(
        database=database,
        department_data=department_data,
    )


@router.get(
    "/departments",
    response_model=list[DepartmentResponse],
)
def list_departments(
    database: Session = Depends(get_db),
    _: User = Depends(get_current_any_user),
) -> list[Department]:
    return get_departments(
        database=database,
    )


@router.post(
    "/categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_category(
    category_data: CategoryCreate,
    database: Session = Depends(get_db),
    _: User = Depends(get_current_administrator),
) -> Category:
    department = get_department_by_id(
        database=database,
        department_id=category_data.department_id,
    )

    if department is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found",
        )

    return create_category(
        database=database,
        category_data=category_data,
    )


@router.get(
    "/categories",
    response_model=list[CategoryResponse],
)
def list_categories(
    department_id: uuid.UUID | None = None,
    database: Session = Depends(get_db),
    _: User = Depends(get_current_any_user),
) -> list[Category]:
    return get_categories(
        database=database,
        department_id=department_id,
    )