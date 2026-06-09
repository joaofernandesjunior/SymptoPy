# modules/raciocinio/arboviroses/engine_arboviroses.py
# Motor de raciocínio clínico — Arboviroses (Dengue / Chikungunya / Zika)
# Protocolo: Ministério da Saúde — Guia Prático de Arboviroses Urbanas 2ª ed. 2025
# Classificação: Grupos A / B / C / D + Chikungunya + Zika
#
# TRAVA DE SEGURANÇA: AINE e AAS CONTRAINDICADOS em dengue (todos os grupos)
# Sequência: Grupo D → Grupo C → Chikungunya → Zika → Grupo B → Grupo A → Indiferenciada

# =============================================================================
# AUXILIARES
# =============================================================================

# Taxonomia exata MS 2025 — 8 sinais de alarme
_SINAIS_ALARME_KEYS = (
    'dor_abdominal_intensa',
    'vomitos_persistentes',
    'acumulo_liquidos',
    'hipotensao_postural',
    'hepatomegalia_referida',
    'sangramento_mucosa',
    'letargia_irritabilidade',
    'aumento_hematocrito',
)

_SINAIS_ALARME_LABEL = {
    'dor_abdominal_intensa':   'Dor abdominal intensa (referida ou a palpacao) e continua',
    'vomitos_persistentes':    'Vomitos persistentes',
    'acumulo_liquidos':        'Acumulo de liquidos (ascite, derrame pleural, derrame pericardico)',
    'hipotensao_postural':     'Hipotensao postural e/ou lipotimia',
    'hepatomegalia_referida':  'Hepatomegalia dolorosa > 2 cm abaixo do rebordo costal',
    'sangramento_mucosa':      'Sangramento de mucosa',
    'letargia_irritabilidade': 'Letargia e/ou irritabilidade',
    'aumento_hematocrito':     'Aumento progressivo do hematocrito (>= 10% em relacao a dosagem anterior)',
}

_COMORBIDADES_GRUPO_B = (
    'gestante',
    'diabetes',
    'has_cardiovascular',
    'hematologica',
    'drc',
    'doenca_hepatica',
    'obesidade_grave',
    'extremo_idade',
    'risco_social',
)

_COMORBIDADES_LABEL = {
    'gestante':           'Gestante',
    'diabetes':           'Diabetes mellitus',
    'has_cardiovascular': 'HAS / doenca cardiovascular',
    'hematologica':       'Doenca hematologica (falciforme, plaquetopenia previa)',
    'drc':                'Doenca renal cronica',
    'doenca_hepatica':    'Doenca hepatica previa (cirrose, hepatite cronica)',
    'obesidade_grave':    'Obesidade grave (IMC > 40)',
    'extremo_idade':      'Extremo de idade (< 2 anos ou > 60 anos)',
    'risco_social':       'Risco social (mora sozinho, sem acesso a UBS)',
}


def _alarmes_presentes(dados):
    return [k for k in _SINAIS_ALARME_KEYS if dados.get(k)]


def _comorbidades_presentes(dados):
    return [k for k in _COMORBIDADES_GRUPO_B if dados.get(k)]


def _calcular_hidratacao(dados):
    peso = float(dados.get('peso_kg') or 70)
    return {
        'peso_kg':         peso,
        'oral_ml_dia':     round(peso * 60),     # Grupo A — 60 mL/kg/dia
        'iv_grupo_c_ml':   round(peso * 10),     # Grupo C — 10 mL/kg/h × 1h
        'iv_grupo_d_ml':   round(peso * 20),     # Grupo D — 20 mL/kg em 20 min
    }


def _alerta_aine():
    return {
        'aine_contraindicado': True,
        'aine_msg': (
            'AINE E AAS CONTRAINDICADOS — DENGUE SUSPEITA. '
            'Ibuprofeno / Nimesulida / Diclofenaco / Piroxicam / Cetoprofeno / AAS: '
            'risco de HEMORRAGIA GRAVE, CHOQUE e Sindrome de Reye (< 18 anos). '
            '1a linha: Dipirona Monidratada 500-1000 mg VO 6/6h (max 4 g/dia). '
            'Alternativa: Paracetamol 500-750 mg VO 6/6h (MAX 3 g/dia — teto reduzido pelo risco hepatico).'
        ),
    }


# =============================================================================
# FLUXO DIAGNÓSTICO — CHECAGENS
# =============================================================================

def _e_grupo_d(dados):
    """Choque / Dengue Grave — qualquer sinal de instabilidade hemodinâmica."""
    return any([
        dados.get('hipotensao_severa'),
        dados.get('pulso_filiforme'),
        dados.get('tec_maior_3s'),
        dados.get('sudorese_fria'),
    ])


def _tem_sinal_alarme(dados):
    return bool(_alarmes_presentes(dados))


def _suspeita_chikungunya(dados):
    """
    Artralgia incapacitante + simétrica sem sinais de alarme de dengue.
    Fase crônica: artralgia > 3 meses (mesmo sem febre ativa).
    """
    artralgia_aguda = (
        dados.get('artralgia_presente') and
        dados.get('artralgia_incapacitante') and
        dados.get('artralgia_simetrica')
    )
    artralgia_cronica = dados.get('artralgia_meses', 0) >= 3

    return artralgia_aguda or artralgia_cronica


