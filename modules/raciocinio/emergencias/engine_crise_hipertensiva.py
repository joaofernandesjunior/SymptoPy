# modules/raciocinio/emergencias/engine_crise_hipertensiva.py
# Crise hipertensiva no PA adulto — a tríade que evita o erro mais comum:
#
#   1. PSEUDOCRISE — dor/ansiedade/bexigoma elevando a PA → tratar a CAUSA,
#      NÃO dar anti-hipertensivo (a PA cai quando a dor passa).
#   2. PA ELEVADA ASSINTOMÁTICA — crônico mal controlado que veio por outro
#      motivo → ajustar esquema de base + seguimento; sem urgência real.
#   3. URGÊNCIA (PA ≥ 180/120 SEM lesão de órgão-alvo) → captopril 25–50 mg VO,
#      queda alvo ≤ 25% em 24–48h, observar 1–2h, alta com ajuste.
#   4. EMERGÊNCIA (lesão de órgão-alvo) → droga IV escolhida PELA SÍNDROME:
#         encefalopatia  → nitroprussiato (↓20-25% na 1ª hora)
#         EAP            → nitroglicerina + furosemida (nitroprussiato alternativa)
#         SCA            → nitroglicerina (NÃO se sildenafil < 24-48h ou VD)
#         dissecção      → BETABLOQUEIO PRIMEIRO (FC < 60), nitroprussiato depois
#         AVC isquêmico  → só tratar se > 220/120 (185/110 se candidato a trombólise)
#         AVC hemorrágico→ alvo PAS ~140 (INTERACT2), labetalol/nicardipina
#         eclâmpsia      → SULFATO DE MAGNÉSIO + hidralazina IV — ⛔ IECA e
#                          nitroprussiato VETADOS na gestação
#         adrenérgica    → benzodiazepínico (cocaína); ⛔ betabloqueio isolado
#
# Saída padrão emergências: Plano A (tratar aqui) / Plano B (encaminhar + carta).

def _parse_num(v):
    try:
        return float(str(v).replace(',', '.'))
    except (TypeError, ValueError):
        return None


_RX_CAPTOPRIL = {
    'linha': 'Urgência hipertensiva — 1ª opção',
    'medicamento': 'Captopril 25 mg',
    'prescricoes': [{'quantidade': '2', 'unidade': 'comprimidos',
                     'posologia': '25–50 mg VO agora (NÃO sublingual); '
                                  'reavaliar PA em 60–90 min'}],
    'nota': 'Alvo: queda ≤ 25% nas primeiras horas — NÃO normalizar. '
            '⛔ Gestante (IECA). Cautela: hipercalemia, depleção de volume, '
            'estenose bilateral de a. renal. Nifedipina SL é CONTRAINDICADA.',
}

_RX_CLONIDINA = {
    'linha': 'Urgência — alternativa (se IECA contraindicado)',
    'medicamento': 'Clonidina 0,1 mg',
    'prescricoes': [{'quantidade': '1', 'unidade': 'comprimido',
                     'posologia': '0,1–0,2 mg VO; repetir 0,1 mg/h se necessário '
                                  '(máx 0,6 mg)'}],
    'nota': 'Sedação é o efeito colateral dominante. Evitar se sonolência já presente.',
}


