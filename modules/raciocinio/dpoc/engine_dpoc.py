# modules/raciocinio/dpoc/engine_dpoc.py
# Motor de raciocínio clínico — DPOC (episódico-crônico)
#
# Baseado em: GOLD 2026
# Escopo: adulto ambulatorial
#
# Categorias exacerbação:
#   dpoc_emergencia          — grave → PS/UTI
#   dpoc_exacerbacao_moderada — ATB + corticoide → APS
#   dpoc_exacerbacao_leve    — só broncodilatador → APS
#
# Categorias rotina (GOLD ABE):
#   dpoc_grupo_a             — LAMA ou LABA mono
#   dpoc_grupo_b             — LAMA + LABA
#   dpoc_grupo_e             — LAMA + LABA ± ICS (eosinófilos)


# =============================================================================
# ANTHONISEN — INDICAÇÃO DE ATB
# =============================================================================

def _anthonisen(dados):
    """
    Retorna (n_criterios, criterios, atb_indicado).
    ATB: ≥ 2 de 3 critérios, obrigatoriamente incluindo escarro purulento.
    """
    crit = []
    if dados.get('piora_dispneia'):      crit.append('piora da dispneia')
    if dados.get('aumento_volume_escarro'): crit.append('aumento do volume de escarro')
    if dados.get('escarro_purulento'):   crit.append('escarro purulento')

    atb = len(crit) >= 2 and dados.get('escarro_purulento', False)
    return len(crit), crit, atb


# =============================================================================
# GRAVIDADE DA EXACERBAÇÃO
# =============================================================================

def _gravidade_exacerbacao(dados):
    spo2 = dados.get('spo2', 95)

    # Grave → PS
    if (dados.get('alt_consciencia') or
            dados.get('falencia_respiratoria') or
            dados.get('hipotensao_exac') or
            spo2 < 85):
        return 'grave'

    # Moderada → APS (precisa corticoide + possivelmente ATB)
    if (dados.get('escarro_purulento') or
            dados.get('aumento_volume_escarro') or
            dados.get('piora_dispneia') or
            (85 <= spo2 < 92)):
        return 'moderada'

    return 'leve'


# =============================================================================
# GOLD ABE — CLASSIFICAÇÃO CRÔNICA
# =============================================================================

def _gold_abe(dados):
    """Retorna grupo 'A', 'B' ou 'E'."""
    cat      = dados.get('cat_score', 0) or 0
    mmrc     = dados.get('mmrc', 0) or 0
    exac_ano = dados.get('exacerbacoes_ultimo_ano', 0) or 0
    hosp_ano = dados.get('hospitalizacao_ultimo_ano', False)

    alta_sintomas = cat >= 10 or mmrc >= 2
    alto_risco    = exac_ano >= 1 or hosp_ano

    if alto_risco:
        return 'E'
    if alta_sintomas:
        return 'B'
    return 'A'


# =============================================================================
# GOLD GRADE (espirometria)
# =============================================================================

def _gold_grade(fev1_pct):
    if fev1_pct is None:
        return None
    if fev1_pct >= 80: return 1
    if fev1_pct >= 50: return 2
    if fev1_pct >= 30: return 3
    return 4


# =============================================================================
# INDICAÇÃO DE ICS
# =============================================================================

def _indicar_ics(dados, grupo):
    """Retorna (indicado: bool, justificativa: str)."""
    eosin = dados.get('eosinofilos', 0) or 0
    exac  = dados.get('exacerbacoes_ultimo_ano', 0) or 0
    hosp  = dados.get('hospitalizacao_ultimo_ano', False)

    if grupo == 'E':
        if eosin >= 300:
            return True, f'Eosinófilos ≥ 300 cél/μL ({eosin}) — adicionar ICS ao LAMA+LABA (triple)'
        if eosin >= 100 and (exac >= 2 or hosp):
            return True, f'Eosinófilos {eosin} + exacerbações frequentes — considerar ICS'
    return False, ''


# =============================================================================
# ALPHA-1 ANTITRIPSIN — TRIAGEM
# =============================================================================

