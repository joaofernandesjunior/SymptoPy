# modules/raciocinio/tosse/engine_tosse.py
# Motor de raciocínio clínico — Tosse
#
# Roteador 0: imunossupressão (PCP/TB atípica antes de tudo)
# Roteador 1: duração → aguda | subaguda | crônica
# Crônica: Algoritmo de Irwin (IECA → UACS → Asma → DRGE/LPR → TB → Neoplasia)
#
# Categorias únicas:
#   tosse_aguda_viral | tosse_aguda_bacteriana | tosse_pertussis_suspeita
#   tosse_subaguda_pos_infecciosa | tosse_ieca | tosse_uacs
#   tosse_asma_variante | tosse_drge_lpr | tosse_tb_suspeita
#   tosse_pneumonia_atipica | tosse_pcp_suspeita | tosse_neoplasia_suspeita
#   investigar_tosse_cronica


# =============================================================================
# IMUNOSSUPRESSÃO — flags transversais
# =============================================================================

def _avaliar_imunossupressao(dados):
    flags = []

    hiv = dados.get('hiv_diagnosticado')
    em_tarv = dados.get('hiv_em_tarv')
    cd4 = dados.get('cd4_valor')

    if hiv:
        if not em_tarv:
            flags.append({
                'achado': 'HIV diagnosticado sem TARV',
                'urgencia': 'urgente',
                'acao': 'Iniciar investigação imediata para infecções oportunistas (PCP, TB, MAC). Encaminhar infectologia.',
            })
        elif cd4 is not None and cd4 < 200:
            flags.append({
                'achado': f'HIV em TARV com CD4 = {cd4} céls/mm³ (< 200)',
                'urgencia': 'urgente',
                'acao': 'CD4 crítico — risco elevado de PCP e outras oportunistas. Profilaxia com SMX-TMP se não em uso.',
            })
    elif dados.get('hiv_fatores_risco') and not dados.get('hiv_testado_recente'):
        flags.append({
            'achado': 'Fatores de risco para HIV sem testagem recente',
            'urgencia': 'atenção',
            'acao': 'Solicitar anti-HIV. Quadro de tosse seca + dispneia progressiva em paciente não testado exige exclusão de PCP.',
        })

    if dados.get('corticoide_cronico'):
        flags.append({
            'achado': 'Corticosteroide sistêmico crônico (> 3 meses)',
            'urgencia': 'atenção',
            'acao': 'Risco aumentado de PCP, Aspergillus e TB. Considerar profilaxia com SMX-TMP se prednisona ≥ 20 mg/dia.',
        })

    if dados.get('imunossupressao_outro'):
        flags.append({
            'achado': 'Imunossupressão por transplante / quimioterapia / biológico',
            'urgencia': 'atenção',
            'acao': 'Investigar infecção oportunista — escopo depende do agente imunossupressor.',
        })

    if dados.get('contato_tb'):
        flags.append({
            'achado': 'Contato confirmado com caso de tuberculose',
            'urgencia': 'atenção',
            'acao': 'ILTB: PPD + IGRA. Tratamento da ILTB se positivo (Isoniazida 6 meses ou Rifampicina 4 meses).',
        })

    return {'flags': flags}


def _suspeita_pcp(dados, imuno):
    """PCP: tosse seca + dispneia progressiva + imunossupressão (sem febrão)."""
    imuno_presente = dados.get('imunossuprimido') or any(
        f['urgencia'] == 'urgente' for f in imuno.get('flags', [])
    )
    tosse_seca = not dados.get('tosse_produtiva')
    dispneia_prog = dados.get('dispneia_progressiva')
    sem_febre_alta = not dados.get('febre_alta')

    return imuno_presente and tosse_seca and dispneia_prog and sem_febre_alta


# =============================================================================
# TOSSE AGUDA (<3 semanas)
# =============================================================================

