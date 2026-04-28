
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from database.db_config import get_db_engine
except ImportError:
    from db_config import get_db_engine
import requests
import feedparser
import datetime
from sqlalchemy import text

def get_engine():
    return get_db_engine()

def scrape_yahoo_news():
    print(f"[{datetime.datetime.now()}] 開始抓取政治新聞...")
    engine = get_engine()

    # 分類器
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from scraper.categorizer import categorize_content

    # Get all locations via raw SQL
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, name FROM locations WHERE name IS NOT NULL"))
        loc_dict = {row[1]: row[0] for row in result.fetchall()}

    # 政治新聞 RSS (Yahoo)
    rss_url = "https://tw.news.yahoo.com/rss/politics"
    try:
        feed = feedparser.parse(rss_url)
    except Exception as e:
        print(f"RSS 讀取失敗: {e}")
        return

    added_count = 0
    for entry in feed.entries:
        title = entry.title
        link = entry.link
        try:
            pub_time = datetime.datetime(*entry.published_parsed[:6])
        except:
            pub_time = datetime.datetime.utcnow()

        summary = entry.get('summary', '')

        # Check if already exists
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id FROM news WHERE url = :url"), {"url": link})
            if result.fetchone():
                continue

        # Determine location
        loc_id = None
        for loc_name, l_id in loc_dict.items():
            if loc_name and (loc_name in title or loc_name in summary):
                if loc_name != "全國":
                    loc_id = l_id
                    break

        if not loc_id:
            loc_id = loc_dict.get("全國")

        # Categorize
        combined_text = title + " " + summary
        issue_cat, party_cat = categorize_content(combined_text)

        # Insert via raw SQL (bypasses ORM identity key issue)
        with engine.connect() as conn:
            try:
                conn.execute(text("""
                    INSERT INTO news (source, title, content, url, publish_time, location_id, issue_category, party_stance)
                    VALUES (:source, :title, :content, :url, :pub_time, :location_id, :issue_cat, :party_cat)
                    ON CONFLICT (url) DO NOTHING
                """), {
                    "source": "Yahoo新聞",
                    "title": title[:200],
                    "content": summary[:2000] if summary else "",
                    "url": link,
                    "pub_time": pub_time,
                    "location_id": loc_id,
                    "issue_cat": issue_cat,
                    "party_cat": party_cat
                })
                conn.commit()
                added_count += 1
            except Exception as e:
                print(f"插入失敗: {e}")

    print(f"[{datetime.datetime.now()}] 新聞抓取完成，共新增 {added_count} 筆資料。")

if __name__ == "__main__":
    scrape_yahoo_news()
