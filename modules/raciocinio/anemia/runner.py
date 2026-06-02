# modules/raciocinio/anemia/runner.py

import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from modules.raciocinio.anemia.engine_anemia import interpretar_anemia

_GRAU_LABEL = {
    'normal':     'NORMAL',
    'leve':       'LEVE',
    'moderada':   'MODERADA',
    'grave':      'GRAVE',
    'muito_grave':'MUITO GRAVE / RISCO DE VIDA',
}


def _sep(c='─', n=54):
    return c * n


def _formatar_resultado(resultado) -> str:
    linhas = []
    linhas.append('=' * 54)
    linhas.append('  INTERPRETAÇÃO DE HEMOGRAMA — ANEMIA')
    linhas.append('=' * 54)

    categoria = resultado.get('categoria', '')

    # ── Sem anemia ─────────────────────────────────────────────────
    if categoria == 'sem_anemia':
        linhas.append(f'\n  ✓ SEM ANEMIA')
        linhas.append(f'  Hb {resultado["hb"]} g/dL — limiar: {resultado["limiar"]} g/dL ({resultado["descr_sexo"]})')
        linhas.append(f'\n  Conduta:')
        for c in resultado.get('conduta', []):
            linhas.append(f'  • {c}')
        linhas.append('=' * 54)
        return '\n'.join(linhas)

    # ── Pancitopenia ────────────────────────────────────────────────
    if categoria == 'pancitopenia':
        linhas.append('\n  ⚠  PANCITOPENIA — ENCAMINHAMENTO URGENTE')
        linhas.append(_sep())
        linhas.append(f'  Hb: {resultado["hb"]} g/dL  |  Leuco: {resultado["wbc"]} ×10³/µL  |  Plaq: {resultado["plt"]} ×10³/µL')
        linhas.append(f'  Gravidade anemia: {_GRAU_LABEL.get(resultado["grau"], resultado["grau"])}')
        linhas.append(f'\n  Diagnóstico: {resultado["diagnostico"]}')
        linhas.append('\n  Conduta:')
        for c in resultado.get('conduta', []):
            linhas.append(f'  • {c}')
        linhas.append('=' * 54)
        return '\n'.join(linhas)

    # ── Cabeçalho geral ─────────────────────────────────────────────
    hb     = resultado.get('hb', '?')
    mcv    = resultado.get('mcv', '?')
    rdw    = resultado.get('rdw', '?')
    rpi    = resultado.get('rpi')
    grau   = _GRAU_LABEL.get(resultado.get('grau', ''), resultado.get('grau', ''))
    tipo   = resultado.get('tipo_mcv', '')
    deficit= resultado.get('deficit_hb', '')

    linhas.append(f'\n  Hb: {hb} g/dL  |  VCM: {mcv} fL  |  RDW: {rdw}%  |  RPI: {rpi if rpi is not None else "não calculado"}')
    linhas.append(f'  Gravidade: {grau} (déficit {deficit} g/dL abaixo do limiar)')
    linhas.append(f'  Tipo: Anemia {tipo}')

    if resultado.get('alerta_transfusao'):
        linhas.append('')
        linhas.append('  ╔══════════════════════════════════════════════════╗')
        linhas.append('  ║  ⚠  ANEMIA GRAVE — AVALIAR TRANSFUSÃO            ║')
        linhas.append('  ║  Hb < 7 g/dL (ou < 8 com DCV) = critério         ║')
        linhas.append('  ╚══════════════════════════════════════════════════╝')

    # ── Diagnóstico ─────────────────────────────────────────────────
    linhas.append('')
    linhas.append(_sep())
    linhas.append(f'  DIAGNÓSTICO: {resultado.get("diagnostico", "")}')
    linhas.append(_sep())
    padrao = resultado.get('padrao', '')
    if padrao:
        linhas.append(f'  Padrão: {padrao}')

    # ── Exames confirmatórios ────────────────────────────────────────
    exames = resultado.get('exames_confirmatórios', [])
    if exames:
        linhas.append('\n  EXAMES A SOLICITAR / CONFIRMAR:')
        for e in exames:
            linhas.append(f'  • {e}')

    # ── Tratamento ──────────────────────────────────────────────────
    trat = resultado.get('tratamento', {})
    if trat:
        linhas.append('\n  TRATAMENTO:')
        if isinstance(trat, dict):
            for chave, valor in trat.items():
                linhas.append(f'  [{chave.replace("_", " ").upper()}]')
                linhas.append(f'    {valor}')
        elif isinstance(trat, list):
            for item in trat:
                linhas.append(f'  • {item}')

    # ── Encaminhamento ───────────────────────────────────────────────
    enc = resultado.get('encaminhamento')
    if enc:
        linhas.append(f'\n  ENCAMINHAMENTO: {enc}')

    linhas.append('\n' + '=' * 54)
    return '\n'.join(linhas)


def _copiar_clipboard(texto):
    try:
        import subprocess
        proc = subprocess.Popen(['clip'], stdin=subprocess.PIPE)
        proc.communicate(texto.encode('utf-8'))
        print('\n  [Copiado para clipboard]')
    except Exception:
        pass


def rodar(arquivo_json):
    sys.stdout.reconfigure(encoding='utf-8')
    with open(arquivo_json, encoding='utf-8') as f:
        dados = json.load(f)
    resultado   = interpretar_anemia(dados)
    texto_saida = _formatar_resultado(resultado)
    print(texto_saida)
    _copiar_clipboard(texto_saida)
    return resultado
