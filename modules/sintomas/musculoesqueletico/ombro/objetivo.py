# objetivo_ombro.py — Exame físico dirigido: Dor no Ombro
# V1 — baseado em Pocket Guide to MSK Diagnosis (Cooper) + Open Evidence 2026
# Carrega JSON do subjetivo, adiciona achados e salva versão completa
# Rodar da raiz: python3 -m modules.sintomas.musculoesqueletico.ombro.objetivo
#
# Testes com evidência (Open Evidence 2026):
# Painful arc:           sens 71%, esp 81%, LR+ 3.7
# Hawkins-Kennedy:       sens 76%, esp 48%, LR+ 1.5
# Neer:                  sens 64-68%, esp 30-61%
# Empty can (Jobe):      sens 71%, esp 49%
# Drop arm:              sens 24%, esp 93%, LR+ 3.3  ← alta esp para ruptura total
# External rotation lag: sens 47%, esp 94%, LR+ 7.2  ← melhor para ruptura
# Cross-arm adduction:   sens 77%, esp 79%  ← AC joint
# Speed:                 sens 54%, esp 81%  ← bíceps
# Yergason:              sens 43%, esp 79%  ← bíceps
# ROM passivo global:    padrão capsulite adesiva (ER > ABD > RI)

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

def carregar_subjetivo(caminho=None):
    if caminho:
        with open(caminho, encoding='utf-8') as f:
            return json.load(f)
    pasta = 'dados_pacientes'
    arquivos = [f for f in os.listdir(pasta) if f.startswith('ombro_subjetivo_')]
    if not arquivos:
        raise FileNotFoundError('Nenhum subjetivo de ombro encontrado. Rode subjetivo_ombro.py primeiro.')
    arquivos.sort(reverse=True)
    caminho = os.path.join(pasta, arquivos[0])
    print(f'  Carregando: {caminho}\n')
    with open(caminho, encoding='utf-8') as f:
        return json.load(f)


# =============================================================================
# BLOCOS DO EXAME FÍSICO
# =============================================================================

def bloco_inspecao(dados):
    """
    BLOCO 1 — Inspeção
    Pocket Guide: "inspect for obvious signs of muscle atrophy or asymmetry"
    """
    _bloco('BLOCO 1 — Inspeção')

    dados['atrofia_muscular']       = sn('  Atrofia visível (fossa supraespinhosa, infraespinhosa, deltóide)? ')
    dados['assimetria_ombros']      = sn('  Assimetria entre os dois ombros? ')
    dados['deformidade_ac']         = sn('  Deformidade ou proeminência visível na articulação AC (clavícula)? ')
    dados['scapular_winging']       = sn('  Escápula "em asa" visível ao repouso ou ao empurrar parede? ')
    dados['calor_local']            = sn('  Calor ou eritema local ao toque? ')


def bloco_palpacao(dados, subjetivo):
    """
    BLOCO 2 — Palpação
    Pocket Guide: palpate AC joint, bicipital groove (lateral to coracoid),
                  subacromial bursa (expose by extending + internally rotating arm)
    """
    _bloco('BLOCO 2 — Palpação Dirigida')

    # Sempre
    dados['dor_palpacao_subacromia']    = sn('  Dor à palpação do espaço subacromial (sob o acrômio)? ')
    dados['dor_palpacao_ac']            = sn('  Dor à palpação da articulação AC (topo do ombro)? ')

    # Condicional — se dor anterior/bicipital no subjetivo
    if subjetivo.get('dor_anterior_bicipital'):
        print()
        dados['dor_palpacao_sulco_bicipital'] = sn('  Dor à palpação do sulco bicipital (anterior do braço)? ')
    else:
        dados['dor_palpacao_sulco_bicipital'] = False

    # Sempre — palpação glenoumeral
    dados['dor_palpacao_glenoumeral']   = sn('  Dor à palpação posterior da articulação glenoumeral? ')


