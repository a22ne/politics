
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from database.db_config import get_db_engine
except ImportError:
    from db_config import get_db_engine
import sys
import os
import requests
from bs4 import BeautifulSoup
import feedparser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_setup import Location, Politician, News

def get_db_session():
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def scrape_yahoo_news():
    print(f"[{datetime.datetime.now()}] 開始抓取政治新聞...")
    session = get_db_session()
    
    # Get all locations
    locations = session.query(Location).all()
    loc_dict = {loc.name: loc.id for loc in locations}
    
    # 政治新聞 RSS (Yahoo)
    rss_url = "https://tw.news.yahoo.com/rss/politics"
    feed = feedparser.parse(rss_url)
    
    added_count = 0
    for entry in feed.entries:
        title = entry.title
        link = entry.link
        # parse publish time (RFC 822)
        try:
            pub_time = datetime.datetime(*entry.published_parsed[:6])
        except:
            pub_time = datetime.datetime.utcnow()
            
        summary = entry.get('summary', '')
        
        # Check if already exists
        if session.query(News).filter_by(url=link).first():
            continue
            
        # Determine location
        loc_id = None
        for loc_name, l_id in loc_dict.items():
            if loc_name in title or loc_name in summary:
                if loc_name != "全國":
                    loc_id = l_id
                    break
        
        # If no specific county, assign to "全國"
        if not loc_id:
            loc_id = loc_dict.get("全國")
            
        # Categorize
        combined_text = title + " " + summary
        from scraper.categorizer import categorize_content
        issue_cat, party_cat = categorize_content(combined_text)
            
        news_item = News(
            source="Yahoo新聞",
            title=title,
            content=summary,
            url=link,
            publish_time=pub_time,
            location_id=loc_id,
            issue_category=issue_cat,
            party_stance=party_cat
        )
        session.add(news_item)
        added_count += 1
        
    session.commit()
    session.close()
    print(f"[{datetime.datetime.now()}] 新聞抓取完成，共新增 {added_count} 筆資料。")

if __name__ == "__main__":
    scrape_yahoo_news()
