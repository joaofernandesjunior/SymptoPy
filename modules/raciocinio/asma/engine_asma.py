# modules/raciocinio/asma/engine_asma.py
# Motor de raciocínio clínico — Asma (episódico-crônico)
#
# Baseado em: GINA 2025
# Escopo: adulto ambulatorial
#
# Bloco 1 separa: 'crise' vs 'rotina'
#
# Categorias crise:
#   asma_emergencia          — risco de vida → UTI/PS imediato
#   asma_crise_grave         — grave → PS (beira do limite APS)
#   asma_crise_leve_moderada — leve-moderada → manejar na APS
#
# Categorias rotina:
#   asma_controlada          — GINA step manter ou step-down
#   asma_parcialmente_ctrl   — 1-2 critérios → step-up 1
#   asma_nao_controlada      — ≥3 critérios → step-up 2 ou encaminhar


# =============================================================================
# STEP 1 — GRAVIDADE DA CRISE (GINA 2025)
# =============================================================================

def _gravidade_crise(dados):
    """
    Retorna 'risco_de_vida', 'grave' ou 'leve_moderada'.
    Usa pior parâmetro presente.
    """
    spo2 = dados.get('spo2', 100)

    # Risco de vida
    if (dados.get('sonolencia_confusao') or
            dados.get('torax_silencioso') or
            dados.get('nao_consegue_falar') or
            spo2 < 90):
        return 'risco_de_vida'

    # Grave
    if (dados.get('fala_palavras_apenas') or
            dados.get('fr_maior_30') or
            dados.get('fc_maior_120') or
            dados.get('uso_musculatura_acessoria') or
            (90 <= spo2 <= 95) or
            (dados.get('pefr_percentual', 100) <= 50)):
        return 'grave'

    return 'leve_moderada'


# =============================================================================
# STEP 2 — CONTROLE CRÔNICO (GINA 2025)
# =============================================================================

_CRITERIOS_CONTROLE = [
    ('sintomas_diurnos_mais_2sem', 'Sintomas diurnos > 2×/semana'),
    ('despertar_noturno',          'Despertar noturno por asma'),
    ('saba_mais_2sem',             'Uso de SABA aliviador > 2×/semana (exceto pré-exercício)'),
    ('limitacao_atividade',        'Limitação de atividade por asma'),
]


def _avaliar_controle(dados):
    """Retorna (n_criterios, lista_criterios_presentes)."""
    presentes = []
    for chave, descr in _CRITERIOS_CONTROLE:
        if dados.get(chave):
            presentes.append(descr)
    return len(presentes), presentes


# =============================================================================
# GINA STEP — PRÓXIMA RECOMENDAÇÃO
# =============================================================================

_GINA_STEPS = {
    1: {
        'label':    'Step 1 — Asma leve intermitente',
        'track1':   'Budesonida/Formoterol 100/6 mcg — 1-2 puffs SOS (anti-inflamatório aliviador)',
        'track2':   'Salbutamol SOS + considerar ICS baixa dose diário',
        'ics_dose': 'Baixa (≤ 400 mcg budesonida/dia)',
    },
    2: {
        'label':    'Step 2 — Asma leve persistente',
        'track1':   'Budesonida/Formoterol 100/6 mcg — 1-2 puffs SOS (GINA prefere a ICS diário)',
        'track2':   'Budesonida 200-400 mcg/dia + Salbutamol SOS',
        'ics_dose': 'Baixa (200-400 mcg budesonida/dia)',
    },
    3: {
        'label':    'Step 3 — MART baixa dose',
        'track1':   'Budesonida/Formoterol 100/6 mcg — 1-2 puffs 2×/dia + SOS (MART, máx 12 puffs/dia)',
        'track2':   'ICS média dose OU ICS baixa dose + LABA; +LAMA se não controlada',
        'ics_dose': 'Baixa-Média (200-800 mcg/dia)',
    },
    4: {
        'label':    'Step 4 — MART média dose',
        'track1':   'Budesonida/Formoterol 200/6 mcg — 2 puffs 2×/dia + SOS (MART)',
        'track2':   'ICS média dose + LABA + considerar LAMA',
        'ics_dose': 'Média (400-800 mcg/dia)',
    },
    5: {
        'label':    'Step 5 — Asma grave não controlada',
        'track1':   'Budesonida/Formoterol MART alta dose + encaminhar pneumologia',
        'track2':   'ICS alta dose + LABA + LAMA; avaliar biológico (anti-IgE, anti-IL5, anti-IL4Rα)',
        'ics_dose': 'Alta (> 800 mcg/dia)',
    },
}


