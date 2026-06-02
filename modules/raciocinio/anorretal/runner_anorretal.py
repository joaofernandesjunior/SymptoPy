import json
from .engine_anorretal import interpretar_anorretal

def rodar(arquivo_json: str) -> dict:
    with open(arquivo_json, encoding='utf-8') as f:
        dados = json.load(f)
    resultado = interpretar_anorretal(dados)
    resultado['tipo'] = 'anorretal'
    return resultado
