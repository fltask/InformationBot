from sqlalchemy import create_engine, inspect
import os
from dotenv import load_dotenv

engine = create_engine("sqlite:///bot.db")  # <-- убедись, что путь точно совпадает
inspector = inspect(engine)
print("Список таблиц:", inspector.get_table_names())

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))
inspector = inspect(engine)

print("Список таблиц в базе данных:")
for table in inspector.get_table_names():
    print("-", table)