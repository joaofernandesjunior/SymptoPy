import json
from .engine_edema import interpretar_edema

def rodar(arquivo_json: str) -> dict:
    with open(arquivo_json, encoding='utf-8') as f:
        dados = json.load(f)
    resultado = interpretar_edema(dados)
    resultado['tipo'] = 'edema'
    return resultado
