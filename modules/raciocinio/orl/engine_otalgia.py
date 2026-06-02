# modules/raciocinio/orl/engine_otalgia.py
# Motor de raciocínio clínico — Otalgia (Dor de Ouvido)
#
# Hierarquia STEP:
#   STEP 1  Mastoidite aguda → PS urgente
#   STEP 2  OMA (watchful waiting vs ATB) | Otite Externa | OE Maligna
#   STEP 2  DTM leve
#   STEP 3  Disfunção tuba de Eustáquio crônica (encaminhamento eletivo)
#
# Fontes:
#   - AAP Clinical Practice Guideline — AOM 2013 (reafirmado 2023)
#   - Open Evidence / AAP 2023: watchful waiting criteria inalterados
#   - AOE: Rosenfeld 2014 AAO-HNS + Open Evidence 2024
#   - DTM: AAOMS consensus (conservador APS)


# =============================================================================
# HELPERS
# =============================================================================

def _rx(linha, medicamento, prescricoes, nota=None):
    return {'linha': linha, 'medicamento': medicamento,
            'prescricoes': prescricoes, 'nota': nota}


def _p(quantidade, unidade, posologia):
    return {'quantidade': quantidade, 'unidade': unidade, 'posologia': posologia}


def _achados(dados) -> list:
    a = []
    lat = dados.get('lateralidade', '')
    if lat:
        a.append(f'otalgia {lat.lower()}')
    if dados.get('febre'):
        a.append(f'febre ({dados.get("temperatura_grau", "")})')
    if dados.get('trago_positivo'):
        a.append('trago positivo')
    if dados.get('mt_abaulada'):
        a.append('MT abaulada')
    if dados.get('mt_hiperemia'):
        a.append('MT hiperemiada')
    if dados.get('mt_perfurada'):
        a.append('MT perfurada')
    if dados.get('otorreia'):
        a.append(f'otorreia ({dados.get("otorreia_tipo", "").lower()})')
    if dados.get('hipoagusia'):
        a.append('hipoacusia ipsilateral')
    if dados.get('canal_edema'):
        a.append('canal edemaciado')
    if dados.get('dor_retroauricular'):
        a.append('DOR RETROAURICULAR')
    if dados.get('pavilhao_projetado'):
        a.append('pavilhão projetado')
    if dados.get('iras_recente'):
        a.append('IRAS recente')
    if dados.get('banho_piscina'):
        a.append('exposição à água')
    if dados.get('bruxismo'):
        a.append('bruxismo')
    if dados.get('click_mandibula'):
        a.append('click mandibular')
    return a


# =============================================================================
# STEP 1 — MASTOIDITE (PS URGENTE)
# =============================================================================

def _resultado_mastoidite(dados) -> dict:
    sinais = []
    if dados.get('dor_retroauricular'):   sinais.append('dor/eritema retroauricular')
    if dados.get('pavilhao_projetado'):   sinais.append('pavilhão projetado para frente')
    if dados.get('flutuacao_retroaur'):   sinais.append('flutuação retroauricular')
    if dados.get('febre_mais_72h_atb'):   sinais.append('febre persistindo após 72h de ATB')

    raciocinio = (
        f'Otalgia com: {", ".join(sinais)} '
        '→ mastoidite aguda até prova em contrário. '
        'Extensão da OMA para o processo mastóide (osso esponjoso retroauricular). '
        'Complicações: abscesso subperiosteal, meningite, trombose do seio lateral, abscesso cerebral. '
        'TC de mastóide confirma. ATB IV (ceftriaxona) + drenagem cirúrgica (mastoidectomia) conforme evolução. '
        'NÃO manejar ambulatorialmente.'
    )
    return {
        'tipo': 'orl', 'subtipo': 'otalgia',
        'categoria': 'orl_mastoidite',
        'diagnostico': 'Mastoidite Aguda Suspeita — PS Urgente',
        'urgencia': 'urgente', 'raciocinio': raciocinio,
        'achados': _achados(dados), 'red_flags': ['Mastoidite suspeita'],
        'exames': [],
        'conduta': [
            'Encaminhar PS/ORL — mastoidite requer ATB IV e possível cirurgia',
            'Não prescrever ATB oral e mandar para casa — risco de progressão',
        ],
        'prescricoes_estruturadas': [],
        'orientacoes': {},
        'encaminhar': 'PS/Otorrinolaringologia — urgente',
        'retorno': '',
    }


