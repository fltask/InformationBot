import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import models  # <--- добавьте эту строку!
from database.base import Base

target_metadata = Base.metadata

from logging.config import fileConfig
from sqlalchemy import create_engine
from alembic import context

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Получаем строку подключения из alembic.ini

from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise ValueError("DATABASE_URL не задана или пуста! Пропишите её в .env, например: DATABASE_URL=sqlite:///bot.db")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = create_engine(db_url)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


# Для отладки можно оставить вывод:
print("TABLES:")
for t in target_metadata.tables:
    print("-", t)
print("DB URL:", db_url)
