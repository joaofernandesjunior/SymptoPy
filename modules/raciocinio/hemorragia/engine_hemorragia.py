# modules/raciocinio/hemorragia/engine_hemorragia.py
# Motor de raciocínio clínico — Hemorragia Digestiva (HDA + HDB) — Adulto
#
# Hierarquia STEP:
#   STEP 1  Instabilidade hemodinâmica → SAMU/PS emergência
#   STEP 2  UGIB: GBS 0–1 → alta; GBS ≥2 → internação; variceal vs não-variceal
#   STEP 3  LGIB: Oakland ≤8 → alta; >8 → internação; instável → angioTC
#   STEP 4  Etiologia LGIB: hemorroida / fissura / diverticular / angiodisplasia /
#           isquêmica / DII / infecciosa / neoplasia / pós-polipectomia
#
# Fontes: ACG 2023, BSG 2021 (UGIB), AGA/BSG 2023 (LGIB), ESGE


# =============================================================================
# HELPERS
# =============================================================================

def _rx(linha, medicamento, prescricoes, nota=None):
    return {'linha': linha, 'medicamento': medicamento,
            'prescricoes': prescricoes, 'nota': nota}


def _p(quantidade, unidade, posologia):
    return {'quantidade': quantidade, 'unidade': unidade, 'posologia': posologia}


def _shock_index(d) -> float:
    pas = d.get('pas') or 120
    fc  = d.get('fc')  or 70
    if pas == 0:
        return 99.0
    return fc / pas


# =============================================================================
# GLASGOW-BLATCHFORD SCORE
# =============================================================================

def _gbs(d) -> int:
    score = 0
    bun = d.get('bun') or 0
    if bun >= 70:           score += 6
    elif bun >= 28:         score += 4
    elif bun >= 22.4:       score += 3
    elif bun >= 18.2:       score += 2

    hb   = d.get('hb') or 15
    sexo = d.get('sexo', 'masculino')
    if sexo == 'masculino':
        if hb < 10:         score += 6
        elif hb < 12:       score += 3
        elif hb < 13:       score += 1
    else:
        if hb < 10:         score += 6
        elif hb < 12:       score += 1

    pas = d.get('pas') or 120
    if pas < 90:            score += 3
    elif pas < 100:         score += 2
    elif pas < 110:         score += 1

    fc = d.get('fc') or 70
    if fc >= 100:           score += 1

    if d.get('melena'):     score += 1
    if d.get('sincope'):    score += 2
    if d.get('hepatopatia_gbs'): score += 2
    if d.get('icc'):        score += 2

    return score


# =============================================================================
# OAKLAND SCORE
# =============================================================================

def _oakland(d) -> int:
    score = 0
    idade = d.get('idade') or 0
    if idade >= 70:         score += 5
    elif idade >= 40:       score += 3

    if (d.get('sexo') or 'feminino') == 'masculino':
        score += 1

    if d.get('lgib_previo'):   score += 4
    if d.get('dre_sangue'):    score += 1

    fc = d.get('fc') or 70
    if fc >= 120:           score += 3
    elif fc >= 90:          score += 1

    pas = d.get('pas') or 120
    if pas < 90:            score += 5
    elif pas < 120:         score += 2

    hb = d.get('hb') or 13
    if hb < 9:              score += 7
    elif hb < 12:           score += 4

    return score


# =============================================================================
# TRANSFUSÃO
# =============================================================================

def _transfusion_needed(d) -> bool:
    hb  = d.get('hb') or 15
    dcv = d.get('dcv') or d.get('cirrose')
    si  = _shock_index(d)
    if si > 1:
        return True          # instável → transfundir independente
    if hb < 7:
        return True
    if hb < 8 and dcv:
        return True
    return False


def _transfusion_rx(d) -> list:
    hb  = d.get('hb') or 15
    dcv = d.get('dcv') or d.get('cirrose')
    alvo = 8 if dcv else 7
    return [_rx('Hemotransfusão',
                'Concentrado de hemácias',
                [_p('1 CH por vez', 'IV', f'até Hb ≥ {alvo} g/dL')],
                nota=f'Meta Hb ≥ {alvo} g/dL. Estratégia restritiva (ACG 2023).')]


# =============================================================================
# REVERSÃO DE ANTICOAGULANTE
# =============================================================================