def _sindrome_emergencia(dados) -> tuple[str, str, dict, dict, list] | None:
    """Detecta a síndrome de lesão de órgão-alvo e retorna
    (categoria, diagnóstico, plano_a, plano_b, alertas)."""

    gestante = dados.get('gestante') or dados.get('gestante_20sem')

    # ── Eclâmpsia / pré-eclâmpsia grave — prioridade na gestante ─────────────
    if gestante and (dados.get('tod_encefalopatia') or dados.get('tod_convulsao')
                     or dados.get('epigastralgia_gestante')):
        return (
            'cha_eclampsia',
            'EMERGÊNCIA HIPERTENSIVA GESTACIONAL — eclâmpsia/pré-eclâmpsia grave',
            {'titulo': 'PLANO A — Tratar AQUI (até estabilizar)',
             'itens': ['SULFATO DE MAGNÉSIO: ataque 4 g IV em 20 min + manutenção 1-2 g/h',
                       'Hidralazina 5 mg IV a cada 20 min (máx 20 mg) OU nifedipina 10 mg VO',
                       'Alvo: PAS 140–155 / PAD 90–105 (não normalizar — perfusão placentária)',
                       'Decúbito lateral esquerdo + O₂',
                       'Gluconato de cálcio à mão (antídoto do MgSO₄)']},
            {'titulo': 'PLANO B — Transferir para obstetrícia (sempre, após MgSO₄)',
             'itens': ['MgSO₄ ANTES do transporte — a convulsão mata na ambulância',
                       'USA com médico', 'Avisar maternidade de alto risco']},
            ['⛔ GESTANTE: IECA (captopril) e nitroprussiato VETADOS',
             '⚠️ O tratamento definitivo da eclâmpsia é o PARTO'],
        )

    # ── Dissecção de aorta ───────────────────────────────────────────────────
    if dados.get('tod_dor_lacerante'):
        return (
            'cha_emergencia_dissecao',
            'EMERGÊNCIA HIPERTENSIVA — suspeita de dissecção de aorta',
            {'titulo': 'PLANO A — Anti-impulso AQUI',
             'itens': ['BETABLOQUEIO PRIMEIRO: esmolol/metoprolol IV — alvo FC < 60 em 20 min',
                       'SÓ DEPOIS vasodilatador: nitroprussiato — alvo PAS 100–120',
                       '⛔ Vasodilatador SEM betabloqueio prévio = taquicardia reflexa '
                       '→ mais força de cisalhamento na parede da aorta',
                       'Analgesia plena (morfina)', 'Angio-TC de aorta'],},
            {'titulo': 'PLANO B — Encaminhar (sem angio-TC/cirurgia)',
             'itens': ['Betabloqueio + analgesia ANTES de sair', 'USA obrigatória',
                       'Avisar destino: suspeita de dissecção']},
            ['⛔ NÃO antiagregar/anticoagular até excluir dissecção'],
        )

    # ── EAP — edema agudo de pulmão hipertensivo ─────────────────────────────
    if dados.get('tod_eap'):
        return (
            'cha_emergencia_eap',
            'EMERGÊNCIA HIPERTENSIVA — edema agudo de pulmão',
            {'titulo': 'PLANO A — Tratar AQUI',
             'itens': ['NITROGLICERINA IV em bomba: 10–20 µg/min, titular a cada 5 min '
                       '(é a droga DESTA síndrome — venodilatação ↓ pré-carga)',
                       'Furosemida 0,5–1 mg/kg IV',
                       'VNI (CPAP/BiPAP) precoce — reduz IOT',
                       'Alternativa sem nitroglicerina: nitroprussiato em bomba',
                       'Alvo: ↓ 20–25% na 1ª hora + melhora respiratória']},
            {'titulo': 'PLANO B — Encaminhar',
             'itens': ['Furosemida IV + nitrato (isossorbida 5 mg SL se sem bomba) antes de sair',
                       'VNI durante transporte se disponível — USA', 'O₂ alvo ≥ 90%']},
            [],
        )

    # ── SCA — dor torácica isquêmica ─────────────────────────────────────────
    if dados.get('tod_dor_isquemica'):
        return (
            'cha_emergencia_sca',
            'EMERGÊNCIA HIPERTENSIVA — síndrome coronariana aguda',
            {'titulo': 'PLANO A — Tratar AQUI',
             'itens': ['NITROGLICERINA IV (droga desta síndrome)',
                       '⛔ Nitrato VETADO se: sildenafil/tadalafil < 24–48h ou infarto de VD',
                       'Betabloqueio se sem sinais de IC/choque',
                       'Seguir protocolo de dor torácica (módulo próprio): ECG + AAS + estratificação',
                       'Alvo: alívio da dor + PA < 140/90 gradual']},
            {'titulo': 'PLANO B — Encaminhar',
             'itens': ['AAS 300 mastigado + nitrato SL (se sem veto) antes de sair',
                       'USA com desfibrilador']},
            [],
        )

    # ── AVC — déficit focal ──────────────────────────────────────────────────
    if dados.get('tod_deficit_focal'):
        return (
            'cha_emergencia_avc',
            'EMERGÊNCIA HIPERTENSIVA — AVC em curso (déficit focal)',
            {'titulo': 'PLANO A — Serviço com TC',
             'itens': ['TC de crânio ANTES de decidir tratar a PA — isquêmico × hemorrágico '
                       'mudam tudo',
                       'ISQUÊMICO: só tratar se PA > 220/120 (ou > 185/110 SE candidato a '
                       'trombólise) — queda ≤ 15% em 24h; penumbra depende de pressão',
                       'HEMORRÁGICO: alvo PAS ~140 (INTERACT2) — labetalol/nicardipina '
                       '(nitroprussiato é 2ª linha: ↑ PIC)',
                       'Glicemia capilar (hipoglicemia mimetiza AVC)'],},
            {'titulo': 'PLANO B — Sem TC no serviço',
             'itens': ['⛔ NÃO BAIXAR A PA ÀS CEGAS — sem TC não se sabe se isquêmico',
                       'Transferir IMEDIATO (janela de trombólise: 4,5h do início)',
                       'Anotar HORÁRIO EXATO do início do déficit na carta',
                       'Glicemia capilar antes de sair', 'USA']},
            ['⚠️ AVC isquêmico: baixar PA agressivamente AMPLIA a área infartada'],
        )

    # ── Encefalopatia hipertensiva ───────────────────────────────────────────
    if dados.get('tod_encefalopatia') or dados.get('tod_convulsao'):
        return (
            'cha_emergencia_encefalopatia',
            'EMERGÊNCIA HIPERTENSIVA — encefalopatia hipertensiva',
            {'titulo': 'PLANO A — Tratar AQUI (com bomba de infusão)',
             'itens': ['NITROPRUSSIATO em bomba: 0,25–0,5 µg/kg/min, titular '
                       '(proteger equipo da LUZ; risco de cianeto se > 48h ou DRC/hepatopatia)',
                       'Alternativas: labetalol ou nicardipina IV (sem risco de cianeto)',
                       'Alvo: ↓ 20–25% da PAM na 1ª HORA — nunca normalizar '
                       '(autorregulação cerebral deslocada no hipertenso crônico)',
                       'Diagnóstico é de EXCLUSÃO: TC para afastar AVC se déficit focal']},
            {'titulo': 'PLANO B — Sem bomba/UTI',
             'itens': ['Encaminhar para UTI — droga IV titulável é o tratamento',
                       'Evitar VO de ação rápida no transporte (queda não titulável)',
                       'USA com médico']},
            [],
        )

    # ── Crise adrenérgica (cocaína / feocromocitoma) ─────────────────────────
    if dados.get('uso_cocaina_simpaticomimetico'):
        return (
            'cha_adrenergica',
            'Crise hipertensiva ADRENÉRGICA (cocaína/simpaticomimético)',
            {'titulo': 'PLANO A — Tratar AQUI',
             'itens': ['BENZODIAZEPÍNICO é a 1ª droga (diazepam 5–10 mg IV) — '
                       'trata a descarga adrenérgica na origem',
                       '⛔ BETABLOQUEIO ISOLADO VETADO — alfa sem oposição piora a PA',
                       'Se persistir: nitroglicerina/fentolamina (ou nitroprussiato)',
                       'ECG: cocaína também faz SCA'],},
            {'titulo': 'PLANO B — Encaminhar',
             'itens': ['Benzodiazepínico antes de sair', 'Monitorizar — risco de arritmia']},
            ['⛔ Betabloqueador isolado contraindicado na intoxicação por cocaína'],
        )

    return None


