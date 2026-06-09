def sn(pergunta):
    while True:
        resp = input(pergunta).strip().lower()
        if resp in ("s", "n"):
            return resp == "s"
        print("Digite s ou n.")


def perguntar_int(pergunta):
    while True:
        try:
            return int(input(pergunta).strip())
        except ValueError:
            print("Digite um número inteiro.")


def coletar_subjetivo_tosse():
    d = {}

    print("\n=== SUBJETIVO ESPECÍFICO: TOSSE ===")

    d["duracao_dias"] = perguntar_int("Há quantos dias está tossindo? ")

    d["produtiva"] = sn("A tosse tem catarro? ")
    d["hemoptise"] = sn("Tem sangue no escarro? ")

    d["febre"] = sn("Teve febre? ")
    d["dispneia"] = sn("Tem falta de ar? ")
    d["dor_pleuritica"] = sn("Tem dor no peito ao respirar ou tossir? ")
    d["coriza"] = sn("Tem coriza? ")
    d["odinofagia"] = sn("Tem dor de garganta? ")

    d["chiado"] = sn("Tem chiado no peito? ")
    d["asma"] = sn("Tem asma? ")
    d["dpoc"] = sn("Tem DPOC? ")

    d["perda_peso"] = sn("Teve perda de peso não intencional? ")
    d["sudorese_noturna"] = sn("Tem sudorese noturna? ")
    d["imunossupressao"] = sn("Tem imunossupressão? ")
    d["contato_tb"] = sn("Teve contato com tuberculose? ")

    d["vomitos"] = sn("Teve episódio recente de vômitos? ")
    d["disfagia"] = sn("Tem dificuldade para engolir? ")

    d["azia"] = sn("Tem azia ou queimação? ")
    d["regurgitacao"] = sn("Tem regurgitação ou gosto amargo na boca? ")
    d["pigarro"] = sn("Tem pigarro ou sensação de secreção escorrendo na garganta? ")
    d["tosse_noturna"] = sn("A tosse piora à noite? ")

    d["ieca"] = sn("Usa IECA (ex: captopril, enalapril, lisinopril)? ")

    return d