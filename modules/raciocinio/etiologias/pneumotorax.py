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

def avaliar_pneumotorax(subj, obj, admissao, paciente):
    score = 0
    achados = []

    if subj['inicio_agudo']:
        score += 2
        achados.append('inicio_agudo')

    if subj['dor_pleura']:
        score += 2
        achados.append('dor_pleuritica')

    pneumo_info = interpretar_pneumo(admissao['objetivo']['pneumo'])

    if pneumo_info["mv_reduzido"]:
        score += 5  # aqui você aumenta o peso
        achados.append('mv_diminuido_ou_ausente')

    if subj['repouso']:
        score += 1
        achados.append('dispneia_em_repouso')

    if obj['musculatura_acessoria']:
        score += 1
        achados.append('musculatura_acessoria')

    forca = classificar_forca(score, forte=6, moderado=5)

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