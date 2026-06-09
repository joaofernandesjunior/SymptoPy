# engine_coluna.py — Engine de raciocínio clínico: Dor Lombar
# Referência: Symptom to Diagnosis (S2D) + diretrizes ACP/ACR
# Chaves de entrada: geradas por sintomas/musculoesqueletico/coluna/subjetivo.py + objetivo.py
# API de saída: contratada pelo runner.py (ver chaves no agregador principal)

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
from modules.raciocinio.musculoesqueletico.red_flags_msk import aplicar_trava_idoso_aine

# =============================================================================
# BLOCO 0A — RED FLAGS DE EMERGÊNCIA (Síndrome da Cauda Equina)
# =============================================================================

def _avaliar_cauda_equina(dados):
    """Retorna lista de flag_dicts se qualquer sinal de CES for detectado."""
    acao = (
        'Encaminhamento IMEDIATO ao PS/Neurocirurgia. '
        'RNM lombar de emergência. Não aguardar consulta eletiva.'
    )
    flags = []
    mapa = [
        ('anestesia_em_sela',               'Anestesia em sela (dormência perineal/nádegas)'),
        ('retencao_urinaria',               'Retenção urinária aguda'),
        ('incontinencia_fecal',             'Incontinência fecal recente'),
        ('fraqueza_bilateral_mmii',         'Fraqueza bilateral progressiva de MMII'),
        ('deficit_neurologico_progressivo', 'Déficit motor progressivo recente'),
    ]
    for chave, descricao in mapa:
        if dados.get(chave):
            flags.append({'urgencia': 'emergencia', 'achado': descricao, 'acao': acao})
    return flags


# =============================================================================
# BLOCO 0B — RED FLAGS URGENTES (neoplasia, infecção, fratura)
# =============================================================================

def _avaliar_red_flags_urgentes(dados):
    """Retorna lista de flag_dicts para red flags não emergenciais."""
    flags = []

    # --- Neoplasia ---
    score_neo = 0
    achados_neo = []
    if dados.get('historico_cancer'):
        score_neo += 3; achados_neo.append('histórico pessoal de câncer')
    if dados.get('perda_de_peso_inexplicada'):
        score_neo += 2; achados_neo.append('perda de peso inexplicada')
    if dados.get('dor_noturna_sem_alivio'):
        score_neo += 2; achados_neo.append('dor noturna sem alívio postural')
    if dados.get('idade_acima_50') and dados.get('dor_nova'):
        score_neo += 1; achados_neo.append('> 50 anos com dor nova')
    if dados.get('dor_cronica') and not dados.get('melhora_com_repouso'):
        score_neo += 1; achados_neo.append('dor crônica sem resposta ao repouso')
    if score_neo >= 3:
        flags.append({
            'urgencia': 'urgente',
            'achado': f'Suspeita de neoplasia espinhal (score {score_neo}): {", ".join(achados_neo)}',
            'acao': 'RX lombar + VHS + PSA (homem ≥ 50a) + hemograma. Retorno em 1 semana com resultados.',
        })

    # --- Infecção / Espondilodiscite ---
    score_inf = 0
    achados_inf = []
    if dados.get('febre'):
        score_inf += 3; achados_inf.append('febre ou calafrios')
    if dados.get('imunossupressao'):
        score_inf += 2; achados_inf.append('imunossupressão')
    if dados.get('uso_drogas_iv'):
        score_inf += 2; achados_inf.append('uso de drogas intravenosas')
    if dados.get('bacteremia_recente'):
        score_inf += 2; achados_inf.append('bacteremia recente')
    if dados.get('uso_cronico_corticoide'):
        score_inf += 1; achados_inf.append('corticoide crônico')
    if dados.get('dor_palpacao_processos_espinhosos'):
        score_inf += 1; achados_inf.append('dor à palpação dos processos espinhosos')
    if score_inf >= 3:
        flags.append({
            'urgencia': 'urgente',
            'achado': f'Suspeita de espondilodiscite (score {score_inf}): {", ".join(achados_inf)}',
            'acao': (
                'RNM com gadolínio (padrão-ouro) + PCR + hemograma + hemocultura. '
                'Internação se febre alta ou sepse. Não iniciar ATB antes das hemoculturas.'
            ),
        })

    # --- Fratura vertebral ---
    score_fra = 0
    achados_fra = []
    if dados.get('trauma_significativo'):
        score_fra += 3; achados_fra.append('trauma significativo recente')
    if dados.get('idade_acima_70') and dados.get('dor_nova'):
        score_fra += 2; achados_fra.append('> 70 anos com dor nova')
    if dados.get('uso_cronico_corticoide'):
        score_fra += 2; achados_fra.append('corticoide crônico')
    if dados.get('osteoporose'):
        score_fra += 1; achados_fra.append('osteoporose conhecida')
    if score_fra >= 2:
        flags.append({
            'urgencia': 'urgente',
            'achado': f'Suspeita de fratura vertebral (score {score_fra}): {", ".join(achados_fra)}',
            'acao': (
                'RX lombar AP + Perfil imediato. TC se RX negativo com alta suspeita. '
                'Restrição de carga. Encaminhar ortopedia. Avaliar DXA e tratamento de osteoporose.'
            ),
        })

    return flags


