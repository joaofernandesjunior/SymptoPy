from utils.perguntas import sn

def _interpretar_hints(hi_alterado, ny_multidirecional, skew_presente):
    """
    Interpreta os três componentes do HINTS e devolve resultado + motivo.
 
    Regra: qualquer componente sugestivo de central = central.
    HINTS benigno exige os TRÊS periféricos simultaneamente.
    """
    achados_centrais = []
 
    if not hi_alterado:
        achados_centrais.append("Head Impulse negativo (reflexo vestíbulo-ocular intacto)")
    if ny_multidirecional:
        achados_centrais.append("Nistagmo multidirecional")
    if skew_presente:
        achados_centrais.append("Test of Skew positivo (desvio vertical)")
 
    if achados_centrais:
        return True, achados_centrais   # preocupante=True, motivos
    else:
        return False, []                # preocupante=False, sem achados centrais

def coletar_objetivo_vertigem():
    obj = {}

    print("\n=== OBJETIVO ESPECÍFICO: VERTIGEM / TONTURA ===")

    obj["deficit_focal"] = sn("Há déficit neurológico focal ao exame? [s/n] ")
    obj["incapaz_de_andar"] = sn("O paciente está incapaz de andar sem ajuda? [s/n] ")

    print("\n--- DIX-HALLPIKE ---")
    obj["dix_hallpike_realizado"] = sn("Dix-Hallpike foi realizado? [s/n] ")
    if obj["dix_hallpike_realizado"]:
        obj["dix_hallpike_positivo"] = sn("Dix-Hallpike foi positivo/típico para VPPB? [s/n] ")
    else:
        obj["dix_hallpike_positivo"] = False

    print("\n--- ORTOSTATISMO ---")
    obj["ortostatismo_sugestivo"] = sn("Há ortostatismo sugestivo ao exame/sinais vitais? [s/n] ")

    print("\n--- HINTS ---")
    print("(Indicado em síndrome vestibular aguda contínua — não usar em episódica posicional)")
    obj["hints_realizado"] = sn("HINTS foi realizado? [s/n] ")
 
    if obj["hints_realizado"]:
 
        print("\n  [1/3] HEAD IMPULSE TEST")
        print("  Vire rapidamente a cabeça do paciente ~20° para cada lado.")
        print("  Observe se os olhos ficam fixos no alvo ou fazem sacada corretiva.")
        hi_alterado = sn("  Head Impulse ALTERADO (sacada corretiva visível)? [s/n] ")
 
        print("\n  [2/3] NYSTAGMUS")
        print("  Peça ao paciente para olhar reto, depois para direita, depois para esquerda.")
        print("  Observe a direção do nistagmo em cada posição do olhar.")
        ny_multidirecional = sn("  Nistagmo MUDA DE DIREÇÃO conforme posição do olhar? [s/n] ")
 
        print("\n  [3/3] TEST OF SKEW")
        print("  Cubra e descubra alternadamente cada olho (cover-uncover test).")
        print("  Observe se há desvio vertical do olho ao ser descoberto.")
        skew_presente = sn("  Desvio vertical presente (Test of Skew positivo)? [s/n] ")
 
        preocupante, motivos = _interpretar_hints(hi_alterado, ny_multidirecional, skew_presente)
 
        print("\n  >>> RESULTADO HINTS:")
        if preocupante:
            print("SUGESTIVO DE CAUSA CENTRAL")
            for m in motivos:
                print(f"     - {m}")
            print("  Conduta: neuroimagem e avaliação urgente.")
        else:
            print("  ✓  HINTS BENIGNO — padrão periférico nos três componentes.")
            print("  Head Impulse alterado + nistagmo unidirecional + sem skew.")
            print("  Mais compatível com neurite vestibular ou causa periférica.")
 
        obj["hints_preocupante"] = preocupante
        obj["hints_componentes"] = {
            "hi_alterado": hi_alterado,
            "ny_multidirecional": ny_multidirecional,
            "skew_presente": skew_presente,
        }
 
    else:
        obj["hints_preocupante"] = False
        obj["hints_componentes"] = None
 
    obj["perda_auditiva_nova_objetiva"] = sn("\nHá perda auditiva nova ao exame? [s/n] ")
 
    return obj