def _suspeita_zika(dados):
    """
    Exantema pruriginoso e/ou conjuntivite não purulenta.
    Febre tipicamente baixa ou ausente em Zika.
    """
    return (
        (dados.get('exantema_presente') and dados.get('exantema_pruriginoso')) or
        dados.get('conjuntivite_nao_purulenta')
    )


def _e_grupo_b(dados):
    return (
        bool(_comorbidades_presentes(dados)) or
        dados.get('prova_laco_positiva')
    )


def _tem_quadro_febril(dados):
    return dados.get('febre_presente') or dados.get('dias_febre', 0) > 0


# =============================================================================
# CONDUTAS POR GRUPO
# =============================================================================

def _conduta_grupo_d(dados, hid):
    return [
        '!! DENGUE GRAVE / CHOQUE — EMERGENCIA IMEDIATA !!',
        f'Expansao IV: SF 0,9% ou Ringer Lactato {hid["iv_grupo_d_ml"]} mL ({hid["peso_kg"]:.0f} kg x 20 mL/kg) em 20 MINUTOS',
        'Reavaliacao hemodinamica a cada 15-30 min',
        'Se sem melhora: repetir expansao ate 3 ciclos (60 mL/kg total)',
        'Acesso venoso duplo / central se necessario',
        'Monitoramento continuo: FC, PA, diurese (meta: 1-2 mL/kg/h), hematocrito',
        'Hemograma urgente: plaquetas e hematocrito',
        'Internar UTI / sala de emergencia',
        'Notificacao compulsoria imediata',
    ]


def _conduta_grupo_c(dados, hid, alarmes):
    return [
        'INTERNACAO IMEDIATA — Sinais de Alarme presentes',
        f'Hidratacao IV: SF 0,9% ou Ringer Lactato {hid["iv_grupo_c_ml"]} mL ({hid["peso_kg"]:.0f} kg x 10 mL/kg) na PRIMEIRA HORA',
        'Reavaliacao clinica e hemodinamica apos 1h',
        'Hemograma com plaquetas: URGENTE e a cada 4-6h',
        'Manter hidratacao IV ate resolucao dos alarmes e estabilidade hemodinamica',
        'Monitorar: diurese (meta 1 mL/kg/h), nivel de consciencia, PA',
        'Notificacao compulsoria dentro de 24h',
    ]


def _conduta_grupo_b(dados, hid, comorbidades):
    vol  = hid['oral_ml_dia']
    peso = hid['peso_kg']
    sro  = round(vol / 3)
    cas  = vol - sro
    linhas = [
        'OBSERVACAO NA UBS — 4-6 HORAS (Grupo B)',
        '!! INICIAR HIDRATACAO ORAL IMEDIATAMENTE — NAO aguardar hemograma sem suporte hidrico !!',
        f'Volume meta: {vol} mL/dia ({peso:.0f} kg x 60 mL/kg)',
        f'  SRO: {sro} mL durante a observacao (4-6h) — oferecer continuamente na poltrona',
        f'  Pos-alta domiciliar: {cas} mL em liquidos caseiros ate fim do dia',
        '1a linha: Dipirona Monidratada 500-1000 mg VO 6/6h se febre ou dor',
        'Alternativa: Paracetamol 500-750 mg VO 6/6h (MAX 3 g/dia)',
        '!! PROIBIDO: AINE e AAS — risco de hemorragia grave',
        'HEMOGRAMA com plaquetas: coletar na admissao — URGENTE',
        'Reavaliacao clinica ao final das 4-6h: se piora, reclassificar Grupo C/D',
        'Retorno em 24h para reavaliacao clinica e hemograma seriado',
        'Notificacao compulsoria dentro de 24h',
    ]
    if dados.get('gestante'):
        linhas += [
            'GESTANTE: encaminhar pre-natal de alto risco urgente',
            'US obstetrico se suspeita de Zika concomitante',
        ]
    if dados.get('prova_laco_positiva'):
        linhas.append('Prova do Laco positiva: monitorar plaquetas de perto — maior risco de dengue')
    return linhas


def _conduta_grupo_a(dados, hid):
    vol   = hid['oral_ml_dia']
    peso  = hid['peso_kg']
    sro   = round(vol / 3)           # 1/3 SRO nas primeiras 4-6h
    cas   = vol - sro                # 2/3 liquidos caseiros restante do dia
    return [
        'MANEJO AMBULATORIAL (Grupo A)',
        '1a linha: Dipirona Monidratada 500-1000 mg VO 6/6h se febre ou dor (max 4 g/dia)',
        'Alternativa: Paracetamol 500-750 mg VO 6/6h (MAX 3 g/dia — hepatotoxicidade na dengue)',
        '!! PROIBIDO: Ibuprofeno, Nimesulida, Diclofenaco, Piroxicam, Cetoprofeno, AAS',
        f'Hidratacao total: {vol} mL/dia ({peso:.0f} kg x 60 mL/kg)',
        f'  SRO: {sro} mL nas primeiras 4-6h (1/3 do volume total)',
        f'  Liquidos caseiros: {cas} mL distribuidos no restante do dia (agua, suco, agua de coco)',
        'Repouso relativo durante o periodo febril',
        'FASE CRITICA D3-D6: piora apos melhora inicial = retorno IMEDIATO',
        'Retorno programado em 48h para reavaliacao clinica',
        'Notificacao compulsoria dentro de 24h',
    ]


