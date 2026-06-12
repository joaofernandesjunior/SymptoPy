# modules/raciocinio/emergencias/engine_anafilaxia.py
# Anafilaxia e reações alérgicas agudas no PA adulto.
#
#   1. ANAFILAXIA (critérios WAO 2020) → ADRENALINA IM é a 1ª e única droga que
#      salva — coxa anterolateral, repetível a cada 5-15 min. Anti-histamínico e
#      corticoide são ADJUVANTES, nunca substitutos e nunca primeiro.
#   2. URTICÁRIA/ANGIOEDEMA SEM critério de anafilaxia → anti-histamínico, observar
#      progressão; corticoide se extenso.
#   3. ANGIOEDEMA POR IECA (bradicinina) → NÃO responde a adrenalina/anti-H1 como
#      o histaminérgico; suspender IECA, proteger via aérea, considerar icatibanto.
#
# O erro clássico é hesitar na adrenalina e começar por anti-histamínico — o
# módulo coloca a adrenalina IM como primeira linha sempre que há critério.
#
# Saída padrão emergências: Plano A (tratar aqui) / Plano B (encaminhar + carta).

# Critérios WAO 2020 — anafilaxia provável se (1) OU (2):
#  (1) início agudo com envolvimento de PELE/MUCOSA + ≥1 de: comprometimento
#      respiratório, hipotensão/sintomas de hipoperfusão, sintomas GI graves.
#  (2) hipotensão/broncoespasmo/envolvimento laríngeo após exposição a alérgeno
#      conhecido/provável (mesmo SEM lesão de pele).

def _peso(dados):
    try:
        return float(str(dados.get('peso_kg')).replace(',', '.'))
    except (TypeError, ValueError):
        return None


def _rx_adrenalina(peso):
    if peso:
        dose_ml = min(0.5, round(0.01 * peso, 2))
        pos = (f'{dose_ml} mL (0,01 mg/kg → {peso:.0f} kg) IM na COXA anterolateral; '
               f'repetir a cada 5-15 min se sem resposta')
    else:
        pos = ('0,5 mg = 0,5 mL da solução 1 mg/mL (1:1000) IM na COXA anterolateral '
               '(adulto); repetir a cada 5-15 min se sem resposta')
    return {
        'linha': '1ª LINHA — IMEDIATA (não atrasar)',
        'medicamento': 'Adrenalina 1 mg/mL (1:1000) IM',
        'prescricoes': [{'quantidade': '1', 'unidade': 'ampola', 'posologia': pos}],
        'nota': 'IM na face anterolateral da coxa (vasto lateral) — NÃO subcutânea, '
                'NÃO deltoide. Sem dose máxima absoluta na emergência: repetir é seguro. '
                '2 doses sem resposta → adrenalina IV em BIC (ambiente monitorizado).',
    }


def _rx_adjuvantes():
    return [
        {
            'linha': 'Adjuvante — broncoespasmo',
            'medicamento': 'Salbutamol spray/nebulização',
            'prescricoes': [{'quantidade': '', 'unidade': '',
                             'posologia': 'Nebulização ou 4-8 jatos com espaçador, repetir conforme necessário'}],
            'nota': 'Para o componente broncoespástico — NÃO substitui a adrenalina.',
        },
        {
            'linha': 'Adjuvante — anti-histamínico (alívio de prurido/urticária)',
            'medicamento': 'Difenidramina / Prometazina',
            'prescricoes': [{'quantidade': '', 'unidade': '',
                             'posologia': 'Difenidramina 25-50 mg IV/IM (ou prometazina 25 mg IM)'}],
            'nota': 'ADJUVANTE — só alivia pele/prurido, não trata via aérea nem choque. '
                    'Nunca como primeira/única droga.',
        },
        {
            'linha': 'Adjuvante — corticoide (prevenir bifásica)',
            'medicamento': 'Hidrocortisona / Metilprednisolona',
            'prescricoes': [{'quantidade': '', 'unidade': '',
                             'posologia': 'Hidrocortisona 200 mg IV (ou metilprednisolona 1-2 mg/kg)'}],
            'nota': 'Efeito tardio (horas) — pode reduzir reação bifásica. NÃO age na fase aguda.',
        },
    ]


def _criterio_anafilaxia(dados):
    pele = dados.get('pele_mucosa')   # urticária, prurido, angioedema, flushing
    resp = dados.get('comprometimento_respiratorio')  # dispneia, sibilo, estridor, hipoxemia
    cardio = dados.get('hipotensao_sincope')          # hipotensão, síncope, colapso
    gi = dados.get('sintomas_gi_graves')              # vômitos, cólica intensa
    alergeno = dados.get('exposicao_alergeno')

    # Critério 1: pele/mucosa + ≥1 sistema
    if pele and (resp or cardio or gi):
        return True, 'pele/mucosa + ' + ', '.join(
            s for s, ok in [('respiratório', resp), ('cardiovascular', cardio),
                            ('GI grave', gi)] if ok)
    # Critério 2: alérgeno provável + hipotensão OU broncoespasmo/laringe
    if alergeno and (resp or cardio):
        return True, 'exposição a alérgeno + ' + ('comprometimento respiratório'
                                                  if resp else 'hipotensão')
    return False, ''


