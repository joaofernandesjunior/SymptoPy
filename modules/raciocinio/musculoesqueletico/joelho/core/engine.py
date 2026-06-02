# joelho/core/engine.py
# Motor de raciocínio clínico para dor no joelho
# Recebe: dicionário de dados clínicos (bool + strings)
# Devolve: red flags / padrão / hipóteses / conduta / imagem
# Base: Open Evidence 2026 / OARSI / ACR / Pocket Guide MSK

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from modules.raciocinio.musculoesqueletico.red_flags_msk import avaliar_red_flags_msk, aplicar_trava_idoso_aine
from modules.raciocinio.musculoesqueletico.padrao_dor import classificar_mecanismo_dor
from modules.raciocinio.musculoesqueletico.mecanico_inflamatorio import classificar_padrao
from modules.raciocinio.musculoesqueletico.regras_ottawa import ottawa_joelho


# =============================================================================
# 1. AUXILIAR
# =============================================================================

def _forca(score, forte, moderado):
    if score >= forte:
        return 'alta'
    if score >= moderado:
        return 'moderada'
    return 'baixa'


# =============================================================================
# 2. HIPÓTESES ESPECÍFICAS DO JOELHO
# =============================================================================

def avaliar_oa(dados):
    score = 0
    pos = []
    neg = []

    if dados.get('idade_acima_45'):
        score += 2; pos.append('idade > 45')
    else:
        neg.append('idade <= 45')

    if dados.get('dor_mecanica'):
        score += 2; pos.append('dor mecânica')
    else:
        neg.append('sem padrão mecânico')

    if dados.get('rigidez_matinal_menos_30min'):
        score += 2; pos.append('rigidez matinal < 30min')
    else:
        neg.append('rigidez >= 30min ou ausente')

    if dados.get('crepitacao'):
        score += 1; pos.append('crepitação')
    else:
        neg.append('sem crepitação')

    if dados.get('dor_linha_articular'):
        score += 1; pos.append('dor na linha articular')
    else:
        neg.append('sem dor na linha articular')

    if dados.get('derrame_articular'):
        score += 1; pos.append('derrame articular')
    else:
        neg.append('sem derrame')

    if dados.get('inicio_insidioso'):
        score += 1; pos.append('início insidioso')
    else:
        neg.append('início agudo')

    f = _forca(score, forte=7, moderado=5)
    conduta = [
        'Pilar 1: exercício de fortalecimento + perda de peso se IMC > 25',
        'Pilar 2: paracetamol regular; AINE tópico antes de AINE oral; atenção HAS/DRC',
        'Pilar 3: infiltração corticoide em crise aguda; ácido hialurônico se falha dos pilares 1 e 2',
        'Rx AP com carga para estadiamento Kellgren-Lawrence',
        'Encaminhar ortopedia se grau IV ou refratário com impacto funcional grave'
    ] if f in ['alta', 'moderada'] else []

    return {
        'hipotese': 'osteoartrose_joelho', 'score': score, 'forca': f,
        'provavel': f in ['alta', 'moderada'], 'positivos': pos, 'negativos': neg,
        'conduta': conduta, 'imagem': 'Rx AP com carga (estadiamento)',
        'candidato_infiltracao': True,
        'motivo_infiltracao': 'OA com dor refratária a conservador ou crise inflamatória aguda',
        'tipo_sugerido': 'corticoide (crise aguda) ou ácido hialurônico (dor crônica refratária)',
        'bloqueios_seguranca': ['excluir artrite séptica', 'não infiltrar se cirurgia < 6 semanas']
    }


