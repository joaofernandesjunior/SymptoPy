# =============================================================================
# SELEÇÃO DE ATB — PNEUMONIA AMBULATORIAL (PAC)
# Referência: IDSA/ATS 2019 · SBPT 2018 · UpToDate 2024
# =============================================================================

def _selecionar_atb_pac(paciente):
    """
    Retorna dicionário com esquema ATB para PAC ambulatorial.

    Cenário A — sem comorbidades e sem ATB nos últimos 90 dias:
        Amoxicilina 500mg 8/8h × 7 dias ± Azitromicina (se atípico)

    Cenário B — com comorbidades OU ATB < 90 dias:
        Opção 1: Amox-Clav 875/125mg 12/12h × 7d + Azitromicina 500mg 1x/d × 5d
        Opção 2 (alternativa): Levofloxacino 750mg 1x/d × 5d  OU  500mg × 7d
    """
    comorb = paciente.get('comorbidades', '').lower()
    chv    = paciente.get('chv', '').lower()
    idade  = int(paciente.get('idade', 0))

    cenario_b = any([
        'diabet'   in comorb,
        'icc'      in comorb or 'insuficiência cardíaca' in comorb,
        'dpoc'     in comorb,
        'drc'      in comorb or 'renal crônica' in comorb,
        'hiv'      in comorb or 'transplante' in comorb or 'imunossupres' in comorb,
        idade >= 65,
        ('atb' in chv or 'antibiótico' in chv) and ('90' in chv or '3 mes' in chv or 'recente' in chv),
    ])

    if not cenario_b:
        return {
            'cenario': 'A',
            'descricao': 'Sem comorbidades e sem ATB nos últimos 90 dias',
            'atb_principal': {
                'medicamento': 'Amoxicilina 500mg',
                'dose': '500mg VO 8/8h por 7 dias',
                'via': 'Oral',
                'duracao': '7 dias',
                'prescricoes': [
                    {'quantidade': 21, 'unidade': 'cápsulas',
                     'posologia': 'Tomar 1 cápsula de 8 em 8 horas por 7 dias.'},
                ],
            },
            'cobertura_atipico': {
                'medicamento': 'Azitromicina 500mg',
                'dose': '500mg VO 1x/dia por 5 dias',
                'via': 'Oral',
                'duracao': '5 dias',
                'nota': 'Adicionar se padrão de atípico: início gradual, tosse seca, pouco leucocitose, infiltrado intersticial',
                'prescricoes': [
                    {'quantidade': 5, 'unidade': 'comprimidos',
                     'posologia': 'Tomar 1 comprimido ao dia por 5 dias.'},
                ],
            },
        }

    return {
        'cenario': 'B',
        'descricao': 'Com comorbidades ou ATB nos últimos 90 dias',
        'opcao_1': {
            'nome': 'Amoxicilina+Clavulanato + Azitromicina (1ª linha preferida)',
            'atb_principal': {
                'medicamento': 'Amoxicilina+Clavulanato 875/125mg',
                'dose': '875/125mg VO 12/12h por 7 dias',
                'via': 'Oral',
                'duracao': '7 dias',
                'prescricoes': [
                    {'quantidade': 14, 'unidade': 'comprimidos',
                     'posologia': 'Tomar 1 comprimido de 12 em 12 horas por 7 dias.'},
                ],
            },
            'atb_atipico': {
                'medicamento': 'Azitromicina 500mg',
                'dose': '500mg VO 1x/dia por 5 dias',
                'via': 'Oral',
                'duracao': '5 dias',
                'prescricoes': [
                    {'quantidade': 5, 'unidade': 'comprimidos',
                     'posologia': 'Tomar 1 comprimido ao dia por 5 dias.'},
                ],
            },
        },
        'opcao_2': {
            'nome': 'Levofloxacino em monoterapia (quinolona respiratória)',
            'nota': 'Usar quando Amox-Clav indisponível, alergia confirmada ou falha terapêutica prévia. Reservar fluoroquinolonas sempre que possível.',
            'atb_principal': {
                'medicamento': 'Levofloxacino 750mg',
                'dose': '750mg VO 1x/dia por 5 dias',
                'via': 'Oral',
                'duracao': '5 dias',
                'prescricoes': [
                    {'quantidade': 5, 'unidade': 'comprimidos',
                     'posologia': 'Tomar 1 comprimido ao dia por 5 dias.'},
                ],
            },
            'alternativo': {
                'medicamento': 'Levofloxacino 500mg',
                'dose': '500mg VO 1x/dia por 7 dias',
                'via': 'Oral',
                'duracao': '7 dias',
                'prescricoes': [
                    {'quantidade': 7, 'unidade': 'comprimidos',
                     'posologia': 'Tomar 1 comprimido ao dia por 7 dias.'},
                ],
            },
        },
    }


