# _teste_diarreia.py
# Testes unitários do engine de diarreia no adulto — 13 categorias
# Rodar da raiz: python _teste_diarreia.py

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.dirname(__file__))

from modules.raciocinio.diarreia.engine_diarreia import interpretar_diarreia

PASSOU = 0
FALHOU = 0
ERROS  = []


def _base():
    """Dicionário base mínimo — imunocompetente, sem sepse, sem desidratação."""
    return {
        'imunossuprimido':             False,
        'hiv_diagnosticado':           False,
        'transplante_quimio_biologico':False,
        'corticoide_cronico':          False,
        'cd4_valor':                   None,
        'hipotensao_conhecida':        False,
        'alteracao_consciencia':       False,
        'extremidades_frias':          False,
        'dor_abdominal_peritoneal':    False,
        'sinais_sepse':                False,
        'desidratacao_grau':           'sem',
        'fezes_sanguinolentas':        False,
        'febre_38_5':                  False,
        'atb_recente_3m':              False,
        'internacao_recente_3m':       False,
        'viagem_recente':              False,
        'viagem_asia':                 False,
        'destino_viagem':              '',
        'surto_alimentar':             False,
        'alimento_suspeito':           '',
        'incubacao_horas':             0,
        'piora_com_lacteos':           False,
        'uso_aine_recente':            False,
        'metformina_dose_alta':        False,
        'hematochezia_cronica':        False,
        'perda_peso_involuntaria':     False,
        'anemia_sintomas':             False,
        'hf_ccr_primeiro_grau':        False,
        'nocturna':                    False,
        'piora_com_gluten':            False,
        'piora_estresse':              False,
        'dor_piora_estresse':          False,
        'dor_melhora_evacuacao':       False,
        'medicamentos_suspeitos_diarreia': False,
        'quais_medicamentos_suspeitos':'',
        'calprotectina_disponivel':    False,
        'calprotectina_valor':         None,
        'idade':                       35,
    }


def _testar(nome, dados, categoria_esperada):
    global PASSOU, FALHOU, ERROS
    try:
        resultado  = interpretar_diarreia(dados)
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
        print(f'  [ERRO]   {nome} — {e}')
        FALHOU += 1
        ERROS.append(nome)


# =============================================================================
print('\n' + '=' * 54)
print('  TESTE — Engine: Diarreia no Adulto (13 categorias)')
print('=' * 54)
# =============================================================================

# ── TC01: Imunossuprimido — HIV + CD4 < 50 ───────────────────────────────────
d = _base()
d.update({'duracao_dias': 5, 'hiv_diagnosticado': True, 'imunossuprimido': True,
          'cd4_valor': 30, 'cd4_conhecido': True})
_testar('TC01 — Imunossuprimido (HIV CD4 = 30)', d, 'diarreia_imunossuprimido')

# ── TC02: Sepse ───────────────────────────────────────────────────────────────
d = _base()
d.update({'duracao_dias': 3, 'hipotensao_conhecida': True, 'sinais_sepse': True,
          'desidratacao_grau': 'grave'})
_testar('TC02 — Sepse (hipotensao + sinais_sepse)', d, 'diarreia_sepse')

# ── TC03: Disenteria bacilar — sangue + febre ≥ 38.5°C ───────────────────────
d = _base()
d.update({'duracao_dias': 4, 'fezes_sanguinolentas': True, 'febre_38_5': True})
_testar('TC03 — Disenteria bacilar (sangue + febre)', d, 'diarreia_disenteria_bacilar')

# ── TC04: STEC — sangue SEM febre ────────────────────────────────────────────
d = _base()
d.update({'duracao_dias': 2, 'fezes_sanguinolentas': True, 'febre_38_5': False})
_testar('TC04 — STEC suspeita (sangue sem febre)', d, 'diarreia_stec_suspeita')

