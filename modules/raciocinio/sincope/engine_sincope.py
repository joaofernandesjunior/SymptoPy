# modules/raciocinio/sincope/engine_sincope.py
# Motor de raciocínio clínico — Síncope
#
# Baseado em: ESC 2018, Canadian Syncope Risk Score (CSRS)
# Escopo: adulto ambulatorial
#
# Categorias:
#   sincope_emergencia          — red flags → PS imediato
#   sincope_vasovagal           — vasovagal confirmada
#   sincope_situacional         — miccional/defecação/tosse
#   sincope_ortostatica         — hipotensão ortostática
#   sincope_cardiaca_alto_risco — CSRS ≥4 → internação
#   sincope_cardiaca_medio_risco — CSRS 1-3 → avaliação expedita
#   sincope_indeterminada       — sem diagnóstico após avaliação básica


# =============================================================================
# STEP 1 — RED FLAGS
# =============================================================================

_RED_FLAGS_ECG = [
    ('ecg_brugada',           'Padrão Brugada (supradesnivelamento ST V1-V3)'),
    ('ecg_preexcitacao',      'Pré-excitação ventricular (WPW)'),
    ('ecg_bav3',              'Bloqueio AV de 3º grau'),
    ('ecg_brd_ou_bre_novo',   'BRE/BRD novo ou desconhecido'),
    ('ecg_arritmia_vent',     'Arritmia ventricular (TV/FV) ao ECG/Holter'),
    ('ecg_qtc_maior_480',     'QTc > 480 ms'),
    ('ecg_qrs_maior_130',     'QRS > 130 ms'),
    ('ecg_q_patologica',      'Ondas Q patológicas (isquemia prévia)'),
]


def _avaliar_red_flags(dados):
    flags = []

    if dados.get('doenca_estrutural_cardiaca'):
        flags.append({
            'achado': 'Cardiopatia estrutural conhecida (IC, estenose aórtica, CMHO, IAM prévio)',
            'acao':   'PS urgente — síncope em cardiopata tem mortalidade elevada',
        })
    if dados.get('sincope_esforco'):
        flags.append({
            'achado': 'Síncope durante ou imediatamente após esforço físico',
            'acao':   'PS urgente — excluir CMHO, estenose aórtica, arritmia ventricular',
        })
    if dados.get('historia_familiar_morte_subita'):
        flags.append({
            'achado': 'História familiar de morte súbita (familiar < 50 anos)',
            'acao':   'Investigação de canalopatia — encaminhar cardiologia urgente',
        })
    if dados.get('sincope_com_dor_toracica') or dados.get('sincope_com_dispneia'):
        flags.append({
            'achado': 'Síncope associada a dor torácica ou dispneia',
            'acao':   'PS urgente — excluir TEP, dissecção aórtica, SCA',
        })
    if dados.get('deficit_focal'):
        flags.append({
            'achado': 'Déficit neurológico focal após síncope',
            'acao':   'PS urgente — excluir AVC/AIT (não é síncope verdadeira)',
        })

    # ECG anormais
    ecg_feito = dados.get('ecg_realizado', False)
    if ecg_feito:
        for chave, descr in _RED_FLAGS_ECG:
            if dados.get(chave):
                flags.append({
                    'achado': f'ECG: {descr}',
                    'acao':   'PS urgente — arritmia ou doença estrutural pelo ECG',
                })

    return flags


# =============================================================================
# STEP 2 — CLASSIFICAÇÃO CLÍNICA
# =============================================================================

def _classificar_clinico(dados):
    """Retorna tipo clínico se padrão reconhecível."""

    # Vasovagal — trigger característico + pródromo
    tem_gatilho_vv = (
        dados.get('gatilho_posicional') or
        dados.get('gatilho_emocional') or
        dados.get('gatilho_dor_flebotomia')
    )
    tem_prodrome = (
        dados.get('prodrome_nausea_diaforese') or
        dados.get('prodrome_visual') or
        dados.get('prodrome_calor')
    )
    if tem_gatilho_vv and tem_prodrome:
        return 'vasovagal'

    # Situacional
    if (dados.get('gatilho_miccao') or
            dados.get('gatilho_defecacao') or
            dados.get('gatilho_tosse_deglut')):
        return 'situacional'

    # Ortostática — sintomas ao levantar + queda de PA medida
    sintomas_posicao = dados.get('sintomas_ao_levantar', False)
    queda_medida     = dados.get('queda_pas_20') or dados.get('queda_pad_10')
    if sintomas_posicao and queda_medida:
        return 'ortostatica'

    return None   # não classificável clinicamente


# =============================================================================
# STEP 3 — CANADIAN SYNCOPE RISK SCORE (CSRS)
# =============================================================================

_CSRS_ITEMS = [
    ('predisposicao_vasovagal',   -2, 'Predisposição a síncope vasovagal'),
    ('doenca_cardiaca_conhecida',  1, 'Doença cardíaca (DAC, IC, valvopatia significativa)'),
    ('pa_anormal',                 2, 'PA sistólica 90 ou > 180 mmHg no evento'),
    ('ecg_qrs_maior_130',          1, 'QRS > 130 ms ao ECG'),
    ('ecg_qtc_maior_480',          2, 'QTc > 480 ms ao ECG'),
    ('troponina_elevada',           2, 'Troponina elevada acima do percentil 99'),
]