def classificar_forca(score, forte, moderado):
    if score >= forte:
        return 'alta'
    if score >= moderado:
        return 'moderada'
    return 'baixa'


def avaliar_red_flags_dispneia(subj, obj, admissao):
    red_flags = []

    fc = int(admissao['fc'])
    fr = int(admissao['fr'])
    sato2 = float(str(admissao['sato2']).replace(',', '.'))

    if obj['musculatura_acessoria'] or obj['fala_entrecortada']:
        red_flags.append('desconforto_respiratorio')

    if sato2 < 92:
        red_flags.append('hipoxemia')

    if fr >= 24:
        red_flags.append('taquipneia')

    if subj['sincope']:
        red_flags.append('sincope_com_dispneia')

    if subj['inicio_agudo'] and subj['dor_pleura'] and obj['edema_unilateral_perna']:
        red_flags.append('tep_alto_risco')

    if subj['inicio_agudo'] and subj['repouso'] and obj['musculatura_acessoria']:
        red_flags.append('fisiologia_tensional_ou_gravidade')

    return red_flags


def avaliar_ic(subj, obj, admissao, paciente):
    score = 0
    achados = []

    if subj['ortopneia']:
        score += 2
        achados.append('ortopneia')

    if subj['dpn']:
        score += 2
        achados.append('dpn')

    if subj['dispneia_esforcos']:
        score += 1
        achados.append('dispneia_aos_esforcos')

    if subj['piora_progressiva']:
        score += 1
        achados.append('piora_progressiva')

    if obj['jvd']:
        score += 2
        achados.append('jvd')

    if obj['edema_bilateral_mmii']:
        score += 2
        achados.append('edema_bilateral_mmii')

    pneumo = admissao['objetivo']['pneumo'].lower()
    if 'crept' in pneumo or 'crepit' in pneumo:
        score += 1
        achados.append('crepitacoes')

    forca = classificar_forca(score, forte=6, moderado=4)

    return {
        'diagnostico': 'insuficiencia_cardiaca',
        'score': score,
        'forca': forca,
        'achados': achados,
        'provavel': forca in ['alta', 'moderada']
    }


def avaliar_obstrutivo(subj, obj, admissao, paciente):
    score = 0
    achados = []

    if subj['chiado']:
        score += 2
        achados.append('chiado')

    if subj['tosse']:
        score += 1
        achados.append('tosse')

    if obj['musculatura_acessoria']:
        score += 1
        achados.append('musculatura_acessoria')

    comorb = paciente['comorbidades'].lower()
    chv = paciente['chv'].lower()

    if 'asma' in comorb or 'dpoc' in comorb:
        score += 2
        achados.append('asma_ou_dpoc_previo')

    if 'tabag' in chv:
        score += 1
        achados.append('tabagismo')

    if subj['febre']:
        score -= 1

    if subj['ortopneia'] and subj['dpn']:
        score -= 1

    forca = classificar_forca(score, forte=5, moderado=3)

    return {
        'diagnostico': 'asma_dpoc',
        'score': score,
        'forca': forca,
        'achados': achados,
        'provavel': forca in ['alta', 'moderada']
    }