# =============================================================================
# BLOCO 1 — PADRÃO CLÍNICO
# =============================================================================

def _avaliar_padrao(dados):
    """
    Classifica o padrão clínico dominante.
    Para 'inflamatorio' inclui chaves extras consumidas pelo runner.py.
    """
    # Padrão inflamatório (espondiloartropatia axial)
    score_inf = 0
    achados_inf = []
    if dados.get('rigidez_matinal_acima_60min'):
        score_inf += 3; achados_inf.append('rigidez matinal > 60 min')
    if dados.get('melhora_com_atividade_leve') and dados.get('piora_com_repouso'):
        score_inf += 3; achados_inf.append('melhora com atividade leve, piora com repouso')
    if dados.get('idade_abaixo_40') and dados.get('inicio_insidioso'):
        score_inf += 1; achados_inf.append('início insidioso em < 40 anos')

    if score_inf >= 4:
        return {
            'padrao': 'inflamatorio',
            'achados_inflamatorios': achados_inf,
            'exames_sugeridos': [
                'VHS + PCR (marcadores inflamatórios)',
                'HLA-B27 (espondilite anquilosante)',
                'RX sacroilíacas AP + pelve',
                'Encaminhar reumatologia com exames',
            ],
            'conduta_padrao': [
                'AINE regularmente (não SOS) enquanto aguarda reumatologia',
                'Exercícios de mobilidade articular: natação, alongamento diário de coluna',
                'Fisioterapia postural — movimento é terapêutico no padrão inflamatório',
                'Evitar imobilização prolongada',
            ],
        }

    # Scores para os padrões não-inflamatórios
    score_rad = sum([
        dados.get('dor_irradiada_mmii', False) * 2,
        dados.get('lasegue_positivo', False) * 2,
        dados.get('distribuicao_dermatomal', False) * 2,
        int(dados.get('queimacao_ou_choque_eletrico', False)),
    ])
    score_neu = sum([
        dados.get('claudicacao_neurogenica', False) * 3,
        dados.get('preferencia_direcional_flexao', False) * 2,
    ])
    score_mec = sum([
        dados.get('dor_mecanica', False) * 2,
        int(dados.get('melhora_com_repouso', False)),
        int(dados.get('espasmo_muscular_paravertebral', False)),
    ])

    scores = {'radicular': score_rad, 'neurogenico': score_neu, 'mecanico': score_mec}
    dominante = max(scores, key=scores.get) if any(scores.values()) else 'mecanico'
    return {'padrao': dominante}


# =============================================================================
# BLOCO 2 — MECANISMO
# =============================================================================

def _avaliar_mecanismo(dados):
    alerta_nociplastico = (
        dados.get('csi_acima_40', False) or
        (dados.get('dor_generalizada_ou_difusa', False) and dados.get('dor_cronica', False))
    )
    if dados.get('claudicacao_neurogenica'):
        mecanismo = 'estenótico/neurogênico — canal vertebral comprometido'
    elif dados.get('lasegue_positivo') or dados.get('dor_irradiada_mmii'):
        mecanismo = 'radicular/compressivo — irritação de raiz nervosa'
    elif dados.get('dor_mecanica') or dados.get('espasmo_muscular_paravertebral'):
        mecanismo = 'mecânico/miofascial — sobrecarga postural ou degenerativo'
    else:
        mecanismo = 'inespecífico — sem padrão definido'
    return {'mecanismo_dominante': mecanismo, 'alerta_nociplastico': alerta_nociplastico}