def _reversao_rx(d) -> list:
    atc = d.get('anticoagulante', '')
    rx  = []
    if atc == 'varfarina':
        rx.append(_rx('Reversão varfarina',
                      'Vitamina K + CCP 4 fatores',
                      [_p('10 mg', 'IV lento', 'dose única (Vit K) + CCP dose por peso/INR')],
                      nota='CCP preferido sobre PFC para reversão rápida'))
    elif atc == 'dabigatrana':
        rx.append(_rx('Reversão dabigatrana',
                      'Idarucizumab',
                      [_p('5 g', 'IV', '2 frascos de 2,5 g em sequência')]))
    elif atc in ('apixabana', 'rivaroxabana'):
        rx.append(_rx('Reversão Xa-inibidor',
                      'Andexanet alfa OU CCP 4 fatores',
                      [_p('Andexanet alfa', 'IV', 'dose por agente/dose última tomada')],
                      nota='CCP 4 fatores 25–50 UI/kg se andexanet não disponível'))
    elif atc == 'hbpm':
        rx.append(_rx('Reversão HBPM',
                      'Protamina',
                      [_p('1 mg por 100 UI de HBPM', 'IV lento', 'última dose < 8h')]))
    return rx


# =============================================================================
# ENGINE PRINCIPAL
# =============================================================================

def analisar_hemorragia(dados: dict) -> dict:
    d    = dados
    ramo = d.get('ramo', 'ugib')
    si   = _shock_index(d)
    pas  = d.get('pas') or 120

    # ── STEP 1: Instabilidade hemodinâmica ───────────────────────────────────
    if si > 1 or pas < 90:
        rx = []
        if d.get('anticoagulado'):
            rx.extend(_reversao_rx(d))
        if _transfusion_needed(d):
            rx.extend(_transfusion_rx(d))

        variceal_suspeita = (d.get('cirrose') or d.get('estigmas_htpor') or
                             d.get('varizes_previas')) and ramo == 'ugib'
        if variceal_suspeita:
            rx.append(_rx('Vasoativo (variceal)',
                          'Octreotida',
                          [_p('50 mcg', 'IV bolus', 'seguido de 50 mcg/h infusão contínua')]))
            rx.append(_rx('Antibiótico profilático (cirrose)',
                          'Ceftriaxona',
                          [_p('1 g', 'IV', '1×/dia')],
                          nota='Iniciar IMEDIATAMENTE — reduz mortalidade em cirróticos'))

        cat = 'hd_ugib_instavel' if ramo == 'ugib' else 'hd_lgib_instavel'
        conduta = (
            'SAMU / PS — emergência imediata. '
            '2 acessos venosos calibrosos. O₂ suplementar. Monitorização contínua. '
            'Cristaloide IV (SF 0,9% ou RL). '
        )
        if variceal_suspeita:
            conduta += 'Octreotida + ceftriaxona IV ANTES da endoscopia. '
        if ramo == 'lgib':
            conduta += 'AngioTC urgente para localizar sítio. Embolização se localizado. '
        conduta += 'Endoscopia após estabilização hemodinâmica.'

        return {
            'tipo': 'hemorragia', 'ramo': ramo, 'categoria': cat,
            'urgencia': 'emergencia',
            'diagnostico': f'Hemorragia Digestiva {"Alta" if ramo=="ugib" else "Baixa"} com Instabilidade Hemodinâmica',
            'hipotese_principal': 'hemorragia_instavel',
            'shock_index': round(si, 2),
            'score_nome': None, 'score_valor': None,
            'variceal_suspeita': variceal_suspeita,
            'transfusao': _transfusion_needed(d),
            'conduta': conduta,
            'prescricoes_estruturadas': rx,
            'exames': 'Hemograma, coagulação (TP/INR/TTPa), função renal (BUN/Cr), TGO/TGP, tipagem + prova cruzada, lactato.',
            'encaminhamento': 'SAMU / PS emergência',
            'raciocinio': f'Shock index {round(si,2)} (>1) / PAS {pas} mmHg — instabilidade hemodinâmica confirmada.',
        }

    # ── STEP 2: UGIB branch ───────────────────────────────────────────────────
    if ramo == 'ugib':
        return _ugib(d, si)

    # ── STEP 3: LGIB branch ───────────────────────────────────────────────────
    return _lgib(d, si)


# =============================================================================
# UGIB
# =============================================================================

