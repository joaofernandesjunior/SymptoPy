# modules/raciocinio/musculoesqueletico/quadril/core/runner.py

import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
from modules.raciocinio.musculoesqueletico.quadril.core.engine_quadril import interpretar_quadril


def _sep(c='─', n=54):
    print(c * n)


def _imprimir_resultado(resultado):
    categoria  = resultado['categoria']
    localizacao = resultado.get('localizacao', '')
    loc_pt = {'anterior': 'Anterior / Virilha', 'lateral': 'Lateral / Grande Trocânter',
               'posterior': 'Posterior / Nádega'}.get(localizacao, localizacao)

    print()
    _sep('=')
    print('  RESULTADO — DOR NO QUADRIL')
    _sep('=')
    print(f'\n  Localização referida: {loc_pt}')

    # ── Red Flags ──────────────────────────────────────────────────────
    flags = resultado.get('red_flags', {}).get('flags', [])
    if flags:
        _sep()
        for f in flags:
            urgencia = f['urgencia'].upper()
            print(f'\n  [{urgencia}] {f["achado"]}')
            print(f'  Conduta: {f["acao"]}')

    # ── Alerta AVN ─────────────────────────────────────────────────────
    avn = resultado.get('alerta_avn', {})
    if avn.get('alerta'):
        _sep()
        print(f'\n  ALERTA AVN (score {avn["score"]}): {avn["acao"]}')

    if categoria == 'red_flag_quadril':
        _sep('=')
        print()
        return

    # ── Hipóteses ──────────────────────────────────────────────────────
    provaveis = resultado.get('hipoteses_provaveis', [])
    possiveis  = resultado.get('hipoteses_possiveis', [])
    exclusao   = resultado.get('hipoteses_exclusao', [])

    if not provaveis:
        _sep()
        print('\n  Dados insuficientes para hipótese de força moderada ou alta.')
        print('  Reavaliar com exame físico complementar.')
        _sep('=')
        print()
        return

    _sep()
    print('\n  HIPÓTESES PROVÁVEIS:')
    for h in provaveis:
        print(f'\n  [{h["forca"].upper()}] {h["hipotese"]} (score {h["score"]})')
        for p in h.get('positivos', []):
            print(f'    + {p}')

        if h.get('base'):
            _sep()
            print('  Conduta não-farmacológica:')
            for item in h['base']:
                print(f'  • {item}')

        if h.get('farmacologico'):
            _sep()
            print('  Farmacológico:')
            for item in h['farmacologico']:
                print(f'  • {item}')

        if h.get('fisioterapia'):
            print(f'\n  Fisioterapia: {h["fisioterapia"]}')
        if h.get('imagem'):
            print(f'  Imagem: {h["imagem"]}')
        if h.get('encaminhar'):
            print(f'  Encaminhamento: {h["encaminhar"]}')

    if possiveis:
        _sep()
        print('\n  HIPÓTESES POSSÍVEIS (baixa força):')
        for h in possiveis:
            print(f'  • {h["hipotese"]} (score {h["score"]})')

    if exclusao:
        _sep()
        print('\n  EXCLUÍDAS ATIVAMENTE:')
        for e in exclusao:
            print(f'  • {e}')

    _sep('=')
    print()


def rodar(arquivo_json):
    sys.stdout.reconfigure(encoding='utf-8')
    with open(arquivo_json, encoding='utf-8') as f:
        dados = json.load(f)
    resultado = interpretar_quadril(dados)
    _imprimir_resultado(resultado)
    return resultado
