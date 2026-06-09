# modules/raciocinio/hemorragia/runner.py

import json
from modules.raciocinio.hemorragia.engine_hemorragia import analisar_hemorragia


def rodar(arquivo_json: str) -> dict:
    with open(arquivo_json, encoding='utf-8') as f:
        dados = json.load(f)
    return analisar_hemorragia(dados)