def avaliar_menisco(dados):
    score = 0
    pos = []
    neg = []

    if dados.get('dor_linha_articular'):
        score += 3; pos.append('dor linha articular (sens 83%, esp 83%)')
    else:
        neg.append('sem dor na linha articular')

    if dados.get('mcmurray_positivo'):
        score += 3; pos.append('McMurray positivo (sens 61%, esp 84%)')
    else:
        neg.append('McMurray negativo')

    if dados.get('travamento_ou_estalido'):
        score += 2; pos.append('travamento ou estalido')
    else:
        neg.append('sem travamento')

    if dados.get('trauma_torcao_recente'):
        score += 2; pos.append('torção recente')
    else:
        neg.append('sem torção recente')

    if dados.get('derrame_horas_apos_trauma'):
        score += 1; pos.append('derrame horas após trauma')
    else:
        neg.append('sem derrame pós-trauma')

    if dados.get('idade_acima_40') and not dados.get('trauma_torcao_recente'):
        score += 1; pos.append('> 40 sem trauma — lesão degenerativa provável')

    f = _forca(score, forte=6, moderado=4)
    conduta = [
        'Conservador 4-6 semanas: repouso relativo, gelo, AINE',
        'Fisioterapia para fortalecimento e retorno funcional',
        'RM joelho se persistência após 4-6 semanas — NÃO pedir de rotina no início',
        'Encaminhar ortopedia se bloqueio mecânico persistente'
    ] if f in ['alta', 'moderada'] else []

    return {
        'hipotese': 'lesao_meniscal', 'score': score, 'forca': f,
        'provavel': f in ['alta', 'moderada'], 'positivos': pos, 'negativos': neg,
        'conduta': conduta, 'imagem': 'RM se falha conservadora após 4-6 semanas',
        'candidato_infiltracao': False,
        'motivo_infiltracao': 'Raramente indicada — somente em sinovite reativa refratária após falha conservadora',
        'tipo_sugerido': None,
        'bloqueios_seguranca': ['não infiltrar se bloqueio mecânico persistente']
    }


def avaliar_sdpf(dados):
    score = 0
    pos = []
    neg = []

    if dados.get('dor_anterior_joelho'):
        score += 2; pos.append('dor anterior / atrás da patela')
    else:
        neg.append('sem dor anterior')

    if dados.get('sinal_do_cinema'):
        score += 3; pos.append('sinal do cinema positivo')
    else:
        neg.append('sinal do cinema ausente')

    if dados.get('piora_escadas_ou_agachamento'):
        score += 2; pos.append('piora em escadas ou agachamento')
    else:
        neg.append('sem piora em escadas')

    if dados.get('squat_unipodal_positivo'):
        score += 2; pos.append('squat unipodal reproduz dor (sens 91%, esp 50%)')
    else:
        neg.append('squat unipodal negativo')

    if dados.get('dor_palpacao_facetas_patelares'):
        score += 1; pos.append('dor à palpação das facetas patelares')
    else:
        neg.append('sem dor patelar à palpação')

    if dados.get('idade_abaixo_40') and not dados.get('trauma'):
        score += 1; pos.append('adulto jovem sem trauma — padrão típico')

    f = _forca(score, forte=7, moderado=5)
    conduta = [
        'Fisioterapia é o tratamento principal — VMO e quadril',
        'Palmilhas e bandagem patelar como adjuvantes',
        'Repouso de impacto temporário; AINE como adjuvante',
        'NÃO pedir imagem na apresentação típica',
        'NÃO infiltrar casos biomecânicos puros'
    ] if f in ['alta', 'moderada'] else []

    return {
        'hipotese': 'sindrome_dor_patelofemoral', 'score': score, 'forca': f,
        'provavel': f in ['alta', 'moderada'], 'positivos': pos, 'negativos': neg,
        'conduta': conduta, 'imagem': 'Não indicado na apresentação típica',
        'candidato_infiltracao': False,
        'motivo_infiltracao': 'Não indicada em casos biomecânicos puros sem sinais inflamatórios',
        'tipo_sugerido': None,
        'bloqueios_seguranca': []
    }


