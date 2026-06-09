from modules.raciocinio.motores.priorizacao import classificar_forca
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
        score += 4
        achados.append('edema_unilateral_perna')

    if int(admissao['fc']) > 100:
        score += 1
        achados.append('taquicardia')

    comorb = paciente['comorbidades'].lower()
    if 'cancer' in comorb or 'câncer' in comorb:
        score += 1
        achados.append('cancer')

    forca = classificar_forca(score, forte=6, moderado=4)

    # Conduta por probabilidade (Wells) — ESC 2019
    if forca == 'alta':
        conduta_tep = (
            'Wells ALTA PROBABILIDADE (≥5): '
            'AngioTC de tórax IMEDIATAMENTE — não solicitar D-dímero. '
            'Se instabilidade hemodinâmica: ecocardiograma à beira do leito antes da AngioTC. '
            'Anticoagular empiricamente se AngioTC não disponível em < 1h.'
        )
        ddimero_indicado = False
    elif forca == 'moderada':
        conduta_tep = (
            'Wells PROBABILIDADE MODERADA (2–4): '
            'D-dímero quantitativo. Se positivo → AngioTC de tórax. '
            'Se D-dímero negativo + sem fatores de alta suspeita → TEP excluído.'
        )
        ddimero_indicado = True
    else:
        conduta_tep = (
            'Wells BAIXA PROBABILIDADE (< 2): '
            'D-dímero quantitativo. Se negativo → TEP excluído com alta segurança. '
            'Se positivo → AngioTC de tórax.'
        )
        ddimero_indicado = True

    return {
        'diagnostico': 'tep',
        'score': score,
        'forca': forca,
        'achados': achados,
        'provavel': forca in ['alta', 'moderada'],
        'conduta_tep': conduta_tep,
        'ddimero_indicado': ddimero_indicado,
    }