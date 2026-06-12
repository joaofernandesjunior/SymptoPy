# modules/raciocinio/emergencias/engine_dor_toracica.py
# Dor torácica no PA adulto — STEMI (regra dos 120 min), HEART score,
# e os 3 diferenciais letais (dissecção, TEP, pneumotórax hipertensivo).
#
# Decisões de design (João, 2026-06-12):
#   - A logística decide o STEMI: distância até hemodinâmica EM MINUTOS é
#     campo do formulário (não perfil persistente). ESC/AHA: se PCI não for
#     alcançável em ≤ 120 min do diagnóstico → trombolisar em ≤ 30 min
#     (porta-agulha) e transferir (estratégia fármaco-invasiva).
#   - Demais vias saem com PLANO A (tratar/investigar aqui) + PLANO B
#     (encaminhar + carta) e o médico escolhe.
#
# Categorias:
#   dtx_pneumotorax_hipertensivo  — descompressão IMEDIATA
#   dtx_dissecao_suspeita         — NÃO trombolisar; controlar PA; angio-TC
#   dtx_stemi                     — via logística 120 min
#   dtx_sca_alto_risco            — HEART 7-10 ou tropo elevada/ECG isquêmico
#   dtx_sca_intermediario         — HEART 4-6 → seriar tropo vs encaminhar
#   dtx_baixo_risco               — HEART 0-3 + tropo normal (MACE ~1,7%)
#   dtx_inespecifica              — sem dados suficientes (sem ECG/tropo)

# ── Contraindicações ABSOLUTAS à trombólise (STEMI) ──────────────────────────
_CONTRAIND_TROMBOLISE = [
    ('sangramento_ativo',      'sangramento ativo'),
    ('avc_hemorragico_previo', 'AVC hemorrágico prévio (qualquer época)'),
    ('avci_3m',                'AVC isquêmico < 3 meses'),
    ('neo_snc',                'neoplasia/lesão estrutural de SNC'),
    ('tce_cirurgia_3sem',      'TCE/cirurgia grande < 3 semanas'),
    ('dissecao_suspeita_flag', 'suspeita de dissecção de aorta'),
]


def _heart(dados, idade) -> tuple[int | None, list, bool]:
    """HEART score. Retorna (score, itens, completo)."""
    itens = []
    score = 0
    completo = True

    # H — História
    hist = dados.get('historia_suspeita', '')
    h_pts = {'pouco': 0, 'moderada': 1, 'muito': 2}.get(hist)
    if h_pts is None:
        completo = False
    else:
        score += h_pts
        itens.append(f'História {hist} suspeita ({h_pts})')

    # E — ECG
    if dados.get('ecg_infra_st_t_neg'):
        score += 2; itens.append('ECG: infra de ST / inversão de T (2)')
    elif dados.get('ecg_alteracao_inespecifica'):
        score += 1; itens.append('ECG: alteração inespecífica de repolarização (1)')
    elif dados.get('ecg_normal'):
        itens.append('ECG normal (0)')
    else:
        completo = False

    # A — Age
    if idade is not None:
        a = 2 if idade >= 65 else (1 if idade >= 45 else 0)
        score += a
        itens.append(f'Idade {idade:.0f} ({a})')
    else:
        completo = False

    # R — Fatores de risco (HAS, DM, tabagismo, dislipidemia, obesidade,
    #     história familiar; aterosclerose conhecida = 2 direto)
    n_fr = sum(bool(dados.get(k)) for k in (
        'fr_has', 'fr_dm', 'fr_tabagismo', 'fr_dislipidemia',
        'fr_obesidade', 'fr_hist_familiar'))
    if dados.get('fr_aterosclerose_conhecida'):
        score += 2; itens.append('Aterosclerose conhecida — IAM/AVC/DAP prévio (2)')
    elif n_fr >= 3:
        score += 2; itens.append(f'{n_fr} fatores de risco (2)')
    elif n_fr >= 1:
        score += 1; itens.append(f'{n_fr} fator(es) de risco (1)')
    else:
        itens.append('Sem fatores de risco (0)')

    # T — Troponina
    tropo = dados.get('troponina', '')
    t_pts = {'normal': 0, 'elevada_1_3x': 1, 'elevada_3x': 2}.get(tropo)
    if t_pts is None:
        completo = False
    else:
        score += t_pts
        lbl = {'normal': 'normal', 'elevada_1_3x': '1–3× LSN', 'elevada_3x': '> 3× LSN'}[tropo]
        itens.append(f'Troponina {lbl} ({t_pts})')

    return (score if completo else None), itens, completo


