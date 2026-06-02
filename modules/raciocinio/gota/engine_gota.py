# modules/raciocinio/gota/engine_gota.py
# Motor de raciocínio clínico — Gota / Artrite por Cristais de Urato
#
# Baseado em: EULAR 2016/2022, ACR 2020, Dutch 2010 (Janssens Rule)
# Escopo: adulto ambulatorial
#
# Categorias:
#   gota_artrite_septica_excluir  — PS urgente, artrite séptica a excluir
#   gota_provavel_ataque_agudo    — Dutch ≥ 8, tratar como gota
#   gota_possivel_ataque_agudo    — Dutch 4–7, possível gota / investigar
#   gota_improvavel_ataque_agudo  — Dutch < 4, hipótese alternativa
#   gota_interataque              — período assintomático, avaliar ULT
#   gota_tofacea                  — gota tofácea crônica, ULT mandatório


# =============================================================================
# STEP 1 — RED FLAGS (artrite séptica)
# =============================================================================

def _avaliar_red_flags(dados):
    """Retorna lista de flags que obrigam exclusão de artrite séptica."""
    flags = []

    if dados.get('febre_385'):
        flags.append({
            'achado': 'Febre ≥ 38,5°C com monoartrite aguda',
            'acao':   'Punção articular urgente — excluir artrite séptica; '
                      'cristais e infecção podem coexistir',
        })
    if dados.get('aparencia_toxica'):
        flags.append({
            'achado': 'Aparência tóxica / toxemia sistêmica',
            'acao':   'PS urgente — artrite séptica tem prioridade diagnóstica sobre gota',
        })
    if dados.get('imunossupressao') and dados.get('ataque_atual'):
        flags.append({
            'achado': 'Imunossupressão + artrite aguda',
            'acao':   'Baixo limiar para punção — septe arthritis e gota podem coexistir '
                      'em imunossuprimido',
        })
    return flags


# =============================================================================
# STEP 2 — SCORE DIAGNÓSTICO (Dutch 2010 / Janssens)
# =============================================================================

_DUTCH_ITEMS = [
    ('sexo_masculino',        2.0,  'Sexo masculino'),
    ('ataque_previo',         2.0,  'Ataque articular semelhante prévio'),
    ('inicio_em_1_dia',       0.5,  'Início em menos de 1 dia'),
    ('vermelhidao',           1.0,  'Vermelhidão articular'),
    ('articulacao_mtf1',      2.5,  '1ª articulação metatarsofalangeana (podagra)'),
    ('has_ou_cardiovascular', 1.5,  'HAS ou doença cardiovascular'),
]
_DUTCH_URATO_PESO   = 3.5
_DUTCH_URATO_LIMIAR = 5.88   # mg/dL


def _calcular_dutch(dados):
    """Calcula score de Janssens. Retorna (score: float, itens_positivos: list[str])."""
    score = 0.0
    itens = []

    for chave, peso, descr in _DUTCH_ITEMS:
        if dados.get(chave):
            score += peso
            itens.append(descr)

    urato = dados.get('urato_mgdl')
    if urato is not None and urato > _DUTCH_URATO_LIMIAR:
        score += _DUTCH_URATO_PESO
        itens.append(f'Urato sérico > 5,88 mg/dL (medido: {urato:.1f} mg/dL)')

    return round(score, 1), itens


# =============================================================================
# STEP 3 — FASE CLÍNICA
# =============================================================================

def _identificar_fase(dados):
    """Retorna 'tofacea', 'ataque_agudo' ou 'interataque'."""
    if dados.get('tophi_presentes'):
        return 'tofacea'
    if dados.get('ataque_atual'):
        return 'ataque_agudo'
    return 'interataque'


# =============================================================================
# STEP 4 — CONDUTA ANTI-INFLAMATÓRIA (ataque agudo)
# =============================================================================

