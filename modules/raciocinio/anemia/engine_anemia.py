# modules/raciocinio/anemia/engine_anemia.py
# Motor de interpretação de hemograma e classificação de anemia
#
# Algoritmo baseado em:
#   - WHO 2011 (limiares de anemia)
#   - AFP 2021 (IDA — ferritina ajustada por inflamação)
#   - AFP 2022 (talassemia — eletroforese + índice de Mentzer)
#   - ASH 2023 (hemólise, pancitopenia)
#   - AABB / KDIGO (anemia renal)
#   - Cochrane (ferro oral — dose alternada superior)
#
# Sequência:
#   1. Confirmar anemia e graduar gravidade
#   2. Verificar pancitopenia → encaminhamento urgente
#   3. Classificar por VCM: microcítica / normocítica / macrocítica
#   4. Subclassificar com RDW, reticulócitos, ferritina, exames adicionais
#   5. Situações especiais (ACD vs IDA, deficiência combinada, hemólise, talassemia, renal)


# =============================================================================
# LIMIARES — OMS
# =============================================================================

def _limiar_hb(dados):
    if dados.get('gestante'):
        return 11.0, 'gestante'
    if dados.get('sexo') == 'masculino':
        return 13.0, 'homem adulto'
    return 12.0, 'mulher não gestante'


def _grau_anemia(hb, limiar):
    deficit = limiar - hb
    if hb >= limiar:
        return 'normal', deficit
    if hb >= 10.0:
        return 'leve', deficit
    if hb >= 8.0:
        return 'moderada', deficit
    if hb >= 6.5:
        return 'grave', deficit
    return 'muito_grave', deficit


# =============================================================================
# UTILITÁRIOS
# =============================================================================

def _rpi(dados):
    """Reticulocyte Production Index = retic_corrigido / fator_maturacao."""
    retic = dados.get('retic_pct')
    ht    = dados.get('ht')
    if retic is None or ht is None:
        return None
    ht_normal = 42.0  # valor médio de referência
    retic_corr = (ht / ht_normal) * retic
    if ht >= 36:
        fator = 1.0
    elif ht >= 26:
        fator = 1.5
    elif ht >= 16:
        fator = 2.0
    else:
        fator = 2.5
    return round(retic_corr / fator, 2)


def _mentzer(dados):
    mcv = dados.get('mcv')
    rbc = dados.get('rbc')
    if mcv and rbc and rbc > 0:
        return round(mcv / rbc, 1)
    return None


def _pancitopenia(dados):
    wbc = dados.get('wbc', 99)
    plt = dados.get('plt', 9999)
    return wbc < 4.0 and plt < 150


# =============================================================================
# CLASSIFICAÇÃO MICROCÍTICA (VCM < 80)
# =============================================================================

