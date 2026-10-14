"""Post 数据访问。"""

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from blog_api.models import Post


class PostRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, post: Post) -> Post:
        self.session.add(post)
        self.session.flush()
        return post

    def get_by_id(self, post_id: int) -> Post | None:
        stmt = (
            select(Post)
            .where(Post.id == post_id)
            .options(
                selectinload(Post.author),
                selectinload(Post.category),
                selectinload(Post.tags),
            )
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_slug(self, slug: str) -> Post | None:
        stmt = (
            select(Post)
            .where(Post.slug == slug)
            .options(
                selectinload(Post.author),
                selectinload(Post.category),
                selectinload(Post.tags),
            )
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def list_posts(
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
        """分页查询，返回 (posts, total)。"""
        stmt = select(Post)
        count_stmt = select(func.count(Post.id))

        # 过滤条件
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

        # 总数
        total = self.session.execute(count_stmt).scalar_one()

        # 排序
        if sort.startswith("-"):
            stmt = stmt.order_by(getattr(Post, sort[1:]).desc())
        else:
            stmt = stmt.order_by(getattr(Post, sort).asc())

        # 分页
        stmt = stmt.offset((page - 1) * size).limit(size)
        stmt = stmt.options(
            selectinload(Post.author),
            selectinload(Post.category),
            selectinload(Post.tags),
        )

        posts = list(self.session.execute(stmt).scalars().all())
        return posts, total

    def delete(self, post: Post) -> None:
        self.session.delete(post)
