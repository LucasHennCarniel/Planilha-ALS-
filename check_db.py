import sqlite3
import os

# Verifica banco original
print("="*50)
print("BANCO ORIGINAL (data/sistema_als.db):")
print("="*50)
conn1 = sqlite3.connect('data/sistema_als.db')
cursor1 = conn1.cursor()
cursor1.execute("SELECT COUNT(*) FROM veiculos")
print(f"Total veículos: {cursor1.fetchone()[0]}")
cursor1.execute("SELECT placa, tipo_veiculo FROM veículos LIMIT 3")
print("Primeiros 3:")
for row in cursor1.fetchall():
    print(f"  - {row[0]}: {row[1]}")
conn1.close()

print("\n" + "="*50)
print("BANCO DO EXECUTÁVEL (SistemaALS_Atualizado/data/sistema_als.db):")
print("="*50)
path = os.path.join('SistemaALS_Atualizado', 'data', 'sistema_als.db')
print(f"Caminho: {path}")
print(f"Tamanho: {os.path.getsize(path)} bytes")
conn2 = sqlite3.connect(path)
cursor2 = conn2.cursor()
cursor2.execute("SELECT COUNT(*) FROM veiculos")
print(f"Total veículos: {cursor2.fetchone()[0]}")
conn2.close()
