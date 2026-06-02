# engine_ombro.py — V2
# Motor de raciocínio clínico para dor no ombro
# Responsabilidade: diagnóstico + padrão + conduta de alto nível
#                   candidato a infiltração (sim/não + motivo + bloqueios)
#                   encaminhamento (fisioterapia + ortopedia)
#                   alertas farmacológicos (camada separada, com fallback)
#
# NÃO responsabilidade deste engine:
#   — detalhes técnicos de infiltração (→ módulo procedimentos)
#   — posologia e doses (→ apoio_clinico/medicamentos)
#   — incidências radiológicas específicas (→ runner/documentação)
#
# Base: Open Evidence 2026 / Pocket Guide MSK (Cooper) / ACR / AAOS

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from modules.raciocinio.musculoesqueletico.red_flags_msk import avaliar_red_flags_msk, aplicar_trava_idoso_aine
from modules.raciocinio.musculoesqueletico.padrao_dor import classificar_mecanismo_dor
from modules.raciocinio.musculoesqueletico.mecanico_inflamatorio import classificar_padrao


def _tentar_alertas_farmacologicos(meds, comorbidades, idade, medicacoes, sito):
    """Chama apoio farmacológico com fallback seguro — engine não quebra se mudar."""
    try:
        from apoio_clinico.medicamentos.alertas import gerar_alertas_farmacologicos
        return gerar_alertas_farmacologicos(
            medicamentos=meds,
            comorbidades_str=comorbidades,
            idade=idade,
            medicacoes_str=medicacoes,
            sito_injecao=sito
        )
    except Exception:
        return None  # engine continua mesmo se módulo farmacológico falhar


# =============================================================================
# AUXILIAR
# =============================================================================

def _forca(score, forte, moderado):
    if score >= forte:    return 'alta'
    if score >= moderado: return 'moderada'
    return 'baixa'

def _hipotese_base(nome, score, forca, pos, neg,
                   conduta, imagem, encaminhar,
                   candidato_infiltracao, motivo_infiltracao, bloqueios_seguranca,
                   fisioterapia_msg, meds_sugeridos, sito_injecao=None):
    """
    Estrutura padrão de retorno de hipótese.
    Centraliza campos para facilitar manutenção futura.
    """
    return {
        'hipotese':               nome,
        'score':                  score,
        'forca':                  forca,
        'provavel':               forca in ['alta', 'moderada'],
        'positivos':              pos,
        'negativos':              neg,
        'conduta':                conduta,
        'imagem':                 imagem,
        'encaminhar':             encaminhar,
        'candidato_infiltracao':  candidato_infiltracao,
        'motivo_infiltracao':     motivo_infiltracao,
        'bloqueios_seguranca':    bloqueios_seguranca,
        'fisioterapia':           fisioterapia_msg,
        'medicamentos_sugeridos': meds_sugeridos,
        'sito_injecao':           sito_injecao,
    }


# =============================================================================
# HIPÓTESES ESPECÍFICAS DO OMBRO
# =============================================================================

def avaliar_impingement_manguito(dados):
    score = 0; pos = []; neg = []

    if dados.get('dor_subacromia_lateral'):
        score += 3; pos.append('dor subacromial / lateral')
    else: neg.append('sem dor subacromial')

    if dados.get('piora_overhead'):
        score += 2; pos.append('piora com overhead')
    else: neg.append('sem piora overhead')

    if dados.get('arco_doloroso_positivo'):
        score += 2; pos.append('arco doloroso positivo (sens 71%, esp 81%)')
    else: neg.append('arco doloroso negativo')

    if dados.get('hawkins_kennedy_positivo'):
        score += 1; pos.append('Hawkins-Kennedy positivo')
    else: neg.append('Hawkins-Kennedy negativo')

    if dados.get('neer_positivo'):
        score += 1; pos.append('Neer positivo')
    else: neg.append('Neer negativo')

    if dados.get('dor_palpacao_subacromia'):
        score += 1; pos.append('dor à palpação subacromial')
    else: neg.append('sem dor à palpação subacromial')

    if dados.get('dor_noturna'):
        score += 1; pos.append('dor noturna ao deitar sobre o ombro')

    if dados.get('atividade_overhead_repetitiva'):
        score += 1; pos.append('atividade overhead repetitiva')

    f = _forca(score, forte=7, moderado=5)
    return _hipotese_base(
        nome='sindrome_subacromial_impingement',
        score=score, forca=f, pos=pos, neg=neg,
        conduta=[
            'Fisioterapia supervisionada como tratamento principal',
            'Analgesia oral ou tópica para controle sintomático',
            'Modificação de atividades enquanto em reabilitação',
            'Imagem se sintomas > 6 semanas ou suspeita de ruptura',
        ],
        imagem='Rx ombro se > 6 semanas. Considerar RM se suspeita de ruptura ou falha conservadora.',
        encaminhar='Ortopedia se falha após 3-6 meses de conservador.',
        candidato_infiltracao=True,
        motivo_infiltracao='Impingement limitando participação na fisioterapia',
        bloqueios_seguranca=[
            'Excluir artrite séptica',
            'Não infiltrar se suspeita de ruptura total',
        ],
        fisioterapia_msg='Encaminhar fisioterapia: fortalecimento do manguito rotador e estabilizadores escapulares.',
        meds_sugeridos=['aine_oral', 'aine_topico', 'paracetamol', 'corticoide_injetavel'],
        sito_injecao='subacromia_ombro',
    )


