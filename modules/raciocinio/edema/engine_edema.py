# modules/raciocinio/edema/engine_edema.py
# Motor de raciocínio clínico — Edema de Membros Inferiores
#
# Baseado em: AHA/ESC HF guidelines, ACC/AHA Peripheral Vascular guidelines
# Escopo: adulto ambulatorial
#
# Categorias:
#   edema_dvt_alto_risco       — Wells ≥2 → eco urgente
#   edema_dvt_baixo_risco      — Wells ≤1 → D-dímero
#   edema_celulite             — infecção de pele (unilateral + eritema + calor)
#   edema_cardiaco             — bilateral + sinais cardíacos + BNP
#   edema_renal_nefrotico      — bilateral + proteinúria + hipoalbuminemia
#   edema_hepatico             — bilateral + cirrose / hipoalbuminemia hepática
#   edema_hipotireoidismo      — TSH elevado / mixedema pré-tibial
#   edema_farmacologico        — medicamento causador identificado
#   edema_venoso_cronico       — IVC — CEAP C3+
#   edema_linfedema            — linfedema primário ou secundário
#   edema_investigar           — bilateral sem causa aparente → workup sistêmico


# =============================================================================
# WELLS SCORE — TVP
# =============================================================================

_WELLS_ITEMS = [
    ('cancer_ativo',               1, 'Câncer ativo em tratamento'),
    ('paralisia_imobilizacao',     1, 'Paralisia / imobilização de MMII'),
    ('repouso_cirurgia_recente',   1, 'Repouso > 3 dias ou cirurgia grande < 12 semanas'),
    ('dor_trajeto_venoso',         1, 'Dor localizada no trajeto venoso profundo'),
    ('edema_toda_perna',           1, 'Edema de toda a perna'),
    ('edema_panturrilha_assim',    1, 'Edema assimétrico de panturrilha > 3 cm'),
    ('edema_cacifo_limitado',      1, 'Edema depressível limitado ao membro sintomático'),
    ('veias_colaterais',           1, 'Veias superficiais colaterais (não varicosas)'),
    ('tvp_previa',                 1, 'TVP prévia documentada'),
    ('diagnostico_alternativo',   -2, 'Diagnóstico alternativo tão ou mais provável'),
]


def _calcular_wells(dados):
    score = 0
    itens = []
    for chave, pts, descr in _WELLS_ITEMS:
        if dados.get(chave):
            score += pts
            itens.append(f'{descr} ({pts:+d})')
    return score, itens


# =============================================================================
# MEDICAMENTOS CAUSADORES DE EDEMA
# =============================================================================

_FARMACOS_EDEMA = [
    ('usa_bcc',          'Bloqueador de canal de cálcio (amlodipina, anlodipina)'),
    ('usa_aine',         'AINE (retenção de sódio)'),
    ('usa_corticoide',   'Corticoide sistêmico'),
    ('usa_gabapentina',  'Gabapentina / pregabalina'),
    ('usa_tiazolidiona', 'Tiazolidinediona (pioglitazona)'),
    ('usa_hormonio',     'Terapia hormonal (estrogênio, testosterona)'),
]


def _farmaco_causador(dados):
    causas = []
    for chave, descr in _FARMACOS_EDEMA:
        if dados.get(chave):
            causas.append(descr)
    return causas


# =============================================================================
# HELPERS DE PRESCRIÇÃO
# =============================================================================

def _rx(linha, medicamento, prescricoes, nota=None):
    return {'linha': linha, 'medicamento': medicamento,
            'prescricoes': prescricoes, 'nota': nota}


def _p(q, u, pos):
    return {'quantidade': q, 'unidade': u, 'posologia': pos}


# =============================================================================
# PENTE FINO CLÍNICO — alertas de segurança + prescrições estruturadas
# =============================================================================

