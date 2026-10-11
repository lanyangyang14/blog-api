"""手动测试数据库操作。"""

from sqlalchemy import select

from blog_api.database import SessionLocal
from blog_api.models import User


def main():
    with SessionLocal() as session:
        # 先查有没有
        existing = session.execute(
            select(User).where(User.username == "alice")
        ).scalar_one_or_none()

        if existing:
            print(f"用户已存在: id={existing.id}, username={existing.username}")
            user = existing
        else:
            user = User(
                username="alice",
                email="alice@example.com",
                hashed_password="fake_hash",
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            print(f"创建用户: id={user.id}, username={user.username}")

        # 查询
        stmt = select(User).where(User.username == "alice")
        found = session.execute(stmt).scalar_one_or_none()
        print(f"查询用户: {found}")

        # 清理（可选）
        session.delete(found)
        session.commit()
        print("已删除")


if __name__ == "__main__":
    main()