def _ugib(d, si) -> dict:
    gbs  = _gbs(d)
    hb   = d.get('hb') or 13
    dcv  = d.get('dcv')
    variceal = bool(
        d.get('cirrose') or d.get('estigmas_htpor') or d.get('varizes_previas')
    )
    transfundir = _transfusion_needed(d)

    # ── GBS 0–1: Baixíssimo risco → alta ─────────────────────────────────────
    if gbs <= 1:
        rx = []
        if transfundir:
            rx.extend(_transfusion_rx(d))
        if d.get('anticoagulado'):
            rx.extend(_reversao_rx(d))
        return {
            'tipo': 'hemorragia', 'ramo': 'ugib', 'categoria': 'hd_ugib_gbs_baixo',
            'urgencia': 'ambulatorio',
            'diagnostico': 'Hemorragia Digestiva Alta — Baixo Risco (GBS 0–1)',
            'hipotese_principal': 'ugib_baixo_risco',
            'score_nome': 'GBS', 'score_valor': gbs,
            'variceal_suspeita': variceal,
            'transfusao': transfundir,
            'conduta': (
                f'GBS {gbs} — risco muito baixo. Alta com acompanhamento ambulatorial. '
                'Endoscopia eletiva em < 2 semanas. '
                'Retornar ao PS se: nova hematêmese, melena, síncope ou piora do estado geral.'
            ),
            'prescricoes_estruturadas': rx,
            'exames': 'Hemograma, BUN, creatinina, tipagem sanguínea.',
            'encaminhamento': 'Ambulatório de gastro — endoscopia eletiva',
            'raciocinio': f'GBS {gbs} ≤ 1 — critérios de alta segura (BSG 2021 / ACG 2023). Tranexâmico NÃO recomendado.',
        }

    # ── GBS ≥2: Internação ────────────────────────────────────────────────────
    rx = []
    if transfundir:
        rx.extend(_transfusion_rx(d))
    if d.get('anticoagulado'):
        rx.extend(_reversao_rx(d))

    if variceal:
        return _ugib_variceal(d, gbs, rx, transfundir)
    else:
        return _ugib_nao_variceal(d, gbs, rx, transfundir, dcv)


def _ugib_variceal(d, gbs, rx_base, transfundir) -> dict:
    rx = list(rx_base)
    rx.append(_rx('Vasoativo',
                  'Octreotida',
                  [_p('50 mcg', 'IV bolus', 'seguido de 50 mcg/h infusão × 3–5 dias')],
                  nota='Iniciar ANTES da endoscopia'))
    rx.append(_rx('Antibiótico profilático (cirrose)',
                  'Ceftriaxona',
                  [_p('1 g', 'IV', '1×/dia × 7 dias')],
                  nota='Ou norfloxacino 400mg VO 12/12h se disponível'))
    rx.append(_rx('Procinético pré-endoscopia',
                  'Eritromicina',
                  [_p('250 mg', 'IV', '30–60 min antes da endoscopia (infusão lenta 20–30 min)')],
                  nota='AASLD 2024 / Baveno 2022: considerar se sem contraindicação (QT longo). '
                       'Reduz necessidade de 2ª endoscopia e melhora visualização. '
                       'Sem benefício demonstrado em mortalidade/ressangramento especificamente em variceal. '
                       'Verificar ECG se suspeita de QT prolongado.'))
    return {
        'tipo': 'hemorragia', 'ramo': 'ugib', 'categoria': 'hd_ugib_variceal',
        'urgencia': 'internacao',
        'diagnostico': 'Hemorragia Digestiva Alta — Variceal (Hipertensão Portal)',
        'hipotese_principal': 'ugib_variceal',
        'score_nome': 'GBS', 'score_valor': gbs,
        'variceal_suspeita': True,
        'transfusao': transfundir,
        'conduta': (
            f'GBS {gbs} — internação imediata. '
            'Octreotida IV + ceftriaxona IV IMEDIATAMENTE (antes da endoscopia). '
            'Eritromicina IV 30–60 min antes. '
            'Endoscopia em < 12h após estabilização — ligadura elástica (band ligation) 1ª linha. '
            'Balão de Sengstaken-Blakemore APENAS como ponte em sangramento maciço incontrolável. '
            'TIPS se refratário a endoscopia ou recorrência. '
            'Meta Hb ≥ 8 g/dL em cirróticos (estratégia levemente mais liberal). '
            'Beta-bloqueador (propranolol/nadolol): iniciar APÓS resolução — profilaxia secundária. '
            'Tranexâmico NÃO recomendado.'
        ),
        'prescricoes_estruturadas': rx,
        'exames': 'Hemograma, coagulação (TP/INR/TTPa), TGO/TGP, bilirrubinas, albumina, creatinina, tipagem + prova cruzada.',
        'encaminhamento': 'Internação — gastroenterologia / endoscopia de urgência',
        'raciocinio': f'GBS {gbs} + estigmas de hepatopatia/cirrose — sangramento varicoso até prova em contrário. Antibiótico profilático reduz mortalidade em cirróticos.',
    }


