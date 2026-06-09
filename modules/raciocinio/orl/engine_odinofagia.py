# modules/raciocinio/orl/engine_odinofagia.py
# Motor de raciocínio clínico — Dor de Garganta / Odinofagia
#
# Hierarquia STEP (sintoma-guia transversal):
#   STEP 1  Red flags → PS / Urgência imediata
#   STEP 2  Agudo manejável na APS → prescrição imediata
#   STEP 3  Crônico / eletivo → encaminhamento
#
# Fontes:
#   - Critérios de Centor Modificados (McIsaac 1998, validação IDSA 2012)
#   - IDSA Clinical Practice Guideline — GABHS Pharyngitis (2012)
#   - Sociedade Brasileira de Infectologia — Faringoamigdalite (2024)
#   - CDC Treatment Guidelines — EBV/Mononucleose (2023)
#   - STEP 1: UpToDate — Peritonsillar Abscess + Epiglottitis (2024)


# =============================================================================
# HELPERS — PRESCRIÇÕES ESTRUTURADAS
# =============================================================================

def _rx(linha, medicamento, prescricoes, nota=None):
    return {'linha': linha, 'medicamento': medicamento,
            'prescricoes': prescricoes, 'nota': nota}


def _p(quantidade, unidade, posologia):
    return {'quantidade': quantidade, 'unidade': unidade, 'posologia': posologia}


# =============================================================================
# HELPERS — ACHADOS
# =============================================================================

def _achados(dados) -> list:
    a = []
    score = dados.get('centor_score', 0)
    a.append(f'Centor score: {score}/5')
    if dados.get('febre'):
        a.append(f'febre ({dados.get("temperatura_grau", "")})')
    if dados.get('exsudato_amigdaliano'):
        a.append('exsudato amigdaliano')
    if dados.get('adenopatia_cervical_ant'):
        a.append('adenopatia cervical anterior')
    if not dados.get('tosse'):
        a.append('tosse ausente')
    if dados.get('trismo'):
        a.append('TRISMO')
    if dados.get('sialorreia'):
        a.append('sialorreia')
    if dados.get('voz_batata'):
        a.append('voz "batata na boca"')
    if dados.get('desvio_uvula'):
        a.append('desvio de úvula')
    if dados.get('estridor'):
        a.append('ESTRIDOR')
    if dados.get('adenopatia_generalizada'):
        a.append('adenopatia generalizada')
    if dados.get('rouquidao'):
        a.append('rouquidão associada')
    return a


# =============================================================================
# STEP 1 — RED FLAGS / EMERGÊNCIAS
# =============================================================================

def _check_step1(dados) -> bool:
    return bool(
        dados.get('emergencia_respiratoria') or
        dados.get('abscesso_suspeito')
    )


def _resultado_step1(dados) -> dict:
    # Estridor / insuficiência respiratória > abscesso periamigdaliano
    if dados.get('emergencia_respiratoria'):
        cat       = 'orl_emergencia_respiratoria'
        diag      = 'Obstrução de Vias Aéreas — PS IMEDIATO'
        urgencia  = 'emergencia'
        raciocinio = (
            'Estridor inspiratório ou dificuldade respiratória associada a dor de garganta '
            '→ obstrução de via aérea superior iminente. '
            'Diagnósticos diferenciais críticos: epiglotite aguda, abscesso retrofaríngeo, '
            'angioedema grave, corpo estranho. '
            'Manipulação mínima da orofaringe — risco de laringoespasmo reflexo. '
            'Posição sentada com pescoço estendido. Oxigênio. PS imediato com cirurgião.'
        )
        conduta = [
            'Não deitar o paciente — manter posição sentada',
            'Oxigênio suplementar por máscara (se disponível)',
            'NÃO tentar abrir a boca com espátula (risco de laringoespasmo)',
            'Acionar SAMU / PS com leito de UTI — possível intubação de urgência',
        ]
        encaminhar = 'PA/PS com cirurgião de plantão — IMEDIATO'

    else:  # abscesso_suspeito
        cat       = 'orl_abscesso_periamigdaliano'
        diag      = 'Abscesso Periamigdaliano Suspeito — PS Urgente'
        urgencia  = 'urgente'
        sinais = []
        if dados.get('trismo'):         sinais.append('trismo')
        if dados.get('sialorreia'):     sinais.append('sialorreia')
        if dados.get('voz_batata'):     sinais.append('voz abafada')
        if dados.get('desvio_uvula'):   sinais.append('desvio de úvula')
        if dados.get('disfagia_saliva'): sinais.append('disfagia para saliva')
        raciocinio = (
            f'Dor de garganta com: {", ".join(sinais)} '
            '→ abscesso periamigdaliano até prova em contrário. '
            'Acúmulo de pus no espaço peritonsilar → trismo por espasmo do músculo pterigoideo. '
            'Risco de extensão para espaço retrofaríngeo (abscesso retrofaríngeo) e mediastinite. '
            'NÃO manejar ambulatorialmente.'
        )
        conduta = [
            'Não prescrever antibiótico oral e mandar para casa — risco de extensão',
            'Encaminhar PS/ORL urgente para drenagem cirúrgica',
            'Manter paciente em jejum (possível procedimento)',
        ]
        encaminhar = 'PS/Otorrinolaringologia — drenagem urgente'

    return {
        'tipo': 'orl', 'subtipo': 'odinofagia',
        'categoria': cat, 'diagnostico': diag,
        'urgencia': urgencia, 'raciocinio': raciocinio,
        'achados': _achados(dados), 'red_flags': [diag],
        'exames': [],
        'conduta': conduta,
        'prescricoes_estruturadas': [],
        'orientacoes': {},
        'encaminhar': encaminhar,
        'retorno': '',
    }