def _conduta_chikungunya(dados, hid):
    cronica = dados.get('artralgia_meses', 0) >= 3
    dias    = dados.get('dias_febre', 0)
    ns1     = dados.get('ns1_resultado', 'nao_realizado')

    # Dengue considerada excluída se: NS1 negativo confirmado, OU > D5 (NS1 perde sens.), OU fase crônica
    dengue_excluida = (ns1 == 'negativo') or (dias > 5) or cronica

    if cronica:
        return [
            'CHIKUNGUNYA — FASE CRONICA (artralgia > 3 meses)',
            'AINE 1a linha: Ibuprofeno 400-600 mg VO 8/8h com refeicao (3-5 dias)',
            'Se artralgia incapacitante persistente:',
            '  Codeina 30 mg VO 8/8h OU Tramadol 50 mg VO 8/8h (max 5 dias)',
            'Alternativa AINE: Naproxeno 500 mg VO 12/12h',
            'Fisioterapia: exercicios de mobilidade e fortalecimento — pilar do tratamento',
            'Considerar: Hidroxicloroquina 400 mg/dia se artrite cronica refrataria (> 3 meses)',
            'Encaminhar reumatologia se artrite cronica incapacitante',
            'Notificacao compulsoria se diagnostico laboratorial confirmado',
        ]

    if dengue_excluida:
        motivo = 'NS1 negativo confirmado' if ns1 == 'negativo' else f'> D5 de evolucao (D{dias})'
        return [
            f'CHIKUNGUNYA — FASE AGUDA (Dengue excluida: {motivo})',
            'AINE 1a linha: Ibuprofeno 400 mg VO 8/8h com refeicao por 3-5 dias',
            'Alternativa AINE: Naproxeno 500 mg VO 12/12h',
            'Se artralgia persistir incapacitante apos AINE:',
            '  Codeina 30 mg VO 8/8h OU Tramadol 50 mg VO 8/8h (max 5 dias)',
            'Adjuvante: Dipirona 500-1000 mg VO 6/6h ou Paracetamol 500-750 mg (max 3 g/dia)',
            f'Hidratacao oral: {hid["oral_ml_dia"]} mL/dia ({hid["peso_kg"]:.0f} kg x 60 mL/kg)',
            'Repouso e elevacao de membros edemaciados',
            'Compressa fria sobre articulacoes inflamadas',
            'Fisioterapia precoce: mobilizacao assim que tolerado',
            'Notificacao compulsoria dentro de 24h',
        ]

    # Dengue NÃO excluída — AINEs proibidos
    return [
        f'CHIKUNGUNYA — FASE AGUDA (D{dias} — Dengue ainda NAO excluida)',
        '!! AINEs E AAS TERMINANTEMENTE PROIBIDOS ate exclusao de Dengue !!',
        '1a linha: Dipirona Monidratada 500-1000 mg VO 6/6h (max 4 g/dia)',
        'Alternativa: Paracetamol 500-750 mg VO 6/6h (MAX 3 g/dia — hepatotoxicidade)',
        f'Solicitar NS1 Dengue URGENTE (se <= D5): libera AINE se negativo',
        f'Hidratacao oral: {hid["oral_ml_dia"]} mL/dia ({hid["peso_kg"]:.0f} kg x 60 mL/kg)',
        'Repouso e elevacao de membros edemaciados',
        'Compressa fria sobre articulacoes inflamadas',
        'Fisioterapia precoce: mobilizacao assim que tolerado',
        'Notificacao compulsoria dentro de 24h',
    ]


def _conduta_zika(dados, hid):
    vol  = hid['oral_ml_dia']
    peso = hid['peso_kg']
    sro  = round(vol / 3)
    cas  = vol - sro
    linhas = [
        '1a linha: Dipirona Monidratada 500-1000 mg VO 6/6h se febre ou dor (max 4 g/dia)',
        'Alternativa: Paracetamol 500-750 mg VO 6/6h (MAX 3 g/dia)',
        'AINE e AAS: PROIBIDOS ate exclusao de dengue por cocirculacao',
        f'Hidratacao total: {vol} mL/dia ({peso:.0f} kg x 60 mL/kg)',
        f'  SRO: {sro} mL nas primeiras 4-6h | Liquidos caseiros: {cas} mL restante',
        'Prurido: Loratadina 10 mg VO 1x/dia',
        'Repouso relativo',
        'Notificacao compulsoria imediata — SINAN (codigo A92.8 — Zika)',
        'Orientar prevencao sexual: preservativo por 6 meses (transmissao sexual comprovada)',
        'Rastreio Guillain-Barre: pesquisar fraqueza ou parestesia ascendente',
    ]
    if dados.get('gestante'):
        sem = dados.get('semanas_gestacao', 0)
        linhas += [
            f'!! ZIKA EM GESTANTE {sem} sem — NOTIFICACAO SINAN IMEDIATA (A92.8) !!',
            'Encaminhar pre-natal de alto risco URGENTE (mesmo dia)',
            'US morfologico fetal seriado a cada 3-4 semanas — rastreio microcefalia e anomalias SNC',
            'Acompanhamento multidisciplinar: infectologia + obstetrica + neonatologia',
            '1o trimestre: maior risco de microcefalia — vigilancia maxima',
        ]
    return linhas


