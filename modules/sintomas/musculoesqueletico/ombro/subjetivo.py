# subjetivo_ombro.py — Anamnese de dor no ombro
# V1 — baseado em Pocket Guide to MSK Diagnosis (Cooper) + Open Evidence 2026
# Coleta perguntas em blocos, monta dicionário e salva JSON
# Rodar da raiz: python3 -m modules.sintomas.musculoesqueletico.ombro.subjetivo

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
    Chaves que o engine MSK espera mas não pertencem à anamnese de ombro.
    Cauda equina, neurológico distal de MMII — triagem MSK global, não ombro.
    Exame físico — preenchido em objetivo.py
    Mecanismo de dor fino — preenchido via camada compartilhada
    """
    defaults = {
        # Cauda equina — não é ombro
        'anestesia_em_sela':        False,
        'retencao_urinaria':        False,
        'incontinencia_fecal':      False,
        'fraqueza_bilateral_mmii':  False,
        # Epidemiologia não perguntada aqui
        'uso_drogas_iv':            False,
        'bacteremia_recente':       False,
        'osteoporose':              False,
        # Exame físico — preenchidos em objetivo.py
        'exame_fisico_local_positivo':      False,
        'arco_doloroso_positivo':           False,
        'empty_can_positivo':               False,
        'drop_arm_positivo':                False,
        'neer_positivo':                    False,
        'hawkins_kennedy_positivo':         False,
        'speed_positivo':                   False,
        'yergason_positivo':                False,
        'obrien_positivo':                  False,
        'apprehension_positivo':            False,
        'cross_arm_positivo':               False,
        'gerber_liftoff_positivo':          False,
        'external_rotation_lag_positivo':   False,
        'rom_ativo_limitado':               False,
        'rom_passivo_limitado':             False,
        'atrofia_muscular':                 False,
        'fraqueza_abducao':                 False,
        'fraqueza_rotacao_externa':         False,
        'calor_local':                      False,
        'deformidade_ac':                   False,
        # Mecanismo fino — derivado pelo engine
        'queimacao_ou_choque_eletrico':     False,
        'distribuicao_dermatomal':          False,
        'alodinia':                         False,
        'dor_desproporcional_ao_exame':     False,
        'fadiga_cronica':                   False,
        'sono_nao_restaurador':             False,
        'comprometimento_cognitivo_leve':   False,
        'multiplos_sindromes_somaticos':    False,
        'falha_de_analgesia_convencional':  False,
        'csi_acima_40':                     False,
        'dn4_acima_4':                      False,
        'paindetect_acima_19':              False,
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
    dados['idade_acima_60']  = idade >= 60
    dados['idade_acima_50']  = idade >= 50
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
    dados['dor_nova']    = (op == '1')
    dados['dor_cronica'] = (op == '2')

    print('\n  Lado acometido?')
    print('  1) Direito')
    print('  2) Esquerdo')
    print('  3) Bilateral')
    while True:
        lado = input('  Opção (1/2/3): ').strip()
        if lado in ('1', '2', '3'):
            break
        print('  Digite 1, 2 ou 3.')
    dados['lado_direito']   = (lado == '1')
    dados['lado_esquerdo']  = (lado == '2')
    dados['lado_bilateral'] = (lado == '3')


def bloco_red_flags(dados):
    _bloco('BLOCO 1 — Red Flags')
    print('  Responda s se presente, n se ausente.\n')

    # Red flags sistêmicas
    dados['febre']                          = sn('  Febre ou calafrios associados à dor? ')
    dados['perda_de_peso_inexplicada']       = sn('  Perda de peso inexplicada recentemente? ')
    dados['dor_noturna_sem_alivio']          = sn('  Dor noturna intensa que não melhora com nada? ')
    dados['historico_cancer']                = sn('  Histórico de câncer? ')
    dados['imunossupressao']                 = sn('  Imunossuprimido (HIV, transplante, quimioterapia)? ')
    dados['uso_cronico_corticoide']          = sn('  Uso crônico de corticoide (> 3 meses)? ')

    # Red flag cardiovascular — dor referida cardíaca
    dados['dor_toracica_associada']          = sn('  Dor no peito ou falta de ar junto com a dor no ombro? ')

    # Neurológico proximal — fraqueza de MMSS
    dados['deficit_neurologico_progressivo'] = sn('  Fraqueza progressiva ou perda de sensibilidade no braço/mão? ')

    # Trauma importante
    dados['trauma_significativo']            = sn('  Houve trauma direto no ombro (queda, impacto, luxação)? ')

    # Classificação
    dados['red_flag_sistemica'] = any([
        dados['febre'], dados['perda_de_peso_inexplicada'],
        dados['dor_noturna_sem_alivio'], dados['historico_cancer'],
        dados['imunossupressao'], dados['deficit_neurologico_progressivo']
    ])
    dados['red_flag_cardiovascular']  = dados['dor_toracica_associada']
    dados['sinal_trauma_importante']  = dados['trauma_significativo']
    # trauma segue trilha própria no engine (Rx, neurovascular)
    # não bloqueia o fluxo da mesma forma que febre ou câncer
    dados['red_flag_presente'] = dados['red_flag_sistemica'] or dados['red_flag_cardiovascular']
    dados['dor_nova_flag']            = True
    dados['idade_acima_55']           = dados['idade'] >= 55

    if dados['red_flag_sistemica']:
        print('\n  ⚠️  RED FLAG SISTÊMICA. Documente e avalie antes de continuar.')
    if dados['red_flag_cardiovascular']:
        print('\n  ⚠️  Suspeita de dor referida cardíaca. Avaliar com ECG e troponina se indicado.')
    if dados['sinal_trauma_importante']:
        print('\n  ⚠️  Trauma significativo — suspeitar de fratura ou luxação. Solicitar Rx.')


def bloco_caracteristicas(dados):
    _bloco('BLOCO 2 — Características da Dor')

    # Pocket Guide: Pergunta 1 — localização
    print('\n  Onde está a dor? (escolha a principal)')
    print('  1) Sob o acrômio / lateral do ombro  → rotator cuff / impingement')
    print('  2) Sulco bicipital / anterior         → bíceps')
    print('  3) Articulação AC / superior          → AC joint')
    print('  4) Posterior do ombro                 → SLAP / instabilidade')
    print('  5) Difusa / todo o ombro              → capsulite / OA glenoumeral')
    while True:
        loc = input('  Opção (1-5): ').strip()
        if loc in ('1', '2', '3', '4', '5'):
            break
        print('  Digite um número de 1 a 5.')

    dados['dor_subacromia_lateral']  = (loc == '1')
    dados['dor_anterior_bicipital']  = (loc == '2')
    dados['dor_superior_ac']         = (loc == '3')
    dados['dor_posterior']           = (loc == '4')
    dados['dor_difusa_ombro']        = (loc == '5')

    # Pocket Guide: Pergunta 2 — movimento que piora
    dados['piora_overhead']          = sn('\n  A dor piora com movimentos acima da cabeça? ')
    dados['piora_deceleracao']       = sn('  Piora ao desacelerar o braço (arremessar, nadar)? ')
    dados['piora_rotacao_externa']   = sn('  Piora ao girar o braço para fora? ')
    dados['piora_adducao_cruzada']   = sn('  Piora ao cruzar o braço na frente do peito? ')

    # Pocket Guide: Pergunta 3 — instabilidade
    dados['sensacao_dando_tranco']   = sn('\n  O ombro já "saiu do lugar" ou deu a sensação de ceder? ')

    # Pocket Guide: Pergunta 4 — capsulite
    dados['dor_virou_rigidez']       = sn('  Antes havia mais dor, mas agora predomina rigidez/travamento? ')

    # Padrão temporal
    dados['inicio_insidioso']        = sn('\n  A dor começou gradualmente, sem evento específico? ')
    dados['dor_mecanica']            = sn('  A dor piora com atividade física ou carga no ombro? ')
    dados['melhora_com_repouso']     = sn('  A dor melhora claramente com repouso? ')
    dados['piora_com_repouso']       = sn('  A dor piora quando fica parado ou deitado por muito tempo? ')
    dados['dor_noturna']             = sn('  Dor noturna — acorda à noite ou piora ao deitar sobre o ombro? ')
    dados['dor_localizada']          = not dados['dor_difusa_ombro']

    # Rigidez matinal
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
    dados['piora_noturna_caracteristica'] = dados.get('dor_noturna', False)
    dados['dor_generalizada_ou_difusa']   = dados['dor_difusa_ombro']


def bloco_contexto_clinico(dados):
    _bloco('BLOCO 3 — Contexto Clínico')

    # Fatores de risco por diagnóstico
    dados['atividade_overhead_repetitiva'] = sn('  Trabalho ou esporte com movimentos repetitivos acima da cabeça? ')
    dados['atleta_arremessador']           = sn('  Atleta de arremesso, natação ou tênis? ')
    dados['diabetes']                      = sn('  Tem diabetes? ')
    dados['hipotireoidismo']               = sn('  Tem hipotireoidismo? ')
    dados['cirurgia_ou_imobilizacao_previa']= sn('  Cirurgia ou imobilização prolongada do ombro prévia? ')
    dados['trauma_ac_previo']              = sn('  Já teve separação ou trauma da articulação AC (clavícula)? ')

    # Padrão inflamatório / sistêmico
    dados['articulacoes_multiplas_afetadas'] = sn('  Outras articulações doendo junto? ')
    dados['articulacoes_multiplas']          = dados['articulacoes_multiplas_afetadas']
    dados['calor_ou_eritema_articular']      = sn('  Ombro quente ou vermelho? ')
    dados['sem_calor_ou_eritema']            = not dados['calor_ou_eritema_articular']
    dados['sintomas_sistemicos']             = sn('  Mal-estar geral ou fadiga intensa além da dor? ')
    # piora_com_repouso já perguntada no bloco_caracteristicas
    dados['melhora_com_atividade_leve']      = sn('  A dor melhora ao movimentar levemente? ')
    dados['envolvimento_simetrico']          = False  # raramente perguntado em ombro


def bloco_funcional(dados):
    _bloco('BLOCO 4 — Impacto Funcional')
    print('  Perguntas rápidas sobre limitação.\n')

    dados['incapaz_levantar_braco_altura_ombro'] = sn('  Incapaz de levantar o braço até a altura do ombro? ')
    dados['dificuldade_alcance_posterior']        = sn('  Dificuldade de alcançar as costas (ex: prender sutiã, coçar)? ')
    dados['dificuldade_alcance_lateral']          = sn('  Dificuldade de alcançar objeto lateral ou acima da cabeça? ')
    dados['fraqueza_subjetiva']                   = sn('  Sente fraqueza ao levantar ou segurar objetos com o braço? ')

    # Pocket Guide Pergunta 5 — duração e tentativas de tratamento
    dados['tratamento_previo']                    = sn('\n  Já fez algum tratamento para esse ombro (fisio, injeção, cirurgia)? ')
    dados['duracao_acima_6_semanas']              = sn('  A dor dura há mais de 6 semanas? ')
    dados['duracao_acima_3_meses']                = sn('  A dor dura há mais de 3 meses? ')


# =============================================================================
# SALVAR
# =============================================================================

def salvar_dicionario(dados, pasta='dados_pacientes'):
    os.makedirs(pasta, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome = os.path.join(pasta, f'ombro_subjetivo_{timestamp}.json')
    with open(nome, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f'\n  ✅ Dicionário salvo em: {nome}')
    return nome


# =============================================================================
# MAIN
# =============================================================================

def coletar_subjetivo_ombro():
    print('\n' + '='*50)
    print('  SYMPTOPY — Anamnese: Dor no Ombro  (V1)')
    print('='*50)
    print('  Responda s (sim) ou n (não) para cada pergunta.')

    dados = {}

    bloco_identificacao(dados)
    bloco_red_flags(dados)
    bloco_caracteristicas(dados)
    bloco_contexto_clinico(dados)
    bloco_funcional(dados)
    completar_chaves_padrao(dados)

    # Resumo
    print('\n' + '='*50)
    print('  RESUMO DA ANAMNESE')
    print('='*50)
    lado = 'direito' if dados['lado_direito'] else 'esquerdo' if dados['lado_esquerdo'] else 'bilateral'
    print(f'  Paciente: {dados["idade"]} anos | Ombro: {lado} | Dor: {"nova" if dados["dor_nova"] else "crônica"}')

    if dados['red_flag_sistemica']:
        flags = [k for k in ['febre', 'perda_de_peso_inexplicada', 'dor_noturna_sem_alivio',
                              'historico_cancer', 'imunossupressao', 'deficit_neurologico_progressivo']
                 if dados.get(k)]
        print(f'  ⚠️  Red flags sistêmicas: {", ".join(flags)}')
    if dados['red_flag_cardiovascular']:
        print('  ⚠️  Dor torácica associada — avaliar origem cardíaca')
    if dados['sinal_trauma_importante']:
        print('  ⚠️  Trauma significativo — avaliar fratura ou luxação')

    positivos = [k for k, v in dados.items()
                 if v is True
                 and k not in ['red_flag_sistemica', 'red_flag_cardiovascular',
                                'sinal_trauma_importante', 'red_flag_presente',
                                'dor_nova', 'dor_cronica', 'dor_nova_flag']
                 and not k.startswith('idade_') and not k.startswith('lado_')]
    print(f'\n  Achados positivos ({len(positivos)}):')
    for p in positivos:
        print(f'    + {p}')

    arquivo = salvar_dicionario(dados)
    print('\n  Próximo: objetivo_ombro.py → exame físico → engine → diagnóstico\n')
    return dados, arquivo


if __name__ == '__main__':
    coletar_subjetivo_ombro()