# modules/sintomas/orl/odinofagia_subjetivo.py
# Sintoma-guia: Dor de Garganta / Odinofagia
#
# Cobre: faringoamigdalite bacteriana (Critérios de Centor Modificados),
#        abscesso periamigdaliano, estridor/insuficiência respiratória,
#        mononucleose infecciosa (EBV), viral puro.
#
# Retorna: (dados: dict, arquivo_json: str)

import json
import os
import sys
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from modules.sintomas.abdominal.gastro_subjetivo import _input_num  # reutiliza helper


# ─── Helper local ─────────────────────────────────────────────────────────────

def _ask(prompt, opts=None, default=None):
    """Pergunta simples com opções numeradas."""
    if opts:
        print(f'\n  {prompt}')
        for i, o in enumerate(opts, 1):
            print(f'    {i}. {o}')
        while True:
            raw = input('  → ').strip()
            if raw == '' and default is not None:
                return default
            if raw.isdigit() and 1 <= int(raw) <= len(opts):
                return opts[int(raw) - 1]
            print(f'  ⚠️  Digite um número de 1 a {len(opts)}.')
    else:
        raw = input(f'\n  {prompt}\n  → ').strip()
        return raw if raw else default


def _sim_nao(prompt, default='nao'):
    """Retorna True para sim, False para não."""
    raw = input(f'\n  {prompt} (s/n) → ').strip().lower()
    if raw in ('s', 'sim', 'y', 'yes'):
        return True
    if raw in ('n', 'nao', 'não', 'no'):
        return False
    return default == 'sim'


def _centor_age_score(idade: int) -> int:
    """Modificador de idade dos Critérios de Centor (McIsaac 1998)."""
    if idade is None:
        return 0
    if 3 <= idade <= 14:
        return 1
    if 15 <= idade <= 44:
        return 0
    return -1  # ≥ 45 anos


# =============================================================================
# COLETA PRINCIPAL
# =============================================================================

