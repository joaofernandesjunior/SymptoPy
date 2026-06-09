# modules/raciocinio/musculoesqueletico/mao_punho/core/runner.py

import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
from modules.raciocinio.musculoesqueletico.mao_punho.core.engine_mao_punho import interpretar_mao_punho


def _sep(c='─', n=54):
    print(c * n)


def _imprimir_hipotese(h):
    print(f'\n  [{h["forca"].upper()}] {h["hipotese"]} (score {h["score"]})')
    for p in h.get('positivos', []):
        print(f'    + {p}')

    if h.get('alerta_grave'):
        _sep()
        print('\n  ALERTA: Atrofia tenar / fraqueza — encaminhamento URGENTE para cirurgia de mao.')

    if h.get('alerta_diabetes'):
        _sep()
        print('\n  ALERTA DM: Menor eficacia de infiltracao. Monitorar glicemia apos corticosteroide.')

    nf = h.get('conduta_nao_farmacologica', [])
    if nf:
        _sep()
        print('  Nao-farmacológico:')
        for item in nf:
            print(f'  * {item}')

    farm = h.get('farmacologico', [])
    if farm:
        _sep()
        print('  Farmacológico:')
        for item in farm:
            print(f'  * {item}')

    workup = h.get('workup', [])
    if workup:
        _sep()
        print('  Exames a solicitar:')
        for item in workup:
            print(f'  * {item}')

    enc = h.get('encaminhar', '')
    if enc:
        print(f'\n  Encaminhamento: {enc}')

    img = h.get('imagem', '')
    if img:
        print(f'  Imagem: {img}')

    conduta_dir = h.get('conduta_nao_farmacologica') or h.get('conduta', [])
    # conduta direta (trauma)
    if 'conduta' in h:
        _sep()
        print('  Conduta:')
        for item in h['conduta']:
            print(f'  * {item}')


def _imprimir_resultado(resultado):
    categoria = resultado['categoria']

    print()
    _sep('=')
    print('  RESULTADO — MAO, PUNHO E DEDOS')
    _sep('=')

    # ── Red flags ──────────────────────────────────────────────────────
    flags = resultado.get('red_flags', {}).get('flags', [])
    if flags:
        _sep()
        for f in flags:
            urgencia = f['urgencia'].upper()
            print(f'\n  [{urgencia}] {f["achado"]}')
            print(f'  Conduta: {f["acao"]}')

    if categoria == 'red_flag_mao_punho':
        _sep('=')
        print()
        return

    # ── Trauma escafoide (resultado direto, nao hipoteses) ───────────────
    if categoria == 'trauma_escafoide_suspeito':
        _sep()
        print(f'\n  [{resultado["forca"].upper()}] {resultado["hipotese"]} (score {resultado["score"]})')
        for p in resultado.get('positivos', []):
            print(f'    + {p}')
        nf = resultado.get('conduta_nao_farmacologica', [])
        if nf:
            _sep()
            print('  Conduta:')
            for item in nf:
                print(f'  * {item}')
        farm = resultado.get('farmacologico', [])
        if farm:
            _sep()
            print('  Farmacológico:')
            for item in farm:
                print(f'  * {item}')
        enc = resultado.get('encaminhar', '')
        if enc:
            print(f'\n  Encaminhamento: {enc}')
        img = resultado.get('imagem', '')
        if img:
            print(f'  Imagem: {img}')
        _sep('=')
        print()
        return

    # ── Hipóteses (STC / mecanico / reumatologico) ───────────────────────
    provaveis = resultado.get('hipoteses_provaveis', [])
    possiveis  = resultado.get('hipoteses_possiveis', [])

    _sep()
    label = {
        'tunel_do_carpo':             'SINDROME DO TUNEL DO CARPO',
        'de_quervain':                'TENOSSINOVITE DE DE QUERVAIN',
        'dedo_em_gatilho':            'DEDO EM GATILHO',
        'rizartrose_thumb_cmc':       'RIZARTROSE DO POLEGAR (CMC)',
        'suspeita_artrite_reumatoide': 'SUSPEITA DE ARTRITE REUMATOIDE',
        'avaliacao_mao_punho':        'AVALIACAO DA MAO E PUNHO',
    }.get(categoria, categoria.upper())
    print(f'\n  {label}')

    # Alerta ulnar (STC com suspeita ulnar concomitante)
    alerta_ulnar = resultado.get('alerta_ulnar', '')
    if alerta_ulnar:
        _sep()
        print(f'\n  ALERTA ULNAR: {alerta_ulnar}')

    if not provaveis and not possiveis:
        msg = resultado.get('mensagem', 'Dados insuficientes para hipótese.')
        _sep()
        print(f'\n  {msg}')
        _sep('=')
        print()
        return

    if provaveis:
        print('\n  HIPOTESES PROVÁVEIS:')
        for h in provaveis:
            _imprimir_hipotese(h)

    if possiveis:
        _sep()
        print('\n  HIPOTESES POSSÍVEIS (baixa forca):')
        for h in possiveis:
            print(f'  * {h["hipotese"]} (score {h["score"]})')

    _sep('=')
    print()


def rodar(arquivo_json):
    sys.stdout.reconfigure(encoding='utf-8')
    with open(arquivo_json, encoding='utf-8') as f:
        dados = json.load(f)
    resultado = interpretar_mao_punho(dados)
    _imprimir_resultado(resultado)
    return resultado
