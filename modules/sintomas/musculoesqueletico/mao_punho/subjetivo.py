# modules/sintomas/musculoesqueletico/mao_punho/subjetivo.py
# Anamnese — Dor na Mão, Punho e Dedos
# Roteadores: trauma | neurológico | mecânico-tendíneo | reumatológico
# Rodar da raiz: python -m modules.sintomas.musculoesqueletico.mao_punho.subjetivo

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

    dados['eva_dor'] = perguntar_int('  Intensidade da dor (EVA 0-10): ', 0, 10)

    print('\n  Essa dor é nova ou crônica?')
    print('  1) Nova / aguda (início recente)')
    print('  2) Crônica / recorrente (>= 3 meses)')
    while True:
        op = input('  Opção (1/2): ').strip()
        if op in ('1', '2'):
            break
        print('  Digite 1 ou 2.')
    dados['dor_nova']    = (op == '1')
    dados['dor_cronica'] = (op == '2')


def _bloco_roteador_padrao(dados):
    _bloco('BLOCO 1 — Padrão Clínico (Roteador)')
    print('  Selecione o padrão predominante (orienta os próximos blocos):\n')
    print('  1) TRAUMA — queda com mão espalmada, entorse, impacto direto')
    print('     -> Suspeita de fratura do escafoide ou ligamento')
    print('  2) NEUROLÓGICO — dormência, formigamento, queimação nos dedos')
    print('     -> Síndrome do túnel do carpo ou neuropatia ulnar')
    print('  3) MECÂNICO / TENDÍNEO — dor localizada, estalido, piora com movimento')
    print('     -> De Quervain, dedo em gatilho, rizartrose do polegar')
    print('  4) REUMATOLÓGICO — rigidez matinal, múltiplas articulações, dor simétrica')
    print('     -> Artrite reumatoide, OA generalizada')
    while True:
        op = input('\n  Padrão predominante (1/2/3/4): ').strip()
        if op in ('1', '2', '3', '4'):
            break
        print('  Digite 1, 2, 3 ou 4.')
    dados['padrao_clinico'] = {
        '1': 'trauma',
        '2': 'neurologico',
        '3': 'mecanico',
        '4': 'reumatologico',
    }[op]


def _bloco_trauma(dados):
    _bloco('BLOCO 2A — Trauma (Escafoide / Ligamento)')
    print('  Fratura do escafoide é a fratura mais comum do carpo.')
    print('  XR inicial normal nao exclui fratura (falso-negativo: 30%).\n')
    dados['mecanismo_queda_mao_espalmada'] = sn('  Queda com apoio na mão estendida (FOOSH)? ')
    dados['dor_tabaqueira_anatomica']      = sn('  Dor na tabaqueira anatômica (dorso radial do punho)? ')
    dados['dor_ao_punh_compressao']        = sn('  Dor ao comprimir axialmente o polegar em direção ao punho? ')
    dados['edema_punho_pos_trauma']        = sn('  Edema do punho após o trauma? ')
    dados['limitacao_movimento_trauma']    = sn('  Limitação de movimento do punho após trauma? ')

    if dados['dor_tabaqueira_anatomica']:
        print('\n  ALERTA: Tabaqueira positiva + trauma = suspeita de fratura do escafoide.')
        print('  Imobilizar mesmo com XR normal. Repetir XR em 10-14 dias ou solicitar RM.')


def _bloco_neurologico(dados):
    _bloco('BLOCO 2B — Neurológico (Túnel do Carpo / Neuropatia Ulnar)')
    print('  Mapeie a distribuição da parestesia — define o nervo afetado.\n')

    print('  Território MEDIANO (nervo mediano = STC):')
    print('  Polegar, indicador, médio e metade radial do anular.')
    dados['parestesia_territorio_mediano'] = sn('  Dormência/formigamento nesse território? ')

    print('\n  Território ULNAR (neuropatia ulnar):')
    print('  4o e 5o dedos (anular ulnar e mínimo).')
    dados['parestesia_territorio_ulnar']   = sn('  Dormência/formigamento no 4o e 5o dedos? ')

    _bloco('Caracterização dos Sintomas Neurológicos')
    dados['parestesia_noturna']            = sn('  Dormência noturna que acorda o paciente? ')
    dados['alivio_sacudir_mao']            = sn('  Melhora ao sacudir/agitar a mão (flick sign)? ')
    dados['piora_trabalho_computador']     = sn('  Piora com uso de teclado, mouse ou trabalho manual repetitivo? ')
    dados['fraqueza_pinca_oponencia']      = sn('  Fraqueza ao pinçar ou fazer oponência do polegar? ')
    dados['atrofia_tenar_percebida']       = sn('  Percebe diminuição do volume da região tenar (base do polegar)? ')

    if dados['atrofia_tenar_percebida'] or dados['fraqueza_pinca_oponencia']:
        print('\n  ALERTA: Atrofia tenar ou fraqueza = STC moderado/grave.')
        print('  Encaminhamento URGENTE para cirurgia de mão.')

    # Fatores de risco
    print('\n  --- Fatores de Risco ---')
    dados['diabetes_mellitus']   = sn('  Diabetes mellitus? ')
    dados['obesidade']           = sn('  Obesidade? ')
    dados['gestante_ou_puerpera']= sn('  Gestante ou puérpera? ')
    dados['uso_vibracoes']       = sn('  Uso profissional de ferramentas vibratórias? ')


