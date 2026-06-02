def tem_drc(comorbidades_texto: str) -> bool:
    texto = (comorbidades_texto or "").lower()
    chaves = [
        "drc",
        "doenca renal cronica",
        "doença renal crônica",
        "hemodialise",
        "hemodiálise",
        "dialise",
        "diálise",
    ]
    return any(chave in texto for chave in chaves)


def coletar_complemento_drc() -> dict:
    complemento = {}

    complemento["creatinina_basal"] = input("Creatinina basal ou eGFR basal conhecidos: ").strip()
    complemento["faz_dialise"] = input("Faz diálise? [s/n] ").strip().lower() == "s"

    if complemento["faz_dialise"]:
        complemento["ultima_dialise"] = input("Última diálise: ").strip()
        complemento["problema_acesso"] = input("Problema com acesso/cateter? [s/n] ").strip().lower() == "s"
    else:
        complemento["ultima_dialise"] = ""
        complemento["problema_acesso"] = False

    complemento["perdeu_medicacoes_ou_otc"] = input(
        "Perdeu medicações recentemente ou usou OTC/suplementos novos? "
    ).strip()

    return complemento


def revisar_medicacoes_drc(medicacoes_texto: str) -> list[str]:
    texto = (medicacoes_texto or "").lower()
    alertas = []

    meds_drc = {
        "aumentam_potassio": {
            "losartana": "Losartana/BRA pode aumentar potássio.",
            "enalapril": "Enalapril/IECA pode aumentar potássio.",
            "captopril": "Captopril/IECA pode aumentar potássio.",
            "espironolactona": "Espironolactona aumenta risco de hipercalemia.",
            "trimetoprim": "Trimetoprim pode aumentar potássio.",
        },
        "pioram_funcao_renal": {
            "ibuprofeno": "Ibuprofeno/AINE pode piorar função renal.",
            "diclofenaco": "Diclofenaco/AINE pode piorar função renal.",
            "naproxeno": "Naproxeno/AINE pode piorar função renal.",
            "cetoprofeno": "Cetoprofeno/AINE pode piorar função renal.",
        },
        "rever_dose_ou_seguranca": {
            "metformina": "Metformina: revisar segurança conforme TFG/contexto clínico.",
            "gabapentina": "Gabapentina pode exigir ajuste renal.",
            "pregabalina": "Pregabalina pode exigir ajuste renal.",
            "rivaroxabana": "Rivaroxabana: revisar dose conforme função renal.",
            "apixabana": "Apixabana: revisar dose conforme função renal.",
            "dabigatrana": "Dabigatrana: revisar dose conforme função renal.",
            "nitrofurantoina": "Nitrofurantoína: revisar uso se TFG baixa.",
            "nitrofurantoína": "Nitrofurantoína: revisar uso se TFG baixa.",
        },
        "rever_no_contexto_agudo": {
            "dapagliflozina": "Dapagliflozina: revisar conforme contexto agudo/volume/função renal.",
        }
    }

    for grupo in meds_drc.values():
        for nome, alerta in grupo.items():
            if nome in texto:
                alertas.append(alerta)

    return alertas


def captar_pistas_eliminacoes(eliminacoes_texto: str) -> dict:
    texto = (eliminacoes_texto or "").lower()

    pistas = {
        "anuria": False,
        "oliguria": False,
        "sem_diurese": False,
        "dialise_mencionada": False,
    }

    if "anuria" in texto or "anúria" in texto:
        pistas["anuria"] = True

    if "oliguria" in texto or "oligúria" in texto:
        pistas["oliguria"] = True

    if "sem diurese" in texto:
        pistas["sem_diurese"] = True

    if "ultima urina ha" in texto or "última urina há" in texto:
        pistas["sem_diurese"] = True

    if "hemodialise" in texto or "hemodiálise" in texto or "dialise" in texto or "diálise" in texto:
        pistas["dialise_mencionada"] = True

    return pistas


def avaliar_red_flags_drc(admissao: dict) -> list[str]:
    red_flags = []

    eliminacoes = (admissao.get("objetivo", {}).get("eliminacoes", "") or "").lower()
    analise = (admissao.get("analise", "") or "").lower()

    pistas = captar_pistas_eliminacoes(eliminacoes)

    if pistas["anuria"] or pistas["sem_diurese"]:
        red_flags.append("Anúria/ausência de diurese: avaliar urgência renal.")

    if pistas["oliguria"]:
        red_flags.append("Oligúria importante: avaliar agudização/hipoperfusão/obstrução.")

    if "hipercalemia" in analise or "hiperpotassemia" in analise:
        red_flags.append("Suspeita de hipercalemia: correlacionar com potássio.")

    if "edema agudo de pulmao" in analise or "edema agudo de pulmão" in analise:
        red_flags.append("Possível sobrecarga volêmica grave.")

    return red_flags


def montar_perguntas_sugeridas_drc() -> list[str]:
    return [
        "Creatinina basal ou eGFR basal conhecidos?",
        "Faz diálise? Quando foi a última sessão?",
        "Houve problema com acesso/cateter?",
        "Perdeu medicações ou usou OTC/suplementos novos?",
    ]


def montar_exames_sugeridos_drc() -> list[str]:
    return [
        "Potássio - avaliar hipercalemia",
        "Creatinina - comparar com basal / avaliar agudização",
        "Bicarbonato - avaliar acidose metabólica",
        "EAS - avaliar infecção, hematúria ou injúria glomerular",
        "Hemoglobina - avaliar anemia",
        "ECG - considerar se hipercalemia detectada ou fortemente suspeita",
    ]


def montar_alertas_fixos_drc() -> list[str]:
    return [
        "Revisar potássio e função renal.",
        "Comparar creatinina com basal, se disponível.",
        "Revisar medicações com risco renal/eletrolítico.",
        "Lembrar descompensações comuns da DRC: hipercalemia, acidose, sobrecarga volêmica e agudização da função renal.",
        "Revisar necessidade de ajuste de dose de medicações conforme função renal."
    ]


def avaliar_drc(paciente: dict, admissao: dict) -> dict | None:
    comorbidades = paciente.get("comorbidades", "")
    medicacoes = paciente.get("medicacoes", "")

    if not tem_drc(comorbidades):
        return None

    resultado = {
        "comorbidade": "drc",
        "alertas_fixos": montar_alertas_fixos_drc(),
        "perguntas_sugeridas": montar_perguntas_sugeridas_drc(),
        "exames_sugeridos": montar_exames_sugeridos_drc(),
        "medicacoes_em_atencao": revisar_medicacoes_drc(medicacoes),
        "red_flags": avaliar_red_flags_drc(admissao),
    }

    return resultado