# =============================================================================
# STEP 2A — OE MALIGNA (NECROSANTE) — PS
# =============================================================================

def _resultado_oe_maligna(dados) -> dict:
    raciocinio = (
        'DM / imunodeficiência + otalgia intensa + canal edemaciado/estenótico '
        '→ suspeita de otite externa maligna (necrosante). '
        'Pseudomonas aeruginosa invade osso temporal → osteomielite da base do crânio. '
        'Mortalidade elevada se não tratada. '
        'TC de osso temporal + cintilografia óssea (diagnóstico). '
        'ATB antipseudomonal IV (ciprofloxacino IV ou cefalosporina antipseudomonal). '
        'Internação + ORL.'
    )
    return {
        'tipo': 'orl', 'subtipo': 'otalgia',
        'categoria': 'orl_otite_externa_maligna',
        'diagnostico': 'Otite Externa Maligna (Necrosante) Suspeita — Internação',
        'urgencia': 'urgente', 'raciocinio': raciocinio,
        'achados': _achados(dados), 'red_flags': ['OE maligna — DM + otalgia intensa'],
        'exames': [],
        'conduta': [
            'PS imediato — internação + TC osso temporal',
            'ATB IV antipseudomonal: Ciprofloxacino 400mg IV 12/12h ou Pip/Tazo',
            'ORL urgente para desbridamento e biópsia (excluir neoplasia)',
        ],
        'prescricoes_estruturadas': [],
        'orientacoes': {},
        'encaminhar': 'PS/ORL — internação urgente',
        'retorno': '',
    }


# =============================================================================
# STEP 2B — OTITE EXTERNA AGUDA (AOE)
# =============================================================================

def _resultado_otite_externa(dados) -> dict:
    mt_perf = dados.get('mt_perfurada', False)
    diabetes = dados.get('diabetes', False)

    raciocinio = (
        'Trago positivo' +
        (' + exposição à água (piscina/praia)' if dados.get('banho_piscina') else '') +
        (' + canal edemaciado' if dados.get('canal_edema') else '') +
        ' → otite externa aguda. '
        'Causa principal: Pseudomonas aeruginosa e Staphylococcus aureus. '
        'ATB tópico fluoroquinolônico é 1ª linha — eficácia igual a qualquer outra combinação, '
        'bidiário (melhor adesão), seguro mesmo se MT perfurada. '
        'Sistêmico: apenas se celulite se estendendo além do canal ou imunocomprometido.'
    )

    # Escolha da gota: cipro+dexa preferida (2×/dia, menor sensitização que neomicina)
    gota = 'Ciprofloxacino 0,3% + Dexametasona 0,1%'
    nota_gota = (
        'Seguro mesmo com MT perfurada. 4 gotas NO ouvido afetado, 2×/dia × 7 dias. '
        + ('Se canal muito edemaciado: inserir mechaozinho de gaze para facilitar entrada das gotas. '
           if dados.get('canal_estenose') else '') +
        'Manter ouvido seco — sem piscina/mergulho durante e 7 dias após.'
    )

    prescricoes = [
        _rx('Otológico tópico — 1ª linha', gota,
            [_p('1', 'frasco', '4 gotas no ouvido afetado, 2×/dia × 7 dias')],
            nota_gota),
        _rx('Analgesia', 'Ibuprofeno 600mg',
            [_p('14', 'comprimidos', '1 comp VO 8/8h durante as refeições × 5 dias')],
            'Otalgia da OE é intensa — AINE é superior a paracetamol para alívio.'),
    ]

    if diabetes:
        prescricoes.append(
            _rx('⚠️  ATENÇÃO — Diabético', 'Ciprofloxacino 500mg VO',
                [_p('14', 'comprimidos', '1 comp VO 12/12h × 7 dias')],
                'Diabético com OE: adicionar ATB sistêmico para cobrir extensão e evitar OE maligna. '
                'Controle glicêmico é essencial para resolução.')
        )

    orientacoes = {
        'ouvido_seco': (
            'OUVIDO SECO é regra número 1. Sem piscina, mergulho ou chuveiro no ouvido durante 7 dias + 7 dias após. '
            'No banho: tampão de algodão com vaselina na entrada do canal. '
            'Não usar secador de cabelo diretamente no ouvido.'
        ),
        'cotonete_proibido': (
            'NÃO usar cotonete — remove o cerume protetor e traumatiza o canal. '
            'Cotonete é a principal causa de otite externa.'
        ),
        'gotas': (
            'Aplicar as gotas deitado com o ouvido afetado para cima. '
            'Puxar levemente o pavilhão auricular para trás e para cima (adultos) para abrir o canal. '
            'Ficar deitado 1-2 minutos após aplicar.'
        ),
        'sinais_de_alerta': [
            'Febre alta (> 38,5°C) — OE simples raramente causa febre',
            'Vermelhidão ou inchaço se espalhando para o rosto/pescoço',
            'Zumbido novo ou piora da audição',
            'Sem melhora da dor em 48-72h',
            'Diabéticos: qualquer piora rápida → PS (risco de OE maligna)',
        ],
    }

    return {
        'tipo': 'orl', 'subtipo': 'otalgia',
        'categoria': 'orl_otite_externa',
        'diagnostico': 'Otite Externa Aguda — Gotas Tópicas',
        'urgencia': None, 'raciocinio': raciocinio,
        'achados': _achados(dados), 'red_flags': [],
        'exames': [],
        'conduta': [
            'Manter ouvido seco — sem piscina/mergulho × 7 dias + 7 dias após',
            'Não usar cotonete durante ou após o tratamento',
        ],
        'prescricoes_estruturadas': prescricoes,
        'orientacoes': orientacoes,
        'encaminhar': 'ORL se sem melhora em 7 dias ou progressão',
        'retorno': 'Retorno em 7 dias. PS se febre > 38,5°C ou piora da celulite.',
    }


