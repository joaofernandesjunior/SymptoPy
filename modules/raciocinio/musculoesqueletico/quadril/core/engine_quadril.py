# modules/raciocinio/musculoesqueletico/quadril/core/engine_quadril.py
# Motor diagnóstico — Dor no Quadril
# Fontes: Open Evidence (OARSI/EULAR/AAOS), JAMA, Cochrane

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
from modules.raciocinio.musculoesqueletico.red_flags_msk import aplicar_trava_idoso_aine

# =============================================================================
# RED FLAGS
# =============================================================================

def _avaliar_red_flags(dados):
    flags = []

    if dados.get('encurtamento_rotacao_externa'):
        flags.append({
            'urgencia': 'emergencia',
            'achado':   'Membro encurtado e em rotação externa — fratura de colo femoral',
            'acao':     'PS imediato. Não mobilizar. RX AP pelve urgente.',
        })

    if dados.get('nao_suporta_peso') and dados.get('trauma_recente'):
        flags.append({
            'urgencia': 'urgente',
            'achado':   'Incapacidade de carga após trauma — suspeita de fratura',
            'acao':     'RX AP pelve + frog-leg urgente. Imobilizar e encaminhar PS.',
        })

    if dados.get('nao_suporta_peso') and dados.get('osteoporose') and not dados.get('trauma_recente'):
        flags.append({
            'urgencia': 'urgente',
            'achado':   'Incapacidade de carga + osteoporose — fratura por fragilidade',
            'acao':     'RX urgente mesmo sem trauma claro. Encaminhar ortopedia.',
        })

    if dados.get('febre_sistemica'):
        flags.append({
            'urgencia': 'emergencia',
            'achado':   'Febre + dor no quadril — artrite séptica a descartar',
            'acao':     'PS urgente. Punção articular, hemoculturas. Ortopedia.',
        })

    if dados.get('historico_cancer') and dados.get('dor_noturna_intensa'):
        flags.append({
            'urgencia': 'urgente',
            'achado':   'Histórico de câncer + dor noturna intensa — metástase óssea',
            'acao':     'RX + cintilografia/PET. Encaminhar oncologia/ortopedia urgente.',
        })

    return flags


# =============================================================================
# ALERTA AVN (Necrose Avascular) — transversal, qualquer localização
# =============================================================================

def _avaliar_avn(dados):
    score = 0
    if dados.get('uso_corticoide_cronico'): score += 4
    if dados.get('uso_alcool_cronico'):     score += 3
    if dados.get('dor_noturna_intensa'):    score += 2
    if dados.get('nao_suporta_peso') and not dados.get('trauma_recente'): score += 2

    return {
        'alerta': score >= 4,
        'score':  score,
        'acao':   (
            'MRI urgente — fatores de risco para AVN presentes. '
            'RX inicial pode ser normal; MRI detecta precocemente. '
            'Encaminhar ortopedia.'
        ) if score >= 4 else None,
    }


# =============================================================================
# SCORING — GTPS (Lateral)
# =============================================================================

_PESOS_GTPS = [
    ('dor_palpacao_grande_trocanter', 5, 'Palpação dolorosa do grande trocânter'),
    ('dor_decubito_lateral',          3, 'Piora ao deitar sobre o quadril afetado'),
    ('sinal_trendelenburg',           2, 'Sinal de Trendelenburg positivo'),
    ('inicio_gradual',                1, 'Início gradual sem evento agudo'),
    ('idade_acima_40',                1, 'Idade > 40 anos'),
]


def _score_gtps(dados):
    score, positivos = 0, []
    for chave, peso, rotulo in _PESOS_GTPS:
        if dados.get(chave):
            score += peso
            positivos.append(rotulo)
    forca = 'alta' if score >= 8 else 'moderada' if score >= 5 else 'baixa' if score >= 2 else None
    return score, forca, positivos


