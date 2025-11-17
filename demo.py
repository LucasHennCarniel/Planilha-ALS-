#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Demo script para demonstrar funcionalidades do Sistema de Manutenção
Este script executa operações básicas sem GUI para demonstração
"""

import sys
from unittest.mock import MagicMock

# Mock tkinter para ambiente sem display
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()

from sistema_manutencao import ExcelDatabase
import os


def demo():
    """Demonstração das funcionalidades do sistema"""
    
    print("="*60)
    print("DEMO - Sistema de Controle de Manutenção de Frota ALS")
    print("="*60)
    
    # Usar arquivo de demo
    demo_file = 'demo_manutencao.xlsx'
    
    # Limpar se existir
    if os.path.exists(demo_file):
        os.remove(demo_file)
        print("✓ Arquivo de demo anterior removido")
    
    print("\n1. Inicializando banco de dados...")
    db = ExcelDatabase(demo_file)
    print(f"✓ Banco de dados criado: {demo_file}")
    
    print("\n2. Adicionando registros de manutenção...")
    
    # Adicionar primeiro registro
    record1 = {
        'Veiculo': 'Caminhão Mercedes 1620',
        'Placa': 'ABC-1234',
        'Tipo_Manutencao': 'Preventiva',
        'Descricao': 'Troca de óleo do motor e filtros',
        'Custo': '850.00',
        'KM_Atual': '120000',
        'Proximo_KM': '130000',
        'Status': 'Concluída',
        'Responsavel': 'João Silva',
        'Observacoes': 'Trocado também filtro de combustível'
    }
    db.add_record(record1)
    print("✓ Registro 1 adicionado: Caminhão Mercedes 1620")
    
    # Adicionar segundo registro
    record2 = {
        'Veiculo': 'Van Sprinter',
        'Placa': 'DEF-5678',
        'Tipo_Manutencao': 'Corretiva',
        'Descricao': 'Reparo de suspensão dianteira',
        'Custo': '1200.00',
        'KM_Atual': '85000',
        'Proximo_KM': '85000',
        'Status': 'Em Andamento',
        'Responsavel': 'Maria Santos',
        'Observacoes': 'Aguardando peças'
    }
    db.add_record(record2)
    print("✓ Registro 2 adicionado: Van Sprinter")
    
    # Adicionar terceiro registro
    record3 = {
        'Veiculo': 'Caminhão Volvo FH 540',
        'Placa': 'GHI-9012',
        'Tipo_Manutencao': 'Revisão',
        'Descricao': 'Revisão dos 100.000 km',
        'Custo': '2500.00',
        'KM_Atual': '100000',
        'Proximo_KM': '110000',
        'Status': 'Agendada',
        'Responsavel': 'Pedro Costa',
        'Observacoes': 'Agendado para próxima semana'
    }
    db.add_record(record3)
    print("✓ Registro 3 adicionado: Caminhão Volvo FH 540")
    
    print("\n3. Carregando e exibindo todos os registros...")
    df = db.load_data()
    print(f"\nTotal de registros: {len(df)}")
    print("\n" + df.to_string(index=False))
    
    print("\n4. Testando busca por 'Caminhão'...")
    results = db.search_records('Caminhão', 'Veiculo')
    print(f"✓ Encontrados {len(results)} registros:")
    for _, row in results.iterrows():
        print(f"  - ID {row['ID']}: {row['Veiculo']} ({row['Status']})")
    
    print("\n5. Testando busca por Status 'Agendada'...")
    results = db.search_records('Agendada', 'Status')
    print(f"✓ Encontrados {len(results)} registros:")
    for _, row in results.iterrows():
        print(f"  - ID {row['ID']}: {row['Veiculo']} - {row['Descricao']}")
    
    print("\n6. Atualizando status do registro 2...")
    db.update_record(2, {
        'Status': 'Concluída',
        'Observacoes': 'Serviço concluído com sucesso'
    })
    print("✓ Registro 2 atualizado")
    
    # Verificar atualização
    df = db.load_data()
    updated_record = df[df['ID'] == 2].iloc[0]
    print(f"  Novo status: {updated_record['Status']}")
    print(f"  Nova observação: {updated_record['Observacoes']}")
    
    print("\n7. Estatísticas gerais...")
    df = db.load_data()
    total_cost = df['Custo'].astype(float).sum()
    print(f"✓ Total de registros: {len(df)}")
    print(f"✓ Custo total: R$ {total_cost:.2f}")
    
    status_counts = df['Status'].value_counts()
    print("\n✓ Distribuição por Status:")
    for status, count in status_counts.items():
        print(f"  - {status}: {count}")
    
    tipo_counts = df['Tipo_Manutencao'].value_counts()
    print("\n✓ Distribuição por Tipo:")
    for tipo, count in tipo_counts.items():
        print(f"  - {tipo}: {count}")
    
    print("\n" + "="*60)
    print("DEMO CONCLUÍDA COM SUCESSO!")
    print("="*60)
    print(f"\nArquivo criado: {demo_file}")
    print("Você pode abrir este arquivo no Excel para visualizar os dados.")
    print("\nPara usar a aplicação completa com interface gráfica, execute:")
    print("  python sistema_manutencao.py")
    print("="*60)


if __name__ == "__main__":
    try:
        demo()
    except Exception as e:
        print(f"\n❌ Erro durante a demo: {e}")
        import traceback
        traceback.print_exc()