# =============================================================================
# STEP 2A — MONONUCLEOSE INFECCIOSA (antes de decidir ATB)
# =============================================================================

def _check_mono(dados) -> bool:
    """Mononucleose suspeita — impede uso de amoxicilina."""
    return bool(dados.get('mononucleose_suspeita') or dados.get('rash_apos_amox'))


def _resultado_mono(dados) -> dict:
    raciocinio = (
        'Exsudato amigdaliano + adenopatia generalizada + faixa etária 15–35 anos '
        + ('+ rash após amoxicilina (patognomônico de EBV + aminopenicilina) ' if dados.get('rash_apos_amox') else '') +
        '→ mononucleose infecciosa por EBV altamente suspeita. '
        'CRÍTICO: amoxicilina / ampicilina causam rash maculopapular em ~80% dos casos de EBV — '
        'NÃO prescrever. '
        'Monospot (teste de Paul-Bunnell) positivo em 85% após 1ª semana. '
        'Risco de rotura esplênica com esforço físico intenso — repouso de contato obrigatório.'
    )
    exames = [
        'Monospot (anticorpos heterófilos) — sensibilidade 85% após 7 dias de sintomas',
        'Hemograma com linfócitos atípicos (> 10% é sugestivo)',
        'TGO / TGP (hepatite por EBV em 80% dos casos — geralmente leve)',
        'Se Monospot negativo e sintomas persistem: IgM anti-VCA EBV (mais sensível)',
    ]
    prescricoes = [
        _rx('Analgesia / antitérmico', 'Paracetamol 750mg',
            [_p('30', 'comprimidos', '1 comp VO de 6/6h PRN — máx 4g/dia')],
            'Ibuprofeno é alternativa; evitar AAS (risco de Síndrome de Reye em < 18 anos).'),
    ]
    orientacoes = {
        'repouso': (
            'REPOUSO DE CONTATO obrigatório por 3–4 semanas (ou até confirmação de baço normal). '
            'SEM esportes de contato, lutas, futebol — risco de rotura esplênica.'
        ),
        'alimentacao': 'Dieta normal. Hidratação adequada. Evitar álcool (hepatite associada).',
        'retorno_medico': (
            'Retornar se: dor abdominal intensa súbita (rotura de baço — PS imediato), '
            'dificuldade para respirar, febre prolongada > 2 semanas.'
        ),
        'sinais_de_alerta': [
            'Dor abdominal súbita e intensa (rotura esplênica — PS IMEDIATO)',
            'Dificuldade para respirar ou engolir',
            'Febre persistindo > 2 semanas',
            'Icterícia (pele/olhos amarelos)',
        ],
    }
    return {
        'tipo': 'orl', 'subtipo': 'odinofagia',
        'categoria': 'orl_mononucleose',
        'diagnostico': 'Mononucleose Infecciosa Suspeita (EBV) — SEM amoxicilina',
        'urgencia': None, 'raciocinio': raciocinio,
        'achados': _achados(dados), 'red_flags': [],
        'exames': exames,
        'conduta': [
            '⚠️  NÃO prescrever amoxicilina, ampicilina ou derivados aminopenicilínicos',
            'Tratamento sintomático com paracetamol/ibuprofeno',
            'Repouso de contato 3–4 semanas (risco de rotura esplênica)',
        ],
        'prescricoes_estruturadas': prescricoes,
        'orientacoes': orientacoes,
        'encaminhar': 'Clínica médica / Infectologia se febre > 2 semanas ou hepatite grave',
        'retorno': 'Retorno em 7–10 dias. Monospot: repetir se negativo precocemente.',
    }


