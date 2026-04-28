import sys
sys.path.insert(0, r'c:\Users\Anne\Desktop\系統')
from scraper.backfill_spider import search_one_location
from database.db_config import get_db_engine
from sqlalchemy import text

engine = get_db_engine()
with engine.connect() as conn:
    r = conn.execute(text("SELECT id FROM locations WHERE name='台北市' LIMIT 1"))
    row = r.fetchone()
    taipei_id = row[0] if row else 1

print('測試台北市搜尋（只跑 1 個）...')
n, o = search_one_location('台北市', taipei_id, engine)
print(f'結果：新聞+{n} / 論壇+{o}')
print('測試完成，沒有崩潰！')