def _avaliar_aguda(dados, imuno):
    # Pertussis (prioridade sobre bacteriana)
    pertussis_score = 0
    if dados.get('tosse_paroxistica'):    pertussis_score += 4
    if dados.get('guincho_inspiratorio'): pertussis_score += 4
    if dados.get('vomito_pos_tosse'):     pertussis_score += 2
    if dados.get('contato_pertussis'):    pertussis_score += 3
    if dados.get('duracao_semanas', 0) >= 2: pertussis_score += 1

    if pertussis_score >= 6:
        return {
            'categoria': 'tosse_pertussis_suspeita',
            'red_flags': imuno,
            'hipotese': 'Coqueluche (Bordetella pertussis) — suspeita',
            'score': pertussis_score,
            'positivos': _listar_positivos_pertussis(dados),
            'conduta': [
                'Azitromicina 500 mg/dia por 5 dias (reduz transmissão, não resolve sintomas na fase paroxística)',
                'Isolamento respiratório por 5 dias após início do ATB (ou 3 semanas se sem ATB)',
                'PCR nasofaringe para confirmação diagnóstica',
                'Notificação compulsória obrigatória — SINAN',
                'Investigar vacinação (dTpa) e contatos — comunicantes devem receber quimioprofilaxia',
            ],
            'encaminhar': 'Vigilância epidemiológica. Lactentes com tosse paroxística: PS urgente.',
        }

    # Pneumonia bacteriana
    bacteriana_score = 0
    if dados.get('febre_alta'):               bacteriana_score += 3
    if dados.get('estertores_ausculta'):      bacteriana_score += 4
    if dados.get('expectoracao_purulenta'):   bacteriana_score += 2
    if dados.get('dor_pleuritica'):           bacteriana_score += 2
    if dados.get('dispneia_progressiva'):     bacteriana_score += 1
    if dados.get('saturacao_baixa'):          bacteriana_score += 3
    if dados.get('imunossuprimido'):          bacteriana_score += 2

    if bacteriana_score >= 6:
        return {
            'categoria': 'tosse_aguda_bacteriana',
            'red_flags': imuno,
            'hipotese': 'Pneumonia Bacteriana — provável',
            'score': bacteriana_score,
            'positivos': _listar_positivos_bacteriana(dados),
            'conduta': [
                'RX de tórax (PA + perfil) — confirmar consolidação e extensão',
                'Hemograma + PCR + creatinina + ureia (CURB-65 / PSI)',
                'Hígido SEM comorbidades: Amoxicilina 1 g 8/8h VO × 5–7 dias '
                '(1ª linha — ATS/IDSA 2019; macrolídeo NÃO é 1ª linha por resistência pneumocócica > 30%)',
                'COM comorbidades (DM, DRC, ICC, DPOC, tabagismo, neoplasia, ATB < 3 meses): '
                'Amox/Clavulanato 875/125 mg 12/12h + Azitromicina 500 mg/dia × 5 dias',
                'Suspeita de atípica (jovem, intersticial, sem expectoração, sem toxemia): '
                'Azitromicina 500 mg/dia × 5d OU Doxiciclina 100 mg 12/12h × 7d',
                'Alergia a penicilina: Levofloxacino 750 mg/dia × 5 dias',
                'CURB-65: 0–1 → ambulatorial | 2 → ponderar internação | ≥ 3 → internar | ≥ 5 → avaliar UTI',
            ],
            'internacao': dados.get('saturacao_baixa') or dados.get('febre_alta'),
        }

    # Viral — bronquite aguda (produtiva) ou IVAS (seca). Diagnóstico por exclusão
    # de pneumonia/pertussis: rótulo conservador + ressalvas explícitas.
    produtiva = dados.get('tosse_produtiva') or dados.get('expectoracao_purulenta')
    semanas = dados.get('duracao_semanas', 0) or 0
    quase_pertussis = pertussis_score >= 4  # paroxística/duração sem cruzar o limiar

    if produtiva:
        hipotese = 'Bronquite Aguda (provável viral) — autolimitada'
        positivos = ['Tosse produtiva sem critérios de pneumonia '
                     f'(score bacteriano {bacteriana_score}/6) — escarro purulento NÃO '
                     'indica antibiótico isoladamente']
    else:
        hipotese = 'Infecção Viral de Vias Aéreas Superiores'
        positivos = ['Quadro autolimitado, sem critérios de gravidade']

    ressalvas = []
    if quase_pertussis:
        ressalvas.append(
            '⚠️ Tosse paroxística' + (f' há {semanas} semanas' if semanas >= 2 else '') +
            ' — considerar COQUELUCHE (PCR nasofaringe; azitromicina empírica se '
            'epidemiologia/contato; notificar).')
    ressalvas.append(
        '⚠️ Reavaliar PNEUMONIA se surgirem estertores localizados, dor pleurítica, '
        'taquipneia (FR ≥ 24) ou SpO₂ < 94% — o exame físico mudou a hipótese.')

    return {
        'categoria': 'tosse_aguda_viral',
        'red_flags': imuno,
        'hipotese': hipotese,
        'score': bacteriana_score,
        'positivos': positivos,
        'ressalvas': ressalvas,
        'conduta': [
            'Tratamento sintomático: analgésico/antitérmico (paracetamol 500–1000 mg 6/6h)',
            'Hidratação oral adequada',
            'Mel 1 colher de sobremesa antes de dormir (evidência para alívio da tosse — adultos)',
            'Não indicar antibiótico — sem critérios de infecção bacteriana',
            'Retorno se febre > 5 dias, piora do estado geral, dispneia ou hemoptise',
            'Se influenza + grupo de risco + início < 48h: Oseltamivir 75 mg 12/12h por 5 dias',
        ],
        'alerta_influenza': dados.get('mialgia_intensa') and not dados.get('vacinado_influenza'),
    }


def _listar_positivos_pertussis(dados):
    r = []
    if dados.get('tosse_paroxistica'):    r.append('Tosse em acessos paroxísticos')
    if dados.get('guincho_inspiratorio'): r.append('Guincho inspiratório (whoop) após os acessos')
    if dados.get('vomito_pos_tosse'):     r.append('Vômito pós-tosse')
    if dados.get('contato_pertussis'):    r.append('Contato com caso suspeito de coqueluche')
    return r


def _listar_positivos_bacteriana(dados):
    r = []
    if dados.get('febre_alta'):             r.append('Febre ≥ 38.5 °C')
    if dados.get('estertores_ausculta'):    r.append('Estertores crepitantes à ausculta')
    if dados.get('expectoracao_purulenta'): r.append('Expectoração purulenta')
    if dados.get('dor_pleuritica'):         r.append('Dor pleurítica')
    if dados.get('saturacao_baixa'):        r.append('SatO₂ < 94%')
    return r


# =============================================================================
# TOSSE SUBAGUDA (3–8 semanas)
# =============================================================================

def _avaliar_subaguda(dados, imuno):
    if dados.get('piora_progressiva'):
        # Redireciona para crônica
        return _avaliar_cronica(dados, imuno)

    positivos = []
    if dados.get('infeccao_recente_precedeu'): positivos.append('IVRS precedente nas últimas 8 semanas')
    if dados.get('chiado_novo'):               positivos.append('Chiado novo (hiper-reatividade brônquica pós-infecciosa)')
    if dados.get('tosse_paroxistica'):         positivos.append('Acessos paroxísticos — pertussis tardio a excluir')

    return {
        'categoria': 'tosse_subaguda_pos_infecciosa',
        'red_flags': imuno,
        'hipotese': 'Tosse Subaguda Pós-Infecciosa (hiper-reatividade transitória)',
        'positivos': positivos or ['Quadro subagudo sem critérios de gravidade'],
        'conduta': [
            'Expectativa ativa — maioria resolve espontaneamente em 8 semanas',
            'Se chiado associado: salbutamol spray 2–4 jatos SOS (hiper-reatividade transitória)',
            'Se paroxísticos: considerar Bordetella pertussis — PCR nasofaringe + Azitromicina empírica',
            'Se sem melhora em 8 semanas ou piora: investigar como tosse crônica (Irwin)',
        ],
        'alerta_pertussis': dados.get('tosse_paroxistica'),
    }


# =============================================================================
# TOSSE CRÔNICA — IRWIN SEQUENCIAL (≥8 semanas)
# =============================================================================

