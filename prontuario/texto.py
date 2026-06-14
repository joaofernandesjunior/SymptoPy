# ============================================================
# PADRÃO: cada sintoma tem duas funções:
#   gerar_subjetivo_<sintoma>(admissao) -> str
#   gerar_objetivo_<sintoma>(admissao)  -> str
#
# Para adicionar um sintoma novo, basta criar esse par de funções
# e registrá-lo em SINTOMAS_REGISTRADOS abaixo.
# gerar_texto_prontuario() nunca precisa ser editado.
# ============================================================

# ------------------------------------------------------------------
# UTILITÁRIO
# ------------------------------------------------------------------

def _partes_para_texto(partes, separador=", "):
    """Junta uma lista de partes numa string limpa. Retorna '' se vazia."""
    partes = [p for p in partes if p]
    if not partes:
        return ""
    return separador.join(partes) + "."


def _get_dados_modulo(admissao, modulo_nome, tipo='msk'):
    """Busca dados de um módulo pelo nome, suportando multi-queixa.

    Prioridade: dados_por_modulo (multi-queixa) → chaves legadas (single).
    """
    dados = admissao.get('dados_por_modulo', {}).get(modulo_nome)
    if dados:
        return dados
    if tipo == 'msk' and admissao.get('modulo_msk') == modulo_nome:
        return admissao.get('dados_msk')
    if tipo == 'organico' and admissao.get('modulo_organico') == modulo_nome:
        return admissao.get('dados_organico')
    return None


# ------------------------------------------------------------------
# DISPNEIA
# ------------------------------------------------------------------

def gerar_subjetivo_dispneia(admissao):
    # Web (módulo PA de triagem): dados_por_modulo tem o novo conjunto de campos
    disp_web = _get_dados_modulo(admissao, 'dispneia', 'organico')
    if disp_web:
        return _subjetivo_dispneia_pa(disp_web)

    disp = admissao.get("subjetivo_especifico", {}).get("dispneia")
    if not disp:
        return ""

    partes = []

    if disp.get("inicio_agudo"):
        partes.append("Relata início agudo")
    else:
        partes.append("Relata início não agudo")

    if disp.get("piora_progressiva"):
        partes.append("com piora progressiva")
    else:
        partes.append("sem piora progressiva")

    if disp.get("repouso"):
        partes.append("dispneia em repouso")
    else:
        partes.append("nega dispneia em repouso")

    _bool_fields = [
        ("febre",              "refere febre",               "nega febre"),
        ("tosse",              "refere tosse",               "nega tosse"),
        ("chiado",             "refere chiado",              "nega chiado"),
        ("dor_tx",             "refere dor torácica",        "nega dor torácica"),
        ("dor_pleura",         "refere dor pleurítica",      "nega dor pleurítica"),
        ("hemoptise",          "refere hemoptise",           "nega hemoptise"),
        ("sincope",            "refere síncope",             "nega síncope"),
        ("ortopneia",          "refere ortopneia",           "nega ortopneia"),
        ("dpn",                "refere DPN",                 "nega DPN"),
        ("tosse_noturna",      "refere tosse noturna",       "nega tosse noturna"),
        ("dispneia_esforcos",  "refere dispneia aos esforços", "nega dispneia aos esforços"),
    ]

    for chave, se_sim, se_nao in _bool_fields:
        partes.append(se_sim if disp.get(chave) else se_nao)

    return _partes_para_texto(partes, separador=". ")


def gerar_objetivo_dispneia(admissao):
    disp_obj = admissao.get("objetivo_especifico", {}).get("dispneia")
    if not disp_obj:
        return ""

    partes = []

    _bool_fields = [
        ("musculatura_acessoria",   "com uso de musculatura acessória",   "sem uso de musculatura acessória"),
        ("fala_entrecortada",       "fala entrecortada",                  "sem fala entrecortada"),
        ("jvd",                     "com turgência jugular",              "sem turgência jugular"),
        ("edema_bilateral_mmii",    "com edema bilateral de MMII",        "sem edema bilateral de MMII"),
        ("edema_unilateral_perna",  "com edema unilateral de perna",      "sem edema unilateral de perna"),
    ]

    for chave, se_sim, se_nao in _bool_fields:
        partes.append(se_sim if disp_obj.get(chave) else se_nao)

    return _partes_para_texto(partes, separador=". ")


# ------------------------------------------------------------------
# VERTIGEM
# ------------------------------------------------------------------

def _negativas_vertigem(vert: dict) -> str:
    """Red flags centrais que foram perguntados e respondidos como ausentes."""
    neg = []
    if vert.get('diplopia') is False:
        neg.append('diplopia')
    if vert.get('fraqueza') is False:
        neg.append('fraqueza focal')
    if vert.get('parestesias') is False:
        neg.append('parestesias')
    if vert.get('cefaleia') is False:
        neg.append('cefaleia associada')
    return _fmt_negativas(neg)


def gerar_subjetivo_vertigem(admissao):
    # Tenta formato web (dados_por_modulo) e fallback para formato CLI (subjetivo_especifico)
    vert = (_get_dados_modulo(admissao, 'vertigem', 'organico')
            or admissao.get("subjetivo_especifico", {}).get("vertigem"))
    if not vert:
        return ""

    partes = []

    # Só appenda se True (campos opcionais sem negativa explícita)
    _campos_positivos = [
        ("sensacao_rotatoria",         "refere sensação rotatória"),
        ("sensacao_pre_sincope",        "refere sensação de pré-síncope"),
        ("desequilibrio",              "refere desequilíbrio"),
        ("inicio_subito",              "início súbito"),
        ("duracao_segundos_minutos",   "episódios de curta duração (segundos a minutos)"),
        ("duracao_horas",              "episódios com duração de horas"),
        ("duracao_dias",               "sintomas contínuos por dias"),
        ("recorrente",                 "quadro recorrente"),
        ("continuo",                   "quadro contínuo"),
        ("gatilho_mudar_posicao",      "associado a mudança de posição da cabeça"),
        ("gatilho_levantar",           "associado a ortostatismo"),
        ("gatilho_espontaneo",         "sem gatilho claro"),
        ("nauseas_vomitos",            "com náuseas/vômitos"),
        ("cefaleia",                   "associado a cefaleia"),
        ("diplopia",                   "com diplopia"),
        ("fraqueza",                   "com fraqueza"),
        ("parestesias",                "com parestesias"),
        ("perda_auditiva",             "com perda auditiva"),
        ("zumbido",                    "com zumbido"),
    ]

    for chave, texto in _campos_positivos:
        if vert.get(chave):
            partes.append(texto)

    neg = _negativas_vertigem(vert)
    if neg:
        partes.append(neg)

    return _partes_para_texto(partes, separador=". ")


def gerar_objetivo_vertigem(admissao):
    vert_obj = admissao.get("objetivo_especifico", {}).get("vertigem")
    if not vert_obj:
        return ""

    partes = []

    if vert_obj.get("deficit_focal"):
        partes.append("com déficit neurológico focal")
    else:
        partes.append("sem déficit neurológico focal")

    if vert_obj.get("incapaz_de_andar"):
        partes.append("incapaz de deambular sem auxílio")

    if vert_obj.get("dix_hallpike_realizado"):
        if vert_obj.get("dix_hallpike_positivo"):
            partes.append("Dix-Hallpike positivo")
        else:
            partes.append("Dix-Hallpike negativo")

    if vert_obj.get("ortostatismo_sugestivo"):
        partes.append("ortostatismo presente")

    if vert_obj.get("hints_realizado"):
        if vert_obj.get("hints_preocupante"):
            partes.append("HINTS sugestivo de causa central")
        else:
            partes.append("HINTS não sugestivo de central")

    if vert_obj.get("perda_auditiva_nova_objetiva"):
        partes.append("perda auditiva ao exame")

    return _partes_para_texto(partes, separador=". ")


# ------------------------------------------------------------------
# HELPER — conduta como lista ou string
# ------------------------------------------------------------------

def _render_conduta_lista(conduta):
    """Aceita string (legacy) ou lista de strings. Retorna texto formatado."""
    if isinstance(conduta, list):
        linhas = "\n".join(f"  • {c}" for c in conduta if c)
        return f"Conduta sugerida:\n{linhas}"
    return f"Conduta sugerida: {conduta}."


# ------------------------------------------------------------------
# VERTIGEM — análise automática
# ------------------------------------------------------------------

_LABEL_VERTIGEM = {
    'bppv':                      'VPPB — Canal Posterior',
    'bppv_canal_horizontal':     'VPPB — Canal Horizontal',
    'sindrome_vestibular_aguda': 'Síndrome Vestibular Aguda (neurite / AVC a excluir)',
    'presincope':                'Pré-síncope',
    'presincope_ortostatica':    'Hipotensão Ortostática',
    'provavel_meniere':          'Doença de Ménière (provável)',
    'possivel_migranea_vestibular': 'Enxaqueca Vestibular (possível)',
    'episodica_espontanea_indefinida': 'Vertigem Episódica Espontânea — investigar',
    'possivel_central':          'Causa Central — URGENTE',
    'indefinido':                'Tontura sem padrão definido',
}

def _gerar_texto_vertigem_analise(resultado):
    """Gera texto de impressão automática para vertigem."""
    dx    = resultado.get('diagnostico', '')
    label = _LABEL_VERTIGEM.get(dx, dx.replace('_', ' ').upper())
    exame = 'sim' if resultado.get('necessita_exame') else 'não'
    return (
        f"Hipótese principal: {label}. "
        f"Necessita exame complementar: {exame}."
    )


# ------------------------------------------------------------------
# CEFALEIA
# ------------------------------------------------------------------

def _negativas_cefaleia(cef: dict) -> str:
    """Red flags meníngeos/hemorrágicos perguntados e respondidos como ausentes."""
    neg = []
    if cef.get('febre') is False:
        neg.append('febre')
    if cef.get('rigidez_nuca') is False:
        neg.append('rigidez de nuca')
    if cef.get('deficit_focal') is False:
        neg.append('déficit focal')
    if cef.get('pior_da_vida') is False:
        neg.append('pior cefaleia da vida')
    if cef.get('inicio_subito') is False:
        neg.append('início súbito')
    return _fmt_negativas(neg)


def gerar_subjetivo_cefaleia(admissao):
    # Web: dados_por_modulo; CLI: subjetivo_especifico
    cef = (_get_dados_modulo(admissao, 'cefaleia', 'organico')
           or admissao.get("subjetivo_especifico", {}).get("cefaleia"))
    if not cef:
        return ""

    partes = []

    # Único campo com negativa explícita — só quando foi perguntado
    if "nova" in cef:
        partes.append("cefaleia nova" if cef.get("nova") else "cefaleia não nova")
    else:
        partes.append("Cefaleia")

    _campos_positivos = [
        ("recorrente",           "com episódios semelhantes prévios"),
        ("inicio_subito",        "de início súbito"),
        ("pior_da_vida",         "referida como pior cefaleia da vida"),
        ("localizacao_unilateral", "unilateral"),
        ("pulsatil",             "de caráter pulsátil"),
        ("pressao",              "em pressão/aperto"),
        ("piora_atividade",      "com piora à atividade física"),
        ("nausea",               "associada a náusea"),
        ("fotofobia",            "com fotofobia"),
        ("fonofobia",            "com fonofobia"),
        ("aura",                 "precedida por aura"),
        ("febre",                "associada a febre"),
        ("rigidez_nuca",         "com rigidez de nuca"),
        ("deficit_focal",        "com déficit focal referido"),
    ]

    for chave, texto in _campos_positivos:
        if cef.get(chave):
            partes.append(texto)

    neg = _negativas_cefaleia(cef)
    if neg:
        partes.append(neg)

    return _partes_para_texto(partes, separador=", ")


def gerar_objetivo_cefaleia(admissao):
    """
    Cefaleia normalmente não tem campos de exame físico específico além
    do neurológico geral. Retorna '' por padrão — implemente conforme
    seu modelo de dados crescer.
    """
    return ""


# ------------------------------------------------------------------
# ANÁLISE AUTOMÁTICA (inclui lógica de diagnóstico de cefaleia)
# ------------------------------------------------------------------

def _gerar_texto_cefaleia_analise(subj, resultado):
    """Gera o texto de impressão automática para cefaleia."""
    partes = []
    dx = resultado["diagnostico"]

    _descritores = {
        "cefaleia secundaria grave": [
            ("inicio_subito",        "de início súbito"),
            ("pior_da_vida",         "descrita como pior cefaleia da vida"),
            ("inicio_esforco_sexo",  "com início durante esforço/atividade sexual"),
            ("febre",                "associada a febre"),
            ("deficit_focal",        "com déficit neurológico referido"),
        ],
        "enxaqueca": [
            ("localizacao_unilateral", "unilateral"),
            ("pulsatil",             "de caráter pulsátil"),
            ("piora_atividade",      "com piora à atividade física"),
            ("nausea",               "associada a náusea"),
            ("fotofobia",            "com fotofobia"),
            ("fonofobia",            "com fonofobia"),
            ("aura",                 "com aura"),
        ],
        "cefaleia tensional": [
            ("pressao",              "em pressão/aperto"),
        ],
        "cefaleia em salvas": [
            ("localizacao_unilateral", "unilateral"),
            ("lacrimejamento",       "com lacrimejamento"),
            ("rinorreia",            "com rinorreia"),
            ("agitacao",             "com agitação durante a crise"),
        ],
    }

    _rotulos = {
        "cefaleia secundaria grave": "Cefaleia com sinais de alarme",
        "enxaqueca":                 "Cefaleia com características de enxaqueca",
        "cefaleia tensional":        "Cefaleia com padrão sugestivo de cefaleia tensional",
        "cefaleia em salvas":        "Cefaleia com padrão sugestivo de cefaleia em salvas",
    }

    # matching por prefixo — dx secundário inclui etiologia no nome
    chave_rotulo = next((k for k in _rotulos if dx.startswith(k)), None)
    rotulo = _rotulos.get(chave_rotulo, "Cefaleia sem padrão clínico bem definido no momento")
    partes.append(rotulo)

    for chave, texto in _descritores.get(chave_rotulo, []):
        if subj.get(chave):
            partes.append(texto)

    texto_base = ", ".join(partes) + "."
    return (
        f"{texto_base} "
        f"Hipótese principal: {resultado['diagnostico']}. "
        f"Necessita exame complementar: {'sim' if resultado['necessita_exame'] else 'não'}."
    )


def _gerar_analise_single(resultado, admissao):
    """Roteia um único resultado para sua função de formatação."""
    if resultado.get("tipo") == "cefaleia":
        # Web: dados_por_modulo; CLI: subjetivo_especifico
        subj = (_get_dados_modulo(admissao, 'cefaleia', 'organico')
                or admissao.get("subjetivo_especifico", {}).get("cefaleia", {}))
        return _gerar_texto_cefaleia_analise(subj, resultado)

    if resultado.get("tipo") == "vertigem":
        return _gerar_texto_vertigem_analise(resultado)

    if resultado.get("tipo") == "urinario":
        return _gerar_texto_urinario_analise(resultado)

    if resultado.get("tipo") == "palpitacao":
        return _analise_palpitacao(resultado)

    if resultado.get("tipo") == "gota":
        return _analise_gota(resultado)
    if resultado.get("tipo") == "asma":
        return _analise_asma(resultado)
    if resultado.get("tipo") == "dpoc":
        return _analise_dpoc(resultado)
    if resultado.get("tipo") == "sincope":
        return _analise_sincope(resultado)
    if resultado.get("tipo") == "anorretal":
        return _analise_anorretal(resultado)
    if resultado.get("tipo") == "edema":
        return _analise_edema(resultado)
    if resultado.get("tipo") == "ictericia":
        return _analise_ictericia(resultado)

    categoria = resultado.get("categoria", "")

    if categoria in ("red_flag_emergencia", "padrao_inflamatorio", "avaliacao_completa"):
        dados = _get_dados_modulo(admissao, 'coluna', 'msk') or {}
        return _gerar_texto_coluna_analise(resultado, dados)

    if categoria in ("fibromialgia_confirmada", "criterios_insuficientes", "investigar_causa_secundaria"):
        dados = _get_dados_modulo(admissao, 'fibromialgia', 'msk') or {}
        return _gerar_texto_fibromialgia_analise(resultado, dados)

    if categoria in ("red_flag_quadril", "avaliacao_quadril"):
        dados = _get_dados_modulo(admissao, 'quadril', 'msk') or {}
        return _gerar_texto_quadril_analise(resultado, dados)

    if categoria in (
        "trauma_ottawa_positivo", "entorse_tornozelo",
        "fasciite_plantar", "tendinopatia_aquiles",
        "morton_neuroma", "avaliacao_tornozelo_pe",
        "red_flag_tornozelo_pe",
    ):
        dados = _get_dados_modulo(admissao, 'tornozelo_pe', 'msk') or {}
        return _gerar_texto_tornozelo_pe_analise(resultado, dados)

    if categoria in (
        "trauma_escafoide_suspeito", "tunel_do_carpo",
        "de_quervain", "dedo_em_gatilho",
        "rizartrose_thumb_cmc", "suspeita_artrite_reumatoide",
        "avaliacao_mao_punho", "red_flag_mao_punho",
    ):
        dados = _get_dados_modulo(admissao, 'mao_punho', 'msk') or {}
        return _gerar_texto_mao_punho_analise(resultado, dados)

    if categoria in (
        "tosse_pcp_suspeita", "tosse_aguda_viral", "tosse_aguda_bacteriana",
        "tosse_pertussis_suspeita", "tosse_subaguda_pos_infecciosa",
        "tosse_ieca", "tosse_uacs", "tosse_asma_variante", "tosse_drge_lpr",
        "tosse_tb_suspeita", "tosse_pneumonia_atipica", "tosse_neoplasia_suspeita",
        "investigar_tosse_cronica",
    ):
        dados = _get_dados_modulo(admissao, 'tosse', 'organico') or {}
        return _gerar_texto_tosse_analise(resultado, dados)

    if categoria in (
        "fadiga_red_flags", "fadiga_secundaria_laboratorial",
        "fadiga_secundaria_apneia", "fadiga_secundaria_psiquiatrica",
        "fadiga_me_sfc", "fadiga_idiopatica_subaguda",
    ):
        dados = _get_dados_modulo(admissao, 'fadiga', 'organico') or {}
        return _gerar_texto_fadiga_analise(resultado, dados)

    if categoria in (
        "diarreia_imunossuprimido", "diarreia_sepse",
        "diarreia_disenteria_bacilar", "diarreia_stec_suspeita",
        "diarreia_c_diff", "diarreia_viajante", "diarreia_toxinfeccao",
        "diarreia_aguda_watery", "diarreia_persistente",
        "diarreia_cronica_alarme_urgente", "diarreia_cronica_alarme_eletivo",
        "diarreia_dii_suspeita", "diarreia_sii_d",
    ):
        dados = _get_dados_modulo(admissao, 'diarreia', 'organico') or {}
        return _gerar_texto_diarreia_analise(resultado, dados)

    if categoria in (
        "arboviral_grupo_d", "arboviral_grupo_c", "arboviral_grupo_b",
        "arboviral_grupo_a", "chikungunya_suspeita", "zika_suspeita",
        "arboviral_indiferenciada",
    ):
        dados = _get_dados_modulo(admissao, 'arboviroses', 'organico') or {}
        return _gerar_texto_arboviroses_analise(resultado, dados)

    if categoria in (
        "ivas_emergencia", "ivas_mononucleose", "ivas_influenza",
        "ivas_gas", "ivas_rinossinusite", "ivas_laringite", "ivas_viral",
    ):
        dados = _get_dados_modulo(admissao, 'ivas', 'organico') or {}
        return _gerar_texto_ivas_analise(resultado, dados)

    # Formato compacto (diagnóstico único — módulos legados)
    partes = []
    if all(k in resultado for k in ("diagnostico", "conduta", "necessita_exame")):
        partes.append(f"Hipótese principal: {resultado['diagnostico']}.")
        partes.append(_render_conduta_lista(resultado['conduta']))
        partes.append(f"Necessita exame complementar: {'sim' if resultado['necessita_exame'] else 'não'}.")
        return "\n".join(partes)

    # Formato expandido (múltiplos diagnósticos / red flags)
    if resultado.get("red_flags"):
        partes.append("Alertas de gravidade: " + ", ".join(resultado["red_flags"]) + ".")
    if resultado.get("diagnosticos_provaveis"):
        nomes = [d["diagnostico"] for d in resultado["diagnosticos_provaveis"]]
        partes.append("Hipóteses prováveis: " + ", ".join(nomes) + ".")
    if resultado.get("diagnosticos_possiveis"):
        nomes = [d["diagnostico"] for d in resultado["diagnosticos_possiveis"]]
        partes.append("Hipóteses possíveis: " + ", ".join(nomes) + ".")
    if resultado.get("exames_iniciais"):
        partes.append("Exames iniciais sugeridos: " + ", ".join(resultado["exames_iniciais"]) + ".")
    if resultado.get("proximos_scores"):
        scores = [s["score"] for s in resultado["proximos_scores"]]
        partes.append("Próxima estratificação sugerida: " + ", ".join(scores) + ".")
    if resultado.get("diagnosticos_exclusao"):
        partes.append(
            "Se hipóteses principais não se confirmarem, considerar: "
            + ", ".join(resultado["diagnosticos_exclusao"]) + "."
        )
    return " ".join(partes)


def gerar_analise_automatica(admissao):
    """Gera impressão automática para todas as queixas da admissão."""
    analises = admissao.get('analises_automaticas', [])

    if analises:
        blocos = []
        for entrada in analises:
            queixa    = entrada.get('queixa', '')
            resultado = entrada['resultado']
            texto = _gerar_analise_single(resultado, admissao)
            if texto:
                prefixo = f"[{queixa.upper()}]\n" if len(analises) > 1 else ""
                blocos.append(f"{prefixo}{texto}")
        return '\n\n'.join(b for b in blocos if b)

    # Fallback: formato legado (single analise_automatica)
    resultado = admissao.get('analise_automatica')
    if not resultado:
        return ''
    return _gerar_analise_single(resultado, admissao)


# ------------------------------------------------------------------
# COMORBIDADES
# ------------------------------------------------------------------

def gerar_comorbidades_automaticas(admissao):
    resultados = admissao.get("comorbidades_automaticas", {})
    if not resultados:
        return ""

    complementares = admissao.get("comorbidades_complementares", {})
    drc_comp = complementares.get("drc")
    partes = []

    if "drc" in resultados:
        drc = resultados["drc"]
        partes.append("DRC — pontos de atenção:")

        for alerta in drc.get("alertas_fixos", []):
            partes.append(f"- {alerta}")

        if drc_comp:
            partes.append("Complemento DRC:")
            partes.append(f"- Creatinina basal/eGFR: {drc_comp.get('creatinina_basal') or 'não informado'}")
            partes.append(f"- Faz diálise: {'sim' if drc_comp.get('faz_dialise') else 'não'}")

            if drc_comp.get("faz_dialise"):
                partes.append(f"- Última diálise: {drc_comp.get('ultima_dialise') or 'não informado'}")
                partes.append(f"- Problema com acesso/cateter: {'sim' if drc_comp.get('problema_acesso') else 'não'}")

            partes.append(
                f"- Perdeu medicações / OTC / suplementos novos: "
                f"{drc_comp.get('perdeu_medicacoes_ou_otc') or 'não informado'}"
            )
        elif drc.get("perguntas_sugeridas"):
            partes.append("Perguntas úteis por DRC:")
            for pergunta in drc["perguntas_sugeridas"]:
                partes.append(f"- {pergunta}")

        for med in drc.get("medicacoes_em_atencao", []):
            partes.append(f"- {med}")

        if drc.get("red_flags"):
            partes.append("Red flags por DRC:")
            for rf in drc["red_flags"]:
                partes.append(f"- {rf}")

        if drc_comp or drc.get("red_flags"):
            for exame in drc.get("exames_sugeridos", []):
                partes.append(f"- {exame}")

    return "\n".join(partes)


# ------------------------------------------------------------------
# REGISTRO DE SINTOMAS
# Para adicionar um sintoma novo: crie o par de funções acima e
# adicione uma entrada aqui. Nada mais precisa mudar.
# ------------------------------------------------------------------


# ------------------------------------------------------------------
# MSK — JOELHO
# ------------------------------------------------------------------

def _negativas_joelho(dados: dict) -> str:
    neg = []
    if dados.get('red_flag_sistemica') is False:
        neg.append('red flag sistêmica')
    return _fmt_negativas(neg)


def gerar_subjetivo_joelho(admissao):
    dados = _get_dados_modulo(admissao, 'joelho', 'msk')
    if not dados:
        return ""
    partes = []
    idade = dados.get("idade", "?")
    dor   = "nova" if dados.get("dor_nova") else "crônica/recorrente"
    partes.append(f"Paciente de {idade} anos com dor {dor} no joelho")
    if dados.get("inicio_insidioso"):      partes.append("de início insidioso")
    if dados.get("dor_mecanica"):          partes.append("com piora à carga e atividade")
    if dados.get("melhora_com_repouso"):   partes.append("com melhora ao repouso")
    if dados.get("rigidez_matinal_menos_30min"): partes.append("com rigidez matinal curta (< 30min)")
    if dados.get("rigidez_matinal_acima_60min"):  partes.append("com rigidez matinal prolongada (> 60min)")
    if dados.get("dor_linha_articular"):   partes.append("com dor na linha articular")
    if dados.get("sinal_do_cinema"):       partes.append("com sinal do cinema positivo")
    if dados.get("dor_anterior_joelho"):   partes.append("com dor anterior ao joelho")
    if dados.get("piora_escadas_ou_agachamento"): partes.append("com piora em escadas")
    if dados.get("travamento_ou_estalido"): partes.append("com episódios de travamento/estalido")
    if dados.get("dor_medial_abaixo_linha_articular"): partes.append("com dor medial abaixo da linha articular")
    if dados.get("massa_fossa_poplitea"):  partes.append("com massa na fossa poplítea relatada")
    if dados.get("trauma_agudo"):          partes.append("com trauma agudo recente")
    if dados.get("red_flag_sistemica"):    partes.append("⚠️ RED FLAG sistêmica identificada")

    neg = _negativas_joelho(dados)
    if neg:
        partes.append(neg)

    return _partes_para_texto(partes, separador=". ")


def gerar_objetivo_joelho(admissao):
    dados = _get_dados_modulo(admissao, 'joelho', 'msk')
    if not dados:
        return ""
    partes = ["Exame físico do joelho"]
    insp = []
    if dados.get("derrame_articular"):         insp.append("derrame intra-articular")
    if dados.get("edema_prepatelar_visivel"):   insp.append("edema pré-patelar superficial")
    if dados.get("calor_intenso_local"):        insp.append("calor local")
    partes.append("Inspeção: " + (", ".join(insp) if insp else "sem alterações"))
    palp = []
    if dados.get("dor_linha_articular_palpacao"): palp.append("dor à palpação da linha articular")
    if dados.get("dor_palpacao_facetas_patelares"): palp.append("dor nas facetas patelares")
    if dados.get("dor_palpacao_anserina"):      palp.append("dor à palpação anserina")
    if dados.get("massa_poplitea_palpavel"):    palp.append("massa poplítea palpável")
    partes.append("Palpação: " + (", ".join(palp) if palp else "sem pontos dolorosos"))
    mov = []
    if dados.get("flexao_limitada"):   mov.append("flexão limitada")
    if dados.get("extensao_limitada"): mov.append("extensão limitada")
    if dados.get("crepitacao"):        mov.append("crepitação")
    partes.append("Movimento: " + (", ".join(mov) if mov else "arco preservado, sem crepitação"))
    testes = []
    if dados.get("mcmurray_positivo"):       testes.append("McMurray positivo")
    if dados.get("squat_unipodal_positivo"): testes.append("squat unipodal reproduz dor")
    if testes:
        partes.append("Testes: " + ", ".join(testes))
    return _partes_para_texto(partes, separador=". ")


# ------------------------------------------------------------------
# MSK — OMBRO
# ------------------------------------------------------------------

def _negativas_ombro(dados: dict) -> str:
    neg = []
    if dados.get('red_flag_sistemica') is False:
        neg.append('red flag sistêmica')
    if dados.get('red_flag_cardiovascular') is False:
        neg.append('red flag cardiovascular')
    return _fmt_negativas(neg)


def gerar_subjetivo_ombro(admissao):
    dados = _get_dados_modulo(admissao, 'ombro', 'msk')
    if not dados:
        return ""
    partes = []
    idade = dados.get("idade", "?")
    dor   = "nova" if dados.get("dor_nova") else "crônica/recorrente"
    lado  = "direito" if dados.get("lado_direito") else "esquerdo" if dados.get("lado_esquerdo") else "bilateral"
    partes.append(f"Paciente de {idade} anos com dor {dor} no ombro {lado}")
    if dados.get("dor_subacromia_lateral"):    partes.append("localizada na região subacromial/lateral")
    if dados.get("dor_anterior_bicipital"):    partes.append("com dor anterior no sulco bicipital")
    if dados.get("dor_superior_ac"):           partes.append("com dor na articulação AC")
    if dados.get("dor_difusa_ombro"):          partes.append("de distribuição difusa no ombro")
    if dados.get("piora_overhead"):            partes.append("com piora em movimentos acima da cabeça")
    if dados.get("dor_virou_rigidez"):         partes.append("com história de dor que evoluiu para rigidez progressiva")
    if dados.get("sensacao_dando_tranco"):     partes.append("com sensação de instabilidade/ombro cedendo")
    if dados.get("dor_noturna"):               partes.append("com dor noturna ao deitar sobre o ombro")
    if dados.get("diabetes"):                  partes.append("(diabético — fator de risco para capsulite)")
    if dados.get("duracao_acima_3_meses"):     partes.append("com duração superior a 3 meses")
    if dados.get("red_flag_sistemica"):        partes.append("⚠️ RED FLAG sistêmica identificada")
    if dados.get("red_flag_cardiovascular"):   partes.append("⚠️ Dor torácica associada — origem cardíaca avaliada")

    neg = _negativas_ombro(dados)
    if neg:
        partes.append(neg)

    return _partes_para_texto(partes, separador=". ")


def gerar_objetivo_ombro(admissao):
    dados = _get_dados_modulo(admissao, 'ombro', 'msk')
    if not dados:
        return ""
    partes = ["Exame físico do ombro"]
    insp = []
    if dados.get("atrofia_muscular"):  insp.append("atrofia muscular")
    if dados.get("deformidade_ac"):    insp.append("deformidade AC visível")
    if dados.get("calor_local"):       insp.append("calor local")
    partes.append("Inspeção: " + (", ".join(insp) if insp else "sem alterações"))
    palp = []
    if dados.get("dor_palpacao_subacromia"):      palp.append("dor subacromial")
    if dados.get("dor_palpacao_ac"):               palp.append("dor à palpação AC")
    if dados.get("dor_palpacao_sulco_bicipital"):  palp.append("dor no sulco bicipital")
    partes.append("Palpação: " + (", ".join(palp) if palp else "sem pontos dolorosos"))
    rom = []
    if dados.get("rom_ativo_limitado"):   rom.append("movimento ativo limitado")
    if dados.get("rom_passivo_limitado"): rom.append("movimento passivo também limitado")
    if dados.get("padrão_restricao_re_predomina"): rom.append("RE mais restrita — padrão capsular")
    partes.append("Movimento: " + (", ".join(rom) if rom else "arco de movimento preservado"))
    forca = []
    if dados.get("fraqueza_abducao"):          forca.append("fraqueza de abdução")
    if dados.get("fraqueza_rotacao_externa"):  forca.append("fraqueza de rotação externa")
    if forca:
        partes.append("Força: " + ", ".join(forca))
    testes = []
    if dados.get("arco_doloroso_positivo"):            testes.append("arco doloroso positivo")
    if dados.get("hawkins_kennedy_positivo"):           testes.append("Hawkins-Kennedy positivo")
    if dados.get("empty_can_positivo"):                testes.append("empty can positivo")
    if dados.get("drop_arm_positivo"):                 testes.append("drop arm positivo")
    if dados.get("external_rotation_lag_positivo"):    testes.append("lag de RE positivo")
    if dados.get("speed_positivo"):                    testes.append("Speed positivo")
    if dados.get("cross_arm_positivo"):                testes.append("cross-arm positivo")
    if dados.get("apprehension_positivo"):             testes.append("apprehension positivo")
    if testes:
        partes.append("Testes: " + ", ".join(testes))
    return _partes_para_texto(partes, separador=". ")

# ------------------------------------------------------------------
# MSK — COLUNA (LOMBALGIA)
# ------------------------------------------------------------------

_CAUDA_EQUINA_KEYS = [
    'anestesia_em_sela', 'retencao_urinaria', 'incontinencia_fecal', 'fraqueza_bilateral_mmii',
]


def _negativas_coluna(dados: dict) -> str:
    neg = []
    # Síndrome da cauda equina — collapse dos 4 marcadores
    # Só documenta ausência se TODOS os 4 campos foram explicitamente negados (is False)
    if all(dados.get(k) is False for k in _CAUDA_EQUINA_KEYS):
        neg.append('síndrome da cauda equina')
    # Red flags sistêmicas — documentar ausência individual
    if dados.get('febre') is False:
        neg.append('febre')
    if dados.get('perda_de_peso_inexplicada') is False:
        neg.append('perda de peso inexplicada')
    if dados.get('historico_cancer') is False:
        neg.append('histórico de câncer')
    if dados.get('imunossupressao') is False:
        neg.append('imunossupressão')
    return _fmt_negativas(neg)

def gerar_subjetivo_coluna(admissao):
    dados = _get_dados_modulo(admissao, 'coluna', 'msk')
    if not dados:
        return ""

    partes = []
    idade = dados.get("idade", "?")
    dor   = "nova" if dados.get("dor_nova") else "crônica/recorrente"
    eva   = dados.get("eva_dor", "?")
    partes.append(f"Paciente de {idade} anos com dor lombar {dor} (EVA {eva}/10)")

    if dados.get("inicio_insidioso"):           partes.append("de início insidioso")
    if dados.get("dor_mecanica"):               partes.append("com piora ao movimento e carga")
    if dados.get("melhora_com_repouso"):        partes.append("com melhora ao repouso")
    if dados.get("piora_com_repouso"):          partes.append("com piora ao permanecer parado")
    if dados.get("melhora_com_atividade_leve"): partes.append("com melhora à atividade leve")
    if dados.get("rigidez_matinal_menos_30min"):
        partes.append("com rigidez matinal de curta duração (< 30 min — padrão mecânico)")
    if dados.get("rigidez_matinal_acima_60min"):
        partes.append("com rigidez matinal prolongada (> 60 min — padrão inflamatório)")
    if dados.get("dor_localizada"):
        partes.append("dor localizada na região lombar, sem irradiação")

    # Irradiação radicular
    if dados.get("dor_irradiada_mmii"):
        rad = "com irradiação para membros inferiores"
        if dados.get("distribuicao_dermatomal"):    rad += " em distribuição dermatomal"
        if dados.get("queimacao_ou_choque_eletrico"): rad += " com qualidade em queimação/choque elétrico"
        partes.append(rad)
    else:
        partes.append("nega irradiação para membros inferiores")
    if dados.get("formigamento_ou_dormencia"):
        partes.append("refere formigamento ou dormência nas pernas")
    if dados.get("claudicacao_neurogenica"):
        partes.append(
            "claudicação neurogênica — dor e peso nas pernas ao caminhar "
            "com alívio ao sentar ou curvar o tronco para frente"
        )
    else:
        partes.append("nega claudicação neurogênica")

    # Preferência direcional
    if dados.get("preferencia_direcional_extensao"):
        partes.append("melhora com extensão lombar — padrão de centralização (McKenzie positivo)")
    if dados.get("preferencia_direcional_flexao"):
        partes.append("melhora com flexão do tronco — shopping cart sign")

    # Red flags subjetivos
    rf = []
    if dados.get("febre"):                      rf.append("febre")
    if dados.get("perda_de_peso_inexplicada"):   rf.append("perda de peso inexplicada")
    if dados.get("historico_cancer"):            rf.append("histórico de câncer")
    if dados.get("imunossupressao"):             rf.append("imunossupressão")
    if dados.get("dor_noturna_sem_alivio"):      rf.append("dor noturna sem alívio postural")
    if dados.get("trauma_significativo"):        rf.append("trauma significativo recente")
    if dados.get("anestesia_em_sela"):           rf.append("⚠️ ANESTESIA EM SELA")
    if dados.get("retencao_urinaria"):           rf.append("⚠️ RETENÇÃO URINÁRIA")
    if dados.get("incontinencia_fecal"):         rf.append("⚠️ INCONTINÊNCIA FECAL")
    if dados.get("fraqueza_bilateral_mmii"):     rf.append("⚠️ FRAQUEZA BILATERAL DE MMII")
    if rf:
        partes.append("Red flags presentes: " + ", ".join(rf))

    neg = _negativas_coluna(dados)
    if neg:
        partes.append(neg)

    return _partes_para_texto(partes, separador=". ")


def gerar_objetivo_coluna(admissao):
    dados = _get_dados_modulo(admissao, 'coluna', 'msk')
    if not dados:
        return ""

    partes = ["Exame físico dirigido para coluna lombar"]

    # Inspeção
    insp = []
    if dados.get("deformidade_coluna"):            insp.append("deformidade visível (escoliose/hipercifose)")
    if dados.get("espasmo_muscular_paravertebral"): insp.append("espasmo muscular paravertebral")
    partes.append("Inspeção: " + (", ".join(insp) if insp else "sem deformidades, postura preservada"))

    # Palpação
    palp = []
    if dados.get("dor_palpacao_processos_espinhosos"):
        palp.append("dor à palpação dos processos espinhosos (sinal de fratura/infecção)")
    if dados.get("dor_palpacao_paravertebral"):
        palp.append("dor à palpação da musculatura paravertebral")
    if dados.get("giordano_positivo"):
        palp.append("Giordano positivo — suspeita de pielonefrite")
    partes.append("Palpação: " + (", ".join(palp) if palp else "sem pontos dolorosos"))

    # ADM
    adm = []
    if dados.get("dor_movimento_flexao"):   adm.append("dor à flexão anterior do tronco")
    if dados.get("dor_movimento_extensao"): adm.append("dor à extensão do tronco")
    partes.append("ADM: " + (", ".join(adm) if adm else "amplitude preservada, sem dor aos movimentos"))

    # Neurológico
    neuro = []
    if dados.get("lasegue_positivo"):
        neuro.append("Lasègue positivo")
        if dados.get("lasegue_contralateral_positivo"):
            neuro.append("Lasègue contralateral positivo")
    else:
        neuro.append("Lasègue negativo bilateralmente")

    reflexos = []
    if dados.get("reflexo_patelar_diminuido"):  reflexos.append("patelar (L4) diminuído")
    if dados.get("reflexo_aquileu_diminuido"):   reflexos.append("aquileu (S1) diminuído")
    if reflexos:
        neuro.append("reflexo " + ", ".join(reflexos))
    else:
        neuro.append("reflexos patelares e aquileus presentes e simétricos")

    forca = []
    if dados.get("fraqueza_dorsiflexao_pe"):   forca.append("fraqueza de dorsiflexão do pé (L5)")
    if dados.get("fraqueza_plantiflexao_pe"):  forca.append("fraqueza de plantiflexão do pé (S1)")
    neuro.append(", ".join(forca) if forca else "força preservada em dorsiflexão e plantiflexão")

    if dados.get("deficit_sensibilidade_mmii"):
        neuro.append("déficit de sensibilidade dermatomal em MMII")
    else:
        neuro.append("sem déficit de sensibilidade")

    partes.append("Neurológico: " + "; ".join(neuro))

    return _partes_para_texto(partes, separador=". ")


def _gerar_texto_coluna_analise(resultado, dados):
    """Gera impressão automática em prosa clínica fluida para lombalgia."""
    categoria = resultado.get("categoria")
    linhas    = []

    # ── Emergência ──────────────────────────────────────────────────
    if categoria == "red_flag_emergencia":
        flags   = resultado["red_flags"]["flags"]
        achados = "; ".join(f["achado"] for f in flags)
        acao    = flags[0]["acao"] if flags else "Encaminhar PS/Neurocirurgia imediatamente."
        return (
            f"⚠️ EMERGÊNCIA — SÍNDROME DA CAUDA EQUINA identificada. "
            f"Sinais presentes: {achados}. {acao}"
        )

    # ── Red flags urgentes ───────────────────────────────────────────
    for f in resultado.get("red_flags", {}).get("flags", []):
        linhas.append(f"⚠️ Red flag [{f['urgencia'].upper()}] — {f['achado']}. Conduta: {f['acao']}")

    # ── Padrão inflamatório ──────────────────────────────────────────
    if categoria == "padrao_inflamatorio":
        p       = resultado.get("padrao", {})
        achados = ", ".join(p.get("achados_inflamatorios", []))
        exames  = "; ".join(p.get("exames_sugeridos", [])[:3])
        cond    = p.get("conduta_padrao", ["AINE regular; encaminhar reumatologia"])[0]
        linhas.append(
            f"Padrão inflamatório axial ({achados}), sugestivo de espondiloartropatia. "
            f"Solicitar: {exames}. Conduta inicial: {cond}."
        )
        return "\n".join(linhas)

    # ── Avaliação completa ───────────────────────────────────────────
    mecanismo   = resultado.get("mecanismo", {})
    padrao_nome = resultado.get("padrao", {}).get("padrao", "").replace("_", " ")
    hipos_prov  = resultado.get("hipoteses_provaveis", [])
    hipos_poss  = resultado.get("hipoteses_possiveis", [])
    excl        = resultado.get("hipoteses_exclusao", [])
    alertas     = resultado.get("alertas_farmacologicos")

    if not hipos_prov:
        linhas.append(
            "Quadro clínico com dados insuficientes para hipótese de força moderada ou alta. "
            "Reavaliar com exame físico complementar."
        )
        return "\n".join(linhas)

    h      = hipos_prov[0]
    nome_h = h["hipotese"].replace("_", " ").capitalize()
    pos_str = "; ".join(h.get("positivos", [])[:4])

    # Linha diagnóstica principal
    linha_dx = (
        f"Impressão clínica compatível com {nome_h} "
        f"(força {h['forca']}, score {h['score']} pontos), "
        f"padrão {padrao_nome}, mecanismo {mecanismo.get('mecanismo_dominante', '')}. "
        f"Achados positivos principais: {pos_str}."
    )
    if len(hipos_prov) > 1:
        h2 = hipos_prov[1]
        linha_dx += (
            f" Hipótese secundária a considerar: "
            f"{h2['hipotese'].replace('_', ' ')} (score {h2['score']}, força {h2['forca']})."
        )
    if hipos_poss:
        nomes_pos = ", ".join(hp["hipotese"].replace("_", " ") for hp in hipos_poss)
        linha_dx += f" Também considerar: {nomes_pos}."
    if excl:
        excl_str = ", ".join(e.replace("_", " ") for e in excl)
        linha_dx += f" Excluir ativamente: {excl_str}."
    linhas.append(linha_dx)

    if mecanismo.get("alerta_nociplastico"):
        linhas.append(
            "Alerta nociplástico: AINE e infiltrações têm eficácia muito limitada — "
            "priorizar abordagem multimodal (exercício aeróbico, psicologia, neuromoduladores)."
        )

    return "\n\n".join(linhas)


# ------------------------------------------------------------------
# MSK — FIBROMIALGIA
# ------------------------------------------------------------------

_REGIOES_FM = [
    ('MSE', 'Membros superiores esquerdos',
     ['ombro_esquerdo', 'braco_esquerdo_sup', 'braco_esquerdo_inf', 'mao_punho_esquerdo']),
    ('MSD', 'Membros superiores direitos',
     ['ombro_direito', 'braco_direito_sup', 'braco_direito_inf', 'mao_punho_direito']),
    ('MIE', 'Membros inferiores esquerdos',
     ['quadril_nadega_esquerdo', 'coxa_esquerda', 'perna_esquerda', 'tornozelo_pe_esquerdo']),
    ('MID', 'Membros inferiores direitos',
     ['quadril_nadega_direito', 'coxa_direita', 'perna_direita', 'tornozelo_pe_direito']),
    ('Axial', 'Região axial',
     ['pescoco', 'dorso_superior', 'lombar', 'torax', 'abdome']),
]
_LABEL_FM = {
    'ombro_esquerdo': 'ombro esq.', 'braco_esquerdo_sup': 'braço esq. sup.',
    'braco_esquerdo_inf': 'braço esq. inf.', 'mao_punho_esquerdo': 'mão/punho esq.',
    'ombro_direito': 'ombro dir.', 'braco_direito_sup': 'braço dir. sup.',
    'braco_direito_inf': 'braço dir. inf.', 'mao_punho_direito': 'mão/punho dir.',
    'quadril_nadega_esquerdo': 'quadril/nádega esq.', 'coxa_esquerda': 'coxa esq.',
    'perna_esquerda': 'perna esq.', 'tornozelo_pe_esquerdo': 'tornozelo/pé esq.',
    'quadril_nadega_direito': 'quadril/nádega dir.', 'coxa_direita': 'coxa dir.',
    'perna_direita': 'perna dir.', 'tornozelo_pe_direito': 'tornozelo/pé dir.',
    'pescoco': 'pescoço', 'dorso_superior': 'dorso superior', 'lombar': 'lombar',
    'torax': 'tórax', 'abdome': 'abdome',
    'mandibula_esquerda': 'mandíbula esq.', 'mandibula_direita': 'mandíbula dir.',
}
_SSS_LABEL = {0: 'ausente', 1: 'leve', 2: 'moderado', 3: 'grave'}
_SINTOMA_PT = {'dor': 'DOR', 'fadiga': 'FADIGA', 'sono': 'SONO NÃO-REPARADOR', 'humor': 'HUMOR/DEPRESSÃO'}


def _negativas_fibromialgia(dados: dict) -> str:
    neg = []
    # Bandeiras de exclusão (febre, perda de peso, sinovite) — se ausentes, reforça diagnóstico de FM
    if dados.get('flags_inflamatorios_exclusao') is False:
        neg.append('sinais inflamatórios/sistêmicos de exclusão')
    return _fmt_negativas(neg)


def gerar_subjetivo_fibromialgia(admissao):
    dados = _get_dados_modulo(admissao, 'fibromialgia', 'msk')
    if not dados:
        return ""

    partes = []
    idade  = dados.get("idade", "?")
    eva    = dados.get("eva_dor", "?")
    partes.append(
        f"Paciente de {idade} anos com queixa de dor crônica difusa (EVA {eva}/10), "
        f"presente há {'pelo menos 3 meses' if dados.get('duracao_sintomas_3_meses') else 'duração não confirmada de 3 meses'}"
    )

    # WPI — áreas positivas agrupadas por região
    regioes_afetadas = []
    total_wpi = 0
    for _, rotulo, areas in _REGIOES_FM:
        positivos = [_LABEL_FM[a] for a in areas if dados.get(a)]
        if positivos:
            regioes_afetadas.append(f"{rotulo} ({', '.join(positivos)})")
            total_wpi += len(positivos)
    extra = [_LABEL_FM[a] for a in ['mandibula_esquerda', 'mandibula_direita'] if dados.get(a)]
    if extra:
        total_wpi += len(extra)
        regioes_afetadas.append(f"mandíbulas ({', '.join(extra)})")

    n_regioes = sum(
        1 for _, _, areas in _REGIOES_FM
        if any(dados.get(a) for a in areas)
    )
    if regioes_afetadas:
        partes.append(
            f"Distribuição da dor em {n_regioes}/5 regiões corporais: "
            + "; ".join(regioes_afetadas)
            + f" — WPI = {total_wpi}/21"
        )
    else:
        partes.append("Sem áreas dolorosas mapeadas no WPI")

    # SSS
    f_score = dados.get('sss_fadiga', 0)
    s_score = dados.get('sss_sono', 0)
    c_score = dados.get('sss_cognitivo', 0)
    sss_p1  = f_score + s_score + c_score
    sss_p2_itens = []
    if dados.get('sss_cefaleia'):      sss_p2_itens.append("cefaleia frequente")
    if dados.get('sss_dor_abdominal'): sss_p2_itens.append("dor abdominal/cólica")
    if dados.get('sss_depressao'):     sss_p2_itens.append("humor deprimido")
    sss_p2 = len(sss_p2_itens)
    sss    = sss_p1 + sss_p2

    sss_desc = (
        f"fadiga {_SSS_LABEL[f_score]}, "
        f"sono {_SSS_LABEL[s_score]}, "
        f"cognição {_SSS_LABEL[c_score]}"
    )
    partes.append(f"Gravidade dos sintomas (SSS P1): {sss_desc}")
    if sss_p2_itens:
        partes.append(f"Sintomas somáticos adicionais (SSS P2): {', '.join(sss_p2_itens)}")
    partes.append(f"SSS total = {sss}/12")

    sintoma = _SINTOMA_PT.get(dados.get('sintoma_predominante', 'dor'), 'DOR')
    partes.append(f"Sintoma que mais impacta a qualidade de vida: {sintoma}")

    if dados.get('flags_inflamatorios_exclusao'):
        partes.append(
            "Sinais sugestivos de causa secundária relatados (febre, perda de peso ou sinovite) "
            "— investigação de doença inflamatória/sistêmica indicada antes de confirmar FM"
        )

    neg = _negativas_fibromialgia(dados)
    if neg:
        partes.append(neg)

    return _partes_para_texto(partes, separador=". ")


def gerar_objetivo_fibromialgia(admissao):
    dados = _get_dados_modulo(admissao, 'fibromialgia', 'msk')
    if not dados:
        return ""
    return ""


def _gerar_texto_fibromialgia_analise(resultado, dados):
    """Impressão automática em prosa clínica para fibromialgia."""
    categoria = resultado.get("categoria")
    scores    = resultado.get("scores", {})
    criterios = resultado.get("criterios", {})
    conduta   = resultado.get("conduta", {})
    sintoma   = _SINTOMA_PT.get(resultado.get("sintoma_predominante", "dor"), "DOR")
    linhas    = []

    wpi       = scores.get("wpi", "?")
    sss       = scores.get("sss", "?")
    n_reg     = scores.get("n_regioes", "?")
    score_str = f"WPI = {wpi}/21 | SSS = {sss}/12 | Regiões = {n_reg}/5"

    # ── Causa secundária ────────────────────────────────────────────
    if categoria == "investigar_causa_secundaria":
        linhas.append(
            f"Flags inflamatórios presentes — investigar causa secundária antes de confirmar FM. "
            f"Scores obtidos: {score_str}."
        )
        return "\n".join(linhas)

    # ── Scores + status diagnóstico ─────────────────────────────────
    if categoria == "fibromialgia_confirmada":
        cond = criterios.get("condicao_usada", "?")
        linhas.append(
            f"FIBROMIALGIA CONFIRMADA pelos critérios ACR 2016 (Condição {cond}). "
            f"{score_str}. Sintoma predominante relatado: {sintoma}."
        )
    else:
        linhas.append(
            f"Critérios ACR 2016 não completamente preenchidos no momento. {score_str}."
        )
        faltando = resultado.get("criterios_faltando", [])
        if faltando:
            linhas.append("Critérios faltando: " + "; ".join(faltando) + ".")

    # ── Alerta AINE/opioide (implicação diagnóstica) ─────────────────
    if conduta.get("alerta"):
        linhas.append(conduta["alerta"])

    return "\n\n".join(linhas)


# ------------------------------------------------------------------
# MSK — QUADRIL
# ------------------------------------------------------------------

_LOC_PT_QUADRIL = {
    'anterior': 'anterior / virilha (groin)',
    'lateral':  'lateral / grande trocânter',
    'posterior': 'posterior / nádega',
}


def _negativas_quadril(dados: dict) -> str:
    neg = []
    if dados.get('historico_cancer') is False:
        neg.append('histórico de câncer')
    if dados.get('febre_sistemica') is False:
        neg.append('febre sistêmica')
    if dados.get('nao_suporta_peso') is False:
        neg.append('incapacidade de apoio do membro')
    if dados.get('uso_corticoide_cronico') is False:
        neg.append('corticosteroide crônico')
    return _fmt_negativas(neg)


def gerar_subjetivo_quadril(admissao):
    dados = _get_dados_modulo(admissao, 'quadril', 'msk')
    if not dados:
        return ''

    partes = []
    idade = dados.get('idade', '?')
    eva   = dados.get('eva_dor', '?')
    dor   = 'nova' if dados.get('dor_nova') else 'crônica/recorrente'
    loc   = _LOC_PT_QUADRIL.get(dados.get('localizacao_dor', ''), dados.get('localizacao_dor', '?'))

    partes.append(
        f"Paciente de {idade} anos com dor {dor} no quadril {loc} (EVA {eva}/10)"
    )

    if dados.get('inicio_gradual'):     partes.append('de início gradual')
    if dados.get('piora_caminhar_escadas'): partes.append('com piora ao caminhar e subir escadas')
    if dados.get('dor_sentado_prolongado'): partes.append('com dor ao sentar prolongado')
    if dados.get('dor_decubito_lateral'):   partes.append('com piora ao deitar sobre o quadril afetado')
    if dados.get('dor_flexao_quadril'):     partes.append('com dor ao fletir o quadril')
    if dados.get('atleta_jovem_ativo'):     partes.append('em atleta / praticante de atividade intensa')
    if dados.get('sintomas_lombares_assoc'): partes.append('com sintomas lombares associados')

    rf = []
    if dados.get('uso_corticoide_cronico'): rf.append('uso crônico de corticoide (risco de AVN)')
    if dados.get('uso_alcool_cronico'):     rf.append('uso crônico de álcool (risco de AVN)')
    if dados.get('osteoporose'):            rf.append('osteoporose')
    if dados.get('historico_cancer'):       rf.append('histórico de câncer')
    if dados.get('nao_suporta_peso'):       rf.append('incapacidade de apoio do membro')
    if dados.get('encurtamento_rotacao_externa'): rf.append('ENCURTAMENTO + ROTACAO EXTERNA')
    if dados.get('febre_sistemica'):        rf.append('febre sistêmica')
    if dados.get('dor_noturna_intensa'):    rf.append('dor noturna intensa em repouso')
    if rf:
        partes.append('Red flags / fatores de risco: ' + ', '.join(rf))

    neg = _negativas_quadril(dados)
    if neg:
        partes.append(neg)

    return _partes_para_texto(partes, separador='. ')


def gerar_objetivo_quadril(admissao):
    dados = _get_dados_modulo(admissao, 'quadril', 'msk')
    if not dados:
        return ''

    partes = ['Exame físico do quadril']

    # Marcha
    marcha = []
    if dados.get('marcha_antalgica'):    marcha.append('marcha antálgica')
    if dados.get('marcha_trendelenburg'): marcha.append('marcha de Trendelenburg')
    partes.append('Marcha: ' + (', '.join(marcha) if marcha else 'sem alterações'))

    # Palpação
    palp = []
    if dados.get('dor_palpacao_grande_trocanter'): palp.append('dor à palpação do grande trocânter')
    if dados.get('dor_palpacao_anterior_groin'):   palp.append('dor na região anterior / virilha')
    partes.append('Palpação: ' + (', '.join(palp) if palp else 'sem pontos dolorosos'))

    # ADM
    adm = []
    if dados.get('limitacao_rotacao_interna'): adm.append('limitação de rotação interna')
    if dados.get('limitacao_rotacao_externa'): adm.append('limitação de rotação externa')
    if dados.get('limitacao_abducao_adicao'):  adm.append('limitação de abdução/adução')
    if dados.get('crepitacao_movimento'):      adm.append('crepitação ao movimento')
    partes.append('ADM: ' + (', '.join(adm) if adm else 'amplitude preservada'))

    # Testes
    testes = []
    if dados.get('faber_positivo'):      testes.append('FABER positivo')
    if dados.get('fadir_positivo'):      testes.append('FADIR positivo')
    if dados.get('sinal_trendelenburg'): testes.append('Trendelenburg positivo')
    if not dados.get('faber_positivo') and not dados.get('fadir_positivo'):
        testes.append('FABER e FADIR negativos (exclui FAI/labro com S 97%)')
    partes.append('Testes: ' + ', '.join(testes))

    return _partes_para_texto(partes, separador='. ')


def _gerar_texto_quadril_analise(resultado, dados):
    """Impressão automática em prosa clínica para dor no quadril."""
    categoria  = resultado.get('categoria')
    flags      = resultado.get('red_flags', {}).get('flags', [])
    avn        = resultado.get('alerta_avn', {})
    provaveis  = resultado.get('hipoteses_provaveis', [])
    possiveis  = resultado.get('hipoteses_possiveis', [])
    exclusao   = resultado.get('hipoteses_exclusao', [])
    loc        = _LOC_PT_QUADRIL.get(resultado.get('localizacao', ''), '')
    linhas     = []

    # ── Red flags ───────────────────────────────────────────────────
    for f in flags:
        linhas.append(f"[{f['urgencia'].upper()}] {f['achado']}. Conduta: {f['acao']}")

    if categoria == 'red_flag_quadril':
        return '\n'.join(linhas)

    # ── Alerta AVN ──────────────────────────────────────────────────
    if avn.get('alerta'):
        linhas.append(f"ALERTA AVN (score {avn['score']}): {avn['acao']}")

    # ── Hipótese principal ──────────────────────────────────────────
    if not provaveis:
        linhas.append(
            'Dados clínicos insuficientes para hipótese de força moderada ou alta. '
            'Reavaliar com exame físico complementar ou imagem.'
        )
        return '\n'.join(linhas)

    h      = provaveis[0]
    pos_str = '; '.join(h.get('positivos', [])[:4])
    linha_dx = (
        f"Quadro clínico compatível com {h['hipotese']} "
        f"(força {h['forca']}, score {h['score']}) — localização {loc}. "
        f"Achados positivos: {pos_str}."
    )
    if len(provaveis) > 1:
        h2 = provaveis[1]
        linha_dx += f" Considerar também: {h2['hipotese']} (score {h2['score']})."
    if possiveis:
        linha_dx += ' Possível: ' + ', '.join(p['hipotese'] for p in possiveis) + '.'
    if exclusao:
        linha_dx += ' Excluídos: ' + '; '.join(exclusao) + '.'
    linhas.append(linha_dx)

    return '\n\n'.join(linhas)


_LOC_PT_TORNOZELO = {
    'calcanhar_plantar':  'plantar (calcanhar)',
    'posterior_aquiles':  'posterior (Aquiles)',
    'antepé_morton':      'antepé (3-4o dedos)',
    'tornozelo_articular': 'articular (tornozelo)',
}


def _negativas_tornozelo_pe(dados: dict) -> str:
    neg = []
    if dados.get('uso_quinolona') is False:
        neg.append('uso de fluoroquinolona')
    if dados.get('corticosteroide_previo') is False:
        neg.append('infiltração prévia de corticoide no tendão')
    return _fmt_negativas(neg)


def gerar_subjetivo_tornozelo_pe(admissao):
    dados = _get_dados_modulo(admissao, 'tornozelo_pe', 'msk')
    if not dados:
        return ''

    partes = []
    idade = dados.get('idade', '?')
    eva   = dados.get('eva_dor', '?')
    dor   = 'nova' if dados.get('dor_nova') else 'crônica/recorrente'

    if dados.get('trauma_recente'):
        partes.append(
            f"Paciente de {idade} anos com queixa de dor no tornozelo/pé após trauma (EVA {eva}/10)"
        )
        if dados.get('mecanismo_inversao'):
            partes.append('mecanismo de inversão')
        if dados.get('incapaz_apoio_4_passos'):
            partes.append('incapaz de apoiar o membro')
        if dados.get('ja_entorces_previos'):
            partes.append('episódios prévios de entorse no mesmo tornozelo')
    else:
        loc = _LOC_PT_TORNOZELO.get(dados.get('localizacao_dor', ''), dados.get('localizacao_dor', '?'))
        partes.append(
            f"Paciente de {idade} anos com dor {dor} no tornozelo/pé — região {loc} (EVA {eva}/10)"
        )
        if dados.get('dor_primeiro_passo_manha'):
            partes.append('dor nos primeiros passos pela manhã')
        if dados.get('dor_melhora_caminhar'):
            partes.append('com melhora após aquecimento')
        if dados.get('dor_piora_fim_dia'):
            partes.append('e piora ao fim do dia')
        if dados.get('rigidez_manha_aquiles'):
            partes.append('rigidez matinal no Aquiles')
        if dados.get('queimacao_entre_dedos'):
            partes.append('queimação/formigamento entre 3-4o dedos')
        if dados.get('piora_calcado_estreito'):
            partes.append('piora com calçado estreito')

    rf = []
    if dados.get('uso_quinolona'):        rf.append('uso de fluoroquinolona')
    if dados.get('corticosteroide_previo'): rf.append('infiltração prévia de corticoide no tendão')
    if dados.get('sobrepeso_obesidade'):  rf.append('sobrepeso/obesidade')
    if rf:
        partes.append('Fatores de risco: ' + ', '.join(rf))

    neg = _negativas_tornozelo_pe(dados)
    if neg:
        partes.append(neg)

    return _partes_para_texto(partes, separador='. ')


def gerar_objetivo_tornozelo_pe(admissao):
    dados = _get_dados_modulo(admissao, 'tornozelo_pe', 'msk')
    if not dados:
        return ''

    partes = ['Exame físico do tornozelo/pé']

    # Inspeção
    insp = []
    if dados.get('edema_tornozelo'):    insp.append('edema peri-maleolar')
    if dados.get('equimose_visivel'):   insp.append('equimose presente')
    if dados.get('deformidade_visivel'): insp.append('deformidade óssea')
    if dados.get('pe_plano_valgismo'):  insp.append('pé plano / valgismo')
    partes.append('Inspeção: ' + (', '.join(insp) if insp else 'sem alterações visíveis'))

    # Ottawa / trauma
    if dados.get('trauma_recente'):
        ottawa_pos = any([
            dados.get('palpacao_maleolo_lateral_positiva'),
            dados.get('palpacao_maleolo_medial_positiva'),
            dados.get('palpacao_base_5o_meta_positiva'),
            dados.get('palpacao_navicular_positiva'),
            dados.get('incapaz_apoio_exame'),
        ])
        partes.append(
            'Ottawa (trauma): ' + ('POSITIVO — RX indicado' if ottawa_pos else 'negativo — fratura improvável')
        )
        if dados.get('dor_ligamentos_laterais'):
            partes.append('dor ligamentos laterais (ATFL/CFL)')

    # Fasciite
    if dados.get('dor_tuberosidade_medial_calc'):
        partes.append('dor à palpação da tuberosidade medial do calcâneo (fasciite plantar)')
    if dados.get('dor_dorsiflexao_passiva'):
        partes.append('windlass test positivo')

    # Aquiles
    aquiles = []
    if dados.get('dor_zona_critica_aquiles'):    aquiles.append('dor na zona crítica 2-6 cm')
    if dados.get('espessamento_nodulo_aquiles'):  aquiles.append('espessamento focal')
    if dados.get('thompson_positivo'):            aquiles.append('Thompson POSITIVO — suspeita de ruptura!')
    if aquiles:
        partes.append('Aquiles: ' + ', '.join(aquiles))

    # Morton
    if dados.get('mulder_positivo'):
        partes.append('Mulder positivo (neuroma de Morton)')

    return _partes_para_texto(partes, separador='. ')


def _gerar_texto_tornozelo_pe_analise(resultado, dados):
    """Impressão em prosa clínica para dor no tornozelo/pé."""
    categoria = resultado.get('categoria')
    flags     = resultado.get('red_flags', {}).get('flags', [])
    alerta_aq = resultado.get('alerta_aquiles', {})
    provaveis = resultado.get('hipoteses_provaveis', [])
    possiveis  = resultado.get('hipoteses_possiveis', [])
    linhas    = []

    for f in flags:
        linhas.append(f"[{f['urgencia'].upper()}] {f['achado']}. Conduta: {f['acao']}")

    if alerta_aq.get('alerta'):
        linhas.append(f"ALERTA: {alerta_aq['mensagem']}")

    if categoria == 'red_flag_tornozelo_pe':
        return '\n'.join(linhas)

    if categoria == 'trauma_ottawa_positivo':
        achados = resultado.get('achados_positivos', [])
        linha = 'Ottawa positivo — RX indicado. Achados: ' + '; '.join(achados[:3]) + '.'
        linhas.append(linha)
        return '\n\n'.join(linhas)

    if categoria == 'entorse_tornozelo':
        achados = resultado.get('achados_positivos', [])
        linhas.append('Ottawa negativo — fratura improvável. ' + '; '.join(achados[:3]) + '.')
        alerta_inst = resultado.get('alerta_instabilidade', '')
        if alerta_inst:
            linhas.append(f"Alerta: {alerta_inst}")
        return '\n\n'.join(linhas)

    if not provaveis and not possiveis:
        msg = resultado.get('mensagem', 'Dados insuficientes — reavaliar com exame complementar.')
        linhas.append(msg)
        return '\n'.join(linhas)

    h = provaveis[0] if provaveis else possiveis[0]
    pos_str = '; '.join(h.get('positivos', [])[:4])
    linha_dx = (
        f"Quadro compatível com {h['hipotese']} "
        f"(força {h['forca']}, score {h['score']}). "
        f"Achados: {pos_str}."
    )
    if len(provaveis) > 1:
        linha_dx += f" Considerar também: {provaveis[1]['hipotese']}."
    if possiveis:
        linha_dx += ' Possível: ' + ', '.join(p['hipotese'] for p in possiveis) + '.'
    linhas.append(linha_dx)

    alerta_csi = h.get('alerta_csi', '')
    if alerta_csi:
        linhas.append(f"ALERTA: {alerta_csi}")

    return '\n\n'.join(linhas)


_CATEGORIA_MAO_LABEL = {
    'trauma_escafoide_suspeito':    'Fratura do Escafoide (suspeita)',
    'tunel_do_carpo':               'Síndrome do Túnel do Carpo',
    'de_quervain':                  'Tenossinovite de De Quervain',
    'dedo_em_gatilho':              'Dedo em Gatilho',
    'rizartrose_thumb_cmc':         'Rizartrose do Polegar (CMC)',
    'suspeita_artrite_reumatoide':  'Suspeita de Artrite Reumatoide',
    'avaliacao_mao_punho':          'Avaliação Mão/Punho',
}


def _negativas_mao_punho(dados: dict) -> str:
    neg = []
    if dados.get('atrofia_tenar_percebida') is False:
        neg.append('atrofia tenar')
    return _fmt_negativas(neg)


def gerar_subjetivo_mao_punho(admissao):
    dados = _get_dados_modulo(admissao, 'mao_punho', 'msk')
    if not dados:
        return ''

    partes = []
    idade  = dados.get('idade', '?')
    eva    = dados.get('eva_dor', '?')
    dor    = 'nova' if dados.get('dor_nova') else 'crônica/recorrente'
    padrao = {
        'trauma':        'traumático',
        'neurologico':   'neurológico (parestesia)',
        'mecanico':      'mecânico/tendíneo',
        'reumatologico': 'reumatológico (articular)',
    }.get(dados.get('padrao_clinico', ''), dados.get('padrao_clinico', '?'))

    partes.append(
        f"Paciente de {idade} anos com dor {dor} na mão/punho, padrão {padrao} (EVA {eva}/10)"
    )

    # Trauma
    if dados.get('mecanismo_queda_mao_espalmada'):
        partes.append('queda com apoio em mão espalmada (FOOSH)')
    if dados.get('dor_tabaqueira_anatomica') or dados.get('tabaqueira_positiva'):
        partes.append('dor na tabaqueira anatômica')

    # Neurológico
    if dados.get('parestesia_noturna'):
        partes.append('parestesia noturna que acorda o paciente')
    if dados.get('alivio_sacudir_mao'):
        partes.append('alívio ao sacudir a mão (flick sign)')
    if dados.get('parestesia_territorio_mediano'):
        partes.append('em território mediano (polegar/indicador/médio)')
    if dados.get('parestesia_territorio_ulnar'):
        partes.append('em território ulnar (4o e 5o dedos)')
    if dados.get('atrofia_tenar_percebida'):
        partes.append('ATROFIA TENAR referida pelo paciente — grave')

    # Mecânico
    if dados.get('finkelstein_positivo') or (dados.get('dor_radial_punho') and dados.get('piora_movimento_polegar')):
        partes.append('dor dorsorradial ao mover o polegar (De Quervain)')
    if dados.get('estalido_bloqueio_dedo') or dados.get('gatilho_bloqueio_ativo'):
        partes.append('estalido/travamento de dedo (gatilho)')
    if dados.get('piora_pincar_girar') or dados.get('dor_base_polegar_cmC'):
        partes.append('dor na base do polegar ao pinçar/girar (rizartrose CMC)')

    # Reumatológico
    if dados.get('rigidez_matinal_prolongada'):
        partes.append('rigidez matinal > 30 minutos')
    if dados.get('acometimento_simetrico'):
        partes.append('acometimento simétrico bilateral')

    rf = []
    if dados.get('diabetes_mellitus'): rf.append('diabetes mellitus')
    if dados.get('obesidade'):         rf.append('obesidade')
    if dados.get('gestante_ou_puerpera'): rf.append('gestante/puérpera')
    if rf:
        partes.append('Fatores de risco: ' + ', '.join(rf))

    neg = _negativas_mao_punho(dados)
    if neg:
        partes.append(neg)

    return _partes_para_texto(partes, separador='. ')


def gerar_objetivo_mao_punho(admissao):
    dados = _get_dados_modulo(admissao, 'mao_punho', 'msk')
    if not dados:
        return ''

    partes = ['Exame físico mão/punho']

    # Inspeção
    insp = []
    if dados.get('edema_maos'):
        insp.append('edema' + (' simétrico' if dados.get('edema_simetrico') else ' assimétrico'))
    if dados.get('deformidade_visivel'): insp.append('deformidade articular')
    if dados.get('atrofia_tenar'):       insp.append('ATROFIA TENAR')
    if dados.get('atrofia_hipotenar'):   insp.append('atrofia hipotenar')
    if dados.get('nodulos_heberden_exame'): insp.append('nódulos de Heberden (IFD)')
    if dados.get('nodulos_bouchard_exame'): insp.append('nódulos de Bouchard (IFP)')
    partes.append('Inspeção: ' + (', '.join(insp) if insp else 'sem alterações'))

    # Trauma
    if dados.get('tabaqueira_positiva'):
        partes.append('tabaqueira anatômica POSITIVA (suspeita de fratura do escafoide)')
    if dados.get('compressao_axial_polegar_positiva'):
        partes.append('compressão axial do polegar positiva')

    # STC
    tests_stc = []
    if dados.get('durkan_positivo'):  tests_stc.append('Durkan+')
    if dados.get('phalen_positivo'):  tests_stc.append('Phalen+')
    if dados.get('tinel_positivo'):   tests_stc.append('Tinel+')
    if tests_stc:
        partes.append('Testes STC: ' + ', '.join(tests_stc))
    if dados.get('froment_positivo'):
        partes.append('Froment positivo — suspeita de neuropatia ulnar')

    # Mecânico
    if dados.get('finkelstein_positivo'):
        partes.append('Finkelstein positivo (E 100% para De Quervain)')
    if dados.get('polia_a1_dor_nodulo') or dados.get('gatilho_bloqueio_ativo'):
        partes.append('polia A1 positiva / bloqueio de dedo ao exame (gatilho)')
    if dados.get('grind_test_positivo'):
        partes.append('axial grind test positivo (E 97% para rizartrose CMC)')
    if dados.get('traction_shift_positivo'):
        partes.append('traction shift test positivo (E 100%)')

    # Reumatológico
    if dados.get('squeeze_mcf_positivo'): partes.append('squeeze MCF positivo (sinovite)')
    if dados.get('sinovite_mcf_punho'):   partes.append('sinovite de MCF/punho ao exame')
    if dados.get('press_test_positivo'):  partes.append('press test positivo (TFCC)')

    return _partes_para_texto(partes, separador='. ')


def _gerar_texto_mao_punho_analise(resultado, dados):
    """Impressão em prosa clínica para mão/punho."""
    categoria = resultado.get('categoria')
    flags     = resultado.get('red_flags', {}).get('flags', [])
    provaveis = resultado.get('hipoteses_provaveis', [])
    possiveis  = resultado.get('hipoteses_possiveis', [])
    linhas    = []

    for f in flags:
        linhas.append(f"[{f['urgencia'].upper()}] {f['achado']}. Conduta: {f['acao']}")

    if categoria == 'red_flag_mao_punho':
        return '\n'.join(linhas)

    # Trauma escafoide (resultado direto)
    if categoria == 'trauma_escafoide_suspeito':
        pos_str = '; '.join(resultado.get('positivos', [])[:3])
        linhas.append(
            f"Suspeita de fratura do escafoide "
            f"(força {resultado.get('forca')}, score {resultado.get('score')}). "
            f"Achados: {pos_str}."
        )
        return '\n\n'.join(linhas)

    if not provaveis and not possiveis:
        msg = resultado.get('mensagem', 'Dados insuficientes — reavaliar.')
        linhas.append(msg)
        return '\n'.join(linhas)

    h = provaveis[0] if provaveis else possiveis[0]
    pos_str = '; '.join(h.get('positivos', [])[:4])
    label   = _CATEGORIA_MAO_LABEL.get(categoria, categoria)
    linha_dx = (
        f"Quadro compatível com {label} "
        f"(força {h['forca']}, score {h['score']}). "
        f"Achados: {pos_str}."
    )
    if len(provaveis) > 1:
        linha_dx += f" Considerar também: {provaveis[1]['hipotese']}."
    if possiveis:
        linha_dx += ' Possível: ' + ', '.join(p['hipotese'] for p in possiveis) + '.'
    linhas.append(linha_dx)

    if h.get('alerta_grave'):
        linhas.append('ALERTA: Atrofia tenar — encaminhamento URGENTE para cirurgia de mão.')
    if h.get('alerta_diabetes'):
        linhas.append('ALERTA DM: menor eficácia de infiltração — monitorar glicemia.')

    alerta_ulnar = resultado.get('alerta_ulnar', '')
    if alerta_ulnar:
        linhas.append(f"Alerta: {alerta_ulnar}")

    return '\n\n'.join(linhas)


# ------------------------------------------------------------------
# NEGATIVAS — helper compartilhado
# ------------------------------------------------------------------

def _fmt_negativas(itens: list) -> str:
    """Formata lista de negativas explícitas como 'Nega: X, Y, Z' (sem ponto final)."""
    return ('Nega: ' + ', '.join(itens)) if itens else ''


# ------------------------------------------------------------------
# ORGÂNICO — TOSSE
# ------------------------------------------------------------------

def _negativas_tosse(dados: dict) -> str:
    """Pertinentes negativas documentadas no #Subjetivo — Tosse."""
    neg = []
    # Imunossupressão (sempre perguntado)
    if dados.get('hiv_diagnosticado') is False:
        neg.append('HIV')
    if dados.get('corticoide_cronico') is False:
        neg.append('corticosteroide crônico')
    if dados.get('contato_tb') is False:
        neg.append('contato com TB')
    # Campos pedidos apenas na tosse aguda
    if 'hemoptise' in dados and dados.get('hemoptise') is False:
        neg.append('hemoptise')
    # Campos pedidos apenas na tosse crônica
    if 'uso_ieca' in dados and dados.get('uso_ieca') is False:
        neg.append('uso de IECA')
    if 'perda_peso_involuntaria' in dados and dados.get('perda_peso_involuntaria') is False:
        neg.append('perda de peso involuntária')
    if 'tabagismo_ativo' in dados and dados.get('tabagismo_ativo') is False:
        neg.append('tabagismo ativo')
    return _fmt_negativas(neg)


def gerar_subjetivo_tosse(admissao):
    dados = _get_dados_modulo(admissao, 'tosse', 'organico')
    if not dados:
        return ''

    partes = []
    semanas = dados.get('duracao_semanas', 0)

    if semanas < 3:
        duracao = f'aguda ({semanas} semana{"s" if semanas != 1 else ""})'
    elif semanas < 8:
        duracao = f'subaguda ({semanas} semanas)'
    else:
        duracao = f'crônica ({semanas} semanas)'

    carater = 'produtiva' if dados.get('tosse_produtiva') else 'seca'
    partes.append(f'Tosse {carater} de duração {duracao}')

    if dados.get('hemoptise'):
        partes.append('com hemoptise')
    if dados.get('dispneia_assoc'):
        partes.append('dispneia progressiva' if dados.get('dispneia_progressiva') else 'dispneia associada')
    if dados.get('febre'):
        partes.append('febre alta' if dados.get('febre_alta') else 'febre')

    # Imunossupressão
    if dados.get('imunossuprimido'):
        isup = []
        if dados.get('hiv_diagnosticado'):
            s = 'HIV+'
            if dados.get('hiv_em_tarv') is False:
                s += ' sem TARV'
            if dados.get('cd4_valor'):
                s += f" CD4={dados['cd4_valor']}"
            isup.append(s)
        if dados.get('corticoide_cronico'):
            isup.append('corticoide crônico')
        if dados.get('imunossupressao_outro'):
            isup.append('outra imunossupressão')
        partes.append('Imunossupressão: ' + ', '.join(isup))

    if dados.get('contato_tb'):
        partes.append('contato com TB')

    # Sinais agudos
    sinais_agudos = []
    if dados.get('coriza_espirros'):       sinais_agudos.append('coriza/espirros')
    if dados.get('odinofagia'):            sinais_agudos.append('odinofagia')
    if dados.get('tosse_paroxistica'):     sinais_agudos.append('acessos paroxísticos')
    if dados.get('guincho_inspiratorio'):  sinais_agudos.append('guincho inspiratório')
    if sinais_agudos:
        partes.append(', '.join(sinais_agudos))

    # Gatilhos crônicos
    if dados.get('uso_ieca'):
        partes.append(f"uso de IECA ({dados.get('ieca_qual') or 'não especificado'})")
    if dados.get('sensacao_gotejamento'):
        partes.append('sensação de gotejamento pós-nasal')
    if dados.get('piora_noturna_madrugada') or dados.get('piora_exercicio'):
        partes.append('piora noturna/ao exercício')
    if dados.get('chiado_episodico'):
        partes.append('chiado episódico')
    if dados.get('pirose_regurgitacao'):
        partes.append('pirose/regurgitação')

    # Alertas
    rf = []
    if dados.get('perda_peso_involuntaria'):
        rf.append(f"perda de peso ({dados.get('perda_peso_kg', '?')} kg)")
    if dados.get('sudorese_noturna'):
        rf.append('sudorese noturna')
    if dados.get('tabagismo_ativo'):
        rf.append(f"tabagismo {dados.get('tabagismo_maco_ano', '?')} maços-ano")
    if dados.get('mudanca_padrao_tosse'):
        rf.append('mudança do padrão da tosse')
    if dados.get('dor_toracica_persistente'):
        rf.append('dor torácica persistente')
    if dados.get('rouquidao_persistente'):
        rf.append('rouquidão persistente')
    if rf:
        partes.append('Alertas: ' + ', '.join(rf))

    neg = _negativas_tosse(dados)
    if neg:
        partes.append(neg)

    return _partes_para_texto(partes, separador='. ')


_LABEL_TOSSE = {
    'tosse_ieca':               'Tosse por IECA',
    'tosse_uacs':               'UACS — gotejamento pós-nasal',
    'tosse_asma_variante':      'Asma / tosse variante de asma',
    'tosse_drge_lpr':           'DRGE / LPR',
    'tosse_tb_suspeita':        'Tuberculose — suspeita',
    'tosse_pneumonia_atipica':  'Pneumonia atípica',
    'tosse_neoplasia_suspeita': 'Suspeita de neoplasia pulmonar',
    'investigar_tosse_cronica': 'Tosse crônica — investigar',
}


def _gerar_texto_tosse_analise(resultado, dados):
    """Impressão em prosa clínica para tosse."""
    categoria = resultado.get('categoria', '')
    linhas    = []

    flags = resultado.get('red_flags', {}).get('flags', [])
    for f in flags:
        linhas.append(f"[{f['urgencia'].upper()}] {f['achado']}. Ação: {f['acao']}")

    if categoria == 'tosse_pcp_suspeita':
        pos_str = '; '.join(resultado.get('positivos', [])[:3])
        linhas.append(f"[URGENTE] {resultado.get('hipotese', 'PCP suspeita')}. Achados: {pos_str}.")
        return '\n\n'.join(linhas)

    if categoria in ('tosse_aguda_viral', 'tosse_aguda_bacteriana', 'tosse_pertussis_suspeita'):
        pos_str = '; '.join(resultado.get('positivos', [])[:3])
        linhas.append(f"{resultado.get('hipotese', '')}. Achados: {pos_str}.")
        if resultado.get('alerta_influenza'):
            linhas.append('ALERTA: síndrome gripal — cobertura viral a considerar (≤48h de sintomas).')
        return '\n\n'.join(linhas)

    if categoria == 'tosse_subaguda_pos_infecciosa':
        linhas.append(f"{resultado.get('hipotese', 'Tosse subaguda pós-infecciosa')}.")
        if resultado.get('alerta_pertussis'):
            linhas.append('ALERTA: pertussis a excluir — PCR nasofaringe indicado.')
        return '\n\n'.join(linhas)

    # Crônica
    label     = _LABEL_TOSSE.get(categoria, categoria)
    provaveis = resultado.get('hipoteses_provaveis', [])
    possiveis  = resultado.get('hipoteses_possiveis', [])

    if not provaveis and not possiveis:
        msg = resultado.get('mensagem', 'Dados insuficientes.')
        linhas.append(f"Tosse crônica — {label}. {msg}")
        return '\n'.join(linhas)

    linhas.append(f"Tosse crônica — {label}.")

    if provaveis:
        h       = provaveis[0]
        pos_str = '; '.join(h.get('positivos', [])[:4])
        linhas.append(
            f"Hipótese principal: {h['hipotese']} (força {h['forca']}, score {h['score']}). "
            f"Achados: {pos_str}."
        )
        if len(provaveis) > 1:
            h2 = provaveis[1]
            linhas.append(f"Hipótese secundária: {h2['hipotese']} (score {h2['score']}).")

    if possiveis:
        linhas.append('Possíveis (baixa força): ' + ', '.join(h['hipotese'] for h in possiveis) + '.')

    return '\n\n'.join(linhas)


# ------------------------------------------------------------------
# ORGÂNICO — FADIGA CRÔNICA
# ------------------------------------------------------------------

def _negativas_fadiga(dados: dict) -> str:
    """Red flags de urgência/malignidade perguntados e respondidos como ausentes."""
    neg = []
    if dados.get('febre_persistente') is False:
        neg.append('febre persistente')
    if dados.get('linfadenopatia_fixa') is False:
        neg.append('linfadenopatia fixa')
    if dados.get('deficit_neurologico_focal') is False:
        neg.append('déficit neurológico focal')
    if dados.get('dor_toracica_esforco') is False:
        neg.append('dor torácica ao esforço')
    if dados.get('ideacao_suicida_ativa') is False:
        neg.append('ideação suicida ativa')
    return _fmt_negativas(neg)


def gerar_subjetivo_fadiga(admissao):
    dados = _get_dados_modulo(admissao, 'fadiga', 'organico')
    if not dados:
        return ''

    partes = []

    dur = dados.get('duracao_meses', 0)
    if dur:
        partes.append(f'Fadiga crônica há {dur} meses')
    else:
        partes.append('Fadiga crônica (duração não especificada)')

    if dados.get('fadiga_nova_onset'):
        partes.append('início definido')
    if dados.get('inicio_pos_infeccao'):
        partes.append('início pós-infeccioso')
    if dados.get('reducao_atividade_substancial'):
        partes.append('redução substancial de atividade')

    # PEM
    if dados.get('pem_presente'):
        pem_str = 'PEM presente'
        if dados.get('pem_delay_horas'):
            pem_str += ' (crash retardado)'
        dias = dados.get('pem_dias_recuperacao', 0)
        if dias:
            pem_str += f', recuperação {dias}d'
        partes.append(pem_str)

    # Sono
    if dados.get('sono_nao_reparador'):
        partes.append('sono não-reparador')
    if dados.get('insonia'):
        partes.append('insônia')

    # Cognitivo / ortostase
    if dados.get('brain_fog'):
        partes.append('brain fog')
    if dados.get('intolerancia_ortostatica'):
        partes.append('intolerância ortostática')

    # STOP-BANG
    sb = dados.get('stopbang_total', 0)
    if sb >= 3:
        risco = 'alto' if sb >= 5 else 'intermediário'
        partes.append(f'STOP-BANG {sb}/8 (risco {risco})')

    # PHQ-2 / GAD-2
    phq2 = dados.get('phq2_total', 0)
    gad2 = dados.get('gad2_total', 0)
    humores = []
    if phq2 >= 3:
        humores.append(f'PHQ-2 {phq2} — depressão')
    if gad2 >= 3:
        humores.append(f'GAD-2 {gad2} — ansiedade')
    if humores:
        partes.append('Triagem: ' + ', '.join(humores))

    # Perda de peso
    if dados.get('perda_peso_involuntaria'):
        pct = dados.get('perda_peso_pct', 0)
        partes.append(f'perda de peso involuntária {pct:.1f}%')

    neg = _negativas_fadiga(dados)
    if neg:
        partes.append(neg)

    return _partes_para_texto(partes, separador='. ')


def _gerar_texto_fadiga_analise(resultado, dados):
    """Impressão em prosa clínica para o SOAP — fadiga crônica."""
    categoria = resultado.get('categoria', '')
    linhas    = []

    if categoria == 'fadiga_red_flags':
        flags = resultado.get('red_flags', {}).get('flags', [])
        for f in flags:
            linhas.append(f"[{f['urgencia'].upper()}] {f['achado']}. Ação: {f['acao']}.")
        return '\n\n'.join(linhas)

    if categoria == 'fadiga_secundaria_laboratorial':
        lab     = resultado.get('lab', {})
        achados = lab.get('achados', [])
        descrs  = [f"{a['lab']}: {a['achado']}" for a in achados[:3]]
        linhas.append('Causa secundária identificada — ' + '; '.join(descrs) + '.')
        return '\n\n'.join(linhas)

    if categoria == 'fadiga_secundaria_apneia':
        sb = resultado.get('stopbang', 0)
        linhas.append(f'STOP-BANG = {sb}/8 — alto risco para apneia obstrutiva do sono.')
        return '\n\n'.join(linhas)

    if categoria == 'fadiga_secundaria_psiquiatrica':
        phq2 = resultado.get('phq2', 0)
        gad2 = resultado.get('gad2', 0)
        itens = []
        if phq2 >= 3:
            itens.append(f'PHQ-2 = {phq2} → depressão')
        if gad2 >= 3:
            itens.append(f'GAD-2 = {gad2} → ansiedade')
        linhas.append('Triagem positiva: ' + '; '.join(itens) + '. PEM ausente.')
        return '\n\n'.join(linhas)

    if categoria == 'fadiga_me_sfc':
        criterios = resultado.get('criterios', {})
        dur       = criterios.get('duracao', 0)
        adicionais = []
        if criterios.get('brain_fog'):
            adicionais.append('brain fog')
        if criterios.get('ortostase'):
            adicionais.append('intolerância ortostática')
        adicionais_str = ', '.join(adicionais) if adicionais else 'nenhum adicional'
        linhas.append(
            f'EM/SFC — critérios IOM 2015 completos. Duração: {dur} meses. '
            f'Tríade: redução de atividade + PEM + sono não-reparador. '
            f'Critério adicional: {adicionais_str}.'
        )
        linhas.append(
            'GET (Graded Exercise Therapy) CONTRAINDICADO — NICE 2021 (recomendação forte contra).'
        )
        return '\n\n'.join(linhas)

    if categoria == 'fadiga_idiopatica_subaguda':
        criterios = resultado.get('criterios', {})
        faltando  = criterios.get('faltando', [])
        dur       = criterios.get('duracao', 0)
        nice_poss = criterios.get('nice_possivel', False)

        base = f'Fadiga há {dur} meses — critérios IOM 2015 incompletos.'
        if nice_poss:
            base += ' NICE 2021 possível (≥4 meses).'
        linhas.append(base)

        if faltando:
            linhas.append('Critérios faltando: ' + '; '.join(faltando[:3]) + '.')

        return '\n\n'.join(linhas)

    return f'Fadiga — {categoria}.'


# ------------------------------------------------------------------
# ORGÂNICO — DIARREIA NO ADULTO
# ------------------------------------------------------------------

_LABEL_DIARREIA = {
    'diarreia_imunossuprimido':        'Imunossuprimido — workup amplo',
    'diarreia_sepse':                  'Sepse — internação imediata',
    'diarreia_disenteria_bacilar':     'Disenteria bacilar',
    'diarreia_stec_suspeita':          'STEC suspeita — NÃO ATB, NÃO loperamida',
    'diarreia_c_diff':                 'C. difficile — suspeita',
    'diarreia_viajante':               'Diarreia do viajante',
    'diarreia_toxinfeccao':            'Toxinfecção alimentar',
    'diarreia_aguda_watery':           'Gastroenterite aguda viral',
    'diarreia_persistente':            'Diarreia persistente — investigar parasitas',
    'diarreia_cronica_alarme_urgente': 'Diarreia crônica — alarme urgente',
    'diarreia_cronica_alarme_eletivo': 'Diarreia crônica — investigação eletiva',
    'diarreia_dii_suspeita':           'DII suspeita (Crohn/RCU)',
    'diarreia_sii_d':                  'SII-D (funcional)',
}


def _negativas_diarreia(dados: dict) -> str:
    """Pertinentes negativas documentadas no #Subjetivo — Diarreia."""
    neg = []
    if dados.get('fezes_sanguinolentas') is False:
        neg.append('sangue nas fezes')
    if dados.get('viagem_recente') is False:
        neg.append('viagem recente')
    if dados.get('atb_recente_3m') is False:
        neg.append('ATB nos últimos 3 meses')
    if dados.get('imunossuprimido') is False:
        neg.append('imunossupressão')
    if dados.get('sinais_sepse') is False:
        neg.append('sinais de sepse')
    return _fmt_negativas(neg)


def gerar_subjetivo_diarreia(admissao):
    dados = _get_dados_modulo(admissao, 'diarreia', 'organico')
    if not dados:
        return ''

    partes = []
    dur  = dados.get('duracao_dias', 0)
    evac = dados.get('evacuacoes_por_dia', 0)

    if dur <= 14:
        tipo_dur = f'aguda ({dur} dia{"s" if dur != 1 else ""})'
    elif dur <= 30:
        tipo_dur = f'persistente ({dur} dias)'
    else:
        tipo_dur = f'crônica ({dur} dias)'

    carats = []
    if dados.get('fezes_aquosas'):        carats.append('aquosa')
    if dados.get('fezes_sanguinolentas'): carats.append('sanguinolenta')
    if dados.get('fezes_mucosas'):        carats.append('com muco')
    if dados.get('fezes_gordurosas'):     carats.append('gordurosa/esteatorreia')
    carat_str = '/'.join(carats) if carats else 'não especificado'

    partes.append(f'Diarreia {tipo_dur}, {evac} evacuações/dia, fezes {carat_str}')

    if dados.get('febre_38_5'):
        partes.append('febre ≥ 38.5°C')
    elif dados.get('febre'):
        partes.append('febre')

    if dados.get('nausea_vomito'):
        partes.append('náusea/vômito' + (' incoercível' if dados.get('vomito_incoercivel') else ''))

    if dados.get('tenesmo'):
        partes.append('tenesmo')

    # Desidratação
    desat = dados.get('desidratacao_grau', 'sem')
    if desat != 'sem':
        partes.append(f'desidratação {desat}')

    # Imunossupressão
    if dados.get('imunossuprimido'):
        isup = []
        if dados.get('hiv_diagnosticado'):
            s = 'HIV+'
            cd4 = dados.get('cd4_valor')
            if cd4 is not None:
                s += f' CD4={cd4}'
            isup.append(s)
        if dados.get('transplante_quimio_biologico'):
            isup.append('transplante/quimio/biológico')
        if dados.get('corticoide_cronico'):
            isup.append('corticoide crônico')
        partes.append('Imunossupressão: ' + ', '.join(isup))

    # Contexto
    if dados.get('atb_recente_3m'):
        partes.append(f'ATB recente ({dados.get("qual_atb_recente") or "não especificado"})')
    if dados.get('viagem_recente'):
        partes.append(f'viagem recente — {dados.get("destino_viagem", "destino não informado")}')
    if dados.get('surto_alimentar'):
        partes.append(f'surto alimentar ({dados.get("alimento_suspeito", "alimento suspeito")})')

    # Alarmes crônicos
    alarmes = []
    if dados.get('perda_peso_involuntaria'):
        alarmes.append(f'perda de peso {dados.get("perda_peso_kg", "?")} kg')
    if dados.get('anemia_sintomas'):    alarmes.append('anemia')
    if dados.get('hematochezia_cronica'): alarmes.append('hematoquesia crônica')
    if dados.get('nocturna'):           alarmes.append('diarreia noturna')
    if alarmes:
        partes.append('Alarmes: ' + ', '.join(alarmes))

    neg = _negativas_diarreia(dados)
    if neg:
        partes.append(neg)

    return _partes_para_texto(partes, separador='. ')


def _gerar_texto_diarreia_analise(resultado, dados):
    """Impressão em prosa clínica para o SOAP — diarreia no adulto."""
    categoria = resultado.get('categoria', '')
    linhas    = []

    label = _LABEL_DIARREIA.get(categoria, categoria)
    desat = resultado.get('desidratacao_grau', 'sem')

    # Alertas críticos de segurança primeiro
    alertas = []
    if resultado.get('atb_contraindicado'):
        alertas.append('ANTIBIÓTICO CONTRAINDICADO — risco de SHU')
    if resultado.get('loperamida_contraindicada'):
        alertas.append('LOPERAMIDA CONTRAINDICADA — risco de megacólon tóxico')
    if resultado.get('internacao'):
        alertas.append('INTERNAÇÃO indicada')
    if resultado.get('notificar_vigilancia'):
        alertas.append('Notificar Vigilância Epidemiológica')

    cabec = f'{label}.'
    if desat != 'sem':
        cabec += f' Desidratação {desat}.'
    if alertas:
        cabec += ' ' + ' | '.join(alertas) + '.'
    linhas.append(cabec)

    # (exames solicitados → #Plano)

    # Detalhes específicos por categoria
    if categoria == 'diarreia_imunossuprimido':
        cd4  = resultado.get('cd4', 'desconhecido')
        pats = resultado.get('patogenos_suspeitos', [])
        if pats:
            linhas.append('Oportunistas: ' + '; '.join(pats[:3]) + '.')

    if categoria == 'diarreia_toxinfeccao':
        agente = resultado.get('agente_provavel', '')
        if agente:
            linhas.append(f'Agente provável: {agente}.')

    if categoria == 'diarreia_viajante':
        destino = resultado.get('destino', '')
        if destino:
            linhas.append(f'Destino: {destino}.')
        if resultado.get('asia'):
            linhas.append('Resistência a fluoroquinolonas > 90% neste destino (Ásia).')

    if categoria in ('diarreia_dii_suspeita', 'diarreia_sii_d', 'diarreia_cronica_alarme_eletivo'):
        calp = resultado.get('calprotectina')
        if calp is not None:
            linhas.append(f'Calprotectina fecal: {calp} mcg/g.')

    if resultado.get('zona_cinzenta'):
        linhas.append('Calprotectina zona cinzenta (50–200 mcg/g) — resultado indeterminado.')

    alarmes = resultado.get('alarmes', [])
    if alarmes:
        linhas.append('Alarmes: ' + ', '.join(alarmes) + '.')

    if resultado.get('pendente'):
        linhas.append(resultado['pendente'] + '.')

    return '\n\n'.join(linhas)


# ------------------------------------------------------------------
# ARBOVIROSES — subjetivo em prosa + análise automática
# ------------------------------------------------------------------

_LABEL_ARBOVIROSES = {
    'arboviral_grupo_d':        'Dengue Grave / Choque — Grupo D',
    'arboviral_grupo_c':        'Dengue com Sinais de Alarme — Grupo C',
    'arboviral_grupo_b':        'Dengue Provável — Grupo B (Condição Especial)',
    'arboviral_grupo_a':        'Dengue Provável — Grupo A (Ambulatorial)',
    'chikungunya_suspeita':     'Chikungunya (suspeita)',
    'zika_suspeita':            'Zika (suspeita)',
    'arboviral_indiferenciada': 'Síndrome Febril Arboviral Indiferenciada',
}

_ALARME_LABEL_ARBO = {
    'dor_abdominal_intensa':   'dor abdominal intensa',
    'vomitos_persistentes':    'vômitos persistentes',
    'sangramento_mucosa':      'sangramento de mucosa',
    'hipotensao_postural':     'hipotensão postural',
    'letargia_irritabilidade': 'letargia/irritabilidade',
    'hepatomegalia_referida':  'hepatomegalia referida',
}


_ALARMES_ARBO_KEYS = [
    'dor_abdominal_intensa', 'vomitos_persistentes', 'acumulo_liquidos',
    'hipotensao_postural', 'hepatomegalia_referida', 'sangramento_mucosa',
    'letargia_irritabilidade', 'aumento_hematocrito',
]
_CHOQUE_ARBO_KEYS = ['hipotensao_severa', 'pulso_filiforme', 'tec_maior_3s', 'sudorese_fria']


def _negativas_arboviroses(dados: dict) -> str:
    """Pertinentes negativas documentadas no #Subjetivo — Arboviroses."""
    neg = []
    # Área endêmica — clinicamente relevante quando ausente
    if dados.get('area_endemica') is False:
        neg.append('área endêmica de dengue')
    # Sinais de alarme — documenta ausência coletiva se nenhum estiver presente
    if not any(dados.get(k) for k in _ALARMES_ARBO_KEYS):
        neg.append('sinais de alarme de dengue')
    # Sinais de choque
    if not any(dados.get(k) for k in _CHOQUE_ARBO_KEYS):
        neg.append('sinais de choque')
    # Gestação
    if dados.get('gestante') is False:
        neg.append('gestação')
    return _fmt_negativas(neg)


def gerar_subjetivo_arboviroses(admissao):
    dados = _get_dados_modulo(admissao, 'arboviroses', 'organico')
    if not dados:
        return ''

    partes = []

    # Febre
    if dados.get('febre_presente'):
        dias = dados.get('dias_febre', 0)
        txt = f'febre há {dias} dia{"s" if dias != 1 else ""}'
        if dados.get('febre_alta'):
            txt += ' (≥ 38,5°C)'
        if dados.get('inicio_subito'):
            txt += ', início súbito'
        partes.append(txt.capitalize())

    # Sintomas sistêmicos
    sist = []
    if dados.get('cefaleia'):            sist.append('cefaleia')
    if dados.get('mialgia_intensa'):     sist.append('mialgia intensa')
    if dados.get('dor_retroorbitaria'):  sist.append('dor retroorbitária')
    if dados.get('nausea'):              sist.append('náusea')
    if dados.get('vomitos'):             sist.append('vômitos')
    if sist:
        partes.append(', '.join(sist))

    # Exantema
    if dados.get('exantema_presente'):
        txt = 'exantema'
        if dados.get('exantema_pruriginoso'):
            txt += ' pruriginoso'
        partes.append(txt)

    # Artralgia
    if dados.get('artralgia_presente'):
        txt = 'artralgia'
        if dados.get('artralgia_incapacitante'):
            txt += ' incapacitante'
        if dados.get('artralgia_simetrica'):
            txt += ' simétrica'
        if dados.get('edema_articular'):
            txt += ' com edema articular'
        meses = dados.get('artralgia_meses', 0)
        if meses >= 3:
            txt += f' há {meses} meses (fase crônica)'
        partes.append(txt)

    # Conjuntivite
    if dados.get('conjuntivite'):
        partes.append('conjuntivite não purulenta' if dados.get('conjuntivite_nao_purulenta') else 'conjuntivite')

    # Sinais de alarme
    alarmes = [_ALARME_LABEL_ARBO.get(k, k)
               for k in _ALARME_LABEL_ARBO if dados.get(k)]
    if alarmes:
        partes.append('SINAIS DE ALARME: ' + ', '.join(alarmes))

    # Sinais de choque
    choque = []
    if dados.get('hipotensao_severa'):  choque.append('hipotensão severa')
    if dados.get('pulso_filiforme'):    choque.append('pulso filiforme')
    if dados.get('tec_maior_3s'):       choque.append('TEC > 3s')
    if dados.get('sudorese_fria'):      choque.append('sudorese fria')
    if choque:
        partes.append('SINAIS DE CHOQUE: ' + ', '.join(choque))

    # Comorbidades
    comorbs = []
    if dados.get('gestante'):           comorbs.append(f'gestante ({dados.get("semanas_gestacao", "?")} semanas)')
    if dados.get('diabetes'):           comorbs.append('DM2')
    if dados.get('has_cardiovascular'): comorbs.append('HAS/cardiovascular')
    if dados.get('drc'):                comorbs.append('DRC')
    if dados.get('hematologica'):       comorbs.append('hemopatia')
    if comorbs:
        partes.append('Comorbidades: ' + ', '.join(comorbs))

    # Prova do laço
    if dados.get('prova_laco_positiva'):
        partes.append('prova do laço positiva')

    neg = _negativas_arboviroses(dados)
    if neg:
        partes.append(neg)

    return '. '.join(partes) + '.' if partes else ''


def _gerar_texto_arboviroses_analise(resultado, dados):
    categoria = resultado.get('categoria', '')
    label = _LABEL_ARBOVIROSES.get(categoria, categoria.upper())
    linhas = []

    grupo = resultado.get('grupo_dengue', '')
    linhas.append(f'{label}.' + (f' Grupo {grupo} (MS 2023).' if grupo else ''))

    # AINE
    if resultado.get('aine_contraindicado'):
        linhas.append('AINE E AAS CONTRAINDICADOS — usar exclusivamente Paracetamol.')
    elif categoria == 'chikungunya_suspeita':
        linhas.append(resultado.get('aine_msg', ''))

    # Zika em gestante
    if resultado.get('alerta_gestante_zika'):
        linhas.append('ALERTA: Zika em gestante — notificação imediata, pré-natal alto risco urgente.')

    # Sinais de alarme
    alarmes = resultado.get('sinais_alarme', [])
    if alarmes:
        nomes = [_ALARME_LABEL_ARBO.get(a, a) for a in alarmes]
        linhas.append(f'Sinais de alarme: {", ".join(nomes)}.')

    # Chikungunya fase
    if categoria == 'chikungunya_suspeita':
        fase = 'crônica' if resultado.get('fase_cronica') else 'aguda'
        linhas.append(f'Fase {fase}.')

    return ' '.join(linhas)


_LABEL_IVAS = {
    'ivas_emergencia':    'Emergência faríngea/cervical',
    'ivas_mononucleose':  'Mononucleose infecciosa (EBV)',
    'ivas_influenza':     'Influenza',
    'ivas_gas':           'Faringite GAS (Estreptococo Grupo A)',
    'ivas_rinossinusite': 'Rinossinusite aguda',
    'ivas_laringite':     'Laringite aguda',
    'ivas_viral':         'IVAS viral',
}


_EMERG_IVAS_KEYS = [
    'assimetria_tonsilar', 'trismo', 'voz_abafada',
    'sialorreia', 'estridor', 'dificuldade_respiratoria', 'edema_submandibular',
]


def _negativas_ivas(dados: dict) -> str:
    """Pertinentes negativas documentadas no #Subjetivo — IVAS."""
    neg = []
    # Sinais de emergência faríngea/cervical — colapsa os 7 em um único item
    if not any(dados.get(k) for k in _EMERG_IVAS_KEYS):
        neg.append('sinais de emergência faríngea')
    # Alergia à penicilina
    if dados.get('alergia_penicilina') is False:
        neg.append('alergia à penicilina')
    # Histórico de FRA
    if dados.get('historico_fra') is False:
        neg.append('FRA prévia')
    # Imunossupressão
    if dados.get('imunossupressao') is False:
        neg.append('imunossupressão')
    return _fmt_negativas(neg)


def gerar_subjetivo_ivas(admissao):
    dados = _get_dados_modulo(admissao, 'ivas', 'organico')
    if not dados:
        return ''

    partes = []

    # Queixa principal + tempo
    dias = dados.get('dias_sintomas', 0)
    inicio_txt = f'há {dias} dia{"s" if dias != 1 else ""}'
    if dados.get('inicio_subito_horas'):
        inicio_txt += ', com início súbito em horas'

    queixa = f'Odinofagia {inicio_txt}'
    rfl = []
    if dados.get('assimetria_tonsilar'):       rfl.append('assimetria tonsilar e desvio de úvula')
    if dados.get('trismo'):                    rfl.append('trismo')
    if dados.get('voz_abafada'):               rfl.append('voz abafada ("batata quente")')
    if dados.get('sialorreia'):                rfl.append('sialorreia')
    if dados.get('estridor'):                  rfl.append('estridor inspiratório')
    if dados.get('dificuldade_respiratoria'):  rfl.append('dificuldade respiratória')
    if dados.get('edema_submandibular'):       rfl.append('edema submandibular endurecido')
    if rfl:
        queixa += f', associada a {", ".join(rfl)}'
    partes.append(queixa + '.')

    # Febre
    if dados.get('febre_alta_39'):
        partes.append('Febre alta (≥39°C) referida.')
    elif dados.get('febre_38'):
        partes.append('Febre (≥38°C) referida.')
    else:
        partes.append('Nega febre.')

    # Tosse
    partes.append('Tosse presente.' if dados.get('tosse_presente') else 'Sem tosse.')

    # Exsudato e linfonodos
    orofar = []
    if dados.get('exsudato_tonsilar'):           orofar.append('exsudato tonsilar')
    if dados.get('linfadenopatia_anterior'):     orofar.append('linfonodos cervicais anteriores dolorosos')
    if dados.get('linfadenopatia_posterior'):    orofar.append('linfonodos cervicais posteriores aumentados')
    if orofar:
        partes.append(f'Refere {", ".join(orofar)}.')

    # Padrão influenza / mono
    if dados.get('mialgia_intensa'):
        partes.append('Mialgia intensa.')
    if dados.get('esplenomegalia_referida'):
        partes.append('Dor no flanco esquerdo sugestiva de esplenomegalia.')

    # Sinusite
    sin = []
    if dados.get('dor_facial'):            sin.append('dor facial e pressão sinusal')
    if dados.get('descarga_purulenta'):    sin.append('descarga nasal purulenta')
    if dados.get('duplo_agravamento'):     sin.append('duplo agravamento (melhora seguida de piora)')
    if dados.get('sintomas_10_dias'):      sin.append('sintomas persistentes há mais de 10 dias')
    if sin:
        partes.append(', '.join(sin).capitalize() + '.')

    # Rouquidão
    if dados.get('rouquidao_predominante'):
        partes.append('Rouquidão como sintoma predominante.')

    # RADT
    if dados.get('radt_realizado'):
        partes.append('RADT realizado: ' + ('positivo.' if dados.get('radt_positivo') else 'negativo.'))

    # Alergias
    if dados.get('alergia_anafilatica'):
        partes.append('Alergia anafilática à penicilina (urticária/angioedema/anafilaxia).')
    elif dados.get('alergia_penicilina'):
        partes.append('Alergia não-anafilática à penicilina (rash sem urticária).')
    if dados.get('historico_fra'):
        partes.append('Histórico de febre reumática aguda.')

    # Comorbidades relevantes para oseltamivir
    comorbs = []
    if dados.get('gestante'):              comorbs.append('gestante')
    if dados.get('asma_dpoc'):            comorbs.append('asma/DPOC')
    if dados.get('doenca_cardiovascular'): comorbs.append('cardiopatia')
    if dados.get('drc'):                  comorbs.append('DRC')
    if dados.get('diabetes'):             comorbs.append('DM')
    if dados.get('imunossupressao'):      comorbs.append('imunossupressão')
    if comorbs:
        partes.append(f'Fatores de risco: {", ".join(comorbs)}.')

    neg = _negativas_ivas(dados)
    if neg:
        partes.append(neg + '.')   # IVAS usa ' '.join() — partes já levam ponto

    return ' '.join(partes)


_SCORE_PROB_IVAS = {
    -1: '<7%', 0: '7-13%', 1: '7-13%',
     2: '21-38%', 3: '21-38%', 4: '51-70%', 5: '51-70%',
}


def _gerar_texto_ivas_analise(resultado, dados):
    """Texto para #Análise do prontuário — IVAS."""
    categoria = resultado.get('categoria', '')
    score     = resultado.get('score_mcisaac', 0)
    prob      = _SCORE_PROB_IVAS.get(score, '?')

    if categoria == 'ivas_emergencia':
        tipo  = resultado.get('emergencia_tipo', '')
        nomes = {
            'abscesso_peritonsilar': 'Abscesso peritonsilar (quinsy)',
            'epiglotite':            'Epiglotite/supraglotite',
            'ludwig':                'Angina de Ludwig',
        }
        sinais = resultado.get('sinais_presentes', '')
        return (f"{nomes.get(tipo, 'Emergência faríngea/cervical')} — diagnóstico clínico de urgência. "
                f"Sinais: {sinais}. Encaminhamento imediato indicado.")

    if categoria == 'ivas_mononucleose':
        dias   = dados.get('dias_sintomas', '?')
        extras = []
        if dados.get('linfadenopatia_posterior'): extras.append('linfadenopatia posterior')
        if dados.get('esplenomegalia_referida'):  extras.append('esplenomegalia referida')
        return (f"Mononucleose infecciosa por EBV — suspeita. "
                f"Sintomas há {dias} dias com {' e '.join(extras) if extras else 'padrão sugestivo'}. "
                f"ATENÇÃO: amoxicilina/ampicilina contraindicadas — rash em 80-100% dos casos.")

    if categoria == 'ivas_influenza':
        dias      = dados.get('dias_sintomas', '?')
        alto_risco = any([
            int(dados.get('idade', 0)) >= 65, dados.get('asma_dpoc'),
            dados.get('doenca_cardiovascular'), dados.get('drc'), dados.get('hepatopatia'),
            dados.get('diabetes'), dados.get('imunossupressao'),
            dados.get('gestante'), dados.get('obesidade_grave'),
        ])
        txt = (f"Influenza — suspeita clínica. Padrão: início súbito, mialgia intensa, "
               f"febre alta, sem exsudato tonsilar. Sintomas há {dias} dia{'s' if int(str(dias)) != 1 else ''}.")
        if alto_risco:
            txt += " Fator de alto risco presente — cobertura antiviral precoce a considerar."
        return txt

    if categoria == 'ivas_gas':
        criterios = []
        if dados.get('febre_38'):                criterios.append('febre ≥38°C')
        if dados.get('exsudato_tonsilar'):        criterios.append('exsudato tonsilar')
        if dados.get('linfadenopatia_anterior'):  criterios.append('linfonodos cervicais anteriores dolorosos')
        if not dados.get('tosse_presente'):       criterios.append('ausência de tosse')
        if int(dados.get('idade', 30)) >= 45:     criterios.append('ajuste etário −1 (≥45 anos)')
        crit_str = ' + '.join(criterios) if criterios else 'critérios avaliados'
        rec = resultado.get('recomendacao_atb', '')
        rec_map = {
            'tratar':          'RADT positivo — GAS confirmado.',
            'tratar_empirico': f'RADT indisponível — probabilidade de GAS {prob}; tratamento empírico.',
            'indicar_radt':    f'Probabilidade de GAS {prob} — RADT indicado para confirmar.',
            'nao_tratar':      'RADT negativo — GAS descartado em adulto.',
        }
        return (f"Faringite por Estreptococo do Grupo A (GAS) — avaliação. "
                f"Score de McIsaac {score} pontos ({crit_str}): probabilidade de GAS {prob}. "
                f"{rec_map.get(rec, '')}")

    if categoria == 'ivas_rinossinusite':
        dias  = dados.get('dias_sintomas', 0)
        duplo = dados.get('duplo_agravamento', False)
        if int(str(dias)) > 10 or dados.get('sintomas_10_dias') or duplo:
            motivo = 'duplo agravamento' if duplo else f'sintomas persistentes há {dias} dias (>10 dias)'
            return (f"Rinossinusite aguda — provável etiologia bacteriana ({motivo}). "
                    f"Dor facial e descarga purulenta presentes.")
        return (f"Rinossinusite aguda — provável etiologia viral (sintomas há {dias} dias, "
                f"sem critérios bacterianos). Dor facial e descarga purulenta presentes.")

    if categoria == 'ivas_laringite':
        return ("Laringite aguda — etiologia viral provável. "
                "Rouquidão como sintoma predominante, sem critérios de alarme. ATB não indicado.")

    # ivas_viral
    return (f"IVAS viral — diagnóstico de exclusão. Score de McIsaac {score} "
            f"(probabilidade GAS {prob}), sem critérios de mononucleose, influenza, sinusite ou laringite. "
            f"ATB não indicado.")


def _rx(atb, prefixo='Prescrevo:'):
    """Formata um ATB no estilo receituário: nome ------ Ncp / posologia."""
    linhas = [prefixo]
    nome = atb.get('medicamento', '')
    for i, p in enumerate(atb.get('prescricoes', [])):
        if i > 0:
            linhas += ['', 'ou']
        qtd  = str(p['quantidade'])
        uni  = p['unidade']
        fill = max(3, 50 - len(nome) - len(qtd) - len(uni))
        linhas.append(f'{nome} {"-" * fill} {qtd} {uni}')
        linhas.append(f'  {p["posologia"]}')
    if atb.get('nota'):
        linhas.append(f'  Obs.: {atb["nota"]}')
    return linhas


_LABEL_URINARIO = {
    'cistite_simples':              'Cistite não complicada',
    'cistite_complicada':           'Cistite complicada (cultura obrigatória)',
    'cistite_gestante':             'Cistite na gestante',
    'cistite_recorrente':           'Cistite recorrente',
    'pielonefrite_ambulatorial':    'Pielonefrite — tratamento ambulatorial',
    'pielonefrite_emergencia':      'Pielonefrite — critérios de internação',
    'itu_masculina':                'ITU masculina (sempre complicada)',
    'prostatite_aguda':             'Prostatite aguda bacteriana',
    'prostatite_cronica':           'Prostatite crônica / CPPS',
    'hpb_stui':                     'HPB — sintomas do trato urinário inferior',
    'uretrite_ist':                 'Uretrite / IST',
    'vaginite_candida':             'Candidíase vulvovaginal',
    'vaginite_bv':                  'Vaginose bacteriana',
    'vaginite_atrofica':            'Síndrome geniturinária da menopausa',
    'herpes_genital':               'Herpes genital',
    'sd_uretral':                   'Síndrome uretral',
    'hematuria_macro_emergencia':   'Hematúria macroscópica — emergência',
    'hematuria_macro_urgente':      'Hematúria macroscópica — encaminhar urologia',
    'hematuria_macro_itu':          'Hematúria macroscópica + ITU',
    'hematuria_macro_calculose':    'Hematúria — cálculo urinário provável',
    'hematuria_micro_glomerular':   'Hematúria microscópica — padrão glomerular',
    'hematuria_micro_alto_risco':   'Hematúria microscópica — alto risco',
    'hematuria_micro_moderado_risco': 'Hematúria microscópica — risco moderado',
    'hematuria_micro_baixo_risco':  'Hematúria microscópica — baixo risco',
    'hematuria_nao_confirmada':     'Hematúria não confirmada',
    'red_flag_urinario':            'Queixa urinária com red flag',
}

_URGENCIA_LABEL = {
    'emergencia': 'EMERGÊNCIA — PA/PS imediato',
    'urgente':    'urgente — avaliação hoje',
    'eletivo':    'eletivo',
}


def _gerar_texto_urinario_analise(resultado):
    """Impressão em prosa clínica para o #Análise do SOAP — queixas urinárias."""
    categoria  = resultado.get('categoria', '')
    diagnostico = resultado.get('diagnostico', '')
    urgencia   = resultado.get('urgencia')
    linhas     = []

    label = _LABEL_URINARIO.get(categoria, diagnostico or categoria)

    # Cabeçalho: categoria + urgência
    cabec = label + '.'
    if urgencia:
        urg_txt = _URGENCIA_LABEL.get(urgencia, urgencia)
        cabec  += f' Encaminhamento {urg_txt}.'
    linhas.append(cabec)

    # Red flags (emergência)
    for flag in resultado.get('red_flags', []):
        achado = flag.get('achado', '')
        acao   = flag.get('acao', '')
        if achado:
            linhas.append(f'Alerta: {achado}' + (f' → {acao}' if acao else '') + '.')

    # Achados clínicos relevantes (primeiros 4)
    achados = resultado.get('achados', [])
    if achados:
        linhas.append('Achados: ' + ' | '.join(achados[:4]) + '.')

    # Exames (primeiros 4)
    exames = resultado.get('exames', [])
    if exames:
        linhas.append('Solicitar: ' + ', '.join(exames[:4]) + '.')

    return '\n'.join(linhas)


def _plano_urinario(resultado):
    """Texto para #Plano do prontuário — Queixas Urinárias."""
    categoria  = resultado.get('categoria', '')
    diagnostico = resultado.get('diagnostico', 'Queixa urinária')
    urgencia   = resultado.get('urgencia')
    linhas     = [f'Queixa Urinária — {diagnostico}']

    # Urgência / encaminhamento primeiro
    if urgencia == 'emergencia':
        linhas += ['', '⚠️  ENCAMINHAMENTO IMEDIATO — PA/PS']
        for c in resultado.get('conduta', []):
            linhas.append(f'• {c}')
        linhas += [
            '',
            'Critérios de sepse urinária: febre + calafrio OU hipotensão OU alteração mental.',
        ]
        return '\n'.join(linhas)

    # Encaminhamento urgente / eletivo
    enc = resultado.get('encaminhar')
    if enc and urgencia == 'urgente':
        linhas += ['', f'→ Encaminhar: {enc}']

    # Exames
    exames = resultado.get('exames', [])
    if exames:
        linhas += ['', 'Solicito:']
        for e in exames:
            linhas.append(f'  • {e}')

    # Condutas não farmacológicas
    conduta = resultado.get('conduta', [])
    if conduta:
        linhas += ['', 'Oriento:']
        for c in conduta:
            linhas.append(f'  • {c}')

    # Prescrições estruturadas
    prescricoes = resultado.get('prescricoes_estruturadas', [])
    if prescricoes:
        linhas += ['']
        for med in prescricoes:
            linha_label = med.get('linha', '')
            if linha_label:
                linhas.append(f'[{linha_label}]')
            linhas += _rx(med)
            linhas.append('')

    # Encaminhamento eletivo (ao final)
    if enc and urgencia not in ('emergencia', 'urgente'):
        linhas += [f'Encaminhamento eletivo: {enc}']

    # Retorno
    retorno = resultado.get('retorno', '')
    if retorno:
        linhas += ['', retorno]

    return '\n'.join(linhas)


def _plano_cefaleia(resultado):
    """Texto para #Plano do prontuário — Cefaleia."""
    dx      = resultado.get('diagnostico', '')
    linhas  = []

    # ── Secundária grave — encaminhamento ───────────────────────────────────
    if 'secundaria grave' in dx:
        linhas += [
            'Encaminhamento imediato ao PS — cefaleia com sinais de alarme.',
            'NÃO analgesia empírica antes da TC de crânio sem contraste.',
        ]
        return '\n'.join(linhas)

    # ── Cefaleia em salvas ───────────────────────────────────────────────────
    if 'salvas' in dx or 'cluster' in dx:
        linhas += [
            'Abortivo da crise:',
            '• O₂ 100% — máscara NRM 12–15 L/min por 15–20 min.',
            '• Sumatriptano 6mg SC (uso particular) — padrão-ouro se O₂ insuficiente.',
            '',
            'Profilaxia (iniciar junto ao abortivo):',
        ]
        linhas += [f'• {c}' for c in resultado.get('conduta', [])
                   if any(k in c for k in ('Verapamil', 'Prednisolona', 'Litio', 'Lítio'))]
        linhas.append('Encaminhar neurologia / ambulatório de cefaleia.')
        return '\n'.join(linhas)

    # ── Enxaqueca ────────────────────────────────────────────────────────────
    if 'enxaqueca' in dx:
        linhas += [
            'Crise (tomar ao 1º sinal — não esperar dor estabelecida):',
            '• Ibuprofeno 400–600 mg VO (1ª linha, NNT 7.2).',
            '• Alternativo (uso particular): Sumatriptano 50–100 mg VO.',
            '• Se náusea intensa: Metoclopramida 10 mg VO antes do analgésico.',
            '',
            'Profilaxia (≥ 4 crises/mês ou crises incapacitantes):',
            '',
            'Prescrevo (1ª linha):',
        ]
        linhas += [
            'Propranolol 40mg ----------- 60 comprimidos',
            '  Tomar 1 comprimido de 12 em 12 horas por 30 dias (reavaliação)',
            '  * Contraindicado em asma, BAV, bradicardia sintomática',
            '',
            'ou (especialmente se insônia ou tensional associada):',
            'Amitriptilina 25mg --------- 30 comprimidos',
            '  Semana 1: Tomar ½ comprimido (~12,5 mg) ao deitar',
            '    (partir ao meio — SUS não disponibiliza 10mg; ~12,5mg é dose de início adequada)',
            '  Semana 2+: Tomar 1 comprimido (25 mg) ao deitar',
            '  * Efeito profilático surge em 4–8 semanas — não abandonar antes',
            '  * Cuidado: sedação, boca seca; evitar em glaucoma e BAV',
            '',
            'ou (se falha das 1as linhas — ATENÇÃO):',
            'Topiramato 25mg (inicio) → titular até 50–100mg/dia — encaminhar neurologia',
            '  !! TERATOGÊNICO — anticoncepção efetiva obrigatória em mulheres férteis !!',
            '',
            'Orientações:',
            '• MOH: NÃO usar AINE ou triptano > 10 dias/mês — cronifica a dor.',
            '• Diário de cefaleia: anotar frequência, duração, intensidade e gatilhos.',
        ]
        return '\n'.join(linhas)

    # ── Tensional ────────────────────────────────────────────────────────────
    if 'tensional' in dx:
        linhas += [
            'Crise:',
            '• Paracetamol 500–750 mg VO — 1ª escolha (menor risco de MOH).',
            '• Alt.: Ibuprofeno 400 mg VO 8/8h — máx 3 dias consecutivos.',
            '',
            'Profilaxia (se ≥ 15 dias/mês — cefaleia tensional crônica):',
            'Amitriptilina 25mg --------- 30 comprimidos',
            '  Semana 1: Tomar ½ comprimido (~12,5 mg) ao deitar',
            '    (partir ao meio — SUS não disponibiliza 10mg)',
            '  Semana 2+: Tomar 1 comprimido (25 mg) ao deitar',
            '  * Não usar em glaucoma, retenção urinária ou arritmia conhecida',
            '',
            'Orientações:',
            '• Revisar postura, sono e estresse.',
            '• Fisioterapia cervical e relaxamento progressivo — eficácia semelhante à medicação.',
            '• MOH: suspender analgésico se uso > 10–15 dias/mês.',
        ]
        return '\n'.join(linhas)

    # ── Sem padrão definido ──────────────────────────────────────────────────
    linhas += [
        'Analgesia de crise: Paracetamol 500–1000 mg VO ou Dipirona 1 g VO.',
        'Diário de cefaleia por 4 semanas — retornar com registro para classificação.',
    ]
    return '\n'.join(linhas)


def _plano_pneumonia(atb):
    """Texto para #Plano do prontuário — PAC ambulatorial."""

    def _rx_pac(med, prefixo='Prescrevo:'):
        """_rx sem repetir a nota quando ela já está em contexto."""
        linhas = [prefixo]
        nome = med.get('medicamento', '')
        for i, p in enumerate(med.get('prescricoes', [])):
            if i > 0:
                linhas += ['', 'ou']
            qtd  = str(p['quantidade'])
            uni  = p['unidade']
            fill = max(3, 50 - len(nome) - len(qtd) - len(uni))
            linhas.append(f'{nome} {"-" * fill} {qtd} {uni}')
            linhas.append(f'  {p["posologia"]}')
        return linhas

    linhas  = []
    cenario = atb.get('cenario', 'A')
    desc    = atb.get('descricao', '')

    linhas += [
        f'Pneumonia Adquirida na Comunidade — Cenário {cenario}',
        f'({desc})',
        '',
    ]

    if cenario == 'A':
        linhas += _rx_pac(atb.get('atb_principal', {}))
        at = atb.get('cobertura_atipico', {})
        if at:
            nota = at.get('nota', '')
            linhas += ['', f'+ Cobertura de atípicos (se padrão atípico: {nota}):']
            linhas += _rx_pac(at, prefixo='Adicionar:')
    else:
        op1 = atb.get('opcao_1', {})
        op2 = atb.get('opcao_2', {})
        if op1:
            linhas += [f'Opção 1 — {op1.get("nome", "")}:', '']
            linhas += _rx_pac(op1.get('atb_principal', {}))
            if op1.get('atb_atipico'):
                linhas += ['', '+ Cobertura de atípicos:']
                linhas += _rx_pac(op1.get('atb_atipico', {}), prefixo='Adicionar:')
        if op2:
            linhas += [
                '',
                f'Opção 2 — {op2.get("nome", "")}',
                f'  ({op2.get("nota", "")})',
                '',
            ]
            linhas += _rx_pac(op2.get('atb_principal', {}))
            alt = op2.get('alternativo', {})
            if alt:
                linhas += ['', 'ou (se 750mg indisponível):']
                linhas += _rx_pac(alt)

    linhas += [
        '',
        'Critérios de internação — CURB-65 (internar se ≥ 2 pontos):',
        '  C = confusão mental aguda  |  U = ureia ≥ 43 mg/dL',
        '  R = FR ≥ 30/min            |  B = PAS < 90 ou PAD ≤ 60 mmHg',
        '  65 = idade ≥ 65 anos',
        'Retorno imediato se: SatO₂ < 92%, FR > 24/min, não tolera VO ou piora em 48h.',
    ]
    return '\n'.join(linhas)


def _plano_ivas(resultado, dados):
    """Texto para #Plano do prontuário — IVAS."""
    categoria = resultado.get('categoria', '')
    linhas    = []

    if categoria == 'ivas_emergencia':
        tipo  = resultado.get('emergencia_tipo', '')
        nomes = {
            'abscesso_peritonsilar': 'abscesso peritonsilar',
            'epiglotite':            'epiglotite',
            'ludwig':                'angina de Ludwig',
        }
        linhas.append(
            f'Encaminhamento urgente para PS/especialidade ({nomes.get(tipo, "emergência")}) '
            f'— não tratar em UBS.'
        )
        for c in resultado.get('conduta', [])[:4]:
            linhas.append(f'• {c}')
        return '\n'.join(linhas)

    if categoria == 'ivas_mononucleose':
        linhas += [
            'ATB: não prescrito (amoxicilina/ampicilina contraindicadas na mononucleose).',
            '',
            'Sintomáticos:',
            '• Prescrevo Dipirona 1000mg VO 6/6h se dor ou febre (máx 4g/dia).',
            '• Alt.: Ibuprofeno 400mg VO 8/8h.',
            '',
            'Oriento restrição de esportes de contato por 4-6 semanas (risco de ruptura esplênica).',
            'Oriento retorno imediato se: dor abdominal intensa, dispneia ou estridor, rigidez de nuca.',
        ]
        return '\n'.join(linhas)

    if categoria == 'ivas_influenza':
        dias      = int(dados.get('dias_sintomas', 99))
        alto_risco = any([
            int(dados.get('idade', 0)) >= 65, dados.get('asma_dpoc'),
            dados.get('doenca_cardiovascular'), dados.get('drc'), dados.get('hepatopatia'),
            dados.get('diabetes'), dados.get('imunossupressao'),
            dados.get('gestante'), dados.get('obesidade_grave'),
        ])
        if dias <= 2 and alto_risco:
            linhas.append('Prescrevo Oseltamivir 75mg VO 12/12h por 5 dias (alto risco, sintomas ≤48h).')
        linhas += [
            '',
            'Sintomáticos:',
            '• Prescrevo Dipirona 1000mg VO 6/6h se dor ou febre (máx 4g/dia).',
            '• Alt.: Paracetamol 500-1000mg VO 6/6h (máx 3g/dia — teto reduzido por risco de interseção epidemiológica).',
            '',
            'Oriento repouso e hidratação oral adequada.',
            'Oriento retorno imediato se: dispneia, SatO2 <95%, piora após melhora inicial.',
        ]
        return '\n'.join(linhas)

    if categoria == 'ivas_gas':
        rec     = resultado.get('recomendacao_atb', '')
        atb     = resultado.get('atb_prescrito')    # None quando indicar_radt
        atb_rec = resultado.get('atb_recomendado')  # sempre presente
        atb_alt = resultado.get('atb_alternativo')  # sempre presente

        if rec == 'nao_tratar':
            linhas.append('ATB: não indicado — RADT negativo descarta GAS em adultos.')

        elif rec == 'indicar_radt':
            linhas.append('ATB: aguardar resultado do RADT antes de prescrever.')
            linhas.append('')
            if atb_rec:
                linhas += _rx(atb_rec, prefixo='Se RADT positivo — Prescrevo:')
            if atb_alt:
                linhas.append('')
                linhas += _rx(atb_alt, prefixo='Alternativo:')

        else:  # tratar / tratar_empirico
            if atb:
                linhas += _rx(atb)
            if atb_alt:
                linhas.append('')
                linhas += _rx(atb_alt, prefixo='Alternativo:')
        linhas += [
            '',
            'Sintomáticos:',
            '• Prescrevo Dipirona 1000mg VO 6/6h se dor ou febre (máx 4g/dia).',
            '• Alt.: Paracetamol 500-1000mg VO 6/6h (máx 3g/dia — teto reduzido por risco de interseção epidemiológica).',
            '• Alt.: Ibuprofeno 400mg VO 8/8h se odinofagia intensa '
            '(suspender se RADT negativo + rash → reconsiderar mononucleose).',
        ]
        if dados.get('odinofagia_severa') or resultado.get('odinofagia_severa'):
            linhas.append(
                '• Adjuvante: Dexametasona 6-10mg VO/IM DU (ou Prednisona 40mg VO DU) '
                '— odinofagia grave com dificuldade para deglutir; reduz edema tonsilar e alivia rapidamente.'
            )
        linhas += [
            '',
            'Orientações: pastilhas analgésicas (benzocaína/cetilpiridínio) para alívio local; '
            'gargarejo com água morna + sal; hidratação oral; repouso.',
            'Oriento retorno imediato se: não melhora em 48-72h com ATB; assimetria tonsilar ou '
            'trismo (abscesso peritonsilar); rash com ATB (pensar mononucleose); febre >7 dias.',
        ]
        return '\n'.join(linhas)

    if categoria == 'ivas_rinossinusite':
        dias      = int(dados.get('dias_sintomas', 0))
        duplo     = dados.get('duplo_agravamento', False)
        bacteriana = dias > 10 or dados.get('sintomas_10_dias') or duplo
        if bacteriana:
            linhas += [
                'Prescrevo Amoxicilina-Clavulanato 875/125mg VO 12/12h por 5-7 dias.',
                'Alt.: Doxiciclina 100mg VO 12/12h por 5-7 dias (se alergia à penicilina).',
            ]
        else:
            linhas.append('ATB: não indicado (provável viral, <10 dias, sem duplo agravamento).')
        linhas += [
            '',
            'Prescrevo lavagem nasal com SF 0,9% 3-4x/dia.',
            'Prescrevo Fluticasona spray nasal 50mcg/puff — 2 puffs/narina 1x/dia.',
            'Prescrevo Dipirona 1000mg VO 6/6h ou Ibuprofeno 400mg VO 8/8h se dor facial.',
            'Oriento retorno se: edema periorbital, cefaleia intensa + rigidez de nuca, '
            'piora após 72h com ATB.',
        ]
        return '\n'.join(linhas)

    if categoria == 'ivas_laringite':
        linhas += [
            'ATB: não indicado.',
            'Prescrevo Ibuprofeno 400mg VO 8/8h por 3-5 dias se inflamação laríngea.',
            'Orientações: repouso vocal; líquidos mornos; umidificação do ar; evitar tabaco e álcool.',
            'Oriento: rouquidão persistente >3 semanas sem causa → laringoscopia.',
        ]
        return '\n'.join(linhas)

    # ivas_viral
    linhas += [
        'ATB: não indicado — IVAS viral.',
        'Sintomáticos:',
        '• Prescrevo Dipirona 1000mg VO 6/6h se dor ou febre (máx 4g/dia).',
        '• Alt.: Paracetamol 500-1000mg VO 6/6h (máx 3g/dia — teto reduzido por risco de interseção epidemiológica).',
        '• Alt.: Ibuprofeno 400mg VO 8/8h se odinofagia intensa.',
        'Orientações: pastilhas analgésicas; gargarejo com água morna + sal; '
        'hidratação oral; repouso.',
        'Oriento retorno se: febre >7 dias, surgimento de exsudato, piora após melhora.',
    ]
    return '\n'.join(linhas)


# ------------------------------------------------------------------
# GASTRO — #Análise e #Plano
# ------------------------------------------------------------------

_LABEL_GASTRO = {
    'gastro_emergencia_peritonite':           'Peritonite / Abdôme Agudo',
    'gastro_emergencia_obstrucao':            'Obstrução Intestinal',
    'gastro_emergencia_sangramento_gi':       'Sangramento Digestivo Ativo',
    'gastro_emergencia_apendicite':           'Apendicite Aguda Suspeita',
    'gastro_emergencia_colecistite':          'Colecistite Aguda',
    'gastro_emergencia_isquemia_mesenterica': 'Isquemia Mesentérica',
    'gastro_emergencia_ectopica':             'Gravidez Ectópica Suspeita',
    'gastro_emergencia_diverticulite_complicada': 'Diverticulite Complicada',
    'gastro_dip':                             'DIP — Doença Inflamatória Pélvica',
    'gastro_diverticulite_ambulatorial':      'Diverticulite Ambulatorial',
    'gastro_ibd_suspeita':                    'IBD Suspeita (Crohn / Retocolite)',
    'gastro_celiaca_suspeita':                'Doença Celíaca Suspeita',
    'gastro_parasitose_ameba':                'Amebíase Intestinal',
    'gastro_parasitose_helminto':             'Helmintose',
    'gastro_parasitose_protozoa':             'Giardíase',
    'gastro_colica_biliar':                   'Cólica Biliar',
    'gastro_dispepsia_hp_positivo':           'Erradicação H. pylori (V Consenso Br 2025)',
    'gastro_dispepsia_hp_testandteat':        'Dispepsia — Test-and-Treat H. pylori',
    'gastro_dispepsia_funcional':             'Dispepsia Funcional',
    'gastro_sii_c':                           'SII-C',
    'gastro_sii_d':                           'SII-D',
    'gastro_sii_m':                           'SII-M',
    'gastro_constipacao_funcional':           'Constipação Funcional',
    'gastro_intolerancia_lactose':            'Intolerância à Lactose',
    'gastro_nausea_vomito':                   'Náusea / Vômito',
    'gastro_inespecifico':                    'Dor Abdominal — Em Investigação',
}

_GASTRO_CATS = frozenset(_LABEL_GASTRO.keys())


def _analise_gastro(resultado):
    """Impressão clínica em prosa para #Análise — Queixas GI."""
    cat       = resultado.get('categoria', '')
    diag      = resultado.get('diagnostico', '')
    urgencia  = resultado.get('urgencia')
    raciocinio = resultado.get('raciocinio', '')
    achados   = resultado.get('achados', [])
    linhas    = []

    label = _LABEL_GASTRO.get(cat, diag)

    # Cabeçalho
    cab = label + '.'
    if urgencia == 'emergencia':
        cab += ' Encaminhamento IMEDIATO.'
    elif urgencia == 'urgente':
        cab += ' Urgente.'
    linhas.append(cab)

    # Raciocínio clínico (por que acho que é isso)
    if raciocinio:
        linhas.append(raciocinio)

    # Achados clínicos
    if achados:
        linhas.append('Achados: ' + ' | '.join(achados[:5]) + '.')

    # Alerta C. diff
    if resultado.get('alerta_cdiff'):
        linhas.append(
            'Atenção: ATB recente + diarreia → pesquisar C. difficile '
            '(toxina A/B nas fezes). Não prescrever loperamida até excluir.'
        )

    # Exames (primeiros 3)
    exames = resultado.get('exames', [])
    if exames:
        linhas.append('Solicitar: ' + ' | '.join(
            [e for e in exames[:3] if not e.startswith('⚠️')]
        ) + '.')

    return '\n'.join(linhas)


def _plano_gastro(resultado):
    """Texto para #Plano + #Orientações — Queixas GI."""
    cat      = resultado.get('categoria', '')
    diag     = resultado.get('diagnostico', '')
    urgencia = resultado.get('urgencia')
    linhas   = [f'Gastro — {_LABEL_GASTRO.get(cat, diag)}']

    # Emergência
    if urgencia == 'emergencia':
        linhas += ['', '⚠️  ENCAMINHAMENTO IMEDIATO — PA/PS']
        for c in resultado.get('conduta', []):
            linhas.append(f'• {c}')
        return '\n'.join(linhas)

    # ── Alertas de segurança (pente fino) — renderizados no TOPO ──────────────
    for alerta in resultado.get('alertas_seguranca', []):
        linhas += ['', alerta]

    # Encaminhamento urgente
    enc = resultado.get('encaminhar')
    if enc and urgencia == 'urgente':
        linhas += ['', f'→ {enc}']

    # Alerta C. diff (legado — mantido por compatibilidade com engines sem pente fino)
    if resultado.get('alerta_cdiff') and not any(
        'C. diff' in a for a in resultado.get('alertas_seguranca', [])
    ):
        linhas += [
            '',
            '⚠️  ATB recente + diarreia → considerar C. difficile',
            '   Solicitar: pesquisa de toxina A/B nas fezes',
            '   Não prescrever loperamida até excluir colite por C. diff',
        ]

    # Exames
    exames = resultado.get('exames', [])
    if exames:
        linhas += ['', 'Solicito:']
        for e in exames:
            linhas.append(f'  • {e}')

    # Conduta não farmacológica
    conduta = resultado.get('conduta', [])
    if conduta:
        linhas += ['', 'Oriento:']
        for c in conduta:
            linhas.append(f'  • {c}')

    # Prescrições estruturadas
    prescricoes = resultado.get('prescricoes_estruturadas', [])
    if prescricoes:
        linhas += ['']
        for med in prescricoes:
            linha_label = med.get('linha', '')
            if linha_label:
                linhas.append(f'[{linha_label}]')
            linhas += _rx(med)
            linhas.append('')

    # Encaminhamento eletivo
    if enc and urgencia not in ('emergencia', 'urgente'):
        linhas += [f'Encaminhamento eletivo: {enc}']

    # Retorno
    retorno = resultado.get('retorno', '')
    if retorno:
        linhas += ['', retorno]

    # #Orientações ao Paciente
    orientacoes = resultado.get('orientacoes', {})
    if orientacoes:
        linhas += ['', '#Orientações ao Paciente:']
        for chave, valor in orientacoes.items():
            if chave == 'sinais_de_alerta':
                linhas += ['', 'Retornar imediatamente se:']
                for s in valor:
                    linhas.append(f'  ⚠️  {s}')
            elif isinstance(valor, str) and valor.strip():
                titulo = chave.replace('_', ' ').replace('alimentacao', 'Alimentação').replace('hidratacao', 'Hidratação').replace('rotina', 'Rotina').replace('exercicio', 'Exercício').replace('higiene', 'Higiene').replace('posicional', 'Posição').replace('estilo_de_vida', 'Estilo de Vida').replace('conduta_parceiro', 'Parceiro').replace('abstinencia', 'Abstinência').replace('retorno_72h', 'Retorno 72h').replace('reteste', 'Reteste').replace('importante', 'Importante').replace('familia', 'Família').replace('agua', 'Água')
                linhas += ['', f'[{titulo}]']
                for sublinha in valor.split('\n'):
                    sublinha = sublinha.strip()
                    if sublinha:
                        linhas.append(f'  {sublinha}')

    return '\n'.join(linhas)


# ------------------------------------------------------------------
# ORL — Sintoma-guia: Odinofagia (dor de garganta)
# ------------------------------------------------------------------

_LABEL_ORL = {
    'orl_emergencia_respiratoria':      '🔴 Obstrução Via Aérea — PS IMEDIATO',
    'orl_abscesso_periamigdaliano':     '🔴 Abscesso Periamigdaliano — PS Urgente',
    'orl_mononucleose':                 '🟡 Mononucleose Infecciosa (EBV) — SEM amoxicilina',
    'orl_faringoamigdalite_bacteriana': '🟢 Faringoamigdalite Bacteriana (GAS) — ATB',
    'orl_faringoamigdalite_test_treat': '🟡 Faringoamigdalite — TRA Centor 2',
    'orl_faringoamigdalite_viral':      '⚪ Faringoamigdalite Viral — Sintomático',
    'orl_disfonia_cronica':             '🟡 Disfonia ≥ 3 Semanas — Encaminhar ORL',
    # otalgia
    'orl_otite_media_aguda':            '🟢 Otite Média Aguda — Watchful / Amoxicilina',
    'orl_otite_externa':                '🟢 Otite Externa — Gotas Tópicas',
    'orl_otite_externa_maligna':        '🔴 Otite Externa Maligna — Internação Urgente',
    'orl_mastoidite':                   '🔴 Mastoidite Aguda — PS Urgente',
    'orl_dtm':                          '🟢 Disfunção Temporomandibular — Conservador',
    'orl_otalgia_inespecifica':         '⚪ Otalgia — Investigação',
    # rinossinusite
    'orl_rsab':                         '🟡 Rinossinusite Aguda Bacteriana — ATB 5–7d',
    'orl_ivas_viral':                   '⚪ IVAS Viral — Sintomático (sem ATB)',
    'orl_rinite_alergica':              '🟢 Rinite Alérgica — Anti-hist. + Corticoide Nasal',
    'orl_rsc':                          '🔵 Rinossinusite Crônica — Encaminhar ORL',
    'orl_rsc_polipose':                 '🔵 RSC com Polipose — Encaminhar ORL',
    'orl_polipose_nasal':               '🔵 Polipose Nasal — Encaminhar ORL',
    'orl_rinossinusite_intermediario':  '⚪ Rinossinusite — Observação Ativa 48–72h',
    'orl_rinossinusite_complicacao_orbital':  '🔴 Complicação Orbitária de RSA — PS Imediato',
    'orl_rinossinusite_complicacao_meningea': '🔴 Complicação Intracraniana de RSA — SAMU',
    # epistaxe (futuro)
    'orl_epistaxe_anterior':            '🟢 Epistaxe Anterior — Manejo Local',
    'orl_epistaxe_refrataria':          '🔴 Epistaxe Refratária — PS Urgente',
}

_ORL_CATS = frozenset(_LABEL_ORL.keys())


def _analise_odinofagia(resultado):
    """Impressão clínica em prosa para #Análise — Odinofagia / Dor de Garganta."""
    cat        = resultado.get('categoria', '')
    diag       = resultado.get('diagnostico', '')
    urgencia   = resultado.get('urgencia')
    raciocinio = resultado.get('raciocinio', '')
    achados    = resultado.get('achados', [])
    linhas     = []

    label = _LABEL_ORL.get(cat, diag)

    cab = label + '.'
    if urgencia == 'emergencia':
        cab += ' ENCAMINHAMENTO IMEDIATO.'
    elif urgencia == 'urgente':
        cab += ' Urgente.'
    linhas.append(cab)

    if raciocinio:
        linhas.append(raciocinio)

    if achados:
        linhas.append('Achados: ' + ' | '.join(achados[:6]) + '.')

    exames = resultado.get('exames', [])
    if exames:
        linhas.append('Solicitar: ' + ' | '.join(exames[:2]) + '.')

    return '\n'.join(linhas)


def _plano_odinofagia(resultado):
    """Texto para #Plano + #Orientações — Odinofagia."""
    cat      = resultado.get('categoria', '')
    diag     = resultado.get('diagnostico', '')
    urgencia = resultado.get('urgencia')
    linhas   = [f'ORL — {_LABEL_ORL.get(cat, diag)}']

    # Emergência
    if urgencia == 'emergencia':
        linhas += ['', '⚠️  ENCAMINHAMENTO IMEDIATO — PA/PS']
        for c in resultado.get('conduta', []):
            linhas.append(f'• {c}')
        return '\n'.join(linhas)

    # Encaminhamento urgente
    enc = resultado.get('encaminhar')
    if enc and urgencia == 'urgente':
        linhas += ['', f'→ {enc}']

    # Exames
    exames = resultado.get('exames', [])
    if exames:
        linhas += ['', 'Solicito:']
        for e in exames:
            linhas.append(f'  • {e}')

    # Conduta não farmacológica
    conduta = resultado.get('conduta', [])
    if conduta:
        linhas += ['', 'Oriento:']
        for c in conduta:
            linhas.append(f'  • {c}')

    # Prescrições estruturadas
    prescricoes = resultado.get('prescricoes_estruturadas', [])
    if prescricoes:
        linhas += ['']
        for med in prescricoes:
            lb = med.get('linha', '')
            if lb:
                linhas.append(f'[{lb}]')
            linhas += _rx(med)
            linhas.append('')

    # Encaminhamento eletivo
    if enc and urgencia not in ('emergencia', 'urgente'):
        linhas += [f'Encaminhamento eletivo: {enc}']

    # Retorno
    retorno = resultado.get('retorno', '')
    if retorno:
        linhas += ['', retorno]

    # #Orientações ao Paciente
    orientacoes = resultado.get('orientacoes', {})
    _titulo_map = {
        'alivio_garganta':    'Alívio da Garganta',
        'hidratacao':         'Hidratação',
        'atb_compliance':     'Antibiótico — Use até o Fim',
        'transmissao':        'Transmissão',
        'repouso':            'Repouso',
        'alimentacao':        'Alimentação',
        'retorno_medico':     'Retorno Médico',
    }
    if orientacoes:
        linhas += ['', '#Orientações ao Paciente:']
        for chave, valor in orientacoes.items():
            if chave == 'sinais_de_alerta':
                linhas += ['', 'Retornar imediatamente se:']
                for s in valor:
                    linhas.append(f'  ⚠️  {s}')
            elif isinstance(valor, str) and valor.strip():
                titulo = _titulo_map.get(chave, chave.replace('_', ' ').title())
                linhas += ['', f'[{titulo}]']
                for sub in valor.split('\n'):
                    sub = sub.strip()
                    if sub:
                        linhas.append(f'  {sub}')

    return '\n'.join(linhas)


# ------------------------------------------------------------------
# OTALGIA — #Plano  (subtipo 'otalgia' roteia aqui)
# ------------------------------------------------------------------

_OTALGIA_CATS = frozenset({
    'orl_mastoidite', 'orl_otite_externa_maligna', 'orl_otite_externa',
    'orl_otite_media_aguda', 'orl_dtm', 'orl_otalgia_inespecifica',
})

_OTALGIA_TITULO_MAP = {
    'ouvido_seco':        'Ouvido Seco — Regra n°1',
    'cotonete_proibido':  'Cotonete Proibido',
    'gotas':              'Como Aplicar as Gotas',
    'dor_e_febre':        'Dor e Febre',
    'atb_compliance':     'Antibiótico — Tome até o Fim',
    'watchful_waiting':   'Observação em Casa (Watchful Waiting)',
    'dieta_mole':         'Dieta Mole',
    'calor_local':        'Calor Local',
    'bruxismo':           'Bruxismo — Range os Dentes',
    'postura':            'Postura',
}


def _plano_oma_ww(resultado):
    """
    Renderer especial para OMA em Watchful Waiting.
    Separa visualmente a analgesia (usar agora) da receita de resgate ATB
    com trava de segurança em negrito/linha dupla — evita retorno ao PS
    apenas para carimbar o antibiótico.
    """
    cat  = resultado.get('categoria', '')
    diag = resultado.get('diagnostico', '')
    linhas = [f'ORL — {_LABEL_ORL.get(cat, diag)}']
    linhas += ['', '→ Observação ativa 48–72h sem ATB (critério AAP 2023: ≥2a, unilateral, não grave)']

    conduta = resultado.get('conduta', [])
    if conduta:
        linhas += ['', 'Oriento:']
        for c in conduta:
            linhas.append(f'  • {c}')

    # Separar prescrições em "usar agora" e "resgate" (ATB condicional)
    todas_rx   = resultado.get('prescricoes_estruturadas', [])
    rx_agora   = [p for p in todas_rx if 'RESGATE' not in p.get('linha', '').upper()]
    rx_resgate = [p for p in todas_rx if 'RESGATE' in p.get('linha', '').upper()]

    if rx_agora:
        linhas += ['', '[PRESCRIÇÃO — USAR AGORA]']
        for med in rx_agora:
            lb = med.get('linha', '')
            if lb:
                linhas.append(f'[{lb}]')
            linhas += _rx(med)
            linhas.append('')

    if rx_resgate:
        sep = '─' * 56
        linhas += [
            '',
            sep,
            '  ⚠️  RECEITA DE SEGURANÇA — NÃO AVIAR AGORA',
            '  Entregar ao responsável. Aviar e usar SOMENTE se,',
            '  após 48–72h de observação, a criança apresentar:',
            '    • Dor no ouvido que persiste ou piora',
            '    • Febre que aparece ou não cede',
            '    • Choro inconsolável / irritabilidade intensa',
            sep,
        ]
        for med in rx_resgate:
            # Remover prefixo "Prescrição de RESGATE — " do label
            lb = med.get('linha', '').replace('Prescrição de RESGATE — ', '').strip()
            if lb:
                linhas.append(f'[{lb}]')
            linhas += _rx(med)
            linhas.append('')

    enc = resultado.get('encaminhar')
    if enc:
        linhas += ['', f'Encaminhamento eletivo: {enc}']

    retorno = resultado.get('retorno', '')
    if retorno:
        linhas += ['', retorno]

    orientacoes = resultado.get('orientacoes', {})
    if orientacoes:
        linhas += ['', '#Orientações ao Paciente:']
        for chave, valor in orientacoes.items():
            if chave == 'sinais_de_alerta':
                linhas += ['', 'Retornar imediatamente se:']
                for s in valor:
                    linhas.append(f'  ⚠️  {s}')
            elif isinstance(valor, str) and valor.strip():
                titulo = _OTALGIA_TITULO_MAP.get(chave, chave.replace('_', ' ').title())
                linhas += ['', f'[{titulo}]']
                for sub in valor.split('\n'):
                    sub = sub.strip()
                    if sub:
                        linhas.append(f'  {sub}')

    return '\n'.join(linhas)


def _plano_otalgia(resultado):
    """
    Dispatcher de #Plano para otalgia.
    OMA + watchful_waiting → renderer com trava de segurança visível.
    Demais categorias → renderer ORL genérico (_plano_odinofagia).
    """
    if (resultado.get('categoria') == 'orl_otite_media_aguda'
            and resultado.get('watchful_waiting')):
        return _plano_oma_ww(resultado)
    # Fallback: renderer genérico (mastoidite, OE, DTM, inespecífica…)
    return _plano_odinofagia(resultado)


# ------------------------------------------------------------------
# OFTALMO — #Plano  (subtipo 'olho_vermelho' roteia aqui)
# ------------------------------------------------------------------

_LABEL_OFTALMO = {
    'oft_trauma_ocular':              '🔴 Trauma Ocular — PS Imediato',
    'oft_glaucoma_agudo':             '🔴 Glaucoma Agudo de Ângulo Fechado — PS Imediato',
    'oft_endoftalmite':               '🔴 Endoftalmite Pós-Operatória — Oftalmo Emergência',
    'oft_ulcera_cornea':              '🔴 Úlcera de Córnea (Lente de Contato) — Oftalmo Urgente',
    'oft_uveite_glaucoma_suspeito':   '🔴 Ciliary Flush — Uveíte/Glaucoma Suspeito — Oftalmo Urgente',
    'oft_celulite_orbitaria':         '🔴 Celulite Orbitária — PS Urgente',
    'oft_celulite_preseptal':         '🟡 Celulite Pré-Septal — ATB Oral + Retorno 24–48h',
    'oft_hordeoleo':                  '🟢 Hordéolo (Orzolho) — Compressa Morna + Tobramicina',
    'oft_hemorragia_subconj':         '⚪ Hemorragia Subconjuntival — Evolução Espontânea',
    'oft_conjuntivite_bacteriana':    '🟢 Conjuntivite Bacteriana — Tobramicina 0,3% × 7d',
    'oft_conjuntivite_viral':         '🟡 Conjuntivite Viral (Adenovírus) — Isolamento Obrigatório',
    'oft_conjuntivite_alergica':      '🟢 Conjuntivite Alérgica — Cetotifeno 0,025%',
    'oft_olho_vermelho_inespecifico': '⚪ Olho Vermelho Inespecífico — Oftalmo Eletivo',
}

_OFT_CATS = frozenset(_LABEL_OFTALMO.keys())

_OFT_TITULO_MAP = {
    'lente_de_contato':     'Lente de Contato',
    'higiene_ocular':       'Higiene Ocular',
    'contagio':             'Contagiosidade',
    'isolamento_e_higiene': 'Isolamento e Higiene',
    'objetos_pessoais':     'Objetos Pessoais — Não Compartilhar',
    'superficies':          'Superfícies — Hipoclorito (não álcool)',
    'atestado':             'Afastamento / Atestado',
    'controle_de_alergenos':'Controle de Alérgenos',
    'tecnica_colírio':      'Técnica de Aplicação do Colírio',
    'compressa_morna':      'Compressa Morna — Técnica',
    'higiene':              'Higiene',
    'tranquilizacao':       'Tranquilização',
    'vigilancia':           'Vigilância',
}


def _analise_oftalmo(resultado):
    """Impressão clínica em prosa para #Análise — Olho Vermelho."""
    cat        = resultado.get('categoria', '')
    diag       = resultado.get('diagnostico', '')
    urgencia   = resultado.get('urgencia')
    raciocinio = resultado.get('raciocinio', '')
    achados    = resultado.get('achados', [])
    linhas     = []

    label = _LABEL_OFTALMO.get(cat, diag)
    cab = label + '.'
    if urgencia == 'emergencia':
        cab += ' ENCAMINHAMENTO IMEDIATO.'
    elif urgencia == 'urgente':
        cab += ' Urgente — Oftalmologia.'
    linhas.append(cab)

    if raciocinio:
        linhas.append(raciocinio)

    if achados:
        linhas.append('Achados: ' + ' | '.join(achados[:6]) + '.')

    exames = resultado.get('exames', [])
    if exames:
        linhas.append('Solicitar: ' + ' | '.join(exames[:2]) + '.')

    return '\n'.join(linhas)


def _plano_olho_vermelho(resultado):
    """Texto para #Plano + #Orientações — Olho Vermelho / Oftalmo."""
    cat      = resultado.get('categoria', '')
    diag     = resultado.get('diagnostico', '')
    urgencia = resultado.get('urgencia')
    linhas   = [f'Oftalmo — {_LABEL_OFTALMO.get(cat, diag)}']

    # ── Emergência: bloco de alerta máximo ───────────────────────────────────
    if urgencia == 'emergencia':
        linhas += ['', '⚠️  ENCAMINHAMENTO IMEDIATO — PS / Oftalmologia emergência']
        for c in resultado.get('conduta', []):
            linhas.append(f'• {c}')
        enc = resultado.get('encaminhar')
        if enc:
            linhas += ['', f'→ {enc}']
        return '\n'.join(linhas)

    # ── Urgente: encaminhar em destaque ──────────────────────────────────────
    enc = resultado.get('encaminhar')
    if enc and urgencia == 'urgente':
        linhas += ['', f'→ {enc}']
        for c in resultado.get('conduta', []):
            linhas.append(f'• {c}')

    # ── Exames ───────────────────────────────────────────────────────────────
    exames = resultado.get('exames', [])
    if exames:
        linhas += ['', 'Solicito:']
        for e in exames:
            linhas.append(f'  • {e}')

    # ── Conduta não-farmacológica (urgente já foi mostrada acima) ────────────
    conduta = resultado.get('conduta', [])
    if conduta and urgencia != 'urgente':
        linhas += ['', 'Oriento:']
        for c in conduta:
            linhas.append(f'  • {c}')

    # ── Prescrições estruturadas ─────────────────────────────────────────────
    prescricoes = resultado.get('prescricoes_estruturadas', [])
    if prescricoes:
        linhas += ['']
        for med in prescricoes:
            lb = med.get('linha', '')
            if lb:
                linhas.append(f'[{lb}]')
            linhas += _rx(med)
            linhas.append('')

    # ── Atestado / afastamento ───────────────────────────────────────────────
    dias = resultado.get('dias_atestado')
    if dias:
        linhas += [f'Atestado: {dias} dias.']

    # ── Encaminhamento eletivo ───────────────────────────────────────────────
    if enc and urgencia not in ('emergencia', 'urgente'):
        linhas += ['', f'Encaminhamento eletivo: {enc}']

    # ── Retorno ──────────────────────────────────────────────────────────────
    retorno = resultado.get('retorno', '')
    if retorno:
        linhas += ['', retorno]

    # ── #Orientações ao Paciente ─────────────────────────────────────────────
    orientacoes = resultado.get('orientacoes', {})
    if not orientacoes:
        return '\n'.join(linhas)

    linhas += ['', '#Orientações ao Paciente:']

    # Conjuntivite viral → bloco de isolamento com separador visual
    if cat == 'oft_conjuntivite_viral' and (
            'isolamento_e_higiene' in orientacoes or 'superficies' in orientacoes):
        sep = '─' * 56
        linhas += [
            '',
            sep,
            '  ⚠️  ALERTA DE ISOLAMENTO — ADENOVÍRUS',
            '  O adenovírus sobrevive até 2 semanas em superfícies.',
            '  Álcool 70% NÃO elimina o adenovírus.',
            '  Usar hipoclorito 0,1% ou quaternário de amônio.',
            sep,
        ]

    for chave, valor in orientacoes.items():
        if chave == 'sinais_de_alerta':
            linhas += ['', 'Retornar imediatamente se:']
            for s in valor:
                linhas.append(f'  ⚠️  {s}')
        elif isinstance(valor, str) and valor.strip():
            titulo = _OFT_TITULO_MAP.get(chave, chave.replace('_', ' ').title())
            linhas += ['', f'[{titulo}]']
            for sub in valor.split('\n'):
                sub = sub.strip()
                if sub:
                    linhas.append(f'  {sub}')

    return '\n'.join(linhas)


# ------------------------------------------------------------------
# PALPITAÇÃO — #Análise e #Plano
# ------------------------------------------------------------------

_LABEL_PALPITACAO = {
    'pal_instabilidade_hemodinamica': '🔴 Instabilidade Hemodinâmica — SAMU/PS Imediato',
    'pal_wpw':                        '🔴 WPW (Pré-Excitação) — PS Urgente',
    'pal_tv_qrs_largo':               '🔴 Taquicardia QRS Largo — TV Suspeita — PS Imediato',
    'pal_brugada_sincope':            '🔴 Brugada + Síncope — PS / Eletrofisiologia Urgente',
    'pal_qt_longo_sincope':           '🔴 QT Longo + Síncope — Torsades Suspeita — PS Imediato',
    'pal_sincope_arritmia':           '🟠 Síncope + Palpitação — Investigação Urgente',
    'pal_flutter':                    '🟠 Flutter Atrial — Cardiologia Urgente',
    'pal_fa_nova_cardioversao':       '🟡 FA Nova < 48h — Cardioversão Química (Propafenona)',
    'pal_fa_nova_controle_fc':        '🟡 FA — Controle de FC + Anticoagulação',
    'pal_fa_cronica':                 '🟢 FA Crônica — Metoprolol + DOAC',
    'pal_tsv_paroxistica':            '🟢 TSV Paroxística — Valsalva + Metoprolol',
    'pal_extrassistolia':             '⚪ Extrassistolia — Holter Eletivo',
    'pal_hipertireoidismo':           '🟡 Palpitação por Hipertireoidismo — TSH + Propranolol',
    'pal_anemia':                     '🟡 Palpitação por Anemia — Hemograma + Causa',
    'pal_ansiedade_panico':           '🟢 Transtorno do Pânico — ISRS + TCC',
    'pal_farmaco_estimulante':        '🟡 Palpitação por Fármaco/Estimulante',
    'pal_inespecifico':               '⚪ Palpitação Inespecífica — Holter 24h',
}

_PAL_CATS = frozenset(_LABEL_PALPITACAO.keys())


def _analise_palpitacao(resultado):
    """Impressão clínica em prosa para #Análise — Palpitação."""
    cat        = resultado.get('categoria', '')
    diag       = resultado.get('diagnostico', '')
    urgencia   = resultado.get('urgencia', '')
    raciocinio = resultado.get('raciocinio', '')
    achados    = resultado.get('achados', [])
    linhas     = []

    label = _LABEL_PALPITACAO.get(cat, diag)
    cab   = label + '.'
    if urgencia == 'emergencia':
        cab += ' ENCAMINHAMENTO IMEDIATO — SAMU/PS.'
    elif urgencia == 'urgente':
        cab += ' Avaliação urgente — Cardiologia ou PS.'
    linhas.append(cab)

    if raciocinio:
        linhas.append(raciocinio)

    if achados:
        linhas.append('Achados: ' + ' | '.join(achados[:6]) + '.')

    rf = [r for r in resultado.get('red_flags', []) if r]
    if rf:
        linhas.append('Atenção: ' + ' | '.join(rf[:3]) + '.')

    exames = resultado.get('exames', [])
    if exames:
        linhas.append('Solicitar: ' + ' | '.join(exames[:3]) + '.')

    score = resultado.get('cha2ds2_score')
    if score is not None:
        sexo_f = resultado.get('sexo_feminino', False)
        limiar = 3 if sexo_f else 2
        anticoag = 'indicada' if score >= limiar else 'não indicada de rotina'
        linhas.append(f'CHA₂DS₂-VASc = {score} → anticoagulação {anticoag}.')

    return '\n'.join(linhas)


def _plano_palpitacao(resultado):
    """Texto para #Plano + #Orientações — Palpitação."""
    cat      = resultado.get('categoria', '')
    diag     = resultado.get('diagnostico', '')
    urgencia = resultado.get('urgencia', '')
    linhas   = [f'Palpitação — {_LABEL_PALPITACAO.get(cat, diag)}']

    # ── Alertas de segurança — sempre no topo ─────────────────────────────────
    for alerta in resultado.get('alertas_seguranca', []):
        linhas.append(alerta)

    # ── Emergência ────────────────────────────────────────────────────────────
    if urgencia == 'emergencia':
        linhas += ['', '⚠️  ENCAMINHAMENTO IMEDIATO — SAMU 192 / PS']
        rf = [r for r in resultado.get('red_flags', []) if r]
        for r in rf:
            linhas.append(f'⚠️  {r}')
        for c in resultado.get('conduta', []):
            linhas.append(f'• {c}')
        enc = resultado.get('encaminhar')
        if enc:
            linhas += ['', f'→ {enc}']
        return '\n'.join(linhas)

    # ── Encaminhar urgente ────────────────────────────────────────────────────
    enc = resultado.get('encaminhar')
    if enc and urgencia == 'urgente':
        linhas += ['', f'→ {enc}']

    # ── Red flags (não emergência) ────────────────────────────────────────────
    rf = [r for r in resultado.get('red_flags', []) if r]
    if rf:
        for r in rf:
            linhas.append(f'⚠️  {r}')

    # ── Exames ────────────────────────────────────────────────────────────────
    exames = resultado.get('exames', [])
    if exames:
        linhas += ['', 'Solicito:']
        for e in exames:
            linhas.append(f'  • {e}')

    # ── Conduta ───────────────────────────────────────────────────────────────
    conduta = [c for c in resultado.get('conduta', []) if c]
    if conduta:
        linhas += ['', 'Oriento/Conduzo:']
        for c in conduta:
            linhas.append(f'  • {c}')

    # ── Prescrições estruturadas ──────────────────────────────────────────────
    prescricoes = resultado.get('prescricoes_estruturadas', [])
    if prescricoes:
        linhas += ['']
        for med in prescricoes:
            lb = med.get('linha', '')
            if lb:
                linhas.append(f'[{lb}]')
            linhas += _rx(med)
            linhas.append('')

    # ── Atestado ──────────────────────────────────────────────────────────────
    dias = resultado.get('dias_atestado')
    if dias:
        linhas += [f'Atestado: {dias} dia(s).']

    # ── Encaminhamento eletivo ────────────────────────────────────────────────
    if enc and urgencia not in ('emergencia', 'urgente'):
        linhas += ['', f'Encaminhamento: {enc}']

    # ── Retorno ───────────────────────────────────────────────────────────────
    retorno = resultado.get('retorno', '')
    if retorno:
        linhas += ['', f'Retorno: {retorno}']

    # ── #Orientações ao Paciente ──────────────────────────────────────────────
    orientacoes = resultado.get('orientacoes', {})
    if not orientacoes:
        return '\n'.join(linhas)

    linhas += ['', '#Orientações ao Paciente:']

    # WPW → alerta de medicamentos proibidos em destaque
    if cat == 'pal_wpw':
        sep = '─' * 56
        linhas += [
            '',
            sep,
            '  ⚠️  ALERTA WPW — MEDICAMENTOS PROIBIDOS',
            '  NUNCA use: Verapamil, Diltiazem, Digoxina.',
            '  Esses remédios podem causar fibrilação ventricular letal.',
            '  Informe sempre qualquer médico/PS sobre o WPW.',
            sep,
        ]

    for chave, valor in orientacoes.items():
        if isinstance(valor, str) and valor.strip():
            titulo = chave.replace('_', ' ').title()
            linhas += ['', f'[{titulo}]']
            for sub in valor.split('\n'):
                sub = sub.strip()
                if sub:
                    linhas.append(f'  {sub}')

    return '\n'.join(linhas)


# ------------------------------------------------------------------
# VERTIGEM — #Plano
# ------------------------------------------------------------------

_LABEL_VERTIGEM_PLANO = {
    'bppv':                             'VPPB — Canal Posterior',
    'bppv_canal_horizontal':            'VPPB — Canal Horizontal',
    'sindrome_vestibular_aguda':        'Síndrome Vestibular Aguda',
    'presincope':                       'Pré-Síncope',
    'presincope_ortostatica':           'Pré-Síncope Ortostática',
    'provavel_meniere':                 'Provável Doença de Ménière',
    'possivel_migranea_vestibular':     'Enxaqueca Vestibular Provável',
    'episodica_espontanea_indefinida':  'Vertigem Episódica — Investigar Causa',
    'possivel_central':                 'Possível Causa Central — Encaminhar Urgente',
    'indefinido':                       'Fenomenologia Indefinida — Ampliar Avaliação',
}

_ENC_KW = ('encaminhar', 'Encaminhar', 'Neurologista', 'neurologista',
           'otoneurologia', 'PS/', 'PS urgente', 'emergencia', 'emergência')


def _plano_vertigem(resultado):
    """Texto para #Plano — Vertigem."""
    diag    = resultado.get('diagnostico', '')
    conduta = resultado.get('conduta', [])
    linhas  = [f'Vertigem — {_LABEL_VERTIGEM_PLANO.get(diag, diag.replace("_", " ").title())}']

    for item in conduta:
        if item.startswith('──'):
            linhas += ['', item]
        elif item.startswith('  '):
            linhas.append(item)            # sub-etapas das manobras — manter indentação
        elif any(k in item for k in _ENC_KW):
            linhas.append(f'→ {item}')
        else:
            linhas.append(f'• {item}')

    if resultado.get('necessita_exame'):
        linhas += ['', '(Exames indicados — ver #Análise)']

    return '\n'.join(linhas)


# ------------------------------------------------------------------
# TOSSE — #Plano
# ------------------------------------------------------------------

_LABEL_TOSSE_PLANO = {
    'tosse_pcp_suspeita':            'PCP — Urgência (PS imediato)',
    'tosse_aguda_viral':             'Tosse Aguda Viral',
    'tosse_aguda_bacteriana':        'Pneumonia Bacteriana',
    'tosse_pertussis_suspeita':      'Coqueluche — Suspeita',
    'tosse_subaguda_pos_infecciosa': 'Tosse Subaguda Pós-Infecciosa',
    'tosse_ieca':                    'Tosse por IECA',
    'tosse_uacs':                    'UACS / Gotejamento Pós-Nasal',
    'tosse_asma_variante':           'Asma / Tosse Variante de Asma',
    'tosse_drge_lpr':                'DRGE / LPR',
    'tosse_tb_suspeita':             'TB Pulmonar — Suspeita',
    'tosse_pneumonia_atipica':       'Pneumonia Atípica',
    'tosse_neoplasia_suspeita':      'Suspeita de Neoplasia Pulmonar',
    'investigar_tosse_cronica':      'Tosse Crônica — Investigação Sequencial',
}


def _plano_tosse(resultado):
    """Texto para #Plano — Tosse."""
    categoria = resultado.get('categoria', '')
    linhas    = [f'Tosse — {_LABEL_TOSSE_PLANO.get(categoria, categoria)}']

    # ── Alertas de segurança (Beers idoso etc.) — sempre no topo ─────────────
    for alerta in resultado.get('alertas_seguranca', []):
        linhas.append(alerta)

    # ── Aguda / subaguda / PCP — resultado plano com 'conduta' ───────────────
    conduta = resultado.get('conduta')
    if conduta:
        linhas.append('')
        for item in conduta:
            if any(k in item for k in _ENC_KW) or item.startswith('PS'):
                linhas.append(f'→ {item}')
            else:
                linhas.append(f'• {item}')
        enc = resultado.get('encaminhar')
        if enc:
            linhas += ['', f'→ Encaminhar: {enc}']
        return '\n'.join(linhas)

    # ── Crônica — hipoteses com conduta_nao_farmacologica + farmacologico ────
    for h in resultado.get('hipoteses_provaveis', []):
        linhas += ['', f'[{h.get("hipotese", "")}]']
        for item in h.get('conduta_nao_farmacologica', []):
            linhas.append(f'• {item}')
        farm = h.get('farmacologico', [])
        if farm:
            linhas += ['', 'Prescrevo / trato:']
            for item in farm:
                linhas.append(f'  {item}')
        enc = h.get('encaminhar')
        if enc:
            linhas.append(f'→ Encaminhar: {enc}')

    # ── investigar_tosse_cronica — mensagem guia Irwin ────────────────────────
    msg = resultado.get('mensagem')
    if msg:
        linhas += ['', msg]

    return '\n'.join(linhas)


# ------------------------------------------------------------------
# DIARREIA — #Plano
# ------------------------------------------------------------------

def _plano_diarreia(resultado):
    """Texto para #Plano — Diarreia."""
    categoria = resultado.get('categoria', '')
    label     = _LABEL_DIARREIA.get(categoria, categoria)
    linhas    = [f'Diarreia — {label}']

    # Alertas de segurança primeiro
    if resultado.get('internacao'):
        linhas += ['', '⚠️  INTERNAÇÃO indicada.']
    if resultado.get('atb_contraindicado'):
        linhas.append('⚠️  ANTIBIÓTICO CONTRAINDICADO — risco de SHU.')
    if resultado.get('loperamida_contraindicada'):
        linhas.append('⚠️  LOPERAMIDA CONTRAINDICADA — risco de megacólon tóxico.')
    if resultado.get('notificar_vigilancia'):
        linhas.append('⚠️  Notificar Vigilância Epidemiológica — SINAN.')

    conduta = resultado.get('conduta', [])
    if conduta:
        linhas.append('')
        for item in conduta:
            linhas.append(f'• {item}')

    exames = resultado.get('exames', [])
    if exames:
        linhas += ['', 'Solicitar:']
        for e in exames:
            linhas.append(f'  • {e}')

    enc = resultado.get('encaminhar')
    if enc:
        linhas += ['', f'→ Encaminhar: {enc}']

    retorno = resultado.get('retorno')
    if retorno:
        linhas += ['', retorno]

    return '\n'.join(linhas)


# ------------------------------------------------------------------
# ARBOVIROSES — #Plano
# ------------------------------------------------------------------

def _plano_arboviroses(resultado):
    """Texto para #Plano — Arboviroses (Dengue / Chikungunya / Zika)."""
    categoria = resultado.get('categoria', '')
    label     = _LABEL_ARBOVIROSES.get(categoria, categoria)
    linhas    = [f'Arbovirose — {label}']

    if resultado.get('internacao'):
        uti = resultado.get('uti', False)
        linhas += ['', f'⚠️  {"INTERNAÇÃO EM UTI" if uti else "INTERNAÇÃO"} indicada — encaminhar PS.']

    if resultado.get('aine_contraindicado'):
        msg = resultado.get('aine_msg', 'AINE CONTRAINDICADO')
        linhas += ['', f'⚠️  {msg}']

    conduta = resultado.get('conduta', [])
    if conduta:
        linhas.append('')
        for item in conduta:
            linhas.append(f'• {item}')

    exames = resultado.get('exames', [])
    if exames:
        linhas += ['', 'Solicitar:']
        for e in exames:
            linhas.append(f'  • {e}')

    sinais = resultado.get('sinais_retorno', [])
    if sinais:
        linhas += ['', 'Sinais de retorno imediato:']
        for s in sinais:
            linhas.append(f'  ⚠️  {s}')

    return '\n'.join(linhas)


# ------------------------------------------------------------------
# FEBRE SEM FOCO — #Análise + #Plano
# ------------------------------------------------------------------

_FEBRE_CATS = frozenset({
    'febre_emergencia', 'febre_com_foco',
    'febre_aguda_viral', 'febre_aguda_investigar',
    'febre_prolongada', 'febre_fuo',
})


def _analise_febre(resultado: dict) -> str:
    """Texto para #Análise — Febre sem Foco."""
    cat  = resultado.get('categoria', '')
    dias = resultado.get('dias', 1)
    temp = resultado.get('temperatura', 38.0)

    if cat == 'febre_emergencia':
        flags = resultado.get('red_flags', [])
        achados = '; '.join(f['achado'] for f in flags)
        return f'Febre com red flag(s) — encaminhamento emergencial. Achados: {achados}.'

    if cat == 'febre_com_foco':
        foco = resultado.get('foco', {})
        return (f'Febre com foco localizatório identificado — {foco.get("descricao", "")}. '
                f'Temperatura {temp}°C há {dias} dia(s). '
                f'Conduzir pelo módulo de {foco.get("modulo", "módulo específico")}.')

    if cat == 'febre_aguda_viral':
        return (f'Febre aguda ({dias} dia(s), {temp}°C) sem foco localizatório e sem sinais de alarme. '
                f'Síndrome viral autolimitada — manejo sintomático.')

    if cat == 'febre_aguda_investigar':
        fatores = resultado.get('fatores_atencao', [])
        fat_str = '; '.join(fatores[:3])
        return (f'Febre aguda ({dias} dia(s), {temp}°C) sem foco definido, com fator(es) de atenção: {fat_str}. '
                f'Investigação laboratorial indicada antes de conduta expectante.')

    if cat == 'febre_prolongada':
        epi = resultado.get('contexto_epi', [])
        epi_str = ' | '.join(epi) if epi else 'sem contexto epidemiológico específico'
        return (f'Febre prolongada ({dias} dia(s), {temp}°C) sem foco identificado. '
                f'Contexto: {epi_str}. Investigação escalonada indicada.')

    if cat == 'febre_fuo':
        return (f'Febre de Origem Obscura (FUO) — {dias} dia(s), {temp}°C. '
                f'Temperatura ≥ 38,3°C documentada por ≥ 3 semanas sem diagnóstico após workup básico. '
                f'Causas: infecção (35%), neoplasia (20%), doença inflamatória (15%), miscelânea/idiopática (30%). '
                f'Encaminhar Clínica Médica / Infectologia.')

    return ''


def _plano_febre(resultado: dict) -> str:
    """Texto para #Plano — Febre sem Foco (6 categorias)."""
    cat  = resultado.get('categoria', '')
    dias = resultado.get('dias', 1)
    temp = resultado.get('temperatura', 38.0)
    linhas = []

    for alerta in resultado.get('alertas_seguranca', []):
        linhas.append(alerta)
    if resultado.get('alertas_seguranca'):
        linhas.append('')

    # ── EMERGÊNCIA ──────────────────────────────────────────────────
    if cat == 'febre_emergencia':
        flags = resultado.get('red_flags', [])
        linhas.append('🔴 EMERGÊNCIA — Encaminhar PS Imediato')
        linhas.append('')
        for f in flags:
            linhas.append(f'• {f["achado"]}')
            linhas.append(f'  → {f["acao"]}')
        linhas.append('')
        linhas.append('⚠️  NÃO adiar transporte. Ligar 192 (SAMU) se instável hemodinamicamente.')
        return '\n'.join(linhas)

    # ── FOCO IDENTIFICADO — REDIRECIONAR ────────────────────────────
    if cat == 'febre_com_foco':
        foco = resultado.get('foco', {})
        modulo = foco.get('modulo', '')
        keyword = foco.get('keyword_entrada', '')
        linhas.append(f'Febre com Foco — {foco.get("descricao", "")}')
        linhas.append(f'Temperatura: {temp}°C há {dias} dia(s)')
        linhas.append('')
        if modulo:
            linhas.append(f'→ Conduzir pelo módulo: {modulo.upper()}')
            if keyword:
                linhas.append(f'  (iniciar consulta digitando: "{keyword}")')
        else:
            linhas.append('→ Investigar conforme achado clínico')
        linhas.append('')
        linhas.append('Sintomático enquanto aguarda consulta específica:')
        linhas.append('• Paracetamol 500–1000 mg 6/6h se necessário')
        linhas.append('• Hidratação oral: mínimo 2–3 L/dia')
        return '\n'.join(linhas)

    # ── FEBRE AGUDA VIRAL ────────────────────────────────────────────
    if cat == 'febre_aguda_viral':
        linhas.append(f'Febre Aguda Viral — Autolimitada ({dias} dia(s), {temp}°C)')
        linhas.append('')
        linhas.append('Tratamento sintomático:')
        linhas.append('• Paracetamol 500–1000 mg 6/6h VO se T > 38°C ou desconforto')
        linhas.append('  OU Ibuprofeno 400–600 mg 8/8h VO (preferir se mialgia intensa)')
        linhas.append('  ⚠️  Evitar AAS em adultos febris (síndrome de Reye em viroses)')
        linhas.append('• Hidratação oral: mínimo 2–3 L/dia (água, soro caseiro, isotônico)')
        linhas.append('• Repouso relativo — sem restrição absoluta de atividade')
        linhas.append('')
        linhas.append('Retornar SE:')
        linhas.append('• Febre persistir > 7 dias ou piorar após melhora inicial')
        linhas.append('• Surgir rash, petéquias, rigidez de nuca ou alt. de consciência')
        linhas.append('• Piora do estado geral ou dificuldade respiratória')
        linhas.append('• Temperatura ≥ 39,5°C não responsiva à medicação')
        return '\n'.join(linhas)

    # ── FEBRE AGUDA — INVESTIGAR ────────────────────────────────────
    if cat == 'febre_aguda_investigar':
        fatores = resultado.get('fatores_atencao', [])
        labs    = resultado.get('labs', {})
        linhas.append(f'Febre Aguda sem Foco — Investigação Indicada ({dias} dia(s), {temp}°C)')
        linhas.append('')
        linhas.append('Fator(es) de atenção:')
        for f in fatores:
            linhas.append(f'  • {f}')
        linhas.append('')
        linhas.append('Exames (se ainda não realizados):')
        linhas.append('• Hemograma completo + diferencial')
        linhas.append('• PCR e/ou VHS')
        linhas.append('• Urina rotina + urocultura')
        if temp >= 39.5 or any('calafrio' in f.lower() for f in fatores):
            linhas.append('• Hemoculturas × 2 (antes de iniciar ATB, em sítios diferentes)')
        linhas.append('• RX tórax (se tosse, dispneia ou dúvida de foco pulmonar)')
        if any('viagem' in f.lower() or 'carrapato' in f.lower() for f in fatores):
            linhas.append('• Sorologias epidemiológicas conforme destino/exposição')
        if labs:
            linhas.append('')
            linhas.append('Exames disponíveis:')
            if 'leucocitos' in labs:
                linhas.append(f'  Leucócitos: {labs["leucocitos"]:,.0f}/mm³')
            if 'pcr_mgL' in labs:
                linhas.append(f'  PCR: {labs["pcr_mgL"]} mg/L')
            if 'vhs' in labs:
                linhas.append(f'  VHS: {labs["vhs"]} mm/h')
        linhas.append('')
        linhas.append('Sintomático:')
        linhas.append('• Paracetamol 500–1000 mg 6/6h + hidratação oral 2–3 L/dia')
        linhas.append('• ATB APENAS se foco bacteriano definido — não empírico sem causa')
        linhas.append('')
        linhas.append('Retorno: 48–72h com resultados ou antes se piora.')
        return '\n'.join(linhas)

    # ── FEBRE PROLONGADA (7–21 dias) ────────────────────────────────
    if cat == 'febre_prolongada':
        epi  = resultado.get('contexto_epi', [])
        labs = resultado.get('labs', {})
        linhas.append(f'Febre Prolongada — Investigação Escalonada ({dias} dias, {temp}°C)')
        if epi:
            linhas.append('Contexto epidemiológico: ' + ' | '.join(epi))
        linhas.append('')
        linhas.append('Painel laboratorial 1ª fase:')
        linhas.append('• Hemograma + diferencial + reticulócitos')
        linhas.append('• PCR, VHS, LDH, DHL, bilirrubinas, ALT/AST')
        linhas.append('• Hemoculturas × 2 (intervaladas, preferencialmente sem ATB prévio)')
        linhas.append('• Urina rotina + urocultura')
        linhas.append('• RX tórax')
        linhas.append('• PPD/IGRA + BAAR × 2 (basal para TB)')
        linhas.append('')
        if 'viagem' in str(epi).lower():
            linhas.append('Sorologias epidemiológicas (viagem):')
            linhas.append('• Gota espessa / Antígeno HRP2 (malária)')
            linhas.append('• Sorologias: leptospirose, febre tifoide (Widal), ricketsiose')
            linhas.append('')
        linhas.append('Sorologias gerais:')
        linhas.append('• Monospot (EBV); HIV AgP24 + anticorpo; CMV IgM; Toxoplasmose IgM')
        linhas.append('• ANA, FR (triagem inflamatória)')
        linhas.append('')
        linhas.append('⚠️  Evitar ATB empírico sem foco definido (pode mascarar diagnóstico).')
        linhas.append('Retorno: 1 semana com resultados — reavaliar para FUO se persistir ≥ 21 dias.')
        return '\n'.join(linhas)

    # ── FUO — FEBRE DE ORIGEM OBSCURA ───────────────────────────────
    if cat == 'febre_fuo':
        epi  = resultado.get('contexto_epi', [])
        labs = resultado.get('labs', {})
        linhas.append(f'Febre de Origem Obscura (FUO) — {dias} dias, {temp}°C')
        linhas.append('Definição: T ≥ 38,3°C documentada, ≥ 3 semanas, sem diagnóstico após workup básico.')
        linhas.append('')
        linhas.append('Etiologia em adultos imunocompetentes:')
        linhas.append('  Infecção 35% | Neoplasia 20% | Inflamatória/autoimune 15% | Miscelânea 5% | Sem dx 25%')
        linhas.append('')
        linhas.append('Painel diagnóstico completo:')
        linhas.append('• Hemoculturas × 3 (intervaladas, preferencialmente sem ATB)')
        linhas.append('• TC tórax-abdome-pelve com contraste (lesão focal, linfadenopatia, esplenomegalia)')
        linhas.append('• Ecocardiograma transtorácico (endocardite subaguda)')
        linhas.append('• ANA, anti-dsDNA, ANCA, FR, anti-CCP (autoimune/vasculite)')
        linhas.append('• LDH, β2-microglobulina (linfoma/malignidade hematológica)')
        linhas.append('• Sorologias: HIV, EBV, CMV, Toxoplasma, Brucella, Leptospirose')
        linhas.append('• BAAR × 3 + cultura de escarro / PPD ou IGRA (TB)')
        if 'viagem' in str(epi).lower():
            linhas.append('• Gota espessa + sorologia para febre tifoide, ricketsiose, leishmaniose')
        linhas.append('• Biópsia de medula óssea se sem diagnóstico após TC + sorologias')
        linhas.append('• PET-CT se workup inicial negativo (excelente para linfoma e focos ocultos)')
        linhas.append('')
        linhas.append('⚠️  NÃO iniciar ATB ou corticoide empírico sem diagnóstico definido.')
        linhas.append('→ Encaminhar: Clínica Médica / Infectologia para investigação sistemática.')
        return '\n'.join(linhas)

    return ''


# ------------------------------------------------------------------
# ASMA — #Análise + #Plano
# ------------------------------------------------------------------

_ASMA_CATS = frozenset({
    'asma_emergencia', 'asma_crise_grave', 'asma_crise_leve_moderada',
    'asma_controlada', 'asma_parcialmente_ctrl', 'asma_nao_controlada',
})


def _analise_asma(resultado: dict) -> str:
    cat  = resultado.get('categoria', '')
    grav = resultado.get('gravidade', '')
    spo2 = resultado.get('spo2')
    pefr = resultado.get('pefr')

    if cat == 'asma_emergencia':
        return ('Crise asmática com risco de vida — UTI/PS imediato. '
                'Achados: tórax silencioso / sonolência / SpO₂ < 90%.')
    if cat == 'asma_crise_grave':
        spo2_str = f' SpO₂ {spo2}%.' if spo2 else ''
        pefr_str = f' PEFR {pefr}% do previsto.' if pefr else ''
        return (f'Crise asmática grave (GINA 2025).{spo2_str}{pefr_str} '
                f'Critérios: fala em palavras / FR > 30 / FC > 120 / SpO₂ 90–95%.')
    if cat == 'asma_crise_leve_moderada':
        spo2_str = f' SpO₂ {spo2}%.' if spo2 else ''
        return (f'Crise asmática leve-moderada (GINA 2025).{spo2_str} '
                f'Paciente fala em frases, sem critérios de gravidade.')

    # Rotina
    controle = resultado.get('controle', '')
    step     = resultado.get('step_atual', '?')
    criterios = resultado.get('criterios', [])
    _CTRL = {
        'controlada':           'Asma controlada',
        'parcialmente_controlada': 'Asma parcialmente controlada',
        'nao_controlada':       'Asma não controlada',
    }
    label    = _CTRL.get(controle, 'Asma')
    crit_str = ('; '.join(criterios) + '.') if criterios else 'Sem critérios de mau controle.'
    exac_str = ' Exacerbação no último ano.' if resultado.get('exacerbacao_ano') else ''
    return f'{label} — Step GINA {step}. {crit_str}{exac_str}'


def _plano_asma(resultado: dict) -> str:
    cat  = resultado.get('categoria', '')
    linhas = []

    if cat == 'asma_emergencia':
        linhas.append('⚠️  ASMA — RISCO DE VIDA → UTI/PS IMEDIATO')
        linhas.append('• Salbutamol 10 puffs via espaçador a cada 20 min (≡ ou superior à NEB; menos contaminação)')
        linhas.append('  — usar NEB contínua só se SpO₂ muito baixa / incapaz de coordenar o espaçador')
        linhas.append('• Ipratrópio 8 puffs associado ao SABA')
        linhas.append('• O₂ controlado: meta SpO₂ 93–95%')
        linhas.append('• Corticoide: Hidrocortisona 200 mg IV (incapaz de deglutir/falar em palavras)')
        linhas.append('• Sulfato de magnésio 2g IV em 20 min')
        linhas.append('• Preparar para intubação se necessário')
        return '\n'.join(linhas)

    if cat == 'asma_crise_grave':
        linhas.append('⚠️  Crise Asmática Grave — Borderline PS / APS')
        linhas.append('')
        linhas.append('Broncodilatador (espaçador ≡ ou superior à nebulização):')
        linhas.append('• Salbutamol 4–10 puffs via espaçador a cada 20 min × 3 doses na 1ª hora')
        linhas.append('• Ipratrópio 4–8 puffs (80–160 mcg) junto com SABA')
        linhas.append('• O₂ controlado: meta SpO₂ 93–95%')
        linhas.append('')
        linhas.append('Corticoide sistêmico — iniciar na 1ª hora:')
        linhas.append('• Prednisona/Prednisolona 40–50 mg VO × 5 dias (SEM desmame) — preferido OU')
        linhas.append('• Hidrocortisona 200 mg IV se incapaz de deglutir / fala em palavras')
        linhas.append('')
        linhas.append('Reavaliar em 1h — se sem melhora ou PEFR < 60%: PS imediato.')
        return '\n'.join(linhas)

    if cat == 'asma_crise_leve_moderada':
        linhas.append('Crise Asmática Leve-Moderada — Manejo APS (GINA 2025)')
        linhas.append('')
        linhas.append('Broncodilatador (espaçador ≡ ou superior à nebulização; menos contaminação):')
        linhas.append('• Salbutamol 4–10 puffs via espaçador (MDI + câmara expansora)')
        linhas.append('  Repetir a cada 20 min por até 3 doses na 1ª hora')
        linhas.append('• Ipratrópio 4–8 puffs se moderada (menos hospitalizações)')
        linhas.append('')
        linhas.append('Corticoide sistêmico (se não resposta completa ou moderada):')
        linhas.append('• Prednisona/Prednisolona 40–50 mg/dia VO × 5 dias (SEM necessidade de desmame)')
        linhas.append('• Via oral equivale à IV — não há vantagem de IV se tolerar VO')
        linhas.append('')
        linhas.append('Alta domiciliar se:')
        linhas.append('• PEFR/VEF1 60–80% do previsto + sintomas melhorados')
        linhas.append('• SpO₂ > 94% em ar ambiente + sem SABA por ≥ 3–4h')
        linhas.append('')
        linhas.append('Plano de ação escrito: zona verde / amarela / vermelha.')
        linhas.append('Retorno em 2–7 dias (pós-exacerbação).')
        return '\n'.join(linhas)

    # Rotina
    step_rec  = resultado.get('step_recomendado', 2)
    acao_step = resultado.get('acao_step', '')
    info      = resultado.get('info_step', {})
    controle  = resultado.get('controle', '')
    tecnica   = resultado.get('tecnica_ok', True)
    adesao    = resultado.get('adesao_ok', True)
    eosin     = resultado.get('eosinofilos')

    linhas.append(f'Asma — Controle Crônico (GINA 2025)')
    linhas.append('')
    linhas.append(f'Avaliação: {controle.replace("_"," ").title()}')
    linhas.append(f'{acao_step}')
    linhas.append('')
    linhas.append(f'Step {step_rec} — {info.get("label","")}:')
    linhas.append(f'Track 1 (preferido GINA): {info.get("track1","")}')
    linhas.append(f'Track 2 (alternativa):    {info.get("track2","")}')
    linhas.append(f'Dose de ICS: {info.get("ics_dose","")}')

    if not tecnica:
        linhas.append('')
        linhas.append('⚠️  Técnica inalatória INCORRETA — revisar antes de step-up')
        linhas.append('  (má técnica é causa frequente de controle insuficiente)')
    if not adesao:
        linhas.append('')
        linhas.append('⚠️  Adesão insuficiente — abordar barreiras antes de trocar medicação')
    if eosin and eosin >= 150:
        linhas.append(f'')
        linhas.append(f'Eosinófilos {eosin} cél/μL — asma eosinofílica confirmada.')
        if step_rec >= 5:
            linhas.append('  Candidato a biológico anti-IL5 (mepolizumab) — encaminhar pneumologia.')

    linhas.append('')
    linhas.append('Gatilhos / comorbidades:')
    linhas.append('• AINE/AAS → evitar (AERD); betabloqueador → evitar não-seletivo')
    linhas.append('• Rinite: corticoide intranasal melhora controle da asma')
    linhas.append('• DRGE: tratar PPIs se sintomático')
    linhas.append('')
    linhas.append('Vacinação:')
    linhas.append('• Influenza — anual')
    linhas.append('• Pneumococo — PCV20 ou PCV15 + PPSV23')
    return '\n'.join(linhas)


# ------------------------------------------------------------------
# DPOC — #Análise + #Plano
# ------------------------------------------------------------------

_DPOC_CATS = frozenset({
    'dpoc_emergencia', 'dpoc_exacerbacao_moderada', 'dpoc_exacerbacao_leve',
    'dpoc_grupo_a', 'dpoc_grupo_b', 'dpoc_grupo_e',
})


def _analise_dpoc(resultado: dict) -> str:
    cat  = resultado.get('categoria', '')
    spo2 = resultado.get('spo2')

    if cat == 'dpoc_emergencia':
        spo2_str = f' SpO₂ {spo2}%.' if spo2 else ''
        return (f'Exacerbação grave de DPOC — PS/UTI imediato.{spo2_str} '
                f'Critérios de gravidade presentes (alteração de consciência / insuficiência respiratória).')

    if cat == 'dpoc_exacerbacao_moderada':
        n = resultado.get('anthonisen', 0)
        crit = '; '.join(resultado.get('criterios', []))
        atb_str = 'ATB indicado (escarro purulento presente).' if resultado.get('atb') else 'ATB não indicado (sem purulência).'
        return (f'AECOPD moderada — {n}/3 critérios de Anthonisen ({crit}). {atb_str}')

    if cat == 'dpoc_exacerbacao_leve':
        return ('AECOPD leve — sem critérios completos de Anthonisen. '
                'Aumento de broncodilatador de resgate suficiente.')

    # Rotina
    grupo = resultado.get('grupo', '')
    grade = resultado.get('gold_grade')
    cat_s = resultado.get('cat_score')
    mmrc  = resultado.get('mmrc')
    exac  = resultado.get('exacerbacoes', 0)
    ics   = resultado.get('ics_just', '')
    grade_str = f' GOLD Grau {grade}.' if grade else ''
    cat_str   = f' CAT ~{cat_s}.' if cat_s is not None else ''
    mmrc_str  = f' mMRC {mmrc}.' if mmrc is not None else ''
    exac_str  = f' {exac} exacerbação(ões)/ano.' if exac is not None else ''
    ics_str   = f' {ics}' if ics else ''
    return (f'DPOC Grupo {grupo} (GOLD 2026).{grade_str}{cat_str}{mmrc_str}'
            f'{exac_str}{ics_str}')


def _plano_dpoc(resultado: dict) -> str:
    cat  = resultado.get('categoria', '')
    linhas = []

    # ── Alertas de segurança (alvo de O₂) — sempre no topo ───────────────────
    for alerta in resultado.get('alertas_seguranca', []):
        linhas.append(alerta)
    if resultado.get('alertas_seguranca'):
        linhas.append('')

    if cat == 'dpoc_emergencia':
        linhas.append('⚠️  AECOPD GRAVE — PS/UTI')
        linhas.append('• Salbutamol 4–8 puffs via espaçador + Ipratrópio (≡ ou superior à NEB)')
        linhas.append('• O₂ controlado: meta SpO₂ 88–92% (NÃO ultrapassar — risco de hipercapnia)')
        linhas.append('• Prednisona 40 mg/dia VO × 5 dias (Hidrocortisona IV só se não deglutir)')
        linhas.append('• ATB se purulência (Anthonisen)')
        linhas.append('• Avaliar VNI se pH < 7,35 ou PaCO₂ > 45 mmHg')
        return '\n'.join(linhas)

    if cat in ('dpoc_exacerbacao_moderada', 'dpoc_exacerbacao_leve'):
        atb  = resultado.get('atb', False)
        linhas.append(f'AECOPD {"Moderada" if cat == "dpoc_exacerbacao_moderada" else "Leve"} — Manejo APS (GOLD 2026)')
        linhas.append('')
        linhas.append('Broncodilatador — espaçador ≡ ou superior à nebulização:')
        linhas.append('• Salbutamol 4–8 puffs via espaçador a cada 4–6h (ou 2,5 mg NEB)')
        linhas.append('• Ipratrópio 4–8 puffs junto com salbutamol (combinação superior)')
        linhas.append('• O₂ controlado se hipoxemia: meta SpO₂ 88–92% (titular ao mínimo)')
        if cat == 'dpoc_exacerbacao_moderada':
            linhas.append('')
            linhas.append('Corticoide sistêmico:')
            linhas.append('• Prednisona 40 mg/dia VO × 5 dias (SEM desmame) — GOLD 2026')
            linhas.append('  (5 dias = eficácia igual a 10–15 dias, menos efeitos adversos)')
            linhas.append('')
            if atb:
                linhas.append('Antibiótico — escarro purulento (Anthonisen indicação):')
                linhas.append('• Amoxicilina-clavulanato 875/125 mg 12/12h × 5 dias (1ª linha)')
                linhas.append('• Alt.: doxiciclina 100 mg 12/12h OU azitromicina 500 mg/dia × 3 dias')
                linhas.append('• 2ª linha (exacerbações frequentes / resistência): levofloxacino 500 mg/dia')
            else:
                linhas.append('ATB não indicado — sem escarro purulento (Anthonisen incompleto).')
        linhas.append('')
        linhas.append('Retorno em 48–72h para reavaliação.')
        return '\n'.join(linhas)

    # Rotina — GOLD ABE
    grupo    = resultado.get('grupo', 'A')
    ics_ind  = resultado.get('ics_indicado', False)
    ics_just = resultado.get('ics_just', '')
    eosin    = resultado.get('eosinofilos')
    tabag    = resultado.get('tabagismo_ativo', False)
    alfa1    = resultado.get('alfa1_triar', False)

    linhas.append(f'DPOC Grupo {grupo} — Controle Crônico (GOLD 2026)')
    linhas.append('')

    if grupo == 'A':
        linhas.append('Tratamento inicial:')
        linhas.append('• LAMA: Tiotrópio 18 mcg 1×/dia (Spiriva) OU Umeclidínio 62,5 mcg 1×/dia')
        linhas.append('  Alt.: LABA (formoterol ou salmeterol) se intolerância ao LAMA')
    elif grupo == 'B':
        linhas.append('Tratamento inicial:')
        linhas.append('• LAMA + LABA (combinação de dose única preferida):')
        linhas.append('  Umeclidínio/Vilanterol 62,5/25 mcg 1×/dia (Anoro) OU')
        linhas.append('  Tiotrópio/Olodaterol 2,5/2,5 mcg 2 puffs 1×/dia (Stiolto)')
    elif grupo == 'E':
        linhas.append('Tratamento inicial:')
        linhas.append('• LAMA + LABA — obrigatório (GOLD E)')
        if ics_ind:
            linhas.append(f'• Adicionar ICS (terapia tripla) — {ics_just}')
            linhas.append('  Triple: LAMA + LABA + ICS em inalador único quando disponível')
        else:
            linhas.append(f'• ICS não indicado agora (eosinófilos < 100{" — eosin: " + str(eosin) if eosin else ""})')
            linhas.append('  Adicionar ICS se eosinófilos ≥ 300 ou ≥ 100 com exacerbações frequentes')

    linhas.append('')
    linhas.append('Não-farmacológico:')
    if tabag:
        linhas.append('⚠️  CESSAÇÃO DO TABAGISMO — intervenção mais importante:')
        linhas.append('  • Vareniclina (Champix) 0,5 mg/dia × 3d → 0,5 mg 12/12h × 4d → 1 mg 12/12h × 11 sem')
        linhas.append('  • Alt.: Bupropiona 150 mg/dia × 3d → 150 mg 12/12h × 7–12 sem')
        linhas.append('  • TRN (adesivo + goma) como 3ª opção')
    linhas.append('• Reabilitação pulmonar — para todos os sintomáticos (Grupo B e E)')
    linhas.append('• Atividade física regular, suporte nutricional se desnutrição')
    linhas.append('')
    linhas.append('Vacinação:')
    linhas.append('• Influenza — anual')
    linhas.append('• Pneumococo — PCV20 ou PCV15 + PPSV23')
    linhas.append('• RSV — se ≥ 60 anos')
    linhas.append('• COVID-19 — conforme calendário vigente')

    if alfa1:
        linhas.append('')
        linhas.append('⚠️  Triagem de alfa-1 antitripsina indicada (idade < 45a / não fumante / predomínio basal).')

    return '\n'.join(linhas)


# ------------------------------------------------------------------
# SÍNCOPE — #Análise + #Plano
# ------------------------------------------------------------------

_SINCOPE_CATS = frozenset({
    'sincope_emergencia', 'sincope_vasovagal', 'sincope_situacional',
    'sincope_ortostatica', 'sincope_cardiaca_alto_risco',
    'sincope_cardiaca_medio_risco', 'sincope_indeterminada',
})


def _analise_sincope(resultado: dict) -> str:
    cat   = resultado.get('categoria', '')
    csrs  = resultado.get('csrs_score', 0)
    risco = resultado.get('csrs_risco', '')
    descr = resultado.get('csrs_descr', '')
    itens = resultado.get('csrs_itens', [])

    if cat == 'sincope_emergencia':
        flags = resultado.get('red_flags', [])
        ach   = '; '.join(f['achado'] for f in flags)
        return f'Síncope com sinal de alarme — encaminhamento imediato indicado. Achados: {ach}.'

    _LABELS = {
        'sincope_vasovagal':           'Síncope vasovagal — diagnóstico clínico',
        'sincope_situacional':         'Síncope situacional (miccional / defecação / tosse)',
        'sincope_ortostatica':         'Síncope por hipotensão ortostática',
        'sincope_cardiaca_alto_risco': 'Síncope de provável causa cardíaca — alto risco',
        'sincope_cardiaca_medio_risco':'Síncope sem causa definida — risco intermediário',
        'sincope_indeterminada':       'Síncope de causa indeterminada após avaliação inicial',
    }
    label = _LABELS.get(cat, 'Síncope')
    csrs_str = f'CSRS {csrs:+d} ({risco} — {descr}).'
    itens_str = ('; '.join(itens) + '.') if itens else ''
    causa_oh = resultado.get('causa_oh')
    oh_str   = f' Causa provável de HO: {causa_oh}.' if causa_oh else ''
    return f'{label}. {csrs_str}{(" Itens: " + itens_str) if itens_str else ""}{oh_str}'


def _plano_sincope(resultado: dict) -> str:
    cat   = resultado.get('categoria', '')
    linhas = []

    for alerta in resultado.get('alertas_seguranca', []):
        linhas.append(alerta)
    if resultado.get('alertas_seguranca'):
        linhas.append('')

    if cat == 'sincope_emergencia':
        flags = resultado.get('red_flags', [])
        linhas.append('⚠️  SÍNCOPE COM ALARME — Avaliação de Emergência')
        linhas.append('')
        for f in flags:
            linhas.append(f'• {f["achado"]}')
            linhas.append(f'  → {f["acao"]}')
        linhas.append('')
        linhas.append('ECG de 12 derivações imediato. Não dispensar sem avaliação cardiológica.')
        return '\n'.join(linhas)

    if cat == 'sincope_vasovagal':
        linhas.append('Síncope Vasovagal — Manejo Ambulatorial')
        linhas.append('')
        linhas.append('Educação do paciente:')
        linhas.append('• Reconhecer pródromo e deitar imediatamente (não tentar permanecer de pé)')
        linhas.append('• Evitar gatilhos: ortostatismo prolongado, calor, ambientes fechados, jejum')
        linhas.append('')
        linhas.append('Medidas físicas (primeira linha — ESC 2018):')
        linhas.append('• Cruzar as pernas e contrair musculatura ao sentir o pródromo')
        linhas.append('• Apertar o punho + tensionar o braço (contra-pressão isométrica)')
        linhas.append('• Aumentar ingesta hídrica: 2–3 L/dia')
        linhas.append('• Aumentar sal: 6–10 g/dia (se sem HAS ou ICC)')
        linhas.append('')
        linhas.append('Retorno: se episódios ≥ 2/ano ou episódio injurioso → cardiologia')
        return '\n'.join(linhas)

    if cat == 'sincope_situacional':
        linhas.append('Síncope Situacional — Manejo')
        linhas.append('• Orientar sobre mecanismo (reflexo vagal durante micção/defecação/tosse)')
        linhas.append('• Sentar para urinar / defecar sempre que possível')
        linhas.append('• Hidratação adequada; evitar manobra de Valsalva prolongada')
        linhas.append('• ECG basal para documentação')
        return '\n'.join(linhas)

    if cat == 'sincope_ortostatica':
        causa = resultado.get('causa_oh', 'investigar')
        linhas.append('Hipotensão Ortostática — Manejo')
        linhas.append('')
        if causa == 'farmacológica' or resultado.get('medicamentos_causais'):
            linhas.append('⚠️  Revisar e reduzir anti-hipertensivos, diuréticos e alfa-bloqueadores.')
        linhas.append('')
        linhas.append('Medidas não farmacológicas (ESC 2018 — Classe I):')
        linhas.append('• Ingestão rápida de 500 mL de água ao levantar (elevação aguda da PA)')
        linhas.append('• Levantar devagar: sentar 1 min antes de ficar de pé')
        linhas.append('• Meia de compressão 30–40 mmHg ou faixa abdominal')
        linhas.append('• Cabeça elevada 10–20° ao dormir (reduz diurese noturna)')
        linhas.append('• Refeições pequenas e frequentes (evitar hipotensão pós-prandial)')
        linhas.append('• Sal 6–10 g/dia + 2–3 L/dia de água (se sem contraindicação)')
        if causa == 'neurogenica':
            linhas.append('')
            linhas.append('Causa neurógena — considerar:')
            linhas.append('• Midodrina 2,5–10 mg 3×/dia (evitar dose após 18h)')
            linhas.append('• Fludrocortisona 0,1–0,2 mg/dia (monitorar K+ e edema)')
        return '\n'.join(linhas)

    # Alto / médio risco ou indeterminado
    risco = resultado.get('csrs_risco', '')
    linhas.append(f'Síncope — {cat.replace("_"," ").title()}')
    linhas.append('')
    linhas.append('Avaliação mínima obrigatória:')
    linhas.append('• ECG de 12 derivações (se não feito)')
    linhas.append('• PA ortostática (deitado → de pé 1 e 3 min)')
    if risco in ('alto', 'muito_alto'):
        linhas.append('')
        linhas.append('⚠️  CSRS ≥ 4 — hospitalização ou avaliação cardiológica urgente.')
        linhas.append('• Monitorização cardíaca contínua')
        linhas.append('• Ecocardiograma + holter 24–48h')
    elif risco == 'medio':
        linhas.append('')
        linhas.append('CSRS 1–3 — avaliação cardiológica expedita (< 2 semanas).')
        linhas.append('• Ecocardiograma se sopro ou suspeita estrutural')
        linhas.append('• Holter 24h ou monitor de eventos 30 dias se palpitação prévia')
    else:
        linhas.append('• Reassurance se padrão benigno confirmado')
        linhas.append('• Retorno se recorrência ou lesão no episódio')
    return '\n'.join(linhas)


# ------------------------------------------------------------------
# ANORRETAL — #Análise + #Plano
# ------------------------------------------------------------------

_ANORRETAL_CATS = frozenset({
    'anorretal_colonoscopia_urgente', 'hemorroida_grau_1_2',
    'hemorroida_grau_3', 'hemorroida_grau_4', 'hemorroida_trombosada',
    'fissura_anal', 'prurido_anal',
})


def _analise_anorretal(resultado: dict) -> str:
    cat = resultado.get('categoria', '')

    if cat == 'anorretal_colonoscopia_urgente':
        flags = resultado.get('red_flags', [])
        ach   = '; '.join(f['achado'] for f in flags)
        return f'Sangramento anorretal com sinal de alarme — colonoscopia indicada. Achados: {ach}.'

    if cat == 'hemorroida_trombosada':
        h   = resultado.get('horas', 0)
        ab  = resultado.get('abordagem', 'conservador')
        txt = 'Hemorroida externa trombosada aguda'
        txt += f' — {h}h de evolução. '
        txt += 'Dentro da janela de 72h — candidata a incisão e drenagem.' if ab == 'incisao_drenagem' \
               else 'Após 72h — manejo conservador (pico de dor já passado).'
        return txt

    _LABELS = {
        'hemorroida_grau_1_2': 'Doença hemorroidária — Graus I–II',
        'hemorroida_grau_3':   'Doença hemorroidária — Grau III (prolapso com redução manual)',
        'hemorroida_grau_4':   'Doença hemorroidária — Grau IV (prolapso irredutível)',
        'fissura_anal':        'Fissura anal',
        'prurido_anal':        'Prurido anal',
    }
    label = _LABELS.get(cat, cat)

    if cat == 'fissura_anal':
        tipo = resultado.get('tipo_fissura', 'aguda')
        return f'{label} — {tipo}. ' + (
            'Fissura crônica (> 6 semanas) — fibras do esfíncter interno expostas / tag sentinela possível.'
            if tipo == 'cronica' else
            'Fissura aguda (< 6 semanas) — potencial de resolução com conservador.'
        )

    if cat == 'prurido_anal':
        causas = resultado.get('causas', ['idiopático'])
        return f'{label}. Causa(s) provável(is): {"; ".join(causas)}.'

    grau = resultado.get('grau', '')
    return f'{label}. Classificação de Goligher {grau}.'


def _plano_anorretal(resultado: dict) -> str:
    cat  = resultado.get('categoria', '')
    linhas = []

    # ── Alertas de segurança — sempre no topo ─────────────────────────────────
    for alerta in resultado.get('alertas_seguranca', []):
        linhas.append(alerta)
    if resultado.get('alertas_seguranca'):
        linhas.append('')

    if cat == 'anorretal_colonoscopia_urgente':
        flags = resultado.get('red_flags', [])
        linhas.append('⚠️  COLONOSCOPIA INDICADA')
        for f in flags:
            linhas.append(f'• {f["achado"]} → {f["acao"]}')
        linhas.append('')
        linhas.append('Enquanto aguarda: fibra + hidratação + evitar straining.')
        return '\n'.join(linhas)

    if cat == 'hemorroida_trombosada':
        ab = resultado.get('abordagem', 'conservador')
        linhas.append('Hemorroida Trombosada')
        if ab == 'incisao_drenagem':
            linhas.append('• Incisão e drenagem sob anestesia local — alívio imediato da dor')
            linhas.append('• Orientar: curativo seco + banho de assento 3×/dia')
            linhas.append('• Analgesia: dipirona 1g 6/6h + ibuprofeno 400mg 8/8h por 5 dias')
        else:
            linhas.append('• Manejo conservador (> 72h — pico de dor já passou)')
            linhas.append('• Banho de assento morno 3–4×/dia')
            linhas.append('• Analgesia oral + pomada de lidocaína 5% local')
            linhas.append('• Fibra + hidratação')
        return '\n'.join(linhas)

    if cat in ('hemorroida_grau_1_2', 'hemorroida_grau_3'):
        grau = resultado.get('grau', 'I')
        linhas.append(f'Doença Hemorroidária Grau {grau}')
        linhas.append('')
        linhas.append('Base (todos os graus):')
        linhas.append('• Fibra alimentar: 25–30 g/dia (psyllium 1 sachê/dia + frutas)')
        linhas.append('• Hidratação: ≥ 2 L/dia')
        linhas.append('• Evitar straining (não forçar a defecação)')
        linhas.append('• Flebotônicos: diosmina + hesperidina 500 mg 2×/dia por 3–6 meses')
        linhas.append('  (reduz sangramento e dor, 80% recidiva em 3–6 meses sem hábito intestinal)')
        if grau in ('I', 'II'):
            linhas.append('')
            linhas.append('Procedimento (se falha conservadora — Graus I–II):')
            linhas.append('• Ligadura elástica: 89% de resolução sintomática — encaminhar coloproctologia')
            linhas.append('• Fotocoagulação infravermelha (alternativa à ligadura)')
        else:
            linhas.append('')
            linhas.append('Grau III — Ligadura elástica preferida (primeira linha):')
            linhas.append('• Encaminhar coloproctologia para ligadura elástica')
            linhas.append('• Cirurgia se falha da ligadura ou doença mista')
        return '\n'.join(linhas)

    if cat == 'hemorroida_grau_4':
        linhas.append('Doença Hemorroidária Grau IV — Encaminhamento Cirúrgico')
        linhas.append('• Hemorroidectomia excisional (recidiva 2–10%) — encaminhar coloproctologia')
        linhas.append('• Base: fibra + hidratação enquanto aguarda cirurgia')
        linhas.append('• Analgesia local: pomada de lidocaína 5%')
        return '\n'.join(linhas)

    if cat == 'fissura_anal':
        tipo = resultado.get('tipo_fissura', 'aguda')
        linhas.append(f'Fissura Anal — {tipo.capitalize()}')
        linhas.append('')
        linhas.append('Base (aguda e crônica):')
        linhas.append('• Fibra 25–30 g/dia + hidratação 2 L/dia')
        linhas.append('• Banho de assento morno 15–20 min após cada evacuação')
        linhas.append('• Lidocaína 5% pomada tópica antes da defecação')
        if tipo == 'aguda':
            linhas.append('')
            linhas.append('Fissura aguda: ~50% resolvem com conservador em 4–6 semanas.')
        else:
            linhas.append('')
            linhas.append('Fissura crônica — terapia tópica farmacológica:')
            linhas.append('• Diltiazem 2% creme 2×/dia × 8 semanas (67–90% cura; cefaleia em 20%)')
            linhas.append('• Alternativa: nitroglicerina 0,2% pomada 2×/dia (cefaleia frequente)')
            linhas.append('• Falha tópica: toxina botulínica → encaminhar coloproctologia')
        return '\n'.join(linhas)

    if cat == 'prurido_anal':
        causas = resultado.get('causas', ['idiopático'])
        linhas.append('Prurido Anal')
        linhas.append('')
        for c in causas:
            if 'Enterobius' in c or 'Oxiuros' in c or 'oxiuro' in c.lower():
                linhas.append('• Oxiuros: albendazol 400 mg dose única; repetir em 2 semanas')
                linhas.append('  Tratar todos os contactantes domiciliares')
            elif 'andida' in c or 'candida' in c.lower():
                linhas.append('• Candidíase: clotrimazol creme 1% 2×/dia × 2 semanas')
            elif 'contato' in c.lower() or 'irritat' in c.lower():
                linhas.append('• Dermatite de contato: eliminar irritantes, emoliente barreira')
                linhas.append('  Corticoide tópico leve (hidrocortisona 1%) por ≤ 2 semanas')
            elif 'dietético' in c.lower() or 'dietetico' in c.lower():
                linhas.append('• Reduzir: café, chá, chocolate, condimentados, álcool')
            else:
                linhas.append(f'• {c}')
        linhas.append('')
        linhas.append('Medidas gerais (primário/idiopático):')
        linhas.append('• Higiene: limpeza suave com água (sem papel agressivo, sem sabão forte)')
        linhas.append('• Emoliente barreira: óxido de zinco ou vaselina perianal')
        linhas.append('• Evitar umidade prolongada (trocar cueca frequentemente)')
        linhas.append('• Casos refratários: capsaicina 0,006% ou tacrolimo 0,1% pomada')
        return '\n'.join(linhas)

    return '\n'.join(linhas)


# ------------------------------------------------------------------
# EDEMA — #Análise + #Plano
# ------------------------------------------------------------------

_EDEMA_CATS = frozenset({
    'edema_dvt_alto_risco', 'edema_dvt_baixo_risco', 'edema_celulite',
    'edema_cardiaco', 'edema_renal_nefrotico', 'edema_hepatico',
    'edema_hipotireoidismo', 'edema_farmacologico', 'edema_venoso_cronico',
    'edema_linfedema', 'edema_investigar',
})


def _analise_edema(resultado: dict) -> str:
    cat   = resultado.get('categoria', '')
    lat   = resultado.get('lateral', resultado.get('lateralidade', ''))

    if cat == 'edema_dvt_alto_risco':
        w = resultado.get('wells_score', 0)
        i = '; '.join(resultado.get('wells_itens', []))
        return (f'Edema unilateral com suspeita de TVP — Wells {w} (alto risco). '
                f'Achados: {i}. Ecodoppler venoso indicado.')
    if cat == 'edema_dvt_baixo_risco':
        w = resultado.get('wells_score', 0)
        return (f'Edema unilateral — Wells {w} (baixo risco para TVP). '
                f'D-dímero negativo praticamente exclui TVP.')
    if cat == 'edema_celulite':
        return 'Edema unilateral com eritema e calor — celulite infecciosa.'
    if cat == 'edema_cardiaco':
        bnp = 'BNP elevado confirmado.' if resultado.get('bnp_elevado') else 'BNP não dosado.'
        return f'Edema bilateral de provável origem cardíaca (insuficiência cardíaca). {bnp}'
    if cat == 'edema_renal_nefrotico':
        return 'Edema bilateral com proteinúria intensa — síndrome nefrótica a investigar.'
    if cat == 'edema_hepatico':
        return 'Edema bilateral associado a disfunção hepática / cirrose — hipoalbuminemia.'
    if cat == 'edema_hipotireoidismo':
        tsh = resultado.get('tsh')
        return f'Edema bilateral / mixedema pré-tibial — hipotireoidismo.' + (f' TSH: {tsh} mUI/L.' if tsh else '')
    if cat == 'edema_farmacologico':
        farm = '; '.join(resultado.get('farmacos', []))
        return f'Edema bilateral de causa farmacológica. Medicamento(s) provável(is): {farm}.'
    if cat == 'edema_venoso_cronico':
        return 'Edema bilateral / unilateral crônico compatível com insuficiência venosa crônica (IVC).'
    if cat == 'edema_linfedema':
        causa = resultado.get('causa', 'primário')
        return f'Edema não depressível compatível com linfedema {causa}.'
    return 'Edema de etiologia a investigar — workup sistêmico indicado.'


def _plano_edema(resultado: dict) -> str:
    cat  = resultado.get('categoria', '')
    linhas = []

    for alerta in resultado.get('alertas_seguranca', []):
        linhas.append(alerta)
    if resultado.get('alertas_seguranca'):
        linhas.append('')

    if cat == 'edema_dvt_alto_risco':
        linhas.append('⚠️  TVP SUSPEITA — Wells ≥ 2')
        linhas.append('• Ecodoppler venoso com compressão — urgente (mesmo dia ou próximo dia útil)')
        linhas.append('• Enquanto aguarda: não massagear, membro elevado, analgesia')
        linhas.append('• Se TVP confirmada: anticoagulação (rivaroxabana 15mg 2×/dia × 21d → 20mg/dia)')
        linhas.append('• Encaminhar hematologia/angiologia para seguimento')
        return '\n'.join(linhas)

    if cat == 'edema_dvt_baixo_risco':
        linhas.append('Edema Unilateral — Baixo Risco de TVP')
        linhas.append('• D-dímero: se negativo → TVP excluída')
        linhas.append('• Se D-dímero positivo → ecodoppler venoso')
        linhas.append('• Investigar IVC, linfedema, celulite, cisto de Baker')
        return '\n'.join(linhas)

    if cat == 'edema_celulite':
        linhas.append('Celulite de Membros Inferiores')
        linhas.append('• Amoxicilina-clavulanato 875/125 mg 12/12h × 7–10 dias')
        linhas.append('  Alt.: cefalexina 500 mg 6/6h (se sem risco de MRSA)')
        linhas.append('• Elevação do membro afetado')
        linhas.append('• Demarcar a borda do eritema com caneta para monitorar progressão')
        linhas.append('• Retorno em 48h — se piora → PS para ATB IV')
        return '\n'.join(linhas)

    if cat == 'edema_cardiaco':
        linhas.append('Edema por Insuficiência Cardíaca')
        linhas.append('')
        linhas.append('Exames: BNP (se não feito), ECG, ecocardiograma, RX tórax')
        linhas.append('')
        linhas.append('Diurético:')
        linhas.append('• Furosemida 20–40 mg/dia VO; ajustar pela resposta')
        linhas.append('• Associar espironolactona 25 mg/dia (FEVr reduzida)')
        linhas.append('• Meta: -0,5 a 1 kg/dia até peso seco')
        linhas.append('')
        linhas.append('Encaminhar cardiologia para otimização do tratamento da IC.')
        return '\n'.join(linhas)

    if cat == 'edema_renal_nefrotico':
        linhas.append('Síndrome Nefrótica — Investigação')
        linhas.append('• Proteinúria de 24h ou relação Pt/Cr na urina')
        linhas.append('• Albumina sérica, lipidograma, complemento')
        linhas.append('• Encaminhar nefrologia')
        linhas.append('• Diurético com cautela (hipovolemia relativa frequente)')
        return '\n'.join(linhas)

    if cat == 'edema_hepatico':
        linhas.append('Edema por Cirrose / Hipoalbuminemia Hepática')
        linhas.append('• Espironolactona 100 mg/dia + furosemida 40 mg/dia (razão 100:40)')
        linhas.append('• Restrição de sódio < 2 g/dia')
        linhas.append('• Encaminhar hepatologia para avaliação de ascite e manejo da cirrose')
        return '\n'.join(linhas)

    if cat == 'edema_hipotireoidismo':
        linhas.append('Edema por Hipotireoidismo')
        linhas.append('• Levotiroxina — iniciar ou ajustar dose (TSH alvo 0,5–2,5 mUI/L)')
        linhas.append('• Reavaliação de TSH em 6–8 semanas')
        linhas.append('• Edema resolve com controle hormonal adequado')
        return '\n'.join(linhas)

    if cat == 'edema_farmacologico':
        farm = resultado.get('farmacos', [])
        linhas.append('Edema Farmacológico')
        linhas.append('')
        for f in farm:
            if 'canal de cálcio' in f.lower() or 'bcc' in f.lower():
                linhas.append(f'• {f}: substituir por IECA/BRA ou reduzir dose se possível')
            elif 'aine' in f.lower():
                linhas.append(f'• {f}: suspender ou reduzir; usar paracetamol como alternativa')
            elif 'gabapentina' in f.lower() or 'pregabalina' in f.lower():
                linhas.append(f'• {f}: reduzir dose ou trocar para duloxetina (se dor neuropática)')
            else:
                linhas.append(f'• {f}: avaliar redução de dose ou substituição')
        linhas.append('')
        linhas.append('Se medicamento não puder ser suspenso: furosemida 20–40 mg conforme necessário.')
        return '\n'.join(linhas)

    if cat == 'edema_venoso_cronico':
        linhas.append('Insuficiência Venosa Crônica (IVC)')
        linhas.append('')
        linhas.append('Tratamento:')
        linhas.append('• Meia de compressão 20–30 mmHg (C3) ou 30–40 mmHg (C4–C6)')
        linhas.append('  ⚠️  Medir índice tornozelo-braquial antes se suspeita de DAP')
        linhas.append('• Elevação dos membros (acima do nível do coração) 3×/dia por 30 min')
        linhas.append('• Venotônicos: diosmina + hesperidina (Daflon) 500 mg 2×/dia')
        linhas.append('• Exercício: caminhada diária, evitar ortostatismo prolongado')
        linhas.append('• Ablação (laser/RF) se refluxo significativo — encaminhar angiologia')
        return '\n'.join(linhas)

    if cat == 'edema_linfedema':
        causa = resultado.get('causa', '')
        linhas.append(f'Linfedema {"Secundário" if causa == "secundario" else "Primário"}')
        linhas.append('')
        linhas.append('Terapia Descongestiva Complexa (TDC):')
        linhas.append('• Drenagem linfática manual — fisioterapia especializada')
        linhas.append('• Enfaixamento multicamadas → depois meia de compressão 40–60 mmHg')
        linhas.append('• Exercício com compressão, cuidado da pele')
        linhas.append('• NÃO usar diuréticos (não são eficazes em linfedema)')
        linhas.append('• Encaminhar linfologista ou fisioterapia especializada')
        return '\n'.join(linhas)

    # edema_investigar
    linhas.append('Edema Bilateral — Workup Sistêmico')
    linhas.append('')
    linhas.append('Solicitar:')
    linhas.append('• BNP, ECG (descartar ICC)')
    linhas.append('• TSH (hipotireoidismo)')
    linhas.append('• AST, ALT, albumina, bilirrubinas (hepatopatia)')
    linhas.append('• Creatinina + relação Pt/Cr urina (nefrótico)')
    linhas.append('• Glicemia (DM como fator de risco)')
    linhas.append('• Rever todos os medicamentos em uso')
    return '\n'.join(linhas)


# ------------------------------------------------------------------
# ICTERÍCIA — #Análise + #Plano
# ------------------------------------------------------------------

_ICTERICIA_CATS = frozenset({
    'ictericia_emergencia', 'ictericia_gilbert', 'ictericia_hemolitica',
    'ictericia_hepatocelular', 'ictericia_colestatica_obs', 'ictericia_colestatica_intra',
})


def _analise_ictericia(resultado: dict) -> str:
    cat = resultado.get('categoria', '')

    if cat == 'ictericia_emergencia':
        flags = resultado.get('red_flags', [])
        ach   = '; '.join(f['achado'] for f in flags)
        return f'Icterícia com sinal de alarme — encaminhamento emergencial. Achados: {ach}.'

    if cat == 'ictericia_gilbert':
        return ('Hiperbilirrubinemia indireta isolada — síndrome de Gilbert provável. '
                'Enzimas hepáticas normais, sem hemólise. Condição benigna e hereditária.')

    if cat == 'ictericia_hemolitica':
        return ('Icterícia pré-hepática — padrão de bilirrubina indireta predominante. '
                'Investigar hemólise: hemograma, LDH, haptoglobina, reticulócitos, esfregaço.')

    if cat == 'ictericia_hepatocelular':
        causas = resultado.get('causas', [])
        c_str  = '; '.join(causas)
        return (f'Icterícia hepatocelular — AST/ALT predominante. '
                f'Hipóteses etiológicas: {c_str}.')

    if cat == 'ictericia_colestatica_obs':
        pend = resultado.get('us_pendente', False)
        if pend:
            return ('Icterícia com padrão colestático — US abdominal pendente. '
                    'Se ductos dilatados → obstrução biliar (cálculo / neoplasia) → CPRE/EUS.')
        return ('Icterícia colestática com ductos biliares dilatados ao US — '
                'obstrução extrahepática. Diferencial: coledocolitíase vs. neoplasia de cabeça de pâncreas.')

    if cat == 'ictericia_colestatica_intra':
        causas = resultado.get('causas', [])
        c_str  = '; '.join(causas)
        return (f'Icterícia colestática intrahepática — ductos normais ao US. '
                f'Causa(s) provável(is): {c_str}.')

    return 'Icterícia — etiologia a determinar.'


def _plano_ictericia(resultado: dict) -> str:
    cat    = resultado.get('categoria', '')
    linhas = []

    # ── Alertas de segurança — sempre no topo ─────────────────────────────────
    for alerta in resultado.get('alertas_seguranca', []):
        linhas.append(alerta)
    if resultado.get('alertas_seguranca'):
        linhas.append('')

    if cat == 'ictericia_emergencia':
        flags = resultado.get('red_flags', [])
        linhas.append('⚠️  ICTERÍCIA COM ALARME — Encaminhamento Emergencial')
        for f in flags:
            linhas.append(f'• {f["achado"]}')
            linhas.append(f'  → {f["acao"]}')
        return '\n'.join(linhas)

    if cat == 'ictericia_gilbert':
        linhas.append('Síndrome de Gilbert — Reassurance')
        linhas.append('• Condição benigna, hereditária, sem tratamento necessário')
        linhas.append('• Icterícia piora com jejum, estresse, infecção ou exercício intenso')
        linhas.append('• Confirmar: bilirrubina indireta < 3–4 mg/dL, enzimas normais, sem hemólise')
        linhas.append('• Não há dieta específica; evitar jejum prolongado')
        return '\n'.join(linhas)

    if cat == 'ictericia_hemolitica':
        linhas.append('Icterícia Hemolítica — Investigação')
        linhas.append('• Hemograma + esfregaço de sangue periférico')
        linhas.append('• LDH, haptoglobina, reticulócitos')
        linhas.append('• Coombs direto (hemólise autoimune)')
        linhas.append('• G6PD se histórico de crise hemolítica')
        linhas.append('• Encaminhar hematologia se hemólise confirmada')
        return '\n'.join(linhas)

    if cat == 'ictericia_hepatocelular':
        causas = resultado.get('causas', [])
        linhas.append('Hepatite — Workup Etiológico')
        linhas.append('')
        linhas.append('Solicitar:')
        linhas.append('• Anti-HAV IgM | HBsAg + anti-HBc IgM + HBV DNA | Anti-HCV + HCV RNA')
        linhas.append('• ANA + anti-músculo liso + IgG (hepatite autoimune)')
        linhas.append('• Nível de paracetamol se suspeita de intoxicação')
        linhas.append('• Revisão completa de medicamentos e suplementos')
        linhas.append('')
        for c in causas:
            if 'alcoól' in c.lower():
                linhas.append('Hepatite alcoólica: abstinência + suporte nutricional + tiamina')
            elif 'HCV' in c or 'hepatite c' in c.lower():
                linhas.append('HCV confirmado → encaminhar gastroenterologia/hepatologia para DAAs (cura > 95%)')
            elif 'HBV' in c or 'hepatite b' in c.lower():
                linhas.append('HBV: observar se agudo leve; tratar se INR>1,5 ou encefalopatia; '
                               'encaminhar hepatologia se cronicidade')
            elif 'HAV' in c or 'hepatite a' in c.lower():
                linhas.append('HAV: suporte + repouso; monitorar INR para insuficiência fulminante')
        return '\n'.join(linhas)

    if cat == 'ictericia_colestatica_obs':
        linhas.append('Icterícia Colestática Obstrutiva')
        linhas.append('')
        if resultado.get('us_pendente'):
            linhas.append('US abdominal (primeiro passo):')
            linhas.append('• Ductos dilatados → CPRE (terapêutica) ou EUS (diagnóstica)')
            linhas.append('• Ductos normais → colestase intrahepática → AMA, MRCP')
        else:
            linhas.append('Ductos dilatados confirmados → obstrução biliar extrahepática:')
            linhas.append('• TC abdome com contraste IV — avaliar massa pancreática / coledocolitíase')
            linhas.append('• CA 19-9 + CEA (triagem de malignidade)')
            linhas.append('• CPRE se coledocolitíase provável (cólica biliar, cálculo no US)')
            linhas.append('• EUS se massa/suspeita de malignidade')
            linhas.append('• Encaminhar gastroenterologia/cirurgia urgente')
        return '\n'.join(linhas)

    if cat == 'ictericia_colestatica_intra':
        causas = resultado.get('causas', [])
        linhas.append('Colestase Intrahepática — Investigação')
        linhas.append('')
        for c in causas:
            if 'PBC' in c or 'biliar primária' in c.lower():
                linhas.append('• CBP/PBC (AMA+): ácido ursodesoxicólico 13–15 mg/kg/dia')
                linhas.append('  Encaminhar hepatologia')
            elif 'CEP' in c or 'esclerosante' in c.lower():
                linhas.append('• CEP suspeita: MRCP para padrão de estenoses em colar de contas')
                linhas.append('  Encaminhar hepatologia/gastroenterologia')
            elif 'DILI' in c or 'medicament' in c.lower():
                linhas.append('• DILI colestático: suspender medicamento responsável')
                linhas.append('  Monitorar enzimas a cada 2 semanas até normalização')
            else:
                linhas.append(f'• {c}')
        return '\n'.join(linhas)

    return ''


# ------------------------------------------------------------------
# GOTA — #Análise + #Plano
# ------------------------------------------------------------------

_GOTA_CATS = frozenset({
    'gota_artrite_septica_excluir',
    'gota_provavel_ataque_agudo',
    'gota_possivel_ataque_agudo',
    'gota_improvavel_ataque_agudo',
    'gota_interataque',
    'gota_tofacea',
})


def _analise_gota(resultado: dict) -> str:
    """Texto para #Análise — Gota."""
    cat        = resultado.get('categoria', '')
    score      = resultado.get('score_dutch', 0.0)
    itens      = resultado.get('score_itens', [])
    fase       = resultado.get('fase', '')
    urato      = resultado.get('urato_mgdl')
    arts       = resultado.get('articulacoes', '')

    if cat == 'gota_artrite_septica_excluir':
        flags   = resultado.get('red_flags', [])
        achados = '; '.join(f['achado'] for f in flags)
        return (
            f'Artrite aguda — artrite séptica a excluir ANTES de tratar como gota. '
            f'Sinais de alarme: {achados}.'
        )

    itens_str = '; '.join(itens) if itens else 'nenhum item positivo registrado'

    if cat == 'gota_provavel_ataque_agudo':
        arts_str = f' ({arts})' if arts else ''
        return (
            f'Ataque agudo de gota — provável{arts_str}. '
            f'Score de Janssens {score}/15 pontos (≥ 8 → probabilidade > 80%). '
            f'Achados positivos: {itens_str}.'
        )

    if cat == 'gota_possivel_ataque_agudo':
        arts_str = f' ({arts})' if arts else ''
        urato_str = f' Ácido úrico {urato:.1f} mg/dL.' if urato is not None else ''
        return (
            f'Artrite aguda — possível gota{arts_str}. '
            f'Score de Janssens {score}/15 pontos (zona intermediária 4–7). '
            f'Achados positivos: {itens_str}.{urato_str}'
        )

    if cat == 'gota_improvavel_ataque_agudo':
        arts_str = f' ({arts})' if arts else ''
        return (
            f'Artrite aguda — gota improvável{arts_str}. '
            f'Score de Janssens {score}/15 pontos (< 4 → > 97% excludente). '
            f'Considerar hipótese alternativa: pseudogota, artrite reativa, '
            f'artrite séptica, artrite reumatoide.'
        )

    if cat == 'gota_interataque':
        n = resultado.get('n_ataques_ano', 0) or 0
        conf = ' (diagnóstico confirmado previamente)' if resultado.get('gota_confirmada') else ''
        return (
            f'Gota em período intercrítico{conf}. '
            f'{n} ataque{"s" if n != 1 else ""} no último ano. '
            f'Sem artrite aguda no momento.'
        )

    if cat == 'gota_tofacea':
        return (
            'Gota tofácea crônica — tophi presentes. '
            'Indica doença de longa data com deposição tecidual de cristais de urato. '
            'ULT mandatório (indicação forte — ACR 2020).'
        )

    return f'Gota — {cat}.'


def _plano_gota(resultado: dict) -> str:
    """Texto para #Plano — Gota."""
    cat    = resultado.get('categoria', '')
    fase   = resultado.get('fase', '')
    linhas = []

    # ── Alertas de segurança — sempre no topo ─────────────────────────────────
    for alerta in resultado.get('alertas_seguranca', []):
        linhas.append(alerta)
    if resultado.get('alertas_seguranca'):
        linhas.append('')

    # ── Artrite séptica a excluir ────────────────────────────────────────────
    if cat == 'gota_artrite_septica_excluir':
        flags = resultado.get('red_flags', [])
        linhas.append('⚠️  ARTRITE SÉPTICA A EXCLUIR — Gota')
        linhas.append('')
        for f in flags:
            linhas.append(f'• {f["achado"]}')
            linhas.append(f'  → {f["acao"]}')
        linhas.append('')
        linhas.append('NÃO iniciar colchicina/AINE sem excluir infecção articular.')
        return '\n'.join(linhas)

    # ── Gota improvável — diagnóstico diferencial ────────────────────────────
    if cat == 'gota_improvavel_ataque_agudo':
        linhas.append('Gota improvável — Investigação de Diagnóstico Diferencial')
        linhas.append('')
        linhas.append('Exames:')
        linhas.append('• Ácido úrico sérico, hemograma, PCR, VHS')
        linhas.append('• RX articular — pesquisar condrocalcinose (pseudogota/CPPD)')
        linhas.append('• FR, anti-CCP, RX mãos/pés — se suspeita de artrite reumatoide')
        linhas.append('')
        linhas.append('Diagnósticos alternativos a considerar:')
        linhas.append('• Pseudogota (CPPD) — calcificação na cartilagem ao RX')
        linhas.append('• Artrite reativa — sorologias conforme contexto clínico')
        linhas.append('• Artrite reumatoide — padrão simétrico, pequenas articulações')
        linhas.append('• Artrite séptica — se febre + toxemia → punção + PS (ver red flags)')
        return '\n'.join(linhas)

    # ── Ataque agudo (provável ou possível) ──────────────────────────────────
    conduta_aguda = resultado.get('conduta_aguda', {})
    if fase == 'ataque_agudo' and conduta_aguda:
        opcoes  = conduta_aguda.get('opcoes', [])
        alertas = conduta_aguda.get('alertas', [])
        gelo    = conduta_aguda.get('gelo', False)

        titulo = 'Gota — Ataque Agudo' + (' (Provável)' if 'provavel' in cat else ' (Possível)')
        linhas.append(titulo)

        if alertas:
            linhas.append('')
            for a in alertas:
                linhas.append(f'⚠️  {a}')

        linhas.append('')
        linhas.append('Anti-inflamatório (escolher 1):')
        for i, op in enumerate(opcoes, 1):
            linhas.append(f'')
            linhas.append(f'{i}. {op["agente"]}')
            linhas.append(f'   {op["dose"]}')
            if op.get('obs'):
                linhas.append(f'   Obs.: {op["obs"]}')

        if gelo:
            linhas.append('')
            linhas.append('Adjuvante: Gelo local 20–30 min, 3–4×/dia (ACR 2020).')

        linhas.append('')
        linhas.append('Repouso articular durante o ataque.')
        linhas.append('')
        linhas.append(
            'IMPORTANTE: Não iniciar alopurinol durante o ataque agudo sem '
            'anti-inflamatório de cobertura (pode prolongar o flare).'
        )

        if cat == 'gota_possivel_ataque_agudo':
            linhas.append('')
            linhas.append('─── CONFIRMAÇÃO DIAGNÓSTICA (score intermediário) ───────')
            linhas.append('• Ácido úrico sérico — coletar 2–4 semanas APÓS o flare')
            linhas.append('  (durante o ataque pode estar falsamente normal)')
            linhas.append('• RX articular — erosões com borda esclerótica e')
            linhas.append('  "overhanging edge" são sugestivas de gota')
            linhas.append('• US articular (se disponível) — sinal do duplo contorno')

    # ── ULT (todos exceto artrite séptica / improvável) ──────────────────────
    ult = resultado.get('ult', {})
    if ult and cat not in ('gota_artrite_septica_excluir', 'gota_improvavel_ataque_agudo'):
        indicacao = ult.get('indicacao', 'nenhuma')

        linhas.append('')
        linhas.append('─── TRATAMENTO HIPOURICEMIANTE (ULT) ───────────────────')

        if ult.get('ja_usa_ult'):
            linhas.append('Já em uso de hipouricemiante.')
            urato_atual = ult.get('urato_atual')
            if urato_atual is not None:
                alvo = 'META ATINGIDA ✓' if urato_atual < 6.0 else f'ACIMA DA META (alvo < 6,0 mg/dL)'
                linhas.append(f'Ácido úrico atual: {urato_atual:.1f} mg/dL — {alvo}')
            if indicacao in ('forte', 'condicional') and (urato_atual or 0) >= 6.0:
                linhas.append('Titular dose até atingir meta < 6,0 mg/dL.')
        else:
            _IND = {
                'forte':       '✅ Indicação FORTE — iniciar após controle do ataque',
                'condicional': '⚠️  Indicação CONDICIONAL — discutir com paciente',
                'nenhuma':     'ℹ️  Sem indicação formal no momento (< 2 ataques/ano sem complicações)',
            }
            linhas.append(_IND.get(indicacao, ''))

            if indicacao in ('forte', 'condicional'):
                dose  = ult.get('dose_inicio')
                freq  = ult.get('freq', '1×/dia')
                egfr  = ult.get('egfr', 90)

                if dose:
                    linhas.append(f'Alopurinol: iniciar {dose} mg {freq}.')
                    linhas.append(ult.get('titulacao', ''))
                    linhas.append(f'Meta: urato sérico {ult.get("alvo_urato", "< 6,0 mg/dL")}.')
                    linhas.append('')
                    linhas.append(f'Profilaxia: {ult.get("profilaxia", "")}')
                else:
                    linhas.append('eGFR < 15 — alopurinol com cautela extrema; consultar nefrologista.')

                if ult.get('alerta_hla'):
                    linhas.append('')
                    linhas.append(
                        '⚠️  HLA-B*5801: Triagem recomendada antes de iniciar alopurinol '
                        '(origem coreana / chinesa Han / tailandesa). '
                        'Risco de síndrome de hipersensibilidade grave (SJS/DRESS).'
                    )

                linhas.append('')
                linhas.append('Controle: ácido úrico sérico 4–6 semanas após cada ajuste de dose.')

    # ── Dieta e estilo de vida ───────────────────────────────────────────────
    linhas.append('')
    linhas.append('─── DIETA E ESTILO DE VIDA ───────────────────────────────')
    linhas.append('Evitar: vísceras (fígado, rins), anchovas, sardinhas, frutos do mar.')
    linhas.append('Reduzir: carne vermelha, cerveja e destilados (aumentam urato).')
    linhas.append('Limitar: bebidas adoçadas com frutose / xarope de milho.')
    linhas.append('Hidratação: ≥ 2 litros/dia.')
    linhas.append('Benéfico: laticínios desnatados, cerejas, café (efeito hipouricemiante leve).')
    linhas.append('')
    linhas.append(
        'Nota: dieta tem efeito modesto (reduz ~1 mg/dL de urato). '
        'ULT é o pilar do controle a longo prazo.'
    )

    return '\n'.join(linhas)


# ------------------------------------------------------------------
# CONSCIÊNCIA — #Plano
# ------------------------------------------------------------------

_CONSCIENCIA_CATS = frozenset({
    'hipoglicemia', 'hipoxia_grave', 'overdose_opioide',
    'pos_ictal', 'status_epilepticus', 'avc_sangramento',
    'meningite_encefalite', 'tce_hematoma',
    'intoxicacao_opioide', 'intoxicacao_benzo', 'intoxicacao_alcool_intox',
    'intoxicacao_antidepressivo', 'intoxicacao_organofosforado', 'intoxicacao_co',
    'intoxicacao_desconhecido', 'intoxicacao_alcool',
    'encefalopatia_metabolica', 'crise_dissociativa', 'anc_indefinida',
})

_CID_CONSCIENCIA = {
    'hipoglicemia':            'E16.0',
    'hipoxia_grave':           'R09.0',
    'overdose_opioide':        'T40.2',
    'pos_ictal':               'G40.9',
    'status_epilepticus':      'G41.9',
    'avc_sangramento':         'I64',
    'meningite_encefalite':    'G03.9',
    'tce_hematoma':            'S09.9',
    'intoxicacao_benzo':       'T42.4',
    'intoxicacao_organofosforado': 'T60.0',
    'intoxicacao_co':          'T58',
    'intoxicacao_antidepressivo': 'T43.0',
    'intoxicacao_alcool':      'T51.0',
    'encefalopatia_metabolica':'G93.4',
    'crise_dissociativa':      'F44.5',
    'anc_indefinida':          'R55',
}


def _plano_consciencia(resultado: dict) -> str:
    cat  = resultado.get('categoria', '')
    cid  = _CID_CONSCIENCIA.get(cat, '')
    diag = resultado.get('diagnostico', '')
    cid_str = f' — CID-10: {cid}' if cid else ''
    urg  = {'emergencia': '🔴 EMERGÊNCIA', 'urgente': '🟠 URGENTE', 'eletivo': '🟢 Eletivo'}.get(
        resultado.get('urgencia', ''), '')
    linhas = [f'{urg} | Glasgow {resultado.get("glasgow","?")}/15{cid_str}', f'{diag}', '']

    # ── Alertas de segurança — sempre no topo ─────────────────────────────────
    for alerta in resultado.get('alertas_seguranca', []):
        linhas.append(alerta)
    if resultado.get('alertas_seguranca'):
        linhas.append('')

    if resultado.get('iot_alerta'):
        linhas.append('⚠️  GLASGOW ≤ 8 — AVALIAR IOT / SAMU')
        linhas.append('')

    for c in resultado.get('conduta', []):
        if c:
            linhas.append(f'{"  " if c.startswith("  ") else "• "}{c}')

    exames = resultado.get('exames', [])
    if exames:
        linhas += ['', 'Exames:']
        for e in exames: linhas.append(f'• {e}')

    enc = resultado.get('encaminhamento')
    if enc: linhas += ['', f'Encaminhamento: {enc}']
    return '\n'.join(linhas)


def _negativas_consciencia(dados: dict) -> str:
    """Pertinentes negativas documentadas no #Subjetivo — ANC."""
    neg = []
    if dados.get('trauma_cabeca') is False:
        neg.append('trauma craniencefálico')
    if dados.get('deficit_focal') is False:
        neg.append('déficit focal')
    if dados.get('rigidez_nuca') is False:
        neg.append('rigidez de nuca')
    if dados.get('convulsao_obs') is False:
        neg.append('convulsão observada')
    if dados.get('febre') is False:
        neg.append('febre')
    if dados.get('alcool_drogas') is False and dados.get('alcool_halito') is False:
        neg.append('intoxicação por álcool/drogas')
    if dados.get('intoxicacao_suspeita') is False:
        neg.append('intoxicação suspeita')
    return _fmt_negativas(neg)


def gerar_subjetivo_consciencia(admissao):
    """Texto #Subjetivo — Alteração do Nível de Consciência."""
    dados = _get_dados_modulo(admissao, 'consciencia', 'organico')
    if not dados:
        return ''

    partes = []
    g = dados.get('glasgow_total', 15)
    spo2 = dados.get('spo2')
    gli  = dados.get('glicemia')
    pa   = dados.get('pa_sistolica')
    fc   = dados.get('fc')

    # Nível de consciência
    _GLASGOW_DESC = {
        range(14, 16): 'consciente (Glasgow normal)',
        range(9, 14):  'rebaixamento leve de consciência',
        range(3, 9):   'rebaixamento grave de consciência (coma)',
    }
    desc = 'rebaixamento de consciência'
    for faixa, texto in _GLASGOW_DESC.items():
        if g in faixa:
            desc = texto
            break
    partes.append(f'Alteração do nível de consciência — Glasgow {g}/15 ({desc}).')

    # Vitais relevantes
    vitais = []
    if spo2 is not None and spo2 < 94:
        vitais.append(f'SpO₂ {spo2}%')
    if pa is not None and pa < 90:
        vitais.append(f'PA {pa} mmHg')
    if fc is not None and fc > 100:
        vitais.append(f'FC {fc} bpm')
    if gli is not None and gli < 70:
        vitais.append(f'Glicemia {gli} mg/dL')
    if vitais:
        partes.append('Sinais críticos: ' + ', '.join(vitais) + '.')

    # Pistas AEIOU TIPS
    pistas = []
    if dados.get('alcool_drogas') or dados.get('alcool_halito'):
        pistas.append('álcool/drogas')
    if dados.get('epilepsia_previa'):
        pistas.append('epilepsia prévia')
    if dados.get('convulsao_obs'):
        pistas.append('convulsão observada')
    if dados.get('pos_ictal'):
        pistas.append('estado pós-ictal')
    if dados.get('trauma_cabeca'):
        pistas.append('trauma craniencefálico')
    if dados.get('foco_infeccioso'):
        pistas.append('foco infeccioso')
    if dados.get('intoxicacao_suspeita'):
        pistas.append('intoxicação suspeita')
    if dados.get('renal_cronico'):
        pistas.append('DRC/uremia')
    if dados.get('encefalopatia'):
        pistas.append('encefalopatia')
    if pistas:
        partes.append('Pistas: ' + ', '.join(pistas) + '.')

    # Red flags neurológicos
    rf = []
    if dados.get('deficit_focal'):
        rf.append('déficit focal')
    if dados.get('rigidez_nuca'):
        rf.append('rigidez de nuca')
    if dados.get('cefaleia_intensa'):
        rf.append('cefaleia intensa')
    if dados.get('pupilas_aniso'):
        rf.append('anisocoria')
    if dados.get('lucido_intervalo'):
        rf.append('intervalo lúcido (HED?)')
    if rf:
        partes.append('SINAIS DE ALARME: ' + ', '.join(rf) + '.')

    # Contexto clínico
    ctx = []
    if dados.get('dpoc_conhecido'):
        ctx.append('DPOC')
    if dados.get('desnutricao'):
        ctx.append('desnutrição')
    if dados.get('medicamentos_risco'):
        ctx.append('medicamentos de risco')
    if ctx:
        partes.append('Contexto: ' + ', '.join(ctx) + '.')

    neg = _negativas_consciencia(dados)
    if neg:
        partes.append(neg + '.')

    return ' '.join(partes)


# ------------------------------------------------------------------
# LINFADENOPATIA — #Plano
# ------------------------------------------------------------------

_LINFA_CATS = frozenset({
    'linfadenopatia_reativa', 'ebv_mononucleose', 'doenca_arranhadura_gato',
    'linfadenite_bacteriana', 'tb_linfadenopatia', 'ist_linfadenopatia_inguinal',
    'hiv_infeccao_primaria', 'linfoma_suspeito', 'neoplasia_metastatica',
    'hernia_inguinal_suspeita', 'hernia_femoral_suspeita',
    'massa_inguinal_diferencial', 'linfadenopatia_inguinal_benigna',
})

_CID_LINFA = {
    'hernia_inguinal_suspeita':      'K40.9',  # Hérnia inguinal unilateral NE
    'hernia_femoral_suspeita':       'K41.9',  # Hérnia femoral unilateral NE
    'massa_inguinal_diferencial':    'R59.9',  # Linfadenopatia NE — investigar
    'linfadenopatia_inguinal_benigna': 'R59.0',# Linfadenopatia localizada benigna
    'linfadenopatia_reativa':        'R59.9',
    'ebv_mononucleose':              'B27.0',
    'doenca_arranhadura_gato':       'A28.1',
    'linfadenite_bacteriana':        'L04.9',
    'tb_linfadenopatia':             'A18.2',
    'ist_linfadenopatia_inguinal':   'I88.1',
    'hiv_infeccao_primaria':         'B23.1',
    'linfoma_suspeito':              'C85.9',
    'neoplasia_metastatica':         'C77.9',
}


def _plano_linfadenopatia(resultado: dict) -> str:
    cat  = resultado.get('categoria', '')
    cid  = _CID_LINFA.get(cat, '')
    diag = resultado.get('diagnostico', '')
    cid_str = f' — CID-10: {cid}' if cid else ''
    linhas = [f'{diag}{cid_str}', '']

    # ── Alertas de segurança — sempre no topo ─────────────────────────────────
    for alerta in resultado.get('alertas_seguranca', []):
        linhas.append(alerta)
    if resultado.get('alertas_seguranca'):
        linhas.append('')

    flags = resultado.get('red_flags', [])
    if flags:
        linhas.append('⚠️  Red flags:')
        for f in flags: linhas.append(f'  ⚑ {f}')
        linhas.append('')

    motivos = resultado.get('motivo_biopsia', [])
    if motivos:
        linhas.append('Critérios para biópsia:')
        for m in motivos: linhas.append(f'  • {m}')
        linhas.append('')

    exames = resultado.get('exames', [])
    if exames:
        linhas.append('Exames:')
        for e in exames: linhas.append(f'  • {e}')
        linhas.append('')

    trat = resultado.get('tratamento', {})
    if trat:
        linhas.append('Conduta:')
        for chave, valor in trat.items():
            linhas.append(f'\n[{chave.replace("_"," ").title()}]')
            for linha in str(valor).split('\n'):
                linhas.append(f'  {linha.strip()}')

    enc = resultado.get('encaminhamento')
    if enc:
        linhas += ['', f'Encaminhamento: {enc}']

    ret = resultado.get('retorno')
    if ret:
        linhas += ['', f'Retorno: {ret}']

    return '\n'.join(linhas)


def _negativas_linfadenopatia(dados: dict) -> str:
    """Pertinentes negativas — Linfadenopatia."""
    neg = []
    if dados.get('b_symptoms') is False:
        neg.append('B-symptoms')
    if dados.get('crescimento_rapido') is False:
        neg.append('crescimento rápido')
    if dados.get('esplenomegalia') is False:
        neg.append('esplenomegalia')
    if dados.get('pancitopenia') is False:
        neg.append('pancitopenia')
    if dados.get('exposicao_gato') is False:
        neg.append('exposição a gato')
    if dados.get('comportamento_risco_hiv') is False:
        neg.append('comportamento de risco HIV')
    if dados.get('risco_tb') is False:
        neg.append('risco TB')
    return _fmt_negativas(neg)


def gerar_subjetivo_linfadenopatia(admissao):
    """Texto #Subjetivo — Linfadenopatia."""
    dados = _get_dados_modulo(admissao, 'linfadenopatia', 'organico')
    if not dados:
        return ''

    partes = []

    # Caracterização principal
    loc  = dados.get('localizacao', '')
    tam  = dados.get('tamanho_cm')
    dur  = dados.get('duracao_semanas')
    tex  = dados.get('textura', '')
    _LOC = {
        'cervical': 'cervical', 'supraclavicular': 'supraclavicular',
        'axilar': 'axilar', 'inguinal': 'inguinal',
        'generalizada': 'generalizada', 'outro': 'outra localização',
    }
    _TEX = {
        'mole_movel': 'mole e móvel', 'firme': 'firme',
        'petreo_fixo': 'pétreo e fixo',
    }
    desc_parts = ['Linfadenopatia']
    if loc:
        desc_parts.append(_LOC.get(loc, loc))
    if tam:
        desc_parts.append(f'{tam} cm')
    if tex:
        desc_parts.append(f'consistência {_TEX.get(tex, tex)}')
    if dur:
        desc_parts.append(f'{dur} semanas de evolução')
    if dados.get('doloroso'):
        desc_parts.append('dolorosa')
    if dados.get('multiplos_nodulos'):
        desc_parts.append('múltiplos nódulos')
    partes.append(' — '.join(desc_parts[:2]) + (': ' + ', '.join(desc_parts[2:]) if len(desc_parts) > 2 else '') + '.')

    # B-symptoms / red flags
    rf = []
    if dados.get('b_symptoms'):
        rf.append('B-symptoms')
    if dados.get('crescimento_rapido'):
        rf.append('crescimento rápido')
    if dados.get('esplenomegalia'):
        rf.append('esplenomegalia')
    if dados.get('alargamento_mediastino'):
        rf.append('alargamento de mediastino')
    if dados.get('pancitopenia'):
        rf.append('pancitopenia')
    if dados.get('blastos'):
        rf.append('blastos no hemograma')
    if rf:
        partes.append('SINAIS DE ALARME: ' + ', '.join(rf) + '.')

    # Pistas infecciosas
    pistas = []
    if dados.get('faringite_recente'):
        pistas.append('faringite recente')
    if dados.get('sindrome_mono'):
        pistas.append('síndrome mono-like')
    if dados.get('monospot_positivo'):
        pistas.append('monospot positivo')
    if dados.get('exposicao_gato'):
        pistas.append('exposição a gato')
    if dados.get('problema_dental'):
        pistas.append('problema dental')
    if dados.get('risco_tb'):
        pistas.append('risco de TB')
    if dados.get('comportamento_risco_hiv'):
        pistas.append('comportamento de risco HIV')
    if dados.get('vacina_recente_ax'):
        pistas.append('vacina recente no braço')
    if dados.get('medicamentos_culpados'):
        pistas.append('medicamento causador')
    if pistas:
        partes.append('Pistas: ' + ', '.join(pistas) + '.')

    neg = _negativas_linfadenopatia(dados)
    if neg:
        partes.append(neg + '.')

    return ' '.join(partes)


# ------------------------------------------------------------------
# SONO — #Plano
# ------------------------------------------------------------------

_SONO_CATS = frozenset({
    'tcr_rem_pre_parkinson', 'narcolepsia_suspeita', 'aos_suspeita',
    'spi', 'bruxismo_sono', 'sfas', 'parassonia_nrem', 'pesadelos_tept',
    'desmame_benzo', 'insonia_comportamental', 'insonia_psiquiatrica',
    'insonia_cronica_primaria', 'insonia_subaguda', 'insonia_hipotireoidismo',
    'insonia_dor', 'insonia_turno',
})

_CID_SONO = {
    'insonia_cronica_primaria':   'G47.0',
    'insonia_comportamental':     'G47.0',
    'insonia_psiquiatrica':       'F51.0',
    'insonia_subaguda':           'G47.0',
    'insonia_hipotireoidismo':    'G47.0',
    'insonia_dor':                'G47.0',
    'insonia_turno':              'G47.2',
    'desmame_benzo':              'F13.3',
    'aos_suspeita':               'G47.3',
    'spi':                        'G25.8',
    'bruxismo_sono':              'G47.8',
    'sfas':                       'G47.2',
    'narcolepsia_suspeita':       'G47.4',
    'parassonia_nrem':            'G47.8',
    'pesadelos_tept':             'F43.1',
    'tcr_rem_pre_parkinson':      'G47.5',
}


def _plano_sono(resultado: dict) -> str:
    """Texto para #Plano — Transtornos do Sono."""
    cat  = resultado.get('categoria', '')
    cid  = _CID_SONO.get(cat, '')
    diag = resultado.get('diagnostico', '')
    cid_str = f' — CID-10: {cid}' if cid else ''
    linhas = [f'{diag}{cid_str}', '']

    # ── CBT-I prescrita ──────────────────────────────────────────────
    cbti = resultado.get('cbti')
    if cbti:
        linhas.append('CBT-I — Tratamento Principal:')
        componentes = {
            'restricao_sono':          'Restrição de Sono',
            'controle_estimulo':       'Controle de Estímulo',
            'higiene':                 'Higiene do Sono',
            'reestruturacao_cognitiva':'Reestruturação Cognitiva',
        }
        for chave, label in componentes.items():
            if chave in cbti:
                linhas.append(f'\n[{label}]')
                for linha in cbti[chave].split('\n'):
                    linhas.append(f'  {linha.strip()}')
        linhas.append('')

    # ── Desmame BZD ───────────────────────────────────────────────────
    desmame = resultado.get('desmame')
    if desmame:
        linhas.append('Desmame de Benzodiazepínico:')
        for chave, texto in desmame.items():
            linhas.append(f'\n[{chave.replace("_"," ").title()}]')
            for linha in texto.split('\n'):
                linhas.append(f'  {linha.strip()}')
        linhas.append('')

    # ── Conduta ───────────────────────────────────────────────────────
    conduta = resultado.get('conduta', [])
    if conduta:
        linhas.append('Conduta:')
        for item in conduta:
            prefix = '  ' if item.startswith('  ') else '• '
            linhas.append(f'{prefix}{item}')

    return '\n'.join(linhas)


# ------------------------------------------------------------------
# ANEMIA — subjetivo + #Plano
# ------------------------------------------------------------------

def _negativas_anemia(dados: dict) -> str:
    """Pertinentes negativas — Anemia."""
    neg = []
    if dados.get('sangramento_ativo') is False:
        neg.append('sangramento ativo')
    if dados.get('ictericia') is False:
        neg.append('icterícia')
    if dados.get('esplenomegalia') is False:
        neg.append('esplenomegalia')
    if dados.get('vegetariano_vegano') is False:
        neg.append('dieta restritiva')
    if dados.get('alcool') is False:
        neg.append('etilismo')
    return _fmt_negativas(neg)


def gerar_subjetivo_anemia(admissao):
    """Texto #Subjetivo — Anemia / Hemograma."""
    dados = _get_dados_modulo(admissao, 'anemia', 'organico')
    if not dados:
        return ''

    partes = []
    hb   = dados.get('hb')
    mcv  = dados.get('mcv')
    sexo = dados.get('sexo', '')

    # Dados do hemograma
    if hb is not None:
        _SEX_LIMIAR = {'masculino': 13.0, 'feminino': 12.0}
        limiar = _SEX_LIMIAR.get(sexo, 12.0)
        if dados.get('gestante'):
            limiar = 11.0
        if hb < limiar:
            deficit = round(limiar - hb, 1)
            _VCM_TIPO = {range(0, 80): 'microcítica', range(80, 101): 'normocítica', range(101, 200): 'macrocítica'}
            tipo = next((v for r, v in _VCM_TIPO.items() if mcv and int(mcv) in r), '')
            partes.append(
                f'Anemia {tipo} — Hb {hb} g/dL ({sexo or "adulto"}, déficit {deficit} g/dL)'
                + (f', VCM {mcv} fL' if mcv else '') + '.'
            )
        else:
            partes.append(f'Hb {hb} g/dL — sem anemia ({sexo or "adulto"}).')
    else:
        partes.append('Queixa de anemia / avaliação de hemograma.')

    # Sintomas relevantes
    sint = []
    if dados.get('sintomas_dispneia'):
        sint.append('dispneia')
    if dados.get('sintomas_palpitacao'):
        sint.append('palpitação')
    if dados.get('sintomas_neurologico'):
        sint.append('sintomas neurológicos')
    if dados.get('ictericia'):
        sint.append('icterícia')
    if dados.get('esplenomegalia'):
        sint.append('esplenomegalia')
    if sint:
        partes.append('Sintomas: ' + ', '.join(sint) + '.')

    # Contexto clínico
    ctx = []
    if dados.get('sangramento_ativo'):
        ctx.append('sangramento ativo')
    if dados.get('doenca_cronica'):
        ctx.append('doença crônica/inflamatória')
    if dados.get('gestante'):
        ctx.append('gestante')
    if dados.get('vegetariano_vegano'):
        ctx.append('vegetariano/vegano')
    if dados.get('alcool'):
        ctx.append('etilismo')
    if dados.get('gastro_cirurgia'):
        ctx.append('cirurgia gástrica prévia')
    if ctx:
        partes.append('Contexto: ' + ', '.join(ctx) + '.')

    # Exames adicionais
    labs = []
    ferr = dados.get('ferritina')
    if ferr is not None:
        labs.append(f'ferritina {ferr} ng/mL')
    b12 = dados.get('b12')
    if b12 is not None:
        labs.append(f'B12 {b12} pg/mL')
    folato = dados.get('folato')
    if folato is not None:
        labs.append(f'folato {folato} ng/mL')
    if labs:
        partes.append('Exames: ' + ', '.join(labs) + '.')

    neg = _negativas_anemia(dados)
    if neg:
        partes.append(neg + '.')

    return ' '.join(partes)


_ANEMIA_CATS = frozenset({
    'anemia_ferropriva', 'talassemia_beta', 'talassemia_alfa',
    'talassemia_beta_maior', 'talassemia_suspeita',
    'anemia_doenca_cronica', 'anemia_micro_indefinida', 'anemia_micro_incompleta',
    'anemia_sangramento', 'anemia_hemolitica',
    'anemia_renal', 'anemia_hipotireoidismo',
    'anemia_b12', 'anemia_folato', 'anemia_alcool',
    'anemia_combinada', 'anemia_reticulocitose', 'anemia_smd',
    'anemia_normo_indefinida', 'anemia_macro_indefinida',
    'sem_anemia', 'pancitopenia',
})


def _plano_anemia(resultado: dict) -> str:
    """Texto para #Plano — Interpretação de Hemograma / Anemia."""
    cat  = resultado.get('categoria', '')
    cid  = _CID_MAP.get(cat, '')
    linhas = []

    # ── Alertas de segurança — sempre no topo ─────────────────────────────────
    for alerta in resultado.get('alertas_seguranca', []):
        linhas.append(alerta)
    if resultado.get('alertas_seguranca'):
        linhas.append('')

    # ── Sem anemia ──────────────────────────────────────────────────────────
    if cat == 'sem_anemia':
        linhas.append('✓ Hemoglobina dentro dos limites — sem anemia.')
        linhas.append(resultado.get('mensagem', ''))
        for c in resultado.get('conduta', []):
            linhas.append(f'• {c}')
        return '\n'.join(linhas)

    # ── Pancitopenia ────────────────────────────────────────────────────────
    if cat == 'pancitopenia':
        cid_pan = _CID_MAP.get('pancitopenia', 'D61.9')
        linhas.append(f'⚠️  PANCITOPENIA — ENCAMINHAMENTO URGENTE — CID-10: {cid_pan}')
        linhas.append('')
        linhas.append(resultado.get('mensagem', ''))
        linhas.append(f'Diagnóstico: {resultado.get("diagnostico", "")}')
        linhas.append('')
        linhas.append('Conduta:')
        for c in resultado.get('conduta', []):
            linhas.append(f'• {c}')
        return '\n'.join(linhas)

    # ── Cabeçalho padrão ────────────────────────────────────────────────────
    hb    = resultado.get('hb', '?')
    mcv   = resultado.get('mcv', '?')
    rdw   = resultado.get('rdw', '?')
    rpi   = resultado.get('rpi')
    grau  = resultado.get('grau', '')
    tipo  = resultado.get('tipo_mcv', '')
    diag  = resultado.get('diagnostico', '')

    _GRAU = {
        'leve': 'Leve', 'moderada': 'Moderada',
        'grave': 'Grave', 'muito_grave': 'Muito Grave',
    }

    cid_str = f' — CID-10: {cid}' if cid else ''
    linhas.append(f'Anemia {tipo} — {_GRAU.get(grau, grau)}{cid_str}')

    # ── Alerta de transfusão ─────────────────────────────────────────────────
    if resultado.get('alerta_transfusao'):
        linhas.append('')
        linhas.append('⚠️  ANEMIA GRAVE — AVALIAR TRANSFUSÃO')
        linhas.append('Critério: Hb < 7 g/dL (ou < 8 g/dL com doença cardiovascular)')

    # ── Exames confirmatórios ────────────────────────────────────────────────
    exames = resultado.get('exames_confirmatórios', [])
    if exames:
        linhas.append('')
        linhas.append('Exames a solicitar / confirmar:')
        for e in exames:
            linhas.append(f'• {e}')

    # ── Tratamento — farmacológico e não farmacológico ───────────────────────
    trat = resultado.get('tratamento', {})
    if trat:
        if isinstance(trat, dict):
            farm = trat.get('farmacologico') or trat.get('primeira_linha')
            nfarm = trat.get('nao_farmacologico')
            admin = trat.get('administracao')
            dur   = trat.get('duracao_monitoramento') or trat.get('duracao')
            resp  = trat.get('resposta')
            atenc = trat.get('atencao')

            if farm:
                linhas.append('')
                linhas.append('Tratamento farmacológico:')
                for linha in farm.split('\n'):
                    linhas.append(f'  {linha.strip()}')
            if admin:
                linhas.append('')
                linhas.append('Como tomar:')
                for linha in admin.split('\n'):
                    linhas.append(f'  {linha.strip()}')
            if dur:
                linhas.append('')
                linhas.append('Duração / monitoramento:')
                for linha in dur.split('\n'):
                    linhas.append(f'  {linha.strip()}')
            if resp:
                linhas.append(f'  Resposta esperada: {resp}')
            if atenc:
                linhas.append('')
                linhas.append(f'⚠️  {atenc}')
            if nfarm:
                linhas.append('')
                linhas.append('Medidas não farmacológicas:')
                for linha in nfarm.split('\n'):
                    linhas.append(f'  {linha.strip()}')

            # demais chaves (hemólise, talassemia, etc.)
            chaves_exibidas = {
                'farmacologico', 'primeira_linha', 'nao_farmacologico',
                'administracao', 'duracao_monitoramento', 'duracao',
                'resposta', 'atencao', 'alternativa', 'alternativa_oral',
                'indicacao_im', 'causa', 'iv',
            }
            for chave, valor in trat.items():
                if chave not in chaves_exibidas and valor:
                    label = chave.replace('_', ' ').title()
                    linhas.append('')
                    linhas.append(f'[{label}]')
                    for linha in str(valor).split('\n'):
                        linhas.append(f'  {linha.strip()}')

        elif isinstance(trat, list):
            linhas.append('')
            linhas.append('Tratamento:')
            for item in trat:
                linhas.append(f'• {item}')

    # ── Encaminhamento ───────────────────────────────────────────────────────
    enc = resultado.get('encaminhamento')
    if enc:
        linhas.append('')
        linhas.append(f'Encaminhamento: {enc}')

    return '\n'.join(linhas)


# ------------------------------------------------------------------
# FADIGA — #Plano
# ------------------------------------------------------------------

_FADIGA_CATS = frozenset({
    'fadiga_red_flags', 'fadiga_secundaria_laboratorial',
    'fadiga_secundaria_apneia', 'fadiga_secundaria_psiquiatrica',
    'fadiga_me_sfc', 'fadiga_idiopatica_subaguda',
})


def _plano_fadiga(resultado: dict) -> str:
    """Texto para #Plano — Fadiga Crônica (6 categorias)."""
    cat    = resultado.get('categoria', '')
    linhas = []

    # ── Alertas de segurança — sempre no topo ─────────────────────────────────
    for alerta in resultado.get('alertas_seguranca', []):
        linhas.append(alerta)
    if resultado.get('alertas_seguranca'):
        linhas.append('')

    # ── RED FLAGS ────────────────────────────────────────────────────
    if cat == 'fadiga_red_flags':
        flags = resultado.get('red_flags', {}).get('flags', [])
        linhas.append('⚠️  RED FLAGS — Investigação Dirigida (não tratar como fadiga primária)')
        for f in flags:
            urg = '🔴' if f.get('urgencia') == 'urgente' else '🟡'
            linhas.append(f"{urg} {f['achado']}")
            linhas.append(f"   → {f['acao']}")
        linhas.append('')
        linhas.append('Retorno: 1–2 semanas ou urgência conforme gravidade do flag.')
        return '\n'.join(linhas)

    # ── CAUSA LABORATORIAL IDENTIFICADA ──────────────────────────────
    if cat == 'fadiga_secundaria_laboratorial':
        lab     = resultado.get('lab', {})
        achados = lab.get('achados', [])
        linhas.append('EXIT STRATEGY — Causa Secundária Identificada')
        linhas.append('Tratar causa base antes de avançar o algoritmo de fadiga primária.')
        linhas.append('')
        for a in achados:
            linhas.append(f"• {a['lab']} {a['valor']}: {a['achado']}")
            linhas.append(f"  Tratamento: {a['tratamento']}")
            if a.get('encaminhar'):
                linhas.append(f"  Encaminhar: {a['encaminhar']}")
        linhas.append('')
        linhas.append('Reavaliação: 8–12 semanas após início do tratamento.')
        linhas.append('Se fadiga persistir após correção → prosseguir algoritmo.')
        return '\n'.join(linhas)

    # ── APNEIA OBSTRUTIVA DO SONO ─────────────────────────────────────
    if cat == 'fadiga_secundaria_apneia':
        sb = resultado.get('stopbang', 0)
        linhas.append(f'Apneia Obstrutiva do Sono — STOP-BANG = {sb}/8 (Alto Risco)')
        linhas.append('')
        linhas.append('Conduta:')
        linhas.append('• Encaminhar: polissonografia ou oximetria noturna como triagem')
        linhas.append('• Perda de peso se IMC elevado (↓ ~1 evento/h por kg perdido)')
        linhas.append('• Suspender álcool e benzodiazepínicos à noite')
        linhas.append('• Posição lateral (decúbito lateral preferencial ao supino)')
        linhas.append('• CPAP: indicado se IAH ≥ 15 ou ≥ 5 com sintomas')
        linhas.append('  → Encaminhar Pneumologia/Otorrino para titulação de CPAP')
        linhas.append('')
        linhas.append('Reavaliação: após polissonografia + 4 semanas de CPAP (se indicado).')
        return '\n'.join(linhas)

    # ── CAUSA PSIQUIÁTRICA (depressão/ansiedade, sem PEM) ────────────
    if cat == 'fadiga_secundaria_psiquiatrica':
        phq2 = resultado.get('phq2', 0)
        gad2 = resultado.get('gad2', 0)
        linhas.append('Fadiga de Etiologia Psiquiátrica (PEM ausente)')
        linhas.append('')
        if phq2 >= 3:
            linhas.append(f'• PHQ-2 = {phq2}/6 → Triagem positiva para Depressão')
            linhas.append('  → Aplicar PHQ-9 completo; se PHQ-9 ≥ 10: ISRS 1ª linha')
            linhas.append('  → Sertralina 50 mg/dia (titular até 100–200 mg) OU')
            linhas.append('     Escitalopram 10 mg/dia (titular até 20 mg)')
        if gad2 >= 3:
            linhas.append(f'• GAD-2 = {gad2}/6 → Triagem positiva para Ansiedade')
            linhas.append('  → Aplicar GAD-7 completo; se GAD-7 ≥ 10: ISRS 1ª linha')
        linhas.append('')
        linhas.append('⚠️  PEM ausente — exercício gradual PODE ser indicado')
        linhas.append('   (ao contrário de ME/SFC, onde GET é contraindicado)')
        linhas.append('')
        linhas.append('Conduta adicional:')
        linhas.append('• TCC (Terapia Cognitivo-Comportamental) — encaminhar psicologia')
        linhas.append('• Higiene do sono e ativação comportamental')
        linhas.append('• Reavaliação: 4 semanas (resposta ao ISRS esperada em 4–6 sem)')
        linhas.append('')
        linhas.append('⚠️  PHQ-2/GAD-2 positivos NÃO excluem ME/SFC se PEM surgir.')
        return '\n'.join(linhas)

    # ── ME/SFC — critérios IOM 2015 completos ────────────────────────
    if cat == 'fadiga_me_sfc':
        criterios = resultado.get('criterios', {})
        dur       = criterios.get('duracao', 0)
        adicionais = []
        if criterios.get('brain_fog'):  adicionais.append('brain fog/disfunção cognitiva')
        if criterios.get('ortostase'):  adicionais.append('intolerância ortostática')
        adic_str = ', '.join(adicionais) if adicionais else '—'
        linhas.append(f'Encefalomielite Miálgica / SFC — IOM 2015 ({dur} meses)')
        linhas.append(f'Tríade: redução de atividade + PEM + sono não-reparador')
        linhas.append(f'Critério adicional presente: {adic_str}')
        linhas.append('')
        linhas.append('🔴 GET (Graded Exercise Therapy) CONTRAINDICADO — NICE 2021')
        linhas.append('   Risco de agravamento permanente por PEM desencadeado por esforço.')
        linhas.append('')
        linhas.append('Conduta — PACING (estratégia central):')
        linhas.append('• Estabelecer linha de base sustentável sem desencadear PEM')
        linhas.append('• Fragmentar atividades em blocos curtos + descanso ativo entre eles')
        linhas.append('• Evitar ciclo boom-bust — descansar também nos dias bons')
        linhas.append('• Aumentar atividade somente após semanas–meses de estabilidade (5–10%/vez)')
        linhas.append('')
        linhas.append('Manejo sintomático:')
        linhas.append('• Sono: higiene rigorosa; melatonina 0,5–3 mg; trazodona 25–50 mg se refratário')
        if criterios.get('ortostase'):
            linhas.append('• Intolerância ortostática: hidratação 2–3 L/dia, sal aumentado,')
            linhas.append('  meia compressiva 30–40 mmHg, elevar cabeceira 10–15°')
        linhas.append('• Dor: paracetamol/AINE em doses regulares; naltrexona LDN off-label')
        linhas.append('• Brain fog: pacing cognitivo (limitação de estimulação sensorial)')
        linhas.append('')
        linhas.append('Encaminhar: Ambulatório de ME/SFC ou Neurologista com interesse na síndrome.')
        return '\n'.join(linhas)

    # ── FADIGA IDIOPÁTICA / SUBAGUDA ─────────────────────────────────
    if cat == 'fadiga_idiopatica_subaguda':
        criterios  = resultado.get('criterios', {})
        faltando   = criterios.get('faltando', [])
        dur        = criterios.get('duracao', 0)
        nice_poss  = criterios.get('nice_possivel', False)
        lab_pend   = resultado.get('lab_pendente', False)
        phq2       = resultado.get('phq2', 0)
        stopbang   = resultado.get('stopbang', 0)

        titulo = f'Fadiga Crônica — Critérios IOM 2015 Incompletos ({dur} meses)'
        if nice_poss:
            titulo += ' — NICE 2021 possível (≥ 4 meses)'
        linhas.append(titulo)

        if faltando:
            linhas.append('Critérios ainda ausentes: ' + '; '.join(faltando) + '.')
        linhas.append('')

        linhas.append('Conduta:')
        if lab_pend:
            linhas.append('• Solicitar painel laboratorial:')
            linhas.append('  Hemograma, ferritina, TSH, glicemia, creatinina, ALT,')
            linhas.append('  VHS, PCR, vitamina B12, 25-OH vitamina D')
        linhas.append('• Higiene do sono: horário regular, sem telas 1h antes, quarto escuro e fresco')
        linhas.append('• Atividade física leve (caminhada 10–20 min, 3×/sem) SE tolerada sem piora')
        linhas.append('• Pacing leve — conservação de energia, evitar sobrecarga')
        if phq2 >= 2:
            linhas.append(f'• PHQ-2 = {phq2} — aplicar PHQ-9 completo (rastreio de depressão)')
        if stopbang >= 3:
            linhas.append(f'• STOP-BANG = {stopbang} — considerar triagem para apneia do sono')
        linhas.append('')
        linhas.append('Reavaliação: 4–8 semanas — reclassificar se critérios IOM evoluírem.')
        linhas.append('Se PEM surgir → reavaliar para ME/SFC (interromper exercício gradual).')
        return '\n'.join(linhas)

    return ''


# ------------------------------------------------------------------
# MSK — #Plano (genérico — joelho, ombro, coluna, fibromialgia,
#               quadril, tornozelo/pé, mão/punho)
# ------------------------------------------------------------------

_MSK_CATS = frozenset({
    # joelho / coluna (categorias compartilhadas)
    'avaliacao_completa', 'padrao_inflamatorio', 'red_flag_emergencia',
    # ombro
    'avaliacao_ombro', 'red_flag_ombro',
    # fibromialgia
    'fibromialgia_confirmada', 'criterios_insuficientes', 'investigar_causa_secundaria',
    # quadril
    'red_flag_quadril', 'avaliacao_quadril',
    # tornozelo / pé
    'trauma_ottawa_positivo', 'entorse_tornozelo', 'fasciite_plantar',
    'tendinopatia_aquiles', 'morton_neuroma', 'avaliacao_tornozelo_pe', 'red_flag_tornozelo_pe',
    # mão / punho
    'trauma_escafoide_suspeito', 'tunel_do_carpo', 'de_quervain', 'dedo_em_gatilho',
    'rizartrose_thumb_cmc', 'suspeita_artrite_reumatoide', 'avaliacao_mao_punho', 'red_flag_mao_punho',
})


def _plano_msk(resultado):
    """Texto para #Plano — módulos MSK (genérico)."""
    categoria = resultado.get('categoria', '')
    diag      = resultado.get('diagnostico', '') or categoria.replace('_', ' ').title()
    linhas    = [f'MSK — {diag}']

    # ── Red flag de emergência ────────────────────────────────────────────────
    rf = resultado.get('red_flags', {})
    if isinstance(rf, dict) and rf.get('tem_emergencia'):
        linhas += ['', '⚠️  RED FLAG DE EMERGÊNCIA — encaminhar imediatamente.']
        for alerta in rf.get('alertas', []):
            if isinstance(alerta, dict):
                achado = alerta.get('achado', '')
                acao   = alerta.get('acao', '')
                linhas.append(f'  [!] {achado}' + (f' → {acao}' if acao else ''))
            else:
                linhas.append(f'  [!] {alerta}')
        return '\n'.join(linhas)

    # ── Flat dict: trauma / fibromialgia / casos sem hipoteses aninhadas ─────
    if not resultado.get('hipoteses_provaveis') and not resultado.get('hipoteses_possiveis'):
        conduta = resultado.get('conduta', [])
        farm    = resultado.get('farmacologico', [])
        if conduta:
            linhas.append('')
            for item in conduta:
                if any(k in item for k in _ENC_KW):
                    linhas.append(f'→ {item}')
                else:
                    linhas.append(f'• {item}')
        if farm:
            linhas += ['', 'Farmacológico:']
            for item in farm:
                linhas.append(f'  {item}')
        img = resultado.get('imagem')
        if img:
            linhas += ['', f'Imagem: {img}']
        enc = resultado.get('encaminhar')
        if enc:
            linhas += ['', f'→ Encaminhar: {enc}']
        return '\n'.join(linhas)

    # ── Nested hipoteses (padrão principal — joelho, ombro, coluna…) ─────────
    for grupo, titulo in [
        ('hipoteses_provaveis', 'Hipóteses prováveis'),
        ('hipoteses_possiveis', 'Hipóteses possíveis'),
    ]:
        hips = resultado.get(grupo, [])
        if not hips:
            continue
        linhas += ['', f'{titulo}:']
        for h in hips:
            nome = (h.get('hipotese') or h.get('diagnostico') or '').replace('_', ' ').title()
            linhas += ['', f'[{nome}]']

            for item in h.get('conduta', []):
                if any(k in item for k in _ENC_KW):
                    linhas.append(f'→ {item}')
                else:
                    linhas.append(f'• {item}')

            farm = h.get('farmacologico', [])
            if farm:
                linhas += ['', 'Farmacológico:']
                for item in farm:
                    linhas.append(f'  {item}')

            img = h.get('imagem')
            if img:
                linhas.append(f'  Imagem: {img}')

            enc = h.get('encaminhar')
            if enc:
                linhas.append(f'→ Encaminhar: {enc}')

    # Hipóteses de exclusão (quando sem prováveis — sugerir o diferencial)
    if not resultado.get('hipoteses_provaveis'):
        exclusao = resultado.get('hipoteses_exclusao', [])
        if exclusao:
            linhas += ['', 'Excluir: ' + ', '.join(str(e).replace('_', ' ') for e in exclusao) + '.']

    return '\n'.join(linhas)


# ------------------------------------------------------------------
# PALPITAÇÃO — subjetivo + negativas
# ------------------------------------------------------------------

_RITMO_LABEL_PAL = {
    'acelerado_regular':   'coração acelerado e regular',
    'acelerado_irregular': 'coração acelerado e irregular',
    'batida_extra':        'batida extra / "flip"',
    'pausa':               'pausa / "coração para"',
    'forte_mas_normal':    'batimento forte com ritmo normal',
    'indeterminado':       'ritmo não caracterizável pelo paciente',
}
_DUR_LABEL_PAL = {
    'segundos':   '< 30 s',
    'minutos':    '1–30 min',
    'horas':      '> 30 min',
    'persistente': 'persistente',
}


def _negativas_palpitacao(dados: dict) -> str:
    neg = []
    if dados.get('sincope') is False:
        neg.append('síncope')
    if dados.get('dor_toracica') is False:
        neg.append('dor torácica')
    if dados.get('instabilidade_hemodinamica') is False:
        neg.append('instabilidade hemodinâmica')
    if dados.get('morte_subita_familiar') is False:
        neg.append('morte súbita familiar')
    if dados.get('uso_cocaina_estimulante') is False:
        neg.append('substâncias estimulantes')
    if dados.get('cardiopatia_estrutural') is False:
        neg.append('cardiopatia estrutural')
    return _fmt_negativas(neg)


def gerar_subjetivo_palpitacao(admissao):
    dados = _get_dados_modulo(admissao, 'palpitacao', 'organico')
    if not dados:
        return ''

    partes = []

    # Caracterização
    ritmo = _RITMO_LABEL_PAL.get(dados.get('ritmo_percebido', ''), '')
    dur   = _DUR_LABEL_PAL.get(dados.get('duracao_episodio', ''), '')
    if ritmo:
        desc = f'Palpitação — {ritmo}'
        if dur:
            desc += f', duração {dur}'
        if dados.get('inicio_subito') and dados.get('termino_subito'):
            desc += ', início e término súbitos'
        elif dados.get('inicio_subito'):
            desc += ', início súbito'
        partes.append(desc + '.')

    # Contexto: repouso / esforço / primeiro episódio
    ctx = []
    if dados.get('em_repouso'):        ctx.append('em repouso')
    if dados.get('ao_esforco'):        ctx.append('ao esforço')
    if dados.get('primeiro_episodio'): ctx.append('primeiro episódio na vida')
    if ctx:
        partes.append(', '.join(ctx).capitalize() + '.')

    # Red flags sintomáticos
    rf_sint = []
    if dados.get('sincope'):         rf_sint.append('síncope')
    if dados.get('presincope'):      rf_sint.append('pré-síncope')
    if dados.get('dor_toracica'):    rf_sint.append('dor torácica')
    if dados.get('dispneia_grave'):  rf_sint.append('dispneia grave')
    if dados.get('sudorese_fria'):   rf_sint.append('sudorese fria')
    if dados.get('confusao_mental'): rf_sint.append('confusão mental')
    if rf_sint:
        partes.append('SINAIS DE ALARME: ' + ', '.join(rf_sint) + '.')

    # Gatilhos
    gat = []
    if dados.get('gatilho_cafeina_alcool'): gat.append('cafeína/álcool')
    if dados.get('gatilho_estresse'):       gat.append('estresse/pânico')
    if dados.get('gatilho_exercicio'):      gat.append('exercício')
    if dados.get('gatilho_pos_refeicao'):   gat.append('pós-refeição')
    if dados.get('gatilho_decubito'):       gat.append('decúbito lateral esquerdo')
    if gat:
        partes.append('Gatilho: ' + ', '.join(gat) + '.')

    # Fármacos e substâncias
    farm = []
    if dados.get('uso_simpaticomimatico'):    farm.append('simpaticomimético')
    if dados.get('uso_hormonio_tireoidiano'): farm.append('levotiroxina')
    if dados.get('uso_antiarritmico'):        farm.append('antiarrítmico/tricíclico')
    if dados.get('uso_cocaina_estimulante'):  farm.append('cocaína/estimulantes')
    if farm:
        partes.append('Fármacos/substâncias: ' + ', '.join(farm) + '.')

    # Comorbidades
    comorbs = []
    if dados.get('cardiopatia_estrutural'): comorbs.append('cardiopatia estrutural')
    if dados.get('has'):                    comorbs.append('HAS')
    if dados.get('dm'):                     comorbs.append('DM')
    if dados.get('avc_previo'):             comorbs.append('AVC/AIT prévio')
    if dados.get('fa_conhecida'):           comorbs.append('FA conhecida')
    if comorbs:
        partes.append('Comorbidades: ' + ', '.join(comorbs) + '.')

    # Histórico familiar
    fam = []
    if dados.get('morte_subita_familiar'):   fam.append('morte súbita < 40 anos')
    if dados.get('cardiomiopatia_familiar'): fam.append('cardiomiopatia/Brugada familiar')
    if fam:
        partes.append('HF: ' + ', '.join(fam) + '.')

    # ECG
    if dados.get('ecg_disponivel'):
        ritmo_ecg = dados.get('ecg_ritmo', '')
        fc_ecg    = dados.get('ecg_fc')
        ecg_str   = f'ECG: {ritmo_ecg}'
        if fc_ecg:
            ecg_str += f' FC {fc_ecg} bpm'
        if dados.get('ecg_qt_longo'):  ecg_str += ', QTc prolongado'
        if dados.get('ecg_brugada'):   ecg_str += ', padrão Brugada'
        if dados.get('ecg_bve'):       ecg_str += ', BRE novo'
        partes.append(ecg_str + '.')

    # CHA₂DS₂-VASc (se calculado)
    if 'cha2ds2_score' in dados:
        score = dados['cha2ds2_score']
        partes.append(
            f'CHA₂DS₂-VASc = {score}' +
            (' → anticoagulação indicada' if dados.get('anticoagulacao_indicada') else '') +
            '.'
        )

    neg = _negativas_palpitacao(dados)
    if neg:
        partes.append(neg + '.')

    return ' '.join(partes)


# ------------------------------------------------------------------
# URINÁRIO — subjetivo + negativas
# ------------------------------------------------------------------

_QUEIXA_LABEL_URIN = {
    'sintomas_miccionais_baixos': 'Sintomas miccionais baixos',
    'hematuria_macro':            'Hematúria macroscópica',
    'secrecao_uretral':           'Corrimento uretral',
    'corrimento_vaginal':         'Corrimento vaginal',
    'dor_pelvica':                'Dor pélvica/perineal',
    'incontinencia_urinaria':     'Incontinência urinária',
    'outras_queixas_urinarias':   'Queixa urinária',
}


def _negativas_urinario(dados: dict) -> str:
    neg = []
    if dados.get('febre') is False:            neg.append('febre')
    if dados.get('calafrio') is False:         neg.append('calafrio')
    if dados.get('dor_lombar') is False:       neg.append('dor lombar')
    if dados.get('ppd_positivo') is False:     neg.append('punho-percussão lombar negativa')
    if dados.get('hematuria_macro') is False:  neg.append('hematúria macroscópica')
    if dados.get('hematuria_indolor') is False: neg.append('hematúria indolor')
    if dados.get('secrecao_uretral') is False and dados.get('secrecao_vaginal') is False:
        neg.append('corrimento/secreção genital')
    if dados.get('ist_risco') is False:        neg.append('risco de IST')
    if dados.get('gestante') is False:         neg.append('gestação')
    if dados.get('hipotensao') is False:       neg.append('instabilidade hemodinâmica')
    return _fmt_negativas(neg)


def gerar_subjetivo_urinario(admissao):
    dados = _get_dados_modulo(admissao, 'urinario', 'organico')
    if not dados:
        return ''

    partes = []
    sexo = dados.get('sexo', '')

    # Queixa principal
    qp = _QUEIXA_LABEL_URIN.get(dados.get('queixa_principal', ''), 'Queixa urinária')
    partes.append(qp)

    # Sintomas miccionais
    sint = []
    if dados.get('disuria'):       sint.append('disúria')
    if dados.get('frequencia'):    sint.append('polaciúria')
    if dados.get('urgencia'):      sint.append('urgência miccional')
    if dados.get('nocturia'):      sint.append('noctúria')
    if dados.get('dor_suprapubica'): sint.append('dor suprapúbica')
    if sint:
        partes.append(', '.join(sint))

    # Hematúria
    if dados.get('hematuria_macro'):
        partes.append('hematúria macroscópica')
    elif dados.get('hematuria_micro'):
        partes.append('hematúria microscópica')

    # Sistêmicos — pielonefrite / sepse
    sist = []
    if dados.get('febre'):    sist.append('febre')
    if dados.get('calafrio'): sist.append('calafrio')
    if dados.get('dor_lombar') or dados.get('ppd_positivo'):
        sist.append('dor lombar' + (' com PPD +' if dados.get('ppd_positivo') else ''))
    if dados.get('nausea_vomito'): sist.append('náusea/vômito')
    if sist:
        partes.append(', '.join(sist))

    # Feminino — corrimento
    if sexo == 'F':
        if dados.get('secrecao_vaginal'):
            tipo = dados.get('corrimento_tipo', '')
            partes.append('corrimento vaginal' + (f' ({tipo})' if tipo else ''))
        if dados.get('prurido_genital'):  partes.append('prurido genital')
        if dados.get('lesao_genital'):    partes.append('lesão genital')
        if dados.get('gestante'):
            sem = dados.get('semanas_gestacao', '?')
            partes.append(f'gestante ({sem} semanas)')

    # Masculino — próstata / uretral
    if sexo == 'M':
        sint_m = []
        if dados.get('hesitancia'):           sint_m.append('hesitância')
        if dados.get('jato_fraco'):           sint_m.append('jato fraco')
        if dados.get('gotejamento_terminal'): sint_m.append('gotejamento terminal')
        if dados.get('secrecao_uretral'):     sint_m.append('corrimento uretral')
        if dados.get('dor_perineal'):         sint_m.append('dor perineal')
        if sint_m:
            partes.append(', '.join(sint_m))

    neg = _negativas_urinario(dados)
    if neg:
        partes.append(neg)

    return _partes_para_texto(partes, separador='. ')


# ------------------------------------------------------------------
# ORGÂNICO — GOTA / ARTRITE POR CRISTAIS DE URATO
# ------------------------------------------------------------------

def _negativas_gota(dados: dict) -> str:
    """Pertinentes negativas documentadas no #Subjetivo — Gota."""
    neg = []
    if dados.get('febre_385') is False:
        neg.append('febre')
    if dados.get('aparencia_toxica') is False:
        neg.append('aparência tóxica')
    if dados.get('tophi_presentes') is False:
        neg.append('tophi visíveis')
    if dados.get('anticoagulado') is False:
        neg.append('anticoagulante em uso')
    if dados.get('imunossupressao') is False:
        neg.append('imunossupressão')
    return _fmt_negativas(neg)


def gerar_subjetivo_gota(admissao):
    dados = _get_dados_modulo(admissao, 'gota', 'organico')
    if not dados:
        return ''

    partes = []
    sexo_m = dados.get('sexo_masculino', True)
    sexo   = 'masculino' if sexo_m else 'feminino'
    idade  = dados.get('idade', '?')

    if dados.get('ataque_atual'):
        arts = dados.get('articulacoes', 'articulação não especificada')
        n    = dados.get('n_articulacoes_afetadas', 1) or 1
        mono = 'mono-artrite' if n == 1 else f'oligo-artrite ({n} articulações)'
        partes.append(f'Paciente {sexo} de {idade} anos com {mono} aguda — {arts}')
        if dados.get('inicio_em_1_dia'):
            partes.append('início em menos de 24h')
        if dados.get('vermelhidao'):
            partes.append('vermelhidão articular')
    else:
        partes.append(f'Paciente {sexo} de {idade} anos em período intercrítico de gota')

    if dados.get('tophi_presentes'):
        partes.append('tophi visíveis')

    n_ataques = dados.get('n_ataques_ano', 0) or 0
    if n_ataques:
        partes.append(f'{n_ataques} ataque{"s" if n_ataques != 1 else ""} no último ano')

    if dados.get('ataque_previo'):
        partes.append('ataque articular semelhante prévio')

    urato = dados.get('urato_mgdl')
    if urato is not None:
        partes.append(f'ácido úrico = {urato:.1f} mg/dL')

    if dados.get('has_ou_cardiovascular'):
        partes.append('HAS / doença cardiovascular')

    # Red flags
    rf = []
    if dados.get('febre_385'):
        rf.append('febre ≥ 38,5°C')
    if dados.get('aparencia_toxica'):
        rf.append('aparência tóxica')
    if dados.get('imunossupressao'):
        rf.append('imunossupressão')
    if rf:
        partes.append('⚠️ Red flags: ' + ', '.join(rf))

    egfr = dados.get('egfr')
    if egfr is not None:
        partes.append(f'eGFR {int(egfr)} mL/min')

    if dados.get('ja_usa_ult'):
        qual      = dados.get('qual_ult', 'hipouricemiante')
        urato_ult = dados.get('urato_atual_mgdl')
        ult_str   = f'em uso de {qual}'
        if urato_ult is not None:
            alvo = '(meta atingida)' if urato_ult < 6.0 else '(acima da meta < 6,0)'
            ult_str += f', urato {urato_ult:.1f} mg/dL {alvo}'
        partes.append(ult_str)

    neg = _negativas_gota(dados)
    if neg:
        partes.append(neg)

    return _partes_para_texto(partes, separador='. ')


def gerar_objetivo_gota(admissao):
    return ''


# ------------------------------------------------------------------
# ORGÂNICO — SÍNCOPE
# ------------------------------------------------------------------

def gerar_subjetivo_sincope(admissao):
    dados = _get_dados_modulo(admissao, 'sincope', 'organico')
    if not dados: return ''
    partes = []
    idade = dados.get('idade', '?')
    if dados.get('sincope_esforco'):
        partes.append(f'Paciente de {idade} anos com síncope aos esforços')
    elif dados.get('sintomas_ao_levantar'):
        partes.append(f'Paciente de {idade} anos com síncope ao ortostatismo')
    else:
        partes.append(f'Paciente de {idade} anos com episódio de síncope')
    if dados.get('prodrome_nausea_diaforese') or dados.get('prodrome_visual'):
        partes.append('com pródromo (náusea/diaforese/escurecimento visual)')
    else:
        partes.append('sem pródromo relatado')
    if dados.get('gatilho_posicional'): partes.append('gatilho: ortostatismo prolongado')
    if dados.get('gatilho_emocional'):  partes.append('gatilho: emoção/dor')
    if dados.get('gatilho_miccao'):     partes.append('gatilho: micção/defecação/tosse')
    if dados.get('recuperacao_rapida'): partes.append('recuperação rápida e espontânea')
    if dados.get('palpitacao_antes'):   partes.append('palpitação antes do episódio')
    if dados.get('doenca_estrutural_cardiaca'): partes.append('⚠️ cardiopatia estrutural conhecida')
    if dados.get('ecg_realizado'):
        ecg_achs = []
        if dados.get('ecg_qtc_maior_480'): ecg_achs.append('QTc>480ms')
        if dados.get('ecg_brugada'):       ecg_achs.append('padrão Brugada')
        if dados.get('ecg_bav3'):          ecg_achs.append('BAV 3º grau')
        if ecg_achs: partes.append('ECG: ' + ', '.join(ecg_achs))
        else: partes.append('ECG realizado sem alterações de alarme')
    if dados.get('pa_ortostatica_medida'):
        if dados.get('queda_pas_20'): partes.append('queda PA sistólica ≥ 20 mmHg ao ortostatismo')
    return _partes_para_texto(partes, separador='. ')

def gerar_objetivo_sincope(admissao): return ''


# ------------------------------------------------------------------
# ORGÂNICO — FEBRE SEM FOCO
# ------------------------------------------------------------------

def gerar_subjetivo_febre(admissao):
    dados = _get_dados_modulo(admissao, 'febre', 'organico')
    if not dados: return ''
    partes = []
    idade = dados.get('idade', '?')
    temp  = dados.get('temperatura_max')
    dias  = dados.get('dias_febre')
    cab = f'Paciente de {idade} anos com febre'
    if temp: cab += f' (Tmáx {temp}°C)'
    if dias is not None: cab += f' há {dias} dia(s)'
    partes.append(cab)

    if dados.get('calafrio_rigor'):    partes.append('com calafrio com rigor')
    if dados.get('sudorese_noturna'):  partes.append('sudorese noturna')

    # Foco localizatório
    _FOCOS = [('foco_faringeo','faríngeo'), ('foco_respiratorio','respiratório'),
              ('foco_urinario','urinário'), ('foco_gi','gastrointestinal'),
              ('foco_pele_partes_moles','pele/partes moles'), ('artralgia_artrite','articular')]
    focos = [nome for chave, nome in _FOCOS if dados.get(chave)]
    if focos:
        partes.append('foco localizatório: ' + ', '.join(focos))
    if dados.get('exantema'):
        tipo = dados.get('exantema_tipo', '')
        partes.append(f'exantema{(" " + tipo) if tipo else ""}')

    # Red flags presentes
    _RF = [('peticuias_purpura','petéquias/púrpura'), ('rigidez_nuca','rigidez de nuca'),
           ('hipotensao','hipotensão'), ('taquicardia_fc_120','FC ≥ 120'),
           ('alt_consciencia','alteração de consciência'), ('aparencia_toxica','aparência toxêmica')]
    rfs = [nome for chave, nome in _RF if dados.get(chave)]
    if rfs:
        partes.append('⚠️ sinais de alarme: ' + ', '.join(rfs))

    # Imunossupressão
    _IMU = [('imunossupressao_grave','imunossupressão grave'), ('neutropenia','neutropenia'),
            ('asplenia','asplenia'), ('corticoide_cronico_alto','corticoide alto')]
    imu = [nome for chave, nome in _IMU if dados.get(chave)]
    if imu:
        partes.append('imunidade: ' + ', '.join(imu))

    # Epidemiologia
    _EPI = [('viagem_area_endemica','viagem a área endêmica'), ('contato_animal','contato com animais'),
            ('picada_carrapato_inseto','picada de carrapato/inseto'),
            ('internacao_recente_30d','internação recente'), ('uso_atb_recente','ATB recente'),
            ('contato_tb','contato com TB')]
    epi = [nome for chave, nome in _EPI if dados.get(chave)]
    if epi:
        partes.append('epidemiologia: ' + ', '.join(epi))

    txt = _partes_para_texto(partes, separador='. ')

    # ── Negativas pertinentes ────────────────────────────────────────────────
    _NEG = [
        ('peticuias_purpura',   'petéquias'),
        ('rigidez_nuca',        'rigidez de nuca'),
        ('alt_consciencia',     'alteração de consciência'),
        ('foco_respiratorio',   'sintomas respiratórios'),
        ('foco_urinario',       'sintomas urinários'),
        ('foco_gi',             'sintomas gastrointestinais'),
        ('foco_faringeo',       'odinofagia'),
        ('exantema',            'exantema'),
        ('viagem_area_endemica','viagem recente'),
        ('imunossupressao_grave','imunossupressão'),
    ]
    negs = [nome for chave, nome in _NEG if dados.get(chave) is False]
    if negs:
        txt += ' Nega: ' + ', '.join(negs) + '.'
    return txt

def gerar_objetivo_febre(admissao): return ''


# ------------------------------------------------------------------
# ORGÂNICO — SANGRAMENTO ANORRETAL / PRURIDO ANAL
# ------------------------------------------------------------------

def gerar_subjetivo_anorretal(admissao):
    dados = _get_dados_modulo(admissao, 'anorretal', 'organico')
    if not dados: return ''
    partes = []
    idade = dados.get('idade', '?')
    if dados.get('sangramento_principal') and dados.get('prurido_perianal'):
        partes.append(f'Paciente de {idade} anos com sangramento anorretal e prurido perianal')
    elif dados.get('sangramento_principal'):
        partes.append(f'Paciente de {idade} anos com sangramento anorretal')
    elif dados.get('prurido_perianal'):
        partes.append(f'Paciente de {idade} anos com prurido perianal')
    else:
        partes.append(f'Paciente de {idade} anos com queixa anorretal')
    if dados.get('sangramento_no_papel'): partes.append('sangue no papel/superfície das fezes')
    if dados.get('sangue_misturado_fezes'): partes.append('⚠️ sangue misturado às fezes')
    if dados.get('dor_durante_defecacao'): partes.append('dor intensa à defecação')
    if dados.get('prolapso_irredutivel'): partes.append('⚠️ prolapso irredutível')
    elif dados.get('prolapso_reducao_manual'): partes.append('prolapso com redução manual')
    elif dados.get('prolapso_reducao_espontanea'): partes.append('prolapso com redução espontânea')
    if dados.get('hemorroida_trombosada_externa'):
        h = dados.get('horas_desde_trombose', '?')
        partes.append(f'hemorroida externa trombosada há {h}h')
    neg = []
    if dados.get('perda_peso_involuntaria') is False: neg.append('perda de peso')
    if dados.get('mudanca_habito_intestinal_4sem') is False: neg.append('alteração de hábito intestinal')
    if neg: partes.append(_fmt_negativas(neg))
    return _partes_para_texto(partes, separador='. ')

def gerar_objetivo_anorretal(admissao): return ''


# ------------------------------------------------------------------
# ORGÂNICO — EDEMA DE MEMBROS INFERIORES
# ------------------------------------------------------------------

def gerar_subjetivo_edema(admissao):
    dados = _get_dados_modulo(admissao, 'edema', 'organico')
    if not dados: return ''
    partes = []
    lateral = dados.get('lateralidade', 'bilateral')
    inicio  = 'agudo' if dados.get('inicio_agudo') else 'crônico'
    partes.append(f'Edema {lateral} {inicio} de membros inferiores')

    # ── Positivos ────────────────────────────────────────────────────────────
    if dados.get('edema_nao_depressivel'):    partes.append('edema não depressível (borrachudo)')
    if dados.get('edema_facial'):             partes.append('edema facial associado')
    if dados.get('dor_trajeto_venoso'):       partes.append('dor no trajeto venoso')
    if dados.get('eritema_calor_local'):      partes.append('eritema e calor local')
    if dados.get('porta_entrada_ou_infeccao'):partes.append('porta de entrada/infecção')
    if dados.get('edema_toda_perna'):         partes.append('edema de toda a perna')
    if dados.get('edema_panturrilha_assim'):  partes.append('panturrilha assimétrica > 3 cm')
    if dados.get('veias_colaterais'):         partes.append('veias colaterais')
    if dados.get('tvp_previa'):               partes.append('TVP prévia')
    if dados.get('cancer_ativo'):             partes.append('câncer ativo')
    if dados.get('repouso_cirurgia_recente'): partes.append('imobilização/cirurgia recente')
    if dados.get('dispneia_esforco'):         partes.append('dispneia aos esforços/ortopneia')
    if dados.get('bnp_elevado'):              partes.append('BNP elevado')
    if dados.get('proteinuria_pesada'):       partes.append('proteinúria intensa')
    if dados.get('cirrose_conhecida'):        partes.append('cirrose hepática')
    if dados.get('ascite'):                   partes.append('ascite')
    if dados.get('ictericia'):                partes.append('icterícia/hipoalbuminemia hepática')
    if dados.get('hiperpigmentacao_pernas'):  partes.append('hiperpigmentação/lipodermatoesclerose')
    if dados.get('varizes'):                  partes.append('varizes visíveis')
    if dados.get('mixedema_pretibial'):       partes.append('mixedema pré-tibial')
    if dados.get('tsh_elevado'):
        tsh = dados.get('tsh_valor')
        partes.append(f'TSH elevado ({tsh} mUI/L)' if tsh else 'TSH elevado')
    if dados.get('cirurgia_linfonodos'):      partes.append('cirurgia de linfonodos/radioterapia prévia')
    if dados.get('hipoalbuminemia'):          partes.append('hipoalbuminemia')
    if dados.get('sinais_sistemicos'):        partes.append('sinais sistêmicos (febre/emagrecimento)')
    if dados.get('apneia_sono'):              partes.append('apneia do sono')

    # Medicamentos causadores
    _MEDS = [('usa_bcc','BCC'), ('usa_aine','AINE'), ('usa_corticoide','corticoide'),
             ('usa_gabapentina','gabapentina/pregabalina'), ('usa_tiazolidiona','pioglitazona'),
             ('usa_hormonio','hormônio')]
    farm = [nome for chave, nome in _MEDS if dados.get(chave)]
    if farm: partes.append('medicamentos em uso: ' + ', '.join(farm))

    txt = _partes_para_texto(partes, separador='. ')

    # ── Negativas pertinentes (só as explicitamente negadas — is False) ───────
    _NEG = [
        ('dor_trajeto_venoso',       'dor no trajeto venoso'),
        ('eritema_calor_local',      'eritema/calor local'),
        ('edema_panturrilha_assim',  'assimetria de panturrilha'),
        ('tvp_previa',               'TVP prévia'),
        ('cancer_ativo',             'câncer ativo'),
        ('dispneia_esforco',         'dispneia/ortopneia'),
        ('proteinuria_pesada',       'proteinúria'),
        ('cirrose_conhecida',        'cirrose'),
        ('sinais_sistemicos',        'sinais sistêmicos'),
    ]
    negs = [nome for chave, nome in _NEG if dados.get(chave) is False]
    if negs:
        txt += ' Nega: ' + ', '.join(negs) + '.'

    return txt

def gerar_objetivo_edema(admissao): return ''


# ------------------------------------------------------------------
# ORGÂNICO — ICTERÍCIA
# ------------------------------------------------------------------

def gerar_subjetivo_ictericia(admissao):
    dados = _get_dados_modulo(admissao, 'ictericia', 'organico')
    if not dados: return ''
    partes = []
    idade = dados.get('idade', '?')
    partes.append(f'Paciente de {idade} anos com icterícia')
    if dados.get('ictericia_flutuante'): partes.append('padrão flutuante')
    elif dados.get('ictericia_progressiva'): partes.append('progressiva e persistente')
    if dados.get('urina_escura'): partes.append('colúria')
    if dados.get('fezes_acolicas'): partes.append('acolia fecal')
    if dados.get('prurido_cutaneo'): partes.append('prurido cutâneo')
    if dados.get('colica_biliar'): partes.append('cólica biliar')
    if dados.get('dor_hcd'): partes.append('⚠️ dor em HCD')
    if dados.get('perda_peso_involuntaria'): partes.append('⚠️ perda de peso involuntária')
    if dados.get('uso_alcool_excessivo'): partes.append('etilismo significativo')
    if dados.get('medicamento_hepatotoxico'): partes.append('medicamento hepatotóxico')
    if dados.get('gilbert_previamente_diagnosticado'): partes.append('síndrome de Gilbert prévia')
    neg = []
    if dados.get('hipotensao') is False: neg.append('hipotensão')
    if dados.get('encefalopatia_hepatica') is False: neg.append('encefalopatia')
    if neg: partes.append(_fmt_negativas(neg))
    return _partes_para_texto(partes, separador='. ')

def gerar_objetivo_ictericia(admissao): return ''


# ------------------------------------------------------------------
# ORGÂNICO — ASMA (episódico-crônico)
# ------------------------------------------------------------------

def gerar_subjetivo_asma(admissao):
    dados = _get_dados_modulo(admissao, 'asma', 'organico')
    if not dados: return ''
    partes = []
    tipo = dados.get('consulta_tipo', 'rotina')
    if tipo == 'crise':
        spo2 = dados.get('spo2', '?')
        pefr = dados.get('pefr_percentual')
        partes.append('Crise asmática aguda')
        if dados.get('sonolencia_confusao') or dados.get('torax_silencioso'):
            partes.append('⚠️ risco de vida (sonolência / tórax silencioso)')
        elif dados.get('fala_palavras_apenas') or dados.get('fr_maior_30'):
            partes.append('padrão grave (fala em palavras / FR > 30)')
        else:
            partes.append('padrão leve-moderado (fala em frases)')
        if spo2 != '?': partes.append(f'SpO₂ {spo2}%')
        if pefr: partes.append(f'PEFR {pefr}% do previsto')
        if dados.get('usa_ics_regular') is False: partes.append('sem ICS regular')
    else:
        step = dados.get('step_atual', '?')
        partes.append(f'Asma — consulta de rotina (Step GINA {step})')
        ctrl_issues = []
        if dados.get('sintomas_diurnos_mais_2sem'): ctrl_issues.append('sintomas diurnos > 2×/sem')
        if dados.get('despertar_noturno'): ctrl_issues.append('despertar noturno')
        if dados.get('saba_mais_2sem'): ctrl_issues.append('SABA > 2×/sem')
        if dados.get('limitacao_atividade'): ctrl_issues.append('limitação de atividade')
        if dados.get('exacerbacao_ultimo_ano'): ctrl_issues.append('exacerbação no último ano')
        if ctrl_issues: partes.append('critérios de mau controle: ' + ', '.join(ctrl_issues))
        else: partes.append('sem critérios de mau controle')
        if dados.get('tecnica_inalacao_correta') is False: partes.append('⚠️ técnica inalatória incorreta')
        if dados.get('adesao_medicacao') is False: partes.append('⚠️ baixa adesão relatada')
    if dados.get('usa_betabloqueador'): partes.append('⚠️ betabloqueador em uso')
    if dados.get('usa_aine_aas'): partes.append('AINE/AAS em uso')
    return _partes_para_texto(partes, separador='. ')

def gerar_objetivo_asma(admissao): return ''


# ------------------------------------------------------------------
# ORGÂNICO — DPOC (episódico-crônico)
# ------------------------------------------------------------------

def gerar_subjetivo_dpoc(admissao):
    dados = _get_dados_modulo(admissao, 'dpoc', 'organico')
    if not dados: return ''
    partes = []
    tipo = dados.get('consulta_tipo', 'rotina')
    if tipo == 'exacerbacao':
        partes.append('Exacerbação aguda de DPOC')
        crit = []
        if dados.get('piora_dispneia'): crit.append('piora da dispneia')
        if dados.get('aumento_volume_escarro'): crit.append('aumento de escarro')
        if dados.get('escarro_purulento'): crit.append('escarro purulento')
        if crit: partes.append(f'Critérios de Anthonisen: {", ".join(crit)}')
        spo2 = dados.get('spo2')
        if spo2: partes.append(f'SpO₂ {spo2}%')
        if dados.get('alt_consciencia'): partes.append('⚠️ alteração de consciência')
    else:
        cat = dados.get('cat_score', '?')
        mmrc = dados.get('mmrc', '?')
        exac = dados.get('exacerbacoes_ultimo_ano', 0)
        partes.append(f'DPOC — rotina (CAT ~{cat}, mMRC {mmrc}, {exac} exacerbações/ano)')
        fev1 = dados.get('fev1_percentual')
        if fev1: partes.append(f'VEF1 {fev1}% do previsto')
        eosino = dados.get('eosinofilos')
        if eosino: partes.append(f'eosinófilos {eosino} cél/μL')
    if dados.get('tabagismo_ativo'): partes.append('⚠️ tabagista ativo')
    return _partes_para_texto(partes, separador='. ')

def gerar_objetivo_dpoc(admissao): return ''


# ------------------------------------------------------------------
# CELULITE / ERISIPELA — subjetivo, #Análise, #Plano
# ------------------------------------------------------------------

_CELULITE_CATS = frozenset({
    'cel_fasciite', 'cel_sepse', 'cel_grave', 'cel_bolhosa',
    'cel_abscesso', 'cel_moderada', 'cel_leve', 'cel_recorrente',
})

_CID_CELULITE = {
    'face':           'L03.2',
    'mmii_unilateral':'L03.115',
    'mmii_bilateral': 'L03.116',
    'pe':             'L03.115',
    'mao_braco':      'L03.011',
    'tronco':         'L03.311',
    'outro':          'L03.90',
}


def gerar_subjetivo_celulite(admissao):
    dados = _get_dados_modulo(admissao, 'celulite', 'organico')
    if not dados:
        return ''
    partes = []

    loc_map = {
        'mmii_unilateral': 'MMII unilateral',
        'mmii_bilateral':  'MMII bilateral',
        'face':            'face',
        'mao_braco':       'mão/braço',
        'tronco':          'tronco',
        'pe':              'pé',
        'outro':           'outro',
    }
    loc = loc_map.get(dados.get('localizacao', ''), '')
    tempo_map = {
        'horas': '< 24h',
        'um_a_dois_dias': '1–2 dias',
        'tres_a_cinco_dias': '3–5 dias',
        'mais_cinco_dias': '> 5 dias',
    }
    tempo = tempo_map.get(dados.get('tempo_evolucao', ''), '')
    if loc:
        partes.append(f'Celulite/erisipela em {loc}')
    if tempo:
        partes.append(f'evolução há {tempo}')

    # porta de entrada
    porta = []
    if dados.get('tinea_pedis'):        porta.append('tinea pedis')
    if dados.get('ferida_ulcera'):      porta.append('ferida/úlcera')
    if dados.get('picada_trauma'):      porta.append('picada/trauma')
    if dados.get('pe_diabetico'):       porta.append('pé diabético')
    if dados.get('manicure_pedicure'):  porta.append('manicure/pedicure')
    if dados.get('uso_drogas_iv'):      porta.append('uso de drogas IV')
    if dados.get('mordedura_animal'):   porta.append('mordedura/imersão')
    if dados.get('trauma_penetrante'):  porta.append('trauma penetrante')
    if porta:
        partes.append(f'Porta de entrada: {", ".join(porta)}')

    # sinais sistêmicos
    sist = []
    if dados.get('febre'):
        temp = dados.get('temp_celsius')
        sist.append(f'febre ({temp}°C)' if temp else 'febre')
    if dados.get('taquicardia'):    sist.append('taquicardia')
    if dados.get('taquipneia'):     sist.append('taquipneia')
    if dados.get('mal_estar_calafrio'): sist.append('mal-estar/calafrios')
    if sist:
        partes.append(f'Sintomas sistêmicos: {", ".join(sist)}')

    # sinais locais
    locais = []
    if dados.get('borda_nitida'):        locais.append('borda bem demarcada')
    if dados.get('linfangite'):          locais.append('linfangite')
    if dados.get('flutuacao'):           locais.append('flutuação/abscesso')
    if dados.get('bolhas'):
        if dados.get('bolhas_hemorragicas'): locais.append('bolhas hemorrágicas')
        else:                                locais.append('bolhas tensas')
    if dados.get('crepitacao'):          locais.append('⚠️ crepitação')
    if dados.get('necrose'):             locais.append('⚠️ necrose/pele violácea')
    if dados.get('dor_desproporcional'): locais.append('⚠️ dor desproporcional')
    if locais:
        partes.append(f'Sinais locais: {", ".join(locais)}')

    # comorbidades relevantes
    comorb = []
    if dados.get('diabetes'):         comorb.append('DM')
    if dados.get('imunossupressao') or dados.get('neutropenia'): comorb.append('imunossupressão')
    if dados.get('linfedema'):         comorb.append('linfedema')
    if dados.get('insuf_venosa'):      comorb.append('insuf. venosa')
    if comorb:
        partes.append(f'Comorbidades: {", ".join(comorb)}')

    # negativas
    neg = []
    if dados.get('crepitacao') is False:          neg.append('crepitação')
    if dados.get('necrose') is False:             neg.append('necrose')
    if dados.get('dor_desproporcional') is False: neg.append('dor desproporcional')
    if neg:
        partes.append(f'Nega: {", ".join(neg)}')

    return _partes_para_texto(partes, separador='. ')


def gerar_objetivo_celulite(admissao): return ''


# ------------------------------------------------------------------
# HEMORRAGIA DIGESTIVA — subjetivo, #Análise, #Plano
# ------------------------------------------------------------------

_HEMORRAGIA_CATS = frozenset({
    'hd_ugib_gbs_baixo', 'hd_ugib_nao_variceal', 'hd_ugib_variceal',
    'hd_ugib_instavel', 'hd_lgib_instavel',
    'hd_lgib_hemorroida', 'hd_lgib_fissura', 'hd_lgib_diverticular',
    'hd_lgib_angiodisplasia', 'hd_lgib_isquemica', 'hd_lgib_dii',
    'hd_lgib_infecciosa', 'hd_lgib_neoplasia', 'hd_lgib_pos_polipectomia',
    'hd_lgib_internacao',
})

_CID_HEMORRAGIA = {
    'hd_ugib_gbs_baixo':       'K92.2',
    'hd_ugib_nao_variceal':    'K92.0',
    'hd_ugib_variceal':        'I85.01',
    'hd_ugib_instavel':        'K92.0',
    'hd_lgib_instavel':        'K92.2',
    'hd_lgib_hemorroida':      'K64.9',
    'hd_lgib_fissura':         'K60.0',
    'hd_lgib_diverticular':    'K57.33',
    'hd_lgib_isquemica':       'K55.9',
    'hd_lgib_dii':             'K51.9',
    'hd_lgib_infecciosa':      'A09',
    'hd_lgib_neoplasia':       'C18.9',
    'hd_lgib_pos_polipectomia':'K92.2',
    'hd_lgib_internacao':      'K92.2',
}


def gerar_subjetivo_hemorragia(admissao):
    dados = _get_dados_modulo(admissao, 'hemorragia', 'organico')
    if not dados:
        return ''
    partes = []

    tipo_map = {
        'hematemese':   'hematêmese (vômito com sangue vivo)',
        'borra_cafe':   'hematêmese em borra de café',
        'melena':       'melena (fezes pretas/alcatronadas)',
        'hematoquezia': 'hematoquezia (sangue vivo nas fezes)',
        'marrom_escuro':'fezes marrom-escuras',
        'papel_apenas': 'sangue apenas no papel higiênico',
    }
    tipo = tipo_map.get(dados.get('tipo_sangramento', ''), '')
    if tipo:
        partes.append(f'Queixa: {tipo}')

    ramo = dados.get('ramo', '')
    if ramo == 'ugib':
        partes.append('HDA')
    elif ramo == 'lgib':
        partes.append('HDB')

    # hemodinâmica
    pas = dados.get('pas')
    fc  = dados.get('fc')
    if pas and fc:
        si = round(fc / pas, 2)
        partes.append(f'PA {pas} mmHg / FC {fc} bpm (shock index {si})')
    if dados.get('sincope'):
        partes.append('⚠️ síncope')

    # contexto UGIB
    if ramo == 'ugib':
        hb = dados.get('hb')
        bun = dados.get('bun')
        if hb:  partes.append(f'Hb {hb} g/dL')
        if bun: partes.append(f'BUN {bun} mg/dL')
        if dados.get('cirrose') or dados.get('hepatopatia_gbs'):
            partes.append('hepatopatia/cirrose')
        if dados.get('varizes_previas'):
            partes.append('varizes esofágicas prévias')
        if dados.get('aine_asa'):
            partes.append('uso de AINE/AAS')
        if dados.get('pud_previo'):
            partes.append('PUD prévio')

    # contexto LGIB
    if ramo == 'lgib':
        hb = dados.get('hb')
        if hb: partes.append(f'Hb {hb} g/dL')
        if dados.get('dor_evacuacao'):   partes.append('dor à evacuação')
        if dados.get('diarreia_sangue'): partes.append('diarreia com sangue')
        if dados.get('febre'):           partes.append('febre')
        if dados.get('mudanca_habito'):  partes.append('⚠️ mudança de hábito intestinal')
        if dados.get('perda_peso'):      partes.append('⚠️ perda de peso')
        if dados.get('dii_conhecida'):   partes.append('DII conhecida')
        if dados.get('dcv_dm'):          partes.append('DM/vasculopatia')

    # anticoagulação
    if dados.get('anticoagulado'):
        atc = dados.get('anticoagulante') or 'anticoagulante'
        partes.append(f'em uso de {atc}')

    # negativas
    neg = []
    if dados.get('cirrose') is False and ramo == 'ugib':
        neg.append('nega cirrose')
    if dados.get('anticoagulado') is False:
        neg.append('nega anticoagulante')
    if neg:
        partes.append(f'Nega: {", ".join(neg)}')

    return _partes_para_texto(partes, separador='. ')


def gerar_objetivo_hemorragia(admissao): return ''


def _analise_hemorragia(resultado: dict) -> str:
    cat   = resultado.get('categoria', '')
    diag  = resultado.get('diagnostico', 'Hemorragia digestiva')
    ramo  = resultado.get('ramo', '')
    score_n = resultado.get('score_nome')
    score_v = resultado.get('score_valor')
    si    = resultado.get('shock_index')
    rac   = resultado.get('raciocinio', '')

    linhas = [diag + '.']
    if score_n is not None and score_v is not None:
        linhas.append(f'{score_n}: {score_v} pontos.')
    if si is not None:
        linhas.append(f'Shock index: {si}.')
    if resultado.get('transfusao'):
        linhas.append('Transfusão indicada.')
    if resultado.get('variceal_suspeita'):
        linhas.append('Sangramento varicoso suspeito — octreotida + antibiótico imediatos.')
    if rac:
        linhas.append(rac)
    return ' '.join(linhas)


def _plano_hemorragia(resultado: dict) -> str:
    cat     = resultado.get('categoria', '')
    conduta = resultado.get('conduta', '')
    exames  = resultado.get('exames', '')
    enc     = resultado.get('encaminhamento')
    ramo    = resultado.get('ramo', 'ugib')
    score_n = resultado.get('score_nome')
    score_v = resultado.get('score_valor')
    linhas  = []

    # ── Alertas de segurança (pente fino) ─────────────────────────────────────
    for alerta in resultado.get('alertas_seguranca', []):
        linhas += ['', alerta]

    urg_map = {
        'hd_ugib_instavel':      '⚠️⚠️ EMERGÊNCIA — HDA Instável',
        'hd_lgib_instavel':      '⚠️⚠️ EMERGÊNCIA — HDB Instável',
        'hd_ugib_variceal':      '⚠️ Internação — HDA Variceal',
        'hd_ugib_nao_variceal':  '⚠️ Internação — HDA Não Variceal',
        'hd_lgib_internacao':    '⚠️ Internação — HDB',
        'hd_lgib_isquemica':     '⚠️ Internação — Colite Isquêmica',
        'hd_lgib_dii':           'Internação se grave — DII Flare',
        'hd_ugib_gbs_baixo':     'Alta — HDA Baixo Risco (GBS ≤ 1)',
        'hd_lgib_hemorroida':    'Alta — Hemorroida',
        'hd_lgib_fissura':       'Alta — Fissura Anal',
        'hd_lgib_diverticular':  'Alta (Oakland ≤ 8) — Diverticular/Angiodisplasia',
        'hd_lgib_infecciosa':    'Alta — Colite Infecciosa',
        'hd_lgib_neoplasia':     '⚠️ Colonoscopia Urgente — Suspeita Neoplasia',
        'hd_lgib_pos_polipectomia': 'Endoscopia — Pós-polipectomia',
    }
    if cat in urg_map:
        linhas.append(urg_map[cat])

    if score_n and score_v is not None:
        linhas.append(f'{score_n}: {score_v} pontos.')

    if conduta:
        linhas.append('')
        linhas.append('Conduta:')
        for frase in conduta.split('. '):
            frase = frase.strip()
            if frase:
                linhas.append(f'• {frase}.')

    if resultado.get('transfusao'):
        linhas.append('')
        dcv = resultado.get('categoria', '').endswith('variceal') or False
        meta = 8 if (dcv or 'variceal' in cat) else 7
        linhas.append(f'Transfusão: meta Hb ≥ {meta} g/dL (estratégia restritiva — ACG 2023).')

    if exames:
        linhas.append('')
        linhas.append(f'Exames: {exames}')

    if enc:
        linhas.append('')
        linhas.append(f'Encaminhamento: {enc}')

    return '\n'.join(linhas)


def _analise_celulite(resultado: dict) -> str:
    cat  = resultado.get('categoria', '')
    diag = resultado.get('diagnostico', 'Celulite')
    ach  = resultado.get('achados', [])
    sirs = resultado.get('sirs')
    lrin = resultado.get('lrinec')
    rac  = resultado.get('raciocinio', '')

    linhas = [diag + '.']
    if ach:
        linhas.append(f'Achados: {", ".join(ach)}.')
    if sirs is not None:
        linhas.append(f'SIRS: {sirs} critério(s).')
    if lrin is not None and lrin > 0:
        linhas.append(f'LRINEC: {lrin} pontos{"  (≥6 — alto risco fasciite)" if lrin >= 6 else ""}.')
    if rac:
        linhas.append(rac)
    return ' '.join(linhas)


def _plano_celulite(resultado: dict) -> str:
    cat     = resultado.get('categoria', '')
    conduta = resultado.get('conduta', '')
    exames  = resultado.get('exames', '')
    enc     = resultado.get('encaminhamento')
    sirs    = resultado.get('sirs', 0)
    linhas  = []

    # ── Alertas de segurança (pente fino) ─────────────────────────────────────
    for alerta in resultado.get('alertas_seguranca', []):
        linhas += ['', alerta]

    urg_map = {
        'cel_fasciite':  '⚠️⚠️ EMERGÊNCIA CIRÚRGICA — Fasciite Necrotizante',
        'cel_sepse':     '⚠️ EMERGÊNCIA — Celulite + Sepse',
        'cel_grave':     '⚠️ Internação — Celulite Grave',
        'cel_bolhosa':   '⚠️ Internação preferencial — Erisipela/Celulite Bolhosa',
        'cel_abscesso':  'Drenagem + Ambulatório',
        'cel_moderada':  'Ambulatório — ATB oral + retorno 48h',
        'cel_leve':      'Alta — ATB oral',
        'cel_recorrente':'Alta — ATB oral + profilaxia',
    }
    if cat in urg_map:
        linhas.append(urg_map[cat])

    if conduta:
        linhas.append('')
        linhas.append('Conduta:')
        for frase in conduta.split('. '):
            frase = frase.strip()
            if frase:
                linhas.append(f'• {frase}.')

    # Marcação da pele (sempre orientar quando não é emergência)
    if cat not in ('cel_fasciite', 'cel_sepse'):
        linhas.append('')
        linhas.append('Marcação da pele: marcar borda do eritema com caneta permanente + data/hora.')
        linhas.append('Retorno em 24–48h: progressão além da marcação = falha → internação.')

    if exames:
        linhas.append('')
        linhas.append(f'Exames: {exames}')

    if enc:
        linhas.append('')
        linhas.append(f'Encaminhamento: {enc}')

    return '\n'.join(linhas)


# ------------------------------------------------------------------
# GASTRO — Subjetivo
# ------------------------------------------------------------------

def gerar_subjetivo_gastro(admissao):
    dados = _get_dados_modulo(admissao, 'gastro', tipo='organico')
    if not dados:
        return ''

    partes = []

    # Localização + caráter + duração
    loc_label = {
        'epigastrico': 'epigástrica', 'fsd': 'em FSD', 'fid': 'em FID',
        'fie': 'em FIE', 'hipogastrico_pelvico': 'pélvica',
        'periumbilical': 'periumbilical', 'difuso': 'difusa',
    }
    car_label = {
        'colica': 'caráter cólico', 'queimacao': 'em queimação',
        'constante': 'constante', 'distensao': 'tipo distensão',
        'aguda_subita': 'início súbito intenso', 'difusa_leve': 'difusa e leve',
    }
    dur_label = {
        'horas': '< 24h', 'dias': 'há dias', 'semanas': 'há semanas',
        'meses_1_3': 'há meses', 'meses_mais_3': 'crônica (> 3 meses)',
    }
    loc = loc_label.get(dados.get('localizacao', ''), 'abdominal')
    car = car_label.get(dados.get('carater', ''), '')
    dur = dur_label.get(dados.get('duracao', ''), '')
    intro = f'Dor {loc}'
    if car:
        intro += f', {car}'
    if dur:
        intro += f', {dur}'
    partes.append(intro)

    # Intensidade
    intens = dados.get('intensidade', '')
    if intens in ('intensa', 'catastrofica'):
        partes.append(f'intensidade {intens}')

    # Febre
    grau = dados.get('febre_grau', 'sem')
    if grau != 'sem':
        partes.append(f'febre {grau}')

    # Sintomas associados
    _sim = [
        ('nausea',      'náuseas'),
        ('vomito',      'vômitos'),
        ('hematemese',  'hematêmese'),
        ('melena',      'melena'),
        ('hematoquezia','hematoquezia'),
        ('perda_peso',  'perda de peso involuntária'),
        ('ictericia',   'icterícia'),
        ('muco_fezes',  'muco nas fezes'),
        ('esteatorreia','esteatorreia'),
        ('alivio_evacuacao', 'alívio após evacuar'),
    ]
    pos = [label for chave, label in _sim if dados.get(chave)]
    if pos:
        partes.append(f'associado a {", ".join(pos)}')

    # Hábito intestinal alterado
    hab_label = {
        'constipacao': 'constipação', 'diarreia': 'diarreia',
        'alternancia': 'alternância diarreia/constipação',
        'sem_evacuacao_gases': 'obstipação total (sem fezes e sem gases)',
    }
    hab = hab_label.get(dados.get('habito_intestinal', ''), '')
    if hab:
        partes.append(hab)

    # Negativas pertinentes
    neg = []
    if dados.get('peritonismo') is False:
        neg.append('nega peritonismo')
    if dados.get('hematemese') is False:
        neg.append('nega hematêmese')
    if dados.get('melena') is False:
        neg.append('nega melena')
    if dados.get('perda_peso') is False:
        neg.append('nega perda de peso')
    if neg:
        partes.append('Nega: ' + ', '.join(neg))

    return _partes_para_texto(partes)


def gerar_objetivo_gastro(admissao):
    dados = _get_dados_modulo(admissao, 'gastro', tipo='organico')
    if not dados:
        return ''
    achados = []
    if dados.get('murphy_positivo'):
        achados.append('Murphy positivo')
    if dados.get('mcburney_positivo'):
        achados.append('McBurney positivo')
    if dados.get('blumberg_positivo'):
        achados.append('Blumberg positivo')
    if dados.get('rigidez'):
        achados.append('rigidez involuntária')
    if dados.get('fie_dolorosa'):
        achados.append('FIE dolorosa')
    if dados.get('fid_dolorosa'):
        achados.append('FID dolorosa')
    if dados.get('rha_ausentes'):
        achados.append('RHA ausentes')
    if not achados:
        return ''
    return f'Abdôme: {", ".join(achados)}.'


# ------------------------------------------------------------------
# SONO — Subjetivo
# ------------------------------------------------------------------

def gerar_subjetivo_sono(admissao):
    dados = _get_dados_modulo(admissao, 'sono', tipo='organico')
    if not dados:
        return ''

    partes = []

    isi = dados.get('isi_score', 0) or 0
    if isi > 0:
        grau = 'sem significância clínica' if isi <= 7 else (
               'leve' if isi <= 14 else ('moderada' if isi <= 21 else 'grave'))
        partes.append(f'ISI = {isi}/28 (insônia {grau})')

    sb = dados.get('stopbang_score', 0) or 0
    if sb >= 3:
        partes.append(f'STOP-BANG = {sb}/8 (alto risco AOS)')

    ew = dados.get('epworth_score', 0) or 0
    if ew > 10:
        partes.append(f'Epworth = {ew}/24')

    spi = dados.get('spi_criterios', 0) or 0
    if spi == 4:
        partes.append('SPI — 4 critérios presentes')

    _sim = [
        ('cataplexia',              'cataplexia'),
        ('paralisia_sono',          'paralisia do sono'),
        ('alucinacao_adormecer',    'alucinações hipnagógicas'),
        ('sono_diurno_irresistivel','sono diurno irresistível'),
        ('tcr_rem_age_sonhos',      'age os sonhos — TCR-REM suspeito'),
        ('ranger_dentes',           'bruxismo (range os dentes)'),
        ('sonambulismo',            'sonambulismo'),
        ('terror_noturno',          'terror noturno'),
        ('pesadelos_freq',          'pesadelos frequentes'),
        ('benzo_em_uso',            'benzodiazepínico em uso crônico'),
        ('depressao_ansiedade',     'depressão / ansiedade'),
        ('turno_irregular',         'turno de trabalho irregular'),
        ('dor_cronica_noturna',     'dor crônica noturna'),
    ]
    pos = [label for chave, label in _sim if dados.get(chave)]
    if pos:
        partes.append('; '.join(pos))

    _neg_campos = [
        ('cataplexia',   'nega cataplexia'),
        ('sonambulismo', 'nega sonambulismo'),
    ]
    neg = [label for chave, label in _neg_campos if dados.get(chave) is False]
    if neg:
        partes.append('Nega: ' + ', '.join(neg))

    return _partes_para_texto(partes)


# ------------------------------------------------------------------
# #ANÁLISE — ANEMIA / SONO / CONSCIÊNCIA / LINFADENOPATIA
# (diagnóstico + CID + justificativa; a conduta fica no #Plano)
# ------------------------------------------------------------------

_ANEMIA_CATS = frozenset({
    'anemia_alcool', 'anemia_b12', 'anemia_combinada', 'anemia_doenca_cronica',
    'anemia_ferropriva', 'anemia_folato', 'anemia_hemolitica',
    'anemia_hipotireoidismo', 'anemia_macro_indefinida', 'anemia_micro_incompleta',
    'anemia_micro_indefinida', 'anemia_normo_indefinida', 'anemia_renal',
    'anemia_reticulocitose', 'anemia_sangramento', 'anemia_smd',
    'pancitopenia', 'sem_anemia',
    'talassemia_alfa', 'talassemia_beta', 'talassemia_beta_maior',
    'talassemia_suspeita',
})

_SONO_CATS = frozenset({
    'aos_suspeita', 'bruxismo_sono', 'desmame_benzo', 'insonia_comportamental',
    'insonia_cronica_primaria', 'insonia_dor', 'insonia_hipotireoidismo',
    'insonia_psiquiatrica', 'insonia_subaguda', 'insonia_turno',
    'narcolepsia_suspeita', 'parassonia_nrem', 'pesadelos_tept',
    'sfas', 'spi', 'tcr_rem_pre_parkinson',
})

_CONSCIENCIA_CATS = frozenset({
    'anc_indefinida', 'avc_sangramento', 'choque_hemodinamico',
    'crise_dissociativa', 'encefalopatia_metabolica', 'hipoglicemia',
    'hipoxia_grave', 'intoxicacao_alcool', 'meningite_encefalite',
    'overdose_opioide', 'pos_ictal', 'status_epilepticus', 'tce_hematoma',
})

_LINFA_CATS = frozenset({
    'doenca_arranhadura_gato', 'ebv_mononucleose', 'hiv_infeccao_primaria',
    'ist_linfadenopatia_inguinal', 'linfadenite_bacteriana',
    'linfadenopatia_inguinal_benigna', 'linfadenopatia_reativa',
    'linfoma_suspeito', 'massa_inguinal_diferencial', 'neoplasia_metastatica',
    'tb_linfadenopatia',
})


def _analise_anemia(resultado: dict) -> str:
    """#Análise — Anemia: classificação + CID + padrão laboratorial."""
    cat  = resultado.get('categoria', '')
    cid  = _CID_MAP.get(cat, '')
    cid_str = f' — CID-10: {cid}' if cid else ''

    if cat == 'sem_anemia':
        return '✓ Hemoglobina dentro dos limites para sexo/idade — sem anemia.'

    if cat == 'pancitopenia':
        return (f'⚠️ PANCITOPENIA{cid_str}. '
                'Acometimento das três séries — investigação hematológica urgente '
                '(aplasia, infiltração medular, SMD). Não conduzir como anemia isolada.')

    linhas = []
    grau = {'leve': 'leve', 'moderada': 'moderada', 'grave': 'grave',
            'muito_grave': 'muito grave'}.get(resultado.get('grau', ''), '')
    tipo = resultado.get('tipo_mcv', '')
    diag = resultado.get('diagnostico', '')
    linhas.append(f'{diag}{cid_str}.')

    # Justificativa laboratorial — por que fechou esse padrão
    hb  = resultado.get('hb')
    mcv = resultado.get('mcv')
    rdw = resultado.get('rdw')
    rpi = resultado.get('rpi')
    limiar = resultado.get('limiar')
    descr  = resultado.get('descr_sexo', '')
    lab = []
    if hb is not None and limiar:
        lab.append(f'Hb {hb} g/dL (limiar {limiar} para {descr})')
    if mcv: lab.append(f'VCM {mcv} fL → padrão {tipo.lower()}' if tipo else f'VCM {mcv} fL')
    if rdw: lab.append(f'RDW {rdw}%')
    if rpi is not None: lab.append(f'RPI {rpi}')
    if lab:
        linhas.append('Base laboratorial: ' + ' | '.join(lab) +
                      (f'. Gravidade: anemia {grau}.' if grau else '.'))

    padrao = resultado.get('padrao', '')
    if padrao:
        linhas.append(f'Padrão: {padrao}.')

    if resultado.get('alerta_transfusao'):
        linhas.append('⚠️ Hb em faixa de avaliação para transfusão '
                      '(< 7 g/dL, ou < 8 com doença cardiovascular).')
    return '\n'.join(linhas)


def _analise_sono(resultado: dict) -> str:
    """#Análise — Transtornos do Sono: diagnóstico + CID + scores que fecharam."""
    cat  = resultado.get('categoria', '')
    cid  = _CID_SONO.get(cat, '')
    cid_str = f' — CID-10: {cid}' if cid else ''
    diag = resultado.get('diagnostico', '')
    linhas = [f'{diag}{cid_str}.']

    just = []
    isi_grau = resultado.get('isi_grau', '')
    if isi_grau:
        just.append(f'ISI em faixa de insônia {isi_grau}')
    if cat == 'aos_suspeita':
        just.append('STOP-BANG em faixa de alto risco para apneia obstrutiva do sono')
    if cat == 'spi':
        just.append('4 critérios diagnósticos de SPI presentes (URGE)')
    if cat == 'narcolepsia_suspeita':
        just.append('sonolência diurna irresistível + sintomas acessórios (cataplexia/paralisia/alucinações)')
    if cat == 'tcr_rem_pre_parkinson':
        just.append('comportamento de atuação dos sonhos — TCR-REM, marcador precoce de sinucleinopatia')
    if just:
        linhas.append('Base diagnóstica: ' + '; '.join(just) + '.')
    return '\n'.join(linhas)


def _analise_consciencia(resultado: dict) -> str:
    """#Análise — ANC: diagnóstico + CID + Glasgow e pista etiológica."""
    cat  = resultado.get('categoria', '')
    cid  = _CID_CONSCIENCIA.get(cat, '')
    cid_str = f' — CID-10: {cid}' if cid else ''
    diag = resultado.get('diagnostico', '')
    g    = resultado.get('glasgow')
    urg  = {'emergencia': '🔴 EMERGÊNCIA', 'urgente': '🟠 Urgente',
            'eletivo': '🟢 Eletivo'}.get(resultado.get('urgencia', ''), '')

    linhas = [f'{diag}{cid_str}.']
    base = []
    if g is not None:
        base.append(f'Glasgow {g}/15')
    if urg:
        base.append(f'prioridade {urg}')
    if resultado.get('iot_alerta'):
        base.append('⚠️ Glasgow ≤ 8 — via aérea ameaçada')
    if base:
        linhas.append('Estratificação: ' + ' | '.join(base) + '.')
    linhas.append('Abordagem etiológica sistemática AEIOU-TIPS — causas estruturais, '
                  'metabólicas e tóxicas devem ser ativamente excluídas.')
    return '\n'.join(linhas)


def _analise_linfadenopatia(resultado: dict) -> str:
    """#Análise — Linfadenopatia: diagnóstico + CID + padrão e red flags."""
    cat  = resultado.get('categoria', '')
    cid  = _CID_LINFA.get(cat, '')
    cid_str = f' — CID-10: {cid}' if cid else ''
    diag = resultado.get('diagnostico', '')
    linhas = [f'{diag}{cid_str}.']

    padrao = resultado.get('padrao', '')
    if padrao:
        # Filtra segmentos sem valor preenchido ("Local: ", "Doloroso: None", "Tamanho: 0 cm")
        segs = []
        for seg in padrao.replace('\n', '|').split('|'):
            seg = seg.strip()
            if not seg:
                continue
            valor = seg.split(':', 1)[-1].strip() if ':' in seg else seg
            if valor in ('', 'None', '0 cm', '0 semanas'):
                continue
            segs.append(seg)
        if segs:
            linhas.append('Caracterização: ' + ' | '.join(segs) + '.')

    flags = resultado.get('red_flags', [])
    if flags:
        linhas.append('⚠️ Red flags presentes: ' + ', '.join(flags) + '.')
    elif cat in ('linfadenopatia_reativa', 'linfadenopatia_inguinal_benigna'):
        linhas.append('Sem red flags (sem sintomas B, sem crescimento progressivo, '
                      'sem consistência endurecida/aderida) — padrão benigno/reativo.')

    if resultado.get('biopsia'):
        linhas.append('Critérios para biópsia presentes.')
    return '\n'.join(linhas)


# ------------------------------------------------------------------
# TEP — Subjetivo, #Análise (bayesiana), #Plano A/B
# ------------------------------------------------------------------

def gerar_subjetivo_tep(admissao):
    dados = _get_dados_modulo(admissao, 'tep', 'organico')
    if not dados:
        return ''
    partes = []

    # Instabilidade primeiro
    inst = []
    if dados.get('hipotensao_choque'):  inst.append('🔴 hipotensão/choque')
    if dados.get('pocus_vd_disfuncao'): inst.append('🔴 disfunção de VD ao POCUS')
    if dados.get('sangramento_ativo'):  inst.append('⛔ sangramento ativo')
    if inst:
        partes.append('Instabilidade: ' + ', '.join(inst))

    # Itens Wells positivos
    wells = []
    if dados.get('tvp_sinais_clinicos'):   wells.append('sinais clínicos de TVP')
    if dados.get('tep_mais_provavel'):     wells.append('TEP como hipótese mais provável')
    if dados.get('fc_maior_100'):          wells.append('FC > 100')
    if dados.get('imobilizacao_cirurgia'): wells.append('imobilização/cirurgia recente')
    if dados.get('tep_tvp_previo'):        wells.append('TEP/TVP prévio')
    if dados.get('hemoptise'):             wells.append('hemoptise')
    if dados.get('neoplasia_ativa'):       wells.append('neoplasia ativa')
    if wells:
        partes.append('Fatores Wells: ' + ', '.join(wells))

    # Negativas pertinentes
    neg = []
    if dados.get('hemoptise') is False:             neg.append('hemoptise')
    if dados.get('tvp_sinais_clinicos') is False:   neg.append('sinais de TVP')
    if dados.get('hipotensao_choque') is False:     neg.append('instabilidade hemodinâmica')
    if dados.get('tep_tvp_previo') is False:        neg.append('TEP/TVP prévio')
    if neg:
        partes.append('Nega: ' + ', '.join(neg))

    ddimer = dados.get('ddimer_valor')
    if ddimer:
        partes.append(f'D-dímero colhido: {ddimer} µg/L FEU')

    return _partes_para_texto(partes, separador='. ')


def _analise_tep(resultado: dict) -> str:
    """#Análise — TEP com probabilidades bayesianas explícitas."""
    linhas = [f"{resultado.get('diagnostico', '')}"]
    linhas.append(resultado.get('raciocinio', ''))

    itens = resultado.get('wells_itens', [])
    if itens:
        linhas.append('Itens Wells: ' + '; '.join(itens) + '.')
    perc_pos = resultado.get('perc_itens_positivos')
    if perc_pos:
        linhas.append('PERC positivo em: ' + ', '.join(perc_pos) +
                      ' — PERC não exclui, seguir fluxo D-dímero.')
    return '\n'.join(l for l in linhas if l)


def gerar_subjetivo_dor_toracica(admissao):
    dados = _get_dados_modulo(admissao, 'dor_toracica', 'organico')
    if not dados:
        return ''
    partes = []

    # Letais primeiro
    rf = []
    if dados.get('choque_hipotensao'):     rf.append('🔴 instabilidade hemodinâmica')
    if dados.get('mv_abolido_unilateral'): rf.append('🔴 MV abolido unilateral')
    if dados.get('dor_lacerante_dorso'):   rf.append('🔴 dor lacerante irradiando ao dorso')
    if dados.get('assimetria_pulsos_pa'):  rf.append('🔴 assimetria de pulsos/PA')
    if rf:
        partes.append('Sinais de alarme: ' + ', '.join(rf))

    # Caracterização HEART
    hist = {'pouco': 'pouco suspeita para SCA', 'moderada': 'moderadamente suspeita',
            'muito': 'muito suspeita (aperto, irradiação, sudorese)'}.get(
            dados.get('historia_suspeita', ''), '')
    if hist:
        partes.append(f'História {hist}')

    # ECG
    ecg = []
    if dados.get('ecg_supra_st'):       ecg.append('🔴 SUPRA de ST')
    if dados.get('ecg_bre_novo'):       ecg.append('🔴 BRE novo')
    if dados.get('ecg_infra_st_t_neg'): ecg.append('infra de ST/inversão de T')
    if dados.get('ecg_alteracao_inespecifica'): ecg.append('alteração inespecífica')
    if dados.get('ecg_normal'):         ecg.append('normal')
    if ecg:
        partes.append('ECG: ' + ', '.join(ecg))

    # Fatores de risco
    frs = [l for k, l in [('fr_has', 'HAS'), ('fr_dm', 'DM'), ('fr_tabagismo', 'tabagismo'),
                          ('fr_dislipidemia', 'dislipidemia'), ('fr_obesidade', 'obesidade'),
                          ('fr_hist_familiar', 'história familiar DAC'),
                          ('fr_aterosclerose_conhecida', 'aterosclerose conhecida')]
           if dados.get(k)]
    if frs:
        partes.append('FRCV: ' + ', '.join(frs))

    tropo = {'normal': 'normal', 'elevada_1_3x': 'elevada 1–3× LSN',
             'elevada_3x': 'elevada > 3× LSN'}.get(dados.get('troponina', ''), '')
    if tropo:
        partes.append(f'Troponina {tropo}')

    # Negativas
    neg = []
    if dados.get('dor_lacerante_dorso') is False:  neg.append('dor lacerante/dorsal')
    if dados.get('choque_hipotensao') is False:    neg.append('instabilidade')
    if dados.get('assimetria_pulsos_pa') is False: neg.append('assimetria de pulsos')
    if neg:
        partes.append('Nega: ' + ', '.join(neg))

    return _partes_para_texto(partes, separador='. ')


def _analise_dtx(resultado: dict) -> str:
    """#Análise — dor torácica com HEART detalhado."""
    linhas = [resultado.get('diagnostico', '')]
    linhas.append(resultado.get('raciocinio', ''))
    itens = resultado.get('heart_itens', [])
    if itens and resultado.get('heart_score') is not None:
        linhas.append('Componentes HEART: ' + '; '.join(itens) + '.')
    return '\n'.join(l for l in linhas if l)


def gerar_subjetivo_crise_hipertensiva(admissao):
    dados = _get_dados_modulo(admissao, 'crise_hipertensiva', 'organico')
    if not dados:
        return ''
    partes = []

    pas, pad = dados.get('pas'), dados.get('pad')
    if pas and pad:
        partes.append(f'PA aferida {pas:.0f}×{pad:.0f} mmHg' if isinstance(pas, float)
                      else f'PA aferida {pas}×{pad} mmHg')

    tod = []
    if dados.get('tod_encefalopatia'): tod.append('🔴 confusão/cefaleia intensa')
    if dados.get('tod_convulsao'):     tod.append('🔴 convulsão')
    if dados.get('tod_deficit_focal'): tod.append('🔴 déficit focal novo')
    if dados.get('tod_dor_isquemica'): tod.append('🔴 dor torácica isquêmica')
    if dados.get('tod_eap'):           tod.append('🔴 dispneia/estertores')
    if dados.get('tod_dor_lacerante'): tod.append('🔴 dor lacerante dorsal')
    if tod:
        partes.append('Órgão-alvo: ' + ', '.join(tod))

    ctx = []
    if dados.get('dor_presente'):      ctx.append('dor presente')
    if dados.get('ansiedade_panico'):  ctx.append('ansiedade/pânico')
    if dados.get('retencao_urinaria'): ctx.append('retenção urinária')
    if dados.get('uso_cocaina_simpaticomimetico'): ctx.append('uso de simpaticomimético')
    if dados.get('gestante_20sem'):    ctx.append('gestante ≥ 20 sem')
    if dados.get('ma_adesao'):         ctx.append('má adesão ao tratamento')
    if ctx:
        partes.append('Contexto: ' + ', '.join(ctx))

    neg = []
    if dados.get('tod_encefalopatia') is False: neg.append('alteração neurológica')
    if dados.get('tod_dor_isquemica') is False: neg.append('dor torácica')
    if dados.get('tod_eap') is False:           neg.append('dispneia')
    if dados.get('tod_deficit_focal') is False: neg.append('déficit focal')
    if neg:
        partes.append('Nega: ' + ', '.join(neg))

    return _partes_para_texto(partes, separador='. ')


def _analise_cha(resultado: dict) -> str:
    """#Análise — crise hipertensiva."""
    linhas = [resultado.get('diagnostico', '')]
    linhas.append(resultado.get('raciocinio', ''))
    return '\n'.join(l for l in linhas if l)


def gerar_subjetivo_disglicemia(admissao):
    dados = _get_dados_modulo(admissao, 'disglicemia', 'organico')
    if not dados:
        return ''
    partes = []
    gli = dados.get('glicemia')
    if gli:
        partes.append(f'Glicemia capilar {gli:.0f} mg/dL' if isinstance(gli, float)
                      else f'Glicemia capilar {gli} mg/dL')
    pos = []
    if dados.get('rebaixamento'):                 pos.append('🔴 rebaixamento de consciência')
    if dados.get('sintomas_neuroglicopenicos'):   pos.append('sintomas neuroglicopênicos')
    if dados.get('cetonemia_cetonuria'):          pos.append('cetonemia/cetonúria')
    if pos:
        partes.append('Apresenta: ' + ', '.join(pos))
    ctx = []
    if dados.get('uso_sulfonilureia'):   ctx.append('uso de sulfonilureia')
    if dados.get('etilista_desnutrido'): ctx.append('etilista/desnutrido')
    if ctx:
        partes.append('Contexto: ' + ', '.join(ctx))
    return _partes_para_texto(partes, separador='. ')


def gerar_subjetivo_anafilaxia(admissao):
    dados = _get_dados_modulo(admissao, 'anafilaxia', 'organico')
    if not dados:
        return ''
    partes = []
    sis = []
    if dados.get('pele_mucosa'):                sis.append('pele/mucosa (urticária/angioedema/flushing)')
    if dados.get('comprometimento_respiratorio'): sis.append('🔴 respiratório')
    if dados.get('hipotensao_sincope'):         sis.append('🔴 cardiovascular (hipotensão/síncope)')
    if dados.get('sintomas_gi_graves'):         sis.append('GI grave')
    if sis:
        partes.append('Sistemas: ' + ', '.join(sis))
    if dados.get('exposicao_alergeno'):
        partes.append('Exposição a alérgeno conhecido/provável')
    if dados.get('angioedema_isolado'):
        partes.append('Angioedema isolado' + (' em uso de IECA' if dados.get('uso_ieca') else ''))
    if dados.get('uso_betabloqueador'):
        partes.append('Em uso de betabloqueador')
    return _partes_para_texto(partes, separador='. ')


def _analise_emergencia_generica(resultado: dict) -> str:
    """#Análise — diagnóstico + raciocínio (disglicemia, anafilaxia, dispneia)."""
    linhas = [resultado.get('diagnostico', ''), resultado.get('raciocinio', '')]
    return '\n'.join(l for l in linhas if l)


def _subjetivo_dispneia_pa(dados: dict) -> str:
    """Subjetivo do módulo de triagem de dispneia (formato web)."""
    partes = []
    rf = []
    if dados.get('rebaixamento'):          rf.append('🔴 rebaixamento')
    if dados.get('torax_silencioso'):      rf.append('🔴 tórax silencioso')
    if dados.get('exaustao_respiratoria'): rf.append('🔴 exaustão respiratória')
    if dados.get('cianose'):               rf.append('🔴 cianose')
    if rf:
        partes.append('Gravidade: ' + ', '.join(rf))

    congest = [l for k, l in [('ortopneia', 'ortopneia'), ('dpn', 'DPN'),
               ('edema_bilateral_mmii', 'edema bilateral MMII'), ('turgencia_jugular', 'TJ'),
               ('crepitantes_bibasais', 'crepitantes bibasais'), ('b3_ritmo_galope', 'B3')]
               if dados.get(k)]
    if congest:
        partes.append('Congestivo: ' + ', '.join(congest))

    infec = [l for k, l in [('febre', 'febre'), ('tosse_produtiva', 'tosse produtiva'),
             ('crepitantes_localizados', 'crepitantes localizados')] if dados.get(k)]
    if infec:
        partes.append('Infeccioso: ' + ', '.join(infec))

    obstr = [l for k, l in [('sibilos', 'sibilos'), ('tabagista', 'tabagista'),
             ('dpoc_conhecida', 'DPOC conhecida'), ('asma_conhecida', 'asma conhecida')]
             if dados.get(k)]
    if obstr:
        partes.append('Obstrutivo: ' + ', '.join(obstr))

    embol = [l for k, l in [('inicio_subito', 'início súbito'), ('dor_pleuritica', 'dor pleurítica'),
             ('hemoptise', 'hemoptise'), ('fator_risco_tev', 'fator de risco TEV')]
             if dados.get(k)]
    if embol:
        partes.append('Súbito/embólico: ' + ', '.join(embol))

    focal = [l for k, l in [('mv_abolido_unilateral', 'MV abolido unilateral'),
             ('timpanismo', 'timpanismo'), ('macicez', 'macicez'),
             ('trauma_toracico', 'trauma torácico'), ('desvio_traqueia', '🔴 desvio de traqueia')]
             if dados.get(k)]
    if focal:
        partes.append('Ausculta/percussão: ' + ', '.join(focal))

    hb = dados.get('hb')
    naopulm = []
    if hb: naopulm.append(f'Hb {hb}')
    if dados.get('palidez'): naopulm.append('palidez')
    if dados.get('parestesias_periorais'): naopulm.append('parestesias periorais')
    if dados.get('contexto_ansiedade'): naopulm.append('contexto ansioso')
    if naopulm:
        partes.append('Não-pulmonar: ' + ', '.join(naopulm))

    return _partes_para_texto(partes, separador='. ')


def _plano_tep(resultado: dict) -> str:
    """#Plano A/B — genérico para módulos de emergência (TEP, dor torácica…)."""
    linhas = []

    for alerta in resultado.get('alertas_seguranca', []):
        linhas.append(alerta)
    if resultado.get('alertas_seguranca'):
        linhas.append('')

    for chave in ('plano_a', 'plano_b'):
        plano = resultado.get(chave)
        if not plano:
            continue
        linhas.append(f"▶ {plano['titulo']}")
        for item in plano['itens']:
            linhas.append(f'  • {item}')
        linhas.append('')

    return '\n'.join(linhas).rstrip()


# ------------------------------------------------------------------
# ORL — Odinofagia / Dor de Garganta — Subjetivo
# ------------------------------------------------------------------

def gerar_subjetivo_odinofagia(admissao):
    dados = _get_dados_modulo(admissao, 'odinofagia', 'organico')
    if not dados:
        return ''
    partes = []

    # Achados faríngeos positivos
    farm = []
    if dados.get('febre'):
        temp = dados.get('temperatura_grau')
        farm.append(f'febre ({temp}°C)' if temp else 'febre')
    if dados.get('exsudato_amigdaliano'):  farm.append('exsudato amigdaliano')
    if dados.get('adenopatia_cervical_ant'): farm.append('adenopatia cervical anterior dolorosa')
    if dados.get('rouquidao'):             farm.append('rouquidão')
    if dados.get('rouquidao_cronica'):     farm.append('rouquidão > 3 semanas')
    if farm:
        partes.append(f'Apresenta: {", ".join(farm)}')

    # Sinais de alarme / abscesso
    alarme = []
    if dados.get('trismo'):               alarme.append('trismo')
    if dados.get('sialorreia'):           alarme.append('sialorreia')
    if dados.get('voz_batata'):           alarme.append('voz "de batata quente"')
    if dados.get('desvio_uvula'):         alarme.append('desvio de úvula')
    if dados.get('disfagia_saliva'):      alarme.append('incapaz de engolir saliva')
    if dados.get('estridor'):             alarme.append('⚠ ESTRIDOR')
    if dados.get('dificuldade_respiratoria'): alarme.append('⚠ dificuldade respiratória')
    if alarme:
        partes.append(f'Sinais de alarme: {", ".join(alarme)}')

    # Contexto infeccioso
    ctx = []
    if dados.get('adenopatia_generalizada'): ctx.append('adenopatia generalizada')
    if dados.get('esplenomegalia_referida'):  ctx.append('dor em QSE / esplenomegalia')
    if dados.get('rash_apos_amox'):           ctx.append('rash após amoxicilina')
    if ctx:
        partes.append(f'{", ".join(ctx).capitalize()}')

    # Pertinentes negativos
    neg = []
    if dados.get('tosse') is False:               neg.append('tosse')
    if dados.get('exsudato_amigdaliano') is False: neg.append('exsudato amigdaliano')
    if dados.get('adenopatia_cervical_ant') is False: neg.append('adenopatia cervical')
    if dados.get('trismo') is False:              neg.append('trismo')
    if dados.get('estridor') is False:            neg.append('estridor')
    if neg:
        partes.append(f'Nega: {", ".join(neg)}')

    # Alergias
    if dados.get('alergia_penicilina_grave'):
        partes.append('Alergia GRAVE à penicilina (anafilaxia/urticária)')
    elif dados.get('alergia_penicilina'):
        partes.append('Alergia não grave à penicilina')

    return _partes_para_texto(partes, separador='. ')


# ------------------------------------------------------------------
# ORL — Otalgia / Dor de Ouvido — Subjetivo
# ------------------------------------------------------------------

def gerar_subjetivo_otalgia(admissao):
    dados = _get_dados_modulo(admissao, 'otalgia', 'organico')
    if not dados:
        return ''
    partes = []

    # Lateralidade
    lat = dados.get('lateralidade', '')
    lat_txt = {'direito': 'direita', 'esquerdo': 'esquerda', 'bilateral': 'bilateral'}.get(lat, '')
    intro = f'Otalgia {lat_txt}' if lat_txt else 'Otalgia'
    if dados.get('otalgia_grave'):
        intro += ' intensa'
    partes.append(intro)

    # Achados otoscópicos / canal
    otos = []
    if dados.get('trago_positivo'):      otos.append('trago positivo')
    if dados.get('canal_edema'):         otos.append('edema de canal')
    if dados.get('mt_abaulada'):         otos.append('MT abaulada')
    if dados.get('mt_hiperemia'):        otos.append('MT hiperemiada')
    if dados.get('mt_efusao'):           otos.append('efusão retrochimpânica')
    if dados.get('mt_perfurada'):        otos.append('perfuração timpânica')
    if dados.get('otorreia_purulenta'):  otos.append('otorreia purulenta')
    elif dados.get('otorreia'):          otos.append('otorreia')
    if otos:
        partes.append(f'Ao exame: {", ".join(otos)}')

    # Sintomas associados
    assoc = []
    if dados.get('iras_recente'):        assoc.append('IVAS precedeu o quadro')
    if dados.get('ouvido_cheio'):        assoc.append('sensação de ouvido cheio')
    if dados.get('hipoagusia'):          assoc.append('hipoacusia')
    if dados.get('banho_piscina'):       assoc.append('exposição a água/piscina')
    if dados.get('conjuntivite_purulenta'): assoc.append('conjuntivite purulenta')
    if dados.get('febre'):
        temp = dados.get('temperatura_grau')
        assoc.append(f'febre ({temp}°C)' if temp else 'febre')
    if assoc:
        partes.append('Associado: ' + ', '.join(assoc))

    # Sinais de alarme / mastoidite
    alarme = []
    if dados.get('dor_retroauricular'): alarme.append('⚠ dor retroauricular')
    if dados.get('pavilhao_projetado'): alarme.append('⚠ pavilhão projetado')
    if dados.get('flutuacao_retroaur'): alarme.append('⚠ flutuação retroauricular')
    if alarme:
        partes.append(f'Sinais alarme: {", ".join(alarme)}')

    # DTM
    dtm = []
    if dados.get('dor_mastigacao'): dtm.append('dor ao mastigar')
    if dados.get('bruxismo'):       dtm.append('bruxismo')
    if dados.get('click_mandibula'): dtm.append('estalido mandibular')
    if dados.get('dor_matinal'):    dtm.append('dor matinal')
    if dtm:
        partes.append(f'DTM: {", ".join(dtm)}')

    # Pertinentes negativos
    neg = []
    if dados.get('dor_retroauricular') is False: neg.append('dor retroauricular')
    if dados.get('trago_positivo') is False:     neg.append('dor à compressão do trago')
    if dados.get('otorreia') is False:           neg.append('otorreia')
    if neg:
        partes.append(f'Nega: {", ".join(neg)}')

    return _partes_para_texto(partes, separador='. ')


# ------------------------------------------------------------------
# ORL — Rinossinusite / Obstrução Nasal — Subjetivo
# ------------------------------------------------------------------

def gerar_subjetivo_rinossinusite(admissao):
    dados = _get_dados_modulo(admissao, 'rinossinusite', 'organico')
    if not dados:
        return ''
    partes = []

    # Duração
    dur = dados.get('duracao_dias_aprox', 0) or 0
    if dur:
        partes.append(f'Sintomas nasossinusais há {dur} dias')
    elif dados.get('duracao_cronica'):
        partes.append('Rinossinusite crônica (≥ 12 semanas)')

    # Sintomas nasais positivos
    sxs = []
    if dados.get('obstrucao_nasal'):        sxs.append('obstrução nasal')
    if dados.get('rinorreia_purulenta'):    sxs.append('rinorreia purulenta')
    if dados.get('rinorreia_clara'):        sxs.append('rinorreia clara')
    if dados.get('rinorreia'):              sxs.append('rinorreia')
    if dados.get('gotejamento_pos_nasal'):  sxs.append('gotejamento pós-nasal')
    if dados.get('dor_facial'):             sxs.append('dor/pressão facial')
    if dados.get('hiposmia_anosmia'):       sxs.append('hiposmia/anosmia')
    if dados.get('febre'):
        sxs.append('febre alta' if dados.get('febre_alta') else 'febre')
    if sxs:
        txt_sxs = ', '.join(sxs)
        partes.append(txt_sxs[0].upper() + txt_sxs[1:])

    # Padrão alérgico
    alergi = []
    if dados.get('espirros_salva'):         alergi.append('espirros em salva')
    if dados.get('prurido_nasal_ocular'):   alergi.append('prurido nasal/ocular')
    if dados.get('piora_sazonal'):          alergi.append('piora sazonal')
    if dados.get('alergenos_conhecidos'):   alergi.append('alérgenos conhecidos')
    if alergi:
        partes.append(f'Padrão alérgico: {", ".join(alergi)}')

    # Curso / piora
    if dados.get('double_sickening'):
        partes.append('Double-sickening — piora após período de melhora')

    # Red flags
    rf = []
    if dados.get('edema_periorbital'):      rf.append('⚠ edema periorbital')
    if dados.get('diplopia'):               rf.append('⚠ diplopia')
    if dados.get('proptose'):               rf.append('⚠ proptose')
    if dados.get('rigidez_nucal'):          rf.append('⚠ rigidez de nuca')
    if dados.get('cefaleia_intensa'):       rf.append('⚠ cefaleia intensa')
    if dados.get('alteracao_consciencia'):  rf.append('⚠ alt. de consciência')
    if rf:
        partes.append(f'Red flags: {", ".join(rf)}')

    # Pertinentes negativos
    neg = []
    if dados.get('rinorreia_purulenta') is False:  neg.append('rinorreia purulenta')
    if dados.get('dor_facial') is False:           neg.append('dor facial')
    if dados.get('febre') is False:                neg.append('febre')
    if dados.get('edema_periorbital') is False:    neg.append('edema periorbital')
    if neg:
        partes.append(f'Nega: {", ".join(neg)}')

    return _partes_para_texto(partes, separador='. ')


# ------------------------------------------------------------------
# Oftalmo — Olho Vermelho — Subjetivo
# ------------------------------------------------------------------

def gerar_subjetivo_olho_vermelho(admissao):
    dados = _get_dados_modulo(admissao, 'olho_vermelho', 'organico')
    if not dados:
        return ''
    partes = []

    # Lateralidade
    lat = dados.get('lateralidade', '')
    lat_txt = {'direito': 'direito', 'esquerdo': 'esquerdo', 'bilateral': 'bilateral'}.get(lat, '')
    intro = f'Olho vermelho {lat_txt}' if lat_txt else 'Olho vermelho'
    if dados.get('bilateral'):
        intro = 'Olho vermelho bilateral'
    partes.append(intro)

    # Sintomas visuais / dor
    sxs = []
    if dados.get('dor_intensa'):        sxs.append('dor intensa')
    elif dados.get('dor_ocular'):       sxs.append('desconforto ocular')
    if dados.get('visao_turva'):        sxs.append('visão turva')
    if dados.get('halos_coloridos'):    sxs.append('halos coloridos')
    if dados.get('fotofobia'):          sxs.append('fotofobia')
    if dados.get('corpo_estranho_sensacao'): sxs.append('sensação de corpo estranho')
    if dados.get('prurido_ocular'):     sxs.append('prurido ocular')
    if sxs:
        txt_sxs = ', '.join(sxs)
        partes.append(txt_sxs[0].upper() + txt_sxs[1:])

    # Secreção
    sec = []
    if dados.get('secrecao_purulenta'):  sec.append('secreção purulenta')
    if dados.get('palpebra_grudada'):    sec.append('pálpebra grudada ao acordar')
    if dados.get('secrecao_aquosa'):     sec.append('secreção aquosa')
    if dados.get('lacrimejamento'):      sec.append('lacrimejamento')
    if sec:
        txt_sec = ', '.join(sec)
        partes.append(txt_sec[0].upper() + txt_sec[1:])

    # Contexto / epidemiologia
    ctx = []
    if dados.get('lente_de_contato'):         ctx.append('usuário de lente de contato')
    if dados.get('dormiu_com_lente'):         ctx.append('dormiu com lente')
    if dados.get('pos_cirurgico_ocular'):     ctx.append('pós-cirúrgico ocular')
    if dados.get('contato_conjuntivite'):     ctx.append('contato com conjuntivite')
    if dados.get('adenopatia_preauricular'):  ctx.append('adenopatia pré-auricular')
    if dados.get('rinite_alergica_conhecida'): ctx.append('rinite alérgica conhecida')
    if ctx:
        txt_ctx = ', '.join(ctx)
        partes.append(txt_ctx[0].upper() + txt_ctx[1:])

    # Trauma
    if dados.get('trauma_quimico'):
        partes.append('⚠ Trauma químico (lavagem imediata)')
    if dados.get('trauma_penetrante'):
        partes.append('⚠ Trauma penetrante')

    # Red flags
    rf = []
    if dados.get('ciliary_flush'):          rf.append('⚠ ciliary flush')
    if dados.get('edema_palpebral') and dados.get('limitacao_motilidade'): rf.append('⚠ limitação de motilidade')
    if dados.get('proptose'):               rf.append('⚠ proptose')
    if rf:
        partes.append(f'Red flags: {", ".join(rf)}')

    # Pertinentes negativos
    neg = []
    if dados.get('dor_intensa') is False:        neg.append('dor intensa')
    if dados.get('visao_turva') is False:        neg.append('queda de acuidade visual')
    if dados.get('halos_coloridos') is False:    neg.append('halos coloridos')
    if dados.get('secrecao_purulenta') is False: neg.append('secreção purulenta')
    if dados.get('ciliary_flush') is False:      neg.append('ciliary flush')
    if neg:
        partes.append(f'Nega: {", ".join(neg)}')

    return _partes_para_texto(partes, separador='. ')


SINTOMAS_REGISTRADOS = [
    ("dispneia",  gerar_subjetivo_dispneia,  gerar_objetivo_dispneia),
    ("vertigem",  gerar_subjetivo_vertigem,  gerar_objetivo_vertigem),
    ("cefaleia",  gerar_subjetivo_cefaleia,  gerar_objetivo_cefaleia),
    ("joelho",    gerar_subjetivo_joelho,    gerar_objetivo_joelho),
    ("ombro",     gerar_subjetivo_ombro,     gerar_objetivo_ombro),
    ("coluna",       gerar_subjetivo_coluna,       gerar_objetivo_coluna),
    ("fibromialgia", gerar_subjetivo_fibromialgia, gerar_objetivo_fibromialgia),
    ("quadril",      gerar_subjetivo_quadril,      gerar_objetivo_quadril),
    ("tornozelo_pe", gerar_subjetivo_tornozelo_pe, gerar_objetivo_tornozelo_pe),
    ("mao_punho",    gerar_subjetivo_mao_punho,    gerar_objetivo_mao_punho),
    ("tosse",        gerar_subjetivo_tosse,        lambda _: ""),
    ("fadiga",   gerar_subjetivo_fadiga,   lambda _: ""),
    ("diarreia",     gerar_subjetivo_diarreia,     lambda _: ""),
    ("arboviroses",  gerar_subjetivo_arboviroses,  lambda _: ""),
    ("ivas",         gerar_subjetivo_ivas,         lambda _: ""),
    ("palpitacao",   gerar_subjetivo_palpitacao,   lambda _: ""),
    ("urinario",     gerar_subjetivo_urinario,     lambda _: ""),
    ("gota",         gerar_subjetivo_gota,         gerar_objetivo_gota),
    ("sincope",      gerar_subjetivo_sincope,      gerar_objetivo_sincope),
    ("anorretal",    gerar_subjetivo_anorretal,    gerar_objetivo_anorretal),
    ("edema",        gerar_subjetivo_edema,        gerar_objetivo_edema),
    ("ictericia",    gerar_subjetivo_ictericia,    gerar_objetivo_ictericia),
    ("asma",         gerar_subjetivo_asma,         gerar_objetivo_asma),
    ("dpoc",         gerar_subjetivo_dpoc,         gerar_objetivo_dpoc),
    ("celulite",     gerar_subjetivo_celulite,     gerar_objetivo_celulite),
    ("hemorragia",   gerar_subjetivo_hemorragia,   gerar_objetivo_hemorragia),
    ("febre",        gerar_subjetivo_febre,        gerar_objetivo_febre),
    ("gastro",       gerar_subjetivo_gastro,       gerar_objetivo_gastro),
    ("sono",         gerar_subjetivo_sono,         lambda _: ""),
    ("consciencia",  gerar_subjetivo_consciencia,  lambda _: ""),
    ("linfadenopatia", gerar_subjetivo_linfadenopatia, lambda _: ""),
    ("anemia",       gerar_subjetivo_anemia,       lambda _: ""),
    ("tep",          gerar_subjetivo_tep,          lambda _: ""),
    ("dor_toracica", gerar_subjetivo_dor_toracica, lambda _: ""),
    ("crise_hipertensiva", gerar_subjetivo_crise_hipertensiva, lambda _: ""),
    ("disglicemia",  gerar_subjetivo_disglicemia,  lambda _: ""),
    ("anafilaxia",   gerar_subjetivo_anafilaxia,   lambda _: ""),
    ("odinofagia",   gerar_subjetivo_odinofagia,   lambda _: ""),
    ("otalgia",      gerar_subjetivo_otalgia,       lambda _: ""),
    ("rinossinusite",gerar_subjetivo_rinossinusite, lambda _: ""),
    ("olho_vermelho",gerar_subjetivo_olho_vermelho, lambda _: ""),
    # ("dor_toracica", gerar_subjetivo_dor_toracica, gerar_objetivo_dor_toracica),
]


# ------------------------------------------------------------------
# PRONTUÁRIO
# ------------------------------------------------------------------
# RECEITAS — renderização universal de prescricoes_estruturadas
# ------------------------------------------------------------------

def _render_receitas(resultado):
    """
    Converte prescricoes_estruturadas + orientacoes de qualquer resultado
    no formato de receituário clínico (Rx pad), pronto para copiar ao documento.

    Formato por prescrição:
        Medicamento Dose ─────────── Quantidade
        Posologia
        Obs.: Nota (se existir)

    Depois das prescrições, exibe seção Orientações se existirem.
    Retorna '' se não há nem prescrições nem orientações.
    """
    rxs        = resultado.get('prescricoes_estruturadas', [])
    orientacoes = resultado.get('orientacoes', {})
    if not rxs and not orientacoes:
        return ''

    _SEP_WIDTH = 42  # largura total da linha de cabeçalho do Rx

    linhas = []

    for i, rx in enumerate(rxs):
        if i > 0:
            linhas.append('')

        med    = rx.get('medicamento', '')
        linha  = rx.get('linha', '')          # ex.: '1ª linha — antiemético'
        nota   = rx.get('nota', '')
        presc  = rx.get('prescricoes', [])

        if linha:
            linhas.append(f'({linha})')

        for p in presc:
            unidade   = p.get('unidade', '')
            quantidade = p.get('quantidade', '')
            posologia  = p.get('posologia', '')

            med_dose = f'{med} {unidade}'.strip()
            dots = '─' * max(4, _SEP_WIDTH - len(med_dose))
            linhas.append(f'{med_dose} {dots} {quantidade}')
            if posologia:
                linhas.append(posologia)

        if nota:
            linhas.append(f'Obs.: {nota}')

    if orientacoes:
        linhas.append('')
        linhas.append('Orientações:')
        _TITULO = {
            # ── Gerais ──────────────────────────────────────────────────
            'hidratacao':        'Hidratação',
            'repouso':           'Repouso',
            'sinais_retorno':    'Sinais de retorno',
            # ── Diarreia / GECA ─────────────────────────────────────────
            'reidratacao_oral':  'Reidratação oral',
            'alimentacao':       'Alimentação',
            # ── IVAS ────────────────────────────────────────────────────
            'atb_adesao':        'Adesão ao antibiótico',
            'aguardar_radt':     'Aguardar resultado do RADT',
            'restricao_esportes': 'Restrição esportiva',
            'alerta_amoxicilina': 'Alerta — Amoxicilina',
            'lavagem_nasal':     'Lavagem nasal',
            'repouso_vocal':     'Repouso vocal',
            # ── Tosse ───────────────────────────────────────────────────
            'mel':               'Mel (alívio da tosse)',
            'expectativa':       'Evolução esperada',
            'suspender_ieca':    'Suspender IECA',
            'prazo':             'Prazo para melhora',
            'tecnica_inalatoria': 'Técnica inalatória',
            'gatilhos':          'Evitar gatilhos',
            'medidas_comportamentais': 'Medidas comportamentais',
            'isolamento':        'Isolamento',
            'contatos':          'Comunicantes',
            # ── Arboviroses ─────────────────────────────────────────────
            'fase_critica':      'Fase crítica (D3-D6)',
            'observacao':        'Observação na UBS',
            'aguardar_ns1':      'Aguardar NS1 Dengue',
            'articulacoes':      'Articulações',
            'fisioterapia':      'Fisioterapia',
            'prevencao_sexual':  'Prevenção sexual',
            # ── Palpitação ──────────────────────────────────────────────
            'alerta_wpw':        'Alerta WPW',
            'brugada_alerta':    'Alerta Brugada',
            'qt_longo_alerta':   'Alerta QT longo',
            'sincope_cuidados':  'Cuidados pós-síncope',
            'fa_orientacao':     'Sobre a FA',
            'fa_controle_fc':    'Sobre o controle da FC',
            'fa_cronica':        'FA crônica — cuidados',
            'valsalva_tecnica':  'Manobra de Valsalva',
            'quando_ps':         'Quando ir ao PS',
            'retorno_urgente':   'Retorno urgente',
            'extrassistolia_info': 'Sobre as batidas extras',
            'tireoidismo_info':  'Sobre a tireoide',
            'anemia_info':       'Sobre a anemia',
            'panico_info':       'Sobre o pânico',
            'farmaco_info':      'Sobre a substância',
            'inespecifico_info': 'Sobre a palpitação',
            # ── ORL / Oftalmo ───────────────────────────────────────────
            'sinais_de_alerta':  'Sinais de alerta — retornar imediatamente',
            'alivio_garganta':   'Alívio da garganta',
            'atb_compliance':    'Antibiótico — usar até o fim',
            'transmissao':       'Transmissão',
            'higiene_ocular':    'Higiene ocular',
            'higiene_maos':      'Higiene das mãos',
            'compressas':        'Compressas',
            'lentes_contato':    'Lentes de contato',
            'analgesia':         'Analgesia',
            'ouvido_seco':       'Manter ouvido seco',
            'calor_local':       'Calor local',
            'lente_de_contato':  'Lentes de contato',
            'tranquilizacao':    'Tranquilização',
            'encaminhar':        'Encaminhamento',
            'retorno':           'Retorno',
        }
        for chave, texto in orientacoes.items():
            titulo = _TITULO.get(chave, chave.replace('_', ' ').capitalize())
            # Valores em lista (ex.: sinais_de_alerta) → um bullet por item
            if isinstance(texto, (list, tuple)):
                linhas.append(f'• {titulo}:')
                for item in texto:
                    linhas.append(f'    ⚠ {item}')
            else:
                linhas.append(f'• {titulo}: {texto}')

    return '\n'.join(linhas)


# =============================================================================
# CID-10 — LOOKUP CENTRAL
# =============================================================================

_CID_MAP = {
    # ── IVAS ──────────────────────────────────────────────────────────────────
    'ivas_viral':                    'J06.9',   # IVAS sem especificação
    'ivas_gas':                      'J02.0',   # Faringite estreptocócica
    'ivas_mononucleose':             'B27.0',   # Mononucleose infecciosa por EBV
    'ivas_influenza':                'J11.1',   # Influenza sem vírus identificado
    'ivas_rinossinusite':            'J01.9',   # Rinossinusite aguda
    'ivas_laringite':                'J04.0',   # Laringite aguda
    # ivas_emergencia → tratado com sub-lookup abaixo

    # ── Tosse ─────────────────────────────────────────────────────────────────
    'tosse_aguda_viral':             'J06.9',
    'tosse_aguda_bacteriana':        'J18.9',   # Pneumonia não especificada
    'tosse_pertussis_suspeita':      'A37.9',   # Coqueluche sem especificação
    'tosse_subaguda_pos_infecciosa': 'R05',     # Tosse
    'tosse_ieca':                    'R05',
    'tosse_uacs':                    'J30.4',   # Rinite alérgica não especificada
    'tosse_asma_variante':           'J45.9',   # Asma não especificada
    'tosse_drge_lpr':                'K21.9',   # DRGE sem esofagite
    'tosse_tb_suspeita':             'A16.2',   # TB pulmonar sem confirmação bact.
    'tosse_pneumonia_atipica':       'J22',     # Infecção aguda NE das VAS inferiores
    'tosse_pcp_suspeita':            'B59',     # Pneumocistose (Pneumocystis jirovecii)
    'tosse_neoplasia_suspeita':      'C34.9',   # Neoplasia maligna do brônquio/pulmão
    'investigar_tosse_cronica':      'R05',

    # ── Diarreia ──────────────────────────────────────────────────────────────
    'diarreia_aguda_watery':         'A09',     # Gastroenterite infecciosa presumida
    'diarreia_toxinfeccao':          'A05.9',   # Intoxicação alimentar bacteriana NE
    'diarreia_disenteria_bacilar':   'A03.9',   # Shigelose NE
    'diarreia_stec_suspeita':        'A04.3',   # E. coli enterohemorrágica
    'diarreia_c_diff':               'A04.7',   # Enterocolite por C. difficile
    'diarreia_viajante':             'A09',
    'diarreia_persistente':          'K52.9',   # Gastroenterite NE não infecciosa
    'diarreia_sii_d':                'K58.0',   # SII com diarreia
    'diarreia_dii_suspeita':         'K52.9',   # Colite NE (DII suspeita)
    'diarreia_cronica_alarme_eletivo': 'K52.9',
    'diarreia_cronica_alarme_urgente': 'K52.9',
    'diarreia_imunossuprimido':      'K52.9',
    'diarreia_sepse':                'A09',

    # ── Arboviroses ───────────────────────────────────────────────────────────
    'arboviral_grupo_a':             'A90',     # Dengue (sem hemorragia)
    'arboviral_grupo_b':             'A90',
    'arboviral_grupo_c':             'A91',     # Dengue hemorrágica
    'arboviral_grupo_d':             'A91',
    'chikungunya_suspeita':          'A92.0',   # Febre Chikungunya
    'zika_suspeita':                 'A92.8',   # Outras febres arbovira especificadas
    'arboviral_indiferenciada':      'A92.9',   # Febre viral por artrópode NE

    # ── Palpitação ────────────────────────────────────────────────────────────
    'pal_instabilidade_hemodinamica': 'I49.9',  # Arritmia cardíaca NE
    'pal_wpw':                        'I45.6',  # Síndrome de pré-excitação
    'pal_tv_qrs_largo':               'I47.2',  # Taquicardia ventricular
    'pal_brugada_sincope':            'I49.8',  # Outras arritmias cardíacas especificadas
    'pal_qt_longo_sincope':           'I49.8',
    'pal_flutter':                    'I48.3',  # Flutter atrial típico
    'pal_fa_nova_cardioversao':       'I48.0',  # FA paroxística
    'pal_fa_nova_controle_fc':        'I48.0',
    'pal_fa_cronica':                 'I48.2',  # FA persistente de longa duração
    'pal_tsv_paroxistica':            'I47.1',  # Taquicardia supraventricular
    'pal_extrassistolia':             'I49.4',  # Outras extrassístoles
    'pal_sincope_arritmia':           'I49.9',
    'pal_anemia':                     'D64.9',  # Anemia NE
    'pal_hipertireoidismo':           'E05.9',  # Tireotoxicose NE
    'pal_ansiedade_panico':           'F41.0',  # Transtorno de pânico
    'pal_farmaco_estimulante':        'F15.1',  # Transt. por uso de estimulantes
    'pal_inespecifico':               'R00.2',  # Palpitações

    # ── Urinário ──────────────────────────────────────────────────────────────
    'cistite_simples':               'N30.0',   # Cistite aguda
    'cistite_complicada':            'N30.0',
    'cistite_recorrente':            'N30.0',
    'cistite_gestante':              'O23.1',   # ITU na gravidez
    'pielonefrite_ambulatorial':     'N10',     # Nefrite tubulointersticial aguda
    'pielonefrite_emergencia':       'N10',
    'itu_masculina':                 'N39.0',   # ITU de localização NE
    'prostatite_aguda':              'N41.0',   # Prostatite aguda
    'prostatite_cronica':            'N41.1',   # Prostatite crônica
    'uretrite_ist':                  'N34.1',   # Uretrite não específica
    'sd_uretral':                    'N34.3',   # Síndrome uretral aguda
    'hpb_stui':                      'N40',     # Hiperplasia benigna da próstata
    'hematuria_macro_itu':           'R31',     # Hematúria
    'hematuria_macro_calculose':     'N20.9',   # Cálculo urinário NE
    'hematuria_macro_urgente':       'R31',
    'hematuria_micro_alto_risco':    'R31',
    'hematuria_micro_moderado_risco': 'R31',
    'hematuria_micro_baixo_risco':   'R31',
    'hematuria_micro_glomerular':    'N02.9',   # Hematúria recorrente e persistente
    'hematuria_nao_confirmada':      'R31',
    'herpes_genital':                'A60.0',   # Herpes genital
    'vaginite_candida':              'B37.3',   # Candidíase vulvovaginal
    'vaginite_bv':                   'N76.0',   # Vaginite aguda
    'vaginite_atrofica':             'N95.2',   # Vaginite atrófica pós-menopausa
    'red_flag_urinario':             'N39.0',

    # ── ORL — Odinofagia ──────────────────────────────────────────────────────
    'orl_mononucleose':              'B27.0',
    'orl_disfonia_cronica':          'J38.3',   # Outras doenças das cordas vocais
    'orl_faringoamigdalite_bacteriana': 'J03.0', # Amigdalite estreptocócica
    'orl_faringoamigdalite_test_treat': 'J02.9', # Faringite aguda NE (aguardando TRA)
    'orl_faringoamigdalite_viral':   'J02.9',   # Faringite aguda NE
    'orl_abscesso_periamigdaliano':  'J36',     # Abscesso periamigdaliano
    'orl_emergencia_respiratoria':   'J05.1',   # Epiglotite aguda (obstrução VA suspeita)

    # ── ORL — Otalgia ─────────────────────────────────────────────────────────
    'orl_otite_media_aguda':         'H66.0',   # Otite média supurativa aguda
    'orl_otite_externa':             'H60.9',   # Otite externa NE
    'orl_otite_externa_maligna':     'H60.2',   # Otite externa maligna (necrotizante)
    'orl_mastoidite':                'H70.9',   # Mastoidite NE
    'orl_dtm':                       'K07.6',   # Disfunção articulação temporomandibular
    'orl_otalgia_inespecifica':      'H92.0',   # Otalgia

    # ── Oftalmologia ──────────────────────────────────────────────────────────
    'oft_conjuntivite_viral':        'B30.9',   # Conjuntivite viral NE
    'oft_conjuntivite_bacteriana':   'H10.0',   # Conjuntivite mucopurulenta
    'oft_conjuntivite_alergica':     'H10.1',   # Conjuntivite atópica aguda
    'oft_hemorragia_subconj':        'H11.3',   # Hemorragia subconjuntival
    'oft_glaucoma_agudo':            'H40.2',   # Glaucoma de ângulo fechado
    'oft_uveite_glaucoma_suspeito':  'H20.9',   # Iridociclite NE
    'oft_ulcera_cornea':             'H16.0',   # Úlcera da córnea
    'oft_hordeoleo':                 'H00.0',   # Hordéolo e calázio
    'oft_celulite_preseptal':        'H05.0',   # Celulite orbitária
    'oft_celulite_orbitaria':        'H05.0',
    'oft_endoftalmite':              'H44.0',   # Endoftalmite purulenta
    'oft_trauma_ocular':             'S05.9',   # Traumatismo do olho NE
    'oft_olho_vermelho_inespecifico': 'H10.9',  # Conjuntivite NE

    # ── ORL — Rinossinusite ───────────────────────────────────────────────────
    'orl_ivas_viral':                          'J06.9',  # IVAS viral NE
    'orl_rinite_alergica':                     'J30.4',  # Rinite alérgica NE
    'orl_rinossinusite_intermediario':         'J01.9',  # Rinossinusite aguda NE — observação ativa
    'orl_rsab':                                'J01.9',  # Rinossinusite aguda bacteriana
    'orl_rsc':                                 'J32.9',  # Rinossinusite crônica NE
    'orl_rsc_polipose':                        'J33.0',  # Pólipo nasal
    'orl_rinossinusite_complicacao_orbital':   'H05.0',  # Celulite orbitária (complicação)
    'orl_rinossinusite_complicacao_meningea':  'G00.9',  # Meningite bacteriana NE (complicação)

    # ── Febre sem Foco ────────────────────────────────────────────────────────
    'febre_emergencia':       'R50.9',  # Febre NE — emergência
    'febre_com_foco':         'R50.9',  # Febre com foco — ver módulo específico
    'febre_aguda_viral':      'B34.9',  # Infecção viral NE
    'febre_aguda_investigar': 'R50.9',  # Febre sem foco — investigação
    'febre_prolongada':       'R50.1',  # Febre persistente
    'febre_fuo':              'R50.1',  # Febre de origem desconhecida

    # ── Asma ──────────────────────────────────────────────────────────────────
    'asma_emergencia':           'J45.1',  # Asma predominantemente alérgica — risco de vida
    'asma_crise_grave':          'J45.1',  # Asma grave — PS
    'asma_crise_leve_moderada':  'J45.1',  # Asma leve-moderada — APS
    'asma_controlada':           'J45.1',  # Asma controlada
    'asma_parcialmente_ctrl':    'J45.1',  # Asma parcialmente controlada
    'asma_nao_controlada':       'J45.1',  # Asma não controlada

    # ── DPOC ──────────────────────────────────────────────────────────────────
    'dpoc_emergencia':           'J44.1',  # DPOC com exacerbação aguda — grave
    'dpoc_exacerbacao_moderada': 'J44.1',  # DPOC exacerbação moderada — APS
    'dpoc_exacerbacao_leve':     'J44.1',  # DPOC exacerbação leve
    'dpoc_grupo_a':              'J44.1',  # DPOC Grupo A
    'dpoc_grupo_b':              'J44.1',  # DPOC Grupo B
    'dpoc_grupo_e':              'J44.1',  # DPOC Grupo E (exacerbador)

    # ── Síncope ───────────────────────────────────────────────────────────────
    'sincope_emergencia':           'R55',    # Síncope e colapso — emergência
    'sincope_vasovagal':            'R55',    # Síncope vasovagal
    'sincope_situacional':          'R55',    # Síncope situacional
    'sincope_ortostatica':          'I95.1',  # Hipotensão ortostática
    'sincope_cardiaca_alto_risco':  'I49.9',  # Arritmia NE — síncope de alto risco
    'sincope_cardiaca_medio_risco': 'R55',    # Síncope — causa cardíaca intermediária
    'sincope_indeterminada':        'R55',    # Síncope de causa indeterminada

    # ── Anorretal ─────────────────────────────────────────────────────────────
    'anorretal_colonoscopia_urgente': 'K62.5',  # Hemorragia retal — urgente
    'hemorroida_grau_1_2':           'K64.0',  # Hemorroidas grau I-II
    'hemorroida_grau_3':             'K64.2',  # Hemorroidas grau III
    'hemorroida_grau_4':             'K64.3',  # Hemorroidas grau IV
    'hemorroida_trombosada':         'K64.5',  # Hemorroida perianal trombosada
    'fissura_anal':                  'K60.2',  # Fissura anal NE
    'prurido_anal':                  'L29.0',  # Prurido anal

    # ── Edema de Membros Inferiores ───────────────────────────────────────────
    'edema_dvt_alto_risco':    'I80.2',  # Tromboflebite — TVP suspeita
    'edema_dvt_baixo_risco':   'R60.0',  # Edema localizado
    'edema_celulite':          'L03.1',  # Celulite de MMII
    'edema_cardiaco':          'I50.9',  # Insuficiência cardíaca NE
    'edema_renal_nefrotico':   'N04.9',  # Síndrome nefrótica NE
    'edema_hepatico':          'K74.6',  # Cirrose hepática NE
    'edema_hipotireoidismo':   'E03.9',  # Hipotireoidismo NE
    'edema_farmacologico':     'R60.0',  # Edema bilateral — causa farmacológica
    'edema_venoso_cronico':    'I87.2',  # Insuficiência venosa crônica
    'edema_linfedema':         'I89.0',  # Linfedema NE
    'edema_investigar':        'R60.9',  # Edema NE — investigar

    # ── Icterícia ─────────────────────────────────────────────────────────────
    'ictericia_emergencia':         'K83.0',  # Colangite / icterícia com emergência
    'ictericia_gilbert':            'E80.4',  # Síndrome de Gilbert
    'ictericia_hemolitica':         'D59.9',  # Anemia hemolítica NE
    'ictericia_hepatocelular':      'K75.9',  # Doença hepática inflamatória NE
    'ictericia_colestatica_obs':    'K80.5',  # Cálculo de ducto biliar / obstrução
    'ictericia_colestatica_intra':  'K83.1',  # Obstrução de ducto biliar intrahepática

    # ── Gota / Artrite por Cristais ───────────────────────────────────────────
    'gota_artrite_septica_excluir':  'M00.9',  # Artrite infecciosa NE — a excluir
    'gota_provavel_ataque_agudo':    'M10.9',  # Gota NE — ataque agudo provável
    'gota_possivel_ataque_agudo':    'M10.9',  # Gota NE — possível, investigar
    'gota_improvavel_ataque_agudo':  'M13.9',  # Artrite NE — gota improvável
    'gota_interataque':              'M10.9',  # Gota NE — período intercrítico
    'gota_tofacea':                  'M10.0',  # Gota tofácea idiopática

    # ── Anemia ────────────────────────────────────────────────────────────────
    'anemia_ferropriva':              'D50.9',  # Anemia ferropriva NE
    'talassemia_beta':                'D56.3',  # Traço de beta-talassemia
    'talassemia_alfa':                'D56.3',  # Traço de alfa-talassemia (mesmo código)
    'talassemia_beta_maior':          'D56.1',  # Beta-talassemia
    'talassemia_suspeita':            'D56.9',  # Talassemia NE
    'anemia_doenca_cronica':          'D63.8',  # Anemia em outras doenças crônicas
    'anemia_micro_indefinida':        'D64.9',  # Anemia NE
    'anemia_micro_incompleta':        'D64.9',
    'anemia_sangramento':             'D62',    # Anemia pós-hemorrágica aguda
    'anemia_hemolitica':              'D59.9',  # Anemia hemolítica adquirida NE
    'anemia_renal':                   'D63.1',  # Anemia em doença renal crônica
    'anemia_hipotireoidismo':         'D63.8',  # Anemia em doença crônica (hipotireoidismo)
    'anemia_b12':                     'D51.9',  # Anemia por deficiência de B12 NE
    'anemia_folato':                  'D52.9',  # Anemia por deficiência de folato NE
    'anemia_alcool':                  'D64.9',  # Macrocitose alcoólica
    'anemia_combinada':               'D53.1',  # Anemia megaloblástica por deficiência combinada
    'anemia_reticulocitose':          'D59.9',
    'anemia_smd':                     'D46.9',  # Síndrome mielodisplásica NE
    'anemia_normo_indefinida':        'D64.9',
    'anemia_macro_indefinida':        'D64.9',
    'pancitopenia':                   'D61.9',  # Anemia aplástica / pancitopenia NE

    # ── Fadiga ────────────────────────────────────────────────────────────────
    'fadiga_red_flags':               'R53',    # Mal-estar e fadiga — red flags (investigação urgente)
    'fadiga_me_sfc':                  'G93.3',  # Síndrome de fadiga pós-viral (ME/SFC)
    'fadiga_secundaria_apneia':       'G47.3',  # Apneia de sono
    'fadiga_secundaria_psiquiatrica': 'F48.0',  # Neurastenia / fadiga de etiologia psíquica
    'fadiga_secundaria_laboratorial': 'R53',    # Fadiga — causa laboratorial identificada
    'fadiga_idiopatica_subaguda':     'R53',    # Mal-estar e fadiga idiopática/subaguda

    # ── Gastro ────────────────────────────────────────────────────────────────
    'gastro_celiaca_suspeita':            'K90.0',  # Doença celíaca
    'gastro_colica_biliar':              'K80.2',  # Calculose da vesícula biliar sem colecistite
    'gastro_constipacao_funcional':      'K59.0',  # Constipação
    'gastro_dip':                        'N73.0',  # Salpingite e ooforite aguda (DIP)
    'gastro_diverticulite_ambulatorial': 'K57.3',  # Diverticulite do intestino grosso, sem abscesso/perfuração
    'gastro_ibd_suspeita':              'K52.9',  # Colite NE (DII suspeita — Crohn/RCUI)
    'gastro_inespecifico':              'R10.4',  # Outras dores abdominais e NE
    'gastro_intolerancia_lactose':      'E73.9',  # Intolerância à lactose NE
    'gastro_nausea_vomito':             'R11',    # Náusea e vômitos

    # ── MSK — Ombro ───────────────────────────────────────────────────────────
    'avaliacao_completa':       'M75.9',  # Lesão do ombro NE (avaliação em andamento)
    'padrao_inflamatorio':      'M06.9',  # Artrite reumatoide NE (padrão inflamatório)
    'red_flag_cardiovascular':  'I20.9',  # Angina NE (dor referida cardiovascular)
    'red_flag_emergencia':      'M75.9',  # Lesão do ombro NE — emergência

    # ── MSK — Coluna (engine legado low_back_pain) ────────────────────────────
    'red_flag':          'G83.4',  # Síndrome da cauda equina (suspeita)
    'horizontal_spinal': 'M54.4',  # Lumbago com ciática / radiculopatia
    'non_spinal':        'M54.5',  # Dor lombar — origem não vertebral
    'observe':           'M54.5',  # Dor lombar baixa — observação ativa

    # ── MSK — Mão/Punho ───────────────────────────────────────────────────────
    'avaliacao_mao_punho':    'M79.9',  # Doença dos tecidos moles NE
    'red_flag_mao_punho':     'M79.9',
    'suspeita_artrite_reumatoide': 'M06.9',  # Artrite reumatoide NE
    'trauma_escafoide_suspeito':   'S62.0',  # Fratura do escafoide da mão
    'tunel_do_carpo':              'G56.0',  # Síndrome do túnel do carpo

    # ── MSK — Quadril ─────────────────────────────────────────────────────────
    'avaliacao_quadril':  'M79.9',  # Doença dos tecidos moles NE (avaliação em andamento)
    'red_flag_quadril':   'M79.9',

    # ── MSK — Tornozelo / Pé ──────────────────────────────────────────────────
    'avaliacao_tornozelo_pe': 'M79.9',
    'red_flag_tornozelo_pe':  'M79.9',

    # ── Fibromialgia / dor crônica difusa ────────────────────────────────────
    'fibromialgia_confirmada':     'M79.7',  # Fibromialgia
    'criterios_insuficientes':     'R52.2',  # Outra dor crônica (critérios ACR não preenchidos)
    'investigar_causa_secundaria': 'R52.2',  # Dor crônica em investigação

    # ── TEP ──────────────────────────────────────────────────────────────────
    'tep_alto_risco':         'I26.0',  # Embolia pulmonar com cor pulmonale agudo
    'tep_provavel_imagem':    'I26.9',  # Embolia pulmonar sem cor pulmonale (suspeita)
    'tep_baixa_prob':         'R06.0',  # Dispneia (TEP improvável)
    'tep_descartado_perc':    'R06.0',  # Dispneia — TEP excluído clinicamente
    'tep_descartado_ddimer':  'R06.0',  # Dispneia — TEP excluído por D-dímero

    # ── Crise hipertensiva ───────────────────────────────────────────────────
    'cha_pseudocrise':              'R03.0',  # PA elevada sem diagnóstico de HAS
    'cha_assintomatica':            'I10',    # HAS essencial
    'cha_urgencia':                 'I16.0',  # Urgência hipertensiva
    'cha_emergencia_encefalopatia': 'I67.4',  # Encefalopatia hipertensiva
    'cha_emergencia_eap':           'I50.1',  # Edema agudo de pulmão
    'cha_emergencia_sca':           'I20.0',  # Angina instável/SCA
    'cha_emergencia_avc':           'I64',    # AVC não especificado
    'cha_emergencia_dissecao':      'I71.0',  # Dissecção de aorta
    'cha_eclampsia':                'O15.9',  # Eclâmpsia
    'cha_adrenergica':              'F14.0',  # Intoxicação por cocaína (crise adrenérgica)

    # ── Dispneia (roteador) ──────────────────────────────────────────────────
    'disp_pneumotorax':       'J93.0',  # Pneumotórax (hipertensivo: espontâneo de tensão)
    'disp_ic_eap':            'I50.1',  # Insuficiência VE / EAP
    'disp_pneumonia':         'J18.9',  # Pneumonia não especificada
    'disp_obstrutivo':        'J44.1',  # DPOC exacerbada (asma: ver módulo)
    'disp_suspeita_tep':      'I26.9',  # Embolia pulmonar (suspeita)
    'disp_derrame_pleural':   'J90',    # Derrame pleural
    'disp_anemia':            'D64.9',  # Anemia não especificada
    'disp_hiperventilacao':   'F45.33', # Hiperventilação / disfunção respiratória somatoforme
    'disp_indefinida':        'R06.0',  # Dispneia

    # ── Disglicemia ──────────────────────────────────────────────────────────
    'hipoglicemia':           'E16.2',  # Hipoglicemia não especificada
    'cad':                    'E10.1',  # DM com cetoacidose
    'ehh':                    'E11.0',  # DM2 com coma hiperosmolar
    'hiperglicemia_simples':  'R73.9',  # Hiperglicemia não especificada
    'glicemia_normal':        'R73.9',
    'disglicemia_sem_dado':   'R73.9',

    # ── Anafilaxia / alergia ─────────────────────────────────────────────────
    'anafilaxia':                  'T78.2',  # Choque anafilático não especificado
    'angioedema_ieca':             'T88.6',  # Reação adversa a droga (angioedema por IECA)
    'urticaria_angioedema':        'T78.3',  # Angioedema / urticária
    'reacao_alergica_indefinida':  'T78.4',  # Alergia não especificada

    # ── Dor torácica ─────────────────────────────────────────────────────────
    'dtx_stemi':                    'I21.9',  # IAM com supra (não especificado)
    'dtx_sca_alto_risco':           'I20.0',  # Angina instável / NSTEMI
    'dtx_sca_intermediario':        'I20.9',  # Angina não especificada (em estratificação)
    'dtx_baixo_risco':              'R07.4',  # Dor torácica não especificada
    'dtx_inespecifica':             'R07.4',
    'dtx_dissecao_suspeita':        'I71.0',  # Dissecção de aorta
    'dtx_pneumotorax_hipertensivo': 'J93.0',  # Pneumotórax hipertensivo
    'entorse_tornozelo':      'S93.4',  # Entorse e distensão do tornozelo
    'trauma_ottawa_positivo': 'S82.6',  # Fratura do maléolo lateral (Ottawa positivo)
    'fasciite_plantar':       'M72.2',  # Fasciite plantar
    'tendinopatia_aquiles':   'M76.6',  # Tendinite do tendão de Aquiles
    'morton_neuroma':         'G57.6',  # Lesão do nervo plantar (Neuroma de Morton)

    # ── Hemorragia Digestiva ──────────────────────────────────────────────────
    'hd_ugib_gbs_baixo':       'K92.2',
    'hd_ugib_nao_variceal':    'K92.0',
    'hd_ugib_variceal':        'I85.01',
    'hd_ugib_instavel':        'K92.0',
    'hd_lgib_instavel':        'K92.2',
    'hd_lgib_hemorroida':      'K64.9',
    'hd_lgib_fissura':         'K60.0',
    'hd_lgib_diverticular':    'K57.33',
    'hd_lgib_isquemica':       'K55.9',
    'hd_lgib_dii':             'K51.9',
    'hd_lgib_infecciosa':      'A09',
    'hd_lgib_neoplasia':       'C18.9',
    'hd_lgib_pos_polipectomia':'K92.2',
    'hd_lgib_internacao':      'K92.2',

    # ── Celulite / Erisipela ──────────────────────────────────────────────────
    'cel_leve':      'L03.90',  # Celulite NE (ajustado por localização em _analise_celulite)
    'cel_moderada':  'L03.90',
    'cel_grave':     'L03.90',
    'cel_bolhosa':   'A46',     # Erisipela
    'cel_abscesso':  'L02.91',  # Abscesso cutâneo NE
    'cel_fasciite':  'M72.6',   # Fasciite necrotizante
    'cel_sepse':     'L03.90',
    'cel_recorrente':'L03.90',
}

# Sub-mapa para IVAS emergência (depende de resultado['emergencia_tipo'])
_CID_IVAS_EMERG = {
    'abscesso_peritonsilar': 'J36',    # Abscesso peritonsilar
    'epiglotite':            'J05.1',  # Epiglotite aguda
    'ludwig':                'K12.2',  # Celulite de boca / Angina de Ludwig
}

# Sub-mapa para diarreia_aguda_watery (depende de etiologia)
_CID_DIARREIA_WATERY = {
    'viral':      'A08.4',  # Gastroenterite viral NE
    'rotavirus':  'A08.0',
    'norovirus':  'A08.1',
    'adenovirus': 'A08.2',
}


# Engines legados (vertigem/cefaleia) não têm 'categoria' — lookup por diagnóstico
_CID_VERTIGEM_LEGADO = {
    'bppv':                        'H81.1',  # VPPB
    'bppv_canal_horizontal':       'H81.1',
    'sindrome_vestibular_aguda':   'H81.2',  # Neuronite vestibular
    'provavel_meniere':            'H81.0',  # Doença de Ménière
    'possivel_migranea_vestibular':'G43.9',  # Migrânea NE (vestibular)
    'possivel_central':            'H81.4',  # Vertigem de origem central
    'presincope':                  'R55',    # Síncope e colapso
    'presincope_ortostatica':      'I95.1',  # Hipotensão ortostática
    'indefinido':                  'R42',    # Tontura e instabilidade
}

_CID_CEFALEIA_LEGADO = {
    'enxaqueca':                   'G43.9',  # Migrânea NE
    'cefaleia tensional':          'G44.2',  # Cefaleia tensional
    'cefaleia em salvas':          'G44.0',  # Cefaleia em salvas
    'cefaleia sem padrao definido':'R51',    # Cefaleia
}


def _get_cid(resultado: dict) -> str:
    """Retorna o código CID-10 correspondente ao resultado clínico."""
    cat = resultado.get('categoria', '')

    # Engines legados sem categoria — lookup por tipo + diagnóstico
    if not cat:
        diag = str(resultado.get('diagnostico', ''))
        if resultado.get('tipo') == 'vertigem':
            return _CID_VERTIGEM_LEGADO.get(diag, 'R42')
        if resultado.get('tipo') == 'cefaleia':
            if diag.startswith('cefaleia secundaria grave'):
                return 'R51'
            return _CID_CEFALEIA_LEGADO.get(diag, 'R51')

    # IVAS emergência — sub-lookup por tipo
    if cat == 'ivas_emergencia':
        sub = resultado.get('emergencia_tipo', '')
        return _CID_IVAS_EMERG.get(sub, 'J39.9')

    # Diarreia watery — refinar por etiologia se disponível
    if cat == 'diarreia_aguda_watery':
        etiol = str(resultado.get('etiologia_suspeita', '')).lower()
        for key, cid in _CID_DIARREIA_WATERY.items():
            if key in etiol:
                return cid
        return 'A08.4' if 'viral' in str(resultado.get('raciocinio', '')).lower() else 'A09'

    return _CID_MAP.get(cat, '')


def _injetar_cid(txt: str, cid: str) -> str:
    """Injeta '— CID-10: X' logo após a primeira sentença diagnóstica.

    Exemplo:
      'Gastroenterite aguda viral. Desidratação leve...'
      → 'Gastroenterite aguda viral — CID-10: A08.4. Desidratação leve...'
    """
    if not cid or not txt:
        return txt
    if 'CID-10' in txt:
        return txt   # já injetado — não duplicar
    # Injetar após o primeiro ponto que termina sentença (fim de frase),
    # ignorando pontos DENTRO de números/decimais (ex: "38.5°C") e abreviações.
    idx = -1
    for i, ch in enumerate(txt):
        if ch != '.':
            continue
        anterior = txt[i - 1] if i > 0 else ''
        proximo  = txt[i + 1] if i + 1 < len(txt) else ''
        # ponto entre dígitos → decimal, não é fim de frase
        if anterior.isdigit() and proximo.isdigit():
            continue
        # ponto seguido de espaço ou fim → fim de sentença válido
        if proximo == '' or proximo == ' ':
            idx = i
            break
    if idx >= 0:
        prefix = txt[:idx].rstrip()
        suffix = txt[idx + 1:]
        return f'{prefix} — CID-10: {cid}.{suffix}'
    # Sem ponto de fim de frase: appenda no fim
    return f'{txt} — CID-10: {cid}.'


# ------------------------------------------------------------------

def gerar_texto_prontuario(paciente, admissao):
    obj = admissao.get('objetivo', {})

    # Estado geral: "s" expandido para texto padrão
    eg = obj.get('estado_geral', '').strip()
    if eg.lower() in ('s', 'sim', 'y', '1'):
        eg = 'BEG, corado, hidratado, orientado, eupneico'

    # ── IDENTIFICAÇÃO ──────────────────────────────────────────────────────────
    sexo_str = {'m': 'masculino', 'f': 'feminino'}.get(
        paciente.get('sexo', '').lower(), paciente.get('sexo', ''))
    id_linha = f"ID: {paciente.get('nome', '')}, {paciente.get('idade', '')} anos, {sexo_str}"
    if paciente.get('profissao'):
        id_linha += f", {paciente['profissao']}"
    if paciente.get('procedencia'):
        id_linha += f", procedente de {paciente['procedencia']}"
    if paciente.get('rg_hc'):
        id_linha += f" (HC {paciente['rg_hc']})"

    linhas = [
        id_linha,
        f"Contexto social: {paciente.get('contexto_social', '')}",
        f"CHV: {paciente.get('chv', '')}",
        f"Comorbidades: {paciente.get('comorbidades', 'nega') or 'nega'}",
        f"Medicações: {paciente.get('medicacoes', 'nega') or 'nega'}",
        f"Alergias: {paciente.get('alergias', 'nega') or 'nega'}",
        f"Cx prévias: {paciente.get('cirurgias_previas', 'nega') or 'nega'}",
        f"Internamentos: {paciente.get('internamentos', 'nega') or 'nega'}",
        '',
        f"Queixa principal: {admissao.get('queixa_principal', '')}",
    ]

    # ── S: ─────────────────────────────────────────────────────────────────────
    linhas.append('\nS:')
    hma = admissao.get('hma', '').strip()
    if hma:
        linhas.append(hma)
    for _, fn_subj, _ in SINTOMAS_REGISTRADOS:
        txt = fn_subj(admissao)
        if txt:
            linhas.append(txt)

    # ── O: ─────────────────────────────────────────────────────────────────────
    linhas.append('\nO:')
    pa   = admissao.get('pa', '_') or '_'
    fc   = admissao.get('fc', '_') or '_'
    fr   = admissao.get('fr', '_') or '_'
    sat  = admissao.get('sato2', '_') or '_'
    temp = admissao.get('temperatura', '_') or '_'
    hgt  = admissao.get('glicemia', '_') or '_'
    linhas.append(
        f"Sinais vitais: PA {pa} mmHg | FC {fc} bpm | FR {fr} ipm | "
        f"SatO2 {sat}% | T {temp}°C | Glicemia {hgt} mg/dL"
    )
    if admissao.get('news2'):
        linhas.append(admissao['news2'])
    if eg:
        linhas.append(f"Estado geral: {eg}")
    for chave, label in [
        ('neuro',       'Neuro'),
        ('pneumo',      'Pneumo'),
        ('cardio',      'Cardio'),
        ('abdome',      'Abdome'),
        ('mmii',        'MMII'),
        ('pele',        'Pele/mucosas'),
        ('orofaringe',  'Orofaringe'),
        ('eliminacoes', 'Dieta/diurese/evacuação'),
    ]:
        val = obj.get(chave, '')
        if val:
            linhas.append(f"{label}: {val}")
    # Objetivos específicos dos módulos (MSK)
    for _, _, fn_obj in SINTOMAS_REGISTRADOS:
        txt = fn_obj(admissao)
        if txt:
            linhas.append(txt)

    # ── EXAMES COMPLEMENTARES ──────────────────────────────────────────────────
    exames = admissao.get('exames_complementares', '').strip()
    linhas.append(f"\nExames complementares: {exames if exames else 'não solicitados'}")

    # ── #Análise ───────────────────────────────────────────────────────────────
    linhas.append('\n#Análise:')
    analise_gerada = False
    for entrada in admissao.get('analises_automaticas', []):
        resultado = entrada.get('resultado')
        if not resultado:
            continue
        categoria = resultado.get('categoria', '')
        if categoria.startswith('ivas_'):
            dados_mod = _get_dados_modulo(admissao, 'ivas', 'organico') or {}
            txt = _gerar_texto_ivas_analise(resultado, dados_mod)
        elif resultado.get('tipo') == 'urinario':
            txt = _gerar_texto_urinario_analise(resultado)
        elif resultado.get('tipo') == 'gastro':
            txt = _analise_gastro(resultado)
        elif resultado.get('tipo') == 'orl':
            txt = _analise_odinofagia(resultado)
        elif resultado.get('tipo') == 'oftalmo':
            txt = _analise_oftalmo(resultado)
        elif resultado.get('tipo') == 'palpitacao' or categoria in _PAL_CATS:
            txt = _analise_palpitacao(resultado)
        elif resultado.get('tipo') == 'febre' or categoria in _FEBRE_CATS:
            txt = _analise_febre(resultado)
        elif resultado.get('tipo') == 'gota' or categoria in _GOTA_CATS:
            txt = _analise_gota(resultado)
        elif resultado.get('tipo') == 'asma' or categoria in _ASMA_CATS:
            txt = _analise_asma(resultado)
        elif resultado.get('tipo') == 'dpoc' or categoria in _DPOC_CATS:
            txt = _analise_dpoc(resultado)
        elif resultado.get('tipo') == 'sincope' or categoria in _SINCOPE_CATS:
            txt = _analise_sincope(resultado)
        elif resultado.get('tipo') == 'anorretal' or categoria in _ANORRETAL_CATS:
            txt = _analise_anorretal(resultado)
        elif resultado.get('tipo') == 'edema' or categoria in _EDEMA_CATS:
            txt = _analise_edema(resultado)
        elif resultado.get('tipo') == 'ictericia' or categoria in _ICTERICIA_CATS:
            txt = _analise_ictericia(resultado)
        elif resultado.get('tipo') == 'celulite' or categoria in _CELULITE_CATS:
            txt = _analise_celulite(resultado)
        elif resultado.get('tipo') == 'hemorragia' or categoria in _HEMORRAGIA_CATS:
            txt = _analise_hemorragia(resultado)
        elif resultado.get('tipo') == 'tep':
            txt = _analise_tep(resultado)
        elif resultado.get('tipo') == 'dor_toracica':
            txt = _analise_dtx(resultado)
        elif resultado.get('tipo') == 'crise_hipertensiva':
            txt = _analise_cha(resultado)
        elif resultado.get('tipo') in ('disglicemia', 'anafilaxia', 'dispneia'):
            txt = _analise_emergencia_generica(resultado)
        elif categoria in _ANEMIA_CATS:
            txt = _analise_anemia(resultado)
        elif categoria in _SONO_CATS:
            txt = _analise_sono(resultado)
        elif categoria in _CONSCIENCIA_CATS:
            txt = _analise_consciencia(resultado)
        elif categoria in _LINFA_CATS:
            txt = _analise_linfadenopatia(resultado)
        else:
            txt = gerar_analise_automatica(admissao)
        if txt:
            txt = _injetar_cid(txt, _get_cid(resultado))
            linhas.append(txt)
            analise_gerada = True
    if not analise_gerada:
        txt = gerar_analise_automatica(admissao)
        if txt:
            linhas.append(txt)
    txt_comorb = gerar_comorbidades_automaticas(admissao)
    if txt_comorb:
        linhas.append(txt_comorb)

    # ── #Plano ─────────────────────────────────────────────────────────────────
    linhas.append('\n#Plano:')
    plano_gerado = False
    for entrada in admissao.get('analises_automaticas', []):
        resultado = entrada.get('resultado')
        if not resultado:
            continue
        categoria = resultado.get('categoria', '')

        # IVAS
        if categoria.startswith('ivas_'):
            dados_mod = _get_dados_modulo(admissao, 'ivas', 'organico') or {}
            txt = _plano_ivas(resultado, dados_mod)
            if txt:
                linhas.append(txt)
                plano_gerado = True

        # Cefaleia
        elif resultado.get('tipo') == 'cefaleia':
            txt = _plano_cefaleia(resultado)
            if txt:
                linhas.append(txt)
                plano_gerado = True

        # Emergências — planos A/B (TEP, dor torácica, crise hipertensiva, disglicemia, anafilaxia, dispneia)
        elif resultado.get('tipo') in ('tep', 'dor_toracica', 'crise_hipertensiva',
                                       'disglicemia', 'anafilaxia', 'dispneia'):
            txt = _plano_tep(resultado)
            if txt:
                linhas.append(txt)
                plano_gerado = True

        # Queixa urinária (disúria / hematúria)
        elif resultado.get('tipo') == 'urinario':
            txt = _plano_urinario(resultado)
            if txt:
                linhas.append(txt)
                plano_gerado = True

        # Vertigem
        elif resultado.get('tipo') == 'vertigem':
            txt = _plano_vertigem(resultado)
            if txt:
                linhas.append(txt)
                plano_gerado = True

        # Tosse
        elif categoria.startswith('tosse_') or categoria == 'investigar_tosse_cronica':
            txt = _plano_tosse(resultado)
            if txt:
                linhas.append(txt)
                plano_gerado = True

        # Diarreia
        elif categoria.startswith('diarreia_'):
            txt = _plano_diarreia(resultado)
            if txt:
                linhas.append(txt)
                plano_gerado = True

        # Arboviroses (Dengue / Chikungunya / Zika)
        elif categoria in ('arboviral_grupo_d', 'arboviral_grupo_c', 'arboviral_grupo_b',
                           'arboviral_grupo_a', 'chikungunya_suspeita', 'zika_suspeita',
                           'arboviral_indiferenciada'):
            txt = _plano_arboviroses(resultado)
            if txt:
                linhas.append(txt)
                plano_gerado = True

        # Gastro — dor abdominal e queixas GI
        elif resultado.get('tipo') == 'gastro' or categoria in _GASTRO_CATS:
            txt = _plano_gastro(resultado)
            if txt:
                linhas.append(txt)
                plano_gerado = True

        # ORL — sintoma-guia (odinofagia, otalgia, rinossinusite…)
        elif resultado.get('tipo') == 'orl' or categoria in _ORL_CATS:
            if resultado.get('subtipo') == 'otalgia':
                txt = _plano_otalgia(resultado)
            else:
                txt = _plano_odinofagia(resultado)
            if txt:
                linhas.append(txt)
                plano_gerado = True

        # Oftalmo — olho vermelho e queixas oftalmológicas
        elif resultado.get('tipo') == 'oftalmo' or categoria in _OFT_CATS:
            txt = _plano_olho_vermelho(resultado)
            if txt:
                linhas.append(txt)
                plano_gerado = True

        # Palpitação — arritmias e taquicardias
        elif resultado.get('tipo') == 'palpitacao' or categoria in _PAL_CATS:
            txt = _plano_palpitacao(resultado)
            if txt:
                linhas.append(txt)
                plano_gerado = True

        # Febre sem foco
        elif resultado.get('tipo') == 'febre' or categoria in _FEBRE_CATS:
            txt = _plano_febre(resultado)
            if txt:
                linhas.append(txt)
                plano_gerado = True

        # Asma
        elif resultado.get('tipo') == 'asma' or categoria in _ASMA_CATS:
            txt = _plano_asma(resultado)
            if txt:
                linhas.append(txt)
                plano_gerado = True

        # DPOC
        elif resultado.get('tipo') == 'dpoc' or categoria in _DPOC_CATS:
            txt = _plano_dpoc(resultado)
            if txt:
                linhas.append(txt)
                plano_gerado = True

        # Síncope
        elif resultado.get('tipo') == 'sincope' or categoria in _SINCOPE_CATS:
            txt = _plano_sincope(resultado)
            if txt:
                linhas.append(txt)
                plano_gerado = True

        # Sangramento anorretal / prurido anal
        elif resultado.get('tipo') == 'anorretal' or categoria in _ANORRETAL_CATS:
            txt = _plano_anorretal(resultado)
            if txt:
                linhas.append(txt)
                plano_gerado = True

        # Edema de membros inferiores
        elif resultado.get('tipo') == 'edema' or categoria in _EDEMA_CATS:
            txt = _plano_edema(resultado)
            if txt:
                linhas.append(txt)
                plano_gerado = True

        # Icterícia
        elif resultado.get('tipo') == 'ictericia' or categoria in _ICTERICIA_CATS:
            txt = _plano_ictericia(resultado)
            if txt:
                linhas.append(txt)
                plano_gerado = True

        # Gota / Artrite por Cristais de Urato
        elif resultado.get('tipo') == 'gota' or categoria in _GOTA_CATS:
            txt = _plano_gota(resultado)
            if txt:
                linhas.append(txt)
                plano_gerado = True

        # Consciência / ANC
        elif categoria in _CONSCIENCIA_CATS or categoria.startswith('intoxicacao_'):
            txt = _plano_consciencia(resultado)
            if txt:
                linhas.append(txt)
                plano_gerado = True

        # Linfadenopatia
        elif categoria in _LINFA_CATS:
            txt = _plano_linfadenopatia(resultado)
            if txt:
                linhas.append(txt)
                plano_gerado = True

        # Sono — transtornos do sono
        elif categoria in _SONO_CATS:
            txt = _plano_sono(resultado)
            if txt:
                linhas.append(txt)
                plano_gerado = True

        # Anemia — interpretação de hemograma
        elif categoria in _ANEMIA_CATS:
            txt = _plano_anemia(resultado)
            if txt:
                linhas.append(txt)
                plano_gerado = True

        # Fadiga crônica / ME-SFC / causa secundária
        elif categoria in _FADIGA_CATS:
            txt = _plano_fadiga(resultado)
            if txt:
                linhas.append(txt)
                plano_gerado = True

        # Celulite / Erisipela
        elif resultado.get('tipo') == 'celulite' or categoria in _CELULITE_CATS:
            txt = _plano_celulite(resultado)
            if txt:
                linhas.append(txt)
                plano_gerado = True

        # Hemorragia Digestiva (HDA + HDB)
        elif resultado.get('tipo') == 'hemorragia' or categoria in _HEMORRAGIA_CATS:
            txt = _plano_hemorragia(resultado)
            if txt:
                linhas.append(txt)
                plano_gerado = True

        # MSK — joelho, ombro, coluna, fibromialgia, quadril, tornozelo/pé, mão/punho
        elif categoria in _MSK_CATS:
            txt = _plano_msk(resultado)
            if txt:
                linhas.append(txt)
                plano_gerado = True

        # Dispneia / Pneumonia — lê ATB de diagnosticos_provaveis/possiveis
        else:
            todos_dx = (
                resultado.get('diagnosticos_provaveis', []) +
                resultado.get('diagnosticos_possiveis', [])
            )
            for dx in todos_dx:
                if dx.get('diagnostico') == 'pneumonia' and dx.get('atb_recomendado'):
                    txt = _plano_pneumonia(dx['atb_recomendado'])
                    if txt:
                        linhas.append(txt)
                        plano_gerado = True
                    break  # só uma vez por admissão

    if not plano_gerado:
        linhas.append('[Plano a preencher]')

    # ── #Receitas ──────────────────────────────────────────────────────────────
    # Coleta prescrições estruturadas + orientações de todos os módulos da admissão.
    # Módulos que ainda não têm prescricoes_estruturadas simplesmente não geram bloco.
    receitas_blocos = []
    for entrada in admissao.get('analises_automaticas', []):
        resultado = entrada.get('resultado')
        if not resultado:
            continue
        txt = _render_receitas(resultado)
        if txt:
            receitas_blocos.append(txt)

    if receitas_blocos:
        linhas.append('\n#Receitas:')
        for bloco in receitas_blocos:
            linhas.append(bloco)

    # ── #Encaminhamento ────────────────────────────────────────────────────────
    # Carta estruturada gerada pelos módulos de emergência (Plano B) — pronta
    # para imprimir/transcrever ao escolher encaminhar.
    for entrada in admissao.get('analises_automaticas', []):
        resultado = entrada.get('resultado')
        if resultado and resultado.get('carta_encaminhamento'):
            linhas.append('\n#Encaminhamento (se Plano B — preencher horários):')
            linhas.append(resultado['carta_encaminhamento'])

    return '\n'.join(linhas)