def _enriquecer_edema(resultado, dados):
    cat = resultado.get('categoria', '')
    alertas, rx = [], []
    try:
        idade = int(dados.get('idade', 0) or 0)
    except (ValueError, TypeError):
        idade = 0

    # ── Alertas transversais ─────────────────────────────────────────────────
    # AINE como causa de edema no idoso (Beers — nefrotóxico)
    if dados.get('usa_aine') and idade >= 65:
        alertas.append(
            '⚠️ ALERTA BEERS (≥ 65 anos): AINE é causa frequente de edema e é nefrotóxico no idoso — '
            'suspender e trocar por paracetamol. Reavaliar o edema após 1–2 semanas sem AINE.')

    # ── Por categoria: alertas + Rx estruturada ──────────────────────────────
    if cat == 'edema_dvt_alto_risco':
        alertas.append(
            '🔴 TVP proximal tem risco de EMBOLIA PULMONAR. Se dispneia súbita, dor torácica '
            'pleurítica, taquicardia ou síncope → investigar TEP (AngioTC de tórax) IMEDIATAMENTE.')
        rx.append(_rx('Anticoagulação (após confirmar TVP no ecodoppler)',
                      'Rivaroxabana',
                      [_p('1 caixa', '15 mg', '1 cp 12/12h × 21 dias → depois 20 mg 1×/dia')],
                      nota='Iniciar só após confirmação. Ajustar/evitar se ClCr < 30 mL/min '
                           '(preferir HNF/HBPM). Alternativa: apixabana 10 mg 12/12h × 7d → 5 mg 12/12h.'))

    elif cat == 'edema_celulite':
        rx.append(_rx('ATB — celulite de MMII',
                      'Amoxicilina-Clavulanato',
                      [_p('14 comp.', '875/125 mg', '1 cp 12/12h × 7–10 dias, com alimento')],
                      nota='Alergia/MRSA: cefalexina 500 mg 6/6h ou SMX-TMP. Demarcar borda + elevar membro.'))

    elif cat == 'edema_cardiaco':
        rx.append(_rx('Diurético de alça',
                      'Furosemida',
                      [_p('1 caixa', '40 mg', '1 cp pela manhã (ajustar pela resposta/peso)')],
                      nota='Meta -0,5 a 1 kg/dia. Monitorar K+ e função renal.'))
        rx.append(_rx('Antagonista mineralocorticoide (ICFEr)',
                      'Espironolactona',
                      [_p('1 caixa', '25 mg', '1 cp/dia')],
                      nota='Vigiar hipercalemia, sobretudo se DRC/IECA-BRA associados.'))

    elif cat == 'edema_hepatico':
        rx.append(_rx('Diuréticos (razão 100:40 — cirrose)',
                      'Espironolactona + Furosemida',
                      [_p('—', '100 mg + 40 mg', 'Espironolactona 100 mg/dia + Furosemida 40 mg/dia')],
                      nota='Restrição de sódio < 2 g/dia. Encaminhar hepatologia.'))

    elif cat == 'edema_hipotireoidismo':
        rx.append(_rx('Reposição hormonal',
                      'Levotiroxina',
                      [_p('1 caixa', '50 mcg', '1 cp/dia em jejum (ajustar por TSH; iniciar 25 mcg se idoso/DCV)')],
                      nota='Reavaliar TSH em 6–8 semanas (alvo 0,5–2,5 mUI/L).'))

    elif cat == 'edema_venoso_cronico':
        rx.append(_rx('Venotônico (adjuvante)',
                      'Diosmina + Hesperidina',
                      [_p('1 caixa', '450/50 mg', '1 cp 12/12h')],
                      nota='Pilar = meia de compressão 20–30 mmHg + elevação. Medir ITB antes se suspeita de DAP.'))

    if alertas:
        resultado['alertas_seguranca'] = alertas
    if rx:
        resultado['prescricoes_estruturadas'] = rx
    return resultado


# =============================================================================
# PONTO DE ENTRADA
# =============================================================================

def interpretar_edema(dados):
    return _enriquecer_edema(_interpretar_edema_core(dados), dados)