def _score_ieca(dados):
    score = 0
    positivos = []
    if dados.get('uso_ieca'):
        score += 5
        positivos.append(f'Uso de IECA ({dados.get("ieca_qual", "não especificado")})')
    if dados.get('tosse_inicio_apos_ieca'):
        score += 4
        positivos.append('Tosse iniciou após início do IECA (relação temporal)')
    if not dados.get('tosse_produtiva'):
        score += 1
        positivos.append('Tosse seca (padrão típico de IECA)')
    forca = 'alta' if score >= 8 else 'moderada' if score >= 5 else 'baixa'
    return {
        'nome': 'tosse_ieca', 'hipotese': 'Tosse por IECA',
        'score': score, 'forca': forca, 'positivos': positivos,
        'conduta_nao_farmacologica': [
            'Suspender IECA — substituir por ARA-II (losartana, valsartana, candesartana)',
            'Tosse cessa em 1–4 semanas após suspensão (confirma diagnóstico retrospectivamente)',
        ],
        'farmacologico': [
            'Sem farmacoterapia adicional para a tosse — resolução com suspensão do IECA',
            'Losartana 50 mg/dia como substituto (mesma indicação cardiovascular)',
        ],
    }


def _score_uacs(dados):
    score = 0
    positivos = []
    if dados.get('sensacao_gotejamento'):     score += 3; positivos.append('Sensação de gotejamento pós-nasal')
    if dados.get('clearing_frequente'):       score += 2; positivos.append('Pigarro / clearing frequente da garganta')
    if dados.get('piora_deitado_noturno'):    score += 2; positivos.append('Piora ao deitar (drena mais na posição horizontal)')
    if dados.get('rinite_sinusite_assoc'):    score += 2; positivos.append('Rinite ou sinusite associada')
    if dados.get('voz_anasalada'):            score += 1; positivos.append('Voz anasalada / obstrução nasal')
    if dados.get('descarga_posterior_vista'): score += 3; positivos.append('Descarga posterior visível ao exame da orofaringe')
    forca = 'alta' if score >= 8 else 'moderada' if score >= 4 else 'baixa'
    return {
        'nome': 'tosse_uacs', 'hipotese': 'UACS — Síndrome da Tosse de Vias Aéreas Superiores (Gotejamento Pós-Nasal)',
        'score': score, 'forca': forca, 'positivos': positivos,
        'conduta_nao_farmacologica': [
            'Lavagem nasal com soro fisiológico 0,9% — 2 a 3× ao dia',
            'Evitar alérgenos e irritantes nasais conhecidos',
        ],
        'farmacologico': [
            'Anti-histamínico de 1ª geração: clorfeniramina 4 mg 8/8h ou prometazina 25 mg à noite',
            '(Loratadina e cetirizina NÃO funcionam para UACS — sem efeito anticolinérgico central)',
            'Corticosteroide nasal: budesonida 64 mcg ou mometasona 50 mcg — 2 jatos/narina/dia',
            'Se sinusite bacteriana concomitante: amoxicilina 500 mg 8/8h por 10 dias',
            'Resposta esperada em 2–4 semanas',
        ],
    }


def _score_asma(dados):
    score = 0
    positivos = []
    if dados.get('piora_noturna_madrugada'): score += 3; positivos.append('Piora noturna / madrugada (padrão asmático)')
    if dados.get('piora_exercicio'):         score += 2; positivos.append('Piora com exercício (broncoespasmo induzido)')
    if dados.get('piora_frio_odores'):       score += 2; positivos.append('Piora com ar frio ou odores fortes')
    if dados.get('chiado_episodico'):        score += 2; positivos.append('Chiado episódico')
    if dados.get('historia_atopia'):         score += 2; positivos.append('Histórico de atopia (rinite / eczema / alergia)')
    if dados.get('asma_diagnosticada'):      score += 3; positivos.append('Asma já diagnosticada previamente')

    # Espirometria
    espiro = _interpretar_espirometria(dados)
    if espiro.get('realizada'):
        if espiro.get('obstrutivo_reversivel'):
            score += 5; positivos.append(f'Espirometria: {espiro["conclusao"]}')
        elif espiro.get('resposta_bd'):
            score += 3; positivos.append(f'Espirometria: {espiro["conclusao"]}')
        elif espiro.get('normal'):
            positivos.append('Espirometria normal — não exclui asma (trial com CI indicado)')

    forca = 'alta' if score >= 10 else 'moderada' if score >= 5 else 'baixa'
    return {
        'nome': 'tosse_asma_variante',
        'hipotese': 'Asma / Tosse Variante de Asma',
        'score': score, 'forca': forca, 'positivos': positivos,
        'espirometria': espiro,
        'conduta_nao_farmacologica': [
            'Evitar gatilhos identificados (exercício, frio, alérgenos)',
            'Técnica inalatória correta — conferir na consulta',
        ],
        'farmacologico': [
            'Corticosteroide inalatório (CI): budesonida 200–400 mcg/dia ou beclometasona 200–400 mcg/dia',
            'Trial de 4–8 semanas: resposta confirma diagnóstico',
            'Se sem controle com CI isolado: adicionar LABA (formoterol ou salmeterol)',
            'Salbutamol spray 2–4 jatos SOS (broncoespasmo agudo)',
            'DPOC concomitante (tabagista): LAMA (tiotrópio) + LABA, CI com cautela',
        ],
        'espiro_sugerida': not dados.get('espiro_realizada'),
    }


