from app.db.database import Base

from datetime import datetime
from sqlalchemy import BigInteger, String, DateTime, Boolean, Text
from dateutil.tz import tzutc
from sqlalchemy.orm import Mapped, mapped_column


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    send_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    repeat: Mapped[str | None] = mapped_column(String, nullable=True)  # None, 'daily', 'weekly', 'monthly'
    is_sent: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    dt_created: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, 
        default=lambda: datetime.now(tzutc())
    )
    dt_updated: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
        default=lambda: datetime.now(tzutc()),
        onupdate=lambda: datetime.now(tzutc())
    )

    def __repr__(self) -> str:
        return (
            f"<Notification(id={self.id}, telegram_id={self.telegram_id}, send_at={self.send_at}, repeat={self.repeat}, is_sent={self.is_sent})>"
        )