def avaliar_ruptura_manguito(dados):
    score = 0; pos = []; neg = []

    if dados.get('external_rotation_lag_positivo'):
        score += 4; pos.append('lag de RE positivo (esp 94%, LR+ 7.2) — melhor teste')
    else: neg.append('lag de RE negativo')

    if dados.get('drop_arm_positivo'):
        score += 3; pos.append('drop arm positivo (esp 93%) — sugere ruptura total')
    else: neg.append('drop arm negativo')

    if dados.get('empty_can_positivo'):
        score += 2; pos.append('empty can positivo')
    else: neg.append('empty can negativo')

    if dados.get('fraqueza_abducao'):
        score += 2; pos.append('fraqueza à abdução')
    else: neg.append('força de abdução preservada')

    if dados.get('fraqueza_rotacao_externa'):
        score += 2; pos.append('fraqueza à rotação externa')
    else: neg.append('força de RE preservada')

    if dados.get('atrofia_muscular'):
        score += 2; pos.append('atrofia muscular visível')
    else: neg.append('sem atrofia')

    if dados.get('idade_acima_60'):
        score += 1; pos.append('> 60 anos — prevalência aumentada')

    f = _forca(score, forte=7, moderado=5)

    ruptura_total = dados.get('drop_arm_positivo') or dados.get('external_rotation_lag_positivo')

    return _hipotese_base(
        nome='ruptura_manguito_rotador',
        score=score, forca=f, pos=pos, neg=neg,
        conduta=[
            'RM de ombro para estadiar e guiar decisão',
            'Fisioterapia como primeira linha em ruptura parcial ou idoso sedentário',
            'Analgesia com paracetamol ou tópico — evitar AINE oral se perfil de risco',
        ],
        imagem='RM ombro — necessária para estadiar e guiar decisão conservador vs cirúrgico.',
        encaminhar='Ortopedia: ruptura total em paciente jovem/ativo ou falha após 3 meses de conservador.',
        candidato_infiltracao=not ruptura_total,
        motivo_infiltracao=(
            'Ruptura parcial refratária — considerar infiltração apenas após fisioterapia'
            if not ruptura_total else
            'Não infiltrar — suspeita de ruptura total'
        ),
        bloqueios_seguranca=['Não infiltrar se ruptura total confirmada ou fortemente suspeita'],
        fisioterapia_msg='Encaminhar fisioterapia: informar suspeita de ruptura. Fortalecimento progressivo e estabilização escapular.',
        meds_sugeridos=['paracetamol', 'aine_topico', 'aine_oral'],
        sito_injecao='subacromia_ombro' if not ruptura_total else None,
    )