def _exames_por_categoria(categoria, dados):
    dias = dados.get('dias_febre', 0)
    exames = []

    if categoria in ('arboviral_grupo_d', 'arboviral_grupo_c'):
        exames = [
            'Hemograma com plaquetas URGENTE (repetir a cada 4-6h)',
            'Hematocrito (marcador de extravasamento plasmatico)',
            'NS1 Antigeno Dengue (positivo D1-D5)',
            'Funcao renal (ureia, creatinina) e hepatica (TGO, TGP)',
            'Coagulograma se sangramento',
            'Glicemia, ionograma',
        ]
    elif categoria == 'arboviral_grupo_b':
        exames = [
            'Hemograma com plaquetas — OBRIGATORIO (1a consulta)',
            'NS1 Antigeno Dengue se <= 5 dias de doenca',
            'IgM/IgG Dengue se > 5 dias de doenca',
        ]
    elif categoria == 'arboviral_grupo_a':
        exames = [
            'NS1 Antigeno Dengue se <= 5 dias (confirmar etiologia)',
            'IgM Dengue se > 5 dias',
            'Hemograma: nao obrigatorio se < 5 dias e quadro leve',
        ]
    elif categoria == 'chikungunya_suspeita':
        exames = [
            'PCR Chikungunya (positivo ate D7 de doenca) — confirmacao',
            'IgM/IgG Chikungunya se > 7 dias',
            'NS1 Dengue para exclusao de cocirculacao',
            'Hemograma (excluir leucopenia de dengue)',
            'PCR/dosagem articular se artrite cronica (excluir AR)',
        ]
    elif categoria == 'zika_suspeita':
        exames = [
            'PCR Zika em sangue e urina (positivo ate D7)',
            'NS1 e IgM Dengue para exclusao',
            'IgM Chikungunya para exclusao',
            'Se gestante: US obstetrico + encaminhar pre-natal alto risco',
        ]
    else:
        exames = [
            'NS1 Antigeno Dengue (D1-D5)',
            'IgM Dengue (> D5)',
            'Hemograma com plaquetas',
        ]
    return exames


def _sinais_retorno():
    return [
        'Dor abdominal intensa e continua',
        'Vomitos persistentes',
        'Acumulo de liquidos (barriga inchada, falta de ar)',
        'Sangramento (gengival, nasal, urina escura, fezes escuras)',
        'Tontura ao levantar / desmaio (hipotensao postural)',
        'Sonolencia excessiva / confusao mental / irritabilidade',
        'Ausencia de urina por > 6 horas',
        '!! FASE CRITICA D3-D6: piora apos melhora inicial = URGENCIA IMEDIATA',
    ]


# =============================================================================
# FECHAMENTO DIAGNÓSTICO — CRITÉRIOS USADOS
# =============================================================================

def _ns1_linha(dados):
    """Linha resumida sobre o resultado NS1 se disponível."""
    ns1 = dados.get('ns1_resultado', 'nao_realizado')
    dias = dados.get('dias_febre', 0)
    if ns1 == 'positivo':
        return 'NS1 Dengue POSITIVO — DENGUE CONFIRMADA (sorológico)'
    if ns1 == 'negativo' and dias <= 5:
        return f'NS1 negativo (D{dias} — sensibilidade incompleta antes D5; repetir IgM apos D5)'
    if ns1 == 'negativo' and dias > 5:
        return 'NS1 negativo (> D5 — esperado; solicitar IgM Dengue)'
    if ns1 == 'indeterminado':
        return 'NS1 indeterminado — repetir em 24-48h ou solicitar ELISA'
    return None  # nao_realizado


def _criterios_grupo_d(dados):
    linhas = ['CHOQUE / DENGUE GRAVE — criterios presentes:']
    mapa = {
        'hipotensao_severa': 'PA <= 90/60 mmHg (hipotensao severa)',
        'pulso_filiforme':   'Pulso filiforme (radial impalpavel)',
        'tec_maior_3s':      'TEC > 3 segundos (perfusao comprometida)',
        'sudorese_fria':     'Sudorese fria / extremidades frias',
    }
    for k, v in mapa.items():
        if dados.get(k):
            linhas.append(f'  [+] {v}')
    ns1 = _ns1_linha(dados)
    if ns1:
        linhas.append(f'  [NS1] {ns1}')
    return linhas


def _criterios_grupo_c(alarmes):
    linhas = ['SINAIS DE ALARME presentes — INTERNACAO OBRIGATORIA:']
    for a in alarmes:
        linhas.append(f'  [+] {_SINAIS_ALARME_LABEL[a]}')
    return linhas


def _criterios_chikungunya(dados):
    linhas = ['SUSPEITA CHIKUNGUNYA:']
    if dados.get('artralgia_incapacitante'):
        linhas.append('  [+] Artralgia incapacitante (impede atividades basicas)')
    if dados.get('artralgia_simetrica'):
        linhas.append('  [+] Artralgia simetrica bilateral')
    if dados.get('edema_articular'):
        linhas.append('  [+] Edema articular visivel')
    meses = dados.get('artralgia_meses', 0)
    if meses >= 3:
        linhas.append(f'  [+] Artralgia ha {meses} meses (fase cronica confirmada)')
    ns1 = _ns1_linha(dados)
    if ns1:
        prefixo = '  [!!]' if dados.get('ns1_resultado') == 'positivo' else '  [NS1]'
        linhas.append(f'{prefixo} {ns1}')
    if dados.get('ns1_resultado') == 'positivo':
        linhas.append('  [!!] NS1 Dengue positivo — REVISAR: cocirculacao ou reclassificar como Dengue')
    return linhas


