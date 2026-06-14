# modules/raciocinio/emergencias/engine_dispneia.py
# Dispneia aguda no adulto — o "roteador clínico" do PA/UPA.
#
# A dispneia não é um diagnóstico: é um sintoma com ~8 causas que matam de
# formas diferentes. Este engine TRIA o padrão e:
#   - resolve as causas que ele cobre (IC/EAP, pneumonia, pneumotórax, derrame,
#     anemia grave, hiperventilação),
#   - e CRUZA para os módulos dedicados quando o padrão aponta para eles
#     (asma, DPOC, TEP — que têm lógica própria de score/Bayes).
#
# Passo 0: falência respiratória iminente (independe da causa) → estabilizar.
# Passo 1: padrão dominante decide a etiologia.
#
# CURB-65 embutido para pneumonia (decisão ambulatório × internação).
# Saída padrão emergências: Plano A (tratar aqui) / Plano B (encaminhar + carta).

def _num(v):
    try:
        return float(str(v).replace(',', '.'))
    except (TypeError, ValueError):
        return None


def _curb65(dados, idade):
    """CURB-65: confusão, ureia > 50, FR ≥ 30, PAS < 90 ou PAD ≤ 60, idade ≥ 65."""
    score, itens = 0, []
    if dados.get('confusao_mental'):
        score += 1; itens.append('Confusão')
    ureia = _num(dados.get('ureia'))
    if ureia is not None and ureia > 50:
        score += 1; itens.append(f'Ureia {ureia:.0f} > 50')
    fr = _num(dados.get('fr'))
    if fr is not None and fr >= 30:
        score += 1; itens.append(f'FR {fr:.0f} ≥ 30')
    pas = _num(dados.get('pas')); pad = _num(dados.get('pad'))
    if (pas is not None and pas < 90) or (pad is not None and pad <= 60):
        score += 1; itens.append('PA baixa')
    if idade is not None and idade >= 65:
        score += 1; itens.append(f'Idade {idade:.0f} ≥ 65')
    return score, itens


def _carta(motivo, dados_serv, ja_feito, solicito):
    l = ['ENCAMINHAMENTO — DISPNEIA AGUDA', '', f'Motivo: {motivo}', '']
    l.append('Dados deste serviço:')
    for d in dados_serv:
        l.append(f'  • {d}')
    l.append('')
    if ja_feito:
        l.append('Já realizado (registrar horários):')
        for f in ja_feito:
            l.append(f'  • {f} — às ____h____')
        l.append('')
    l.append(f'Solicito: {solicito}')
    l.append('Segue: ECG, Rx/exames disponíveis e este resumo.')
    return '\n'.join(l)