def _classificar_micro(dados):
    ferritina   = dados.get('ferritina')
    sat_transf  = dados.get('sat_transf')
    rdw         = dados.get('rdw', 0)
    doenca_cr   = dados.get('doenca_cronica', False)
    eletroforese= dados.get('eletroforese_hb', False)
    hba2        = dados.get('hba2_elevada')
    hbf         = dados.get('hbf_elevada')
    rbc         = dados.get('rbc')
    mentzer     = _mentzer(dados)

    # ── Regra 1: ferritina < 30 → IDA clara ──────────────────────────
    if ferritina is not None and ferritina < 30:
        return {
            'diagnostico': 'Anemia Ferropriva (IDA)',
            'categoria': 'anemia_ferropriva',
            'padrao': 'VCM baixo · RDW elevado · Ferritina < 30 ng/mL',
            'exames_confirmatórios': [
                'Investigar causa: sangramento GI (se homem/pós-menopausa), menorragia, má absorção',
                'Sangue oculto nas fezes se sangramento GI suspeito',
            ],
            'tratamento': _rx_ferropriva(),
            'encaminhamento': None,
        }

    # ── Regra 2: inflamação crônica + ferritina < 100 → IDA em doença crônica
    if doenca_cr and ferritina is not None and ferritina < 100:
        return {
            'diagnostico': 'Anemia Ferropriva em contexto de doença crônica',
            'categoria': 'anemia_ferropriva',
            'padrao': 'VCM baixo · Ferritina < 100 ng/mL (limiar ajustado pela inflamação — AFP 2021)',
            'exames_confirmatórios': [
                'Ferro sérico, TIBC, saturação de transferrina',
                'Receptor solúvel de transferrina (sTfR) se disponível',
            ],
            'tratamento': _rx_ferropriva(),
            'encaminhamento': None,
        }

    # ── Regra 3: ferritina 30–99 → checar sat transf ─────────────────
    if ferritina is not None and 30 <= ferritina < 100:
        if sat_transf is not None and sat_transf < 20:
            return {
                'diagnostico': 'Anemia Ferropriva (satTransf < 20%)',
                'categoria': 'anemia_ferropriva',
                'padrao': f'Ferritina {ferritina} ng/mL (intermediária) · Sat. transf. {sat_transf}% < 20%',
                'exames_confirmatórios': [
                    'Confirmar com sTfR se disponível',
                    'Investigar causa da deficiência de ferro',
                ],
                'tratamento': _rx_ferropriva(),
                'encaminhamento': None,
            }
        # Sat transf ≥ 20% ou não disponível — avaliar talassemia / ACD
        if eletroforese:
            return _classificar_talassemia(dados, ferritina, mentzer, hba2, hbf)
        return {
            'diagnostico': 'Microcitose — etiologia a definir',
            'categoria': 'anemia_micro_indefinida',
            'padrao': f'Ferritina {ferritina} ng/mL · Sat. transf. {"não disponível" if sat_transf is None else f"{sat_transf}% (≥ 20%)"}',
            'exames_confirmatórios': [
                'Eletroforese de hemoglobina (beta-talassemia, HbS)',
                'Saturação de transferrina + TIBC se não disponível',
                'Receptor solúvel de transferrina (sTfR)',
            ],
            'tratamento': ['Aguardar resultado de eletroforese antes de tratar'],
            'encaminhamento': 'Hematologia se eletroforese anormal',
        }

    # ── Regra 4: ferritina alta + talassemia suspeita ─────────────────
    if eletroforese:
        return _classificar_talassemia(dados, ferritina, mentzer, hba2, hbf)

    # ── Regra 5: doença crônica sem ferritina → ACD ──────────────────
    if doenca_cr:
        return {
            'diagnostico': 'Anemia de Doença Crônica (ACD)',
            'categoria': 'anemia_doenca_cronica',
            'padrao': 'VCM baixo/normal · Doença crônica conhecida · Ferro sérico baixo',
            'exames_confirmatórios': [
                'Ferritina (tipicamente > 100), ferro sérico, TIBC (baixo/normal)',
                'PCR e VHS para confirmar estado inflamatório',
            ],
            'tratamento': [
                'Tratar doença de base',
                'Se eGFR < 60 ou neoplasia: considerar agente estimulador de eritropoiese (AEE) — nefrologia/oncologia',
            ],
            'encaminhamento': 'Nefrologia se DRC eGFR < 60',
        }

    # ── Fallback: ferritina não disponível → solicitar ───────────────
    return {
        'diagnostico': 'Anemia microcítica — investigação incompleta',
        'categoria': 'anemia_micro_incompleta',
        'padrao': 'VCM baixo · Ferritina não disponível',
        'exames_confirmatórios': [
            'SOLICITAR: ferritina, ferro sérico, TIBC, saturação de transferrina',
            'Eletroforese de hemoglobina se origem étnica de risco (mediterrâneo, África, Ásia)',
        ],
        'tratamento': ['Aguardar ferritina antes de tratar'],
        'encaminhamento': None,
    }