def bloco_rom(dados):
    """
    BLOCO 3 — Arco de movimento
    Pocket Guide: Apley Scratch test (RI + adução), alcance posterior do pescoço (RE + abdução),
                  passive cross-arm (AC joint stress)
    Open Evidence: padrão capsulite = ER > ABD > RI (todos restritos passivamente)
    """
    _bloco('BLOCO 3 — Arco de Movimento')

    dados['rom_ativo_limitado']         = sn('  Movimento ativo limitado (não consegue levantar o braço livremente)? ')
    dados['rom_passivo_limitado']       = sn('  Movimento passivo também limitado (quando você move o braço do paciente)? ')

    if dados['rom_passivo_limitado']:
        print('\n  Se passivo limitado — qual movimento está mais restrito?')
        print('  1) Rotação externa (RE) mais limitada que os outros')
        print('  2) Abdução mais limitada')
        print('  3) Rotação interna mais limitada')
        print('  4) Todos igualmente limitados (limitação global)')
        while True:
            op = input('  Opção (1-4): ').strip()
            if op in ('1', '2', '3', '4'):
                break
            print('  Digite 1, 2, 3 ou 4.')
        dados['padrão_restricao_re_predomina']      = (op == '1')  # capsulite adesiva
        dados['padrão_restricao_abducao']           = (op == '2')
        dados['padrão_restricao_ri']                = (op == '3')
        dados['padrão_restricao_global']            = (op == '4')
    else:
        dados['padrão_restricao_re_predomina']      = False
        dados['padrão_restricao_abducao']           = False
        dados['padrão_restricao_ri']                = False
        dados['padrão_restricao_global']            = False

    # Adução cruzada passiva (AC joint)
    dados['dor_adducao_cruzada_passiva'] = sn('\n  Dor ao cruzar passivamente o braço na frente do peito (teste AC)? ')


def bloco_forca(dados):
    """
    BLOCO 4 — Força muscular
    Pocket Guide: testar abdução (C5), RE (C5-6), RI, flexão, elevação escapular
    """
    _bloco('BLOCO 4 — Força Muscular')

    dados['fraqueza_abducao']           = sn('  Fraqueza à abdução (paciente não consegue resistir à força para baixo)? ')
    dados['fraqueza_rotacao_externa']   = sn('  Fraqueza à rotação externa contra resistência? ')
    dados['fraqueza_rotacao_interna']   = sn('  Fraqueza à rotação interna contra resistência? ')
    dados['fraqueza_flexao']            = sn('  Fraqueza à flexão anterior do ombro? ')


def bloco_testes_alvo(dados, subjetivo):
    """
    BLOCO 5 — Testes especiais alvo
    Modulares: só faz o que o subjetivo sinalizou
    Pocket Guide + Open Evidence — testes com melhor acurácia por diagnóstico
    """
    _bloco('BLOCO 5 — Testes Alvo')

    # --- IMPINGEMENT / ROTATOR CUFF (sempre se dor subacromial ou lateral) ---
    if subjetivo.get('dor_subacromia_lateral') or subjetivo.get('piora_overhead'):
        print('\n  → Testes de impingement:\n')
        # Painful arc: sens 71%, esp 81% — melhor teste de triagem para impingement
        dados['arco_doloroso_positivo']     = sn('  Arco doloroso entre 60-120° de abdução (painful arc)? ')
        # Hawkins-Kennedy: sens 76%
        dados['hawkins_kennedy_positivo']   = sn('  Hawkins-Kennedy positivo (ombro 90° flexão + RI forçada → dor)? ')
        # Neer: sens 64-68%
        dados['neer_positivo']              = sn('  Neer positivo (flexão passiva com RI → dor subacromial)? ')
    else:
        dados['arco_doloroso_positivo']     = False
        dados['hawkins_kennedy_positivo']   = False
        dados['neer_positivo']              = False

    # --- RUPTURA ROTATOR CUFF (se fraqueza ou suspeita de tear) ---
    if dados.get('fraqueza_abducao') or subjetivo.get('fraqueza_subjetiva'):
        print('\n  → Testes para ruptura:\n')
        # Empty can (Jobe): sens 71%, esp 49% — supraspinatus
        dados['empty_can_positivo']             = sn('  Empty can positivo (abdução 90° + RI "lata vazia" → fraqueza/dor)? ')
        # Drop arm: sens 24%, esp 93% — específico para ruptura total
        dados['drop_arm_positivo']              = sn('  Drop arm positivo (incapaz de baixar o braço lentamente)? ')
        # External rotation lag: sens 47%, esp 94%, LR+ 7.2 — melhor para ruptura
        dados['external_rotation_lag_positivo'] = sn('  Sinal de lag em RE (braço não mantém RE passiva ao soltar)? ')
        # Gerber lift-off: subscapularis
        dados['gerber_liftoff_positivo']        = sn('  Gerber lift-off positivo (mão nas costas, incapaz de empurrar posterior)? ')
    else:
        dados['empty_can_positivo']             = False
        dados['drop_arm_positivo']              = False
        dados['external_rotation_lag_positivo'] = False
        dados['gerber_liftoff_positivo']        = False

    # --- BÍCEPS (se dor anterior/bicipital) ---
    if subjetivo.get('dor_anterior_bicipital'):
        print('\n  → Testes para bíceps:\n')
        # Speed: sens 54%, esp 81%
        dados['speed_positivo']     = sn('  Speed positivo (flexão resistida com cotovelo estendido e supinado → dor sulco)? ')
        # Yergason: sens 43%, esp 79%
        dados['yergason_positivo']  = sn('  Yergason positivo (supinação resistida com cotovelo 90° → dor sulco bicipital)? ')
    else:
        dados['speed_positivo']     = False
        dados['yergason_positivo']  = False

    # --- AC JOINT (se dor superior ou trauma AC) ---
    if subjetivo.get('dor_superior_ac') or subjetivo.get('trauma_ac_previo'):
        print('\n  → Teste AC joint:\n')
        # Cross-arm adduction: sens 77%, esp 79%
        dados['cross_arm_positivo'] = sn('  Cross-arm adduction positivo (adução passiva cruzada → dor AC)? ')
    else:
        dados['cross_arm_positivo'] = False

    # --- SLAP / LABRUM (se dor posterior, instabilidade ou atleta arremessador) ---
    if subjetivo.get('dor_posterior') or subjetivo.get('atleta_arremessador') or subjetivo.get('sensacao_dando_tranco'):
        print('\n  → Testes para SLAP / instabilidade:\n')
        # O'Brien: dor interna com supinação, alívio com pronação = SLAP
        dados['obrien_positivo']        = sn('  O\'Brien positivo (dor INTERNA com mão supinada, alivia com pronação)? ')
        # Apprehension: instabilidade anterior
        dados['apprehension_positivo']  = sn('  Apprehension test positivo (RE passiva 90° → apreensão do paciente)? ')
    else:
        dados['obrien_positivo']        = False
        dados['apprehension_positivo']  = False

    # Marcar exame físico como realizado
    dados['exame_fisico_local_positivo'] = any([
        dados.get('dor_palpacao_subacromia'),
        dados.get('arco_doloroso_positivo'),
        dados.get('empty_can_positivo'),
        dados.get('drop_arm_positivo'),
        dados.get('external_rotation_lag_positivo'),
        dados.get('fraqueza_abducao'),
        dados.get('fraqueza_rotacao_externa'),
        dados.get('rom_passivo_limitado'),
    ])