def _ugib_nao_variceal(d, gbs, rx_base, transfundir, dcv) -> dict:
    rx = list(rx_base)
    rx.append(_rx('IBP endovenoso',
                  'Omeprazol (ou Pantoprazol)',
                  [_p('80 mg', 'IV bolus', 'seguido de 8 mg/h infusão × 72h')],
                  nota='Pré e pós endoscopia se lesão de alto risco. Oral após 72h × 4–8 semanas.'))
    rx.append(_rx('Procinético pré-endoscopia',
                  'Eritromicina',
                  [_p('250 mg', 'IV', '30–60 min antes da endoscopia')],
                  nota='Opcional — melhora visualização por esvaziamento gástrico'))

    urgencia_endo = 'endoscopia < 12h' if gbs >= 7 else 'endoscopia dentro de 24h'
    return {
        'tipo': 'hemorragia', 'ramo': 'ugib', 'categoria': 'hd_ugib_nao_variceal',
        'urgencia': 'internacao',
        'diagnostico': 'Hemorragia Digestiva Alta — Não Variceal (PUD / Gastrite / Mallory-Weiss)',
        'hipotese_principal': 'ugib_nao_variceal',
        'score_nome': 'GBS', 'score_valor': gbs,
        'variceal_suspeita': False,
        'transfusao': transfundir,
        'conduta': (
            f'GBS {gbs} — internação. {urgencia_endo}. '
            'IBP IV bolus + infusão contínua. Eritromicina IV antes. '
            'Endoscopia hemostática se úlcera com sangramento ativo ou vaso visível. '
            'Adrenalina NUNCA isolada — combinar com clip / térmica / esclerosante. '
            'Pós-endoscopia: IBP IV 72h → oral 4–8 semanas (úlcera). '
            'H. pylori: testar TODOS com úlcera péptica sangrante → erradicar se positivo. '
            'AINE/AAS: suspender se possível. '
            'Tranexâmico NÃO recomendado. '
            'Anticoagulante: reiniciar em < 7 dias se indicação mantida (balancear trombose × ressangramento).'
        ),
        'prescricoes_estruturadas': rx,
        'exames': 'Hemograma, coagulação, BUN/Cr (BUN:Cr > 30 sugere HDA), tipagem + prova cruzada, TGO/TGP.',
        'encaminhamento': 'Internação — gastroenterologia / endoscopia digestiva',
        'raciocinio': f'GBS {gbs} ≥ 2 — sem estigmas de hepatopatia. Causa mais provável: PUD / gastrite / Mallory-Weiss. BSG 2021: sem benefício de endoscopia < 12h vs 24h em não-variceal estável.',
    }


# =============================================================================
# LGIB
# =============================================================================

