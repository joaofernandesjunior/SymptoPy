# modules/raciocinio/sono/runner.py

import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from modules.raciocinio.sono.engine_sono import interpretar_sono, _isi_grau, _isi_grau_label


_ISI_LABEL = {
    'sem_clinica': 'Sem significância clínica (0–7)',
    'leve':        'Leve (8–14)',
    'moderada':    'Moderada (15–21)',
    'grave':       'Grave (22–28)',
}

_CAT_TITULO = {
    'tcr_rem_pre_parkinson':   '⚠️  TRANSTORNO COMPORTAMENTAL DO SONO REM — Marcador Pré-Parkinson',
    'narcolepsia_suspeita':    '⚠️  NARCOLEPSIA SUSPEITA',
    'aos_suspeita':            'APNEIA OBSTRUTIVA DO SONO — Alto Risco',
    'spi':                     'SÍNDROME DAS PERNAS INQUIETAS',
    'bruxismo_sono':           'BRUXISMO DO SONO',
    'sfas':                    'SÍNDROME DA FASE ATRASADA DO SONO',
    'parassonia_nrem':         'PARASSONIA NREM',
    'pesadelos_tept':          'PESADELOS RECORRENTES / TEPT',
    'desmame_benzo':           'INSÔNIA POR USO CRÔNICO DE BENZODIAZEPÍNICO',
    'insonia_comportamental':  'INSÔNIA COMPORTAMENTAL',
    'insonia_psiquiatrica':    'INSÔNIA — COMPONENTE PSIQUIÁTRICO',
    'insonia_cronica_primaria':'INSÔNIA CRÔNICA PRIMÁRIA',
    'insonia_subaguda':        'INSÔNIA SUBAGUDA / LEVE',
    'insonia_hipotireoidismo': 'INSÔNIA SECUNDÁRIA — HIPOTIREOIDISMO',
    'insonia_dor':             'INSÔNIA SECUNDÁRIA — DOR CRÔNICA',
    'insonia_turno':           'DISTÚRBIO DO SONO POR TURNO DE TRABALHO',
}


def _sep(n=58):
    return '─' * n


def _formatar(resultado) -> str:
    linhas = []
    cat    = resultado.get('categoria', '')
    titulo = _CAT_TITULO.get(cat, cat.upper().replace('_', ' '))

    linhas.append('=' * 58)
    linhas.append('  TRANSTORNOS DO SONO — RESULTADO')
    linhas.append('=' * 58)
    linhas.append(f'\n  {titulo}')
    linhas.append(f'  Diagnóstico: {resultado.get("diagnostico", "")}')

    # ISI
    isi = resultado.get('isi_score') or resultado.get('isi_grau')
    if isi:
        grau_label = _ISI_LABEL.get(resultado.get('isi_grau', ''), '')
        if grau_label:
            linhas.append(f'  ISI: {grau_label}')

    linhas.append('')

    # Scores (AOS)
    if cat == 'aos_suspeita':
        linhas.append(f'  STOP-BANG: {resultado.get("stopbang")}/8')
        linhas.append(f'  Epworth:   {resultado.get("epworth")}/24')
        linhas.append(f'  IMC:       {resultado.get("imc")} kg/m²')
        linhas.append(f'  Pescoço:   {resultado.get("circunferencia_cervical")} cm')
        if resultado.get('risco_grave'):
            linhas.append('  ★ Risco GRAVE — priorizar polissonografia')
        linhas.append('')

    # Narcolepsia — critérios
    if cat == 'narcolepsia_suspeita':
        crit = resultado.get('criterios', {})
        linhas.append('  Critérios presentes:')
        for k, v in crit.items():
            if v:
                linhas.append(f'  ✓ {k.replace("_", " ").title()}')
        linhas.append('')

    # Bruxismo — critérios
    if cat == 'bruxismo_sono':
        crit = resultado.get('criterios_presentes', {})
        linhas.append('  Critérios de bruxismo do sono:')
        for k, v in crit.items():
            marca = '✓' if v else '○'
            linhas.append(f'  {marca} {k.replace("_", " ").title()}')
        if resultado.get('isrs_associado'):
            linhas.append('\n  ⚠️  ISRS em uso — pode ser causa do bruxismo')
        if resultado.get('aos_coexiste'):
            linhas.append('  ⚠️  AOS coexistente — tratar AOS primeiro')
        linhas.append('')

    # CBT-I prescrita
    cbti = resultado.get('cbti')
    if cbti:
        linhas.append(_sep())
        linhas.append('  CBT-I — TRATAMENTO PRINCIPAL')
        linhas.append(_sep())
        for comp, texto in cbti.items():
            linhas.append(f'\n  [{comp.replace("_", " ").upper()}]')
            for linha in texto.split('\n'):
                linhas.append(f'  {linha.strip()}')

    # Desmame BZD
    desmame = resultado.get('desmame')
    if desmame:
        linhas.append('')
        linhas.append(_sep())
        linhas.append('  DESMAME DE BENZODIAZEPÍNICO')
        linhas.append(_sep())
        for chave, texto in desmame.items():
            linhas.append(f'\n  [{chave.upper()}]')
            for linha in texto.split('\n'):
                linhas.append(f'  {linha.strip()}')

    # Conduta
    conduta = resultado.get('conduta', [])
    if conduta:
        linhas.append('')
        linhas.append(_sep())
        linhas.append('  CONDUTA')
        linhas.append(_sep())
        for item in conduta:
            linhas.append(f'  {"  " if item.startswith("  ") else "• "}{item}')

    linhas.append('\n' + '=' * 58)
    return '\n'.join(linhas)


def _clipboard(texto):
    try:
        import subprocess
        p = subprocess.Popen(['clip'], stdin=subprocess.PIPE)
        p.communicate(texto.encode('utf-8'))
    except Exception:
        pass


def rodar(arquivo_json):
    sys.stdout.reconfigure(encoding='utf-8')
    with open(arquivo_json, encoding='utf-8') as f:
        dados = json.load(f)
    resultado = interpretar_sono(dados)
    texto     = _formatar(resultado)
    print(texto)
    _clipboard(texto)
    return resultado
