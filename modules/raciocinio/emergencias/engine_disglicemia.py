# modules/raciocinio/emergencias/engine_disglicemia.py
# Disglicemia no PA adulto — hipoglicemia, CAD e EHH.
#
#   1. HIPOGLICEMIA (glicemia < 70, sintomática < 54) — corrigir SEMPRE primeiro,
#      antes de qualquer outra coisa. Consciente → VO; rebaixado → glicose IV
#      (ou glucagon IM se sem acesso). Tríade de Whipple.
#   2. CAD — glicemia > 250 + acidose (pH < 7,3 / HCO3 < 18) + cetose.
#      Pilares: VOLUME primeiro, POTÁSSIO antes da insulina, insulina em BIC,
#      NÃO usar bicarbonato de rotina, procurar o gatilho (infecção/má adesão).
#   3. EHH — glicemia > 600 + osmolaridade > 320 + SEM acidose significativa.
#      Desidratação ainda mais grave; reposição volêmica é o carro-chefe.
#   4. HIPERGLICEMIA SIMPLES — alta sem acidose/hiperosmolaridade → ajuste + alta.
#
# Saída padrão emergências: Plano A (tratar aqui) / Plano B (encaminhar + carta).

def _num(v):
    try:
        return float(str(v).replace(',', '.'))
    except (TypeError, ValueError):
        return None


def _rx_glicose_vo():
    return {
        'linha': 'Hipoglicemia — paciente CONSCIENTE',
        'medicamento': 'Carboidrato de absorção rápida VO',
        'prescricoes': [{'quantidade': '15–20 g', 'unidade': 'glicose',
                         'posologia': '15 g VO (3 sachês de glicose, ou 150 mL de suco/'
                                      'refrigerante comum, ou 1 colher de sopa de açúcar '
                                      'em água); remedir em 15 min — repetir se < 70'}],
        'nota': 'Regra dos 15: 15 g, remedir em 15 min. Após normalizar, oferecer '
                'refeição/lanche com carboidrato complexo para evitar recidiva.',
    }


def _rx_glicose_iv():
    return {
        'linha': 'Hipoglicemia — paciente REBAIXADO / sem VO segura',
        'medicamento': 'Glicose hipertônica 50%',
        'prescricoes': [{'quantidade': '40–60 mL', 'unidade': 'glicose 50% IV',
                         'posologia': '4 ampolas de 10 mL (40 mL) IV em bolus; '
                                      'remedir em 15 min e repetir se necessário'}],
        'nota': 'Sem acesso venoso: Glucagon 1 mg IM/SC. Se etilista/desnutrido: '
                'Tiamina 100 mg IV ANTES da glicose (prevenir Wernicke). '
                'Manter SG 10% em infusão se hipoglicemia por sulfonilureia (recidiva).',
    }


def _carta(motivo, estratificacao, ja_feito, solicito):
    l = ['ENCAMINHAMENTO — EMERGÊNCIA METABÓLICA', '', f'Motivo: {motivo}', '']
    l.append('Dados deste serviço:')
    for e in estratificacao:
        l.append(f'  • {e}')
    l.append('')
    if ja_feito:
        l.append('Já realizado (registrar horários):')
        for f in ja_feito:
            l.append(f'  • {f} — às ____h____')
        l.append('')
    l.append(f'Solicito: {solicito}')
    l.append('Segue: glicemias seriadas, exames e este resumo.')
    return '\n'.join(l)


