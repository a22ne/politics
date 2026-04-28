import time
import schedule
import datetime
import sys
import os
import threading

# ── 確保專案根目錄在 Python 路徑中
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# ── 強制載入 .env（Supabase 金鑰）
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE_DIR, '.env'), override=True)
    print("✅ .env 已載入")
except ImportError:
    print("⚠️  python-dotenv 未安裝，請執行 pip install python-dotenv")

# ── 預先 import 所有爬蟲函式
from scraper.news_spider import scrape_yahoo_news
from scraper.forum_spider import scrape_ptt_hatepolitics
from scraper.backfill_spider import backfill_history

# ──────────────────────────────────────
# 【即時新聞】每 2 小時跑一次
# ──────────────────────────────────────
def run_realtime_scrapers():
    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n[{ts}] 🚀 即時爬蟲啟動...")

    print("  📰 抓取 Yahoo 政治新聞...")
    try:
        scrape_yahoo_news()
    except Exception as e:
        print(f"  ⚠️  新聞爬蟲錯誤: {e}")

    print("  💬 抓取 PTT 政黑板...")
    try:
        scrape_ptt_hatepolitics()
    except Exception as e:
        print(f"  ⚠️  論壇爬蟲錯誤: {e}")

    ts2 = datetime.datetime.now().strftime('%H:%M:%S')
    print(f"  [{ts2}] ✅ 即時資料已同步到雲端！下次執行：2 小時後")

# ──────────────────────────────────────
# 【歷史資料】背景執行一次
# ──────────────────────────────────────
def run_backfill_in_background():
    print("\n[背景] 📚 歷史資料補齊爬蟲啟動（需要較長時間，請勿關閉視窗）...")
    try:
        backfill_history()
        print("[背景] ✅ 歷史資料補齊完成！")
    except Exception as e:
        print(f"[背景] ⚠️  歷史資料補齊錯誤: {e}")
        import traceback
        traceback.print_exc()

# ──────────────────────────────────────
# 主程式
# ──────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("🤖  台灣政治情報系統 — 全自動爬蟲守衛")
    print("=" * 55)
    print("📌  即時新聞：每 2 小時自動抓取一次")
    print("📌  歷史資料：背景執行（2022 至今）")
    print("⚠️   請勿關閉此視窗，關閉後爬蟲停止！")
    print("=" * 55)

    # 1. 先跑一次即時爬蟲
    run_realtime_scrapers()

    # 2. 在背景執行緒跑歷史補齊
    backfill_thread = threading.Thread(target=run_backfill_in_background, daemon=True)
    backfill_thread.start()

    # 3. 排程：每 2 小時重複即時爬蟲
    schedule.every(2).hours.do(run_realtime_scrapers)

    print("\n⏳ 系統運行中，等待下一輪即時抓取...\n")

    # 4. 主迴圈
    while True:
        schedule.run_pending()
        time.sleep(60)

