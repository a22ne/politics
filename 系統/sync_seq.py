from database.db_config import get_db_engine
from sqlalchemy import text
engine = get_db_engine()
with engine.begin() as conn:
    conn.execute(text("SELECT setval('locations_id_seq', COALESCE((SELECT MAX(id) FROM locations), 1))"))
    conn.execute(text("SELECT setval('election_history_id_seq', COALESCE((SELECT MAX(id) FROM election_history), 1))"))
print('Sequences synced!')
