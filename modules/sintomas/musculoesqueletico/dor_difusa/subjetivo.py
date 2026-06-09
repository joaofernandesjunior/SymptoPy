# subjetivo.py — Anamnese de Dor Difusa (Fibromialgia)
# Roteiro guiado para o SymptoPy (cálculo de WPI e SSS - ACR 2016)
# Rodar da raiz: python -m modules.sintomas.musculoesqueletico.dor_difusa.subjetivo

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

def perguntar_gravidade(sintoma_nome):
    print(f'\n  Gravidade de {sintoma_nome} na última semana:')
    print('  0) Ausente / sem problema')
    print('  1) Leve ou fraco (geralmente leve ou intermitente)')
    print('  2) Moderado (nível considerável, frequentemente presente)')
    print('  3) Grave (persistente, incomoda muito, interfere na vida diária)')
    while True:
        val = perguntar_int('  Opção (0-3): ')
        if 0 <= val <= 3:
            return val
        print('  Digite um valor entre 0 e 3.')

def completar_chaves_padrao(dados):
    """Inicializa chaves que o motor central espera."""
    defaults = {
        # Exame físico — preenchido em objetivo.py
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
        
        # Joelho / Ombro defaults
        'sensibilidade_isolada_patela':     False,
        'sensibilidade_cabeca_fibula':      False,
        'incapaz_flexao_90':                False,
        'incapaz_suportar_peso':            False,
        'trauma_torcao_recente':            False,
        'derrame_horas_apos_trauma':        False,
        'crepitacao':                       False,
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
    dados['idade_acima_65']  = idade >= 65
    dados['idade_acima_50']  = idade >= 50
    dados['idade_abaixo_40'] = idade < 40

    while True:
        eva = perguntar_int('  Intensidade da dor atual (EVA de 0 a 10): ')
        if 0 <= eva <= 10:
            break
        print('  Digite um valor entre 0 e 10.')
    dados['eva_dor'] = eva

    dados['dor_nova']     = False
    dados['dor_cronica']  = True


def bloco_red_flags(dados):
    _bloco('BLOCO 1 — Red Flags (Dor Difusa)')
    print('  Responda s se presente, n se ausente.\n')

    # Sistêmicos
    dados['febre']                     = sn('  Febre ou calafrios associados? ')
    dados['perda_de_peso_inexplicada']  = sn('  Perda de peso inexplicada recentemente? ')
    dados['dor_noturna_sem_alivio']     = sn('  Dor noturna intensa que impede o sono mesmo sem movimento? ')
    dados['historico_cancer']           = sn('  Histórico pessoal de câncer? ')
    dados['imunossupressao']            = sn('  Imunossuprimido (HIV, transplante, corticoide)? ')
    dados['uso_cronico_corticoide']     = sn('  Uso crônico de corticoide? ')
    dados['osteoporose']                = sn('  Osteoporose estabelecida? ')
    dados['trauma_significativo']       = sn('  Histórico de trauma físico grave recente como gatilho? ')
    
    # Sinais neurológicos distais
    dados['deficit_neurologico_progressivo'] = sn('  Déficit neurológico focal novo e progressivo (perda de força, paralisia)? ')
    dados['anestesia_em_sela']          = False
    dados['retencao_urinaria']          = False
    dados['incontinencia_fecal']        = False
    dados['fraqueza_bilateral_mmii']    = False

    dados['red_flag_sistemica'] = any([
        dados['febre'], dados['perda_de_peso_inexplicada'],
        dados['dor_noturna_sem_alivio'], dados['historico_cancer'],
        dados['imunossupressao'], dados['deficit_neurologico_progressivo']
    ])
    dados['red_flag_presente'] = dados['red_flag_sistemica'] or dados['trauma_significativo']


def bloco_wpi(dados):
    _bloco('BLOCO 2 — W widespread Pain Index (Regiões Dolorosas)')
    print('  Indique quais das 19 regiões abaixo o paciente sentiu dor na última semana.')
    print('  Digite os números separados por vírgula (ex: 1, 2, 7, 17, 19) ou pressione Enter se nenhuma:')
    print('\n  [Membros Superiores]')
    print('  1) Mandíbula Esquerda         2) Mandíbula Direita')
    print('  3) Ombro/Clavícula Esquerdo   4) Ombro/Clavícula Direito')
    print('  5) Braço Esquerdo             6) Braço Direito')
    print('  7) Antebraço Esquerdo         8) Antebraço Direito')
    print('  [Membros Inferiores]')
    print('  9) Quadril/Glúteo Esquerdo   10) Quadril/Glúteo Direito')
    print('  11) Coxa Esquerda            12) Coxa Direito')
    print('  13) Perna Esquerda           14) Perna Direita')
    print('  [Esqueleto Axial / Tronco]')
    print('  15) Pescoço (Cervical)')
    print('  16) Costas Superior (Dorsal)')
    print('  17) Costas Inferior (Lombar)')
    print('  18) Tórax (Peito)')
    print('  19) Abdômen')

    regioes_map = {
        1: 'mandibula_esquerda', 2: 'mandibula_direita',
        3: 'ombro_esquerdo', 4: 'ombro_direito',
        5: 'braco_esquerdo', 6: 'braco_direito',
        7: 'antebraço_esquerdo', 8: 'antebraço_direito',
        9: 'quadril_esquerdo', 10: 'quadril_direito',
        11: 'coxa_esquerda', 12: 'coxa_direita',
        13: 'perna_esquerdo', 14: 'perna_direita',
        15: 'pescoço_cervical', 16: 'costas_superior_dorsal',
        17: 'costas_inferior_lombar', 18: 'torax_peito',
        19: 'abdomen'
    }

    # Inicializar todas as regiões como False
    for r_nome in regioes_map.values():
        dados[f'dor_regiao_{r_nome}'] = False

    while True:
        entrada = input('\n  Regiões dolorosas (números): ').strip()
        if not entrada:
            break
        try:
            numeros = [int(n.strip()) for n in entrada.split(',')]
            if all(1 <= num <= 19 for num in numeros):
                for num in numeros:
                    dados[f'dor_regiao_{regioes_map[num]}'] = True
                break
            else:
                print('  Digite apenas números entre 1 e 19.')
        except ValueError:
            print('  Formato inválido. Use números separados por vírgula (ex: 1, 3, 5).')

    # Calcula WPI total
    wpi_score = sum(1 for r_nome in regioes_map.values() if dados.get(f'dor_regiao_{r_nome}'))
    dados['wpi_score'] = wpi_score
    print(f'  -> WPI calculado: {wpi_score} / 19 regiões')


def bloco_sss(dados):
    _bloco('BLOCO 3 — Symptom Severity Scale (Gravidade dos Sintomas)')

    # Sintomas principais
    dados['fadiga_score'] = perguntar_gravidade('Fadiga')
    dados['sono_nao_restaurador_score'] = perguntar_gravidade('Sono não reparador/restaurador')
    dados['comprometimento_cognitivo_score'] = perguntar_gravidade('Dificuldade cognitiva / memória')

    # Sintomas somáticos acessórios (ACR 2016 simplificado)
    _bloco('Sintomas Somáticos Acessórios')
    print('  Responda se o paciente apresentou esses sintomas nos últimos 6 meses:')
    
    dados['sintoma_cefaleia'] = sn('  Dor de cabeça frequente/crônica? ')
    dados['sintoma_dor_abdominal'] = sn('  Dor ou cólica no abdômen inferior (ex: síndrome do cólon irritável)? ')
    dados['sintoma_depressao'] = sn('  Transtorno depressivo ou sintomas depressivos recorrentes? ')

    somáticos_acessorios = sum([dados['sintoma_cefaleia'], dados['sintoma_dor_abdominal'], dados['sintoma_depressao']])
    dados['somaticos_acessorios_score'] = somáticos_acessorios

    # SSS Score total (Fadiga [0-3] + Sono [0-3] + Cognição [0-3] + Somáticos [0-3])
    sss_score = dados['fadiga_score'] + dados['sono_nao_restaurador_score'] + dados['comprometimento_cognitivo_score'] + somáticos_acessorios
    dados['sss_score'] = sss_score
    print(f'\n  -> SSS calculado: {sss_score} / 12 pontos')

    # Derivados clínicos para o motor nociplástico central
    dados['dor_generalizada_ou_difusa'] = dados['wpi_score'] >= 4
    dados['dor_desproporcional_ao_exame'] = True  # típico na dor difusa/fibro
    dados['fadiga_cronica'] = dados['fadiga_score'] >= 2
    dados['sono_nao_restaurador'] = dados['sono_nao_restaurador_score'] >= 2
    dados['comprometimento_cognitivo_leve'] = dados['comprometimento_cognitivo_score'] >= 1
    dados['multiplos_sindromes_somaticos'] = somáticos_acessorios >= 2
    dados['falha_de_analgesia_convencional'] = sn('\n  Paciente relata falha de resposta a analgésicos comuns (AINEs/dipirona/paracetamol)? ')
    
    # Critério temporal
    dados['duracao_acima_3_meses'] = sn('  Os sintomas descritos duram há pelo menos 3 meses? ')
    dados['duracao_acima_6_semanas'] = dados['duracao_acima_3_meses']


# =============================================================================
# SALVAR
# =============================================================================

def salvar_dicionario(dados, pasta='dados_pacientes'):
    os.makedirs(pasta, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome = os.path.join(pasta, f'dor_difusa_subjetivo_{timestamp}.json')
    with open(nome, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f'\n  ✅ Dicionário salvo em: {nome}')
    return nome


# =============================================================================
# MAIN
# =============================================================================

def coletar_subjetivo_dor_difusa():
    print('\n' + '='*50)
    print('  SYMPTOPY — Anamnese: Dor Difusa / Fibromialgia')
    print('='*50)
    print('  Responda às perguntas sobre dor generalizada e severidade de sintomas.')

    dados = {}

    bloco_identificacao(dados)
    bloco_red_flags(dados)
    bloco_wpi(dados)
    bloco_sss(dados)
    completar_chaves_padrao(dados)

    # Resumo
    print('\n' + '='*50)
    print('  RESUMO DA ANAMNESE DE DOR DIFUSA')
    print('='*50)
    print(f'  Idade: {dados["idade"]} anos | Dor crônica: {"Sim" if dados["dor_cronica"] else "Não"} | EVA: {dados["eva_dor"]}/10')
    print(f'  WPI: {dados["wpi_score"]} | SSS: {dados["sss_score"]}')
    print(f'  Duração >= 3 meses: {"Sim" if dados["duracao_acima_3_meses"] else "Não"}')

    if dados['red_flag_presente']:
        print('  ⚠️  Alerta: Red Flags presentes! Excluir causas secundárias e graves.')

    arquivo = salvar_dicionario(dados)
    print('\n  Próximo: objetivo.py (Exame físico geral/articular) → engine_fibromialgia.py\n')
    return dados, arquivo


if __name__ == '__main__':
    coletar_subjetivo_dor_difusa()
