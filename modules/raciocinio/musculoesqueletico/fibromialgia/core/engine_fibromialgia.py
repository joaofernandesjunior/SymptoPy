# modules/raciocinio/musculoesqueletico/fibromialgia/core/engine_fibromialgia.py
# Motor diagnóstico — Fibromialgia / Dor Crônica Difusa
# Fontes: ACR 2016, JAMA 2021, Cochrane 2025, EULAR, AAFP

# =============================================================================
# CONSTANTES
# =============================================================================

_REGIOES = {
    'MSE':   ['ombro_esquerdo', 'braco_esquerdo_sup', 'braco_esquerdo_inf', 'mao_punho_esquerdo'],
    'MSD':   ['ombro_direito',  'braco_direito_sup',  'braco_direito_inf',  'mao_punho_direito'],
    'MIE':   ['quadril_nadega_esquerdo', 'coxa_esquerda', 'perna_esquerda', 'tornozelo_pe_esquerdo'],
    'MID':   ['quadril_nadega_direito',  'coxa_direita',  'perna_direita',  'tornozelo_pe_direito'],
    'Axial': ['pescoco', 'dorso_superior', 'lombar', 'torax', 'abdome'],
}
_WPI_EXTRA  = ['mandibula_esquerda', 'mandibula_direita']
_WPI_TODAS  = [a for areas in _REGIOES.values() for a in areas] + _WPI_EXTRA

_ALERTA_AINE_OPIOIDE = (
    "⚠️ AINE e opioides NÃO tratam sensibilização central (Cochrane 2025). "
    "Risco de hiperalgesia induzida por opioide com uso crônico. Evitar como estratégia principal."
)


# =============================================================================
# SCORES
# =============================================================================

def _calcular_scores(dados):
    wpi = sum(1 for a in _WPI_TODAS if dados.get(a))
    p1  = (dados.get('sss_fadiga', 0)
           + dados.get('sss_sono', 0)
           + dados.get('sss_cognitivo', 0))
    p2  = sum([
        bool(dados.get('sss_cefaleia')),
        bool(dados.get('sss_dor_abdominal')),
        bool(dados.get('sss_depressao')),
    ])
    sss       = p1 + p2
    n_regioes = sum(
        1 for areas in _REGIOES.values()
        if any(dados.get(a) for a in areas)
    )
    return wpi, sss, p1, p2, n_regioes


# =============================================================================
# CRITÉRIOS ACR 2016
# =============================================================================

def _avaliar_criterios(dados, wpi, sss, n_regioes):
    criterio_duracao = bool(dados.get('duracao_sintomas_3_meses'))
    criterio_regioes = n_regioes >= 4
    condicao_A       = wpi >= 7 and sss >= 5
    condicao_B       = 4 <= wpi <= 6 and sss >= 9
    criterio_mat     = condicao_A or condicao_B
    confirmado       = criterio_duracao and criterio_regioes and criterio_mat

    faltando = []
    if not criterio_duracao:
        faltando.append('Duração insuficiente (< 3 meses)')
    if not criterio_regioes:
        faltando.append(f'Regiões afetadas insuficientes ({n_regioes}/5 — exige >= 4)')
    if not criterio_mat:
        if wpi < 4:
            faltando.append(f'WPI muito baixo ({wpi}/21 — minimo 4)')
        elif wpi <= 6:
            faltando.append(
                f'WPI intermediario ({wpi}) exige SSS >= 9 para condicao B '
                f'(SSS atual: {sss})'
            )
        else:
            faltando.append(
                f'SSS insuficiente ({sss}/12) para WPI = {wpi} '
                f'(condicao A exige SSS >= 5)'
            )

    return {
        'confirmado':          confirmado,
        'criterio_duracao':    criterio_duracao,
        'criterio_regioes':    criterio_regioes,
        'criterio_matematico': criterio_mat,
        'condicao_usada':      'A' if condicao_A else ('B' if condicao_B else None),
    }, faltando


