# modules/raciocinio/oftalmo/engine_olho_vermelho.py
# Motor de raciocínio clínico — Olho Vermelho
#
# Hierarquia STEP:
#   STEP 1  Trauma penetrante / químico → PS imediato (lavar se químico)
#   STEP 1  Glaucoma agudo (halos + dor intensa + visão turva) → PS imediato
#   STEP 1  Lente de contato + dor + fotofobia → Oftalmo urgente 24h (Pseudomonas!)
#   STEP 1  Ciliary flush → uveíte anterior / glaucoma → Oftalmo urgente
#   STEP 1  Celulite orbitária → PS + ATB IV
#   STEP 1  Pós-cirúrgico + dor + visão turva → endoftalmite → Oftalmo emergência
#   STEP 2  Conjuntivite bacteriana → Tobramicina 0,3% (NÃO Cloranfenicol)
#   STEP 2  Conjuntivite viral (adenovírus) → sintomático + isolamento agressivo
#   STEP 2  Conjuntivite alérgica → Ketotifeno + anti-histamínico VO
#   STEP 2  Hemorragia subconjuntival → tranquilizar + verificar PA
#   STEP 2  Hordéolo → compressa morna + Tobramicina tópica
#   STEP 2  Celulite pré-septal leve → Cefadroxila VO
#   STEP 3  Blefarite crônica / Calázio recidivante → Oftalmo eletivo
#
# Fontes:
#   - AAO Preferred Practice Pattern — Conjunctivitis (2019, atualização 2023)
#   - UpToDate — Contact lens-related corneal ulcer + Uveitis + Acute angle-closure (2024)
#   - CDC — Epidemic keratoconjunctivitis (EKC) guidance (2023)
#   - Cloranfenicol: risco de anemia aplásica idiossincrática (BMJ 1993; Fraunfelder 2004)


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
    if dados.get('lateralidade'):
        a.append(dados['lateralidade'].lower())
    if dados.get('duracao_sintomas'):
        a.append(f'duração {dados["duracao_sintomas"]}')
    if dados.get('ciliary_flush'):
        a.append('CILIARY FLUSH')
    if dados.get('dor_intensa'):
        a.append('dor intensa')
    elif dados.get('dor_ocular'):
        a.append('dor ocular')
    if dados.get('fotofobia'):
        a.append('fotofobia')
    if dados.get('halos_coloridos'):
        a.append('halos coloridos')
    if dados.get('visao_turva'):
        a.append('visão turva')
    if dados.get('lente_de_contato'):
        a.append('USUÁRIO DE LENTE')
    if dados.get('secrecao_purulenta'):
        a.append('secreção purulenta')
    if dados.get('secrecao_aquosa'):
        a.append('secreção aquosa')
    if dados.get('palpebra_grudada'):
        a.append('pálpebra grudada')
    if dados.get('prurido_ocular'):
        a.append('prurido')
    if dados.get('adenopatia_preauricular'):
        a.append('adenopatia pré-auricular')
    if dados.get('edema_palpebral'):
        a.append('edema palpebral')
    if dados.get('hemorragia_subconj'):
        a.append('hemorragia subconjuntival')
    return a


# =============================================================================
# STEP 1 — TRAUMA PENETRANTE / QUÍMICO
# =============================================================================

def _resultado_trauma(dados) -> dict:
    quimico    = dados.get('trauma_quimico', False)
    penetrante = dados.get('trauma_penetrante', False)

    if quimico:
        raciocinio = (
            'Trauma químico ocular — emergência máxima. '
            'Álcalis (amônia, soda cáustica, cal) causam liquefação do estroma corneal por saponificação — '
            'penetração rápida e profunda, pior prognóstico. '
            'Ácidos coagulam proteínas (barreira autolimitante). '
            'LAVAGEM IMEDIATA com SF ou água: 1-2L por 15-30 min com a pálpebra aberta — '
            'iniciar ANTES de qualquer outro cuidado. Não esperar o PS para lavar.'
        )
        conduta = [
            '🔴 LAVAR O OLHO IMEDIATAMENTE — SF 0,9% ou água limpa, 15–30 min, pálpebra aberta',
            'NÃO tampar o olho antes de lavar',
            'PS / Oftalmologia emergência após lavagem',
        ]
    else:
        raciocinio = (
            'Trauma penetrante ocular suspeito — emergência. '
            'Risco de endoftalmite (< 24h de contaminação), descolamento de retina, '
            'hipema, lesão do nervo óptico. '
            'NÃO pressionar o olho — risco de extrusão do conteúdo. '
            'Tampa protetora (copo plástico cortado) sobre o olho sem pressão.'
        )
        conduta = [
            '🔴 PS imediato — trauma penetrante',
            'Proteger o olho com tampa côncava (copo plástico) — NÃO comprimir',
            'Nada por boca (anestesia geral pode ser necessária)',
            'Não tentar remover corpo estranho penetrante',
        ]

    return {
        'tipo': 'oftalmo', 'subtipo': 'olho_vermelho',
        'categoria': 'oft_trauma_ocular',
        'diagnostico': f'Trauma Ocular {"Químico" if quimico else "Penetrante"} — PS Imediato',
        'urgencia': 'emergencia', 'raciocinio': raciocinio,
        'achados': _achados(dados), 'red_flags': ['Trauma ocular'],
        'exames': [], 'conduta': conduta,
        'prescricoes_estruturadas': [],
        'orientacoes': {},
        'encaminhar': 'PS / Oftalmologia — emergência',
        'retorno': '',
    }


# =============================================================================
# STEP 1 — GLAUCOMA AGUDO DE ÂNGULO FECHADO
# =============================================================================

