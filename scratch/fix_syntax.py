import re

with open('src/main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "Total:" in line and "stats['total_registros']" in line:
        lines[i] = line.replace("stats['total_registros']", "stats['total']")
    if "Total:" in line and "stats['total']" in line:
        lines[i] = line.replace('\\"', '"') # in case I messed up

with open('src/main.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