# =============================================================================
# CONDUTA TAILORED
# =============================================================================

def _conduta_tailored(dados, confirmado):
    sintoma = dados.get('sintoma_predominante', 'dor')

    base = [
        "Educação em neurociência da dor (PNE): explicar sensibilização central como "
        "mecanismo — reduz catastrofização e melhora adesão ao tratamento",
        "Higiene do sono: horário regular, evitar telas 1h antes de dormir, "
        "ambiente escuro e fresco",
        "Alinhamento de expectativas: melhora modesta e gradual ao longo de semanas a meses; "
        "meta principal é funcionalidade, não ausência total de dor",
    ]

    if not confirmado:
        return {
            'base':              base,
            'nao_farmacologico': ["Exercício físico leve e progressivo enquanto investigação prossegue"],
            'farmacologico':     [],
            'alerta':            None,
            'nota_eficacia':     None,
        }

    if sintoma == 'dor':
        nao_farm = [
            "Exercício aeróbico de moderada intensidade: caminhada, natação ou bicicleta "
            "— 30 min, >= 3x/semana (nivel A — EULAR/Cochrane 2025)",
            "Exercício de resistência progressiva como alternativa equivalente ao aeróbico",
        ]
        farm = [
            "Duloxetina 30 mg/dia VO -> titular para 60 mg/dia após 4 semanas "
            "(nível A — JAMA 2021; dose 120 mg superior para dor + depressão concomitante)",
            "Pregabalina 75 mg/dia -> 150 mg/dia (alternativa de nível A; "
            "preferir se EVA > 7 ou componente neuropático associado)",
        ]
        nota = (
            "Duloxetina e Pregabalina: NNT ≈ 10 para resposta de 50% na dor. "
            "Preferir duloxetina quando há humor deprimido associado. "
            "Testar por mínimo 3 meses antes de concluir ineficácia."
        )

    elif sintoma == 'fadiga':
        nao_farm = [
            "Mind-body: Yoga, Tai Chi ou Pilates — evidencia especifica para fadiga em FM "
            "(Cochrane 2025; NNT ~7 para melhora de fadiga)",
            "Exercício de fortalecimento progressivo como alternativa",
        ]
        farm = []
        nota = (
            "ATENÇÃO: CBT e Mindfulness isolados NÃO melhoram fadiga em FM "
            "(Cochrane 2025) — não indicar como intervenção primária para esta queixa. "
            "Reservar CBT para manejo de dor e humor."
        )

    elif sintoma == 'sono':
        nao_farm = [
            "CBT focada em insônia (CBT-I): abordagem de primeira linha para sono não-reparador",
            "Exercício aeróbico regular — melhora arquitetura do sono em FM",
        ]
        farm = [
            "Amitriptilina 10 mg VO à noite -> titular até 25 mg/noite se bem tolerada "
            "(nível A para sono e dor noturna; dose analgésica ≠ dose antidepressiva)",
            "Ciclobenzaprina 5 mg VO à noite (alternativa à amitriptilina)",
            "Pregabalina à noite (opção adicional se dor noturna for componente predominante)",
        ]
        nota = (
            "Amitriptilina: iniciar sempre com 10 mg — efeitos colinérgicos (boca seca, "
            "constipação, retenção urinária) são dose-dependentes. "
            "Cautela em homens com HBP e em idosos acima de 65 anos."
        )

    else:  # humor / depressão
        nao_farm = [
            "Exercício físico regular — efeito antidepressivo documentado (nível A)",
            "CBT / Mindfulness: eficaz para humor deprimido em FM "
            "(diferente do efeito em fadiga — aqui tem evidência positiva)",
        ]
        farm = [
            "Duloxetina 30 mg/dia -> 60 mg/dia "
            "(primeira escolha quando humor deprimido é queixa central; "
            "dose 120 mg superior para dor + depressão concomitante — JAMA 2021)",
        ]
        nota = (
            "Evitar ISRS isolados em FM — evidência insuficiente para dor. "
            "Amitriptilina em baixa dose (10–25 mg à noite) pode ser combinada "
            "com duloxetina para benefício adicional no sono."
        )

    return {
        'base':              base,
        'nao_farmacologico': nao_farm,
        'farmacologico':     farm,
        'alerta':            _ALERTA_AINE_OPIOIDE,
        'nota_eficacia':     nota,
    }


