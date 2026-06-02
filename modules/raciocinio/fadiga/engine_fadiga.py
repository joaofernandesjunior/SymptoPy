# modules/raciocinio/fadiga/engine_fadiga.py
# Motor de raciocínio clínico — Fadiga Crônica
#
# Sequência de exclusão:
#   1. Red flags (urgência imediata)
#   2. Causa secundária laboratorial (exit strategy)
#   3. Apneia obstrutiva do sono (STOP-BANG ≥ 5)
#   4. Transtorno psiquiátrico (PHQ-2/GAD-2 ≥ 3 sem PEM)
#   5. ME/SFC (critérios IOM 2015 completos)
#   6. Fadiga idiopática/subaguda (critérios incompletos)
#
# Categorias únicas:
#   fadiga_red_flags | fadiga_secundaria_laboratorial
#   fadiga_secundaria_apneia | fadiga_secundaria_psiquiatrica
#   fadiga_me_sfc | fadiga_idiopatica_subaguda


# =============================================================================
# RED FLAGS
# =============================================================================

def _avaliar_red_flags(dados):
    flags = []

    perda_pct = dados.get('perda_peso_pct') or 0
    if dados.get('perda_peso_involuntaria'):
        if perda_pct >= 5:
            flags.append({
                'achado': f'Perda de peso involuntária ≥ 5% ({perda_pct:.1f}% referido)',
                'urgencia': 'urgente',
                'acao': 'Investigar neoplasia, tuberculose, doença inflamatória sistêmica — '
                        'RX tórax, hemograma, VHS, LDH, pesquisa de BAAR',
            })
        else:
            flags.append({
                'achado': f'Perda de peso involuntária (percentual: {perda_pct:.1f}%)',
                'urgencia': 'atenção',
                'acao': 'Quantificar perda — se ≥ 5% em 6 meses, investigar causas graves',
            })

    if dados.get('febre_persistente'):
        flags.append({
            'achado': 'Febre persistente ou recorrente sem foco identificado',
            'urgencia': 'urgente',
            'acao': 'Hemoculturas × 2, BAAR × 2, ANA, anti-dsDNA, LDH, PET-CT — '
                    'excluir neoplasia, vasculite, infecção crônica',
        })

    if dados.get('linfadenopatia_fixa'):
        flags.append({
            'achado': 'Linfonodomegalia fixa, endurecida ou > 2 cm',
            'urgencia': 'urgente',
            'acao': 'Biópsia de linfonodo — excluir linfoma e neoplasia metastática; '
                    'solicitar LDH + β2-microglobulina + TC tórax-abdome',
        })

    if dados.get('deficit_neurologico_focal'):
        flags.append({
            'achado': 'Déficit neurológico focal (fraqueza, parestesia, ataxia, diplopia)',
            'urgencia': 'urgente',
            'acao': 'Neurologia urgente — RM de encéfalo e medula com contraste',
        })

    if dados.get('dor_toracica_esforco'):
        flags.append({
            'achado': 'Dor torácica ao esforço ou dispneia progressiva',
            'urgencia': 'urgente',
            'acao': 'ECG + troponina + ecocardiograma — excluir isquemia miocárdica e ICC',
        })

    if dados.get('hepatoesplenomegalia'):
        flags.append({
            'achado': 'Hepatoesplenomegalia ao exame físico',
            'urgencia': 'atenção',
            'acao': 'US abdominal + LDH + β2-microglobulina — excluir doença linfoproliferativa',
        })

    if dados.get('ideacao_suicida_ativa'):
        flags.append({
            'achado': 'Ideação suicida ativa',
            'urgencia': 'urgente',
            'acao': 'Avaliação psiquiátrica imediata — considerar internação involuntária',
        })

    return {'flags': flags}


# =============================================================================
# EXCLUSÃO LABORATORIAL (exit strategy)
# =============================================================================