def _conduta_gtps(forca, dados):
    base = [
        'Repouso relativo — evitar deitar sobre o lado afetado',
        'Alongamento da banda iliotibial e fortalecimento de abdutores',
        'Fisioterapia: fortalecimento de glúteo médio e mínimo (sustentação a longo prazo)',
    ]
    farm = []
    if forca in ('alta', 'moderada'):
        farm = [
            'Infiltração com corticoide (CSI): triamcinolona 20-40 mg + anestésico local '
            '— alívio rápido em 1-3 meses; fisioterapia para sustentação após a crise',
            'AINE oral tem baixa eficácia isolada para GTPS — preferir CSI se dor aguda intensa',
        ]
    return {
        'base': base,
        'farmacologico': farm,
        'fisioterapia': 'Fortalecimento de abdutores + alongamento de IT band',
        'imagem': 'Não rotineira; considerar US para confirmar se dúvida diagnóstica',
        'encaminhar': None if forca != 'alta' else
                      'Ortopedia se refratário após 2 ciclos de CSI + fisioterapia',
    }


# =============================================================================
# SCORING — OA de Quadril (Anterior, > 50 anos)
# =============================================================================

_PESOS_OA = [
    ('limitacao_rotacao_interna',  3, 'Limitação de rotação interna (S 66%, E 79%)'),
    ('limitacao_abducao_adicao',   3, 'Limitação de abdução/adução (S 80%, E 81%)'),
    ('marcha_antalgica',           2, 'Marcha antálgica'),
    ('inicio_gradual',             2, 'Início gradual'),
    ('idade_acima_50',             2, 'Idade > 50 anos'),
    ('dor_sentado_prolongado',     1, 'Dor ao sentar por períodos prolongados'),
    ('piora_caminhar_escadas',     1, 'Piora ao caminhar ou subir escadas'),
    ('crepitacao_movimento',       1, 'Crepitação ao movimento'),
]


def _score_oa(dados):
    score, positivos = 0, []
    for chave, peso, rotulo in _PESOS_OA:
        if dados.get(chave):
            score += peso
            positivos.append(rotulo)
    forca = 'alta' if score >= 9 else 'moderada' if score >= 5 else 'baixa' if score >= 2 else None
    return score, forca, positivos


def _conduta_oa(forca, dados):
    nao_farm = [
        'Exercício aeróbico de baixo impacto: caminhada, bicicleta, natação (nivel A — OARSI)',
        'Fisioterapia: fortalecimento de quadríceps e glúteos, treino de equilíbrio',
        'Perda de peso se sobrepeso/obesidade (reduz carga articular)',
        'Uso de bengala no lado contralateral se dor intensa',
    ]
    farm = ['Paracetamol 500-1000 mg até 3x/dia (alternativa de menor eficácia, menos EAS)']
    if not any([dados.get('historico_cancer'), dados.get('febre_sistemica')]):
        farm.insert(0,
            'AINE oral se sem contraindicação (IRC, IC, doença péptica): '
            'ibuprofeno 400 mg 8/8h ou naproxeno 500 mg 12/12h c/ refeição'
        )
    encaminhar = None
    if forca == 'alta':
        encaminhar = (
            'Ortopedia se refratário após 3-6 meses conservador '
            '(candidato a artroplastia total de quadril)'
        )
    return {
        'base': nao_farm,
        'farmacologico': farm,
        'fisioterapia': 'Fortalecimento glúteo + quadríceps + equilíbrio; hidroterapia como alternativa',
        'imagem': 'RX AP pelve + frog-leg lateral (confirma OA; estadiamento Kellgren-Lawrence)',
        'encaminhar': encaminhar,
    }


# =============================================================================
# SCORING — FAI / Patologia Labral (Anterior, jovem/atleta)
# =============================================================================

