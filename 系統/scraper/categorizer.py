def categorize_content(text):
    """簡單的雙層分類器"""
    issue_cat = "其他"
    party_cat = "未提及"
    
    # 議題字典
    issues = {
        "選舉造勢": ["造勢", "拜票", "民調", "參選", "選戰", "得票", "選舉"],
        "施政與政策": ["政策", "施政", "法案", "預算", "建設", "補助", "市政"],
        "爭議事件": ["爭議", "弊案", "貪污", "炎上", "道歉", "失言", "查辦", "風波"],
        "民生經濟": ["物價", "房價", "通膨", "薪資", "停電", "缺水", "經濟", "加薪", "股市"],
        "兩岸與外交": ["兩岸", "外交", "中共", "美國", "台海", "中國"]
    }
    
    # 政黨字典
    parties = {
        "國民黨": ["國民黨", "藍營", "蔣萬安", "侯友宜", "盧秀燕", "朱立倫", "徐巧芯"],
        "民進黨": ["民進黨", "綠營", "賴清德", "陳其邁", "黃偉哲", "蘇貞昌", "林右昌", "沈伯洋", "王義川"],
        "民眾黨": ["民眾黨", "白營", "柯文哲", "黃珊珊", "高虹安", "黃國昌"],
        "時代力量": ["時代力量", "王婉諭"],
    }
    
    if not text:
        return issue_cat, party_cat
        
    # 判斷議題
    for k, v in issues.items():
        if any(keyword in text for keyword in v):
            issue_cat = k
            break
            
    # 判斷政黨
    for k, v in parties.items():
        if any(keyword in text for keyword in v):
            party_cat = k
            break
            
    return issue_cat, party_cat
