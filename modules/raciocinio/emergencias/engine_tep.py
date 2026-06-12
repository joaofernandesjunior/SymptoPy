# modules/raciocinio/emergencias/engine_tep.py
# TEP — Tromboembolismo Pulmonar com raciocínio bayesiano explícito.
#
# Pipeline (ESC 2019 + PEGeD 2019 + PERC):
#   0. INSTÁVEL? → TEP de alto risco: POCUS/eco; VD disfuncional + choque →
#      reperfusão SEM angio-TC (paciente não vai ao tomógrafo).
#   1. Wells dois níveis → probabilidade PRÉ-teste (improvável ≤4 ≈ 12% | provável >4 ≈ 37%)
#   2. PERC (só se improvável): 8/8 negativos → P < 2% (abaixo do limiar de TESTE) → encerra.
#   3. D-dímero com limiar ajustado por idade (>50a: idade × 10 µg/L FEU).
#   4. Bayes: odds pós = odds pré × LR.  D-dímero(-) LR ≈ 0,10 | D-dímero(+) LR ≈ 1,7.
#   5. Dois limiares na saída:
#      - TESTE (~2%): abaixo → não investigar mais.
#      - TRATAMENTO (ESC 2019): prob. alta → anticoagular JÁ (antes da confirmação);
#        intermediária → anticoagular se confirmação demora > 4h; baixa → se > 24h.
#
# Saída em DOIS PLANOS (decisão do João, 2026-06-12):
#   plano_a — investigar/tratar AQUI (assume angio-TC disponível)
#   plano_b — ENCAMINHAR, com carta de encaminhamento estruturada pronta
# O médico escolhe na hora conforme o serviço onde está.

# ── Wells (versão dois níveis) ────────────────────────────────────────────────
_WELLS_ITEMS = [
    ('tvp_sinais_clinicos',   3.0, 'Sinais clínicos de TVP (edema + dor à palpação)'),
    ('tep_mais_provavel',     3.0, 'TEP é o diagnóstico mais provável (julgamento clínico)'),
    ('fc_maior_100',          1.5, 'FC > 100 bpm'),
    ('imobilizacao_cirurgia', 1.5, 'Imobilização ≥ 3 dias ou cirurgia < 4 semanas'),
    ('tep_tvp_previo',        1.5, 'TEP/TVP prévio'),
    ('hemoptise',             1.0, 'Hemoptise'),
    ('neoplasia_ativa',       1.0, 'Neoplasia ativa (tratamento < 6 meses ou paliativo)'),
]

# ── PERC (aplicável só se Wells improvável) ───────────────────────────────────
_PERC_ITEMS = [
    ('perc_idade_50',        'Idade ≥ 50 anos'),
    ('fc_maior_100',         'FC ≥ 100 bpm'),          # compartilhado com Wells
    ('perc_spo2_95',         'SpO₂ < 95% em ar ambiente'),
    ('perc_edema_unilateral','Edema unilateral de MMII'),
    ('hemoptise',            'Hemoptise'),              # compartilhado com Wells
    ('imobilizacao_cirurgia','Cirurgia/trauma < 4 semanas'),
    ('tep_tvp_previo',       'TEP/TVP prévio'),
    ('perc_estrogeno',       'Uso de estrogênio'),
]

# Probabilidades pré-teste (Wells dois níveis — Christopher Study / PEGeD)
_PRE_IMPROVAVEL = 0.12
_PRE_PROVAVEL   = 0.37

# Likelihood ratios — D-dímero de alta sensibilidade (ELISA quantitativo)
_LR_DDIMER_NEG = 0.10
_LR_DDIMER_POS = 1.70

LIMIAR_TESTE = 0.02   # abaixo: não investigar (Pauker-Kassirer; PERC valida ~<2%)

# ── sPESI — estratificação para o TEP confirmado/provável ────────────────────
_SPESI_ITEMS = [
    ('spesi_idade_80',      'Idade > 80 anos'),
    ('neoplasia_ativa',     'Neoplasia ativa'),
    ('spesi_cardiopulmonar','Doença cardiopulmonar crônica (IC/DPOC)'),
    ('fc_maior_100',        'FC ≥ 110 bpm'),   # aproximação: item original é 110
    ('spesi_pas_100',       'PAS < 100 mmHg'),
    ('perc_spo2_95',        'SpO₂ < 90%'),     # aproximação conservadora
]