def _resultado_glaucoma_agudo(dados) -> dict:
    pio = dados.get('pio_mmhg')
    raciocinio = (
        'Halos coloridos + dor ocular intensa + visão turva → '
        'glaucoma agudo de ângulo fechado até prova em contrário. '
        + (f'PIO medida: {pio} mmHg. ' if pio else '') +
        'Mecanismo: bloqueio pupilar → fechamento do ângulo câmara anterior → '
        'PIO sobe abruptamente (40–80 mmHg) → comprime nervo óptico. '
        'Irreversível em horas sem tratamento. '
        'Pupila em semimidríase fixa, córnea turva (edema estromal), câmara rasa. '
        'Tratamento: timolol 0,5% + pilocarpina 2% + acetazolamida VO + manitol IV — '
        'oftalmo emergência para iridotomia a laser.'
    )
    return {
        'tipo': 'oftalmo', 'subtipo': 'olho_vermelho',
        'categoria': 'oft_glaucoma_agudo',
        'diagnostico': 'Glaucoma Agudo de Ângulo Fechado — PS Imediato',
        'urgencia': 'emergencia', 'raciocinio': raciocinio,
        'achados': _achados(dados),
        'red_flags': ['Halos coloridos + dor intensa + visão turva = glaucoma agudo'],
        'exames': [],
        'conduta': [
            '🔴 PS / Oftalmologia — emergência (risco de cegueira permanente em horas)',
            'Não dilatar pupila — piora o bloqueio angular',
            'Posição sentada (facilita afastamento do cristalino)',
        ],
        'prescricoes_estruturadas': [],
        'orientacoes': {},
        'encaminhar': 'PS / Oftalmologia emergência — iridotomia a laser',
        'retorno': '',
    }


# =============================================================================
# STEP 1 — LENTE DE CONTATO + DOR — ÚLCERA DE CÓRNEA (PSEUDOMONAS)
# =============================================================================

def _resultado_ulcera_cornea_lente(dados) -> dict:
    dormiu = dados.get('dormiu_com_lente', False)
    irreg  = dados.get('lente_uso_irregular', False)

    raciocinio = (
        'Usuário de lente de contato + dor ocular + fotofobia/visão turva '
        '→ úlcera de córnea bacteriana até prova em contrário. '
        + ('Dormiu com a lente: fator de risco máximo (hipóxia corneal). '
           if dormiu else '') +
        ('Uso irregular da lente (tempo prolongado): fator de risco. '
         if irreg else '') +
        'Pseudomonas aeruginosa é o agente mais temido em usuários de lente: '
        'colagenase bacteriana pode perfurar a córnea em 24–48h. '
        'Mesmo dor leve em usuário de lente = Oftalmo urgente (exame com lâmpada de fenda). '
        'ATB tópico empírico de alta potência (fluoroquinolona) iniciado pelo oftalmo. '
        'NÃO prescrever colírio ambulatorial e aguardar — risco de perfuração.'
    )
    return {
        'tipo': 'oftalmo', 'subtipo': 'olho_vermelho',
        'categoria': 'oft_ulcera_cornea',
        'diagnostico': 'Úlcera de Córnea Suspeita (Usuário de Lente) — Oftalmo Urgente 24h',
        'urgencia': 'urgente', 'raciocinio': raciocinio,
        'achados': _achados(dados),
        'red_flags': ['Lente de contato + dor + fotofobia → Pseudomonas — avaliação urgente'],
        'exames': [],
        'conduta': [
            '🔴 REMOVER A LENTE DE CONTATO IMEDIATAMENTE',
            'Oftalmo urgente (lâmpada de fenda + coloração fluoresceína) dentro de 24h',
            'NÃO prescrever colírio antibiótico ambulatorial sem avaliação corneal',
            'Não usar a lente de contato até alta do oftalmologista',
        ],
        'prescricoes_estruturadas': [],
        'orientacoes': {
            'lente_de_contato': (
                'RETIRE A LENTE DE CONTATO AGORA e não recoloque até liberação do oftalmologista. '
                'Guarde a lente e o estojo para o oftalmologista examinar (cultura de Pseudomonas). '
                'Use óculos enquanto aguarda a consulta.'
            ),
            'sinais_de_alerta': [
                'Piora rápida da dor — ir ao PS imediatamente',
                'Visão embaçando progressivamente',
                'Mancha branca na córnea (úlcera visível) — PS imediato',
            ],
        },
        'encaminhar': 'Oftalmologia — urgente (dentro de 24h)',
        'retorno': '',
    }


# =============================================================================
# STEP 1 — CILIARY FLUSH → UVEÍTE ANTERIOR / GLAUCOMA
# =============================================================================

def _resultado_ciliary_flush(dados) -> dict:
    raciocinio = (
        'Ciliary flush (hiperemia pericorneal / perilimbal) identificado — '
        'sinal de processo inflamatório intrao cular até prova em contrário. '
        'Diferença clínica chave: '
        'Conjuntivite → vermelhidão difusa, máxima na periferia, menor ao redor da córnea. '
        'Uveíte/Glaucoma → vermelhidão em HALO ao redor da córnea/íris, menor na periferia. '
        'Principais causas com ciliary flush: '
        '(1) Uveíte anterior — dor + fotofobia + miose + precipitados ceráticos; '
        '(2) Glaucoma agudo — halos + dor intensa + midríase fixa; '
        '(3) Ceratite / Úlcera corneal. '
        'Exame com lâmpada de fenda é mandatório — impossível diferenciar sem biomicroscopia.'
    )
    return {
        'tipo': 'oftalmo', 'subtipo': 'olho_vermelho',
        'categoria': 'oft_uveite_glaucoma_suspeito',
        'diagnostico': 'Ciliary Flush — Uveíte Anterior / Glaucoma Suspeito — Oftalmo Urgente',
        'urgencia': 'urgente', 'raciocinio': raciocinio,
        'achados': _achados(dados),
        'red_flags': ['Ciliary flush — processo intraocular até prova em contrário'],
        'exames': [],
        'conduta': [
            'Oftalmologia urgente (lâmpada de fenda + tonometria)',
            'NÃO dilatar pupila na APS sem saber a causa',
            'NÃO tratar como conjuntivite — colírio antibiótico não resolve uveíte',
        ],
        'prescricoes_estruturadas': [],
        'orientacoes': {},
        'encaminhar': 'Oftalmologia — urgente (< 24–48h)',
        'retorno': '',
    }