def avaliar_pneumonia(subj, obj, admissao, paciente):
    score = 0
    achados = []

    if subj['febre']:
        score += 2
        achados.append('febre')

    if subj['tosse']:
        score += 2
        achados.append('tosse')

    if subj['dor_pleura']:
        score += 1
        achados.append('dor_pleuritica')

    pneumo = admissao['objetivo']['pneumo'].lower()
    if 'crept' in pneumo or 'crepit' in pneumo:
        score += 2
        achados.append('crepitacoes')

    fr = int(admissao['fr'])
    if fr > 20:
        score += 1
        achados.append('taquipneia')

    forca = classificar_forca(score, forte=6, moderado=4)
    provavel = forca in ['alta', 'moderada']

    # Seleção de ATB apenas quando pneumonia é provável (evitar receita prematura)
    atb = _selecionar_atb_pac(paciente) if provavel else None

    return {
        'diagnostico': 'pneumonia',
        'score': score,
        'forca': forca,
        'achados': achados,
        'provavel': provavel,
        'atb_recomendado': atb,
    }


def avaliar_tep(subj, obj, admissao, paciente):
    score = 0
    achados = []

    if subj['inicio_agudo']:
        score += 2
        achados.append('inicio_agudo')

    if subj['dor_pleura']:
        score += 2
        achados.append('dor_pleuritica')

    if subj['hemoptise']:
        score += 2
        achados.append('hemoptise')

    if subj['sincope']:
        score += 2
        achados.append('sincope')

    if obj['edema_unilateral_perna']:
        score += 3
        achados.append('edema_unilateral_perna')

    if int(admissao['fc']) > 100:
        score += 1
        achados.append('taquicardia')

    comorb = paciente['comorbidades'].lower()
    if 'cancer' in comorb or 'câncer' in comorb:
        score += 1
        achados.append('cancer')

    forca = classificar_forca(score, forte=6, moderado=4)

    return {
        'diagnostico': 'tep',
        'score': score,
        'forca': forca,
        'achados': achados,
        'provavel': forca in ['alta', 'moderada']
    }


def avaliar_pneumotorax(subj, obj, admissao, paciente):
    score = 0
    achados = []

    if subj['inicio_agudo']:
        score += 2
        achados.append('inicio_agudo')

    if subj['dor_pleura']:
        score += 2
        achados.append('dor_pleuritica')

    if subj['repouso']:
        score += 1
        achados.append('dispneia_em_repouso')

    if obj['musculatura_acessoria']:
        score += 1
        achados.append('musculatura_acessoria')

    pneumo = admissao['objetivo']['pneumo'].lower()
    if 'mv diminu' in pneumo or 'ausente' in pneumo:
        score += 2
        achados.append('mv_diminuido_ou_ausente')

    forca = classificar_forca(score, forte=5, moderado=4)

    return {
        'diagnostico': 'pneumotorax',
        'score': score,
        'forca': forca,
        'achados': achados,
        'provavel': forca in ['alta', 'moderada']
    }


def avaliar_valvar_arritmia(subj, obj, admissao, paciente):
    score = 0
    achados = []

    cardio = admissao['objetivo']['cardio'].lower()

    if subj['dor_tx']:
        score += 1
        achados.append('dor_toracica')

    if 'sopro' in cardio:
        score += 2
        achados.append('sopro')

    if 'irregular' in cardio or 'arritm' in cardio:
        score += 2
        achados.append('ritmo_irregular')

    if obj['jvd']:
        score += 1
        achados.append('jvd')

    forca = classificar_forca(score, forte=4, moderado=3)

    return {
        'diagnostico': 'valvar_ou_arritmia',
        'score': score,
        'forca': forca,
        'achados': achados,
        'provavel': forca in ['alta', 'moderada']
    }

def tem_diagnostico(lista_diagnosticos, nome, forca_minima='alta'):
    for d in lista_diagnosticos:
        if d['diagnostico'] == nome:
            if forca_minima == 'alta' and d['forca'] == 'alta':
                return True
            if forca_minima == 'moderada' and d['forca'] in ['alta', 'moderada']:
                return True
    return False


