"""
修復 Supabase PostgreSQL 中各表的主鍵自動遞增設定
(SQLite 會自動做，但 PostgreSQL 需要明確設定 SEQUENCE)
"""
import sys
import os
sys.path.insert(0, r'c:\Users\Anne\Desktop\系統')
from database.db_config import get_db_engine
from sqlalchemy import text

engine = get_db_engine()

fix_sql = """
-- 修復所有表格的 ID 序列，讓 PostgreSQL 能自動遞增
DO $$
DECLARE
    max_id integer;
BEGIN
    -- news table
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM news;
    PERFORM setval('news_id_seq', max_id + 1, false);
    
    -- opinions table  
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM opinions;
    PERFORM setval('opinions_id_seq', max_id + 1, false);
    
    -- locations table
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM locations;
    PERFORM setval('locations_id_seq', max_id + 1, false);
    
    -- politicians table
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM politicians;
    PERFORM setval('politicians_id_seq', max_id + 1, false);
    
    -- region_profiles table
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM region_profiles;
    PERFORM setval('region_profiles_id_seq', max_id + 1, false);
    
    -- election_history table
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM election_history;
    PERFORM setval('election_history_id_seq', max_id + 1, false);
    
    RAISE NOTICE '✅ 所有 ID 序列已修復！';
END;
$$;
"""

# 也嘗試直接設定 DEFAULT SEQUENCE (另一種方法)
fix_sql_v2 = """
ALTER TABLE news ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY;
ALTER TABLE opinions ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY;
"""

print("🔧 開始修復 PostgreSQL 序列...")
try:
    with engine.connect() as conn:
        conn.execute(text(fix_sql))
        conn.commit()
        print("✅ 序列修復成功！")
        
        # 驗證
        result = conn.execute(text("SELECT COUNT(*) FROM news"))
        print(f"新聞表格: {result.fetchone()[0]} 筆")
        
except Exception as e:
    print(f"❌ 方法一失敗: {e}")
    print("嘗試方法二：重新建立帶有 SERIAL 的表格設定...")
    try:
        with engine.connect() as conn:
            # 直接用 ALTER SEQUENCE 修正
            for table in ['news', 'opinions', 'locations', 'politicians', 'region_profiles', 'election_history']:
                try:
                    conn.execute(text(f"""
                        DO $$ BEGIN
                            IF EXISTS (SELECT 1 FROM pg_sequences WHERE sequencename = '{table}_id_seq') THEN
                                PERFORM setval('{table}_id_seq', COALESCE((SELECT MAX(id) FROM {table}), 0) + 1, false);
                            END IF;
                        END $$;
                    """))
                    print(f"  ✅ {table}_id_seq 已修復")
                except Exception as te:
                    print(f"  ⚠️ {table}: {te}")
            conn.commit()
    except Exception as e2:
        print(f"❌ 方法二也失敗: {e2}")

print("\n🔍 測試插入一筆新聞...")
try:
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO news (source, title, content, url, publish_time, location_id, issue_category, party_stance)
            VALUES ('測試', '測試新聞標題', '測試內容', 'http://test.com/unique123', NOW(), NULL, '其他', '未提及')
            ON CONFLICT (url) DO NOTHING
        """))
        conn.commit()
        result = conn.execute(text("SELECT COUNT(*) FROM news"))
        print(f"✅ 插入測試成功！新聞表格現有 {result.fetchone()[0]} 筆")
except Exception as e:
    print(f"❌ 插入測試失敗: {e}")
