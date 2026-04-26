import time
import schedule
import subprocess
import datetime
import sys

import os

# 取得目前程式所在的資料夾絕對路徑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_scrapers():
    print(f"\n[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 開始執行自動爬蟲任務...")
    
    # 執行新聞爬蟲
    print("📰 正在抓取最新新聞...")
    news_script = os.path.join(BASE_DIR, "scraper", "news_spider.py")
    subprocess.run([sys.executable, news_script])
    
    # 執行論壇爬蟲
    print("💬 正在抓取最新論壇文章...")
    forum_script = os.path.join(BASE_DIR, "scraper", "forum_spider.py")
    subprocess.run([sys.executable, forum_script])
    
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ 爬蟲任務結束！資料已同步到雲端。等待下一輪執行...")

# 設定每 2 小時自動抓取一次
schedule.every(2).hours.do(run_scrapers)

if __name__ == "__main__":
    print("🤖 全自動爬蟲守衛已啟動！")
    print("⚠️ 只要這個黑色視窗不關閉，系統就會每 2 小時自動幫您上網抓一次最新資料並同步到網頁！")
    
    # 啟動時先跑一次
    run_scrapers()
    
    # 持續倒數等待
    while True:
        schedule.run_pending()
        time.sleep(60)