def _classificar_talassemia(dados, ferritina, mentzer, hba2, hbf):
    rdw = dados.get('rdw', 0)
    rbc = dados.get('rbc')

    if hba2:
        return {
            'diagnostico': 'Traço de Beta-Talassemia',
            'categoria': 'talassemia_beta',
            'padrao': f'VCM baixo · RDW normal/baixo · HbA₂ elevada na eletroforese · Mentzer {mentzer}',
            'exames_confirmatórios': ['Confirmar com teste genético se planejamento familiar'],
            'tratamento': [
                'Nenhum tratamento necessário — traço (não é doença)',
                'NÃO suplementar ferro sem IDA documentada (ferritina baixa)',
                'Aconselhamento genético (risco de beta-talassemia major se parceiro também for portador)',
            ],
            'encaminhamento': 'Genética/hematologia se planejamento reprodutivo',
        }
    if hbf:
        return {
            'diagnostico': 'Beta-Talassemia (HbF elevada / HbA reduzida)',
            'categoria': 'talassemia_beta_maior',
            'padrao': 'HbF elevada + HbA reduzida ou ausente na eletroforese',
            'exames_confirmatórios': ['Teste genético para confirmação'],
            'tratamento': ['Encaminhar hematologia — pode requerer transfusão regular'],
            'encaminhamento': 'Hematologia — urgente',
        }
    # HbA₂ normal + ferritina normal → alfa-talassemia suspeita
    if hba2 is False:
        return {
            'diagnostico': 'Traço de Alfa-Talassemia (suspeita)',
            'categoria': 'talassemia_alfa',
            'padrao': f'VCM baixo · HbA₂ normal · Mentzer {mentzer} · Ferritina normal',
            'exames_confirmatórios': ['Teste genético (deleção no gene HBA1/HBA2) para confirmar'],
            'tratamento': [
                'Nenhum tratamento necessário se traço',
                'NÃO suplementar ferro',
                'Aconselhamento genético',
            ],
            'encaminhamento': 'Genética se planejamento reprodutivo',
        }
    # Mentzer disponível sem eletroforese
    if mentzer is not None:
        if mentzer < 13:
            return {
                'diagnostico': 'Talassemia suspeita (Mentzer < 13)',
                'categoria': 'talassemia_suspeita',
                'padrao': f'VCM baixo · Mentzer = {mentzer} (< 13) · RDW normal/baixo',
                'exames_confirmatórios': ['Eletroforese de hemoglobina', 'Teste genético'],
                'tratamento': ['Aguardar eletroforese — NÃO iniciar ferro empiricamente'],
                'encaminhamento': 'Hematologia',
            }
    return {
        'diagnostico': 'Microcitose — talassemia vs IDA — investigação pendente',
        'categoria': 'anemia_micro_indefinida',
        'padrao': 'VCM baixo · Ferritina normal/alta · Eletroforese necessária',
        'exames_confirmatórios': ['Eletroforese de hemoglobina', 'Ferro sérico + TIBC'],
        'tratamento': ['Aguardar resultado antes de tratar'],
        'encaminhamento': 'Hematologia',
    }


# =============================================================================
# CLASSIFICAÇÃO NORMOCÍTICA (VCM 80–100)
# =============================================================================

