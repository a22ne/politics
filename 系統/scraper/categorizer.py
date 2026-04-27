def categorize_content(text):
    """進階的計分制分類器"""
    issue_cat = "其他"
    party_cat = "未提及"
    
    # 議題字典
    issues = {
        "選舉造勢": ["造勢", "拜票", "民調", "參選", "選戰", "得票", "選舉", "凍蒜", "掃街"],
        "施政與政策": ["政策", "施政", "法案", "預算", "建設", "補助", "市政", "三讀", "修法"],
        "爭議事件": ["爭議", "弊案", "貪污", "炎上", "道歉", "失言", "查辦", "風波", "圖利", "收賄"],
        "民生經濟": ["物價", "房價", "通膨", "薪資", "停電", "缺水", "經濟", "加薪", "股市", "台積電"],
        "兩岸與外交": ["兩岸", "外交", "中共", "美國", "台海", "中國", "國際", "統獨", "共機"]
    }
    
    # 政黨核心人物與代稱字典 (擴充)
    parties = {
        "國民黨": ["國民黨", "藍營", "泛藍", "蔣萬安", "侯友宜", "盧秀燕", "朱立倫", "徐巧芯", "韓國瑜", "馬英九", "趙少康", "立法院長", "藍委"],
        "民進黨": ["民進黨", "綠營", "泛綠", "賴清德", "陳其邁", "黃偉哲", "蘇貞昌", "林右昌", "沈伯洋", "王義川", "蔡英文", "蕭美琴", "柯建銘", "綠委", "卓榮泰"],
        "民眾黨": ["民眾黨", "白營", "柯文哲", "黃珊珊", "高虹安", "黃國昌", "陳智菡", "白委", "小草"],
        "時代力量": ["時代力量", "王婉諭", "時力"],
    }
    
    # 正面形容詞 (用於加分)
    positive_words = ["肯定", "支持", "看好", "政績", "優秀", "讚", "推", "貢獻", "造福", "進步"]
    
    if not text:
        return issue_cat, party_cat
        
    # 判斷議題 (計分制)
    issue_scores = {k: sum(text.count(kw) for kw in v) for k, v in issues.items()}
    if max(issue_scores.values(), default=0) > 0:
        issue_cat = max(issue_scores, key=issue_scores.get)
            
    # 判斷政黨 (計分制 + 正面詞彙加權)
    party_scores = {}
    
    # 計算文章中出現多少正面詞彙
    pos_count = sum(text.count(pw) for pw in positive_words)
    
    for party, keywords in parties.items():
        # 基礎分數：關鍵人物或政黨名稱出現的次數
        base_score = sum(text.count(kw) for kw in keywords)
        
        # 隱藏加分機制：如果該政黨被高度提及，且文章充滿正面詞彙，給予額外加權
        # 這有助於在「多黨混戰」的新聞中，把新聞歸給主要被誇獎的對象
        if base_score > 0:
            party_scores[party] = base_score + (pos_count * 0.5)
        else:
            party_scores[party] = 0
            
    # 選出最高分的政黨
    if max(party_scores.values(), default=0) > 0:
        party_cat = max(party_scores, key=party_scores.get)
            
    return issue_cat, party_cat