# =============================================================================
# STEP 2C — OTITE MÉDIA AGUDA (OMA)
# =============================================================================

def _resultado_oma(dados) -> dict:
    idade       = dados.get('idade', 18)
    crianca     = idade < 18
    crianca_peq = idade < 2  # < 24 meses
    bilateral   = dados.get('bilateral', False)
    tratar      = dados.get('oma_tratar_imediato', True)
    atb_rec     = dados.get('atb_recente_30d', False)
    conj_pur    = dados.get('conjuntivite_purulenta', False)
    oma_rec     = dados.get('oma_recorrente', False)

    # Motivos para tratar imediatamente
    motivos_tratar = []
    if idade < 0.5:          motivos_tratar.append('< 6 meses')
    if crianca_peq and bilateral: motivos_tratar.append('bilateral < 2 anos')
    if dados.get('febre_alta'): motivos_tratar.append('febre ≥ 39°C')
    if dados.get('otalgia_mais_48h'): motivos_tratar.append('otalgia > 48h')
    if dados.get('otorreia_purulenta'): motivos_tratar.append('otorreia purulenta')
    if dados.get('seguimento_incerto'): motivos_tratar.append('retorno incerto')
    if conj_pur:             motivos_tratar.append('conjuntivite purulenta concomitante')

    if tratar:
        raciocinio = (
            'Otalgia + IRAS recente + ' +
            (f'MT abaulada/hiperemiada ' if dados.get('mt_abaulada') or dados.get('mt_hiperemia') else '') +
            '→ Otite Média Aguda. '
            + (f'Tratamento imediato indicado: {", ".join(motivos_tratar)}. '
               if motivos_tratar else 'Tratamento indicado. ') +
            ('Em adultos: amoxicilina-clavulanato é a escolha padrão '
             '(cobertura de H. influenzae e M. catarrhalis beta-lactamase positivos). '
             if not crianca else
             'Crianças: amoxicilina em alta dose (80–90 mg/kg/dia) é 1ª linha. ') +
            'Amox-Clav indicada se: ATB recente 30d, conjuntivite purulenta, OMA recorrente.'
        )
    else:
        raciocinio = (
            'Otalgia + IRAS recente + MT alterada → OMA, sem critério de tratamento imediato. '
            f'Criança {"≥ 2 anos" if idade >= 2 else "6–23 meses"} + unilateral + não grave: '
            'watchful waiting (WW) é seguro — AAP 2013/2023 (sem mudança). '
            'WW por 48–72h com analgesia. '
            'Fornecer prescrição de resgate a ser preenchida SOMENTE se: '
            'dor persistir ou piorar após 48–72h, febre aparecer ou elevar, humor muito alterado. '
            'Retorno garantido é pré-requisito do WW.'
        )

    # ── Prescrições ──────────────────────────────────────────────────────────
    prescricoes = []

    # Indicações de Amox-Clav como 1ª escolha (em vez de amox pura)
    usar_amoxclav_1a = (
        not crianca or   # adultos: amox-clav diretamente
        atb_rec or
        conj_pur or
        (oma_rec and atb_rec)
    )

    if tratar:
        if crianca:
            dose_amox_kg = '80–90 mg/kg/dia'
            if not usar_amoxclav_1a:
                prescricoes.append(
                    _rx('1ª linha (crianças)', f'Amoxicilina',
                        [_p(f'{dose_amox_kg}', '÷ 2 doses/dia',
                            '12/12h VO — calcular dose pelo peso (80–90 mg/kg/dia)')],
                        f'Duração: {"10 dias" if crianca_peq or dados.get("febre_alta") else "5–7 dias se ≥ 6 anos + leve/moderado, 7 dias se 2-5 anos"}. '
                        'Ex: 20kg → 1.600–1.800 mg/dia → Amox 875mg 12/12h (comp) ou suspensão 400mg/5mL.')
                )
            prescricoes.append(
                _rx(
                    'Amox-Clav (se: ATB 30d / conjuntivite purulenta / OMA recorrente)',
                    'Amoxicilina-Clavulanato 600/42,9mg/5mL susp.',
                    [_p('frasco conforme peso', '÷ 2 doses/dia',
                        '90 mg/kg/dia (componente amox) VO 12/12h — calcular pelo peso')],
                    'Duração igual à amoxicilina. Refrigerar após abrir.')
            )
        else:
            # Adultos: Amox-Clav diretamente
            prescricoes.append(
                _rx('1ª linha (adultos)', 'Amoxicilina-Clavulanato 875/125mg',
                    [_p('14', 'comprimidos', '1 comp VO 12/12h × 5–7 dias')],
                    'Tomar junto às refeições (reduz náusea). '
                    'Cobertura ampliada: H. influenzae e M. catarrhalis produtores de beta-lactamase.')
            )

    # Analgesia sempre
    if crianca:
        prescricoes.append(
            _rx('Analgesia (criança)', 'Paracetamol 200mg/mL gotas',
                [_p('1', 'frasco', '1 gota/kg VO de 6/6h PRN (máx 5 doses/dia)')],
                'Ou Ibuprofeno 10 mg/kg/dose 8/8h se > 6 meses e sem contraindicação.')
        )
    else:
        prescricoes.append(
            _rx('Analgesia', 'Ibuprofeno 600mg',
                [_p('14', 'comprimidos', '1 comp VO 8/8h durante as refeições × 5 dias PRN')],
                'Preferir ibuprofeno: melhor ação analgésica que paracetamol na otalgia.')
        )

    # Prescrição de resgate (watchful waiting)
    if not tratar:
        prescricoes.append(
            _rx(
                'Prescrição de RESGATE — preencher SOMENTE se piorar em 48–72h',
                'Amoxicilina-Clavulanato 875/125mg' if not crianca else 'Amoxicilina suspensão',
                [_p('14' if not crianca else 'frasco', 'comp / dose calculada',
                    '1 comp VO 12/12h × 5–7 dias — INICIAR APENAS se: dor piora, febre aparece, '
                    'ou sem melhora após 72h')],
                'Explique ao cuidador: entregar a prescrição FÍSICA mas não usar imediatamente.')
        )

    orientacoes = {
        'dor_e_febre': (
            'Analgesia é o principal tratamento independente de ATB. '
            'Ibuprofeno 400–600mg (adultos) ou dose pediátrica 8/8h PRN. '
            'Calor local (compressa morna) sobre o ouvido alivia a dor.'
        ),
        'atb_compliance': (
            'Tomar o antibiótico até o FIM do curso. '
            'Não parar por melhora precoce — recidiva e resistência bacteriana.'
        ) if tratar else None,
        'watchful_waiting': (
            'O antibiótico NÃO é necessário agora — maioria das OMA melhora sem ATB em 48–72h. '
            'Você recebeu uma prescrição de RESGATE: só preencher e comprar o antibiótico SE '
            'a dor piorar, a febre aparecer ou não houver melhora após 72h.'
        ) if not tratar else None,
        'sinais_de_alerta': [
            'Dor atrás do ouvido (vermelhidão ou inchaço) — mastoidite',
            'Ouvido projetado para frente',
            'Febre alta (> 39°C) ou que não cede',
            'Perda de audição progressiva',
            'Zumbido intenso novo',
            'Sem melhora em 48–72h (watchful waiting)',
        ] if not tratar else [
            'Vermelhidão/inchaço atrás do ouvido',
            'Febre que não cede após 48–72h de ATB',
            'Piora da dor após melhora inicial',
        ],
    }
    orientacoes = {k: v for k, v in orientacoes.items() if v}

    # Duração e retorno
    if crianca_peq or dados.get('febre_alta'):
        duracao = '10 dias'
    elif crianca and idade >= 6:
        duracao = '5–7 dias'
    elif crianca:
        duracao = '7 dias'
    else:
        duracao = '5–7 dias (adulto)'

    cat  = 'orl_otite_media_aguda'
    diag = f'Otite Média Aguda — {"Tratar" if tratar else "Watchful Waiting 48–72h"}'

    return {
        'tipo': 'orl', 'subtipo': 'otalgia',
        'categoria': cat, 'diagnostico': diag,
        'urgencia': None, 'raciocinio': raciocinio,
        'watchful_waiting': not tratar,          # gate para _plano_atalgia no texto.py
        'achados': _achados(dados), 'red_flags': [],
        'exames': [],
        'conduta': (
            [f'ATB por {duracao}. Retorno se sem melhora em 48–72h.']
            if tratar else
            ['Watchful waiting 48–72h. Prescrição de resgate entregue.',
             'Retorno garantido em 48–72h (presencial ou telefone).']
        ),
        'prescricoes_estruturadas': prescricoes,
        'orientacoes': orientacoes,
        'encaminhar': 'ORL se: ≥ 3 episódios/6 meses, efusão persistente > 3 meses, perda auditiva',
        'retorno': f'Retorno em 48–72h {"para reavaliação (WW)" if not tratar else "se sem melhora"}.',
    }