# =============================================================================
# BLOCOS 3–5 — SCORING POR HIPÓTESE
# =============================================================================

def _score_radiculopatia(dados):
    score = 0
    positivos = []
    criterios = [
        ('dor_irradiada_mmii',             3, 'dor irradiada para MMII (abaixo do joelho)'),
        ('distribuicao_dermatomal',         2, 'distribuição dermatomal clara'),
        ('queimacao_ou_choque_eletrico',    2, 'qualidade em queimação ou choque elétrico'),
        ('formigamento_ou_dormencia',       1, 'formigamento ou dormência nas pernas'),
        ('lasegue_positivo',                3, 'Lasègue positivo — SLR+ (sensib. ~80%)'),
        ('lasegue_contralateral_positivo',  3, 'Lasègue contralateral positivo (especif. >90%)'),
        ('reflexo_patelar_diminuido',       2, 'reflexo patelar diminuído — L4'),
        ('reflexo_aquileu_diminuido',       2, 'reflexo aquileu diminuído — S1'),
        ('fraqueza_dorsiflexao_pe',         2, 'fraqueza dorsiflexão do pé — L5'),
        ('fraqueza_plantiflexao_pe',        2, 'fraqueza plantiflexão do pé — S1'),
        ('deficit_sensibilidade_mmii',      2, 'déficit de sensibilidade dermatomal'),
        ('dor_movimento_flexao',            1, 'dor à flexão lombar'),
    ]
    for chave, pts, desc in criterios:
        if dados.get(chave):
            score += pts; positivos.append(desc)
    if dados.get('idade_abaixo_40'):
        score += 1; positivos.append('idade < 40 anos — pico de hérnia discal')
    if dados.get('preferencia_direcional_extensao'):
        score += 1; positivos.append('centralização com extensão — McKenzie positivo')
    forca = 'alta' if score >= 10 else ('moderada' if score >= 6 else ('baixa' if score >= 3 else None))
    return score, forca, positivos


def _score_estenose(dados):
    score = 0
    positivos = []
    criterios = [
        ('claudicacao_neurogenica',       4, 'claudicação neurogênica — piora ao caminhar, melhora ao sentar/curvar'),
        ('preferencia_direcional_flexao', 3, 'alívio com flexão do tronco — shopping cart sign'),
        ('formigamento_ou_dormencia',     2, 'formigamento ou dormência nos MMII'),
        ('dor_cronica',                   1, 'caráter crônico'),
        ('dor_movimento_extensao',        2, 'dor à extensão lombar — fecha o canal'),
        ('reflexo_aquileu_diminuido',     1, 'reflexo aquileu diminuído'),
        ('deficit_sensibilidade_mmii',    1, 'déficit de sensibilidade nos MMII'),
    ]
    for chave, pts, desc in criterios:
        if dados.get(chave):
            score += pts; positivos.append(desc)
    if dados.get('idade_acima_60'):
        score += 2; positivos.append('idade > 60 anos — estenose degenerativa')
    forca = 'alta' if score >= 9 else ('moderada' if score >= 6 else ('baixa' if score >= 3 else None))
    return score, forca, positivos


def _score_mecanica(dados):
    score = 0
    positivos = []
    criterios = [
        ('dor_mecanica',                   2, 'dor piora com movimento/carga — padrão mecânico'),
        ('melhora_com_repouso',            2, 'melhora com repouso'),
        ('inicio_insidioso',               1, 'início insidioso'),
        ('dor_localizada',                 1, 'dor localizada sem irradiação'),
        ('rigidez_matinal_menos_30min',    1, 'rigidez matinal < 30 min — padrão mecânico'),
        ('espasmo_muscular_paravertebral', 2, 'espasmo muscular paravertebral'),
        ('dor_palpacao_paravertebral',     2, 'dor à palpação paravertebral'),
        ('dor_movimento_flexao',           1, 'dor à flexão'),
        ('dor_movimento_extensao',         1, 'dor à extensão'),
    ]
    for chave, pts, desc in criterios:
        if dados.get(chave):
            score += pts; positivos.append(desc)
    if dados.get('dor_cronica') and dados.get('idade_acima_45'):
        score += 1; positivos.append('dor crônica em > 45 anos — componente degenerativo/OA')
    if not dados.get('dor_irradiada_mmii'):
        score += 1; positivos.append('ausência de irradiação para MMII')
    if not dados.get('lasegue_positivo'):
        score += 1; positivos.append('Lasègue negativo')
    if not dados.get('claudicacao_neurogenica'):
        score += 1; positivos.append('ausência de claudicação neurogênica')
    forca = 'alta' if score >= 10 else ('moderada' if score >= 6 else ('baixa' if score >= 3 else None))
    return score, forca, positivos


