# _teste_arboviroses.py
# Testes unitários — Engine Arboviroses (Dengue / Chikungunya / Zika)
# 24 casos — cobertura 100% das 7 categorias + MS 2025 (8 alarmes, AINE condicional)
# Rodar da raiz: python _teste_arboviroses.py

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.dirname(__file__))

from modules.raciocinio.arboviroses.engine_arboviroses import interpretar_arboviroses

PASSOU = 0
FALHOU = 0
ERROS  = []


def _base():
    """Paciente adulto de 70 kg sem nenhum critério especial."""
    return {
        # Febre
        'febre_presente':      True,
        'dias_febre':          3,
        'febre_alta':          True,
        'inicio_subito':       True,
        # Sintomas sistêmicos
        'cefaleia':            True,
        'mialgia_intensa':     True,
        'dor_retroorbitaria':  True,
        'nausea':              True,
        'vomitos':             False,
        # Exantema
        'exantema_presente':   False,
        'exantema_pruriginoso': False,
        # Artralgia
        'artralgia_presente':      False,
        'artralgia_incapacitante': False,
        'artralgia_simetrica':     False,
        'edema_articular':         False,
        'artralgia_meses':         0,
        # Conjuntivite
        'conjuntivite':              False,
        'conjuntivite_nao_purulenta': False,
        # Sinais de alarme (8 — MS 2025)
        'dor_abdominal_intensa':   False,
        'vomitos_persistentes':    False,
        'acumulo_liquidos':        False,
        'hipotensao_postural':     False,
        'hepatomegalia_referida':  False,
        'sangramento_mucosa':      False,
        'letargia_irritabilidade': False,
        'aumento_hematocrito':     False,
        # NS1 rápido
        'ns1_realizado':           False,
        'ns1_resultado':           'nao_realizado',
        # Sinais de choque
        'hipotensao_severa':   False,
        'pulso_filiforme':     False,
        'tec_maior_3s':        False,
        'sudorese_fria':       False,
        # Prova do laço
        'prova_laco_realizada': False,
        'prova_laco_positiva':  False,
        # Comorbidades
        'gestante':            False,
        'semanas_gestacao':    0,
        'diabetes':            False,
        'has_cardiovascular':  False,
        'hematologica':        False,
        'drc':                 False,
        'doenca_hepatica':     False,
        'obesidade_grave':     False,
        'extremo_idade':       False,
        'risco_social':        False,
        # Dados
        'peso_kg':             70.0,
        'area_endemica':       True,
    }


def _testar(nome, dados, categoria_esperada, checks_extras=None):
    global PASSOU, FALHOU, ERROS
    try:
        resultado = interpretar_arboviroses(dados)
        cat_obtida = resultado.get('categoria', '')
        ok = cat_obtida == categoria_esperada
        if checks_extras:
            for chave, valor in checks_extras.items():
                if resultado.get(chave) != valor:
                    ok = False
                    print(f'  [CHECK FALHOU] {nome}: {chave} esperado={valor} obtido={resultado.get(chave)}')
        if ok:
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
print('\n' + '=' * 60)
print('  TESTE — Engine: Arboviroses (24 casos / MS 2025)')
print('=' * 60)
# =============================================================================

# ── TC01: Grupo D — Choque (hipotensão severa + pulso filiforme) ─────────────
d = _base()
d.update({'hipotensao_severa': True, 'pulso_filiforme': True, 'tec_maior_3s': True})
_testar('TC01 — Grupo D: Choque (hipotensão + pulso filiforme + TEC > 3s)',
        d, 'arboviral_grupo_d',
        {'aine_contraindicado': True, 'internacao': True, 'uti': True})

# ── TC02: Grupo D — Choque por sudorese fria isolada ─────────────────────────
d = _base()
d.update({'sudorese_fria': True, 'tec_maior_3s': True})
_testar('TC02 — Grupo D: Choque por sudorese fria + TEC > 3s',
        d, 'arboviral_grupo_d')

# ── TC03: Grupo C — Dor abdominal intensa ────────────────────────────────────
d = _base()
d.update({'dor_abdominal_intensa': True})
_testar('TC03 — Grupo C: Sinal de alarme — dor abdominal intensa',
        d, 'arboviral_grupo_c',
        {'aine_contraindicado': True, 'internacao': True})

# ── TC04: Grupo C — Vômitos persistentes ─────────────────────────────────────
d = _base()
d.update({'vomitos_persistentes': True})
_testar('TC04 — Grupo C: Sinal de alarme — vomitos persistentes',
        d, 'arboviral_grupo_c')

# ── TC05: Grupo C — Sangramento de mucosa ────────────────────────────────────
d = _base()
d.update({'sangramento_mucosa': True})
_testar('TC05 — Grupo C: Sinal de alarme — sangramento mucosa',
        d, 'arboviral_grupo_c')