# =============================================================================
# STEP 1 — CELULITE ORBITÁRIA
# =============================================================================

def _resultado_celulite_orbitaria(dados) -> dict:
    raciocinio = (
        'Edema palpebral + limitação da motilidade ocular e/ou proptose → '
        'celulite orbitária (pós-septal) até prova em contrário. '
        'Diferença crítica de celulite pré-septal: '
        'Pré-septal: edema palpebral, sem limitação de motilidade, sem proptose — '
        'geralmente sem risco de cegueira; '
        'Orbitária: extensão posterior ao septo orbitário — '
        'compressão do nervo óptico e trombose do seio cavernoso como complicações graves. '
        'TC de órbitas com contraste: obrigatória para diferenciar e guiar cirurgia. '
        'ATB IV: ceftriaxona + metronidazol (cobertura de Staph, Strep e anaeróbios).'
    )
    return {
        'tipo': 'oftalmo', 'subtipo': 'olho_vermelho',
        'categoria': 'oft_celulite_orbitaria',
        'diagnostico': 'Celulite Orbitária Suspeita — PS Urgente',
        'urgencia': 'urgente', 'raciocinio': raciocinio,
        'achados': _achados(dados),
        'red_flags': ['Celulite orbitária — limitação motilidade + edema palpebral'],
        'exames': [],
        'conduta': [
            'PS urgente — TC de órbitas com contraste',
            'ATB IV: Ceftriaxona 2g IV 12/12h + Metronidazol 500mg IV 8/8h',
            'Oftalmo + Otorrino (investigar foco sinusal) + Cirurgia se abscesso',
        ],
        'prescricoes_estruturadas': [],
        'orientacoes': {},
        'encaminhar': 'PS — Oftalmologia + Cirurgia urgente',
        'retorno': '',
    }


# =============================================================================
# STEP 1 — ENDOFTALMITE (PÓS-CIRÚRGICO)
# =============================================================================

def _resultado_endoftalmite(dados) -> dict:
    raciocinio = (
        'Cirurgia ocular recente + olho vermelho + dor + visão turva → '
        'endoftalmite pós-operatória até prova em contrário. '
        'Endoftalmite aguda pós-catarata: pico 1–3 semanas pós-op. '
        'Agentes: Staph epidermidis (mais comum), Staph aureus, gram-negativos. '
        'Progressão rápida — horas a dias para perda do globo ocular. '
        'Tratamento: antibiótico intravítreo (vancomicina + ceftazidima) ± vitrectomia. '
        'NÃO dar alta sem avaliação oftalmológica urgente.'
    )
    return {
        'tipo': 'oftalmo', 'subtipo': 'olho_vermelho',
        'categoria': 'oft_endoftalmite',
        'diagnostico': 'Endoftalmite Pós-Operatória Suspeita — Oftalmo Emergência',
        'urgencia': 'emergencia', 'raciocinio': raciocinio,
        'achados': _achados(dados),
        'red_flags': ['Pós-cirúrgico + dor + visão turva = endoftalmite até prova em contrário'],
        'exames': [],
        'conduta': [
            '🔴 Oftalmo emergência — injeção intravítrea urgente',
            'Não usar colírio antibiótico tópico como único tratamento',
        ],
        'prescricoes_estruturadas': [],
        'orientacoes': {},
        'encaminhar': 'Oftalmologia — emergência',
        'retorno': '',
    }


# =============================================================================
# STEP 2A — CONJUNTIVITE BACTERIANA
# =============================================================================