# =============================================================================
# STEP 2D — DTM LEVE
# =============================================================================

def _resultado_dtm(dados) -> dict:
    n = dados.get('dtm_criterios_n', 2)
    criterios = []
    if dados.get('dor_mastigacao'):     criterios.append('dor à mastigação')
    if dados.get('dor_matinal'):        criterios.append('piora matinal')
    if dados.get('bruxismo'):           criterios.append('bruxismo')
    if dados.get('click_mandibula'):    criterios.append('click mandibular')
    if dados.get('limitacao_abertura'): criterios.append('limitação de abertura')
    if dados.get('dor_temporal'):       criterios.append('irradiação temporal')

    raciocinio = (
        f'Otalgia com {n} critérios de DTM: {", ".join(criterios)}. '
        'Sem febre, sem trago positivo, sem contexto de IRAS → otalgia referida da ATM. '
        'A articulação temporomandibular está localizada imediatamente anterior ao meato acústico externo, '
        'explicando a irradiação da dor. '
        'Bruxismo noturno é o principal fator de sobrecarga. '
        'Manejo conservador: ≥ 80% resolvem em semanas-meses sem procedimento.'
    )
    prescricoes = [
        _rx('AINE (anti-inflamatório) × 7–10 dias', 'Ibuprofeno 600mg',
            [_p('21', 'comprimidos', '1 comp VO 8/8h durante as refeições × 7–10 dias')],
            'Tomar com alimento. Não usar em gastrite ativa ou IRC — substituir por Paracetamol 750mg 6/6h.'),
    ]
    orientacoes = {
        'dieta_mole': (
            'Dieta mole por 7–14 dias: sem alimentos duros (carne seca, cana, nuts, baguete dura), '
            'sem goma de mascar, sem abrir a boca muito amplo (hambúrguer grande, maçã inteira). '
            'Preferir: ovos, frango macio, massa, sopas, iogurte.'
        ),
        'calor_local': (
            'Compressa morna (não quente) sobre a articulação (frente do ouvido) por 15 min, 3–4×/dia. '
            'Calor reduz espasmo muscular e melhora a dor.'
        ),
        'bruxismo': (
            'Se range os dentes durante o sono: encaminhar dentista para placa de bruxismo (night guard). '
            'Técnicas de relaxamento antes de dormir (evitar telas, reduzir cafeína no período noturno).'
        ) if dados.get('bruxismo') else None,
        'postura': (
            'Evitar apoiar o queixo na mão. '
            'Postura do pescoço em frente ao computador: tela ao nível dos olhos.'
        ),
        'sinais_de_alerta': [
            'Febre — sugere infecção (não é DTM)',
            'Trismo muito limitante (< 3 dedos de abertura)',
            'Assimetria ou desvio da mandíbula ao abrir',
            'Sem melhora em 4–6 semanas',
        ],
    }
    orientacoes = {k: v for k, v in orientacoes.items() if v}

    return {
        'tipo': 'orl', 'subtipo': 'otalgia',
        'categoria': 'orl_dtm',
        'diagnostico': 'Disfunção Temporomandibular (DTM) — Manejo Conservador',
        'urgencia': None, 'raciocinio': raciocinio,
        'achados': _achados(dados), 'red_flags': [],
        'exames': ['RX panorâmico (dentista) se dúvida ou má oclusão'],
        'conduta': [
            'AINE × 7–10 dias + dieta mole + calor local',
            'Encaminhamento dentista para placa de bruxismo (eletivo)',
        ],
        'prescricoes_estruturadas': prescricoes,
        'orientacoes': orientacoes,
        'encaminhar': 'Dentista/Estomatologista (placa noturna) — eletivo',
        'retorno': 'Retorno em 2–4 semanas. Fisioterapia ATM se refratário.',
    }


