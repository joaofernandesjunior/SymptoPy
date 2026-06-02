# modules/raciocinio/vertigem_dx.py
# Motor de raciocínio clínico — Vertigem e Tonturas
# Arquitetura: legado — compatível com dispatcher.py
# Condutas: listas detalhadas com manobras, doses e encaminhamento

# =============================================================================
# CLASSIFICAÇÃO TITRATE (inalterada)
# =============================================================================

def classificar_titrate(subj):
    # 1. Aguda contínua / síndrome vestibular aguda
    if subj["continuo"] and subj["duracao_dias"]:
        return "aguda_continua"

    # 2. Episódica desencadeada por posição
    if (
        subj["gatilho_mudar_posicao"]
        and subj["duracao_segundos_minutos"]
        and subj["recorrente"]
        and subj["sensacao_rotatoria"]
    ):
        return "episodica_desencadeada"

    # 3. Episódica espontânea
    if (
        subj["gatilho_espontaneo"]
        and subj["recorrente"]
        and (subj["duracao_segundos_minutos"] or subj["duracao_horas"])
    ):
        return "episodica_espontanea"

    # 4. Presíncope
    if subj["sensacao_pre_sincope"] or subj["sincope"]:
        return "presincope"

    # 5. Desequilíbrio
    if subj["desequilibrio"] and not subj["sensacao_rotatoria"]:
        return "desequilibrio"

    return "indefinida"


def detectar_red_flags_subjetivas(subj):
    red_flags = []
    if subj["diplopia"]:    red_flags.append("diplopia")
    if subj["disartria"]:   red_flags.append("disartria")
    if subj["fraqueza"]:    red_flags.append("fraqueza")
    if subj["parestesias"]: red_flags.append("parestesias")
    if subj["cefaleia"]:    red_flags.append("cefaleia_associada")
    return red_flags


def detectar_inconsistencias_subjetivas(subj):
    inconsistencias = []
    if subj["continuo"] and subj["recorrente"]:
        inconsistencias.append("continuo_e_recorrente_ao_mesmo_tempo")
    if subj["gatilho_mudar_posicao"] and subj["gatilho_espontaneo"]:
        inconsistencias.append("gatilho_posicional_e_espontaneo_ao_mesmo_tempo")
    if subj["sensacao_rotatoria"] and subj["sensacao_pre_sincope"]:
        inconsistencias.append("vertigem_e_presincope_ao_mesmo_tempo")
    return inconsistencias


def priorizar_vertigem(subj):
    classificacao = classificar_titrate(subj)
    red_flags     = detectar_red_flags_subjetivas(subj)
    inconsistencias = detectar_inconsistencias_subjetivas(subj)

    if red_flags:
        prioridade = "alta"
        caminho    = "avaliar_causa_central_ou_grave"
    elif inconsistencias:
        prioridade = "media"
        caminho    = "reentrevistar_e_esclarecer_fenomenologia"
    else:
        prioridade = "baixa"
        caminho    = classificacao

    return {
        "classificacao":  classificacao,
        "red_flags":      red_flags,
        "inconsistencias": inconsistencias,
        "prioridade":     prioridade,
        "caminho":        caminho,
    }


# =============================================================================
# CONDUTAS DETALHADAS (listas de strings)
# =============================================================================

def _conduta_bppv_canal_posterior():
    return [
        'Confirmar com manobra de Dix-Hallpike: girar cabeça 45° para o lado suspeito, '
        'deitar rapidamente — nistagmo torsional geotrópico confirma canal posterior',
        'Manobra de Epley (canal posterior): 4 posicoes sequenciais, 30s cada — sucesso ~80% em 1 sessao',
        '  [1] Dix-Hallpike: deitado, cabeca 45° para o lado afetado',
        '  [2] Girar cabeca 90° para o lado oposto (mantendo deitado)',
        '  [3] Rolar o corpo inteiro 90° de lado (nariz aponta para baixo)',
        '  [4] Sentar lentamente',
        'Se Epley nao resolver em 2 tentativas: manobra de Semont (deitar lateralmente com velocidade)',
        'Betaistina 16 mg VO 8/8h por 2-4 semanas (facilita compensacao central)',
        'Exercicios de Brandt-Daroff domésticos: 3x/dia por 2 semanas (recidivas ou manobra incompleta)',
        'Nao restringir movimento de cabeca apos manobra — evidencia nao suporta repouso',
        'Retorno se recidiva em < 1 semana ou nistagmo atipico (down-beat ou multidirecional)',
    ]


def _conduta_bppv_canal_horizontal():
    return [
        'Padrao: nistagmo horizontal (nao torsional), piora nos dois lados ao Roll test',
        'Roll test (Pagnini-McClure): supino, virar cabeca 90° para cada lado — nistagmo horizontal',
        '  Geotrópico (bate para o lado afetado) = variante canalicular → BBQ Roll',
        '  Apogeotrópico (bate para o lado oposto) = variante cupuloliítica → Gufoni',
        'Manobra de BBQ Roll (Lempert): 4 rotacoes de 90° em supino, pausa de 30s em cada posicao',
        'Manobra de Gufoni: deitar rapidamente para o lado afetado + rotacao da cabeca 45° para baixo',
        'Manobra de Yacovino: alternativa para formas atipicas ou suspeita de canal anterior',
        'Betaistina 16 mg VO 8/8h por 2-4 semanas',
        'Retorno em 1-2 semanas para reavaliacao do nistagmo',
    ]