def _triagem_alfa1(dados):
    idade     = dados.get('idade', 50) or 50
    fumante   = dados.get('tabagismo_ativo', False) or dados.get('ex_tabagista', False)
    hist_fam  = dados.get('historia_familiar_dpoc', False)
    fev1_pct  = dados.get('fev1_percentual')
    predom_bas = dados.get('enfisema_predominio_basal', False)

    return (idade < 45 and not fumante) or predom_bas or hist_fam


# =============================================================================
# ALERTA DE OXIGENOTERAPIA (alvo 88–92% na DPOC)
# =============================================================================

def _alerta_o2_dpoc(dados):
    """
    Alvo de SpO₂ na DPOC = 88–92%. O₂ em excesso inibe o drive hipóxico →
    acidose hipercápnica (narcose por CO₂). Dispara alerta se a SpO₂ medida
    estiver ACIMA de 92% no contexto de exacerbação (possível hiperóxia
    iatrogênica) ou sempre como lembrete do teto.
    """
    alertas = ['⚠️ ALVO DE O₂ NA DPOC = 88–92%. Titular O₂ ao MÍNIMO necessário — '
               'O₂ em excesso inibe o drive hipóxico e causa acidose hipercápnica (narcose por CO₂).']
    spo2 = dados.get('spo2')
    if spo2 is not None and spo2 > 92:
        alertas.insert(0,
            f'🔴 SpO₂ {spo2}% ACIMA do alvo (88–92%) — se em O₂ suplementar, REDUZIR o fluxo. '
            'Hiperóxia no DPOC retentor → hipercapnia e acidose. Colher gasometria arterial.')
    return alertas


# =============================================================================
# PONTO DE ENTRADA
# =============================================================================

def interpretar_dpoc(dados):
    tipo = dados.get('consulta_tipo', 'rotina')

    # ── EXACERBAÇÃO ──────────────────────────────────────────────────────────
    if tipo == 'exacerbacao':
        grav = _gravidade_exacerbacao(dados)
        n_crit, crit_list, atb = _anthonisen(dados)
        alerta_o2 = _alerta_o2_dpoc(dados)

        if grav == 'grave':
            return {
                'categoria':  'dpoc_emergencia',
                'tipo':       'dpoc',
                'spo2':       dados.get('spo2'),
                'alertas_seguranca': alerta_o2,
            }

        if grav == 'moderada':
            return {
                'categoria':  'dpoc_exacerbacao_moderada',
                'anthonisen': n_crit,
                'criterios':  crit_list,
                'atb':        atb,
                'tipo':       'dpoc',
                'spo2':       dados.get('spo2'),
                'alertas_seguranca': alerta_o2,
            }

        return {
            'categoria':  'dpoc_exacerbacao_leve',
            'anthonisen': n_crit,
            'criterios':  crit_list,
            'atb':        False,
            'tipo':       'dpoc',
            'spo2':       dados.get('spo2'),
            'alertas_seguranca': alerta_o2,
        }

    # ── ROTINA / CONTROLE ────────────────────────────────────────────────────
    grupo     = _gold_abe(dados)
    fev1_pct  = dados.get('fev1_percentual')
    grade     = _gold_grade(fev1_pct)
    ics_ind, ics_just = _indicar_ics(dados, grupo)
    alfa1_triar = _triagem_alfa1(dados)

    cat_map = {'A': 'dpoc_grupo_a', 'B': 'dpoc_grupo_b', 'E': 'dpoc_grupo_e'}

    return {
        'categoria':     cat_map[grupo],
        'grupo':         grupo,
        'gold_grade':    grade,
        'fev1_pct':      fev1_pct,
        'cat_score':     dados.get('cat_score'),
        'mmrc':          dados.get('mmrc'),
        'exacerbacoes':  dados.get('exacerbacoes_ultimo_ano', 0),
        'ics_indicado':  ics_ind,
        'ics_just':      ics_just,
        'eosinofilos':   dados.get('eosinofilos'),
        'alfa1_triar':   alfa1_triar,
        'tabagismo_ativo': dados.get('tabagismo_ativo', False),
        'tipo':          'dpoc',
    }
