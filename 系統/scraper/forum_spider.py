
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
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_setup import Location, Opinion

def get_db_session():
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def scrape_ptt_hatepolitics():
    print(f"[{datetime.datetime.now()}] 開始抓取 PTT 政黑板輿情...")
    session = get_db_session()
    
    # Get all locations
    locations = session.query(Location).all()
    loc_dict = {loc.name: loc.id for loc in locations}
    
    url = "https://www.ptt.cc/bbs/HatePolitics/index.html"
    headers = {"User-Agent": "Mozilla/5.0"}
    cookies = {"over18": "1"}
    
    try:
        response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching PTT: {e}")
        session.close()
        return

    soup = BeautifulSoup(response.text, "html.parser")
    posts = soup.find_all("div", class_="r-ent")
    
    added_count = 0
    for post in posts:
        title_tag = post.find("div", class_="title").find("a")
        if not title_tag:
            continue
            
        title = title_tag.text.strip()
        if "公告" in title:
            continue
            
        link = "https://www.ptt.cc" + title_tag["href"]
        
        # Check if already exists
        if session.query(Opinion).filter_by(url=link).first():
            continue
            
        nrec_tag = post.find("div", class_="nrec").text.strip()
        score = 0
        if nrec_tag == "爆":
            score = 100
        elif nrec_tag.startswith("X"):
            score = -10
        elif nrec_tag.isdigit():
            score = int(nrec_tag)
            
        # Determine location based on title
        loc_id = None
        for loc_name, l_id in loc_dict.items():
            if loc_name in title or loc_name.replace("市", "").replace("縣", "") in title:
                if loc_name != "全國":
                    loc_id = l_id
                    break
        
        if not loc_id:
            loc_id = loc_dict.get("全國")
            
        # Categorize
        from scraper.categorizer import categorize_content
        issue_cat, party_cat = categorize_content(title)
            
        opinion_item = Opinion(
            platform="PTT政黑板",
            title=title,
            content="", # Not scraping content for performance, just title
            url=link,
            publish_time=datetime.datetime.utcnow(),
            engagement_score=score,
            location_id=loc_id,
            issue_category=issue_cat,
            party_stance=party_cat
        )
        session.add(opinion_item)
        added_count += 1
        
    session.commit()
    session.close()
    print(f"[{datetime.datetime.now()}] PTT 抓取完成，共新增 {added_count} 筆資料。")

if __name__ == "__main__":
    scrape_ptt_hatepolitics()
