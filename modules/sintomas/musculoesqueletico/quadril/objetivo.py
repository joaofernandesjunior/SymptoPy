# modules/sintomas/musculoesqueletico/quadril/objetivo.py
# Exame físico dirigido — Dor no Quadril
# Cada bloco inclui técnica resumida antes da pergunta para facilitar a execução
# Rodar da raiz: python -m modules.sintomas.musculoesqueletico.quadril.objetivo

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


def _tecnica(linhas):
    """Imprime instrução de técnica do exame antes da pergunta s/n."""
    print()
    for linha in linhas:
        print(f'  {linha}')


def carregar_subjetivo(caminho=None):
    if caminho:
        with open(caminho, encoding='utf-8') as f:
            return json.load(f)
    pasta = 'dados_pacientes'
    arquivos = [f for f in os.listdir(pasta) if f.startswith('quadril_subjetivo_')]
    if not arquivos:
        raise FileNotFoundError('Nenhum subjetivo de quadril encontrado. Rode subjetivo.py primeiro.')
    arquivos.sort(reverse=True)
    caminho = os.path.join(pasta, arquivos[0])
    print(f'  Carregando: {caminho}')
    with open(caminho, encoding='utf-8') as f:
        return json.load(f)


# =============================================================================
# BLOCOS DO EXAME FÍSICO
# =============================================================================

def bloco_inspecao_marcha(dados):
    _bloco('BLOCO 1 — Inspeção e Marcha')
    print('  Observe o paciente andando e em pé antes de deitar.\n')

    _tecnica([
        'MARCHA ANTÁLGICA: fase de apoio encurtada no lado doloroso,',
        'tronco inclina para o lado afetado para reduzir a carga articular.',
    ])
    dados['marcha_antalgica'] = sn('  Marcha antálgica presente? ')

    _tecnica([
        'MARCHA DE TRENDELENBURG: tronco cai para o lado CONTRALATERAL',
        'ao apoio — indica fraqueza de abdutores (glúteo médio/mínimo).',
        'Distinto da marcha antálgica onde o tronco vai para o lado afetado.',
    ])
    dados['marcha_trendelenburg'] = sn('  Marcha de Trendelenburg presente? ')

    _tecnica([
        'ENCURTAMENTO + ROTAÇÃO EXTERNA: membro em repouso mais curto',
        'e com pé rodado externamente — sinal clínico de fratura de colo femoral.',
    ])
    dados['encurtamento_visivel'] = sn('  Encurtamento ou rotação externa visível em repouso? ')


def bloco_palpacao(dados, subjetivo):
    _bloco('BLOCO 2 — Palpação Dirigida')
    localizacao = subjetivo.get('localizacao_dor', '')

    _tecnica([
        'GRANDE TROCÂNTER: com paciente em decúbito lateral (lado afetado para cima),',
        'palpe a face lateral proximal do fêmur com polegar firme.',
        'Positivo: dor pontual e reprodutível ao pressionar — principal achado de GTPS.',
    ])
    dados['dor_palpacao_grande_trocanter'] = sn('  Palpação dolorosa do grande trocânter? ')

    if localizacao == 'anterior' or not localizacao:
        _tecnica([
            'GROIN / VIRILHA ANTERIOR: palpe o triângulo femoral (abaixo do ligamento',
            'inguinal, medial ao sartório). Dor = suspeita intra-articular (OA, FAI, AVN).',
        ])
        dados['dor_palpacao_anterior_groin'] = sn('  Dor à palpação na região anterior / virilha? ')
    else:
        dados['dor_palpacao_anterior_groin'] = False


def bloco_amplitude_movimento(dados):
    _bloco('BLOCO 3 — Amplitude de Movimento (ADM)')
    print('  Paciente em decúbito dorsal. Compare sempre com o lado contralateral.\n')

    _tecnica([
        'ROTAÇÃO INTERNA: joelho flexionado a 90°, rode o pé lateralmente',
        '(a tíbia vai para fora = rotação interna do quadril).',
        'Normal: ~45°. Limitação + dor = OA (S 66%, E 79%).',
    ])
    dados['limitacao_rotacao_interna'] = sn('  Rotação interna limitada ou dolorosa (<20-30° vs contralateral)? ')

    _tecnica([
        'ROTAÇÃO EXTERNA: mesmo posicionamento, rode o pé medialmente.',
        'Normal: ~45°. Avaliar simetria.',
    ])
    dados['limitacao_rotacao_externa'] = sn('  Rotação externa limitada ou dolorosa? ')

    _tecnica([
        'ABDUÇÃO / ADUÇÃO: com quadril em extensão, afaste e aproxime o membro.',
        'Limitação de adução: S 80%, E 81% para OA.',
        'Limitação de abdução: S 80%, E 81% para OA.',
    ])
    dados['limitacao_abducao_adicao'] = sn('  Abdução ou adução limitadas ou dolorosas? ')

    dados['crepitacao_movimento'] = sn('  Crepitação ao mover o quadril passivamente? ')