def avaliar_capsulite_adesiva(dados):
    score = 0; pos = []; neg = []

    if dados.get('dor_virou_rigidez'):
        score += 4; pos.append('dor que progressivamente virou rigidez — padrão clássico')
    else: neg.append('sem padrão dor→rigidez')

    if dados.get('rom_passivo_limitado'):
        score += 3; pos.append('ROM passivo limitado')
    else: neg.append('ROM passivo preservado')

    if dados.get('padrão_restricao_re_predomina'):
        score += 2; pos.append('restrição de RE predominante — padrão capsular')
    else: neg.append('sem padrão capsular típico')

    if dados.get('padrão_restricao_global'):
        score += 2; pos.append('limitação global de movimentos')

    if dados.get('dificuldade_alcance_posterior'):
        score += 1; pos.append('dificuldade de alcançar área posterior')

    if dados.get('diabetes'):
        score += 1; pos.append('diabetes — principal fator de risco')

    if dados.get('hipotireoidismo'):
        score += 1; pos.append('hipotireoidismo — fator de risco')

    if dados.get('cirurgia_ou_imobilizacao_previa'):
        score += 1; pos.append('cirurgia ou imobilização prévia')

    f = _forca(score, forte=7, moderado=5)
    return _hipotese_base(
        nome='capsulite_adesiva',
        score=score, forca=f, pos=pos, neg=neg,
        conduta=[
            'Analgesia para controle da dor',
            'Fisioterapia: mobilização passiva progressiva e alongamento capsular',
            'Considerar infiltração precoce — evidência de encurtamento da duração dos sintomas',
            'Informar sobre história natural: resolução esperada em 12-36 meses',
        ],
        imagem='Rx ombro para excluir outras causas. RM se dúvida diagnóstica.',
        encaminhar='Ortopedia se sem melhora após 9-12 meses (liberação artroscópica).',
        candidato_infiltracao=True,
        motivo_infiltracao='Capsulite adesiva — infiltração glenoumeral pode encurtar duração dos sintomas',
        bloqueios_seguranca=[
            'Monitorar glicemia 5-7 dias se diabético',
            'Preferir abordagem intra-articular glenoumeral sobre subacromial',
        ],
        fisioterapia_msg='Encaminhar fisioterapia: mobilização passiva progressiva, alongamento capsular. Combinar com infiltração para melhores resultados.',
        meds_sugeridos=['paracetamol', 'aine_oral', 'aine_topico', 'corticoide_injetavel'],
        sito_injecao='glenoumeral',
    )


def avaliar_tendinopatia_biceps(dados):
    score = 0; pos = []; neg = []

    if dados.get('dor_anterior_bicipital'):
        score += 3; pos.append('dor anterior / sulco bicipital')
    else: neg.append('sem dor anterior')

    if dados.get('dor_palpacao_sulco_bicipital'):
        score += 2; pos.append('dor à palpação do sulco bicipital')
    else: neg.append('sem dor à palpação do sulco')

    if dados.get('speed_positivo'):
        score += 2; pos.append('Speed positivo (sens 54%, esp 81%)')
    else: neg.append('Speed negativo')

    if dados.get('yergason_positivo'):
        score += 2; pos.append('Yergason positivo (sens 43%, esp 79%)')
    else: neg.append('Yergason negativo')

    if dados.get('piora_overhead'):
        score += 1; pos.append('piora overhead')

    if dados.get('piora_deceleracao'):
        score += 1; pos.append('piora com desaceleração')

    f = _forca(score, forte=7, moderado=4)
    return _hipotese_base(
        nome='tendinopatia_biceps',
        score=score, forca=f, pos=pos, neg=neg,
        conduta=[
            'Fisioterapia como primeira linha',
            'Analgesia oral ou tópica',
            'Modificação de atividades',
            'Infiltração na bainha bicipital apenas em casos selecionados refratários',
        ],
        imagem='US ou RM se suspeita de ruptura parcial ou SLAP associado.',
        encaminhar='Ortopedia se falha após 3 meses ou suspeita de SLAP.',
        candidato_infiltracao=True,
        motivo_infiltracao='Tendinopatia bicipital refratária — infiltração da bainha em casos selecionados',
        bloqueios_seguranca=[
            'Não infiltrar intratendinoso — risco de ruptura',
            'Preferir guia ultrassonográfico para infiltração bicipital',
        ],
        fisioterapia_msg='Encaminhar fisioterapia: fortalecimento excêntrico do bíceps, mobilização neural.',
        meds_sugeridos=['aine_oral', 'aine_topico', 'paracetamol'],
        sito_injecao=None,
    )


