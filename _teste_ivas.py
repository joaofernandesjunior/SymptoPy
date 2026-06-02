# _teste_ivas.py
# Testes unitários — IVAS / Faringite
# Cobertura: todas as 7 categorias + variantes de score, alergia, oseltamivir
# Executar: python _teste_ivas.py

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modules.raciocinio.ivas.engine_ivas import interpretar_ivas

_OK   = 0
_FAIL = 0


def _assert(label, cond, info=''):
    global _OK, _FAIL
    if cond:
        print(f'  [OK]   {label}')
        _OK += 1
    else:
        print(f'  [FAIL] {label}' + (f' — {info}' if info else ''))
        _FAIL += 1


def _base():
    """Paciente adulto padrão — todos os flags em False/0/safe."""
    return {
        # Dados básicos
        'idade':                 30,
        'dias_sintomas':         2,
        # Red flags
        'assimetria_tonsilar':   False,
        'trismo':                False,
        'voz_abafada':           False,
        'sialorreia':            False,
        'estridor':              False,
        'dificuldade_respiratoria': False,
        'edema_submandibular':   False,
        # McIsaac
        'febre_38':              False,
        'febre_alta_39':         False,
        'tosse_presente':        True,
        'exsudato_tonsilar':     False,
        'linfadenopatia_anterior': False,
        # Diferencial
        'inicio_subito_horas':   False,
        'mialgia_intensa':       False,
        'linfadenopatia_posterior': False,
        'esplenomegalia_referida': False,
        # Sinusite / laringite
        'dor_facial':            False,
        'descarga_purulenta':    False,
        'duplo_agravamento':     False,
        'sintomas_10_dias':      False,
        'rouquidao_predominante': False,
        # RADT
        'radt_realizado':        False,
        'radt_positivo':         False,
        # Alergia / aderência
        'alergia_penicilina':    False,
        'alergia_anafilatica':   False,
        'aderencia_preocupa':    False,
        'historico_fra':         False,
        # Comorbidades (oseltamivir)
        'asma_dpoc':             False,
        'doenca_cardiovascular': False,
        'drc':                   False,
        'hepatopatia':           False,
        'diabetes':              False,
        'imunossupressao':       False,
        'gestante':              False,
        'obesidade_grave':       False,
    }


# =============================================================================
# TC01-04 — EMERGÊNCIAS
# =============================================================================

def tc01():
    """Abscesso peritonsilar: assimetria + trismo."""
    d = _base()
    d.update({'assimetria_tonsilar': True, 'trismo': True})
    r = interpretar_ivas(d)
    _assert('TC01 — categoria ivas_emergencia', r['categoria'] == 'ivas_emergencia')
    _assert('TC01 — emergencia_tipo abscesso', r.get('emergencia_tipo') == 'abscesso_peritonsilar')
    _assert('TC01 — internacao True', r.get('internacao') is True)


def tc02():
    """Epiglotite: estridor + sialorreia."""
    d = _base()
    d.update({'estridor': True, 'sialorreia': True})
    r = interpretar_ivas(d)
    _assert('TC02 — categoria ivas_emergencia', r['categoria'] == 'ivas_emergencia')
    _assert('TC02 — emergencia_tipo epiglotite', r.get('emergencia_tipo') == 'epiglotite')


def tc03():
    """Angina de Ludwig: edema submandibular."""
    d = _base()
    d.update({'edema_submandibular': True})
    r = interpretar_ivas(d)
    _assert('TC03 — categoria ivas_emergencia', r['categoria'] == 'ivas_emergencia')
    _assert('TC03 — emergencia_tipo ludwig', r.get('emergencia_tipo') == 'ludwig')


def tc04():
    """Dificuldade respiratória isolada → epiglotite presumida."""
    d = _base()
    d.update({'dificuldade_respiratoria': True})
    r = interpretar_ivas(d)
    _assert('TC04 — categoria ivas_emergencia', r['categoria'] == 'ivas_emergencia')
    _assert('TC04 — emergencia_tipo epiglotite (presumido)', r.get('emergencia_tipo') == 'epiglotite')


