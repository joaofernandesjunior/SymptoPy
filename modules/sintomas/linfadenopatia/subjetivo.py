# modules/sintomas/linfadenopatia/subjetivo.py
# Anamnese dirigida — Linfadenopatia — Adulto
#
# BLOCO 0 — Demográfico (idade, sexo)
# BLOCO 1 — Características do linfonodo (localização, tamanho, textura, duração)
# BLOCO 2 — Red flags (sintomas B, esplenomegalia, CBC anormal)
# BLOCO 3 — Localizado vs. generalizado + território de drenagem
# BLOCO 4 — Exames disponíveis (hemograma, sorologias)
#
# Rodar: python -m modules.sintomas.linfadenopatia.subjetivo

import json, os, sys
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from utils.perguntas import sn


def _bloco(t):
    print(f'\n{"─"*56}\n  {t}\n{"─"*56}')

def _int(prompt, mn=0, mx=9999):
    while True:
        try:
            v = int(input(prompt).strip())
            if mn <= v <= mx: return v
            print(f'  Digite {mn}–{mx}.')
        except ValueError:
            print('  Número inteiro.')

def _float(prompt):
    while True:
        try: return float(input(prompt).strip().replace(',', '.'))
        except ValueError: print('  Número (ex: 2.5).')

def _escolha(prompt, ops):
    for i, (_, l) in enumerate(ops, 1): print(f'  {i}. {l}')
    while True:
        try:
            idx = int(input(prompt).strip())
            if 1 <= idx <= len(ops): return ops[idx-1][0]
            print(f'  1–{len(ops)}.')
        except ValueError: print('  Número.')


