import re

with open('src/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(
    r"texto = f\"📊  Total: \{stats\['total_registros'\]\}  \|  \"",
    r"texto = f\"📊  Total: {stats['total']}  |  \"",
    content
)

with open('src/main.py', 'w', encoding='utf-8') as f:
    f.write(content)