# =============================================================================
# STEP 3 — OTALGIA INESPECÍFICA / TUBA
# =============================================================================

def _resultado_otalgia_inespecifica(dados) -> dict:
    raciocinio = (
        'Otalgia sem padrão específico identificado. '
        'Diferenciais a considerar: disfunção da tuba de Eustáquio (barotrauma, resfriado), '
        'otalgia referida (amigdalite, dental, cervical), cerume impactado. '
        'Investigação básica e retorno para reavaliação.'
    )
    return {
        'tipo': 'orl', 'subtipo': 'otalgia',
        'categoria': 'orl_otalgia_inespecifica',
        'diagnostico': 'Otalgia — Investigação em Andamento',
        'urgencia': None, 'raciocinio': raciocinio,
        'achados': _achados(dados), 'red_flags': [],
        'exames': ['Otoscopia (se não realizada)', 'Avaliação dentária se suspeita odontológica'],
        'conduta': ['Analgesia PRN', 'Investigar otalgia referida (garganta, dente, cervical)'],
        'prescricoes_estruturadas': [
            _rx('Analgesia PRN', 'Ibuprofeno 600mg',
                [_p('10', 'comprimidos', '1 comp VO 8/8h PRN — máx 5 dias')], None)
        ],
        'orientacoes': {
            'sinais_de_alerta': [
                'Febre',
                'Secreção saindo do ouvido',
                'Vermelhidão atrás do ouvido',
                'Perda súbita de audição',
            ],
        },
        'encaminhar': 'ORL eletivo se sem causa identificada em 2–4 semanas',
        'retorno': 'Retorno em 1–2 semanas para reavaliação.',
    }


