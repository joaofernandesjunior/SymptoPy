# modules/raciocinio/anorretal/engine_anorretal.py
# Motor de raciocínio clínico — Sangramento Anorretal + Prurido Anal
#
# Baseado em: ACG Guidelines, Goligher classification
# Escopo: adulto ambulatorial
#
# Categorias:
#   anorretal_colonoscopia_urgente — red flags → encaminhar colonoscopia
#   hemorroida_grau_1_2            — graus I-II, conservador/ligadura
#   hemorroida_grau_3              — grau III, ligadura elástica
#   hemorroida_grau_4              — grau IV, cirurgia
#   hemorroida_trombosada          — trombosada externa aguda
#   fissura_anal                   — aguda ou crônica
#   prurido_anal                   — prurido sem sangramento significativo


# =============================================================================
# STEP 1 — RED FLAGS (→ colonoscopia / encaminhamento)
# =============================================================================

def _avaliar_red_flags(dados):
    flags = []

    idade = dados.get('idade', 0)
    if idade >= 45 and dados.get('sangramento_novo'):
        flags.append({
            'achado': f'Idade ≥ 45 anos com sangramento retal novo',
            'acao':   'Colonoscopia para exclusão de neoplasia colorretal',
        })
    if dados.get('sangue_misturado_fezes'):
        flags.append({
            'achado': 'Sangue misturado às fezes (não apenas cobrindo ou no papel)',
            'acao':   'Colonoscopia — padrão sugestivo de lesão proximal (não anorretal)',
        })
    if dados.get('perda_peso_involuntaria'):
        flags.append({
            'achado': 'Perda de peso involuntária associada',
            'acao':   'Investigação de neoplasia — colonoscopia + exames sistêmicos',
        })
    if dados.get('mudanca_habito_intestinal_4sem'):
        flags.append({
            'achado': 'Alteração de hábito intestinal por mais de 4 semanas',
            'acao':   'Colonoscopia para exclusão de neoplasia colorretal ou DII',
        })
    if dados.get('historia_familiar_ccr') or dados.get('historia_pessoal_ccr'):
        flags.append({
            'achado': 'História familiar ou pessoal de câncer colorretal',
            'acao':   'Colonoscopia independentemente da queixa atual',
        })
    if dados.get('anemia_ferropriva_confirmada'):
        flags.append({
            'achado': 'Anemia ferropriva confirmada em exame',
            'acao':   'Colonoscopia — perdas ocultas de alto trato ou cólon',
        })
    return flags


# =============================================================================
# STEP 2 — TIPO DE QUEIXA
# =============================================================================

def _identificar_queixa(dados):
    """Retorna 'hemorroida', 'fissura', 'prurido' ou None."""
    if dados.get('sangramento_sem_dor') or dados.get('prolapso_anorretal'):
        return 'hemorroida'
    if dados.get('dor_durante_defecacao') and dados.get('sangramento_no_papel'):
        return 'fissura'
    if dados.get('prurido_perianal') and not dados.get('sangramento_significativo'):
        return 'prurido'
    if dados.get('sangramento_no_papel') or dados.get('sangramento_gotejamento'):
        return 'hemorroida'   # default para sangramento baixo sem dor
    return None


# =============================================================================
# STEP 3 — GRAU DE HEMORROIDA (Goligher)
# =============================================================================

def _grau_hemorroida(dados):
    """Retorna grau I–IV baseado em prolapso e redutibilidade."""
    if dados.get('hemorroida_trombosada_externa'):
        return 'trombosada'
    if dados.get('prolapso_irredutivel'):
        return 'IV'
    if dados.get('prolapso_reducao_manual'):
        return 'III'
    if dados.get('prolapso_reducao_espontanea'):
        return 'II'
    return 'I'   # sem prolapso — sangramento apenas


# =============================================================================
# STEP 4 — FISSURA AGUDA vs. CRÔNICA
# =============================================================================

def _tipo_fissura(dados):
    """'aguda' (< 6-8 semanas) ou 'cronica'."""
    semanas = dados.get('duracao_fissura_semanas', 0) or 0
    if semanas >= 6 or dados.get('fissura_cronica_confirmada'):
        return 'cronica'
    return 'aguda'


# =============================================================================
# STEP 5 — CAUSA DO PRURIDO
# =============================================================================

_CAUSAS_PRURIDO = [
    ('oxiuros_suspeita',     'Oxiuros (Enterobius vermicularis)'),
    ('candida_perianal',     'Candidíase perianal'),
    ('dermatite_contato',    'Dermatite de contato / irritativa'),
    ('psoríase_perianal',    'Psoríase perianal'),
    ('lichen_escleroso',     'Líquen escleroso'),
    ('incontinencia_fecal',  'Incontinência fecal / escape fecal'),
    ('gatilho_dietetico',    'Gatilho dietético (café, chocolate, condimentados)'),
    ('medicamento_causador', 'Medicamento (tetraciclina, colchicina, quinidina)'),
]