def _resultado_conjuntivite_bacteriana(dados) -> dict:
    bilateral = dados.get('bilateral', False)
    crianca   = dados.get('idade', 18) < 12

    raciocinio = (
        'Secreção purulenta/mucopurulenta + pálpebra grudada ao acordar '
        + ('+ bilateral ' if bilateral else '') +
        '→ conjuntivite bacteriana. '
        'Agentes mais comuns: Staphylococcus aureus, Streptococcus pneumoniae, '
        'Haemophilus influenzae (crianças), Moraxella catarrhalis. '
        'Tobramicina 0,3%: cobertura ampla gram-positivos e gram-negativos, '
        'excelente penetração corneal, mínima resistência clínica. '
        'Cloranfenicol: EVITAR — risco de anemia aplásica idiossincrática (raro mas fatal) '
        'e taxa crescente de resistência no Brasil. '
        'Ciprofloxacino 0,3%: alternativa quando Pseudomonas for suspeita (sem lente de contato aqui). '
        'Conjuntivite bacteriana não complicada: resolução espontânea em 7–14d, '
        'mas ATB encurta para 2–5d e reduz contagiosidade.'
    )

    prescricoes = [
        _rx('1ª linha — antibiótico tópico',
            'Tobramicina 0,3% colírio',
            [_p('1', 'frasco', '1–2 gotas no olho afetado, 4×/dia × 7 dias')],
            'Nas primeiras 48h: 1–2 gotas a cada 2h se secreção intensa (máx 8 doses/dia). '
            'NÃO usar Cloranfenicol — risco de anemia aplásica + maior resistência. '
            + ('Alternativa igualmente eficaz: Ciprofloxacino 0,3% colírio, mesma posologia. '
               if not crianca else '')),
    ]

    if crianca:
        prescricoes.append(
            _rx('Nota — criança < 12 anos',
                'Tobramicina 0,3% colírio (seguro a partir dos 2 anos)',
                [_p('1', 'frasco', '1 gota no olho afetado, 4×/dia × 5–7 dias')],
                'Em < 1 mês: SEMPRE excluir conjuntivite gonocócica/clamidiana (neonatal) → PS.')
        )

    # Dias de atestado: 3–5 dias (até melhora da secreção)
    dias_atestado = 5 if dados.get('profissional_saude') else 3

    orientacoes = {
        'higiene_ocular': (
            'Lavar as mãos com água e sabão antes e depois de qualquer contato com o olho. '
            'Usar lenço descartável (não de tecido reutilizável) para limpar a secreção. '
            'Aplicar o colírio puxando a pálpebra inferior para baixo e pingando no "bolsão" formado — '
            'não deixar o bico do frasco tocar o olho ou a pálpebra.'
        ),
        'contagio': (
            'A conjuntivite bacteriana é contagiosa até 24–48h após início do colírio. '
            'Não compartilhar toalhas, fronhas, maquiagem ou colírio com outras pessoas. '
            'Se bilateral: use um frasco diferente para cada olho, ou descarte o frasco após o tratamento.'
        ),
        'lente_de_contato': (
            'NÃO use lentes de contato durante o tratamento. '
            'Descarte as lentes usadas no período de infecção. '
            'Só retorne às lentes após término do colírio e sem secreção.'
        ) if dados.get('lente_de_contato') else None,
        'sinais_de_alerta': [
            'Piora da dor ou visão embaçada após 2–3 dias de colírio → Oftalmologista',
            'Vermelhidão se concentrando ao redor da córnea (ciliary flush) → Urgente',
            'Inchaço das pálpebras com febre → PS (celulite pré-septal/orbitária)',
        ],
    }
    orientacoes = {k: v for k, v in orientacoes.items() if v}

    return {
        'tipo': 'oftalmo', 'subtipo': 'olho_vermelho',
        'categoria': 'oft_conjuntivite_bacteriana',
        'diagnostico': 'Conjuntivite Bacteriana — Tobramicina Tópica 7 dias',
        'urgencia': None, 'raciocinio': raciocinio,
        'achados': _achados(dados), 'red_flags': [],
        'exames': [],
        'conduta': [
            'Tobramicina 0,3% colírio × 7 dias',
            f'Afastamento: {dias_atestado} dias (até 48h sem secreção)',
            'Higiene de mãos rigorosa — não compartilhar toalha/fronha',
        ],
        'prescricoes_estruturadas': prescricoes,
        'orientacoes': orientacoes,
        'dias_atestado': dias_atestado,
        'encaminhar': 'Oftalmologista se sem melhora em 5–7 dias ou piora em qualquer momento',
        'retorno': 'Retorno em 5–7 dias. Antes disso se piora da dor ou visão embaçada.',
    }


# =============================================================================
# STEP 2B — CONJUNTIVITE VIRAL (ADENOVÍRUS — EPIDÊMICA)
# =============================================================================