# =============================================================================
# STEP 2B — FARINGOAMIGDALITE (Centor)
# =============================================================================

def _resultado_faringoamigdalite(dados) -> dict:
    score    = dados.get('centor_score', 0)
    alerg    = dados.get('alergia_penicilina', False)
    alerg_g  = dados.get('alergia_penicilina_grave', False)  # anafilaxia

    # ── Probabilidade GAS por score ──────────────────────────────────────────
    if score >= 4:
        prob = '~56%'
        estrategia = 'tratar empiricamente (score ≥ 4)'
        cat  = 'orl_faringoamigdalite_bacteriana'
        diag = 'Faringoamigdalite Bacteriana (GAS) — Centor ≥ 4 → ATB'
        raciocinio = (
            f'Centor score {score}/5 (≥ 4): probabilidade de GAS ~56%. '
            'Critérios positivos: ' +
            ', '.join([
                c for c, v in [
                    ('febre', dados.get('febre')),
                    ('exsudato amigdaliano', dados.get('exsudato_amigdaliano')),
                    ('adenopatia cervical anterior', dados.get('adenopatia_cervical_ant')),
                    ('tosse ausente', not dados.get('tosse')),
                ] if v
            ]) + '. '
            'IDSA 2012 e SBI 2024: tratar empiricamente sem teste rápido se score ≥ 4.'
        )
        tratar = True

    elif score == 3:
        prob = '~32%'
        estrategia = 'tratar empiricamente (score 3 — SBI 2024) ou TRA se disponível'
        cat  = 'orl_faringoamigdalite_bacteriana'
        diag = 'Faringoamigdalite Bacteriana (GAS) — Centor 3 → ATB ou TRA'
        raciocinio = (
            f'Centor score {score}/5 (= 3): probabilidade de GAS ~32%. '
            'SBI 2024: score 3 → tratar empiricamente na APS sem TRA (custo-efetivo no Brasil). '
            'Alternativa: realizar Teste Rápido de Antígeno (TRA) se disponível — '
            'tratar se positivo, sintomático se negativo.'
        )
        tratar = True

    elif score == 2:
        prob = '~15%'
        estrategia = 'test-and-treat — TRA'
        cat  = 'orl_faringoamigdalite_test_treat'
        diag = 'Faringoamigdalite — Centor 2 → Teste Rápido Antígeno (TRA)'
        raciocinio = (
            f'Centor score {score}/5 (= 2): probabilidade de GAS ~15%. '
            'IDSA 2012: score 2 → realizar TRA. Se positivo → tratar; se negativo → sintomático. '
            'Probabilidade baixa, mas não desprezível — TRA evita antibiótico desnecessário '
            'e também não deixa GAS sem tratamento.'
        )
        tratar = False  # depende do TRA

    else:  # score ≤ 1
        prob = '< 10%'
        estrategia = 'viral — NÃO tratar com ATB'
        cat  = 'orl_faringoamigdalite_viral'
        diag = 'Faringoamigdalite Viral — Centor ≤ 1 → Sintomático'
        raciocinio = (
            f'Centor score {score}/5 (≤ 1): probabilidade de GAS < 10%. '
            'Etiologia viral (rinovírus, adenovírus, coronavírus) é a causa mais provável. '
            'Antibiótico NÃO indicado — sem benefício clínico e seleciona resistência. '
            'Tratamento sintomático completo com retorno se piora.'
        )
        tratar = False

    # ── Prescrições ──────────────────────────────────────────────────────────
    prescricoes = []

    if tratar:
        if not alerg:
            # Sem alergia: Penicilina G Benzatina IM ou Amoxicilina oral
            prescricoes.append(
                _rx('1ª linha — Dose Única', 'Penicilina G Benzatina 1.200.000 UI',
                    [_p('1', 'ampola', 'IM profunda, glúteo — DOSE ÚNICA')],
                    'Preferir IM: adesão máxima, sem resistência ao GAS. '
                    'Criança < 27kg: 600.000 UI. Agitar bem a ampola antes de aspirar.')
            )
            prescricoes.append(
                _rx('Alternativa oral × 10 dias', 'Amoxicilina 875mg',
                    [_p('20', 'comprimidos', '1 comp VO 12/12h × 10 dias')],
                    'Tomar até o fim do curso — mesmo sem sintomas — para evitar recidiva e '
                    'sequela reumática.')
            )

        elif not alerg_g:
            # Alergia não anafilática → Cefadroxila
            prescricoes.append(
                _rx('Alergia à penicilina (não anafilática)', 'Cefadroxila 500mg',
                    [_p('20', 'comprimidos', '1 comp VO 12/12h × 10 dias')],
                    'Cefalosporina 1ª geração com excelente atividade contra GAS. '
                    'Reatividade cruzada < 1% — segura em alergia não anafilática a penicilina.')
            )

        else:
            # Alergia grave / anafilaxia → Azitromicina
            prescricoes.append(
                _rx('Alergia grave à penicilina (anafilaxia)', 'Azitromicina 500mg',
                    [
                        _p('1', 'comp (D1)', '500mg VO — dia 1'),
                        _p('4', 'comp 250mg (D2–5)', '250mg VO — dias 2 a 5'),
                    ],
                    '⚠️  Resistência do GAS à azitromicina: 5–15% no Brasil. '
                    'Reavaliar em 72h — sem melhora indica falha ou etiologia viral.')
            )

    # Analgesia sempre
    prescricoes.append(
        _rx('Analgesia / antitérmico', 'Ibuprofeno 600mg',
            [_p('20', 'comprimidos', '1 comp VO 8/8h durante as refeições × 5 dias')],
            'Melhor analgesia para odinofagia que paracetamol. '
            'Substituir por Paracetamol 750mg 6/6h em gastrite ou gestantes.')
    )

    # ── Exames ───────────────────────────────────────────────────────────────
    if score == 2:
        exames = [
            'Teste Rápido de Antígeno (TRA) para Streptococcus pyogenes — decisivo para ATB',
        ]
    elif score <= 1:
        exames = []  # viral: sem exame necessário
    else:
        exames = [
            'TRA não obrigatório (score ≥ 3 → tratar empiricamente)',
            'Solicitar se dúvida diagnóstica ou preferência do paciente',
        ]

    # ── Orientações ──────────────────────────────────────────────────────────
    orientacoes = {
        'alivio_garganta': (
            'Gargarejos com água morna + 1 colher de chá de sal + gotas de limão, 3–4×/dia. '
            'Mel 1 colher de sobremesa puro ou no chá — efeito demulcente comprovado. '
            'Sorvete ou alimentos frios aliviam a dor (vasoconstrição local). '
            'Pastilhas de benzocaína PRN para anestesia local.'
        ),
        'hidratacao': (
            'Líquidos frios ou mornos abundantes (água, chá, caldo, suco sem ácido). '
            'Evitar cítricos (laranja, limão em excesso) — irritam a mucosa. '
            'Picolé de água/suco pode aliviar e hidratar ao mesmo tempo.'
        ),
        'atb_compliance': (
            'TOMAR O ANTIBIÓTICO ATÉ O FINAL mesmo que melhore antes. '
            'Parar antes favorece recidiva e pode levar à febre reumática.'
        ) if tratar and not alerg else None,
        'transmissao': (
            'Strep transmite por gotículas — lavar mãos, não compartilhar utensílios, '
            'afastamento escolar/trabalho enquanto febril (1ª noite de ATB geralmente resolve).'
        ) if tratar else None,
        'sinais_de_alerta': [
            'Dificuldade para respirar ou engolir (PS IMEDIATO)',
            'Dificuldade para abrir a boca (trismo) — PS',
            'Febre que não cede após 48–72h de ATB',
            'Dor de garganta piorando progressivamente',
            'Inchaço visível de um lado do pescoço',
        ],
    }
    # Remove None
    orientacoes = {k: v for k, v in orientacoes.items() if v}

    # ── Amigdalite recorrente ─────────────────────────────────────────────────
    encaminhar = None
    nota_recorrencia = ''
    if dados.get('atb_recente_30d') and tratar:
        nota_recorrencia = (
            'ATB recente em 30 dias: possível episódio recorrente. '
            'Critério de amigdalectomia: ≥ 7 episódios/ano OU ≥ 5 × 2 anos consecutivos. '
            'Registrar frequência e encaminhar ORL eletivo se critério atingido.'
        )
        encaminhar = 'ORL eletivo se critério de recorrência (≥ 7/ano ou ≥ 5 × 2 anos)'

    conduta_extra = []
    if nota_recorrencia:
        conduta_extra.append(nota_recorrencia)

    return {
        'tipo': 'orl', 'subtipo': 'odinofagia',
        'categoria': cat, 'diagnostico': diag,
        'urgencia': None, 'raciocinio': raciocinio,
        'achados': _achados(dados), 'red_flags': [],
        'exames': exames,
        'conduta': conduta_extra + (
            ['Suspender ATB ao final do curso completo — não interromper por melhora precoce']
            if tratar else ['Antibiótico NÃO indicado — não melhora desfecho viral']
        ),
        'prescricoes_estruturadas': prescricoes,
        'orientacoes': orientacoes,
        'encaminhar': encaminhar,
        'retorno': 'Retorno em 48–72h se sem melhora com ATB. PS se piora súbita.',
    }