# ── TC06: Grupo C — Hipotensão postural ──────────────────────────────────────
d = _base()
d.update({'hipotensao_postural': True})
_testar('TC06 — Grupo C: Sinal de alarme — hipotensao postural',
        d, 'arboviral_grupo_c')

# ── TC07: Grupo C — Letargia / irritabilidade ────────────────────────────────
d = _base()
d.update({'letargia_irritabilidade': True})
_testar('TC07 — Grupo C: Sinal de alarme — letargia/irritabilidade',
        d, 'arboviral_grupo_c')

# ── TC08: Chikungunya — Fase aguda < D5 sem NS1 → AINE PROIBIDO ──────────────
d = _base()
d.update({
    'artralgia_presente': True, 'artralgia_incapacitante': True,
    'artralgia_simetrica': True, 'edema_articular': True, 'artralgia_meses': 0,
    'dor_retroorbitaria': False,  # menos tipico de dengue
    # dias_febre=3 (< D5) e ns1_resultado='nao_realizado' → dengue NAO excluida
})
_testar('TC08 — Chikungunya fase aguda D3 sem NS1 (AINE proibido)',
        d, 'chikungunya_suspeita',
        {'fase_cronica': False, 'aine_contraindicado': True})

# ── TC09: Chikungunya — Fase crônica (> 3 meses) ──────────────────────────────
d = _base()
d.update({
    'febre_presente': False, 'dias_febre': 0,
    'artralgia_presente': True, 'artralgia_incapacitante': True,
    'artralgia_simetrica': True, 'artralgia_meses': 5,
})
_testar('TC09 — Chikungunya fase cronica (artralgia 5 meses)',
        d, 'chikungunya_suspeita',
        {'fase_cronica': True})

# ── TC10: Zika — Clássico (exantema pruriginoso + conjuntivite) ───────────────
d = _base()
d.update({
    'febre_alta': False,  # febre baixa em Zika
    'exantema_presente': True, 'exantema_pruriginoso': True,
    'conjuntivite': True, 'conjuntivite_nao_purulenta': True,
    'mialgia_intensa': False, 'dor_retroorbitaria': False,
})
_testar('TC10 — Zika classico (exantema pruriginoso + conjuntivite)',
        d, 'zika_suspeita',
        {'alerta_gestante_zika': False})

# ── TC11: Zika — Gestante (notificação imediata) ──────────────────────────────
d = _base()
d.update({
    'exantema_presente': True, 'exantema_pruriginoso': True,
    'conjuntivite_nao_purulenta': True,
    'gestante': True, 'semanas_gestacao': 16,
})
_testar('TC11 — Zika em gestante (16 semanas)',
        d, 'zika_suspeita',
        {'alerta_gestante_zika': True, 'semanas_gestacao': 16})

# ── TC12: Grupo B — Gestante sem padrão Zika ──────────────────────────────────
d = _base()
d.update({'gestante': True, 'semanas_gestacao': 28})
_testar('TC12 — Grupo B: gestante sem padrao Zika',
        d, 'arboviral_grupo_b',
        {'aine_contraindicado': True})

# ── TC13: Grupo B — Diabetes mellitus ────────────────────────────────────────
d = _base()
d.update({'diabetes': True})
_testar('TC13 — Grupo B: diabetes mellitus',
        d, 'arboviral_grupo_b')

# ── TC14: Grupo B — Prova do laço positiva ────────────────────────────────────
d = _base()
d.update({'prova_laco_realizada': True, 'prova_laco_positiva': True})
_testar('TC14 — Grupo B: prova do laco positiva',
        d, 'arboviral_grupo_b',
        {'prova_laco': True})

# ── TC15: Grupo A — Febre sem alarme sem risco (70 kg) ───────────────────────
d = _base()
_testar('TC15 — Grupo A: ambulatorial (febre isolada, 70 kg)',
        d, 'arboviral_grupo_a',
        {'aine_contraindicado': True, 'internacao': False})

# ── TC16: Indiferenciada — sem febre, sem dados suficientes ──────────────────
d = _base()
d.update({'febre_presente': False, 'dias_febre': 0, 'febre_alta': False,
          'mialgia_intensa': False, 'cefaleia': False, 'dor_retroorbitaria': False})
_testar('TC16 — Indiferenciada (sem febre, sem criterio)',
        d, 'arboviral_indiferenciada')

# ── TC17: Grupo D tem precedência sobre alarme (choque + alarme) ──────────────
d = _base()
d.update({'hipotensao_severa': True, 'dor_abdominal_intensa': True, 'sangramento_mucosa': True})
_testar('TC17 — Grupo D prevalece sobre Grupo C (choque + alarmes)',
        d, 'arboviral_grupo_d')

