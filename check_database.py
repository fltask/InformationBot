#!/usr/bin/env python3
"""
Скрипт для проверки базы данных
"""

from database.config import get_db
from database.crud import get_user_by_telegram_id, get_user_logs
from database.models import User, Log
from sqlalchemy.orm import Session


def check_database():
    """Проверка базы данных"""
    db = next(get_db())
    try:
        # Проверяем количество пользователей
        users_count = db.query(User).count()
        print(f"Количество пользователей в базе: {users_count}")

        # Проверяем количество логов
        logs_count = db.query(Log).count()
        print(f"Количество логов в базе: {logs_count}")

        # Показываем последние 5 пользователей
        print("\nПоследние 5 пользователей:")
        recent_users = db.query(User).order_by(User.registered_at.desc()).limit(5).all()
        for user in recent_users:
            print(
                f"ID: {user.id}, Telegram ID: {user.telegram_id}, Имя: {user.name}, Зарегистрирован: {user.registered_at}"
            )

        # Показываем последние 10 логов
        print("\nПоследние 10 логов:")
        recent_logs = db.query(Log).order_by(Log.timestamp.desc()).limit(10).all()
        for log in recent_logs:
            print(
                f"ID: {log.id}, Пользователь ID: {log.user_id}, Команда: {log.command}, Время: {log.timestamp}"
            )

    except Exception as e:
        print(f"Ошибка при проверке базы данных: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    check_database()
