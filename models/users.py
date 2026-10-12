from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, String, Integer, Text, ForeignKey, Index, Enum

#基类
class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        comment="创建时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间"
    )

#用户类
class User(Base):
    __tablename__ = 'user'
    #创建索引
    __table_args__ = (
        Index('username_UNIQUE', 'username'),
        Index('phone_UNIQUE', 'phone'),
    )
    id : Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    username : Mapped[str] = mapped_column(
        String(50),
        comment="用户名"
    )
    password : Mapped[str] = mapped_column(
        String(255),
        comment="密码（加密存储）"
    )
    nickname : Mapped[Optional[str]] = mapped_column(
        String(50),
        comment="昵称"
    )
    avatar : Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="头像URL"
    )
    gender : Mapped[Optional[str]] = mapped_column(
        Enum('male', 'female','unknown'),
        default="unknown",
        comment="性别"
    )
    bio : Mapped[Optional[str]] = mapped_column(
        String(500),
        comment="个人简介"
    )
    phone : Mapped[Optional[str]] = mapped_column(
        String(20),
        comment="手机号"
    )

class UserToken(Base):
    """用户令牌表 ORM 模型。"""

    __tablename__ = "user_token"

    __table_args__ = (
        Index("token_UNIQUE", "token", unique=True),
        Index("fk_user_token_user_idx", "user_id"),
    )

    # 令牌表只有 created_at，取消继承 Base 中的 updated_at 映射。
    updated_at = None

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="令牌ID"
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            User.id,
            name="fk_user_token_user",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        comment="用户ID",
    )
    token: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="令牌值"
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, comment="过期时间"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False, comment="创建时间"
    )

    def __repr__(self):
        return f"<UserToken(id={self.id}, user_id={self.user_id})>"