def _avaliar_laboratorial(dados):
    if not dados.get('labs_disponiveis'):
        return {'diagnostico': False, 'achados': [], 'pendente': True}

    achados = []

    # TSH
    tsh = dados.get('tsh')
    if tsh is not None:
        if tsh > 10:
            achados.append({
                'lab': 'TSH', 'valor': f'{tsh} mIU/L',
                'achado': f'Hipotireoidismo franco (TSH = {tsh} mIU/L)',
                'tratamento': 'Levotiroxina — dose baseada em peso (~1,6 mcg/kg/dia); '
                              'dosar T4L e anticorpos anti-TPO antes de iniciar',
                'encaminhar': 'Endocrinologia se TSH > 10, bócio ou nódulo tireoidiano',
            })
        elif tsh < 0.3:
            achados.append({
                'lab': 'TSH', 'valor': f'{tsh} mIU/L',
                'achado': f'Hipertireoidismo (TSH suprimido = {tsh} mIU/L)',
                'tratamento': 'Dosar T4L + T3L livres + anticorpos anti-TSH (TRAb)',
                'encaminhar': 'Endocrinologia',
            })

    # Ferritina
    ferritina = dados.get('ferritina')
    if ferritina is not None and ferritina < 15:
        achados.append({
            'lab': 'Ferritina', 'valor': f'{ferritina} ng/mL',
            'achado': f'Deficiência de ferro (Ferritina = {ferritina} ng/mL)',
            'tratamento': 'Sulfato ferroso 300 mg 2–3×/dia com vitamina C, longe de antiácidos; '
                          'investigar sangramento oculto (colonoscopia se indicado)',
            'encaminhar': 'Gastroenterologia se suspeita de sangramento digestivo',
        })

    # HbA1c
    hba1c = dados.get('hba1c')
    if hba1c is not None and hba1c >= 6.5:
        achados.append({
            'lab': 'HbA1c', 'valor': f'{hba1c}%',
            'achado': f'Diabetes mellitus tipo 2 (HbA1c = {hba1c}%)',
            'tratamento': 'Metformina 500 mg/dia (titular até 2g/dia); '
                          'orientações nutricionais; rastreio de complicações microvasculares',
            'encaminhar': '',
        })

    # Glicemia de jejum
    glicemia = dados.get('glicemia_jejum')
    if glicemia is not None and glicemia >= 126:
        achados.append({
            'lab': 'Glicemia', 'valor': f'{glicemia} mg/dL',
            'achado': f'Critério diagnóstico de DM (glicemia jejum = {glicemia} mg/dL)',
            'tratamento': 'Confirmar com 2ª dosagem em dia diferente — iniciar manejo de DM2',
            'encaminhar': '',
        })

    # Anemia
    hb = dados.get('hemoglobina')
    if hb is not None:
        sexo_f = dados.get('sexo_feminino', False)
        corte  = 12.0 if sexo_f else 13.0
        if hb < corte:
            achados.append({
                'lab': 'Hemoglobina', 'valor': f'{hb} g/dL',
                'achado': f'Anemia (Hb = {hb} g/dL — corte {corte} g/dL para '
                           f'{"mulheres" if sexo_f else "homens"})',
                'tratamento': 'Investigar etiologia: ferritina, B12, folato, reticulócitos, '
                              'esfregaço de sangue periférico',
                'encaminhar': 'Hematologia se anemia grave (Hb < 8) ou causa não identificada',
            })

    # DRC
    creat = dados.get('creatinina')
    if creat is not None and creat > 1.5:
        achados.append({
            'lab': 'Creatinina', 'valor': f'{creat} mg/dL',
            'achado': f'Disfunção renal sugestiva de DRC (Creatinina = {creat} mg/dL)',
            'tratamento': 'Calcular eGFR (CKD-EPI); solicitar urina rotina + microalbuminúria; '
                          'rever medicações nefrotóxicas',
            'encaminhar': 'Nefrologia se eGFR < 30',
        })

    # Hepatopatia
    alt = dados.get('alt')
    if alt is not None and alt > 120:
        achados.append({
            'lab': 'ALT', 'valor': f'{alt} U/L',
            'achado': f'Hepatopatia (ALT = {alt} U/L — > 3× limite superior da normalidade)',
            'tratamento': 'Investigar DHGNA, hepatite viral (HBsAg, anti-HCV), '
                          'medicamentos hepatotóxicos; solicitar GGT e bilirrubinas',
            'encaminhar': 'Gastroenterologia / Hepatologia',
        })

    return {
        'diagnostico': len(achados) > 0,
        'achados': achados,
        'pendente': False,
    }


