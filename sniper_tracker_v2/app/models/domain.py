from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, BigInteger, Boolean, Integer, ForeignKey, DateTime, Numeric, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True) # Например: "Free", "Pro"
    price: Mapped[int] = mapped_column(Integer, default=0) # Цена в гривнах
    max_active_tasks: Mapped[int] = mapped_column(Integer, default=1) # Допустимое кол-во задач
    check_interval_minutes: Mapped[int] = mapped_column(Integer, default=60) # Интервал парсинга

    users: Mapped[List["User"]] = relationship(back_populates="plan")

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    telegram_chat_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    
    # НОВОЕ ПОЛЕ ДЛЯ ПРИВЯЗКИ TELEGRAM (Deep Linking)
    telegram_connect_token: Mapped[Optional[str]] = mapped_column(String(100), unique=True, index=True, nullable=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Старые поля можно оставить для совместимости, но логика будет опираться на plan_id
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    premium_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # НОВЫЕ ПОЛЯ ДЛЯ СИСТЕМЫ ТАРИФОВ
    plan_id: Mapped[Optional[int]] = mapped_column(ForeignKey("subscription_plans.id"), nullable=True)
    plan: Mapped[Optional["SubscriptionPlan"]] = relationship(back_populates="users")

    tasks: Mapped[List["SearchTask"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    payments: Mapped[List["Payment"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class SearchTask(Base):
    __tablename__ = "search_tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False) # Сюда вставляем готовую ссылку с OLX

    # Специфика недвижимости
    min_price: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_price: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    rooms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    owner_only: Mapped[bool] = mapped_column(Boolean, default=False)

    check_interval_minutes: Mapped[int] = mapped_column(Integer, default=30)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # НОВОЕ ПОЛЕ ДЛЯ ПЛАНИРОВЩИКА CELERY
    last_checked: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    owner: Mapped["User"] = relationship(back_populates="tasks")
    ads: Mapped[List["ScrapedAd"]] = relationship(back_populates="task", cascade="all, delete-orphan")

class ScrapedAd(Base):
    __tablename__ = "scraped_ads"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("search_tasks.id"), nullable=False)
    external_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    seller_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    task: Mapped["SearchTask"] = relationship(back_populates="ads")

class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    payment_intent_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    user: Mapped["User"] = relationship(back_populates="payments")