def _bloco_mecanico(dados):
    _bloco('BLOCO 2C — Mecânico / Tendíneo')
    print('  Identifique a estrutura afetada pelo padrão de dor.\n')

    print('  --- De Quervain (1o compartimento extensor — radial do punho) ---')
    dados['dor_radial_punho']              = sn('  Dor no punho dorsorradial (lado do polegar)? ')
    dados['piora_movimento_polegar']       = sn('  Piora ao mover o polegar (pinçar, segurar)? ')
    dados['uso_smartphone_intenso']        = sn('  Uso intenso de smartphone ou tablet (>4h/dia)? ')
    dados['trabalho_manual_repetitivo']    = sn('  Trabalho manual repetitivo (costura, montagem)? ')
    dados['gestante_pos_parto']            = sn('  Gestante ou pós-parto recente (até 6 meses)? ')

    print('\n  --- Dedo em Gatilho (polia A1) ---')
    dados['estalido_bloqueio_dedo']        = sn('  Estalido ou travamento ao fletir/estender algum dedo? ')
    dados['nodulo_palpavel_palma']         = sn('  Percebe nódulo doloroso na palma da mão (na base do dedo)? ')

    if dados['diabetes_mellitus'] if 'diabetes_mellitus' in dados else False:
        print('  INFO: Diabéticos têm até 20% de prevalência de dedo em gatilho.')
    elif dados['estalido_bloqueio_dedo']:
        dados['diabetes_mellitus'] = sn('  Paciente tem diabetes mellitus? ')

    print('\n  --- Rizartrose do Polegar (CMC) ---')
    dados['dor_base_polegar_cmC']          = sn('  Dor na base do polegar (articulação carpometacarpal)? ')
    dados['piora_pincar_girar']            = sn('  Piora ao pinçar, girar (abrir tampa, girar chave)? ')
    dados['proeminencia_dorsal_polegar']   = sn('  Abaulamento/deformidade na base do polegar? ')
    dados['pos_menopausa_feminino']        = sn('  Paciente feminina pós-menopausa? ')


def _bloco_reumatologico(dados):
    _bloco('BLOCO 2D — Reumatológico')
    print('  Distingue artrite inflamatória (AR) de OA generalizada.\n')

    dados['rigidez_matinal_prolongada']    = sn('  Rigidez matinal > 30 minutos? ')
    dados['acometimento_simetrico']        = sn('  Dor ou edema simétrico (ambas as mãos)? ')
    dados['mcf_punho_afetados']            = sn('  Articulações MCF (base dos dedos) ou punhos afetados? ')
    dados['ifd_preservadas']              = sn('  Articulações IFD (ponta dos dedos) POUPADAS? ')
    dados['sintomas_sistemicos']           = sn('  Fadiga, febre baixa ou mal-estar geral? ')
    dados['historico_artrite']             = sn('  Histórico pessoal ou familiar de artrite reumatoide? ')

    print('\n  --- Nódulos e Deformidades ---')
    dados['nodulos_heberden']              = sn('  Nódulos de Heberden (IFD — ponta dos dedos)? ')
    dados['nodulos_bouchard']              = sn('  Nódulos de Bouchard (IFP — meio dos dedos)? ')

    if dados['rigidez_matinal_prolongada'] and dados['acometimento_simetrico'] and dados['ifd_preservadas']:
        print('\n  ALERTA: Padrão sugestivo de AR — encaminhar para Reumatologia.')
    elif dados['nodulos_heberden'] or dados['nodulos_bouchard']:
        print('\n  INFO: Nódulos de Heberden/Bouchard sugerem OA (nao AR).')


# =============================================================================
# SALVAR
# =============================================================================

def salvar_dicionario(dados, pasta='dados_pacientes'):
    os.makedirs(pasta, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome = os.path.join(pasta, f'mao_punho_subjetivo_{timestamp}.json')
    with open(nome, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f'\n  Dicionário salvo em: {nome}')
    return nome


# =============================================================================
# MAIN
# =============================================================================

def coletar_subjetivo_mao_punho(dados_preenchidos=None):
    print('\n' + '='*54)
    print('  SYMPTOPY — Anamnese: Mão, Punho e Dedos')
    print('='*54)
    print('  Responda s (sim) ou n (não) para cada pergunta.')

    dados = dados_preenchidos.copy() if dados_preenchidos else {}

    _bloco_identificacao(dados)
    _bloco_roteador_padrao(dados)

    padrao = dados.get('padrao_clinico', '')
    if padrao == 'trauma':
        _bloco_trauma(dados)
    elif padrao == 'neurologico':
        _bloco_neurologico(dados)
    elif padrao == 'mecanico':
        _bloco_mecanico(dados)
    elif padrao == 'reumatologico':
        _bloco_reumatologico(dados)

    arquivo = salvar_dicionario(dados)
    print('\n  Próximo: objetivo.py (Exame físico da mão/punho)\n')
    return dados, arquivo


if __name__ == '__main__':
    import sys as _sys
    _sys.stdout.reconfigure(encoding='utf-8')
    coletar_subjetivo_mao_punho()
