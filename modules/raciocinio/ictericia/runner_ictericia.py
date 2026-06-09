import json
from .engine_ictericia import interpretar_ictericia

def rodar(arquivo_json: str) -> dict:
    with open(arquivo_json, encoding='utf-8') as f:
        dados = json.load(f)
    resultado = interpretar_ictericia(dados)
    resultado['tipo'] = 'ictericia'
    return resultado
