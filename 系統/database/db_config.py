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
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def get_db_engine():
    # 使用 psycopg2，避免 pg8000 的死鎖問題
    return create_engine(DATABASE_URL)