def sugerir_scores_segunda_camada(provaveis, subj, obj, admissao, paciente):
    proximos_scores = []

    if tem_diagnostico(provaveis, 'tep', 'alta'):
        proximos_scores.append({
            'diagnostico': 'tep',
            'score': 'Wells/PERC',
            'motivo': 'TEP forte o suficiente para estratificação'
        })

    if tem_diagnostico(provaveis, 'pneumonia', 'alta'):
        proximos_scores.append({
            'diagnostico': 'pneumonia',
            'score': 'CURB-65',
            'motivo': 'Pneumonia forte o suficiente para estratificar gravidade/disposição'
        })

    if tem_diagnostico(provaveis, 'insuficiencia_cardiaca', 'alta'):
        proximos_scores.append({
            'diagnostico': 'insuficiencia_cardiaca',
            'score': 'BNP/eco pathway',
            'motivo': 'IC forte o suficiente para confirmação/estratificação'
        })

    if tem_diagnostico(provaveis, 'asma_dpoc', 'alta'):
        comorb = paciente['comorbidades'].lower()
        if 'dpoc' in comorb:
            proximos_scores.append({
                'diagnostico': 'asma_dpoc',
                'score': 'BAP-65',
                'motivo': 'DPOC exacerbado provável'
            })

    if tem_diagnostico(provaveis, 'valvar_ou_arritmia', 'alta'):
        cardio = admissao['objetivo']['cardio'].lower()
        if 'irregular' in cardio or 'fibril' in cardio:
            proximos_scores.append({
                'diagnostico': 'valvar_ou_arritmia',
                'score': 'CHA2DS2-VASc / HAS-BLED',
                'motivo': 'Somente se fibrilação atrial estiver confirmada'
            })

    return proximos_scores


def interpretar_dispneia(subj, obj, admissao, paciente):
    red_flags = avaliar_red_flags_dispneia(subj, obj, admissao)

    candidatos = [
        avaliar_ic(subj, obj, admissao, paciente),
        avaliar_obstrutivo(subj, obj, admissao, paciente),
        avaliar_pneumonia(subj, obj, admissao, paciente),
        avaliar_tep(subj, obj, admissao, paciente),
        avaliar_pneumotorax(subj, obj, admissao, paciente),
        avaliar_valvar_arritmia(subj, obj, admissao, paciente),
    ]

    provaveis = [c for c in candidatos if c['provavel']]
    provaveis.sort(key=lambda x: x['score'], reverse=True)

    diagnosticos_exclusao = []
    if not provaveis:
        diagnosticos_exclusao = ['anemia', 'psicogenico_ansiedade']

    exames_iniciais = ['ECG', 'Raio-X de tórax']

    if any(c['diagnostico'] == 'insuficiencia_cardiaca' for c in provaveis):
        exames_iniciais.extend(['BNP', 'Ecocardiograma'])

    if any(c['diagnostico'] == 'pneumonia' for c in provaveis):
        exames_iniciais.extend(['Hemograma', 'PCR'])

    if any(c['diagnostico'] == 'tep' and c['forca'] == 'alta' for c in provaveis):
        exames_iniciais.extend(['D-dímero'])

    proximos_scores = sugerir_scores_segunda_camada(provaveis, subj, obj, admissao, paciente)

    return {
    'red_flags': red_flags,
    'diagnosticos_provaveis': [c for c in provaveis if c['forca'] == 'alta'],
    'diagnosticos_possiveis': [c for c in provaveis if c['forca'] == 'moderada'],
    'diagnosticos_exclusao': diagnosticos_exclusao,
    'exames_iniciais': exames_iniciais,
    'proximos_scores': proximos_scores,
    'proximos_passos_diagnosticos': [
        'Aplicar Wells/PERC se TEP seguir relevante',
        'Aplicar CURB-65 se pneumonia provável',
        'Solicitar BNP/NT-proBNP se IC provável',
        'Aplicar BAP-65 se padrão compatível com DPOC exacerbado'
    ]
}