def _bayes(pre: float, lr: float) -> float:
    odds = pre / (1.0 - pre)
    odds_pos = odds * lr
    return odds_pos / (1.0 + odds_pos)


def _wells(dados) -> tuple[float, list]:
    score, itens = 0.0, []
    for chave, pts, descr in _WELLS_ITEMS:
        if dados.get(chave):
            score += pts
            itens.append(f'{descr} (+{pts:g})')
    return score, itens


def _perc(dados, idade) -> list:
    """Itens PERC positivos (lista vazia = PERC totalmente negativo)."""
    positivos = []
    for chave, descr in _PERC_ITEMS:
        if chave == 'perc_idade_50':
            if idade is not None and idade >= 50:
                positivos.append(descr)
        elif dados.get(chave):
            positivos.append(descr)
    return positivos


def _ddimer_limiar(idade) -> float:
    """Limiar ajustado por idade (µg/L FEU): 500, ou idade×10 acima de 50 anos."""
    if idade is not None and idade > 50:
        return float(idade) * 10.0
    return 500.0


def _spesi(dados) -> tuple[int, list]:
    score, itens = 0, []
    for chave, descr in _SPESI_ITEMS:
        if dados.get(chave):
            score += 1
            itens.append(descr)
    return score, itens


def _rx_enoxaparina(peso_kg) -> dict:
    if peso_kg:
        dose = round(float(peso_kg))
        posologia = f'{dose} mg ({peso_kg} kg × 1 mg/kg) SC 12/12h'
    else:
        posologia = '1 mg/kg SC 12/12h (calcular pelo peso)'
    return {
        'linha': 'Anticoagulação — TEP suspeito/confirmado',
        'medicamento': 'Enoxaparina 1 mg/kg',
        'prescricoes': [{'quantidade': '1', 'unidade': 'seringa por dose',
                         'posologia': posologia}],
        'nota': 'Checar contraindicações: sangramento ativo, plaquetopenia < 50.000, '
                'cirurgia SNC/olho recente. Se ClCr < 30: 1 mg/kg 1×/dia ou HNF.',
    }


def _carta_encaminhamento(dados, contexto: dict) -> str:
    """Carta de encaminhamento estruturada — pronta para imprimir/transcrever."""
    l = ['ENCAMINHAMENTO — SUSPEITA DE TEP', '']
    l.append(f"Motivo: {contexto['motivo']}")
    l.append('')
    l.append(f"Estratificação realizada neste serviço:")
    l.append(f"  • Wells: {contexto['wells_score']:g} ({contexto['classe_pre']}) "
             f"— probabilidade pré-teste ≈ {contexto['pre_teste']*100:.0f}%")
    if contexto.get('ddimer_txt'):
        l.append(f"  • D-dímero: {contexto['ddimer_txt']}")
    if contexto.get('pos_teste') is not None:
        l.append(f"  • Probabilidade PÓS-teste estimada ≈ {contexto['pos_teste']*100:.0f}%")
    if contexto.get('spesi_txt'):
        l.append(f"  • sPESI: {contexto['spesi_txt']}")
    l.append('')
    feitos = contexto.get('ja_realizado', [])
    if feitos:
        l.append('Já realizado neste serviço (registrar horários):')
        for f in feitos:
            l.append(f'  • {f} — às ____h____')
    l.append('')
    l.append(f"Solicito: {contexto['solicito']}")
    l.append('Segue: ECG, exames disponíveis e este resumo.')
    return '\n'.join(l)