# ── TC05: C. difficile — ATB recente ─────────────────────────────────────────
d = _base()
d.update({'duracao_dias': 7, 'atb_recente_3m': True, 'qual_atb_recente': 'Amoxicilina'})
_testar('TC05 — C. difficile (ATB recente, sem sangue/febre)', d, 'diarreia_c_diff')

# ── TC06: Diarreia do viajante — Índia (Ásia) ────────────────────────────────
d = _base()
d.update({'duracao_dias': 3, 'viagem_recente': True, 'destino_viagem': 'India',
          'viagem_asia': True})
_testar('TC06 — Viajante (India — FQ resistencia)', d, 'diarreia_viajante')

# ── TC07: Toxinfecção alimentar ───────────────────────────────────────────────
d = _base()
d.update({'duracao_dias': 1, 'surto_alimentar': True,
          'alimento_suspeito': 'frango grelhado', 'incubacao_horas': 10})
_testar('TC07 — Toxinfeccao alimentar (2+ pessoas, frango, 10h)', d, 'diarreia_toxinfeccao')

# ── TC08: Watery sem alarmes ──────────────────────────────────────────────────
d = _base()
d.update({'duracao_dias': 3})
_testar('TC08 — Aguda watery (viral autolimitada, sem alarmes)', d, 'diarreia_aguda_watery')

# ── TC09: Watery com suspeita de lactose (ainda watery) ──────────────────────
d = _base()
d.update({'duracao_dias': 5, 'piora_com_lacteos': True})
_testar('TC09 — Aguda watery + suspeita de lactose', d, 'diarreia_aguda_watery')

# ── TC10: Persistente 14–30 dias ─────────────────────────────────────────────
d = _base()
d.update({'duracao_dias': 20})
_testar('TC10 — Persistente (20 dias — excluir parasitas)', d, 'diarreia_persistente')

# ── TC11: Crônica — alarme urgente (hematoquesia crônica) ────────────────────
d = _base()
d.update({'duracao_dias': 60, 'hematochezia_cronica': True})
_testar('TC11 — Cronica alarme urgente (hematoquesia)', d, 'diarreia_cronica_alarme_urgente')

# ── TC12: Crônica — DII suspeita (calprotectina = 350) ───────────────────────
d = _base()
d.update({'duracao_dias': 90, 'calprotectina_disponivel': True,
          'calprotectina_valor': 350.0})
_testar('TC12 — DII suspeita (calprotectina = 350 mcg/g)', d, 'diarreia_dii_suspeita')

# ── TC13: Crônica — SII-D (calprotectina = 25) ───────────────────────────────
d = _base()
d.update({'duracao_dias': 90, 'calprotectina_disponivel': True,
          'calprotectina_valor': 25.0,
          'dor_melhora_evacuacao': True, 'piora_estresse': True})
_testar('TC13 — SII-D (calprotectina = 25, padrao funcional)', d, 'diarreia_sii_d')

# ── TC14: Crônica — zona cinzenta (calprotectina = 120) ──────────────────────
d = _base()
d.update({'duracao_dias': 90, 'calprotectina_disponivel': True,
          'calprotectina_valor': 120.0})
_testar('TC14 — Zona cinzenta calprotectina (120 mcg/g)', d, 'diarreia_cronica_alarme_eletivo')

# ── TC15: Crônica — alarme eletivo (perda de peso, sem calprotectina) ────────
d = _base()
d.update({'duracao_dias': 60, 'perda_peso_involuntaria': True, 'perda_peso_kg': 5.0})
_testar('TC15 — Cronica alarme eletivo (perda de peso)', d, 'diarreia_cronica_alarme_eletivo')

# =============================================================================
print()
print('─' * 54)
total = PASSOU + FALHOU
print(f'  Resultado: {PASSOU}/{total} testes passaram')
if ERROS:
    print(f'  Falhos: {", ".join(ERROS)}')
print('─' * 54)
sys.exit(0 if FALHOU == 0 else 1)
