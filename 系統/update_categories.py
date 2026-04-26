import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_setup import News, Opinion
from scraper.categorizer import categorize_content

def update_categories():
    print("開始回溯更新現有資料的分類標籤...")
    db_path = 'sqlite:///database/political_data.db'
    engine = create_engine(db_path)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Update News
    news_items = session.query(News).filter(News.issue_category == None).all()
    n_count = 0
    for item in news_items:
        text = (item.title or "") + " " + (item.content or "")
        issue, party = categorize_content(text)
        item.issue_category = issue
        item.party_stance = party
        n_count += 1
        
    # Update Opinions
    opinion_items = session.query(Opinion).filter(Opinion.issue_category == None).all()
    o_count = 0
    for item in opinion_items:
        text = (item.title or "") + " " + (item.content or "")
        issue, party = categorize_content(text)
        item.issue_category = issue
        item.party_stance = party
        o_count += 1
        
    session.commit()
    session.close()
    print(f"分類標籤更新完成。共更新 {n_count} 筆新聞, {o_count} 筆輿情。")

if __name__ == "__main__":
    update_categories()
