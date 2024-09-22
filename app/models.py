from datetime import datetime, timezone
from hashlib import md5
from typing import Optional

import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login


# UserMixin 提供了四个通用方法，is_authenticated, is_active, is_anonymous, get_id
class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    # 反向关联，和 Post 建立双向通信
    posts: so.WriteOnlyMapped["Post"] = so.relationship(back_populates="author")

    def avatar(self, size):
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return f"https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}"

    # __repr__ 方法用于在调试和日志中打印对象，便于调试
    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Flask-Login 需要从 session 中读取当前用户状态
@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    # 用 lambda 来保证每次创建时都使用当前时间
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)

    author: so.Mapped[User] = so.relationship(back_populates="posts")

    def __repr__(self):
        return f"<Post {self.body}>"