def _classificar_normo(dados):
    rpi       = _rpi(dados)
    ferritina = dados.get('ferritina')
    creatinina= dados.get('creatinina')
    tsh       = dados.get('tsh')
    b12       = dados.get('b12')
    folato    = dados.get('folato')
    rdw       = dados.get('rdw', 0)
    doenca_cr = dados.get('doenca_cronica', False)
    sangramento = dados.get('sangramento_ativo', False)
    ictericia   = dados.get('ictericia', False)
    esplenomeg  = dados.get('esplenomegalia', False)

    # ── Sangramento ativo — diagnóstico clínico, independe do RPI ────
    if sangramento:
        return {
            'diagnostico': 'Anemia por Perda Aguda de Sangue',
            'categoria': 'anemia_sangramento',
            'padrao': f'VCM normal · Sangramento ativo relatado · RPI {rpi if rpi is not None else "não calculado"}',
            'exames_confirmatórios': ['Identificar e controlar fonte de sangramento'],
            'tratamento': [
                'Reposição volêmica',
                'Transfusão se Hb < 7 g/dL (ou < 8 g/dL em cardiovascular)',
                'Tratar causa: GI → colonoscopia/EDA; menorragia → ginecologia',
            ],
            'encaminhamento': 'PS/hospital se instabilidade hemodinâmica',
        }

    # ── Hiperproliferativa: hemólise ─────────────────────────────────
    if rpi is not None and rpi > 2.5:
        if sangramento:
            return {
                'diagnostico': 'Anemia por Perda Aguda de Sangue',
                'categoria': 'anemia_sangramento',
                'padrao': f'VCM normal · RPI {rpi} (> 2.5) · Sangramento relatado',
                'exames_confirmatórios': ['Identificar e controlar fonte de sangramento'],
                'tratamento': [
                    'Reposição volêmica',
                    'Transfusão se Hb < 7 g/dL (ou < 8 g/dL em cardiovascular)',
                    'Tratar causa: GI → colonoscopia/EDA; menorragia → ginecologia',
                ],
                'encaminhamento': 'PS/hospital se instabilidade hemodinâmica',
            }
        # Hemólise suspeita
        return {
            'diagnostico': 'Anemia Hemolítica — investigar',
            'categoria': 'anemia_hemolitica',
            'padrao': f'VCM normal · RPI {rpi} (> 2.5) · {"Icterícia/esplenomegalia presentes" if (ictericia or esplenomeg) else "Sintomas hemolíticos"}',
            'exames_confirmatórios': [
                'LDH (elevado em hemólise)',
                'Bilirrubina indireta (elevada)',
                'Haptoglobina (baixa/ausente)',
                'Esfregaço periférico: esferócitos, esquistócitos, células foice',
                'Teste de Coombs direto (DAT)',
                '  → Positivo: AHAI, hemólise por fármaco',
                '  → Negativo: esferocitose hereditária, def. G6PD, PTT/SHU, HPN',
            ],
            'tratamento': _rx_hemolitica(),
            'encaminhamento': 'Hematologia urgente se queda > 2 g/dL em 24h ou esquistócitos',
        }

    # ── Hipoproliferativa: RPI < 2.5 ─────────────────────────────────
    # Anemia renal
    if creatinina is not None and creatinina > 1.4:
        egfr_estimado = 'provável < 60 mL/min' if creatinina > 1.4 else ''
        return {
            'diagnostico': 'Anemia Renal (EPO-deficiente)',
            'categoria': 'anemia_renal',
            'padrao': f'VCM normal · Reticulócitos baixos · Creatinina {creatinina} mg/dL ({egfr_estimado})',
            'exames_confirmatórios': [
                'eGFR (CKD-EPI)', 'Eritropoietina sérica', 'Ferritina + sat transf (alvo: ferritina > 100, sat transf > 20%)',
            ],
            'tratamento': {
                'farmacologico': (
                    'Corrigir deficiência de ferro se ferritina < 100 ou sat transf < 20%\n'
                    '    Se Hb < 10 g/dL em DRC → AEE (epoetina alfa / darbepoetina) — nefrologia\n'
                    '    Alvo de Hb: 10–11,5 g/dL (não ultrapassar 13 — risco CV aumentado)\n'
                    '    Transfusão se Hb < 7 g/dL sintomático'
                ),
                'nao_farmacologico': (
                    'Controle rigoroso da DRC: PA alvo < 130/80, glicemia controlada em diabéticos\n'
                    '    Dieta hipoproteica supervisionada (0,6–0,8 g/kg/dia) — retarda progressão renal\n'
                    '    Restrição de potássio e fósforo conforme orientação do nefrologista\n'
                    '    Cessar tabagismo — acelera progressão da DRC\n'
                    '    Atividade física aeróbica leve (melhora eritropoiese e qualidade de vida em DRC)'
                ),
            },
            'encaminhamento': 'Nefrologia — urgente se Hb < 7 ou DRC avançada',
        }

    # Hipotireoidismo
    if tsh is not None and tsh > 4.5:
        return {
            'diagnostico': 'Anemia por Hipotireoidismo',
            'categoria': 'anemia_hipotireoidismo',
            'padrao': f'VCM normal · TSH {tsh} mUI/L (elevado)',
            'exames_confirmatórios': ['T4 livre', 'Anti-TPO'],
            'tratamento': [
                'Levotiroxina — dose conforme peso e TSH-alvo',
                'Anemia geralmente resolve com reposição hormonal',
            ],
            'encaminhamento': None,
        }

    # Deficiência nutricional precoce (B12 ou ferro antes de macrocitose)
    if b12 is not None and b12 < 200:
        return _rx_b12_normovmc(b12)
    if folato is not None and folato < 2.0:
        return _rx_folato_normovmc(folato)
    if ferritina is not None and ferritina < 30:
        return {
            'diagnostico': 'Deficiência de Ferro Precoce (antes de microcitose)',
            'categoria': 'anemia_ferropriva',
            'padrao': f'VCM normal · Ferritina {ferritina} ng/mL (< 30) · RDW possivelmente elevado',
            'exames_confirmatórios': ['Ferro sérico, TIBC, sat transf'],
            'tratamento': _rx_ferropriva(),
            'encaminhamento': None,
        }

    # Deficiência combinada (RDW alto + VCM normal)
    rdw_alto = rdw > 14.5
    b12_baixo  = b12 is not None and b12 < 200
    ferro_baixo = ferritina is not None and ferritina < 30
    if rdw_alto and (b12_baixo or ferro_baixo):
        return {
            'diagnostico': 'Deficiência Combinada (ferro + B12/folato) — padrão dimórfico',
            'categoria': 'anemia_combinada',
            'padrao': f'VCM normal · RDW {rdw}% (elevado) — populações micro e macrocíticas se cancelam',
            'exames_confirmatórios': [
                'Ferritina, B12, folato (checar todos)',
                'Esfregaço periférico: anisocitose acentuada, população dimórfica',
            ],
            'tratamento': [
                'Sulfato ferroso 15–20 mg Fe elementar/dia (em jejum, dias alternados)',
                'Cianocobalamina 1000 µg/dia VO',
                'Ácido fólico 1 mg/dia',
                'Tratar as duas deficiências simultaneamente',
            ],
            'encaminhamento': None,
        }

    # ACD
    if doenca_cr:
        return {
            'diagnostico': 'Anemia de Doença Crônica (ACD)',
            'categoria': 'anemia_doenca_cronica',
            'padrao': 'VCM normal · Reticulócitos baixos · Doença crônica subjacente',
            'exames_confirmatórios': [
                'Ferritina (tipicamente > 100 em ACD pura)',
                'PCR/VHS para confirmar inflamação',
                'sTfR se dúvida entre ACD e IDA coexistente',
            ],
            'tratamento': [
                'Tratar doença de base',
                'AEE (epoetina) se anemia renal ou neoplásica — encaminhar especialista',
            ],
            'encaminhamento': 'Conforme doença subjacente',
        }

    # Aplasia/infiltração medular — pancitopenia já triada acima
    return {
        'diagnostico': 'Anemia Normocítica Hipoproliferativa — etiologia a definir',
        'categoria': 'anemia_normo_indefinida',
        'padrao': 'VCM normal · Reticulócitos baixos · Sem causa clara identificada',
        'exames_confirmatórios': [
            'Ferritina, B12, folato, creatinina, TSH (se ainda não colhidos)',
            'Esfregaço periférico',
            'EPO sérica',
            'Se persistir sem causa: biópsia de medula óssea — hematologia',
        ],
        'tratamento': ['Investigação antes de tratar empiricamente'],
        'encaminhamento': 'Hematologia se sem causa identificada após workup básico',
    }


