# modules/raciocinio/celulite/engine_celulite.py
# Motor de raciocínio clínico — Celulite e Erisipela — Adulto
#
# Hierarquia STEP:
#   STEP 1  Fasciite necrotizante (red flags ou LRINEC ≥6) → PS cirurgião
#   STEP 1  Instabilidade hemodinâmica → PS
#   STEP 2  ≥2 SIRS → internação + ATB IV
#   STEP 3  Bolhas hemorrágicas / necróticas → internação preferencial
#   STEP 4  Abscesso → drenagem obrigatória
#   STEP 5  1 SIRS → ATB oral + retorno 48h
#   STEP 6  0 SIRS → ATB oral + alta
#   STEP 7  Recorrente (≥3/ano) → profilaxia
#
# Fonte: IDSA 2014 — Stevens et al., Clin Infect Dis 59(2):147-59


# =============================================================================
# HELPERS
# =============================================================================

def _rx(linha, medicamento, prescricoes, nota=None):
    return {'linha': linha, 'medicamento': medicamento,
            'prescricoes': prescricoes, 'nota': nota}


def _p(quantidade, unidade, posologia):
    return {'quantidade': quantidade, 'unidade': unidade, 'posologia': posologia}


def _sirs_count(d) -> int:
    n = 0
    if d.get('febre') or d.get('hipotermia'):
        n += 1
    if d.get('taquicardia'):
        n += 1
    if d.get('taquipneia'):
        n += 1
    # leucocitose/leucopenia só se labs disponíveis
    leu = d.get('leucocitos')
    if leu is not None and (leu > 12000 or leu < 4000):
        n += 1
    return n


def _lrinec(d) -> int:
    score = 0
    pcr = d.get('pcr')
    if pcr is not None:
        if pcr > 150:
            score += 2
    leu = d.get('leucocitos')
    if leu is not None:
        if leu > 25000:
            score += 2
        elif leu >= 15000:
            score += 1
    hb = d.get('hb')
    if hb is not None:
        if hb < 11:
            score += 2
        elif hb <= 13.5:
            score += 1
    na = d.get('sodio')
    if na is not None and na < 135:
        score += 2
    cr = d.get('creatinina')
    if cr is not None and cr > 1.6:
        score += 2
    gli = d.get('glicemia')
    if gli is not None and gli > 180:
        score += 1
    return score


def _mrsa_risk(d) -> bool:
    return bool(
        d.get('mrsa_colonizacao') or
        d.get('uso_drogas_iv') or
        d.get('trauma_penetrante') or
        d.get('drenagem_purulenta') or
        d.get('mrsa_internacao_recente') or
        d.get('falha_beta_lactamico')
    )


def _imunocomp(d) -> bool:
    return bool(
        d.get('imunossupressao') or
        d.get('neutropenia') or
        d.get('malignidade')
    )


def _atb_oral(d) -> list:
    """Prescrição oral por perfil de alergia e risco de MRSA."""
    alergia = d.get('alergia_penicilina', 'nenhuma')
    mrsa = _mrsa_risk(d)
    purulenta = d.get('drenagem_purulenta') or d.get('flutuacao')
    loc = d.get('localizacao', '')

    rx = []

    if mrsa or purulenta:
        # Cobertura de MRSA necessária
        if alergia == 'anafilatica':
            rx.append(_rx('1ª linha (MRSA + anafilaxia betalact.)',
                          'Clindamicina',
                          [_p('300–450 mg', 'VO', '8/8h × 5–7 dias')]))
            rx.append(_rx('Alternativo',
                          'Doxiciclina',
                          [_p('100 mg', 'VO', '12/12h × 5–7 dias')]))
        else:
            rx.append(_rx('1ª linha (MRSA)',
                          'SMX-TMP',
                          [_p('800/160 mg', 'VO', '12/12h × 5–7 dias')]))
            rx.append(_rx('Alternativo (MRSA)',
                          'Clindamicina',
                          [_p('300–450 mg', 'VO', '8/8h × 5–7 dias')]))
        return rx

    # Sem MRSA — streptocócico / MSSA
    if alergia == 'anafilatica':
        rx.append(_rx('1ª linha (alergia anafilática betalact.)',
                      'Clindamicina',
                      [_p('300–450 mg', 'VO', '8/8h × 5 dias')]))
    elif alergia == 'nao_anafilatica':
        rx.append(_rx('1ª linha (alergia não anafilática)',
                      'Clindamicina',
                      [_p('300–450 mg', 'VO', '8/8h × 5 dias')]))
    else:
        # Sem alergia
        borda_nitida = d.get('borda_nitida')
        if borda_nitida:
            # Erisipela — estreptocócica predominante
            rx.append(_rx('1ª linha (erisipela)',
                          'Amoxicilina',
                          [_p('500 mg', 'VO', '8/8h × 5–7 dias')]))
            rx.append(_rx('Alternativo (erisipela)',
                          'Penicilina Benzatina',
                          [_p('1.200.000 UI', 'IM', 'dose única (se adesão incerta)')],
                          nota='Reservar para casos com adesão duvidosa'))
        else:
            rx.append(_rx('1ª linha (celulite)',
                          'Cefalexina',
                          [_p('500 mg', 'VO', '6/6h × 5 dias')]))
            rx.append(_rx('Alternativo',
                          'Amoxicilina',
                          [_p('500 mg', 'VO', '8/8h × 5 dias')]))
    return rx