# =============================================================================
# CONDUTAS EMBUTIDAS
# =============================================================================

def _conduta_radiculopatia(dados, forca):
    mackenzie = dados.get('preferencia_direcional_extensao', False)
    exercicio = (
        'McKenzie — Extensão em pronação (prone press-up): '
        'deitar de barriga para baixo, empurrar o tronco para cima com os braços '
        'mantendo a pelve no chão. 10 rep × 3x/dia. '
        'PARAR se a dor irradiar mais para a perna.'
    ) if mackenzie else (
        'Repouso relativo máx. 2 dias; iniciar extensões em pronação assim que a dor tolerar.'
    )
    return {
        'conduta': [
            exercicio,
            'Caminhada leve 20 min/dia conforme tolerância — evitar sedentarismo.',
            'AINE × 5–7 dias: Ibuprofeno 400–600 mg 8/8h c/ alimento  OU  Naproxeno 500 mg 12/12h.',
            'Etoricoxibe 60–90 mg/dia (COX-2 se risco GI ou HAS controlada).',
            'Paracetamol 750–1000 mg 6/6h — adjuvante seguro em DRC e idosos.',
            'Componente neuropático → Amitriptilina 10–25 mg AO DORMIR (1ª linha: dor + sono).',
            '                       → Gabapentina 300 mg → titular até 900 mg/dia (avisar sonolência).',
            '                       → Pregabalina 75 mg → 150–300 mg/dia (início mais rápido).',
            'Relaxante muscular se espasmo: Ciclobenzaprina 5 mg AO DORMIR × 5 dias (sedante — avisar).',
            'Retorno em 4–6 semanas. Antecipa se: déficit motor progressivo ou piora da irradiação.',
        ],
        'fisioterapia': (
            'McKenzie supervisionado; tração lombar se radiculopatia confirmada; '
            'TENS para dor neuropática crônica. Fortalecimento de core após fase aguda.'
        ),
        'imagem': (
            'RNM lombar APENAS se: déficit neurológico progressivo, '
            'falha conservadora > 6 semanas ou suspeita de CES.'
        ),
        'encaminhar': (
            'Ortopedia/Neurocirurgia se: falha conservadora ≥ 6 semanas com déficit motor '
            'ou dor insuportável refratária.'
        ) if forca in ('alta', 'moderada') else None,
    }


def _conduta_estenose(forca):
    return {
        'conduta': [
            'Williams — Joelho ao peito: deitar, puxar ambos os joelhos ao peito, '
            'segurar 30s. 10 rep × 3x/dia.',
            'Williams — Inclinação pélvica: apertar a lombar contra o chão 5s. 10 rep × 3x/dia.',
            'Pedalinho no ar: simular pedalar por 1–2 min — posição fletida sem impacto axial.',
            'Bicicleta ergométrica: excelente — posição fletida, sem carga axial.',
            'Caminhada com apoio (bengala/andador) em postura levemente fletida; '
            'parar ao primeiro sinal de claudicação e sentar.',
            'Paracetamol 750–1000 mg 6/6h (base segura em idosos — menos risco GI/CV).',
            'AINE × 5 dias se sem contraindicação (cautela: DRC, HAS, > 70 anos).',
            'Gabapentina 300 mg → titular até 600–900 mg/dia '
            '(evidência moderada para claudicação neurogênica).',
            'Evitar extensão lombar prolongada e postura ereta estática.',
            'Orientar flexão ao caminhar — reduz dor de claudicação imediatamente.',
            'Retorno em 4–6 semanas. Antecipa se: claudicação piorando ou novo déficit motor.',
        ],
        'fisioterapia': (
            'Hidroterapia (excelente — posição fletida, sem impacto); '
            'fortalecimento de core em flexão; RPG. Evitar extensão lombar.'
        ),
        'imagem': (
            'RNM lombar eletiva — não urgente se sem déficit progressivo. '
            'Priorizar se claudicação intensa limitando AVD.'
        ),
        'encaminhar': (
            'Ortopedia/Neurocirurgia se: falha conservadora ≥ 3 meses com limitação funcional '
            'importante. Infiltração epidural de corticoide pode preceder a cirurgia.'
        ) if forca in ('alta', 'moderada') else None,
    }


