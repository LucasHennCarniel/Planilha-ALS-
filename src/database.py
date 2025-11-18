"""
Gerenciamento de dados e persistência
"""
import pandas as pd
import os
from datetime import datetime
from .utils import (
    calcular_dias_manutencao, 
    calcular_status, 
    formatar_data_br,
    limpar_texto
)


class DatabaseManager:
    """
    Gerencia operações de banco de dados (Excel)
    """
    
    def __init__(self, arquivo_excel='data/PROGRAMAÇÃO MANUTENÇÃO (CÓPIA 2).xlsx'):
        self.arquivo = arquivo_excel
        self.df = None
        self.colunas_obrigatorias = [
            'DATA', 'PLACA', 'KM', 'VEÍCULO', 'DESTINO PROGRAMADO',
            'SERVIÇO A EXECUTAR', 'STATUS', 'DATA ENTRADA', 'DATA SAÍDA',
            'TOTAL DE DIAS EM MANUTENÇÃO', 'NR° OF', 'OBS'
        ]
        
        # Cria pastas se não existirem
        os.makedirs('data', exist_ok=True)
        os.makedirs('output', exist_ok=True)
        os.makedirs('backup', exist_ok=True)
        
        self.carregar_dados()
    
    
    def carregar_dados(self):
        """
        Carrega dados do Excel ou cria novo arquivo
        """
        try:
            if os.path.exists(self.arquivo):
                # Tenta ler da primeira aba
                self.df = pd.read_excel(self.arquivo, sheet_name=0)
                
                # Remove linhas completamente vazias
                self.df = self.df.dropna(how='all')
                
                # Garante que todas as colunas existem
                for col in self.colunas_obrigatorias:
                    if col not in self.df.columns:
                        self.df[col] = ''
                
                # Limpa dados
                self.df = self.df.fillna('')
                
                # *** FILTRO IMPORTANTE: Remove registros sem PLACA (linhas vazias) ***
                self.df = self.df[self.df['PLACA'].astype(str).str.strip() != '']
                
                # Reset do índice após filtrar
                self.df = self.df.reset_index(drop=True)
                
            else:
                # Cria DataFrame vazio com colunas obrigatórias
                self.df = pd.DataFrame(columns=self.colunas_obrigatorias)
                
        except Exception as e:
            # Cria DataFrame vazio em caso de erro
            self.df = pd.DataFrame(columns=self.colunas_obrigatorias)
    
    
    def salvar_dados(self):
        """
        Salva dados no Excel com backup
        """
        try:
            # Faz backup antes de salvar
            if os.path.exists(self.arquivo):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_file = f'backup/backup_{timestamp}.xlsx'
                import shutil
                shutil.copy2(self.arquivo, backup_file)
            
            # Recalcula campos automáticos antes de salvar
            self.recalcular_campos()
            
            # Salva o arquivo
            self.df.to_excel(self.arquivo, index=False, sheet_name='PROGRAMAÇÃO')
            return True
            
        except Exception as e:
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
