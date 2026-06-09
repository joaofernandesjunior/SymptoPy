# modules/sintomas/celulite/subjetivo.py
# Coleta subjetiva — Celulite e Erisipela (adulto)
# Fonte: IDSA 2014 (Stevens et al., Clin Infect Dis)

import json, os, tempfile
from utils.perguntas import pergunta_multipla_escolha, pergunta_sim_nao, pergunta_texto, pergunta_numero


def coletar_subjetivo_celulite(dados_preenchidos=None):
    dados = dict(dados_preenchidos or {})

    print('\n=== CELULITE / ERISIPELA ===')

    # ── Bloco 1: Localização e tempo ─────────────────────────────────────────
    print('\n-- Localização --')
    dados['localizacao'] = pergunta_multipla_escolha(
        'Localização da lesão:',
        ['mmii_unilateral', 'mmii_bilateral', 'face', 'mao_braco', 'tronco', 'pe', 'outro'],
        labels=['MMII unilateral', 'MMII bilateral', 'Face', 'Mão/braço', 'Tronco', 'Pé', 'Outro'],
    )
    dados['tempo_evolucao'] = pergunta_multipla_escolha(
        'Tempo de evolução:',
        ['horas', 'um_a_dois_dias', 'tres_a_cinco_dias', 'mais_cinco_dias'],
        labels=['< 24h', '1–2 dias', '3–5 dias', '> 5 dias'],
    )

    # ── Bloco 2: Porta de entrada ─────────────────────────────────────────────
    print('\n-- Porta de entrada --')
    dados['tinea_pedis']       = pergunta_sim_nao('Tinea pedis / micose interdigital?')
    dados['ferida_ulcera']     = pergunta_sim_nao('Ferida, úlcera ou fissura cutânea?')
    dados['picada_trauma']     = pergunta_sim_nao('Picada de inseto, trauma ou arranhão?')
    dados['pe_diabetico']      = pergunta_sim_nao('Pé diabético (lesão em diabético)?')
    dados['manicure_pedicure'] = pergunta_sim_nao('Manicure / pedicure recente?')
    dados['uso_drogas_iv']     = pergunta_sim_nao('Uso de drogas intravenosas?')
    dados['mordedura_animal']  = pergunta_sim_nao('Mordedura de animal ou imersão em água?')
    dados['trauma_penetrante'] = pergunta_sim_nao('Trauma penetrante?')

    # ── Bloco 3: Sintomas sistêmicos (SIRS) ──────────────────────────────────
    print('\n-- Sintomas sistêmicos --')
    dados['febre']             = pergunta_sim_nao('Febre (temperatura >38°C)?')
    if dados['febre']:
        dados['temp_celsius'] = pergunta_numero('Temperatura (°C):', minimo=36.0, maximo=42.0)
    else:
        dados['temp_celsius'] = None
    dados['hipotermia']        = pergunta_sim_nao('Hipotermia (<36°C)?')
    dados['taquicardia']       = pergunta_sim_nao('FC >90 bpm?')
    dados['taquipneia']        = pergunta_sim_nao('FR >20 ipm?')
    dados['mal_estar_calafrio'] = pergunta_sim_nao('Mal-estar geral / calafrios?')
    dados['hipotensao']        = pergunta_sim_nao('Hipotensão ou instabilidade hemodinâmica?')

    # ── Bloco 4: Sinais locais (red flags fasciite) ───────────────────────────
    print('\n-- Sinais locais --')
    dados['borda_nitida']      = pergunta_sim_nao('Borda bem demarcada (tipo erisipela)?')
    dados['flutuacao']         = pergunta_sim_nao('Flutuação / abscesso?')
    dados['bolhas']            = pergunta_sim_nao('Bolhas (vesículas/flictenas)?')
    if dados.get('bolhas'):
        dados['bolhas_hemorragicas'] = pergunta_sim_nao('Bolhas hemorrágicas ou necróticas?')
    else:
        dados['bolhas_hemorragicas'] = False
    dados['crepitacao']        = pergunta_sim_nao('Crepitação à palpação?')
    dados['necrose']           = pergunta_sim_nao('Necrose ou pele violácea?')
    dados['linfangite']        = pergunta_sim_nao('Estria vermelha subindo (linfangite)?')
    dados['dor_desproporcional'] = pergunta_sim_nao('Dor desproporcional ao exame?')
    dados['progressao_rapida'] = pergunta_sim_nao('Progressão rápida apesar de ATB?')

    # ── Bloco 5: Comorbidades ─────────────────────────────────────────────────
    print('\n-- Comorbidades --')
    dados['diabetes']          = pergunta_sim_nao('Diabetes mellitus?')
    dados['obesidade']         = pergunta_sim_nao('Obesidade?')
    dados['drc']               = pergunta_sim_nao('Doença renal crônica?')
    dados['imunossupressao']   = pergunta_sim_nao('Imunossupressão (quimio, transplante, HIV, corticoide crônico)?')
    dados['neutropenia']       = pergunta_sim_nao('Neutropenia ou quimioterapia ativa?')
    dados['insuf_venosa']      = pergunta_sim_nao('Insuficiência venosa crônica?')
    dados['linfedema']         = pergunta_sim_nao('Linfedema?')
    dados['malignidade']       = pergunta_sim_nao('Malignidade ativa?')

    # ── Bloco 6: Risco de MRSA ───────────────────────────────────────────────
    print('\n-- Fatores de risco para MRSA --')
    dados['mrsa_colonizacao']  = pergunta_sim_nao('MRSA conhecido (colonização ou infecção prévia)?')
    dados['mrsa_internacao_recente'] = pergunta_sim_nao('Internação hospitalar recente (< 3 meses)?')
    dados['drenagem_purulenta'] = pergunta_sim_nao('Drenagem purulenta?')
    dados['falha_beta_lactamico'] = pergunta_sim_nao('Falha em beta-lactâmico oral recente?')

    # ── Bloco 7: Episódios anteriores ────────────────────────────────────────
    print('\n-- Histórico --')
    dados['episodios_anteriores'] = pergunta_numero(
        'Quantos episódios de celulite/erisipela no último ano? (0 se primeiro):',
        minimo=0, maximo=20,
    )

    # ── Bloco 8: Alergia a antibióticos ──────────────────────────────────────
    print('\n-- Alergias --')
    dados['alergia_penicilina'] = pergunta_multipla_escolha(
        'Alergia a penicilina / beta-lactâmico:',
        ['nenhuma', 'nao_anafilatica', 'anafilatica'],
        labels=['Nenhuma', 'Não anafilática (rash, intolerância)', 'Anafilática (urticária/edema/choque)'],
    )

    # ── Bloco 9: Exames disponíveis (opcional — para LRINEC) ─────────────────
    print('\n-- Exames (se disponíveis — para LRINEC) --')
    tem_labs = pergunta_sim_nao('Há resultados laboratoriais disponíveis?')
    if tem_labs:
        dados['pcr']         = pergunta_numero('PCR (mg/L): (0 se não disponível)', minimo=0, maximo=999)
        dados['leucocitos']  = pergunta_numero('Leucócitos (/μL): (ex: 12000)', minimo=0, maximo=100000)
        dados['hb']          = pergunta_numero('Hemoglobina (g/dL):', minimo=0, maximo=25)
        dados['sodio']       = pergunta_numero('Sódio (mEq/L):', minimo=110, maximo=165)
        dados['creatinina']  = pergunta_numero('Creatinina (mg/dL):', minimo=0, maximo=30)
        dados['glicemia']    = pergunta_numero('Glicemia (mg/dL):', minimo=0, maximo=999)
    else:
        for k in ('pcr', 'leucocitos', 'hb', 'sodio', 'creatinina', 'glicemia'):
            dados[k] = None

    fd, caminho = tempfile.mkstemp(suffix='_celulite.json')
    os.close(fd)
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    return dados, caminho
