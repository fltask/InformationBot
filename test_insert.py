from database.db import SessionLocal
from database.models import User, Log

session = SessionLocal()

# Создаем пользователя
new_user = User(
    telegram_id="123456789",
    name="Юрий",
    subscription_settings="weather:daily"
)

session.add(new_user)
session.commit()

# Лог действия
new_log = Log(
    user_id=new_user.id,
    command="/start"
)

session.add(new_log)
session.commit()

print("Тестовая запись добавлена!")