from modules.raciocinio.motores.priorizacao import classificar_forca

def avaliar_respiratoria_infecciosa(subj, obj, admissao, paciente):
    score = 0
    achados = []

    if subj["febre"]:
        score += 1
        achados.append("febre")

    if subj["tosse"]:
        score += 2
        achados.append("tosse")

    if subj["dor_pleura"]:
        score += 1
        achados.append("dor_pleuritica")

    pneumo = admissao["objetivo"]["pneumo"].lower()
    if "crept" in pneumo or "crepit" in pneumo:
        score += 3
        achados.append("crepitacoes")

    if int(admissao["fr"]) > 20:
        score += 1
        achados.append("taquipneia")

    forca = classificar_forca(score, forte=5, moderado=3)

    return {
        "sindrome": "respiratoria_infecciosa",
        "score": score,
        "forca": forca,
        "achados": achados,
        "provavel": forca in ["alta", "moderada"]
    }