def avaliar_patologia_ac(dados):
    score = 0; pos = []; neg = []

    if dados.get('dor_superior_ac'):
        score += 3; pos.append('dor na face superior / AC')
    else: neg.append('sem dor superior')

    if dados.get('cross_arm_positivo'):
        score += 3; pos.append('cross-arm adduction positivo (sens 77%, esp 79%)')
    else: neg.append('cross-arm negativo')

    if dados.get('dor_palpacao_ac'):
        score += 2; pos.append('dor à palpação da AC')
    else: neg.append('sem dor à palpação AC')

    if dados.get('deformidade_ac'):
        score += 2; pos.append('deformidade AC visível')
    else: neg.append('sem deformidade AC')

    if dados.get('trauma_ac_previo'):
        score += 1; pos.append('trauma AC prévio')

    if dados.get('piora_adducao_cruzada'):
        score += 1; pos.append('piora com adução cruzada')

    f = _forca(score, forte=7, moderado=4)
    return _hipotese_base(
        nome='patologia_ac_joint',
        score=score, forca=f, pos=pos, neg=neg,
        conduta=[
            'Rx ombro para estadiar',
            'Analgesia e modificação de atividades',
            'Considerar infiltração AC se OA confirmada e refratária',
        ],
        imagem='Rx ombro AP — considerar incidência com carga conforme suspeita clínica.',
        encaminhar='Ortopedia se separação AC grave ou OA com limitação funcional importante.',
        candidato_infiltracao=True,
        motivo_infiltracao='OA AC refratária ao conservador',
        bloqueios_seguranca=[
            'Volume pequeno — AC é articulação pequena',
            'Excluir separação AC aguda antes de infiltrar',
        ],
        fisioterapia_msg='Encaminhar fisioterapia: fortalecimento periscapular, correção postural.',
        meds_sugeridos=['aine_oral', 'aine_topico', 'paracetamol', 'corticoide_injetavel'],
        sito_injecao='ac_joint',
    )


def avaliar_instabilidade_slap(dados):
    """V1 conservador — diagnosticar padrão e encaminhar. Não pesar demais."""
    score = 0; pos = []; neg = []

    if dados.get('sensacao_dando_tranco'):
        score += 3; pos.append('sensação de ombro cedendo')
    else: neg.append('sem instabilidade relatada')

    if dados.get('apprehension_positivo'):
        score += 3; pos.append('apprehension positivo — instabilidade anterior')
    else: neg.append('apprehension negativo')

    if dados.get('obrien_positivo'):
        score += 2; pos.append("O'Brien positivo — possível SLAP")
    else: neg.append("O'Brien negativo")

    if dados.get('atleta_arremessador'):
        score += 1; pos.append('atleta de arremesso')

    if dados.get('dor_posterior'):
        score += 1; pos.append('dor posterior — padrão labral')

    f = _forca(score, forte=6, moderado=4)
    return _hipotese_base(
        nome='instabilidade_labral',
        score=score, forca=f, pos=pos, neg=neg,
        conduta=[
            'Encaminhar ortopedia e solicitar RM',
            'Fisioterapia como primeira linha se instabilidade leve/atraumática',
        ],
        imagem='RM ombro — necessária para avaliação labral.',
        encaminhar='Ortopedia — decisão conservador vs cirúrgico depende do grau e mecanismo.',
        candidato_infiltracao=False,
        motivo_infiltracao='Não infiltrar antes de RM — pode mascarar lesão labral',
        bloqueios_seguranca=['Aguardar diagnóstico por imagem antes de qualquer procedimento'],
        fisioterapia_msg='Encaminhar fisioterapia: estabilização glenoumeral dinâmica. Instabilidade atraumática responde bem à reabilitação.',
        meds_sugeridos=['paracetamol', 'aine_topico'],
        sito_injecao=None,
    )


# =============================================================================
# AGREGADOR PRINCIPAL
# =============================================================================

