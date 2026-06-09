# objetivo.py — Exame físico dirigido: Dor Lombar (Coluna)
# V1 — confirmação neurológica e biomecânica da dor lombar
# Carrega JSON do subjetivo, adiciona achados do exame físico e salva completo
# Rodar da raiz: python -m modules.sintomas.musculoesqueletico.coluna.objetivo

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
    """Carrega o JSON mais recente do subjetivo da coluna se caminho não especificado."""
    if caminho:
        with open(caminho, encoding='utf-8') as f:
            return json.load(f)

    pasta = 'dados_pacientes'
    arquivos = [f for f in os.listdir(pasta) if f.startswith('coluna_subjetivo_')]
    if not arquivos:
        raise FileNotFoundError('Nenhum subjetivo de coluna encontrado em dados_pacientes/. '
                                'Rode subjetivo.py primeiro.')
    arquivos.sort(reverse=True)
    caminho = os.path.join(pasta, arquivos[0])
    print(f'  Carregando: {caminho}')
    with open(caminho, encoding='utf-8') as f:
        return json.load(f)


# =============================================================================
# BLOCOS DO EXAME FÍSICO
# =============================================================================

def bloco_inspecao_palpacao(dados):
    _bloco('BLOCO 1 — Inspeção e Palpação da Coluna')

    dados['deformidade_coluna'] = sn('  Deformidade visível na coluna (ex: escoliose acentuada, hipercifose, retificação da lordose)? ')
    dados['espasmo_muscular_paravertebral'] = sn('  Espasmo muscular paravertebral visível ou palpável? ')
    
    # Palpação de pontos chave
    dados['dor_palpacao_processos_espinhosos'] = sn('  Dor localizada à palpação de processos espinhosos (sinal de fratura/infecção)? ')
    dados['dor_palpacao_paravertebral'] = sn('  Dor à palpação da musculatura paravertebral (sinal de lombalgia mecânica/miofascial)? ')
    dados['giordano_positivo'] = sn('  Giordano positivo (dor à punção-percussão lombar - suspeita de pielonefrite)? ')


def bloco_movimento(dados):
    _bloco('BLOCO 2 — Amplitude de Movimento (Mobilidade)')

    dados['dor_movimento_flexao'] = sn('  Dor ou limitação importante na FLEXÃO anterior do tronco? ')
    dados['dor_movimento_extensao'] = sn('  Dor ou limitação importante na EXTENSÃO do tronco? ')


def bloco_neurologico_e_manobras(dados, subjetivo):
    _bloco('BLOCO 3 — Neurológico e Manobras Especiais')

    # Radiculopatia (só se refere dor irradiada ou dormência nas pernas no subjetivo)
    tem_sintoma_perna = subjetivo.get('dor_irradiada_mmii') or subjetivo.get('formigamento_ou_dormencia')

    if tem_sintoma_perna:
        print('  --- Teste de Lasegue (Estiramento Radicular) ---')
        dados['lasegue_positivo'] = sn('  Teste de Elevação da Perna Estendida (Lasegue) POSITIVO (dor irradiada no dermátomo entre 30° e 70°)? ')
        if dados['lasegue_positivo']:
            dados['lasegue_contralateral_positivo'] = sn('  Lasegue CONTRALATERAL positivo (reproduz dor na perna afetada ao elevar a perna sã)? ')
        else:
            dados['lasegue_contralateral_positivo'] = False
    else:
        dados['lasegue_positivo'] = False
        dados['lasegue_contralateral_positivo'] = False

    # Exame neurológico sumário dos MMII
    print('\n  --- Exame Neuromotor e Reflexos (L4/L5/S1) ---')
    dados['reflexo_patelar_diminuido'] = sn('  Reflexo Patelar (L4) diminuído ou abolido unilateralmente? ')
    dados['reflexo_aquileu_diminuido'] = sn('  Reflexo Aquileu (S1) diminuído ou abolido unilateralmente? ')
    
    dados['fraqueza_dorsiflexao_pe'] = sn('  Fraqueza na dorsiflexão do pé/hálux (L5 - ex: dificuldade de andar nos calcanhares)? ')
    dados['fraqueza_plantiflexao_pe'] = sn('  Fraqueza na plantiflexão do pé (S1 - ex: dificuldade de ficar nas pontas dos pés)? ')
    
    dados['deficit_sensibilidade_mmii'] = sn('  Déficit de sensibilidade tátil/dolorosa dermatomal evidente nos membros inferiores? ')

    # Agregadores do exame físico local
    dados['exame_fisico_local_positivo'] = any([
        dados['espasmo_muscular_paravertebral'], dados['dor_palpacao_processos_espinhosos'],
        dados['dor_palpacao_paravertebral'], dados['dor_movimento_flexao'],
        dados['dor_movimento_extensao'], dados['lasegue_positivo'],
        dados['reflexo_patelar_diminuido'], dados['reflexo_aquileu_diminuido'],
        dados['fraqueza_dorsiflexao_pe'], dados['fraqueza_plantiflexao_pe'],
        dados['deficit_sensibilidade_mmii']
    ])


# =============================================================================
# SALVAR DICIONÁRIO COMPLETO
# =============================================================================

def salvar_completo(dados, pasta='dados_pacientes'):
    os.makedirs(pasta, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome = os.path.join(pasta, f'coluna_completo_{timestamp}.json')
    with open(nome, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f'\n  ✅ Dicionário completo salvo em: {nome}')
    return nome


# =============================================================================
# MAIN
# =============================================================================

def coletar_objetivo_coluna(caminho_subjetivo=None):
    print('\n' + '='*50)
    print('  SYMPTOPY — Exame Físico: Dor Lombar (Coluna)')
    print('='*50)
    print('  Registre os achados do exame físico.\n')

    subjetivo = carregar_subjetivo(caminho_subjetivo)
    dados = subjetivo.copy()

    bloco_inspecao_palpacao(dados)
    bloco_movimento(dados)
    bloco_neurologico_e_manobras(dados, subjetivo)

    # Resumo dos achados positivos
    chaves_objetivo = [
        'deformidade_coluna', 'espasmo_muscular_paravertebral',
        'dor_palpacao_processos_espinhosos', 'dor_palpacao_paravertebral',
        'giordano_positivo', 'dor_movimento_flexao', 'dor_movimento_extensao',
        'lasegue_positivo', 'lasegue_contralateral_positivo',
        'reflexo_patelar_diminuido', 'reflexo_aquileu_diminuido',
        'fraqueza_dorsiflexao_pe', 'fraqueza_plantiflexao_pe',
        'deficit_sensibilidade_mmii'
    ]

    print('\n' + '='*50)
    print('  ACHADOS DO EXAME FÍSICO DA COLUNA')
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
    print('\n  Próximo: engine_coluna.py → interpretação clínica\n')
    return dados, arquivo


if __name__ == '__main__':
    coletar_objetivo_coluna()