def _contraind_trombolise(dados) -> list:
    return [descr for chave, descr in _CONTRAIND_TROMBOLISE if dados.get(chave)]


def _rx_stemi_base(peso_kg, vai_trombolisar: bool, idade) -> list:
    """Kit farmacológico do STEMI antes do transporte/reperfusão."""
    rxs = [
        {
            'linha': 'Antiagregação 1 — IMEDIATO',
            'medicamento': 'AAS 100 mg',
            'prescricoes': [{'quantidade': '3', 'unidade': 'comprimidos',
                             'posologia': '300 mg VO MASTIGADOS agora, dose única'}],
            'nota': 'Mastigar acelera absorção. Contraindicação real é rara (alergia verdadeira).',
        },
    ]
    if vai_trombolisar and idade is not None and idade >= 75:
        clop = ('75 mg VO agora (SEM dose de ataque — ≥ 75 anos com trombolítico)', '1')
    else:
        clop = ('300 mg VO agora, dose única de ataque', '4')
    rxs.append({
        'linha': 'Antiagregação 2',
        'medicamento': 'Clopidogrel 75 mg',
        'prescricoes': [{'quantidade': clop[1], 'unidade': 'comprimidos',
                         'posologia': clop[0]}],
        'nota': 'Com trombolítico: ataque 300 mg (< 75 anos) ou 75 mg (≥ 75 anos).',
    })
    if peso_kg:
        enox = f'{round(float(peso_kg))} mg ({peso_kg} kg × 1 mg/kg) SC 12/12h'
    else:
        enox = '1 mg/kg SC 12/12h (calcular pelo peso)'
    rxs.append({
        'linha': 'Anticoagulação',
        'medicamento': 'Enoxaparina 1 mg/kg',
        'prescricoes': [{'quantidade': '1', 'unidade': 'seringa por dose',
                         'posologia': enox}],
        'nota': '≥ 75 anos: 0,75 mg/kg SC 12/12h SEM bolus IV. ClCr < 30: 1 mg/kg 1×/dia.',
    })
    if vai_trombolisar:
        if peso_kg:
            p = float(peso_kg)
            tnk = ('30 mg' if p < 60 else '35 mg' if p < 70 else
                   '40 mg' if p < 80 else '45 mg' if p < 90 else '50 mg')
            tnk_pos = f'{tnk} IV em bolus único (peso {peso_kg} kg)'
        else:
            tnk_pos = 'Bolus IV único por peso: <60kg=30 | 60-69=35 | 70-79=40 | 80-89=45 | ≥90=50 mg'
        rxs.append({
            'linha': 'TROMBOLÍTICO — porta-agulha ≤ 30 min',
            'medicamento': 'Tenecteplase (TNK)',
            'prescricoes': [{'quantidade': '1', 'unidade': 'frasco',
                             'posologia': tnk_pos}],
            'nota': '≥ 75 anos: considerar MEIA dose. Checar contraindicações ANTES. '
                    'Alternativa: alteplase regime acelerado 90 min.',
        })
    return rxs


def _carta_dtx(contexto: dict) -> str:
    l = ['ENCAMINHAMENTO — DOR TORÁCICA', '']
    l.append(f"Motivo: {contexto['motivo']}")
    l.append('')
    l.append('Estratificação realizada neste serviço:')
    for linha in contexto.get('estratificacao', []):
        l.append(f'  • {linha}')
    l.append('')
    feitos = contexto.get('ja_realizado', [])
    if feitos:
        l.append('Já realizado neste serviço (registrar horários):')
        for f in feitos:
            l.append(f'  • {f} — às ____h____')
        l.append('')
    l.append(f"Solicito: {contexto['solicito']}")
    l.append('Segue: ECG (ORIGINAL ou foto), exames e este resumo.')
    return '\n'.join(l)


