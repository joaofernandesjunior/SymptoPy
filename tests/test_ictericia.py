# tests/test_ictericia.py
# Smoke tests — engine de Icterícia
# Rodar: python tests/test_ictericia.py

import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.raciocinio.ictericia.engine_ictericia import interpretar_ictericia


def _run(caso, dados):
    esp = dados.pop('_esperado')
    r   = interpretar_ictericia(dados)
    cat = r.get('categoria', '')
    ok  = cat == esp
    st  = 'OK  ' if ok else 'FAIL'
    print(f'[{st}] {caso} -> {cat}  (esp: {esp})')
    if not ok:
        print(f'       causas={r.get("causas",[])}')
    return ok


CASOS = [
    # 1. Tríade de Charcot → emergência
    {
        'ictericia': True, 'febre': True, 'dor_hcd': True,
        'hipotensao': False, 'alt_consciencia': False,
        'inr_maior_1_5': False, 'encefalopatia_hepatica': False,
        'perda_peso_involuntaria': False,
        '_esperado': 'ictericia_emergencia',
    },
    # 2. Pêntade de Reynolds → emergência
    {
        'ictericia': True, 'febre': True, 'dor_hcd': True,
        'hipotensao': True, 'alt_consciencia': True,
        'inr_maior_1_5': False, 'encefalopatia_hepatica': False,
        'perda_peso_involuntaria': False,
        '_esperado': 'ictericia_emergencia',
    },
    # 3. IHA → emergência
    {
        'ictericia': True, 'febre': False, 'dor_hcd': False,
        'hipotensao': False, 'alt_consciencia': False,
        'inr_maior_1_5': True, 'encefalopatia_hepatica': True,
        'perda_peso_involuntaria': False,
        '_esperado': 'ictericia_emergencia',
    },
    # 4. Malignidade → emergência
    {
        'ictericia': True, 'perda_peso_involuntaria': True,
        'febre': False, 'dor_hcd': False,
        'hipotensao': False, 'alt_consciencia': False,
        'inr_maior_1_5': False, 'encefalopatia_hepatica': False,
        '_esperado': 'ictericia_emergencia',
    },
    # 5. Gilbert — sem enzimas elevadas
    {
        'ictericia': True, 'febre': False, 'dor_hcd': False,
        'hipotensao': False, 'alt_consciencia': False,
        'inr_maior_1_5': False, 'encefalopatia_hepatica': False,
        'perda_peso_involuntaria': False,
        'gilbert_previamente_diagnosticado': True,
        '_esperado': 'ictericia_gilbert',
    },
    # 6. Hemolítica — bilirrubina indireta predominante
    {
        'ictericia': True, 'febre': False, 'dor_hcd': False,
        'hipotensao': False, 'alt_consciencia': False,
        'inr_maior_1_5': False, 'encefalopatia_hepatica': False,
        'perda_peso_involuntaria': False,
        'bilirrubina_direta': 0.5, 'bilirrubina_indireta': 4.0,
        'alt_u_l': 0, 'ast_u_l': 0, 'alp_u_l': 0, 'ggt_u_l': 0,
        'gilbert_previamente_diagnosticado': False,
        '_esperado': 'ictericia_hemolitica',
    },
    # 7. Hepatocelular — ALT elevado
    {
        'ictericia': True, 'febre': False, 'dor_hcd': False,
        'hipotensao': False, 'alt_consciencia': False,
        'inr_maior_1_5': False, 'encefalopatia_hepatica': False,
        'perda_peso_involuntaria': False,
        'alt_u_l': 320, 'ast_u_l': 200, 'alp_u_l': 80, 'ggt_u_l': 60,
        'bilirrubina_direta': 2.0, 'bilirrubina_indireta': 1.0,
        'gilbert_previamente_diagnosticado': False,
        'uso_alcool_excessivo': False, 'medicamento_hepatotoxico': False,
        '_esperado': 'ictericia_hepatocelular',
    },
    # 8. Colestática obstrutiva (ductos dilatados)
    {
        'ictericia': True, 'febre': False, 'dor_hcd': False,
        'hipotensao': False, 'alt_consciencia': False,
        'inr_maior_1_5': False, 'encefalopatia_hepatica': False,
        'perda_peso_involuntaria': False,
        'alt_u_l': 50, 'ast_u_l': 40, 'alp_u_l': 350, 'ggt_u_l': 280,
        'bilirrubina_direta': 4.0, 'bilirrubina_indireta': 0.5,
        'ductos_dilatados_us': True,
        'gilbert_previamente_diagnosticado': False,
        '_esperado': 'ictericia_colestatica_obs',
    },
    # 9. Colestática intrahepática (ductos normais)
    {
        'ictericia': True, 'febre': False, 'dor_hcd': False,
        'hipotensao': False, 'alt_consciencia': False,
        'inr_maior_1_5': False, 'encefalopatia_hepatica': False,
        'perda_peso_involuntaria': False,
        'alt_u_l': 50, 'ast_u_l': 40, 'alp_u_l': 300, 'ggt_u_l': 260,
        'bilirrubina_direta': 3.0, 'bilirrubina_indireta': 0.5,
        'ductos_dilatados_us': False,
        'ama_positivo': True,
        'gilbert_previamente_diagnosticado': False,
        '_esperado': 'ictericia_colestatica_intra',
    },
    # 10. Hepatite alcoólica (padrão hepatocelular)
    {
        'ictericia': True, 'febre': False, 'dor_hcd': False,
        'hipotensao': False, 'alt_consciencia': False,
        'inr_maior_1_5': False, 'encefalopatia_hepatica': False,
        'perda_peso_involuntaria': False,
        'alt_u_l': 100, 'ast_u_l': 250, 'alp_u_l': 90, 'ggt_u_l': 200,
        'bilirrubina_direta': 3.0, 'bilirrubina_indireta': 1.0,
        'gilbert_previamente_diagnosticado': False,
        'uso_alcool_excessivo': True,
        '_esperado': 'ictericia_hepatocelular',
    },
]