# ── TC18: Hidratação grupo A calculada corretamente (80 kg) ──────────────────
d = _base()
d.update({'peso_kg': 80.0})
r = interpretar_arboviroses(d)
esperado_oral = 80 * 60  # 4800 mL
ok_hid = r.get('hidratacao', {}).get('oral_ml_dia') == esperado_oral
nome = 'TC18 — Calculo hidratacao oral Grupo A (80 kg = 4800 mL/dia)'
if r.get('categoria') == 'arboviral_grupo_a' and ok_hid:
    print(f'  [OK] {nome}')
    PASSOU += 1
else:
    print(f'  [FALHOU] {nome}')
    print(f'           Categoria: {r.get("categoria")}')
    print(f'           oral_ml_dia: {r.get("hidratacao", {}).get("oral_ml_dia")} (esperado {esperado_oral})')
    FALHOU += 1
    ERROS.append(nome)

# ── TC19: Hidratação grupo D calculada corretamente (60 kg) ──────────────────
d = _base()
d.update({'hipotensao_severa': True, 'peso_kg': 60.0})
r = interpretar_arboviroses(d)
esperado_iv_d = 60 * 20  # 1200 mL
ok_hid_d = r.get('hidratacao', {}).get('iv_grupo_d_ml') == esperado_iv_d
nome = 'TC19 — Calculo IV Grupo D (60 kg = 1200 mL em 20 min)'
if r.get('categoria') == 'arboviral_grupo_d' and ok_hid_d:
    print(f'  [OK] {nome}')
    PASSOU += 1
else:
    print(f'  [FALHOU] {nome}')
    print(f'           iv_grupo_d_ml: {r.get("hidratacao", {}).get("iv_grupo_d_ml")} (esperado {esperado_iv_d})')
    FALHOU += 1
    ERROS.append(nome)

# ── TC20: Chikungunya com NS1 negativo → AINE liberado ───────────────────────
d = _base()
d.update({
    'artralgia_presente': True, 'artralgia_incapacitante': True, 'artralgia_simetrica': True,
    'ns1_realizado': True, 'ns1_resultado': 'negativo',  # dengue excluida laboratorialmente
})
r = interpretar_arboviroses(d)
nome = 'TC20 — Chikungunya: aine_contraindicado=False (NS1 negativo confirmado)'
if r.get('categoria') == 'chikungunya_suspeita' and r.get('aine_contraindicado') is False:
    print(f'  [OK] {nome}')
    PASSOU += 1
else:
    print(f'  [FALHOU] {nome}')
    print(f'           aine_contraindicado: {r.get("aine_contraindicado")}')
    FALHOU += 1
    ERROS.append(nome)

# ── TC21: Novo alarme MS 2025 — Acúmulo de líquidos → Grupo C ────────────────
d = _base()
d.update({'acumulo_liquidos': True})
_testar('TC21 — Grupo C: sinal de alarme — acumulo de liquidos (MS 2025)',
        d, 'arboviral_grupo_c',
        {'aine_contraindicado': True, 'internacao': True})

# ── TC22: Novo alarme MS 2025 — Aumento hematócrito → Grupo C ────────────────
d = _base()
d.update({'aumento_hematocrito': True})
_testar('TC22 — Grupo C: sinal de alarme — aumento progressivo hematocrito (MS 2025)',
        d, 'arboviral_grupo_c',
        {'internacao': True})

# ── TC23: Chikungunya aguda > D5 sem NS1 → AINE liberado por tempo ───────────
d = _base()
d.update({
    'artralgia_presente': True, 'artralgia_incapacitante': True, 'artralgia_simetrica': True,
    'dias_febre': 6,  # > D5 → NS1 perde sens. → dengue excluida pelo tempo
})
_testar('TC23 — Chikungunya D6: dengue excluida por tempo (AINE liberado)',
        d, 'chikungunya_suspeita',
        {'aine_contraindicado': False})

# ── TC24: Grupo B — prescricao_observacao presente e hidratacao imediata ──────
d = _base()
d.update({'diabetes': True, 'peso_kg': 65.0})
r = interpretar_arboviroses(d)
nome = 'TC24 — Grupo B: prescricao_observacao gerada com hidratacao supervisionada'
rx = r.get('prescricao_observacao', {})
ok = (
    r.get('categoria') == 'arboviral_grupo_b' and
    bool(rx.get('sintomaticos')) and
    bool(rx.get('hidratacao_supervisionada')) and
    bool(rx.get('laboratorio_urgente'))
)
if ok:
    print(f'  [OK] {nome}')
    PASSOU += 1
else:
    print(f'  [FALHOU] {nome}')
    print(f'           categoria={r.get("categoria")} | rx_obs={bool(rx)}')
    FALHOU += 1
    ERROS.append(nome)

# =============================================================================
print()
print('─' * 60)
total = PASSOU + FALHOU
print(f'  Resultado: {PASSOU}/{total} testes passaram')
if ERROS:
    print(f'  Falhos: {", ".join(ERROS)}')
print('─' * 60)
sys.exit(0 if FALHOU == 0 else 1)
