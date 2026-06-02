# modules/raciocinio/febre/engine_febre.py
# Motor de raciocínio clínico — Febre sem Foco
#
# Escopo: ADULTO (≥ 18 anos) imunocompetente, ambulatório
# Pediátrico (< 18a) e neutropênico grave → protocolo separado / PS imediato
#
# Sequência de decisão:
#   1. Red flags / emergência → PS imediato
#   2. Foco localizável → redirecionar módulo específico
#   3. Duração < 7 dias, sem alarme → febre_aguda_viral
#   4. Duração < 7 dias, com fator de atenção → febre_aguda_investigar
#   5. 7–21 dias → febre_prolongada
#   6. ≥ 21 dias + ≥ 38.3°C → febre_fuo (Febre de Origem Obscura)
#
# Categorias únicas:
#   febre_emergencia | febre_com_foco
#   febre_aguda_viral | febre_aguda_investigar
#   febre_prolongada | febre_fuo


# =============================================================================
# STEP 1 — RED FLAGS / EMERGÊNCIA
# =============================================================================

def _avaliar_emergencia(dados):
    flags = []

    if dados.get('peticuias_purpura'):
        flags.append({
            'achado': 'Petéquias / púrpura',
            'acao': 'Meningococcemia ou vasculite sistêmica — PS imediato; ceftriaxona IM antes do transporte se demora > 30 min',
        })
    if dados.get('rigidez_nuca'):
        flags.append({
            'achado': 'Rigidez de nuca',
            'acao': 'Meningite — SAMU / PS imediato; ceftriaxona + vancomicina + dexametasona IV',
        })
    if dados.get('hipotensao'):
        flags.append({
            'achado': 'Hipotensão (PA sistólica < 90 mmHg)',
            'acao': 'Sepse — PS imediato; acesso venoso + cristaloide + hemoculturas + ATB precoce',
        })
    if dados.get('taquicardia_fc_120'):
        flags.append({
            'achado': 'Taquicardia (FC ≥ 120 bpm) em repouso',
            'acao': 'Provável sepse ou instabilidade — PS urgente',
        })
    if dados.get('alt_consciencia'):
        flags.append({
            'achado': 'Alteração de consciência',
            'acao': 'Encefalopatia / sepse — SAMU / PS imediato',
        })
    if dados.get('aparencia_toxica'):
        flags.append({
            'achado': 'Aparência tóxica (impressão clínica de gravidade)',
            'acao': 'PS urgente — não manejar ambulatorialmente',
        })
    if dados.get('imunossupressao_grave'):
        flags.append({
            'achado': 'Imunossupressão grave (HIV avançado, quimioterapia, transplante, biológico)',
            'acao': 'Neutropênico febril ou equivalente — PS urgente; ATB empírico amplo espectro IV',
        })
    if dados.get('asplenia'):
        flags.append({
            'achado': 'Asplenia (esplenectomia ou anemia falciforme)',
            'acao': 'Sepse fulminante por encapsulados — PS urgente; ceftriaxona IM antes do transporte',
        })
    if dados.get('neutropenia'):
        flags.append({
            'achado': 'Neutropenia conhecida (ANC < 500)',
            'acao': 'Neutropênico febril — PS urgente; hemoculturas + ATB IV empírico imediato',
        })

    return flags


# =============================================================================
# STEP 2 — FOCO LOCALIZÁVEL
# =============================================================================

def _identificar_foco(dados):
    """Retorna dict com descrição e módulo sugerido, ou None."""
    exantema_tipo = dados.get('exantema_tipo', '')

    if dados.get('foco_faringeo'):
        return {
            'descricao':       'Sintomas faringeais (odinofagia, adenomegalia)',
            'modulo':          'ivas',
            'keyword_entrada': 'dor de garganta',
        }
    if dados.get('foco_respiratorio'):
        return {
            'descricao':       'Sintomas respiratórios (tosse, dispneia)',
            'modulo':          'tosse',
            'keyword_entrada': 'tosse',
        }
    if dados.get('foco_urinario'):
        return {
            'descricao':       'Sintomas urinários (disúria, polaciúria, dor lombar/flanco)',
            'modulo':          'urinario',
            'keyword_entrada': 'disúria',
        }
    if dados.get('foco_gi'):
        return {
            'descricao':       'Sintomas gastrointestinais (diarreia, dor abdominal)',
            'modulo':          'diarreia',
            'keyword_entrada': 'diarreia',
        }
    if dados.get('exantema') and dados.get('viagem_area_endemica'):
        return {
            'descricao':       'Exantema febril + viagem a área endêmica → suspeita arboviral',
            'modulo':          'arboviroses',
            'keyword_entrada': 'dengue',
        }
    if dados.get('exantema') and exantema_tipo == 'eritema_migrans':
        return {
            'descricao':       'Eritema migrans (alvo) → suspeita de Doença de Lyme',
            'modulo':          None,
            'keyword_entrada': None,
        }
    if dados.get('foco_pele_partes_moles'):
        return {
            'descricao':       'Infecção de pele / partes moles (celulite, abscesso)',
            'modulo':          None,
            'keyword_entrada': None,
        }
    return None


