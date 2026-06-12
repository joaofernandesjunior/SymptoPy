# modules/transversal/news2.py
# NEWS2 — National Early Warning Score 2 (RCP 2017)
# Substitui o qSOFA como triagem objetiva de deterioração/sepse
# (Surviving Sepsis Campaign 2021 recomenda CONTRA qSOFA como triagem isolada).
#
# 7 parâmetros: FR, SpO2, O2 suplementar, temperatura, PAS, FC, consciência.
# Calculado automaticamente a partir dos sinais vitais do cabeçalho — zero
# perguntas extras além de 2 checkboxes (O2 suplementar, consciência alterada).
#
# Bandas de risco (RCP):
#   0–4   → baixo      (monitorização de rotina)
#   3 em qualquer parâmetro isolado → baixo-médio (revisão médica)
#   5–6   → médio      (resposta urgente — pensar sepse)
#   ≥ 7   → alto       (resposta emergencial — equipe de cuidados críticos)


def _pts_fr(fr):
    if fr is None: return None
    if fr <= 8:    return 3
    if fr <= 11:   return 1
    if fr <= 20:   return 0
    if fr <= 24:   return 2
    return 3


def _pts_spo2(spo2):
    # Escala 1 (sem DPOC hipercápnica — escala 2 é exceção, não implementada)
    if spo2 is None: return None
    if spo2 <= 91:  return 3
    if spo2 <= 93:  return 2
    if spo2 <= 95:  return 1
    return 0


def _pts_temp(t):
    if t is None:   return None
    if t <= 35.0:   return 3
    if t <= 36.0:   return 1
    if t <= 38.0:   return 0
    if t <= 39.0:   return 1
    return 2


def _pts_pas(pas):
    if pas is None: return None
    if pas <= 90:   return 3
    if pas <= 100:  return 2
    if pas <= 110:  return 1
    if pas <= 219:  return 0
    return 3


def _pts_fc(fc):
    if fc is None:  return None
    if fc <= 40:    return 3
    if fc <= 50:    return 1
    if fc <= 90:    return 0
    if fc <= 110:   return 1
    if fc <= 130:   return 2
    return 3


def parse_pas(pa_str) -> float | None:
    """Extrai a PAS de uma string '120/80' (ou número direto)."""
    if pa_str is None:
        return None
    if isinstance(pa_str, (int, float)):
        return float(pa_str)
    txt = str(pa_str).strip().replace(',', '.')
    if not txt:
        return None
    try:
        return float(txt.split('/')[0].split('x')[0].strip())
    except (ValueError, IndexError):
        return None


def _num(v) -> float | None:
    if v is None:
        return None
    try:
        return float(str(v).strip().replace(',', '.'))
    except ValueError:
        return None


def calcular_news2(vitais: dict) -> dict | None:
    """
    vitais: {'fr', 'spo2', 'temperatura', 'pa' (ou 'pas'), 'fc',
             'o2_suplementar' (bool), 'consciencia_alterada' (bool)}
    Retorna dict com score, banda, ação e detalhamento — ou None se
    nenhum parâmetro numérico foi informado.
    """
    fr   = _num(vitais.get('fr'))
    spo2 = _num(vitais.get('spo2') or vitais.get('sato2'))
    temp = _num(vitais.get('temperatura') or vitais.get('temp'))
    fc   = _num(vitais.get('fc'))
    pas  = _num(vitais.get('pas')) or parse_pas(vitais.get('pa'))

    componentes = {
        'FR':   _pts_fr(fr),
        'SpO2': _pts_spo2(spo2),
        'Temp': _pts_temp(temp),
        'PAS':  _pts_pas(pas),
        'FC':   _pts_fc(fc),
    }
    medidos = {k: v for k, v in componentes.items() if v is not None}
    if not medidos:
        return None

    score = sum(medidos.values())
    if vitais.get('o2_suplementar'):
        score += 2
        medidos['O2 suplementar'] = 2
    if vitais.get('consciencia_alterada'):
        score += 3
        medidos['Consciência alterada'] = 3

    max_isolado = max(medidos.values())
    n_faltando = len(componentes) - len([k for k in componentes if componentes[k] is not None])

    if score >= 7:
        banda, acao = 'alto', 'Resposta EMERGENCIAL — monitorização contínua, considerar UTI/transferência'
    elif score >= 5:
        banda, acao = 'medio', 'Resposta urgente — avaliar SEPSE, monitorização horária'
    elif max_isolado == 3:
        banda, acao = 'baixo_medio', 'Parâmetro isolado crítico (3 pts) — revisão médica imediata do parâmetro'
    else:
        banda, acao = 'baixo', 'Monitorização de rotina'

    detalhe = ' | '.join(f'{k} +{v}' for k, v in medidos.items() if v > 0) or 'todos os parâmetros normais'

    return {
        'score': score,
        'banda': banda,
        'acao': acao,
        'detalhe': detalhe,
        'parametros_medidos': len(medidos),
        'parametros_faltando': n_faltando,
        'incompleto': n_faltando > 0,
    }


def texto_news2(n: dict | None) -> str:
    """Linha pronta para o O: do SOAP."""
    if not n:
        return ''
    flag = {'alto': '🔴', 'medio': '🟠', 'baixo_medio': '🟡', 'baixo': '🟢'}.get(n['banda'], '')
    txt = f"NEWS2 = {n['score']} {flag} ({n['acao']})"
    if n['score'] > 0:
        txt += f" — {n['detalhe']}"
    if n['incompleto']:
        txt += f" [parcial: {n['parametros_faltando']} parâmetro(s) não medido(s)]"
    return txt