def interpretar_ombro(dados):

    # BLOCO 1 — Red flags sistêmicas
    red_flags = avaliar_red_flags_msk(dados)
    if red_flags['tem_emergencia']:
        return {
            'categoria': 'red_flag_emergencia',
            'red_flags': red_flags,
            'mensagem': 'RED FLAG DE EMERGÊNCIA. Interromper avaliação de rotina.',
        }

    # Red flag cardiovascular — dor referida
    if dados.get('red_flag_cardiovascular'):
        return {
            'categoria': 'red_flag_cardiovascular',
            'mensagem': 'Dor torácica associada. Avaliar origem cardíaca antes de tratar ombro.',
            'red_flags': red_flags,
        }

    # BLOCO 2 — Trauma: marca, obriga imagem, mas CONTINUA o raciocínio
    trauma_presente = dados.get('sinal_trauma_importante', False)

    # BLOCO 3 — Padrão mecânico vs inflamatório
    padrao = classificar_padrao(dados)
    if padrao['alerta_inflamatorio']:
        return {
            'categoria': 'padrao_inflamatorio',
            'padrao': padrao,
            'mensagem': 'Padrão inflamatório. Solicitar labs e considerar reumatologia.',
        }

    # BLOCO 4 — Mecanismo de dor
    mecanismo = classificar_mecanismo_dor(dados)

    # BLOCO 5 — Hipóteses específicas (incluindo traumáticas)
    candidatos = [
        avaliar_impingement_manguito(dados),
        avaliar_ruptura_manguito(dados),
        avaliar_capsulite_adesiva(dados),
        avaliar_tendinopatia_biceps(dados),
        avaliar_patologia_ac(dados),
        avaliar_instabilidade_slap(dados),
    ]

    provaveis = sorted(
        [c for c in candidatos if c['forca'] == 'alta'],
        key=lambda x: x['score'], reverse=True
    )
    possiveis = sorted(
        [c for c in candidatos if c['forca'] == 'moderada'],
        key=lambda x: x['score'], reverse=True
    )
    exclusao = ['artrite_septica_ombro', 'fratura_occult', 'neoplasia'] \
               if not provaveis and not possiveis else []

    # BLOCO 6 — Alertas farmacológicos (camada separada, com fallback)
    meds_sugeridos = []
    for h in provaveis + possiveis:
        for m in h.get('medicamentos_sugeridos', []):
            if m not in meds_sugeridos:
                meds_sugeridos.append(m)

    sito = provaveis[0].get('sito_injecao') if provaveis else None

    alertas_farm = _tentar_alertas_farmacologicos(
        meds=meds_sugeridos,
        comorbidades=dados.get('comorbidades_paciente', ''),
        idade=dados.get('idade', 0),
        medicacoes=dados.get('medicacoes_paciente', ''),
        sito=sito
    ) if meds_sugeridos else None

    # Trava de segurança — AINE vetado em ≥ 60 anos
    aplicar_trava_idoso_aine(provaveis, dados)
    aplicar_trava_idoso_aine(possiveis, dados)

    return {
        'categoria': 'avaliacao_completa',
        'trauma_presente': trauma_presente,
        'alerta_trauma': 'Solicitar Rx de ombro. Avaliar fratura e integridade neurovascular.' if trauma_presente else None,
        'red_flags': red_flags,
        'padrao': padrao,
        'mecanismo': mecanismo,
        'hipoteses_provaveis': provaveis,
        'hipoteses_possiveis': possiveis,
        'hipoteses_exclusao': exclusao,
        'alertas_farmacologicos': alertas_farm,
    }


# =============================================================================
# TESTES
# =============================================================================