# =============================================================================
# CLASSIFICAÇÃO MACROCÍTICA (VCM > 100)
# =============================================================================

def _classificar_macro(dados):
    b12        = dados.get('b12')
    folato     = dados.get('folato')
    tsh        = dados.get('tsh')
    rpi        = _rpi(dados)
    rdw        = dados.get('rdw', 0)
    alcool     = dados.get('alcool', False)
    gastro_cx  = dados.get('gastro_cirurgia', False)
    veg        = dados.get('vegetariano_vegano', False)
    mcv        = dados.get('mcv', 0)
    neurologic = dados.get('sintomas_neurologico', False)

    # ── B12 baixa ─────────────────────────────────────────────────────
    if b12 is not None and b12 < 200:
        graves = neurologic or b12 < 100
        return {
            'diagnostico': f'Deficiência de Vitamina B12 ({"grave — sintomas neurológicos" if graves else "sem envolvimento neurológico aparente"})',
            'categoria': 'anemia_b12',
            'padrao': f'VCM {dados["mcv"]} fL · B12 {b12} pg/mL (< 200) · RDW {rdw}%',
            'exames_confirmatórios': [
                'Ácido metilmalônico (MMA — elevado em def. B12)',
                'Homocisteína (elevada em B12 e folato)',
                'Anti-fator intrínseco (anemia perniciosa)',
                'Esfregaço periférico: neutrófilos hipersegmentados',
            ],
            'tratamento': _rx_b12(graves, gastro_cx, veg),
            'encaminhamento': 'Neurologia se sintomas neurológicos; gastro se suspeita má absorção',
        }

    # ── Folato baixo ─────────────────────────────────────────────────
    if folato is not None and folato < 2.0:
        return {
            'diagnostico': 'Deficiência de Ácido Fólico',
            'categoria': 'anemia_folato',
            'padrao': f'VCM {dados["mcv"]} fL · Folato {folato} ng/mL (< 2.0) · B12 normal',
            'exames_confirmatórios': [
                'MMA — normal (diferencia de B12)',
                'Homocisteína elevada',
                'Esfregaço periférico: neutrófilos hipersegmentados',
            ],
            'tratamento': _rx_folato(alcool),
            'encaminhamento': None,
        }

    # ── Hipotireoidismo ───────────────────────────────────────────────
    if tsh is not None and tsh > 4.5:
        return {
            'diagnostico': 'Anemia Macrocítica por Hipotireoidismo',
            'categoria': 'anemia_hipotireoidismo',
            'padrao': f'VCM {dados["mcv"]} fL · TSH {tsh} mUI/L (elevado)',
            'exames_confirmatórios': ['T4 livre', 'Anti-TPO'],
            'tratamento': ['Levotiroxina — dose conforme peso e TSH-alvo'],
            'encaminhamento': None,
        }

    # ── Álcool ────────────────────────────────────────────────────────
    if alcool:
        return {
            'diagnostico': 'Macrocitose por Álcool (efeito tóxico direto na medula)',
            'categoria': 'anemia_alcool',
            'padrao': f'VCM {dados["mcv"]} fL · Uso de álcool relatado · B12/folato normais',
            'exames_confirmatórios': [
                'GGT e transaminases (hepatopatia alcoólica)',
                'B12 e folato (excluir deficiência concomitante — frequente em alcoólatras)',
            ],
            'tratamento': {
                'farmacologico': (
                    'Ácido fólico 1 mg/dia (alcoólatras frequentemente deficientes mesmo com folato sérico normal)\n'
                    '    Vitamina B1 (tiamina) 100 mg/dia — prevenir encefalopatia de Wernicke\n'
                    '    VCM normaliza em 2–4 meses após abstinência'
                ),
                'nao_farmacologico': (
                    'Abstinência alcoólica — tratamento principal e único eficaz para reverter a macrocitose\n'
                    '    Encaminhar para CAPS AD ou programa de apoio à dependência de álcool\n'
                    '    Dieta equilibrada com folhosos, leguminosas (folato), carnes e ovos (B12)\n'
                    '    Abordar entrevista motivacional — ambivalência é normal neste momento\n'
                    '    Orientar família sobre síndrome de abstinência (tremor, confusão 24–72h após parar)'
                ),
            },
            'encaminhamento': 'CAPS AD / suporte para dependência de álcool',
        }

    # ── Reticulocitose (hemólise/sangramento) — com macrocitose ──────
    if rpi is not None and rpi > 2.5:
        return {
            'diagnostico': 'Macrocitose por Reticulocitose (células jovens grandes)',
            'categoria': 'anemia_reticulocitose',
            'padrao': f'VCM {dados["mcv"]} fL · RPI {rpi} > 2.5 — reticulócitos grandes elevam VCM',
            'exames_confirmatórios': [
                'LDH, bilirrubina indireta, haptoglobina (hemólise?)',
                'Coombs direto',
                'Esfregaço periférico',
            ],
            'tratamento': _rx_hemolitica(),
            'encaminhamento': 'Hematologia se hemólise confirmada',
        }

    # ── VCM > 115 sem causa clara → SMD suspeita ─────────────────────
    if mcv > 115:
        return {
            'diagnostico': 'Macrocitose grave sem causa identificada — Síndrome Mielodisplásica suspeita',
            'categoria': 'anemia_smd',
            'padrao': f'VCM {mcv} fL (> 115) · B12, folato, TSH normais · Sem álcool ou medicamentos',
            'exames_confirmatórios': [
                'Esfregaço periférico: células displásicas, blastócitos',
                'Mielograma — hematologia',
            ],
            'tratamento': ['Encaminhar hematologia com urgência'],
            'encaminhamento': 'Hematologia — urgente',
        }

    # ── Medicamentos (hidroxiureia, MTX, AZT) ────────────────────────
    return {
        'diagnostico': 'Macrocitose — causa a investigar',
        'categoria': 'anemia_macro_indefinida',
        'padrao': f'VCM {dados["mcv"]} fL · B12/folato/TSH {"não disponíveis" if (b12 is None and folato is None) else "normais"}',
        'exames_confirmatórios': [
            'B12, folato, TSH (se ainda não solicitados)',
            'Revisar medicamentos: hidroxiureia, metotrexato, AZT, quimioterapia',
            'GGT/transaminases se hepatopatia suspeita',
            'Esfregaço periférico',
        ],
        'tratamento': ['Aguardar resultado dos exames para tratar causa específica'],
        'encaminhamento': 'Hematologia se VCM > 115 ou pancitopenia',
    }


