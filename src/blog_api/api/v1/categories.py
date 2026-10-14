"""Category API。"""

from fastapi import APIRouter, status

from blog_api.api.deps import DbSession
from blog_api.models import Category
from blog_api.schemas import CategoryCreate, CategoryResponse, CategoryUpdate
from blog_api.services import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(data: CategoryCreate, db: DbSession) -> Category:
    """创建分类。"""
    service = CategoryService(db)
    return service.create(data)


@router.get("", response_model=list[CategoryResponse])
def list_categories(db: DbSession) -> list[Category]:
    """分类列表。"""
    service = CategoryService(db)
    return service.list_all()


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: DbSession) -> Category:
    """分类详情。"""
    service = CategoryService(db)
    return service.get(category_id)


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, data: CategoryUpdate, db: DbSession) -> Category:
    """更新分类。"""
    service = CategoryService(db)
    return service.update(category_id, data)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: DbSession) -> None:
    """删除分类。"""
    service = CategoryService(db)
    service.delete(category_id)
