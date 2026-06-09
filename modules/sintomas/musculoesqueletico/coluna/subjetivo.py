# subjetivo.py — Anamnese de Dor Lombar (Coluna)
# Roteiro guiado para o SymptoPy
# Rodar da raiz: python -m modules.sintomas.musculoesqueletico.coluna.subjetivo

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
    Preenche chaves de outros módulos que o motor central pode esperar
    e assegura que as chaves de exame físico estão inicializadas como False.
    """
    defaults = {
        # Triagem infecciosa sistêmica / fatores de risco
        'uso_drogas_iv':            False,
        'bacteremia_recente':       False,
        
        # Exame físico — preenchidos em objetivo.py
        'dor_palpacao_processos_espinhosos': False,
        'dor_palpacao_paravertebral':        False,
        'lasegue_positivo':                 False,
        'lasegue_contralateral_positivo':   False,
        'giordano_positivo':                False,
        'reflexo_patelar_diminuido':        False,
        'reflexo_aquileu_diminuido':        False,
        'fraqueza_dorsiflexao_pe':          False,
        'fraqueza_plantiflexao_pe':         False,
        'deficit_sensibilidade_mmii':       False,
        'exame_fisico_local_positivo':      False,
        
        # Joelho / Ombro defaults (para compatibilidade)
        'sensibilidade_isolada_patela': False,
        'sensibilidade_cabeca_fibula':  False,
        'incapaz_flexao_90':            False,
        'incapaz_suportar_peso':        False,
        'trauma_torcao_recente':        False,
        'derrame_horas_apos_trauma':    False,
        'crepitacao':                    False,
        
        # Dor Nociplástica defaults
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
    if isinstance(dados.get('idade'), int) and dados['idade'] > 0:
        idade = dados['idade']
        print(f'  Idade: {idade} anos (herdada da identificação do paciente)')
    else:
        idade = perguntar_int('  Idade do paciente: ')
        dados['idade'] = idade
    dados['idade_acima_70']  = idade >= 70
    dados['idade_acima_55']  = idade >= 55
    dados['idade_acima_50']  = idade >= 50
    dados['idade_acima_45']  = idade >= 45
    dados['idade_acima_40']  = idade >= 40
    dados['idade_abaixo_40'] = idade < 40

    while True:
        eva = perguntar_int('  Intensidade da dor (EVA de 0 a 10): ')
        if 0 <= eva <= 10:
            break
        print('  Digite um valor entre 0 e 10.')
    dados['eva_dor'] = eva

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
    _bloco('BLOCO 1 — Red Flags (Coluna)')
    print('  Responda s se presente, n se ausente.\n')

    # Sistêmicos gerais
    dados['febre']                     = sn('  Febre ou calafrios associados? ')
    dados['perda_de_peso_inexplicada']  = sn('  Perda de peso inexplicada recentemente? ')
    dados['dor_noturna_sem_alivio']     = sn('  Dor na cama / deitado que não alivia com nenhuma posição? ')
    dados['historico_cancer']           = sn('  Histórico pessoal de câncer? ')
    dados['imunossupressao']            = sn('  Imunossuprimido (HIV, transplante, corticoide sistêmico)? ')
    dados['uso_cronico_corticoide']     = sn('  Uso crônico de corticoide (> 3 meses)? ')
    dados['osteoporose']                = sn('  Diagnóstico de osteoporose? ')
    
    # Trauma
    dados['trauma_significativo']       = sn('  Houve queda de altura, acidente automobilístico ou trauma lombar direto? ')

    # Cauda Equina (Urgência Absoluta)
    print('\n  --- Sinais Neurológicos Críticos (Cauda Equina) ---')
    dados['anestesia_em_sela']          = sn('  Adormecimento ou dormência na região pubiana, nádegas ou períneo (sela)? ')
    dados['retencao_urinaria']          = sn('  Dificuldade recente para urinar ou retenção urinária súbita? ')
    dados['incontinencia_fecal']        = sn('  Incontinência fecal recente ou perda involuntária de fezes? ')
    dados['fraqueza_bilateral_mmii']    = sn('  Fraqueza importante e progressiva em AMBAS as pernas? ')
    dados['deficit_neurologico_progressivo'] = sn('  Déficit motor progressivo recente (ex: pé caído, perna falhando ao andar)? ')

    # Agregadores de Red Flag
    dados['red_flag_sistemica'] = any([
        dados['febre'], dados['perda_de_peso_inexplicada'],
        dados['dor_noturna_sem_alivio'], dados['historico_cancer'],
        dados['imunossupressao'], dados['deficit_neurologico_progressivo']
    ])
    dados['sinal_cauda_equina'] = any([
        dados['anestesia_em_sela'], dados['retencao_urinaria'],
        dados['incontinencia_fecal'], dados['fraqueza_bilateral_mmii']
    ])
    dados['red_flag_presente'] = dados['red_flag_sistemica'] or dados['sinal_cauda_equina'] or dados['trauma_significativo']

    if dados['sinal_cauda_equina']:
        print('\n  ⚠️  SINAIS DE CAUDA EQUINA IDENTIFICADOS. Encaminhamento imediato para RM e Neurocirurgia!')
    elif dados['red_flag_sistemica']:
        print('\n  ⚠️  RED FLAG SISTÊMICA. Avalie causas secundárias antes do manejo de rotina.')


def bloco_caracteristicas(dados):
    _bloco('BLOCO 2 — Características da Dor')

    dados['inicio_insidioso']    = sn('  A dor começou de forma gradual, sem trauma recente? ')
    dados['dor_mecanica']        = sn('  A dor piora ao carregar peso, inclinar-se ou com movimento físico? ')
    dados['melhora_com_repouso'] = sn('  A dor melhora quando deita ou repousa? ')
    
    dados['piora_com_repouso']         = sn('  A dor piora se ficar parado na mesma posição ou deitado por muito tempo? ')
    dados['melhora_com_atividade_leve'] = sn('  A dor melhora após caminhar ou fazer exercícios leves? ')
    
    dados['dor_localizada']      = sn('  A dor é localizada somente nas costas (não espalhada pelo corpo)? ')

    print('\n  Rigidez matinal lombar — quanto tempo dura ao acordar?')
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

    # Derivadas para mecanismo
    dados['piora_com_atividade']          = dados['dor_mecanica']
    dados['piora_com_movimento_ou_carga'] = dados['dor_mecanica']
    dados['inicio_insidioso_com_uso']     = dados['inicio_insidioso'] and dados['dor_mecanica']
    dados['sem_sintomas_neurologicos']    = not (dados['deficit_neurologico_progressivo'] or dados['anestesia_em_sela'])
    dados['dor_generalizada_ou_difusa']   = not dados['dor_localizada']


def bloco_radicular_claudicacao(dados):
    _bloco('BLOCO 3 — Sintomas Radiculares e Canal')

    dados['dor_irradiada_mmii']        = sn('  A dor desce/irradia para as pernas (abaixo do joelho)? ')
    dados['formigamento_ou_dormencia']  = sn('  Tem formigamento ou dormência nas pernas ou pés? ')
    
    if dados['dor_irradiada_mmii'] or dados['formigamento_ou_dormencia']:
        dados['distribuicao_dermatomal'] = sn('  A dor ou dormência segue uma linha específica pela perna até o pé? ')
        dados['queimacao_ou_choque_eletrico'] = sn('  A dor parece uma queimação ou choque elétrico na perna? ')
    else:
        dados['distribuicao_dermatomal'] = False
        dados['queimacao_ou_choque_eletrico'] = False

    # Estenose de canal / claudicação neurogênica
    print('\n  --- Claudicação Neurogênica ---')
    dados['claudicacao_neurogenica']   = sn('  Sente dor ou peso nas pernas ao caminhar que obriga a parar, sentar ou inclinar-se para frente? ')
    
    # Preferência direcional
    print('\n  --- Preferência Direcional (Alívio Domiciliar) ---')
    dados['preferencia_direcional_extensao'] = sn('  A dor lombar MELHORA quando você joga o tronco para trás (extensão)? ')
    dados['preferencia_direcional_flexao']   = sn('  A dor lombar MELHORA quando você se curva para frente (ex: apoiando em carrinho de compras)? ')


# =============================================================================
# SALVAR
# =============================================================================

def salvar_dicionario(dados, pasta='dados_pacientes'):
    os.makedirs(pasta, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome = os.path.join(pasta, f'coluna_subjetivo_{timestamp}.json')
    with open(nome, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f'\n  ✅ Dicionário salvo em: {nome}')
    return nome


# =============================================================================
# MAIN
# =============================================================================

def coletar_subjetivo_coluna(dados_preenchidos=None):
    print('\n' + '='*50)
    print('  SYMPTOPY — Anamnese: Dor Lombar (Coluna)')
    print('='*50)
    print('  Responda s (sim) ou n (não) para cada pergunta.')

    dados = dados_preenchidos.copy() if dados_preenchidos else {}

    bloco_identificacao(dados)
    bloco_red_flags(dados)
    bloco_caracteristicas(dados)
    bloco_radicular_claudicacao(dados)
    completar_chaves_padrao(dados)

    # Resumo rápido
    print('\n' + '='*50)
    print('  RESUMO DA ANAMNESE LOMBAR')
    print('='*50)
    print(f'  Idade: {dados["idade"]} anos | '
          f'Dor: {"nova" if dados["dor_nova"] else "crônica/recorrente"}')

    if dados['sinal_cauda_equina']:
        print('  ⛔ ⚠️ ALERTA CRÍTICO: Cauda Equina identificada!')
    elif dados['red_flag_sistemica']:
        print('  ⚠️ Red Flags sistêmicas ativas!')

    arquivo = salvar_dicionario(dados)
    print('\n  Próximo: objetivo.py (Exame físico da coluna) → engine.py\n')
    return dados, arquivo


if __name__ == '__main__':
    coletar_subjetivo_coluna()
