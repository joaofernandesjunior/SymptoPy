# modules/raciocinio/diarreia/engine_diarreia.py
# Motor de raciocínio clínico — Diarreia no Adulto (PA / APS)
#
# Sequência de exclusão:
#   0. Imunossuprimido (HIV CD4 < 200 / transplante / quimio)
#   1. Sepse (qualquer duração — internação imediata)
#   2. [AGUDA ≤ 14d]
#      3a. Disenteria bacilar (sangue + febre ≥ 38.5°C)
#      3b. STEC suspeita (sangue SEM febre) — NÃO ATB, NÃO loperamida
#      4a. C. difficile (ATB < 3m ou internação recente)
#      4b. Diarreia do viajante
#      4c. Toxinfecção alimentar (surto ≥ 2 pessoas)
#      5.  Watery sem alarmes (viral / lactose / auto-limitada)
#   6. [PERSISTENTE 15–30d] → parasitas
#   7. [CRÔNICA > 30d]
#      a. Alarme urgente (hematoquesia / massa)
#      b. DII suspeita (calprotectina > 200)
#      c. SII-D (calprotectina < 50 ou padrão funcional)
#      d. Zona cinzenta (calprotectina 50–200)
#      e. Alarme eletivo (perda de peso / anemia / ≥ 50a / HF CCR)
#
# Categorias únicas (prefixo diarreia_):
#   diarreia_imunossuprimido | diarreia_sepse
#   diarreia_disenteria_bacilar | diarreia_stec_suspeita
#   diarreia_c_diff | diarreia_viajante | diarreia_toxinfeccao
#   diarreia_aguda_watery | diarreia_persistente
#   diarreia_cronica_alarme_urgente | diarreia_cronica_alarme_eletivo
#   diarreia_dii_suspeita | diarreia_sii_d


# =============================================================================
# AUXILIARES DE DESIDRATAÇÃO
# =============================================================================

def _classificar_desidratacao(dados):
    """Classifica grau de desidratação a partir de sintomas (sem objetivo.py)."""
    grau = dados.get('desidratacao_grau', '')
    if grau in ('grave', 'moderada', 'leve', 'sem'):
        return grau

    # Recalcular se não pré-classificado (ex.: testes unitários)
    if (dados.get('hipotensao_conhecida') or dados.get('alteracao_consciencia')
            or dados.get('olhos_fundos')):
        return 'grave'
    if (dados.get('oliguria') or dados.get('tontura_ortostase')
            or (dados.get('sede_intensa') and dados.get('mucosas_ressecadas'))):
        return 'moderada'
    if dados.get('sede_intensa') or dados.get('mucosas_ressecadas'):
        return 'leve'
    return 'sem'


def _conduta_desidratacao(grau):
    """Retorna linhas de conduta de hidratação por grau."""
    if grau == 'grave':
        return [
            'INTERNAÇÃO — desidratação grave (≥ 10% peso corporal estimado)',
            'SF 0.9% ou Ringer Lactato IV: 20–30 mL/kg em bolus → reavaliar',
            'Monitorização: débito urinário-alvo ≥ 0.5 mL/kg/h, PA, FC, estado mental',
        ]
    if grau == 'moderada':
        return [
            'SRO OMS baixa osmolaridade: 100 mL/kg em 4 horas VO',
            'Reavaliação clínica em 4h — se não melhora ou vômito incoercível → IV',
            'Repor perdas em curso: ~10 mL/kg por evacuação adicional',
            'SRO caseiro (emergência): 6 col. chá de açúcar + ½ col. chá de sal em 1 L de água filtrada',
        ]
    if grau == 'leve':
        return [
            'SRO OMS: 50 mL/kg em 4 horas VO',
            'Alternativa (SRO indisponível): água de coco natural OU isotônico (Gatorade/Pedialyte) + biscoito salgado — NÃO substitui SRO em desidratação moderada/grave',
            'Retomar alimentação normal o mais cedo possível (BRAT sem vantagem)',
            'Repor perdas: ~10 mL/kg por evacuação',
        ]
    return [
        'SRO de manutenção: ~10 mL/kg por evacuação — prevenir desidratação',
        'Alternativa: água de coco natural OU isotônico + alimentos salgados (se SRO indisponível)',
        'Retomar alimentação normal imediatamente',
    ]


