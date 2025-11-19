import pandas as pd

# Lê o Excel
arquivo = 'data/PROGRAMAÇÃO MANUTENÇÃO (CÓPIA 2).xlsx'
df = pd.read_excel(arquivo)

print(f"📊 Total de linhas no Excel: {len(df)}")
print(f"\n📋 Colunas encontradas:")
for i, col in enumerate(df.columns):
    print(f"  {i+1}. '{col}'")

print(f"\n✅ Primeiras 3 linhas COM dados:")
for idx, row in df.head(3).iterrows():
    print(f"\n--- Linha {idx+1} ---")
    print(f"  DATA: '{row.get('DATA', 'N/A')}'")
    print(f"  PLACA: '{row.get('PLACA', 'N/A')}'")
    print(f"  DATA ENTRADA: '{row.get('DATA ENTRADA', 'N/A')}'")
    print(f"  VEÍCULO: '{row.get('VEÍCULO', 'N/A')}'")
    print(f"  STATUS: '{row.get('STATUS', 'N/A')}'")

print(f"\n🔍 Contando linhas não-vazias...")
contador = 0
for idx, row in df.iterrows():
    placa = str(row.get('PLACA', '')).strip()
    data = str(row.get('DATA', '')).strip()
    data_entrada = str(row.get('DATA ENTRADA', '')).strip()
    
    if placa and data and data_entrada:
        contador += 1

print(f"\n✅ Linhas com dados completos: {contador}")