# =============================================================================
# CRITÉRIOS IOM 2015 / ME-SFC
# =============================================================================

def _avaliar_criterios_iom(dados):
    duracao   = dados.get('duracao_meses', 0)
    reducao   = dados.get('reducao_atividade_substancial', False)
    nova      = dados.get('fadiga_nova_onset', True)
    pem       = dados.get('pem_presente', False)
    sono      = dados.get('sono_nao_reparador', False)
    brain_fog = dados.get('brain_fog', False)
    ortostase = dados.get('intolerancia_ortostatica', False)

    core_ok   = duracao >= 6 and reducao and nova and pem and sono
    adicional = brain_fog or ortostase

    faltando = []
    if duracao < 6:    faltando.append(f'Duração ≥ 6 meses (atual: {duracao} meses)')
    if not reducao:    faltando.append('Redução substancial de atividade')
    if not nova:       faltando.append('Início definido (não fadiga lifelong)')
    if not pem:        faltando.append('PEM — mal-estar pós-esforço (critério central obrigatório)')
    if not sono:       faltando.append('Sono não-reparador')
    if not adicional:  faltando.append('≥ 1 critério adicional: brain fog OU intolerância ortostática')

    return {
        'core_ok':      core_ok,
        'adicional_ok': adicional,
        'completo':     core_ok and adicional,
        'faltando':     faltando,
        'brain_fog':    brain_fog,
        'ortostase':    ortostase,
        'duracao':      duracao,
        'nice_possivel': 4 <= duracao < 6 and reducao and pem and sono,
    }


# =============================================================================
# PONTO DE ENTRADA
# =============================================================================