def _conduta_avs():
    return [
        '── RED FLAG PRIORITÁRIO — ATAXIA DE MARCHA SEVERA ──',
        '⚠️ Incapacidade de ficar de pé sem apoio = sinal isolado mais forte de AVC cerebelar.',
        '   Aciona PS imediato MESMO SE HINTS parecer ambíguo ou periférico no plantão.',
        '   Não liberar paciente que não consegue ficar de pé sem apoio.',
        '',
        '── HINTS (Head Impulse, Nystagmus, Test of Skew) ──',
        'Se treinado: HINTS completo S 100% / E 96% para AVC de fossa posterior',
        '  Central (preocupante): impulso normal + nistagmo multidirecional + skew',
        '  Periferico (tranquilizador): impulso anormal + nistagmo unidirecional + sem skew',
        'Sem treinamento em HINTS ou qualquer red flag → TC cranio urgente',
        '  Atencao: TC tem sensibilidade de apenas 16% para AVC de fossa posterior nas primeiras 24h',
        '  Preferir RNM DWI se disponivel — padrao ouro para AVC cerebelar/tronco',
        '── Neurite Vestibular (HINTS periferico, sem deficit focal, SEM ataxia severa) ──',
        'Metilprednisolona 100 mg/dia VO x 3 dias, reducao progressiva ate 22 dias (evidencia moderada)',
        'Betaistina 24 mg VO 12/12h apos refeicoes por 6-8 semanas',
        'Evitar sedativos vestibulares (dimenidrinato, prometazina) > 3 dias — prejudicam compensacao central',
        'Fisioterapia vestibular assim que tolerado (exercicios de Cawthorne-Cooksey)',
        '── Encaminhamento ──',
        'Neurologista urgente se HINTS sugestivo de central, ataxia severa OU qualquer deficit focal novo',
    ]


def _conduta_presincope():
    return [
        'Medir PA: deitado → apos 1 min sentado → apos 3 min em pe',
        'Hipotensao ortostatica: queda >= 20 mmHg sistolica OU >= 10 mmHg diastoica',
        'Revisar medicamentos: anti-hipertensivos, diureticos, alfa-bloqueadores, antidepressivos triciclicos',
        'Orientar: levantar lentamente, exercicios de bomba de panturrilha antes de se levantar, hidratacao',
        'Meias de compressao graduada 20-30 mmHg se hipotensao ortostatica confirmada',
        'Encaminhar cardiologia se sincope recorrente inexplicada ou suspeita de arritmia',
    ]


def _conduta_meniere():
    return [
        'Solicitar audiometria + imitanciometria (perda neurossensorial flutuante nas baixas frequencias)',
        'Dieta hipossodica < 2 g Na/dia — pilar do tratamento nao farmacologico',
        'Betaistina 24 mg VO 12/12h apos refeicoes (dose Meniere — pode usar por anos sem dependencia)',
        'Evitar cafeina, alcool e tabaco (precipitam crises)',
        'Crise aguda: dimenidrinato 50 mg VO ou ondansetrona 4-8 mg VO/SL para nauseas',
        '  Evitar uso cronico de antivertiginosos — prejudicam compensacao central',
        'Encaminhar otoneurologia: VEMP, considerar punção intratimpanica com glicocorticoide',
    ]


def _conduta_migranea_vestibular():
    return [
        'Criterios ICHD-III: >= 5 episodios de vertigem + historia de migranea + >= 50% episodios '
        'com cefaleia migranosa, foto/fonofobia ou aura visual',
        'Crise com cefaleia: sumatriptano 50-100 mg VO (uso particular) + AINE',
        'Crise sem cefaleia: metoclopramida 10 mg VO ou ondansetrona 4-8 mg se nauseas',
        'Profilaxia (>= 3 episodios/mes): propranolol 40-80 mg/dia, amitriptilina 10-25 mg a noite',
        'Controle de gatilhos: privacao de sono, estresse, alimentos (queijo curado, vinho tinto)',
        'Encaminhar neurologia se duvida diagnostica ou profilaxia necessaria',
    ]


def _conduta_central():
    return [
        'TC de cranio sem contraste urgente (excluir hemorragia — baixa sensibilidade para fossa posterior)',
        'Preferir RNM DWI urgente se disponivel — padrao ouro para AVC cerebelar/tronco encefálico',
        'Nao mobilizar paciente com suspeita de AVC ate avaliacao neurologica',
        'Encaminhar PS/emergencia ou chamar neurologista',
    ]


# =============================================================================
# FUNÇÕES DE AVALIAÇÃO
# =============================================================================