# =============================================================================
# TC05-06 — MONONUCLEOSE
# =============================================================================

def tc05():
    """Mononucleose: > 7 dias + linfadenopatia posterior."""
    d = _base()
    d.update({'dias_sintomas': 10, 'linfadenopatia_posterior': True})
    r = interpretar_ivas(d)
    _assert('TC05 — categoria ivas_mononucleose', r['categoria'] == 'ivas_mononucleose')
    _assert('TC05 — amoxicilina contraindicada', r.get('amoxicilina_contraindicada') is True)
    _assert('TC05 — sinais_retorno presentes', len(r.get('sinais_retorno', [])) > 0)


def tc06():
    """Mononucleose via esplenomegalia (sem linfadenopatia posterior)."""
    d = _base()
    d.update({'dias_sintomas': 12, 'esplenomegalia_referida': True})
    r = interpretar_ivas(d)
    _assert('TC06 — categoria ivas_mononucleose', r['categoria'] == 'ivas_mononucleose')
    _assert('TC06 — conduta menciona esporte', any('esporte' in c.lower() or 'contato' in c.lower()
                                                    for c in r.get('conduta', [])))


# =============================================================================
# TC07-09 — INFLUENZA
# =============================================================================

def tc07():
    """Influenza clássica: início súbito + mialgia + febre alta + sem exsudato."""
    d = _base()
    d.update({'inicio_subito_horas': True, 'mialgia_intensa': True,
              'febre_alta_39': True, 'febre_38': True,
              'exsudato_tonsilar': False, 'dias_sintomas': 1})
    r = interpretar_ivas(d)
    _assert('TC07 — categoria ivas_influenza', r['categoria'] == 'ivas_influenza')
    _assert('TC07 — sinais_retorno presentes', len(r.get('sinais_retorno', [])) > 0)


def tc08():
    """Influenza + DM + <= 48h → oseltamivir indicado."""
    d = _base()
    d.update({'inicio_subito_horas': True, 'mialgia_intensa': True,
              'febre_alta_39': True, 'febre_38': True,
              'dias_sintomas': 1, 'diabetes': True})
    r = interpretar_ivas(d)
    _assert('TC08 — categoria ivas_influenza', r['categoria'] == 'ivas_influenza')
    conduta_str = ' '.join(r.get('conduta', [])).lower()
    _assert('TC08 — oseltamivir indicado na conduta', 'oseltamivir 75 mg' in conduta_str)
    _assert('TC08 — alto risco reconhecido', 'alto risco' in conduta_str or 'oseltamivir indicado' in conduta_str)


def tc09():
    """Influenza + sem risco + > 48h → oseltamivir não indicado como 1ª linha."""
    d = _base()
    d.update({'inicio_subito_horas': True, 'mialgia_intensa': True,
              'febre_alta_39': True, 'febre_38': True,
              'dias_sintomas': 3})
    r = interpretar_ivas(d)
    _assert('TC09 — categoria ivas_influenza', r['categoria'] == 'ivas_influenza')
    conduta_str = ' '.join(r.get('conduta', [])).lower()
    _assert('TC09 — menciona limitação de oseltamivir >48h', '> 48h' in conduta_str or '48h' in conduta_str)


# =============================================================================
# TC10-14 — GAS / McIsaac
# =============================================================================