def interpretar_crise_hipertensiva(dados: dict) -> dict:
    pas = _parse_num(dados.get('pas'))
    pad = _parse_num(dados.get('pad'))
    pa_txt = (f'{pas:.0f}×{pad:.0f}' if pas and pad else
              f'{pas:.0f}×?' if pas else 'não informada')

    base = {'tipo': 'crise_hipertensiva', 'pas': pas, 'pad': pad,
            'alertas_seguranca': [], 'prescricoes_estruturadas': []}

    # ── 4. EMERGÊNCIA — lesão de órgão-alvo domina qualquer número ───────────
    sind = _sindrome_emergencia(dados)
    if sind:
        cat, diag, plano_a, plano_b, alertas = sind
        r = {
            **base,
            'categoria': cat,
            'diagnostico': diag,
            'urgencia': 'emergencia',
            'raciocinio': (
                f'PA {pa_txt} mmHg + LESÃO AGUDA DE ÓRGÃO-ALVO = emergência '
                f'hipertensiva — droga IV titulável escolhida PELA SÍNDROME, '
                f'não pelo número. A pressa é controlada: na maioria das síndromes '
                f'o alvo é ↓ 20–25% na 1ª hora (exceções: dissecção — agressivo; '
                f'AVC isquêmico — quase não tratar).'
            ),
            'alertas_seguranca': alertas,
            'plano_a': plano_a,
            'plano_b': plano_b,
        }
        r['carta_encaminhamento'] = '\n'.join([
            'ENCAMINHAMENTO — EMERGÊNCIA HIPERTENSIVA', '',
            f'Motivo: {diag}',
            f'PA na admissão: {pa_txt} mmHg — às ____h____', '',
            'Já realizado neste serviço (registrar):',
            '  • Droga/dose: ______________________ — às ____h____',
            '  • PA após: ______ × ______ — às ____h____', '',
            'Solicito: UTI + droga IV titulável + investigação de órgão-alvo',
            'Segue: ECG, exames e este resumo.',
        ])
        return r

    # ── 1. PSEUDOCRISE — causa identificável elevando a PA ───────────────────
    causas = []
    if dados.get('dor_presente'):        causas.append('dor')
    if dados.get('ansiedade_panico'):    causas.append('ansiedade/pânico')
    if dados.get('retencao_urinaria'):   causas.append('retenção urinária/bexigoma')
    if causas:
        return {
            **base,
            'categoria': 'cha_pseudocrise',
            'diagnostico': f'PSEUDOCRISE hipertensiva — PA elevada por: {", ".join(causas)}',
            'urgencia': 'ambulatorio',
            'raciocinio': (
                f'PA {pa_txt} mmHg com causa identificável ({", ".join(causas)}) e SEM '
                f'lesão de órgão-alvo = pseudocrise. Tratar a CAUSA — analgesia, '
                f'ansiolítico ou sondagem — e REMEDIR a PA depois. Dar anti-hipertensivo '
                f'aqui trata o número, não o paciente, e ensina conduta errada '
                f'(a PA ia cair de qualquer jeito quando a dor passasse).'
            ),
            'plano_a': {'titulo': 'PLANO ÚNICO — Tratar a causa',
                        'itens': ['Analgesia / ansiolítico / sondagem conforme a causa',
                                  'REMEDIR PA após 30–60 min com paciente confortável',
                                  'Se persistir ≥ 180/120 sem causa → reclassificar como urgência',
                                  'NÃO prescrever anti-hipertensivo de ação rápida']},
            'plano_b': None,
        }

    # ── 2 e 3. Sem lesão de órgão-alvo — o número decide ────────────────────
    urgencia_num = (pas is not None and pas >= 180) or (pad is not None and pad >= 120)

    if urgencia_num:
        rxs = [_RX_CAPTOPRIL]
        if dados.get('gestante') or dados.get('gestante_20sem'):
            rxs = []  # IECA vetado — gestante com PA ≥ 160/110 é caso obstétrico
        elif dados.get('alergia_ieca') or dados.get('hipercalemia_conhecida'):
            rxs = [_RX_CLONIDINA]
        r = {
            **base,
            'categoria': 'cha_urgencia',
            'diagnostico': f'URGÊNCIA hipertensiva — PA {pa_txt} sem lesão de órgão-alvo',
            'urgencia': 'urgente',
            'raciocinio': (
                f'PA {pa_txt} mmHg (≥ 180/120) SEM lesão aguda de órgão-alvo = urgência '
                f'hipertensiva. Redução GRADUAL: ≤ 25% nas primeiras 24–48h, por via ORAL. '
                f'Captopril 25–50 mg VO (início 15–30 min, pico ~1h) é 1ª opção; '
                f'⛔ nifedipina SL contraindicada (queda abrupta → isquemia). '
                f'Observar 1–2h, confirmar tendência de queda e dar alta com ajuste do '
                f'esquema crônico + retorno em 24–72h. Internação NÃO indicada.'
                + (' ⚠️ GESTANTE: IECA vetado — PA ≥ 160/110 na gestação é manejo '
                   'obstétrico (metildopa/nifedipina VO + encaminhar pré-natal de alto '
                   'risco HOJE).' if dados.get('gestante') or dados.get('gestante_20sem') else '')
            ),
            'prescricoes_estruturadas': rxs,
            'plano_a': {'titulo': 'PLANO ÚNICO — Manejo no próprio serviço',
                        'itens': ['Captopril 25–50 mg VO (receita) — reavaliar em 60–90 min',
                                  'Queda ~10–25% + assintomático → ALTA',
                                  'Ajustar/retomar esquema anti-hipertensivo crônico '
                                  '(má adesão é a causa nº 1)',
                                  'Retorno ambulatorial em 24–72h com PA aferida',
                                  'Aparecer sintoma de órgão-alvo durante a observação → '
                                  'reclassificar como EMERGÊNCIA']},
            'plano_b': None,
        }
        return r

    return {
        **base,
        'categoria': 'cha_assintomatica',
        'diagnostico': f'PA elevada assintomática ({pa_txt}) — sem critério de crise',
        'urgencia': 'ambulatorio',
        'raciocinio': (
            f'PA {pa_txt} mmHg, abaixo de 180/120, sem sintomas e sem lesão de '
            f'órgão-alvo: NÃO é crise hipertensiva — é hipertensão crônica mal '
            f'controlada flagrada no PA. Reduzir agudamente não traz benefício e '
            f'pode causar hipoperfusão. Conduta: ajustar o esquema de base e '
            f'garantir seguimento ambulatorial.'
        ),
        'plano_a': {'titulo': 'PLANO ÚNICO — Ajuste e seguimento',
                    'itens': ['NÃO prescrever anti-hipertensivo de ação rápida',
                              'Verificar adesão ao esquema atual (causa nº 1)',
                              'Ajustar/retomar medicação crônica',
                              'Agendar seguimento ambulatorial < 7 dias',
                              'Orientar sinais de alarme (cefaleia intensa, dor torácica, '
                              'dispneia, déficit) → retorno imediato']},
        'plano_b': None,
    }
