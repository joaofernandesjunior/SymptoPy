# subjetivo.py — Anamnese de dor no joelho
# V3 — corrigido após revisão clínica detalhada
# Separado do engine — salva JSON para revisão antes de processar
# Rodar da raiz: python3 -m modules.sintomas.musculoesqueletico.joelho.subjetivo

import json
import os
import sys
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
from utils.perguntas import sn


# =============================================================================
# AUXILIARES
# =============================================================================

def _bloco(titulo):
    print(f'\n{"─"*50}')
    print(f'  {titulo}')
    print(f'{"─"*50}')

def perguntar_int(prompt):
    while True:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print('  Digite um número inteiro.')

def completar_chaves_padrao(dados):
    """
    Preenche chaves que o engine MSK espera mas que não pertencem
    à anamnese específica de joelho.

    Chaves de cauda equina (anestesia_em_sela, retencao_urinaria etc.)
    são da triagem MSK global — ficam False aqui e seriam perguntadas
    num módulo de coluna, não de joelho.

    deficit_neurologico_progressivo está no subjetivo apenas como
    triagem de red flag global MSK, não como hipótese de joelho.
    """
    defaults = {
        # Cauda equina — triagem MSK global, não joelho
        'anestesia_em_sela':        False,
        'retencao_urinaria':        False,
        'incontinencia_fecal':      False,
        'fraqueza_bilateral_mmii':  False,
        # Epidemiologia não perguntada nesta versão
        'uso_drogas_iv':            False,
        'bacteremia_recente':       False,
        # Osteoporose — placeholder para futura expansão (fratura por insuficiência)
        'osteoporose':              False,
        # Exame físico — preenchidos em objetivo.py
        'exame_fisico_local_positivo':   False,
        'derrame_articular':             False,
        'crepitacao':                    False,
        'mcmurray_positivo':             False,
        'squat_unipodal_positivo':       False,
        'dor_palpacao_facetas_patelares':False,
        'calor_intenso_local':           False,
        'transiluminacao_positiva':      False,
        # Mecanismo de dor — não perguntados diretamente no subjetivo de joelho
        'queimacao_ou_choque_eletrico':  False,
        'distribuicao_dermatomal':       False,
        'alodinia':                      False,
        'dor_desproporcional_ao_exame':  False,
        'fadiga_cronica':                False,
        'sono_nao_restaurador':          False,
        'comprometimento_cognitivo_leve':False,
        'multiplos_sindromes_somaticos': False,
        'falha_de_analgesia_convencional':False,
        'csi_acima_40':                  False,
        'dn4_acima_4':                   False,
        'paindetect_acima_19':           False,
    }
    for chave, valor in defaults.items():
        dados.setdefault(chave, valor)


# =============================================================================
# BLOCOS DE PERGUNTAS
# =============================================================================

def bloco_identificacao(dados):
    _bloco('IDENTIFICAÇÃO')
    idade = perguntar_int('  Idade do paciente: ')
    dados['idade']           = idade
    dados['idade_acima_70']  = idade >= 70
    dados['idade_acima_55']  = idade >= 55
    dados['idade_acima_50']  = idade >= 50
    dados['idade_acima_45']  = idade >= 45
    dados['idade_acima_40']  = idade >= 40
    dados['idade_abaixo_40'] = idade < 40

    print('\n  Essa dor é nova ou recorrente/crônica?')
    print('  1) Nova (primeira vez ou início recente)')
    print('  2) Recorrente / crônica (já vem de antes)')
    while True:
        op = input('  Opção (1/2): ').strip()
        if op in ('1', '2'):
            break
        print('  Digite 1 ou 2.')
    dados['dor_nova']     = (op == '1')
    dados['dor_cronica']  = (op == '2')


def bloco_red_flags(dados):
    _bloco('BLOCO 1 — Red Flags')
    print('  Responda s se presente, n se ausente.\n')

    # Red flags sistêmicas — motivo de parar e investigar antes do diagnóstico de joelho
    dados['febre']                           = sn('  Febre ou calafrios associados à dor? ')
    dados['perda_de_peso_inexplicada']        = sn('  Perda de peso inexplicada recentemente? ')
    dados['dor_noturna_sem_alivio']           = sn('  Dor noturna intensa que não melhora com nada? ')
    dados['historico_cancer']                 = sn('  Histórico de câncer? ')
    dados['imunossupressao']                  = sn('  Imunossuprimido (HIV, transplante, quimioterapia)? ')
    # uso_cronico_corticoide não entra em red_flag_sistemica mas pesa futuramente em:
    # risco de fratura por insuficiência, risco infeccioso e cautela em procedimentos
    dados['uso_cronico_corticoide']           = sn('  Uso crônico de corticoide (> 3 meses)? ')

    # Neurológico — triagem MSK global. Não é hipótese de joelho.
    # O engine não deve tratar isso como diagnóstico de joelho — é sinal de alerta de outra camada.
    dados['deficit_neurologico_progressivo']  = sn('  Fraqueza ou perda de sensibilidade no pé ou perna? ')

    # Sinal de trauma importante — categoria própria, não mistura com sistêmicas
    dados['hemartrose_imediata']              = sn('  Joelho inchou em MINUTOS após trauma grave? ')

    # Derivadas para o engine
    dados['trauma_significativo']  = dados['hemartrose_imediata']

    # Classificação separada — usada no resumo e no engine
    dados['red_flag_sistemica'] = any([
        dados['febre'], dados['perda_de_peso_inexplicada'],
        dados['dor_noturna_sem_alivio'], dados['historico_cancer'],
        dados['imunossupressao'], dados['deficit_neurologico_progressivo']
    ])
    dados['sinal_trauma_importante'] = dados['hemartrose_imediata']
    dados['red_flag_presente']       = dados['red_flag_sistemica'] or dados['sinal_trauma_importante']

    if dados['red_flag_sistemica']:
        print('\n  ⚠️  RED FLAG SISTÊMICA. Documente e avalie antes de continuar.')
    if dados['sinal_trauma_importante']:
        print('\n  ⚠️  Hemartrose imediata — suspeitar LCA / fratura intra-articular.')