def _atb_iv(d) -> list:
    """Prescrição IV para internação."""
    mrsa = _mrsa_risk(d)
    imunocomp = _imunocomp(d)

    rx = []

    if imunocomp or (mrsa and imunocomp):
        rx.append(_rx('1ª linha (imunossuprimido grave)',
                      'Vancomicina + Piperacilina-tazobactam',
                      [_p('15–20 mg/kg', 'IV', 'q8–12h (Vanco) + 4,5g q6h (PipTazo)')]))
    elif mrsa:
        rx.append(_rx('1ª linha (risco MRSA)',
                      'Vancomicina',
                      [_p('15–20 mg/kg', 'IV', 'q8–12h')],
                      nota='Alvo trough 15–20 mcg/mL'))
        rx.append(_rx('Alternativo (se vanco contraindicada)',
                      'Linezolida',
                      [_p('600 mg', 'IV/VO', 'q12h')]))
    else:
        rx.append(_rx('1ª linha (sem MRSA)',
                      'Cefazolina',
                      [_p('1–2 g', 'IV', 'q8h')]))
        rx.append(_rx('Alternativo',
                      'Ceftriaxona',
                      [_p('1–2 g', 'IV', 'dose diária')]))
    return rx


# =============================================================================
# ENGINE PRINCIPAL
# =============================================================================

