from sqlalchemy import ForeignKey, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.models import Base

class Radar(Base):
    __tablename__ = "radars"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    last_charge: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    battery_capacity: Mapped[int] = mapped_column(Integer)  # mWh
