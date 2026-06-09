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

    return proximos_scores


def classificar_forca(score, forte, moderado):
    if score >= forte:
        return 'alta'
    if score >= moderado:
        return 'moderada'
    return 'baixa'