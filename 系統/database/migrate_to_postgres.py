import os
import sqlite3
import pandas as pd
from sqlalchemy import create_engine
from db_config import get_db_engine, DATABASE_URL

def migrate_data():
    print("🚀 開始準備搬家資料庫...")
    
    # 1. Connect to Local SQLite
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sqlite_path = os.path.join(BASE_DIR, 'database', 'political_data.db')
    
    if not os.path.exists(sqlite_path):
        print("❌ 找不到本機 SQLite 資料庫，無法搬家！")
        return
        
    sqlite_engine = create_engine(f"sqlite:///{sqlite_path}")
    
    # 2. Check if cloud DB is configured
    if not DATABASE_URL or "sqlite" in DATABASE_URL:
        print("❌ 未設定雲端 PostgreSQL 連線字串 (DATABASE_URL)。請確認 .env 設定！")
        return
        
    print(f"🔗 連接到雲端資料庫: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'Hidden'}")
    pg_engine = get_db_engine()
    
    # Tables to migrate
    tables = [
        "locations",
        "region_profiles",
        "election_history",
        "news",
        "opinions"
    ]
    
    try:
        for table in tables:
            print(f"📦 正在讀取本機表單: {table} ...")
            try:
                df = pd.read_sql_table(table, sqlite_engine)
            except ValueError:
                print(f"   ⚠️ 表單 {table} 不存在，跳過。")
                continue
                
            if df.empty:
                print(f"   ⚠️ 表單 {table} 是空的，跳過。")
                continue
                
            print(f"   📤 正在寫入雲端: {table} ({len(df)} 筆資料) ...")
            df.to_sql(table, pg_engine, if_exists='replace', index=False)
            print(f"   ✅ {table} 搬家成功！")
            
        print("🎉 資料庫搬家大功告成！現在所有的資料都在雲端上了！")
    except Exception as e:
        print(f"❌ 搬家過程中發生錯誤: {e}")

if __name__ == "__main__":
    migrate_data()