def avaliar_bppv(subj, obj=None):
    red_flags = detectar_red_flags_subjetivas(subj)
    if red_flags:
        return None

    if (
        subj["gatilho_mudar_posicao"]
        and subj["duracao_segundos_minutos"]
        and subj["recorrente"]
        and subj["sensacao_rotatoria"]
        and not subj["duracao_dias"]
        and not subj["sincope"]
    ):
        canal_hz = obj and (obj.get('roll_test_positivo') or obj.get('canal_horizontal'))
        return {
            'tipo':           'vertigem',
            'diagnostico':    'bppv_canal_horizontal' if canal_hz else 'bppv',
            'conduta':        _conduta_bppv_canal_horizontal() if canal_hz else _conduta_bppv_canal_posterior(),
            'necessita_exame': False,
        }
    return None


def avaliar_avs(subj):
    if subj["continuo"] and subj["duracao_dias"]:
        return {
            'tipo':           'vertigem',
            'diagnostico':    'sindrome_vestibular_aguda',
            'conduta':        _conduta_avs(),
            'necessita_exame': True,
        }
    return None


def avaliar_presincope(subj):
    if subj["sensacao_pre_sincope"]:
        return {
            'tipo':           'vertigem',
            'diagnostico':    'presincope',
            'conduta':        _conduta_presincope(),
            'necessita_exame': True,
        }
    return None


def avaliar_episodica_espontanea(subj):
    if classificar_titrate(subj) != "episodica_espontanea":
        return None

    if subj["perda_auditiva"] or subj["zumbido"] or subj["plenitude_auricular"]:
        return {
            'tipo':           'vertigem',
            'diagnostico':    'provavel_meniere',
            'conduta':        _conduta_meniere(),
            'necessita_exame': True,
        }

    if subj["cefaleia"]:
        return {
            'tipo':           'vertigem',
            'diagnostico':    'possivel_migranea_vestibular',
            'conduta':        _conduta_migranea_vestibular(),
            'necessita_exame': False,
        }

    return {
        'tipo':           'vertigem',
        'diagnostico':    'episodica_espontanea_indefinida',
        'conduta': [
            'Investigar: Meniere (audiometria), enxaqueca vestibular (historia migranosa) ou TIA (fatores cardiovasculares)',
            'Holter se suspeita cardiovascular',
            'Encaminhar otoneurologia ou neurologia conforme suspeita dominante',
        ],
        'necessita_exame': True,
    }


def decidir_conduta_vertigem(subj):
    prioridade = priorizar_vertigem(subj)

    if prioridade["prioridade"] == "alta":
        return {
            'tipo':           'vertigem',
            'diagnostico':    'possivel_central',
            'conduta':        _conduta_central(),
            'necessita_exame': True,
        }

    if prioridade["caminho"] == "episodica_desencadeada":
        return avaliar_bppv(subj)

    if prioridade["caminho"] == "aguda_continua":
        return avaliar_avs(subj)

    if prioridade["caminho"] == "presincope":
        return avaliar_presincope(subj)

    if prioridade["caminho"] == "episodica_espontanea":
        return avaliar_episodica_espontanea(subj)

    return {
        'tipo':           'vertigem',
        'diagnostico':    'indefinido',
        'conduta': [
            'Coletar anamnese mais detalhada — fenomenologia nao se encaixa em padrao TITRATE claro',
            'Considerar Holter, audiometria, avaliacao neurologica conforme contexto',
        ],
        'necessita_exame': True,
    }


# =============================================================================
# ENTRY POINT
# =============================================================================

def interpretar_vertigem(subj, obj):
    if obj["deficit_focal"] or obj["incapaz_de_andar"] or obj["hints_preocupante"]:
        return {
            'tipo':           'vertigem',
            'diagnostico':    'possivel_central',
            'conduta':        _conduta_central(),
            'necessita_exame': True,
        }

    if obj["ortostatismo_sugestivo"]:
        return {
            'tipo':           'vertigem',
            'diagnostico':    'presincope_ortostatica',
            'conduta':        _conduta_presincope(),
            'necessita_exame': True,
        }

    if obj["dix_hallpike_positivo"]:
        canal_hz = obj.get('roll_test_positivo') or obj.get('canal_horizontal')
        return {
            'tipo':           'vertigem',
            'diagnostico':    'bppv_canal_horizontal' if canal_hz else 'bppv',
            'conduta':        _conduta_bppv_canal_horizontal() if canal_hz else _conduta_bppv_canal_posterior(),
            'necessita_exame': False,
        }

    return decidir_conduta_vertigem(subj)


# =============================================================================
# STANDALONE
# =============================================================================

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    from modules.sintomas.vertigem.vertigem_subjetivo import coletar_subjetivo_vertigem
    from modules.sintomas.vertigem.vertigem_objetivo import coletar_objetivo_vertigem

    subj = coletar_subjetivo_vertigem()
    obj  = coletar_objetivo_vertigem()

    print("\n--- RESULTADO VERTIGEM ---\n")
    resultado = interpretar_vertigem(subj, obj)
    print(f"Diagnostico: {resultado['diagnostico']}")
    print("Conduta:")
    for linha in resultado['conduta']:
        print(f"  {linha}")