def _criterios_zika(dados):
    linhas = ['SUSPEITA ZIKA:']
    if dados.get('exantema_pruriginoso'):
        linhas.append('  [+] Exantema pruriginoso (caracteristico)')
    if dados.get('conjuntivite_nao_purulenta'):
        linhas.append('  [+] Conjuntivite nao purulenta (hiperemia bilateral)')
    if not dados.get('febre_alta'):
        linhas.append('  [+] Febre baixa ou ausente (padrao Zika — distingue de Dengue)')
    ns1 = _ns1_linha(dados)
    if ns1:
        linhas.append(f'  [NS1] {ns1}')
    if dados.get('gestante'):
        sem = dados.get('semanas_gestacao', 0)
        linhas.append(f'  [!!] Gestante {sem} semanas — risco microcefalia fetal (1o trimestre critico)')
    return linhas


def _criterios_grupo_b(dados, comorbidades):
    linhas = ['CONDICAO ESPECIAL (GRUPO B) — criterios:']
    for c in comorbidades:
        linhas.append(f'  [+] {_COMORBIDADES_LABEL[c]}')
    if dados.get('prova_laco_positiva'):
        linhas.append('  [+] Prova do Laco POSITIVA (>= 20 petequias/pol2)')
    ns1 = _ns1_linha(dados)
    if ns1:
        linhas.append(f'  [NS1] {ns1}')
    return linhas


def _criterios_grupo_a(dados):
    linhas = ['DENGUE PROVAVEL GRUPO A:']
    if dados.get('febre_presente'):
        linhas.append('  [+] Febre presente')
    if dados.get('febre_alta'):
        linhas.append('  [+] Febre alta (>= 38,5 C)')
    if dados.get('inicio_subito'):
        linhas.append('  [+] Inicio subito (horas)')
    if dados.get('dor_retroorbitaria'):
        linhas.append('  [+] Dor retroorbitaria')
    if dados.get('mialgia_intensa'):
        linhas.append('  [+] Mialgia intensa')
    if dados.get('area_endemica'):
        linhas.append('  [+] Residente / esteve em area endemica Aedes aegypti')
    if dados.get('prova_laco_positiva'):
        linhas.append('  [+] Prova do Laco positiva')
    ns1 = _ns1_linha(dados)
    if ns1:
        linhas.append(f'  [NS1] {ns1}')
    return linhas


# =============================================================================
# RECEITA DE ALTA — GRUPO A / PRESCRIÇÃO DE OBSERVAÇÃO — GRUPO B
# =============================================================================

def _receita_grupo_a(dados, hid):
    peso  = hid['peso_kg']
    vol   = hid['oral_ml_dia']
    sro   = round(vol / 3)         # 1/3 SRO nas primeiras 4-6h
    cas   = vol - sro               # 2/3 liquidos caseiros
    sro_h = round(sro / 5)         # taxa SRO em 5h (media 4-6h)
    return {
        'medicamentos': [
            '1a LINHA — Dipirona Monidratada 500 mg',
            '  Dose: 1-2 comp. (500-1000 mg) VO de 6/6h',
            '  Max: 4 g/dia (8 comp.) — enquanto febre/dor',
            '',
            'ALTERNATIVA — Paracetamol 500 mg',
            '  Dose: 1-1,5 comp. (500-750 mg) VO de 6/6h',
            '  MAX: 3 g/dia — TETO REDUZIDO (risco hepatico)',
            '',
            '!! PROIBIDO ABSOLUTAMENTE:',
            '   Ibuprofeno / Nimesulida / Diclofenaco',
            '   Piroxicam / Cetoprofeno / AAS',
            '   Risco: HEMORRAGIA GRAVE + Reye (<18 anos)',
        ],
        'hidratacao_prescrita': [
            f'VOLUME META: {vol} mL/dia ({peso:.0f} kg x 60 mL/kg)',
            f'',
            f'  1/3 = SRO: {sro} mL nas primeiras 4-6h de casa',
            f'    Taxa: {sro_h} mL/h (~1 copo a cada hora)',
            f'    Opcoes: Pedialyte, Reidral, soro caseiro',
            f'',
            f'  2/3 = Liquidos caseiros: {cas} mL no restante',
            f'    Opcoes: agua, agua de coco, sucos s/ acucar',
            f'    Evitar: refrigerante, cafe, alcool',
        ],
        'orientacoes_alta': [
            'Repouso relativo durante periodo febril',
            'Retorno programado: 48h (mesmo se estiver bem)',
            'FASE CRITICA D3-D6: piora apos melhora = URGENCIA',
            'RETORNO IMEDIATO se:',
            '  - Dor abdominal intensa / vomitos repetidos',
            '  - Sangramento (gengiva, nariz, urina escura)',
            '  - Tontura ao levantar / desmaio',
            '  - Sonolencia excessiva / confusao mental',
            'Notificacao: medico notifica caso suspeito em 24h',
        ],
    }


