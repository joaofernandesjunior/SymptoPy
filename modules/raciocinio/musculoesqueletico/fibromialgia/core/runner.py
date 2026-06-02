# modules/raciocinio/musculoesqueletico/fibromialgia/core/runner.py

import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
from modules.raciocinio.musculoesqueletico.fibromialgia.core.engine_fibromialgia import (
    interpretar_fibromialgia,
)


def _sep(c='─', n=54):
    print(c * n)


def _imprimir_resultado(resultado):
    categoria = resultado['categoria']
    scores    = resultado['scores']
    criterios = resultado['criterios']

    print()
    _sep('=')
    print('  RESULTADO — FIBROMIALGIA / DOR CRÔNICA DIFUSA')
    _sep('=')

    # ── Scores ────────────────────────────────────────────────────────
    print(
        f'\n  WPI: {scores["wpi"]}/21  |  '
        f'SSS: {scores["sss"]}/12  '
        f'(P1: {scores["sss_p1"]}/9  P2: {scores["sss_p2"]}/3)'
    )
    print(f'  Regiões afetadas: {scores["n_regioes"]}/5')

    # ── Diagnóstico ───────────────────────────────────────────────────
    _sep()
    if categoria == 'investigar_causa_secundaria':
        print('\n  ⚠️  FLAGS INFLAMATÓRIOS — Investigar causa secundária antes de confirmar FM')

    elif categoria == 'fibromialgia_confirmada':
        cond = criterios.get('condicao_usada', '?')
        print(f'\n  ✅ FIBROMIALGIA CONFIRMADA (Condição {cond} — ACR 2016)')
        sintoma = resultado['sintoma_predominante'].upper()
        print(f'  Sintoma predominante relatado: {sintoma}')

    else:
        print('\n  ❌ Critérios ACR 2016 não preenchidos no momento')
        for f in resultado.get('criterios_faltando', []):
            print(f'     • {f}')

    # ── Conduta ───────────────────────────────────────────────────────
    conduta = resultado.get('conduta', {})

    if conduta.get('base'):
        _sep()
        print('\n  BASE (universal):')
        for item in conduta['base']:
            print(f'  • {item}')

    if conduta.get('nao_farmacologico'):
        _sep()
        print(f'\n  NÃO-FARMACOLÓGICO (foco: {resultado["sintoma_predominante"]}):')
        for item in conduta['nao_farmacologico']:
            print(f'  • {item}')

    if conduta.get('farmacologico'):
        _sep()
        print('\n  FARMACOLÓGICO:')
        for item in conduta['farmacologico']:
            print(f'  • {item}')

    if conduta.get('nota_eficacia'):
        print(f'\n  📊 {conduta["nota_eficacia"]}')

    if conduta.get('alerta'):
        _sep()
        print(f'\n  {conduta["alerta"]}')

    # ── Encaminhamento ────────────────────────────────────────────────
    if resultado.get('encaminhar'):
        _sep()
        print(f'\n  Encaminhamento: {resultado["encaminhar"]}')

    _sep('=')
    print()


def rodar(arquivo_json):
    sys.stdout.reconfigure(encoding='utf-8')
    with open(arquivo_json, encoding='utf-8') as f:
        dados = json.load(f)
    resultado = interpretar_fibromialgia(dados)
    _imprimir_resultado(resultado)
    return resultado
