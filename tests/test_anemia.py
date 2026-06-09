# tests/test_anemia.py
# Smoke tests — engine de anemia
# Rodar: python -m pytest tests/test_anemia.py -v
#     ou: python tests/test_anemia.py

import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.raciocinio.anemia.engine_anemia import interpretar_anemia


def _run(caso, dados):
    r = interpretar_anemia(dados)
    cat = r.get('categoria', '')
    ok  = cat == dados.get('_esperado')
    status = '✓' if ok else '✗'
    print(f'  {status} [{caso}] → {cat}  (esperado: {dados["_esperado"]})')
    if not ok:
        print(f'      diagnóstico: {r.get("diagnostico", "")}')
    return ok


def _base(sexo='feminino', gestante=False, doenca_cronica=False):
    return {
        'sexo': sexo, 'gestante': gestante, 'doenca_cronica': doenca_cronica,
        'wbc': 6.0, 'plt': 250,
        'retic_disponivel': False, 'retic_pct': None, 'ht': None,
        'ferro_disponivel': False, 'ferritina': None,
        'ferro_serico': None, 'tibc': None, 'sat_transf': None,
        'b12': None, 'folato': None, 'creatinina': None, 'tsh': None,
        'eletroforese_hb': False, 'hba2_elevada': None, 'hbf_elevada': None,
        'sangramento_ativo': False, 'ictericia': False, 'esplenomegalia': False,
        'alcool': False, 'vegetariano_vegano': False, 'gastro_cirurgia': False,
        'sintomas_fadiga': True, 'sintomas_dispneia': False,
        'sintomas_palpitacao': False, 'sintomas_neurologico': False,
        'rbc': None,
    }


CASOS = [
    # 1. Sem anemia — Hb normal
    ('sem_anemia_mulher', {**_base(), 'hb': 13.0, 'mcv': 88, 'rdw': 13.0,
                           '_esperado': 'sem_anemia'}),

    # 2. IDA clássica — ferritina baixa, VCM microcítico
    ('ida_classica', {**_base(), 'hb': 9.5, 'mcv': 72, 'rdw': 16.5,
                      'ferro_disponivel': True, 'ferritina': 8.0,
                      '_esperado': 'anemia_ferropriva'}),

    # 3. IDA em doença crônica — ferritina 60 (abaixo de 100)
    ('ida_doenca_cronica', {**_base(doenca_cronica=True),
                             'hb': 9.0, 'mcv': 76, 'rdw': 15.5,
                             'ferro_disponivel': True, 'ferritina': 60.0,
                             '_esperado': 'anemia_ferropriva'}),

    # 4. IDA intermediária — ferritina 35 + sat transf < 20%
    ('ida_sat_transf', {**_base(), 'hb': 10.2, 'mcv': 75, 'rdw': 15.0,
                        'ferro_disponivel': True, 'ferritina': 35.0, 'sat_transf': 15.0,
                        '_esperado': 'anemia_ferropriva'}),

    # 5. Traço de beta-talassemia — eletroforese + HbA2 elevada
    ('talassemia_beta', {**_base(), 'hb': 10.5, 'mcv': 65, 'rdw': 12.5,
                         'rbc': 5.8,
                         'ferro_disponivel': True, 'ferritina': 80.0,
                         'eletroforese_hb': True, 'hba2_elevada': True, 'hbf_elevada': False,
                         '_esperado': 'talassemia_beta'}),

    # 6. Alfa-talassemia suspeita — eletroforese + HbA2 normal
    ('talassemia_alfa', {**_base(), 'hb': 10.8, 'mcv': 68, 'rdw': 12.0,
                         'ferro_disponivel': True, 'ferritina': 90.0,
                         'eletroforese_hb': True, 'hba2_elevada': False, 'hbf_elevada': False,
                         '_esperado': 'talassemia_alfa'}),

    # 7. Anemia hemolítica — VCM normal, RPI alto
    ('hemolitica', {**_base(), 'hb': 8.5, 'mcv': 90, 'rdw': 17.0,
                    'retic_disponivel': True, 'retic_pct': 8.5, 'ht': 26.0,
                    'ictericia': True,
                    '_esperado': 'anemia_hemolitica'}),

    # 8. Anemia renal — VCM normal, creatinina elevada
    ('anemia_renal', {**_base(sexo='masculino'), 'hb': 9.0, 'mcv': 86, 'rdw': 13.5,
                      'retic_disponivel': True, 'retic_pct': 1.2, 'ht': 27.0,
                      'creatinina': 2.8,
                      '_esperado': 'anemia_renal'}),

    # 9. Deficiência de B12 — VCM macrocítico
    ('def_b12', {**_base(sexo='masculino'), 'hb': 10.0, 'mcv': 108, 'rdw': 16.5,
                 'b12': 140.0,
                 '_esperado': 'anemia_b12'}),

    # 10. Deficiência de folato — VCM macrocítico, B12 normal
    ('def_folato', {**_base(), 'hb': 10.5, 'mcv': 105, 'rdw': 16.0,
                    'b12': 350.0, 'folato': 1.2, 'alcool': True,
                    '_esperado': 'anemia_folato'}),

    # 11. Pancitopenia → encaminhamento urgente
    ('pancitopenia', {**_base(), 'hb': 7.5, 'mcv': 88, 'rdw': 14.0,
                      'wbc': 2.1, 'plt': 80,
                      '_esperado': 'pancitopenia'}),

    # 12. Anemia por sangramento agudo — normocítica + RPI alto + sangramento
    ('sangramento_agudo', {**_base(), 'hb': 8.0, 'mcv': 87, 'rdw': 13.5,
                           'retic_disponivel': True, 'retic_pct': 6.0, 'ht': 24.0,
                           'sangramento_ativo': True,
                           '_esperado': 'anemia_sangramento'}),

    # 13. Macrocitose alcoólica — VCM alto, B12/folato normais, álcool
    ('alcool', {**_base(sexo='masculino'), 'hb': 11.5, 'mcv': 104, 'rdw': 15.5,
                'b12': 400.0, 'folato': 5.0, 'tsh': 1.8, 'alcool': True,
                '_esperado': 'anemia_alcool'}),
]


def main():
    print('\n' + '=' * 54)
    print('  SMOKE TESTS — ENGINE ANEMIA')
    print('=' * 54)
    resultados = [_run(nome, dados) for nome, dados in CASOS]
    total = len(resultados)
    passou = sum(resultados)
    print(f'\n  Resultado: {passou}/{total} OK')
    print('=' * 54)
    return passou == total


if __name__ == '__main__':
    ok = main()
    sys.exit(0 if ok else 1)