_PESOS_FAI = [
    ('faber_positivo',       3, 'FABER positivo (S 72-91%)'),
    ('fadir_positivo',       3, 'FADIR positivo (S 72-91%)'),
    ('atleta_jovem_ativo',   3, 'Atleta ou praticante de atividade intensa'),
    ('dor_flexao_quadril',   2, 'Dor ao fletir o quadril'),
    ('dor_sentado_prolongado', 1, 'Dor ao sentar prolongado'),
    ('idade_abaixo_40',      1, 'Idade < 40 anos'),
]

_BONUS_FAI = 2  # Ambos FABER e FADIR positivos = bônus pela combinação (S 97%)


def _score_fai(dados):
    score, positivos = 0, []
    for chave, peso, rotulo in _PESOS_FAI:
        if dados.get(chave):
            score += peso
            positivos.append(rotulo)
    if dados.get('faber_positivo') and dados.get('fadir_positivo'):
        score += _BONUS_FAI
        positivos.append('FABER + FADIR positivos combinados (S 97% para FAI/labro)')
    forca = 'alta' if score >= 9 else 'moderada' if score >= 5 else 'baixa' if score >= 2 else None
    return score, forca, positivos


def _conduta_fai(forca):
    return {
        'base': [
            'Fisioterapia: fortalecimento de core e estabilizadores pélvicos',
            'Modificação de atividade: reduzir movimentos de flexão extrema enquanto aguarda imagem',
        ],
        'farmacologico': [
            'AINE por curto prazo para controle da dor enquanto aguarda investigação',
        ],
        'fisioterapia': 'Core, estabilizadores pélvicos e propriocepção',
        'imagem': (
            'MRI de quadril (padrão-ouro para labro e cartilagem); '
            'artro-RM se MRI convencional inconclusivo para ruptura labral'
        ),
        'encaminhar': (
            'Ortopedia / cirurgia de quadril para avaliação de artroscopia '
            '(FAI tipo cam/pincer ou ruptura labral confirmada)'
        ),
    }


# =============================================================================
# SCORING — Dor Referida / Lombar / SIJ (Posterior)
# =============================================================================

_PESOS_REFERIDA = [
    ('sintomas_lombares_assoc',   4, 'Sintomas lombares associados'),
    ('inicio_gradual',            1, 'Início gradual'),
]


def _score_dor_referida(dados):
    score, positivos = 0, []
    for chave, peso, rotulo in _PESOS_REFERIDA:
        if dados.get(chave):
            score += peso
            positivos.append(rotulo)

    faber_neg = not dados.get('faber_positivo')
    fadir_neg = not dados.get('fadir_positivo')
    if faber_neg and fadir_neg and dados.get('faber_realizado') and dados.get('fadir_realizado'):
        score += 3
        positivos.append('FABER e FADIR negativos — exclui patologia intra-articular (S 97%)')

    forca = 'alta' if score >= 6 else 'moderada' if score >= 3 else 'baixa' if score >= 1 else None
    return score, forca, positivos


def _conduta_dor_referida():
    return {
        'base': [
            'Investigar coluna lombar como fonte primária da dor',
            'Avaliar sacroilíaca: manobras de provocação (FABER posterior, Gaenslen)',
        ],
        'farmacologico': ['AINE ou paracetamol para controle sintomático enquanto investiga'],
        'fisioterapia': 'Coluna lombar e SIJ — encaminhar para módulo de lombalgia se indicado',
        'imagem': 'RX AP pelve para exclusão. Considerar RX lombar se sintomas lombares proeminentes.',
        'encaminhar': None,
    }


# =============================================================================
# CONSOLIDAÇÃO DAS HIPÓTESES
# =============================================================================

