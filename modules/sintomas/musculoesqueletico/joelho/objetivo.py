# objetivo.py — Exame físico dirigido: Dor no Joelho
# V1 — confirmação anatômica, não repetição da anamnese
# Carrega JSON do subjetivo, adiciona achados e salva versão completa
# Rodar da raiz: python3 -m modules.sintomas.musculoesqueletico.joelho.objetivo
#
# Regra de ouro: cada pergunta responde uma de sete coisas:
#   1. tem líquido?
#   2. tem inflamação forte?
#   3. tem dor articular interna?
#   4. tem dor patelofemoral?
#   5. tem bursa superficial?
#   6. tem cisto poplíteo?
#   7. tem sinal mecânico meniscal?

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
    arquivos = [f for f in os.listdir(pasta) if f.startswith('joelho_subjetivo_')]
    if not arquivos:
        raise FileNotFoundError('Nenhum subjetivo encontrado em dados_pacientes/. '
                                'Rode subjetivo.py primeiro.')
    arquivos.sort(reverse=True)
    caminho = os.path.join(pasta, arquivos[0])
    print(f'  Carregando: {caminho}')
    with open(caminho, encoding='utf-8') as f:
        return json.load(f)


# =============================================================================
# BLOCOS DO EXAME FÍSICO
# =============================================================================

def bloco_inspecao(dados):
    """
    BLOCO 1 — Inspeção geral
    Separa: derrame intra-articular / bursite superficial / inflamação aguda
    """
    _bloco('BLOCO 1 — Inspeção Geral')

    dados['derrame_articular']       = sn('  Derrame intra-articular visível (joelho "cheio", flutuação)? ')
    dados['calor_intenso_local']     = sn('  Calor local importante ao toque? ')
    dados['edema_prepatelar_visivel']= sn('  Edema mole e visível SOBRE a patela (bursite superficial)? ')
    # deformidade_grosseira: útil para trauma grave e ortopedia pesada.
    # Peso baixo nas hipóteses de APS — coletado para triagem, não para score.
    dados['deformidade_grosseira']   = sn('  Deformidade grosseira (varo, valgo, subluxação aparente)? ')

    # descarga_peso_preservada: complementa Ottawa do subjetivo sem redundância.
    # Não usar como decisão forte no engine — aqui serve como contexto funcional.
    dados['descarga_peso_preservada']= sn('  Paciente consegue apoiar peso no membro sem grande dificuldade? ')


def bloco_palpacao(dados, subjetivo):
    """
    BLOCO 2 — Palpação dirigida
    Conversa diretamente com os hot spots do subjetivo.
    """
    _bloco('BLOCO 2 — Palpação Dirigida')

    # Linha articular — sempre pergunta (discriminador universal)
    dados['dor_linha_articular_palpacao'] = sn('  Dor à palpação da linha articular (medial ou lateral)? ')

    # Facetas patelares — só se dor anterior no subjetivo
    if subjetivo.get('dor_anterior_joelho'):
        dados['dor_palpacao_facetas_patelares'] = sn('  Dor à palpação das facetas patelares (joelho em extensão)? ')
    else:
        dados['dor_palpacao_facetas_patelares'] = False

    # Anserina — só se dor medial abaixo da linha articular
    if subjetivo.get('dor_medial_abaixo_linha_articular'):
        dados['dor_palpacao_anserina'] = sn('  Dor à palpação ~5cm abaixo da linha articular medial (bursite anserina)? ')
    else:
        dados['dor_palpacao_anserina'] = False

    # Massa poplítea — só se massa relatada no subjetivo
    if subjetivo.get('massa_fossa_poplitea'):
        dados['massa_poplitea_palpavel'] = sn('  Massa palpável na fossa poplítea? ')
        # transiluminacao_positiva: útil mas pouco usado na prática real.
        # Mantido para completude — peso baixo no engine, não é decisor forte.
        dados['transiluminacao_positiva']= sn('  Transiluminação positiva (conteúdo líquido confirmado)? ')
    else:
        dados['massa_poplitea_palpavel'] = False
        dados['transiluminacao_positiva']= False