def _conduta_mecanica(dados, forca):
    oa = dados.get('dor_cronica', False) and dados.get('idade_acima_45', False)
    conduta = [
        'Caminhada 20–30 min/dia em ritmo confortável (melhor evidência para lombalgia crônica — grau A).',
        'Bird-dog: 4 apoios, estender braço direito + perna esquerda simultaneamente, '
        'segurar 5s. Alternar. 10 rep × 2x/dia.',
        'Dead bug: deitar de costas, abaixar braço + perna opostos '
        'sem perder contato da lombar com o chão. 10 rep × 2x/dia.',
        'Alongamento de iliopsoas: ajoelhar em um joelho, avançar pé oposto, '
        'pressionar quadril para frente 30s. Cada lado × 2x/dia.',
        'Calor local: bolsa de água quente 15–20 min × 3x/dia (fase aguda com espasmo).',
        'AINE × 5–7 dias: Ibuprofeno 400–600 mg 8/8h  OU  Naproxeno 500 mg 12/12h.',
        'Paracetamol 750–1000 mg 6/6h (DRC, idosos ou adjuvante).',
    ]
    if oa:
        conduta.append(
            'Duloxetina 30 mg/dia × 1 semana → 60 mg/dia '
            '(evidência nível A para lombalgia crônica, especialmente com componente de humor).'
        )
    conduta += [
        'Relaxante muscular se espasmo intenso: Ciclobenzaprina 5–10 mg AO DORMIR × 5 dias.',
        'REPOUSO PROLONGADO PIORA — retornar às atividades normais o quanto antes (evidência A).',
        'Ergonomia: cadeira com apoio lombar, monitor na altura dos olhos; '
        'dormir em decúbito lateral com travesseiro entre os joelhos.',
        'Retorno em 4–6 semanas. Antecipa se: irradiação nova, fraqueza ou sintomas neurológicos.',
    ]
    return {
        'conduta': conduta,
        'fisioterapia': (
            'Terapia manual (Mulligan/Maitland), RPG, pilates terapêutico, '
            'TENS para dor crônica. Fortalecimento de core é o pilar a longo prazo.'
        ),
        'imagem': (
            'RX lombar AP + Perfil se: dor crônica > 4–6 semanas sem melhora '
            'ou avaliação de OA em > 50 anos. '
            'RNM não indicada de rotina para lombalgia mecânica inespecífica.'
        ),
        'encaminhar': (
            'Ortopedia: OA avançada ou instabilidade segmentar se falha conservadora > 3 meses.'
        ) if oa else (
            'Reavaliar em 4–6 semanas. Encaminhamento raramente necessário na lombalgia inespecífica.'
        ),
    }


# =============================================================================
# CONSOLIDAÇÃO DE HIPÓTESES
# =============================================================================

def _consolidar_hipoteses(dados):
    sc_rad, fo_rad, po_rad = _score_radiculopatia(dados)
    hipo_rad = None
    if fo_rad:
        hipo_rad = {
            'hipotese': 'radiculopatia_lombar',
            'forca': fo_rad, 'score': sc_rad, 'positivos': po_rad,
            **_conduta_radiculopatia(dados, fo_rad),
        }

    sc_est, fo_est, po_est = _score_estenose(dados)
    hipo_est = None
    if fo_est:
        hipo_est = {
            'hipotese': 'estenose_do_canal_vertebral',
            'forca': fo_est, 'score': sc_est, 'positivos': po_est,
            **_conduta_estenose(fo_est),
        }

    sc_mec, fo_mec, po_mec = _score_mecanica(dados)
    subtipo = (
        'lombalgia_mecanica_oa_coluna'
        if dados.get('dor_cronica') and dados.get('idade_acima_45')
        else 'lombalgia_mecanica_inespecifica'
    )
    hipo_mec = None
    if fo_mec:
        hipo_mec = {
            'hipotese': subtipo,
            'forca': fo_mec, 'score': sc_mec, 'positivos': po_mec,
            **_conduta_mecanica(dados, fo_mec),
        }

    todas = [h for h in [hipo_rad, hipo_est, hipo_mec] if h is not None]
    todas.sort(key=lambda h: h['score'], reverse=True)

    # Desambiguação: claudicação favorece estenose quando scores estão próximos
    if (hipo_rad and hipo_est and
            abs(hipo_rad['score'] - hipo_est['score']) <= 2 and
            dados.get('claudicacao_neurogenica')):
        todas.sort(
            key=lambda h: (
                h['score'] if h['hipotese'] != 'radiculopatia_lombar' else h['score'] - 3
            ),
            reverse=True,
        )

    provaveis = [h for h in todas if h['forca'] in ('alta', 'moderada')]
    possiveis = [h for h in todas if h['forca'] == 'baixa']

    exclusao = []
    if dados.get('rigidez_matinal_acima_60min') or dados.get('piora_com_repouso'):
        exclusao.append('espondiloartropatia_axial')
    if dados.get('giordano_positivo'):
        exclusao.append('pielonefrite_lombalgia_visceral')
    if dados.get('idade_acima_60') and dados.get('dor_nova') and not dados.get('trauma_significativo'):
        exclusao.append('fratura_vertebral_por_fragilidade')
    if not exclusao:
        exclusao.append('fratura_vertebral_por_fragilidade')

    return {'provaveis': provaveis, 'possiveis': possiveis, 'exclusao': exclusao}