def _resultado_conjuntivite_viral(dados) -> dict:
    prof_saude = dados.get('profissional_saude', False)
    bilateral  = dados.get('bilateral', False)
    aden_preaur = dados.get('adenopatia_preauricular', False)

    raciocinio = (
        'Secreção aquosa + bilateral'
        + (' + adenopatia pré-auricular' if aden_preaur else '')
        + (' + contato com caso confirmado' if dados.get('contato_conjuntivite') else '')
        + ' → conjuntivite viral, provavelmente adenovírus. '
        'Adenovírus (esp. sorotipo 8, 19, 37 — ceratoconjuntivite epidêmica) sobrevive '
        '2 semanas em superfícies secas e até 35 dias em água. '
        'Sem tratamento antiviral eficaz disponível (ganciclovir tópico: dados limitados). '
        'Tratamento: sintomático. '
        'Isolamento é a principal medida de saúde pública — '
        'adenovírus causa surtos em hospitais, escolas e quartéis. '
        + ('Profissional de saúde: afastamento de atividades com pacientes por 14 dias '
           'ou até resolução completa da secreção. '
           if prof_saude else '')
    )

    # Dias de isolamento/atestado
    if prof_saude:
        dias_isolamento = 14
        motivo_isolamento = 'Profissional de saúde — afastamento de cuidado direto de pacientes'
    else:
        dias_isolamento = 7
        motivo_isolamento = 'Escola / trabalho presencial de contato'

    prescricoes = [
        _rx('Lubrificante ocular (alívio sintomático)',
            'Lágrima artificial sem conservante (unidoses)',
            [_p('1', 'caixa', '1–2 gotas no olho afetado, 4–6×/dia pelo tempo que precisar')],
            'Gelada (armazenar na geladeira — não congelar): maior alívio da ardência. '
            'Preferir unidoses sem conservante — conservantes irritam o olho inflamado. '
            'Marcas: Optive, Systane, Lacrifilm, Refresh — qualquer equivalente.'),
        _rx('Compressa fria (anti-inflamatório local)',
            'Compressa fria (pano limpo ou gaze + água gelada)',
            [_p('—', '—', '5–10 min sobre os olhos fechados, 3–4×/dia')],
            'Reduz edema palpebral, ardência e lacrimejamento. '
            'Pano INDIVIDUAL — não compartilhar. Lavar após cada uso.'),
    ]

    orientacoes = {
        'isolamento_e_higiene': (
            '⚠️  O adenovírus é ALTAMENTE CONTAGIOSO e sobrevive semanas em superfícies. '
            'Isolamento social por pelo menos 7 dias (ou até secreção zerar). '
            'Lavar as mãos com água + sabão por 20 segundos OU álcool 70% '
            'TODA vez que tocar o olho, face ou qualquer objeto que possa ter sido contaminado. '
            'Não apertar a mão de ninguém sem lavar as mãos antes.'
        ),
        'objetos_pessoais': (
            'NÃO compartilhar toalhas, fronhas, travesseiros, óculos, maquiagem, '
            'colírio nem qualquer objeto que toque o rosto. '
            'Trocar a fronha diariamente durante o período de isolamento. '
            'Descartar lentes de contato usadas. '
            'Limpar óculos com álcool 70% diariamente.'
        ),
        'superficies': (
            'Desinfetar com álcool 70% (não eficaz para adenovírus — usar hipoclorito 0,1% '
            'ou lenços com quaternário de amônio): maçanetas, torneiras, interruptores, '
            'teclado, telefone e qualquer superfície tocada frequentemente. '
            'O adenovírus NÃO é eliminado pelo álcool comum — usar hipoclorito ou '
            'produto com quaternário de amônio nas superfícies.'
        ),
        'atestado': (
            f'Afastamento recomendado: {dias_isolamento} dias. '
            f'Motivo: {motivo_isolamento}. '
            'A conjuntivite viral por adenovírus é causa legal de afastamento — '
            'atestado pode ser fornecido pelo médico assistente.'
        ),
        'sinais_de_alerta': [
            'Visão embaçada persistindo após 2 semanas → Oftalmologista (ceratite pseudo-membranosa)',
            'Vermelhidão se concentrando ao redor da córnea → Urgente',
            'Piora progressiva após 1 semana (maioria melhora gradualmente)',
            'Dor intensa — conjuntivite viral NÃO causa dor intensa (reavalie o diagnóstico)',
        ],
    }

    return {
        'tipo': 'oftalmo', 'subtipo': 'olho_vermelho',
        'categoria': 'oft_conjuntivite_viral',
        'diagnostico': 'Conjuntivite Viral (Adenovírus) — Sintomático + Isolamento',
        'urgencia': None, 'raciocinio': raciocinio,
        'achados': _achados(dados), 'red_flags': [],
        'exames': [],
        'conduta': [
            f'Isolamento social: {dias_isolamento} dias (adenovírus em superfícies até 2 semanas)',
            'Lágrima artificial gelada 4–6×/dia + compressa fria',
            'NÃO antibiótico — viral, sem benefício',
            'Higiene de mãos compulsória — hipoclorito em superfícies (álcool é ineficaz)',
        ],
        'prescricoes_estruturadas': prescricoes,
        'orientacoes': orientacoes,
        'dias_atestado': dias_isolamento,
        'encaminhar': 'Oftalmologista se visão embaçada persistir > 2 semanas',
        'retorno': f'Retorno em {dias_isolamento} dias ou antes se piora da visão.',
    }


# =============================================================================
# STEP 2C — CONJUNTIVITE ALÉRGICA
# =============================================================================

def _resultado_conjuntivite_alergica(dados) -> dict:
    rinite_concomitante = dados.get('rinite_alergica_concomitante', False)

    raciocinio = (
        'Prurido ocular intenso + '
        + ('rinite concomitante + ' if rinite_concomitante else '') +
        ('histórico de alergia + ' if dados.get('rinite_alergica_conhecida') else '') +
        ('piora sazonal ' if dados.get('piora_sazonal_ocular') else '') +
        '→ conjuntivite alérgica. '
        'Mediada por IgE: alérgenos (pólen, ácaro, epitélio animal) ativam mastócitos '
        'conjuntivais → histamina → prurido, quemose, lacrimejamento. '
        'Cetotifeno 0,025%: dupla ação (anti-histamínico + estabilizador de mastócito) — '
        'superior a anti-histamínico puro. '
        'Anti-histamínico oral complementa quando há rinite alérgica concomitante.'
    )

    prescricoes = [
        _rx('1ª linha — colírio anti-histamínico/estabilizador',
            'Cetotifeno 0,025% colírio',
            [_p('1', 'frasco', '1 gota no(s) olho(s) afetado(s), 2×/dia (manhã e noite)')],
            'Pode usar continuamente durante a estação de exposição. '
            'Alternativas: Olopatadina 0,1% 2×/dia, Epinastina 0,05% 2×/dia.'),
        _rx('Adjuvante — lágrima artificial (diluir e lavar alérgeno)',
            'Lágrima artificial sem conservante (unidoses)',
            [_p('1', 'caixa', '1–2 gotas, 4×/dia — usar 15 min ANTES do cetotifeno')],
            'Lava os alérgenos da superfície conjuntival. '
            'Gelada: maior alívio do prurido (vasoconstrição local).'),
    ]

    if rinite_concomitante:
        prescricoes.append(
            _rx('Anti-histamínico oral (rinite + olho concomitante)',
                'Loratadina 10mg',
                [_p('30', 'comprimidos', '1 comp VO 1×/dia (manhã) durante exposição ao alérgeno')],
                'Alternativas: Cetirizina 10mg, Bilastina 20mg, Fexofenadina 180mg. '
                'Não sedativo. Bilastina/fexofenadina têm menor risco de sedação residual.')
        )

    orientacoes = {
        'controle_de_alergenos': (
            'Evitar o contato com o alérgeno desencadeante: '
            'Pólen: manter janelas fechadas em dias ventosos, óculos escuros ao sair. '
            'Ácaro: capa antiácaro no travesseiro e colchão, lavagem semanal com água quente (60°C). '
            'Animal de estimação: não deixar o pet no quarto, lavar as mãos após contato.'
        ),
        'tecnica_colírio': (
            'Aplicar o colírio com a cabeça levemente inclinada para trás. '
            'Puxar a pálpebra inferior para baixo, pingar no "bolsão" formado. '
            'Fechar os olhos por 2 minutos após. '
            'Não espremer — 1 gota é suficiente (o excesso escorre e é desperdiçado).'
        ),
        'sinais_de_alerta': [
            'Visão turva ou dor intensa — não é conjuntivite alérgica simples → reavalie',
            'Vermelhidão ao redor da córnea (ciliary flush) → Oftalmo urgente',
            'Sem melhora após 7–14 dias de tratamento regular → Alergologista',
        ],
    }

    return {
        'tipo': 'oftalmo', 'subtipo': 'olho_vermelho',
        'categoria': 'oft_conjuntivite_alergica',
        'diagnostico': 'Conjuntivite Alérgica — Cetotifeno + Anti-histamínico',
        'urgencia': None, 'raciocinio': raciocinio,
        'achados': _achados(dados), 'red_flags': [],
        'exames': [
            'Prick test (Alergologista) — se refratária ou candidato a imunoterapia',
        ],
        'conduta': [
            'Cetotifeno 0,025% colírio 2×/dia durante exposição ao alérgeno',
            'Controle de exposição ao alérgeno desencadeante',
            ('Loratadina 10mg VO 1×/dia (rinite concomitante)' if rinite_concomitante else
             'Anti-histamínico oral se prurido generalizado ou rinite associada'),
        ],
        'prescricoes_estruturadas': prescricoes,
        'orientacoes': orientacoes,
        'encaminhar': 'Alergologista (eletivo) — prick test + imunoterapia se refratária',
        'retorno': 'Retorno em 2–4 semanas para avaliação de resposta.',
    }


