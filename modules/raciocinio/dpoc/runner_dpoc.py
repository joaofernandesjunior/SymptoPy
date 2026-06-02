import json
from .engine_dpoc import interpretar_dpoc

def rodar(arquivo_json: str) -> dict:
    with open(arquivo_json, encoding='utf-8') as f:
        dados = json.load(f)
    resultado = interpretar_dpoc(dados)
    resultado['tipo'] = 'dpoc'
    return resultado