# =============================================================================
# STEP 3/4 — FEBRE AGUDA — fatores que indicam investigação
# =============================================================================

_FATORES_INVESTIGAR = [
    ('calafrio_rigor',          'Calafrio com rigor (tremor intenso)'),
    ('sudorese_noturna',        'Sudorese noturna'),
    ('dm',                      'Diabetes mellitus'),
    ('drc',                     'Doença renal crônica'),
    ('icc',                     'Insuficiência cardíaca'),
    ('cirrose',                 'Cirrose hepática'),
    ('internacao_recente_30d',  'Internação nos últimos 30 dias'),
    ('contato_animal',          'Contato com animal (leptospirose, brucelose)'),
    ('picada_carrapato_inseto', 'Picada de carrapato / inseto (riquetsiose)'),
    ('viagem_area_endemica',    'Viagem a área endêmica (malária, febre tifoide)'),
    ('artralgia_artrite',       'Artralgia / artrite'),
    ('contato_tb',              'Contato com tuberculose'),
    ('uso_atb_recente',         'Uso recente de ATB (selecionar resistentes)'),
]


def _tem_fator_investigar(dados, temp):
    """Retorna lista de fatores presentes que justificam investigação laboratorial."""
    fatores = []
    if temp >= 39.5:
        fatores.append('Temperatura ≥ 39,5°C')
    for chave, descr in _FATORES_INVESTIGAR:
        if dados.get(chave):
            fatores.append(descr)
    return fatores


# =============================================================================
# PONTO DE ENTRADA
# =============================================================================

def _enriquecer_febre(resultado, dados):
    """Pente fino — alertas (stewardship/neutropenia) + antitérmico/ATB estruturado."""
    cat = resultado.get('categoria', '')
    alertas, rx = [], []
    try:
        idade = int(dados.get('idade', 0) or 0)
    except (ValueError, TypeError):
        idade = 0

    # ── Antitérmico (sintomático) — categorias ambulatoriais ─────────────────
    if cat in ('febre_aguda_viral', 'febre_com_foco', 'febre_aguda_investigar'):
        rx.append({
            'linha': 'Sintomático — antitérmico/analgésico',
            'medicamento': 'Dipirona',
            'prescricoes': [{'quantidade': '1 frasco/20 cp', 'unidade': '500 mg/mL ou 1 g',
                             'posologia': '1 g VO até 6/6h se T > 38°C ou desconforto (máx 4 g/dia)'}],
            'nota': 'Alternativa: Paracetamol 500–1000 mg 6/6h (máx 4 g/dia; preferir se discrasia). '
                    'EVITAR AAS em adulto febril por virose (síndrome de Reye). Hidratação 2–3 L/dia.',
        })

    # ── Stewardship — febre sem foco no imunocompetente ──────────────────────
    if cat in ('febre_aguda_viral', 'febre_aguda_investigar'):
        alertas.append(
            '⚠️ STEWARDSHIP: febre AGUDA sem foco no imunocompetente é majoritariamente VIRAL. '
            'NÃO prescrever antibiótico empírico — só mascara o diagnóstico, aumenta resistência e efeitos adversos. '
            'Reavaliar em 48–72h; investigar/tratar conforme o foco que surgir.')

    # ── Neutropenia febril / imunossupressão / asplenia — ATB em < 1h ────────
    if dados.get('neutropenia') or dados.get('imunossupressao_grave') or dados.get('asplenia'):
        alertas.append(
            '🔴 NEUTROPENIA FEBRIL / IMUNOSSUPRESSÃO: emergência infecciosa. Hemoculturas (2 sítios) + '
            'ATB IV de amplo espectro em < 1 HORA — NÃO aguardar resultados. Lactato + foco clínico.')
        rx.append({
            'linha': 'ATB empírico imediato (neutropenia febril)',
            'medicamento': 'Cefepima',
            'prescricoes': [{'quantidade': '—', 'unidade': '2 g',
                             'posologia': '2 g IV de 8/8h — primeira dose AGORA (< 1h)'}],
            'nota': 'Alternativa: Piperacilina-tazobactam 4,5 g IV 6/6h. Associar vancomicina se '
                    'suspeita de cateter/pele/MRSA ou instabilidade. Encaminhar PS/hemato urgente.',
        })

    if alertas:
        resultado['alertas_seguranca'] = alertas
    if rx:
        resultado['prescricoes_estruturadas'] = rx
    return resultado


