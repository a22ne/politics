from database.db_config import get_db_engine
from sqlalchemy import text

def kill_idle_transactions():
    engine = get_db_engine()
    with engine.connect() as conn:
        # 找出所有超過 1 分鐘且卡在 idle in transaction 的連線並砍掉
        query = text("""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE state = 'idle in transaction'
            AND pid <> pg_backend_pid();
        """)
        try:
            conn.execute(query)
            conn.commit()
            print("Successfully killed idle transactions.")
        except Exception as e:
            print(f"Error killing transactions: {e}")

if __name__ == '__main__':
    kill_idle_transactions()
