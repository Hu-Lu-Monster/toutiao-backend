from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from models.news import News
from models.users import User

class Base(DeclarativeBase):
    pass
#
class History(Base):
    __tablename__ = "history"

    __table_args__ = (
        UniqueConstraint("user_id", "news_id", name="user_news_unique"),
        Index("fk_favorite_user_idx", "user_id"),
        Index("fk_favorite_news_idx", "news_id"),
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="浏览历史ID"
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            User.id,
            name="fk_favorite_user",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        comment="用户ID",
    )
    news_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            News.id,
            name="fk_favorite_news",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        comment="新闻ID",
    )
    view_time: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False, comment="浏览时间"
    )

    def __repr__(self):
        return (
            f"<History(id={self.id}, user_id={self.user_id}, "
            f"news_id={self.news_id}, created_at={self.view_time})>"
        )
