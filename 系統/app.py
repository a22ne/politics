import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import os
import sys

# Set up page config
st.set_page_config(page_title="台灣區域選戰情報與輿情系統", layout="wide", page_icon="🇹🇼")

import base64

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return ""

bg_path = os.path.join(BASE_DIR, "assets", "bg.png")
bg_img = get_base64_of_bin_file(bg_path)

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{bg_img}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    [data-testid="stSidebar"] {{
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.2);
    }}
    [data-testid="stSidebar"] > div:first-child {{
        background: transparent !important;
    }}

    [data-testid="stHeader"] {{
        background: transparent !important;
    }}

    [data-testid="stMetric"] {{
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.15) 0%, rgba(255, 255, 255, 0.05) 100%);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 30px;
        padding: 25px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        color: white;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}
    
    [data-testid="stMetric"]:hover {{
        transform: translateY(-8px);
        box-shadow: 0 15px 45px 0 rgba(0, 0, 0, 0.4);
    }}

    .info-box {{ 
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.12) 0%, rgba(255, 255, 255, 0.02) 100%);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        padding: 25px; 
        border-radius: 30px; 
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-top: 1px solid rgba(255, 255, 255, 0.5);
        border-left: 1px solid rgba(255, 255, 255, 0.5);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
        color: white;
    }}

    h1, h2, h3, h4, h5, h6, p, span, div, label, li, a, th, td {{ 
        color: #ffffff !important;
        text-shadow: 0px 1px 3px rgba(0,0,0,0.6);
    }}
    
    div[data-baseweb="popover"], 
    div[data-baseweb="popover"] * {{
        color: #333333 !important;
        text-shadow: none !important;
    }}
    div[data-baseweb="popover"] ul {{
        background-color: #ffffff !important;
    }}
    div[data-baseweb="popover"] li:hover {{
        background-color: #f0f2f6 !important;
    }}

    [data-testid="stDataFrame"] {{
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(8px);
        border-radius: 20px;
        padding: 10px;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }}
    
    div[data-baseweb="select"] > div {{
        border-radius: 20px;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.4);
    }}
    
    div[role="radiogroup"] {{
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 10px 20px;
        border-radius: 30px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        display: inline-flex;
    }}
    
    .streamlit-expanderHeader {{
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }}

    .stButton > button {{
        background: rgba(255, 255, 255, 0.2) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        border-radius: 30px !important;
    }}
    .stButton > button:hover {{
        background: rgba(255, 255, 255, 0.35) !important;
        border-color: #ffffff !important;
    }}

    .main .block-container {{ padding-top: 3rem; }}
