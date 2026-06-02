# tests/test_hemorragia.py
# Smoke tests — módulo Hemorragia Digestiva (HDA + HDB)
# Executar: python tests/test_hemorragia.py

import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.raciocinio.hemorragia.engine_hemorragia import analisar_hemorragia


def test(nome, dados, esperado_cat, esperado_urgencia=None,
         contem=None, nao_contem=None):
    r = analisar_hemorragia(dados)
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

_UGIB_BASE = {
    'ramo': 'ugib', 'tipo_sangramento': 'melena',
    'sexo': 'masculino', 'idade': 50,
    'pas': 120, 'fc': 75,
    'sincope': False, 'palidez_sudorese': False,
    'bun': 15, 'hb': 14,
    'melena': False, 'hepatopatia_gbs': False, 'icc': False,
    'cirrose': False, 'estigmas_htpor': False, 'varizes_previas': False,
    'alcool_cronico': False, 'aine_asa': False, 'hp_conhecido': False,
    'pud_previo': False, 'dcv': False,
    'anticoagulado': False, 'anticoagulante': None, 'inr': None,
    'endoscopia_recente': False, 'cirurgia_gi': False,
}

_LGIB_BASE = {
    'ramo': 'lgib', 'tipo_sangramento': 'hematoquezia',
    'sexo': 'masculino', 'idade': 35,
    'pas': 125, 'fc': 72,
    'sincope': False, 'palidez_sudorese': False,
    'hb': 13,
    'lgib_previo': False, 'dre_sangue': False,
    'papel_apenas': False, 'dor_evacuacao': False,
    'diarreia_sangue': False, 'dor_abdominal': False,
    'febre': False, 'atb_recente': False, 'viagem_recente': False,
    'mudanca_habito': False, 'perda_peso': False,
    'pos_polipectomia': False, 'dii_conhecida': False,
    'dcv_dm': False, 'idoso_indolor': False,
    'anticoagulado': False, 'anticoagulante': None, 'inr': None,
    'hepatopatia_gbs': False, 'cirrose': False,
    'endoscopia_recente': False, 'cirurgia_gi': False,
}


def _u(**kw):
    d = dict(_UGIB_BASE); d.update(kw); return d

def _l(**kw):
    d = dict(_LGIB_BASE); d.update(kw); return d


# 01 — UGIB GBS 0 → alta + endoscopia eletiva
resultados.append(test(
    '01_ugib_gbs0_alta',
    _u(bun=15, hb=14, pas=130, fc=70, melena=False, sincope=False,
       hepatopatia_gbs=False, icc=False),
    'hd_ugib_gbs_baixo', 'ambulatorio',
    contem=['eletiv'],
))

# 02 — UGIB GBS 3 (melena + Hb 11 homem) → internação + PPI + endoscopia 24h
resultados.append(test(
    '02_ugib_gbs3_internacao_ppi',
    _u(melena=True, hb=11, bun=15, pas=120, fc=80,
       sincope=False, hepatopatia_gbs=False, icc=False),
    'hd_ugib_nao_variceal', 'internacao',
    contem=['omeprazol', '24'],
))

# 03 — UGIB GBS alto + cirrose → variceal: octreotida + ceftriaxona + 12h
resultados.append(test(
    '03_ugib_variceal_octreotida_ceftriaxona',
    _u(melena=True, hb=9, bun=30, pas=105, fc=105,
       hepatopatia_gbs=True, cirrose=True, icc=False, sincope=True),
    'hd_ugib_variceal', 'internacao',
    contem=['octreotida', 'ceftriaxona', '12h'],
))

# 04 — UGIB Hb 6.5, estável, sem DCV → transfundir
resultados.append(test(
    '04_ugib_hb65_transfundir',
    _u(hb=6.5, melena=True, bun=20, pas=115, fc=88, dcv=False),
    'hd_ugib_nao_variceal', 'internacao',
    contem=['transfus'],
))