def tc10():
    """Score McIsaac = 4, RADT indisponível → tratar_empirico (empírico por impossibilidade de teste)."""
    d = _base()
    d.update({'exsudato_tonsilar': True, 'linfadenopatia_anterior': True,
              'febre_38': True, 'tosse_presente': False,
              'radt_disponivel': False})   # sem RADT → empírico
    # Score: +1+1+1+1 = 4 | radt_disponivel=False → tratar_empirico
    r = interpretar_ivas(d)
    _assert('TC10 — categoria ivas_gas', r['categoria'] == 'ivas_gas')
    _assert('TC10 — score_mcisaac = 4', r.get('score_mcisaac') == 4)
    _assert('TC10 — recomendacao tratar_empirico (RADT indisponível)', r.get('recomendacao_atb') == 'tratar_empirico')
    _assert('TC10 — atb_prescrito amoxicilina', 'Amoxicilina' in r.get('atb_prescrito', {}).get('medicamento', ''))
    _rx10 = (r.get('atb_prescrito') or {}).get('prescricoes', [{}])
    _assert('TC10 — amoxicilina 30cp (SUS-safe)', _rx10[0].get('quantidade') == 30)
    _assert('TC10 — posologia 8/8h', '8 em 8' in _rx10[0].get('posologia', ''))


def tc11():
    """Score McIsaac = 2: febre + sem tosse (sem exsudato, sem linfonodo) → indicar RADT."""
    d = _base()
    d.update({'febre_38': True, 'tosse_presente': False,
              'exsudato_tonsilar': False, 'linfadenopatia_anterior': False})
    # Score: +1(febre) +1(sem tosse) = 2
    r = interpretar_ivas(d)
    _assert('TC11 — categoria ivas_gas', r['categoria'] == 'ivas_gas')
    _assert('TC11 — score_mcisaac = 2', r.get('score_mcisaac') == 2)
    _assert('TC11 — recomendacao indicar_radt', r.get('recomendacao_atb') == 'indicar_radt')
    _assert('TC11 — atb_prescrito None (aguardar RADT)', r.get('atb_prescrito') is None)
    _assert('TC11 — atb_recomendado presente (para plano condicional)',
            r.get('atb_recomendado') is not None)
    _assert('TC11 — criterios_usados menciona RADT disponivel',
            'RADT disponível' in (r.get('criterios_usados') or ''))


def tc12():
    """RADT positivo → tratar independente do score."""
    d = _base()
    d.update({'radt_realizado': True, 'radt_positivo': True,
              'febre_38': False, 'tosse_presente': True,
              'exsudato_tonsilar': False, 'linfadenopatia_anterior': False})
    # Score = 0, mas RADT+
    r = interpretar_ivas(d)
    _assert('TC12 — categoria ivas_gas (RADT+)', r['categoria'] == 'ivas_gas')
    _assert('TC12 — recomendacao tratar', r.get('recomendacao_atb') == 'tratar')
    _assert('TC12 — atb_prescrito presente', r.get('atb_prescrito') is not None)


def tc13():
    """RADT negativo + score=3 → nao_tratar (adulto: RADT- descarta GAS)."""
    d = _base()
    d.update({'febre_38': True, 'tosse_presente': False, 'exsudato_tonsilar': True,
              'linfadenopatia_anterior': False,
              'radt_realizado': True, 'radt_positivo': False})
    # Score = 1(febre)+1(sem tosse)+1(exsudato) = 3 — mas RADT-
    r = interpretar_ivas(d)
    _assert('TC13 — categoria ivas_gas (score=3 mas RADT-)', r['categoria'] == 'ivas_gas')
    _assert('TC13 — recomendacao nao_tratar', r.get('recomendacao_atb') == 'nao_tratar')
    _assert('TC13 — atb_prescrito None', r.get('atb_prescrito') is None)


def tc14():
    """Score = 0: ivas_viral (sem critérios especiais)."""
    d = _base()
    # febre_38=False, tosse_presente=True, exsudato=False, linfonodo=False → score=0
    r = interpretar_ivas(d)
    _assert('TC14 — categoria ivas_viral', r['categoria'] == 'ivas_viral')
    _assert('TC14 — score_mcisaac = 0', r.get('score_mcisaac') == 0)


# =============================================================================
# TC15-18 — SELEÇÃO DE ANTIBIÓTICO
# =============================================================================

