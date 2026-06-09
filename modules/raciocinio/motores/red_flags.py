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
