# modules/sintomas/musculoesqueletico/quadril/subjetivo.py
# Anamnese de Dor no Quadril
# Rodar da raiz: python -m modules.sintomas.musculoesqueletico.quadril.subjetivo

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
    print(f'\n{"─"*54}')
    print(f'  {titulo}')
    print(f'{"─"*54}')


def perguntar_int(prompt, minimo=0, maximo=100):
    while True:
        try:
            val = int(input(prompt).strip())
            if minimo <= val <= maximo:
                return val
            print(f'  Digite um valor entre {minimo} e {maximo}.')
        except ValueError:
            print('  Digite um número inteiro.')


# =============================================================================
# BLOCOS
# =============================================================================

def _bloco_identificacao(dados):
    _bloco('IDENTIFICAÇÃO')
    if isinstance(dados.get('idade'), int) and dados['idade'] > 0:
        print(f'  Idade: {dados["idade"]} anos (herdada da identificação do paciente)')
    else:
        dados['idade'] = perguntar_int('  Idade do paciente: ', 0, 120)

    dados['eva_dor'] = perguntar_int('  Intensidade da dor (EVA 0–10): ', 0, 10)

    print('\n  Essa dor é nova ou recorrente/crônica?')
    print('  1) Nova (início recente)')
    print('  2) Recorrente / crônica')
    while True:
        op = input('  Opção (1/2): ').strip()
        if op in ('1', '2'):
            break
        print('  Digite 1 ou 2.')
    dados['dor_nova']    = (op == '1')
    dados['dor_cronica'] = (op == '2')


def _bloco_localizacao(dados):
    _bloco('BLOCO 1 — Localização da Dor (Roteador Clínico)')
    print('  A localização orienta diretamente a hipótese principal.\n')
    print('  1) Anterior / virilha (inguinal / groin)')
    print('     → Suspeita intra-articular: OA, FAI, labro, AVN')
    print('  2) Lateral (face externa do quadril / grande trocânter)')
    print('     → Síndrome Dolorosa do Grande Trocânter (GTPS / bursite)')
    print('  3) Posterior (nádega / isquio / glúteo)')
    print('     → Dor referida: coluna lombar, SIJ, glútea profunda')
    while True:
        op = input('\n  Localização (1/2/3): ').strip()
        if op in ('1', '2', '3'):
            break
        print('  Digite 1, 2 ou 3.')
    dados['localizacao_dor'] = {'1': 'anterior', '2': 'lateral', '3': 'posterior'}[op]


def _bloco_red_flags(dados):
    _bloco('BLOCO 2 — Red Flags (Urgência / Emergência)')
    print('  Responda s se presente, n se ausente.\n')

    dados['nao_suporta_peso']            = sn('  Não consegue apoiar o pé no chão / andar? ')
    dados['encurtamento_rotacao_externa'] = sn('  Membro visivelmente encurtado e rodado para fora? ')
    dados['febre_sistemica']             = sn('  Febre ou calafrios associados? ')
    dados['trauma_recente']              = sn('  Trauma recente (queda, acidente)? ')
    dados['historico_cancer']            = sn('  Histórico pessoal de câncer? ')
    dados['perda_peso_inexplicada']       = sn('  Perda de peso inexplicada? ')
    dados['dor_noturna_intensa']         = sn('  Dor intensa em repouso / noturna sem alívio postural? ')

    dados['red_flag_presente'] = any([
        dados['nao_suporta_peso'],
        dados['encurtamento_rotacao_externa'],
        dados['febre_sistemica'],
        dados['historico_cancer'] and dados['dor_noturna_intensa'],
    ])

    if dados['encurtamento_rotacao_externa']:
        print('\n  ALERTA: Fratura de colo femoral — encaminhar PS imediatamente.')
    elif dados['nao_suporta_peso'] and dados['trauma_recente']:
        print('\n  ALERTA: Suspeita de fratura — avaliar RX urgente.')
    elif dados['febre_sistemica']:
        print('\n  ALERTA: Artrite séptica a descartar — PS urgente.')


def _bloco_contexto(dados):
    _bloco('BLOCO 3 — Contexto e Características')

    dados['inicio_gradual']          = sn('  A dor começou de forma gradual (sem evento agudo)? ')
    dados['piora_caminhar_escadas']  = sn('  Piora ao caminhar, subir escadas ou agachar? ')
    dados['dor_sentado_prolongado']  = sn('  Dor ao ficar sentado por períodos prolongados? ')
    dados['dor_decubito_lateral']    = sn('  Piora ao deitar sobre o quadril afetado? ')
    dados['dor_flexao_quadril']      = sn('  Dor ao fletir o quadril (ex: amarrar o sapato)? ')
    dados['atleta_jovem_ativo']      = sn('  Paciente atleta ou pratica atividade física intensa? ')
    dados['sintomas_lombares_assoc'] = sn('  Dor ou irradiação lombar associada? ')

    print('\n  --- Fatores de Risco Específicos ---')
    dados['uso_corticoide_cronico'] = sn('  Uso crônico de corticoide (> 3 meses)? ')
    dados['uso_alcool_cronico']     = sn('  Uso crônico de álcool? ')
    dados['osteoporose']            = sn('  Diagnóstico de osteoporose? ')

    # Derivadas de idade
    idade = dados.get('idade', 0)
    dados['idade_acima_50'] = idade >= 50
    dados['idade_acima_40'] = idade >= 40
    dados['idade_abaixo_40'] = idade < 40


# =============================================================================
# SALVAR
# =============================================================================

def salvar_dicionario(dados, pasta='dados_pacientes'):
    os.makedirs(pasta, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome = os.path.join(pasta, f'quadril_subjetivo_{timestamp}.json')
    with open(nome, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f'\n  Dicionário salvo em: {nome}')
    return nome


# =============================================================================
# MAIN
# =============================================================================

def coletar_subjetivo_quadril(dados_preenchidos=None):
    print('\n' + '='*54)
    print('  SYMPTOPY — Anamnese: Dor no Quadril')
    print('='*54)
    print('  Responda s (sim) ou n (não) para cada pergunta.')

    dados = dados_preenchidos.copy() if dados_preenchidos else {}

    _bloco_identificacao(dados)
    _bloco_localizacao(dados)
    _bloco_red_flags(dados)
    _bloco_contexto(dados)

    arquivo = salvar_dicionario(dados)
    print('\n  Próximo: objetivo.py (Exame físico do quadril)\n')
    return dados, arquivo


if __name__ == '__main__':
    coletar_subjetivo_quadril()
