# _teste_fadiga.py
# Testes unitários do engine de fadiga crônica
# Rodar da raiz: python _teste_fadiga.py

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.dirname(__file__))

from modules.raciocinio.fadiga.engine_fadiga import interpretar_fadiga

PASSOU  = 0
FALHOU  = 0
ERROS   = []


def _testar(nome, dados, categoria_esperada):
    global PASSOU, FALHOU, ERROS
    try:
        resultado = interpretar_fadiga(dados)
        cat_obtida = resultado.get('categoria', '')
        if cat_obtida == categoria_esperada:
            print(f'  [OK] {nome}')
            PASSOU += 1
        else:
            print(f'  [FALHOU] {nome}')
            print(f'           Esperado : {categoria_esperada}')
            print(f'           Obtido   : {cat_obtida}')
            FALHOU += 1
            ERROS.append(nome)
    except Exception as e:
        print(f'  [ERRO] {nome} — {e}')
        FALHOU += 1
        ERROS.append(nome)


# =============================================================================
# CASOS DE TESTE
# =============================================================================

print('\n' + '=' * 54)
print('  TESTE — Engine: Fadiga Crônica')
print('=' * 54)

# ── TC01: Red flag — perda de peso ≥ 5% ──────────────────────────────────────
_testar(
    'TC01 — Red flag (perda de peso ≥ 5%)',
    {
        'perda_peso_involuntaria': True,
        'perda_peso_pct': 7.0,
        'labs_disponiveis': False,
        'stopbang_total': 0,
        'phq2_total': 0,
        'gad2_total': 0,
        'pem_presente': False,
        'duracao_meses': 3,
        'reducao_atividade_substancial': False,
        'fadiga_nova_onset': True,
        'sono_nao_reparador': False,
        'brain_fog': False,
        'intolerancia_ortostatica': False,
    },
    'fadiga_red_flags',
)

# ── TC02: Red flag — ideação suicida ─────────────────────────────────────────
_testar(
    'TC02 — Red flag (ideação suicida ativa)',
    {
        'perda_peso_involuntaria': False,
        'perda_peso_pct': 0,
        'ideacao_suicida_ativa': True,
        'labs_disponiveis': False,
        'stopbang_total': 1,
        'phq2_total': 2,
        'gad2_total': 1,
        'pem_presente': False,
        'duracao_meses': 2,
        'reducao_atividade_substancial': False,
        'fadiga_nova_onset': True,
        'sono_nao_reparador': False,
        'brain_fog': False,
        'intolerancia_ortostatica': False,
    },
    'fadiga_red_flags',
)

# ── TC03: Causa laboratorial — TSH = 15 ──────────────────────────────────────
_testar(
    'TC03 — Laboratorial (TSH = 15 mIU/L — hipotireoidismo franco)',
    {
        'perda_peso_involuntaria': False,
        'perda_peso_pct': 0,
        'labs_disponiveis': True,
        'sexo_feminino': True,
        'tsh': 15.0,
        'hemoglobina': 13.5,
        'ferritina': 30.0,
        'hba1c': 5.4,
        'glicemia_jejum': 88.0,
        'creatinina': 0.9,
        'alt': 28.0,
        'stopbang_total': 0,
        'phq2_total': 0,
        'gad2_total': 0,
        'pem_presente': False,
        'duracao_meses': 5,
        'reducao_atividade_substancial': False,
        'fadiga_nova_onset': True,
        'sono_nao_reparador': False,
        'brain_fog': False,
        'intolerancia_ortostatica': False,
    },
    'fadiga_secundaria_laboratorial',
)

# ── TC04: Causa laboratorial — ferritina = 8 ─────────────────────────────────
_testar(
    'TC04 — Laboratorial (Ferritina = 8 ng/mL — deficiência de ferro)',
    {
        'perda_peso_involuntaria': False,
        'perda_peso_pct': 0,
        'labs_disponiveis': True,
        'sexo_feminino': True,
        'tsh': 2.1,
        'hemoglobina': 12.8,
        'ferritina': 8.0,
        'hba1c': 5.2,
        'glicemia_jejum': 92.0,
        'creatinina': 0.8,
        'alt': 22.0,
        'stopbang_total': 0,
        'phq2_total': 1,
        'gad2_total': 1,
        'pem_presente': False,
        'duracao_meses': 4,
        'reducao_atividade_substancial': False,
        'fadiga_nova_onset': True,
        'sono_nao_reparador': False,
        'brain_fog': False,
        'intolerancia_ortostatica': False,
    },
    'fadiga_secundaria_laboratorial',
)