def avaliar_bursite(dados):
    score = 0
    pos = []
    neg = []

    if dados.get('inchaço_sobre_patela'):
        score += 3; pos.append('edema mole sobre a patela')
    else:
        neg.append('sem edema pré-patelar')

    if dados.get('trabalho_ajoelhado'):
        score += 2; pos.append('trabalho ajoelhado')
    else:
        neg.append('sem exposição ajoelhada')

    if dados.get('dor_medial_abaixo_linha_articular'):
        score += 2; pos.append('dor medial ~5cm abaixo da linha articular (anserina)')
    else:
        neg.append('sem dor anserina')

    if dados.get('dor_cruzar_pernas'):
        score += 1; pos.append('dor ao cruzar as pernas')
    else:
        neg.append('sem dor ao cruzar pernas')

    if dados.get('obesidade_ou_oa_associada'):
        score += 1; pos.append('obesidade/OA — risco para bursite anserina')

    f = _forca(score, forte=5, moderado=3)
    septica = dados.get('febre') or dados.get('calor_intenso_local')
    conduta = []
    if f in ['alta', 'moderada']:
        conduta = ['Proteção local, gelo, AINE por 1-2 semanas',
                   'Afastar da atividade causadora']
        if septica:
            conduta.append('⚠️ NÃO INFILTRAR — suspeita séptica. Drenagem com cultura urgente.')
        else:
            conduta.append('Infiltração corticoide na bursa se refratária após 2 semanas')

    return {
        'hipotese': 'bursite_joelho', 'score': score, 'forca': f,
        'provavel': f in ['alta', 'moderada'], 'positivos': pos, 'negativos': neg,
        'conduta': conduta, 'imagem': 'Não indicado rotineiramente',
        'candidato_infiltracao': True,
        'motivo_infiltracao': 'Bursite refratária após 2 semanas de conservador',
        'tipo_sugerido': 'corticoide na bursa',
        'bloqueios_seguranca': ['NUNCA infiltrar se suspeita de bursite séptica (febre, calor intenso)']
    }


def avaliar_cisto_baker(dados):
    score = 0
    pos = []
    neg = []

    if dados.get('massa_fossa_poplitea'):
        score += 4; pos.append('massa/plenitude na fossa poplítea')
    else:
        neg.append('sem massa poplítea')

    if dados.get('dificuldade_flexao_completa'):
        score += 2; pos.append('dificuldade de flexão completa')
    else:
        neg.append('flexão completa preservada')

    if dados.get('transiluminacao_positiva'):
        score += 2; pos.append('transiluminação positiva')
    else:
        neg.append('transiluminação não realizada ou negativa')

    if dados.get('oa_ou_lesao_meniscal_conhecida'):
        score += 1; pos.append('causa base conhecida (OA ou menisco)')

    f = _forca(score, forte=5, moderado=3)
    conduta = [
        'Tratar a CAUSA BASE (OA ou menisco) — cisto é consequência',
        'AINE e repouso relativo',
        'Aspiração se volumoso e limitando flexão',
        'NÃO aspirar se líquido purulento ou hemorrágico'
    ] if f in ['alta', 'moderada'] else []

    return {
        'hipotese': 'cisto_de_baker', 'score': score, 'forca': f,
        'provavel': f in ['alta', 'moderada'], 'positivos': pos, 'negativos': neg,
        'conduta': conduta, 'imagem': 'Ultrassom se dúvida ou antes de aspiração',
        'candidato_infiltracao': True,
        'motivo_infiltracao': 'Cisto volumoso limitando flexão',
        'tipo_sugerido': 'aspiração guiada — tratar causa base simultaneamente',
        'bloqueios_seguranca': ['não aspirar se líquido purulento ou hemorrágico']
    }


# =============================================================================
# 3. AGREGADOR PRINCIPAL
# =============================================================================

