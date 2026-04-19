import os
from sqlalchemy import create_engine
from app.models import Base
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

print("Подключение к базе данных...")
engine = create_engine(DATABASE_URL)

print("Создание таблиц...")
Base.metadata.create_all(bind=engine)
print("✅ Таблицы успешно созданы!")