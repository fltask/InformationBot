from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

# Создаем базовый класс для моделей
Base = declarative_base()


class User(Base):
    """Модель пользователя"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    registered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    # JSON строка с настройками подписки
    subscription_settings = Column(Text, nullable=True)

    # Связь с логами
    logs = relationship("Log", back_populates="user")


class Log(Base):
    """Модель лога запросов"""

    __tablename__ = "logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    command = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Связь с пользователем
    user = relationship("User", back_populates="logs")