def tc15():
    """Alergia NÃO-anafilática → cefalexina. RADT indisponível para forçar prescrição."""
    d = _base()
    d.update({'exsudato_tonsilar': True, 'linfadenopatia_anterior': True,
              'febre_38': True, 'tosse_presente': False,
              'alergia_penicilina': True, 'alergia_anafilatica': False,
              'radt_disponivel': False})
    r = interpretar_ivas(d)
    _assert('TC15 — categoria ivas_gas', r['categoria'] == 'ivas_gas')
    _assert('TC15 — atb cefalexina', 'Cefalexina' in r.get('atb_prescrito', {}).get('medicamento', ''))
    _rx15 = (r.get('atb_prescrito') or {}).get('prescricoes', [{}])
    _assert('TC15 — cefalexina 40cp (QID correto)', _rx15[0].get('quantidade') == 40)
    _assert('TC15 — posologia 6/6h', '6 em 6' in _rx15[0].get('posologia', ''))
    alt = r.get('atb_alternativo') or {}
    _assert('TC15 — alternativo cefadroxila', 'Cefadroxila' in alt.get('medicamento', ''))
    _rx15_alt = alt.get('prescricoes', [{}])
    _assert('TC15 — cefadroxila 10cp', _rx15_alt[0].get('quantidade') == 10)


def tc16():
    """Alergia ANAFILÁTICA → clindamicina. RADT indisponível para forçar prescrição."""
    d = _base()
    d.update({'exsudato_tonsilar': True, 'linfadenopatia_anterior': True,
              'febre_38': True, 'tosse_presente': False,
              'alergia_penicilina': True, 'alergia_anafilatica': True,
              'radt_disponivel': False})
    r = interpretar_ivas(d)
    _assert('TC16 — categoria ivas_gas', r['categoria'] == 'ivas_gas')
    _assert('TC16 — atb clindamicina', 'Clindamicina' in r.get('atb_prescrito', {}).get('medicamento', ''))
    _rx16 = (r.get('atb_prescrito') or {}).get('prescricoes', [{}])
    _assert('TC16 — clindamicina 30cp', _rx16[0].get('quantidade') == 30)
    _assert('TC16 — posologia 8/8h', '8 em 8' in _rx16[0].get('posologia', ''))
    alt = r.get('atb_alternativo') or {}
    _assert('TC16 — alternativo azitromicina', 'Azitromicina' in alt.get('medicamento', ''))
    _rx16_alt = alt.get('prescricoes', [{}])
    _assert('TC16 — azitromicina 3cp', _rx16_alt[0].get('quantidade') == 3)


def tc17():
    """Aderência preocupa → benzatina IM (sem alternativo). RADT indisponível."""
    d = _base()
    d.update({'exsudato_tonsilar': True, 'linfadenopatia_anterior': True,
              'febre_38': True, 'tosse_presente': False,
              'aderencia_preocupa': True, 'radt_disponivel': False})
    r = interpretar_ivas(d)
    _assert('TC17 — categoria ivas_gas', r['categoria'] == 'ivas_gas')
    _assert('TC17 — atb benzatina', 'Benzatina' in r.get('atb_prescrito', {}).get('medicamento', '')
            or 'Benzatina' in r.get('atb_prescrito', {}).get('medicamento', ''))
    _assert('TC17 — sem alternativo (benzatina é única opção)', r.get('atb_alternativo') is None)


def tc18():
    """Histórico de FRA → benzatina IM. RADT indisponível para ativar prescrição."""
    d = _base()
    d.update({'exsudato_tonsilar': True, 'linfadenopatia_anterior': True,
              'febre_38': True, 'tosse_presente': False,
              'historico_fra': True, 'radt_disponivel': False})
    r = interpretar_ivas(d)
    _assert('TC18 — categoria ivas_gas', r['categoria'] == 'ivas_gas')
    atb = r.get('atb_prescrito') or {}
    _assert('TC18 — atb benzatina (FRA)', 'Benzatina' in atb.get('medicamento', '')
            or 'Penicilina G' in atb.get('medicamento', ''))