def _recomendar_step(step_atual, controle):
    """Retorna step recomendado e ação."""
    if controle == 'controlada':
        novo_step = max(1, step_atual - 1)
        acao = f'Step-down — reduzir ICS 25-50% se controlada ≥ 3 meses. Ir para Step {novo_step}.'
    elif controle == 'parcialmente_controlada':
        novo_step = min(5, step_atual + 1)
        acao = f'Step-up 1 — controle insuficiente. Ir para Step {novo_step}.'
    else:  # não controlada
        novo_step = min(5, step_atual + 2)
        if novo_step >= 5:
            acao = 'Step-up para Step 5 + encaminhar pneumologia. Verificar adesão e técnica inalatória.'
        else:
            acao = f'Step-up 2 — controle ruim. Ir para Step {novo_step}. Verificar adesão e técnica.'
    return novo_step, acao, _GINA_STEPS.get(novo_step, _GINA_STEPS[5])


# =============================================================================
# PONTO DE ENTRADA
# =============================================================================

def interpretar_asma(dados):
    tipo = dados.get('consulta_tipo', 'rotina')

    # ── CRISE AGUDA ──────────────────────────────────────────────────────────
    if tipo == 'crise':
        grav = _gravidade_crise(dados)
        spo2 = dados.get('spo2', 100)
        pefr = dados.get('pefr_percentual', 100)

        if grav == 'risco_de_vida':
            return {
                'categoria':  'asma_emergencia',
                'gravidade':  'risco_de_vida',
                'tipo':       'asma',
                'spo2':       spo2,
                'pefr':       pefr,
            }
        if grav == 'grave':
            return {
                'categoria':  'asma_crise_grave',
                'gravidade':  'grave',
                'tipo':       'asma',
                'spo2':       spo2,
                'pefr':       pefr,
            }
        return {
            'categoria':  'asma_crise_leve_moderada',
            'gravidade':  'leve_moderada',
            'tipo':       'asma',
            'spo2':       spo2,
            'pefr':       pefr,
        }

    # ── ROTINA / CONTROLE ────────────────────────────────────────────────────
    n_crit, criterios = _avaliar_controle(dados)
    exacerbacao_ano   = dados.get('exacerbacao_ultimo_ano', False)

    if n_crit == 0 and not exacerbacao_ano:
        controle  = 'controlada'
        categoria = 'asma_controlada'
    elif n_crit <= 2 and not exacerbacao_ano:
        controle  = 'parcialmente_controlada'
        categoria = 'asma_parcialmente_ctrl'
    else:
        controle  = 'nao_controlada'
        categoria = 'asma_nao_controlada'

    step_atual = dados.get('step_atual', 2)
    novo_step, acao_step, info_step = _recomendar_step(step_atual, controle)

    return {
        'categoria':        categoria,
        'controle':         controle,
        'criterios':        criterios,
        'exacerbacao_ano':  exacerbacao_ano,
        'step_atual':       step_atual,
        'step_recomendado': novo_step,
        'acao_step':        acao_step,
        'info_step':        info_step,
        'eosinofilos':      dados.get('eosinofilos'),
        'tecnica_ok':       dados.get('tecnica_inalacao_correta', True),
        'adesao_ok':        dados.get('adesao_medicacao', True),
        'tipo':             'asma',
    }
