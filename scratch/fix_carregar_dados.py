import re

with open('src/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace self.db.carregar_dados() with pass or just remove it.
# Actually let's just comment it out.
content = content.replace("self.db.carregar_dados()", "# self.db.carregar_dados() no longer needed")

with open('src/main.py', 'w', encoding='utf-8') as f:
    f.write(content)