# =============================================================================
# STEP 3 — ROUQUIDÃO CRÔNICA (gate: ≥ 3 semanas)
# =============================================================================

def _resultado_rouquidao_cronica(dados) -> dict:
    """Rouquidão ≥ 3 semanas — rastrear neoplasia de laringe."""
    raciocinio = (
        'Rouquidão / disfonia persistente ≥ 3 semanas → rastreio obrigatório de neoplasia de laringe. '
        'Fatores de risco: tabagismo (principal), etilismo, DRGE. '
        'Nasofibroscopia ou laringoscopia indireta é o padrão para visualização das pregas vocais. '
        'Encaminhamento ORL eletivo com urgência funcional (semanas, não meses).'
    )
    return {
        'tipo': 'orl', 'subtipo': 'odinofagia',
        'categoria': 'orl_disfonia_cronica',
        'diagnostico': 'Disfonia Persistente ≥ 3 Semanas — Rastrear Neoplasia de Laringe',
        'urgencia': 'urgente', 'raciocinio': raciocinio,
        'achados': _achados(dados), 'red_flags': ['Disfonia > 3 semanas em adulto'],
        'exames': ['Nasofibroscopia / laringoscopia indireta (ORL)'],
        'conduta': [
            'Encaminhar ORL — laringe visível com nasofibroscópio',
            'NÃO demorar: se neoplasia, estadiamento precoce muda prognóstico drasticamente',
            'Investigar DRGE como causa benigna (pH-metria / empírico com IBP × 8 semanas)',
        ],
        'prescricoes_estruturadas': [],
        'orientacoes': {
            'sinais_de_alerta': [
                'Piora progressiva da rouquidão',
                'Dor ao engolir persistente',
                'Perda de peso involuntária',
                'Nódulo palpável no pescoço',
            ],
        },
        'encaminhar': 'ORL — nasofibroscopia (prioridade semanas, não meses)',
        'retorno': 'Após consulta ORL.',
    }