# =============================================================================
# PRESCRIÇÕES ESTRUTURADAS
# =============================================================================

def _rx_ferropriva():
    return {
        'farmacologico': (
            'Sulfato ferroso 40 mg Fe elementar VO, dias alternados — 1ª linha (Cochrane 2021)\n'
            '    Alternativa: Sulfato ferroso 325 mg (65 mg Fe elementar) em dias alternados\n'
            '    Ferro EV se: intolerância oral, má absorção (Crohn, gastrectomia) ou perdas > reposição'
        ),
        'administracao': (
            'Tomar em jejum ou com vitamina C (suco de laranja 200 mL)\n'
            '    Aguardar ≥ 1h para café, chá, leite, cálcio, antiácidos (reduzem absorção)\n'
            '    Fezes podem escurecer — orientar paciente'
        ),
        'duracao_monitoramento': (
            'Hb deve subir ≥ 1 g/dL em 1 mês → confirma diagnóstico\n'
            '    Continuar 3–6 meses após normalização da Hb para repor estoques medulares'
        ),
        'nao_farmacologico': (
            'Dieta rica em ferro: carnes vermelhas, vísceras (fígado), feijão, lentilha, espinafre, tofu\n'
            '    Combinações que aumentam absorção: carne + legumes + vitamina C na mesma refeição\n'
            '    Evitar na mesma refeição: chá, café, leite, queijo, ovos (quelantes do ferro)\n'
            '    Tratar causa de base: menorragia (ginecologia), sangramento GI (colonoscopia/EDA)'
        ),
    }