def bloco_movimento(dados):
    """
    BLOCO 3 — Arco de movimento
    Pouco e bom: o que muda decisão em OA, SDPF, Baker e derrame.
    """
    _bloco('BLOCO 3 — Movimento')

    dados['flexao_limitada']    = sn('  Flexão limitada (não chega a 120° confortavelmente)? ')
    dados['extensao_limitada']  = sn('  Extensão limitada (joelho não estende completamente)? ')
    dados['crepitacao']         = sn('  Crepitação audível ou palpável durante o movimento? ')


def bloco_testes_alvo(dados, subjetivo):
    """
    BLOCO 4 — Testes alvo
    Modulares: só testa o que o subjetivo sinalizou.
    Regra: exame físico confirma ou derruba — não repete anamnese.
    """
    _bloco('BLOCO 4 — Testes Alvo')
    fez_algum = False

    # McMurray — só se dor na linha articular ou torção
    if subjetivo.get('dor_linha_articular') or subjetivo.get('trauma_torcao_recente'):
        dados['mcmurray_positivo'] = sn('  McMurray positivo (sens 61%, esp 84%)? ')
        fez_algum = True
    else:
        dados['mcmurray_positivo'] = False

    # Squat unipodal — só se dor anterior
    if subjetivo.get('dor_anterior_joelho'):
        dados['squat_unipodal_positivo'] = sn('  Squat unipodal reproduz a dor anterior (sens 91%, esp 50%)? ')
        fez_algum = True
    else:
        dados['squat_unipodal_positivo'] = False

    # Sinal de flutuação patelar — só se derrame visível
    if dados.get('derrame_articular'):
        dados['sinal_flutuacao_patelar'] = sn('  Sinal de flutuação patelar positivo (confirma derrame)? ')
        fez_algum = True
    else:
        dados['sinal_flutuacao_patelar'] = False

    if not fez_algum:
        print('  Nenhum teste alvo indicado pelo padrão do subjetivo.')

    # Marcar exame físico como realizado para o engine
    dados['exame_fisico_local_positivo'] = any([
        dados.get('derrame_articular'), dados.get('calor_intenso_local'),
        dados.get('dor_linha_articular_palpacao'), dados.get('dor_palpacao_facetas_patelares'),
        dados.get('crepitacao'), dados.get('mcmurray_positivo'),
        dados.get('squat_unipodal_positivo')
    ])


# =============================================================================
# SALVAR DICIONÁRIO COMPLETO
# =============================================================================

def salvar_completo(dados, pasta='dados_pacientes'):
    os.makedirs(pasta, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome = os.path.join(pasta, f'joelho_completo_{timestamp}.json')
    with open(nome, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f'\n  ✅ Dicionário completo salvo em: {nome}')
    return nome


# =============================================================================
# MAIN
# =============================================================================

def coletar_objetivo_joelho(caminho_subjetivo=None):
    print('\n' + '='*50)
    print('  SYMPTOPY — Exame Físico: Dor no Joelho  (V1)')
    print('='*50)
    print('  Registre os achados do exame físico.\n')

    subjetivo = carregar_subjetivo(caminho_subjetivo)
    dados = subjetivo.copy()   # herda tudo do subjetivo

    bloco_inspecao(dados)
    bloco_palpacao(dados, subjetivo)
    bloco_movimento(dados)
    bloco_testes_alvo(dados, subjetivo)

    # Resumo dos achados positivos do objetivo
    chaves_objetivo = [
        'derrame_articular', 'calor_intenso_local', 'edema_prepatelar_visivel',
        'deformidade_grosseira', 'dor_linha_articular_palpacao',
        'dor_palpacao_facetas_patelares', 'dor_palpacao_anserina',
        'massa_poplitea_palpavel', 'transiluminacao_positiva',
        'flexao_limitada', 'extensao_limitada', 'crepitacao',
        'mcmurray_positivo', 'squat_unipodal_positivo', 'sinal_flutuacao_patelar'
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
    print('\n  Próximo: runner.py → carrega este JSON → engine → diagnóstico\n')
    return dados, arquivo


if __name__ == '__main__':
    coletar_objetivo_joelho()