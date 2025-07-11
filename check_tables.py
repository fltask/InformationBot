from sqlalchemy import create_engine, inspect
import os
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))
inspector = inspect(engine)

print("Список таблиц в базе данных:")
for table in inspector.get_table_names():
    print("-", table)