def _rx_b12(graves, gastro_cx, veg):
    if graves or gastro_cx:
        return {
            'farmacologico': (
                'Cianocobalamina 1000 µg IM/dia × 7 dias → semanal × 4 semanas → mensal (indefinido)\n'
                '    VO alternativa: 1000–2000 µg/dia (absorção passiva — eficaz mesmo sem fator intrínseco)'
            ),
            'indicacao_im': 'Sintomas neurológicos, anemia perniciosa ou gastrectomia → preferir IM',
            'duracao': 'Indefinida se anemia perniciosa ou gastrectomia — não suspender',
            'resposta': 'Reticulocitose em 3–5 dias · Hb sobe em 1–2 semanas · Neurológico melhora lentamente',
            'nao_farmacologico': (
                'Dieta: carnes, vísceras, frutos do mar, ovos, laticínios são as únicas fontes naturais\n'
                '    Veganos/vegetarianos estritos: suplementação VO contínua é obrigatória (sem fonte alimentar adequada)\n'
                '    Alimentos fortificados: leite vegetal, cereais matinais enriquecidos com B12'
            ),
        }
    return {
        'farmacologico': (
            'Cianocobalamina 1000–2000 µg/dia VO × 3–6 meses\n'
            '    IM se má absorção comprovada ou não-aderência à via oral'
        ),
        'duracao': '3–6 meses; se causa dietética (vegano): suplemento contínuo',
        'resposta': 'Reticulocitose em 3–5 dias · Hb sobe em 1–2 semanas',
        'nao_farmacologico': (
            'Dieta: carnes, ovos, laticínios, frutos do mar\n'
            '    Veganos: suplementação VO permanente — impossível suprir pela dieta sem alimentos animais\n'
            '    Alimentos fortificados como alternativa parcial'
        ),
    }


def _rx_b12_normovmc(b12):
    return {
        'diagnostico': 'Deficiência de B12 Precoce (VCM ainda normal)',
        'categoria': 'anemia_b12',
        'padrao': f'VCM normal · B12 {b12} pg/mL (< 200) · Deficiência antes de macrocitose',
        'exames_confirmatórios': ['MMA sérico', 'Homocisteína', 'Anti-fator intrínseco'],
        'tratamento': _rx_b12(False, False, False),
        'encaminhamento': None,
    }


def _rx_folato(alcool):
    return {
        'farmacologico': 'Ácido fólico 1–5 mg/dia VO × 1–4 meses (até resolução + replete estoques)',
        'atencao': '⚠️  Sempre excluir def. B12 antes — folato mascara B12 e pode piorar neurologia',
        'causa': 'Álcool (principal)' if alcool else 'Dietética / má absorção / medicamentos (MTX, fenitoína, TMP)',
        'nao_farmacologico': (
            'Dieta: folhosos escuros (espinafre, couve, rúcula), feijão, lentilha, brócolis, abacate\n'
            '    Cocção reduz folato — preferir levemente cozidos ou crus\n'
            + ('    Abstinência alcoólica — álcool reduz absorção e aumenta excreção de folato' if alcool
               else '    Revisar medicamentos que interferem: metotrexato, fenitoína, sulfametoxazol-trimetoprim\n'
                    '    Gestação: ácido fólico 400–800 µg/dia profilático (previne defeitos do tubo neural)')
        ),
    }


