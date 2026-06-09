# modules/raciocinio/gota/runner_gota.py

import json
from .engine_gota import interpretar_gota


def rodar(arquivo_json: str) -> dict:
    """Carrega JSON do subjetivo e retorna resultado do engine."""
    with open(arquivo_json, encoding='utf-8') as f:
        dados = json.load(f)
    resultado = interpretar_gota(dados)
    resultado['tipo'] = 'gota'
    return resultado
