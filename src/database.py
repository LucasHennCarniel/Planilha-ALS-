"""
Gerenciamento de dados e persistência - SQLite Integrado
"""
import sqlite3
import pandas as pd
import os
import shutil
from datetime import datetime
from .utils import (
    calcular_dias_manutencao, 
    calcular_status, 
    formatar_data_br,
    limpar_texto
)


class DatabaseManager:
    """
    Gerencia operações de banco de dados com SQLite
    Interface compatível com código existente (usa DataFrame)
    """
    
    def __init__(self, db_path='data/sistema_als.db'):
        self.db_path = db_path
        self.conn = None
        self.df = None  # Mantém compatibilidade com código existente
        
        self.colunas_obrigatorias = [
            'DATA', 'PLACA', 'KM', 'VEÍCULO', 'DESTINO PROGRAMADO',
            'SERVIÇO A EXECUTAR', 'STATUS', 'DATA ENTRADA', 'DATA SAÍDA',
            'TOTAL DE DIAS EM MANUTENÇÃO', 'NR° OF', 'OBS'
        ]
        
        # Cria pastas se não existirem
        os.makedirs('data', exist_ok=True)
        os.makedirs('output', exist_ok=True)
        os.makedirs('backup', exist_ok=True)
        
        self.conectar()
        self.criar_tabelas()
        self.carregar_dados()
    
    
    def conectar(self):
        """Conecta ao banco SQLite"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.execute("PRAGMA foreign_keys = ON")
            return True
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            return False
    
    
    def criar_tabelas(self):
        """Cria tabelas se não existirem"""
        try:
            cursor = self.conn.cursor()
            
            # Tabela MANUTENÇÕES (estrutura idêntica ao Excel)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS manutencoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT NOT NULL,
                    placa TEXT NOT NULL,
                    km INTEGER,
                    veiculo TEXT,
                    destino_programado TEXT,
                    servico_executar TEXT,
                    status TEXT,
                    data_entrada TEXT,
                    data_saida TEXT,
                    total_dias_manutencao INTEGER,
                    nr_of TEXT,
                    obs TEXT,
                    UNIQUE(placa, data)
                )
            """)
            
            # Índices para performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_placa ON manutencoes(placa)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_data ON manutencoes(data)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON manutencoes(status)")
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Erro ao criar tabelas: {e}")
            return False
    
    
    def carregar_dados(self):
        """
        Carrega dados do SQLite para DataFrame (compatibilidade)
        """
        try:
            # Lê do SQLite
            query = "SELECT * FROM manutencoes ORDER BY data DESC"
            self.df = pd.read_sql_query(query, self.conn)
            
            # Renomeia colunas para formato Excel (maiúsculas com acentos)
            if not self.df.empty:
                self.df = self.df.rename(columns={
                    'data': 'DATA',
                    'placa': 'PLACA',
                    'km': 'KM',
                    'veiculo': 'VEÍCULO',
                    'destino_programado': 'DESTINO PROGRAMADO',
                    'servico_executar': 'SERVIÇO A EXECUTAR',
                    'status': 'STATUS',
                    'data_entrada': 'DATA ENTRADA',
                    'data_saida': 'DATA SAÍDA',
                    'total_dias_manutencao': 'TOTAL DE DIAS EM MANUTENÇÃO',
                    'nr_of': 'NR° OF',
                    'obs': 'OBS'
                })
                
                # Remove coluna ID (compatibilidade)
                if 'id' in self.df.columns:
                    self.df = self.df.drop(columns=['id'])
                
                self.df = self.df.fillna('')
            else:
                # Cria DataFrame vazio
                self.df = pd.DataFrame(columns=self.colunas_obrigatorias)
                
        except Exception as e:
            print(f"Aviso: {e}")
            self.df = pd.DataFrame(columns=self.colunas_obrigatorias)
    
    
    def salvar_dados(self):
        """
        Salva dados do DataFrame no SQLite com backup
        """
        try:
            # Faz backup do banco
            if os.path.exists(self.db_path):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_file = f'backup/database_backup_{timestamp}.db'
                shutil.copy2(self.db_path, backup_file)
            
            # Recalcula campos automáticos
            self.recalcular_campos()
            
            # Limpa tabela
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM manutencoes")
            
            # Insere dados do DataFrame
            for _, row in self.df.iterrows():
                cursor.execute("""
                    INSERT INTO manutencoes (
                        data, placa, km, veiculo, destino_programado,
                        servico_executar, status, data_entrada, data_saida,
                        total_dias_manutencao, nr_of, obs
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row.get('DATA', ''),
                    row.get('PLACA', ''),
                    row.get('KM', 0),
                    row.get('VEÍCULO', ''),
                    row.get('DESTINO PROGRAMADO', ''),
                    row.get('SERVIÇO A EXECUTAR', ''),
                    row.get('STATUS', ''),
                    row.get('DATA ENTRADA', ''),
                    row.get('DATA SAÍDA', ''),
                    row.get('TOTAL DE DIAS EM MANUTENÇÃO', 0),
                    row.get('NR° OF', ''),
                    row.get('OBS', '')
                ))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
            self.conn.rollback()
            return False
    
    
    def recalcular_campos(self):
        """
        Recalcula campos automáticos (dias, status)
        """
        for idx, row in self.df.iterrows():
            # Calcula dias em manutenção
            dias = calcular_dias_manutencao(
                row.get('DATA ENTRADA'), 
                row.get('DATA SAÍDA')
            )
            self.df.at[idx, 'TOTAL DE DIAS EM MANUTENÇÃO'] = dias
            
            # Atualiza status
            status = calcular_status(
                row.get('DATA ENTRADA'),
                row.get('DATA SAÍDA'),
                row.get('STATUS', '')
            )
            self.df.at[idx, 'STATUS'] = status
    
    
    def adicionar_registro(self, dados):
        """
        Adiciona novo registro
        """
        try:
            # Garante que todos os campos existem
            registro = {}
            for col in self.colunas_obrigatorias:
                registro[col] = dados.get(col, '')
            
            # Cria DataFrame com novo registro
            novo_registro = pd.DataFrame([registro])
            
            # Adiciona ao DataFrame principal
            self.df = pd.concat([self.df, novo_registro], ignore_index=True)
            
            return True
            
        except Exception as e:
            return False
    
    
    def atualizar_registro(self, indice, dados):
        """
        Atualiza registro existente
        """
        try:
            for chave, valor in dados.items():
                if chave in self.df.columns:
                    self.df.at[indice, chave] = valor
            
            return True
            
        except Exception as e:
            return False
    
    
    def excluir_registro(self, indice):
        """
        Exclui registro
        """
        try:
            self.df = self.df.drop(indice).reset_index(drop=True)
            return True
            
        except Exception as e:
            return False
    
    
    def buscar_registros(self, filtros):
        """
        Busca registros com filtros
        """
        df_filtrado = self.df.copy()
        
        for campo, valor in filtros.items():
            if valor and campo in df_filtrado.columns:
                df_filtrado = df_filtrado[
                    df_filtrado[campo].astype(str).str.contains(str(valor), case=False, na=False)
                ]
        
        return df_filtrado
    
    
    def obter_estatisticas(self):
        """
        Retorna estatísticas gerais
        """
        stats = {}
        
        # Total de registros
        stats['total_registros'] = len(self.df)
        
        # Veículos em serviço
        em_servico = len(self.df[self.df['STATUS'].str.upper() == 'EM SERVIÇO'])
        stats['em_servico'] = em_servico
        
        # Finalizados
        finalizados = len(self.df[self.df['STATUS'].str.upper() == 'FINALIZADO'])
        stats['finalizados'] = finalizados
        
        # Tempo médio de manutenção
        self.df['TOTAL DE DIAS EM MANUTENÇÃO'] = pd.to_numeric(
            self.df['TOTAL DE DIAS EM MANUTENÇÃO'], errors='coerce'
        )
        tempo_medio = self.df['TOTAL DE DIAS EM MANUTENÇÃO'].mean()
        stats['tempo_medio'] = tempo_medio if not pd.isna(tempo_medio) else 0
        
        # Placas únicas
        placas_unicas = self.df[self.df['PLACA'] != '']['PLACA'].nunique()
        stats['placas_unicas'] = placas_unicas
        
        return stats
    
    
    def obter_dataframe_exibicao(self):
        """
        Retorna DataFrame formatado para exibição
        """
        df_display = self.df.copy()
        
        # Formata datas
        for col in ['DATA', 'DATA ENTRADA', 'DATA SAÍDA']:
            if col in df_display.columns:
                df_display[col] = df_display[col].apply(formatar_data_br)
        
        # Formata números
        if 'TOTAL DE DIAS EM MANUTENÇÃO' in df_display.columns:
            df_display['DIAS'] = df_display['TOTAL DE DIAS EM MANUTENÇÃO'].apply(
                lambda x: str(int(x)) if pd.notna(x) and x != '' else '0'
            )
        
        return df_display
