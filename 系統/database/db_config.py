import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Load .env file if it exists
load_dotenv()

# Cloud database URL
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    # Fallback to local SQLite
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'database', 'political_data.db')}"

if DATABASE_URL:
    # 統一使用 postgresql+pg8000（純 Python，不依賴 psycopg2 二進位檔）
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+pg8000://", 1)
    elif DATABASE_URL.startswith("postgresql://") and "+pg8000" not in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+pg8000://", 1)

def get_db_engine():
    return create_engine(DATABASE_URL)