# =============================================================================
# ALERTAS FARMACOLÓGICOS
# =============================================================================

def _alertas_farmacologicos(hipoteses_provaveis, dados):
    alertas = []
    if dados.get('imunossupressao') or dados.get('uso_cronico_corticoide'):
        alertas.append('⚠️  AINE com cautela: imunossupressão ativa — preferir Paracetamol como base.')
    if dados.get('idade_acima_60'):
        alertas.append(
            '⚠️  > 60 anos: evitar AINE > 5 dias (risco GI/CV/renal). '
            'Ciclobenzaprina aumenta risco de queda — usar com cautela.'
        )
    nomes = [h['hipotese'] for h in hipoteses_provaveis]
    if any('radiculopatia' in n for n in nomes) and dados.get('dor_cronica'):
        alertas.append(
            '💊  Lombalgia radicular crônica: Amitriptilina 10–25 mg ao dormir é '
            '1ª linha (sono + dor neuropática). AINE tem eficácia limitada a longo prazo.'
        )
    if any('oa' in n for n in nomes):
        alertas.append(
            '💊  Lombalgia crônica/OA: Duloxetina 30→60 mg/dia tem evidência nível A '
            'e é preferível ao uso prolongado de AINE.'
        )
    return '\n'.join(alertas) if alertas else None


# =============================================================================
# BLOCO LONGITUDINAL (stub — próxima iteração)
# =============================================================================

def _avaliar_evolucao(dados):
    """Rastreio de retorno mensal/trimestral na UBS. Stub — implementar na próxima iteração."""
    if not dados.get('dor_cronica'):
        return {'ativo': False}
    return {
        'ativo': True,
        'implementado': False,
        'eva_atual': dados.get('eva_dor'),
        'nota': (
            'Rastreio longitudinal pendente — próxima iteração: '
            'comparar EVA atual vs. anterior, adesão a exercícios, '
            'classificar evolução (melhora/estagnação/piora), atualizar red flags.'
        ),
    }


# =============================================================================
# AGREGADOR PRINCIPAL
# Saída compatível com runner.py — não renomear chaves de primeiro nível.
# =============================================================================