def _score_drge(dados):
    score = 0
    positivos = []
    tem_pirose = (dados.get('pirose_regurgitacao') or
                  dados.get('piora_pos_prandial') or
                  dados.get('piora_deitado_drge'))
    lpr_sem_pirose = dados.get('tosse_sem_pirose') and not tem_pirose

    if dados.get('pirose_regurgitacao'):   score += 3; positivos.append('Pirose ou regurgitação ácida')
    if dados.get('piora_pos_prandial'):    score += 3; positivos.append('Piora da tosse pós-prandial')
    if dados.get('piora_deitado_drge'):    score += 2; positivos.append('Piora ao deitar (refluxo noturno)')
    if dados.get('rouquidao_matinal'):     score += 3; positivos.append('Rouquidão matinal (LPR — sinal específico)')
    if dados.get('globus_faringeo'):       score += 2; positivos.append('Globus faríngeo (sensação de "caroço")')
    if dados.get('tosse_sem_pirose'):      score += 2; positivos.append('LPR silencioso — tosse sem pirose')

    forca = 'alta' if score >= 8 else 'moderada' if score >= 4 else 'baixa'

    if lpr_sem_pirose:
        # Evidência fraca para IBP empírico em LPR sem pirose (ACG 2022 / ACCP)
        farmacologico = [
            'LPR sem pirose: IBP empírico NÃO é 1ª linha — evidência insuficiente (ACG 2022)',
            'Priorizar medidas comportamentais por 8–12 semanas antes de qualquer trial medicamentoso',
            'Se optar por trial após falha comportamental: omeprazol 20 mg 2×/dia × 12–16 semanas',
            'Sem resposta em 16 semanas: pH-impedanciometria + laringoscopia para confirmação de LPR',
        ]
    else:
        # DRGE clássico com pirose: IBP recomendado
        farmacologico = [
            'IBP 2×/dia (antes das refeições): omeprazol 20 mg ou pantoprazol 40 mg',
            'DRGE: mínimo 8 semanas; reavaliação clínica após suspensão',
            'Resposta ao IBP confirma diagnóstico (trial terapêutico)',
        ]

    return {
        'nome': 'tosse_drge_lpr',
        'hipotese': ('LPR (Refluxo Laringofaríngeo) — sem pirose' if lpr_sem_pirose
                     else 'DRGE / LPR (Refluxo Laringofaríngeo)'),
        'score': score, 'forca': forca, 'positivos': positivos,
        'conduta_nao_farmacologica': [
            'Elevar cabeceira da cama 15–20 cm (DRGE noturno)',
            'Não deitar por 3h após refeições',
            'Evitar: cafeína, álcool, alimentos gordurosos, tabaco, chocolate, menta',
            'Refeições menores e mais frequentes',
            'Perda de peso se IMC elevado (reduz pressão no EEI)',
        ],
        'farmacologico': farmacologico,
    }


def _score_tb_atipica(dados):
    score = 0
    positivos = []
    semanas = dados.get('duracao_semanas', 0)
    if semanas >= 3:                             score += 2; positivos.append(f'Tosse ≥ 3 semanas ({semanas} sem) — critério PNCT')
    if dados.get('hemoptise'):                   score += 4; positivos.append('Hemoptise — red flag para TB e neoplasia')
    if dados.get('perda_peso_involuntaria'):      score += 3; positivos.append(f'Perda de peso involuntária ({dados.get("perda_peso_kg", "?")} kg)')
    if dados.get('sudorese_noturna'):            score += 3; positivos.append('Sudorese noturna (encharca o pijama)')
    if dados.get('contato_tb'):                  score += 4; positivos.append('Contato confirmado com tuberculose')
    if dados.get('imunossuprimido'):             score += 3; positivos.append('Imunossupressão — apresentação atípica de TB')
    if dados.get('inicio_insidioso_progressivo'):score += 2; positivos.append('Início insidioso e progressivo sem evento agudo')
    if dados.get('sem_febre_alta_quadro_prolongado'): score += 1; positivos.append('Quadro prolongado sem febre alta (atípica)')

    # Alta suspeita de TB × Pneumonia atípica
    tb_flags = sum([
        bool(dados.get('hemoptise')),
        bool(dados.get('perda_peso_involuntaria')),
        bool(dados.get('sudorese_noturna')),
        bool(dados.get('contato_tb')),
    ])
    categoria = 'tosse_tb_suspeita' if tb_flags >= 2 else 'tosse_pneumonia_atipica'

    forca = 'alta' if score >= 10 else 'moderada' if score >= 5 else 'baixa'

    conduta_tb = [
        'Escarro BAAR × 2 amostras (manhã de dias consecutivos) + cultura em LJ',
        'RX tórax: infiltrado em ápices, cavitações, linfonodos hilares',
        'Se imunossuprimido: atenção — TB pode ter apresentação atípica (BAAR falso-negativo)',
        'Notificação compulsória — SINAN (suspeita já notifica)',
        'Encaminhar para pneumologia / infectologia para tratamento (RIPE)',
    ]
    conduta_atipica = [
        'RX tórax: infiltrado intersticial bilateral, lobar ou segmentar',
        'Azitromicina 500 mg/dia por 5 dias (Mycoplasma / Chlamydophila / Legionella)',
        'Doxiciclina 100 mg 12/12h por 14 dias como alternativa',
        'Se Legionella suspeita (cooling towers, ar-condicionado): antígeno urinário',
    ]

    return {
        'nome': categoria,
        'hipotese': 'TB Pulmonar — suspeita' if categoria == 'tosse_tb_suspeita' else 'Pneumonia Atípica (Mycoplasma / Chlamydophila / Legionella)',
        'score': score, 'forca': forca, 'positivos': positivos,
        'conduta_nao_farmacologica': ['Isolamento respiratório até exclusão de TB'] if tb_flags >= 2 else [],
        'farmacologico': conduta_tb if categoria == 'tosse_tb_suspeita' else conduta_atipica,
        'encaminhar': 'Pneumologia / Infectologia' if categoria == 'tosse_tb_suspeita' else 'Retorno se sem melhora em 5–7 dias',
    }


def _score_neoplasia(dados):
    score = 0
    positivos = []
    maco_ano = dados.get('tabagismo_maco_ano', 0)
    idade = dados.get('idade', 0)

    if maco_ano >= 20:                           score += 4; positivos.append(f'Tabagismo {maco_ano} maços-ano (alto risco)')
    elif maco_ano > 0:                           score += 2; positivos.append(f'Tabagismo {maco_ano} maços-ano')
    if idade >= 45:                              score += 2; positivos.append(f'Idade {idade} anos (faixa de risco)')
    if dados.get('hemoptise'):                   score += 5; positivos.append('Hemoptise — sinal de alarme para neoplasia')
    if dados.get('mudanca_padrao_tosse'):         score += 3; positivos.append('Mudança no padrão habitual da tosse')
    if dados.get('perda_peso_involuntaria'):      score += 3; positivos.append('Perda de peso involuntária')
    if dados.get('adenopatia_percebida'):         score += 4; positivos.append('Adenopatia supraclavicular / cervical / axilar')
    if dados.get('dor_toracica_persistente'):     score += 3; positivos.append('Dor torácica persistente')
    if dados.get('rouquidao_persistente'):        score += 2; positivos.append('Rouquidão persistente > 3 semanas')
    if dados.get('disfagia'):                     score += 2; positivos.append('Disfagia associada')

    forca = 'alta' if score >= 12 else 'moderada' if score >= 6 else 'baixa'
    return {
        'nome': 'tosse_neoplasia_suspeita',
        'hipotese': 'Suspeita de Neoplasia Pulmonar',
        'score': score, 'forca': forca, 'positivos': positivos,
        'conduta_nao_farmacologica': [
            'RX tórax (PA + perfil) — urgente',
            'CT tórax com contraste se RX anormal ou suspeita mantida',
        ],
        'farmacologico': ['Sem farmacoterapia até diagnóstico — não adiar investigação por tratar sintomaticamente'],
        'encaminhar': 'Pneumologia / Oncologia torácica — urgente se adenopatia, hemoptise ou massa visível',
        'imagem': 'RX tórax urgente → CT tórax → broncoscopia / biopsia conforme achado',
    }


