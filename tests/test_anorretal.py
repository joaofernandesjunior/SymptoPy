# tests/test_anorretal.py
# Smoke tests — engine de Anorretal
# Rodar: python tests/test_anorretal.py

import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.raciocinio.anorretal.engine_anorretal import interpretar_anorretal


def _run(caso, dados):
    esp = dados.pop('_esperado')
    r   = interpretar_anorretal(dados)
    cat = r.get('categoria', '')
    ok  = cat == esp
    st  = 'OK  ' if ok else 'FAIL'
    print(f'[{st}] {caso} -> {cat}  (esp: {esp})')
    if not ok:
        print(f'       grau={r.get("grau")}, abordagem={r.get("abordagem")}')
    return ok


def _base():
    return {
        'sangramento_novo': False, 'sangue_misturado_fezes': False,
        'perda_peso_involuntaria': False, 'mudanca_habito_intestinal_4sem': False,
        'historia_familiar_ccr': False, 'historia_pessoal_ccr': False,
        'anemia_ferropriva_confirmada': False,
        'idade': 35,
        'sangramento_sem_dor': False, 'prolapso_anorretal': False,
        'dor_durante_defecacao': False, 'sangramento_no_papel': False,
        'sangramento_gotejamento': False, 'sangramento_significativo': False,
        'prurido_perianal': False,
        'prolapso_redutivel': False, 'prolapso_irredutivel': False,
        'prolapso_espontaneo': False, 'prolapso_manual': False,
        'trombose_externa': False, 'horas_desde_trombose': 999,
        'fissura_cronica': False,
    }


CASOS = [
    # 1. Red flag: ≥ 45 anos + sangramento novo
    dict(_base(), idade=50, sangramento_novo=True, sangramento_no_papel=True,
         _esperado='anorretal_colonoscopia_urgente'),

    # 2. Red flag: sangue misturado às fezes
    dict(_base(), sangue_misturado_fezes=True,
         _esperado='anorretal_colonoscopia_urgente'),

    # 3. Red flag: perda de peso
    dict(_base(), perda_peso_involuntaria=True, sangramento_no_papel=True,
         _esperado='anorretal_colonoscopia_urgente'),

    # 4. Red flag: mudança de hábito > 4 semanas
    dict(_base(), mudanca_habito_intestinal_4sem=True,
         _esperado='anorretal_colonoscopia_urgente'),

    # 5. Hemorroida grau I-II (sem prolapso)
    dict(_base(), sangramento_sem_dor=True,
         _esperado='hemorroida_grau_1_2'),

    # 6. Hemorroida grau II (prolapso espontâneo redutível)
    dict(_base(), sangramento_sem_dor=True, prolapso_anorretal=True,
         prolapso_reducao_espontanea=True,
         _esperado='hemorroida_grau_1_2'),

    # 7. Hemorroida grau III (redução manual necessária)
    dict(_base(), sangramento_sem_dor=True, prolapso_anorretal=True,
         prolapso_reducao_manual=True,
         _esperado='hemorroida_grau_3'),

    # 8. Hemorroida grau IV (irredutível)
    dict(_base(), sangramento_sem_dor=True, prolapso_anorretal=True,
         prolapso_irredutivel=True,
         _esperado='hemorroida_grau_4'),

    # 9. Trombosada < 72h → incisão
    dict(_base(), hemorroida_trombosada_externa=True, horas_desde_trombose=48,
         sangramento_sem_dor=True,
         _esperado='hemorroida_trombosada'),

    # 10. Trombosada > 72h → conservador
    dict(_base(), hemorroida_trombosada_externa=True, horas_desde_trombose=100,
         sangramento_sem_dor=True,
         _esperado='hemorroida_trombosada'),

    # 11. Fissura anal aguda
    dict(_base(), dor_durante_defecacao=True, sangramento_no_papel=True,
         _esperado='fissura_anal'),

    # 12. Prurido perianal
    dict(_base(), prurido_perianal=True,
         _esperado='prurido_anal'),
]


def _check_pente_fino():
    ok = True

    # Red flag → alerta não assumir hemorroida
    d = dict(_base(), idade=50, sangramento_novo=True, sangramento_no_papel=True)
    r = interpretar_anorretal(d)
    tem = any('colonoscopia' in a.lower() or 'Red flag' in a or 'CCR' in a
              for a in r.get('alertas_seguranca', []))
    st = 'OK  ' if tem else 'FAIL'
    print(f'[{st}] pente_fino_red_flag_colonoscopia -> alertas presente? {tem}')
    ok = ok and tem

    # Trombose < 72h → alerta janela cirúrgica
    d2 = dict(_base(), hemorroida_trombosada_externa=True, sangramento_sem_dor=True,
              horas_desde_trombose=24)
    r2 = interpretar_anorretal(d2)
    tem2 = any('janela' in a.lower() or 'Incisão' in a or '72h' in a
               for a in r2.get('alertas_seguranca', []))
    st2 = 'OK  ' if tem2 else 'FAIL'
    print(f'[{st2}] pente_fino_trombose_janela -> alerta janela? {tem2}')
    ok = ok and tem2

    return ok


if __name__ == '__main__':
    print('=' * 50)
    print('ANORRETAL — testes de regressão')
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