def interpretar_anafilaxia(dados: dict) -> dict:
    base = {'tipo': 'anafilaxia', 'alertas_seguranca': [],
            'prescricoes_estruturadas': []}
    peso = _peso(dados)

    # ── 3. Angioedema por IECA (bradicinina) — não é histaminérgico ──────────
    if dados.get('angioedema_isolado') and dados.get('uso_ieca') and not dados.get('pele_mucosa'):
        return {
            **base,
            'categoria': 'angioedema_ieca',
            'diagnostico': 'Angioedema por IECA (mediado por bradicinina)',
            'urgencia': 'emergencia',
            'raciocinio': (
                'Angioedema (lábios/língua/glote) SEM urticária, em uso de IECA = '
                'angioedema bradicinérgico. NÃO responde bem a adrenalina/anti-H1/'
                'corticoide como o histaminérgico — mas, na dúvida ou se houver '
                'comprometimento de via aérea, dar adrenalina IM mesmo assim (risco baixo, '
                'benefício possível). O essencial é PROTEGER A VIA AÉREA precocemente — '
                'progressão para glote pode exigir IOT/cricotireoidostomia. '
                'Suspender o IECA definitivamente.'
            ),
            'alertas_seguranca': ['⚠️ Via aérea pode fechar rápido — IOT precoce, não esperar. '
                                  'Suspender IECA para sempre (contraindicado depois).'],
            'plano_a': {'titulo': 'PLANO A — Tratar AQUI (com via aérea avançada)',
                        'itens': ['Avaliar via aérea CONTINUAMENTE — IOT precoce se progressão',
                                  'Adrenalina IM se envolvimento de via aérea (risco baixo)',
                                  'Suspender IECA definitivamente',
                                  'Considerar icatibanto/C1-inibidor se disponível',
                                  'Observação prolongada — angioedema pode evoluir por horas']},
            'plano_b': {'titulo': 'PLANO B — Encaminhar',
                        'itens': ['Garantir via aérea ANTES do transporte se houver dúvida',
                                  'USA com material de via aérea difícil',
                                  'Suspender IECA', 'Carta abaixo']},
            'carta_encaminhamento': '\n'.join([
                'ENCAMINHAMENTO — ANGIOEDEMA POR IECA', '',
                'Motivo: angioedema bradicinérgico com risco de via aérea',
                '', 'Dados deste serviço:',
                '  • Angioedema sem urticária, em uso de IECA',
                '  • Via aérea: ____________________ (pérvia/comprometida)',
                '', 'Já realizado (registrar horários):',
                '  • IECA suspenso',
                '  • Adrenalina/IOT (se feito): ____ — às ____h____',
                '', 'Solicito: observação com via aérea avançada disponível',
            ]),
        }

    # ── 1. ANAFILAXIA ────────────────────────────────────────────────────────
    eh_ana, motivo = _criterio_anafilaxia(dados)
    if eh_ana:
        rxs = [_rx_adrenalina(peso)]
        if dados.get('comprometimento_respiratorio'):
            rxs.append(_rx_adjuvantes()[0])  # salbutamol
        rxs += _rx_adjuvantes()[1:]          # anti-H1 + corticoide

        alertas = ['⚠️ ADRENALINA IM É A 1ª DROGA — não atrasar por anti-histamínico/'
                   'corticoide (são adjuvantes). Hesitar mata.']
        if dados.get('uso_betabloqueador'):
            alertas.append('⚠️ Em uso de betabloqueador: adrenalina pode ter resposta '
                           'reduzida → considerar GLUCAGON 1-5 mg IV.')

        return {
            **base,
            'categoria': 'anafilaxia',
            'diagnostico': 'ANAFILAXIA (critério WAO)',
            'urgencia': 'emergencia',
            'raciocinio': (
                f'Critério de anafilaxia preenchido: {motivo}. '
                'ADRENALINA IM 0,01 mg/kg (máx 0,5 mg) na coxa anterolateral É O '
                'TRATAMENTO — imediata, repetível a cada 5-15 min. Decúbito dorsal com '
                'MMII elevados (NÃO sentar/levantar — risco de "empty ventricle"). '
                'O₂ + volume (SF 0,9% 1-2 L se hipotensão). Anti-histamínico e corticoide '
                'são ADJUVANTES e não mudam o desfecho agudo. Observar 4-6h (até 24h se '
                'grave/refratária) pela reação BIFÁSICA. Prescrever autoinjetor e '
                'encaminhar a alergista na alta.'
            ),
            'alertas_seguranca': alertas,
            'prescricoes_estruturadas': rxs,
            'plano_a': {'titulo': 'PLANO A — Tratar AQUI',
                        'itens': ['ADRENALINA IM JÁ (receita) — repetir a cada 5-15 min se preciso',
                                  'Decúbito dorsal + MMII elevados (não sentar)',
                                  'O₂ alto fluxo + monitorização',
                                  'SF 0,9% 1-2 L IV se hipotensão (choque distributivo)',
                                  'Salbutamol se broncoespasmo; anti-H1 + corticoide adjuvantes',
                                  '2 doses de adrenalina sem resposta → adrenalina IV em BIC',
                                  'Betabloqueado refratário → glucagon',
                                  'Observar 4-6h (bifásica) + autoinjetor na alta + alergista']},
            'plano_b': {'titulo': 'PLANO B — Encaminhar (após adrenalina)',
                        'itens': ['ADRENALINA IM ANTES de qualquer transporte',
                                  'Manter decúbito + O₂ + acesso venoso na ambulância',
                                  'Levar adrenalina extra para o trajeto (bifásica/recidiva)',
                                  'USA com médico', 'Carta abaixo']},
            'carta_encaminhamento': '\n'.join([
                'ENCAMINHAMENTO — ANAFILAXIA', '',
                f'Motivo: anafilaxia ({motivo})', '',
                'Já realizado (registrar horários):',
                '  • Adrenalina IM ____ mg — às ____h____ (nº de doses: ____)',
                '  • SF 0,9% ____ mL IV', '  • O₂ / adjuvantes: ____',
                '', 'Gatilho suspeito: ______________________',
                'Solicito: observação ≥ 6h por reação bifásica + alergista',
                'Segue: este resumo.',
            ]),
        }

    # ── 2. URTICÁRIA / ANGIOEDEMA SEM critério de anafilaxia ─────────────────
    if dados.get('pele_mucosa') or dados.get('angioedema_isolado'):
        extenso = dados.get('urticaria_extensa') or dados.get('angioedema_isolado')
        rxs = [{
            'linha': 'Urticária/angioedema — 1ª linha',
            'medicamento': 'Anti-histamínico H1 não sedante',
            'prescricoes': [{'quantidade': '', 'unidade': '',
                             'posologia': 'Loratadina/cetirizina 10 mg VO 1×/dia '
                                          '(ou difenidramina 25-50 mg se precisar parenteral)'}],
            'nota': 'Pode dobrar a dose do anti-H1 não sedante em urticária refratária.',
        }]
        if extenso:
            rxs.append({
                'linha': 'Se extenso/angioedema',
                'medicamento': 'Prednisona',
                'prescricoes': [{'quantidade': '', 'unidade': '',
                                 'posologia': 'Prednisona 40 mg VO/dia por 3-5 dias'}],
                'nota': 'Curso curto para urticária extensa ou angioedema sem critério de anafilaxia.',
            })
        return {
            **base,
            'categoria': 'urticaria_angioedema',
            'diagnostico': 'Urticária/angioedema SEM critério de anafilaxia',
            'urgencia': 'ambulatorio',
            'raciocinio': (
                'Reação cutânea (urticária/angioedema) SEM comprometimento respiratório, '
                'cardiovascular ou GI grave → não preenche critério de anafilaxia. '
                'Anti-histamínico H1 é a 1ª linha; corticoide curto se extenso. '
                'ATENÇÃO: orientar retorno IMEDIATO se surgir dispneia, aperto na garganta, '
                'rouquidão, tontura ou vômitos — pode evoluir para anafilaxia. '
                'Identificar e afastar o gatilho.'
            ),
            'alertas_seguranca': ['⚠️ Reavaliar se progressão — surgimento de sintoma '
                                  'respiratório/cardiovascular reclassifica como ANAFILAXIA '
                                  '(adrenalina IM).'],
            'prescricoes_estruturadas': rxs,
            'plano_a': {'titulo': 'PLANO ÚNICO — Tratar e orientar',
                        'itens': ['Anti-histamínico H1 (receita)',
                                  'Corticoide curto se extenso/angioedema',
                                  'Afastar o gatilho suspeito',
                                  'Observar progressão antes da alta',
                                  'Retorno IMEDIATO se dispneia/disfonia/tontura/vômito']},
            'plano_b': None,
        }

    # ── Sem dados suficientes ────────────────────────────────────────────────
    return {
        **base,
        'categoria': 'reacao_alergica_indefinida',
        'diagnostico': 'Reação alérgica — caracterizar sistemas envolvidos',
        'urgencia': 'urgente',
        'raciocinio': 'Caracterizar envolvimento de pele/mucosa, respiratório, '
                      'cardiovascular e GI para aplicar critério de anafilaxia (WAO). '
                      'Na dúvida com sintoma respiratório/cardiovascular após alérgeno: '
                      'tratar como anafilaxia (adrenalina IM).',
        'plano_a': {'titulo': 'PLANO ÚNICO', 'itens': ['Caracterizar sistemas envolvidos',
                                                       'Limiar BAIXO para adrenalina IM']},
        'plano_b': None,
    }