def bloco_trauma(dados):
    _bloco('BLOCO 2 — Trauma')

    dados['trauma_agudo'] = sn('  Houve trauma agudo recente (queda, torção, impacto)? ')

    if dados['trauma_agudo']:
        print('\n  → Aplicando Regras de Ottawa:\n')
        dados['sensibilidade_isolada_patela'] = sn('  Dor à palpação isolada na patela? ')
        dados['sensibilidade_cabeca_fibula']  = sn('  Dor à palpação na cabeça da fíbula? ')
        dados['incapaz_flexao_90']            = sn('  Incapaz de fletir o joelho a 90°? ')
        dados['incapaz_suportar_peso']        = sn('  Incapaz de dar 4 passos com carga? ')
        dados['trauma_torcao_recente']        = sn('  O mecanismo foi torção do joelho? ')
        dados['derrame_horas_apos_trauma']    = sn('  Joelho inchou horas depois do trauma? ')
    else:
        dados['sensibilidade_isolada_patela'] = False
        dados['sensibilidade_cabeca_fibula']  = False
        dados['incapaz_flexao_90']            = False
        dados['incapaz_suportar_peso']        = False
        dados['trauma_torcao_recente']        = False
        dados['derrame_horas_apos_trauma']    = False

    dados['trauma']                    = dados['trauma_agudo']
    dados['trauma_ou_sobrecarga_recente'] = dados['trauma_agudo']


def bloco_caracteristicas(dados):
    _bloco('BLOCO 3 — Características da Dor')

    dados['inicio_insidioso']    = sn('  A dor começou de forma gradual, sem trauma? ')
    dados['dor_mecanica']        = sn('  A dor piora com atividade física ou carga no joelho? ')
    dados['melhora_com_repouso'] = sn('  A dor melhora com repouso? ')

    # Separados — piora com repouso e melhora com movimento são fenômenos distintos
    dados['piora_com_repouso']        = sn('  A dor piora quando fica parado ou deitado por muito tempo? ')
    dados['melhora_com_atividade_leve']= sn('  A dor melhora ao se movimentar levemente? ')

    dados['dor_localizada']      = sn('  A dor é localizada no joelho (não difusa pelo corpo todo)? ')

    print('\n  Rigidez matinal — quanto tempo dura ao acordar?')
    print('  1) Menos de 30 minutos')
    print('  2) Mais de 60 minutos')
    print('  3) Sem rigidez matinal')
    while True:
        op = input('  Opção (1/2/3): ').strip()
        if op in ('1', '2', '3'):
            break
        print('  Digite 1, 2 ou 3.')

    dados['rigidez_matinal_menos_30min'] = (op == '1')
    dados['rigidez_matinal_acima_60min'] = (op == '2')

    # Derivadas para camada de mecanismo
    dados['piora_com_atividade']          = dados['dor_mecanica']
    dados['piora_com_movimento_ou_carga'] = dados['dor_mecanica']
    dados['inicio_insidioso_com_uso']     = dados['inicio_insidioso'] and dados['dor_mecanica']
    dados['sem_sintomas_neurologicos']    = not dados.get('deficit_neurologico_progressivo', False)
    dados['formigamento_ou_dormencia']    = dados.get('deficit_neurologico_progressivo', False)
    dados['deficit_sensorial_ou_reflexo'] = dados.get('deficit_neurologico_progressivo', False)
    dados['piora_noturna_caracteristica'] = dados.get('dor_noturna_sem_alivio', False)
    dados['dor_generalizada_ou_difusa']   = not dados.get('dor_localizada', True)


def bloco_inflamatorio(dados):
    _bloco('BLOCO 4 — Padrão Inflamatório')
    print('  Foca nos discriminadores principais.\n')

    dados['articulacoes_multiplas_afetadas'] = sn('  Outras articulações doendo junto (além do joelho)? ')
    dados['articulacoes_multiplas']          = dados['articulacoes_multiplas_afetadas']
    dados['calor_ou_eritema_articular']      = sn('  Joelho quente ou vermelho? ')
    dados['sem_calor_ou_eritema']            = not dados['calor_ou_eritema_articular']
    dados['sintomas_sistemicos']             = sn('  Mal-estar geral, fadiga intensa junto com a dor? ')
    dados['envolvimento_simetrico']          = False   # não perguntado — inferido se necessário