def _causa_prurido(dados):
    causas = []
    for chave, descr in _CAUSAS_PRURIDO:
        if dados.get(chave):
            causas.append(descr)
    return causas if causas else ['primário / idiopático']


# =============================================================================
# PONTO DE ENTRADA
# =============================================================================

def _interpretar_anorretal_core(dados):
    # ── 1. Red flags ─────────────────────────────────────────────────────────
    flags = _avaliar_red_flags(dados)
    if flags:
        return {
            'categoria': 'anorretal_colonoscopia_urgente',
            'red_flags': flags,
            'tipo':      'anorretal',
        }

    # ── 2. Queixa principal ──────────────────────────────────────────────────
    queixa = _identificar_queixa(dados)

    if queixa == 'hemorroida':
        grau = _grau_hemorroida(dados)
        if grau == 'trombosada':
            horas = dados.get('horas_desde_trombose', 999)
            return {
                'categoria':    'hemorroida_trombosada',
                'horas':        horas,
                'abordagem':    'incisao_drenagem' if horas <= 72 else 'conservador',
                'tipo':         'anorretal',
            }
        cat_map = {'I': 'hemorroida_grau_1_2', 'II': 'hemorroida_grau_1_2',
                   'III': 'hemorroida_grau_3',  'IV': 'hemorroida_grau_4'}
        return {
            'categoria': cat_map.get(grau, 'hemorroida_grau_1_2'),
            'grau':      grau,
            'tipo':      'anorretal',
        }

    if queixa == 'fissura':
        tipo_f = _tipo_fissura(dados)
        return {
            'categoria':   'fissura_anal',
            'tipo_fissura': tipo_f,
            'tipo':        'anorretal',
        }

    if queixa == 'prurido':
        causas = _causa_prurido(dados)
        return {
            'categoria': 'prurido_anal',
            'causas':    causas,
            'tipo':      'anorretal',
        }

    # Sangramento inespecífico sem classificação clara
    return {
        'categoria': 'hemorroida_grau_1_2',
        'grau':      'I',
        'tipo':      'anorretal',
    }


# =============================================================================
# PENTE FINO — alertas de segurança transversais
# =============================================================================

def _enriquecer_anorretal(resultado: dict, dados: dict) -> dict:
    """Adiciona alertas_seguranca ao resultado (renderizados no topo do #Plano)."""
    alertas = []
    cat = resultado.get('categoria', '')

    # Colonoscopia: não adiar em ≥ 45 anos com sangramento novo
    if cat == 'anorretal_colonoscopia_urgente':
        alertas.append(
            '⚠️ Red flag presente — NÃO assumir hemorroida sem colonoscopia. '
            'CCR pode coexistir com doença hemorroidária'
        )

    # Hemorroida grau IV: risco de estrangulamento → cirurgia urgente se necrose
    if cat == 'hemorroida_grau_4':
        alertas.append(
            '⚠️ Hemorroida grau IV — encaminhar cirurgia. '
            'Se prolapso irredutível + dor intensa + necrose: PS urgente '
            '(estrangulamento hemorroidário)'
        )

    # Trombose < 72h: janela para incisão
    if cat == 'hemorroida_trombosada':
        horas = resultado.get('horas', 999)
        if horas <= 72:
            alertas.append(
                f'⚠️ Trombose há {horas}h — ainda dentro da janela (≤ 72h). '
                'Incisão e drenagem sob anestesia local alivia dor rapidamente. '
                'Após 72h: tratamento conservador (sitz bath, fibras, analgesia)'
            )
        else:
            alertas.append(
                f'⚠️ Trombose há {horas}h — fora da janela cirúrgica (> 72h). '
                'Tratamento conservador: sitz bath, fibras, analgesia, resolução em 7–10d'
            )

    # Fissura crônica + primeiro tratamento: não cirurgia antes de tópicos
    if cat == 'fissura_anal':
        tipo = resultado.get('tipo_fissura', '')
        if tipo == 'cronica':
            alertas.append(
                '⚠️ Fissura crônica: tentar nitroglicerina 0,2% ou diltiazem 2% tópico '
                'por 6–8 semanas ANTES de indicar cirurgia (esfincterotomia lateral interna)'
            )

    resultado['alertas_seguranca'] = alertas
    return resultado


def interpretar_anorretal(dados: dict) -> dict:
    """Ponto de entrada público — core + pente fino."""
    return _enriquecer_anorretal(_interpretar_anorretal_core(dados), dados)