def _conduta_aguda(dados):
    """
    Seleciona e ranqueia opções anti-inflamatórias.
    Respeita: AINE trava ≥ 60 anos, eGFR, anticoagulação,
    inibidor CYP3A4/Pgp, ICC, úlcera péptica ativa, DM descontrolado.
    """
    egfr     = dados.get('egfr') or 90.0   # assumir normal se não informado
    idade    = dados.get('idade', 0)
    anticoag = dados.get('anticoagulado', False)
    icc      = dados.get('icc', False)
    dpud     = dados.get('dpud', False)
    dm_desc  = dados.get('dm_descontrolado', False)
    cyp_pgp  = dados.get('inibidor_cyp3a4_pgp', False)
    n_joints = dados.get('n_articulacoes_afetadas', 1) or 1

    opcoes  = []
    alertas = []

    # ── Colchicina ───────────────────────────────────────────────────────────
    if cyp_pgp:
        alertas.append(
            'Colchicina CONTRAINDICADA — inibidor de CYP3A4/P-gp detectado '
            '(claritromicina, ciclosporina, verapamil, etc.) → risco de toxicidade grave'
        )
    elif egfr < 30:
        alertas.append('Colchicina CONTRAINDICADA — eGFR < 30 mL/min')
    elif egfr < 60:
        opcoes.append({
            'agente': 'Colchicina (dose reduzida — eGFR 30–59)',
            'dose':   '0,6 mg VO dose única; repetir após 24h se necessário. '
                      'Manutenção: 0,6 mg 1×/dia até resolução.',
            'obs':    'Monitorar sinais de miotoxicidade (mialgia + CK)',
        })
    else:
        opcoes.append({
            'agente': 'Colchicina',
            'dose':   '1,2 mg VO imediatamente + 0,6 mg após 1h (dose de ataque). '
                      'Manutenção: 0,6 mg 1–2×/dia até resolução (7–10 dias).',
            'obs':    'Iniciar nas primeiras 24–36h para máxima eficácia',
        })

    # ── AINE ────────────────────────────────────────────────────────────────
    aine_contraindicado = (
        egfr < 60 or anticoag or icc or dpud or idade >= 60
    )

    if not aine_contraindicado:
        opcoes.append({
            'agente': 'Naproxeno',
            'dose':   '500 mg VO 12/12h por 5–7 dias.',
            'obs':    'Alt.: ibuprofeno 800 mg 8/8h ou indometacina 50 mg 8/8h',
        })
    else:
        motivos_aine = []
        if idade >= 60:
            motivos_aine.append('≥ 60 anos (risco GI/CV elevado)')
        if egfr < 60:
            motivos_aine.append(f'eGFR {int(egfr)} — AINE nefrotóxico')
        if anticoag:
            motivos_aine.append('anticoagulante em uso')
        if icc:
            motivos_aine.append('insuficiência cardíaca')
        if dpud:
            motivos_aine.append('úlcera péptica ativa')
        if motivos_aine:
            alertas.append('AINE contraindicado: ' + '; '.join(motivos_aine))

    # ── Corticoide ──────────────────────────────────────────────────────────
    if n_joints == 1:
        opcoes.append({
            'agente': 'Triancinolona intra-articular',
            'dose':   '20–40 mg IA dose única (volume ajustado ao tamanho da articulação).',
            'obs':    'Preferência em mono-artrite quando VO contraindicado ou impraticável',
        })

    opcoes.append({
        'agente': 'Prednisona',
        'dose':   '30–40 mg/dia VO por 5–7 dias; reduzir 5 mg/dia após resolução.',
        'obs':    'Alternativa IM: triancinolona 60 mg IM dose única',
    })

    if dm_desc:
        alertas.append(
            'Corticoide sistêmico pode descompensar DM — '
            'preferir triancinolona IA se articulação acessível; monitorar glicemia'
        )

    return {
        'opcoes':  opcoes,
        'alertas': alertas,
        'gelo':    True,   # ACR 2020 recomendação condicional
    }


# =============================================================================
# STEP 5 — ULT (urate-lowering therapy)
# =============================================================================