# =============================================================================
# TC19-20 — RINOSSINUSITE
# =============================================================================

def tc19():
    """Rinossinusite com duplo agravamento → bacteriana."""
    d = _base()
    d.update({'dor_facial': True, 'descarga_purulenta': True,
              'duplo_agravamento': True, 'dias_sintomas': 7})
    r = interpretar_ivas(d)
    _assert('TC19 — categoria ivas_rinossinusite', r['categoria'] == 'ivas_rinossinusite')
    conduta_str = ' '.join(r.get('conduta', [])).lower()
    _assert('TC19 — conduta inclui ATB (amoxicilina-clavulanato)', 'amoxicilina' in conduta_str)


def tc20():
    """Rinossinusite > 10 dias persistente → bacteriana."""
    d = _base()
    d.update({'dor_facial': True, 'descarga_purulenta': True,
              'dias_sintomas': 12, 'sintomas_10_dias': True})
    r = interpretar_ivas(d)
    _assert('TC20 — categoria ivas_rinossinusite', r['categoria'] == 'ivas_rinossinusite')
    conduta_str = ' '.join(r.get('conduta', [])).lower()
    _assert('TC20 — conduta inclui ATB', 'amoxicilina' in conduta_str or 'atb' in conduta_str)


# =============================================================================
# TC21 — LARINGITE
# =============================================================================

def tc21():
    """Laringite: rouquidão predominante, score baixo."""
    d = _base()
    d.update({'rouquidao_predominante': True})
    r = interpretar_ivas(d)
    _assert('TC21 — categoria ivas_laringite', r['categoria'] == 'ivas_laringite')
    conduta_str = ' '.join(r.get('conduta', [])).lower()
    _assert('TC21 — conduta menciona repouso vocal', 'repouso vocal' in conduta_str)
    _assert('TC21 — conduta menciona ATB nao indicado', 'atb' in conduta_str or 'antibiótico' in conduta_str or 'antibiotico' in conduta_str)


# =============================================================================
# TC22 — IVAS VIRAL (default)
# =============================================================================

def tc22():
    """IVAS viral padrão: sem nenhum critério especial."""
    d = _base()
    # Todos os flags False/safe, score=0
    r = interpretar_ivas(d)
    _assert('TC22 — categoria ivas_viral', r['categoria'] == 'ivas_viral')
    conduta_str = ' '.join(r.get('conduta', [])).lower()
    _assert('TC22 — conduta menciona tratamento sintomático', 'dipirona' in conduta_str or 'sintomático' in conduta_str or 'sintomat' in conduta_str)
    _assert('TC22 — conduta menciona ATB não indicado', 'atb' in conduta_str or 'antibiótico' in conduta_str or 'antibiotico' in conduta_str)


# =============================================================================
# TC23 — AJUSTE DE IDADE (McIsaac >= 45)
# =============================================================================

def tc23():
    """Idade 55 anos: score bruto 4 → ajuste -1 → score 3 → indicar RADT."""
    d = _base()
    d.update({'idade': 55,
              'exsudato_tonsilar': True, 'linfadenopatia_anterior': True,
              'febre_38': True, 'tosse_presente': False})
    # Bruto: 4 | -1 (idade>=45) = 3
    r = interpretar_ivas(d)
    _assert('TC23 — score_mcisaac = 3 (ajuste de idade)', r.get('score_mcisaac') == 3)
    _assert('TC23 — categoria ivas_gas', r['categoria'] == 'ivas_gas')
    _assert('TC23 — recomendacao indicar_radt', r.get('recomendacao_atb') == 'indicar_radt')


# =============================================================================
# TC24 — RADT+ bloqueia mononucleose → ivas_gas
# =============================================================================

