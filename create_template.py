"""
Gerador do Template de Manutenção Excel
"""

import pandas as pd

def create_template():
    """Cria template Excel para o sistema"""
    
    # Dados de exemplo
    data = {
        'ID': [1, 2],
        'Data': ['17/11/2025', '17/11/2025'],
        'Veiculo': ['Caminhão Mercedes 1620', 'Van Sprinter'],
        'Placa': ['ABC-1234', 'XYZ-5678'],
        'Tipo_Manutencao': ['Preventiva', 'Corretiva'],
        'Descricao': ['Troca de óleo e filtros', 'Reparo de suspensão'],
        'Custo': [500.00, 1200.00],
        'KM_Atual': [45000, 38000],
        'Proximo_KM': [50000, 38000],
        'Status': ['Concluída', 'Pendente'],
        'Responsavel': ['João Silva', 'Maria Santos'],
        'Observacoes': ['Trocado filtro de ar também', 'Aguardando peça']
    }
    
    df = pd.DataFrame(data)
    
    # Salvar template
    df.to_excel('template_manutencao.xlsx', index=False, sheet_name='Manutencoes')
    print("Template criado: template_manutencao.xlsx")

if __name__ == "__main__":
    create_template()
