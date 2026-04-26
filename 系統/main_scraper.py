import schedule
import time
import datetime
import threading
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from scraper.news_spider import scrape_yahoo_news
from scraper.forum_spider import scrape_ptt_hatepolitics

def run_crawlers():
    print(f"\n--- [{datetime.datetime.now()}] 啟動例行性抓取任務 ---")
    try:
        scrape_yahoo_news()
    except Exception as e:
        print(f"Error scraping news: {e}")
        
    try:
        scrape_ptt_hatepolitics()
    except Exception as e:
        print(f"Error scraping forum: {e}")
    print(f"--- 抓取任務結束 ---\n")

def start_scheduler():
    print("啟動常駐抓取服務...")
    # First run immediately
    run_crawlers()
    
    # Schedule every 30 minutes
    schedule.every(30).minutes.do(run_crawlers)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    start_scheduler()