# =============================================================================
# SALVAR COMPLETO
# =============================================================================

def salvar_completo(dados, pasta='dados_pacientes'):
    os.makedirs(pasta, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome = os.path.join(pasta, f'ombro_completo_{timestamp}.json')
    with open(nome, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f'\n  ✅ Dicionário completo salvo em: {nome}')
    return nome


# =============================================================================
# MAIN
# =============================================================================

def coletar_objetivo_ombro(caminho_subjetivo=None):
    print('\n' + '='*50)
    print('  SYMPTOPY — Exame Físico: Dor no Ombro  (V1)')
    print('='*50)
    print('  Registre os achados do exame físico.\n')

    subjetivo = carregar_subjetivo(caminho_subjetivo)
    dados = subjetivo.copy()

    bloco_inspecao(dados)
    bloco_palpacao(dados, subjetivo)
    bloco_rom(dados)
    bloco_forca(dados)
    bloco_testes_alvo(dados, subjetivo)

    # Resumo
    chaves_objetivo = [
        'atrofia_muscular', 'assimetria_ombros', 'deformidade_ac', 'scapular_winging',
        'calor_local', 'dor_palpacao_subacromia', 'dor_palpacao_ac',
        'dor_palpacao_sulco_bicipital', 'dor_palpacao_glenoumeral',
        'rom_ativo_limitado', 'rom_passivo_limitado', 'padrão_restricao_re_predomina',
        'dor_adducao_cruzada_passiva',
        'fraqueza_abducao', 'fraqueza_rotacao_externa', 'fraqueza_rotacao_interna',
        'arco_doloroso_positivo', 'hawkins_kennedy_positivo', 'neer_positivo',
        'empty_can_positivo', 'drop_arm_positivo', 'external_rotation_lag_positivo',
        'gerber_liftoff_positivo', 'speed_positivo', 'yergason_positivo',
        'cross_arm_positivo', 'obrien_positivo', 'apprehension_positivo',
    ]

    print('\n' + '='*50)
    print('  ACHADOS DO EXAME FÍSICO')
    print('='*50)
    positivos = [k for k in chaves_objetivo if dados.get(k)]
    negativos = [k for k in chaves_objetivo if not dados.get(k)]

    if positivos:
        print(f'  Positivos ({len(positivos)}):')
        for p in positivos:
            print(f'    + {p}')
    if negativos:
        print(f'  Negativos ({len(negativos)}):')
        for n in negativos:
            print(f'    - {n}')

    arquivo = salvar_completo(dados)
    print('\n  Próximo: runner_ombro.py → engine → diagnóstico\n')
    return dados, arquivo


if __name__ == '__main__':
    coletar_objetivo_ombro()