
import sys
import os

# ── 強制從專案根目錄載入 .env（不管從哪裡呼叫本腳本都能找到 Supabase 金鑰）
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, _ROOT)
_env_path = os.path.join(_ROOT, '.env')
try:
    from dotenv import load_dotenv
    load_dotenv(_env_path, override=True)
except ImportError:
    pass

try:
    from database.db_config import get_db_engine
except ImportError:
    from db_config import get_db_engine

import datetime
import time
import re
from sqlalchemy import text

def categorize_content(text_str):
    """簡單的雙層分類器"""
    issue_cat = "其他"
    party_cat = "未提及"
    issues = {
        "選舉造勢": ["造勢", "拜票", "民調", "參選", "選戰", "得票", "選舉"],
        "施政與政策": ["政策", "施政", "法案", "預算", "建設", "補助", "市政"],
        "爭議事件": ["爭議", "弊案", "貪污", "炎上", "道歉", "失言", "查辦", "風波"],
        "民生經濟": ["物價", "房價", "通膨", "薪資", "停電", "缺水", "交通"],
        "兩岸與外交": ["兩岸", "外交", "中共", "美國", "台海", "國防"],
    }
    parties = {
        "國民黨": ["國民黨", "藍營", "蔣萬安", "侯友宜", "盧秀燕", "朱立倫", "韓國瑜"],
        "民進黨": ["民進黨", "綠營", "賴清德", "陳其邁", "黃偉哲", "沈伯洋", "林右昌"],
        "民眾黨": ["民眾黨", "白營", "柯文哲", "黃珊珊", "高虹安"],
        "時代力量": ["時代力量", "王婉諭"],
    }
    for k, v in issues.items():
        if any(kw in text_str for kw in v):
            issue_cat = k
            break
    for k, v in parties.items():
        if any(kw in text_str for kw in v):
            party_cat = k
            break
    return issue_cat, party_cat


def search_one_location(loc_name, loc_id, engine):
    """對單一縣市執行搜尋，並寫入資料庫"""
    # 每次都重新建立 DDGS 實例，避免記憶體累積
    try:
        try:
            from ddgs import DDGS
        except ImportError:
            from duckduckgo_search import DDGS
    except ImportError:
        print(f"  [!] ddgs / duckduckgo_search 未安裝，跳過 {loc_name}")
        return 0, 0

    # 針對台灣可信媒體的搜尋模板
    queries = [
        f"{loc_name} 選舉 site:udn.com OR site:ltn.com.tw OR site:cna.com.tw",
        f"{loc_name} 政治 site:udn.com OR site:ltn.com.tw OR site:chinatimes.com",
        f"{loc_name} 議員 OR 縣長 OR 市長 2024 OR 2025 OR 2026",
    ]

    added_news = 0
    added_opinions = 0

    for q in queries:
        try:
            ddgs = DDGS()
            results = ddgs.text(q, region='zh-tw', safesearch='off', timelimit='y', max_results=8)
            time.sleep(2)  # 避免頻率限制
        except Exception as e:
            print(f"  [!] 搜尋 '{loc_name}' 失敗: {e}")
            continue

        if not results:
            continue

        for r in results:
            title = r.get('title', '')
            body = r.get('body', '')
            url = r.get('href', '')

            if not title or not url:
                continue
            # 確保是中文內容
            if not re.search(r'[\u4e00-\u9fff]', title):
                continue

            combined = title + " " + body
            issue_cat, party_cat = categorize_content(combined)

            is_opinion = "facebook" in url or "dcard" in url

            with engine.connect() as conn:
                try:
                    if is_opinion:
                        conn.execute(text("""
                            INSERT INTO opinions (platform, title, content, url, publish_time, engagement_score, location_id, issue_category, party_stance)
                            VALUES (:platform, :title, :content, :url, NOW(), 0, :loc_id, :issue_cat, :party_cat)
                            ON CONFLICT (url) DO NOTHING
                        """), {
                            "platform": "Facebook" if "facebook" in url else "Dcard",
                            "title": title[:200],
                            "content": body[:1000],
                            "url": url,
                            "loc_id": loc_id,
                            "issue_cat": issue_cat,
                            "party_cat": party_cat
                        })
                        added_opinions += 1
                    else:
                        conn.execute(text("""
                            INSERT INTO news (source, title, content, url, publish_time, location_id, issue_category, party_stance)
                            VALUES (:source, :title, :content, :url, NOW(), :loc_id, :issue_cat, :party_cat)
                            ON CONFLICT (url) DO NOTHING
                        """), {
                            "source": "歷史搜尋",
                            "title": title[:200],
                            "content": body[:1000],
                            "url": url,
                            "loc_id": loc_id,
                            "issue_cat": issue_cat,
                            "party_cat": party_cat
                        })
                        added_news += 1
                    conn.commit()
                except Exception as e:
                    pass  # 重複或其他錯誤直接略過

    return added_news, added_opinions


def backfill_history():
    print(f"[{datetime.datetime.now()}] 開始執行歷史資料補齊 (Backfill)...")
    engine = get_db_engine()

    # 取得所有縣市
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, name FROM locations WHERE level='county' AND name IS NOT NULL AND name != '全國'"))
        locations = [(row[0], row[1]) for row in result.fetchall()]

    total_news = 0
    total_opinions = 0

    for loc_id, loc_name in locations:
        print(f"  🔍 搜尋 {loc_name} 歷史資料...", end=" ", flush=True)
        try:
            n, o = search_one_location(loc_name, loc_id, engine)
            print(f"新聞+{n} / 論壇+{o}")
            total_news += n
            total_opinions += o
        except Exception as e:
            # 即使某個縣市崩潰，繼續下一個
            print(f"跳過（{e}）")

        time.sleep(3)  # 每縣市之間等 3 秒，避免被封鎖

    print(f"[{datetime.datetime.now()}] ✅ 歷史資料補齊完成！共新增 {total_news} 筆新聞、{total_opinions} 筆論壇資料。")


if __name__ == "__main__":
    backfill_history()
