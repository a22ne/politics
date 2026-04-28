"""
在 Supabase 中建立缺少的 UNIQUE INDEX (url 欄位)
"""
import sys
import os
sys.path.insert(0, r'c:\Users\Anne\Desktop\系統')
from database.db_config import get_db_engine
from sqlalchemy import text

engine = get_db_engine()

print("🔧 建立 UNIQUE INDEX for url 欄位...")
with engine.connect() as conn:
    try:
        conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS news_url_unique ON news(url)"))
        print("✅ news.url UNIQUE INDEX 建立成功")
    except Exception as e:
        print(f"news: {e}")
    
    try:
        conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS opinions_url_unique ON opinions(url)"))
        print("✅ opinions.url UNIQUE INDEX 建立成功")
    except Exception as e:
        print(f"opinions: {e}")
    
    conn.commit()

print("\n🔍 再次測試插入...")
with engine.connect() as conn:
    try:
        conn.execute(text("""
            INSERT INTO news (source, title, content, url, publish_time, location_id, issue_category, party_stance)
            VALUES ('測試', '測試新聞標題', '測試內容', 'http://test.com/unique123456', NOW(), NULL, '其他', '未提及')
        """))
        conn.commit()
        result = conn.execute(text("SELECT COUNT(*) FROM news"))
        print(f"✅ 插入成功！新聞表格現有 {result.fetchone()[0]} 筆")
    except Exception as e:
        print(f"❌ 插入失敗: {e}")
