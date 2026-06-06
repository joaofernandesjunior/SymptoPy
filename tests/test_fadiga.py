# tests/test_fadiga.py
# Smoke tests — engine de Fadiga
# Rodar: python tests/test_fadiga.py

import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.raciocinio.fadiga.engine_fadiga import interpretar_fadiga


def _run(caso, dados):
    esp = dados.pop('_esperado')
    r   = interpretar_fadiga(dados)
    cat = r.get('categoria', '')
    ok  = cat == esp
    st  = 'OK  ' if ok else 'FAIL'
    print(f'[{st}] {caso} -> {cat}  (esp: {esp})')
    if not ok:
        print(f'       stopbang={r.get("stopbang")}, phq2={r.get("phq2")}, gad2={r.get("gad2")}')
    return ok


def _base():
    return {
        # STOP-BANG todos negativos
        'sb_ronco': False, 'sb_cansaco_diurno': False, 'sb_apneia_observada': False,
        'sb_pressao_alta': False, 'sb_imc_35': False, 'sb_idade_50': False,
        'sb_pescoco_40': False, 'sb_masculino': False,
        # PHQ-2 / GAD-2
        'phq2_total': 0, 'gad2_total': 0,
        # PEM e critérios IOM 2015 — campo exato do engine
        'pem_presente': False,
        'sono_nao_reparador': False,
        'duracao_meses': 3,
        'reducao_atividade_substancial': False,
        'fadiga_nova_onset': True,
        'brain_fog': False,
        'intolerancia_ortostatica': False,
        # Red flags
        'perda_peso_involuntaria': False, 'febre_persistente': False,
        'linfadenopatia_fixa': False, 'deficit_neurologico_focal': False,
        'sangramento': False, 'dispneia_esforco_progressiva': False,
        'hepatoesplenomegalia': False, 'massa_palpavel': False,
        # Laboratorial — valores reais que o engine lê
        'tsh': None, 'ferritina': None, 'hba1c': None,
        'glicemia_jejum': None, 'hemoglobina': None,
        'creatinina': None, 'alt': None,
    }


CASOS = [
    # 1. Red flag: perda de peso ≥ 5%
    dict(_base(), perda_peso_involuntaria=True, perda_peso_pct=7.0,
         _esperado='fadiga_red_flags'),

    # 2. Red flag: febre persistente
    dict(_base(), febre_persistente=True, _esperado='fadiga_red_flags'),

    # 3. Red flag: linfadenopatia fixa
    dict(_base(), linfadenopatia_fixa=True, _esperado='fadiga_red_flags'),

    # 4. Causa laboratorial: hipotireoidismo (TSH > 10)
    dict(_base(), labs_disponiveis=True, tsh=12.5,
         _esperado='fadiga_secundaria_laboratorial'),

    # 5. Causa laboratorial: anemia (Hb abaixo do limiar — mulher: < 12 g/dL)
    dict(_base(), labs_disponiveis=True, hemoglobina=10.5, sexo_feminino=True,
         _esperado='fadiga_secundaria_laboratorial'),

    # 6. Apneia — STOP-BANG ≥ 5
    dict(_base(), sb_ronco=True, sb_cansaco_diurno=True, sb_apneia_observada=True,
         sb_pressao_alta=True, sb_imc_35=True, sb_masculino=True,
         _esperado='fadiga_secundaria_apneia'),

    # 7. Psiquiátrica — PHQ-2 ≥ 3, sem PEM
    dict(_base(), phq2_total=4, pem_presente=False,
         _esperado='fadiga_secundaria_psiquiatrica'),

    # 8. ME/SFC — critérios IOM completos (brain_fog)
    dict(_base(),
         duracao_meses=8, reducao_atividade_substancial=True, fadiga_nova_onset=True,
         pem_presente=True, sono_nao_reparador=True, brain_fog=True,
         _esperado='fadiga_me_sfc'),

    # 9. ME/SFC com intolerância ortostática em vez de brain_fog
    dict(_base(),
         duracao_meses=7, reducao_atividade_substancial=True, fadiga_nova_onset=True,
         pem_presente=True, sono_nao_reparador=True, intolerancia_ortostatica=True,
         _esperado='fadiga_me_sfc'),

    # 10. Idiopática — nada se encaixa acima
    dict(_base(), _esperado='fadiga_idiopatica_subaguda'),

    # 11. IOM incompleto (sem PEM) → idiopática mesmo com outros critérios
    dict(_base(),
         duracao_meses=8, reducao_atividade_substancial=True, fadiga_nova_onset=True,
         pem_presente=False, sono_nao_reparador=True, brain_fog=True,
         _esperado='fadiga_idiopatica_subaguda'),
]


def _check_pente_fino():
    ok = True

    # ME/SFC → alerta GET contraindicado
    d = dict(_base())
    d.update(duracao_meses=8, reducao_atividade_substancial=True, fadiga_nova_onset=True,
             pem_presente=True, sono_nao_reparador=True, brain_fog=True)
    r = interpretar_fadiga(d)
    tem = any('CONTRAINDICADO' in a or 'GET' in a
              for a in r.get('alertas_seguranca', []))
    st = 'OK  ' if tem else 'FAIL'
    print(f'[{st}] pente_fino_me_sfc_get -> alertas_seguranca GET? {tem}')
    ok = ok and tem

    # Psiquiátrica → alerta suicídio
    d2 = dict(_base(), phq2_total=5)
    r2 = interpretar_fadiga(d2)
    tem2 = any('suicida' in a.lower() or 'suicídio' in a
               for a in r2.get('alertas_seguranca', []))
    st2 = 'OK  ' if tem2 else 'FAIL'
    print(f'[{st2}] pente_fino_psiq_suicidio -> alertas_seguranca suicídio? {tem2}')
    ok = ok and tem2

    return ok


if __name__ == '__main__':
    print('=' * 50)
    print('FADIGA — testes de regressão')
    print('=' * 50)
    total = 0
    passed = 0
    for i, caso in enumerate(CASOS, 1):
        total += 1
        if _run(f'caso_{i:02d}', caso):
            passed += 1

    print()
    print('Pente fino:')
    pf_ok = _check_pente_fino()
    if pf_ok:
        passed += 2
    total += 2

    print()
    print('=' * 50)
    print(f'{passed}/{total} testes passaram')
    if passed < total:
        sys.exit(1)
