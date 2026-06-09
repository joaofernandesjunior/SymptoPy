# modules/raciocinio/ictericia/engine_ictericia.py
# Motor de raciocínio clínico — Icterícia
#
# Baseado em: AASLD, EASL, ACG Guidelines
# Escopo: adulto ambulatorial
#
# Categorias:
#   ictericia_emergencia         — colangite/IHA/malignidade com alarme → PS
#   ictericia_gilbert            — bilirrubina indireta isolada + enzimas normais
#   ictericia_hemolitica         — pré-hepática: hemólise
#   ictericia_hepatocelular      — AST/ALT predominante → workup hepatite
#   ictericia_colestatica_obs    — ALP/GGT predominante + ductos dilatados → ERCP
#   ictericia_colestatica_intra  — ALP/GGT predominante + ductos normais → PBC/PSC/DILI


# =============================================================================
# STEP 1 — RED FLAGS / EMERGÊNCIA
# =============================================================================

def _avaliar_emergencia(dados):
    flags = []

    # Tríade de Charcot (colangite)
    if dados.get('febre') and dados.get('dor_hcd') and dados.get('ictericia'):
        flags.append({
            'achado': 'Tríade de Charcot (febre + dor HCD + icterícia) — colangite aguda',
            'acao':   'PS imediato — ATB IV + descompressão biliar urgente',
        })
    # Pêntade de Reynolds (colangite grave)
    if dados.get('hipotensao') or dados.get('alt_consciencia'):
        flags.append({
            'achado': 'Pêntade de Reynolds — colangite grave com choque / encefalopatia',
            'acao':   'PS imediato — UTI + CPRE de emergência',
        })
    # Insuficiência hepática aguda
    if dados.get('inr_maior_1_5') and dados.get('encefalopatia_hepatica'):
        flags.append({
            'achado': 'IHA — INR > 1,5 + encefalopatia hepática',
            'acao':   'PS imediato — hepatologia urgente + avaliação para transplante',
        })
    # Malignidade com alarme
    if dados.get('perda_peso_involuntaria') and dados.get('ictericia'):
        flags.append({
            'achado': 'Icterícia + perda de peso involuntária — malignidade a excluir',
            'acao':   'Imagem urgente (TC abdome + CA 19-9 + CEA) + encaminhamento oncologia',
        })
    return flags


# =============================================================================
# STEP 2 — PADRÃO BIOQUÍMICO
# =============================================================================

def _padrao_bioquimico(dados):
    """Classifica padrão enzimático baseado nos valores disponíveis."""
    alt = dados.get('alt_u_l', 0) or 0
    ast = dados.get('ast_u_l', 0) or 0
    alp = dados.get('alp_u_l', 0) or 0
    ggt = dados.get('ggt_u_l', 0) or 0
    bili_dir = dados.get('bilirrubina_direta', 0) or 0
    bili_ind = dados.get('bilirrubina_indireta', 0) or 0

    # Se labs não disponíveis — usar padrão sintomático
    if not any([alt, ast, alp, ggt, bili_dir, bili_ind]):
        return _padrao_sintomatic(dados)

    # Bilirrubina indireta predominante → pré-hepático
    if bili_ind > 0 and bili_dir > 0:
        if bili_ind > bili_dir * 2:
            return 'pre_hepatica'

    transaminases = max(alt, ast)
    colestaticas   = max(alp, ggt)

    # Sem elevação de enzimas → Gilbert provável (se indireta isolada e enzimas normais)
    if transaminases == 0 and colestaticas == 0:
        return 'gilbert_suspeita'

    if colestaticas > transaminases * 2 or (alp > 3 * 40 and alt < 3 * 40):
        return 'colestatica'
    if transaminases > 0:
        return 'hepatocelular'

    return 'indeterminado'


def _padrao_sintomatic(dados):
    """Padrão baseado em clínica quando labs ausentes."""
    if dados.get('ictericia_flutuante') and dados.get('colica_biliar'):
        return 'colestatica'
    if dados.get('hepatite_viral_suspeita') or dados.get('uso_hepatotoxicos'):
        return 'hepatocelular'
    return 'indeterminado'


# =============================================================================
# CAUSAS DE HEPATITE (WORKUP)
# =============================================================================

def _causas_hepatite(dados):
    """Lista de hipóteses etiológicas para padrão hepatocelular."""
    causas = []
    if dados.get('uso_alcool_excessivo'):
        causas.append('hepatite alcoólica (AST/ALT > 2:1)')
    if dados.get('medicamento_hepatotoxico') or dados.get('suplem_herbal'):
        causas.append('DILI — drug-induced liver injury')
    if dados.get('hepatite_b_hbsag') or dados.get('contato_hepatite_b'):
        causas.append('hepatite B')
    if dados.get('hepatite_c_suspeita'):
        causas.append('hepatite C')
    if dados.get('hepatite_a_suspeita') or dados.get('viagem_area_endemica'):
        causas.append('hepatite A')
    if dados.get('doenca_autoimune_conhecida'):
        causas.append('hepatite autoimune')
    if dados.get('steatose_fatores_risco'):
        causas.append('MASLD / doença hepática gordurosa')
    if not causas:
        causas.append('etiologia a investigar (viral + autoimune + farmacológica)')
    return causas