# =============================================================================
# ESPIROMETRIA — INTERPRETAÇÃO AUTOMÁTICA
# =============================================================================

def _interpretar_espirometria(dados):
    if not dados.get('espiro_realizada'):
        return {'realizada': False}

    vef1_cvf_pre  = dados.get('vef1_cvf_pre') or 0
    vef1_cvf_pos  = dados.get('vef1_cvf_pos') or 0
    delta_vef1    = dados.get('delta_vef1_pct') or 0

    obstrutivo         = vef1_cvf_pre < 0.70
    reversivel         = delta_vef1 >= 12 and delta_vef1 > 0
    resposta_bd_apenas = (not obstrutivo) and reversivel
    normal             = not obstrutivo and not reversivel

    if obstrutivo and reversivel:
        conclusao = 'Obstrução reversível — compatível com ASMA'
        padrao = 'obstrutivo_reversivel'
    elif obstrutivo and not reversivel:
        conclusao = 'Obstrução fixa — compatível com DPOC (ou asma não controlada)'
        padrao = 'obstrutivo_fixo'
    elif resposta_bd_apenas:
        conclusao = 'Espirometria normal com resposta ao broncodilatador — considerar asma variante / tosse'
        padrao = 'normal_com_resposta'
    else:
        conclusao = 'Espirometria normal — não exclui asma intermitente/leve. Trial com CI por 4–8 semanas.'
        padrao = 'normal'

    return {
        'realizada': True,
        'vef1_cvf_pre': vef1_cvf_pre,
        'vef1_cvf_pos': vef1_cvf_pos,
        'delta_vef1_pct': delta_vef1,
        'laudo_medico': dados.get('laudo_espiro', ''),
        'obstrutivo_reversivel': obstrutivo and reversivel,
        'obstrutivo_fixo': obstrutivo and not reversivel,
        'resposta_bd': reversivel,
        'normal': normal,
        'padrao': padrao,
        'conclusao': conclusao,
    }


# =============================================================================
# CRÔNICA — INTEGRAÇÃO
# =============================================================================

def _avaliar_cronica(dados, imuno):
    hipoteses = []

    for fn in [_score_ieca, _score_uacs, _score_asma, _score_drge, _score_tb_atipica, _score_neoplasia]:
        h = fn(dados)
        if h['score'] > 0:
            hipoteses.append(h)

    hipoteses.sort(key=lambda x: x['score'], reverse=True)
    provaveis = [h for h in hipoteses if h['forca'] in ('alta', 'moderada')]
    possiveis  = [h for h in hipoteses if h['forca'] == 'baixa']

    if not hipoteses:
        return {
            'categoria': 'investigar_tosse_cronica',
            'red_flags': imuno,
            'hipoteses_provaveis': [],
            'hipoteses_possiveis': [],
            'mensagem': (
                'Tosse crônica sem causa identificada pelos dados disponíveis. '
                'Seguir algoritmo de Irwin: trial sequencial IECA → UACS (anti-histamínico 1G) '
                '→ Asma (CI 4–8 semanas) → DRGE (IBP 8 semanas). '
                'Considerar BENA (bronquite eosinofílica não-asmática) se refratária.'
            ),
            'espirometria': _interpretar_espirometria(dados),
        }

    categoria_principal = hipoteses[0]['nome']

    # Neoplasia ou TB de alta força sobrepõe qualquer outra como categoria
    for h in hipoteses:
        if h['nome'] in ('tosse_neoplasia_suspeita', 'tosse_tb_suspeita') and h['forca'] == 'alta':
            categoria_principal = h['nome']
            break

    return {
        'categoria': categoria_principal,
        'red_flags': imuno,
        'hipoteses_provaveis': provaveis,
        'hipoteses_possiveis': possiveis,
        'espirometria': _interpretar_espirometria(dados),
    }


# =============================================================================
# PRESCRIÇÕES ESTRUTURADAS — enriquecimento pós-categorização
# =============================================================================

