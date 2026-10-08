import pytest
import os
import tempfile
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.manutencao_model import ManutencaoModel
from src.controllers.manutencao_controller import ManutencaoController

@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield path
    if os.path.exists(path):
        try:
            os.remove(path)
        except PermissionError:
            pass

@pytest.fixture
def controller(temp_db):
    model = ManutencaoModel(db_path=temp_db)
    controller = ManutencaoController(model=model)
    yield controller
    if model.conn:
        model.conn.close()

def test_adicionar_registro(controller):
    dados = {
        'DATA': '01/01/2026',
        'PLACA': 'ABC1234',
        'KM': 1000,
        'VEÍCULO': 'CAVALO',
        'DESTINO PROGRAMADO': 'SÃO PAULO',
        'SERVIÇO A EXECUTAR': 'TROCA DE ÓLEO',
        'STATUS': 'EM SERVIÇO',
        'DATA ENTRADA': '01/01/2026',
        'DATA SAÍDA': '',
        'TOTAL DE DIAS EM MANUTENÇÃO': 0,
        'NR° OF': '123',
        'OBS': 'Teste'
    }
    
    sucesso, msg = controller.adicionar_registro(dados)
    assert sucesso is True
    
    registros = controller.obter_todos()
    assert len(registros) == 1
    assert registros[0]['placa'] == 'ABC1234'
    assert registros[0]['status'] == 'EM SERVIÇO'

def test_atualizar_registro(controller):
    dados = {
        'DATA': '01/01/2026',
        'PLACA': 'XYZ9876',
        'KM': 500,
        'VEÍCULO': 'CARRETA',
        'DESTINO PROGRAMADO': 'CURITIBA',
        'SERVIÇO A EXECUTAR': 'PNEUS',
        'STATUS': 'EM SERVIÇO',
        'DATA ENTRADA': '01/01/2026',
        'DATA SAÍDA': '',
        'TOTAL DE DIAS EM MANUTENÇÃO': 0,
        'NR° OF': '456',
        'OBS': ''
    }
    controller.adicionar_registro(dados)
    
    registros = controller.obter_todos()
    id_registro = registros[0]['id']
    
    dados_atualizados = dados.copy()
    dados_atualizados['STATUS'] = 'FINALIZADO'
    dados_atualizados['DATA SAÍDA'] = '02/01/2026'
    
    sucesso, msg = controller.atualizar_registro(id_registro, dados_atualizados)
    assert sucesso is True
    
    registros = controller.obter_todos()
    assert registros[0]['status'] == 'FINALIZADO'

def test_excluir_registro(controller):
    dados = {
        'DATA': '01/01/2026',
        'PLACA': 'DEL1234',
        'STATUS': 'EM TRÂNSITO'
    }
    controller.adicionar_registro(dados)
    
    registros = controller.obter_todos()
    assert len(registros) == 1
    id_registro = registros[0]['id']
    
    sucesso, msg = controller.excluir_registro(id_registro)
    assert sucesso is True
    
    # Exclusão deve remover o registro da lista ativa/geral
    registros = controller.obter_todos()
    assert len(registros) == 0

def test_recalcular_campos(controller):
    dados = {
        'DATA': '01/01/2026',
        'PLACA': 'ABC1234',
        'DATA ENTRADA': '01/01/2026',
        'DATA SAÍDA': '03/01/2026',
        'STATUS': '' 
    }
    # O controller deve autocalcular ao adicionar/atualizar
    controller.adicionar_registro(dados)
    
    registros = controller.obter_todos()
    assert registros[0]['status'] == 'FINALIZADO'
    assert registros[0]['total_dias_manutencao'] == 2 # 3 - 1 = 2

