# modules/sintomas/arboviroses/subjetivo.py
# Coleta subjetiva — Arboviroses: Dengue / Chikungunya / Zika
# Protocolo: Ministério da Saúde 2023 — Classificação A/B/C/D
# Sem objetivo.py dedicado — exame geral cobre (exceto prova do laço)

import json
import os
import sys
import tempfile


def _sn(prompt):
    return input(prompt).strip().lower() in ('s', 'sim', 'y', 'yes', '1')


def _int(prompt, default=0):
    try:
        return int(input(prompt).strip() or str(default))
    except ValueError:
        return default


def _float(prompt, default=0.0):
    try:
        return float(input(prompt).strip().replace(',', '.') or str(default))
    except ValueError:
        return default


# =============================================================================
# ENTRY POINT
# =============================================================================

def coletar_subjetivo_arboviroses(dados_preenchidos=None):
    sys.stdout.reconfigure(encoding='utf-8')
    dados = dict(dados_preenchidos) if dados_preenchidos else {}

    # ── BLOCO 0 — Caracterização da febre ────────────────────────────────────
    print('\n── Arboviroses: Dengue / Chikungunya / Zika ──')
    print('  [Bloco 0] Caracterização da febre\n')

    dados['febre_presente']  = dados.get('febre_presente',  _sn('  Febre presente? [s/n] '))
    dados['dias_febre']      = dados.get('dias_febre',      _int('  Há quantos dias de febre? [0 = sem febre] '))
    dados['febre_alta']      = dados.get('febre_alta',      _sn('  Febre alta (>= 38,5°C)? [s/n] '))
    dados['inicio_subito']   = dados.get('inicio_subito',   _sn('  Início súbito (horas)? [s/n] '))

    # ── BLOCO 1 — Sintomas sistêmicos ────────────────────────────────────────
    print('\n  [Bloco 1] Sintomas sistêmicos\n')

    dados['cefaleia']           = dados.get('cefaleia',           _sn('  Cefaleia? [s/n] '))
    dados['mialgia_intensa']    = dados.get('mialgia_intensa',    _sn('  Mialgia intensa (dores no corpo)? [s/n] '))
    dados['dor_retroorbitaria'] = dados.get('dor_retroorbitaria', _sn('  Dor retroorbitária (atrás dos olhos)? [s/n] '))
    dados['nausea']             = dados.get('nausea',             _sn('  Náusea? [s/n] '))
    dados['vomitos']            = dados.get('vomitos',            _sn('  Vômitos? [s/n] '))

    # ── BLOCO 2 — Exantema ───────────────────────────────────────────────────
    print('\n  [Bloco 2] Exantema\n')

    dados['exantema_presente']   = dados.get('exantema_presente',  _sn('  Exantema / manchas na pele? [s/n] '))
    dados['exantema_pruriginoso'] = False
    if dados['exantema_presente']:
        dados['exantema_pruriginoso'] = dados.get('exantema_pruriginoso',
                                                   _sn('  Exantema pruriginoso (com coceira intensa)? [s/n] '))

    # ── BLOCO 3 — Artralgia ──────────────────────────────────────────────────
    print('\n  [Bloco 3] Artralgia\n')

    dados['artralgia_presente']      = dados.get('artralgia_presente',      _sn('  Artralgia (dor articular)? [s/n] '))
    dados['artralgia_incapacitante'] = False
    dados['artralgia_simetrica']     = False
    dados['edema_articular']         = False
    dados['artralgia_meses']         = 0

    if dados['artralgia_presente']:
        dados['artralgia_incapacitante'] = dados.get('artralgia_incapacitante',
            _sn('  Artralgia incapacitante (impede atividades básicas)? [s/n] '))
        dados['artralgia_simetrica'] = dados.get('artralgia_simetrica',
            _sn('  Artralgia simétrica (bilateral, mesmas articulações)? [s/n] '))
        dados['edema_articular'] = dados.get('edema_articular',
            _sn('  Edema articular visível? [s/n] '))
        dados['artralgia_meses'] = dados.get('artralgia_meses',
            _int('  Artralgia persiste há quantos meses? (0 = fase aguda) ', 0))

    # ── BLOCO 4 — Conjuntivite ───────────────────────────────────────────────
    print('\n  [Bloco 4] Conjuntivite\n')

    dados['conjuntivite']              = dados.get('conjuntivite',              _sn('  Olhos vermelhos (hiperemia conjuntival)? [s/n] '))
    dados['conjuntivite_nao_purulenta'] = False
    if dados['conjuntivite']:
        purulenta = dados.get('_conjuntivite_purulenta',
                              _sn('  Com secreção purulenta (pus)? [s/n] '))
        dados['conjuntivite_nao_purulenta'] = not purulenta

    # ── BLOCO 5 — Sinais de alarme ───────────────────────────────────────────
    print('\n  [Bloco 5] Sinais de Alarme — Dengue (MS 2025 — 8 critérios)\n')

    dados['dor_abdominal_intensa']   = dados.get('dor_abdominal_intensa',
        _sn('  Dor abdominal INTENSA (referida ou à palpação) e contínua? [s/n] '))
    dados['vomitos_persistentes']    = dados.get('vomitos_persistentes',
        _sn('  Vômitos persistentes? [s/n] '))
    dados['acumulo_liquidos']        = dados.get('acumulo_liquidos',
        _sn('  Acúmulo de líquidos (barriga inchada/ascite, falta de ar deitado, dor torácica)? [s/n] '))
    dados['hipotensao_postural']     = dados.get('hipotensao_postural',
        _sn('  Hipotensão postural e/ou lipotimia ao levantar? [s/n] '))
    dados['hepatomegalia_referida']  = dados.get('hepatomegalia_referida',
        _sn('  Hepatomegalia dolorosa > 2 cm referida pelo paciente? [s/n] '))
    dados['sangramento_mucosa']      = dados.get('sangramento_mucosa',
        _sn('  Sangramento de mucosa (gengival, nasal, vaginal, petéquias)? [s/n] '))
    dados['letargia_irritabilidade'] = dados.get('letargia_irritabilidade',
        _sn('  Letargia e/ou irritabilidade marcada? [s/n] '))
    dados['aumento_hematocrito']     = dados.get('aumento_hematocrito',
        _sn('  Hematócrito em aumento progressivo em hemograma anterior (>= 10%)? [s/n] '))

    # ── BLOCO 6 — Sinais de choque ───────────────────────────────────────────
    print('\n  [Bloco 6] Sinais de Choque (Grupo D)\n')

    dados['hipotensao_severa']   = dados.get('hipotensao_severa',   _sn('  PA <= 90/60 mmHg ou queda >= 20 mmHg ao sentar/levantar? [s/n] '))
    dados['pulso_filiforme']     = dados.get('pulso_filiforme',     _sn('  Pulso filiforme (difícil palpar radial)? [s/n] '))
    dados['tec_maior_3s']        = dados.get('tec_maior_3s',        _sn('  TEC > 3 segundos? [s/n] '))
    dados['sudorese_fria']       = dados.get('sudorese_fria',       _sn('  Sudorese fria ou extremidades frias? [s/n] '))

    # ── BLOCO 7 — Prova do Laço ──────────────────────────────────────────────
    print('\n  [Bloco 7] Prova do Laço\n')
    print('  (Inflar manguito até média PAS+PAD por 5 min; positivo >= 20 petéquias/pol² em adulto)\n')

    dados['prova_laco_realizada'] = dados.get('prova_laco_realizada', _sn('  Prova do laço realizada? [s/n] '))
    dados['prova_laco_positiva']  = False
    if dados['prova_laco_realizada']:
        dados['prova_laco_positiva'] = dados.get('prova_laco_positiva',
                                                  _sn('  Prova do laço positiva? [s/n] '))

    # ── BLOCO 7b — Teste Rápido NS1 ──────────────────────────────────────────
    print('\n  [Bloco 7b] Teste Rápido — NS1 Antígeno Dengue\n')
    print('  (Positivo D1-D5 | Sensibilidade: 70-90% | Especificidade: >95%)\n')

    dados['ns1_realizado'] = dados.get('ns1_realizado',
                                        _sn('  Teste rápido NS1 foi realizado nesta consulta? [s/n] '))
    dados['ns1_resultado'] = 'nao_realizado'
    if dados['ns1_realizado']:
        while True:
            r = input('  Resultado NS1: [p]ositivo / [n]egativo / [i]ndeterminado: ').strip().lower()
            if r in ('p', 'positivo'):
                dados['ns1_resultado'] = 'positivo'
                break
            elif r in ('n', 'negativo'):
                dados['ns1_resultado'] = 'negativo'
                break
            elif r in ('i', 'indeterminado'):
                dados['ns1_resultado'] = 'indeterminado'
                break
            print('  Informe: p, n ou i')

    # ── BLOCO 8 — Fatores de risco / Grupo B ─────────────────────────────────
    print('\n  [Bloco 8] Fatores de Risco (Condições Especiais — Grupo B)\n')

    dados['gestante']            = dados.get('gestante',            _sn('  Gestante? [s/n] '))
    dados['semanas_gestacao']    = 0
    if dados['gestante']:
        dados['semanas_gestacao'] = dados.get('semanas_gestacao',
                                              _int('  Semanas de gestação? ', 0))

    dados['diabetes']            = dados.get('diabetes',            _sn('  Diabetes mellitus? [s/n] '))
    dados['has_cardiovascular']  = dados.get('has_cardiovascular',  _sn('  HAS ou doença cardiovascular? [s/n] '))
    dados['hematologica']        = dados.get('hematologica',        _sn('  Doença hematológica (falciforme, plaquetopenia prévia)? [s/n] '))
    dados['drc']                 = dados.get('drc',                 _sn('  Doença renal crônica? [s/n] '))
    dados['doenca_hepatica']     = dados.get('doenca_hepatica',     _sn('  Doença hepática prévia (cirrose, hepatite crônica)? [s/n] '))
    dados['obesidade_grave']     = dados.get('obesidade_grave',     _sn('  Obesidade grave (IMC > 40)? [s/n] '))
    dados['extremo_idade']       = dados.get('extremo_idade',       _sn('  Extremo de idade (< 2 anos ou > 60 anos)? [s/n] '))
    dados['risco_social']        = dados.get('risco_social',        _sn('  Risco social (mora sozinho, sem acesso à UBS)? [s/n] '))

    # ── BLOCO 9 — Dados para cálculo de hidratação ───────────────────────────
    print('\n  [Bloco 9] Dados do Paciente\n')

    dados['peso_kg'] = dados.get('peso_kg', _float('  Peso do paciente (kg, para cálculo de hidratação): ', 70.0))
    if dados['peso_kg'] <= 0:
        dados['peso_kg'] = 70.0

    # Contexto epidemiológico
    dados['area_endemica'] = dados.get('area_endemica', _sn('  Área endêmica de dengue / Aedes aegypti? [s/n] '))

    # ── Salvar ────────────────────────────────────────────────────────────────
    fd, arquivo = tempfile.mkstemp(suffix='.json', prefix='arboviroses_')
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    return dados, arquivo
