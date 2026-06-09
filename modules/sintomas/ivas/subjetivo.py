# modules/sintomas/ivas/subjetivo.py
# Coleta subjetiva — IVAS / Faringite (adulto/adolescente >= 15 anos)
# Referências: ACP/CDC 2025 · IDSA 2025 · Guia McIsaac/Centor modificado

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


# =============================================================================
# ENTRY POINT
# =============================================================================

def coletar_subjetivo_ivas(dados_preenchidos=None):
    sys.stdout.reconfigure(encoding='utf-8')
    dados = dict(dados_preenchidos) if dados_preenchidos else {}

    print('\n── IVAS / Faringite (adulto/adolescente >= 15 anos) ──')

    # ── BLOCO 0 — Dados básicos ───────────────────────────────────────────────
    print('\n  [Bloco 0] Dados básicos\n')

    dados['idade']        = dados.get('idade', _int('  Idade do paciente (anos): ', 30))
    dados['dias_sintomas'] = dados.get('dias_sintomas', _int('  Há quantos dias com os sintomas? ', 2))

    # ── BLOCO 1 — RED FLAGS (verificar antes de tudo) ─────────────────────────
    print('\n  [Bloco 1] Sinais de Alerta — Emergências\n')
    print('  (Responder s/n — qualquer positivo redireciona para conduta urgente)\n')

    dados['assimetria_tonsilar']    = dados.get('assimetria_tonsilar',
        _sn('  Assimetria tonsilar ou desvio de úvula? [s/n] '))
    dados['trismo']                 = dados.get('trismo',
        _sn('  Trismo (dificuldade de abrir a boca)? [s/n] '))
    dados['voz_abafada']            = dados.get('voz_abafada',
        _sn('  Voz abafada ("batata quente" / voz de "boca cheia")? [s/n] '))
    dados['sialorreia']             = dados.get('sialorreia',
        _sn('  Sialorreia (escorrer saliva / incapaz de deglutir)? [s/n] '))
    dados['estridor']               = dados.get('estridor',
        _sn('  Estridor inspiratório (ruído áspero ao inspirar)? [s/n] '))
    dados['dificuldade_respiratoria'] = dados.get('dificuldade_respiratoria',
        _sn('  Dificuldade respiratória ou dispneia? [s/n] '))
    dados['edema_submandibular']    = dados.get('edema_submandibular',
        _sn('  Edema submandibular bilateral endurecido? [s/n] '))

    # ── BLOCO 2 — Critérios de McIsaac ───────────────────────────────────────
    print('\n  [Bloco 2] Score de McIsaac — Faringite GAS\n')

    dados['febre_38']               = dados.get('febre_38',
        _sn('  Febre >= 38°C (medida ou referida)? [s/n] '))
    dados['febre_alta_39']          = dados.get('febre_alta_39',
        _sn('  Febre alta >= 39°C? [s/n] '))
    dados['tosse_presente']         = dados.get('tosse_presente',
        _sn('  Tosse presente? [s/n] '))
    dados['exsudato_tonsilar']      = dados.get('exsudato_tonsilar',
        _sn('  Exsudato tonsilar ou amígdalas muito aumentadas? [s/n] '))
    dados['linfadenopatia_anterior'] = dados.get('linfadenopatia_anterior',
        _sn('  Linfonodos cervicais ANTERIORES dolorosos? [s/n] '))
    dados['odinofagia_severa']       = dados.get('odinofagia_severa',
        _sn('  Odinofagia severa (dificuldade para deglutir líquidos)? [s/n] '))

    # ── BLOCO 3 — Sinais de mononucleose e influenza ──────────────────────────
    print('\n  [Bloco 3] Padrão clínico — diferenciais\n')

    dados['inicio_subito_horas']     = dados.get('inicio_subito_horas',
        _sn('  Início SÚBITO em horas (< 12h para sintomas plenos)? [s/n] '))
    dados['mialgia_intensa']         = dados.get('mialgia_intensa',
        _sn('  Mialgia intensa / dores no corpo? [s/n] '))
    dados['linfadenopatia_posterior'] = dados.get('linfadenopatia_posterior',
        _sn('  Linfonodos cervicais POSTERIORES aumentados? [s/n] '))
    dados['esplenomegalia_referida']  = dados.get('esplenomegalia_referida',
        _sn('  Esplenomegalia ou dor no flanco esquerdo referida? [s/n] '))

    # ── BLOCO 4 — Sintomas de sinusite e laringite ────────────────────────────
    print('\n  [Bloco 4] Localização dos sintomas\n')

    dados['dor_facial']             = dados.get('dor_facial',
        _sn('  Dor facial ou pressão sinusal (fronte/zigoma/nasal)? [s/n] '))
    dados['descarga_purulenta']     = dados.get('descarga_purulenta',
        _sn('  Descarga nasal purulenta (amarela/esverdeada)? [s/n] '))
    dados['duplo_agravamento']      = dados.get('duplo_agravamento',
        _sn('  Duplo agravamento (melhora e piora após 5-7 dias)? [s/n] '))
    dados['sintomas_10_dias']       = dados.get('sintomas_10_dias',
        _sn('  Sintomas nasais/sinusais há mais de 10 dias sem melhora? [s/n] '))
    dados['rouquidao_predominante'] = dados.get('rouquidao_predominante',
        _sn('  Rouquidão como sintoma predominante? [s/n] '))

    # ── BLOCO 5 — Teste rápido de estreptococo (RADT) ─────────────────────────
    print('\n  [Bloco 5] Teste Rápido Estrepto (RADT)\n')
    print('  (Sensibilidade 85-95% | Especificidade 97-99% em adultos)\n')

    dados['radt_realizado'] = dados.get('radt_realizado',
        _sn('  RADT foi realizado nesta consulta? [s/n] '))
    dados['radt_positivo']  = False
    dados['radt_disponivel'] = True
    if dados['radt_realizado']:
        dados['radt_positivo'] = dados.get('radt_positivo',
            _sn('  Resultado do RADT: POSITIVO? [s/n] '))
    else:
        dados['radt_disponivel'] = dados.get('radt_disponivel',
            _sn('  RADT disponível para realizar agora? [s/n] '))

    # ── BLOCO 6 — Perfil alérgico (para seleção de antibiótico) ──────────────
    print('\n  [Bloco 6] Perfil alérgico\n')

    dados['alergia_penicilina']  = dados.get('alergia_penicilina',
        _sn('  Alergia à penicilina? [s/n] '))
    dados['alergia_anafilatica'] = False
    if dados['alergia_penicilina']:
        dados['alergia_anafilatica'] = dados.get('alergia_anafilatica',
            _sn('  Alergia ANAFILÁTICA (urticária, angioedema, anafilaxia)? [s/n] '))

    dados['aderencia_preocupa'] = dados.get('aderencia_preocupa',
        _sn('  Aderência ao tratamento é uma preocupação (prefere dose única)? [s/n] '))
    dados['historico_fra']      = dados.get('historico_fra',
        _sn('  Histórico de febre reumática aguda (FRA)? [s/n] '))

    # ── BLOCO 7 — Fatores de risco para influenza grave ───────────────────────
    print('\n  [Bloco 7] Fatores de risco (para decisão de oseltamivir)\n')

    dados['asma_dpoc']           = dados.get('asma_dpoc',
        _sn('  Asma ou DPOC? [s/n] '))
    dados['doenca_cardiovascular'] = dados.get('doenca_cardiovascular',
        _sn('  Doença cardiovascular (ICC, coronariopatia, cardiomiopatia)? [s/n] '))
    dados['drc']                 = dados.get('drc',
        _sn('  Doença renal crônica (DRC)? [s/n] '))
    dados['hepatopatia']         = dados.get('hepatopatia',
        _sn('  Hepatopatia crônica? [s/n] '))
    dados['diabetes']            = dados.get('diabetes',
        _sn('  Diabetes mellitus? [s/n] '))
    dados['imunossupressao']     = dados.get('imunossupressao',
        _sn('  Imunossupressão (corticoide crônico, HIV, pós-transplante, quimioterapia)? [s/n] '))
    dados['gestante']            = dados.get('gestante',
        _sn('  Gestante? [s/n] '))
    dados['obesidade_grave']     = dados.get('obesidade_grave',
        _sn('  Obesidade grave (IMC > 40)? [s/n] '))

    # ── Salvar ────────────────────────────────────────────────────────────────
    fd, arquivo = tempfile.mkstemp(suffix='.json', prefix='ivas_')
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    return dados, arquivo
