# modules/raciocinio/cefaleia_dx.py
# Motor de raciocínio clínico — Cefaleia
# Arquitetura: legado — compatível com dispatcher.py
# Condutas: listas detalhadas com doses, triptanos e protocolo de cluster

# =============================================================================
# ESTRUTURA DE RETORNO
# =============================================================================

def montar_resultado_cefaleia(diagnostico, conduta, necessita_exame):
    return {
        "tipo":            "cefaleia",
        "diagnostico":     diagnostico,
        "conduta":         conduta,   # lista de strings
        "necessita_exame": necessita_exame,
    }


# =============================================================================
# RED FLAGS
# =============================================================================

def red_flag_subjetivo(d):
    return any([
        d.get("inicio_subito"),
        d.get("pior_da_vida"),
        d.get("inicio_esforco_sexo"),
        d.get("deficit_focal"),
        d.get("febre") and d.get("rigidez_nuca"),
        d.get("confusao"),
        d.get("cancer"),
        d.get("imunossupressao"),
        d.get("idade_maior_50_nova"),
        d.get("progressiva"),
        d.get("trauma"),
    ])


def red_flag_objetivo(obj):
    return any([
        obj.get("deficit_neuro"),
        obj.get("rigidez_nuca"),
        obj.get("papiledema"),
    ])


def red_flag(d, obj):
    return red_flag_subjetivo(d) or red_flag_objetivo(obj)


# =============================================================================
# PADRÕES PRIMÁRIOS
# =============================================================================

def enxaqueca(d):
    return (
        d.get("pulsatil")
        and d.get("localizacao_unilateral")
        and d.get("piora_atividade")
        and (d.get("nausea") or d.get("fotofobia") or d.get("fonofobia"))
    )


def tensional(d):
    return (
        d.get("pressao")
        and not d.get("piora_atividade")
        and not d.get("nausea")
        and not d.get("fotofobia")
    )


def cluster(d):
    return (
        d.get("localizacao_unilateral")
        and (d.get("lacrimejamento") or d.get("rinorreia"))
        and d.get("agitacao")
    )


def classificar_secundaria(d):
    if d.get("inicio_subito") and d.get("pior_da_vida"):
        return "vascular (ex: HSA)"
    if d.get("febre"):
        if d.get("rigidez_nuca") and d.get("confusao"):
            return "infecciosa (ex: meningite/encefalite)"
        if d.get("rigidez_nuca"):
            return "infecciosa (ex: meningite)"
        if d.get("confusao"):
            return "infecciosa (ex: encefalite/meningite)"
    if d.get("uso_analgesico_excessivo"):
        return "substâncias (ex: abuso de analgésicos)"
    if d.get("nova_medicacao"):
        return "substâncias/medicacao (ex: cefaleia induzida por droga)"
    return "indefinida"


# =============================================================================
# CONDUTAS DETALHADAS
# =============================================================================

def _conduta_secundaria_grave(d):
    base = [
        'TC de cranio sem contraste URGENTE (excluir HSA, hemorragia)',
        'Se TC negativa e suspeita de HSA mantida: puncao lombar (xantocromia detectavel em 12h)',
    ]
    if d.get("febre") and d.get("rigidez_nuca"):
        base += [
            'Febre + rigidez de nuca: internacao e antibioticoterapia empirica IMEDIATA',
            '  NAO retardar antibiotico por aguardar TC — risco de morte em meningite bacteriana',
            '  Ceftriaxona 2 g IV + dexametasona 0,15 mg/kg IV (iniciar 15 min antes do antibiotico)',
        ]
    base.append('Encaminhar PS/emergencia imediatamente')
    return base


