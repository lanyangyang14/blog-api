"""Post 服务。"""

import logging
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from blog_api.exceptions import ConflictError, ForbiddenError, NotFoundError
from blog_api.logging_config import get_trace_id
from blog_api.models import Post, User
from blog_api.repositories import (
    CategoryRepository,
    PostRepository,
    TagRepository,
)
from blog_api.schemas import PostCreate, PostUpdate

logger = logging.getLogger(__name__)


class PostService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = PostRepository(session)
        self.category_repo = CategoryRepository(session)
        self.tag_repo = TagRepository(session)

    async def create(self, data: PostCreate, author: User) -> Post:
        if await self.repo.get_by_slug(data.slug):
            raise ConflictError(f"slug {data.slug!r} 已存在")

        if data.category_id and not await self.category_repo.get_by_id(data.category_id):
            raise NotFoundError("Category", data.category_id)

        tags = []
        for tag_id in data.tag_ids:
            tag = await self.tag_repo.get_by_id(tag_id)
            if not tag:
                raise NotFoundError("Tag", tag_id)
            tags.append(tag)

        post = Post(
            title=data.title,
            slug=data.slug,
            summary=data.summary,
            content=data.content,
            status=data.status,
            category_id=data.category_id,
            author_id=author.id,
            published_at=datetime.now() if data.status == "published" else None,
        )
        post.tags = tags

        await self.repo.create(post)
        await self.session.commit()
        refreshed = await self.repo.get_by_id(post.id)
        if refreshed is None:
            raise RuntimeError("Post not found after commit")
            # 如果发布了，异步通知订阅者
        if refreshed.status == "published":
            from blog_api.tasks.notification import notify_new_post

            notify_new_post.delay(
                post_id=refreshed.id,
                title=refreshed.title,
                slug=refreshed.slug,
                author_name=author.username,
            )
        logger.info("文章创建成功: id=%s, title=%s", refreshed.id, refreshed.title)
        return refreshed

    async def get(self, post_id: int) -> Post:
        post = await self.repo.get_by_id(post_id)
        if not post:
            raise NotFoundError("Post", post_id)
        return post

    async def get_by_slug(self, slug: str) -> Post:
        post = await self.repo.get_by_slug(slug)
        if not post:
            raise NotFoundError("Post", slug)
        post.view_count += 1
        await self.session.commit()
        await self.session.refresh(post)
        return post

    async def list_posts(self, **filters: Any) -> tuple[list[Post], int]:
        return await self.repo.list_posts(**filters)

    async def update(self, post_id: int, data: PostUpdate, current_user: User) -> Post:
        post = await self.get(post_id)
        old_status = post.status
        if post.author_id != current_user.id and current_user.role != "admin":
            raise ForbiddenError("无权修改此文章")

        if data.slug and data.slug != post.slug and await self.repo.get_by_slug(data.slug):
            raise ConflictError(f"slug {data.slug!r} 已存在")

        if data.category_id and not await self.category_repo.get_by_id(data.category_id):
            raise NotFoundError("Category", data.category_id)

        update_data = data.model_dump(exclude_unset=True, exclude={"tag_ids"})
        for key, value in update_data.items():
            setattr(post, key, value)

        if data.status == "published" and not post.published_at:
            post.published_at = datetime.now()

        if data.tag_ids is not None:
            tags = []
            for tag_id in data.tag_ids:
                tag = await self.tag_repo.get_by_id(tag_id)
                if not tag:
                    raise NotFoundError("Tag", tag_id)
                tags.append(tag)
            post.tags = tags

        await self.session.commit()
        refreshed = await self.repo.get_by_id(post_id)
        if refreshed is None:
            raise RuntimeError("Post not found after update")
            # 刚刚发布
        if old_status != "published" and refreshed.status == "published":
            from blog_api.tasks.notification import notify_new_post

            notify_new_post.delay(
                post_id=refreshed.id,
                title=refreshed.title,
                slug=refreshed.slug,
                author_name=current_user.username,
                trace_id=get_trace_id(),
            )
        return refreshed

    async def delete(self, post_id: int, current_user: User) -> None:
        post = await self.get(post_id)
        if post.author_id != current_user.id and current_user.role != "admin":
            raise ForbiddenError("无权删除此文章")
        await self.repo.delete(post)
        await self.session.commit()
        # 异步清理关联数据
        from blog_api.tasks.notification import cleanup_post_data

        cleanup_post_data.delay(post_id=post_id)
