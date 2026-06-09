# modules/raciocinio/ivas/engine_ivas.py
# Motor de raciocínio clínico — IVAS / Faringite (adulto/adolescente ≥ 15 anos)
# Referências: ACP/CDC 2025 · IDSA 2025 · Guia de ATB resistência local
#
# Cascata: Emergência → Mononucleose → Influenza → GAS → Sinusite → Laringite → Viral
# Score: McIsaac modificado (Centor + ajuste de idade)
# Antibióticos: amoxicilina 1ª linha; penicilina V; benzatina IM; cefalexina; clindamicina

# =============================================================================
# SCORE DE McISAAC
# =============================================================================

def _calcular_mcisaac(dados):
    """
    Critérios:
      +1 exsudato tonsilar ou amígdalas aumentadas
      +1 linfonodos cervicais anteriores dolorosos
      +1 febre >= 38°C
      +1 ausência de tosse
      -1 idade >= 45 anos (adultos mais velhos têm menor prevalência de GAS)
    Adultos 15-44: ajuste 0; ≥45: -1
    """
    score = 0
    if dados.get('exsudato_tonsilar'):        score += 1
    if dados.get('linfadenopatia_anterior'):  score += 1
    if dados.get('febre_38'):                 score += 1
    if not dados.get('tosse_presente'):       score += 1  # ausência de tosse = +1

    idade = int(dados.get('idade', 30))
    if idade >= 45:
        score -= 1

    return max(score, -1)


def _interpretar_score(score, dados):
    """Retorna recomendação baseada no score e disponibilidade de RADT.

    Score ≥ 2:
      - RADT disponível → indicar_radt (preferência pelo teste em qualquer score)
      - RADT indisponível → tratar_empirico (qualquer score ≥2)
    IDSA: para score ≥4, 'RADT ou empírico' — sistema prefere RADT se disponível.
    """
    radt_realizado  = dados.get('radt_realizado', False)
    radt_positivo   = dados.get('radt_positivo', False)
    radt_disponivel = dados.get('radt_disponivel', True)

    if radt_realizado:
        if radt_positivo: return 'tratar'      # RADT+ → tratar
        else:             return 'nao_tratar'  # RADT− (adulto): descartar GAS

    if score <= 1:
        return 'nao_tratar'         # baixo risco — sem teste, sem ATB

    if radt_disponivel:
        return 'indicar_radt'       # RADT disponível → fazer o teste primeiro (score 2+)
    return 'tratar_empirico'        # RADT indisponível → tratar empiricamente (score 2+)


# =============================================================================
# RED FLAGS — EMERGÊNCIAS
# =============================================================================

_TIPOS_EMERGENCIA = {
    'abscesso_peritonsilar': {
        'nome':    'ABSCESSO PERITONSILAR (QUINSY)',
        'sinais':  'Assimetria tonsilar + desvio uvular + trismo + voz abafada ("batata quente")',
        'conduta': [
            'Encaminhar URGENTE para PS / otorrinolaringologia',
            'Punção aspirativa ou drenagem cirúrgica (I&D) — procedimento de escolha',
            'ATB IV: Ampicilina-Sulbactam 3 g IV 6/6h OU Clindamicina 600-900 mg IV 8/8h',
            'Cobertura para anaeróbios orais (amoxacilina-clavulanato IV)',
            'Hidratação IV e analgesia',
            'TC de pescoço com contraste se dúvida diagnóstica ou piora clínica',
            'Monitorar via aérea — avaliar necessidade de intubação',
        ],
    },
    'epiglotite': {
        'nome':    'EPIGLOTITE / SUPRAGLOTITE — RISCO IMEDIATO DE OBSTRUÇÃO',
        'sinais':  'Estridor + sialorreia + posição de tripé + disfagia grave + toxemia',
        'conduta': [
            'NÃO tentar visualizar epiglote com abaixador de língua — risco de obstrução total',
            'Manter paciente em posição confortável (sentado, inclinado para frente)',
            'Oxigênio suplementar se tolerado',
            'Acionar SAMU / chamar equipe de anestesia e ORL imediatamente',
            'Intubação em ambiente controlado (CC/UTI) — laringoscopia direta ou fibroscópica',
            'ATB IV (após via aérea segura): Ceftriaxona 2 g IV 24/24h OU Cefotaxima 2 g IV 6/6h',
            'Rx de pescoço lateral (apenas se paciente estável): sinal do polegar',
        ],
    },
    'ludwig': {
        'nome':    'ANGINA DE LUDWIG — CELULITE NECROTIZANTE DO ESPAÇO SUBMANDIBULAR',
        'sinais':  'Edema submandibular bilateral rígido + elevação de língua + infecção dentária',
        'conduta': [
            'EMERGÊNCIA — risco alto de obstrução de via aérea',
            'Acionar cirurgia bucomaxilofacial / ORL imediatamente',
            'Via aérea: considerar intubação precoce ou traqueostomia eletiva',
            'ATB IV: Ampicilina-Sulbactam 3 g IV 6/6h OU Pip-Tazo 4,5 g IV 6/6h',
            'TC de pescoço com contraste para avaliar extensão',
            'Drenagem cirúrgica se abscesso presente',
            'Internação em UTI para monitoramento de via aérea',
        ],
    },
}


