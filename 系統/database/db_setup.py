import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import datetime

Base = declarative_base()

class Location(Base):
    __tablename__ = 'locations'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False) # e.g., 台北市, 大安區
    level = Column(String(20), default="county") # "county" or "district"
    parent_id = Column(Integer, ForeignKey('locations.id'), nullable=True) # For nested locations
    
    # Optional relationships
    children = relationship("Location")
    profile = relationship("RegionProfile", back_populates="location", uselist=False)
    elections = relationship("ElectionHistory", back_populates="location")

class RegionProfile(Base):
    """選區情報與簡介"""
    __tablename__ = 'region_profiles'
    id = Column(Integer, primary_key=True)
    location_id = Column(Integer, ForeignKey('locations.id'))
    overview = Column(Text) # 選情簡介
    potential_candidates = Column(Text) # 潛在候選人分析
    
    location = relationship("Location", back_populates="profile")

class ElectionHistory(Base):
    """歷史選舉數據"""
    __tablename__ = 'election_history'
    id = Column(Integer, primary_key=True)
    location_id = Column(Integer, ForeignKey('locations.id'))
    year = Column(Integer)
    election_type = Column(String(50)) # e.g., 縣市長, 議員
    candidate_name = Column(String(50))
    party = Column(String(50))
    votes = Column(Integer)
    vote_percentage = Column(Float)
    is_elected = Column(Integer) # 1 or 0
    
    location = relationship("Location", back_populates="elections")

class Politician(Base):
    __tablename__ = 'politicians'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    party = Column(String(50))
    location_id = Column(Integer, ForeignKey('locations.id'), nullable=True)

class News(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True)
    source = Column(String(50))
    title = Column(String(200), nullable=False)
    content = Column(Text)
    url = Column(String(500), unique=True)
    publish_time = Column(DateTime, default=datetime.datetime.utcnow)
    location_id = Column(Integer, ForeignKey('locations.id'), nullable=True)
    politician_id = Column(Integer, ForeignKey('politicians.id'), nullable=True)
    # 分類
    issue_category = Column(String(50), nullable=True)
    party_stance = Column(String(50), nullable=True)

class Opinion(Base):
    __tablename__ = 'opinions'
    id = Column(Integer, primary_key=True)
    platform = Column(String(50)) # e.g., PTT, Dcard, FB
    title = Column(String(200), nullable=False)
    content = Column(Text)
    url = Column(String(500), unique=True)
    publish_time = Column(DateTime, default=datetime.datetime.utcnow)
    engagement_score = Column(Integer, default=0) 
    location_id = Column(Integer, ForeignKey('locations.id'), nullable=True)
    # 分類
    issue_category = Column(String(50), nullable=True)
    party_stance = Column(String(50), nullable=True)

def init_db(db_path='sqlite:///database/political_data.db'):
    os.makedirs(os.path.dirname(db_path.replace('sqlite:///', '')), exist_ok=True)
    engine = create_engine(db_path)
    # Drop all first for this major migration
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # 1. 寫入縣市與行政區 (示範性)
    counties_data = {
        "台北市": ["中正區", "大同區", "中山區", "松山區", "大安區", "萬華區", "信義區", "士林區", "北投區", "內湖區", "南港區", "文山區"],
        "新北市": ["板橋區", "三重區", "中和區", "永和區", "新莊區", "新店區"], # 僅列部分示範
        "全國": []
    }
    
    county_objs = {}
    for county, districts in counties_data.items():
        c = Location(name=county, level="county")
        session.add(c)
        session.flush() # get id
        county_objs[county] = c.id
        
        for district in districts:
            session.add(Location(name=district, level="district", parent_id=c.id))
            
    # 2. 寫入範例選情簡介與歷史數據 (以台北市為例)
    taipei_id = county_objs["台北市"]
    
    session.add(RegionProfile(
        location_id=taipei_id,
        overview="台北市長期被視為藍營優勢選區，但近年第三勢力崛起，選票結構產生變化。2026 年九合一選舉預計將是國民黨力保執政、民進黨與民眾黨積極挑戰的「三腳督」甚至多強鼎立局面。",
        potential_candidates="蔣萬安 (國民黨, 現任爭取連任), 沈伯洋 (民進黨潛在人選), 黃珊珊 (民眾黨潛在人選)"
    ))
    
    # 2022 台北市長選舉結果
    historical_data = [
        ElectionHistory(location_id=taipei_id, year=2022, election_type="市長", candidate_name="蔣萬安", party="國民黨", votes=575590, vote_percentage=42.29, is_elected=1),
        ElectionHistory(location_id=taipei_id, year=2022, election_type="市長", candidate_name="陳時中", party="民進黨", votes=434558, vote_percentage=31.93, is_elected=0),
        ElectionHistory(location_id=taipei_id, year=2022, election_type="市長", candidate_name="黃珊珊", party="無黨籍", votes=342141, vote_percentage=25.14, is_elected=0)
    ]
    session.add_all(historical_data)
    
    session.commit()
    session.close()
    print("Database re-initialized with deep geography and history schema.")

if __name__ == '__main__':
    init_db()