# =============================================================================
# PONTO DE ENTRADA PRINCIPAL
# =============================================================================

def _centor_age_score(idade: int) -> int:
    """Modificador de idade — Centor Modificado (McIsaac 1998)."""
    if idade is None:
        return 0
    if 3 <= idade <= 14:
        return 1
    if 15 <= idade <= 44:
        return 0
    return -1  # ≥ 45 anos


def interpretar_odinofagia(dados: dict) -> dict:
    """
    Motor de raciocínio — Dor de Garganta / Odinofagia.

    STEP 1: Emergência respiratória / Abscesso periamigdaliano → PS
    STEP 2: Mononucleose suspeita → sintomático SEM amoxicilina
    STEP 2: Faringoamigdalite (Centor 0–5) → ATB ou sintomático
    STEP 3: Rouquidão ≥ 3 semanas → rastrear Ca laringe
    """
    # Recalcula centor_score a partir dos campos brutos se não vier pré-calculado
    # (segurança quando dados chegam via JSON sem passar pelo subjetivo interativo)
    if 'centor_score' not in dados:
        dados['centor_score'] = (
            (1 if dados.get('febre')                   else 0) +
            (1 if dados.get('exsudato_amigdaliano')    else 0) +
            (1 if dados.get('adenopatia_cervical_ant') else 0) +
            (1 if not dados.get('tosse')               else 0) +
            _centor_age_score(dados.get('idade'))
        )

    # STEP 1 — Red flags
    if _check_step1(dados):
        return _resultado_step1(dados)

    # STEP 2A — Mononucleose (antes de decidir antibiótico)
    if _check_mono(dados):
        return _resultado_mono(dados)

    # STEP 3 — Rouquidão crônica isolada (sem amigdalite franca)
    # Gate: rouquidão ≥ 3 semanas + centor score baixo (sintoma guia é a disfonia, não amigdalite)
    if dados.get('rouquidao_cronica') and dados.get('centor_score', 0) <= 1:
        return _resultado_rouquidao_cronica(dados)

    # STEP 2B — Faringoamigdalite (Centor)
    return _resultado_faringoamigdalite(dados)
