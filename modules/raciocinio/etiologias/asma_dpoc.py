from modules.raciocinio.motores.priorizacao import classificar_forca
def avaliar_asma_dpoc(subj, obj, admissao, paciente):
    score = 0
    achados = []

    if subj['chiado']:
        score += 2
        achados.append('chiado')
    else:
        score -= 1

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