# =============================================================================
# AUXILIARES DE TRIAGEM
# =============================================================================

def _avaliar_sepse(dados):
    return bool(
        dados.get('hipotensao_conhecida') or dados.get('alteracao_consciencia')
        or dados.get('extremidades_frias') or dados.get('dor_abdominal_peritoneal')
        or dados.get('sinais_sepse')
    )


def _avaliar_imunossuprimido_grave(dados):
    """True se imunossupressão relevante que altera o roteamento principal."""
    if not dados.get('imunossuprimido'):
        return False
    if dados.get('hiv_diagnosticado'):
        cd4 = dados.get('cd4_valor')
        if cd4 is None or cd4 < 200:
            return True
    if dados.get('transplante_quimio_biologico') or dados.get('corticoide_cronico'):
        return True
    return False


def _agente_toxinfeccao(incubacao_horas):
    """Estima agente por incubação — toxinfecção alimentar."""
    if incubacao_horas == 0:
        return 'Incubação não informada — aguardar microbiologia'
    if incubacao_horas <= 6:
        return 'S. aureus / B. cereus (toxina pré-formada) — vômito predominante, autolimitado 12–24h'
    if incubacao_horas <= 16:
        return 'Clostridium perfringens — diarreia sem vômito, autolimitado 24h'
    if incubacao_horas <= 48:
        return 'Salmonella / Campylobacter / ETEC — diarreia com febre possível'
    return 'Norovírus / E. coli O157:H7 — aguardar microbiologia'


# =============================================================================
# PONTO DE ENTRADA
# =============================================================================

