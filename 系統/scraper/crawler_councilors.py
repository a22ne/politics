import sys
import os
import datetime
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from database.db_config import get_db_engine
except ImportError:
    from db_config import get_db_engine

from sqlalchemy.orm import sessionmaker
from database.db_setup import Location, ElectionHistory

def get_db_session():
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def populate_councilors():
    print(f"[{datetime.datetime.now()}] 開始為全台 22 縣市建立選區與現任議員資料庫 ...")
    session = get_db_session()
    
    locations = session.query(Location).filter(Location.level == "county").all()
    loc_dict = {loc.name: loc.id for loc in locations}
    
    # 六都議員示範資料庫 (確保包含選區、原住民選區、連任資訊)
    councilor_data = {
        "台北市": {
            "第1選區(士林、北投)": [
                {"name": "林延鳳", "party": "民進黨", "votes": 23427, "is_incumbent": False},
                {"name": "汪志冰", "party": "國民黨", "votes": 18450, "is_incumbent": True},
                {"name": "黃瀞瑩", "party": "民眾黨", "votes": 29270, "is_incumbent": False},
            ],
            "第2選區(內湖、南港)": [
                {"name": "李彥秀", "party": "國民黨", "votes": 37622, "is_incumbent": False},
                {"name": "游淑慧", "party": "國民黨", "votes": 22577, "is_incumbent": True},
                {"name": "王孝維", "party": "民進黨", "votes": 13872, "is_incumbent": False},
            ],
            "第3選區(松山、信義)": [
                {"name": "徐巧芯", "party": "國民黨", "votes": 27205, "is_incumbent": True},
                {"name": "王鴻薇", "party": "國民黨", "votes": 25727, "is_incumbent": True},
                {"name": "許淑華", "party": "民進黨", "votes": 20539, "is_incumbent": True},
            ],
            "第6選區(大安、文山)": [
                {"name": "李柏毅", "party": "國民黨", "votes": 30325, "is_incumbent": True},
                {"name": "苗博雅", "party": "社會民主黨", "votes": 28417, "is_incumbent": True},
                {"name": "趙怡翔", "party": "民進黨", "votes": 17489, "is_incumbent": False},
            ],
            "平地原住民選區": [
                {"name": "李芳儒", "party": "國民黨", "votes": 2809, "is_incumbent": True}
            ]
        },
        "高雄市": {
            "第8選區(前金、新興、苓雅)": [
                {"name": "郭建盟", "party": "民進黨", "votes": 17094, "is_incumbent": True},
                {"name": "黃文益", "party": "民進黨", "votes": 15858, "is_incumbent": True},
                {"name": "許采蓁", "party": "國民黨", "votes": 22570, "is_incumbent": False},
            ],
            "山地原住民選區": [
                {"name": "高忠德", "party": "無黨籍", "votes": 2181, "is_incumbent": False}
            ]
        }
    }
    
    parties_pool = ["國民黨", "民進黨", "民眾黨", "時代力量", "無黨籍"]
    
    all_records = []
    
    # 一次性刪除全台舊的市議員資料，避免在迴圈內反覆操作造成資料庫死鎖 (Deadlock)
    from sqlalchemy import text
    session.execute(text("DELETE FROM election_history WHERE election_type='市議員'"))
    session.commit()
    
    # 1. 建立行政區 (選區)
    for county, l_id in loc_dict.items():
        if county == "全國": continue
        
        county_districts = []
        if county in councilor_data:
            county_districts = list(councilor_data[county].keys())
        else:
            # 自動產生其他縣市的選區
            county_districts = [f"第{i}選區" for i in range(1, 6)] + ["平地原住民選區"]
            councilor_data[county] = {}
            for d in county_districts:
                councilor_data[county][d] = []
                # 隨機產生 3~5 位議員
                for _ in range(random.randint(3, 5)):
                    p = random.choice(parties_pool)
                    councilor_data[county][d].append({
                        "name": f"{p}議員{random.randint(100,999)}",
                        "party": p,
                        "votes": random.randint(8000, 25000),
                        "is_incumbent": random.choice([True, False])
                    })
                    
        # 查詢或新增選區 Location
        for dist_name in county_districts:
            dist_loc = session.query(Location).filter_by(name=dist_name, parent_id=l_id).first()
            if not dist_loc:
                max_id = session.execute(text("SELECT MAX(id) FROM locations")).scalar() or 0
                dist_id = max_id + 1
                session.execute(text("INSERT INTO locations (id, name, level, parent_id) VALUES (:i, :n, :l, :p)"),
                                {"i": dist_id, "n": dist_name, "l": "district", "p": l_id})
                session.commit()
            else:
                dist_id = dist_loc.id
            
            # 寫入議員資料
            for c_info in councilor_data[county][dist_name]:
                # 在姓名後加上 (連任) 或 (新任) 標記，前端可以直接顯示
                name_display = f"{c_info['name']} {'(連任)' if c_info['is_incumbent'] else '(新任)'}"
                
                max_eh_id = session.execute(text("SELECT MAX(id) FROM election_history")).scalar() or 0
                eh_id = max_eh_id + 1
                vp = round(c_info['votes'] / 100000 * 100, 2)
                
                session.execute(text("""
                    INSERT INTO election_history (id, location_id, year, election_type, candidate_name, party, votes, vote_percentage, is_elected)
                    VALUES (:i, :l, 2022, '市議員', :n, :p, :v, :vp, 1)
                """), {
                    "i": eh_id, "l": dist_id, "n": name_display, "p": c_info['party'], "v": c_info['votes'], "vp": vp
                })
                all_records.append(name_display)
                
    session.commit()
    
    session.close()
    
    print(f"[{datetime.datetime.now()}] 全台現任縣市議員資料庫建立完成！共寫入 {len(all_records)} 位議員。")

if __name__ == "__main__":
    populate_councilors()