def _tipo_emergencia(dados):
    """Identifica e retorna qual tipo de emergência está presente."""
    # Abscesso peritonsilar: assimetria + (trismo OU voz abafada OU sialorreia)
    if (dados.get('assimetria_tonsilar') and
            (dados.get('trismo') or dados.get('voz_abafada') or dados.get('sialorreia'))):
        return 'abscesso_peritonsilar'

    # Epiglotite: estridor + (sialorreia OU dificuldade respiratória)
    if dados.get('estridor') and (dados.get('sialorreia') or dados.get('dificuldade_respiratoria')):
        return 'epiglotite'

    # Ludwig: edema submandibular bilateral
    if dados.get('edema_submandibular'):
        return 'ludwig'

    # Qualquer dificuldade respiratória com queixa de garganta/pescoço
    if dados.get('dificuldade_respiratoria'):
        return 'epiglotite'  # presunção de epiglotite até prova em contrário

    return None


# =============================================================================
# ANTIBIÓTICOS — GAS FARINGITE
# =============================================================================

_ATBS = {
    'amoxicilina': {
        'medicamento':  'Amoxicilina 500mg',
        'dose':         '500mg VO de 8/8h por 10 dias',
        'via':          'Oral',
        'duracao':      '10 dias',
        'indicacao':    '1ª linha sem alergia à penicilina',
        'nota':         'Farmácia privada: 2cp (1g) ao dia × 10 dias (20cp) — mesma eficácia, mas causa fracionamento no SUS/Farmácia Popular',
        'prescricoes': [
            {'quantidade': 30, 'unidade': 'cápsulas',
             'posologia': 'Tomar 1 cápsula de 8 em 8 horas por 10 dias.'},
        ],
    },
    'penicilina_v': {
        'medicamento':  'Penicilina V 500mg',
        'dose':         '500mg VO 2x/dia',
        'via':          'Oral',
        'duracao':      '10 dias',
        'indicacao':    'Alternativa 1ª linha (espectro mais estreito que amoxicilina)',
        'nota':         '',
        'prescricoes': [
            {'quantidade': 20, 'unidade': 'comprimidos',
             'posologia': 'Tomar 1 comprimido de 12 em 12 horas por 10 dias.'},
        ],
    },
    'benzatina': {
        'medicamento':  'Penicilina G Benzatina 1.200.000 UI',
        'dose':         '1.200.000 UI IM dose única',
        'via':          'Intramuscular profunda (glúteo ou vasto lateral)',
        'duracao':      'Dose única',
        'indicacao':    'Aderência duvidosa OU histórico de febre reumática aguda',
        'nota':         'Preferida em contexto social precário ou FRA prévia',
        'prescricoes': [
            {'quantidade': 1, 'unidade': 'frasco-ampola',
             'posologia': 'Aplicar 1 injeção intramuscular profunda (glúteo) — dose única.'},
        ],
    },
    'cefalexina': {
        'medicamento':  'Cefalexina 500mg',
        'dose':         '500mg VO de 6/6h por 10 dias',
        'via':          'Oral',
        'duracao':      '10 dias',
        'indicacao':    'Alergia NÃO anafilática à penicilina',
        'nota':         'Cross-reatividade com penicilina < 1% nas alergias não anafiláticas',
        'prescricoes': [
            {'quantidade': 40, 'unidade': 'cápsulas',
             'posologia': 'Tomar 1 cápsula de 6 em 6 horas por 10 dias.'},
        ],
    },
    'cefadroxil': {
        'medicamento':  'Cefadroxila 1000mg',
        'dose':         '1000mg VO 1x/dia',
        'via':          'Oral',
        'duracao':      '10 dias',
        'indicacao':    'Alergia não anafilática à penicilina — dose única (aderência)',
        'nota':         '',
        'prescricoes': [
            {'quantidade': 10, 'unidade': 'comprimidos',
             'posologia': 'Tomar 1 comprimido ao dia por 10 dias.'},
        ],
    },
    'clindamicina': {
        'medicamento':  'Clindamicina 300mg',
        'dose':         '300mg VO 3x/dia',
        'via':          'Oral',
        'duracao':      '10 dias',
        'indicacao':    'Alergia ANAFILÁTICA à penicilina',
        'nota':         'Resistência GAS < 1%; risco de C. difficile maior que penicilinas',
        'prescricoes': [
            {'quantidade': 30, 'unidade': 'cápsulas',
             'posologia': 'Tomar 1 cápsula de 8 em 8 horas por 10 dias.'},
        ],
    },
    'azitromicina': {
        'medicamento':  'Azitromicina 500mg',
        'dose':         '500mg 1x/dia',
        'via':          'Oral',
        'duracao':      '3 dias',
        'indicacao':    'Alergia anafilática à penicilina (alternativa à clindamicina)',
        'nota':         'Atenção: resistência GAS crescente (5-15%) — solicitar cultura se falha terapêutica',
        'prescricoes': [
            {'quantidade': 3, 'unidade': 'comprimidos',
             'posologia': 'Tomar 1 comprimido ao dia por 3 dias.'},
        ],
    },
}