# =============================================================================
# PONTO DE ENTRADA PRINCIPAL
# =============================================================================

def interpretar_otalgia(dados: dict) -> dict:
    """
    Motor de raciocínio clínico — Otalgia (Dor de Ouvido).

    STEP 1: Mastoidite → PS urgente
    STEP 2: OE Maligna (DM/imunocomp) → PS urgente
    STEP 2: Otite Externa → gotas tópicas
    STEP 2: OMA → watchful waiting vs ATB (AAP 2023)
    STEP 2: DTM → conservador
    STEP 3: Inespecífico
    """
    # STEP 1 — Mastoidite
    if dados.get('mastoidite_suspeita'):
        return _resultado_mastoidite(dados)

    # STEP 2 — OE Maligna (antes de OE simples)
    if dados.get('oe_maligna_suspeita'):
        return _resultado_oe_maligna(dados)

    # STEP 2 — Otite Externa (trago positivo / canal edema / exposição água)
    if dados.get('otite_externa_suspeita'):
        return _resultado_otite_externa(dados)

    # STEP 2 — OMA (IRAS + febre/MT alterada + sem trago)
    if dados.get('oma_suspeita'):
        return _resultado_oma(dados)

    # STEP 2 — DTM (≥ 2 critérios mandibulares, sem febre)
    if dados.get('dtm_suspeita'):
        return _resultado_dtm(dados)

    # STEP 3 — Inespecífico
    return _resultado_otalgia_inespecifica(dados)