def interpretar_fadiga(dados):
    # Calcular STOP-BANG total se não preenchido pelo subjetivo
    if 'stopbang_total' not in dados:
        dados['stopbang_total'] = sum([
            bool(dados.get('sb_ronco')),
            bool(dados.get('sb_cansaco_diurno')),
            bool(dados.get('sb_apneia_observada')),
            bool(dados.get('sb_pressao_alta')),
            bool(dados.get('sb_imc_35')),
            bool(dados.get('sb_idade_50')),
            bool(dados.get('sb_pescoco_40')),
            bool(dados.get('sb_masculino')),
        ])

    stopbang = dados['stopbang_total']
    phq2     = dados.get('phq2_total', 0)
    gad2     = dados.get('gad2_total', 0)
    pem      = dados.get('pem_presente', False)

    # ── 1. Red flags ────────────────────────────────────────────────
    red_flags = _avaliar_red_flags(dados)
    if red_flags['flags']:
        return {
            'categoria': 'fadiga_red_flags',
            'red_flags': red_flags,
            'conduta': [
                'Investigação dirigida ao red flag — não prosseguir algoritmo de fadiga primária',
                'Exames conforme achado específico (ver conduta de cada flag)',
                'Retorno em 1–2 semanas ou urgência conforme gravidade',
            ],
        }

    # ── 2. Exit strategy laboratorial ───────────────────────────────
    lab = _avaliar_laboratorial(dados)
    if lab['diagnostico']:
        return {
            'categoria': 'fadiga_secundaria_laboratorial',
            'lab': lab,
            'conduta': [
                'EXIT STRATEGY — tratar causa secundária identificada antes de prosseguir',
                'Reavaliação de fadiga após 8–12 semanas de tratamento da causa base',
                'Se fadiga persistir após correção: prosseguir algoritmo de fadiga primária',
            ],
        }

    # ── 3. Apneia (STOP-BANG ≥ 5) ───────────────────────────────────
    if stopbang >= 5:
        return {
            'categoria': 'fadiga_secundaria_apneia',
            'stopbang': stopbang,
            'conduta': [
                f'STOP-BANG = {stopbang}/8 — ALTO RISCO para Apneia Obstrutiva do Sono',
                'Encaminhar para polissonografia ou oximetria de pulso noturna como triagem',
                'Perda de peso se IMC elevado (~1 evento/hora por kg perdido)',
                'Suspender álcool e sedativos à noite; posição lateral',
                'CPAP: indicado se IAH ≥ 15 ou ≥ 5 com sintomas — encaminhar pneumologia/otorrino',
            ],
        }

    # ── 4. Psiquiátrica (sem PEM) ────────────────────────────────────
    if (phq2 >= 3 or gad2 >= 3) and not pem:
        conduta = []
        if phq2 >= 3:
            conduta.append(f'PHQ-2 = {phq2}/6 — triagem POSITIVA para depressão → aplicar PHQ-9 completo')
        if gad2 >= 3:
            conduta.append(f'GAD-2 = {gad2}/6 — triagem POSITIVA para ansiedade → aplicar GAD-7 completo')
        conduta += [
            'PEM ausente — diferencia de ME/SFC (fadiga piora com atividade, mas sem crash retardado)',
            'Se PHQ-9 ≥ 10: ISRS de primeira linha (sertralina 50 mg/dia ou escitalopram 10 mg/dia)',
            'TCC: indicada para depressão e ansiedade — encaminhar psicologia',
            'Fadiga por depressão PODE melhorar com exercício gradual (ao contrário de ME/SFC)',
            'Comorbidade é comum — PHQ-2/GAD-2 positivos não excluem ME/SFC se PEM estiver presente',
        ]
        return {
            'categoria': 'fadiga_secundaria_psiquiatrica',
            'phq2': phq2, 'gad2': gad2,
            'conduta': conduta,
            'alerta': 'PEM ausente — exercício gradual pode ser indicado (ao contrário de ME/SFC)',
        }

    # ── 5. ME/SFC — IOM 2015 ────────────────────────────────────────
    criterios = _avaliar_criterios_iom(dados)
    if criterios['completo']:
        return {
            'categoria': 'fadiga_me_sfc',
            'criterios': criterios,
            'phq2': phq2, 'gad2': gad2, 'stopbang': stopbang,
            'get_contraindicado': True,
            'conduta': [
                'PACING — estratégia principal (NICE 2021 / CDC)',
                'Estabelecer linha de base de atividade sustentável sem desencadear PEM',
                'Fragmentar atividades em blocos curtos com descanso ativo entre eles',
                'Evitar ciclos boom-bust — descansar também nos dias bons',
                'Aumentar atividade SOMENTE após semanas–meses de estabilidade (5–10% por vez)',
                'Sono: higiene rigorosa; melatonina 0,5–3 mg ou trazodona 25–50 mg se insônia refratária',
                'Intolerância ortostática: hidratação 2–3 L/dia, sal aumentado, meia compressiva 30–40 mmHg',
                'Dor: paracetamol / AINE em doses regulares; naltrexona em baixa dose (off-label)',
                'Encaminhar: ambulatório de ME/SFC ou neurologista com interesse na síndrome',
            ],
        }

    # ── 6. Fadiga idiopática/subaguda ───────────────────────────────
    return {
        'categoria': 'fadiga_idiopatica_subaguda',
        'criterios': criterios,
        'phq2': phq2, 'gad2': gad2, 'stopbang': stopbang,
        'lab_pendente': lab.get('pendente', False),
        'conduta': [
            'Solicitar painel laboratorial inicial se ainda não realizado',
            'Tratar comorbidades identificadas (sono, humor, dor)',
            'Higiene do sono: horário regular, sem telas 1h antes, quarto escuro e fresco',
            'Atividade física leve (caminhada 10–20 min, 3×/sem) SE tolerada sem piora de sintomas',
            'Estratégias de conservação de energia — pacing leve conforme tolerância',
            'Reavaliação em 4–8 semanas — reclassificar se critérios IOM 2015 evoluírem',
        ],
        'mensagem': 'Fadiga com critérios incompletos para ME/SFC — acompanhar evolução.',
    }