def _selecionar_atb(dados):
    """Retorna o dicionário do antibiótico mais adequado + alt (se houver)."""
    alergia    = dados.get('alergia_penicilina', False)
    anafilatica = dados.get('alergia_anafilatica', False)
    aderencia  = dados.get('aderencia_preocupa', False)
    fra        = dados.get('historico_fra', False)

    if not alergia:
        if aderencia or fra:
            return _ATBS['benzatina'], None
        return _ATBS['amoxicilina'], _ATBS['penicilina_v']

    if not anafilatica:
        return _ATBS['cefalexina'], _ATBS['cefadroxil']

    return _ATBS['clindamicina'], _ATBS['azitromicina']


# =============================================================================
# PRESCRIÇÕES ESTRUTURADAS — HELPERS
# =============================================================================

def _atb_to_rx(atb_dict, linha='1ª linha — ATB'):
    """Converte entrada _ATBS → formato prescricoes_estruturadas."""
    presc_out = []
    for p in atb_dict.get('prescricoes', []):
        qt   = p.get('quantidade', '')
        unit = p.get('unidade', '')
        presc_out.append({
            'quantidade': f'{qt} {unit}'.strip(),
            'unidade':    '',           # dose já embutida no nome do medicamento
            'posologia':  p.get('posologia', ''),
        })
    return {
        'linha':       linha,
        'medicamento': atb_dict.get('medicamento', ''),
        'prescricoes': presc_out,
        'nota':        atb_dict.get('nota', ''),
    }


_RX_SINT_IVAS = [
    {
        'linha':       '1ª linha — antipirético / analgésico',
        'medicamento': 'Dipirona',
        'prescricoes': [{'quantidade': '20 comprimidos', 'unidade': '500 mg',
                         'posologia': 'Tomar 1 comprimido a cada 6 horas se febre ou dor (máx 4×/dia).'}],
        'nota': '',
    },
    {
        'linha':       'Alternativo — anti-inflamatório (odinofagia intensa)',
        'medicamento': 'Ibuprofeno',
        'prescricoes': [{'quantidade': '30 comprimidos', 'unidade': '400 mg',
                         'posologia': 'Tomar 1 comprimido a cada 8 horas com alimento.'}],
        'nota': 'Evitar em gastrite, doença renal crônica ou uso de anticoagulante.',
    },
]

_ORI_IVAS = {
    'hidratacao':     'Ingerir ao menos 2 litros de líquidos por dia — água, chá morno, suco diluído.',
    'repouso':        'Repouso relativo até resolução da febre; retornar às atividades quando assintomático.',
    'atb_adesao':     'Completar todos os dias do antibiótico mesmo com melhora dos sintomas — interromper antes aumenta risco de resistência.',
    'sinais_retorno': 'Retornar se: febre por mais de 7 dias, dificuldade para respirar, trismo (não consegue abrir a boca) ou piora após melhora inicial.',
}


# =============================================================================
# CONDUTAS POR DIAGNÓSTICO
# =============================================================================

def _sintomaticos_viral():
    """Tratamento sintomático padrão para IVAS viral."""
    return [
        'Dipirona 500-1000 mg VO 6/6h se febre ou dor',
        'Alternativa: Paracetamol 500-1000 mg VO 6/6h (max 4 g/dia)',
        'AINE (ibuprofeno 400 mg VO 8/8h): opção para odinofagia intensa — eficaz para dor de garganta',
        'Pastilhas analgésicas (benzocaína, cetilpiridínio): alívio local',
        'Gargarejo com água morna + sal: melhora o desconforto faríngeo',
        'Hidratação oral adequada',
        'Repouso até resolução dos sintomas',
    ]


def _conduta_gas(dados, score, recomendacao, atb_principal, atb_alt):
    linhas = []
    prob_map = {-1: '< 7%', 0: '7-13%', 1: '7-13%', 2: '21-38%',
                3: '21-38%', 4: '51-70%', 5: '51-70%'}
    prob = prob_map.get(score, '> 50%')

    linhas.append(f'McIsaac: {score} pontos | Probabilidade GAS: {prob}')

    if recomendacao == 'nao_tratar':
        linhas += [
            'Conduta: NÃO tratar com antibiótico — baixo risco de GAS',
            'RADT não indicado — tratamento sintomático',
        ] + _sintomaticos_viral()
        linhas.append('Retorno se febre persistir > 5-7 dias ou surgir exsudato')
        return linhas

    if recomendacao == 'indicar_radt':
        linhas += [
            'Conduta: SOLICITAR RADT (Teste Rápido Estrepto) antes de prescrever ATB',
            '  Se RADT +: tratar com antibiótico (ver abaixo)',
            '  Se RADT − (adulto): NÃO tratar — sensibilidade 85-95% é suficiente em adultos',
            '  Criança/adolescente < 18 anos com RADT −: considerar cultura de orofaringe',
        ] + _sintomaticos_viral()
        linhas.append('')
        linhas.append('--- Se RADT positivo, prescrever ---')

    if recomendacao in ('tratar', 'tratar_empirico', 'indicar_radt'):
        if dados.get('radt_positivo'):
            linhas.insert(0, 'RADT positivo — GAS confirmado → tratar')
        elif recomendacao == 'tratar_empirico':
            linhas.append('Score 4-5: tratamento empírico ou confirmar com RADT disponível')

        linhas.append(f'ATB 1ª escolha: {atb_principal["medicamento"]}')
        linhas.append(f'  Dose: {atb_principal["dose"]}')
        linhas.append(f'  Via: {atb_principal["via"]} | Duração: {atb_principal["duracao"]}')
        if atb_principal.get('nota'):
            linhas.append(f'  Nota: {atb_principal["nota"]}')

        if atb_alt:
            linhas.append(f'ATB alternativo: {atb_alt["medicamento"]} — {atb_alt["dose"]}')

        linhas += [
            '',
            'ATENÇÃO: Duração de 10 dias é OBRIGATÓRIA — cursos menores não erradicam GAS',
            'NÃO tratar portadores crônicos assintomáticos (não transmitem e não têm risco de FRA)',
        ] + _sintomaticos_viral()
        linhas.append('Retorno: se piora ou não melhora em 48-72h com ATB → reavaliar')

    return linhas