def tc24():
    """RADT+ com sinais de mono: suspeita_mono bloqueada → ivas_gas."""
    d = _base()
    d.update({'dias_sintomas': 10, 'linfadenopatia_posterior': True,
              'radt_realizado': True, 'radt_positivo': True,
              'exsudato_tonsilar': True})
    # suspeita_mono = (10>7 AND linfad_post AND NOT radt_positivo) → False
    # score = +1 (exsudato) + ... → >= 2 → ivas_gas
    r = interpretar_ivas(d)
    _assert('TC24 — RADT+ bloqueia mono -> ivas_gas', r['categoria'] == 'ivas_gas')
    _assert('TC24 — recomendacao tratar (RADT+)', r.get('recomendacao_atb') == 'tratar')


# =============================================================================
# TC25 — RADT INDISPONÍVEL + score intermediário → tratar empiricamente
# =============================================================================

def tc25():
    """RADT indisponível + score = 2 → tratar_empirico (não pedir para realizar RADT depois)."""
    d = _base()
    d.update({'febre_38': True, 'tosse_presente': False,
              'exsudato_tonsilar': False, 'linfadenopatia_anterior': False,
              'radt_realizado': False, 'radt_disponivel': False})
    # Score: +1(febre) +1(sem tosse) = 2; RADT indisponível → tratar empiricamente
    r = interpretar_ivas(d)
    _assert('TC25 — categoria ivas_gas', r['categoria'] == 'ivas_gas')
    _assert('TC25 — score_mcisaac = 2', r.get('score_mcisaac') == 2)
    _assert('TC25 — recomendacao tratar_empirico (RADT indisponível)', r.get('recomendacao_atb') == 'tratar_empirico')
    _assert('TC25 — atb_prescrito presente (empirismo)', r.get('atb_prescrito') is not None)
    _assert('TC25 — atb_recomendado presente', r.get('atb_recomendado') is not None)
    _assert('TC25 — criterios_usados menciona RADT indisponivel',
            'indisponível' in (r.get('criterios_usados') or '').lower())


# =============================================================================
# TC26A/B — Caso clínico: 19F, GAS score=4, odinofagia severa
#   19 anos, febre 38.2°C, exsudato purulento bilateral, linfonodo cervical
#   anterior doloroso bilateral, sem tosse. Sem red flags. Sem sinais de mono.
# =============================================================================

_DADOS_19F = {
    # Dados básicos
    'idade': 19, 'dias_sintomas': 3,
    # Red flags — todos negativos
    'assimetria_tonsilar': False, 'trismo': False, 'voz_abafada': False,
    'sialorreia': False, 'estridor': False, 'dificuldade_respiratoria': False,
    'edema_submandibular': False,
    # McIsaac — 4 critérios positivos
    'febre_38': True, 'febre_alta_39': False,
    'tosse_presente': False,          # ausência de tosse (+1)
    'exsudato_tonsilar': True,        # exsudato bilateral (+1)
    'linfadenopatia_anterior': True,  # linfonodo anterior doloroso (+1)
    'odinofagia_severa': True,        # dificuldade para deglutir líquidos
    # Diferencial — sem sinais de mono ou influenza
    'inicio_subito_horas': False, 'mialgia_intensa': False,
    'linfadenopatia_posterior': False, 'esplenomegalia_referida': False,
    # Sinusite/laringite — negativos
    'dor_facial': False, 'descarga_purulenta': False, 'duplo_agravamento': False,
    'sintomas_10_dias': False, 'rouquidao_predominante': False,
    # RADT — não realizado (variado por teste)
    'radt_realizado': False, 'radt_positivo': False,
    # Alergia — sem alergia
    'alergia_penicilina': False, 'alergia_anafilatica': False,
    'aderencia_preocupa': False, 'historico_fra': False,
    # Comorbidades — sem fatores de risco
    'asma_dpoc': False, 'doenca_cardiovascular': False, 'drc': False,
    'hepatopatia': False, 'diabetes': False, 'imunossupressao': False,
    'gestante': False, 'obesidade_grave': False,
}