def _consolidar_hipoteses(dados):
    localizacao = dados.get('localizacao_dor', '')
    hipoteses = []

    if localizacao == 'lateral':
        score, forca, pos = _score_gtps(dados)
        if forca:
            hipoteses.append({
                'hipotese':   'GTPS (Síndrome Dolorosa do Grande Trocânter)',
                'forca':      forca,
                'score':      score,
                'positivos':  pos,
                **_conduta_gtps(forca, dados),
            })

    if localizacao == 'anterior':
        score_oa, forca_oa, pos_oa = _score_oa(dados)
        if forca_oa:
            hipoteses.append({
                'hipotese':  'OA de Quadril',
                'forca':     forca_oa,
                'score':     score_oa,
                'positivos': pos_oa,
                **_conduta_oa(forca_oa, dados),
            })

        score_fai, forca_fai, pos_fai = _score_fai(dados)
        if forca_fai:
            hipoteses.append({
                'hipotese':  'FAI / Patologia Labral',
                'forca':     forca_fai,
                'score':     score_fai,
                'positivos': pos_fai,
                **_conduta_fai(forca_fai),
            })

    if localizacao == 'posterior':
        score_ref, forca_ref, pos_ref = _score_dor_referida(dados)
        if forca_ref:
            hipoteses.append({
                'hipotese':  'Dor Referida (Lombar / SIJ / Glútea Profunda)',
                'forca':     forca_ref,
                'score':     score_ref,
                'positivos': pos_ref,
                **_conduta_dor_referida(),
            })

    # Se localização incerta ou sem hipótese forte: rodar todos e rankear
    if not hipoteses:
        for fn, nome in [
            (_score_gtps,         'GTPS'),
            (_score_oa,           'OA de Quadril'),
            (_score_fai,          'FAI / Patologia Labral'),
            (_score_dor_referida, 'Dor Referida'),
        ]:
            s, f, p = fn(dados)
            if f:
                hipoteses.append({'hipotese': nome, 'forca': f, 'score': s, 'positivos': p})

    hipoteses.sort(key=lambda h: h['score'], reverse=True)

    ordem = {'alta': 0, 'moderada': 1, 'baixa': 2}
    provaveis = [h for h in hipoteses if h['forca'] in ('alta', 'moderada')]
    possiveis  = [h for h in hipoteses if h['forca'] == 'baixa']
    exclusao   = []

    # Regra de exclusão: FABER + FADIR negativos descartam FAI/labro com S 97%
    if not dados.get('faber_positivo') and not dados.get('fadir_positivo'):
        exclusao.append('FAI / Patologia Labral (FABER e FADIR negativos — S 97%)')

    return provaveis, possiveis, exclusao


# =============================================================================
# ENTRY POINT
# =============================================================================

def interpretar_quadril(dados):
    red_flags = _avaliar_red_flags(dados)
    avn       = _avaliar_avn(dados)

    if red_flags and any(f['urgencia'] == 'emergencia' for f in red_flags):
        return {
            'categoria':   'red_flag_quadril',
            'localizacao': dados.get('localizacao_dor', ''),
            'red_flags':   {'flags': red_flags},
            'alerta_avn':  avn,
            'hipoteses_provaveis':  [],
            'hipoteses_possiveis':  [],
            'hipoteses_exclusao':   [],
        }

    provaveis, possiveis, exclusao = _consolidar_hipoteses(dados)

    # Trava de segurança — AINE vetado em ≥ 60 anos
    aplicar_trava_idoso_aine(provaveis, dados)
    aplicar_trava_idoso_aine(possiveis, dados)

    return {
        'categoria':          'avaliacao_quadril',
        'localizacao':        dados.get('localizacao_dor', ''),
        'red_flags':          {'flags': red_flags},
        'alerta_avn':         avn,
        'hipoteses_provaveis': provaveis,
        'hipoteses_possiveis': possiveis,
        'hipoteses_exclusao':  exclusao,
    }


# =============================================================================
# TESTE ISOLADO
# =============================================================================

