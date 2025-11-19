#!/usr/bin/env python
# -*- coding: utf-8 -*-
codigo = '''"""
Gestão de Cadastro de Destinos - SQLite Integrado
"""
import sqlite3
import pandas as pd
import os
from datetime import datetime


class GerenciadorDestinos:
    """
    Gerencia o cadastro de destinos de manutenção no SQLite
    Mantém interface compatível com DataFrame
    """
    
    def __init__(self, db_path='data/sistema_als.db'):
        self.db_path = db_path
        self.conn = None
        self.df = None
        
        self.conectar()
        self.criar_tabela()
        self.carregar_destinos()
        self.garantir_destinos_padrao()
    
    
    def conectar(self):
        """Conecta ao banco SQLite"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            return True
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            return False
    
    
    def criar_tabela(self):
        """Cria tabela de destinos se não existir"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS destinos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_destino TEXT NOT NULL UNIQUE,
                    data_cadastro TEXT,
                    ativo INTEGER DEFAULT 1
                )
            """)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Erro ao criar tabela: {e}")
            return False
    
    
    def carregar_destinos(self):
        """Carrega destinos do SQLite para DataFrame"""
        try:
            query = "SELECT * FROM destinos ORDER BY nome_destino"
            self.df = pd.read_sql_query(query, self.conn)
            
            if not self.df.empty:
                self.df = self.df.rename(columns={
                    'nome_destino': 'NOME_DESTINO',
                    'data_cadastro': 'DATA_CADASTRO',
                    'ativo': 'ATIVO'
                })
                self.df['ATIVO'] = self.df['ATIVO'].astype(bool)
            else:
                self.df = self.criar_dataframe_vazio()
                
        except Exception as e:
            print(f"Aviso: {e}")
            self.df = self.criar_dataframe_vazio()
    
    
    def criar_dataframe_vazio(self):
        """Cria DataFrame vazio com estrutura correta"""
        return pd.DataFrame(columns=['NOME_DESTINO', 'DATA_CADASTRO', 'ATIVO'])
    
    
    def garantir_destinos_padrao(self):
        """Garante que os destinos padrão existam no banco"""
        destinos_padrao = [
            'AGYLE', 'BOM SUCESSO', 'FARROUPILHA', 'FLORIÓPOLIS',
            'G&V', 'GARIBALDI', 'JOINVILLE/SC', 'NOVA TRENTO', 'SALTO VELOSO'
        ]
        
        for destino in destinos_padrao:
            self.adicionar_destino(destino, silencioso=True)
    
    
    def adicionar_destino(self, nome, silencioso=False):
        """Adiciona novo destino ao cadastro"""
        try:
            nome = nome.upper().strip()
            
            cursor = self.conn.cursor()
            cursor.execute("SELECT nome_destino FROM destinos WHERE UPPER(nome_destino) = ?", (nome,))
            if cursor.fetchone():
                if not silencioso:
                    return False, "Destino já cadastrado!"
                return True, "Destino já existe"
            
            cursor.execute("""
                INSERT INTO destinos (nome_destino, data_cadastro, ativo)
                VALUES (?, ?, 1)
            """, (nome, datetime.now().strftime('%d/%m/%Y')))
            
            self.conn.commit()
            self.carregar_destinos()
            
            if not silencioso:
                return True, "Destino cadastrado com sucesso!"
            return True, "OK"
            
        except Exception as e:
            self.conn.rollback()
            if not silencioso:
                return False, f"Erro: {e}"
            return False, str(e)
    
    
    def obter_destinos_ativos(self):
        """Retorna lista de destinos ativos"""
        if self.df.empty:
            return []
        
        destinos_ativos = self.df[self.df['ATIVO'] == True].copy()
        return sorted(destinos_ativos['NOME_DESTINO'].tolist())
    
    
    def atualizar_destino(self, indice, nome, ativo):
        """Atualiza dados de um destino"""
        try:
            id_destino = self.df.iloc[indice]['id']
            
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE destinos 
                SET nome_destino = ?, ativo = ?
                WHERE id = ?
            """, (nome.upper(), 1 if ativo else 0, id_destino))
            
            self.conn.commit()
            self.carregar_destinos()
            return True, "Destino atualizado com sucesso!"
        except Exception as e:
            self.conn.rollback()
            return False, f"Erro: {e}"
    
    
    def excluir_destino(self, indice):
        """Desativa um destino (não exclui, apenas marca como inativo)"""
        try:
            id_destino = self.df.iloc[indice]['id']
            cursor = self.conn.cursor()
            cursor.execute("UPDATE destinos SET ativo = 0 WHERE id = ?", (id_destino,))
            self.conn.commit()
            self.carregar_destinos()
            return True, "Destino desativado com sucesso!"
        except Exception as e:
            self.conn.rollback()
            return False, f"Erro: {e}"
'''

with open('src/destinos.py', 'w', encoding='utf-8') as f:
    f.write(codigo)
    
print("✅ Arquivo destinos.py criado com sucesso!")
