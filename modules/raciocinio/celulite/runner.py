# modules/raciocinio/celulite/runner.py

import json
from modules.raciocinio.celulite.engine_celulite import analisar_celulite


def rodar(arquivo_json: str) -> dict:
    with open(arquivo_json, encoding='utf-8') as f:
        dados = json.load(f)
    return analisar_celulite(dados)
