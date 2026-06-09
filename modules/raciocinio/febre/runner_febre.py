# modules/raciocinio/febre/runner_febre.py
import json
from .engine_febre import interpretar_febre


def rodar(arquivo_json: str) -> dict:
    """Carrega dados do subjetivo e retorna resultado do engine."""
    with open(arquivo_json, encoding='utf-8') as f:
        dados = json.load(f)
    resultado = interpretar_febre(dados)
    resultado['tipo'] = 'febre'
    return resultado
