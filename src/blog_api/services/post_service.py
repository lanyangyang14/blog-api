"""Post 服务。"""

import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from blog_api.exceptions import ConflictError, ForbiddenError, NotFoundError
from blog_api.models import Post, User
from blog_api.repositories import CategoryRepository, PostRepository, TagRepository
from blog_api.schemas import PostCreate, PostUpdate

logger = logging.getLogger(__name__)


class PostService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = PostRepository(session)
        self.category_repo = CategoryRepository(session)
        self.tag_repo = TagRepository(session)

    def create(self, data: PostCreate, author: User) -> Post:
        if self.repo.get_by_slug(data.slug):
            raise ConflictError(f"slug {data.slug!r} 已存在")

        if data.category_id and not self.category_repo.get_by_id(data.category_id):
            raise NotFoundError("Category", data.category_id)

        # 处理标签
        tags = []
        for tag_id in data.tag_ids:
            tag = self.tag_repo.get_by_id(tag_id)
            if not tag:
                raise NotFoundError("Tag", tag_id)
            tags.append(tag)

        # 构建 Post
        post = Post(
            title=data.title,
            slug=data.slug,
            summary=data.summary,
            content=data.content,
            status=data.status,
            category_id=data.category_id,
            author_id=author.id,
            published_at=datetime.now(UTC) if data.status == "published" else None,
        )
        post.tags = tags

        self.repo.create(post)
        self.session.commit()
        self.session.refresh(post)
        logger.info("文章创建成功: id=%s, title=%s", post.id, post.title)
        return post

    def get(self, post_id: int) -> Post:
        post = self.repo.get_by_id(post_id)
        if not post:
            raise NotFoundError("Post", post_id)
        return post

    def get_by_slug(self, slug: str) -> Post:
        post = self.repo.get_by_slug(slug)
        if not post:
            raise NotFoundError("Post", slug)
        # 浏览量 +1
        post.view_count += 1
        self.session.commit()
        self.session.refresh(post)
        return post

    def list_posts(self, **filters: Any) -> tuple[list[Post], int]:
        return self.repo.list_posts(**filters)

    def update(self, post_id: int, data: PostUpdate, current_user: User) -> Post:
        post = self.get(post_id)

        # 权限：只能作者或管理员
        if post.author_id != current_user.id and current_user.role != "admin":
            raise ForbiddenError("无权修改此文章")

        # slug 唯一性
        if data.slug and data.slug != post.slug and self.repo.get_by_slug(data.slug):
            raise ConflictError(f"slug {data.slug!r} 已存在")

        # 分类存在性
        if data.category_id and not self.category_repo.get_by_id(data.category_id):
            raise NotFoundError("Category", data.category_id)

        # 更新字段
        update_data = data.model_dump(exclude_unset=True, exclude={"tag_ids"})
        for key, value in update_data.items():
            setattr(post, key, value)

        # 状态变成 published 时设置 published_at
        if data.status == "published" and not post.published_at:
            post.published_at = datetime.now(UTC)

        # 更新标签
        if data.tag_ids is not None:
            tags = []
            for tag_id in data.tag_ids:
                tag = self.tag_repo.get_by_id(tag_id)
                if not tag:
                    raise NotFoundError("Tag", tag_id)
                tags.append(tag)
            post.tags = tags

        self.session.commit()
        self.session.refresh(post)
        return post

    def delete(self, post_id: int, current_user: User) -> None:
        post = self.get(post_id)
        if post.author_id != current_user.id and current_user.role != "admin":
            raise ForbiddenError("无权删除此文章")
        self.repo.delete(post)
        self.session.commit()
