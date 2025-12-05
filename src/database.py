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
            
            # Tabela NOTAS (para anotações futuras)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_programada TEXT NOT NULL,
                    placa TEXT NOT NULL,
                    status TEXT,
                    observacao TEXT,
                    data_criacao TEXT,
                    UNIQUE(placa, data_programada)
                )
            """)
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notas_placa ON notas(placa)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notas_data ON notas(data_programada)")
            
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
        Garante que dados estão salvos - JÁ SALVAMOS NO ADICIONAR/ATUALIZAR
        Apenas faz commit final e backup
        """
        try:
            # Commit final (garantia)
            self.conn.commit()
            
            # Faz backup do banco (apenas a cada hora para não lotar)
            if os.path.exists(self.db_path):
                backup_dir = 'backup'
                # Verifica último backup
                backups = [f for f in os.listdir(backup_dir) if f.startswith('database_backup_')]
                fazer_backup = True
                
                if backups:
                    ultimo_backup = max(backups)
                    # Extrai timestamp do nome
                    try:
                        timestamp_str = ultimo_backup.replace('database_backup_', '').replace('.db', '')
                        ultimo_timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                        # Só faz backup se passou mais de 1 hora
                        if (datetime.now() - ultimo_timestamp).seconds < 3600:
                            fazer_backup = False
                    except:
                        pass
                
                if fazer_backup:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    backup_file = f'{backup_dir}/database_backup_{timestamp}.db'
                    shutil.copy2(self.db_path, backup_file)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
            return False
    
    
    def recalcular_campos(self):
        """
        Recalcula APENAS campos automáticos (dias em manutenção)
        NÃO sobrescreve status escolhido pelo usuário
        ATUALIZA NO SQLITE TAMBÉM
        """
        try:
            cursor = self.conn.cursor()
            
            for idx, row in self.df.iterrows():
                placa = row['PLACA']
                data = row['DATA']
                
                # Calcula dias em manutenção
                dias = calcular_dias_manutencao(
                    row.get('DATA ENTRADA'), 
                    row.get('DATA SAÍDA')
                )
                self.df.at[idx, 'TOTAL DE DIAS EM MANUTENÇÃO'] = dias
                
                # Atualiza dias no SQLite
                cursor.execute("""
                    UPDATE manutencoes 
                    SET total_dias_manutencao = ? 
                    WHERE placa = ? AND data = ?
                """, (dias, placa, data))
                
                # NÃO recalcula status - mantém o que o usuário escolheu
                # Se o status estiver vazio, aí sim calcula
                if not row.get('STATUS') or pd.isna(row.get('STATUS')) or row.get('STATUS') == '':
                    status = calcular_status(
                        row.get('DATA ENTRADA'),
                        row.get('DATA SAÍDA'),
                        ''
                    )
                    self.df.at[idx, 'STATUS'] = status
                    
                    # Atualiza status no SQLite
                    cursor.execute("""
                        UPDATE manutencoes 
                        SET status = ? 
                        WHERE placa = ? AND data = ?
                    """, (status, placa, data))
            
            # Commit todas as atualizações
            self.conn.commit()
            
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Erro ao recalcular campos: {e}")
    
    
    def adicionar_registro(self, dados):
        """
        Adiciona novo registro - SALVA NO BANCO PRIMEIRO
        """
        try:
            # 1. SALVA NO SQLITE PRIMEIRO
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO manutencoes (
                    data, placa, km, veiculo, destino_programado,
                    servico_executar, status, data_entrada, data_saida,
                    total_dias_manutencao, nr_of, obs
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dados.get('DATA', ''),
                dados.get('PLACA', '').upper(),
                dados.get('KM', 0),
                dados.get('VEÍCULO', ''),
                dados.get('DESTINO PROGRAMADO', ''),
                dados.get('SERVIÇO A EXECUTAR', ''),
                dados.get('STATUS', ''),
                dados.get('DATA ENTRADA', ''),
                dados.get('DATA SAÍDA', ''),
                dados.get('TOTAL DE DIAS EM MANUTENÇÃO', 0),
                dados.get('NR° OF', ''),
                dados.get('OBS', '')
            ))
            
            # 2. COMMIT IMEDIATAMENTE
            self.conn.commit()
            
            # 3. ATUALIZA DATAFRAME
            self.carregar_dados()
            
            return True
            
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Erro ao adicionar: {e}")
            return False
    
    
    def atualizar_registro(self, indice, dados):
        """
        Atualiza registro existente - SALVA NO BANCO PRIMEIRO
        PRIORIZA STATUS ESCOLHIDO PELO USUÁRIO
        """
        try:
            # Pega placa e data para identificar o registro
            placa = self.df.iloc[indice]['PLACA']
            data = self.df.iloc[indice]['DATA']
            
            # IMPORTANTE: Se o usuário alterou o STATUS, essa mudança TEM PRIORIDADE
            # Não recalcula status automaticamente durante uma edição
            status_usuario = dados.get('STATUS', '').strip().upper()
            
            # 1. ATUALIZA NO SQLITE PRIMEIRO
            cursor = self.conn.cursor()
            
            # Monta UPDATE dinâmico
            campos_update = []
            valores = []
            
            for chave, valor in dados.items():
                # Mapeia nome da coluna
                nome_coluna = chave.lower().replace(' ', '_').replace('°', '').replace('ç', 'c')
                nome_coluna = nome_coluna.replace('destinoprogramado', 'destino_programado')
                nome_coluna = nome_coluna.replace('servicoaexecutar', 'servico_executar')
                nome_coluna = nome_coluna.replace('dataentrada', 'data_entrada')
                nome_coluna = nome_coluna.replace('datasaida', 'data_saida')
                nome_coluna = nome_coluna.replace('totaldedasemmanutencao', 'total_dias_manutencao')
                nome_coluna = nome_coluna.replace('nr_of', 'nr_of')
                
                # GARANTIA: Se o usuário escolheu um STATUS, usa ele (não recalcula)
                if chave == 'STATUS' and status_usuario:
                    campos_update.append(f"{nome_coluna} = ?")
                    valores.append(status_usuario)
                else:
                    campos_update.append(f"{nome_coluna} = ?")
                    valores.append(valor)
            
            # Adiciona WHERE
            valores.extend([placa, data])
            
            sql = f"UPDATE manutencoes SET {', '.join(campos_update)} WHERE placa = ? AND data = ?"
            cursor.execute(sql, valores)
            
            # 2. COMMIT IMEDIATAMENTE
            self.conn.commit()
            
            # 3. ATUALIZA DATAFRAME (mantém status do usuário)
            for chave, valor in dados.items():
                if chave in self.df.columns:
                    # Garante que status do usuário é preservado
                    if chave == 'STATUS' and status_usuario:
                        self.df.at[indice, chave] = status_usuario
                    else:
                        self.df.at[indice, chave] = valor
            
            return True
            
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Erro ao atualizar: {e}")
            return False
    
    
    def excluir_registro(self, indice):
        """
        Exclui registro - DELETA DO SQLITE PRIMEIRO
        """
        try:
            # Pega placa e data para identificar o registro
            placa = self.df.iloc[indice]['PLACA']
            data = self.df.iloc[indice]['DATA']
            
            # 1. DELETA DO SQLITE PRIMEIRO
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM manutencoes WHERE placa = ? AND data = ?", (placa, data))
            
            # 2. COMMIT IMEDIATAMENTE
            self.conn.commit()
            
            # 3. ATUALIZA DATAFRAME
            self.df = self.df.drop(indice).reset_index(drop=True)
            
            return True
            
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Erro ao excluir: {e}")
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
