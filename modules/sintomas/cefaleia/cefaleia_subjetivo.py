def sn(pergunta):
    while True:
        resp = input(pergunta).strip().lower()
        if resp in ("s", "n"):
            return resp == "s"
        print("Digite s ou n.")


def coletar_subjetivo_cefaleia():
    d = {}

    # BASE
    d["nova"] = sn("É uma cefaleia nova? ")
    d["recorrente"] = sn("Já teve episódios semelhantes antes? ")
    d["inicio_subito"] = sn("Começou de forma súbita? ")
    d["pior_da_vida"] = sn("É a pior cefaleia da vida? ")
    d["inicio_esforco_sexo"] = sn("Começou durante esforço ou atividade sexual? ")

    d["localizacao_unilateral"] = sn("A dor é unilateral? ")
    d["pulsatil"] = sn("A dor é pulsátil? ")
    d["pressao"] = sn("A dor é em pressão/aperto? ")
    d["piora_atividade"] = sn("Piora com atividade física? ")

    # RED FLAGS
    d["febre"] = sn("Teve febre? ")
    d["rigidez_nuca"] = sn("Teve rigidez de nuca? ")
    d["confusao"] = sn("Teve confusão ou sonolência? ")
    d["deficit_focal"] = sn("Teve fraqueza, dormência ou fala alterada? ")
    d["alteracao_visual"] = sn("Teve alteração visual persistente? ")

    d["cancer"] = sn("Tem histórico de câncer? ")
    d["imunossupressao"] = sn("Tem imunossupressão? ")
    d["gestacao_puerperio"] = sn("Está grávida ou no puerpério? ")
    d["trauma"] = sn("Houve trauma recente? ")

    d["idade_maior_50_nova"] = sn("Tem mais de 50 anos e essa cefaleia é nova? ")
    d["progressiva"] = sn("A dor vem piorando progressivamente? ")
    d["valsalva"] = sn("Piora com tosse, espirro ou esforço? ")

    d["uso_analgesico_excessivo"] = sn("Usa analgésicos frequentemente? ")
    d["nova_medicacao"] = sn("Começou algum remédio novo recentemente? ")

    # DIRECIONADAS (só se não parecer grave)
    if not any([
        d["febre"], d["rigidez_nuca"], d["confusao"], d["deficit_focal"],
        d["cancer"], d["imunossupressao"], d["trauma"]
    ]):
        d["nausea"] = sn("Tem náusea ou vômitos? ")
        d["fotofobia"] = sn("Tem sensibilidade à luz? ")
        d["fonofobia"] = sn("Tem sensibilidade a sons? ")
        d["aura"] = sn("Teve aura antes da dor? ")

        d["lacrimejamento"] = sn("Tem lacrimejamento no olho do mesmo lado? ")
        d["rinorreia"] = sn("Tem coriza do mesmo lado da dor? ")
        d["agitacao"] = sn("Fica inquieto durante a crise? ")

    return d