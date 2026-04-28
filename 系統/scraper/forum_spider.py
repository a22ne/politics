
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from database.db_config import get_db_engine
except ImportError:
    from db_config import get_db_engine
import requests
from bs4 import BeautifulSoup
import datetime
from sqlalchemy import text

def get_engine():
    return get_db_engine()

def scrape_ptt_hatepolitics():
    print(f"[{datetime.datetime.now()}] 開始抓取 PTT 政黑板輿情...")
    engine = get_engine()

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from scraper.categorizer import categorize_content

    # Get all locations via raw SQL
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, name FROM locations WHERE name IS NOT NULL"))
        loc_dict = {row[1]: row[0] for row in result.fetchall()}

    url = "https://www.ptt.cc/bbs/HatePolitics/index.html"
    headers = {"User-Agent": "Mozilla/5.0"}
    cookies = {"over18": "1"}

    try:
        response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching PTT: {e}")
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
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id FROM opinions WHERE url = :url"), {"url": link})
            if result.fetchone():
                continue

        nrec_tag = post.find("div", class_="nrec").text.strip()
        score = 0
        if nrec_tag == "爆":
            score = 100
        elif nrec_tag.startswith("X"):
            score = -10
        elif nrec_tag.isdigit():
            score = int(nrec_tag)

        # Determine location
        loc_id = None
        for loc_name, l_id in loc_dict.items():
            if loc_name and (loc_name in title or loc_name.replace("市", "").replace("縣", "") in title):
                if loc_name != "全國":
                    loc_id = l_id
                    break

        if not loc_id:
            loc_id = loc_dict.get("全國")

        # Categorize
        issue_cat, party_cat = categorize_content(title)

        # Insert via raw SQL
        with engine.connect() as conn:
            try:
                conn.execute(text("""
                    INSERT INTO opinions (platform, title, content, url, publish_time, engagement_score, location_id, issue_category, party_stance)
                    VALUES (:platform, :title, :content, :url, :pub_time, :score, :location_id, :issue_cat, :party_cat)
                    ON CONFLICT (url) DO NOTHING
                """), {
                    "platform": "PTT政黑板",
                    "title": title[:200],
                    "content": "",
                    "url": link,
                    "pub_time": datetime.datetime.utcnow(),
                    "score": score,
                    "location_id": loc_id,
                    "issue_cat": issue_cat,
                    "party_cat": party_cat
                })
                conn.commit()
                added_count += 1
            except Exception as e:
                print(f"插入失敗: {e}")

    print(f"[{datetime.datetime.now()}] PTT 抓取完成，共新增 {added_count} 筆資料。")

if __name__ == "__main__":
    scrape_ptt_hatepolitics()