def _lgib(d, si) -> dict:
    oakland = _oakland(d)
    transfundir = _transfusion_needed(d)

    # Instabilidade moderada: síncope ativa + sangramento + Oakland alto
    sangramento_ativo = bool(d.get('sincope') or d.get('palidez_sudorese'))
    if sangramento_ativo and oakland > 8:
        rx = []
        if transfundir:
            rx.extend(_transfusion_rx(d))
        if d.get('anticoagulado'):
            rx.extend(_reversao_rx(d))
        return {
            'tipo': 'hemorragia', 'ramo': 'lgib', 'categoria': 'hd_lgib_instavel',
            'urgencia': 'emergencia',
            'diagnostico': 'Hemorragia Digestiva Baixa — Instável / Sangramento Ativo',
            'hipotese_principal': 'lgib_instavel',
            'score_nome': 'Oakland', 'score_valor': oakland,
            'transfusao': transfundir,
            'conduta': (
                'AngioTC urgente — detecta sangramento ≥ 0,5 mL/min. '
                'Sítio localizado → embolização transcateter. '
                'Sítio não localizado + estável → endoscopia alta para excluir HDA. '
                'Falha radiológica → cirurgia. '
                'Ressuscitação paralela ao diagnóstico.'
            ),
            'prescricoes_estruturadas': rx,
            'exames': 'Hemograma, coagulação, BUN/Cr, tipagem + prova cruzada, lactato.',
            'encaminhamento': 'PS — radiologia intervencionista / cirurgia',
            'raciocinio': f'Oakland {oakland} + sinais de instabilidade. AngioTC antes da colonoscopia.',
        }

    # Oakland ≤8: baixo risco → alta
    if oakland <= 8:
        etiol = _etiologia_lgib(d)
        rx = []
        if transfundir:
            rx.extend(_transfusion_rx(d))
        rx.extend(etiol['rx'])
        return {
            'tipo': 'hemorragia', 'ramo': 'lgib', 'categoria': etiol['cat'],
            'urgencia': 'ambulatorio',
            'diagnostico': etiol['diag'],
            'hipotese_principal': etiol['hipotese'],
            'score_nome': 'Oakland', 'score_valor': oakland,
            'transfusao': transfundir,
            'conduta': etiol['conduta'],
            'prescricoes_estruturadas': rx,
            'exames': etiol['exames'],
            'encaminhamento': etiol['enc'],
            'raciocinio': f'Oakland {oakland} ≤ 8 — critérios de alta segura. {etiol["rac"]}',
        }

    # Oakland >8: internação + colonoscopia
    etiol = _etiologia_lgib(d)
    rx = []
    if transfundir:
        rx.extend(_transfusion_rx(d))
    rx.extend(etiol['rx'])
    return {
        'tipo': 'hemorragia', 'ramo': 'lgib', 'categoria': 'hd_lgib_internacao',
        'urgencia': 'internacao',
        'diagnostico': f'Hemorragia Digestiva Baixa — Internação ({etiol["hipotese"]})',
        'hipotese_principal': etiol['hipotese'],
        'score_nome': 'Oakland', 'score_valor': oakland,
        'transfusao': transfundir,
        'conduta': (
            f'Oakland {oakland} > 8 — internação. Colonoscopia durante a internação. '
            + etiol['conduta']
        ),
        'prescricoes_estruturadas': rx,
        'exames': 'Hemograma, coagulação, BUN/Cr, tipagem. ' + etiol['exames'],
        'encaminhamento': 'Internação — gastroenterologia / colonoscopia',
        'raciocinio': f'Oakland {oakland} > 8. {etiol["rac"]}',
    }


