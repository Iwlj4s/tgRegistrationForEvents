from sqlalchemy import String, Integer, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class Events(Base):
    __tablename__ = 'events'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    event_name: Mapped[str] = mapped_column(Text, nullable=False)
    event_date: Mapped[str] = mapped_column(Text, nullable=False)
    event_time: Mapped[str] = mapped_column(Text, nullable=False)


class Users(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    phone: Mapped[int] = mapped_column(Integer, nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False)


class UsersEvents(Base):
    __tablename__ = 'usersEvents'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_event_id: Mapped[int] = mapped_column(Integer, ForeignKey('events.id'), nullable=False)
    user_event_name: Mapped[str] = mapped_column(Text, nullable=False)
    user_tg_id: Mapped[int] = mapped_column(Integer, nullable=False)
    user_name: Mapped[str] = mapped_column(String(150), nullable=False)
    user_phone: Mapped[int] = mapped_column(Integer, nullable=False)
    user_email: Mapped[str] = mapped_column(Text, nullable=False)


class ClosedEvents(Base):
    __tablename__ = 'closedEvents'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey('events.id'), nullable=False)
    event_name: Mapped[str] = mapped_column(Text, nullable=False)
    event_date: Mapped[str] = mapped_column(Text, nullable=False)
    event_time: Mapped[str] = mapped_column(Text, nullable=False)


class Admins(Base):
    __tablename__ = 'admins'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    phone: Mapped[int] = mapped_column(Integer, nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False)
