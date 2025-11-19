import sqlite3

conn = sqlite3.connect('data/sistema_als.db')
cursor = conn.cursor()

# Mostra estrutura da tabela
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='manutencoes'")
print("ESTRUTURA DA TABELA:")
print(cursor.fetchone()[0])
print("\n")

# Conta registros
cursor.execute("SELECT COUNT(*) FROM manutencoes")
print(f"Total de registros: {cursor.fetchone()[0]}")

# Mostra primeiros 3 registros
cursor.execute("SELECT data, placa, data_entrada FROM manutencoes LIMIT 3")
print("\nPrimeiros registros:")
for row in cursor.fetchall():
    print(f"  Data: {row[0]}, Placa: {row[1]}, Data Entrada: {row[2]}")

conn.close()