def _sintomaticos_tosse(dados):
    """
    Árvore de decisão de sintomáticos por TIPO de tosse (PA adulto):
      - Seca irritativa pós-viral → antitussígeno (Levodropropizina periférico / Dextrometorfano central)
      - Produtiva com muco espesso → mucolítico (Acetilcisteína / Ambroxol) + pilar hidratação
    Trava Beers (≥ 65 anos): alerta contra anti-histamínicos de 1ª geração como sedativo de tosse.
    Retorna (lista_rx, lista_alertas_plano).
    """
    rx, alertas = [], []
    try:
        idade = int(dados.get('idade', 0) or 0)
    except (ValueError, TypeError):
        idade = 0
    produtiva = dados.get('tosse_produtiva')

    if produtiva:
        rx.append({
            'linha':       'Sintomático — mucolítico/fluidificante (tosse produtiva)',
            'medicamento': 'Acetilcisteína',
            'prescricoes': [{'quantidade': '5 sachês/comp.', 'unidade': '600 mg',
                             'posologia': 'Tomar 1 vez ao dia, dissolvido em água, por 5 a 7 dias.'}],
            'nota': 'PILAR PRINCIPAL é a HIDRATAÇÃO FLUIDA (≥ 2 L/dia) — o mucolítico é adjuvante. '
                    'Alternativa: Ambroxol 30 mg VO 8/8h. NÃO associar com antitussígeno (retém secreção).',
        })
        rx.append({
            'linha':       'Opção noturna — antitussígeno (se fase seca / tosse noturna incomodativa)',
            'medicamento': 'Levodropropizina',
            'prescricoes': [{'quantidade': '1 frasco', 'unidade': '60 mg (6 mg/mL)',
                             'posologia': 'Tomar 10 mL (60 mg) VO ao deitar, por até 5 dias.'}],
            'nota': 'Usar APENAS se a tosse seca noturna estiver atrapalhando o sono — '
                    'NÃO associar com acetilcisteína/ambroxol na mesma dose (risco de retenção de secreção). '
                    'Antitussígeno periférico (levodropropizina) — alternativa central: Dextrometorfano 15–30 mg.',
        })
    else:
        rx.append({
            'linha':       'Sintomático — antitussígeno (tosse seca irritativa)',
            'medicamento': 'Levodropropizina',
            'prescricoes': [{'quantidade': '1 frasco', 'unidade': '60 mg (6 mg/mL)',
                             'posologia': 'Tomar 10 mL (60 mg) VO a cada 8 horas, por até 7 dias.'}],
            'nota': 'Antitussígeno de ação PERIFÉRICA — menos sedação que os centrais. '
                    'Alternativa central: Dextrometorfano 15–30 mg 6/6h se disponível. '
                    'Reservar para tosse seca que atrapalha sono/atividades.',
        })

    if idade >= 65:
        alertas.append(
            '⚠️ ALERTA BEERS (≥ 65 anos): EVITAR anti-histamínicos de 1ª geração '
            '(dexclorfeniramina, prometazina, difenidramina) como sedativo da tosse — '
            'risco anticolinérgico: quedas, retenção urinária e delirium. '
            'Preferir antitussígeno periférico (levodropropizina).'
        )
        rx.append({
            'linha':       '⚠️ ALERTA BEERS — Idoso ≥ 65 anos',
            'medicamento': 'EVITAR anti-histamínico de 1ª geração',
            'prescricoes': [],
            'nota': 'Dexclorfeniramina/prometazina contraindicados como sedativo de tosse no idoso '
                    '(risco anticolinérgico: quedas, retenção urinária, delirium). '
                    'Usar levodropropizina (periférico) se antitussígeno necessário.',
        })

    return rx, alertas