# =============================================================================
# ENCAMINHAMENTO
# =============================================================================

def _encaminhamento(confirmado, flag_exclusao):
    if flag_exclusao:
        return (
            "Investigar causa secundária: hemograma, VHS, PCR, FAN, TSH, CPK, "
            "fator reumatoide. Encaminhar reumatologia se investigação inconclusiva."
        )
    if not confirmado:
        return (
            "Critérios ACR 2016 não preenchidos — reavaliar em 4–6 semanas. "
            "Encaminhar reumatologia se quadro persistir sem diagnóstico definido."
        )
    return None  # FM confirmada -> manejo em APS


# =============================================================================
# ENTRY POINT
# =============================================================================

def interpretar_fibromialgia(dados):
    wpi, sss, sss_p1, sss_p2, n_regioes = _calcular_scores(dados)
    criterios, faltando = _avaliar_criterios(dados, wpi, sss, n_regioes)
    flag_exclusao = bool(dados.get('flags_inflamatorios_exclusao'))

    if flag_exclusao:
        categoria = 'investigar_causa_secundaria'
    elif criterios['confirmado']:
        categoria = 'fibromialgia_confirmada'
    else:
        categoria = 'criterios_insuficientes'

    return {
        'categoria': categoria,
        'scores': {
            'wpi':       wpi,
            'sss':       sss,
            'sss_p1':    sss_p1,
            'sss_p2':    sss_p2,
            'n_regioes': n_regioes,
        },
        'criterios':           criterios,
        'criterios_faltando':  faltando,
        'sintoma_predominante': dados.get('sintoma_predominante', 'dor'),
        'conduta':             _conduta_tailored(dados, criterios['confirmado']),
        'encaminhar':          _encaminhamento(criterios['confirmado'], flag_exclusao),
    }


# =============================================================================
# TESTE ISOLADO
# =============================================================================