def interpretar_diarreia(dados):
    duracao = dados.get('duracao_dias', 0)
    desat   = _classificar_desidratacao(dados)
    sro     = _conduta_desidratacao(desat)

    # ── 0. Imunossuprimido grave ─────────────────────────────────────────────
    if _avaliar_imunossuprimido_grave(dados):
        cd4 = dados.get('cd4_valor')
        if cd4 is not None and cd4 < 50:
            patogenos = [
                'CMV colite (diarreia sanguinolenta + CD4 < 50)',
                'MAC — Mycobacterium avium complex (febre + diarreia + suores noturnos)',
                'Cryptosporidium (diarreia aquosa volumosa)',
                'Microsporidium',
            ]
        elif cd4 is not None and cd4 < 200:
            patogenos = [
                'Cryptosporidium', 'Cystoisospora belli', 'Microsporidium',
            ]
        else:
            patogenos = [
                'Campylobacter', 'Salmonella', 'Shigella', 'C. difficile',
                '(CD4 > 200 ou desconhecido — espectro similar ao imunocompetente)',
            ]
        return {
            'categoria': 'diarreia_imunossuprimido',
            'cd4': cd4,
            'patogenos_suspeitos': patogenos,
            'desidratacao_grau': desat,
            'conduta': [
                f'Imunossuprimido — CD4 = {cd4 if cd4 is not None else "desconhecido"} cél/mm³',
                'Baixo limiar de internação — especialmente CD4 < 50',
                'Workup amplo: coprocultura + PCR multiplex fecal + O&P × 3 (3 amostras)',
                'BAAR modificado (Kinyoun) para Cryptosporidium / Isospora / Cyclospora',
                'Se CD4 < 50: hemoculturas micobacterianas (MAC) + PCR CMV no sangue',
                'C. diff: testar se ATB recente ou hospitalização (GDH + toxina EIA)',
                'CD4 desconhecido → dosar antes da alta',
                *sro,
            ],
            'exames': [
                'Coprocultura', 'PCR multiplex fecal', 'O&P × 3',
                'BAAR modificado', 'C. diff (se indicado)',
                'PCR CMV / hemocultura micobacteriana (se CD4 < 50)',
                'CD4 se desconhecido',
            ],
            'internacao': cd4 is None or cd4 < 50 or _avaliar_sepse(dados),
        }

    # ── 1. Sepse ─────────────────────────────────────────────────────────────
    if _avaliar_sepse(dados):
        sinais = [
            k for k in (
                'hipotensao_conhecida', 'alteracao_consciencia',
                'extremidades_frias', 'dor_abdominal_peritoneal',
            ) if dados.get(k)
        ]
        return {
            'categoria': 'diarreia_sepse',
            'sinais': sinais,
            'desidratacao_grau': desat,
            'conduta': [
                'INTERNAÇÃO IMEDIATA — sepse / suspeita de choque séptico',
                'SF 0.9% ou Ringer Lactato IV: 30 mL/kg em 3h (Sepsis-3)',
                'Hemoculturas × 2 ANTES de iniciar ATB',
                'ATB empírico: Ceftriaxona 1g IV 1×/dia ou Ciprofloxacino 400 mg IV 12/12h',
                'Lactato sérico, PCR, hemograma, BMP, creatinina — urgentes',
                'Coprocultura + PCR multiplex (Campylobacter, Salmonella, Shigella, STEC)',
                'C. diff se ATB recente ou internação prévia',
            ],
            'exames': [
                'Hemoculturas × 2', 'Lactato', 'Hemograma', 'BMP', 'PCR',
                'Coprocultura + PCR multiplex', 'C. diff se indicado',
            ],
            'internacao': True,
        }

    # ── FLUXO AGUDA (≤ 14 dias) ──────────────────────────────────────────────
    if duracao <= 14:
        sangue = dados.get('fezes_sanguinolentas', False)
        febre  = dados.get('febre_38_5', False)

        # 3a. Disenteria bacilar — sangue + febre ≥ 38.5°C
        if sangue and febre:
            return {
                'categoria': 'diarreia_disenteria_bacilar',
                'desidratacao_grau': desat,
                'loperamida_contraindicada': True,
                'conduta': [
                    'Disenteria bacilar — Shigella / Campylobacter / Salmonella invasiva',
                    '1ª linha: Azitromicina 500 mg/dia × 3 dias VO (IDSA 2017 / ACG 2016)',
                    'Ásia / Índia: Azitromicina obrigatória — resistência FQ > 90% em Campylobacter',
                    'Shigella dysenteriae: 5 dias superior a dose única ou 3 dias',
                    'Salmonella NÃO tratar se imunocompetente e não grave (prolonga shedding)',
                    'Tratar Salmonella se: grave / bacteremia / imunossuprimido / > 50a com aterosclerose / prótese',
                    'Se Salmonella com indicação: Ciprofloxacino 500 mg 12/12h × 5–7d OU Azitromicina 500 mg/dia × 5–7d',
                    'LOPERAMIDA CONTRAINDICADA — risco de megacólon tóxico',
                    *sro,
                ],
                'exames': [
                    'Coprocultura', 'PCR multiplex fecal',
                    'Hemograma + PCR + creatinina',
                ],
                'internacao': desat == 'grave',
            }

        # 3b. STEC suspeita — sangue SEM febre
        if sangue and not febre:
            return {
                'categoria': 'diarreia_stec_suspeita',
                'desidratacao_grau': desat,
                'loperamida_contraindicada': True,
                'atb_contraindicado': True,
                'conduta': [
                    'SUSPEITA DE STEC (E. coli O157:H7) — sangue sem febre',
                    'ANTIBIÓTICO CONTRAINDICADO — aumenta risco de SHU (Síndrome Hemolítico-Urêmica)',
                    'LOPERAMIDA CONTRAINDICADA — risco de megacólon tóxico',
                    'Coprocultura urgente com pesquisa específica de STEC + toxina Shiga',
                    'PCR multiplex fecal se disponível (detecta STEC e toxina)',
                    'Hemograma + creatinina + LDH + plaquetas — triagem de SHU',
                    'Monitorar SHU: anemia hemolítica + plaquetopenia + IRA → internar imediatamente',
                    *sro,
                ],
                'exames': [
                    'Coprocultura (STEC + Shiga toxin EIA)',
                    'PCR multiplex fecal',
                    'Hemograma', 'Creatinina', 'LDH', 'Plaquetas',
                ],
                'internacao': desat == 'grave',
                'alerta_shu': True,
            }

        # 4a. C. difficile — ATB recente ou internação
        if dados.get('atb_recente_3m') or dados.get('internacao_recente_3m'):
            atb_ref = dados.get('qual_atb_recente', '')
            return {
                'categoria': 'diarreia_c_diff',
                'atb_recente': atb_ref,
                'desidratacao_grau': desat,
                'conduta': [
                    f'Suspeita de C. difficile — ATB recente ({atb_ref or "não especificado"}) / internação',
                    'Diagnóstico: 2 etapas — GDH antígeno ou PCR (NAAT) → confirmar toxina EIA',
                    'EVITAR antidiarreicos (loperamida) — risco de megacólon tóxico',
                    '1ª linha (IDSA/ACG 2021): Vancomicina 125 mg VO 4×/dia × 10 dias',
                    'Fidaxomicina 200 mg VO 2×/dia × 10 dias (menor recorrência — se disponível)',
                    'Metronidazol 500 mg TID × 10 dias: alternativa APENAS se vancomicina/fidaxomicina indisponíveis',
                    'CDI GRAVE (WBC ≥ 15.000 ou Cr ≥ 1.5): Vancomicina 125 mg VO QID × 10d — considerar internação',
                    'CDI FULMINANTE (hipotensão + íleo): Vancomicina 500 mg VO/SNG QID + Metronidazol 500 mg IV 8/8h',
                    'Probióticos NÃO recomendados para prevenção de CDI (evidência insuficiente — ACG 2021)',
                    *sro,
                ],
                'exames': [
                    'C. diff GDH + toxina EIA (ou NAAT/PCR)',
                    'Hemograma (WBC)', 'Creatinina',
                ],
                'criterios_gravidade': {
                    'grave':      'WBC ≥ 15.000 células/µL OU Creatinina ≥ 1.5 mg/dL',
                    'fulminante': 'Hipotensão + íleo OU megacólon',
                },
                'internacao': desat == 'grave',
            }

        # 4b. Diarreia do viajante
        if dados.get('viagem_recente'):
            asia  = dados.get('viagem_asia', False)
            dest  = dados.get('destino_viagem', 'destino não informado')
            atb   = (
                'Azitromicina 500 mg dose única VO (Ásia — FQ resistência > 90% em Campylobacter)'
                if asia else
                'Azitromicina 500 mg dose única VO  OU  Ciprofloxacino 750 mg dose única VO'
            )
            return {
                'categoria': 'diarreia_viajante',
                'destino': dest,
                'asia': asia,
                'desidratacao_grau': desat,
                'conduta': [
                    f'Diarreia do viajante — {dest}',
                    f'ATB empírico (moderado-grave ou febre): {atb}',
                    'Grave (afeta atividades) ou febre: estender para 3 dias',
                    'Rifaximina 200 mg TID × 3 dias: APENAS diarreia não-invasiva sem febre/sangue',
                    'NÃO usar rifaximina se febre, sangue ou suspeita de Campylobacter/Shigella/Salmonella',
                    'Loperamida SEGURA se apirético e sem sangue: 4 mg inicial + 2 mg/evacuação, máx 8 mg/48h',
                    'Combinação Azitromicina + Loperamida encurta duração vs. ATB isolado (ACG 2016)',
                    'Ondansetrona 4–8 mg VO/IV se vômito impede SRO',
                    *sro,
                ],
                'internacao': desat == 'grave' or _avaliar_sepse(dados),
            }

        # 4c. Toxinfecção alimentar
        if dados.get('surto_alimentar'):
            incubacao = dados.get('incubacao_horas', 0)
            agente    = _agente_toxinfeccao(incubacao)
            return {
                'categoria': 'diarreia_toxinfeccao',
                'alimento_suspeito': dados.get('alimento_suspeito', ''),
                'incubacao_horas':   incubacao,
                'agente_provavel':   agente,
                'desidratacao_grau': desat,
                'conduta': [
                    f'Toxinfecção alimentar — {agente}',
                    'ATB geralmente NÃO indicado — diarreia por toxina é auto-limitada',
                    'Salmonella não-tifóidea imunocompetente: NÃO tratar (prolonga shedding)',
                    'Loperamida segura se apirético e sem sangue: 4 mg + 2 mg/evacuação, máx 8 mg',
                    'Bismuto subsalicilato: 30 mL a cada 30 min, máx 8 doses (alternativa)',
                    'Ondansetrona 4–8 mg se vômito predominante',
                    'NOTIFICAR Vigilância Epidemiológica — surto deve ser registrado',
                    *sro,
                ],
                'notificar_vigilancia': True,
                'internacao': desat == 'grave',
            }

        # 5. Aguda watery — viral / lactose / auto-limitada
        lactose = dados.get('piora_com_lacteos', False)
        aine    = dados.get('uso_aine_recente', False)
        metform = dados.get('metformina_dose_alta', False)

        notas_extra = []
        if lactose:
            notas_extra += [
                'SUSPEITA: intolerância à lactose — piora com laticínios',
                'Retirar lácteos por 2 semanas; substituir por versão sem lactose ou bebida vegetal',
                'Lactase oral (farmácia) pode ser usada junto às refeições com lácteos',
            ]
        if aine:
            notas_extra.append('AINE: pode causar diarreia osmótica/inflamatória — suspender se possível')
        if metform:
            notas_extra.append('Metformina ≥ 2 g/dia: efeito adverso comum — considerar dose menor ou formulação ER')

        vomito  = dados.get('vomito', False) or dados.get('nausea', False)
        febre_d = dados.get('febre', False)

        # Prescrições estruturadas — formato Rx pad
        rx_list = []
        if vomito:
            rx_list.append({
                'linha': '1ª linha — antiemético',
                'medicamento': 'Ondansetrona',
                'prescricoes': [{
                    'quantidade': '10 comprimidos (1 caixa)',
                    'unidade': '8 mg',
                    'posologia': (
                        'Tomar 1 comprimido a cada 8 horas se náusea ou vômito '
                        '(máx 3×/dia × 3 dias)'
                    ),
                }],
                'nota': (
                    'Comprimido bucodispersível (ODT): dissolver na língua — vantagem em vômitos intensos. '
                    'Se indisponível: usar Metoclopramida (ver abaixo).'
                ),
            })
            rx_list.append({
                'linha': 'Alternativo — antiemético (se Ondansetrona indisponível)',
                'medicamento': 'Metoclopramida',
                'prescricoes': [{
                    'quantidade': '20 comprimidos',
                    'unidade': '10 mg',
                    'posologia': (
                        'Tomar 1 comprimido 30 minutos antes das refeições, '
                        'a cada 8 horas, se náusea ou vômito (máx 3×/dia × 5 dias)'
                    ),
                }],
                'nota': (
                    'Usar SOMENTE se Ondansetrona indisponível. '
                    'Risco raro de reação extrapiramidal (agitação, movimentos involuntários) — '
                    'suspender imediatamente se ocorrer.'
                ),
            })

        if not febre_d:
            rx_list.append({
                'linha': 'Antidiarreico sintomático (se apirético)',
                'medicamento': 'Loperamida',
                'prescricoes': [{
                    'quantidade': '8 comprimidos',
                    'unidade': '2 mg',
                    'posologia': (
                        'Tomar 2 comprimidos (4 mg) na 1ª evacuação diarreica; '
                        'depois 1 comprimido (2 mg) a cada evacuação. '
                        'Máx 4 comprimidos (8 mg) por dia, por até 48 horas'
                    ),
                }],
                'nota': (
                    'NÃO usar se: febre ≥ 38.5°C, sangue ou muco nas fezes, piora da dor abdominal. '
                    'Venda sem receita (OTC) — farmacista pode orientar.'
                ),
            })

        return {
            'categoria': 'diarreia_aguda_watery',
            'suspeita_lactose': lactose,
            'desidratacao_grau': desat,
            'conduta': [
                'Gastroenterite aguda viral / auto-limitada — manejo sintomático',
                'Loperamida se apirético e sem sangue (4 mg inicial → 2 mg/evacuação, máx 8 mg/dia × 48h)',
                'Ondansetrona 8 mg VO se vômito impede hidratação oral (Metoclopramida 10 mg se indisponível)',
                'BRAT não tem vantagem — retomar alimentação normal assim que possível',
                *notas_extra,
                *sro,
            ],
            'prescricoes_estruturadas': rx_list,
            'orientacoes': {
                'reidratacao_oral': (
                    'Tomar soro oral (sachê de farmácia), água de coco natural ou isotônico '
                    'em goles pequenos e frequentes ao longo do dia. '
                    'A cada evacuação diarreica: repor ~200 mL extras. '
                    'Soro caseiro (emergência): 1 litro de água filtrada + 1 colher de sopa '
                    'de açúcar + 1 colher de chá rasa de sal.'
                ),
                'alimentacao': (
                    'Retomar alimentação normal assim que sentir vontade — não é preciso esperar. '
                    'A dieta BRAT (banana, arroz, torrada, maçã) NÃO tem vantagem comprovada. '
                    'Evitar laticínios e frituras se perceber piora dos sintomas após ingestão.'
                ),
                'sinais_retorno': (
                    'Retornar se: febre ≥ 38.5°C, sangue ou muco nas fezes, '
                    'tontura ao levantar / boca muito seca (desidratação grave), '
                    'vômitos que impedem qualquer ingestão oral, '
                    'ou sem melhora após 7 dias.'
                ),
            },
            'retorno': 'Retornar se: febre ≥ 38.5°C, sangue nas fezes, piora da desidratação ou > 7 dias sem melhora',
            'internacao': desat == 'grave',
        }

    # ── FLUXO PERSISTENTE (15–30 dias) ───────────────────────────────────────
    if duracao <= 30:
        return {
            'categoria': 'diarreia_persistente',
            'duracao': duracao,
            'desidratacao_grau': desat,
            'conduta': [
                f'Diarreia persistente ({duracao} dias) — excluir parasitoses e infecção subaguda',
                'Exames: coprocultura + O&P × 3 (amostras em dias diferentes) + antígeno de Giardia fecal',
                'Giardia lamblia: 1ª linha: Tinidazol 2 g VO dose única (2 cp de 1 g) — melhor adesão e embalagem simples',
                '                 Alt.: Metronidazol 250 mg TID × 7 dias → prescrever 20 cp (1 caixa); omissão da dose do 7° dia não compromete eficácia',
                'Amebíase intestinal: Metronidazol 500 mg TID × 10d → Paromomicina 500 mg TID × 7d (lúmen)',
                'C. diff: testar se ATB recente (GDH + toxina EIA ou PCR)',
                'Calprotectina fecal: solicitar se não disponível (diferencia funcional de orgânica)',
                *sro,
            ],
            'exames': [
                'Coprocultura', 'O&P × 3', 'Giardia antígeno fecal',
                'C. diff se ATB recente', 'Calprotectina fecal',
            ],
            'internacao': desat == 'grave',
        }

    # ── FLUXO CRÔNICO (> 30 dias) ────────────────────────────────────────────
    hematochezia = dados.get('hematochezia_cronica', False)
    peritoneal   = dados.get('dor_abdominal_peritoneal', False)
    perda_peso   = dados.get('perda_peso_involuntaria', False)
    anemia       = dados.get('anemia_sintomas', False)
    hf_ccr       = dados.get('hf_ccr_primeiro_grau', False)
    nocturna     = dados.get('nocturna', False)
    piora_gluten = dados.get('piora_com_gluten', False)
    medicamentos = dados.get('medicamentos_suspeitos_diarreia', False)
    meds_txt     = dados.get('quais_medicamentos_suspeitos', '')
    melhora_evac = dados.get('dor_melhora_evacuacao', False)
    piora_stress = dados.get('piora_estresse', False) or dados.get('dor_piora_estresse', False)
    idade        = dados.get('idade', 0)
    calproto     = dados.get('calprotectina_valor')

    # 7a. Alarme urgente
    if hematochezia or peritoneal:
        alarmes = []
        if hematochezia: alarmes.append('hematoquesia crônica')
        if peritoneal:   alarmes.append('dor abdominal com rigidez peritoneal')
        return {
            'categoria': 'diarreia_cronica_alarme_urgente',
            'alarmes': alarmes,
            'desidratacao_grau': desat,
            'conduta': [
                'Diarreia crônica com ALARME ORGÂNICO GRAVE',
                'COLONOSCOPIA URGENTE — encaminhar Gastroenterologia em < 2 semanas',
                'Hemograma + PCR + ferritina + CEA + albumina',
                'Calprotectina > 150 mcg/g praticamente confirma DII ativa',
                *sro,
            ],
            'exames': [
                'Hemograma', 'Ferritina', 'PCR/VHS', 'CEA', 'Albumina',
                'Calprotectina fecal', 'Colonoscopia urgente',
            ],
            'internacao': desat == 'grave' or _avaliar_sepse(dados),
        }

    # 7b. Calprotectina disponível
    if calproto is not None:
        if calproto > 200:
            return {
                'categoria': 'diarreia_dii_suspeita',
                'calprotectina': calproto,
                'desidratacao_grau': desat,
                'conduta': [
                    f'Calprotectina fecal = {calproto} mcg/g — ALTA (> 200 mcg/g)',
                    'Alta probabilidade de DII ativa (Crohn / RCU) — VPN ~98% para excluir DII se < 50',
                    'COLONOSCOPIA eletiva com biópsia — padrão ouro diagnóstico',
                    'Encaminhar Gastroenterologia (eletivo — não postergar > 4–8 semanas)',
                    'Hemograma + PCR + VHS + ferritina + albumina + B12 + folato',
                    'NÃO iniciar corticoide ou mesalazina sem diagnóstico histológico confirmado',
                    *sro,
                ],
                'exames': [
                    'Colonoscopia com biópsia', 'Hemograma', 'PCR', 'VHS',
                    'Albumina', 'Ferritina', 'B12', 'Folato',
                ],
                'internacao': desat == 'grave',
            }

        if calproto < 50:
            conduta_sii = [
                f'Calprotectina fecal = {calproto} mcg/g — NORMAL (< 50 mcg/g)',
                'Exclui DII com VPN ~98% — diagnóstico de SII-D (funcional)',
                'Dieta Low-FODMAP por 6–8 semanas (reduz sintomas em ~70% dos pacientes)',
                'Antiespasmódicos: Butilescopolamina 10 mg TID OU Mebeverina 135 mg TID',
                'Loperamida 2 mg conforme necessidade, máx 4 doses/dia — controle de episódios',
                'Probióticos: Lactobacillus rhamnosus GG ou Bifidobacterium infantis (evidência modesta)',
                'TCC (Terapia Cognitivo-Comportamental): evidência A para SII — encaminhar psicologia',
                'Colonoscopia NÃO necessária se calprotectina < 50 e sem alarmes',
            ]
            if piora_gluten:
                conduta_sii.append(
                    'Piora com glúten: solicitar tTG-IgA + IgA total (celíaca) ANTES de retirar glúten'
                )
            if medicamentos:
                conduta_sii.append(
                    f'Medicamentos suspeitos: {meds_txt or "não especificados"} — revisar e suspender/ajustar'
                )
            return {
                'categoria': 'diarreia_sii_d',
                'calprotectina': calproto,
                'desidratacao_grau': desat,
                'conduta': conduta_sii,
                'internacao': False,
            }

        # Zona cinzenta 50–200
        return {
            'categoria': 'diarreia_cronica_alarme_eletivo',
            'calprotectina': calproto,
            'zona_cinzenta': True,
            'desidratacao_grau': desat,
            'conduta': [
                f'Calprotectina fecal = {calproto} mcg/g — INDETERMINADA (50–200 mcg/g)',
                'Zona cinzenta: pode ser inflamação leve, AINEs, infecção recente ou DII inicial',
                'Suspender AINEs e repetir calprotectina em 4–6 semanas',
                'Hemograma + PCR + VHS + ferritina — excluir anemia e inflamação sistêmica',
                'Encaminhar Gastroenterologia eletivo se persistir',
                *sro,
            ],
            'exames': [
                'Repetir calprotectina em 4–6 semanas (sem AINEs)',
                'Hemograma', 'PCR', 'VHS', 'Ferritina',
            ],
            'internacao': False,
        }

    # 7c. Alarmes eletivos (sem calprotectina disponível)
    alarmes_eletivos = []
    if perda_peso: alarmes_eletivos.append('perda de peso involuntária')
    if anemia:     alarmes_eletivos.append('anemia / palidez')
    if hf_ccr:     alarmes_eletivos.append('história familiar de CCR ou DII')
    if nocturna:   alarmes_eletivos.append('diarreia noturna')
    if idade >= 50: alarmes_eletivos.append(f'idade ≥ 50 anos ({idade}a)')

    if alarmes_eletivos:
        conduta_elet = [
            'Diarreia crônica com alarmes — colonoscopia eletiva indicada',
            'Alarmes: ' + ', '.join(alarmes_eletivos),
            'Encaminhar Gastroenterologia — colonoscopia eletiva (< 8 semanas)',
            'Hemograma + PCR + VHS + ferritina + CEA + albumina',
            'Calprotectina fecal — solicitar como biomarker pré-colonoscopia',
        ]
        if piora_gluten:
            conduta_elet.append(
                'Piora com glúten: solicitar tTG-IgA + IgA total ANTES de retirar glúten da dieta'
            )
        if medicamentos:
            conduta_elet.append(f'Revisar medicamentos: {meds_txt or "não especificados"}')
        return {
            'categoria': 'diarreia_cronica_alarme_eletivo',
            'alarmes': alarmes_eletivos,
            'desidratacao_grau': desat,
            'conduta': conduta_elet,
            'exames': [
                'Hemograma', 'PCR/VHS', 'Ferritina', 'CEA', 'Albumina',
                'Calprotectina fecal',
                'tTG-IgA + IgA total (se suspeita celíaca)',
            ],
            'internacao': desat == 'grave',
        }

    # 7d. Crônica sem alarmes, sem calprotectina — SII-D provável empírico
    conduta_empirica = [
        'Diarreia crônica sem alarmes — padrão funcional (SII-D provável)',
        'Solicitar calprotectina fecal para confirmar exclusão de DII (< 50 mcg/g exclui com VPN 98%)',
        'Dieta Low-FODMAP por 6–8 semanas (reduz sintomas em ~70%)',
        'Antiespasmódicos: Butilescopolamina 10 mg TID ou Mebeverina 135 mg TID',
        'Loperamida 2 mg conforme necessidade — controle de episódios',
        'TCC: evidência A para SII — encaminhar psicologia',
    ]
    if piora_gluten:
        conduta_empirica.append(
            'Piora com glúten: solicitar tTG-IgA + IgA total ANTES de retirar glúten'
        )
    if medicamentos:
        conduta_empirica.append(
            f'Medicamentos suspeitos: {meds_txt or "não especificados"} — suspender/ajustar'
        )
    return {
        'categoria': 'diarreia_sii_d',
        'calprotectina': None,
        'desidratacao_grau': desat,
        'conduta': conduta_empirica,
        'pendente': 'Solicitar calprotectina fecal para confirmar exclusão de DII',
        'internacao': False,
    }
