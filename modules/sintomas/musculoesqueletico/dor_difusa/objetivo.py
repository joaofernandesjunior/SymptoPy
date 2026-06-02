# objetivo.py — Exame físico dirigido: Dor Difusa / Fibromialgia
# V1 — baseado em critérios de exclusão e confirmação de sensibilização central
# Carrega JSON do subjetivo, adiciona achados do exame físico e salva completo
# Rodar da raiz: python -m modules.sintomas.musculoesqueletico.dor_difusa.objetivo

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
    """Carrega o JSON mais recente do subjetivo se caminho não especificado."""
    if caminho:
        with open(caminho, encoding='utf-8') as f:
            return json.load(f)

    pasta = 'dados_pacientes'
    arquivos = [f for f in os.listdir(pasta) if f.startswith('dor_difusa_subjetivo_')]
    if not arquivos:
        raise FileNotFoundError('Nenhum subjetivo de dor difusa encontrado em dados_pacientes/. '
                                'Rode subjetivo.py primeiro.')
    arquivos.sort(reverse=True)
    caminho = os.path.join(pasta, arquivos[0])
    print(f'  Carregando: {caminho}')
    with open(caminho, encoding='utf-8') as f:
        return json.load(f)


# =============================================================================
# BLOCOS DO EXAME FÍSICO
# =============================================================================

def bloco_exame_articular(dados):
    _bloco('BLOCO 1 — Inspeção e Palpação Articular (Exclusão)')

    # Sinovite/Artrite ativa é um forte sinal de alerta para causas reumatológicas inflamatórias
    dados['presenca_sinovite_artrite'] = sn('  Sinais de sinovite ou artrite ativa (edema articular, calor, eritema em punhos/mão/joelhos)? ')
    dados['calor_ou_eritema_articular'] = dados['presenca_sinovite_artrite']
    dados['sem_calor_ou_eritema'] = not dados['presenca_sinovite_artrite']

    # Dor desproporcional à palpação de tecidos moles (músculos, tendões) sem lesão local
    dados['hiperalgesia_palpacao_tecidos_moles'] = sn('  Hiperalgesia generalizada à palpação leve de tecidos moles (músculos, enteses)? ')


def bloco_amplitude_hipermobilidade(dados):
    _bloco('BLOCO 2 — Arco de Movimento e Hipermobilidade')

    dados['rom_articular_preservado'] = sn('  Arco de movimento (ROM) passivo e ativo preservado em todas as articulações? ')
    dados['hipermobilidade_articular_beighton'] = sn('  Sinais de hipermobilidade articular generalizada (Escore de Beighton >= 5/9)? ')


def bloco_neurologico(dados):
    _bloco('BLOCO 3 — Exame Neurológico')

    # No quadro de fibromialgia clássico, não há déficit neurológico focal (reflexos e força estão normais)
    dados['deficit_neurologico_objetivo'] = sn('  Déficit neurológico focal detectado ao exame (fraqueza muscular focal, hiporreflexia isolada)? ')
    
    # Sensibilidade geral
    dados['alodinia'] = sn('  Alodinia presente (dor provocada por estímulo tátil leve, ex: toque do algodão/roupa)? ')

    # Agregadores do exame físico
    dados['exame_fisico_local_positivo'] = dados['hiperalgesia_palpacao_tecidos_moles'] or dados['alodinia']


# =============================================================================
# SALVAR DICIONÁRIO COMPLETO
# =============================================================================

def salvar_completo(dados, pasta='dados_pacientes'):
    os.makedirs(pasta, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome = os.path.join(pasta, f'dor_difusa_completo_{timestamp}.json')
    with open(nome, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f'\n  ✅ Dicionário completo salvo em: {nome}')
    return nome


# =============================================================================
# MAIN
# =============================================================================

def coletar_objetivo_dor_difusa(caminho_subjetivo=None):
    print('\n' + '='*50)
    print('  SYMPTOPY — Exame Físico: Dor Difusa / Fibromialgia')
    print('='*50)
    print('  Registre os achados do exame físico.')

    subjetivo = carregar_subjetivo(caminho_subjetivo)
    dados = subjetivo.copy()

    bloco_exame_articular(dados)
    bloco_amplitude_hipermobilidade(dados)
    bloco_neurologico(dados)

    chaves_objetivo = [
        'presenca_sinovite_artrite', 'hiperalgesia_palpacao_tecidos_moles',
        'rom_articular_preservado', 'hipermobilidade_articular_beighton',
        'deficit_neurologico_objetivo', 'alodinia'
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
    print('\n  Próximo: engine_fibromialgia.py → diagnóstico e conduta farmacológica\n')
    return dados, arquivo


if __name__ == '__main__':
    coletar_objetivo_dor_difusa()