def interpretar_joelho(dados):

    # BLOCO 1 — Red flags
    red_flags = avaliar_red_flags_msk(dados)
    if red_flags['tem_emergencia']:
        return {
            'categoria': 'red_flag_emergencia',
            'red_flags': red_flags,
            'mensagem': 'RED FLAG DE EMERGÊNCIA. Interromper avaliação de rotina.',
            'proximo_bloco': None
        }

    # BLOCO 2 — Ottawa (só se trauma agudo)
    ottawa = ottawa_joelho(dados) if dados.get('trauma_agudo') else None

    # BLOCO 3 — Padrão mecânico vs inflamatório
    padrao = classificar_padrao(dados)
    if padrao['alerta_inflamatorio']:
        return {
            'categoria': 'padrao_inflamatorio',
            'red_flags': red_flags,
            'ottawa': ottawa,
            'padrao': padrao,
            'mensagem': 'Padrão inflamatório. Solicitar labs e considerar reumatologia.',
            'proximo_bloco': None
        }

    # BLOCO 4 — Mecanismo de dor
    mecanismo = classificar_mecanismo_dor(dados)

    # BLOCO 5 — Hipóteses específicas
    candidatos = [
        avaliar_oa(dados),
        avaliar_menisco(dados),
        avaliar_sdpf(dados),
        avaliar_bursite(dados),
        avaliar_cisto_baker(dados),
    ]
    provaveis = sorted([c for c in candidatos if c['forca'] == 'alta'],
                       key=lambda x: x['score'], reverse=True)
    possiveis = sorted([c for c in candidatos if c['forca'] == 'moderada'],
                       key=lambda x: x['score'], reverse=True)
    exclusao = ['artrite_septica_precoce', 'gota_ou_pseudogota', 'fratura_osteocondral'] \
               if not provaveis and not possiveis else []

    # Trava de segurança — AINE vetado em ≥ 60 anos
    aplicar_trava_idoso_aine(provaveis, dados)
    aplicar_trava_idoso_aine(possiveis, dados)

    return {
        'categoria': 'avaliacao_completa',
        'red_flags': red_flags,
        'ottawa': ottawa,
        'padrao': padrao,
        'mecanismo': mecanismo,
        'hipoteses_provaveis': provaveis,
        'hipoteses_possiveis': possiveis,
        'hipoteses_exclusao': exclusao,
        'proximo_bloco': None
    }


# =============================================================================
# 4. TESTES
# =============================================================================