</style>
""", unsafe_allow_html=True)

from database.db_config import get_db_engine
try:
    from scraper.categorizer import POLITICIANS, ISSUES, PARTIES
except ImportError:
    POLITICIANS = {}
    ISSUES = {}
    PARTIES = {}

@st.cache_resource
def get_engine():
    return get_db_engine()

def load_data(query, engine):
    try:
        return pd.read_sql_query(query, engine)
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()

def extract_top_keywords(df_news, df_opinions):
    """即時關鍵字分析模組"""
    import re
    from collections import Counter
    text_data = []
    if not df_news.empty:
        text_data.extend(df_news['title'].tolist())
    if not df_opinions.empty:
        text_data.extend(df_opinions['title'].tolist())
        
    combined_text = " ".join(text_data)
    
    # 從字典萃取熱門實體
    all_keywords = list(POLITICIANS.keys()) + list(ISSUES.keys()) + list(PARTIES.keys())
    # 加入一些動態熱門詞
    all_keywords.extend(["弊案", "貪污", "選舉", "民調", "補助", "交通", "停電", "房價", "黑金", "兩岸", "網軍"])
    
    counter = Counter()
    for kw in all_keywords:
        count = combined_text.count(kw)
        if count > 0:
            counter[kw] += count
            
    # 移除政黨本身的名稱避免佔據版面
    for party in ["國民黨", "民進黨", "民眾黨"]:
        if party in counter:
            del counter[party]
            
    top_3 = [item[0] for item in counter.most_common(3)]
    while len(top_3) < 3:
        top_3.append("暫無熱點")
    return top_3

def main():
    engine = get_engine()
    
    st.title("📊 台灣區域選戰情報與輿情系統 (進階版)")
    
    # 1. Sidebar - Geographical Hierarchy
    st.sidebar.header("🗺️ 選擇地區")
    
    counties_df = load_data("SELECT id, name FROM locations WHERE level='county'", engine)
    county_options = counties_df.set_index('name')['id'].to_dict() if not counties_df.empty else {}
    
    selected_county_name = st.sidebar.selectbox("縣市", ["所有縣市"] + list(county_options.keys()))
    selected_district_name = "所有行政區"
    loc_id_to_query = None
    
    if selected_county_name != "所有縣市":
        county_id = county_options[selected_county_name]
        loc_id_to_query = county_id
        
        districts_df = load_data(f"SELECT id, name FROM locations WHERE parent_id={county_id}", engine)
        if not districts_df.empty:
            district_options = districts_df.set_index('name')['id'].to_dict()
            selected_district_name = st.sidebar.selectbox("行政區", ["所有行政區"] + list(district_options.keys()))
            if selected_district_name != "所有行政區":
                loc_id_to_query = district_options[selected_district_name]

    # 2. Sidebar - Categorization Filters
    st.sidebar.header("🔍 議題與立場篩選")
    issue_filter = st.sidebar.selectbox("關注議題", ["所有議題", "選舉造勢", "施政與政策", "爭議事件", "民生經濟", "兩岸與外交", "其他"])
    party_filter = st.sidebar.selectbox("相關政黨/立場", ["所有政黨", "國民黨", "民進黨", "民眾黨", "時代力量", "未提及"])

    # Base where clauses for news/opinions
    where_clauses = []
    if loc_id_to_query:
        if selected_district_name == "所有行政區":
            dist_ids_query = f"SELECT id FROM locations WHERE parent_id={loc_id_to_query}"
            dist_ids_df = load_data(dist_ids_query, engine)
            all_loc_ids = [loc_id_to_query] + dist_ids_df['id'].tolist() if not dist_ids_df.empty else [loc_id_to_query]
            loc_tuple = tuple(all_loc_ids) if len(all_loc_ids) > 1 else f"({all_loc_ids[0]})"
            where_clauses.append(f"location_id IN {loc_tuple}")
        else:
            where_clauses.append(f"location_id = {loc_id_to_query}")
            
    if issue_filter != "所有議題":
        where_clauses.append(f"issue_category = '{issue_filter}'")
    if party_filter != "所有政黨":
        where_clauses.append(f"party_stance = '{party_filter}'")
        
    where_str = " AND ".join(where_clauses)
    if where_str:
        where_str = "WHERE " + where_str

    # Get latest news for Keyword Extraction
    recent_news_query = f"SELECT title FROM news {where_str} ORDER BY publish_time DESC LIMIT 50"
    recent_opinions_query = f"SELECT title FROM opinions {where_str} ORDER BY publish_time DESC LIMIT 50"
    df_recent_news = load_data(recent_news_query, engine)
    df_recent_opinions = load_data(recent_opinions_query, engine)
    top_keywords = extract_top_keywords(df_recent_news, df_recent_opinions)

    # 3. Main Content Area
    if selected_county_name != "所有縣市":
        st.header(f"📍 {selected_county_name} {selected_district_name if selected_district_name != '所有行政區' else ''} 政治現況")
        
        # Real-time Keywords Metrics
        st.markdown("##### 🔥 實時熱門關鍵字")
        kw_cols = st.columns(3)
        for i, kw in enumerate(top_keywords):
            with kw_cols[i]:
                st.metric(label=f"熱點 {i+1}", value=kw, delta="高討論度" if kw != "暫無熱點" else None)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Query Profile
        profile_df = load_data(f"SELECT overview, potential_candidates FROM region_profiles WHERE location_id={loc_id_to_query or county_options[selected_county_name]}", engine)
        
        col_prof1, col_prof2 = st.columns([2, 1])
        with col_prof1:
            if not profile_df.empty and pd.notna(profile_df.iloc[0]['overview']):
                st.markdown(f'<div class="info-box"><strong>📖 選情簡介與歷史背景：</strong><br>{profile_df.iloc[0]["overview"]}</div>', unsafe_allow_html=True)
            else:
                st.info("尚無此區的選情簡介。")
                
        with col_prof2:
            if not profile_df.empty and pd.notna(profile_df.iloc[0]['potential_candidates']):
                st.markdown(f'<div class="info-box" style="border-left-color: #d35400;"><strong>👥 潛在參選人：</strong><br>{profile_df.iloc[0]["potential_candidates"]}</div>', unsafe_allow_html=True)

        # Query Election History
        st.subheader("🗳️ 歷史選舉與席次數據")
        elec_type = st.radio("選擇選舉類型", ["縣市長", "總統", "市議員"], horizontal=True)
        
        if elec_type in ["縣市長", "總統"]:
            history_df = load_data(f"SELECT year, candidate_name, party, votes, vote_percentage, is_elected FROM election_history WHERE location_id={loc_id_to_query or county_options[selected_county_name]} AND election_type='{elec_type}' ORDER BY year DESC, votes DESC", engine)
            
            if not history_df.empty:
                latest_year = history_df['year'].max()
                latest_df = history_df[history_df['year'] == latest_year]
                
                col_hist1, col_hist2 = st.columns([1, 1])
                with col_hist1:
                    st.markdown(f"**所有歷史數據 ({elec_type})**")
                    st.dataframe(history_df.rename(columns={'year':'年份', 'candidate_name':'候選人', 'party':'政黨', 'votes':'得票數', 'vote_percentage':'得票率(%)', 'is_elected':'當選'}), hide_index=True)
                with col_hist2:
                    st.markdown(f"**{latest_year} 年得票分佈**")
                    fig_pie = px.pie(latest_df, values='votes', names='candidate_name', hole=0.3, color='party', color_discrete_map={'國民黨':'blue', '民進黨':'green', '民眾黨':'cyan', '無黨籍':'gray', '時代力量':'yellow', '親民黨':'orange'})
                    st.plotly_chart(fig_pie, use_container_width=True)
                    
                trend_df = history_df.groupby(['year', 'party'])['vote_percentage'].sum().reset_index()
                fig_line = px.line(trend_df, x='year', y='vote_percentage', color='party', title='歷屆政黨得票率趨勢', color_discrete_map={'國民黨':'blue', '民進黨':'green', '民眾黨':'cyan', '無黨籍':'gray', '時代力量':'yellow', '親民黨':'orange'})
                st.plotly_chart(fig_line, use_container_width=True)
            else:
                st.info(f"尚無此區的 {elec_type} 歷史數據。")
                
        elif elec_type == "市議員":
            dist_ids_df = load_data(f"SELECT id, name FROM locations WHERE parent_id={county_options[selected_county_name]}", engine)
            if not dist_ids_df.empty:
                dist_ids_tuple = tuple(dist_ids_df['id'].tolist()) if len(dist_ids_df) > 1 else f"({dist_ids_df['id'].iloc[0]})"
                councilor_df = load_data(f"""
                    SELECT l.name as district_name, e.candidate_name, e.party, e.votes 
                    FROM election_history e 
                    JOIN locations l ON e.location_id = l.id 
                    WHERE e.location_id IN {dist_ids_tuple} AND e.election_type='市議員' 
                    ORDER BY l.name, e.votes DESC
                """, engine)
                
                if not councilor_df.empty:
                    col_c1, col_c2 = st.columns([1, 1])
                    with col_c1:
                        st.markdown("**現任各區議員名單 (包含連任資訊與得票數)**")
                        st.dataframe(councilor_df.rename(columns={'district_name':'所屬選區', 'candidate_name':'議員姓名', 'party':'政黨', 'votes':'得票數'}), hide_index=True, use_container_width=True)
                    with col_c2:
                        st.markdown("**全縣市議員政黨席次分佈**")
                        party_counts = councilor_df['party'].value_counts().reset_index()
                        party_counts.columns = ['party', 'count']
                        fig_bar = px.bar(party_counts, x='party', y='count', color='party', color_discrete_map={'國民黨':'blue', '民進黨':'green', '民眾黨':'cyan', '無黨籍':'gray', '時代力量':'yellow'}, title="政黨總席次統計")
                        st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.info("尚無此區的市議員數據。您可以使用 crawler_councilors.py 爬蟲腳本寫入資料。")
            else:
                st.info("尚無此區的市議員數據。")
                
        st.markdown("---")

    # 4. Pagination & Display for News and Opinions
    st.header("📰 即時新聞與公開輿情")
    
    # Initialize session state for pagination
    if 'news_page' not in st.session_state:
        st.session_state.news_page = 1
    if 'opinion_page' not in st.session_state:
        st.session_state.opinion_page = 1
        
    ITEMS_PER_PAGE = 10
    
    # Count totals for pagination
    total_news = load_data(f"SELECT COUNT(id) as c FROM news {where_str}", engine).iloc[0]['c']
    total_opinions = load_data(f"SELECT COUNT(id) as c FROM opinions {where_str}", engine).iloc[0]['c']

    colA, colB = st.columns(2)
    
    with colA:
        st.subheader(f"新聞報導 (共 {total_news} 筆)")
        
        # News Pagination Logic
        total_news_pages = max(1, (total_news + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
        
        # Query News
        news_offset = (st.session_state.news_page - 1) * ITEMS_PER_PAGE
        news_query = f"SELECT title, source, issue_category, party_stance, url, publish_time FROM news {where_str} ORDER BY publish_time DESC LIMIT {ITEMS_PER_PAGE} OFFSET {news_offset}"
        df_news = load_data(news_query, engine)
        
        if not df_news.empty:
            for _, row in df_news.iterrows():
                cat_badge = f"[{row['issue_category']}]" if row['issue_category'] else ""
                party_badge = f"[{row['party_stance']}]" if row['party_stance'] else ""
                st.markdown(f"**[{row['title']}]({row['url']})**")
                st.caption(f"{cat_badge}{party_badge} | 來源: {row['source']} | {row['publish_time']}")
        else:
            st.info("查無符合條件的新聞。")
            
        # News Pagination Controls
        c1, c2, c3 = st.columns([1, 2, 1])
        if c1.button("⬅️ 上一頁", key="news_prev", disabled=st.session_state.news_page <= 1):
            st.session_state.news_page -= 1
            st.rerun()
        c2.markdown(f"<div style='text-align: center; color: white;'>第 {st.session_state.news_page} / {total_news_pages} 頁</div>", unsafe_allow_html=True)
        if c3.button("下一頁 ➡️", key="news_next", disabled=st.session_state.news_page >= total_news_pages):
            st.session_state.news_page += 1
            st.rerun()
            
    with colB:
        st.subheader(f"網路討論 (共 {total_opinions} 筆)")
        
        # Opinion Pagination Logic
        total_opinion_pages = max(1, (total_opinions + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
        
        # Query Opinions
        op_offset = (st.session_state.opinion_page - 1) * ITEMS_PER_PAGE
        opinions_query = f"SELECT title, platform, issue_category, party_stance, url, publish_time FROM opinions {where_str} ORDER BY publish_time DESC LIMIT {ITEMS_PER_PAGE} OFFSET {op_offset}"
        df_opinions = load_data(opinions_query, engine)
        
        if not df_opinions.empty:
            for _, row in df_opinions.iterrows():
                cat_badge = f"[{row['issue_category']}]" if row['issue_category'] else ""
                party_badge = f"[{row['party_stance']}]" if row['party_stance'] else ""
                st.markdown(f"**[{row['title']}]({row['url']})**")
                st.caption(f"{cat_badge}{party_badge} | 平台: {row['platform']} | {row['publish_time']}")
        else:
            st.info("查無符合條件的論壇文章。")

        # Opinion Pagination Controls
        c1, c2, c3 = st.columns([1, 2, 1])
        if c1.button("⬅️ 上一頁", key="op_prev", disabled=st.session_state.opinion_page <= 1):
            st.session_state.opinion_page -= 1
            st.rerun()
        c2.markdown(f"<div style='text-align: center; color: white;'>第 {st.session_state.opinion_page} / {total_opinion_pages} 頁</div>", unsafe_allow_html=True)
        if c3.button("下一頁 ➡️", key="op_next", disabled=st.session_state.opinion_page >= total_opinion_pages):
            st.session_state.opinion_page += 1
            st.rerun()

if __name__ == "__main__":
    main()