def bloco_hotspots(dados):
    _bloco('BLOCO 5 — Localização e Hot Spots')

    dados['dor_anterior_joelho']               = sn('  Dor principalmente na frente do joelho / atrás da patela? ')
    dados['dor_linha_articular']               = sn('  Dor na linha articular (lado interno ou externo)? ')
    dados['massa_fossa_poplitea']              = sn('  Sente um caroço ou pressão atrás do joelho? ')
    dados['relato_derrame']                    = sn('  Joelho parece inchado por dentro, com líquido? ')

    # SDPF — só pergunta se dor anterior
    if dados['dor_anterior_joelho']:
        print()
        dados['sinal_do_cinema']               = sn('  Dor ao levantar depois de muito tempo sentado? ')
        dados['piora_escadas_ou_agachamento']  = sn('  Piora ao subir/descer escadas ou agachar? ')
    else:
        dados['sinal_do_cinema']               = False
        dados['piora_escadas_ou_agachamento']  = False

    # Menisco — só pergunta se dor na linha articular
    if dados['dor_linha_articular']:
        print()
        dados['travamento_ou_estalido']        = sn('  O joelho já travou ou deu estalido? ')
    else:
        dados['travamento_ou_estalido']        = False

    # Bursite pré-patelar e anserina
    dados['inchaço_sobre_patela']              = sn('  Inchaço mole e visível SOBRE a patela (não dentro)? ')
    dados['trabalho_ajoelhado']                = sn('  Trabalha ou trabalhava muito tempo ajoelhado? ')
    dados['dor_medial_abaixo_linha_articular'] = sn('  Dor do lado interno abaixo da linha articular (~5cm)? ')
    dados['dor_cruzar_pernas']                 = sn('  Dói ao cruzar as pernas? ')
    dados['obesidade_ou_oa_associada']         = sn('  Sobrepeso ou diagnóstico prévio de OA? ')

    # Cisto de Baker — só pergunta se massa poplítea
    if dados['massa_fossa_poplitea']:
        print()
        dados['dificuldade_flexao_completa']    = sn('  Dificuldade de dobrar o joelho completamente? ')
        dados['oa_ou_lesao_meniscal_conhecida'] = sn('  Já tem OA ou lesão meniscal diagnosticada? ')
    else:
        dados['dificuldade_flexao_completa']    = False
        dados['oa_ou_lesao_meniscal_conhecida'] = False


# =============================================================================
# SALVAR
# =============================================================================

def salvar_dicionario(dados, pasta='dados_pacientes'):
    os.makedirs(pasta, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome = os.path.join(pasta, f'joelho_subjetivo_{timestamp}.json')
    with open(nome, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f'\n  ✅ Dicionário salvo em: {nome}')
    return nome


# =============================================================================
# MAIN
# =============================================================================

def coletar_subjetivo_joelho():
    print('\n' + '='*50)
    print('  SYMPTOPY — Anamnese: Dor no Joelho  (V3)')
    print('='*50)
    print('  Responda s (sim) ou n (não) para cada pergunta.')

    dados = {}

    bloco_identificacao(dados)
    bloco_red_flags(dados)
    bloco_trauma(dados)
    bloco_caracteristicas(dados)
    bloco_inflamatorio(dados)
    bloco_hotspots(dados)
    completar_chaves_padrao(dados)

    # Resumo
    print('\n' + '='*50)
    print('  RESUMO DA ANAMNESE')
    print('='*50)
    print(f'  Idade: {dados["idade"]} anos | '
          f'Dor: {"nova" if dados["dor_nova"] else "crônica/recorrente"}')

    if dados['red_flag_sistemica']:
        flags = [k for k in ['febre','perda_de_peso_inexplicada','dor_noturna_sem_alivio',
                              'historico_cancer','imunossupressao',
                              'deficit_neurologico_progressivo']
                 if dados.get(k)]
        print(f'  ⚠️  Red flags sistêmicas: {", ".join(flags)}')

    if dados['sinal_trauma_importante']:
        print('  ⚠️  Hemartrose imediata — avaliar LCA / fratura intra-articular')

    positivos = [k for k, v in dados.items()
                 if v is True
                 and k not in ['red_flag_sistemica','sinal_trauma_importante',
                                'red_flag_presente','dor_nova','dor_cronica']
                 and not k.startswith('idade_')]
    print(f'\n  Achados positivos ({len(positivos)}):')
    for p in positivos:
        print(f'    + {p}')

    arquivo = salvar_dicionario(dados)
    print('\n  Próximo: objetivo.py → exame físico → engine.py → diagnóstico\n')
    return dados, arquivo


if __name__ == '__main__':
    coletar_subjetivo_joelho()