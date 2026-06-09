# apoio_clinico/plano_clinico.py
# Gera plano clínico estruturado a partir do output do engine
# Regras:
#   - Não inventa conteúdo novo
#   - Só organiza o que o engine já retornou
#   - Retorna lista de strings prontas para impressão
#   - Funciona para qualquer engine MSK (joelho, ombro, quadril...)

def gerar_analise_sistema(resultado):
    """
    Gera parágrafo de análise clínica a partir do output do engine.
    Retorna string única.
    """
    if resultado.get('categoria') == 'red_flag_emergencia':
        flags = resultado.get('red_flags', {}).get('flags', [])
        achados = ', '.join(f['achado'] for f in flags)
        return f"Red flag de emergência identificada: {achados}. Avaliação de rotina interrompida."

    if resultado.get('categoria') == 'red_flag_cardiovascular':
        return "Possível dor referida de origem cardíaca. Avaliação cardiológica prioritária antes de tratar a queixa musculoesquelética."

    if resultado.get('categoria') == 'padrao_inflamatorio':
        achados = ', '.join(resultado['padrao'].get('achados_inflamatorios', []))
        return f"Padrão inflamatório identificado ({achados}). Investigação sistêmica necessária antes de conduta local."

    # Avaliação completa
    provaveis = resultado.get('hipoteses_provaveis', [])
    possiveis = resultado.get('hipoteses_possiveis', [])
    padrao    = resultado.get('padrao', {}).get('padrao', '').lower()
    mecanismo = resultado.get('mecanismo', {}).get('mecanismo_dominante', '').lower()

    if not provaveis and not possiveis:
        exclusao = resultado.get('hipoteses_exclusao', [])
        excl_txt = ', '.join(e.replace('_', ' ') for e in exclusao)
        return f"Quadro sem hipótese diagnóstica predominante. Excluir ativamente: {excl_txt}."

    hipotese_principal = provaveis[0] if provaveis else possiveis[0]
    nome = hipotese_principal['hipotese'].replace('_', ' ')
    achados_txt = ', '.join(hipotese_principal['positivos'][:3])

    partes = [f"Quadro compatível com {nome}"]
    if padrao:
        partes.append(f"de padrão {padrao}")
    if mecanismo and mecanismo != 'nociceptivo':
        partes.append(f"com componente {mecanismo}")
    if achados_txt:
        partes.append(f"associado a {achados_txt}")

    # Trauma
    if resultado.get('trauma_presente'):
        partes.append("Trauma presente — imagem obrigatória")

    # Nociplástico
    if resultado.get('mecanismo', {}).get('alerta_nociplastico'):
        partes.append("Alerta de sensibilização central — resposta a AINE e infiltração pode ser limitada")

    return '. '.join(partes) + '.'


def gerar_plano_sistema(resultado):
    """
    Gera plano clínico estruturado a partir do output do engine.
    Retorna lista de strings prontas para impressão.
    Não inventa conteúdo — só organiza o que o engine retornou.
    """
    plano = []

    categoria = resultado.get('categoria', '')

    # --- RED FLAGS E PADRÃO INFLAMATÓRIO ---
    if categoria == 'red_flag_emergencia':
        plano.append('⚠️  EMERGÊNCIA — Conduta imediata:')
        for f in resultado.get('red_flags', {}).get('flags', []):
            plano.append(f"   → {f['acao']}")
        return plano

    if categoria == 'red_flag_cardiovascular':
        plano.append('⚠️  Avaliar origem cardíaca antes de tratar queixa MSK:')
        plano.append('   → ECG e troponina se indicado')
        return plano

    if categoria == 'padrao_inflamatorio':
        plano.append('Investigação do padrão inflamatório:')
        for e in resultado.get('padrao', {}).get('exames_sugeridos', []):
            plano.append(f'   → {e}')
        plano.append('Conduta:')
        for c in resultado.get('padrao', {}).get('conduta_padrao', []):
            plano.append(f'   → {c}')
        return plano

    # --- AVALIAÇÃO COMPLETA ---
    provaveis = resultado.get('hipoteses_provaveis', [])
    possiveis = resultado.get('hipoteses_possiveis', [])

    # Alerta de trauma
    if resultado.get('alerta_trauma'):
        plano.append(f"⚠️  {resultado['alerta_trauma']}")

    if not provaveis and not possiveis:
        exclusao = resultado.get('hipoteses_exclusao', [])
        if exclusao:
            plano.append('Excluir ativamente:')
            for e in exclusao:
                plano.append(f'   → {e.replace("_", " ")}')
        return plano

    h = provaveis[0] if provaveis else possiveis[0]

    # 1. CONDUTA INICIAL
    if h.get('conduta'):
        plano.append('Conduta inicial:')
        for c in h['conduta']:
            plano.append(f'   → {c}')

    # 2. FISIOTERAPIA
    if h.get('fisioterapia'):
        plano.append(f'Fisioterapia: {h["fisioterapia"]}')

    # 3. IMAGEM
    if h.get('imagem'):
        plano.append(f'Imagem: {h["imagem"]}')
    else:
        plano.append('Imagem: não indicada neste momento')

    # 4. ENCAMINHAMENTO
    if h.get('encaminhar'):
        plano.append(f'Encaminhar: {h["encaminhar"]}')

    # 5. INFILTRAÇÃO
    if h.get('candidato_infiltracao'):
        plano.append(f'Infiltração: considerar — {h["motivo_infiltracao"]}')
        for b in h.get('bloqueios_seguranca', []):
            plano.append(f'   ⛔ {b}')
    else:
        plano.append(f'Infiltração: não indicada — {h.get("motivo_infiltracao", "")}')

    # 6. REAVALIAÇÃO
    plano.append('Reavaliar em 4-6 semanas ou antes se piora.')

    # 7. HIPÓTESES SECUNDÁRIAS
    if possiveis:
        nomes = ', '.join(h['hipotese'].replace('_', ' ') for h in possiveis)
        plano.append(f'Também considerar: {nomes}.')

    return plano


