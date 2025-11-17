"""
Testes básicos para o Sistema de Manutenção de Frota
"""

import unittest
import pandas as pd
import os
import sys
from unittest.mock import MagicMock

# Mock tkinter before importing sistema_manutencao
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()


class TestExcelDatabase(unittest.TestCase):
    """Testes para a classe ExcelDatabase"""
    
    def setUp(self):
        """Preparar ambiente de teste"""
        self.test_filename = 'test_manutencao.xlsx'
        # Cleanup se existir
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)
    
    def tearDown(self):
        """Limpar após testes"""
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)
    
    def test_initialize_database(self):
        """Testa criação inicial do banco de dados"""
        # Importar apenas a classe necessária
        from sistema_manutencao import ExcelDatabase
        
        db = ExcelDatabase(self.test_filename)
        
        # Verificar se arquivo foi criado
        self.assertTrue(os.path.exists(self.test_filename))
        
        # Verificar estrutura
        df = pd.read_excel(self.test_filename, sheet_name='Manutencoes')
        expected_columns = [
            'ID', 'Data', 'Veiculo', 'Placa', 'Tipo_Manutencao',
            'Descricao', 'Custo', 'KM_Atual', 'Proximo_KM',
            'Status', 'Responsavel', 'Observacoes'
        ]
        self.assertEqual(list(df.columns), expected_columns)
        self.assertEqual(len(df), 0)  # Deve estar vazio
    
    def test_add_record(self):
        """Testa adição de registro"""
        from sistema_manutencao import ExcelDatabase
        
        db = ExcelDatabase(self.test_filename)
        
        record = {
            'Veiculo': 'Caminhão Teste',
            'Placa': 'TST-1234',
            'Tipo_Manutencao': 'Preventiva',
            'Descricao': 'Teste',
            'Custo': '100',
            'KM_Atual': '1000',
            'Proximo_KM': '2000',
            'Status': 'Concluída',
            'Responsavel': 'Teste',
            'Observacoes': 'Obs teste'
        }
        
        # Adicionar registro
        result = db.add_record(record)
        self.assertTrue(result)
        
        # Verificar se foi adicionado
        df = db.load_data()
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['Veiculo'], 'Caminhão Teste')
        self.assertEqual(df.iloc[0]['ID'], 1)
    
    def test_update_record(self):
        """Testa atualização de registro"""
        from sistema_manutencao import ExcelDatabase
        
        db = ExcelDatabase(self.test_filename)
        
        # Adicionar registro
        record = {
            'Veiculo': 'Caminhão Original',
            'Placa': 'TST-1234',
            'Tipo_Manutencao': 'Preventiva',
            'Descricao': 'Teste',
            'Custo': '100',
            'KM_Atual': '1000',
            'Proximo_KM': '2000',
            'Status': 'Pendente',
            'Responsavel': 'Teste',
            'Observacoes': ''
        }
        db.add_record(record)
        
        # Atualizar
        updated_data = {
            'Veiculo': 'Caminhão Atualizado',
            'Status': 'Concluída'
        }
        result = db.update_record(1, updated_data)
        self.assertTrue(result)
        
        # Verificar atualização
        df = db.load_data()
        self.assertEqual(df.iloc[0]['Veiculo'], 'Caminhão Atualizado')
        self.assertEqual(df.iloc[0]['Status'], 'Concluída')
    
    def test_delete_record(self):
        """Testa exclusão de registro"""
        from sistema_manutencao import ExcelDatabase
        
        db = ExcelDatabase(self.test_filename)
        
        # Adicionar dois registros
        for i in range(2):
            record = {
                'Veiculo': f'Caminhão {i+1}',
                'Placa': f'TST-{i+1}234',
                'Tipo_Manutencao': 'Preventiva',
                'Descricao': 'Teste',
                'Custo': '100',
                'KM_Atual': '1000',
                'Proximo_KM': '2000',
                'Status': 'Concluída',
                'Responsavel': 'Teste',
                'Observacoes': ''
            }
            db.add_record(record)
        
        # Verificar que temos 2 registros
        df = db.load_data()
        self.assertEqual(len(df), 2)
        
        # Deletar primeiro
        result = db.delete_record(1)
        self.assertTrue(result)
        
        # Verificar que só resta 1
        df = db.load_data()
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['Veiculo'], 'Caminhão 2')
    
    def test_search_records(self):
        """Testa busca de registros"""
        from sistema_manutencao import ExcelDatabase
        
        db = ExcelDatabase(self.test_filename)
        
        # Adicionar registros variados
        vehicles = ['Caminhão Mercedes', 'Van Sprinter', 'Caminhão Volvo']
        for vehicle in vehicles:
            record = {
                'Veiculo': vehicle,
                'Placa': 'TST-1234',
                'Tipo_Manutencao': 'Preventiva',
                'Descricao': 'Teste',
                'Custo': '100',
                'KM_Atual': '1000',
                'Proximo_KM': '2000',
                'Status': 'Concluída',
                'Responsavel': 'Teste',
                'Observacoes': ''
            }
            db.add_record(record)
        
        # Buscar "Caminhão"
        results = db.search_records('Caminhão', 'Veiculo')
        self.assertEqual(len(results), 2)
        
        # Buscar "Mercedes"
        results = db.search_records('Mercedes', 'Veiculo')
        self.assertEqual(len(results), 1)
        
        # Buscar vazio (deve retornar tudo)
        results = db.search_records('', 'Veiculo')
        self.assertEqual(len(results), 3)


class TestTemplateMethods(unittest.TestCase):
    """Testa o script de criação de template"""
    
    def test_create_template_execution(self):
        """Testa se o script create_template pode ser executado"""
        # Verificar se arquivo existe
        self.assertTrue(os.path.exists('create_template.py'))


if __name__ == '__main__':
    # Suprimir mensagens de GUI do Tkinter
    import warnings
    warnings.filterwarnings('ignore')
    
    # Executar testes
    unittest.main(verbosity=2)