def interpretar_disglicemia(dados: dict) -> dict:
    gli = _num(dados.get('glicemia'))
    ph  = _num(dados.get('ph'))
    hco3 = _num(dados.get('hco3'))
    osmol = _num(dados.get('osmolaridade'))
    cetonas = dados.get('cetonemia_cetonuria')
    rebaixado = dados.get('rebaixamento') or dados.get('glasgow_baixo')

    base = {'tipo': 'disglicemia', 'glicemia': gli,
            'alertas_seguranca': [], 'prescricoes_estruturadas': []}

    # ── 1. HIPOGLICEMIA — corrigir antes de tudo ─────────────────────────────
    if gli is not None and gli < 70:
        sintomatica = gli < 54 or dados.get('sintomas_neuroglicopenicos') or rebaixado
        rx = _rx_glicose_iv() if rebaixado else _rx_glicose_vo()
        alertas = []
        if dados.get('uso_sulfonilureia'):
            alertas.append('⚠️ Hipoglicemia por SULFONILUREIA (glibenclamida): risco de '
                           'RECIDIVA por horas — observação prolongada + SG 10% contínuo; '
                           'considerar octreotida. NÃO dar alta precoce.')
        if dados.get('etilista_desnutrido'):
            alertas.append('⚠️ Etilista/desnutrido: TIAMINA 100 mg IV ANTES da glicose '
                           '(prevenir encefalopatia de Wernicke).')
        return {
            **base,
            'categoria': 'hipoglicemia',
            'diagnostico': f'HIPOGLICEMIA ({gli:.0f} mg/dL)'
                           + (' sintomática/grave' if sintomatica else ''),
            'urgencia': 'emergencia' if rebaixado else 'urgente',
            'raciocinio': (
                f'Glicemia {gli:.0f} mg/dL (< 70). Tríade de Whipple: sintomas + glicemia '
                f'baixa + melhora com correção. CORRIGIR JÁ — a hipoglicemia mata mais '
                f'rápido que a hiperglicemia. '
                + ('Paciente rebaixado → glicose IV. ' if rebaixado
                   else 'Consciente, deglutição segura → VO (regra dos 15). ')
                + 'Sempre buscar a causa: dose excessiva, pulou refeição, '
                'sulfonilureia, DRC, sepse, etilismo.'
            ),
            'alertas_seguranca': alertas,
            'prescricoes_estruturadas': [rx],
            'plano_a': {'titulo': 'PLANO ÚNICO — Corrigir e observar AQUI',
                        'itens': [('Glicose 50% IV (receita) — remedir em 15 min'
                                   if rebaixado else
                                   'Carboidrato VO (receita) — regra dos 15'),
                                  'Remedir glicemia capilar a cada 15 min até > 70',
                                  'Após normalizar: refeição com carboidrato complexo',
                                  'Ajustar dose de insulina/hipoglicemiante que causou',
                                  'Sulfonilureia → observar ≥ 24h (recidiva)']},
            'plano_b': None,
        }

    # ── Sem glicemia informada → não dá pra estratificar ─────────────────────
    if gli is None:
        return {
            **base,
            'categoria': 'disglicemia_sem_dado',
            'diagnostico': 'Disglicemia — glicemia capilar não informada',
            'urgencia': 'urgente',
            'raciocinio': 'Glicemia capilar é obrigatória e imediata em qualquer suspeita '
                          'de disglicemia ou rebaixamento. Aferir antes de prosseguir.',
            'plano_a': {'titulo': 'PLANO ÚNICO', 'itens': ['Glicemia capilar AGORA']},
            'plano_b': None,
        }

    # ── 2. CAD — hiperglicemia + acidose + cetose ────────────────────────────
    acidose = (ph is not None and ph < 7.30) or (hco3 is not None and hco3 < 18)
    cad = gli > 250 and (acidose or cetonas)
    ehh = gli > 600 and (osmol is not None and osmol > 320) and not acidose

    if cad:
        grave = (ph is not None and ph < 7.0) or rebaixado
        k = _num(dados.get('potassio'))
        alerta_k = []
        if k is not None and k < 3.3:
            alerta_k.append('⛔ POTÁSSIO < 3,3 — NÃO iniciar insulina até repor K '
                            '(insulina joga K para dentro da célula → arritmia fatal). '
                            'Repor KCl primeiro.')
        elif k is not None and k > 5.3:
            alerta_k.append('K > 5,3 — não repor potássio agora; iniciar insulina e '
                            'monitorar (cai rápido).')
        return {
            **base,
            'categoria': 'cad',
            'diagnostico': f'CETOACIDOSE DIABÉTICA (glicemia {gli:.0f}'
                           + (f', pH {ph}' if ph else '') + ')'
                           + (' — GRAVE' if grave else ''),
            'urgencia': 'emergencia',
            'raciocinio': (
                f'Glicemia {gli:.0f} + ' + ('acidose ' if acidose else '')
                + ('cetose ' if cetonas else '') + '= CAD. '
                'Ordem dos pilares importa: (1) VOLUME — SF 0,9% 15-20 mL/kg na 1ª hora; '
                '(2) POTÁSSIO antes/junto da insulina (corpo tem déficit mesmo com K '
                'sérico normal); (3) INSULINA regular 0,1 U/kg/h em BIC (só após K ≥ 3,3); '
                '(4) repor glicose (SG 5%) quando glicemia ~200 para manter insulina até '
                'fechar o ânion-gap. Bicarbonato NÃO de rotina (só pH < 6,9). '
                'SEMPRE caçar o gatilho: infecção, má adesão, IAM, primodescompensação.'
            ),
            'alertas_seguranca': alerta_k,
            'plano_a': {'titulo': 'PLANO A — Tratar AQUI (com bomba + eletrólitos seriados)',
                        'itens': ['SF 0,9% 15-20 mL/kg IV na 1ª hora (1-1,5 L)',
                                  'Potássio: repor se < 5,3 (e SEMPRE antes da insulina se < 3,3)',
                                  'Insulina regular 0,1 U/kg/h em BIC após K ≥ 3,3 '
                                  '(considerar SEM bolus)',
                                  'SG 5% quando glicemia ~200-250 (manter insulina até gap fechar)',
                                  'Eletrólitos + gasometria + cetonas a cada 2-4h',
                                  'Investigar e tratar o GATILHO',
                                  'Bicarbonato só se pH < 6,9']},
            'plano_b': {'titulo': 'PLANO B — Encaminhar (sem UTI/bomba/laboratório)',
                        'itens': ['INICIAR SF 0,9% 1 L IV antes/durante o transporte '
                                  '(volume é o que mais salva)',
                                  'NÃO dar insulina sem poder dosar potássio',
                                  'Glicemia capilar seriada na ambulância',
                                  'USA com médico — risco de arritmia/edema cerebral',
                                  'Carta abaixo com gatilho provável']},
            'carta_encaminhamento': _carta(
                f'Cetoacidose diabética (glicemia {gli:.0f}'
                + (f', pH {ph}' if ph else '') + ')'
                + (' GRAVE' if grave else ''),
                [f'Glicemia: {gli:.0f} mg/dL',
                 f'pH: {ph if ph else "não dosado"} | HCO3: {hco3 if hco3 else "ND"}',
                 f'Potássio: {k if k is not None else "não dosado"}',
                 'Gatilho investigado: ______________________'],
                ['SF 0,9% ____ mL IV', 'Potássio (se reposto): ____'],
                'UTI + insulinoterapia em BIC + reposição eletrolítica guiada'),
        }

    # ── 3. EHH — hiperglicemia extrema + hiperosmolar SEM acidose ────────────
    if ehh or (gli > 600 and rebaixado and not acidose):
        return {
            **base,
            'categoria': 'ehh',
            'diagnostico': f'ESTADO HIPERGLICÊMICO HIPEROSMOLAR (glicemia {gli:.0f}'
                           + (f', osmol {osmol:.0f}' if osmol else '') + ')',
            'urgencia': 'emergencia',
            'raciocinio': (
                f'Glicemia {gli:.0f} (> 600) ' + (f'+ osmolaridade {osmol:.0f} (> 320) ' if osmol else '')
                + 'SEM acidose significativa = EHH (típico do idoso DM2, instalação em dias). '
                'Desidratação é ainda MAIOR que na CAD (déficit ~8-10 L) — a reposição '
                'volêmica é o carro-chefe e corrige boa parte da glicemia sozinha. '
                'Insulina em dose menor que na CAD, após volume e potássio. '
                'Mortalidade alta — sempre tem um gatilho (infecção é o nº 1).'
            ),
            'alertas_seguranca': ['⚠️ Corrigir glicemia/osmolaridade LENTAMENTE — '
                                  'queda abrupta → edema cerebral.'],
            'plano_a': {'titulo': 'PLANO A — Tratar AQUI (com UTI + eletrólitos)',
                        'itens': ['SF 0,9% agressivo: 1-1,5 L na 1ª hora, depois ajustar '
                                  'por Na corrigido e estado volêmico',
                                  'Potássio conforme dosagem (mesma lógica da CAD)',
                                  'Insulina regular 0,05-0,1 U/kg/h APÓS volume + K',
                                  'Meta de queda glicêmica gradual (~50-75 mg/dL/h)',
                                  'Investigar e tratar o gatilho (infecção, IAM, AVC)',
                                  'Profilaxia de TEV (estado pró-trombótico)']},
            'plano_b': {'titulo': 'PLANO B — Encaminhar',
                        'itens': ['SF 0,9% 1 L IV antes/durante o transporte',
                                  'NÃO dar insulina sem dosar potássio',
                                  'USA — paciente idoso, alto risco', 'Carta abaixo']},
            'carta_encaminhamento': _carta(
                f'Estado hiperglicêmico hiperosmolar (glicemia {gli:.0f})',
                [f'Glicemia: {gli:.0f} mg/dL',
                 f'Osmolaridade: {osmol if osmol else "não calculada"}',
                 f'pH: {ph if ph else "ND"} (sem acidose significativa)',
                 'Gatilho investigado: ______________________'],
                ['SF 0,9% ____ mL IV'],
                'UTI + reposição volêmica + insulinoterapia + investigação do gatilho'),
        }

    # ── 4. HIPERGLICEMIA SIMPLES — sem acidose/hiperosmolaridade ─────────────
    if gli > 250:
        return {
            **base,
            'categoria': 'hiperglicemia_simples',
            'diagnostico': f'Hiperglicemia sem complicação aguda ({gli:.0f} mg/dL)',
            'urgencia': 'ambulatorio',
            'raciocinio': (
                f'Glicemia {gli:.0f} elevada, mas SEM acidose, sem hiperosmolaridade e '
                f'sem rebaixamento — não é CAD nem EHH. Hiperglicemia simples: descartadas '
                f'as emergências, o manejo é ajuste do tratamento e seguimento. '
                f'Hidratação VO + revisão de adesão/dose. Cetonúria negativa reforça '
                f'segurança para conduta ambulatorial.'
            ),
            'plano_a': {'titulo': 'PLANO ÚNICO — Ajuste e seguimento',
                        'itens': ['Hidratação oral',
                                  'Revisar adesão e dose do esquema antidiabético',
                                  'Dose de correção com insulina rápida se muito sintomático',
                                  'Investigar infecção/transgressão alimentar',
                                  'Retorno ambulatorial precoce + orientar sinais de CAD '
                                  '(náusea, dor abdominal, hálito cetônico, dispneia)']},
            'plano_b': None,
        }

    # ── Glicemia normal/limítrofe ────────────────────────────────────────────
    return {
        **base,
        'categoria': 'glicemia_normal',
        'diagnostico': f'Glicemia {gli:.0f} mg/dL — sem disglicemia aguda',
        'urgencia': 'ambulatorio',
        'raciocinio': f'Glicemia {gli:.0f} dentro/perto da faixa — afastada disglicemia '
                      f'como causa do quadro. Investigar outras causas se sintomático.',
        'plano_a': {'titulo': 'PLANO ÚNICO', 'itens': ['Sem correção glicêmica indicada',
                                                       'Investigar causa alternativa dos sintomas']},
        'plano_b': None,
    }