def interpretar_dispneia(dados: dict) -> dict:
    idade = _num(dados.get('idade'))
    spo2  = _num(dados.get('spo2') or dados.get('sato2'))
    fr    = _num(dados.get('fr'))

    base = {'tipo': 'dispneia', 'alertas_seguranca': [],
            'prescricoes_estruturadas': []}

    # ── PASSO 0: falência respiratória iminente ──────────────────────────────
    falencia = (dados.get('rebaixamento') or dados.get('torax_silencioso')
                or dados.get('exaustao_respiratoria') or dados.get('cianose')
                or (spo2 is not None and spo2 < 85))
    if falencia:
        base['alertas_seguranca'].append(
            '🔴 FALÊNCIA RESPIRATÓRIA IMINENTE — O₂ alto fluxo já; preparar via aérea '
            '(VNI ou IOT). Estabilizar ANTES de investigar a causa.')

    # ── PASSO 1: identificar o padrão dominante ──────────────────────────────

    # (A) PNEUMOTÓRAX — MV abolido unilateral + timpanismo / trauma
    if dados.get('mv_abolido_unilateral') and (dados.get('timpanismo') or
                                               dados.get('trauma_toracico') or
                                               dados.get('inicio_subito')):
        hipertensivo = dados.get('choque_hipotensao') or dados.get('desvio_traqueia')
        r = {
            **base,
            'categoria': 'disp_pneumotorax',
            'diagnostico': ('PNEUMOTÓRAX HIPERTENSIVO' if hipertensivo
                            else 'Pneumotórax (suspeita)'),
            'urgencia': 'emergencia',
            'raciocinio': (
                'MV abolido unilateral + '
                + ('timpanismo/' if dados.get('timpanismo') else '')
                + ('trauma/' if dados.get('trauma_toracico') else '')
                + 'início súbito → pneumotórax. '
                + ('Instabilidade/desvio de traqueia = HIPERTENSIVO: descompressão '
                   'IMEDIATA por agulha (2º EIC LHC ou 5º EIC LAM), NÃO esperar Rx.'
                   if hipertensivo else
                   'Estável: confirmar com Rx/USG; drenar se > 2-3 cm ou sintomático.')
            ),
            'plano_a': {'titulo': 'PLANO A — Tratar AQUI',
                        'itens': (['DESCOMPRESSÃO POR AGULHA JÁ (hipertensivo)']
                                  if hipertensivo else
                                  ['O₂ + Rx/USG tórax confirmatório']) +
                                 ['Dreno torácico em selo d\'água',
                                  'O₂ suplementar (acelera reabsorção)']},
            'plano_b': {'titulo': 'PLANO B — Encaminhar',
                        'itens': (['Descompressão por agulha ANTES de transferir (hipertensivo)']
                                  if hipertensivo else []) +
                                 ['O₂ + USA', 'Serviço com cirurgia/drenagem torácica']},
        }
        if not hipertensivo:
            r['carta_encaminhamento'] = _carta(
                'Pneumotórax — necessita drenagem',
                ['MV abolido unilateral', f'SpO₂ {spo2:.0f}%' if spo2 else 'SpO₂ ND'],
                ['O₂ suplementar'], 'Rx tórax + drenagem torácica')
        return r

    # (B) IC DESCOMPENSADA / EAP — padrão congestivo
    sinais_ic = sum(bool(dados.get(k)) for k in (
        'ortopneia', 'dpn', 'edema_bilateral_mmii', 'turgencia_jugular',
        'crepitantes_bibasais', 'b3_ritmo_galope'))
    if sinais_ic >= 2 or dados.get('eap_franco'):
        eap = dados.get('eap_franco') or (spo2 is not None and spo2 < 90 and sinais_ic >= 2)
        rxs = [
            {'linha': 'Congestão — diurético', 'medicamento': 'Furosemida',
             'prescricoes': [{'quantidade': '', 'unidade': '',
                              'posologia': '0,5–1 mg/kg IV (40 mg se virgem de diurético; '
                                           'dobrar a dose VO habitual se já usa)'}],
             'nota': 'Reavaliar diurese; repetir conforme resposta.'},
        ]
        if eap:
            rxs.insert(0, {
                'linha': 'EAP — venodilatador (1ª linha junto com VNI)',
                'medicamento': 'Nitroglicerina', 'prescricoes': [{'quantidade': '', 'unidade': '',
                    'posologia': 'NTG IV 10–20 µg/min titulável (ou isossorbida 5 mg SL '
                                 'repetível se sem bomba), se PAS > 110'}],
                'nota': '⛔ Evitar se PAS < 90 ou suspeita de infarto de VD.'})
        r = {
            **base,
            'categoria': 'disp_ic_eap',
            'diagnostico': ('EDEMA AGUDO DE PULMÃO (IC descompensada)' if eap
                            else 'Insuficiência cardíaca descompensada'),
            'urgencia': 'emergencia' if eap else 'urgente',
            'raciocinio': (
                f'Padrão congestivo ({sinais_ic} sinais: ortopneia/DPN/edema/TJ/'
                f'crepitantes/B3) → IC descompensada. '
                + ('Hipoxemia + congestão difusa = EAP: VNI (CPAP/BiPAP) PRECOCE reduz '
                   'IOT, nitrato venodilatador ↓ pré-carga, furosemida. ' if eap else
                   'Diurético de alça + investigar fator descompensante (má adesão, '
                   'transgressão de sal, FA, isquemia, infecção). ')
                + 'BNP/NT-proBNP e eco confirmam; Rx mostra congestão.'
            ),
            'prescricoes_estruturadas': rxs,
            'plano_a': {'titulo': 'PLANO A — Tratar AQUI',
                        'itens': (['VNI (CPAP/BiPAP) precoce', 'Nitroglicerina IV se PAS > 110']
                                  if eap else []) +
                                 ['Furosemida IV (receita)', 'O₂ alvo SpO₂ ≥ 94%',
                                  'Sentar o paciente (reduz retorno venoso)',
                                  'ECG + troponina (isquemia como gatilho) + Rx + BNP',
                                  'Investigar e tratar o fator descompensante']},
            'plano_b': {'titulo': 'PLANO B — Encaminhar',
                        'itens': ['Furosemida IV + O₂ (± nitrato SL) antes de sair',
                                  'VNI durante transporte se disponível — USA',
                                  'Carta abaixo']},
        }
        r['carta_encaminhamento'] = _carta(
            ('EAP/IC descompensada' if eap else 'IC descompensada'),
            [f'SpO₂ {spo2:.0f}%' if spo2 else 'SpO₂ ND',
             f'{sinais_ic} sinais congestivos', 'Fator descompensante: ____________'],
            ['Furosemida ____ mg IV', 'O₂ / VNI', 'Nitrato (se EAP)'],
            'Avaliação cardiológica + internação + eco')
        return r

    # (C) PNEUMONIA — febre + tosse + foco pulmonar
    if (dados.get('febre') and (dados.get('tosse_produtiva') or dados.get('crepitantes_localizados'))
            or dados.get('consolidacao_rx')):
        score, itens = _curb65(dados, idade)
        if score <= 1:
            destino = 'AMBULATORIAL (CURB-65 0-1)'
            urg = 'ambulatorio'
        elif score == 2:
            destino = 'considerar internação curta / observação (CURB-65 2)'
            urg = 'urgente'
        else:
            destino = 'INTERNAÇÃO (CURB-65 ≥ 3; ≥ 4-5 avaliar UTI)'
            urg = 'emergencia'
        rxs = []
        if score <= 1:
            rxs.append({'linha': 'PAC ambulatorial — sem comorbidade',
                'medicamento': 'Amoxicilina', 'prescricoes': [{'quantidade': '', 'unidade': '',
                    'posologia': 'Amoxicilina 1 g VO 8/8h × 5-7 dias'}],
                'nota': 'Com comorbidade/uso recente de ATB: amoxicilina-clavulanato '
                        'OU + macrolídeo (azitromicina) para atípicos.'})
        else:
            rxs.append({'linha': 'PAC com internação — ATB precoce',
                'medicamento': 'Ceftriaxona + azitromicina', 'prescricoes': [{'quantidade': '', 'unidade': '',
                    'posologia': 'Ceftriaxona 1 g IV/dia + azitromicina 500 mg IV/dia'}],
                'nota': 'Primeira dose o quanto antes. Coletar culturas se possível, sem atrasar ATB.'})
        r = {
            **base,
            'categoria': 'disp_pneumonia',
            'diagnostico': f'Pneumonia adquirida na comunidade — CURB-65 {score}/5',
            'urgencia': urg,
            'raciocinio': (
                f'Febre + tosse/crepitantes ' + ('+ consolidação ' if dados.get('consolidacao_rx') else '')
                + f'→ PAC. CURB-65 = {score}/5'
                + (f' ({", ".join(itens)})' if itens else '') + f' → {destino}. '
                'Rx de tórax confirma; ATB precoce melhora desfecho. '
                'Lactato + culturas se sinais de sepse.'
            ),
            'prescricoes_estruturadas': rxs,
            'plano_a': {'titulo': 'PLANO A — Tratar AQUI',
                        'itens': ['Rx de tórax', 'ATB conforme CURB-65 (receita) — precoce',
                                  'O₂ alvo SpO₂ ≥ 94% (≥ 90% se DPOC)',
                                  'Hidratação + antitérmico',
                                  'Reavaliar sepse (NEWS2/lactato) se sinais sistêmicos',
                                  f'Destino: {destino}']},
            'plano_b': ({'titulo': 'PLANO B — Encaminhar (CURB-65 ≥ 2 sem retaguarda)',
                         'itens': ['1ª dose de ATB ANTES de transferir',
                                   'O₂ + acesso venoso', 'USA se instável', 'Carta abaixo']}
                        if score >= 2 else None),
        }
        if score >= 2:
            r['carta_encaminhamento'] = _carta(
                f'PAC CURB-65 {score}/5 — necessita internação',
                [f'CURB-65 {score}: {", ".join(itens)}', f'SpO₂ {spo2:.0f}%' if spo2 else 'SpO₂ ND'],
                ['1ª dose de ATB', 'O₂'], 'Internação + ATB IV + suporte')
        return r

    # (D) OBSTRUTIVO — sibilos → asma/DPOC (módulos dedicados)
    if dados.get('sibilos') or dados.get('chiado'):
        provavel = ('DPOC' if (dados.get('tabagista') or dados.get('dpoc_conhecida')
                               or (idade and idade >= 50))
                    else 'asma' if dados.get('asma_conhecida') else 'asma/DPOC')
        prox = 'dpoc' if provavel == 'DPOC' else 'asma'
        return {
            **base,
            'categoria': 'disp_obstrutivo',
            'diagnostico': f'Dispneia obstrutiva (sibilância) — provável {provavel}',
            'urgencia': 'urgente',
            'proximo_modulo': prox,
            'raciocinio': (
                'Sibilância difusa = padrão obstrutivo. '
                f'Perfil sugere {provavel}. Broncodilatador é a base imediata '
                '(salbutamol + ipratrópio NEB) + corticoide sistêmico se moderada-grave. '
                '➡️ Usar o módulo dedicado (Asma ou DPOC) para gravidade GINA/GOLD, '
                'critérios de Anthonisen (ATB na DPOC) e ajuste de manutenção.'
            ),
            'prescricoes_estruturadas': [
                {'linha': 'Broncodilatação — imediata', 'medicamento': 'Salbutamol + ipratrópio NEB',
                 'prescricoes': [{'quantidade': '', 'unidade': '',
                                  'posologia': 'Salbutamol 2,5-5 mg + ipratrópio 0,5 mg NEB, '
                                               'repetir a cada 20 min até 3×'}],
                 'nota': 'Corticoide sistêmico (prednisona 40 mg VO ou hidrocortisona IV) '
                         'se moderada-grave.'}],
            'plano_a': {'titulo': 'PLANO A — Iniciar e classificar',
                        'itens': ['Salbutamol + ipratrópio NEB (receita)',
                                  'Corticoide sistêmico se moderada-grave',
                                  'O₂ alvo 93-95% (88-92% se DPOC)',
                                  '➡️ Abrir módulo ASMA ou DPOC para gravidade e manutenção']},
            'plano_b': {'titulo': 'PLANO B — Encaminhar (crise grave/refratária)',
                        'itens': ['NEB contínua + corticoide + O₂ antes de sair',
                                  'USA se exaustão/silêncio torácico']},
        }

    # (E) TEP — súbita, pleurítica, pulmão "limpo", fator de risco
    if (dados.get('inicio_subito') and (dados.get('dor_pleuritica') or dados.get('hemoptise')
                                        or dados.get('fator_risco_tev'))
            and not dados.get('sibilos')):
        return {
            **base,
            'categoria': 'disp_suspeita_tep',
            'diagnostico': 'Dispneia súbita — suspeita de TEP',
            'urgencia': 'urgente',
            'proximo_modulo': 'tep',
            'raciocinio': (
                'Dispneia súbita + '
                + ('dor pleurítica/' if dados.get('dor_pleuritica') else '')
                + ('hemoptise/' if dados.get('hemoptise') else '')
                + ('fator de risco para TEV ' if dados.get('fator_risco_tev') else '')
                + 'com ausculta pouco alterada → TEP no topo da lista. '
                '➡️ Usar o módulo TEP (Wells + PERC + D-dímero ajustado + probabilidade '
                'pós-teste bayesiana) para decidir angio-TC × anticoagulação empírica.'
            ),
            'plano_a': {'titulo': 'PLANO A — Estratificar', 'itens': [
                'O₂ + acesso venoso',
                '➡️ Abrir módulo TEP para Wells/PERC/Bayes e decisão de imagem/anticoagulação']},
            'plano_b': {'titulo': 'PLANO B — Encaminhar (alta probabilidade, sem angio-TC)',
                        'itens': ['Anticoagulação empírica se alta probabilidade e sem sangramento',
                                  'O₂ + USA', 'Ver carta no módulo TEP']},
        }

    # (F) DERRAME PLEURAL — MV abolido + macicez
    if dados.get('mv_abolido_unilateral') and dados.get('macicez'):
        return {
            **base,
            'categoria': 'disp_derrame_pleural',
            'diagnostico': 'Derrame pleural (suspeita)',
            'urgencia': 'urgente',
            'raciocinio': (
                'MV abolido unilateral + macicez à percussão + FTV reduzido → derrame '
                'pleural. Rx/USG confirma e quantifica. Toracocentese diagnóstica '
                '(critérios de Light) ± de alívio se volumoso/sintomático. '
                'Investigar causa (IC, pneumonia/empiema, neoplasia, TB).'
            ),
            'plano_a': {'titulo': 'PLANO A — Investigar AQUI',
                        'itens': ['Rx/USG de tórax', 'O₂ se hipoxemia',
                                  'Toracocentese diagnóstica (Light) ± alívio',
                                  'Investigar etiologia']},
            'plano_b': {'titulo': 'PLANO B — Encaminhar',
                        'itens': ['O₂ + analgesia', 'Serviço com toracocentese/USG',
                                  'Carta abaixo']},
            'carta_encaminhamento': _carta(
                'Derrame pleural a esclarecer',
                ['MV abolido + macicez unilateral', f'SpO₂ {spo2:.0f}%' if spo2 else 'SpO₂ ND'],
                ['O₂ (se necessário)'], 'Rx/USG + toracocentese + investigação etiológica'),
        }

    # (G) ANEMIA grave — palidez / Hb baixa
    hb = _num(dados.get('hb'))
    if (hb is not None and hb < 7) or (dados.get('palidez') and dados.get('sem_foco_cardiopulmonar')):
        return {
            **base,
            'categoria': 'disp_anemia',
            'diagnostico': f'Dispneia por anemia'
                           + (f' grave (Hb {hb:.1f})' if hb is not None else ''),
            'urgencia': 'urgente',
            'proximo_modulo': 'anemia',
            'raciocinio': (
                'Dispneia + palidez/Hb baixa sem foco cardiopulmonar → anemia como causa '
                '(↓ transporte de O₂). '
                + ('Hb < 7 (ou < 8 com cardiopatia/sintoma) é gatilho de transfusão. '
                   if hb is not None and hb < 7 else '')
                + '➡️ Usar o módulo ANEMIA para classificar (VCM/RDW) e investigar a causa; '
                'buscar sangramento ativo.'
            ),
            'plano_a': {'titulo': 'PLANO A — Tratar AQUI',
                        'itens': ['Hemograma + reticulócitos + ferro/ferritina',
                                  'Transfusão se Hb < 7 (ou < 8 com cardiopatia/instável)',
                                  'Procurar sangramento ativo (toque retal, queixas GI)',
                                  '➡️ Abrir módulo ANEMIA para classificação/causa']},
            'plano_b': {'titulo': 'PLANO B — Encaminhar (anemia grave/sangramento)',
                        'itens': ['Acesso calibroso + cristaloide se instável',
                                  'Serviço com banco de sangue', 'Carta abaixo']},
            'carta_encaminhamento': _carta(
                'Anemia sintomática' + (f' (Hb {hb:.1f})' if hb is not None else ''),
                [f'Hb {hb:.1f}' if hb is not None else 'Hb não dosada',
                 'Sangramento ativo: ____________'],
                ['Acesso venoso ± cristaloide'], 'Transfusão + investigação + banco de sangue'),
        }

    # (H) HIPERVENTILAÇÃO / ANSIEDADE — diagnóstico de EXCLUSÃO
    if (dados.get('parestesias_periorais') or dados.get('contexto_ansiedade')) \
            and (spo2 is None or spo2 >= 96) and not dados.get('febre'):
        return {
            **base,
            'categoria': 'disp_hiperventilacao',
            'diagnostico': 'Hiperventilação / dispneia ansiosa (diagnóstico de exclusão)',
            'urgencia': 'ambulatorio',
            'raciocinio': (
                'Dispneia + parestesias periorais/contexto de ansiedade, com SpO₂ normal, '
                'sem febre e sem achados cardiopulmonares → síndrome de hiperventilação. '
                '⚠️ É diagnóstico de EXCLUSÃO: SpO₂ normal NÃO descarta TEP — só rotular '
                'depois de afastar causas orgânicas. Acolhimento + reeducação respiratória; '
                'NÃO usar saco plástico (risco de hipóxia).'
            ),
            'alertas_seguranca': ['⚠️ Exclusão: reavaliar se SpO₂ cair, surgir febre, dor '
                                  'torácica ou taquicardia desproporcional → investigar causa orgânica.'],
            'plano_a': {'titulo': 'PLANO ÚNICO — Acolher e reavaliar',
                        'itens': ['Ambiente calmo + reeducação respiratória (respiração diafragmática)',
                                  'Confirmar SpO₂ normal e ausência de achados orgânicos',
                                  'NÃO usar saco plástico',
                                  'Abordar ansiedade/pânico de base no seguimento',
                                  'Retorno se dispneia recorrente ou sinal de alarme']},
            'plano_b': None,
        }

    # ── Sem padrão dominante — dispneia a esclarecer ─────────────────────────
    return {
        **base,
        'categoria': 'disp_indefinida',
        'diagnostico': 'Dispneia aguda a esclarecer',
        'urgencia': 'urgente',
        'raciocinio': (
            'Sem padrão dominante identificado. Trio mínimo de UPA: SpO₂ + ECG + '
            'Rx de tórax orienta a maioria. Reaplicar com ausculta/achados completos. '
            'Limiar BAIXO para considerar TEP (pode cursar com exame normal) e SCA '
            '(dispneia pode ser equivalente anginoso, sobretudo em idoso/diabético).'
        ),
        'plano_a': {'titulo': 'PLANO ÚNICO — Investigação básica',
                    'itens': ['SpO₂ + O₂ se < 94%', 'ECG (equivalente anginoso?)',
                              'Rx de tórax', 'Hemograma + função renal ± BNP/D-dímero conforme suspeita',
                              'Reavaliar padrão (congestivo/obstrutivo/infeccioso/embólico)']},
        'plano_b': None,
    }
