# modules/sintomas/orl/rinossinusite_subjetivo.py
# Sintoma-guia: Obstrução Nasal / Sinusite / Rinossinusite
#
# Cobre: IVAS viral (< 7d), RSA bacteriana (critérios 2025 AAO-HNS),
#        Rinite alérgica, RSC (> 12 semanas), Polipose nasal.
#        Red flags: celulite orbitária, complicação meníngea.
#
# Retorna: (dados: dict, arquivo_json: str)

import json
import os
import sys
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))


def _ask(prompt, opts=None, default=None):
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
    raw = input(f'\n  {prompt} (s/n) → ').strip().lower()
    if raw in ('s', 'sim', 'y', 'yes'):
        return True
    if raw in ('n', 'nao', 'não', 'no'):
        return False
    return default == 'sim'


def _input_num(prompt, inteiro=False):
    while True:
        raw = input(f'\n  {prompt}: ').strip()
        try:
            return int(raw) if inteiro else float(raw)
        except ValueError:
            print('  ⚠️  Digite um número.')


# =============================================================================
# COLETA PRINCIPAL
# =============================================================================

def coletar_subjetivo_rinossinusite(dados_preenchidos: dict = None) -> tuple:
    dados = dict(dados_preenchidos or {})

    if 'idade' not in dados:
        dados['idade'] = _input_num('Idade do paciente (anos)', inteiro=True)
    if 'sexo' not in dados:
        dados['sexo'] = _ask('Sexo biológico', ['M', 'F'])

    idade = dados['idade']

    print('\n' + '=' * 60)
    print('  AVALIAÇÃO — OBSTRUÇÃO NASAL / SINUSITE')
    print('=' * 60)

    # ─── BLOCO 1 — Duração (gate crítico) ─────────────────────────────────────
    print('\n  [ Bloco 1 — Duração dos sintomas ]')
    print('  (A duração é o critério diagnóstico mais importante nesse módulo)')

    duracao_raw = _ask(
        'Há quanto tempo com esses sintomas nasais?',
        ['< 7 dias', '7–9 dias', '10–28 dias', '> 4 semanas (1 mês)', '> 12 semanas (3 meses)'],
    )
    dados['duracao_sintomas'] = duracao_raw

    # Mapeamento para número de dias (aproximado)
    _duracao_dias = {
        '< 7 dias':           3,
        '7–9 dias':           8,
        '10–28 dias':         14,
        '> 4 semanas (1 mês)': 30,
        '> 12 semanas (3 meses)': 90,
    }
    dados['duracao_dias_aprox'] = _duracao_dias.get(duracao_raw, 5)
    dados['duracao_cronica'] = dados['duracao_dias_aprox'] >= 84  # ≥ 12 semanas

    # ─── BLOCO 2 — Sintomas nasais ─────────────────────────────────────────────
    print('\n  [ Bloco 2 — Sintomas nasais ]')

    dados['obstrucao_nasal']   = _sim_nao('Obstrução/entupimento nasal?')
    dados['rinorreia']         = _sim_nao('Coriza / secreção nasal?')
    if dados['rinorreia']:
        dados['rinorreia_tipo'] = _ask(
            'Tipo de secreção nasal:',
            ['Clara / aquosa', 'Mucoide (branca/amarelada espessa)', 'Purulenta (verde/amarela)'],
        )
        dados['rinorreia_purulenta'] = ('Purulenta' in dados['rinorreia_tipo'])
        dados['rinorreia_clara']     = ('Clara' in dados['rinorreia_tipo'])
    else:
        dados['rinorreia_tipo']      = None
        dados['rinorreia_purulenta'] = False
        dados['rinorreia_clara']     = False

    dados['gotejamento_pos_nasal'] = _sim_nao('Secreção "caindo" pela garganta (gotejamento pós-nasal)?')
    dados['hiposmia_anosmia']      = _sim_nao('Olfato diminuído (hiposmia) ou ausente (anosmia)?')
    dados['espirros_salva']        = _sim_nao('Espirros em salva (vários seguidos)?')

    # ─── BLOCO 3 — Dor/pressão facial ────────────────────────────────────────
    print('\n  [ Bloco 3 — Dor ou pressão facial ]')

    dados['dor_facial']       = _sim_nao('Dor ou pressão na face / fronte / maçãs do rosto?')
    if dados['dor_facial']:
        dados['dor_facial_loc'] = _ask(
            'Onde a dor é mais intensa?',
            ['Fronte (frontal)', 'Maçãs do rosto / abaixo dos olhos (maxilar)',
             'Entre os olhos (etmoidal)', 'Difusa / não sabe localizar'],
        )
        dados['piora_inclinacao'] = _sim_nao(
            'Dor piora ao inclinar a cabeça para frente / se abaixar?'
        )
        dados['dor_facial_unilateral'] = _sim_nao('A dor facial é predominantemente de UM lado?')
    else:
        dados['dor_facial_loc']        = None
        dados['piora_inclinacao']      = False
        dados['dor_facial_unilateral'] = False

    # ─── BLOCO 4 — Febre e sintomas sistêmicos ────────────────────────────────
    print('\n  [ Bloco 4 — Febre e sintomas sistêmicos ]')

    dados['febre'] = _sim_nao('Febre presente?')
    if dados['febre']:
        temp_raw = _ask(
            'Temperatura máxima:',
            ['< 38°C', '38–38,9°C', '≥ 39°C'],
        )
        dados['temperatura_grau'] = temp_raw
        dados['febre_alta']       = (temp_raw == '≥ 39°C')
    else:
        dados['temperatura_grau'] = 'afebril'
        dados['febre_alta']       = False

    dados['mal_estar_mialgia'] = _sim_nao('Mal-estar intenso / dores no corpo / fadiga?')
    dados['cefaleia']          = _sim_nao('Cefaleia presente?')

    # ─── BLOCO 5 — Critérios diagnósticos RSAB (2025 AAO-HNS) ────────────────
    print('\n  [ Bloco 5 — Padrão de evolução ]')

    dados['double_sickening'] = _sim_nao(
        'Os sintomas estavam melhorando e pioraram novamente após melhora inicial\n'
        '  (piora bifásica / "double sickening")?'
    )

    # Critério grave RSAB: febre alta + rinorreia purulenta unilateral + dor facial ≥ 3-4 dias
    dados['sindrome_grave_rsab'] = (
        dados.get('febre_alta') and
        dados.get('rinorreia_purulenta') and
        dados.get('dor_facial_unilateral') and
        dados['duracao_dias_aprox'] >= 3
    )

    # ─── BLOCO 6 — Sintomas alérgicos ────────────────────────────────────────
    print('\n  [ Bloco 6 — Componente alérgico ]')

    dados['prurido_nasal_ocular'] = _sim_nao('Coceira nos olhos e no nariz (prurido)?')
    dados['piora_sazonal']        = _sim_nao('Piora em determinadas estações (primavera, pó, mofo)?')
    dados['alergenos_conhecidos'] = _sim_nao('Rinite alérgica diagnosticada ou alergia conhecida?')
    dados['corticoide_nasal_uso'] = _sim_nao('Já usa corticoide nasal (Nasonex, Busonid, etc.)?')

    # ─── BLOCO 7 — Red flags orbitários e meníngeos ──────────────────────────
    print('\n  [ Bloco 7 — Red flags — Complicações ]')
    print('  ⚠️  Qualquer positivo = encaminhamento PS imediato')

    dados['edema_periorbital']  = _sim_nao('Inchaço ou vermelhidão ao redor do olho?')
    dados['diplopia']           = _sim_nao('Visão dupla?')
    dados['proptose']           = _sim_nao('Olho projetado para fora (proptose)?')
    dados['rigidez_nucal']      = _sim_nao('Rigidez na nuca (pescoço difícil de fletir)?')
    dados['cefaleia_intensa']   = _sim_nao('Cefaleia muito intensa / pior da vida?')
    dados['alteracao_consciencia'] = _sim_nao('Confusão mental / dificuldade de acordar?')

    # ─── BLOCO 8 — Contexto e fatores de risco ───────────────────────────────
    print('\n  [ Bloco 8 — Contexto ]')

    dados['atb_recente_30d']    = _sim_nao('Uso de antibiótico no último mês?')
    dados['fumante']            = _sim_nao('Fumante?')
    dados['imunossuprimido']    = _sim_nao('Imunodeficiência / uso de imunossupressor?')
    dados['desvio_septo']       = _sim_nao('Desvio de septo nasal conhecido?')
    dados['polipos_conhecidos'] = _sim_nao('Pólipos nasais conhecidos?')

    # Risco de alta resistência / Amox-Clav indicada
    dados['risco_rsab_grave'] = any([
        dados.get('atb_recente_30d'),
        dados.get('imunossuprimido'),
        dados['idade'] < 2 or dados['idade'] > 65,
        dados.get('double_sickening') and dados['duracao_dias_aprox'] >= 10,
    ])

    # Alergia a beta-lactâmicos
    dados['alergia_betalactamico'] = _sim_nao('Alergia a penicilina ou cefalosporinas?')
    if dados['alergia_betalactamico']:
        dados['alergia_tipo_1'] = _sim_nao(
            'A reação foi grave (anafilaxia, urticária generalizada, broncoespasmo)?'
        )
    else:
        dados['alergia_tipo_1'] = False

    # ─── Flags derivadas ──────────────────────────────────────────────────────

    # Red flags orbitários
    dados['red_flag_orbital'] = any([
        dados.get('edema_periorbital'),
        dados.get('diplopia'),
        dados.get('proptose'),
    ])

    # Red flags meníngeos
    dados['red_flag_meningeo'] = any([
        dados.get('rigidez_nucal'),
        dados.get('cefaleia_intensa'),
        dados.get('alteracao_consciencia'),
    ])

    # Critérios RSAB 2025 (AAO-HNS): qualquer um dos três
    # ATENÇÃO: usar bool() explícito — evita o bug "not x is False" que zera o braço de ≥10d
    dados['rsab_criterio'] = (
        dados['duracao_dias_aprox'] >= 10 or
        bool(dados.get('double_sickening')) or
        bool(dados.get('sindrome_grave_rsab'))
    )

    # Trava de segurança: < 7 dias = viral puro (exceto sickening ou grave precoce)
    if (dados['duracao_dias_aprox'] < 7
            and not dados.get('double_sickening')
            and not dados.get('sindrome_grave_rsab')):
        dados['rsab_criterio'] = False

    # Rinite alérgica suspeita
    dados['rinite_alergica_suspeita'] = (
        dados.get('espirros_salva') and
        dados.get('rinorreia_clara') and
        not dados.get('febre') and
        (dados.get('prurido_nasal_ocular') or dados.get('piora_sazonal') or dados.get('alergenos_conhecidos'))
    )

    # ─── Salvar JSON ──────────────────────────────────────────────────────────
    os.makedirs('dados_pacientes', exist_ok=True)
    ts  = datetime.now().strftime('%Y%m%d_%H%M%S')
    arq = os.path.join('dados_pacientes', f'rinossinusite_subjetivo_{ts}.json')
    with open(arq, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    print(f'\n  [Dados salvos: {arq}]')
    return dados, arq


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    dados, arq = coletar_subjetivo_rinossinusite()
    print(f'\nRSAB critério: {dados.get("rsab_criterio")}')
    print(f'Crônica: {dados.get("duracao_cronica")}')
    print(f'Orbital flag: {dados.get("red_flag_orbital")}')