def _conduta_mononucleose(dados):
    return [
        'DIAGNÓSTICO PROVÁVEL: MONONUCLEOSE INFECCIOSA (EBV)',
        '',
        '!! AMOXICILINA / AMPICILINA CONTRAINDICADAS !!',
        '  Risco de rash maculopapular em 80-100% dos pacientes com EBV + aminopenicilina',
        '  O rash NÃO indica alergia à penicilina — é reação imunológica específica do EBV',
        '',
        'Tratamento sintomático:',
        'Dipirona 500-1000 mg VO 6/6h OU Ibuprofeno 400-600 mg VO 8/8h se dor/febre',
        'Repouso relativo — fadiga pode persistir semanas a meses',
        '',
        'Restrição de esportes de contato: 4-6 SEMANAS (risco de ruptura esplênica)',
        'Palpação delicada de baço — evitar exame abdominal vigoroso',
        '',
        'Corticosteroides (prednisona 40-60 mg/dia × 5-7 dias): APENAS se:',
        '  Amígdalas causando obstrução de via aérea',
        '  Trombocitopenia grave ou anemia hemolítica',
        '  Não recomendado rotineiramente',
        '',
        'Workup confirmatório:',
        '  Monospot (anticorpos heterófilos): sens. 70-90% — pode ser negativo na 1ª semana',
        '  Se Monospot negativo: EBV-VCA IgM + EBNA (VCA IgM + = agudo; EBNA − = agudo)',
        '  Hemograma: linfocitose > 50% + > 10% linfócitos atípicos',
        '  TGO/TGP: elevação leve (2-3x normal) em 80-90%',
        'Retorno se: dor abdominal intensa, dispneia, piora progressiva',
    ]


def _conduta_influenza(dados):
    linhas = [
        'DIAGNÓSTICO PROVÁVEL: INFLUENZA',
        '',
        'Tratamento sintomático:',
        'Dipirona 500-1000 mg VO 6/6h OU Paracetamol 500-1000 mg VO 6/6h',
        'Evitar AAS em < 18 anos (Síndrome de Reye)',
        'Repouso e hidratação',
        '',
    ]

    # Oseltamivir
    dias = int(dados.get('dias_sintomas', 99))
    alto_risco = any([
        int(dados.get('idade', 30)) >= 65,
        dados.get('asma_dpoc'),
        dados.get('doenca_cardiovascular'),
        dados.get('drc'),
        dados.get('hepatopatia'),
        dados.get('diabetes'),
        dados.get('imunossupressao'),
        dados.get('gestante'),
        dados.get('obesidade_grave'),
    ])

    if dias <= 2:
        if alto_risco:
            linhas += [
                'OSELTAMIVIR INDICADO (alto risco + ≤ 48h de sintomas):',
                '  Oseltamivir 75 mg VO 2x/dia por 5 dias',
                '  Maior benefício se iniciado dentro de 12-24h do início dos sintomas',
                '  Prescrever mesmo sem teste confirmatório em alto risco durante temporada',
            ]
        else:
            linhas += [
                'Oseltamivir: paciente sem fator de risco — benefício limitado em adultos saudáveis',
                '  Pode considerar se sintomas graves ou evolução incomum',
                '  Dose: Oseltamivir 75 mg VO 2x/dia por 5 dias',
            ]
    else:
        linhas.append(f'Oseltamivir: sintomas com {dias} dias — > 48h, benefício mínimo (não indicado rotineiramente)')

    linhas += [
        '',
        'Investigação: Teste rápido influenza (RIDT) ou PCR durante temporada',
        '  PCR multiplex: maior sensibilidade (> 95%) — preferir se disponível',
        'Retorno se: dispneia, saturação < 95%, piora após melhora inicial (pneumonia pós-viral)',
    ]
    return linhas


