import pytest
import os
import sqlite3
import tempfile
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Vamos testar as novas classes (que ainda vamos criar)
from src.models.destino_model import DestinoModel
from src.controllers.destino_controller import DestinoController

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
    model = DestinoModel(db_path=temp_db)
    controller = DestinoController(model=model)
    yield controller
    if model.conn:
        model.conn.close()

def test_inicializacao_cria_destinos_padrao(controller):
    destinos = controller.obter_destinos_ativos()
    # Deve retornar uma lista de strings
    assert len(destinos) == 9
    assert "AGYLE" in destinos

def test_adicionar_destino(controller):
    sucesso, msg = controller.adicionar_destino("NOVO DESTINO")
    assert sucesso is True
    
    destinos = controller.obter_destinos_ativos()
    assert "NOVO DESTINO" in destinos

def test_adicionar_destino_duplicado(controller):
    controller.adicionar_destino("DUPLICADO")
    sucesso, msg = controller.adicionar_destino("duplicado")
    assert sucesso is False
    assert "já cadastrado" in msg.lower()

def test_excluir_destino(controller):
    controller.adicionar_destino("PARA EXCLUIR")
    
    # No novo modelo, queremos obter todos (incluindo ID) para excluir
    todos_destinos = controller.model.obter_todos()
    destino_alvo = next((d for d in todos_destinos if d['nome_destino'] == "PARA EXCLUIR"), None)
    
    sucesso, msg = controller.excluir_destino(destino_alvo['id'])
    assert sucesso is True
    
    destinos_ativos = controller.obter_destinos_ativos()
    assert "PARA EXCLUIR" not in destinos_ativos

def test_atualizar_destino(controller):
    controller.adicionar_destino("PARA ATUALIZAR")
    
    todos_destinos = controller.model.obter_todos()
    destino_alvo = next((d for d in todos_destinos if d['nome_destino'] == "PARA ATUALIZAR"), None)
    
    sucesso, msg = controller.atualizar_destino(destino_alvo['id'], "ATUALIZADO", ativo=True)
    assert sucesso is True
    
    destinos_ativos = controller.obter_destinos_ativos()
    assert "ATUALIZADO" in destinos_ativos
    assert "PARA ATUALIZAR" not in destinos_ativos