def interpretar_coluna(dados):
    """
    Ponto de entrada do engine de coluna.
    Recebe dict com chaves de subjetivo.py + objetivo.py.
    Retorna resultado estruturado consumível pelo runner.py.

    Chaves obrigatórias na saída:
      categoria, red_flags, padrao, mecanismo,
      hipoteses_provaveis, hipoteses_possiveis, hipoteses_exclusao
    """
    # Emergência absoluta: Cauda Equina
    flags_ces = _avaliar_cauda_equina(dados)
    if flags_ces:
        return {
            'categoria': 'red_flag_emergencia',
            'red_flags': {'flags': flags_ces},
            'padrao': {'padrao': 'emergencia'},
            'mecanismo': {
                'mecanismo_dominante': 'emergência cirúrgica — Síndrome da Cauda Equina',
                'alerta_nociplastico': False,
            },
            'hipoteses_provaveis': [],
            'hipoteses_possiveis': [],
            'hipoteses_exclusao': [],
            'evolucao': _avaliar_evolucao(dados),
        }

    flags_urgentes = _avaliar_red_flags_urgentes(dados)
    padrao         = _avaliar_padrao(dados)

    # Padrão inflamatório: interrompe e direciona
    if padrao['padrao'] == 'inflamatorio':
        return {
            'categoria': 'padrao_inflamatorio',
            'red_flags': {'flags': flags_urgentes},
            'padrao': padrao,
            'mecanismo': {
                'mecanismo_dominante': 'inflamatório axial — suspeita de espondiloartropatia',
                'alerta_nociplastico': False,
            },
            'hipoteses_provaveis': [{
                'hipotese': 'espondiloartropatia_axial',
                'forca': 'moderada',
                'score': 0,
                'positivos': padrao['achados_inflamatorios'],
                'conduta': padrao['conduta_padrao'],
                'fisioterapia': (
                    'Exercícios de mobilidade (natação, alongamento). '
                    'Fisioterapia postural — movimento é terapêutico.'
                ),
                'imagem': 'RX sacroilíacas AP + pelve. RNM se RX normal com alta suspeita.',
                'encaminhar': 'Reumatologia com exames (VHS, PCR, HLA-B27).',
            }],
            'hipoteses_possiveis': [],
            'hipoteses_exclusao': [
                'artrite_reumatoide',
                'doenca_de_crohn_com_manifestacao_axial',
            ],
            'evolucao': _avaliar_evolucao(dados),
        }

    # Avaliação completa
    mecanismo = _avaliar_mecanismo(dados)
    hipoteses = _consolidar_hipoteses(dados)
    alertas   = _alertas_farmacologicos(hipoteses['provaveis'], dados)

    # Trava de segurança — AINE vetado em ≥ 60 anos
    aplicar_trava_idoso_aine(hipoteses['provaveis'], dados)
    aplicar_trava_idoso_aine(hipoteses['possiveis'], dados)

    return {
        'categoria': 'avaliacao_completa',
        'red_flags': {'flags': flags_urgentes},
        'padrao': padrao,
        'mecanismo': mecanismo,
        'hipoteses_provaveis': hipoteses['provaveis'],
        'hipoteses_possiveis': hipoteses['possiveis'],
        'hipoteses_exclusao': hipoteses['exclusao'],
        'alertas_farmacologicos': alertas,
        'evolucao': _avaliar_evolucao(dados),
    }


# =============================================================================
# BLOCO DE TESTE
# Rodar da raiz: python -m modules.raciocinio.musculoesqueletico.coluna.core.engine_coluna
# =============================================================================

