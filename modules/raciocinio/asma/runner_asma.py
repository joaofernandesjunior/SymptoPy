import json
from .engine_asma import interpretar_asma

def rodar(arquivo_json: str) -> dict:
    with open(arquivo_json, encoding='utf-8') as f:
        dados = json.load(f)
    resultado = interpretar_asma(dados)
    resultado['tipo'] = 'asma'
    return resultado