def bloco_testes_provocativos(dados, subjetivo):
    _bloco('BLOCO 4 — Testes Provocativos')
    localizacao = subjetivo.get('localizacao_dor', '')
    dados['faber_realizado']  = False
    dados['fadir_realizado']  = False

    # FABER — útil para qualquer localização
    _tecnica([
        'FABER (Patrick): paciente supino. Posicione o calcanhar do lado afetado',
        'sobre o joelho contralateral (posição em "4").',
        'Aplique pressão suave sobre o joelho fletido em direção à maca.',
        'Positivo ANTERIOR (virilha/groin): patologia intra-articular (FAI, OA, labro).',
        'Positivo POSTERIOR (nádega/SIJ): articulação sacroilíaca.',
        'Sensibilidade: 72-91% para FAI/labro.',
    ])
    dados['faber_positivo'] = sn('  FABER positivo (reproduz dor anterior ou posterior)? ')
    dados['faber_realizado'] = True

    # FADIR — especialmente para localização anterior
    _tecnica([
        'FADIR: paciente supino. Flexione o quadril a 90°, então ADICIONE',
        '(aproxime da linha média) e ROTE INTERNAMENTE (pé vai para fora).',
        'Positivo: dor na virilha/groin = suspeita de FAI ou labro.',
        'Sensibilidade: 72-91%. FABER + FADIR positivos: S 97% para FAI/labro.',
    ])
    dados['fadir_positivo'] = sn('  FADIR positivo (dor anterior com flexão + adução + RI)? ')
    dados['fadir_realizado'] = True

    # Trendelenburg — especialmente para lateral
    _tecnica([
        'TRENDELENBURG: peça ao paciente para ficar em pé sobre o membro AFETADO',
        'por 30 segundos (sem apoio contralateral).',
        'Positivo: pelve CAI do lado contralateral (não sustentado).',
        'Indica fraqueza de abdutores (glúteo médio/mínimo) — associado a GTPS grave.',
    ])
    dados['sinal_trendelenburg'] = sn('  Sinal de Trendelenburg positivo? ')

    # Derivada para o engine: exclui FAI com 97% se ambos negativos
    dados['exame_fisico_local_positivo'] = any([
        dados.get('dor_palpacao_grande_trocanter'),
        dados.get('dor_palpacao_anterior_groin'),
        dados.get('faber_positivo'),
        dados.get('fadir_positivo'),
        dados.get('limitacao_rotacao_interna'),
        dados.get('limitacao_abducao_adicao'),
        dados.get('sinal_trendelenburg'),
    ])


# =============================================================================
# SALVAR
# =============================================================================

def salvar_completo(dados, pasta='dados_pacientes'):
    os.makedirs(pasta, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome = os.path.join(pasta, f'quadril_completo_{timestamp}.json')
    with open(nome, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f'\n  Dicionário completo salvo em: {nome}')
    return nome


# =============================================================================
# MAIN
# =============================================================================

def coletar_objetivo_quadril(caminho_subjetivo=None):
    print('\n' + '='*54)
    print('  SYMPTOPY — Exame Físico: Dor no Quadril')
    print('='*54)
    print('  Técnica resumida antes de cada teste.')
    print('  Registre os achados conforme examina.\n')

    subjetivo = carregar_subjetivo(caminho_subjetivo)
    dados     = subjetivo.copy()

    bloco_inspecao_marcha(dados)
    bloco_palpacao(dados, subjetivo)
    bloco_amplitude_movimento(dados)
    bloco_testes_provocativos(dados, subjetivo)

    # Resumo dos achados
    chaves_objetivo = [
        'marcha_antalgica', 'marcha_trendelenburg', 'encurtamento_visivel',
        'dor_palpacao_grande_trocanter', 'dor_palpacao_anterior_groin',
        'limitacao_rotacao_interna', 'limitacao_rotacao_externa',
        'limitacao_abducao_adicao', 'crepitacao_movimento',
        'faber_positivo', 'fadir_positivo', 'sinal_trendelenburg',
    ]
    print('\n' + '='*54)
    print('  ACHADOS DO EXAME FÍSICO')
    print('='*54)
    positivos = [k for k in chaves_objetivo if dados.get(k)]
    negativos = [k for k in chaves_objetivo if not dados.get(k)]
    if positivos:
        print(f'  Positivos ({len(positivos)}):')
        for p in positivos: print(f'    + {p}')
    if negativos:
        print(f'  Negativos ({len(negativos)}):')
        for n in negativos: print(f'    - {n}')

    arquivo = salvar_completo(dados)
    print('\n  Próximo: runner.py -> engine -> diagnóstico\n')
    return dados, arquivo


if __name__ == '__main__':
    coletar_objetivo_quadril()