# =============================================================================
# STEP 2D — HEMORRAGIA SUBCONJUNTIVAL
# =============================================================================

def _resultado_hemorragia_subconj(dados) -> dict:
    raciocinio = (
        'Mancha vermelha brilhante bem delimitada, sem dor, sem secreção → '
        'hemorragia subconjuntival. '
        'Causas: esforço (tosse, espirro, vômito, levantamento de peso), '
        'uso de anticoagulante/AAS, trauma menor, HAS, manobra de Valsalva. '
        'Sangue entre a conjuntiva e a esclera: sem dor, sem risco à visão. '
        'Resolve espontaneamente em 1–3 semanas (cor muda de vermelho → amarelo → desaparece). '
        'Principal cuidado: verificar PA (HAS pode causar recorrência).'
    )

    return {
        'tipo': 'oftalmo', 'subtipo': 'olho_vermelho',
        'categoria': 'oft_hemorragia_subconj',
        'diagnostico': 'Hemorragia Subconjuntival — Evolução Espontânea',
        'urgencia': None, 'raciocinio': raciocinio,
        'achados': _achados(dados), 'red_flags': [],
        'exames': ['Verificar PA — HAS é causa frequente de recorrência'],
        'conduta': [
            'Tranquilizar — resolve sozinha em 1–3 semanas sem tratamento',
            'Verificar pressão arterial',
            'Revisar uso de anticoagulantes/AAS se recorrente',
        ],
        'prescricoes_estruturadas': [
            _rx('Lubrificante para desconforto (opcional)',
                'Lágrima artificial sem conservante',
                [_p('1', 'frasco', '1–2 gotas 3–4×/dia PRN')],
                'Apenas se houver desconforto — não acelera a reabsorção.'),
        ],
        'orientacoes': {
            'tranquilizacao': (
                'A mancha vermelha parece grave, mas é como uma "meleca de sangue" debaixo '
                'do filme transparente do olho — não entra no olho nem afeta a visão. '
                'Vai mudar de cor (vermelho → amarelo → desaparece) em 1 a 3 semanas. '
                'Não precisa de colírio especial, curativo ou restrição de atividades.'
            ),
            'sinais_de_alerta': [
                'Dor ocular — hemorragia subconjuntival NÃO dói → reavalie',
                'Visão embaçada → Oftalmo urgente',
                'Recorrência frequente sem causa aparente → investigar coagulopatia / HAS',
                'Trauma com força → pode ter lesão interna → PS',
            ],
        },
        'encaminhar': 'Oftalmologista se recorrente (≥ 3 episódios/ano) ou sem causa identificada',
        'retorno': 'Retorno em 3 semanas se não resolver, antes se dor ou visão embaçada.',
    }


# =============================================================================
# STEP 2E — HORDÉOLO (ORZOLHO)
# =============================================================================