def interpretar_tep(dados: dict) -> dict:
    idade = dados.get('idade')
    try:
        idade = float(idade) if idade is not None else None
    except (TypeError, ValueError):
        idade = None
    peso = dados.get('peso_kg')

    wells_score, wells_itens = _wells(dados)
    provavel = wells_score > 4
    pre = _PRE_PROVAVEL if provavel else _PRE_IMPROVAVEL
    classe_pre = 'TEP provável (Wells > 4)' if provavel else 'TEP improvável (Wells ≤ 4)'

    base = {
        'tipo': 'tep',
        'wells_score': wells_score,
        'wells_itens': wells_itens,
        'pre_teste': pre,
        'classe_pre': classe_pre,
        'alertas_seguranca': [],
        'prescricoes_estruturadas': [],
    }
    if dados.get('sangramento_ativo'):
        base['alertas_seguranca'].append(
            '⛔ SANGRAMENTO ATIVO relatado — anticoagulação CONTRAINDICADA até reavaliação; '
            'priorizar transferência para confirmação diagnóstica.')

    # ── 0. INSTÁVEL → TEP de alto risco ──────────────────────────────────────
    if dados.get('hipotensao_choque'):
        vd = dados.get('pocus_vd_disfuncao')
        anticoag_ok = not dados.get('sangramento_ativo')
        r = {
            **base,
            'categoria': 'tep_alto_risco',
            'diagnostico': 'TEP de ALTO RISCO (instabilidade hemodinâmica)',
            'urgencia': 'emergencia',
            'pos_teste': None,
            'raciocinio': (
                'Hipotensão/choque + suspeita de TEP = TEP de alto risco até prova em '
                'contrário. Paciente instável NÃO vai ao tomógrafo: ESC 2019 indica '
                'ecocardiograma/POCUS à beira-leito — disfunção de VD em paciente '
                'instável autoriza REPERFUSÃO SEM angio-TC. '
                + ('POCUS já demonstrou disfunção de VD → critério preenchido.' if vd
                   else 'Realizar POCUS imediatamente: VD dilatado/hipocinético?')
            ),
            'plano_a': {
                'titulo': 'PLANO A — Tratar AQUI (serviço com suporte)',
                'itens': [
                    'MOV + O₂ alvo SpO₂ ≥ 90% + acesso calibroso',
                    'Cristaloide cauteloso ≤ 500 mL (VD falhando piora com volume)',
                    'Noradrenalina se PAS persistir < 90 mmHg',
                    ('TROMBÓLISE: alteplase 100 mg IV em 2h (ou 0,6 mg/kg em 15 min se peri-PCR)'
                     if anticoag_ok and vd else
                     'POCUS para confirmar VD antes de trombolisar' if anticoag_ok else
                     '⛔ Trombólise contraindicada (sangramento) — embolectomia/suporte'),
                    'Heparina NÃO fracionada em bomba (preferida na instabilidade)',
                ],
            },
            'plano_b': {
                'titulo': 'PLANO B — Encaminhar (serviço sem suporte)',
                'itens': [
                    'Estabilização máxima possível ANTES do transporte (MOV, vasopressor)',
                    'Transporte: USA (ambulância avançada) com médico — paciente instável',
                    ('Discutir trombólise ANTES do transporte com a regulação — '
                     'se transferência > 30-60 min e VD disfuncional, trombolisar AQUI'
                     if anticoag_ok else '⛔ Sem trombólise — sangramento ativo'),
                ],
            },
        }
        r['carta_encaminhamento'] = _carta_encaminhamento(dados, {
            'motivo': 'TEP de ALTO RISCO — instabilidade hemodinâmica',
            'wells_score': wells_score, 'classe_pre': classe_pre, 'pre_teste': pre,
            'pos_teste': None, 'ddimer_txt': '',
            'ja_realizado': ['MOV + O₂', 'Acesso venoso',
                             'Trombólise (se realizada): alteplase ____ mg'],
            'solicito': 'UTI + angio-TC quando estável + manejo de TEP de alto risco',
        })
        return r

    # ── 2. PERC — só se improvável ───────────────────────────────────────────
    if not provavel:
        perc_pos = _perc(dados, idade)
        if dados.get('perc_aplicado') and not perc_pos:
            return {
                **base,
                'categoria': 'tep_descartado_perc',
                'diagnostico': 'TEP descartado por PERC (sem exames)',
                'urgencia': 'ambulatorio',
                'pos_teste': None,   # PERC negativo valida "< 2%" (Kline 2008) — sem número pontual
                'raciocinio': (
                    f'Wells {wells_score:g} ({classe_pre}, pré-teste ≈ {pre*100:.0f}%) '
                    f'+ PERC 8/8 negativos → probabilidade < 2% — ABAIXO DO LIMIAR DE TESTE. '
                    f'Investigar agora geraria mais dano (falso-positivo → anticoagulação '
                    f'desnecessária) que benefício. NÃO solicitar D-dímero nem imagem.'
                ),
                'plano_a': {'titulo': 'PLANO ÚNICO — Alta com orientações',
                            'itens': ['Sem exames para TEP',
                                      'Investigar diagnóstico alternativo da dispneia/dor',
                                      'Retorno se piora, síncope ou hemoptise']},
                'plano_b': None,
                'perc_itens_positivos': [],
            }
        base['perc_itens_positivos'] = perc_pos

    # ── 3-4. D-dímero + Bayes ────────────────────────────────────────────────
    ddimer = dados.get('ddimer_valor')
    try:
        ddimer = float(ddimer) if ddimer not in (None, '') else None
    except (TypeError, ValueError):
        ddimer = None
    limiar = _ddimer_limiar(idade)
    limiar_txt = (f'{limiar:.0f} µg/L (ajustado: {idade:.0f} anos × 10)'
                  if idade and idade > 50 else f'{limiar:.0f} µg/L')

    pos = None
    ddimer_txt = ''
    if ddimer is not None and not provavel:
        if ddimer < limiar:
            pos = _bayes(pre, _LR_DDIMER_NEG)
            ddimer_txt = f'{ddimer:.0f} µg/L — NEGATIVO para limiar {limiar_txt}'
            return {
                **base,
                'categoria': 'tep_descartado_ddimer',
                'diagnostico': 'TEP descartado — D-dímero negativo (ajustado por idade)',
                'urgencia': 'ambulatorio',
                'pos_teste': pos,
                'ddimer_txt': ddimer_txt,
                'raciocinio': (
                    f'Wells {wells_score:g} ({classe_pre}, pré-teste ≈ {pre*100:.0f}%). '
                    f'D-dímero {ddimer:.0f} µg/L abaixo do limiar ajustado por idade '
                    f'({limiar_txt}) — LR(-) ≈ 0,10 → probabilidade PÓS-teste ≈ '
                    f'{pos*100:.1f}% — abaixo do limiar de teste (2%). '
                    f'Angio-TC NÃO indicada (PEGeD 2019: seguro, NPV > 99%). '
                    f'Buscar diagnóstico alternativo.'
                ),
                'plano_a': {'titulo': 'PLANO ÚNICO — TEP excluído',
                            'itens': ['Sem angio-TC', 'Investigar diagnóstico alternativo',
                                      'Retorno se piora']},
                'plano_b': None,
            }
        else:
            pos = _bayes(pre, _LR_DDIMER_POS)
            ddimer_txt = f'{ddimer:.0f} µg/L — POSITIVO para limiar {limiar_txt}'
    elif ddimer is not None and provavel:
        # Wells provável: D-dímero NÃO descarta (NPV insuficiente) — registrar apenas
        ddimer_txt = (f'{ddimer:.0f} µg/L — irrelevante para exclusão '
                      f'(Wells provável: ir direto à imagem)')
        pos = pre
    else:
        pos = pre  # sem D-dímero: pós = pré

    # ── 5. Limiar de TRATAMENTO + planos A/B ─────────────────────────────────
    anticoag_ja = provavel or (pos is not None and pos >= 0.30)
    anticoag_se_demora = (not anticoag_ja) and (pos is not None and pos >= LIMIAR_TESTE)
    anticoag_ok = not dados.get('sangramento_ativo')

    spesi_score, spesi_itens = _spesi(dados)
    spesi_txt = f'{spesi_score} ({", ".join(spesi_itens)})' if spesi_itens else '0 — baixo risco'

    raciocinio = (
        f'Wells {wells_score:g} ({classe_pre}) → pré-teste ≈ {pre*100:.0f}%. '
        + (f'D-dímero: {ddimer_txt}. ' if ddimer_txt else
           'D-dímero não realizado. ')
        + (f'Probabilidade PÓS-teste ≈ {pos*100:.0f}% — acima do limiar de teste (2%): '
           f'ANGIO-TC INDICADA. ' if pos >= LIMIAR_TESTE else '')
        + ('LIMIAR DE TRATAMENTO atingido: probabilidade alta → anticoagular AGORA, '
           'antes/independente da confirmação (ESC 2019). ' if anticoag_ja and anticoag_ok else '')
        + ('Probabilidade intermediária: anticoagular se a confirmação demorar > 4h '
           '(caso típico do encaminhamento). ' if anticoag_se_demora and anticoag_ok else '')
        + ('⛔ Anticoagulação suspensa: sangramento ativo. ' if not anticoag_ok else '')
    )

    rxs = []
    if anticoag_ok and (anticoag_ja or anticoag_se_demora):
        rxs.append(_rx_enoxaparina(peso))

    plano_a = {
        'titulo': 'PLANO A — Investigar/tratar AQUI (serviço com angio-TC)',
        'itens': [
            'Angio-TC de tórax (protocolo TEP)',
            ('Anticoagular ANTES do resultado (probabilidade alta)' if anticoag_ja and anticoag_ok
             else 'Anticoagular se resultado demorar > 4h' if anticoag_se_demora and anticoag_ok
             else '⛔ Sem anticoagulação empírica (sangramento)' if not anticoag_ok
             else 'Aguardar resultado sem anticoagulação'),
            f'Estratificar se confirmado: sPESI = {spesi_txt}',
            ('sPESI 0 → considerar tratamento ambulatorial/alta precoce (HESTIA)'
             if spesi_score == 0 else 'sPESI ≥ 1 → internação'),
            'Troponina + ecocardiograma se sPESI ≥ 1 (estratificação intermediário alto/baixo)',
        ],
    }
    plano_b = {
        'titulo': 'PLANO B — Encaminhar (serviço sem angio-TC)',
        'itens': [
            ('Enoxaparina 1 mg/kg SC ANTES de sair — transferência conta como '
             '"confirmação > 4h" (ESC 2019)' if anticoag_ok and (anticoag_ja or anticoag_se_demora)
             else '⛔ Sem anticoagulação (sangramento) — transferir prioritário'),
            'O₂ se SpO₂ < 90%',
            'Transporte: USB se estável; USA se SpO₂ limítrofe ou sPESI ≥ 1',
            'Carta de encaminhamento abaixo — preencher horários',
        ],
    }

    cat = 'tep_provavel_imagem' if pos >= LIMIAR_TESTE else 'tep_baixa_prob'
    r = {
        **base,
        'categoria': cat,
        'diagnostico': (f'Suspeita de TEP — pós-teste ≈ {pos*100:.0f}% → angio-TC indicada'
                        if pos >= LIMIAR_TESTE else
                        'Suspeita de TEP — probabilidade abaixo do limiar de teste'),
        'urgencia': 'urgente' if pos >= LIMIAR_TESTE else 'ambulatorio',
        'pos_teste': pos,
        'ddimer_txt': ddimer_txt,
        'spesi_score': spesi_score,
        'raciocinio': raciocinio,
        'plano_a': plano_a,
        'plano_b': plano_b,
        'prescricoes_estruturadas': rxs,
    }
    r['carta_encaminhamento'] = _carta_encaminhamento(dados, {
        'motivo': f'Suspeita de TEP — necessita angio-TC (indisponível neste serviço)',
        'wells_score': wells_score, 'classe_pre': classe_pre, 'pre_teste': pre,
        'pos_teste': pos, 'ddimer_txt': ddimer_txt, 'spesi_txt': spesi_txt,
        'ja_realizado': (['Enoxaparina 1 mg/kg SC'] if rxs else []) + ['O₂ (se aplicável)'],
        'solicito': 'Angio-TC de tórax protocolo TEP + estratificação e manejo',
    })
    return r