def _analisar_celulite_core(dados: dict) -> dict:
    d = dados
    sirs = _sirs_count(d)
    lrinec = _lrinec(d)
    mrsa = _mrsa_risk(d)
    imunocomp = _imunocomp(d)
    loc = d.get('localizacao', 'mmii_unilateral')
    recorrente = (d.get('episodios_anteriores') or 0) >= 3

    # ── STEP 1: Fasciite necrotizante ─────────────────────────────────────────
    fasciite_clinica = (
        d.get('crepitacao') or
        d.get('necrose') or
        d.get('dor_desproporcional') or
        d.get('progressao_rapida') or
        d.get('bolhas_hemorragicas')
    )
    if fasciite_clinica or lrinec >= 6:
        achados = []
        if d.get('crepitacao'):         achados.append('crepitação')
        if d.get('necrose'):            achados.append('necrose/pele violácea')
        if d.get('dor_desproporcional'): achados.append('dor desproporcional')
        if d.get('bolhas_hemorragicas'): achados.append('bolhas hemorrágicas')
        if d.get('progressao_rapida'):  achados.append('progressão rápida')
        if lrinec >= 6:                 achados.append(f'LRINEC {lrinec}')
        return {
            'tipo': 'celulite',
            'categoria': 'cel_fasciite',
            'urgencia': 'emergencia',
            'diagnostico': 'Fasciite Necrotizante — EMERGÊNCIA CIRÚRGICA',
            'hipotese_principal': 'fasciite_necrotizante',
            'achados': achados,
            'lrinec': lrinec,
            'conduta': (
                'Acionar cirurgia geral IMEDIATAMENTE. '
                'Não aguardar exames de imagem se suspeita clínica alta. '
                'TC/RM apenas se não atrasar exploração cirúrgica (S 88,5% / E 93,3%). '
                'ATB empírico imediato: Vancomicina + Piperacilina-tazobactam IV. '
                'Culturas intraoperatórias.'
            ),
            'prescricoes_estruturadas': [
                _rx('Empírico (fasciite)',
                    'Vancomicina + Piperacilina-tazobactam',
                    [_p('15–20 mg/kg + 4,5g', 'IV', 'q8–12h + q6h')],
                    nota='Iniciar antes da cirurgia — não atrasar intervenção'),
            ],
            'exames': 'CBC, BMP, CRP, lactato, hemoculturas ×2. TC/RM se dúvida e sem atraso cirúrgico.',
            'encaminhamento': 'PS cirurgia geral — emergência imediata',
            'raciocinio': (
                f'Red flags de fasciite presentes: {", ".join(achados) if achados else "LRINEC ≥6"}. '
                '⚠️ LRINEC tem sensibilidade BAIXA (43–68% no cutoff ≥6) — '
                '57% dos casos de fasciite têm LRINEC <6 em estudos prospectivos. '
                'Score NUNCA pode descartar fasciite. Exploração cirúrgica guiada pela clínica, '
                'independente do score. Exame seriado a cada 4–6h se dúvida.'
            ),
        }

    # ── STEP 1b: Instabilidade hemodinâmica ──────────────────────────────────
    if d.get('hipotensao'):
        return {
            'tipo': 'celulite',
            'categoria': 'cel_sepse',
            'urgencia': 'emergencia',
            'diagnostico': 'Celulite com Sepse — PS imediato',
            'hipotese_principal': 'celulite_sepse',
            'achados': ['hipotensão', f'{sirs} critérios SIRS'],
            'lrinec': lrinec,
            'conduta': 'PS imediato. Bundle sepse: hemoculturas × 2, lactato, ATB IV em < 1h.',
            'prescricoes_estruturadas': _atb_iv(d),
            'exames': 'CBC, BMP, CRP, lactato, hemoculturas ×2',
            'encaminhamento': 'PS — sepse/emergência',
            'raciocinio': 'Instabilidade hemodinâmica = sepse até prova em contrário.',
        }

    # ── STEP 2: ≥2 SIRS → internação ─────────────────────────────────────────
    if sirs >= 2 or imunocomp:
        motivo_internacao = []
        if sirs >= 2:   motivo_internacao.append(f'{sirs} critérios SIRS')
        if imunocomp:   motivo_internacao.append('imunossupressão grave')
        return {
            'tipo': 'celulite',
            'categoria': 'cel_grave',
            'urgencia': 'internacao',
            'diagnostico': 'Celulite Grave — Internação + ATB IV',
            'hipotese_principal': 'celulite_grave',
            'achados': motivo_internacao,
            'sirs': sirs,
            'lrinec': lrinec,
            'conduta': (
                'Internação indicada. ATB IV. '
                'Marcar borda do eritema com caneta permanente + hora. '
                'Reavaliação em 24–48h com conferência da marcação. '
                'Elevação do membro afetado.'
            ),
            'prescricoes_estruturadas': _atb_iv(d),
            'exames': 'CBC, BMP, CRP, lactato. Hemoculturas ×2. US partes moles se abscesso suspeito.',
            'encaminhamento': 'Internação clínica / PS',
            'raciocinio': f'Critérios de internação: {", ".join(motivo_internacao)}.',
        }

    # ── STEP 3: Bolhas tensas (sem red flags fasciite) ────────────────────────
    if d.get('bolhas') and not d.get('bolhas_hemorragicas'):
        return {
            'tipo': 'celulite',
            'categoria': 'cel_bolhosa',
            'urgencia': 'internacao',
            'diagnostico': 'Erisipela/Celulite Bolhosa — Internação preferencial',
            'hipotese_principal': 'erisipela_bolhosa',
            'achados': ['bolhas tensas'],
            'sirs': sirs,
            'lrinec': lrinec,
            'conduta': (
                'Internação preferencial — barreira cutânea comprometida. '
                'ATB IV. Cuidados com as bolhas (não romper). '
                'Marcar borda + hora.'
            ),
            'prescricoes_estruturadas': _atb_iv(d),
            'exames': 'CBC, BMP, CRP. Hemoculturas se febre.',
            'encaminhamento': 'Internação',
            'raciocinio': 'Bolhas tensas indicam comprometimento profundo da barreira cutânea.',
        }

    # ── STEP 4: Abscesso → drenagem ──────────────────────────────────────────
    if d.get('flutuacao'):
        celulite_perilesional = d.get('progressao_rapida') or sirs >= 1
        atb = []
        if celulite_perilesional or mrsa:
            atb = _atb_oral(d)
            nota_atb = 'ATB indicado por celulite perilesional/risco MRSA.'
        else:
            nota_atb = 'ATB não indicado em abscesso simples sem celulite perilesional (IDSA 2014).'
        return {
            'tipo': 'celulite',
            'categoria': 'cel_abscesso',
            'urgencia': 'urgente',
            'diagnostico': 'Abscesso com Celulite',
            'hipotese_principal': 'celulite_com_abscesso',
            'achados': ['flutuação/abscesso'],
            'sirs': sirs,
            'lrinec': lrinec,
            'conduta': (
                f'Drenagem cirúrgica OBRIGATÓRIA (procedimento primário). '
                f'{nota_atb} '
                'Marcar borda do eritema. Retorno em 24–48h.'
            ),
            'prescricoes_estruturadas': atb,
            'exames': 'Cultura do pus drenado se MRSA suspeito.',
            'encaminhamento': 'Ambulatório com drenagem / PS se não disponível',
            'raciocinio': 'Drenagem é suficiente em abscesso simples. ATB adicionado apenas se celulite perilesional significativa.',
        }

    # ── STEP 5: 1 SIRS → moderado, oral + retorno 48h ────────────────────────
    if sirs == 1:
        return {
            'tipo': 'celulite',
            'categoria': 'cel_moderada',
            'urgencia': 'ambulatorio_urgente',
            'diagnostico': _diag_label(d),
            'hipotese_principal': _hipotese(d),
            'achados': [f'1 critério SIRS'],
            'sirs': sirs,
            'lrinec': lrinec,
            'conduta': (
                'ATB oral. Marcar borda do eritema + data/hora. '
                'Retorno obrigatório em 24–48h para conferir progressão. '
                'Se progressão além da marcação → internação. '
                'Elevação do membro. Tratar porta de entrada (tinea pedis se presente).'
            ),
            'prescricoes_estruturadas': _atb_oral(d),
            'exames': 'CBC, BMP se internação considerada.',
            'encaminhamento': None,
            'raciocinio': '1 critério SIRS — oral preferencial; IV se não tolerar. Retorno mandatório 48h.',
        }

    # ── STEP 6: 0 SIRS → leve, oral + alta ───────────────────────────────────
    resultado_base = {
        'tipo': 'celulite',
        'categoria': 'cel_leve',
        'urgencia': 'ambulatorio',
        'diagnostico': _diag_label(d),
        'hipotese_principal': _hipotese(d),
        'achados': ['0 critérios SIRS'],
        'sirs': 0,
        'lrinec': lrinec,
        'conduta': (
            'ATB oral × 5 dias. Marcar borda do eritema + data/hora. '
            'Retorno se progressão além da marcação em 24–48h, piora sistêmica ou sem melhora em 48h. '
            'Elevação do membro. Tratar porta de entrada.'
        ),
        'prescricoes_estruturadas': _atb_oral(d),
        'exames': 'Nenhum exame rotineiro necessário (IDSA 2014).',
        'encaminhamento': None,
        'raciocinio': '0 critérios SIRS — manejo ambulatorial. Exames não rotineiros em celulite típica.',
    }

    # ── STEP 7: Recorrente → adicionar profilaxia ─────────────────────────────
    if recorrente:
        resultado_base['categoria'] = 'cel_recorrente'
        resultado_base['urgencia'] = 'ambulatorio'
        resultado_base['conduta'] += (
            ' CELULITE RECORRENTE (≥3 episódios/ano): tratar fatores predisponentes '
            '(tinea pedis, linfedema, insuficiência venosa, obesidade) ANTES de iniciar profilaxia.'
        )
        profilaxia = []
        alergia = d.get('alergia_penicilina', 'nenhuma')
        if alergia == 'anafilatica':
            profilaxia.append(_rx('Profilaxia (alergia anafilática)',
                                  'Eritromicina',
                                  [_p('250 mg', 'VO', '2×/dia × 6–12 meses')]))
        else:
            profilaxia.append(_rx('Profilaxia 1ª linha',
                                  'Penicilina VK',
                                  [_p('250–500 mg', 'VO', '1×/dia × 6–12 meses')],
                                  nota='Reavaliar após 6 meses. Recidiva após suspensão é comum.'))
        resultado_base['prescricoes_estruturadas'] = resultado_base['prescricoes_estruturadas'] + profilaxia
        resultado_base['raciocinio'] += (
            f' {d["episodios_anteriores"]} episódios/ano — profilaxia indicada após controle de fatores predisponentes.'
        )

    return resultado_base