def _etiologia_lgib(d) -> dict:
    """Retorna dicionário com etiologia mais provável + conduta específica."""

    # Pós-polipectomia
    if d.get('pos_polipectomia'):
        return {
            'cat': 'hd_lgib_pos_polipectomia', 'hipotese': 'lgib_pos_polipectomia',
            'diag': 'Hemorragia Digestiva Baixa — Pós-polipectomia',
            'conduta': 'Colonoscopia para clip / hemostasia térmica. Geralmente autolimitado.',
            'rx': [],
            'exames': 'Hemograma.',
            'enc': 'Gastroenterologia / endoscopia',
            'rac': 'Sangramento pós-polipectomia — colonoscopia hemostática.',
        }

    # Fissura anal
    if d.get('dor_evacuacao') and d.get('papel_apenas'):
        rx = [
            _rx('1ª linha (fissura)',
                'Nitroglicerina 0,2–0,4% pomada',
                [_p('Aplicação local', '2×/dia', 'após evacuação × 6–8 semanas')],
                nota='Ou diltiazem 2% gel como alternativa — menos cefaleia'),
        ]
        return {
            'cat': 'hd_lgib_fissura', 'hipotese': 'lgib_fissura_anal',
            'diag': 'Hemorragia Digestiva Baixa — Fissura Anal',
            'conduta': (
                'Fibra alimentar (20–30 g/dia) + amolecedor de fezes + banhos de assento mornos. '
                'Nitroglicerina tópica 0,2–0,4% 2×/dia × 6–8 semanas (1ª linha). '
                'Alternativa: diltiazem 2% gel (menos cefaleia). '
                'Toxina botulínica: casos refratários. '
                'Esfincterotomia lateral interna: fissura crônica refratária ao tratamento clínico.'
            ),
            'rx': rx,
            'exames': 'Anuscopia para confirmar.',
            'enc': 'Ambulatório — proctologia se refratário',
            'rac': 'Dor + sangue no papel = fissura anal até prova em contrário.',
        }

    # Diverticular / Angiodisplasia — idoso sem sintomas de alarme (antes de hemorroida)
    idade = d.get('idade') or 0
    if idade >= 55 and not d.get('dor_evacuacao') and not d.get('papel_apenas') \
            and not d.get('diarreia_sangue') and not d.get('febre') \
            and not d.get('mudanca_habito') and not d.get('dor_abdominal'):
        return {
            'cat': 'hd_lgib_diverticular', 'hipotese': 'lgib_diverticular_angiodisplasia',
            'diag': 'Hemorragia Digestiva Baixa — Diverticular / Angiodisplasia',
            'conduta': (
                '80–90% dos sangramentos diverticulares resolvem espontaneamente. '
                'Colonoscopia após preparo: clips, adrenalina, coagulação térmica. '
                'Se instável ou incapaz de preparo: AngioTC → embolização. '
                'Recorrência / falha: colectomia segmentar. '
                'Angiodisplasia: coagulação a plasma de argônio (colonoscopia). '
                'Revisar anticoagulantes / AINEs / AAS. '
                'Reintroduzir anticoagulante em < 7 dias se indicação mantida.'
            ),
            'rx': [],
            'exames': 'Hemograma, coagulação, tipagem. Colonoscopia após preparo.',
            'enc': 'Internação se Oakland > 8; ambulatório (colonoscopia eletiva) se Oakland ≤ 8',
            'rac': 'Idoso + indolor + sem alarme = diverticular / angiodisplasia mais provável.',
        }

    # Hemorroida
    if d.get('papel_apenas') or (not d.get('dor_abdominal') and not d.get('diarreia_sangue')
                                  and not d.get('febre') and not d.get('mudanca_habito')):
        rx = [
            _rx('Tópico (hemorroida)',
                'Hidrocortisona + lidocaína pomada retal',
                [_p('Aplicação local', '2–3×/dia', '× 7–10 dias')]),
        ]
        return {
            'cat': 'hd_lgib_hemorroida', 'hipotese': 'lgib_hemorroida',
            'diag': 'Hemorragia Digestiva Baixa — Hemorroida',
            'conduta': (
                'Grau I–II: tópico (hidrocortisona + lidocaína) + fibra alimentar + banhos de assento. '
                'Evitar esforço ao evacuar. '
                'Grau III–IV: ligadura elástica, fotocoagulação a infravermelho ou hemorroidectomia. '
                'Colonoscopia para excluir patologia proximal se > 40 anos ou fatores de risco.'
            ),
            'rx': rx,
            'exames': 'Anuscopia. Colonoscopia se > 40 anos ou fatores de risco.',
            'enc': 'Ambulatório — coloproctologia se grau III–IV',
            'rac': 'Sangue no papel / anal sem dor abdominal = hemorroida como 1ª hipótese.',
        }

    # Colite infecciosa / C. diff
    if d.get('febre') and (d.get('atb_recente') or d.get('viagem_recente')):
        rx = []
        if d.get('atb_recente'):
            rx.append(_rx('C. difficile (se confirmado)',
                          'Vancomicina',
                          [_p('125 mg', 'VO', '6/6h × 10 dias')],
                          nota='Ou fidaxomicina 200mg 12/12h × 10 dias (preferencial em recorrência)'))
        return {
            'cat': 'hd_lgib_infecciosa', 'hipotese': 'lgib_colite_infecciosa',
            'diag': 'Hemorragia Digestiva Baixa — Colite Infecciosa',
            'conduta': (
                'Coprocultura + PCR C. difficile. '
                'Se C. diff positivo: vancomicina VO 125mg 6/6h × 10 dias (ou fidaxomicina). '
                'Bacteriana grave + fatores de risco: ciprofloxacino. '
                'Hidratação oral ou IV conforme perda. '
                'Evitar antiperistálticos em colite infecciosa.'
            ),
            'rx': rx,
            'exames': 'Hemograma, PCR. Coprocultura + PCR C. diff. Sódio/potássio se diarreia intensa.',
            'enc': 'Ambulatório — internação se desidratação grave ou imunossupressão',
            'rac': 'Febre + ATB recente / viagem → colite infecciosa / C. diff.',
        }

    # Colite isquêmica — verificar ANTES da DII (dor + vasculopatia é mais específico)
    if d.get('dor_abdominal') and d.get('dcv_dm') and d.get('diarreia_sangue'):
        return {
            'cat': 'hd_lgib_isquemica', 'hipotese': 'lgib_colite_isquemica',
            'diag': 'Hemorragia Digestiva Baixa — Colite Isquêmica',
            'conduta': (
                'Hidratação IV + repouso intestinal. '
                'ATB amplo espectro se grave (ciprofloxacino + metronidazol IV). '
                '⚠️ Sinais de isquemia transmural: defesa abdominal, lático elevado, pneumatose na TC → cirurgia urgente. '
                'Maioria resolve com tratamento conservador. '
                'Colonoscopia eletiva após resolução para confirmar diagnóstico.'
            ),
            'rx': [
                _rx('ATB (isquêmica grave)',
                    'Ciprofloxacino + Metronidazol',
                    [_p('400 mg IV 12/12h + 500 mg IV 8/8h', 'IV', 'até melhora clínica → oral')]),
            ],
            'exames': 'Hemograma, lactato, TC abdome com contraste. Colonoscopia após estabilização.',
            'enc': 'Internação — cirurgia se peritonite',
            'rac': 'Dor abdominal + DM/vasculopatia + diarreia com sangue = isquêmica até prova em contrário.',
        }

    # DII
    if d.get('dii_conhecida') or (d.get('diarreia_sangue') and not d.get('febre')
                                   and not d.get('atb_recente')):
        return {
            'cat': 'hd_lgib_dii', 'hipotese': 'lgib_dii_flare',
            'diag': 'Hemorragia Digestiva Baixa — Flare de DII (Crohn / RCUI)',
            'conduta': (
                'Excluir infecção PRIMEIRO: coprocultura, PCR C. diff, CMV se grave. '
                'Crise grave: metilprednisolona IV 40–60 mg/dia. '
                'Encaminhamento gastroenterologia para biológicos se refratário a corticoide. '
                'Manutenção: mesalazina (RCUI leve–moderada).'
            ),
            'rx': [
                _rx('Flare grave (DII)',
                    'Metilprednisolona',
                    [_p('40–60 mg', 'IV', '1×/dia até controle → desmame oral')],
                    nota='Apenas após excluir infecção (C. diff, CMV)'),
            ],
            'exames': 'Hemograma, PCR/VHS, albumina, coprocultura, PCR C. diff. Calprotectina fecal.',
            'enc': 'Gastroenterologia — colonoscopia eletiva',
            'rac': 'DII conhecida ou padrão crônico sem infecção → flare.',
        }

    # Neoplasia coloretal
    if d.get('mudanca_habito') or d.get('perda_peso'):
        return {
            'cat': 'hd_lgib_neoplasia', 'hipotese': 'lgib_neoplasia_coloretal',
            'diag': 'Hemorragia Digestiva Baixa — Suspeita de Neoplasia Colorretal',
            'conduta': (
                'Colonoscopia + biópsia URGENTE (não eletiva — suspeita de câncer). '
                'TC abdome/pelve + tórax para estadiamento após confirmação. '
                'Encaminhamento oncologia / coloproctologia. '
                'NÃO retardar investigação.'
            ),
            'rx': [],
            'exames': 'Hemograma, CEA, TC abdome/pelve. Colonoscopia com biópsia.',
            'enc': 'Colonoscopia urgente + oncologia / coloproctologia',
            'rac': 'Mudança de hábito intestinal + perda de peso = neoplasia até prova em contrário.',
        }

    # Fallback — etiologia indeterminada
    return {
        'cat': 'hd_lgib_diverticular', 'hipotese': 'lgib_indeterminado',
        'diag': 'Hemorragia Digestiva Baixa — Etiologia Indeterminada',
        'conduta': (
            'Colonoscopia eletiva para esclarecimento diagnóstico. '
            'Excluir neoplasia em pacientes > 40 anos ou com fatores de risco.'
        ),
        'rx': [],
        'exames': 'Hemograma. Colonoscopia.',
        'enc': 'Colonoscopia eletiva',
        'rac': 'Sem etiologia específica identificada — colonoscopia indicada.',
    }