def _enriquecer_tosse_rx(resultado, dados):
    """Adiciona prescricoes_estruturadas + orientacoes conforme categoria."""
    cat = resultado.get('categoria', '')

    # Categorias sem Rx ambulatorial (emergência / investigação especializada)
    if cat in {'tosse_pcp_suspeita', 'tosse_tb_suspeita',
               'tosse_neoplasia_suspeita', 'investigar_tosse_cronica'}:
        return

    # ── Coqueluche ───────────────────────────────────────────────────────────
    if cat == 'tosse_pertussis_suspeita':
        resultado['prescricoes_estruturadas'] = [{
            'linha':       '1ª linha — ATB (redução da transmissão)',
            'medicamento': 'Azitromicina',
            'prescricoes': [{'quantidade': '5 comprimidos', 'unidade': '500 mg',
                             'posologia': 'Tomar 1 comprimido ao dia por 5 dias.'}],
            'nota': 'ATB reduz a transmissão mas não encurta a fase paroxística. Iniciar até 3 semanas do início dos sintomas.',
        }]
        resultado['orientacoes'] = {
            'isolamento':     'Isolamento respiratório por 5 dias após início do ATB (ou 3 semanas se sem ATB).',
            'contatos':       'Comunicantes próximos devem receber quimioprofilaxia com Azitromicina — especialmente lactentes.',
            'sinais_retorno': 'Retornar imediatamente se: apneia, cianose pós-tosse ou qualquer criança < 1 ano com sintomas.',
        }
        return

    # ── Pneumonia bacteriana ─────────────────────────────────────────────────
    if cat == 'tosse_aguda_bacteriana':
        alergia = dados.get('alergia_penicilina', False)
        tem_comorbidade = any([
            dados.get('diabetes'), dados.get('drc'), dados.get('icc'),
            dados.get('dpoc'), dados.get('tabagismo_ativo'),
            dados.get('neoplasia'), dados.get('atb_recente_3m'), dados.get('imunossuprimido'),
        ])
        # Apresentação atípica: jovem, sem expectoração purulenta, sem estertores francos
        atipica = (not dados.get('expectoracao_purulenta') and
                   not dados.get('febre_alta') and
                   not dados.get('estertores_ausculta'))

        if alergia:
            rx = [{
                'linha':       'ATB — alergia à penicilina',
                'medicamento': 'Levofloxacino',
                'prescricoes': [{'quantidade': '5 comprimidos', 'unidade': '750 mg',
                                 'posologia': 'Tomar 1 comprimido ao dia por 5 dias.'}],
                'nota': 'Fluoroquinolona respiratória — cobre pneumococo resistente e atípicos.',
            }]
        elif atipica:
            rx = [{
                'linha':       '1ª linha — ATB (apresentação atípica)',
                'medicamento': 'Azitromicina',
                'prescricoes': [{'quantidade': '5 comprimidos', 'unidade': '500 mg',
                                 'posologia': 'Tomar 1 comprimido ao dia por 5 dias.'}],
                'nota': 'Cobre Mycoplasma, Chlamydophila e Legionella. Alternativa: Doxiciclina 100 mg 12/12h × 7 dias.',
            }]
        elif tem_comorbidade:
            rx = [
                {
                    'linha':       '1ª linha — ATB (com comorbidade)',
                    'medicamento': 'Amoxicilina-Clavulanato',
                    'prescricoes': [{'quantidade': '14 comprimidos', 'unidade': '875/125 mg',
                                     'posologia': 'Tomar 1 comprimido a cada 12 horas por 7 dias — com alimento.'}],
                    'nota': '',
                },
                {
                    'linha':       'Associar — cobertura de atípicos',
                    'medicamento': 'Azitromicina',
                    'prescricoes': [{'quantidade': '5 comprimidos', 'unidade': '500 mg',
                                     'posologia': 'Tomar 1 comprimido ao dia por 5 dias (em paralelo com Amox-Clav).'}],
                    'nota': 'Dupla cobertura em comorbidades — ATS/IDSA 2019.',
                },
            ]
        else:
            rx = [{
                'linha':       '1ª linha — ATB (hígido, sem comorbidade)',
                'medicamento': 'Amoxicilina',
                'prescricoes': [{'quantidade': '21 cápsulas', 'unidade': '500 mg',
                                 'posologia': 'Tomar 2 cápsulas (1 g) a cada 8 horas por 5 a 7 dias.'}],
                'nota': 'Macrolídeo NÃO é 1ª linha — resistência pneumocócica > 30% no Brasil.',
            }]
        resultado['prescricoes_estruturadas'] = rx
        resultado['orientacoes'] = {
            'repouso':        'Repouso relativo até resolução da febre.',
            'hidratacao':     'Hidratação oral generosa — ao menos 2 litros por dia.',
            'sinais_retorno': 'Retornar se: piora após 48-72h com ATB, saturação < 95%, confusão mental ou febre > 5 dias.',
        }
        return

    # ── Viral aguda ──────────────────────────────────────────────────────────
    if cat == 'tosse_aguda_viral':
        rx = [{
            'linha':       '1ª linha — antipirético / analgésico',
            'medicamento': 'Paracetamol',
            'prescricoes': [{'quantidade': '20 comprimidos', 'unidade': '500 mg',
                             'posologia': 'Tomar 1 a 2 comprimidos (500-1000 mg) a cada 6 horas se febre ou mal-estar. Máx 4 g/dia.'}],
            'nota': 'Alternativa: Dipirona 500 mg 6/6h.',
        }]
        rx_sint, alertas = _sintomaticos_tosse(dados)
        rx.extend(rx_sint)
        resultado['prescricoes_estruturadas'] = rx
        if alertas:
            resultado['alertas_seguranca'] = alertas
        resultado['orientacoes'] = {
            'hidratacao':     'Ingerir ao menos 2 litros de líquidos por dia — líquidos quentes ajudam no conforto.',
            'mel':            'Mel de abelha puro: 1 colher de sobremesa antes de dormir — evidência para alívio da tosse em adultos.',
            'sinais_retorno': 'Retornar se: febre por mais de 5 dias, falta de ar, hemoptise ou piora após melhora.',
        }
        return

    # ── Subaguda pós-infecciosa ──────────────────────────────────────────────
    if cat == 'tosse_subaguda_pos_infecciosa':
        rx = []
        if dados.get('chiado_novo'):
            rx.append({
                'linha':       'Broncodilatador SOS (hiper-reatividade transitória)',
                'medicamento': 'Salbutamol spray',
                'prescricoes': [{'quantidade': '1 frasco', 'unidade': '100 mcg/jato',
                                 'posologia': '2 a 4 jatos inalados a cada 4-6 horas se chiado ou aperto no peito. Agitar antes de usar.'}],
                'nota': 'Hiper-reatividade transitória pós-infecciosa — tende a resolver em 4-8 semanas.',
            })
        rx_sint, alertas = _sintomaticos_tosse(dados)
        rx.extend(rx_sint)
        resultado['prescricoes_estruturadas'] = rx
        if alertas:
            resultado['alertas_seguranca'] = alertas
        resultado['orientacoes'] = {
            'expectativa':    'A tosse pós-viral tende a resolver sozinha em até 8 semanas — é esperada e não indica antibiótico.',
            'sinais_retorno': 'Retornar se: tosse persistir mais de 8 semanas, surgir hemoptise, perda de peso ou piora progressiva.',
        }
        return

    # ── Tosse por IECA ───────────────────────────────────────────────────────
    if cat == 'tosse_ieca':
        ieca_qual = dados.get('ieca_qual', 'IECA atual')
        resultado['prescricoes_estruturadas'] = [{
            'linha':       'Substituição do IECA — ARA-II',
            'medicamento': 'Losartana',
            'prescricoes': [{'quantidade': '30 comprimidos', 'unidade': '50 mg',
                             'posologia': 'Tomar 1 comprimido ao dia. Substitui o IECA com a mesma indicação cardiovascular.'}],
            'nota': f'Suspender {ieca_qual} ao iniciar. A tosse deve cessar em 1 a 4 semanas — confirma o diagnóstico retrospectivamente.',
        }]
        resultado['orientacoes'] = {
            'suspender_ieca': f'Suspender {ieca_qual} assim que iniciar Losartana.',
            'prazo':          'Tosse melhora em 1 a 4 semanas. Se não melhorar, investigar outra causa.',
        }
        return

    # ── UACS (gotejamento pós-nasal) ─────────────────────────────────────────
    if cat == 'tosse_uacs':
        resultado['prescricoes_estruturadas'] = [
            {
                'linha':       '1ª linha — anti-histamínico 1ª geração (UACS)',
                'medicamento': 'Clorfeniramina',
                'prescricoes': [{'quantidade': '30 comprimidos', 'unidade': '4 mg',
                                 'posologia': 'Tomar 1 comprimido a cada 8 horas. Pode causar sonolência — preferir à noite na 1ª semana.'}],
                'nota': 'Anti-histamínicos de 2ª geração (Loratadina, Cetirizina) NÃO funcionam para UACS — não têm efeito anticolinérgico.',
            },
            {
                'linha':       'Corticoide nasal (reduz descarga posterior)',
                'medicamento': 'Budesonida spray nasal',
                'prescricoes': [{'quantidade': '1 frasco', 'unidade': '64 mcg/jato',
                                 'posologia': '2 jatos em cada narina, 1 vez ao dia. Incline levemente a cabeça ao aplicar.'}],
                'nota': '',
            },
        ]
        resultado['orientacoes'] = {
            'lavagem_nasal':  'Lavagem nasal com soro fisiológico 0,9% — 2 a 3 vezes ao dia.',
            'prazo':          'Resposta esperada em 2 a 4 semanas. Manter mesmo com melhora parcial.',
            'sinais_retorno': 'Retornar em 4 semanas se sem melhora para investigar sinusite bacteriana.',
        }
        return

    # ── Asma / Tosse variante de asma ────────────────────────────────────────
    if cat == 'tosse_asma_variante':
        resultado['prescricoes_estruturadas'] = [
            {
                'linha':       '1ª linha — corticoide inalatório (trial diagnóstico-terapêutico)',
                'medicamento': 'Budesonida inalatória',
                'prescricoes': [{'quantidade': '1 inalador', 'unidade': '200 mcg/dose',
                                 'posologia': '1 a 2 inalações (200-400 mcg) 2 vezes ao dia. Bochechar com água após usar. Manter 4 a 8 semanas.'}],
                'nota': 'Resposta ao CI em 4-8 semanas confirma asma/tosse variante. Alternativa: Beclometasona 200-400 mcg/dia.',
            },
            {
                'linha':       'Broncodilatador de resgate SOS',
                'medicamento': 'Salbutamol spray',
                'prescricoes': [{'quantidade': '1 frasco', 'unidade': '100 mcg/jato',
                                 'posologia': '2 a 4 jatos inalados se chiado ou dispneia aguda. Agitar antes de usar.'}],
                'nota': 'Uso > 2×/semana indica controle insuficiente — revisar CI ou adicionar LABA.',
            },
        ]
        resultado['orientacoes'] = {
            'tecnica_inalatoria': 'Conferir técnica inalatória na consulta — erro de técnica é causa frequente de falha.',
            'gatilhos':           'Evitar gatilhos: poeira, mofo, pelos de animais, ar frio, exercício intenso, odores fortes.',
            'prazo':              'Retornar em 4 a 8 semanas para avaliação da resposta ao corticoide inalatório.',
        }
        return

    # ── DRGE / LPR ───────────────────────────────────────────────────────────
    if cat == 'tosse_drge_lpr':
        lpr_sem_pirose = (dados.get('tosse_sem_pirose') and
                          not dados.get('pirose_regurgitacao') and
                          not dados.get('piora_pos_prandial'))
        if lpr_sem_pirose:
            resultado['prescricoes_estruturadas'] = []
            resultado['orientacoes'] = {
                'medidas_comportamentais': (
                    'Não deitar por 3h após refeições, elevar cabeceira 15 cm, '
                    'evitar cafeína, álcool, alimentos gordurosos e tabaco.'
                ),
                'prazo':          'Medidas comportamentais por 8 a 12 semanas — evidência de IBP em LPR sem pirose é insuficiente (ACG 2022).',
                'sinais_retorno': 'Retornar em 8 semanas para reavaliação.',
            }
        else:
            resultado['prescricoes_estruturadas'] = [{
                'linha':       '1ª linha — IBP (DRGE com pirose)',
                'medicamento': 'Omeprazol',
                'prescricoes': [{'quantidade': '60 cápsulas', 'unidade': '20 mg',
                                 'posologia': 'Tomar 1 cápsula 30 min antes do café e 1 cápsula 30 min antes do jantar por 8 semanas.'}],
                'nota': 'Alternativa: Pantoprazol 40 mg 2×/dia. Resposta ao IBP confirma DRGE — trial terapêutico.',
            }]
            resultado['orientacoes'] = {
                'medidas_comportamentais': (
                    'Elevar cabeceira 15-20 cm, não deitar 3h após refeições, '
                    'refeições menores e frequentes, evitar cafeína, álcool e gordura.'
                ),
                'prazo':          'Mínimo 8 semanas de IBP. Reavaliar e tentar suspender gradualmente se sem sintomas.',
                'sinais_retorno': 'Retornar se: disfagia, hematemese, perda de peso ou sem melhora em 8 semanas.',
            }
        return

    # ── Pneumonia atípica ─────────────────────────────────────────────────────
    if cat == 'tosse_pneumonia_atipica':
        resultado['prescricoes_estruturadas'] = [{
            'linha':       '1ª linha — ATB (pneumonia atípica)',
            'medicamento': 'Azitromicina',
            'prescricoes': [{'quantidade': '5 comprimidos', 'unidade': '500 mg',
                             'posologia': 'Tomar 1 comprimido ao dia por 5 dias.'}],
            'nota': 'Alternativa: Doxiciclina 100 mg 12/12h × 7 dias. Cobre Mycoplasma, Chlamydophila e Legionella.',
        }]
        resultado['orientacoes'] = {
            'repouso':        'Repouso relativo — pneumonia atípica pode cursar com fadiga prolongada.',
            'sinais_retorno': 'Retornar se: piora após 48-72h com ATB, saturação < 95% ou febre > 5 dias.',
        }
        return


