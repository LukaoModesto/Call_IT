import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category_model import Category
from app.models.department_model import Department
from app.schemas.category_schema import CategoryCreate
from app.schemas.department_schema import DepartmentCreate


def create_department(
    database: Session,
    department_data: DepartmentCreate,
) -> Department:
    department = Department(
        name=department_data.name,
        description=department_data.description,
    )

    database.add(department)
    database.commit()
    database.refresh(department)

    return department


def get_department_by_id(
    database: Session,
    department_id: uuid.UUID,
) -> Department | None:
    statement = select(Department).where(
        Department.id == department_id,
    )

    return database.scalar(statement)


def get_departments(
    database: Session,
) -> list[Department]:
    statement = (
        select(Department)
        .where(Department.is_active.is_(True))
        .order_by(Department.name.asc())
    )

    return list(database.scalars(statement).all())


def create_category(
    database: Session,
    category_data: CategoryCreate,
) -> Category:
    category = Category(
        department_id=category_data.department_id,
        name=category_data.name,
        description=category_data.description,
    )

    database.add(category)
    database.commit()
    database.refresh(category)

    return category


def get_category_by_id(
    database: Session,
    category_id: uuid.UUID,
) -> Category | None:
    statement = select(Category).where(
        Category.id == category_id,
    )

    return database.scalar(statement)


def get_active_category_by_id(
    database: Session,
    category_id: uuid.UUID,
) -> Category | None:
    statement = select(Category).where(
        Category.id == category_id,
        Category.is_active.is_(True),
    )

    return database.scalar(statement)


def get_categories(
    database: Session,
    department_id: uuid.UUID | None = None,
) -> list[Category]:
    statement = (
        select(Category)
        .where(Category.is_active.is_(True))
        .order_by(Category.name.asc())
    )

    if department_id is not None:
        statement = statement.where(
            Category.department_id == department_id,
        )

    return list(database.scalars(statement).all())