if __name__ == '__main__':
    base = {
        'idade': 30, 'comorbidades_paciente': 'nega', 'medicacoes_paciente': 'nega',
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
        'piora_com_atividade': False, 'melhora_com_repouso': False,
        'piora_com_repouso': False, 'melhora_com_atividade_leve': False,
        'inicio_insidioso_com_uso': False, 'dor_localizada': True,
        'dor_generalizada_ou_difusa': False, 'piora_com_movimento_ou_carga': False,
        'sem_sintomas_neurologicos': True, 'formigamento_ou_dormencia': False,
        'deficit_sensorial_ou_reflexo': False, 'piora_noturna_caracteristica': False,
        'dor_difusa_ombro': False, 'queimacao_ou_choque_eletrico': False,
        'distribuicao_dermatomal': False, 'alodinia': False,
        'dor_desproporcional_ao_exame': False, 'fadiga_cronica': False,
        'sono_nao_restaurador': False, 'comprometimento_cognitivo_leve': False,
        'multiplos_sindromes_somaticos': False, 'falha_de_analgesia_convencional': False,
        'csi_acima_40': False, 'dn4_acima_4': False, 'paindetect_acima_19': False,
        'dor_subacromia_lateral': False, 'dor_anterior_bicipital': False,
        'dor_superior_ac': False, 'dor_posterior': False,
        'piora_overhead': False, 'piora_deceleracao': False,
        'piora_rotacao_externa': False, 'piora_adducao_cruzada': False,
        'sensacao_dando_tranco': False, 'dor_virou_rigidez': False,
        'inicio_insidioso': False, 'dor_mecanica': False, 'dor_noturna': False,
        'atividade_overhead_repetitiva': False, 'atleta_arremessador': False,
        'diabetes': False, 'hipotireoidismo': False,
        'cirurgia_ou_imobilizacao_previa': False, 'trauma_ac_previo': False,
        'incapaz_levantar_braco_altura_ombro': False,
        'dificuldade_alcance_posterior': False, 'fraqueza_subjetiva': False,
        'duracao_acima_6_semanas': False, 'duracao_acima_3_meses': False,
        'atrofia_muscular': False, 'deformidade_ac': False, 'calor_local': False,
        'dor_palpacao_subacromia': False, 'dor_palpacao_ac': False,
        'dor_palpacao_sulco_bicipital': False,
        'rom_ativo_limitado': False, 'rom_passivo_limitado': False,
        'padrão_restricao_re_predomina': False, 'padrão_restricao_global': False,
        'fraqueza_abducao': False, 'fraqueza_rotacao_externa': False,
        'fraqueza_rotacao_interna': False, 'arco_doloroso_positivo': False,
        'hawkins_kennedy_positivo': False, 'neer_positivo': False,
        'empty_can_positivo': False, 'drop_arm_positivo': False,
        'external_rotation_lag_positivo': False, 'gerber_liftoff_positivo': False,
        'speed_positivo': False, 'yergason_positivo': False,
        'cross_arm_positivo': False, 'obrien_positivo': False,
        'apprehension_positivo': False, 'exame_fisico_local_positivo': False,
        'idade_acima_60': False, 'idade_acima_50': False, 'idade_acima_40': False,
    }

    casos = {
        'IMPINGEMENT com trauma + HAS': {
            'idade': 45, 'comorbidades_paciente': 'HAS',
            'medicacoes_paciente': 'losartana 50mg',
            'sinal_trauma_importante': True,
            'dor_subacromia_lateral': True, 'piora_overhead': True,
            'arco_doloroso_positivo': True, 'hawkins_kennedy_positivo': True,
            'dor_palpacao_subacromia': True, 'dor_noturna': True,
            'piora_com_atividade': True, 'melhora_com_repouso': True,
        },
        'CAPSULITE com DM2': {
            'idade': 58, 'comorbidades_paciente': 'DM2',
            'medicacoes_paciente': 'metformina 850mg',
            'dor_virou_rigidez': True, 'rom_passivo_limitado': True,
            'padrão_restricao_re_predomina': True, 'diabetes': True,
            'dificuldade_alcance_posterior': True, 'dor_difusa_ombro': True,
            'duracao_acima_3_meses': True, 'idade_acima_50': True,
        },
        'RUPTURA com DRC eGFR 55, 65 anos': {
            'idade': 65, 'comorbidades_paciente': 'HAS, DRC eGFR 55',
            'medicacoes_paciente': 'losartana 50mg',
            'dor_subacromia_lateral': True, 'piora_overhead': True,
            'fraqueza_abducao': True, 'fraqueza_rotacao_externa': True,
            'external_rotation_lag_positivo': True, 'drop_arm_positivo': True,
            'atrofia_muscular': True, 'idade_acima_60': True,
            'idade_acima_50': True, 'dor_noturna': True,
            'piora_com_atividade': True,
        },
    }

    SEP = '=' * 58
    for nome, updates in casos.items():
        caso = base.copy(); caso.update(updates)
        r = interpretar_ombro(caso)
        print(f'\n{SEP}\nCASO: {nome}\n{SEP}')
        print(f'Categoria: {r["categoria"]}')

        if r['categoria'] == 'avaliacao_completa':
            if r.get('alerta_trauma'):
                print(f'⚠️  TRAUMA: {r["alerta_trauma"]}')
            print(f'Padrão: {r["padrao"]["padrao"].upper()} | Mecanismo: {r["mecanismo"]["mecanismo_dominante"].upper()}')

            for h in r['hipoteses_provaveis']:
                print(f'\n  [{h["forca"].upper()}] {h["hipotese"]} (score {h["score"]})')
                print(f'  Achados: {", ".join(h["positivos"][:3])}')
                print(f'  Conduta: {h["conduta"][0]}')
                print(f'  Imagem: {h["imagem"]}')
                print(f'  Encaminhar: {h["encaminhar"]}')
                print(f'  Infiltração: {"✅ " + h["motivo_infiltracao"] if h["candidato_infiltracao"] else "❌ " + h["motivo_infiltracao"]}')
                print(f'  Fisio: {h["fisioterapia"]}')

            if r.get('alertas_farmacologicos'):
                print(f'\nALERTAS FARMACOLÓGICOS:{r["alertas_farmacologicos"]}')