def _conduta_cluster():
    return [
        '── CRISE — tratamento abortivo ──',
        'O2 100%: mascara facial nao-reinalacao (NRM), 12-15 L/min por 15-20 min',
        '  Eficaz em ~70% em 15 min — iniciar o mais rapido possivel ao inicio da crise',
        'Sumatriptano 6 mg SC (uso particular): efeito em 15 min — NNT 2.4 — padrao ouro para abortar',
        '  Maximo 2 injecoes SC em 24h com intervalo de 1h',
        'Lidocaina 4% intranasal: spray no lado da crise (alternativa se sem acesso a O2/triptano)',
        '── PROFILAXIA — iniciar junto com o tratamento abortivo ──',
        'Verapamil 80 mg 3x/dia → aumentar 80 mg/semana ate 240-480 mg/dia',
        '  Monitorar ECG antes de iniciar e com doses > 240 mg/dia (bloqueio AV)',
        'Prednisolona 60 mg/dia x 5 dias → reducao em 2-3 semanas (ponte rapida ate verapamil agir)',
        'Litio (carbonato): alternativa ao verapamil em cluster cronico',
        '── Orientacoes ──',
        'Evitar alcool durante o cluster period — gatilho potente de crise',
        'Encaminhar neurologia / ambulatorio de cefaleia para manejo do periodo em salvas',
    ]


def _conduta_enxaqueca():
    return [
        '── CRISE ──',
        'AINE: ibuprofeno 400-600 mg VO (1a linha — NNT 7.2 para alivio em 2h)',
        '  Naproxeno 500 mg VO: alternativa se duracao mais prolongada esperada',
        'Triptano (uso particular): sumatriptano 50-100 mg VO — iniciar nos 1os 15-30 min',
        '  Sumatriptano 6 mg SC se nausea intensa impossibilita VO (acao em 10-15 min)',
        'Antiemetico: metoclopramida 10 mg VO/IV ou ondansetrona 4-8 mg se vomitos',
        'Repouso em ambiente escuro e silencioso durante a crise',
        'Evitar opioides — aumentam cronificacao e risco de MOH',
        '── PROFILAXIA (>= 4 crises/mes ou crises incapacitantes) ──',
        'Propranolol 40 mg 2x/dia — 1a linha (evitar em asma, IC descompensada, bloqueio AV)',
        'Amitriptilina 10-25 mg a noite — alternativa (especialmente com insonia ou tensional associada)',
        'Topiramato 25-100 mg/dia — boa evidencia; TERATOGENICO — evitar sem contracepcao segura',
        'Valproato 500-1500 mg/dia — alternativa; TERATOGENICO — mesma restricao',
        '── ALERTAS ──',
        'MOH (cefaleia por uso excessivo de analgésico): AINE > 10 dias/mes ou triptano > 10 dias/mes',
        '  MOH agrava e cronifica a cefaleia — revisar frequencia de uso em cada consulta',
        'Diario de cefaleia: monitorar frequencia, duracao, gatilhos e resposta ao tratamento',
    ]


def _conduta_tensional():
    return [
        'Paracetamol 500-1000 mg VO 6/6h — 1a escolha (menor risco de MOH)',
        'AINE (ibuprofeno 400 mg VO) se paracetamol insuficiente',
        'Alerta MOH: uso de analgésico > 10-15 dias/mes → risco de cronificacao',
        '  Se MOH suspeito: retirada progressiva do analgésico + apoio clinico',
        'Tecnicas nao farmacologicas: relaxamento muscular progressivo, biofeedback, fisioterapia cervical',
        'Revisar gatilhos: postura, estresse, privacao de sono, cervicalgia',
        'Cefaleia tensional cronica (>= 15 dias/mes): amitriptilina 10-25 mg a noite como profilaxia',
    ]


# =============================================================================
# ENTRY POINT
# =============================================================================

def interpretar_cefaleia(d, obj):

    if red_flag(d, obj):
        categoria = classificar_secundaria(d)
        return montar_resultado_cefaleia(
            f"cefaleia secundaria grave – etiologia {categoria}",
            _conduta_secundaria_grave(d),
            True,
        )

    if cluster(d):
        return montar_resultado_cefaleia(
            "cefaleia em salvas",
            _conduta_cluster(),
            False,
        )

    if enxaqueca(d):
        return montar_resultado_cefaleia(
            "enxaqueca",
            _conduta_enxaqueca(),
            False,
        )

    if tensional(d):
        return montar_resultado_cefaleia(
            "cefaleia tensional",
            _conduta_tensional(),
            False,
        )

    return montar_resultado_cefaleia(
        "cefaleia sem padrao definido",
        [
            'Reavaliar historia completa e exame fisico',
            'Considerar diario de cefaleia por 4 semanas para caracterizacao',
            'Se cefaleia progressiva ou mudanca de padrao: neuroimagem eletiva',
        ],
        False,
    )
