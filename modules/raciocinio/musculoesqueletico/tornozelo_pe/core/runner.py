# modules/raciocinio/musculoesqueletico/tornozelo_pe/core/runner.py

import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
from modules.raciocinio.musculoesqueletico.tornozelo_pe.core.engine_tornozelo_pe import interpretar_tornozelo_pe


def _sep(c='─', n=54):
    print(c * n)


def _imprimir_resultado(resultado):
    categoria = resultado['categoria']

    print()
    _sep('=')
    print('  RESULTADO — DOR NO TORNOZELO E PÉ')
    _sep('=')

    # ── Red Flags ──────────────────────────────────────────────────────────
    flags = resultado.get('red_flags', {}).get('flags', [])
    if flags:
        _sep()
        for f in flags:
            urgencia = f['urgencia'].upper()
            print(f'\n  [{urgencia}] {f["achado"]}')
            print(f'  Conduta: {f["acao"]}')

    # ── Alerta Corticosteroide Aquiles ─────────────────────────────────────
    alerta = resultado.get('alerta_aquiles', {})
    if alerta.get('alerta'):
        _sep()
        print(f'\n  ALERTA AQUILES: {alerta["mensagem"]}')

    if categoria == 'red_flag_tornozelo_pe':
        _sep('=')
        print()
        return

    # ── Trauma Ottawa Positivo ─────────────────────────────────────────────
    if categoria == 'trauma_ottawa_positivo':
        _sep()
        print('\n  TRAUMA — OTTAWA POSITIVO: RX indicado')
        achados = resultado.get('achados_positivos', [])
        for a in achados:
            print(f'    + {a}')
        _sep()
        print('\n  Conduta:')
        for item in resultado.get('conduta', []):
            print(f'  • {item}')
        enc = resultado.get('encaminhar', '')
        if enc:
            print(f'\n  Encaminhamento: {enc}')
        _sep('=')
        print()
        return

    # ── Entorse de Tornozelo ───────────────────────────────────────────────
    if categoria == 'entorse_tornozelo':
        _sep()
        print('\n  [ALTA] Entorse de Tornozelo — Ottawa negativo')
        for a in resultado.get('achados_positivos', []):
            print(f'    + {a}')
        _sep()
        print('\n  Conduta não-farmacológica:')
        for item in resultado.get('conduta_nao_farmacologica', []):
            print(f'  • {item}')
        _sep()
        print('\n  Farmacológico:')
        for item in resultado.get('farmacologico', []):
            print(f'  • {item}')
        alerta_inst = resultado.get('alerta_instabilidade', '')
        if alerta_inst:
            _sep()
            print(f'\n  ALERTA: {alerta_inst}')
        _sep('=')
        print()
        return

    # ── Hipóteses (fasciite / aquiles / morton) ────────────────────────────
    provaveis = resultado.get('hipoteses_provaveis', [])
    possiveis  = resultado.get('hipoteses_possiveis', [])

    _sep()
    label = {
        'fasciite_plantar':    'FASCIITE PLANTAR',
        'tendinopatia_aquiles': 'TENDINOPATIA DE AQUILES',
        'morton_neuroma':       'NEUROMA DE MORTON',
        'avaliacao_tornozelo_pe': 'AVALIAÇÃO DO TORNOZELO E PÉ',
    }.get(categoria, categoria.upper())
    print(f'\n  {label}')

    if not provaveis and not possiveis:
        msg = resultado.get('mensagem', 'Dados insuficientes para hipótese.')
        _sep()
        print(f'\n  {msg}')
        _sep('=')
        print()
        return

    if provaveis:
        print('\n  HIPÓTESES PROVÁVEIS:')
        for h in provaveis:
            print(f'\n  [{h["forca"].upper()}] {h["hipotese"]} (score {h["score"]})')
            for p in h.get('positivos', []):
                print(f'    + {p}')

            alerta_csi = h.get('alerta_csi', '')
            if alerta_csi:
                _sep()
                print(f'\n  ALERTA: {alerta_csi}')

            nf = h.get('conduta_nao_farmacologica', [])
            if nf:
                _sep()
                print('  Conduta não-farmacológica:')
                for item in nf:
                    print(f'  • {item}')

            farm = h.get('farmacologico', [])
            if farm:
                _sep()
                print('  Farmacológico:')
                for item in farm:
                    print(f'  • {item}')

            prog = h.get('prognostico', '')
            if prog:
                _sep()
                print(f'\n  {prog}')

            ft = h.get('fisioterapia', '')
            if ft:
                print(f'\n  Fisioterapia: {ft}')

            enc = h.get('encaminhar', '')
            if enc:
                print(f'  Encaminhamento: {enc}')

            img = h.get('imagem', '')
            if img:
                print(f'  Imagem: {img}')

    if possiveis:
        _sep()
        print('\n  HIPÓTESES POSSÍVEIS (baixa força):')
        for h in possiveis:
            print(f'  • {h["hipotese"]} (score {h["score"]})')

    _sep('=')
    print()


def rodar(arquivo_json):
    sys.stdout.reconfigure(encoding='utf-8')
    with open(arquivo_json, encoding='utf-8') as f:
        dados = json.load(f)
    resultado = interpretar_tornozelo_pe(dados)
    _imprimir_resultado(resultado)
    return resultado
