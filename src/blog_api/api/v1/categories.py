"""Category API。"""

from fastapi import APIRouter, status

from blog_api.api.deps import DbSession
from blog_api.models import Category
from blog_api.schemas import CategoryCreate, CategoryResponse, CategoryUpdate
from blog_api.services import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(data: CategoryCreate, db: DbSession) -> Category:
    service = CategoryService(db)
    return await service.create(data)


@router.get("", response_model=list[CategoryResponse])
async def list_categories(db: DbSession) -> list[Category]:
    service = CategoryService(db)
    return await service.list_all()


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, db: DbSession) -> Category:
    service = CategoryService(db)
    return await service.get(category_id)


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: int, data: CategoryUpdate, db: DbSession) -> Category:
    service = CategoryService(db)
    return await service.update(category_id, data)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int, db: DbSession) -> None:
    service = CategoryService(db)
    await service.delete(category_id)
