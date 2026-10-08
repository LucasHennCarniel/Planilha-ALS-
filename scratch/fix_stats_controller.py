import re

with open('src/controllers/manutencao_controller.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(
    r"'total': 0, 'em_manutencao': 0, 'finalizados': 0,\n\s*'aguardando': 0, 'em_transito': 0, 'em_servico': 0,\n\s*'tempo_medio': 0",
    r"'total': 0, 'em_manutencao': 0, 'finalizados': 0,\n            'aguardando': 0, 'em_transito': 0, 'em_servico': 0,\n            'tempo_medio': 0, 'placas_unicas': 0",
    content
)

content = re.sub(
    r"'tempo_medio': round\(float\(df\['TOTAL DE DIAS EM MANUTENÇÃO'\]\.mean\(\)\), 1\) if 'TOTAL DE DIAS EM MANUTENÇÃO' in df\.columns else 0\n\s*}",
    r"'tempo_medio': round(float(df['TOTAL DE DIAS EM MANUTENÇÃO'].mean()), 1) if 'TOTAL DE DIAS EM MANUTENÇÃO' in df.columns else 0,\n            'placas_unicas': df['PLACA'].nunique() if 'PLACA' in df.columns else 0\n        }",
    content
)

with open('src/controllers/manutencao_controller.py', 'w', encoding='utf-8') as f:
    f.write(content)
