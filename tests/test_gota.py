# tests/test_gota.py
# Smoke tests — engine de Gota
# Rodar: python tests/test_gota.py

import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.raciocinio.gota.engine_gota import interpretar_gota


def _run(caso, dados):
    r   = interpretar_gota(dados)
    cat = r.get('categoria', '')
    esp = dados.pop('_esperado', None)
    ok  = cat == esp
    status = 'OK  ' if ok else 'FAIL'
    print(f'[{status}] {caso} -> {cat}  (esp: {esp})')
    if not ok:
        print(f'       score_dutch={r.get("score_dutch")}, red_flags={r.get("red_flags",[])}')
    return ok


def _base_ataque():
    return {
        'ataque_atual': True,
        'fase_identificada': None,
        'sexo_masculino': True,
        'ataque_previo': True,
        'inicio_em_1_dia': True,
        'vermelhidao': True,
        'articulacao_mtf1': True,
        'has_ou_cardiovascular': False,
        'urato_mgdl': None,
        'febre_385': False,
        'aparencia_toxica': False,
        'imunossupressao': False,
        'tophi_presentes': False,
        'gota_confirmada_previa': False,
        'n_ataques_ano': 1,
        'egfr': 75,
        'idade': 45,
    }


CASOS = [

    # 1. Dutch ≥ 8 → provável
    dict(_base_ataque(), urato_mgdl=7.5, _esperado='gota_provavel_ataque_agudo'),

    # 2. Dutch 4-7 → possível (sem podagra, sem prévio, sem sexo)
    dict(**{
        'ataque_atual': True, 'fase_identificada': None,
        'sexo_masculino': False, 'ataque_previo': False,
        'inicio_em_1_dia': True, 'vermelhidao': True,
        'articulacao_mtf1': True, 'has_ou_cardiovascular': False,
        'urato_mgdl': 5.0,
        'febre_385': False, 'aparencia_toxica': False, 'imunossupressao': False,
        'tophi_presentes': False, 'gota_confirmada_previa': False,
        'n_ataques_ano': 1, 'egfr': 80, 'idade': 35,
        '_esperado': 'gota_possivel_ataque_agudo',
    }),

    # 3. Dutch < 4 → improvável
    dict(**{
        'ataque_atual': True, 'fase_identificada': None,
        'sexo_masculino': False, 'ataque_previo': False,
        'inicio_em_1_dia': False, 'vermelhidao': False,
        'articulacao_mtf1': False, 'has_ou_cardiovascular': False,
        'urato_mgdl': 4.0,
        'febre_385': False, 'aparencia_toxica': False, 'imunossupressao': False,
        'tophi_presentes': False, 'gota_confirmada_previa': False,
        'n_ataques_ano': 1, 'egfr': 90, 'idade': 30,
        '_esperado': 'gota_improvavel_ataque_agudo',
    }),

    # 4. Febre ≥ 38.5 → artrite séptica a excluir
    dict(_base_ataque(), febre_385=True, _esperado='gota_artrite_septica_excluir'),

    # 5. Aparência tóxica → artrite séptica a excluir
    dict(_base_ataque(), aparencia_toxica=True, _esperado='gota_artrite_septica_excluir'),

    # 6. Tophi → gota tofácea
    dict(**{
        'ataque_atual': False, 'fase_identificada': None,
        'tophi_presentes': True,
        'sexo_masculino': True, 'ataque_previo': True,
        'inicio_em_1_dia': False, 'vermelhidao': False,
        'articulacao_mtf1': False, 'has_ou_cardiovascular': False,
        'urato_mgdl': 8.0,
        'febre_385': False, 'aparencia_toxica': False, 'imunossupressao': False,
        'gota_confirmada_previa': True,
        'n_ataques_ano': 3, 'egfr': 60, 'idade': 55,
        '_esperado': 'gota_tofacea',
    }),

    # 7. Interataque — sem tophi, sem ataque atual
    dict(**{
        'ataque_atual': False, 'fase_identificada': None,
        'tophi_presentes': False,
        'sexo_masculino': True, 'ataque_previo': True,
        'inicio_em_1_dia': False, 'vermelhidao': False,
        'articulacao_mtf1': False, 'has_ou_cardiovascular': False,
        'urato_mgdl': 7.0,
        'febre_385': False, 'aparencia_toxica': False, 'imunossupressao': False,
        'gota_confirmada_previa': True,
        'n_ataques_ano': 2, 'egfr': 80, 'idade': 50,
        '_esperado': 'gota_interataque',
    }),

    # 8. AINE trava: idade ≥ 60 → alerta no resultado
    dict(**{
        'ataque_atual': True, 'fase_identificada': None,
        'sexo_masculino': True, 'ataque_previo': True,
        'inicio_em_1_dia': True, 'vermelhidao': True,
        'articulacao_mtf1': True, 'has_ou_cardiovascular': True,
        'urato_mgdl': 7.0,
        'febre_385': False, 'aparencia_toxica': False, 'imunossupressao': False,
        'tophi_presentes': False, 'gota_confirmada_previa': False,
        'n_ataques_ano': 1, 'egfr': 55, 'idade': 65,
        '_esperado': 'gota_provavel_ataque_agudo',
    }),

    # 9. eGFR < 30 → alerta colchicina
    dict(**{
        'ataque_atual': True, 'fase_identificada': None,
        'sexo_masculino': True, 'ataque_previo': True,
        'inicio_em_1_dia': True, 'vermelhidao': True,
        'articulacao_mtf1': True, 'has_ou_cardiovascular': True,
        'urato_mgdl': 8.0,
        'febre_385': False, 'aparencia_toxica': False, 'imunossupressao': False,
        'tophi_presentes': False, 'gota_confirmada_previa': False,
        'n_ataques_ano': 1, 'egfr': 20, 'idade': 70,
        '_esperado': 'gota_provavel_ataque_agudo',
    }),
]