if __name__ == '__main__':
    import json, sys
    sys.stdout.reconfigure(encoding='utf-8')

    _AREA_POSITIVAS_TODAS = {a: True for a in _WPI_TODAS}

    _CASOS = {
        'FM CONFIRMADA — dor (condição A)': {
            'idade': 42, 'eva_dor': 7,
            'ombro_esquerdo': True,  'ombro_direito': True,
            'braco_esquerdo_sup': True,  'braco_direito_sup': True,
            'braco_esquerdo_inf': False, 'braco_direito_inf': False,
            'mao_punho_esquerdo': True,  'mao_punho_direito': True,
            'quadril_nadega_esquerdo': True, 'coxa_esquerda': True,
            'perna_esquerda': False, 'tornozelo_pe_esquerdo': False,
            'quadril_nadega_direito': True,  'coxa_direita': True,
            'perna_direita': False,  'tornozelo_pe_direito': False,
            'pescoco': True,  'dorso_superior': True, 'lombar': True,
            'torax': False,   'abdome': False,
            'mandibula_esquerda': False, 'mandibula_direita': False,
            'sss_fadiga': 2, 'sss_sono': 1, 'sss_cognitivo': 1,
            'sss_cefaleia': True, 'sss_dor_abdominal': False, 'sss_depressao': False,
            'duracao_sintomas_3_meses': True, 'flags_inflamatorios_exclusao': False,
            'sintoma_predominante': 'dor',
        },
        'FM CONFIRMADA — sono (condição B)': {
            'idade': 55, 'eva_dor': 5,
            'ombro_esquerdo': True,  'ombro_direito': True,
            'braco_esquerdo_sup': False, 'braco_direito_sup': False,
            'braco_esquerdo_inf': False, 'braco_direito_inf': False,
            'mao_punho_esquerdo': True,  'mao_punho_direito': True,
            'quadril_nadega_esquerdo': True, 'coxa_esquerda': False,
            'perna_esquerda': False, 'tornozelo_pe_esquerdo': False,
            'quadril_nadega_direito': True,  'coxa_direita': False,
            'perna_direita': False,  'tornozelo_pe_direito': False,
            'pescoco': True,  'dorso_superior': False, 'lombar': True,
            'torax': False,   'abdome': False,
            'mandibula_esquerda': False, 'mandibula_direita': False,
            'sss_fadiga': 3, 'sss_sono': 3, 'sss_cognitivo': 3,
            'sss_cefaleia': False, 'sss_dor_abdominal': False, 'sss_depressao': False,
            'duracao_sintomas_3_meses': True, 'flags_inflamatorios_exclusao': False,
            'sintoma_predominante': 'sono',
        },
        'FLAG INFLAMATÓRIO — causa secundária': {
            'idade': 38, 'eva_dor': 6,
            'ombro_esquerdo': True,  'ombro_direito': True,
            'braco_esquerdo_sup': False, 'braco_direito_sup': False,
            'braco_esquerdo_inf': False, 'braco_direito_inf': False,
            'mao_punho_esquerdo': True,  'mao_punho_direito': True,
            'quadril_nadega_esquerdo': False, 'coxa_esquerda': False,
            'perna_esquerda': False, 'tornozelo_pe_esquerdo': False,
            'quadril_nadega_direito': False,  'coxa_direita': False,
            'perna_direita': False,  'tornozelo_pe_direito': False,
            'pescoco': True,  'dorso_superior': True, 'lombar': True,
            'torax': False,   'abdome': False,
            'mandibula_esquerda': False, 'mandibula_direita': False,
            'sss_fadiga': 2, 'sss_sono': 1, 'sss_cognitivo': 1,
            'sss_cefaleia': False, 'sss_dor_abdominal': False, 'sss_depressao': False,
            'duracao_sintomas_3_meses': True, 'flags_inflamatorios_exclusao': True,
            'sintoma_predominante': 'dor',
        },
        'CRITÉRIOS INSUFICIENTES': {
            'idade': 30, 'eva_dor': 4,
            'ombro_esquerdo': True,  'ombro_direito': False,
            'braco_esquerdo_sup': False, 'braco_direito_sup': False,
            'braco_esquerdo_inf': False, 'braco_direito_inf': False,
            'mao_punho_esquerdo': False, 'mao_punho_direito': False,
            'quadril_nadega_esquerdo': False, 'coxa_esquerda': False,
            'perna_esquerda': False, 'tornozelo_pe_esquerdo': False,
            'quadril_nadega_direito': False,  'coxa_direita': False,
            'perna_direita': False,  'tornozelo_pe_direito': False,
            'pescoco': True,  'dorso_superior': True, 'lombar': True,
            'torax': False,   'abdome': False,
            'mandibula_esquerda': False, 'mandibula_direita': False,
            'sss_fadiga': 1, 'sss_sono': 1, 'sss_cognitivo': 0,
            'sss_cefaleia': False, 'sss_dor_abdominal': False, 'sss_depressao': False,
            'duracao_sintomas_3_meses': True, 'flags_inflamatorios_exclusao': False,
            'sintoma_predominante': 'fadiga',
        },
    }

    for nome, caso in _CASOS.items():
        print(f'\n{"="*60}')
        print(f'  CASO: {nome}')
        print('='*60)
        r = interpretar_fibromialgia(caso)
        print(json.dumps(r, ensure_ascii=False, indent=2))
