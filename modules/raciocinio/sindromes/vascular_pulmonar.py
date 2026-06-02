from modules.raciocinio.motores.priorizacao import classificar_forca

def avaliar_vascular_pulmonar(subj, obj, admissao, paciente):
    score = 0
    achados = []

    if subj["inicio_agudo"]:
        score += 2
        achados.append("inicio_agudo")

    if subj["dor_pleura"]:
        score += 2
        achados.append("dor_pleuritica")

    if subj["hemoptise"]:
        score += 2
        achados.append("hemoptise")

    if subj["sincope"]:
        score += 2
        achados.append("sincope")

    if obj["edema_unilateral_perna"]:
        score += 3
        achados.append("edema_unilateral_perna")

    if int(admissao["fc"]) > 100:
        score += 1
        achados.append("taquicardia")

    comorb = paciente["comorbidades"].lower()
    if "cancer" in comorb or "câncer" in comorb:
        score += 1
        achados.append("cancer")

    forca = classificar_forca(score, forte=5, moderado=3)

    return {
        "sindrome": "vascular_pulmonar",
        "score": score,
        "forca": forca,
        "achados": achados,
        "provavel": forca in ["alta", "moderada"]
    }