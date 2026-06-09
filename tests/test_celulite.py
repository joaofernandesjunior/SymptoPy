# tests/test_celulite.py
# Smoke tests — módulo Celulite / Erisipela
# Executar: python tests/test_celulite.py

import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.raciocinio.celulite.engine_celulite import analisar_celulite


def test(nome, dados, esperado_cat, esperado_urgencia=None,
         contem=None, nao_contem=None):
    r = analisar_celulite(dados)
    cat  = r.get('categoria', '')
    urg  = r.get('urgencia', '')
    full = (
        str(r.get('conduta', '')) +
        str(r.get('raciocinio', '')) +
        str(r.get('prescricoes_estruturadas', '')) +
        str(r.get('diagnostico', ''))
    ).lower()

    ok = True
    erros = []

    if cat != esperado_cat:
        ok = False
        erros.append(f'  cat={cat!r} esperado={esperado_cat!r}')
    if esperado_urgencia and urg != esperado_urgencia:
        ok = False
        erros.append(f'  urgencia={urg!r} esperado={esperado_urgencia!r}')
    for c in (contem or []):
        if c.lower() not in full:
            ok = False
            erros.append(f'  falta: {c!r}')
    for nc in (nao_contem or []):
        if nc.lower() in full:
            ok = False
            erros.append(f'  nao deveria conter: {nc!r}')

    status = 'OK  ' if ok else 'FAIL'
    print(f'[{status}] {nome}')
    for e in erros: print(e)
    return ok


resultados = []

# ── Base mínima para evitar KeyError nos testes ────────────────────────────
_BASE = {
    'localizacao': 'mmii_unilateral',
    'tempo_evolucao': 'um_a_dois_dias',
    'tinea_pedis': False, 'ferida_ulcera': False, 'picada_trauma': False,
    'pe_diabetico': False, 'manicure_pedicure': False, 'uso_drogas_iv': False,
    'mordedura_animal': False, 'trauma_penetrante': False,
    'febre': False, 'hipotermia': False, 'taquicardia': False,
    'taquipneia': False, 'mal_estar_calafrio': False, 'hipotensao': False,
    'temp_celsius': None,
    'borda_nitida': False, 'flutuacao': False, 'bolhas': False,
    'bolhas_hemorragicas': False, 'crepitacao': False, 'necrose': False,
    'linfangite': False, 'dor_desproporcional': False, 'progressao_rapida': False,
    'diabetes': False, 'obesidade': False, 'drc': False,
    'imunossupressao': False, 'neutropenia': False, 'insuf_venosa': False,
    'linfedema': False, 'malignidade': False,
    'mrsa_colonizacao': False, 'mrsa_internacao_recente': False,
    'drenagem_purulenta': False, 'falha_beta_lactamico': False,
    'episodios_anteriores': 0,
    'alergia_penicilina': 'nenhuma',
    'pcr': None, 'leucocitos': None, 'hb': None,
    'sodio': None, 'creatinina': None, 'glicemia': None,
}


def _d(**kwargs):
    d = dict(_BASE)
    d.update(kwargs)
    return d


# 01 — Erisipela clássica MMII, 0 SIRS → alta + amoxicilina
resultados.append(test(
    '01_erisipela_leve_amoxicilina',
    _d(borda_nitida=True),
    'cel_leve', 'ambulatorio',
    contem=['Amoxicilina'],
))

# 02 — Celulite não-purulenta, 0 SIRS → cefalexina (NÃO TMP-SMX)
resultados.append(test(
    '02_celulite_0sirs_cefalexina',
    _d(),
    'cel_leve', 'ambulatorio',
    contem=['Cefalexina'],
    nao_contem=['smx-tmp', 'trimetoprim'],
))

# 03 — Celulite + DM + febre 38.9 + FC 102 (2 SIRS) → internação IV
resultados.append(test(
    '03_celulite_2sirs_internacao_iv',
    _d(diabetes=True, febre=True, temp_celsius=38.9, taquicardia=True),
    'cel_grave', 'internacao',
    contem=['Cefazolina'],
))

# 04 — Celulite + uso drogas IV + drenagem purulenta → MRSA → vancomicina
resultados.append(test(
    '04_mrsa_vancomicina',
    _d(uso_drogas_iv=True, drenagem_purulenta=True, febre=True,
       taquicardia=True, taquipneia=True),
    'cel_grave', 'internacao',
    contem=['Vancomicina'],
))

# 05 — Abscesso sem celulite perilesional → drenagem, sem ATB
resultados.append(test(
    '05_abscesso_simples_drenagem_sem_atb',
    _d(flutuacao=True),
    'cel_abscesso', 'urgente',
    contem=['drenagem'],
    nao_contem=['cefalexina', 'amoxicilina', 'smx-tmp'],
))

# 06 — Abscesso + MRSA (colonização) → SMX-TMP
resultados.append(test(
    '06_abscesso_mrsa_smxtmp',
    _d(flutuacao=True, mrsa_colonizacao=True),
    'cel_abscesso', 'urgente',
    contem=['SMX-TMP', 'drenagem'],
))

# 07 — Crepitação → fasciite necrotizante
resultados.append(test(
    '07_crepitacao_fasciite',
    _d(crepitacao=True),
    'cel_fasciite', 'emergencia',
    contem=['cirurgia', 'Vancomicina'],
))

# 08 — LRINEC ≥ 6 via labs → fasciite
resultados.append(test(
    '08_lrinec_6_fasciite',
    _d(pcr=200, leucocitos=28000, hb=10, sodio=130, creatinina=1.8, glicemia=190),
    'cel_fasciite', 'emergencia',
    contem=['LRINEC'],
))

# 09 — Bolhas tensas (não hemorrágicas) → internação preferencial
resultados.append(test(
    '09_bolhas_tensas_internacao',
    _d(bolhas=True, bolhas_hemorragicas=False),
    'cel_bolhosa', 'internacao',
))

# 10 — Celulite recorrente (4×/ano) → profilaxia penicilina VK
resultados.append(test(
    '10_recorrente_profilaxia_penicilina_vk',
    _d(episodios_anteriores=4),
    'cel_recorrente', 'ambulatorio',
    contem=['Penicilina VK'],
))

# 11 — Celulite facial → diagnóstico contém 'face'
resultados.append(test(
    '11_celulite_facial',
    _d(localizacao='face'),
    'cel_leve', 'ambulatorio',
    contem=['face'],
))

# 12 — Alergia anafilática → clindamicina (não cefalexina, não amoxicilina)
resultados.append(test(
    '12_alergia_anafilatica_clindamicina',
    _d(alergia_penicilina='anafilatica'),
    'cel_leve', 'ambulatorio',
    contem=['Clindamicina'],
    nao_contem=['cefalexina', 'amoxicilina'],
))

# 13 — Hipotensão → sepse → emergência
resultados.append(test(
    '13_hipotensao_sepse_emergencia',
    _d(hipotensao=True, febre=True, taquicardia=True),
    'cel_sepse', 'emergencia',
    contem=['sepse'],
))

# 14 — 1 SIRS → moderado → retorno 48h
resultados.append(test(
    '14_1sirs_moderado_retorno_48h',
    _d(febre=True, temp_celsius=38.2),
    'cel_moderada', 'ambulatorio_urgente',
    contem=['48'],
))

total   = len(resultados)
passou  = sum(resultados)
print(f'\n{"=" * 50}')
print(f'{passou}/{total} testes passaram')
if passou < total:
    sys.exit(1)
