# padrao_dor.py
# Camada compartilhada — Classificação do mecanismo de dor
# Base: Open Evidence 2026 / IASP / CSI / DN4 / PainDETECT
# Nociceptivo | Neuropático | Nociplástico (sensibilização central)
# O mecanismo dominante guia a conduta — não o diagnóstico anatômico

def classificar_mecanismo_dor(dados):

    # --- NOCICEPTIVO ---
    score_nociceptivo = 0
    achados_nociceptivos = []

    if dados.get('dor_localizada'):
        score_nociceptivo += 2
        achados_nociceptivos.append('dor_localizada')
    if dados.get('piora_com_movimento_ou_carga'):
        score_nociceptivo += 2
        achados_nociceptivos.append('piora_com_movimento_ou_carga')
    if dados.get('melhora_com_repouso'):
        score_nociceptivo += 1
        achados_nociceptivos.append('melhora_com_repouso')
    if dados.get('trauma_ou_sobrecarga_recente'):
        score_nociceptivo += 2
        achados_nociceptivos.append('trauma_ou_sobrecarga_recente')
    if dados.get('exame_fisico_local_positivo'):
        score_nociceptivo += 2
        achados_nociceptivos.append('exame_fisico_local_positivo')
    if dados.get('sem_sintomas_neurologicos'):
        score_nociceptivo += 1
        achados_nociceptivos.append('sem_sintomas_neurologicos')

    # --- NEUROPÁTICO ---
    score_neuropatico = 0
    achados_neuropaticos = []

    if dados.get('queimacao_ou_choque_eletrico'):
        score_neuropatico += 3
        achados_neuropaticos.append('queimacao_ou_choque_eletrico')
    if dados.get('formigamento_ou_dormencia'):
        score_neuropatico += 2
        achados_neuropaticos.append('formigamento_ou_dormencia')
    if dados.get('distribuicao_dermatomal'):
        score_neuropatico += 3
        achados_neuropaticos.append('distribuicao_dermatomal')
    if dados.get('alodinia'):
        score_neuropatico += 2
        achados_neuropaticos.append('alodinia')
    if dados.get('deficit_sensorial_ou_reflexo'):
        score_neuropatico += 2
        achados_neuropaticos.append('deficit_sensorial_ou_reflexo')
    if dados.get('piora_noturna_caracteristica'):
        score_neuropatico += 1
        achados_neuropaticos.append('piora_noturna_caracteristica')

    # --- NOCIPLÁSTICO (sensibilização central) ---
    score_nociplastico = 0
    achados_nociplasticos = []

    if dados.get('dor_generalizada_ou_difusa'):
        score_nociplastico += 3
        achados_nociplasticos.append('dor_generalizada_ou_difusa')
    if dados.get('dor_desproporcional_ao_exame'):
        score_nociplastico += 3
        achados_nociplasticos.append('dor_desproporcional_ao_exame')
    if dados.get('fadiga_cronica'):
        score_nociplastico += 2
        achados_nociplasticos.append('fadiga_cronica')
    if dados.get('sono_nao_restaurador'):
        score_nociplastico += 2
        achados_nociplasticos.append('sono_nao_restaurador')
    if dados.get('comprometimento_cognitivo_leve'):
        score_nociplastico += 1
        achados_nociplasticos.append('comprometimento_cognitivo_leve')
    if dados.get('multiplos_sindromes_somaticos'):
        score_nociplastico += 2
        achados_nociplasticos.append('multiplos_sindromes_somaticos')
    if dados.get('falha_de_analgesia_convencional'):
        score_nociplastico += 2
        achados_nociplasticos.append('falha_de_analgesia_convencional')
    if dados.get('csi_acima_40'):
        score_nociplastico += 3
        achados_nociplasticos.append('csi_acima_40_confirmado')

    # --- SCORES DN4 / PainDETECT (se aplicados) ---
    if dados.get('dn4_acima_4'):
        score_neuropatico += 4
        achados_neuropaticos.append('dn4_positivo_sens80_esp92')
    if dados.get('paindetect_acima_19'):
        score_neuropatico += 4
        achados_neuropaticos.append('paindetect_positivo_sens85_esp80')

    # --- MECANISMO DOMINANTE ---
    scores = {
        'nociceptivo': score_nociceptivo,
        'neuropatico': score_neuropatico,
        'nociplastico': score_nociplastico
    }
    mecanismo_dominante = max(scores, key=scores.get)

    # Misto: dois mecanismos próximos (diferença <= 2)
    scores_sorted = sorted(scores.values(), reverse=True)
    misto = (scores_sorted[0] - scores_sorted[1]) <= 2 and scores_sorted[1] >= 3

    # --- IMPLICAÇÕES TERAPÊUTICAS ---
    implicacoes = {
        'nociceptivo': [
            'AINEs e paracetamol são eficazes',
            'Fisioterapia e reabilitação funcional',
            'Infiltração pode ser indicada (corticoide ou ácido hialurônico)',
            'Prognóstico geralmente favorável com tratamento local'
        ],
        'neuropatico': [
            'AINEs têm eficácia limitada',
            'Gabapentinoides (pregabalina, gabapentina)',
            'Antidepressivos (duloxetina, amitriptilina)',
            'Evitar opioides como primeira linha',
            'Fisioterapia com abordagem neurodinâmica'
        ],
        'nociplastico': [
            'AINEs e opioides têm baixa eficácia — evitar',
            'Infiltrações locais geralmente não resolvem',
            'Duloxetina e pregabalina têm evidência moderada',
            'TCC e educação em neurociência da dor são essenciais',
            'Exercício aeróbico gradual é o tratamento mais eficaz',
            'Higiene do sono e manejo de humor são parte do tratamento',
            'Prognóstico depende de adesão ao tratamento multimodal'
        ]
    }

    return {
        'mecanismo_dominante': mecanismo_dominante,
        'misto': misto,
        'scores': scores,
        'achados_nociceptivos': achados_nociceptivos,
        'achados_neuropaticos': achados_neuropaticos,
        'achados_nociplasticos': achados_nociplasticos,
        'implicacoes_terapeuticas': implicacoes[mecanismo_dominante],
        'alerta_nociplastico': score_nociplastico >= 6
    }


if __name__ == '__main__':
    caso_neuropatico = {
        'dor_localizada': False,
        'piora_com_movimento_ou_carga': False,
        'melhora_com_repouso': False,
        'trauma_ou_sobrecarga_recente': False,
        'exame_fisico_local_positivo': False,
        'sem_sintomas_neurologicos': False,
        'queimacao_ou_choque_eletrico': True,
        'formigamento_ou_dormencia': True,
        'distribuicao_dermatomal': True,
        'alodinia': False,
        'deficit_sensorial_ou_reflexo': True,
        'piora_noturna_caracteristica': True,
        'dor_generalizada_ou_difusa': False,
        'dor_desproporcional_ao_exame': False,
        'fadiga_cronica': False,
        'sono_nao_restaurador': False,
        'comprometimento_cognitivo_leve': False,
        'multiplos_sindromes_somaticos': False,
        'falha_de_analgesia_convencional': False,
        'csi_acima_40': False,
        'dn4_acima_4': True,
        'paindetect_acima_19': False
    }

    resultado = classificar_mecanismo_dor(caso_neuropatico)
    print(f"Mecanismo dominante: {resultado['mecanismo_dominante'].upper()}")
    print(f"Misto: {resultado['misto']}")
    print(f"Scores: {resultado['scores']}")
    print("Condutas:")
    for c in resultado['implicacoes_terapeuticas']:
        print(f"  - {c}")