# =============================================================================
# PONTO DE ENTRADA
# =============================================================================

def interpretar_tosse(dados):
    imuno = _avaliar_imunossupressao(dados)

    # PCP — prioridade absoluta
    if _suspeita_pcp(dados, imuno):
        resultado = {
            'categoria': 'tosse_pcp_suspeita',
            'red_flags': imuno,
            'hipotese': 'PCP (Pneumocystis jirovecii) — suspeita',
            'positivos': [
                'Imunossupressão presente',
                'Tosse seca persistente',
                'Dispneia progressiva aos esforços',
                'Ausência de febre alta (apresentação insidiosa)',
            ],
            'conduta': [
                'PS URGENTE — risco de dessaturação rápida',
                'Gasometria arterial + LDH (elevada em PCP) + anti-HIV se desconhecido',
                'RX tórax: infiltrado intersticial bilateral em vidro-fosco (pode ser normal no início)',
                'TC tórax de alta resolução: mais sensível que RX',
                'Tratamento: SMX-TMP 15–20 mg/kg/dia (trimetoprim) VO/EV por 21 dias',
                'Se pO₂ < 70 mmHg ou gradiente A-a > 35: adicionar prednisona 40 mg 12/12h × 5 dias',
                'Não esperar confirmação para iniciar tratamento empírico',
            ],
        }
        _enriquecer_tosse_rx(resultado, dados)
        return resultado

    semanas = dados.get('duracao_semanas', 0)

    if semanas < 3:
        resultado = _avaliar_aguda(dados, imuno)
    elif semanas < 8:
        resultado = _avaliar_subaguda(dados, imuno)
    else:
        resultado = _avaliar_cronica(dados, imuno)

    _enriquecer_tosse_rx(resultado, dados)
    return resultado