def _check_pente_fino():
    ok = True

    # Emergência → alerta no topo
    d = {
        'ictericia': True, 'febre': True, 'dor_hcd': True,
        'hipotensao': False, 'alt_consciencia': False,
        'inr_maior_1_5': False, 'encefalopatia_hepatica': False,
        'perda_peso_involuntaria': False,
    }
    r = interpretar_ictericia(d)
    tem = any('EMERGÊNCIA' in a or 'Charcot' in a
              for a in r.get('alertas_seguranca', []))
    st = 'OK  ' if tem else 'FAIL'
    print(f'[{st}] pente_fino_emergencia -> alertas_seguranca presente? {tem}')
    ok = ok and tem

    # Colestase obstrutiva → alerta coagulopatia
    d2 = {
        'ictericia': True, 'febre': False, 'dor_hcd': False,
        'hipotensao': False, 'alt_consciencia': False,
        'inr_maior_1_5': False, 'encefalopatia_hepatica': False,
        'perda_peso_involuntaria': False,
        'alt_u_l': 50, 'ast_u_l': 40, 'alp_u_l': 350, 'ggt_u_l': 280,
        'bilirrubina_direta': 4.0, 'bilirrubina_indireta': 0.5,
        'ductos_dilatados_us': True,
    }
    r2 = interpretar_ictericia(d2)
    tem2 = any('coagulograma' in a or 'vit K' in a or 'obstrutiva' in a.lower()
               for a in r2.get('alertas_seguranca', []))
    st2 = 'OK  ' if tem2 else 'FAIL'
    print(f'[{st2}] pente_fino_colestase_obs -> alertas coagulo? {tem2}')
    ok = ok and tem2

    return ok


if __name__ == '__main__':
    print('=' * 50)
    print('ICTERÍCIA — testes de regressão')
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
