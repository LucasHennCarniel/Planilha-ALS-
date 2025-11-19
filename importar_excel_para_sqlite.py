"""
Script de Importação de Dados Excel para SQLite
================================================
Use este script para importar dados de backups antigos em Excel
para o novo banco de dados SQLite.

Uso:
    python importar_excel_para_sqlite.py
"""
import pandas as pd
import sqlite3
import os
from datetime import datetime
import shutil

def importar_excel_para_sqlite():
    """Importa dados do Excel para SQLite"""
    
    print("=" * 60)
    print("IMPORTADOR DE DADOS - Excel → SQLite")
    print("=" * 60)
    print()
    
    # Caminhos dos arquivos
    excel_path = 'data/PROGRAMAÇÃO MANUTENÇÃO (CÓPIA 2).xlsx'
    db_path = 'data/sistema_als.db'
    backup_db_path = f'backup/database_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    
    # Verifica se Excel existe
    if not os.path.exists(excel_path):
        print(f"❌ ERRO: Arquivo Excel não encontrado em:")
        print(f"   {excel_path}")
        print()
        print("📋 Copie o backup Excel para a pasta 'data/' e tente novamente.")
        return False
    
    # Faz backup do banco atual (se existir)
    if os.path.exists(db_path):
        print(f"📦 Fazendo backup do banco atual...")
        os.makedirs('backup', exist_ok=True)
        shutil.copy2(db_path, backup_db_path)
        print(f"✅ Backup salvo: {backup_db_path}")
        print()
        
        # Pergunta se quer sobrescrever
        resposta = input("⚠️  Deseja SOBRESCREVER o banco atual? (S/N): ").strip().upper()
        if resposta != 'S':
            print("❌ Operação cancelada pelo usuário.")
            return False
        
        # Remove banco antigo
        os.remove(db_path)
        print("🗑️  Banco antigo removido.")
        print()
    
    print(f"📂 Lendo arquivo Excel...")
    try:
        df_excel = pd.read_excel(excel_path)
        print(f"✅ {len(df_excel)} registros encontrados no Excel")
    except Exception as e:
        print(f"❌ ERRO ao ler Excel: {e}")
        return False
    
    print()
    print(f"🔧 Criando novo banco SQLite...")
    
    try:
        # Conecta ao banco (cria se não existe)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Cria tabela de manutenções
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS manutencoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                DATA TEXT,
                PLACA TEXT,
                KM REAL,
                [VEÍCULO] TEXT,
                [DESTINO PROGRAMADO] TEXT,
                [SERVIÇO A EXECUTAR] TEXT,
                STATUS TEXT,
                [DATA ENTRADA] TEXT,
                [DATA SAÍDA] TEXT,
                [TOTAL DE DIAS EM MANUTENÇÃO] INTEGER,
                [NR° OF] TEXT,
                OBS TEXT,
                data_criacao TEXT
            )
        """)
        
        # Cria tabela de veículos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS veiculos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                PLACA TEXT UNIQUE NOT NULL,
                TIPO_VEICULO TEXT NOT NULL,
                DESCRICAO TEXT,
                ULTIMA_KM REAL DEFAULT 0,
                STATUS TEXT DEFAULT 'ATIVO',
                data_criacao TEXT
            )
        """)
        
        # Cria tabela de destinos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS destinos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                NOME TEXT UNIQUE NOT NULL,
                STATUS TEXT DEFAULT 'ATIVO',
                data_criacao TEXT
            )
        """)
        
        # Cria tabela de notas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_programada TEXT NOT NULL,
                placa TEXT NOT NULL,
                status TEXT,
                observacao TEXT,
                data_criacao TEXT
            )
        """)
        
        print("✅ Tabelas criadas com sucesso")
        print()
        
        # Importa dados do Excel
        print(f"📥 Importando {len(df_excel)} registros...")
        
        contador = 0
        for idx, row in df_excel.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO manutencoes (
                        DATA, PLACA, KM, [VEÍCULO], [DESTINO PROGRAMADO],
                        [SERVIÇO A EXECUTAR], STATUS, [DATA ENTRADA], [DATA SAÍDA],
                        [TOTAL DE DIAS EM MANUTENÇÃO], [NR° OF], OBS, data_criacao
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(row.get('DATA', '')),
                    str(row.get('PLACA', '')),
                    float(row.get('KM', 0)) if pd.notna(row.get('KM')) else 0,
                    str(row.get('VEÍCULO', '')),
                    str(row.get('DESTINO PROGRAMADO', '')),
                    str(row.get('SERVIÇO A EXECUTAR', '')),
                    str(row.get('STATUS', '')),
                    str(row.get('DATA ENTRADA', '')),
                    str(row.get('DATA SAÍDA', '')),
                    int(row.get('TOTAL DE DIAS EM MANUTENÇÃO', 0)) if pd.notna(row.get('TOTAL DE DIAS EM MANUTENÇÃO')) else 0,
                    str(row.get('NR° OF', '')),
                    str(row.get('OBS', '')),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
                contador += 1
            except Exception as e:
                print(f"⚠️  Erro no registro {idx}: {e}")
        
        conn.commit()
        print(f"✅ {contador} registros importados com sucesso!")
        print()
        
        # Auto-cadastra veículos únicos
        print("🚛 Cadastrando veículos automaticamente...")
        cursor.execute("""
            INSERT OR IGNORE INTO veiculos (PLACA, TIPO_VEICULO, DESCRICAO, STATUS, data_criacao)
            SELECT DISTINCT 
                PLACA,
                [VEÍCULO],
                'Importado automaticamente',
                'ATIVO',
                ?
            FROM manutencoes
            WHERE PLACA IS NOT NULL AND PLACA != ''
        """, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),))
        
        veiculos_cadastrados = cursor.rowcount
        print(f"✅ {veiculos_cadastrados} veículos cadastrados")
        print()
        
        # Auto-cadastra destinos únicos
        print("📍 Cadastrando destinos automaticamente...")
        cursor.execute("""
            INSERT OR IGNORE INTO destinos (NOME, STATUS, data_criacao)
            SELECT DISTINCT 
                [DESTINO PROGRAMADO],
                'ATIVO',
                ?
            FROM manutencoes
            WHERE [DESTINO PROGRAMADO] IS NOT NULL AND [DESTINO PROGRAMADO] != ''
        """, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),))
        
        destinos_cadastrados = cursor.rowcount
        print(f"✅ {destinos_cadastrados} destinos cadastrados")
        print()
        
        conn.commit()
        conn.close()
        
        print("=" * 60)
        print("✅ IMPORTAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print()
        print(f"📊 Resumo:")
        print(f"   • {contador} registros de manutenção")
        print(f"   • {veiculos_cadastrados} veículos únicos")
        print(f"   • {destinos_cadastrados} destinos únicos")
        print()
        print(f"🗄️  Banco de dados: {db_path}")
        print(f"💾 Backup anterior: {backup_db_path if os.path.exists(backup_db_path) else 'N/A'}")
        print()
        print("🚀 Agora você pode executar o sistema normalmente!")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO durante importação: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print()
    importar_excel_para_sqlite()
    print()
    input("Pressione ENTER para sair...")
