from modules.raciocinio.motores.priorizacao import classificar_forca

def interpretar_pneumo(texto):
    t = texto.lower()

    return {
        "mv_reduzido": any(p in t for p in [
            "mv diminu", "mv reduz", "hipofon", "abolido", "ausente"
        ]),
        "crepitacoes": any(p in t for p in [
            "crept", "crepit"
        ]),
        "sibilos": any(p in t for p in [
            "sibil", "chiado"
        ])
    }

def avaliar_pneumonia(subj, obj, admissao, paciente):
    score = 0
    achados = []

    if subj['febre']:
        score += 1
        achados.append('febre')

    if subj['tosse']:
        score += 2
        achados.append('tosse')

    if subj['dor_pleura']:
        score += 1
        achados.append('dor_pleuritica')

    pneumo_info = interpretar_pneumo(admissao['objetivo']['pneumo'])

    if pneumo_info["crepitacoes"]:
        if subj['febre'] or subj['tosse']:
            score += 3
            achados.append('crepitacoes_tipicas_infeccao')
        else:
            score += 1
            achados.append('crepitacoes_isoladas')

    if obj['jvd'] or obj['edema_bilateral_mmii']:
        score -= 1
        achados.append('sinais_congestivos_competindo_com_pneumonia')

    fr = int(admissao['fr'])
    if fr > 20:
        score += 1
        achados.append('taquipneia')

    forca = classificar_forca(score, forte=6, moderado=4)

    return {
        'diagnostico': 'pneumonia',
        'score': score,
        'forca': forca,
        'achados': achados,
        'provavel': forca in ['alta', 'moderada']
    }