"""Post 数据访问。"""

from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from blog_api.models import Post


class PostRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, post: Post) -> Post:
        self.session.add(post)
        await self.session.flush()
        return post

    async def get_by_id(self, post_id: int) -> Post | None:
        stmt = (
            select(Post)
            .where(Post.id == post_id)
            .options(
                selectinload(Post.author),
                selectinload(Post.category),
                selectinload(Post.tags),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Post | None:
        stmt = (
            select(Post)
            .where(Post.slug == slug)
            .options(
                selectinload(Post.author),
                selectinload(Post.category),
                selectinload(Post.tags),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_posts(
        self,
        *,
        page: int = 1,
        size: int = 20,
        status: str | None = None,
        category_id: int | None = None,
        author_id: int | None = None,
        tag_id: int | None = None,
        q: str | None = None,
        sort: str = "-created_at",
    ) -> tuple[list[Post], int]:
        stmt: Any = select(Post)
        count_stmt: Any = select(func.count(Post.id))

        conditions = []
        if status:
            conditions.append(Post.status == status)
        if category_id:
            conditions.append(Post.category_id == category_id)
        if author_id:
            conditions.append(Post.author_id == author_id)
        if tag_id:
            stmt = stmt.join(Post.tags).where(Post.tags.any(id=tag_id))
            count_stmt = count_stmt.join(Post.tags).where(Post.tags.any(id=tag_id))
        if q:
            conditions.append(
                or_(
                    Post.title.ilike(f"%{q}%"),
                    Post.content.ilike(f"%{q}%"),
                )
            )

        for cond in conditions:
            stmt = stmt.where(cond)
            count_stmt = count_stmt.where(cond)

        result = await self.session.execute(count_stmt)
        total: int = result.scalar_one()

        if sort.startswith("-"):
            stmt = stmt.order_by(getattr(Post, sort[1:]).desc())
        else:
            stmt = stmt.order_by(getattr(Post, sort).asc())

        stmt = stmt.offset((page - 1) * size).limit(size)
        stmt = stmt.options(
            selectinload(Post.author),
            selectinload(Post.category),
            selectinload(Post.tags),
        )
        result = await self.session.execute(stmt)
        posts: list[Post] = list(result.scalars().all())
        return posts, total

    async def delete(self, post: Post) -> None:
        await self.session.delete(post)