# =============================================================================
# PONTO DE ENTRADA
# =============================================================================

def _interpretar_ictericia_core(dados):
    # ── 1. Emergência ────────────────────────────────────────────────────────
    flags = _avaliar_emergencia(dados)
    if flags:
        return {
            'categoria': 'ictericia_emergencia',
            'red_flags': flags,
            'tipo':      'ictericia',
        }

    # ── 2. Padrão bioquímico ─────────────────────────────────────────────────
    padrao = _padrao_bioquimico(dados)

    # ── 3. Categoria ─────────────────────────────────────────────────────────
    if padrao == 'gilbert_suspeita' or dados.get('gilbert_previamente_diagnosticado'):
        return {
            'categoria': 'ictericia_gilbert',
            'tipo':      'ictericia',
        }

    if padrao == 'pre_hepatica':
        return {
            'categoria': 'ictericia_hemolitica',
            'tipo':      'ictericia',
        }

    if padrao == 'hepatocelular':
        causas = _causas_hepatite(dados)
        return {
            'categoria': 'ictericia_hepatocelular',
            'causas':    causas,
            'tipo':      'ictericia',
        }

    if padrao == 'colestatica':
        ductos_dilatados = dados.get('ductos_dilatados_us')
        if ductos_dilatados is True:
            return {
                'categoria': 'ictericia_colestatica_obs',
                'tipo':      'ictericia',
            }
        if ductos_dilatados is False:
            # Intrahepática: PBC, PSC, DILI colestático
            causa_intra = []
            if dados.get('ama_positivo'):
                causa_intra.append('Colangite biliar primária (CBP/PBC) — AMA positivo')
            if dados.get('dii_conhecida'):
                causa_intra.append('Colangite esclerosante primária (CEP) — associada a DII')
            if dados.get('medicamento_colestatico'):
                causa_intra.append('Colestase medicamentosa')
            if not causa_intra:
                causa_intra.append('Investigar PBC/CEP/DILI colestático')
            return {
                'categoria':   'ictericia_colestatica_intra',
                'causas':      causa_intra,
                'tipo':        'ictericia',
            }
        # US não realizado ainda
        return {
            'categoria': 'ictericia_colestatica_obs',  # default → pedir US primeiro
            'us_pendente': True,
            'tipo':       'ictericia',
        }

    # Indeterminado — pedir labs básicos primeiro
    return {
        'categoria': 'ictericia_hepatocelular',
        'causas':    _causas_hepatite(dados),
        'tipo':      'ictericia',
    }


# =============================================================================
# PENTE FINO — alertas de segurança transversais
# =============================================================================

def _enriquecer_ictericia(resultado: dict, dados: dict) -> dict:
    """Adiciona alertas_seguranca ao resultado (renderizados no topo do #Plano)."""
    alertas = []
    cat = resultado.get('categoria', '')

    # Emergência: colangite/IHA → nunca manejar ambulatorialmente
    if cat == 'ictericia_emergencia':
        alertas.append(
            '🔴 EMERGÊNCIA — NÃO manejar ambulatorialmente. '
            'Tríade de Charcot / Pêntade de Reynolds / IHA exigem PS + UTI'
        )

    # IHA: paracetamol frequente → N-acetilcisteína se < 24h
    if dados.get('inr_maior_1_5') and dados.get('encefalopatia_hepatica'):
        if dados.get('medicamento_hepatotoxico'):
            alertas.append(
                '⚠️ IHA + hepatotóxico: considerar N-acetilcisteína IV se paracetamol '
                '(eficaz em até 24h). Descontinuar TODOS os hepatotóxicos imediatamente'
            )

    # Hepatite B: não usar AINE (hepatotóxico adicional)
    if cat == 'ictericia_hepatocelular' and (
        dados.get('hepatite_b_hbsag') or dados.get('contato_hepatite_b')
    ):
        alertas.append(
            '⚠️ Hepatite B suspeita: VETO paracetamol em doses altas e AINE — '
            'hepatotoxicidade adicional. Teste HBsAg + anti-HBs + HBeAg urgente'
        )

    # Icterícia obstrutiva: coagulopatia possível → cuidado com procedimentos
    if cat == 'ictericia_colestatica_obs':
        alertas.append(
            '⚠️ Colestase obstrutiva: colher coagulograma antes de qualquer procedimento — '
            'deficiência de vit K pode causar coagulopatia. Vitamina K 10 mg SC se INR > 1,5'
        )

    # Malignidade: não adiar encaminhamento
    if any('malignidade' in str(f.get('achado', '')) for f in resultado.get('red_flags', [])):
        alertas.append(
            '🔴 Malignidade não excluída — TC abdome + CA 19-9 + CEA urgentes. '
            'Encaminhamento oncologia em até 2 semanas'
        )

    resultado['alertas_seguranca'] = alertas
    return resultado


def interpretar_ictericia(dados: dict) -> dict:
    """Ponto de entrada público — core + pente fino."""
    return _enriquecer_ictericia(_interpretar_ictericia_core(dados), dados)