def _conduta_rinossinusite(dados):
    sintomas_dias = int(dados.get('dias_sintomas', 0))
    duplo = dados.get('duplo_agravamento', False)
    linhas = [
        'DIAGNÓSTICO: RINOSSINUSITE AGUDA',
    ]
    # Maioria é viral nos primeiros 10 dias
    if sintomas_dias <= 10 and not duplo:
        linhas += [
            'Provável etiologia VIRAL (< 10 dias, sem duplo agravamento)',
            'ATB NÃO indicado — aguardar evolução',
            '',
            'Tratamento sintomático:',
            'Lavagem nasal com SF 0,9% (soro fisiológico): 3-4x/dia — base do tratamento',
            'Descongestionante tópico: oximetazolina spray nasal 0,1% — usar max 5-7 dias',
            'Corticoide nasal (fluticasona, mometasona): reduz inflamação e congestão',
            'Dipirona/AINE para dor facial e cefaleia',
            'Retorno se: > 10 dias sem melhora, dupla piora ou febre alta',
        ]
    else:
        linhas += [
            'Critérios de sinusite BACTERIANA: > 10 dias persistente OU duplo agravamento',
            'ATB indicado:',
            '  1ª linha: Amoxicilina-Clavulanato 875/125 mg VO 2x/dia por 5-7 dias',
            '  Alergia à penicilina: Doxiciclina 100 mg VO 2x/dia × 5-7 dias',
            '  Alternativa: Levofloxacino 500 mg VO 1x/dia × 5 dias',
            '',
            'Adjuvantes:',
            'Lavagem nasal SF 0,9%: 4-6x/dia',
            'Corticoide nasal (fluticasona) por 2-3 semanas',
            'Retorno se: piora clínica, febre > 72h com ATB, sintomas oculares/neurológicos',
        ]
    return linhas


def _conduta_laringite():
    return [
        'DIAGNÓSTICO: LARINGITE AGUDA (geralmente viral)',
        '',
        'ATB NÃO indicado — etiologia viral na maioria esmagadora dos casos',
        '',
        'Tratamento:',
        'Repouso vocal (falar apenas o necessário — sussurrar pode irritar mais que voz normal)',
        'Hidratação: água morna, chás sem cafeína — manter mucosa umidificada',
        'Umidificador de ar no quarto',
        'Evitar irritantes: tabaco, álcool, ar condicionado muito seco',
        'AINE (ibuprofeno 400 mg VO 8/8h): reduz inflamação laríngea',
        '',
        'Rouquidão persistente > 3 semanas sem causa clara → solicitar laringoscopia',
        '  Excluir: lesão benigna (nódulo, pólipo), DRGE, neoplasia laríngea',
    ]


def _conduta_viral():
    return [
        'DIAGNÓSTICO: IVAS VIRAL / FARINGITE VIRAL',
        '',
        'ATB NÃO indicado — etiologia viral confirmada pelo padrão clínico',
        '',
        'Tratamento sintomático:',
    ] + _sintomaticos_viral() + [
        '',
        'Duração esperada: 5-10 dias de evolução autolimitada',
        'Retorno se: febre > 7 dias, surgimento de exsudato, piora após melhora',
        'Orientar: não retornar apenas para "conseguir antibiótico" — não acelera a melhora',
    ]


# =============================================================================
# EXAMES
# =============================================================================

def _exames(categoria, dados, score):
    radt = dados.get('radt_realizado', False)

    if categoria == 'ivas_emergencia':
        return [
            'TC de pescoço com contraste (abscesso, extensão, via aérea)',
            'Hemograma + PCR + hemocultura (se toxêmico)',
            'Laringoscopia por ORL (avaliar via aérea)',
        ]
    if categoria == 'ivas_mononucleose':
        return [
            'Monospot (anticorpos heterófilos): sens 70-90%, pode ser neg na 1ª semana',
            'EBV-VCA IgM + EBNA: se Monospot negativo e suspeita mantida',
            'Hemograma: linfocitose + linfócitos atípicos > 10%',
            'TGO, TGP (elevação em 80-90%)',
            'RADT estrepto (co-infecção GAS em 30% dos casos de mono)',
        ]
    if categoria == 'ivas_gas':
        exs = []
        if not radt:
            exs.append('RADT (Teste Rápido Estrepto): indicado para score 2-3 antes de ATB')
        if score >= 4 and not radt:
            exs.append('  (Score ≥ 4: RADT ou tratamento empírico — ambas as opções são razoáveis)')
        if dados.get('alergia_anafilatica'):
            exs.append('Cultura de orofaringe + antibiograma (se usar azitromicina — resistência crescente)')
        if not exs:
            exs.append('RADT já realizado — nenhum exame adicional rotineiro')
        return exs
    if categoria == 'ivas_influenza':
        return [
            'RIDT (Teste rápido influenza): sens 50-70%; negativo não exclui na temporada',
            'PCR multiplex (painel respiratório): sens > 95% — preferir se disponível',
            'Hemograma: leucopenia leve comum na influenza',
            'Rx de tórax: se suspeita de pneumonia associada',
        ]
    if categoria == 'ivas_rinossinusite':
        return [
            'Sinusite viral < 10 dias: NÃO solicitar exame de imagem rotineiramente',
            'TC de seios paranasais (sem contraste): se complicação suspeita (celulite orbitária, meningite)',
            'Cultura de secreção nasal: considerar em falha de ATB ou suspeita de resistência',
        ]
    # laringite e viral
    return ['Nenhum exame rotineiro indicado — diagnóstico clínico']


# =============================================================================
# ENTRY POINT
# =============================================================================