if __name__ == '__main__':

    _base = {
        'idade': 45, 'eva_dor': 6, 'dor_nova': False, 'dor_cronica': True,
        'idade_acima_70': False, 'idade_acima_60': False, 'idade_acima_55': False,
        'idade_acima_50': False, 'idade_acima_45': True, 'idade_acima_40': True,
        'idade_abaixo_40': False,
        'febre': False, 'perda_de_peso_inexplicada': False,
        'dor_noturna_sem_alivio': False, 'historico_cancer': False,
        'imunossupressao': False, 'uso_cronico_corticoide': False,
        'osteoporose': False, 'trauma_significativo': False,
        'anestesia_em_sela': False, 'retencao_urinaria': False,
        'incontinencia_fecal': False, 'fraqueza_bilateral_mmii': False,
        'deficit_neurologico_progressivo': False,
        'inicio_insidioso': True, 'dor_mecanica': True,
        'melhora_com_repouso': True, 'piora_com_repouso': False,
        'melhora_com_atividade_leve': False, 'dor_localizada': True,
        'rigidez_matinal_menos_30min': True, 'rigidez_matinal_acima_60min': False,
        'dor_irradiada_mmii': False, 'formigamento_ou_dormencia': False,
        'distribuicao_dermatomal': False, 'queimacao_ou_choque_eletrico': False,
        'claudicacao_neurogenica': False,
        'preferencia_direcional_extensao': False, 'preferencia_direcional_flexao': False,
        'uso_drogas_iv': False, 'bacteremia_recente': False,
        'csi_acima_40': False, 'dor_generalizada_ou_difusa': False,
        'deformidade_coluna': False, 'espasmo_muscular_paravertebral': True,
        'dor_palpacao_processos_espinhosos': False, 'dor_palpacao_paravertebral': True,
        'giordano_positivo': False,
        'dor_movimento_flexao': True, 'dor_movimento_extensao': False,
        'lasegue_positivo': False, 'lasegue_contralateral_positivo': False,
        'reflexo_patelar_diminuido': False, 'reflexo_aquileu_diminuido': False,
        'fraqueza_dorsiflexao_pe': False, 'fraqueza_plantiflexao_pe': False,
        'deficit_sensibilidade_mmii': False, 'exame_fisico_local_positivo': True,
    }

    casos = {
        'CAUDA EQUINA': {**_base, 'anestesia_em_sela': True, 'retencao_urinaria': True},
        'NEOPLASIA': {
            **_base,
            'historico_cancer': True, 'dor_noturna_sem_alivio': True,
            'perda_de_peso_inexplicada': True,
        },
        'INFECÇÃO': {**_base, 'febre': True, 'imunossupressao': True, 'bacteremia_recente': True},
        'FRATURA': {
            **_base, 'trauma_significativo': True,
            'idade_acima_70': True, 'dor_nova': True, 'dor_cronica': False,
        },
        'PADRÃO INFLAMATÓRIO': {
            **_base,
            'rigidez_matinal_acima_60min': True, 'rigidez_matinal_menos_30min': False,
            'melhora_com_atividade_leve': True, 'piora_com_repouso': True,
            'melhora_com_repouso': False, 'idade_abaixo_40': True, 'idade_acima_45': False,
        },
        'RADICULOPATIA': {
            **_base,
            'dor_irradiada_mmii': True, 'distribuicao_dermatomal': True,
            'queimacao_ou_choque_eletrico': True, 'formigamento_ou_dormencia': True,
            'lasegue_positivo': True, 'reflexo_aquileu_diminuido': True,
            'fraqueza_dorsiflexao_pe': True, 'deficit_sensibilidade_mmii': True,
            'preferencia_direcional_extensao': True,
            'dor_localizada': False, 'dor_mecanica': False,
        },
        'ESTENOSE': {
            **_base,
            'claudicacao_neurogenica': True, 'preferencia_direcional_flexao': True,
            'formigamento_ou_dormencia': True, 'dor_movimento_extensao': True,
            'reflexo_aquileu_diminuido': True, 'deficit_sensibilidade_mmii': True,
            'idade_acima_60': True, 'dor_localizada': False,
        },
        'MECÂNICA / OA': _base,
    }

    SEP = '=' * 62

    for nome, caso in casos.items():
        r = interpretar_coluna(caso)
        print(f'\n{SEP}')
        print(f'  CASO: {nome}')
        print(SEP)
        print(f'  Categoria : {r["categoria"]}')
        print(f'  Padrão    : {r["padrao"]["padrao"]}')

        if r['categoria'] == 'red_flag_emergencia':
            for f in r['red_flags']['flags']:
                print(f'  ⛔ [{f["urgencia"].upper()}] {f["achado"]}')
                print(f'     → {f["acao"]}')
            continue

        if r['red_flags']['flags']:
            print('  ⚠️  Red flags urgentes:')
            for f in r['red_flags']['flags']:
                print(f'    [{f["urgencia"].upper()}] {f["achado"][:70]}')

        print(f'  Mecanismo : {r["mecanismo"]["mecanismo_dominante"]}')
        if r['mecanismo']['alerta_nociplastico']:
            print('  ⚠️  Alerta nociplástico ativo')

        if r['hipoteses_provaveis']:
            print('\n  Hipóteses prováveis:')
            for h in r['hipoteses_provaveis']:
                label = h['hipotese'].replace('_', ' ').upper()
                print(f'    [{h["score"]:>2}pts / {h["forca"]}]  {label}')
                print(f'    Achados: {", ".join(h["positivos"][:3])}{"..." if len(h["positivos"]) > 3 else ""}')
                if h['conduta']:
                    print(f'    Conduta: {h["conduta"][0][:85]}')

        if r['hipoteses_possiveis']:
            print('\n  Também considerar:')
            for h in r['hipoteses_possiveis']:
                print(f'    [{h["score"]:>2}pts / {h["forca"]}]  {h["hipotese"].replace("_", " ")}')

        if r['hipoteses_exclusao']:
            print(f'  Excluir ativamente: {", ".join(r["hipoteses_exclusao"])}')

        if r.get('alertas_farmacologicos'):
            print(f'\n  Alertas:\n  {r["alertas_farmacologicos"]}')
