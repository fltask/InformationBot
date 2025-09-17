"""
Конфигурация подключения к базе данных и управление сессиями.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from database.models import Base

# Загружаем переменные окружения
load_dotenv()

# Получаем строку подключения из переменных окружения
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL не найден в переменных окружения")

# Создаем движок базы данных
engine = create_engine(DATABASE_URL)

# Создаем все таблицы
Base.metadata.create_all(bind=engine)

# Фабрика сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Генератор сессий базы данных.

    Открывает сессию, отдает ее в контексте работы,
    а после завершения — закрывает.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