if __name__ == '__main__':
    import json, sys
    sys.stdout.reconfigure(encoding='utf-8')

    _CASOS = {
        'GTPS — alta força': {
            'idade': 52, 'eva_dor': 6, 'localizacao_dor': 'lateral',
            'dor_palpacao_grande_trocanter': True, 'dor_decubito_lateral': True,
            'sinal_trendelenburg': True, 'inicio_gradual': True, 'idade_acima_40': True,
            'nao_suporta_peso': False, 'encurtamento_rotacao_externa': False,
            'febre_sistemica': False, 'trauma_recente': False, 'historico_cancer': False,
            'dor_noturna_intensa': False, 'uso_corticoide_cronico': False,
            'uso_alcool_cronico': False, 'osteoporose': False,
        },
        'OA Quadril — alta força': {
            'idade': 68, 'eva_dor': 7, 'localizacao_dor': 'anterior',
            'limitacao_rotacao_interna': True, 'limitacao_abducao_adicao': True,
            'marcha_antalgica': True, 'inicio_gradual': True, 'idade_acima_50': True,
            'dor_sentado_prolongado': True, 'piora_caminhar_escadas': True,
            'faber_positivo': False, 'fadir_positivo': False, 'atleta_jovem_ativo': False,
            'nao_suporta_peso': False, 'encurtamento_rotacao_externa': False,
            'febre_sistemica': False, 'trauma_recente': False, 'historico_cancer': False,
            'dor_noturna_intensa': False, 'uso_corticoide_cronico': False,
            'uso_alcool_cronico': False, 'osteoporose': False, 'dor_flexao_quadril': False,
            'sintomas_lombares_assoc': False, 'idade_abaixo_40': False, 'crepitacao_movimento': True,
        },
        'FAI / Labro — alta força': {
            'idade': 28, 'eva_dor': 5, 'localizacao_dor': 'anterior',
            'faber_positivo': True, 'fadir_positivo': True,
            'atleta_jovem_ativo': True, 'dor_flexao_quadril': True,
            'dor_sentado_prolongado': True, 'idade_abaixo_40': True,
            'inicio_gradual': True, 'limitacao_rotacao_interna': False,
            'limitacao_abducao_adicao': False, 'marcha_antalgica': False,
            'nao_suporta_peso': False, 'encurtamento_rotacao_externa': False,
            'febre_sistemica': False, 'trauma_recente': False, 'historico_cancer': False,
            'dor_noturna_intensa': False, 'uso_corticoide_cronico': False,
            'uso_alcool_cronico': False, 'osteoporose': False, 'idade_acima_50': False,
            'sintomas_lombares_assoc': False,
        },
        'RED FLAG — Fratura (emergência)': {
            'idade': 80, 'eva_dor': 10, 'localizacao_dor': 'anterior',
            'encurtamento_rotacao_externa': True, 'nao_suporta_peso': True,
            'trauma_recente': True, 'osteoporose': True,
            'febre_sistemica': False, 'historico_cancer': False,
            'dor_noturna_intensa': False, 'uso_corticoide_cronico': False,
            'uso_alcool_cronico': False, 'inicio_gradual': False,
        },
        'ALERTA AVN': {
            'idade': 42, 'eva_dor': 6, 'localizacao_dor': 'anterior',
            'uso_corticoide_cronico': True, 'uso_alcool_cronico': True,
            'dor_noturna_intensa': True, 'nao_suporta_peso': False,
            'encurtamento_rotacao_externa': False, 'febre_sistemica': False,
            'trauma_recente': False, 'historico_cancer': False,
            'inicio_gradual': True, 'faber_positivo': False, 'fadir_positivo': False,
            'atleta_jovem_ativo': False, 'dor_flexao_quadril': True,
            'dor_sentado_prolongado': True, 'idade_abaixo_40': False, 'idade_acima_50': False,
            'limitacao_rotacao_interna': False, 'limitacao_abducao_adicao': False,
            'marcha_antalgica': False, 'sintomas_lombares_assoc': False,
            'piora_caminhar_escadas': False, 'crepitacao_movimento': False,
        },
    }

    for nome, caso in _CASOS.items():
        print(f'\n{"="*60}')
        print(f'  CASO: {nome}')
        print('='*60)
        r = interpretar_quadril(caso)
        print(json.dumps(r, ensure_ascii=False, indent=2))