def interpretar_dor_toracica(dados: dict) -> dict:
    idade = dados.get('idade')
    try:
        idade = float(idade) if idade is not None else None
    except (TypeError, ValueError):
        idade = None
    peso = dados.get('peso_kg')

    base = {'tipo': 'dor_toracica', 'alertas_seguranca': [],
            'prescricoes_estruturadas': []}

    # ── 1. PNEUMOTÓRAX HIPERTENSIVO — mata em minutos ────────────────────────
    if dados.get('mv_abolido_unilateral') and dados.get('choque_hipotensao'):
        return {
            **base,
            'categoria': 'dtx_pneumotorax_hipertensivo',
            'diagnostico': 'PNEUMOTÓRAX HIPERTENSIVO — descompressão IMEDIATA',
            'urgencia': 'emergencia',
            'raciocinio': (
                'MV abolido unilateral + instabilidade = pneumotórax hipertensivo até prova '
                'em contrário. Diagnóstico CLÍNICO — não aguardar RX. '
                'Descompressão imediata: agulha calibrosa no 2º EIC linha hemiclavicular '
                '(ou 5º EIC linha axilar média), seguida de dreno torácico.'
            ),
            'plano_a': {'titulo': 'PLANO ÚNICO — Agir AGORA (não há plano B)',
                        'itens': ['Descompressão com agulha 14G — 2º EIC LHC',
                                  'O₂ alto fluxo', 'Dreno torácico em seguida',
                                  'Só então considerar transferência']},
            'plano_b': None,
        }

    # ── 2. DISSECÇÃO DE AORTA ────────────────────────────────────────────────
    dissecao = (dados.get('dor_lacerante_dorso') and
                (dados.get('assimetria_pulsos_pa') or dados.get('fr_has')))
    if dissecao or dados.get('assimetria_pulsos_pa'):
        ja = ['Acesso venoso + analgesia (morfina)',
              'Betabloqueador IV se disponível (alvo FC < 60, PAS 100-120)']
        r = {
            **base,
            'categoria': 'dtx_dissecao_suspeita',
            'diagnostico': 'Suspeita de DISSECÇÃO DE AORTA',
            'urgencia': 'emergencia',
            'raciocinio': (
                'Dor lacerante com irradiação para dorso '
                + ('+ assimetria de pulsos/PA entre membros ' if dados.get('assimetria_pulsos_pa') else '')
                + '→ dissecção de aorta até prova em contrário. '
                '⛔ NÃO TROMBOLISAR, NÃO ANTICOAGULAR, NÃO ANTIAGREGAR até excluir. '
                'Controle agressivo de FC/PA (anti-impulso) e angio-TC de aorta.'
            ),
            'alertas_seguranca': [
                '⛔ TROMBÓLISE/ANTICOAGULAÇÃO VETADAS — suspeita de dissecção. '
                'Se o ECG mostrar supra (dissecção pode ocluir coronária direita), '
                'a prioridade continua sendo EXCLUIR dissecção antes de reperfundir.'],
            'plano_a': {'titulo': 'PLANO A — Investigar AQUI (serviço com angio-TC)',
                        'itens': ['Angio-TC de aorta total (tórax + abdome)',
                                  'Betabloqueador IV (esmolol/metoprolol) — alvo FC < 60',
                                  'PAS alvo 100–120 mmHg (nitroprussiato APÓS betabloqueio)',
                                  'Analgesia plena com opioide',
                                  'Cirurgia vascular/cardíaca conforme Stanford A/B']},
            'plano_b': {'titulo': 'PLANO B — Encaminhar (serviço sem angio-TC/cirurgia)',
                        'itens': ['Betabloqueio + analgesia ANTES do transporte',
                                  'Transporte: USA obrigatória',
                                  'Avisar o destino: suspeita de dissecção (ativa fluxo)',
                                  'Carta abaixo — preencher horários']},
        }
        r['carta_encaminhamento'] = _carta_dtx({
            'motivo': 'Suspeita de dissecção de aorta — necessita angio-TC + cirurgia',
            'estratificacao': [
                'Dor torácica lacerante com irradiação dorsal',
                'Assimetria de pulsos/PA: ' + ('SIM' if dados.get('assimetria_pulsos_pa') else 'não testemunhada'),
                '⛔ Trombólise/anticoagulação NÃO realizadas (vetadas pela suspeita)'],
            'ja_realizado': ja,
            'solicito': 'Angio-TC de aorta + avaliação de cirurgia cardiovascular',
        })
        return r

    # ── 3. STEMI — a logística decide ────────────────────────────────────────
    if dados.get('ecg_supra_st') or dados.get('ecg_bre_novo'):
        contraind = _contraind_trombolise(dados)
        tem_cate = dados.get('tem_hemodinamica_local')
        dist = dados.get('distancia_hemodinamica_min')
        try:
            dist = float(dist) if dist not in (None, '') else None
        except (TypeError, ValueError):
            dist = None
        tem_tnk = dados.get('tem_trombolitico')

        ecg_achado = 'supra de ST' if dados.get('ecg_supra_st') else 'BRE novo (equivalente)'

        # Árvore logística
        if tem_cate:
            via = 'cate_local'
            estrategia = ('ICP PRIMÁRIA neste serviço — porta-balão < 90 min. '
                          'NÃO trombolisar (cate disponível).')
            vai_tnk = False
        elif dist is not None and dist <= 120:
            via = 'transferir_direto'
            estrategia = (f'Hemodinâmica alcançável em {dist:.0f} min (≤ 120): '
                          'TRANSFERIR DIRETO para ICP primária SEM trombolisar — '
                          'tempo total diagnóstico-balão dentro da janela (ESC/AHA).')
            vai_tnk = False
        elif tem_tnk and not contraind:
            via = 'farmaco_invasiva'
            estrategia = ((f'Hemodinâmica a {dist:.0f} min (> 120)' if dist is not None
                           else 'Hemodinâmica não alcançável em ≤ 120 min')
                          + ' → estratégia FÁRMACO-INVASIVA: trombolisar AQUI '
                            '(porta-agulha ≤ 30 min) e transferir em seguida — '
                            'cate de resgate se sem critérios de reperfusão em 60-90 min.')
            vai_tnk = True
        else:
            via = 'transferir_sem_reperfusao'
            estrategia = ('Sem cate local, sem janela de 120 min e '
                          + ('trombólise CONTRAINDICADA ('
                             + '; '.join(contraind) + ')' if contraind
                             else 'sem trombolítico disponível')
                          + ' → antiagregar + anticoagular + transferir o mais '
                            'rápido possível (USA).')
            vai_tnk = False

        alertas = list(base['alertas_seguranca'])
        if contraind and via != 'farmaco_invasiva':
            alertas.append('⛔ Contraindicação à trombólise: ' + '; '.join(contraind))

        rxs = _rx_stemi_base(peso, vai_tnk, idade)

        r = {
            **base,
            'categoria': 'dtx_stemi',
            'diagnostico': f'STEMI ({ecg_achado}) — via: {via.replace("_", " ")}',
            'urgencia': 'emergencia',
            'raciocinio': (
                f'ECG com {ecg_achado} + dor torácica = STEMI. Tempo é músculo. '
                f'{estrategia}'
            ),
            'alertas_seguranca': alertas,
            'prescricoes_estruturadas': rxs,
            'plano_a': {
                'titulo': ('PLANO A — ICP primária AQUI' if tem_cate else
                           'PLANO A — se houver hemodinâmica acessível'),
                'itens': ['MOV + monitor + desfibrilador AO LADO do paciente',
                          'AAS 300 mastigado + clopidogrel + enoxaparina (receita)',
                          'Ativar hemodinâmica — porta-balão < 90 min',
                          'NÃO esperar troponina para ativar (diagnóstico é ECG + clínica)'],
            },
            'plano_b': {
                'titulo': 'PLANO B — Reperfusão farmacológica + transferência',
                'itens': (['Tenecteplase por peso (receita) — porta-agulha ≤ 30 min'
                           if vai_tnk else
                           ('⛔ Sem trombólise: ' + ('; '.join(contraind) if contraind
                            else 'indisponível') + ' — transferir direto')] +
                          ['Critério de reperfusão: queda > 50% do supra em 60-90 min',
                           'Transporte: USA com desfibrilador — risco de arritmia de reperfusão',
                           'Carta abaixo — preencher horários']),
            },
        }
        r['carta_encaminhamento'] = _carta_dtx({
            'motivo': f'STEMI ({ecg_achado}) — necessita ICP '
                      + ('de resgate/rotina pós-trombólise' if vai_tnk else 'primária'),
            'estratificacao': [
                f'ECG: {ecg_achado} (segue ECG original/foto)',
                f'Estratégia adotada: {via.replace("_", " ")}',
                ('Contraindicações à trombólise: ' + '; '.join(contraind)) if contraind
                else 'Sem contraindicações à trombólise',
            ],
            'ja_realizado': ['AAS 300 mg VO', 'Clopidogrel VO', 'Enoxaparina SC']
                            + (['Tenecteplase ____ mg IV'] if vai_tnk else []),
            'solicito': 'ICP ' + ('pós-trombólise (resgate se sem reperfusão)' if vai_tnk
                                  else 'primária') + ' + UTI coronariana',
        })
        return r

    # ── 4-6. SCA sem supra — HEART score ─────────────────────────────────────
    heart, heart_itens, completo = _heart(dados, idade)
    instavel = dados.get('choque_hipotensao')

    if not completo:
        faltam = []
        if dados.get('historia_suspeita', '') == '': faltam.append('caracterização da história')
        if not any(dados.get(k) for k in ('ecg_normal', 'ecg_alteracao_inespecifica',
                                          'ecg_infra_st_t_neg')): faltam.append('ECG')
        if dados.get('troponina', '') == '': faltam.append('troponina')
        return {
            **base,
            'categoria': 'dtx_inespecifica',
            'diagnostico': 'Dor torácica — estratificação INCOMPLETA',
            'urgencia': 'urgente',
            'heart_itens': heart_itens,
            'raciocinio': (
                'HEART score incompleto — faltam: ' + ', '.join(faltam) + '. '
                'Dor torácica não estratificada não recebe alta. '
                'Sem troponina no serviço → o próprio HEART parcial '
                + (f'(parcial ≥ {sum(1 for i in heart_itens)} itens) ' if heart_itens else '')
                + 'já orienta: história moderada/muito suspeita ou ECG alterado → encaminhar.'
            ),
            'plano_a': {'titulo': 'PLANO A — Completar estratificação AQUI',
                        'itens': ['ECG em até 10 min da chegada (se ainda não feito)',
                                  'Troponina agora + 3h (alta sensibilidade: 0/1-2h)',
                                  'Reaplicar HEART com dados completos']},
            'plano_b': {'titulo': 'PLANO B — Sem ECG/troponina no serviço',
                        'itens': ['História suspeita ou qualquer dúvida → encaminhar para '
                                  'serviço com troponina', 'AAS 300 mg se suspeita de SCA '
                                  'sem contraindicação', 'Carta abaixo']},
        }

    if instavel or heart >= 7 or dados.get('troponina') == 'elevada_3x' \
            or dados.get('ecg_infra_st_t_neg') and dados.get('troponina') != 'normal':
        cat, urg = 'dtx_sca_alto_risco', 'emergencia'
        diag = f'SCA SEM SUPRA de ALTO RISCO — HEART {heart}/10'
        racioc = (f'HEART {heart}/10 (alto risco: MACE ~50-65% em 6 semanas)'
                  + (' + instabilidade' if instavel else '') + '. '
                  'Estratégia invasiva precoce (< 24h; imediata se instável/refratário).')
        rxs = _rx_stemi_base(peso, False, idade)  # mesmo kit sem trombolítico
        plano_a = {'titulo': 'PLANO A — Tratar AQUI (serviço com retaguarda)',
                   'itens': ['MOV + monitor', 'AAS + clopidogrel + enoxaparina (receita)',
                             'Cateterismo < 24h (imediato se instável/dor refratária)',
                             'Seriar troponina + ECG']}
        plano_b = {'titulo': 'PLANO B — Encaminhar',
                   'itens': ['AAS + clopidogrel + enoxaparina ANTES de sair',
                             'Transporte: USA com monitor',
                             'Carta abaixo — preencher horários']}
    elif heart >= 4:
        cat, urg = 'dtx_sca_intermediario', 'urgente'
        diag = f'SCA possível — risco INTERMEDIÁRIO — HEART {heart}/10'
        racioc = (f'HEART {heart}/10 (intermediário: MACE ~12-17% em 6 semanas). '
                  'Não recebe alta da primeira troponina: seriar 3h (ou 1-2h se alta '
                  'sensibilidade) + observação monitorizada.')
        rxs = [{'linha': 'Antiagregação empírica', 'medicamento': 'AAS 100 mg',
                'prescricoes': [{'quantidade': '3', 'unidade': 'comprimidos',
                                 'posologia': '300 mg VO mastigados agora'}],
                'nota': 'Empírico enquanto estratifica — suspender se causa alternativa confirmada.'}]
        plano_a = {'titulo': 'PLANO A — Observar e seriar AQUI',
                   'itens': ['Troponina 0/3h (ou 0/1-2h alta sensibilidade)',
                             'ECG seriado (repetir se dor recorrer)',
                             'Delta positivo ou ECG dinâmico → tratar como alto risco',
                             'Ambos negativos + HEART recalculado < 4 → considerar alta + teste provocativo ambulatorial']}
        plano_b = {'titulo': 'PLANO B — Sem troponina seriada no serviço',
                   'itens': ['Encaminhar para observação com troponina',
                             'AAS antes de sair', 'Carta abaixo']}
    else:
        cat, urg = 'dtx_baixo_risco', 'ambulatorio'
        diag = f'Dor torácica de BAIXO RISCO — HEART {heart}/10'
        racioc = (f'HEART {heart}/10 com troponina normal: MACE ~1,7% em 6 semanas — '
                  'seguro para alta SEM exames adicionais (validação multicêntrica). '
                  'Investigar causa alternativa (parede torácica, refluxo, ansiedade).')
        rxs = []
        plano_a = {'titulo': 'PLANO ÚNICO — Alta com segurança',
                   'itens': ['Sem indicação de internação ou teste provocativo urgente',
                             'Tratar causa provável (musculoesquelética/DRGE)',
                             'Retorno IMEDIATO se: dor em aperto > 20 min, irradiação, '
                             'sudorese, dispneia',
                             'Reavaliação ambulatorial se recorrência']}
        plano_b = None

    r = {
        **base,
        'categoria': cat,
        'diagnostico': diag,
        'urgencia': urg,
        'heart_score': heart,
        'heart_itens': heart_itens,
        'raciocinio': racioc,
        'prescricoes_estruturadas': rxs,
        'plano_a': plano_a,
        'plano_b': plano_b,
    }
    if plano_b:
        r['carta_encaminhamento'] = _carta_dtx({
            'motivo': diag,
            'estratificacao': [f'HEART {heart}/10'] + heart_itens,
            'ja_realizado': ['AAS 300 mg VO'] + (['Clopidogrel', 'Enoxaparina SC']
                                                 if cat == 'dtx_sca_alto_risco' else []),
            'solicito': ('Cateterismo < 24h + UTI coronariana' if cat == 'dtx_sca_alto_risco'
                         else 'Observação monitorizada + troponina seriada'),
        })
    return r