def _prescricao_observacao_grupo_b(dados, hid):
    """Prescrição para uso DENTRO da UBS durante as 4-6h de observação supervisionada."""
    peso  = hid['peso_kg']
    vol   = hid['oral_ml_dia']
    sro   = round(vol / 3)
    cas   = vol - sro
    sro_h = round(sro / 5)         # em ~5h de observacao
    sro_15min = round(sro_h / 4)   # oferecer a cada 15 min
    return {
        'sintomaticos': [
            '1a LINHA — Dipirona Monidratada 500-1000 mg VO 6/6h',
            'ALTERNATIVA — Paracetamol 500-750 mg VO 6/6h (max 3 g/dia)',
            '!! PROIBIDO: AINE (Ibuprofeno/Nimesulida/Diclofenaco/Cetoprofeno) e AAS',
        ],
        'hidratacao_supervisionada': [
            '!! INICIAR IMEDIATAMENTE — NAO aguardar hemograma sem hidratacao !!',
            f'Volume meta: {vol} mL/dia ({peso:.0f} kg x 60 mL/kg)',
            f'SRO durante observacao (4-6h): {sro} mL total',
            f'  Taxa: {sro_h} mL/h — oferecer {sro_15min} mL a cada 15 min na poltrona',
            f'Pos-alta domiciliar (liquidos caseiros): {cas} mL ate fim do dia',
        ],
        'laboratorio_urgente': [
            'Hemograma com plaquetas — coletar na ADMISSAO',
            'NS1 Antigeno Dengue (se D1-D5) ou IgM Dengue (se > D5)',
            'Reavaliacao clinica ao final das 4-6h',
            'Se piora hemodinamica ou alarme: reclassificar Grupo C/D — internar',
        ],
        'monitoramento_enfermagem': [
            'PA e FC: monitorar a cada hora',
            'Nivel de consciencia, mucosas e diurese: avaliar a cada hora',
            'Pesquisar sinais de alarme ativamente durante toda a observacao',
        ],
    }


# =============================================================================
# PRESCRIÇÕES ESTRUTURADAS — enriquecimento pós-categorização
# =============================================================================

