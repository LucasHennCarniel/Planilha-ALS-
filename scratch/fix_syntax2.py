import codecs

with codecs.open('src/main.py', 'r', 'utf-8') as f:
    content = f.read()

content = content.replace('texto = f\\"📊  Total: {stats[\'total\']}  |  \\"', 'texto = f"📊  Total: {stats[\'total\']}  |  "')

with codecs.open('src/main.py', 'w', 'utf-8') as f:
    f.write(content)