def interpretar_febre(dados):
    return _enriquecer_febre(_interpretar_febre_core(dados), dados)


def _interpretar_febre_core(dados):
    dias = dados.get('dias_febre', 1)
    temp = dados.get('temperatura_max', 38.0)

    # ── 1. Emergência ────────────────────────────────────────────────
    flags = _avaliar_emergencia(dados)
    if flags:
        return {
            'categoria':  'febre_emergencia',
            'red_flags':  flags,
            'dias':       dias,
            'temperatura': temp,
        }

    # ── 2. Foco localizável ──────────────────────────────────────────
    foco = _identificar_foco(dados)
    if foco:
        return {
            'categoria':       'febre_com_foco',
            'foco':            foco,
            'dias':            dias,
            'temperatura':     temp,
        }

    # ── 3/4. Febre aguda (< 7 dias) ─────────────────────────────────
    if dias < 7:
        fatores = _tem_fator_investigar(dados, temp)
        if fatores:
            return {
                'categoria':       'febre_aguda_investigar',
                'fatores_atencao': fatores,
                'dias':            dias,
                'temperatura':     temp,
                'labs_disponiveis': dados.get('labs_disponiveis', False),
                'labs':            _resumir_labs(dados),
            }
        return {
            'categoria':   'febre_aguda_viral',
            'dias':        dias,
            'temperatura': temp,
        }

    # ── 5. Febre prolongada (7–21 dias) ─────────────────────────────
    if dias < 21:
        return {
            'categoria':       'febre_prolongada',
            'dias':            dias,
            'temperatura':     temp,
            'contexto_epi':    _resumir_epi(dados),
            'labs_disponiveis': dados.get('labs_disponiveis', False),
            'labs':            _resumir_labs(dados),
        }

    # ── 6. FUO (≥ 21 dias + ≥ 38.3°C) ──────────────────────────────
    return {
        'categoria':       'febre_fuo',
        'dias':            dias,
        'temperatura':     temp,
        'contexto_epi':    _resumir_epi(dados),
        'labs_disponiveis': dados.get('labs_disponiveis', False),
        'labs':            _resumir_labs(dados),
    }


# =============================================================================
# HELPERS
# =============================================================================

def _resumir_labs(dados):
    """Extrai valores laboratoriais disponíveis em dict limpo."""
    if not dados.get('labs_disponiveis'):
        return {}
    lab = {}
    if dados.get('leucocitos') is not None:
        lab['leucocitos'] = dados['leucocitos']
    if dados.get('neutrofilos_abs') is not None:
        lab['neutrofilos_abs'] = dados['neutrofilos_abs']
    if dados.get('pcr_mgL') is not None:
        lab['pcr_mgL'] = dados['pcr_mgL']
    if dados.get('vhs') is not None:
        lab['vhs'] = dados['vhs']
    if dados.get('hemoculturas_feitas'):
        lab['hemoculturas_feitas'] = True
    return lab


def _resumir_epi(dados):
    """Lista de contextos epidemiológicos relevantes."""
    epi = []
    if dados.get('viagem_area_endemica'):
        destino = dados.get('destino_viagem', 'área endêmica')
        epi.append(f'Viagem: {destino}')
    if dados.get('contato_animal'):
        epi.append('Contato com animal')
    if dados.get('picada_carrapato_inseto'):
        epi.append('Picada de carrapato/inseto')
    if dados.get('internacao_recente_30d'):
        epi.append('Internação < 30 dias')
    if dados.get('contato_tb'):
        epi.append('Contato com TB')
    if dados.get('sudorese_noturna'):
        epi.append('Sudorese noturna')
    return epi
