import sys, os
sys.path.insert(0, r'c:\Users\Anne\Desktop\系統')
from database.db_config import get_db_engine, DATABASE_URL
from sqlalchemy import text

print('連線字串:', DATABASE_URL[:60], '...')
engine = get_db_engine()
try:
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1 as test'))
        print('✅ Supabase 連線成功！')
        result2 = conn.execute(text("SELECT COUNT(*) FROM news"))
        print('新聞筆數:', result2.fetchone()[0])
        result3 = conn.execute(text("SELECT COUNT(*) FROM opinions"))
        print('輿情筆數:', result3.fetchone()[0])
        result4 = conn.execute(text("SELECT COUNT(*) FROM locations"))
        print('地區筆數:', result4.fetchone()[0])
        result5 = conn.execute(text("SELECT COUNT(*) FROM election_history"))
        print('選舉歷史筆數:', result5.fetchone()[0])
except Exception as e:
    print('❌ 連線失敗:', e)
    import traceback
    traceback.print_exc()
