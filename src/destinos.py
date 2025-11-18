"""
Gestão de Cadastro de Destinos
"""
import pandas as pd
import os
from datetime import datetime


class GerenciadorDestinos:
    """
    Gerencia o cadastro de destinos de manutenção
    """
    
    def __init__(self):
        self.arquivo = 'data/cadastro_destinos.xlsx'
        self.df = self.carregar_destinos()
        
        # Garante que destinos padrão existam
        self.garantir_destinos_padrao()
    
    
    def carregar_destinos(self):
        """
        Carrega cadastro de destinos ou cria novo
        """
        if os.path.exists(self.arquivo):
            try:
                df = pd.read_excel(self.arquivo)
                return df
            except Exception as e:
                print(f"Erro ao carregar destinos: {e}")
                return self.criar_dataframe_vazio()
        else:
            return self.criar_dataframe_vazio()
    
    
    def criar_dataframe_vazio(self):
        """
        Cria DataFrame vazio com estrutura correta
        """
        return pd.DataFrame(columns=[
            'NOME_DESTINO',
            'DATA_CADASTRO',
            'ATIVO'
        ])
    
    
    def garantir_destinos_padrao(self):
        """
        Garante que destinos padrão existam no cadastro
        """
        destinos_padrao = [
            'AGYLE',
            'BOM SUCESSO',
            'M&S',
            'DAF BARIGUI',
            'PAULISTA FREIOS',
            'KREUSCH',
            'CAMINHALTO',
            'OUTROS'
        ]
        
        alterado = False
        for destino in destinos_padrao:
            if self.df.empty or destino not in self.df['NOME_DESTINO'].values:
                novo_destino = {
                    'NOME_DESTINO': destino,
                    'DATA_CADASTRO': datetime.now().strftime('%d/%m/%Y'),
                    'ATIVO': True
                }
                self.df = pd.concat([self.df, pd.DataFrame([novo_destino])], ignore_index=True)
                alterado = True
        
        if alterado:
            self.salvar_dados()
    
    
    def adicionar_destino(self, nome):
        """
        Adiciona novo destino ao cadastro
        """
        nome = nome.strip().upper()
        
        if not nome:
            return False, "Nome do destino não pode estar vazio!"
        
        # Verifica se destino já existe
        if not self.df.empty and nome in self.df['NOME_DESTINO'].str.upper().values:
            return False, "Destino já cadastrado!"
        
        novo_destino = {
            'NOME_DESTINO': nome,
            'DATA_CADASTRO': datetime.now().strftime('%d/%m/%Y'),
            'ATIVO': True
        }
        
        self.df = pd.concat([self.df, pd.DataFrame([novo_destino])], ignore_index=True)
        self.salvar_dados()
        return True, "Destino cadastrado com sucesso!"
    
    
    def obter_destinos_ativos(self):
        """
        Retorna lista de destinos ativos ordenada alfabeticamente
        """
        if self.df.empty:
            return []
        
        destinos_ativos = self.df[self.df['ATIVO'] == True].copy()
        destinos_ativos = destinos_ativos.sort_values('NOME_DESTINO')
        
        return destinos_ativos['NOME_DESTINO'].tolist()
    
    
    def desativar_destino(self, nome):
        """
        Desativa um destino (não exclui, apenas marca como inativo)
        """
        try:
            mascara = self.df['NOME_DESTINO'].str.upper() == nome.upper()
            if mascara.any():
                self.df.loc[mascara, 'ATIVO'] = False
                self.salvar_dados()
                return True, "Destino desativado com sucesso!"
            return False, "Destino não encontrado!"
        except Exception as e:
            return False, f"Erro ao desativar: {e}"
    
    
    def salvar_dados(self):
        """
        Salva cadastro de destinos no Excel
        """
        try:
            # Garante que diretório existe
            os.makedirs(os.path.dirname(self.arquivo), exist_ok=True)
            
            # Salva
            self.df.to_excel(self.arquivo, index=False, sheet_name='Destinos')
            return True
        except Exception as e:
            print(f"Erro ao salvar destinos: {e}")
            return False
    
    
    def obter_estatisticas(self):
        """
        Retorna estatísticas do cadastro
        """
        if self.df.empty:
            return {
                'total': 0,
                'ativos': 0,
                'inativos': 0
            }
        
        return {
            'total': len(self.df),
            'ativos': len(self.df[self.df['ATIVO'] == True]),
            'inativos': len(self.df[self.df['ATIVO'] == False])
        }