def coletar_subjetivo_odinofagia(dados_preenchidos: dict = None) -> tuple:
    """
    Coleta anamnese de dor de garganta / odinofagia.
    Retorna (dados: dict, arquivo_json: str).
    """
    dados = dict(dados_preenchidos or {})

    # ─── Garantir campos básicos ───────────────────────────────────────────────
    if 'idade' not in dados:
        dados['idade'] = _input_num('Idade do paciente (anos)', inteiro=True)
    if 'sexo' not in dados:
        dados['sexo'] = _ask('Sexo biológico', ['M', 'F'])

    idade = dados['idade']

    print('\n' + '=' * 60)
    print('  AVALIAÇÃO — DOR DE GARGANTA / ODINOFAGIA')
    print('=' * 60)

    # ─── BLOCO 1 — Tempo e evolução ───────────────────────────────────────────
    print('\n  [ Bloco 1 — Tempo e evolução ]')

    inicio_raw = _ask(
        'Quando começou a dor de garganta?',
        ['Hoje', '1-2 dias', '3-7 dias', '> 7 dias'],
    )
    dados['inicio_sintomas'] = inicio_raw

    dados['progressao'] = _ask(
        'Como está evoluindo?',
        ['Melhorando', 'Estável', 'Piorando'],
    )

    # ─── BLOCO 2 — Red flags de abscesso ──────────────────────────────────────
    print('\n  [ Bloco 2 — Red flags de abscesso periamigdaliano ]')
    print('  (Responda com honestidade — influencia a conduta de encaminhamento)')

    dados['trismo']         = _sim_nao('Dificuldade ou dor para abrir a boca completamente (trismo)?')
    dados['sialorreia']     = _sim_nao('Babando sem querer, incapaz de engolir a saliva?')
    dados['voz_batata']     = _sim_nao('Voz "abafada" ou "de batata na boca" (diferente do normal)?')
    dados['desvio_uvula']   = _sim_nao('Desvio da úvula (campanulazinha) para um lado (observou ao iluminar)?')
    dados['disfagia_saliva'] = _sim_nao('Não consegue engolir nem a própria saliva?')

    # ─── BLOCO 3 — Estridor / insuficiência respiratória ─────────────────────
    print('\n  [ Bloco 3 — Dificuldade respiratória ]')
    print('  ⚠️  Estridor = ronco/chiado AO INSPIRAR — emergência absoluta.')

    dados['dificuldade_respiratoria'] = _sim_nao('Alguma dificuldade para respirar agora?')
    dados['estridor'] = False
    if dados['dificuldade_respiratoria']:
        dados['estridor']        = _sim_nao('Barulho de ronco/chiado ao INSPIRAR (estridor)?')
        dados['posicao_sniffing'] = _sim_nao('Prefere ficar sentado com pescoço estendido para frente?')

    # ─── BLOCO 4 — Critérios de Centor Modificados (McIsaac) ─────────────────
    print('\n  [ Bloco 4 — Critérios de Centor Modificados ]')
    print('  (Determina a probabilidade de Streptococcus pyogenes — GAS)')

    dados['febre'] = _sim_nao('Febre atual ou nas últimas 24h (temperatura ≥ 38°C)?')

    if dados['febre']:
        temp_raw = _ask(
            'Temperatura máxima medida:',
            ['< 38°C (sensação sem termômetro)', '38–39°C', '> 39°C'],
        )
        dados['temperatura_grau'] = temp_raw
        dados['febre_alta'] = (temp_raw == '> 39°C')
    else:
        dados['temperatura_grau'] = 'afebril'
        dados['febre_alta']       = False

    dados['tosse'] = _sim_nao('Tosse presente (mesmo que leve)?')
    # Ausência de tosse = +1 no Centor

    dados['exsudato_amigdaliano'] = _sim_nao(
        'Exsudato nas amígdalas — pus / pontos brancos / placas (iluminou com lanterna)?'
    )
    dados['adenopatia_cervical_ant'] = _sim_nao(
        'Gânglios doloridos na parte FRONTAL/LATERAL do pescoço (cervicais anteriores)?'
    )

    # Centor score calculado aqui
    dados['centor_score'] = (
        (1 if dados.get('febre')                    else 0) +
        (1 if dados.get('exsudato_amigdaliano')     else 0) +
        (1 if dados.get('adenopatia_cervical_ant')  else 0) +
        (1 if not dados.get('tosse')                else 0) +
        _centor_age_score(idade)
    )

    # ─── BLOCO 5 — Sintomas sistêmicos e mononucleose ─────────────────────────
    print('\n  [ Bloco 5 — Sintomas sistêmicos ]')

    dados['mialgia_fadiga'] = _sim_nao('Muito cansaço / dores no corpo além da garganta?')
    dados['adenopatia_generalizada'] = _sim_nao(
        'Gânglios aumentados também em outras regiões (axilas, virilha — além do pescoço)?'
    )

    # Gate para mononucleose: exsudato + adenopatia generalizada + faixa etária
    if dados.get('adenopatia_generalizada') or (
            dados.get('exsudato_amigdaliano') and 15 <= idade <= 35):
        print('\n  [ Bloco 5B — Suspeita de Mononucleose Infecciosa (EBV) ]')
        dados['dor_hipocondrio_esq'] = _sim_nao(
            'Dor ou desconforto no lado esquerdo da barriga (baço aumentado)?'
        )
        dados['rash_apos_amox']      = _sim_nao(
            'Usou amoxicilina/ampicilina recentemente e apareceu manchas vermelhas pelo corpo?'
        )
    else:
        dados['dor_hipocondrio_esq'] = False
        dados['rash_apos_amox']      = False

    # ─── BLOCO 6 — Contexto epidemiológico e alergias ─────────────────────────
    print('\n  [ Bloco 6 — Contexto e alergias ]')

    dados['atb_recente_30d']        = _sim_nao('Usou antibiótico nos últimos 30 dias?')
    dados['contato_amigdalite']     = _sim_nao('Contato com caso de amigdalite ou strep confirmado?')
    dados['alergia_penicilina']     = _sim_nao('Alergia a penicilina ou amoxicilina?')

    if dados['alergia_penicilina']:
        dados['alergia_penicilina_grave'] = _sim_nao(
            'A reação foi GRAVE (urticária generalizada, falta de ar, anafilaxia)?'
        )
    else:
        dados['alergia_penicilina_grave'] = False

    # ─── BLOCO 7 — Rouquidão associada ────────────────────────────────────────
    print('\n  [ Bloco 7 — Rouquidão ]')
    dados['rouquidao'] = _sim_nao('Rouquidão / disfonia presente junto com a dor de garganta?')
    if dados['rouquidao']:
        duracao_rouq = _ask(
            'Há quanto tempo está rouco?',
            ['< 3 semanas', '≥ 3 semanas'],
        )
        dados['rouquidao_cronica'] = (duracao_rouq == '≥ 3 semanas')
    else:
        dados['rouquidao_cronica'] = False

    # ─── Flags derivadas ──────────────────────────────────────────────────────
    dados['abscesso_suspeito'] = any([
        dados.get('trismo'),
        dados.get('sialorreia'),
        dados.get('voz_batata'),
        dados.get('desvio_uvula'),
        dados.get('disfagia_saliva'),
    ])

    dados['emergencia_respiratoria'] = (
        dados.get('estridor') or
        dados.get('dificuldade_respiratoria')
    )

    dados['mononucleose_suspeita'] = (
        dados.get('exsudato_amigdaliano') and
        dados.get('adenopatia_generalizada') and
        15 <= idade <= 35
    )

    # ─── Salvar JSON ──────────────────────────────────────────────────────────
    os.makedirs('dados_pacientes', exist_ok=True)
    ts  = datetime.now().strftime('%Y%m%d_%H%M%S')
    arq = os.path.join('dados_pacientes', f'odinofagia_subjetivo_{ts}.json')
    with open(arq, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    print(f'\n  [Dados salvos: {arq}]')
    return dados, arq


# =============================================================================
# CLI direto
# =============================================================================

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    dados, arq = coletar_subjetivo_odinofagia()
    print(f'\nCentor score calculado: {dados.get("centor_score")}')
    print(f'Abscesso suspeito: {dados.get("abscesso_suspeito")}')
    print(f'Emergência respiratória: {dados.get("emergencia_respiratoria")}')