def _interpretar_edema_core(dados):
    lateral = dados.get('lateralidade', 'bilateral')   # 'unilateral' | 'bilateral'
    cronico = dados.get('cronico', False)               # True se > 4 semanas

    # ── Unilateral agudo → DVT / celulite ────────────────────────────────────
    if lateral == 'unilateral':
        # Celulite antes de Wells
        if dados.get('eritema_calor_local') and dados.get('porta_entrada_ou_infeccao'):
            return {
                'categoria': 'edema_celulite',
                'tipo':      'edema',
                'lateral':   'unilateral',
            }

        wells, wells_itens = _calcular_wells(dados)
        if wells >= 2:
            return {
                'categoria':   'edema_dvt_alto_risco',
                'wells_score': wells,
                'wells_itens': wells_itens,
                'tipo':        'edema',
                'lateral':     'unilateral',
            }
        return {
            'categoria':   'edema_dvt_baixo_risco',
            'wells_score': wells,
            'wells_itens': wells_itens,
            'tipo':        'edema',
            'lateral':     'unilateral',
        }

    # ── Bilateral → causas sistêmicas ────────────────────────────────────────

    # Farmacológico primeiro (mais fácil de resolver)
    farmacos = _farmaco_causador(dados)
    if farmacos and not dados.get('sinais_sistemicos'):
        return {
            'categoria': 'edema_farmacologico',
            'farmacos':  farmacos,
            'tipo':      'edema',
            'lateral':   'bilateral',
        }

    # Cardíaco
    if dados.get('dispneia_esforco') or dados.get('ortopneia') or dados.get('bnp_elevado'):
        return {
            'categoria':   'edema_cardiaco',
            'bnp_elevado': dados.get('bnp_elevado', False),
            'tipo':        'edema',
            'lateral':     'bilateral',
        }

    # Renal — nefrótico
    if dados.get('proteinuria_pesada') or (
        dados.get('edema_facial') and dados.get('hipoalbuminemia')
    ):
        return {
            'categoria': 'edema_renal_nefrotico',
            'tipo':      'edema',
            'lateral':   'bilateral',
        }

    # Hepático — cirrose
    if dados.get('cirrose_conhecida') or dados.get('ascite') or (
        dados.get('hipoalbuminemia') and dados.get('ictericia')
    ):
        return {
            'categoria': 'edema_hepatico',
            'tipo':      'edema',
            'lateral':   'bilateral',
        }

    # Hipotireoidismo
    if dados.get('mixedema_pretibial') or dados.get('tsh_elevado'):
        return {
            'categoria': 'edema_hipotireoidismo',
            'tsh':       dados.get('tsh_valor'),
            'tipo':      'edema',
            'lateral':   'bilateral',
        }

    # Venoso crônico bilateral (menos comum mas possível)
    if cronico and (dados.get('varizes') or dados.get('hiperpigmentacao_pernas')):
        return {
            'categoria': 'edema_venoso_cronico',
            'tipo':      'edema',
            'lateral':   'bilateral',
        }

    # Linfedema
    if dados.get('edema_nao_depressivel') or dados.get('cirurgia_linfonodos') or dados.get('radioterapia'):
        return {
            'categoria': 'edema_linfedema',
            'causa':     'secundario' if (dados.get('cirurgia_linfonodos') or dados.get('radioterapia')) else 'primario',
            'tipo':      'edema',
            'lateral':   'bilateral',
        }

    # Venoso crônico unilateral apresentado como bilateral
    if dados.get('varizes') or dados.get('hiperpigmentacao_pernas'):
        return {
            'categoria': 'edema_venoso_cronico',
            'tipo':      'edema',
            'lateral':   'bilateral',
        }

    # Investigar — sem causa identificada
    return {
        'categoria': 'edema_investigar',
        'tipo':      'edema',
        'lateral':   lateral,
        'farmacos':  farmacos,
    }