if __name__ == '__main__':

    base = {
        'febre': False, 'imunossupressao': False, 'uso_drogas_iv': False,
        'bacteremia_recente': False, 'historico_cancer': False,
        'perda_de_peso_inexplicada': False, 'dor_noturna_sem_alivio': False,
        'trauma_significativo': False, 'idade_acima_70': False, 'dor_nova': False,
        'uso_cronico_corticoide': False, 'osteoporose': False,
        'anestesia_em_sela': False, 'retencao_urinaria': False,
        'incontinencia_fecal': False, 'fraqueza_bilateral_mmii': False,
        'hemartrose_imediata': False, 'deficit_neurologico_progressivo': False,
        'rigidez_matinal_acima_60min': False, 'articulacoes_multiplas': False,
        'trauma_agudo': False, 'idade_acima_55': False,
        'sensibilidade_isolada_patela': False, 'sensibilidade_cabeca_fibula': False,
        'incapaz_flexao_90': False, 'incapaz_suportar_peso': False,
        'rigidez_matinal_menos_30min': False, 'piora_com_atividade': False,
        'melhora_com_repouso': False, 'inicio_insidioso_com_uso': False,
        'sem_calor_ou_eritema': False, 'crepitacao': False,
        'piora_com_repouso': False, 'melhora_com_atividade_leve': False,
        'calor_ou_eritema_articular': False, 'articulacoes_multiplas_afetadas': False,
        'sintomas_sistemicos': False, 'envolvimento_simetrico': False,
        'dor_localizada': False, 'piora_com_movimento_ou_carga': False,
        'trauma_ou_sobrecarga_recente': False, 'exame_fisico_local_positivo': False,
        'sem_sintomas_neurologicos': False, 'queimacao_ou_choque_eletrico': False,
        'formigamento_ou_dormencia': False, 'distribuicao_dermatomal': False,
        'alodinia': False, 'deficit_sensorial_ou_reflexo': False,
        'piora_noturna_caracteristica': False, 'dor_generalizada_ou_difusa': False,
        'dor_desproporcional_ao_exame': False, 'fadiga_cronica': False,
        'sono_nao_restaurador': False, 'comprometimento_cognitivo_leve': False,
        'multiplos_sindromes_somaticos': False, 'falha_de_analgesia_convencional': False,
        'csi_acima_40': False, 'dn4_acima_4': False, 'paindetect_acima_19': False,
        'idade_acima_45': False, 'dor_mecanica': False, 'dor_linha_articular': False,
        'derrame_articular': False, 'inicio_insidioso': False,
        'mcmurray_positivo': False, 'travamento_ou_estalido': False,
        'trauma_torcao_recente': False, 'derrame_horas_apos_trauma': False,
        'idade_acima_40': False, 'dor_anterior_joelho': False,
        'sinal_do_cinema': False, 'piora_escadas_ou_agachamento': False,
        'squat_unipodal_positivo': False, 'dor_palpacao_facetas_patelares': False,
        'idade_abaixo_40': False, 'trauma': False,
        'inchaço_sobre_patela': False, 'trabalho_ajoelhado': False,
        'dor_medial_abaixo_linha_articular': False, 'dor_cruzar_pernas': False,
        'obesidade_ou_oa_associada': False, 'calor_intenso_local': False,
        'massa_fossa_poplitea': False, 'dificuldade_flexao_completa': False,
        'transiluminacao_positiva': False, 'oa_ou_lesao_meniscal_conhecida': False,
        'idade_acima_50': False
    }

    casos = {
        'OA CLASSICA': {
            'idade_acima_45': True, 'idade_acima_55': True, 'dor_mecanica': True,
            'rigidez_matinal_menos_30min': True, 'crepitacao': True,
            'dor_linha_articular': True, 'inicio_insidioso': True,
            'piora_com_atividade': True, 'melhora_com_repouso': True,
            'sem_calor_ou_eritema': True, 'dor_localizada': True,
            'exame_fisico_local_positivo': True, 'sem_sintomas_neurologicos': True
        },
        'LESAO MENISCAL': {
            'trauma_agudo': True, 'trauma_torcao_recente': True,
            'dor_linha_articular': True, 'mcmurray_positivo': True,
            'travamento_ou_estalido': True, 'derrame_horas_apos_trauma': True,
            'dor_mecanica': True, 'piora_com_atividade': True,
            'dor_localizada': True, 'exame_fisico_local_positivo': True
        },
        'SDPF JOVEM': {
            'dor_anterior_joelho': True, 'sinal_do_cinema': True,
            'piora_escadas_ou_agachamento': True, 'squat_unipodal_positivo': True,
            'dor_palpacao_facetas_patelares': True, 'idade_abaixo_40': True,
            'dor_localizada': True, 'piora_com_movimento_ou_carga': True,
            'sem_sintomas_neurologicos': True
        },
        'RED FLAG SEPTICA': {
            'febre': True, 'imunossupressao': True,
            'calor_ou_eritema_articular': True, 'derrame_articular': True
        }
    }

    for nome, updates in casos.items():
        caso = base.copy()
        caso.update(updates)
        print(f'\n{"="*55}')
        print(f'CASO: {nome}')
        print('='*55)
        r = interpretar_joelho(caso)
        print(f"Categoria: {r['categoria']}")

        if r['categoria'] == 'red_flag_emergencia':
            for f in r['red_flags']['flags']:
                print(f"  [{f['urgencia'].upper()}] {f['achado']}")
                print(f"  Ação: {f['acao']}")

        elif r['categoria'] == 'padrao_inflamatorio':
            print(f"  Padrão: {r['padrao']['padrao']}")
            print(f"  Exames: {r['padrao']['exames_sugeridos']}")

        else:
            if r.get('ottawa'):
                print(f"  Ottawa: {r['ottawa']['acao']}")
            print(f"  Padrão: {r['padrao']['padrao']}")
            print(f"  Mecanismo: {r['mecanismo']['mecanismo_dominante']}")
            if r['hipoteses_provaveis']:
                print(f"  Hipóteses prováveis:")
                for h in r['hipoteses_provaveis']:
                    print(f"    [{h['forca'].upper()}] {h['hipotese']} (score {h['score']})")
                    for c in h['conduta']:
                        print(f"      → {c}")
            if r['hipoteses_possiveis']:
                print(f"  Hipóteses possíveis:")
                for h in r['hipoteses_possiveis']:
                    print(f"    [{h['forca'].upper()}] {h['hipotese']} (score {h['score']})")
            if r['hipoteses_exclusao']:
                print(f"  Considerar exclusão: {r['hipoteses_exclusao']}")