def _avaliar_ult(dados):
    """Avalia indicação, agente e plano de ULT."""
    tophi         = dados.get('tophi_presentes', False)
    n_ataques_ano = dados.get('n_ataques_ano', 0) or 0
    dano_radio    = dados.get('dano_radiografico', False)
    egfr          = dados.get('egfr') or 90.0
    urato         = dados.get('urato_mgdl')
    urolitiase    = dados.get('urolitiase', False)
    ja_usa_ult    = dados.get('ja_usa_ult', False)
    urato_atual   = dados.get('urato_atual_mgdl')
    hla_risco     = dados.get('origem_alto_risco_hlab5801', False)

    # Indicação (ACR 2020)
    if tophi or n_ataques_ano >= 2 or dano_radio:
        indicacao = 'forte'
    elif egfr < 60 or urolitiase or (urato and urato >= 9.0):
        indicacao = 'condicional'
    else:
        indicacao = 'nenhuma'   # 0–1 ataques/ano sem complicações

    if ja_usa_ult:
        meta_atingida = (urato_atual < 6.0) if urato_atual is not None else None
        return {
            'ja_usa_ult':   True,
            'indicacao':    indicacao,
            'urato_atual':  urato_atual,
            'meta_atingida': meta_atingida,
            'alvo_urato':   '< 6,0 mg/dL',
        }

    # Dose inicial de alopurinol por eGFR
    if egfr >= 60:
        dose_inicio = 100
        freq        = '1×/dia'
    elif egfr >= 30:
        dose_inicio = 50
        freq        = '1×/dia'
    elif egfr >= 15:
        dose_inicio = 50
        freq        = 'a cada 2 dias'
    else:
        dose_inicio = None   # evitar
        freq        = None

    return {
        'ja_usa_ult':   False,
        'indicacao':    indicacao,
        'agente':       'Alopurinol',
        'dose_inicio':  dose_inicio,
        'freq':         freq,
        'titulacao':    'Aumentar 50–100 mg a cada 2–6 semanas até atingir meta',
        'alvo_urato':   '< 6,0 mg/dL',
        'profilaxia':   'Colchicina 0,5–0,6 mg/dia por ≥ 3–6 meses durante todo o ajuste',
        'alerta_hla':   hla_risco,
        'egfr':         egfr,
    }


# =============================================================================
# PONTO DE ENTRADA
# =============================================================================

def interpretar_gota(dados):
    """Motor principal — retorna dict com categoria + conduta estruturada."""

    # ── 1. Red flags ─────────────────────────────────────────────────────────
    flags = _avaliar_red_flags(dados)
    if flags:
        return {
            'categoria':  'gota_artrite_septica_excluir',
            'red_flags':  flags,
            'tipo':       'gota',
        }

    # ── 2. Fase clínica ──────────────────────────────────────────────────────
    fase = _identificar_fase(dados)

    # ── 3. Score diagnóstico ─────────────────────────────────────────────────
    score, score_itens = _calcular_dutch(dados)

    if fase == 'tofacea':
        categoria = 'gota_tofacea'
    elif fase == 'interataque':
        categoria = 'gota_interataque'
    else:   # ataque_agudo
        if score >= 8:
            categoria = 'gota_provavel_ataque_agudo'
        elif score >= 4:
            categoria = 'gota_possivel_ataque_agudo'
        else:
            categoria = 'gota_improvavel_ataque_agudo'

    # ── 4. Conduta ───────────────────────────────────────────────────────────
    conduta_aguda = _conduta_aguda(dados) if fase == 'ataque_agudo' else {}
    ult           = _avaliar_ult(dados)

    return {
        'categoria':     categoria,
        'fase':          fase,
        'score_dutch':   score,
        'score_itens':   score_itens,
        'conduta_aguda': conduta_aguda,
        'ult':           ult,
        'tipo':          'gota',
        # Pass-through
        'tophi_presentes':  dados.get('tophi_presentes', False),
        'n_ataques_ano':    dados.get('n_ataques_ano', 0),
        'urato_mgdl':       dados.get('urato_mgdl'),
        'articulacoes':     dados.get('articulacoes', ''),
        'egfr':             dados.get('egfr'),
        'gota_confirmada':  dados.get('gota_confirmada_previa', False),
    }