def _enriquecer_arboviroses_rx(resultado, dados, hid):
    """Adiciona prescricoes_estruturadas + orientacoes conforme categoria."""
    cat  = resultado.get('categoria', '')
    vol  = hid['oral_ml_dia']
    peso = hid['peso_kg']

    # Grupos C e D: emergência / internação — sem Rx ambulatorial
    if cat in {'arboviral_grupo_d', 'arboviral_grupo_c'}:
        return

    # ── Grupo A — ambulatorial ───────────────────────────────────────────────
    if cat == 'arboviral_grupo_a':
        resultado['prescricoes_estruturadas'] = [
            {
                'linha':       '1ª linha — antipirético / analgésico',
                'medicamento': 'Dipirona Monoidratada',
                'prescricoes': [{'quantidade': '20 comprimidos', 'unidade': '500 mg',
                                 'posologia': 'Tomar 1 a 2 comprimidos (500-1000 mg) a cada 6 horas se febre ou dor. Máx 8 comprimidos (4 g) por dia.'}],
                'nota': 'PROIBIDO: Ibuprofeno, Nimesulida, Diclofenaco, Piroxicam, Cetoprofeno e AAS — risco de hemorragia grave na dengue.',
            },
            {
                'linha':       'Alternativo — antipirético (se Dipirona indisponível)',
                'medicamento': 'Paracetamol',
                'prescricoes': [{'quantidade': '20 comprimidos', 'unidade': '500 mg',
                                 'posologia': 'Tomar 1 comprimido (500 mg) a cada 6 horas. Máx 6 comprimidos (3 g)/dia — teto reduzido pelo risco hepático na dengue.'}],
                'nota': '',
            },
        ]
        resultado['orientacoes'] = {
            'hidratacao':   f'Volume meta: {vol} mL/dia ({peso:.0f} kg × 60 mL/kg). Use soro oral, água de coco ou sucos sem açúcar. Evitar refrigerante, café e álcool.',
            'fase_critica': 'ATENÇÃO: dias 3 a 6 de doença são a fase crítica — piora após melhora inicial é sinal de alarme urgente.',
            'sinais_retorno': 'Retorno obrigatório em 48h mesmo se estiver bem. Voltar imediatamente se: dor abdominal intensa, vômitos repetidos, sangramento, tontura ao levantar ou sonolência excessiva.',
        }
        return

    # ── Grupo B — observação + alta ─────────────────────────────────────────
    if cat == 'arboviral_grupo_b':
        resultado['prescricoes_estruturadas'] = [
            {
                'linha':       '1ª linha — antipirético / analgésico',
                'medicamento': 'Dipirona Monoidratada',
                'prescricoes': [{'quantidade': '20 comprimidos', 'unidade': '500 mg',
                                 'posologia': 'Tomar 1 a 2 comprimidos (500-1000 mg) a cada 6 horas se febre ou dor. Máx 4 g/dia.'}],
                'nota': 'PROIBIDO: Ibuprofeno, Nimesulida, Diclofenaco, Piroxicam, Cetoprofeno e AAS — risco de hemorragia grave.',
            },
        ]
        resultado['orientacoes'] = {
            'observacao':   'Permanência de 4 a 6 horas na UBS com hidratação oral supervisionada e hemograma na chegada.',
            'hidratacao':   f'Volume meta: {vol} mL/dia ({peso:.0f} kg × 60 mL/kg). Soro oral oferecido continuamente durante a observação.',
            'fase_critica': 'Fase crítica: dias 3 a 6. Retornar imediatamente se piora após melhora.',
        }
        return

    # ── Chikungunya ──────────────────────────────────────────────────────────
    if cat == 'chikungunya_suspeita':
        aine_proibido = resultado.get('aine_contraindicado', True)
        cronica = dados.get('artralgia_meses', 0) >= 3
        if not aine_proibido:    # dengue excluída — AINE liberado
            nota_aine = ('Fase crônica: se artralgia refratária > 3 meses, considerar Hidroxicloroquina 400 mg/dia — encaminhar reumatologia.'
                         if cronica else
                         'AINE liberado: dengue excluída (NS1 negativo ou > D5). Alternativa: Naproxeno 500 mg 12/12h.')
            resultado['prescricoes_estruturadas'] = [{
                'linha':       '1ª linha — AINE (dengue excluída)',
                'medicamento': 'Ibuprofeno',
                'prescricoes': [{'quantidade': '30 comprimidos', 'unidade': '400 mg',
                                 'posologia': 'Tomar 1 comprimido a cada 8 horas com alimento por 3 a 5 dias.'}],
                'nota': nota_aine,
            }]
            resultado['orientacoes'] = {
                'articulacoes': 'Compressa fria sobre articulações inflamadas. Elevação dos membros edemaciados.',
                'fisioterapia': 'Fisioterapia precoce com mobilização assim que tolerado — pilar do tratamento da chikungunya.',
                'sinais_retorno': 'Retornar se: febre alta, piora do quadro ou surgimento de dor abdominal intensa.',
            }
        else:    # dengue NÃO excluída — Dipirona obrigatório
            resultado['prescricoes_estruturadas'] = [{
                'linha':       '1ª linha — antipirético (AINE proibido até exclusão de dengue)',
                'medicamento': 'Dipirona Monoidratada',
                'prescricoes': [{'quantidade': '20 comprimidos', 'unidade': '500 mg',
                                 'posologia': 'Tomar 1 a 2 comprimidos (500-1000 mg) a cada 6 horas se febre ou dor. Máx 4 g/dia.'}],
                'nota': 'AINE liberado SOMENTE após NS1 Dengue negativo confirmado — solicitar se ≤ D5.',
            }]
            resultado['orientacoes'] = {
                'aguardar_ns1': 'Solicitar NS1 Dengue (se ≤ D5). AINE pode ser iniciado SE NS1 negativo confirmado.',
                'articulacoes': 'Compressa fria sobre articulações, elevação dos membros edemaciados.',
                'sinais_retorno': 'Retornar imediatamente se: dor abdominal, vômitos repetidos, sangramento ou tontura ao levantar.',
            }
        return

    # ── Zika ─────────────────────────────────────────────────────────────────
    if cat == 'zika_suspeita':
        rx = [{
            'linha':       '1ª linha — antipirético / analgésico',
            'medicamento': 'Dipirona Monoidratada',
            'prescricoes': [{'quantidade': '20 comprimidos', 'unidade': '500 mg',
                             'posologia': 'Tomar 1 a 2 comprimidos (500-1000 mg) a cada 6 horas se febre ou dor. Máx 4 g/dia.'}],
            'nota': 'PROIBIDO: AINE e AAS até exclusão de dengue (cocirculação frequente na mesma área).',
        }]
        if dados.get('exantema_pruriginoso') or dados.get('exantema_presente'):
            rx.append({
                'linha':       'Anti-histamínico (alívio do prurido)',
                'medicamento': 'Loratadina',
                'prescricoes': [{'quantidade': '10 comprimidos', 'unidade': '10 mg',
                                 'posologia': 'Tomar 1 comprimido ao dia enquanto houver prurido.'}],
                'nota': '',
            })
        resultado['prescricoes_estruturadas'] = rx
        resultado['orientacoes'] = {
            'hidratacao':        f'Volume meta: {vol} mL/dia ({peso:.0f} kg × 60 mL/kg). Água, suco natural e soro oral.',
            'prevencao_sexual':  'Usar preservativo por 6 meses após a doença — transmissão sexual comprovada.',
            'sinais_retorno':    'Retornar se: fraqueza nas pernas ou formigamento ascendente (Guillain-Barré), dor abdominal intensa ou piora do quadro.',
        }
        return

    # ── Indiferenciada — aguardar investigação ───────────────────────────────
    # Sem prescrição estruturada até definição diagnóstica


# =============================================================================
# ENTRY POINT
# =============================================================================

