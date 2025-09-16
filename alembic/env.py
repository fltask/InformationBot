from database.models import Base
from logging.config import fileConfig
import os
from dotenv import load_dotenv

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Загружаем переменные окружения из файла .env
load_dotenv()

# это объект конфигурации Alembic, который предоставляет
# доступ к значениям в используемом .ini файле.
config = context.config

# Интерпретируем файл конфигурации для логирования Python.
# Эта строка настраивает логгеры.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# добавьте объект MetaData вашей модели здесь
# для поддержки 'autogenerate'
target_metadata = Base.metadata

# другие значения из конфигурации, определенные потребностями env.py,
# могут быть получены:
# my_important_option = config.get_main_option("my_important_option")
# ... и т.д.


def run_migrations_offline() -> None:
    """Запускает миграции в 'офлайн' режиме.

    Это настраивает контекст только с URL
    и без Engine, хотя Engine также допустим
    здесь. Пропуская создание Engine
    нам даже не нужен DBAPI.

    Вызовы context.execute() здесь выводят данную строку в
    выходной скрипт.

    """
    # Получаем строку подключения из переменных окружения
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL не найден в переменных окружения")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Запускает миграции в 'онлайн' режиме.

    В этом сценарии нам нужно создать Engine
    и связать соединение с контекстом.

    """
    # Получаем строку подключения из переменных окружения
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL не найден в переменных окружения")

    # Создаем конфигурацию для подключения к базе данных
    configuration = config.get_section(config.config_ini_section)
    if configuration is None:
        configuration = {}
    configuration["sqlalchemy.url"] = database_url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
