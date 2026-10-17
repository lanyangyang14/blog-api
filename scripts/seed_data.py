"""插入测试数据。

用法：
    python scripts/seed_data.py
"""

import asyncio
from datetime import UTC, datetime

from sqlalchemy import select

from blog_api.database import AsyncSessionLocal
from blog_api.models import Category, Post, Tag, User


async def seed_data() -> None:
    async with AsyncSessionLocal() as session:
        # 1. 找一个用户（作者）
        result = await session.execute(select(User).limit(1))
        user = result.scalar_one_or_none()
        if not user:
            print("❌ 数据库中没有任何用户，请先在前端或 /docs 中注册一个账号。")
            return
        print(f"✅ 使用作者: {user.username} (id={user.id})")

        # 2. 创建分类
        cat_result = await session.execute(select(Category).where(Category.slug == "tech"))
        category = cat_result.scalar_one_or_none()
        if not category:
            category = Category(name="技术分享", slug="tech", description="编程与开发")
            session.add(category)
            await session.flush()
            print("✅ 创建分类: 技术分享")

        # 3. 创建标签
        tag_result = await session.execute(select(Tag).where(Tag.slug == "python"))
        tag = tag_result.scalar_one_or_none()
        if not tag:
            tag = Tag(name="Python", slug="python")
            session.add(tag)
            await session.flush()
            print("✅ 创建标签: Python")

        # 4. 创建文章
        titles = [
            "FastAPI 从入门到实战",
            "SQLAlchemy 2.0 异步踩坑记录",
            "Vue 3 + Element Plus 快速搭建后台",
        ]

        for i, title in enumerate(titles, 1):
            slug = f"test-post-{i}"

            # 检查是否已存在
            post_result = await session.execute(select(Post).where(Post.slug == slug))
            if post_result.scalar_one_or_none():
                print(f"⏩ 文章 {slug} 已存在，跳过")
                continue

            post = Post(
                title=title,
                slug=slug,
                summary=f"这是《{title}》的摘要内容，用于测试前端展示效果。",
                content=f"## {title}\n\n这里是文章的正文内容。\n\n你可以在这里写很长很长的一段话...\n\n- 支持列表\n- 支持代码块\n\n```python\nprint('Hello World')\n```",
                status="published",
                author_id=user.id,
                category_id=category.id,
                published_at=datetime.now(UTC).replace(tzinfo=None),
            )
            post.tags.append(tag)
            session.add(post)
            print(f"✅ 创建文章: {title}")

        await session.commit()
        print("🎉 所有数据插入成功！")


if __name__ == "__main__":
    asyncio.run(seed_data())
