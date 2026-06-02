from utils.perguntas import sn


def coletar_subjetivo_vertigem():
    dados = {}

    print("\n=== SUBJETIVO ESPECÍFICO: VERTIGEM / TONTURA ===")

    dados["sensacao_rotatoria"] = sn("A tontura é tipo o ambiente rodando? [s/n] ")
    dados["sensacao_pre_sincope"] = sn("Parece que vai desmaiar? [s/n] ")
    dados["desequilibrio"] = sn("A principal sensação é desequilíbrio ao andar ou ficar em pé? [s/n] ")

    print("\n--- TIMING ---")
    dados["inicio_subito"] = sn("Começou de forma súbita? [s/n] ")
    dados["duracao_segundos_minutos"] = sn("Os episódios duram segundos a poucos minutos? [s/n] ")
    dados["duracao_horas"] = sn("Os episódios duram horas? [s/n] ")
    dados["duracao_dias"] = sn("Os sintomas ficam contínuos por dias? [s/n] ")
    dados["recorrente"] = sn("Acontece em episódios recorrentes? [s/n] ")
    dados["continuo"] = sn("A tontura fica contínua, sem voltar totalmente ao normal? [s/n] ")

    print("\n--- TRIGGERS ---")
    dados["gatilho_mudar_posicao"] = sn("Piora ou começa ao virar na cama, olhar para cima ou mudar a posição da cabeça? [s/n] ")
    dados["gatilho_levantar"] = sn("Acontece ao levantar da cama ou da cadeira? [s/n] ")
    dados["gatilho_esforco"] = sn("Acontece com esforço físico? [s/n] ")
    dados["gatilho_espontaneo"] = sn("Acontece sem gatilho claro? [s/n] ")

    print("\n--- ASSOCIADOS ---")
    dados["nauseas_vomitos"] = sn("Tem náuseas ou vômitos? [s/n] ")
    dados["cefaleia"] = sn("Tem cefaleia junto? [s/n] ")
    dados["diplopia"] = sn("Tem visão dupla? [s/n] ")
    dados["disartria"] = sn("Tem fala enrolada? [s/n] ")
    dados["fraqueza"] = sn("Tem fraqueza em braço ou perna? [s/n] ")
    dados["parestesias"] = sn("Tem dormência ou formigamento? [s/n] ")
    dados["perda_auditiva"] = sn("Tem perda auditiva? [s/n] ")
    dados["zumbido"] = sn("Tem zumbido? [s/n] ")
    dados["plenitude_auricular"] = sn("Tem sensação de ouvido tampado/cheio? [s/n] ")
    dados["palpitacoes"] = sn("Tem palpitações? [s/n] ")
    dados["dor_toracica"] = sn("Tem dor no peito? [s/n] ")
    dados["sincope"] = sn("Chegou a desmaiar? [s/n] ")
    dados["infeccao_recente"] = sn("Teve infecção viral recente? [s/n] ")
    dados["trauma"] = sn("Teve trauma recente? [s/n] ")

    return dados

if __name__ == "__main__":
    dados = coletar_subjetivo_vertigem()
    print(dados)