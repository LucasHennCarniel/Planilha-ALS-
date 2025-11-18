"""
Gestão de Cadastro de Veículos
"""
import pandas as pd
import os
from datetime import datetime


class GerenciadorVeiculos:
    """
    Gerencia o cadastro de veículos da frota
    """
    
    def __init__(self):
        self.arquivo = 'data/cadastro_veiculos.xlsx'
        self.df = self.carregar_veiculos()
    
    
    def carregar_veiculos(self):
        """
        Carrega cadastro de veículos ou cria novo
        """
        if os.path.exists(self.arquivo):
            try:
                df = pd.read_excel(self.arquivo)
                return df
            except Exception as e:
                print(f"Erro ao carregar veículos: {e}")
                return self.criar_dataframe_vazio()
        else:
            return self.criar_dataframe_vazio()
    
    
    def criar_dataframe_vazio(self):
        """
        Cria DataFrame vazio com estrutura correta
        """
        return pd.DataFrame(columns=[
            'TIPO_VEICULO',  # CAVALO, CARRETA 1, CARRETA 2, BUG 1, BUG 2, LS
            'PLACA',
            'DESCRICAO',     # Descrição adicional (ex: Cavalo Volvo FH, etc)
            'ULTIMA_KM',     # Última KM registrada
            'DATA_CADASTRO',
            'ATIVO'          # True/False
        ])
    
    
    def adicionar_veiculo(self, tipo, placa, descricao='', km_inicial=0):
        """
        Adiciona novo veículo ao cadastro
        """
        # Verifica se placa já existe
        if not self.df.empty and placa.upper() in self.df['PLACA'].str.upper().values:
            return False, "Placa já cadastrada!"
        
        novo_veiculo = {
            'TIPO_VEICULO': tipo,
            'PLACA': placa.upper(),
            'DESCRICAO': descricao,
            'ULTIMA_KM': km_inicial,
            'DATA_CADASTRO': datetime.now().strftime('%d/%m/%Y'),
            'ATIVO': True
        }
        
        self.df = pd.concat([self.df, pd.DataFrame([novo_veiculo])], ignore_index=True)
        return True, "Veículo cadastrado com sucesso!"
    
    
    def atualizar_veiculo(self, indice, tipo, placa, descricao, ativo):
        """
        Atualiza dados de um veículo
        """
        try:
            self.df.at[indice, 'TIPO_VEICULO'] = tipo
            self.df.at[indice, 'PLACA'] = placa.upper()
            self.df.at[indice, 'DESCRICAO'] = descricao
            self.df.at[indice, 'ATIVO'] = ativo
            return True, "Veículo atualizado com sucesso!"
        except Exception as e:
            return False, f"Erro ao atualizar: {e}"
    
    
    def atualizar_km(self, placa, nova_km):
        """
        Atualiza a KM de um veículo após uma manutenção
        """
        try:
            mascara = self.df['PLACA'].str.upper() == placa.upper()
            if mascara.any():
                self.df.loc[mascara, 'ULTIMA_KM'] = nova_km
                return True
            return False
        except Exception as e:
            print(f"Erro ao atualizar KM: {e}")
            return False
    
    
    def obter_veiculo_por_placa(self, placa):
        """
        Retorna dados de um veículo pela placa
        """
        mascara = self.df['PLACA'].str.upper() == placa.upper()
        if mascara.any():
            return self.df[mascara].iloc[0].to_dict()
        return None
    
    
    def obter_veiculos_ativos(self):
        """
        Retorna lista de veículos ativos
        """
        if self.df.empty:
            return []
        
        veiculos_ativos = self.df[self.df['ATIVO'] == True].copy()
        
        # Formata para exibição: "TIPO - PLACA (Descrição)"
        lista = []
        for _, row in veiculos_ativos.iterrows():
            texto = f"{row['TIPO_VEICULO']} - {row['PLACA']}"
            if row['DESCRICAO']:
                texto += f" ({row['DESCRICAO']})"
            lista.append(texto)
        
        return lista
    
    
    def obter_veiculos_por_tipo(self, tipo):
        """
        Retorna veículos de um tipo específico
        """
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
        """
        Extrai a placa do texto selecionado
        Formato esperado: "TIPO - PLACA (Descrição)" ou "PLACA - Descrição"
        """
        if ' - ' in texto_selecao:
            partes = texto_selecao.split(' - ')
            if len(partes) >= 2:
                # Se começa com tipo de veículo, pega segunda parte
                if partes[0] in ['CAVALO', 'CARRETA 1', 'CARRETA 2', 'BUG 1', 'BUG 2', 'LS']:
                    placa = partes[1].split(' ')[0]  # Pega primeira palavra (a placa)
                else:
                    placa = partes[0]
                return placa.strip()
        return texto_selecao.strip()
    
    
    def excluir_veiculo(self, indice):
        """
        Desativa um veículo (não exclui, apenas marca como inativo)
        """
        try:
            self.df.at[indice, 'ATIVO'] = False
            return True, "Veículo desativado com sucesso!"
        except Exception as e:
            return False, f"Erro ao desativar: {e}"
    
    
    def salvar_dados(self):
        """
        Salva cadastro de veículos no Excel
        """
        try:
            # Garante que diretório existe
            os.makedirs(os.path.dirname(self.arquivo), exist_ok=True)
            
            # Salva
            self.df.to_excel(self.arquivo, index=False, sheet_name='Veículos')
            return True
        except Exception as e:
            print(f"Erro ao salvar veículos: {e}")
            return False
    
    
    def obter_estatisticas(self):
        """
        Retorna estatísticas do cadastro
        """
        if self.df.empty:
            return {
                'total': 0,
                'ativos': 0,
                'inativos': 0,
                'por_tipo': {}
            }
        
        stats = {
            'total': len(self.df),
            'ativos': len(self.df[self.df['ATIVO'] == True]),
            'inativos': len(self.df[self.df['ATIVO'] == False]),
            'por_tipo': {}
        }
        
        # Conta por tipo
        veiculos_ativos = self.df[self.df['ATIVO'] == True]
        if not veiculos_ativos.empty:
            contagem = veiculos_ativos['TIPO_VEICULO'].value_counts().to_dict()
            stats['por_tipo'] = contagem
        
        return stats
