# modules/sintomas/anemia/subjetivo.py
# Coleta de hemograma completo para interpretação de anemia
#
# Fluxo:
#   Bloco 0 — Contexto clínico (sexo, gestante, doença crônica)
#   Bloco 1 — Hemograma básico (Hb, MCV, RDW, leucócitos, plaquetas)
#   Bloco 2 — Reticulócitos (se disponíveis)
#   Bloco 3 — Exames de ferro (ferritina, ferro sérico, TIBC, sat transf)
#   Bloco 4 — Vitaminas e outros (B12, folato, creatinina, TSH)
#   Bloco 5 — Contexto clínico adicional (sangramento, sintomas hemólise)
#
# Rodar da raiz: python -m modules.sintomas.anemia.subjetivo

import json
import os
import sys
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from utils.perguntas import sn


def _bloco(titulo):
    print(f'\n{"─"*54}')
    print(f'  {titulo}')
    print(f'{"─"*54}')


def _perg_float(prompt, obrigatorio=True):
    while True:
        raw = input(prompt).strip().replace(',', '.')
        if not raw:
            if not obrigatorio:
                return None
            print('  Valor obrigatório.')
            continue
        try:
            return float(raw)
        except ValueError:
            print('  Digite um número (ex: 12.5).')


def _perg_float_opt(prompt):
    """Float opcional — Enter para pular."""
    return _perg_float(prompt + ' [Enter=não disponível]: ', obrigatorio=False)


def _opcoes(prompt, opcoes):
    """Menu de opções numeradas. Retorna string da opção escolhida."""
    for i, op in enumerate(opcoes, 1):
        print(f'  {i}. {op}')
    while True:
        raw = input(prompt).strip()
        if raw.isdigit() and 1 <= int(raw) <= len(opcoes):
            return opcoes[int(raw) - 1]
        print(f'  Digite 1–{len(opcoes)}.')


def coletar_subjetivo_anemia(dados_preenchidos=None):
    sys.stdout.reconfigure(encoding='utf-8')
    dados = dados_preenchidos or {}

    print('\n' + '=' * 54)
    print('  INTERPRETAÇÃO DE HEMOGRAMA — ANEMIA')
    print('  Insira os valores do exame para análise')
    print('=' * 54)

    # ── Bloco 0: Contexto ───────────────────────────────────────────
    _bloco('BLOCO 0 — Contexto do paciente')
    dados['sexo'] = _opcoes('  Sexo biológico: ', ['masculino', 'feminino'])
    if dados['sexo'] == 'feminino':
        dados['gestante'] = sn('  Gestante? ')
    else:
        dados['gestante'] = False

    dados['doenca_cronica'] = sn(
        '  Há doença crônica conhecida (IRC, neoplasia, AR, IBD, infecção crônica)? '
    )
    if dados['doenca_cronica']:
        dados['doenca_cronica_qual'] = input('  Qual doença: ').strip()
    else:
        dados['doenca_cronica_qual'] = ''

    # ── Bloco 1: Hemograma básico ────────────────────────────────────
    _bloco('BLOCO 1 — Hemograma completo')
    print('  (valores obrigatórios)')
    dados['hb']  = _perg_float('  Hemoglobina (g/dL): ')
    dados['mcv'] = _perg_float('  VCM — Volume Corpuscular Médio (fL): ')
    dados['rdw'] = _perg_float('  RDW (%): ')
    dados['wbc'] = _perg_float('  Leucócitos (×10³/µL): ')
    dados['plt'] = _perg_float('  Plaquetas (×10³/µL): ')

    # RBC (para índice de Mentzer)
    dados['rbc'] = _perg_float_opt('  Eritrócitos/RBC (×10⁶/µL)')

    # ── Bloco 2: Reticulócitos ───────────────────────────────────────
    _bloco('BLOCO 2 — Reticulócitos')
    dados['retic_disponivel'] = sn('  Reticulócitos disponíveis no laudo? ')
    if dados['retic_disponivel']:
        dados['retic_pct'] = _perg_float('  Reticulócitos (%): ')
        print('  (Hematócrito — necessário para índice de reticulócitos)')
        dados['ht'] = _perg_float('  Hematócrito (%): ')
    else:
        dados['retic_pct'] = None
        dados['ht'] = None

    # ── Bloco 3: Exames de ferro ─────────────────────────────────────
    _bloco('BLOCO 3 — Metabolismo do ferro')
    dados['ferro_disponivel'] = sn('  Exames de ferro disponíveis? ')
    if dados['ferro_disponivel']:
        dados['ferritina']      = _perg_float_opt('  Ferritina (ng/mL)')
        dados['ferro_serico']   = _perg_float_opt('  Ferro sérico (µg/dL)')
        dados['tibc']           = _perg_float_opt('  CTLF/TIBC (µg/dL)')
        dados['sat_transf']     = _perg_float_opt('  Saturação de transferrina (%)')
    else:
        dados['ferritina']    = None
        dados['ferro_serico'] = None
        dados['tibc']         = None
        dados['sat_transf']   = None

    # ── Bloco 4: Vitaminas e outros ──────────────────────────────────
    _bloco('BLOCO 4 — Vitaminas e exames complementares')
    dados['b12']        = _perg_float_opt('  Vitamina B12 (pg/mL)')
    dados['folato']     = _perg_float_opt('  Folato sérico (ng/mL)')
    dados['creatinina'] = _perg_float_opt('  Creatinina (mg/dL)')
    dados['tsh']        = _perg_float_opt('  TSH (mUI/L)')

    # Eletroforese de Hb
    dados['eletroforese_hb'] = sn('  Eletroforese de hemoglobina disponível? ')
    if dados['eletroforese_hb']:
        dados['hba2_elevada'] = sn('  HbA₂ elevada (> 3.5%)? ')
        dados['hbf_elevada']  = sn('  HbF elevada? ')
    else:
        dados['hba2_elevada'] = None
        dados['hbf_elevada']  = None

    # ── Bloco 5: Contexto clínico adicional ─────────────────────────
    _bloco('BLOCO 5 — Contexto clínico')
    dados['sangramento_ativo']   = sn('  Sangramento ativo ou recente (GI, menstrual, trauma)? ')
    dados['ictericia']           = sn('  Icterícia ou urina escura? ')
    dados['esplenomegalia']      = sn('  Esplenomegalia ao exame físico? ')
    dados['alcool']              = sn('  Uso significativo de álcool? ')
    dados['vegetariano_vegano']  = sn('  Dieta vegetariana/vegana estrita? ')
    dados['gastro_cirurgia']     = sn('  Cirurgia gástrica prévia ou doença de má absorção? ')

    # Sintomas clínicos
    dados['sintomas_fadiga']     = sn('  Cansaço/fadiga? ')
    dados['sintomas_dispneia']   = sn('  Dispneia aos esforços? ')
    dados['sintomas_palpitacao'] = sn('  Palpitações? ')
    dados['sintomas_neurologico']= sn('  Parestesias ou alteração neurológica (sugestivo B12)? ')

    # ── Salvar ───────────────────────────────────────────────────────
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    pasta = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'dados_pacientes')
    os.makedirs(pasta, exist_ok=True)
    arquivo = os.path.join(pasta, f'anemia_{ts}.json')
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    print(f'\n  [Dados salvos: {arquivo}]')
    return dados, arquivo


if __name__ == '__main__':
    coletar_subjetivo_anemia()