def _calcular_csrs(dados):
    score = 0
    itens = []
    for chave, pts, descr in _CSRS_ITEMS:
        if dados.get(chave):
            score += pts
            itens.append(f'{descr} ({pts:+d})')
    return score, itens


def _interpretar_csrs(score):
    if score <= -2:
        return 'muito_baixo', '0,3% risco de desfecho grave em 30 dias'
    if score <= 0:
        return 'baixo', '0,8% risco — alta segura com seguimento ambulatorial'
    if score <= 3:
        return 'medio', '3,1% risco — avaliação cardiológica expedita'
    if score <= 5:
        return 'alto', '19,7% risco — hospitalização ou avaliação urgente'
    return 'muito_alto', '> 51% risco — hospitalização imediata'


# =============================================================================
# CAUSAS DE HIPOTENSÃO ORTOSTÁTICA
# =============================================================================

def _causa_oh(dados):
    """Retorna causa provável de OH se pistas presentes."""
    if dados.get('medicamento_hipotensor_em_uso'):
        return 'farmacológica'
    if dados.get('desidratacao_clinica'):
        return 'desidratação'
    if dados.get('diabetes') or dados.get('parkinson') or dados.get('neuropatia_autonomica'):
        return 'neurogenica'
    return 'investigar'


# =============================================================================
# PONTO DE ENTRADA
# =============================================================================

def _enriquecer_sincope(resultado, dados):
    """Pente fino clínico — alertas de segurança (direção, desprescrição)."""
    cat = resultado.get('categoria', '')
    try:
        idade = int(dados.get('idade', 0) or 0)
    except (ValueError, TypeError):
        idade = 0
    alertas = []

    # Restrição de direção/atividades de risco — sempre que não for vasovagal típico
    if cat in ('sincope_emergencia', 'sincope_cardiaca_alto_risco',
               'sincope_cardiaca_medio_risco', 'sincope_indeterminada'):
        alertas.append(
            '⚠️ ORIENTAR: NÃO dirigir, operar máquinas ou atividades de risco (altura/natação) '
            'até esclarecimento etiológico — síncope inexplicada/cardíaca tem risco de recorrência súbita. '
            'Registrar a orientação no prontuário (medicolegal).')

    # Desprescrição de hipotensor (ortostática farmacológica) — reforço no idoso (Beers)
    if dados.get('medicamento_hipotensor_em_uso') and (
            cat == 'sincope_ortostatica' or resultado.get('causa_oh') == 'farmacológica'):
        msg = ('⚠️ Síncope ortostática + anti-hipertensivo/diurético/alfa-bloqueador: '
               'REVISAR e desprescrever/reduzir o agente causal (rever necessidade real).')
        if idade >= 65:
            msg += ' Idoso: alfa-bloqueadores e diuréticos de alça são critérios de Beers neste contexto.'
        alertas.append(msg)

    if alertas:
        resultado['alertas_seguranca'] = alertas
    return resultado


def interpretar_sincope(dados):
    return _enriquecer_sincope(_interpretar_sincope_core(dados), dados)


def _interpretar_sincope_core(dados):
    # ── 1. Red flags ─────────────────────────────────────────────────────────
    flags = _avaliar_red_flags(dados)
    if flags:
        return {
            'categoria': 'sincope_emergencia',
            'red_flags': flags,
            'tipo':      'sincope',
        }

    # ── 2. Classificação clínica ─────────────────────────────────────────────
    tipo_clinico = _classificar_clinico(dados)

    # ── 3. CSRS ──────────────────────────────────────────────────────────────
    csrs_score, csrs_itens = _calcular_csrs(dados)
    csrs_risco, csrs_descr = _interpretar_csrs(csrs_score)

    # ── 4. Categoria final ───────────────────────────────────────────────────
    if tipo_clinico == 'vasovagal':
        categoria = 'sincope_vasovagal'
    elif tipo_clinico == 'situacional':
        categoria = 'sincope_situacional'
    elif tipo_clinico == 'ortostatica':
        categoria = 'sincope_ortostatica'
    elif csrs_risco in ('alto', 'muito_alto'):
        categoria = 'sincope_cardiaca_alto_risco'
    elif csrs_risco == 'medio':
        categoria = 'sincope_cardiaca_medio_risco'
    else:
        categoria = 'sincope_indeterminada'

    return {
        'categoria':    categoria,
        'tipo_clinico': tipo_clinico,
        'csrs_score':   csrs_score,
        'csrs_itens':   csrs_itens,
        'csrs_risco':   csrs_risco,
        'csrs_descr':   csrs_descr,
        'causa_oh':     _causa_oh(dados) if tipo_clinico == 'ortostatica' else None,
        'tipo':         'sincope',
        # Pass-through
        'ecg_realizado':         dados.get('ecg_realizado', False),
        'pa_ortostatica_medida': dados.get('pa_ortostatica_medida', False),
        'medicamentos_causais':  dados.get('medicamento_hipotensor_em_uso', False),
        'idade':                 dados.get('idade', 0),
    }