def tc26a():
    """19F, GAS score=4, RADT disponível → indicar_radt + receita condicional."""
    d = dict(_DADOS_19F)
    d['radt_disponivel'] = True
    r = interpretar_ivas(d)
    _assert('TC26A — categoria ivas_gas', r['categoria'] == 'ivas_gas')
    _assert('TC26A — score_mcisaac = 4', r.get('score_mcisaac') == 4)
    _assert('TC26A — recomendacao indicar_radt (RADT disponível)', r.get('recomendacao_atb') == 'indicar_radt')
    _assert('TC26A — atb_prescrito None (aguardando RADT)', r.get('atb_prescrito') is None)
    _assert('TC26A — atb_recomendado presente (receita condicional)', r.get('atb_recomendado') is not None)
    _assert('TC26A — criterios lista febre', '+1 febre' in (r.get('criterios_usados') or ''))
    _assert('TC26A — criterios lista exsudato', '+1 exsudato' in (r.get('criterios_usados') or ''))
    _assert('TC26A — criterios lista linfonodo', '+1 linfonodo' in (r.get('criterios_usados') or ''))
    _assert('TC26A — criterios lista ausencia de tosse', '+1 ausência de tosse' in (r.get('criterios_usados') or ''))
    _assert('TC26A — criterios menciona RADT disponivel', 'RADT disponível' in (r.get('criterios_usados') or ''))
    _assert('TC26A — odinofagia_severa propagada', r.get('odinofagia_severa') is True)


def tc26b():
    """19F, GAS score=4, RADT indisponível → tratar_empirico + flag [!]."""
    d = dict(_DADOS_19F)
    d['radt_disponivel'] = False
    r = interpretar_ivas(d)
    _assert('TC26B — categoria ivas_gas', r['categoria'] == 'ivas_gas')
    _assert('TC26B — score_mcisaac = 4', r.get('score_mcisaac') == 4)
    _assert('TC26B — recomendacao tratar_empirico (RADT indisponível)', r.get('recomendacao_atb') == 'tratar_empirico')
    _assert('TC26B — atb_prescrito amoxicilina', 'Amoxicilina' in r.get('atb_prescrito', {}).get('medicamento', ''))
    _rx26b = (r.get('atb_prescrito') or {}).get('prescricoes', [{}])
    _assert('TC26B — amoxicilina 30cp SUS', _rx26b[0].get('quantidade') == 30)
    _assert('TC26B — criterios lista todos os 4', all(
        c in (r.get('criterios_usados') or '') for c in ['+1 febre', '+1 exsudato', '+1 linfonodo', '+1 ausência de tosse']
    ))
    _assert('TC26B — criterios flag RADT indisponivel', '[!]' in (r.get('criterios_usados') or ''))
    _assert('TC26B — criterios menciona upgrade empirico', 'empírico' in (r.get('criterios_usados') or '').lower())
    _assert('TC26B — odinofagia_severa propagada', r.get('odinofagia_severa') is True)


# =============================================================================
# RUNNER
# =============================================================================

def main():
    global _OK, _FAIL
    print('\n' + '=' * 58)
    print('  TESTES — IVAS / FARINGITE')
    print('=' * 58)

    for fn in [tc01, tc02, tc03, tc04,
               tc05, tc06,
               tc07, tc08, tc09,
               tc10, tc11, tc12, tc13, tc14,
               tc15, tc16, tc17, tc18,
               tc19, tc20,
               tc21, tc22, tc23, tc24, tc25,
               tc26a, tc26b]:
        print()
        fn()

    print('\n' + '=' * 58)
    total = _OK + _FAIL
    print(f'  RESULTADO: {_OK}/{total} OK  |  {_FAIL} falha(s)')
    print('=' * 58)
    sys.exit(0 if _FAIL == 0 else 1)


if __name__ == '__main__':
    main()
