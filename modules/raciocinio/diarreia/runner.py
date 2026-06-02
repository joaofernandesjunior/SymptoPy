# modules/raciocinio/diarreia/runner.py

import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from modules.raciocinio.diarreia.engine_diarreia import interpretar_diarreia

_LABEL = {
    'diarreia_imunossuprimido':          'IMUNOSSUPRIMIDO — Workup amplo',
    'diarreia_sepse':                    'SEPSE / CHOQUE — Internação imediata',
    'diarreia_disenteria_bacilar':       'DISENTERIA BACILAR',
    'diarreia_stec_suspeita':            'SUSPEITA STEC (E. coli O157) — NÃO ATB / NÃO loperamida',
    'diarreia_c_diff':                   'C. DIFFICILE — Suspeita',
    'diarreia_viajante':                 'DIARREIA DO VIAJANTE',
    'diarreia_toxinfeccao':              'TOXINFECCAO ALIMENTAR',
    'diarreia_aguda_watery':             'GASTROENTERITE AGUDA — Viral / Autolimitada',
    'diarreia_persistente':              'DIARREIA PERSISTENTE — Investigar parasitas',
    'diarreia_cronica_alarme_urgente':   'DIARREIA CRONICA — Alarme urgente (colonoscopia < 2 sem)',
    'diarreia_cronica_alarme_eletivo':   'DIARREIA CRONICA — Investigacao eletiva',
    'diarreia_dii_suspeita':             'DII SUSPEITA (Crohn / RCU) — Calprotectina elevada',
    'diarreia_sii_d':                    'SII-D — Sindrome do Intestino Irritavel (diarreia)',
}

_DESAT_LABEL = {
    'grave':    'GRAVE — IV obrigatorio, internar',
    'moderada': 'MODERADA — SRO 100 mL/kg em 4h',
    'leve':     'LEVE — SRO 50 mL/kg em 4h',
    'sem':      'Sem desidratacao significativa',
}


def _formatar_resultado(resultado) -> str:
    categoria = resultado.get('categoria', '')
    linhas    = []

    linhas.append('=' * 54)
    linhas.append('  RESULTADO — DIARREIA NO ADULTO')
    linhas.append('=' * 54)

    label = _LABEL.get(categoria, categoria.upper())
    linhas.append(f'\n  {label}')

    # Desidratação — exibida em todas as categorias
    desat = resultado.get('desidratacao_grau', 'sem')
    linhas.append(f'  Desidratacao: {_DESAT_LABEL.get(desat, desat)}')

    # Alertas críticos
    if resultado.get('atb_contraindicado'):
        linhas.append('\n  !! ANTIBIOTICO CONTRAINDICADO (risco SHU) !!')
    if resultado.get('loperamida_contraindicada'):
        linhas.append('  !! LOPERAMIDA CONTRAINDICADA (risco megacolon toxico) !!')
    if resultado.get('alerta_shu'):
        linhas.append('  !! MONITORAR SHU: anemia + plaquetopenia + IRA -> internar !!')
    if resultado.get('notificar_vigilancia'):
        linhas.append('  !! NOTIFICAR Vigilancia Epidemiologica (surto alimentar) !!')
    if resultado.get('internacao'):
        linhas.append('  !! INTERNACAO indicada !!')

    # Patógenos (imunossuprimido)
    patogenos = resultado.get('patogenos_suspeitos', [])
    if patogenos:
        linhas.append('\n  Patogenos suspeitos:')
        for p in patogenos:
            linhas.append(f'  • {p}')

    # Agente toxinfecção
    agente = resultado.get('agente_provavel', '')
    if agente:
        linhas.append(f'\n  Agente provavel: {agente}')
        alimento = resultado.get('alimento_suspeito', '')
        if alimento:
            linhas.append(f'  Alimento suspeito: {alimento}')
        incubacao = resultado.get('incubacao_horas', 0)
        if incubacao:
            linhas.append(f'  Incubacao: {incubacao}h')

    # Calprotectina
    calproto = resultado.get('calprotectina')
    if calproto is not None:
        linhas.append(f'\n  Calprotectina fecal: {calproto} mcg/g')

    # Zona cinzenta
    if resultado.get('zona_cinzenta'):
        linhas.append('  (Zona cinzenta 50-200 — repetir em 4-6 sem sem AINEs)')

    # Alarmes crônicos
    alarmes = resultado.get('alarmes', [])
    if alarmes:
        linhas.append('\n  Alarmes identificados:')
        for a in alarmes:
            linhas.append(f'  - {a}')

    # Critérios de gravidade (C. diff)
    crits = resultado.get('criterios_gravidade', {})
    if crits:
        linhas.append('\n  Criterios CDI:')
        for k, v in crits.items():
            linhas.append(f'  {k.capitalize()}: {v}')

    # Conduta
    linhas.append('\n  Conduta:')
    for item in resultado.get('conduta', []):
        linhas.append(f'  • {item}')

    # Exames
    exames = resultado.get('exames', [])
    if exames:
        linhas.append('\n  Exames:')
        for ex in exames:
            linhas.append(f'  • {ex}')

    # Pendente (SII-D sem calprotectina)
    pendente = resultado.get('pendente', '')
    if pendente:
        linhas.append(f'\n  Pendente: {pendente}')

    # Retorno (watery)
    retorno = resultado.get('retorno', '')
    if retorno:
        linhas.append(f'\n  Criterios de retorno: {retorno}')

    # Destino (viajante)
    destino = resultado.get('destino', '')
    if destino and categoria == 'diarreia_viajante':
        asia = resultado.get('asia', False)
        if asia:
            linhas.append('\n  ASIA: Azitromicina obrigatoria (resistencia FQ > 90%)')

    linhas.append('=' * 54)
    return '\n'.join(linhas)


def _copiar_clipboard(texto):
    try:
        import subprocess
        proc = subprocess.Popen(['clip'], stdin=subprocess.PIPE)
        proc.communicate(texto.encode('utf-8'))
        print('\n  [Impressao automatica copiada para o clipboard]')
    except Exception:
        pass


def rodar(arquivo_json):
    sys.stdout.reconfigure(encoding='utf-8')
    with open(arquivo_json, encoding='utf-8') as f:
        dados = json.load(f)
    resultado   = interpretar_diarreia(dados)
    texto_saida = _formatar_resultado(resultado)
    print(texto_saida)
    _copiar_clipboard(texto_saida)
    return resultado