def _resultado_hordeoleo(dados) -> dict:
    raciocinio = (
        'Nódulo doloroso na borda palpebral + eritema localizado + sem febre → '
        'hordéolo externo (orzolho). '
        'Infecção do folículo ciliar (glândula de Zeiss/Moll) por Staph aureus. '
        'Hordéolo interno: glândula de Meibômio infectada — mais profundo, mais doloroso. '
        'Calázio: granuloma estéril (não infeccioso) de glândula de Meibômio bloqueada — '
        'indolor, firme, resolução mais lenta. '
        'Tratamento: compressa morna (abre o ducto obstruído) é suficiente em 80% dos casos. '
        'ATB tópico: Tobramicina para componente infeccioso/recorrente.'
    )
    prescricoes = [
        _rx('Compressa morna — tratamento principal',
            'Compressa morna (pano + água quente — não queimar)',
            [_p('—', '—', 'Compressa morna sobre a pálpebra fechada, 10–15 min, 4×/dia × 7–14 dias')],
            'Temperatura: suportável ao toque (≈ 45°C). '
            'Após a compressa: massagear suavemente a pálpebra em direção à margem ciliar '
            '(expulsa o conteúdo sebáceo). '
            'É o tratamento mais eficaz — mais importante que o colírio.'),
        _rx('Antibiótico tópico (componente infeccioso)',
            'Tobramicina 0,3% pomada oftálmica',
            [_p('1', 'bisnagas', 'Fio de 1cm na margem palpebral afetada, 3×/dia × 7 dias')],
            'Pomada: maior tempo de contato que colírio. '
            'Alternativa: Tobramicina 0,3% colírio 4×/dia se pomada não disponível. '
            'NÃO usar Cloranfenicol.'),
    ]

    orientacoes = {
        'compressa_morna': (
            'A compressa morna é o tratamento mais importante — faça religiosamente 4 vezes ao dia. '
            'Como fazer: molhe um pano limpo em água morna (quase quente, mas suportável) '
            'e aplique sobre o olho FECHADO por 10–15 minutos. '
            'Reaqueça o pano a cada 2–3 minutos para manter a temperatura. '
            'Após a compressa: com o dedo limpo, massageie suavemente a pálpebra '
            'de fora para dentro (em direção ao canto do olho) — ajuda a "espremer" o bloqueio.'
        ),
        'higiene': (
            'Lavar as mãos antes de qualquer manipulação. '
            'NÃO espremer o hordéolo com força — pode disseminar a infecção. '
            'Não compartilhar toalhas ou fronhas. '
            'Retirar maquiagem e não usar durante o tratamento.'
        ),
        'sinais_de_alerta': [
            'Febre ou inchaço se espalhando para além da pálpebra → PS (celulite pré-septal)',
            'Sem melhora após 2 semanas de compressas → Oftalmologista (drenagem)',
            'Endurecimento sem dor que persiste > 4 semanas → Calázio (oftalmo eletivo)',
        ],
    }

    return {
        'tipo': 'oftalmo', 'subtipo': 'olho_vermelho',
        'categoria': 'oft_hordeoleo',
        'diagnostico': 'Hordéolo (Orzolho) — Compressa Morna + Tobramicina Tópica',
        'urgencia': None, 'raciocinio': raciocinio,
        'achados': _achados(dados), 'red_flags': [],
        'exames': [],
        'conduta': [
            'Compressa morna 10–15 min, 4×/dia × 7–14 dias — tratamento principal',
            'Tobramicina pomada 3×/dia × 7 dias',
            'Oftalmo eletivo se não resolver em 2–3 semanas (drenagem)',
        ],
        'prescricoes_estruturadas': prescricoes,
        'orientacoes': orientacoes,
        'encaminhar': 'Oftalmologista (eletivo) se sem melhora em 2–3 semanas',
        'retorno': 'Retorno em 2 semanas. Antes se febre ou inchaço progressivo.',
    }


# =============================================================================
# STEP 2F — CELULITE PRÉ-SEPTAL (leve, sem limitação de motilidade)
# =============================================================================

def _resultado_celulite_preseptal(dados) -> dict:
    raciocinio = (
        'Edema palpebral + eritema + febre, SEM limitação de motilidade ocular e SEM proptose → '
        'celulite pré-septal (anterior ao septo orbitário). '
        'Agentes: Staph aureus, Strep pyogenes, H. influenzae (crianças não vacinadas). '
        'Fontes: picada de inseto, trauma cutâneo, chalázio/hordéolo complicado, sinusite. '
        'Tratamento oral é possível se leve (< 2 anos ou grave → PS + IV). '
        'Vigilância obrigatória: piora dentro de 24–48h → hospitalização.'
    )
    prescricoes = [
        _rx('Antibiótico VO (celulite pré-septal leve)',
            'Cefadroxila 500mg',
            [_p('14', 'comprimidos', '1 comp VO 12/12h × 7–10 dias')],
            'Boa cobertura cutânea (Staph/Strep). '
            'Alternativa: Amoxicilina-Clavulanato 875/125mg 12/12h × 7 dias '
            '(se sinusite como foco ou exposição animal). '
            'RETORNO MANDATÓRIO em 24–48h para reavaliação — piora = hospitalização.'),
    ]

    orientacoes = {
        'vigilancia': (
            'Esta é uma infecção ao redor do olho. '
            'Se piorar (mais inchaço, febre alta, olho começar a se mover com dificuldade) '
            'ligue para a UBS ou vá ao PS — pode precisar de antibiótico na veia.'
        ),
        'sinais_de_alerta': [
            'Piora do inchaço apesar do antibiótico (24–48h) → PS urgente',
            'Dificuldade para mover o olho → PS urgente (celulite orbitária)',
            'Febre alta que não cede',
            'Olho "saltando para fora" → PS imediato',
        ],
    }

    return {
        'tipo': 'oftalmo', 'subtipo': 'olho_vermelho',
        'categoria': 'oft_celulite_preseptal',
        'diagnostico': 'Celulite Pré-Septal — ATB Oral + Retorno 24–48h',
        'urgencia': None, 'raciocinio': raciocinio,
        'achados': _achados(dados), 'red_flags': [],
        'exames': [],
        'conduta': [
            'Cefadroxila 500mg 12/12h × 7–10 dias',
            'Retorno OBRIGATÓRIO em 24–48h para reavaliação',
            'PS se piora antes do retorno',
        ],
        'prescricoes_estruturadas': prescricoes,
        'orientacoes': orientacoes,
        'encaminhar': 'PS se piora / < 2 anos → hospitalização direta',
        'retorno': 'Retorno OBRIGATÓRIO em 24–48h.',
    }


# =============================================================================
# STEP 3 — INVESTIGAÇÃO / REFERÊNCIA ELETIVA
# =============================================================================

