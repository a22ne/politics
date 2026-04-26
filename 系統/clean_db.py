import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_setup import News, Opinion

def clean_db():
    db_path = 'sqlite:///database/political_data.db'
    engine = create_engine(db_path)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Delete garbage from backfill
    n1 = session.query(News).filter(News.source == "網路搜尋").delete()
    n2 = session.query(Opinion).filter(Opinion.platform.in_(["Facebook", "Dcard"])).delete()
    
    session.commit()
    session.close()
    print(f"Deleted {n1} garbage news and {n2} garbage opinions.")

if __name__ == "__main__":
    clean_db()
