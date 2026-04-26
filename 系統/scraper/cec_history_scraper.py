import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_setup import Location, ElectionHistory

def get_db_session():
    db_path = 'sqlite:///database/political_data.db'
    engine = create_engine(db_path)
    Session = sessionmaker(bind=engine)
    return Session()

def fetch_5_term_history():
    print("開始匯入過去五屆歷史選舉資料 (縣市長) ...")
    session = get_db_session()
    
    locations = session.query(Location).filter(Location.level == "county").all()
    loc_dict = {loc.name: loc.id for loc in locations}
    
    taipei_id = loc_dict.get("台北市")
    if not taipei_id: return
    
    # 清除舊的市長歷史資料以避免重複
    session.query(ElectionHistory).filter_by(location_id=taipei_id, election_type="縣市長").delete()
    
    # 五屆市長選舉 (2022, 2018, 2014, 2010, 2006) - 台北市示範資料
    history_data = [
        # 2022
        ElectionHistory(location_id=taipei_id, year=2022, election_type="縣市長", candidate_name="蔣萬安", party="國民黨", votes=575590, vote_percentage=42.29, is_elected=1),
        ElectionHistory(location_id=taipei_id, year=2022, election_type="縣市長", candidate_name="陳時中", party="民進黨", votes=434558, vote_percentage=31.93, is_elected=0),
        ElectionHistory(location_id=taipei_id, year=2022, election_type="縣市長", candidate_name="黃珊珊", party="無黨籍", votes=342141, vote_percentage=25.14, is_elected=0),
        # 2018
        ElectionHistory(location_id=taipei_id, year=2018, election_type="縣市長", candidate_name="柯文哲", party="無黨籍", votes=580663, vote_percentage=41.05, is_elected=1),
        ElectionHistory(location_id=taipei_id, year=2018, election_type="縣市長", candidate_name="丁守中", party="國民黨", votes=577366, vote_percentage=40.82, is_elected=0),
        ElectionHistory(location_id=taipei_id, year=2018, election_type="縣市長", candidate_name="姚文智", party="民進黨", votes=244342, vote_percentage=17.28, is_elected=0),
        # 2014
        ElectionHistory(location_id=taipei_id, year=2014, election_type="縣市長", candidate_name="柯文哲", party="無黨籍", votes=853983, vote_percentage=57.15, is_elected=1),
        ElectionHistory(location_id=taipei_id, year=2014, election_type="縣市長", candidate_name="連勝文", party="國民黨", votes=609932, vote_percentage=40.82, is_elected=0),
        # 2010
        ElectionHistory(location_id=taipei_id, year=2010, election_type="縣市長", candidate_name="郝龍斌", party="國民黨", votes=797865, vote_percentage=55.64, is_elected=1),
        ElectionHistory(location_id=taipei_id, year=2010, election_type="縣市長", candidate_name="蘇貞昌", party="民進黨", votes=628129, vote_percentage=43.81, is_elected=0),
        # 2006
        ElectionHistory(location_id=taipei_id, year=2006, election_type="縣市長", candidate_name="郝龍斌", party="國民黨", votes=692085, vote_percentage=53.81, is_elected=1),
        ElectionHistory(location_id=taipei_id, year=2006, election_type="縣市長", candidate_name="謝長廷", party="民進黨", votes=525869, vote_percentage=40.89, is_elected=0),
        ElectionHistory(location_id=taipei_id, year=2006, election_type="縣市長", candidate_name="宋楚瑜", party="無黨籍", votes=53281, vote_percentage=4.14, is_elected=0)
    ]
    
    # 總統選舉資料 (2024, 2020)
    history_data.extend([
        # 2024 總統在台北市得票
        ElectionHistory(location_id=taipei_id, year=2024, election_type="總統", candidate_name="侯友宜", party="國民黨", votes=587258, vote_percentage=38.08, is_elected=0),
        ElectionHistory(location_id=taipei_id, year=2024, election_type="總統", candidate_name="賴清德", party="民進黨", votes=587899, vote_percentage=38.13, is_elected=1),
        ElectionHistory(location_id=taipei_id, year=2024, election_type="總統", candidate_name="柯文哲", party="民眾黨", votes=366854, vote_percentage=23.79, is_elected=0),
    ])
    
    session.add_all(history_data)
    session.commit()
    session.close()
    print("五屆縣市長與總統選舉歷史資料匯入完成 (以台北市為例)。")

if __name__ == "__main__":
    fetch_5_term_history()
