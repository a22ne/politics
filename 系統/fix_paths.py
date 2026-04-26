import os

search_text = "'sqlite:///c:/Users/Anne/Desktop/系統/database/political_data.db'"
replace_text = "f'sqlite:///{os.path.join(os.path.dirname(os.path.abspath(__file__)), \"database\", \"political_data.db\")}'"

# For app.py, the depth is 0 so it's fine. For scripts in scraper/, the depth is 1, so dirname(__file__) is scraper/. 
# Actually, the safest relative path that works everywhere locally and on Streamlit cloud is just "sqlite:///database/political_data.db" assuming we always run from the root directory.
# Let's just use "sqlite:///database/political_data.db"

replace_text = "'sqlite:///database/political_data.db'"

for root, _, files in os.walk('.'):
    for f in files:
        if f.endswith('.py') and f != 'fix_paths.py':
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            if search_text in content:
                content = content.replace(search_text, replace_text)
                with open(path, 'w', encoding='utf-8') as file:
                    file.write(content)
                print(f"Fixed {path}")

# also fix app.py's db_setup import issue if any
