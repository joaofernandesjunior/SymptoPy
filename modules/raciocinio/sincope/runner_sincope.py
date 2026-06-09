import json
from .engine_sincope import interpretar_sincope

def rodar(arquivo_json: str) -> dict:
    with open(arquivo_json, encoding='utf-8') as f:
        dados = json.load(f)
    resultado = interpretar_sincope(dados)
    resultado['tipo'] = 'sincope'
    return resultado