# 05 — UGIB Hb 7.5, estável, sem DCV → NÃO transfundir
resultados.append(test(
    '05_ugib_hb75_nao_transfundir',
    _u(hb=7.5, melena=True, bun=20, pas=120, fc=78, dcv=False),
    'hd_ugib_nao_variceal', 'internacao',
    nao_contem=['transfus'],
))

# 06 — UGIB Hb 7.5 + DCV → transfundir (limiar 8)
resultados.append(test(
    '06_ugib_hb75_dcv_transfundir',
    _u(hb=7.5, melena=True, bun=20, pas=120, fc=78, dcv=True),
    'hd_ugib_nao_variceal', 'internacao',
    contem=['transfus'],
))

# 07 — LGIB Oakland ≤8, estável → alta + colonoscopia eletiva
resultados.append(test(
    '07_lgib_oakland_baixo_alta',
    _l(idade=30, sexo='feminino', hb=13, pas=130, fc=70),
    'hd_lgib_hemorroida', 'ambulatorio',
))

# 08 — LGIB Oakland >8, estável → internação + colonoscopia
resultados.append(test(
    '08_lgib_oakland_alto_internacao',
    _l(idade=72, sexo='masculino', hb=9.5, pas=105, fc=100,
       lgib_previo=True, dre_sangue=True),
    'hd_lgib_internacao', 'internacao',
    contem=['colonoscopia'],
))

# 09 — LGIB shock index >1 → AngioTC + embolização
resultados.append(test(
    '09_lgib_instavel_angiotc',
    _l(pas=80, fc=110, sincope=True, hb=8),
    'hd_lgib_instavel', 'emergencia',
    contem=['angiotc', 'emboliz'],
))

# 10 — LGIB fissura anal + dor + papel → nitroglicerina
resultados.append(test(
    '10_lgib_fissura_nitroglicerina',
    _l(dor_evacuacao=True, papel_apenas=True),
    'hd_lgib_fissura', 'ambulatorio',
    contem=['nitroglicerina'],
))

# 11 — LGIB hemorroida grau II → tópico + fibra (NÃO cirurgia como 1ª linha)
resultados.append(test(
    '11_lgib_hemorroida_topico',
    _l(papel_apenas=True),
    'hd_lgib_hemorroida', 'ambulatorio',
    contem=['tópico', 'fibra'],
    nao_contem=['hemorroidectomia como 1ª'],
))

# 12 — LGIB idoso + painless + alto volume → diverticular (Oakland ≤8)
resultados.append(test(
    '12_lgib_diverticular_colonoscopia',
    _l(idade=60, hb=13, pas=120, fc=78, diarreia_sangue=False,
       dor_abdominal=False, febre=False, mudanca_habito=False,
       lgib_previo=False, dre_sangue=False),
    'hd_lgib_diverticular', 'ambulatorio',
    contem=['diverticular', 'colonoscopia'],
))

# 13 — LGIB dor abdominal + DM + isquêmica → suporte
resultados.append(test(
    '13_lgib_isquemica_suporte',
    _l(dor_abdominal=True, dcv_dm=True, diarreia_sangue=True,
       idade=65, hb=12, pas=115, fc=90),
    'hd_lgib_isquemica',
    contem=['isquêm', 'cirurgia'],
))

# 14 — Anticoagulado dabigatrana + UGIB grave → idarucizumab
resultados.append(test(
    '14_anticoagulado_dabigatrana_idarucizumab',
    _u(pas=85, fc=105, hb=7, melena=True, bun=35,
       anticoagulado=True, anticoagulante='dabigatrana', inr=None,
       hepatopatia_gbs=False, cirrose=False, icc=False, sincope=True),
    'hd_ugib_instavel', 'emergencia',
    contem=['idarucizumab'],
))


total  = len(resultados)
passou = sum(resultados)
print(f'\n{"=" * 50}')
print(f'{passou}/{total} testes passaram')
if passou < total:
    sys.exit(1)