def formatar_plano_texto(resultado):
    """
    Retorna análise + plano em formato pronto para prontuário.
    """
    analise = gerar_analise_sistema(resultado)
    plano   = gerar_plano_sistema(resultado)

    linhas = []
    linhas.append('Análise do sistema:')
    linhas.append(analise)
    linhas.append('')
    linhas.append('Plano do sistema:')
    for item in plano:
        linhas.append(item)

    return '\n'.join(linhas)


# =============================================================================
# TESTE
# =============================================================================

if __name__ == '__main__':
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

    from modules.raciocinio.musculoesqueletico.ombro.core.engine_ombro import interpretar_ombro

    base = {
        'idade': 45, 'comorbidades_paciente': 'HAS',
        'medicacoes_paciente': 'losartana 50mg',
        'febre': False, 'perda_de_peso_inexplicada': False, 'dor_noturna_sem_alivio': False,
        'historico_cancer': False, 'imunossupressao': False, 'uso_cronico_corticoide': False,
        'deficit_neurologico_progressivo': False, 'hemartrose_imediata': False,
        'trauma_significativo': False, 'osteoporose': False, 'idade_acima_70': False,
        'dor_nova': True, 'bacteremia_recente': False, 'uso_drogas_iv': False,
        'red_flag_cardiovascular': False, 'sinal_trauma_importante': False,
        'articulacoes_multiplas': False, 'articulacoes_multiplas_afetadas': False,
        'rigidez_matinal_acima_60min': False, 'rigidez_matinal_menos_30min': False,
        'calor_ou_eritema_articular': False, 'sem_calor_ou_eritema': True,
        'sintomas_sistemicos': False, 'envolvimento_simetrico': False,
        'piora_com_atividade': True, 'melhora_com_repouso': True,
        'piora_com_repouso': False, 'melhora_com_atividade_leve': False,
        'inicio_insidioso_com_uso': True, 'dor_localizada': True,
        'dor_generalizada_ou_difusa': False, 'piora_com_movimento_ou_carga': True,
        'sem_sintomas_neurologicos': True, 'formigamento_ou_dormencia': False,
        'deficit_sensorial_ou_reflexo': False, 'piora_noturna_caracteristica': False,
        'dor_difusa_ombro': False, 'queimacao_ou_choque_eletrico': False,
        'distribuicao_dermatomal': False, 'alodinia': False,
        'dor_desproporcional_ao_exame': False, 'fadiga_cronica': False,
        'sono_nao_restaurador': False, 'comprometimento_cognitivo_leve': False,
        'multiplos_sindromes_somaticos': False, 'falha_de_analgesia_convencional': False,
        'csi_acima_40': False, 'dn4_acima_4': False, 'paindetect_acima_19': False,
        'dor_subacromia_lateral': True, 'dor_anterior_bicipital': False,
        'dor_superior_ac': False, 'dor_posterior': False,
        'piora_overhead': True, 'piora_deceleracao': False,
        'piora_rotacao_externa': False, 'piora_adducao_cruzada': False,
        'sensacao_dando_tranco': False, 'dor_virou_rigidez': False,
        'inicio_insidioso': True, 'dor_mecanica': True, 'dor_noturna': True,
        'atividade_overhead_repetitiva': True, 'atleta_arremessador': False,
        'diabetes': False, 'hipotireoidismo': False,
        'cirurgia_ou_imobilizacao_previa': False, 'trauma_ac_previo': False,
        'dificuldade_alcance_posterior': False, 'fraqueza_subjetiva': False,
        'duracao_acima_6_semanas': False, 'duracao_acima_3_meses': False,
        'atrofia_muscular': False, 'deformidade_ac': False, 'calor_local': False,
        'dor_palpacao_subacromia': True, 'dor_palpacao_ac': False,
        'dor_palpacao_sulco_bicipital': False,
        'rom_ativo_limitado': False, 'rom_passivo_limitado': False,
        'padrão_restricao_re_predomina': False, 'padrão_restricao_global': False,
        'fraqueza_abducao': False, 'fraqueza_rotacao_externa': False,
        'fraqueza_rotacao_interna': False,
        'arco_doloroso_positivo': True, 'hawkins_kennedy_positivo': True,
        'neer_positivo': True, 'empty_can_positivo': False,
        'drop_arm_positivo': False, 'external_rotation_lag_positivo': False,
        'gerber_liftoff_positivo': False, 'speed_positivo': False,
        'yergason_positivo': False, 'cross_arm_positivo': False,
        'obrien_positivo': False, 'apprehension_positivo': False,
        'exame_fisico_local_positivo': True,
        'idade_acima_60': False, 'idade_acima_50': False, 'idade_acima_40': True,
    }

    resultado = interpretar_ombro(base)
    print(formatar_plano_texto(resultado))