# ── TC05: Apneia — STOP-BANG = 5 ─────────────────────────────────────────────
_testar(
    'TC05 — Apneia (STOP-BANG = 5 — alto risco AOS)',
    {
        'perda_peso_involuntaria': False,
        'perda_peso_pct': 0,
        'labs_disponiveis': True,
        'sexo_feminino': False,
        'tsh': 2.5,
        'hemoglobina': 15.0,
        'ferritina': 45.0,
        'hba1c': 5.5,
        'glicemia_jejum': 95.0,
        'creatinina': 0.9,
        'alt': 30.0,
        # STOP-BANG individual (engine calcula o total se ausente)
        'sb_ronco':            True,
        'sb_cansaco_diurno':   True,
        'sb_apneia_observada': True,
        'sb_pressao_alta':     True,
        'sb_imc_35':           True,
        'sb_idade_50':         False,
        'sb_pescoco_40':       False,
        'sb_masculino':        False,
        # sem stopbang_total pré-calculado — engine deve calcular
        'phq2_total': 1,
        'gad2_total': 0,
        'pem_presente': False,
        'duracao_meses': 6,
        'reducao_atividade_substancial': True,
        'fadiga_nova_onset': True,
        'sono_nao_reparador': True,
        'brain_fog': False,
        'intolerancia_ortostatica': False,
    },
    'fadiga_secundaria_apneia',
)

# ── TC06: Psiquiátrica — PHQ-2 ≥ 3, sem PEM ─────────────────────────────────
_testar(
    'TC06 — Psiquiátrica (PHQ-2 = 4, GAD-2 = 3, PEM ausente)',
    {
        'perda_peso_involuntaria': False,
        'perda_peso_pct': 0,
        'labs_disponiveis': True,
        'sexo_feminino': True,
        'tsh': 2.0,
        'hemoglobina': 13.2,
        'ferritina': 28.0,
        'hba1c': 5.3,
        'glicemia_jejum': 90.0,
        'creatinina': 0.7,
        'alt': 20.0,
        'stopbang_total': 2,
        'phq2_total': 4,
        'gad2_total': 3,
        'pem_presente': False,   # sem PEM — diferencia de ME/SFC
        'duracao_meses': 3,
        'reducao_atividade_substancial': True,
        'fadiga_nova_onset': True,
        'sono_nao_reparador': True,
        'brain_fog': False,
        'intolerancia_ortostatica': False,
    },
    'fadiga_secundaria_psiquiatrica',
)

# ── TC07: ME/SFC — critérios IOM 2015 completos ──────────────────────────────
_testar(
    'TC07 — ME/SFC (IOM 2015 completo: tríade + brain fog + 7 meses)',
    {
        'perda_peso_involuntaria': False,
        'perda_peso_pct': 0,
        'labs_disponiveis': True,
        'sexo_feminino': True,
        'tsh': 1.8,
        'hemoglobina': 13.5,
        'ferritina': 35.0,
        'hba1c': 5.1,
        'glicemia_jejum': 88.0,
        'creatinina': 0.8,
        'alt': 18.0,
        'stopbang_total': 1,
        'phq2_total': 2,
        'gad2_total': 1,
        'pem_presente': True,
        'duracao_meses': 7,
        'reducao_atividade_substancial': True,
        'fadiga_nova_onset': True,
        'sono_nao_reparador': True,
        'brain_fog': True,
        'intolerancia_ortostatica': False,
    },
    'fadiga_me_sfc',
)

# ── TC08: Idiopática — critérios incompletos (sem PEM, sem sono não-reparador)
_testar(
    'TC08 — Idiopática/subaguda (PEM ausente, sono reparador, 4 meses — NICE possível)',
    {
        'perda_peso_involuntaria': False,
        'perda_peso_pct': 0,
        'labs_disponiveis': True,
        'sexo_feminino': False,
        'tsh': 2.3,
        'hemoglobina': 14.8,
        'ferritina': 50.0,
        'hba1c': 5.4,
        'glicemia_jejum': 91.0,
        'creatinina': 0.95,
        'alt': 25.0,
        'stopbang_total': 2,
        'phq2_total': 1,
        'gad2_total': 2,
        'pem_presente': False,    # falta PEM
        'duracao_meses': 4,
        'reducao_atividade_substancial': True,
        'fadiga_nova_onset': True,
        'sono_nao_reparador': False,  # falta sono não-reparador
        'brain_fog': False,
        'intolerancia_ortostatica': False,
    },
    'fadiga_idiopatica_subaguda',
)

# =============================================================================
# RESUMO
# =============================================================================

print()
print('─' * 54)
total = PASSOU + FALHOU
print(f'  Resultado: {PASSOU}/{total} testes passaram')
if ERROS:
    print(f'  Falhos: {", ".join(ERROS)}')
print('─' * 54)
sys.exit(0 if FALHOU == 0 else 1)
