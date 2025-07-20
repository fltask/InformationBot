from sqlalchemy.orm import Session
from database.models import User, Log


def create_user(db: Session, telegram_id: int, name: str) -> User:
    """Создать нового пользователя"""
    db_user = User(telegram_id=telegram_id, name=name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_telegram_id(db: Session, telegram_id: int) -> User:
    """Получить пользователя по Telegram ID"""
    return db.query(User).filter(User.telegram_id == telegram_id).first()


def get_or_create_user(db: Session, telegram_id: int, name: str) -> User:
    """Получить пользователя или создать нового"""
    user = get_user_by_telegram_id(db, telegram_id)
    if not user:
        user = create_user(db, telegram_id, name)
    return user


def create_log(db: Session, user_id: int, command: str) -> Log:
    """Создать лог запроса"""
    db_log = Log(user_id=user_id, command=command)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_user_logs(db: Session, user_id: int, limit: int = 10) -> list[Log]:
    """Получить логи пользователя"""
    return db.query(Log).filter(Log.user_id == user_id).order_by(Log.timestamp.desc()).limit(limit).all()


def update_user_subscription(db: Session, user_id: int, subscription_settings: str) -> User:
    """Обновить настройки подписки пользователя"""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.subscription_settings = subscription_settings
        db.commit()
        db.refresh(user)
    return user
