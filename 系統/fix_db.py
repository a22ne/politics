import os
import glob

import_stmt = '''
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from database.db_config import get_db_engine
except ImportError:
    from db_config import get_db_engine
'''

for file in glob.glob('scraper/*.py') + ['clean_db.py', 'populate_all_districts.py', 'update_categories.py', 'database/db_setup.py']:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    old_code1 = "db_path = 'sqlite:///database/political_data.db'\n    engine = create_engine(db_path)"
    old_code2 = "db_path='sqlite:///database/political_data.db'"
    
    changed = False
    if old_code1 in content:
        content = import_stmt + content.replace(old_code1, "engine = get_db_engine()")
        changed = True
    elif old_code2 in content:
        content = import_stmt + content.replace("def init_db(db_path='sqlite:///database/political_data.db'):", "def init_db():")
        content = content.replace("engine = create_engine(db_path)", "engine = get_db_engine()")
        changed = True
        
    if changed:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Fixed {file}')
