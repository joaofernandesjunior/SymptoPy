from modules.raciocinio.motores.red_flags import avaliar_red_flags_dispneia
from modules.raciocinio.motores.priorizacao import sugerir_scores_segunda_camada

from modules.raciocinio.sindromes.congestiva import avaliar_ic
from modules.raciocinio.sindromes.broncoespastica import avaliar_obstrutivo
from modules.raciocinio.sindromes.respiratoria_infecciosa import avaliar_respiratoria_infecciosa
from modules.raciocinio.sindromes.vascular_pulmonar import avaliar_vascular_pulmonar

from modules.raciocinio.etiologias.pneumonia import avaliar_pneumonia
from modules.raciocinio.etiologias.tep import avaliar_tep
from modules.raciocinio.etiologias.asma_dpoc import avaliar_asma_dpoc
from modules.raciocinio.etiologias.pneumotorax import avaliar_pneumotorax

def interpretar_dispneia(subj, obj, admissao, paciente):
    red_flags = avaliar_red_flags_dispneia(subj, obj, admissao)

    sindromes = {
    "congestiva": avaliar_ic(subj, obj, admissao, paciente),
    "broncoespastica": avaliar_obstrutivo(subj, obj, admissao, paciente),
    "respiratoria_infecciosa": avaliar_respiratoria_infecciosa(subj, obj, admissao, paciente),
    "vascular_pulmonar": avaliar_vascular_pulmonar(subj, obj, admissao, paciente),
}

    candidatos = []

    if sindromes["congestiva"]["provavel"]:
        candidatos.append(sindromes["congestiva"])

    if sindromes["broncoespastica"]["provavel"]:
        candidatos.append(avaliar_asma_dpoc(subj, obj, admissao, paciente))

    if sindromes["respiratoria_infecciosa"]["provavel"]:
        candidatos.append(avaliar_pneumonia(subj, obj, admissao, paciente))

    if sindromes["vascular_pulmonar"]["provavel"]:
        candidatos.append(avaliar_tep(subj, obj, admissao, paciente))

    pneumo_result = avaliar_pneumotorax(subj, obj, admissao, paciente)

    if pneumo_result["score"] > 0:
        candidatos.append(pneumo_result)

    if any(c["diagnostico"] == "tep" and c["forca"] == "alta" for c in candidatos):
        candidatos = [c for c in candidatos if c["diagnostico"] != "pneumotorax"]

    provaveis = [c for c in candidatos if c["provavel"]]
    provaveis.sort(key=lambda x: x["score"], reverse=True)

    diagnosticos_exclusao = []
    if not provaveis:
        diagnosticos_exclusao = ["anemia", "psicogenico_ansiedade"]

    exames_iniciais = ["Raio-X de tórax"]

    if any(c["diagnostico"] == "pneumonia" for c in provaveis):
        exames_iniciais.extend(["Hemograma", "PCR"])

    if any(c["diagnostico"] == "tep" and c["forca"] == "alta" for c in provaveis):
        exames_iniciais.append("D-dímero")

    proximos_scores = sugerir_scores_segunda_camada(provaveis, subj, obj, admissao, paciente)

    return {
        "red_flags": red_flags,
        "sindromes": sindromes,
        "diagnosticos_provaveis": [c for c in provaveis if c["forca"] == "alta"],
        "diagnosticos_possiveis": [c for c in provaveis if c["forca"] == "moderada"],
        "diagnosticos_exclusao": diagnosticos_exclusao,
        "exames_iniciais": exames_iniciais,
        "proximos_scores": proximos_scores,
    }

