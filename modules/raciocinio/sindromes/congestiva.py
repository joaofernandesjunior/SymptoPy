from modules.raciocinio.motores.priorizacao import classificar_forca
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
        score += 3
        achados.append('jvd')

    if obj['edema_bilateral_mmii']:
        score += 3
        achados.append('edema_bilateral_mmii')
    
    if int(admissao['sato2']) <= 92:
        score += 1
        achados.append('hipoxemia')

    pneumo = admissao['objetivo']['pneumo'].lower()
    if 'crept' in pneumo or 'crepit' in pneumo:
        score += 2
        achados.append('crepitacoes')

    forca = classificar_forca(score, forte=6, moderado=4)

    return {
        'diagnostico': 'insuficiencia_cardiaca',
        'score': score,
        'forca': forca,
        'achados': achados,
        'provavel': forca in ['alta', 'moderada']
    }