def _rx_folato_normovmc(folato):
    return {
        'diagnostico': 'Deficiência de Folato Precoce (VCM ainda normal)',
        'categoria': 'anemia_folato',
        'padrao': f'VCM normal · Folato {folato} ng/mL (< 2.0)',
        'exames_confirmatórios': ['MMA (normal — diferencia de B12)', 'Homocisteína'],
        'tratamento': _rx_folato(False),
        'encaminhamento': None,
    }


def _rx_hemolitica():
    return {
        'farmacologico': (
            'AHAI (Coombs+): Prednisona 1 mg/kg/dia → redução gradual após resposta\n'
            '    AHAI refratária: Rituximabe ou esplenectomia — hematologia\n'
            '    PTT/SHU (esquistócitos): HEMATOLOGIA URGENTE — plasmaférese (PTT)\n'
            '    Transfusão se Hb < 7 g/dL ou instabilidade hemodinâmica'
        ),
        'nao_farmacologico': (
            'Def. G6PD: evitar desencadeantes — favas, sulfonamidas, antimaláricos, naftalina\n'
            '    Identificar e suspender fármaco causador (hemólise por droga)\n'
            '    Hidratação adequada durante episódio hemolítico (proteger função renal)\n'
            '    Orientar paciente e familiares sobre reconhecer crise (urina escura, icterícia aguda)'
        ),
    }


# =============================================================================
# ENGINE PRINCIPAL
# =============================================================================

def interpretar_anemia(dados):
    hb       = dados.get('hb', 0)
    mcv      = dados.get('mcv', 0)
    wbc      = dados.get('wbc', 10)
    plt      = dados.get('plt', 200)
    rdw      = dados.get('rdw', 0)
    rpi_val  = _rpi(dados)

    limiar, descr_sexo = _limiar_hb(dados)
    grau, deficit       = _grau_anemia(hb, limiar)

    # ── Sem anemia ────────────────────────────────────────────────────
    if grau == 'normal':
        return {
            'categoria': 'sem_anemia',
            'hb': hb,
            'limiar': limiar,
            'grau': 'normal',
            'mensagem': f'Hb {hb} g/dL está acima do limiar para {descr_sexo} ({limiar} g/dL) — sem anemia.',
            'conduta': ['Investigar outra causa dos sintomas (fadiga, dispneia)'],
        }

    # ── Pancitopenia → encaminhamento imediato ───────────────────────
    if _pancitopenia(dados):
        return {
            'categoria': 'pancitopenia',
            'hb': hb, 'mcv': mcv, 'wbc': wbc, 'plt': plt,
            'grau': grau,
            'mensagem': f'PANCITOPENIA: Hb {hb} + Leucócitos {wbc} + Plaquetas {plt}',
            'diagnostico': 'Pancitopenia — falência medular, leucemia, SMD, aplasia até prova em contrário',
            'conduta': [
                'HEMATOLOGIA URGENTE — biópsia de medula óssea',
                'Esfregaço periférico urgente (blastócitos?)',
                'Suspender medicamentos mielotóxicos',
                'Transfusão se Hb < 7 g/dL ou sangramento ativo',
            ],
        }

    # ── Gravidade muito grave → alerta de transfusão ─────────────────
    alerta_transfusao = grau == 'muito_grave' or (grau == 'grave' and (
        dados.get('sintomas_dispneia') or dados.get('sintomas_palpitacao')
    ))

    # ── Classificação por VCM ─────────────────────────────────────────
    if mcv < 80:
        classif = _classificar_micro(dados)
        tipo_mcv = 'Microcítica'
    elif mcv > 100:
        classif = _classificar_macro(dados)
        tipo_mcv = 'Macrocítica'
    else:
        classif = _classificar_normo(dados)
        tipo_mcv = 'Normocítica'

    return {
        'categoria': classif.get('categoria', 'anemia_indefinida'),
        'hb': hb,
        'mcv': mcv,
        'rdw': rdw,
        'rpi': rpi_val,
        'grau': grau,
        'deficit_hb': round(deficit, 1),
        'tipo_mcv': tipo_mcv,
        'limiar': limiar,
        'descr_sexo': descr_sexo,
        'alerta_transfusao': alerta_transfusao,
        'diagnostico': classif.get('diagnostico', ''),
        'padrao': classif.get('padrao', ''),
        'exames_confirmatórios': classif.get('exames_confirmatórios', []),
        'tratamento': classif.get('tratamento', []),
        'encaminhamento': classif.get('encaminhamento'),
    }