def _resultado_investigar(dados) -> dict:
    raciocinio = (
        'Olho vermelho sem padrão diagnóstico claro nos dados disponíveis. '
        'Diferencial: blefarite crônica, conjuntivite de inclusão (Chlamydia), '
        'episclerite leve, pterígio/pinguécula irritado, síndrome do olho seco. '
        'Avaliação com lâmpada de fenda é necessária para diferenciar.'
    )
    return {
        'tipo': 'oftalmo', 'subtipo': 'olho_vermelho',
        'categoria': 'oft_olho_vermelho_inespecifico',
        'diagnostico': 'Olho Vermelho — Investigação / Oftalmo Eletivo',
        'urgencia': None, 'raciocinio': raciocinio,
        'achados': _achados(dados), 'red_flags': [],
        'exames': ['Oftalmologista (lâmpada de fenda) — eletivo'],
        'conduta': [
            'Lágrima artificial para alívio sintomático',
            'Oftalmologista eletivo para diagnóstico definitivo (lâmpada de fenda)',
        ],
        'prescricoes_estruturadas': [
            _rx('Lubrificante — sintomático',
                'Lágrima artificial sem conservante',
                [_p('1', 'frasco', '1–2 gotas 4×/dia PRN')], None),
        ],
        'orientacoes': {
            'sinais_de_alerta': [
                'Ciliary flush (anel vermelho ao redor da córnea) → Oftalmo urgente',
                'Visão embaçada ou dor intensa → PS',
                'Halos coloridos ao redor de luzes → PS imediato (glaucoma agudo)',
            ],
        },
        'encaminhar': 'Oftalmologista eletivo',
        'retorno': 'Retorno em 1–2 semanas se sem melhora.',
    }


# =============================================================================
# PONTO DE ENTRADA PRINCIPAL
# =============================================================================

def interpretar_olho_vermelho(dados: dict) -> dict:
    """
    Motor de raciocínio clínico — Olho Vermelho.

    STEP 1: Trauma (penetrante/químico) → PS imediato
    STEP 1: Glaucoma agudo (halos + dor intensa + visão turva) → PS imediato
    STEP 1: Endoftalmite pós-cirúrgica → Oftalmo emergência
    STEP 1: Lente de contato + dor → Úlcera córnea Pseudomonas → Oftalmo urgente
    STEP 1: Ciliary flush → Uveíte/Glaucoma → Oftalmo urgente
    STEP 1: Celulite orbitária → PS urgente
    STEP 2: Conjuntivite bacteriana → Tobramicina 0,3%
    STEP 2: Conjuntivite viral (adenovírus) → Sintomático + Isolamento agressivo
    STEP 2: Conjuntivite alérgica → Cetotifeno + Anti-histamínico
    STEP 2: Hemorragia subconjuntival → Tranquilizar + verificar PA
    STEP 2: Hordéolo → Compressa morna + Tobramicina pomada
    STEP 2: Celulite pré-septal leve → Cefadroxila VO + retorno 24–48h
    STEP 3: Inespecífico → Oftalmo eletivo
    """

    # ── STEP 1: Trauma ──────────────────────────────────────────────────────
    if dados.get('trauma_penetrante') or dados.get('trauma_quimico'):
        return _resultado_trauma(dados)

    # ── STEP 1: Endoftalmite pós-cirúrgica ──────────────────────────────────
    if dados.get('endoftalmite_suspeita'):
        return _resultado_endoftalmite(dados)

    # ── STEP 1: Glaucoma agudo (halos + dor intensa + visão turva) ──────────
    if dados.get('glaucoma_agudo_suspeito'):
        return _resultado_glaucoma_agudo(dados)

    # ── STEP 1: Lente de contato + dor — Pseudomonas ────────────────────────
    # Gate explícito: mesmo dor MODERADA em usuário de lente = STEP 1
    if dados.get('ulcera_cornea_suspeita'):
        return _resultado_ulcera_cornea_lente(dados)

    # ── STEP 1: Ciliary flush → Uveíte / Glaucoma ───────────────────────────
    # Mesmo que outros critérios sejam limítrofes — ciliary flush = STEP 1
    if dados.get('ciliary_flush'):
        return _resultado_ciliary_flush(dados)

    # ── STEP 1: Celulite orbitária ───────────────────────────────────────────
    if dados.get('celulite_orbitaria_suspeita'):
        return _resultado_celulite_orbitaria(dados)

    # ── STEP 2: Celulite pré-septal (edema + febre, sem motilidade) ─────────
    if dados.get('celulite_preseptal_suspeita'):
        return _resultado_celulite_preseptal(dados)

    # ── STEP 2: Hordéolo (palpebral, doloroso, sem febre) ───────────────────
    if dados.get('hordeoleo_suspeito'):
        return _resultado_hordeoleo(dados)

    # ── STEP 2: Hemorragia subconjuntival (mancha vermelha brilhante) ────────
    if dados.get('hemorragia_subconj'):
        return _resultado_hemorragia_subconj(dados)

    # ── STEP 2: Conjuntivite bacteriana (pus + pálpebra grudada) ────────────
    if dados.get('conjuntivite_bacteriana_suspeita'):
        return _resultado_conjuntivite_bacteriana(dados)

    # ── STEP 2: Conjuntivite viral (adenovírus) ──────────────────────────────
    if dados.get('conjuntivite_viral_suspeita'):
        return _resultado_conjuntivite_viral(dados)

    # ── STEP 2: Conjuntivite alérgica (prurido dominante) ───────────────────
    if dados.get('conjuntivite_alergica_suspeita'):
        return _resultado_conjuntivite_alergica(dados)

    # ── STEP 3: Inespecífico / Oftalmo eletivo ───────────────────────────────
    return _resultado_investigar(dados)