def interpretar_arboviroses(dados):
    hid          = _calcular_hidratacao(dados)
    alarmes      = _alarmes_presentes(dados)
    comorbidades = _comorbidades_presentes(dados)
    aine         = _alerta_aine()

    # ── 1. Grupo D — Choque / Dengue Grave ──────────────────────────────────
    if _e_grupo_d(dados):
        sinais_choque = [k for k in ('hipotensao_severa', 'pulso_filiforme', 'tec_maior_3s', 'sudorese_fria')
                         if dados.get(k)]
        resultado = {
            'categoria':          'arboviral_grupo_d',
            'grupo_dengue':       'D',
            'sinais_choque':      sinais_choque,
            'sinais_alarme':      alarmes,
            'criterios_usados':   _criterios_grupo_d(dados),
            'hidratacao':         hid,
            'conduta':            _conduta_grupo_d(dados, hid),
            'exames':             _exames_por_categoria('arboviral_grupo_d', dados),
            'internacao':         True,
            'uti':                True,
            **aine,
        }

    # ── 2. Grupo C — Sinais de Alarme ───────────────────────────────────────
    elif _tem_sinal_alarme(dados):
        resultado = {
            'categoria':          'arboviral_grupo_c',
            'grupo_dengue':       'C',
            'sinais_alarme':      alarmes,
            'comorbidades':       comorbidades,
            'criterios_usados':   _criterios_grupo_c(alarmes),
            'hidratacao':         hid,
            'conduta':            _conduta_grupo_c(dados, hid, alarmes),
            'exames':             _exames_por_categoria('arboviral_grupo_c', dados),
            'internacao':         True,
            'uti':                False,
            **aine,
        }

    # ── 3. Chikungunya ──────────────────────────────────────────────────────
    elif _suspeita_chikungunya(dados):
        cronica = dados.get('artralgia_meses', 0) >= 3
        dias    = dados.get('dias_febre', 0)
        ns1     = dados.get('ns1_resultado', 'nao_realizado')
        dengue_excluida = (ns1 == 'negativo') or (dias > 5) or cronica
        resultado = {
            'categoria':           'chikungunya_suspeita',
            'fase_cronica':        cronica,
            'artralgia_meses':     dados.get('artralgia_meses', 0),
            'edema_articular':     dados.get('edema_articular', False),
            'criterios_usados':    _criterios_chikungunya(dados),
            'hidratacao':          hid,
            'conduta':             _conduta_chikungunya(dados, hid),
            'exames':              _exames_por_categoria('chikungunya_suspeita', dados),
            'internacao':          False,
            'aine_contraindicado': not dengue_excluida,
            'aine_msg': (
                'AINE liberado: dengue excluida (NS1 negativo ou > D5)'
                if dengue_excluida else
                'AINE PROIBIDO: aguardar NS1 negativo ou > D5 para liberar'
            ),
        }

    # ── 4. Zika ──────────────────────────────────────────────────────────────
    elif _suspeita_zika(dados):
        gestante = dados.get('gestante', False)
        resultado = {
            'categoria':              'zika_suspeita',
            'alerta_gestante_zika':   gestante,
            'semanas_gestacao':       dados.get('semanas_gestacao', 0) if gestante else 0,
            'exantema_pruriginoso':   dados.get('exantema_pruriginoso', False),
            'conjuntivite':           dados.get('conjuntivite_nao_purulenta', False),
            'criterios_usados':       _criterios_zika(dados),
            'hidratacao':             hid,
            'conduta':                _conduta_zika(dados, hid),
            'exames':                 _exames_por_categoria('zika_suspeita', dados),
            'internacao':             gestante,
            **aine,
        }

    # ── 5. Grupo B — Comorbidades / Risco ───────────────────────────────────
    elif _e_grupo_b(dados):
        resultado = {
            'categoria':              'arboviral_grupo_b',
            'grupo_dengue':           'B',
            'comorbidades':           comorbidades,
            'prova_laco':             dados.get('prova_laco_positiva', False),
            'gestante':               dados.get('gestante', False),
            'criterios_usados':       _criterios_grupo_b(dados, comorbidades),
            'observacao_ubs':         '4-6 HORAS DE OBSERVACAO SUPERVISIONADA NA UBS — hidratacao oral imediata + hemograma na admissao',
            'prescricao_observacao':  _prescricao_observacao_grupo_b(dados, hid),
            'hidratacao':             hid,
            'conduta':                _conduta_grupo_b(dados, hid, comorbidades),
            'exames':                 _exames_por_categoria('arboviral_grupo_b', dados),
            'sinais_retorno':         _sinais_retorno(),
            'internacao':             False,
            **aine,
        }

    # ── 6. Grupo A — Ambulatorial ────────────────────────────────────────────
    elif _tem_quadro_febril(dados):
        resultado = {
            'categoria':          'arboviral_grupo_a',
            'grupo_dengue':       'A',
            'criterios_usados':   _criterios_grupo_a(dados),
            'hidratacao':         hid,
            'conduta':            _conduta_grupo_a(dados, hid),
            'exames':             _exames_por_categoria('arboviral_grupo_a', dados),
            'receita_alta':       _receita_grupo_a(dados, hid),
            'sinais_retorno':     _sinais_retorno(),
            'internacao':         False,
            **aine,
        }

    # ── 7. Indiferenciada ────────────────────────────────────────────────────
    else:
        resultado = {
            'categoria': 'arboviral_indiferenciada',
            'hidratacao': hid,
            'conduta': [
                'Caracterizacao insuficiente — completar anamnese e exame fisico',
                'Solicitar NS1 Dengue (D1-D5) ou IgM (> D5)',
                'Hemograma com plaquetas para rastreio',
                'Retorno se febre ou qualquer sintoma novo',
            ],
            'exames': _exames_por_categoria('arboviral_indiferenciada', dados),
            'internacao': False,
            **aine,
        }

    _enriquecer_arboviroses_rx(resultado, dados, hid)
    return resultado