def coletar_subjetivo_linfadenopatia(dados_preenchidos=None):
    sys.stdout.reconfigure(encoding='utf-8')
    dados = dados_preenchidos or {}

    print('\n' + '='*56)
    print('  LINFADENOPATIA — ANAMNESE DIRIGIDA')
    print('='*56)

    # ── Bloco 0: Demográfico ─────────────────────────────────────────
    _bloco('BLOCO 0 — Dados do paciente')
    dados['idade'] = _int('  Idade (anos): ', 1, 120)
    dados['sexo']  = _escolha('  Sexo: ', [('M','Masculino'), ('F','Feminino')])
    dados['tabagismo']   = sn('  Tabagista atual ou ex-tabagista? ')
    dados['imunossupressao'] = sn('  Imunossuprimido (HIV, corticoide crônico, quimioterapia)? ')
    dados['hiv_conhecido']   = sn('  HIV positivo conhecido? ') if dados['imunossupressao'] else False

    # ── Bloco 1: Características do linfonodo ────────────────────────
    _bloco('BLOCO 1 — Características do linfonodo')
    dados['localizacao'] = _escolha('  Localização predominante: ', [
        ('cervical',         'Cervical (pescoço)'),
        ('axilar',           'Axilar (axila)'),
        ('inguinal',         'Inguinal (virilha)'),
        ('supraclavicular',  'Supraclavicular ← sempre patológico'),
        ('epitroclear',      'Epitroclear (cotovelo)'),
        ('popliteo',         'Poplíteo (atrás do joelho)'),
        ('generalizado',     'Generalizado (≥ 2 regiões não contíguas)'),
    ])

    dados['tamanho_cm'] = _float('  Tamanho estimado do maior linfonodo (cm): ')

    dados['textura'] = _escolha('  Consistência/textura: ', [
        ('mole_movel',  'Mole e móvel (sugestivo reativo)'),
        ('borrachoso',  'Borrachoso / elástico (sugestivo linfoma)'),
        ('duro_fixo',   'Duro, pétreo ou fixo (sugestivo neoplasia)'),
    ])

    dados['doloroso']  = sn('  Linfonodo doloroso à palpação? ')
    dados['duracao_semanas'] = _int('  Há quantas semanas está presente? ', 0, 260)
    dados['crescimento_rapido'] = sn('  Crescimento rápido (> 1 cm em < 2 semanas)? ')
    dados['pele_sobre_linfonodo'] = sn('  Alteração de pele sobre o linfonodo (eritema, flutuação)? ')

    # ── Bloco 2: Red flags ───────────────────────────────────────────
    _bloco('BLOCO 2 — Sintomas B e red flags sistêmicos')
    dados['febre_sem_foco']      = sn('  Febre > 38°C sem causa infecciosa clara? ')
    dados['sudorese_noturna']    = sn('  Sudorese noturna intensa (encharca a roupa)? ')
    dados['perda_peso']          = sn('  Perda de peso involuntária > 4,5 kg em 6 meses? ')
    dados['b_symptoms'] = any([dados['febre_sem_foco'], dados['sudorese_noturna'], dados['perda_peso']])

    dados['esplenomegalia']      = sn('  Esplenomegalia detectada ao exame? ')
    dados['hemoptise']           = sn('  Hemoptise? ')
    dados['alargamento_mediastino'] = sn('  Alargamento de mediastino em RX? (se disponível) ')

    # CBC
    dados['hc_disponivel'] = sn('  Hemograma disponível? ')
    if dados['hc_disponivel']:
        dados['pancitopenia']    = sn('  Pancitopenia (queda de ≥ 2 séries)? ')
        dados['blastos']         = sn('  Blastos ou linfócitos atípicos no esfregaço? ')
        dados['anemia_inexplicada'] = sn('  Anemia sem causa aparente? ')
        dados['ldh_disponivel']  = sn('  LDH disponível? ')
        dados['ldh_valor']       = _float('  LDH (U/L — referência < 240): ') if dados['ldh_disponivel'] else None
    else:
        dados['pancitopenia'] = False
        dados['blastos'] = False
        dados['anemia_inexplicada'] = False
        dados['ldh_disponivel'] = False
        dados['ldh_valor'] = None

    # ── Bloco 3: Território de drenagem / etiologia ──────────────────
    _bloco('BLOCO 3 — Contexto etiológico')

    if dados['localizacao'] in ('cervical',):
        dados['faringite_recente']  = sn('  Faringite / dor de garganta recente? ')
        dados['problema_dental']    = sn('  Problema dentário (abscessso, infecção)? ')
        dados['infeccao_pele_cab']  = sn('  Infecção de pele em cabeça/pescoço? ')
    else:
        dados['faringite_recente'] = dados['problema_dental'] = dados['infeccao_pele_cab'] = False

    if dados['localizacao'] == 'axilar':
        dados['infeccao_mmss']      = sn('  Infecção no membro superior ipsilateral? ')
        dados['exposicao_gato']     = sn('  Arranhão ou mordida de gato (especialmente filhote)? ')
        dados['papula_inoculacao']  = sn('  Pápula/pústula no local da arranhadura? ') if dados['exposicao_gato'] else False
        dados['vacina_recente_ax']  = sn('  Vacinação recente no braço ipsilateral (< 6 semanas)? ')
        dados['alteracao_mama']     = sn('  Alteração mamária (nódulo, descarga, espessamento)? ') if dados['sexo'] == 'F' else False
    else:
        dados['infeccao_mmss'] = dados['exposicao_gato'] = dados['papula_inoculacao'] = False
        dados['vacina_recente_ax'] = dados['alteracao_mama'] = False

    if dados['localizacao'] == 'inguinal':
        dados['infeccao_mmii']      = sn('  Infecção no membro inferior (celulite, ferida)? ')
        dados['contato_sexual_recente'] = sn('  Contato sexual recente desprotegido? ')
        dados['sintomas_ists']      = sn('  Sintomas genitais (úlcera, corrimento, disúria)? ') if dados['contato_sexual_recente'] else False

        # Diferencial hérnia vs. linfonodo
        print('\n  [Diferencial hérnia inguinal / femoral vs. linfonodo]')
        dados['aumenta_valsalva']   = sn('  A massa AUMENTA ou APARECE ao tossir, fazer força ou ficar em pé? ')
        dados['redutivel']          = sn('  A massa SOME ou DIMINUI ao deitar ou empurrar suavemente? ') if dados['aumenta_valsalva'] else False
        dados['sons_intestinais']   = sn('  Há sons intestinais (borborigmos) sobre a massa? ')
        dados['abaixo_lig_inguinal']= sn('  A massa fica ABAIXO da prega inguinal (virilha mais inferior/medial)? ')
        dados['extensao_escrotal']  = sn('  A massa se estende para o escroto ou lábio maior? ') if dados['sexo'] == 'M' or True else False
        dados['multiplos_nodulos']  = sn('  São múltiplos nódulos (> 1 caroço palpável na região)? ')
        dados['piora_esforco']      = sn('  Piora com esforço físico ou ao final do dia? ')
    else:
        dados['infeccao_mmii'] = dados['contato_sexual_recente'] = dados['sintomas_ists'] = False
        dados['aumenta_valsalva'] = dados['redutivel'] = dados['sons_intestinais'] = False
        dados['abaixo_lig_inguinal'] = dados['extensao_escrotal'] = False
        dados['multiplos_nodulos'] = dados['piora_esforco'] = False

    # EBV / mono
    dados['sindrome_mono']    = sn('  Tríade: febre + faringite + adenopatia cervical posterior? ')
    dados['monospot_feito']   = sn('  Monospot realizado? ') if dados['sindrome_mono'] else False
    dados['monospot_positivo']= sn('  Monospot positivo? ') if dados['monospot_feito'] else False

    # TB
    dados['risco_tb'] = sn('  Fator de risco para TB (imigrante, contato TB, HIV, imunossupressão)? ')
    dados['igra_feito']   = sn('  IGRA ou PPD realizado? ') if dados['risco_tb'] else False
    dados['igra_positivo']= sn('  IGRA/PPD positivo? ') if dados['igra_feito'] else False

    # HIV
    dados['hiv_testado']   = sn('  Teste de HIV realizado? ')
    dados['hiv_positivo']  = sn('  HIV positivo? ') if dados['hiv_testado'] else (True if dados['hiv_conhecido'] else False)
    dados['comportamento_risco_hiv'] = sn('  Comportamento de risco para HIV (não testado)? ') if not dados['hiv_testado'] else False

    # ── Bloco 4: ATBs em uso ─────────────────────────────────────────
    _bloco('BLOCO 4 — Tratamentos em curso')
    dados['atb_em_uso']    = sn('  Está em uso de antibiótico para esta adenopatia? ')
    dados['atb_duracao']   = _int('  Há quantos dias? ', 1, 60) if dados['atb_em_uso'] else 0
    dados['melhora_atb']   = sn('  Houve melhora com o antibiótico? ') if dados['atb_em_uso'] else False
    dados['medicamentos_culpados'] = sn('  Usa fenitoína, alopurinol, atenolol ou outro fármaco associado a adenopatia? ')

    # ── Salvar ───────────────────────────────────────────────────────
    ts    = datetime.now().strftime('%Y%m%d_%H%M%S')
    pasta = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'dados_pacientes')
    os.makedirs(pasta, exist_ok=True)
    arq   = os.path.join(pasta, f'linfadenopatia_{ts}.json')
    with open(arq, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f'\n  [Dados salvos: {arq}]')
    return dados, arq


if __name__ == '__main__':
    coletar_subjetivo_linfadenopatia()
