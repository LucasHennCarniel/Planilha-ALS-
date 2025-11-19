"""
Sistema de Importação de Dados - VERSÃO SQLITE
Importa APENAS registros com PLACA e DATA preenchidos
AUTO-CADASTRA VEÍCULOS automaticamente durante importação
"""
import pandas as pd
import os
from datetime import datetime
from tkinter import messagebox
from .utils import limpar_texto


class ImportadorDados:
    """
    Gerencia importação de dados de planilhas externas
    REGRA SIMPLES: Só importa se PLACA e DATA estiverem preenchidos
    """
    
    def __init__(self, database_manager, gerenciador_veiculos=None, gerenciador_destinos=None):
        self.db = database_manager
        self.gerenciador_veiculos = gerenciador_veiculos
        self.gerenciador_destinos = gerenciador_destinos
        self.relatorio_importacao = {
            'total_linhas': 0,
            'linhas_validas': 0,
            'linhas_ignoradas': 0,
            'importados': 0,
            'duplicados': 0,
            'veiculos_cadastrados': 0,  # AUTO-CADASTRO
            'destinos_cadastrados': 0,  # AUTO-CADASTRO
            'erros': 0,
            'detalhes': []
        }
    
    
    def validar_planilha(self, df_importar):
        """
        Valida se a planilha tem as colunas PLACA e DATA
        """
        # Remove colunas "Unnamed" (colunas extras do Excel)
        colunas_unnamed = [col for col in df_importar.columns if str(col).startswith('Unnamed')]
        if colunas_unnamed:
            df_importar = df_importar.drop(columns=colunas_unnamed)
        
        colunas_necessarias = ['PLACA', 'DATA']
        colunas_faltando = []
        
        for col in colunas_necessarias:
            if col not in df_importar.columns:
                colunas_faltando.append(col)
        
        if colunas_faltando:
            return False, f"❌ Colunas obrigatórias não encontradas: {', '.join(colunas_faltando)}\n\nA planilha deve ter as colunas PLACA e DATA."
        
        return True, "Planilha válida"
    
    
    def normalizar_colunas(self, df_importar):
        """
        Garante que todas as colunas obrigatórias existem
        """
        # Remove colunas Unnamed
        colunas_unnamed = [col for col in df_importar.columns if str(col).startswith('Unnamed')]
        if colunas_unnamed:
            df_importar = df_importar.drop(columns=colunas_unnamed)
        
        # Adiciona colunas faltantes com valores vazios
        for col in self.db.colunas_obrigatorias:
            if col not in df_importar.columns:
                df_importar[col] = ''
        
        # Reordena colunas para corresponder ao sistema
        df_importar = df_importar[self.db.colunas_obrigatorias]
        
        return df_importar
    
    
    def limpar_dados(self, df_importar):
        """
        Limpa dados e REMOVE linhas sem PLACA ou DATA
        REGRA SIMPLES: Sem PLACA ou DATA = NÃO IMPORTA
        """
        # Remove linhas completamente vazias
        df_importar = df_importar.dropna(how='all')
        
        # Preenche valores nulos com string vazia
        df_importar = df_importar.fillna('')
        
        # **FILTRO PRINCIPAL: Remove registros SEM PLACA ou SEM DATA**
        total_antes = len(df_importar)
        
        # Remove se PLACA estiver vazia
        df_importar = df_importar[df_importar['PLACA'].astype(str).str.strip() != '']
        
        # Remove se DATA estiver vazia
        df_importar = df_importar[df_importar['DATA'].astype(str).str.strip() != '']
        
        total_depois = len(df_importar)
        linhas_removidas = total_antes - total_depois
        
        if linhas_removidas > 0:
            self.relatorio_importacao['linhas_ignoradas'] = linhas_removidas
            self.relatorio_importacao['detalhes'].append(
                f"🗑️ {linhas_removidas} linhas ignoradas (sem PLACA ou DATA)"
            )
        
        self.relatorio_importacao['linhas_validas'] = total_depois
        
        # Limpa espaços em branco excessivos
        for col in df_importar.columns:
            if df_importar[col].dtype == 'object':  # Apenas colunas de texto
                df_importar[col] = df_importar[col].astype(str).str.strip()
        
        # Converte PLACA para maiúsculas
        df_importar['PLACA'] = df_importar['PLACA'].str.upper()
        
        return df_importar
    
    
    def identificar_duplicatas(self, df_importar):
        """
        Identifica registros que já existem no sistema
        Critério: mesma PLACA + mesma DATA
        """
        if self.db.df.empty:
            return df_importar, pd.DataFrame()
        
        # Cria chave única: PLACA + DATA
        df_importar['_chave'] = df_importar['PLACA'].astype(str) + '_' + df_importar['DATA'].astype(str)
        self.db.df['_chave'] = self.db.df['PLACA'].astype(str) + '_' + self.db.df['DATA'].astype(str)
        
        # Separa novos de duplicados
        chaves_existentes = self.db.df['_chave'].values
        mascara_novos = ~df_importar['_chave'].isin(chaves_existentes)
        
        df_novos = df_importar[mascara_novos].copy()
        df_duplicados = df_importar[~mascara_novos].copy()
        
        # Remove coluna auxiliar
        df_novos = df_novos.drop(columns=['_chave'])
        df_duplicados = df_duplicados.drop(columns=['_chave'])
        self.db.df = self.db.df.drop(columns=['_chave'])
        
        return df_novos, df_duplicados
    
    
    def auto_cadastrar_veiculos(self, df_importar):
        """
        Auto-cadastra veículos que ainda não existem no sistema
        DESCRIÇÃO É OPCIONAL: usa campo VEÍCULO da planilha se disponível
        """
        if not self.gerenciador_veiculos:
            return 0
        
        try:
            # Obtém placas únicas da importação
            placas_importar = df_importar['PLACA'].unique()
            
            # Obtém placas já cadastradas
            veiculos_existentes = self.gerenciador_veiculos.df
            if not veiculos_existentes.empty:
                placas_cadastradas = veiculos_existentes['PLACA'].str.upper().values
            else:
                placas_cadastradas = []
            
            veiculos_novos = 0
            
            # Para cada placa na importação
            for placa in placas_importar:
                placa = placa.upper().strip()
                
                # Se placa ainda não existe, cadastra
                if placa not in placas_cadastradas:
                    # Pega descrição do primeiro registro desta placa
                    registro = df_importar[df_importar['PLACA'] == placa].iloc[0]
                    veiculo_desc = str(registro.get('VEÍCULO', '')).strip()
                    
                    # DESCRIÇÃO OPCIONAL: pode ser vazia
                    if not veiculo_desc or veiculo_desc == 'nan':
                        veiculo_desc = ''
                    
                    # Tenta deduzir tipo
                    tipo = "INDEFINIDO"
                    if veiculo_desc:
                        veiculo_desc_upper = veiculo_desc.upper()
                        if "CAVALO" in veiculo_desc_upper:
                            tipo = "CAVALO"
                        elif "CARRETA" in veiculo_desc_upper:
                            if "1" in veiculo_desc_upper:
                                tipo = "CARRETA 1"
                            elif "2" in veiculo_desc_upper:
                                tipo = "CARRETA 2"
                            else:
                                tipo = "CARRETA"
                        elif "BUG" in veiculo_desc_upper:
                            if "1" in veiculo_desc_upper:
                                tipo = "BUG 1"
                            elif "2" in veiculo_desc_upper:
                                tipo = "BUG 2"
                            else:
                                tipo = "BUG"
                        elif "LS" in veiculo_desc_upper:
                            tipo = "LS"
                    
                    # Cadastra veículo (DESCRIÇÃO OPCIONAL)
                    sucesso, msg = self.gerenciador_veiculos.adicionar_veiculo(
                        tipo=tipo,
                        placa=placa,
                        descricao=veiculo_desc if veiculo_desc else '',  # Vazio se não tiver
                        km_inicial=0
                    )
                    
                    if sucesso:
                        veiculos_novos += 1
                        placas_cadastradas = list(placas_cadastradas) + [placa]
            
            # Salva cadastro atualizado
            if veiculos_novos > 0:
                self.gerenciador_veiculos.df.to_excel(
                    self.gerenciador_veiculos.arquivo, 
                    index=False
                )
            
            return veiculos_novos
            
        except Exception as e:
            print(f"❌ Erro ao auto-cadastrar veículos: {e}")
            return 0
    
    
    def auto_cadastrar_destinos(self, df_importar):
        """
        Auto-cadastra destinos que ainda não existem no sistema
        """
        if not self.gerenciador_destinos:
            return 0
        
        try:
            # Obtém destinos únicos da importação
            destinos_importar = df_importar['DESTINO PROGRAMADO'].unique()
            destinos_importar = [d for d in destinos_importar if d and str(d).strip() and str(d).strip().upper() != 'NAN']
            
            # Obtém destinos já cadastrados
            destinos_existentes = self.gerenciador_destinos.df
            if not destinos_existentes.empty:
                destinos_cadastrados = destinos_existentes['NOME_DESTINO'].str.upper().values
            else:
                destinos_cadastrados = []
            
            destinos_novos = 0
            
            # Para cada destino na importação
            for destino in destinos_importar:
                destino = str(destino).strip().upper()
                
                # Se destino ainda não existe, cadastra
                if destino not in destinos_cadastrados:
                    sucesso, msg = self.gerenciador_destinos.adicionar_destino(destino)
                    
                    if sucesso:
                        destinos_novos += 1
                        destinos_cadastrados = list(destinos_cadastrados) + [destino]
            
            return destinos_novos
            
        except Exception as e:
            print(f"❌ Erro ao auto-cadastrar destinos: {e}")
            return 0
    
    
    def importar_planilha(self, caminho_arquivo, modo='adicionar'):
        """
        Importa dados de uma planilha Excel
        
        REGRA: Só importa registros com PLACA e DATA preenchidos
        
        Modos:
        - 'adicionar': Adiciona registros novos, ignora duplicatas
        - 'sobrescrever': Substitui todos os dados (CUIDADO!)
        - 'mesclar': Atualiza duplicatas e adiciona novos
        """
        try:
            # PASSO 1: Ler arquivo
            self.relatorio_importacao['detalhes'].append("📂 Lendo arquivo...")
            
            if not os.path.exists(caminho_arquivo):
                return False, "❌ Arquivo não encontrado!"
            
            # Lê planilha pulando primeira linha (formato ALS)
            df_importar = pd.read_excel(caminho_arquivo, sheet_name=0, header=1)
            
            # Limpa nomes das colunas (remove espaços extras)
            df_importar.columns = df_importar.columns.str.strip()
            
            self.relatorio_importacao['total_linhas'] = len(df_importar)
            self.relatorio_importacao['detalhes'].append(f"✅ {len(df_importar)} linhas encontradas")
            
            
            # PASSO 2: Validar estrutura (verifica se tem PLACA e DATA)
            self.relatorio_importacao['detalhes'].append("🔍 Validando estrutura...")
            valido, mensagem = self.validar_planilha(df_importar)
            
            if not valido:
                return False, mensagem
            
            self.relatorio_importacao['detalhes'].append("✅ Colunas PLACA e DATA encontradas")
            
            
            # PASSO 3: Normalizar colunas
            self.relatorio_importacao['detalhes'].append("🔧 Normalizando colunas...")
            df_importar = self.normalizar_colunas(df_importar)
            
            
            # PASSO 4: Limpar dados (REMOVE LINHAS SEM PLACA OU DATA)
            self.relatorio_importacao['detalhes'].append("🧹 Limpando dados...")
            df_importar = self.limpar_dados(df_importar)
            
            if df_importar.empty:
                return False, "❌ Nenhum registro válido encontrado!\n\nTodos os registros estão sem PLACA ou DATA preenchidos."
            
            self.relatorio_importacao['detalhes'].append(f"✅ {len(df_importar)} registros válidos (com PLACA e DATA)")
            
            
            # PASSO 4.5: AUTO-CADASTRAR VEÍCULOS NOVOS (se gerenciador disponível)
            if self.gerenciador_veiculos:
                self.relatorio_importacao['detalhes'].append("🚗 Verificando veículos...")
                veiculos_novos = self.auto_cadastrar_veiculos(df_importar)
                if veiculos_novos > 0:
                    self.relatorio_importacao['veiculos_cadastrados'] = veiculos_novos
                    self.relatorio_importacao['detalhes'].append(
                        f"✅ {veiculos_novos} veículos novos cadastrados automaticamente"
                    )
            
            # PASSO 4.6: AUTO-CADASTRAR DESTINOS NOVOS (se gerenciador disponível)
            if self.gerenciador_destinos:
                self.relatorio_importacao['detalhes'].append("🎯 Verificando destinos...")
                destinos_novos = self.auto_cadastrar_destinos(df_importar)
                if destinos_novos > 0:
                    self.relatorio_importacao['destinos_cadastrados'] = destinos_novos
                    self.relatorio_importacao['detalhes'].append(
                        f"✅ {destinos_novos} destinos novos cadastrados automaticamente"
                    )
            
            
            # PASSO 5: Processar conforme modo escolhido
            if modo == 'sobrescrever':
                # Faz backup antes de sobrescrever
                self.db.salvar_dados()  # Salva backup
                self.db.df = df_importar
                self.relatorio_importacao['importados'] = len(df_importar)
                self.relatorio_importacao['detalhes'].append("⚠️ DADOS ANTERIORES SUBSTITUÍDOS")
                
            elif modo == 'adicionar':
                # Identifica duplicatas
                self.relatorio_importacao['detalhes'].append("🔎 Identificando duplicatas...")
                df_novos, df_duplicados = self.identificar_duplicatas(df_importar)
                
                self.relatorio_importacao['duplicados'] = len(df_duplicados)
                self.relatorio_importacao['importados'] = len(df_novos)
                
                if len(df_duplicados) > 0:
                    self.relatorio_importacao['detalhes'].append(
                        f"⚠️ {len(df_duplicados)} registros duplicados (ignorados)"
                    )
                
                # Adiciona apenas registros novos
                if not df_novos.empty:
                    self.db.df = pd.concat([self.db.df, df_novos], ignore_index=True)
                    self.relatorio_importacao['detalhes'].append(
                        f"✅ {len(df_novos)} novos registros importados"
                    )
                else:
                    self.relatorio_importacao['detalhes'].append("ℹ️ Nenhum registro novo encontrado")
            
            elif modo == 'mesclar':
                # Identifica duplicatas
                df_novos, df_duplicados = self.identificar_duplicatas(df_importar)
                
                # Atualiza duplicatas
                if not df_duplicados.empty:
                    for _, row_import in df_duplicados.iterrows():
                        placa = row_import['PLACA']
                        data = row_import['DATA']
                        
                        # Encontra registro correspondente
                        mascara = (self.db.df['PLACA'] == placa) & (self.db.df['DATA'] == data)
                        
                        # Atualiza apenas campos não vazios
                        for col in self.db.colunas_obrigatorias:
                            if row_import[col] and str(row_import[col]).strip():
                                self.db.df.loc[mascara, col] = row_import[col]
                    
                    self.relatorio_importacao['detalhes'].append(
                        f"🔄 {len(df_duplicados)} registros atualizados"
                    )
                
                # Adiciona novos
                if not df_novos.empty:
                    self.db.df = pd.concat([self.db.df, df_novos], ignore_index=True)
                    self.relatorio_importacao['importados'] = len(df_novos)
                    self.relatorio_importacao['detalhes'].append(
                        f"✅ {len(df_novos)} novos registros adicionados"
                    )
            
            
            # PASSO 6: Salvar alterações
            self.relatorio_importacao['detalhes'].append("💾 Salvando dados...")
            sucesso = self.db.salvar_dados()
            
            if not sucesso:
                return False, "❌ Erro ao salvar dados importados"
            
            self.relatorio_importacao['detalhes'].append("✅ Dados salvos com sucesso!")
            
            # Gera mensagem de sucesso
            mensagem = self.gerar_relatorio_texto()
            return True, mensagem
            
        except Exception as e:
            self.relatorio_importacao['erros'] += 1
            self.relatorio_importacao['detalhes'].append(f"❌ Erro: {str(e)}")
            return False, f"❌ Erro na importação: {str(e)}"
    
    
    def gerar_relatorio_texto(self):
        """
        Gera texto formatado do relatório de importação
        """
        linhas = [
            "=" * 50,
            "📊 RELATÓRIO DE IMPORTAÇÃO",
            "=" * 50,
            "",
            f"📝 Total de linhas na planilha: {self.relatorio_importacao['total_linhas']}",
            f"✅ Linhas válidas (com PLACA + DATA): {self.relatorio_importacao['linhas_validas']}",
            f"🗑️ Linhas ignoradas (sem PLACA ou DATA): {self.relatorio_importacao['linhas_ignoradas']}",
            f"🚗 Veículos cadastrados automaticamente: {self.relatorio_importacao['veiculos_cadastrados']}",
            f"🎯 Destinos cadastrados automaticamente: {self.relatorio_importacao['destinos_cadastrados']}",
            f"➕ Registros importados: {self.relatorio_importacao['importados']}",
            f"⚠️ Duplicatas ignoradas: {self.relatorio_importacao['duplicados']}",
            f"❌ Erros: {self.relatorio_importacao['erros']}",
            "",
            "📋 DETALHES:",
            ""
        ]
        
        for detalhe in self.relatorio_importacao['detalhes']:
            linhas.append(f"  {detalhe}")
        
        linhas.extend([
            "",
            "=" * 50,
            "✨ Importação concluída!",
            "=" * 50
        ])
        
        return "\n".join(linhas)
    
    
    def resetar_relatorio(self):
        """
        Reseta estatísticas do relatório
        """
        self.relatorio_importacao = {
            'total_linhas': 0,
            'linhas_validas': 0,
            'linhas_ignoradas': 0,
            'importados': 0,
            'duplicados': 0,
            'veiculos_cadastrados': 0,
            'destinos_cadastrados': 0,
            'erros': 0,
            'detalhes': []
        }
