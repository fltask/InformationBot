from database.models import Base
from database.config import engine


def init_database():
    """Инициализация базы данных - создание всех таблиц"""
    Base.metadata.create_all(bind=engine)
    print("База данных инициализирована успешно!")


if __name__ == "__main__":
    init_database()
