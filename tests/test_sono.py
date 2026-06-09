# tests/test_sono.py
# Smoke tests — engine de transtornos do sono
# Rodar: python tests/test_sono.py

import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.raciocinio.sono.engine_sono import interpretar_sono


def _base():
    return {
        'isi_score': 12, 'stopbang_score': 1, 'epworth_score': 6,
        'stopbang_itens': {'masculino': False},
        'spi_criterios': 0, 'spi_urge_mover': False,
        'spi_piora_repouso': False, 'spi_melhora_movimento': False, 'spi_piora_noite': False,
        'cataplexia': False, 'alucinacao_adormecer': False,
        'paralisia_sono': False, 'sono_diurno_irresistivel': False,
        'tcr_rem_age_sonhos': False, 'idade_tcr': 0,
        'ranger_dentes': False, 'dor_mandibula_manha': False,
        'cefaleia_temporal_manha': False, 'desgaste_dentario': False,
        'dor_atm': False, 'masseter_hipertrofia': False, 'desgaste_incisal': False,
        'isrs_em_uso': False,
        'dorme_bem_horario_proprio': False, 'dificuldade_iniciar': False,
        'sonambulismo': False, 'terror_noturno': False,
        'pesadelos_freq': False, 'pesadelos_trauma': False,
        'benzo_em_uso': False, 'benzo_semanas': 0, 'benzo_qual': '', 'benzo_dose': '',
        'depressao_ansiedade': False, 'phq2_score': 0,
        'dor_cronica_noturna': False, 'turno_irregular': False,
        'tsh_disponivel': False, 'tsh_valor': None,
        'ferritina_disponivel': False, 'ferritina_valor': None,
        'horas_cama': 8, 'horas_sono': 6,
        'duracao_semanas': 16, 'noites_por_semana': 4,
        'so_em_casa': False,
        'tela_na_cama': False, 'alcool_para_dormir': False,
        'cama_escritorio': False, 'exercicio_noturno': False,
        'horario_cama_fixo': True, 'cochilo_diurno': False, 'cochilo_duracao_min': 0,
        'imc': 24.0, 'circunferencia_cervical_cm': 36.0, 'mallampati': 1,
        'atm_dor_palpacao': False, 'abertura_bucal_mm': 45,
    }


def _run(nome, dados, esperado):
    r = interpretar_sono(dados)
    cat = r.get('categoria', '')
    ok  = cat == esperado
    print(f'  {"✓" if ok else "✗"} [{nome}] → {cat}  (esperado: {esperado})')
    if not ok:
        print(f'      diag: {r.get("diagnostico", "")}')
    return ok


CASOS = [
    # 1. TCR-REM > 50 anos → pré-Parkinson
    ('tcr_rem_pre_parkinson',
     {**_base(), 'tcr_rem_age_sonhos': True, 'idade_tcr': 55},
     'tcr_rem_pre_parkinson'),

    # 2. Narcolepsia — cataplexia + sono irresistível + paralisia
    ('narcolepsia',
     {**_base(), 'cataplexia': True, 'sono_diurno_irresistivel': True, 'paralisia_sono': True},
     'narcolepsia_suspeita'),

    # 3. AOS — STOP-BANG 5
    ('aos_stopbang5',
     {**_base(), 'stopbang_score': 5,
      'stopbang_itens': {'masculino': True, 'ronco': True, 'cansaco': True,
                         'apneia_obs': True, 'has': True, 'imc35': True,
                         'idade50': False, 'pescoco': False},
      'epworth_score': 8},
     'aos_suspeita'),

    # 4. SPI — 4 critérios
    ('spi_completo',
     {**_base(), 'spi_criterios': 4, 'spi_urge_mover': True,
      'spi_piora_repouso': True, 'spi_melhora_movimento': True, 'spi_piora_noite': True},
     'spi'),

    # 5. Bruxismo — 3 critérios
    ('bruxismo',
     {**_base(), 'ranger_dentes': True, 'dor_mandibula_manha': True,
      'cefaleia_temporal_manha': True},
     'bruxismo_sono'),

    # 6. Bruxismo + ISRS
    ('bruxismo_isrs',
     {**_base(), 'ranger_dentes': True, 'dor_mandibula_manha': True,
      'desgaste_dentario': True, 'isrs_em_uso': True},
     'bruxismo_sono'),

    # 7. SFAS — dorme bem no horário próprio
    ('sfas',
     {**_base(), 'dorme_bem_horario_proprio': True, 'dificuldade_iniciar': True,
      'stopbang_score': 0, 'spi_criterios': 0},
     'sfas'),

    # 8. Parassonia NREM — sonambulismo
    ('parassonia_nrem',
     {**_base(), 'sonambulismo': True},
     'parassonia_nrem'),

    # 9. Pesadelos + TEPT
    ('pesadelos_tept',
     {**_base(), 'pesadelos_freq': True, 'pesadelos_trauma': True},
     'pesadelos_tept'),

    # 10. Desmame BZD
    ('desmame_benzo',
     {**_base(), 'benzo_em_uso': True, 'benzo_semanas': 12,
      'benzo_qual': 'clonazepam', 'benzo_dose': '1 mg',
      'duracao_semanas': 20, 'noites_por_semana': 5},
     'desmame_benzo'),

    # 11. Insônia comportamental — 4 fatores
    ('insonia_comportamental',
     {**_base(), 'tela_na_cama': True, 'alcool_para_dormir': True,
      'cama_escritorio': True, 'horario_cama_fixo': False,
      'duracao_semanas': 16, 'noites_por_semana': 4},
     'insonia_comportamental'),

    # 12. Insônia psiquiátrica — PHQ2 positivo
    ('insonia_psiquiatrica',
     {**_base(), 'phq2_score': 4, 'depressao_ansiedade': True,
      'duracao_semanas': 10, 'noites_por_semana': 4},
     'insonia_psiquiatrica'),

    # 13. Insônia crônica primária
    ('insonia_cronica_primaria',
     {**_base(), 'isi_score': 16, 'duracao_semanas': 20,
      'noites_por_semana': 5},
     'insonia_cronica_primaria'),
]


def main():
    print('\n' + '=' * 58)
    print('  SMOKE TESTS — ENGINE TRANSTORNOS DO SONO')
    print('=' * 58)
    resultados = [_run(n, d, e) for n, d, e in CASOS]
    total   = len(resultados)
    passou  = sum(resultados)
    print(f'\n  Resultado: {passou}/{total} OK')
    print('=' * 58)
    return passou == total


if __name__ == '__main__':
    ok = main()
    sys.exit(0 if ok else 1)
