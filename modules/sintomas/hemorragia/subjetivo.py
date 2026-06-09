# modules/sintomas/hemorragia/subjetivo.py
# Coleta subjetiva — Hemorragia Digestiva Alta (HDA) e Baixa (HDB)
# Fontes: ACG 2023, BSG 2021 (UGIB), AGA/BSG 2023 (LGIB), ESGE

import json, os, tempfile
from utils.perguntas import pergunta_multipla_escolha, pergunta_sim_nao, pergunta_texto, pergunta_numero


def coletar_subjetivo_hemorragia(dados_preenchidos=None):
    dados = dict(dados_preenchidos or {})

    print('\n=== HEMORRAGIA DIGESTIVA ===')

    # ── Bloco 1: Tipo de sangramento ────────────────────────────────────────
    print('\n-- Tipo de sangramento --')
    dados['tipo_sangramento'] = pergunta_multipla_escolha(
        'Como se apresenta o sangramento?',
        ['hematemese', 'borra_cafe', 'melena', 'hematoquezia', 'marrom_escuro', 'papel_apenas'],
        labels=[
            'Vômito com sangue vivo (hematêmese)',
            'Vômito em borra de café',
            'Fezes pretas/alcatronadas (melena)',
            'Sangue vivo nas fezes (hematoquezia)',
            'Fezes marrom-escuras',
            'Sangue apenas no papel higiênico',
        ],
    )

    # Determina ramo UGIB vs LGIB internamente
    _UGIB = dados['tipo_sangramento'] in ('hematemese', 'borra_cafe', 'melena')
    _LGIB = dados['tipo_sangramento'] in ('hematoquezia', 'marrom_escuro', 'papel_apenas')
    dados['ramo'] = 'ugib' if _UGIB else 'lgib'

    # ── Bloco 2: Status hemodinâmico ─────────────────────────────────────────
    print('\n-- Hemodinâmica --')
    dados['pas'] = pergunta_numero('PA sistólica (mmHg):', minimo=50, maximo=250)
    dados['fc']  = pergunta_numero('FC (bpm):', minimo=30, maximo=200)
    dados['sincope']   = pergunta_sim_nao('Síncope ou pré-síncope?')
    dados['palidez_sudorese'] = pergunta_sim_nao('Palidez extrema ou sudorese fria?')

    # ── Bloco 3: UGIB — variáveis GBS + contexto variceal ───────────────────
    if _UGIB:
        print('\n-- HDA — Glasgow-Blatchford Score --')
        dados['bun']        = pergunta_numero('BUN (mg/dL): (0 se não disponível)', minimo=0, maximo=500)
        dados['hb']         = pergunta_numero('Hemoglobina (g/dL):', minimo=3, maximo=25)
        dados['melena']     = dados['tipo_sangramento'] == 'melena'
        dados['hepatopatia_gbs'] = pergunta_sim_nao('Hepatopatia conhecida / cirrose / hipertensão portal?')
        dados['icc']        = pergunta_sim_nao('Insuficiência cardíaca congestiva?')

        print('\n-- HDA — Risco variceal --')
        dados['cirrose']        = dados['hepatopatia_gbs']
        dados['estigmas_htpor'] = pergunta_sim_nao('Estigmas de hepatopatia (ascite, spider nevi, esplenomegalia)?') if not dados['cirrose'] else True
        dados['varizes_previas']= pergunta_sim_nao('Antecedente de varizes esofágicas ou sangramento varicoso?')
        dados['alcool_cronico'] = pergunta_sim_nao('Uso crônico de álcool?')

        print('\n-- HDA — Contexto --')
        dados['aine_asa']    = pergunta_sim_nao('Uso de AINE ou AAS?')
        dados['hp_conhecido']= pergunta_sim_nao('H. pylori conhecido?')
        dados['pud_previo']  = pergunta_sim_nao('Úlcera péptica prévia?')
        dados['dcv']         = pergunta_sim_nao('Doença cardiovascular conhecida (IAM prévio, AVC, etc.)?')

    # ── Bloco 4: LGIB — Oakland Score + etiologia ────────────────────────────
    if _LGIB:
        print('\n-- HDB — Oakland Score --')
        dados['hb']           = pergunta_numero('Hemoglobina (g/dL):', minimo=3, maximo=25)
        dados['lgib_previo']  = pergunta_sim_nao('Internação prévia por hemorragia digestiva baixa?')
        dados['dre_sangue']   = pergunta_sim_nao('Toque retal com sangue no dedo?')

        print('\n-- HDB — Pistas etiológicas --')
        dados['dor_evacuacao']  = pergunta_sim_nao('Dor ao evacuar / dor anal?')
        dados['papel_apenas']   = dados['tipo_sangramento'] == 'papel_apenas'
        dados['diarreia_sangue']= pergunta_sim_nao('Diarreia com sangue?')
        dados['dor_abdominal']  = pergunta_sim_nao('Dor abdominal associada?')
        dados['febre']          = pergunta_sim_nao('Febre?')
        dados['atb_recente']    = pergunta_sim_nao('Antibiótico nos últimos 3 meses?')
        dados['viagem_recente'] = pergunta_sim_nao('Viagem recente para área endêmica?')
        dados['mudanca_habito'] = pergunta_sim_nao('Mudança no hábito intestinal (últimas semanas)?')
        dados['perda_peso']     = pergunta_sim_nao('Perda de peso não intencional?')
        dados['pos_polipectomia']= pergunta_sim_nao('Colonoscopia com polipectomia recente (< 30 dias)?')
        dados['dii_conhecida']  = pergunta_sim_nao('Doença inflamatória intestinal conhecida (Crohn/RCUI)?')
        dados['dcv_dm']         = pergunta_sim_nao('Doença vascular / DM / aterosclerose?')
        dados['idoso_indolor']  = (dados_preenchidos or {}).get('idade', 0) >= 60

    # ── Bloco 5: Anticoagulação ───────────────────────────────────────────────
    print('\n-- Anticoagulação --')
    dados['anticoagulado'] = pergunta_sim_nao('Em uso de anticoagulante?')
    if dados['anticoagulado']:
        dados['anticoagulante'] = pergunta_multipla_escolha(
            'Qual anticoagulante?',
            ['varfarina', 'apixabana', 'rivaroxabana', 'dabigatrana', 'hbpm', 'outro'],
            labels=['Varfarina', 'Apixabana', 'Rivaroxabana', 'Dabigatrana', 'HBPM', 'Outro'],
        )
        dados['inr'] = pergunta_numero('INR (0 se não disponível):', minimo=0, maximo=15)
    else:
        dados['anticoagulante'] = None
        dados['inr'] = None

    # ── Bloco 6: Histórico ────────────────────────────────────────────────────
    print('\n-- Histórico --')
    dados['endoscopia_recente'] = pergunta_sim_nao('Endoscopia recente (< 30 dias)?')
    dados['cirurgia_gi']        = pergunta_sim_nao('Cirurgia gastrointestinal recente?')
    if not _UGIB:
        dados['hepatopatia_gbs'] = pergunta_sim_nao('Hepatopatia / cirrose?')
        dados['cirrose'] = dados['hepatopatia_gbs']

    fd, caminho = tempfile.mkstemp(suffix='_hemorragia.json')
    os.close(fd)
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    return dados, caminho
