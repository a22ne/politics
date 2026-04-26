
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
import time
from duckduckgo_search import DDGS
import re
from itertools import islice

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_setup import Location, Opinion, News

def get_db_session():
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def categorize_content(text):
    """簡單的雙層分類器"""
    issue_cat = "其他"
    party_cat = "未提及"
    
    # 議題字典
    issues = {
        "選舉造勢": ["造勢", "拜票", "民調", "參選", "選戰", "得票"],
        "施政與政策": ["政策", "施政", "法案", "預算", "建設", "補助"],
        "爭議事件": ["爭議", "弊案", "貪污", "炎上", "道歉", "失言"],
        "民生經濟": ["物價", "房價", "通膨", "薪資", "停電", "缺水"],
        "兩岸與外交": ["兩岸", "外交", "中共", "美國", "台海"]
    }
    
    # 政黨字典
    parties = {
        "國民黨": ["國民黨", "藍營", "蔣萬安", "侯友宜", "盧秀燕", "朱立倫"],
        "民進黨": ["民進黨", "綠營", "賴清德", "陳其邁", "黃偉哲", "蘇貞昌", "林右昌"],
        "民眾黨": ["民眾黨", "白營", "柯文哲", "黃珊珊", "高虹安"],
        "時代力量": ["時代力量", "王婉諭"],
    }
    
    # 判斷議題
    for k, v in issues.items():
        if any(keyword in text for keyword in v):
            issue_cat = k
            break
            
    # 判斷政黨
    for k, v in parties.items():
        if any(keyword in text for keyword in v):
            party_cat = k
            break
            
    return issue_cat, party_cat

def backfill_history(start_date="2022-12-01"):
    print(f"[{datetime.datetime.now()}] 開始執行歷史資料補齊 (Backfill)...")
    session = get_db_session()
    
    # Get major locations to search
    locations = session.query(Location).filter(Location.level == "county").all()
    
    # platforms to search - using credible domains
    queries = [
        "site:facebook.com 政治",
        "site:dcard.tw/f/trending 政治",
        "site:udn.com OR site:ltn.com.tw OR site:chinatimes.com OR site:cna.com.tw"
    ]
    
    added_opinions = 0
    added_news = 0
    
    with DDGS() as ddgs:
        for loc in locations:
            if loc.name == "全國": continue
            print(f"  搜尋 {loc.name} 歷史資料...")
            
            for base_query in queries:
                query_str = f"{loc.name} {base_query}"
                # Use tz-tw for Taiwan, avoid Amazon/Turkish spam
                try:
                    results = ddgs.text(query_str, region='tz-tw', safesearch='off', timelimit='y', max_results=10)
                    time.sleep(2) # sleep to avoid rate limit
                except Exception as e:
                    print(f"Search error: {e}")
                    continue
                
                for r in results:
                    title = r.get('title', '')
                    body = r.get('body', '')
                    url = r.get('href', '')
                    
                    if not title or not url: continue
                    # Verify if it's actually Chinese content (filter out Amazon spam)
                    if not re.search(r'[\u4e00-\u9fff]', title):
                        continue
                    
                    combined_text = title + " " + body
                    issue_cat, party_cat = categorize_content(combined_text)
                    
                    # 決定是 News 還是 Opinion
                    if "facebook" in url or "dcard" in url:
                        # Check if exists
                        if not session.query(Opinion).filter_by(url=url).first():
                            platform = "Facebook" if "facebook" in url else "Dcard"
                            session.add(Opinion(
                                platform=platform,
                                title=title[:199],
                                content=body,
                                url=url,
                                publish_time=datetime.datetime.strptime(start_date, "%Y-%m-%d"), # Approximation for backfill
                                location_id=loc.id,
                                issue_category=issue_cat,
                                party_stance=party_cat
                            ))
                            added_opinions += 1
                    else:
                        if not session.query(News).filter_by(url=url).first():
                            session.add(News(
                                source="網路搜尋",
                                title=title[:199],
                                content=body,
                                url=url,
                                publish_time=datetime.datetime.strptime(start_date, "%Y-%m-%d"),
                                location_id=loc.id,
                                issue_category=issue_cat,
                                party_stance=party_cat
                            ))
                            added_news += 1
            
            session.commit() # commit per location to save progress
            
    session.close()
    print(f"[{datetime.datetime.now()}] 歷史資料補齊完成。新增 {added_opinions} 筆論壇資料, {added_news} 筆新聞資料。")

if __name__ == "__main__":
    backfill_history()