# =============================================================================
# HELPERS DE LABEL
# =============================================================================

def _diag_label(d) -> str:
    if d.get('borda_nitida') and not d.get('flutuacao'):
        loc = _loc_label(d)
        return f'Erisipela — {loc}'
    loc = _loc_label(d)
    return f'Celulite não-complicada — {loc}'


def _hipotese(d) -> str:
    if d.get('borda_nitida') and not d.get('flutuacao'):
        return 'erisipela'
    if d.get('flutuacao'):
        return 'celulite_com_abscesso'
    return 'celulite_nao_complicada'


def _loc_label(d) -> str:
    _MAP = {
        'mmii_unilateral': 'MMII unilateral',
        'mmii_bilateral':  'MMII bilateral',
        'face':            'face',
        'mao_braco':       'mão/braço',
        'tronco':          'tronco',
        'pe':              'pé',
        'outro':           'outro sítio',
    }
    return _MAP.get(d.get('localizacao', ''), 'localização')


# =============================================================================
# PENTE FINO — alertas de segurança transversais
# =============================================================================

def _enriquecer_celulite(resultado: dict, dados: dict) -> dict:
    """Adiciona alertas_seguranca ao resultado (renderizados no topo do #Plano)."""
    alertas = []
    cat    = resultado.get('categoria', '')
    lrinec = resultado.get('lrinec', 0) or 0

    # Uso de drogas IV: bacteremia/endocardite por S. aureus
    if dados.get('uso_drogas_iv'):
        alertas.append(
            '⚠️ Uso de drogas IV → risco de bacteremia + endocardite por S. aureus: '
            'hemoculturas seriadas; ecocardiograma se febre persistente > 72h ou bacteremia confirmada'
        )

    # Pé diabético / diabetes: cobertura gram-negativo + Pseudomonas
    if dados.get('pe_diabetico') or (dados.get('diabetes') and
            dados.get('localizacao') in ('pe', 'mmii_unilateral')):
        alertas.append(
            '⚠️ Pé diabético: cobertura gram-negativa ampliada — '
            'amoxicilina-clavulanato (leve) ou ciprofloxacino + clindamicina (grave); '
            'avaliar isquemia e neuropatia'
        )

    # LRINEC < 6 com sinais clínicos de fasciite — baixa sensibilidade do score
    sinais_fasciite = any(dados.get(k) for k in
                          ('crepitacao', 'necrose', 'dor_desproporcional', 'bolhas_hemorragicas'))
    if sinais_fasciite and cat != 'cel_fasciite' and lrinec < 6:
        alertas.append(
            '⚠️ Sinais clínicos de fasciite com LRINEC < 6: score tem sensibilidade de 43–68% — '
            'NÃO exclui fasciite; reavaliação seriada a cada 4–6h; cirurgia guiada pela clínica'
        )

    # Mordedura / imersão: patógenos especiais
    if dados.get('mordedura_animal'):
        alertas.append(
            '⚠️ Mordedura / imersão em água: cobertura para Pasteurella (animal), '
            'Aeromonas / Vibrio (água doce/salgada) → amoxicilina-clavulanato oral; '
            'notificar raiva se mordedura de cão/gato/morcego'
        )

    resultado['alertas_seguranca'] = alertas
    return resultado


def analisar_celulite(dados: dict) -> dict:
    """Ponto de entrada público — core + pente fino."""
    return _enriquecer_celulite(_analisar_celulite_core(dados), dados)
