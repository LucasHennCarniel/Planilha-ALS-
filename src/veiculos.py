"""
Gestão de Cadastro de Veículos - SQLite Integrado
"""
import sqlite3
import pandas as pd
import os
from datetime import datetime


class GerenciadorVeiculos:
    """
    Gerencia o cadastro de veículos da frota no SQLite
    Mantém interface compatível com DataFrame
    """
    
    def __init__(self, db_path='data/sistema_als.db'):
        self.db_path = db_path
        self.conn = None
        self.df = None  # Compatibilidade
        
        self.conectar()
        self.criar_tabela()
        self.carregar_veiculos()
    
    
    def conectar(self):
        """Conecta ao banco SQLite"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            return True
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            return False
    
    
    def criar_tabela(self):
        """Cria tabela de veículos se não existir"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS veiculos (
                    placa TEXT PRIMARY KEY,
                    tipo_veiculo TEXT NOT NULL,
                    descricao TEXT,
                    ultima_km INTEGER DEFAULT 0,
                    data_cadastro TEXT,
                    ativo INTEGER DEFAULT 1
                )
            """)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Erro ao criar tabela: {e}")
            return False
    
    
    def carregar_veiculos(self):
        """Carrega veículos do SQLite para DataFrame"""
        try:
            query = "SELECT * FROM veiculos ORDER BY placa"
            self.df = pd.read_sql_query(query, self.conn)
            
            # Renomeia para formato Excel (compatibilidade)
            if not self.df.empty:
                self.df = self.df.rename(columns={
                    'tipo_veiculo': 'TIPO_VEICULO',
                    'placa': 'PLACA',
                    'descricao': 'DESCRICAO',
                    'ultima_km': 'ULTIMA_KM',
                    'data_cadastro': 'DATA_CADASTRO',
                    'ativo': 'ATIVO'
                })
                self.df['ATIVO'] = self.df['ATIVO'].astype(bool)
                self.df = self.df.fillna('')
            else:
                self.df = self.criar_dataframe_vazio()
                
        except Exception as e:
            print(f"Aviso: {e}")
            self.df = self.criar_dataframe_vazio()
    
    
    def criar_dataframe_vazio(self):
        """Cria DataFrame vazio com estrutura correta"""
        return pd.DataFrame(columns=[
            'TIPO_VEICULO', 'PLACA', 'DESCRICAO', 
            'ULTIMA_KM', 'DATA_CADASTRO', 'ATIVO'
        ])
    
    
    def adicionar_veiculo(self, tipo, placa, descricao='', km_inicial=0):
        """Adiciona novo veículo ao cadastro"""
        try:
            placa = placa.upper().strip()
            
            # Verifica se já existe
            cursor = self.conn.cursor()
            cursor.execute("SELECT placa FROM veiculos WHERE placa = ?", (placa,))
            if cursor.fetchone():
                return False, "Placa já cadastrada!"
            
            # Insere veículo (descrição OPCIONAL)
            cursor.execute("""
                INSERT INTO veiculos (placa, tipo_veiculo, descricao, ultima_km, data_cadastro, ativo)
                VALUES (?, ?, ?, ?, ?, 1)
            """, (placa, tipo, descricao if descricao else None, km_inicial, datetime.now().strftime('%d/%m/%Y')))
            
            self.conn.commit()
            self.carregar_veiculos()  # Atualiza DataFrame
            return True, "Veículo cadastrado com sucesso!"
            
        except Exception as e:
            self.conn.rollback()
            return False, f"Erro: {e}"
    
    
    def atualizar_veiculo(self, indice, tipo, placa, descricao, ativo):
        """Atualiza dados de um veículo"""
        try:
            placa_antiga = self.df.iloc[indice]['PLACA']
            
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE veiculos 
                SET tipo_veiculo = ?, placa = ?, descricao = ?, ativo = ?
                WHERE placa = ?
            """, (tipo, placa.upper(), descricao if descricao else None, 1 if ativo else 0, placa_antiga))
            
            self.conn.commit()
            self.carregar_veiculos()
            return True, "Veículo atualizado com sucesso!"
        except Exception as e:
            self.conn.rollback()
            return False, f"Erro: {e}"
    
    
    def atualizar_km(self, placa, nova_km):
        """Atualiza a KM de um veículo"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE veiculos SET ultima_km = ? WHERE placa = ?", 
                         (nova_km, placa.upper()))
            self.conn.commit()
            self.carregar_veiculos()
            return True
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    
    def obter_veiculo_por_placa(self, placa):
        """Retorna dados de um veículo pela placa"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM veiculos WHERE placa = ?", (placa.upper(),))
            result = cursor.fetchone()
            if result:
                return {
                    'PLACA': result[0],
                    'TIPO_VEICULO': result[1],
                    'DESCRICAO': result[2] or '',
                    'ULTIMA_KM': result[3],
                    'DATA_CADASTRO': result[4],
                    'ATIVO': bool(result[5])
                }
            return None
        except Exception as e:
            print(f" Erro: {e}")
            return None
    
    
    def obter_veiculos_ativos(self):
        """Retorna lista de veículos ativos formatada"""
        if self.df.empty:
            return []
        
        veiculos_ativos = self.df[self.df['ATIVO'] == True].copy()
        
        lista = []
        for _, row in veiculos_ativos.iterrows():
            texto = f"{row['TIPO_VEICULO']} - {row['PLACA']}"
            if row['DESCRICAO']:
                texto += f" ({row['DESCRICAO']})"
            lista.append(texto)
        
        return lista
    
    
    def obter_veiculos_por_tipo(self, tipo):
        """Retorna veículos de um tipo específico"""
        if self.df.empty:
            return []
        
        mascara = (self.df['TIPO_VEICULO'] == tipo) & (self.df['ATIVO'] == True)
        veiculos = self.df[mascara].copy()
        
        lista = []
        for _, row in veiculos.iterrows():
            texto = f"{row['PLACA']}"
            if row['DESCRICAO']:
                texto += f" - {row['DESCRICAO']}"
            lista.append(texto)
        
        return lista
    
    
    def extrair_placa_da_selecao(self, texto_selecao):
        """Extrai a placa do texto selecionado"""
        if ' - ' in texto_selecao:
            partes = texto_selecao.split(' - ')
            if len(partes) >= 2:
                # Se começa com tipo de veículo, pega segunda parte
                if partes[0] in ['CAVALO', 'CARRETA 1', 'CARRETA 2', 'BUG 1', 'BUG 2', 'LS', 'INDEFINIDO']:
                    placa = partes[1].split(' ')[0]  # Pega primeira palavra (a placa)
                else:
                    placa = partes[0]
                return placa.strip()
        return texto_selecao.strip()
    
    
    def excluir_veiculo(self, indice):
        """Desativa um veículo (não exclui, apenas marca como inativo)"""
        try:
            placa = self.df.iloc[indice]['PLACA']
            cursor = self.conn.cursor()
            cursor.execute("UPDATE veiculos SET ativo = 0 WHERE placa = ?", (placa,))
            self.conn.commit()
            self.carregar_veiculos()
            return True, "Veículo desativado com sucesso!"
        except Exception as e:
            self.conn.rollback()
            return False, f"Erro: {e}"
    
    
    def salvar_dados(self):
        """Mantém compatibilidade (dados já salvos no SQLite)"""
        return True
    
    
    def obter_estatisticas(self):
        """Retorna estatísticas do cadastro"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM veiculos WHERE ativo = 1")
            ativos = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM veiculos")
            total = cursor.fetchone()[0]
            
            # Estatísticas por tipo
            cursor.execute("""
                SELECT tipo_veiculo, COUNT(*) 
                FROM veiculos 
                WHERE ativo = 1 
                GROUP BY tipo_veiculo 
                ORDER BY COUNT(*) DESC
            """)
            por_tipo = dict(cursor.fetchall())
            
            return {
                'total': total,
                'ativos': ativos,
                'inativos': total - ativos,
                'por_tipo': por_tipo
            }
        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
            return {'total': 0, 'ativos': 0, 'inativos': 0, 'por_tipo': {}}