def _check_pente_fino():
    """Verifica que alertas_seguranca aparecem onde esperado."""
    ok = True

    # AINE trava: idade 65 → alerta deve estar presente
    d = {
        'ataque_atual': True, 'fase_identificada': None,
        'sexo_masculino': True, 'ataque_previo': True,
        'inicio_em_1_dia': True, 'vermelhidao': True,
        'articulacao_mtf1': True, 'has_ou_cardiovascular': True,
        'urato_mgdl': 7.0, 'febre_385': False, 'aparencia_toxica': False,
        'imunossupressao': False, 'tophi_presentes': False,
        'gota_confirmada_previa': False, 'n_ataques_ano': 1,
        'egfr': 55, 'idade': 65,
    }
    r = interpretar_gota(d)
    tem_alerta = any('CONTRAINDICADO' in a or 'AINE' in a
                     for a in r.get('alertas_seguranca', []))
    status = 'OK  ' if tem_alerta else 'FAIL'
    print(f'[{status}] pente_fino_aine_idoso -> alertas_seguranca tem AINE? {tem_alerta}')
    ok = ok and tem_alerta

    # eGFR < 30 → alerta colchicina
    d2 = dict(d, egfr=20, idade=70)
    r2 = interpretar_gota(d2)
    tem_egfr = any('eGFR' in a or 'olchicina' in a
                   for a in r2.get('alertas_seguranca', []))
    status2 = 'OK  ' if tem_egfr else 'FAIL'
    print(f'[{status2}] pente_fino_colchicina_egfr -> alertas_seguranca tem eGFR? {tem_egfr}')
    ok = ok and tem_egfr

    return ok


if __name__ == '__main__':
    print('=' * 50)
    print('GOTA — testes de regressão')
    print('=' * 50)
    total = 0
    passed = 0
    for caso in CASOS:
        esp = caso.pop('_esperado', None)
        caso['_esperado'] = esp
        total += 1
        if _run(f'caso_{total:02d}', caso):
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