def interpretar_ivas(dados):
    """
    Retorna dict com:
      categoria, tipo, diagnostico, score_mcisaac, recomendacao_atb,
      conduta, exames, sinais_retorno, [atb_prescrito], [emergencia_tipo]
    """
    score = _calcular_mcisaac(dados)

    # ── 1. EMERGÊNCIA (always first) ────────────────────────────────────────
    tipo_emerg = _tipo_emergencia(dados)
    if tipo_emerg:
        info = _TIPOS_EMERGENCIA.get(tipo_emerg, {})
        return {
            'tipo':          'ivas',
            'categoria':     'ivas_emergencia',
            'diagnostico':   info.get('nome', 'EMERGÊNCIA FARÍNGEA / CERVICAL'),
            'emergencia_tipo': tipo_emerg,
            'sinais_presentes': info.get('sinais', ''),
            'score_mcisaac': score,
            'conduta':       info.get('conduta', []),
            'exames':        _exames('ivas_emergencia', dados, score),
            'internacao':    True,
            'sinais_retorno': [],
        }

    # ── 2. MONONUCLEOSE ──────────────────────────────────────────────────────
    suspeita_mono = (
        int(dados.get('dias_sintomas', 0)) > 7 and
        (dados.get('linfadenopatia_posterior') or dados.get('esplenomegalia_referida')) and
        not dados.get('radt_positivo')   # GAS co-infecção possível mas mono domina
    )
    if suspeita_mono:
        return {
            'tipo':          'ivas',
            'categoria':     'ivas_mononucleose',
            'diagnostico':   'MONONUCLEOSE INFECCIOSA (EBV) — SUSPEITA',
            'score_mcisaac': score,
            'amoxicilina_contraindicada': True,
            'conduta':       _conduta_mononucleose(dados),
            'exames':        _exames('ivas_mononucleose', dados, score),
            'internacao':    False,
            'sinais_retorno': [
                'Dor abdominal intensa (ruptura esplênica)',
                'Dispneia ou estridor (obstrução tonsilar)',
                'Rigidez de nuca / cefaleia intensa (meningite)',
                'Fraqueza muscular progressiva (Guillain-Barré)',
            ],
            'prescricoes_estruturadas': list(_RX_SINT_IVAS),
            'orientacoes': {
                'repouso':            'Repouso relativo — fadiga pode durar semanas a meses.',
                'restricao_esportes': 'Proibido esportes de contato por 4 a 6 semanas — risco de ruptura esplênica.',
                'alerta_amoxicilina': 'NUNCA prescrever Amoxicilina ou Ampicilina durante mononucleose — causa rash intenso em 80-100% dos casos (não é alergia à penicilina).',
                'sinais_retorno':     'Retornar se: dor abdominal intensa, dificuldade respiratória ou rigidez de nuca.',
            },
        }

    # ── 3. INFLUENZA ─────────────────────────────────────────────────────────
    suspeita_influenza = (
        dados.get('inicio_subito_horas') and
        dados.get('mialgia_intensa') and
        (dados.get('febre_alta_39') or dados.get('febre_38')) and
        not dados.get('exsudato_tonsilar')   # influenza raramente tem exsudato
    )
    if suspeita_influenza:
        _dias_flu       = int(dados.get('dias_sintomas', 99))
        _alto_risco_flu = any([
            int(dados.get('idade', 30)) >= 65,
            dados.get('asma_dpoc'), dados.get('doenca_cardiovascular'),
            dados.get('drc'), dados.get('hepatopatia'), dados.get('diabetes'),
            dados.get('imunossupressao'), dados.get('gestante'), dados.get('obesidade_grave'),
        ])
        _rx_flu = [{
            'linha':       '1ª linha — antipirético',
            'medicamento': 'Dipirona',
            'prescricoes': [{'quantidade': '20 comprimidos', 'unidade': '500 mg',
                             'posologia': 'Tomar 1 comprimido a cada 6 horas se febre ou dor (máx 4×/dia).'}],
            'nota': '',
        }]
        if _dias_flu <= 2:
            _rx_flu.append({
                'linha':       ('Antiviral — indicado (alto risco + < 48h)' if _alto_risco_flu
                                else 'Antiviral — considerar (< 48h, sem fator de risco)'),
                'medicamento': 'Oseltamivir',
                'prescricoes': [{'quantidade': '10 cápsulas', 'unidade': '75 mg',
                                 'posologia': 'Tomar 1 cápsula a cada 12 horas por 5 dias — iniciar o mais cedo possível.'}],
                'nota': ('Indicado pelo fator de risco — iniciar sem aguardar confirmação laboratorial durante temporada.' if _alto_risco_flu
                         else 'Benefício limitado em adultos saudáveis — reduz duração ~1 dia se iniciado < 48h. Decisão compartilhada.'),
            })
        return {
            'tipo':          'ivas',
            'categoria':     'ivas_influenza',
            'diagnostico':   'INFLUENZA — SUSPEITA',
            'score_mcisaac': score,
            'conduta':       _conduta_influenza(dados),
            'exames':        _exames('ivas_influenza', dados, score),
            'internacao':    False,
            'sinais_retorno': [
                'Dispneia ou saturação < 95%',
                'Piora após melhora inicial (pneumonia pós-viral)',
                'Confusão mental, rigidez de nuca',
                'Cianose ou taquipneia',
            ],
            'prescricoes_estruturadas': _rx_flu,
            'orientacoes': {
                'hidratacao':     'Ingerir ao menos 2 litros de líquidos por dia.',
                'repouso':        'Repouso até resolução da febre; evitar contato com imunocomprometidos.',
                'sinais_retorno': 'Retornar se: falta de ar, saturação < 95%, confusão mental ou piora após melhora inicial (pneumonia pós-viral).',
            },
        }

    # ── 4. GAS FARINGITE ─────────────────────────────────────────────────────
    recomendacao = _interpretar_score(score, dados)
    if score >= 2 or dados.get('radt_positivo'):
        atb_principal, atb_alt = _selecionar_atb(dados)
        atb_prescrito = atb_principal if recomendacao in ('tratar', 'tratar_empirico') else None

        # criterios_usados — critérios individuais explícitos + justificativa da recomendação
        _crit_partes = []
        if dados.get('exsudato_tonsilar'):        _crit_partes.append('+1 exsudato tonsilar')
        if dados.get('linfadenopatia_anterior'):  _crit_partes.append('+1 linfonodo cervical anterior doloroso')
        if dados.get('febre_38'):                 _crit_partes.append('+1 febre ≥38°C')
        if not dados.get('tosse_presente'):       _crit_partes.append('+1 ausência de tosse')
        if int(dados.get('idade', 30)) >= 45:     _crit_partes.append('-1 idade ≥45 anos')
        _crit_str = '; '.join(_crit_partes) if _crit_partes else 'sem critérios positivos'
        _prob = '51-70%' if score >= 4 else '21-38%'

        if recomendacao == 'tratar':
            _criterios = f'RADT positivo — GAS confirmado. Critérios McIsaac {score}: {_crit_str}.'
        elif recomendacao == 'nao_tratar':
            _criterios = f'RADT negativo — GAS descartado em adultos. Critérios McIsaac {score}: {_crit_str}.'
        elif recomendacao == 'indicar_radt':
            _criterios = (
                f'Score McIsaac {score} (probabilidade GAS {_prob}): {_crit_str}. '
                f'RADT disponível — fazer o teste antes de prescrever ATB.'
            )
        else:  # tratar_empirico — RADT indisponível (único caminho com nova lógica)
            _criterios = (
                f'Score McIsaac {score} (probabilidade GAS {_prob}): {_crit_str}. '
                f'[!] RADT indisponível — upgrade para tratamento empírico imediato.'
            )

        # ── Prescrições estruturadas GAS ───────────────────────────────────────
        if recomendacao in ('tratar', 'tratar_empirico'):
            _rx_gas  = [_atb_to_rx(atb_principal, '1ª linha — ATB (GAS)')]
            if atb_alt:
                _rx_gas.append(_atb_to_rx(atb_alt, 'Alternativo — ATB (GAS)'))
            _rx_gas += list(_RX_SINT_IVAS)
            _ori_gas = _ORI_IVAS.copy()
        elif recomendacao == 'indicar_radt':
            _rx_gas  = list(_RX_SINT_IVAS)
            _ori_gas = {k: v for k, v in _ORI_IVAS.items() if k != 'atb_adesao'}
            _ori_gas['aguardar_radt'] = (
                'Antibiótico apenas se o teste rápido (RADT) for positivo — '
                'não iniciar ATB antes do resultado.'
            )
        else:  # nao_tratar
            _rx_gas  = list(_RX_SINT_IVAS)
            _ori_gas = {k: v for k, v in _ORI_IVAS.items() if k != 'atb_adesao'}

        return {
            'tipo':            'ivas',
            'categoria':       'ivas_gas',
            'diagnostico':     'FARINGITE — AVALIAÇÃO GAS (Estreptococo Grupo A)',
            'score_mcisaac':   score,
            'recomendacao_atb': recomendacao,
            'criterios_usados': _criterios,
            'atb_prescrito':   atb_prescrito,   # None quando indicar_radt (aguardando RADT)
            'atb_recomendado': atb_principal,   # SEMPRE presente — usado no plano condicional
            'atb_alternativo': atb_alt,          # SEMPRE presente
            'alergia_penicilina':  dados.get('alergia_penicilina', False),
            'odinofagia_severa':   dados.get('odinofagia_severa', False),
            'conduta':         _conduta_gas(dados, score, recomendacao, atb_principal, atb_alt),
            'exames':          _exames('ivas_gas', dados, score),
            'internacao':      False,
            'sinais_retorno': [
                'Não melhora em 48-72h com antibiótico → resistência ou diagnóstico errado',
                'Assimetria tonsilar ou trismo (abscesso peritonsilar)',
                'Rash cutâneo com ATB (mononucleose não diagnosticada)',
                'Febre persistente > 7 dias',
            ],
            'prescricoes_estruturadas': _rx_gas,
            'orientacoes':             _ori_gas,
        }

    # ── 5. RINOSSINUSITE ─────────────────────────────────────────────────────
    if (dados.get('dor_facial') and dados.get('descarga_purulenta') and
            (int(dados.get('dias_sintomas', 0)) > 10 or dados.get('duplo_agravamento')
             or dados.get('sintomas_10_dias'))):
        _bacteriana_rs = (int(dados.get('dias_sintomas', 0)) > 10
                          or dados.get('duplo_agravamento', False))
        if _bacteriana_rs:
            _rx_rs = [
                {
                    'linha':       '1ª linha — ATB (sinusite bacteriana)',
                    'medicamento': 'Amoxicilina-Clavulanato',
                    'prescricoes': [{'quantidade': '14 comprimidos', 'unidade': '875/125 mg',
                                     'posologia': 'Tomar 1 comprimido a cada 12 horas por 7 dias — de preferência com alimento.'}],
                    'nota': 'Alergia à penicilina: Doxiciclina 100 mg 2×/dia × 7 dias OU Levofloxacino 500 mg 1×/dia × 5 dias.',
                },
                {
                    'linha':       'Corticoide nasal (adjuvante)',
                    'medicamento': 'Fluticasona spray nasal',
                    'prescricoes': [{'quantidade': '1 frasco', 'unidade': '50 mcg/jato',
                                     'posologia': '2 jatos em cada narina, 1 vez ao dia. Incline levemente a cabeça para frente ao aplicar.'}],
                    'nota': '',
                },
            ]
        else:
            _rx_rs = [
                {
                    'linha':       'Corticoide nasal (viral — base do tratamento)',
                    'medicamento': 'Fluticasona spray nasal',
                    'prescricoes': [{'quantidade': '1 frasco', 'unidade': '50 mcg/jato',
                                     'posologia': '2 jatos em cada narina, 1 vez ao dia por 2 a 3 semanas.'}],
                    'nota': '',
                },
                {
                    'linha':       'Antipirético / analgésico (dor facial)',
                    'medicamento': 'Dipirona',
                    'prescricoes': [{'quantidade': '20 comprimidos', 'unidade': '500 mg',
                                     'posologia': 'Tomar 1 comprimido a cada 6 horas se dor ou febre.'}],
                    'nota': '',
                },
            ]
        return {
            'tipo':          'ivas',
            'categoria':     'ivas_rinossinusite',
            'diagnostico':   'RINOSSINUSITE AGUDA',
            'score_mcisaac': score,
            'conduta':       _conduta_rinossinusite(dados),
            'exames':        _exames('ivas_rinossinusite', dados, score),
            'internacao':    False,
            'sinais_retorno': [
                'Edema/eritema periorbital (celulite orbitária)',
                'Cefaleia intensa + rigidez de nuca (meningite)',
                'Déficit visual ou diplopia',
                'Piora com ATB após 72h',
            ],
            'prescricoes_estruturadas': _rx_rs,
            'orientacoes': {
                'lavagem_nasal':  'Lavagem nasal com soro fisiológico 0,9% — 3 a 4 vezes ao dia (seringa de 20 mL ou kit de lavagem nasal).',
                'hidratacao':     'Ingerir ao menos 2 litros de líquidos por dia.',
                'sinais_retorno': 'Retornar se: inchaço ao redor dos olhos, cefaleia intensa, rigidez de nuca, visão dupla ou piora com antibiótico.',
            },
        }

    # ── 6. LARINGITE ─────────────────────────────────────────────────────────
    if dados.get('rouquidao_predominante'):
        return {
            'tipo':          'ivas',
            'categoria':     'ivas_laringite',
            'diagnostico':   'LARINGITE AGUDA',
            'score_mcisaac': score,
            'conduta':       _conduta_laringite(),
            'exames':        _exames('ivas_laringite', dados, score),
            'internacao':    False,
            'sinais_retorno': [
                'Rouquidão persistente > 3 semanas (neoplasia laríngea)',
                'Estridor (obstrução de via aérea)',
                'Disfagia progressiva',
            ],
            'prescricoes_estruturadas': [
                {
                    'linha':       '1ª linha — anti-inflamatório (inflamação laríngea)',
                    'medicamento': 'Ibuprofeno',
                    'prescricoes': [{'quantidade': '30 comprimidos', 'unidade': '400 mg',
                                     'posologia': 'Tomar 1 comprimido a cada 8 horas com alimento — preferir horário fixo nas primeiras 48-72h.'}],
                    'nota': 'Alternativa se contraindicado: Dipirona 500 mg a cada 6 horas.',
                },
            ],
            'orientacoes': {
                'repouso_vocal': 'Repouso vocal — falar apenas o necessário e em voz normal (sussurrar pode irritar mais a laringe que a voz normal).',
                'hidratacao':    'Hidratação oral generosa: água morna, chás sem cafeína. Evitar tabaco, álcool e ar condicionado muito seco.',
                'sinais_retorno': 'Retornar se: rouquidão persistir mais de 3 semanas ou surgir dificuldade para respirar.',
            },
        }

    # ── 7. IVAS VIRAL (default) ───────────────────────────────────────────────
    return {
        'tipo':          'ivas',
        'categoria':     'ivas_viral',
        'diagnostico':   'IVAS VIRAL / FARINGITE VIRAL',
        'score_mcisaac': score,
        'conduta':       _conduta_viral(),
        'exames':        _exames('ivas_viral', dados, score),
        'internacao':    False,
        'sinais_retorno': [
            'Febre persistente > 7 dias',
            'Surgimento de exsudato tonsilar',
            'Piora abrupta após melhora inicial',
            'Dispneia ou estridor',
        ],
        'prescricoes_estruturadas': list(_RX_SINT_IVAS),
        'orientacoes': {
            'hidratacao':     _ORI_IVAS['hidratacao'],
            'repouso':        _ORI_IVAS['repouso'],
            'sinais_retorno': _ORI_IVAS['sinais_retorno'],
        },
    }
