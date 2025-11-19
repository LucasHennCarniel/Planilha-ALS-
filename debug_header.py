import pandas as pd

# Testa com diferentes configurações de header
arquivo = 'data/PROGRAMAÇÃO MANUTENÇÃO (CÓPIA 2).xlsx'

print("🔍 Testando leitura com header=1 (pula primeira linha)...")
df = pd.read_excel(arquivo, header=1)
print(f"\n📋 Colunas (header=1):")
for i, col in enumerate(df.columns[:15]):
    print(f"  {i+1}. '{col}'")

print(f"\n📊 Primeira linha com dados:")
if len(df) > 0:
    primeira = df.iloc[0]
    print(f"  Coluna 0: '{primeira.iloc[0]}'")
    print(f"  Coluna 1: '{primeira.iloc[1]}'")
    print(f"  Coluna 2: '{primeira.iloc[2]}'")
    print(f"  Coluna 3: '{primeira.iloc[3]}'")
    print(f"  Coluna 4: '{primeira.iloc[4]}'")
