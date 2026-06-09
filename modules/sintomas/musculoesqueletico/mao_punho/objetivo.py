# modules/sintomas/musculoesqueletico/mao_punho/objetivo.py
# Exame físico dirigido — Mão, Punho e Dedos
# Técnica resumida antes de cada questão para facilitar execução
# Rodar da raiz: python -m modules.sintomas.musculoesqueletico.mao_punho.objetivo

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
    print()
    for linha in linhas:
        print(f'  {linha}')


def carregar_subjetivo(caminho=None):
    if caminho:
        with open(caminho, encoding='utf-8') as f:
            return json.load(f)
    pasta = 'dados_pacientes'
    arquivos = [f for f in os.listdir(pasta) if f.startswith('mao_punho_subjetivo_')]
    if not arquivos:
        raise FileNotFoundError('Nenhum subjetivo de mão/punho encontrado. Rode subjetivo.py primeiro.')
    arquivos.sort(reverse=True)
    caminho = os.path.join(pasta, arquivos[0])
    print(f'  Carregando: {caminho}')
    with open(caminho, encoding='utf-8') as f:
        return json.load(f)


# =============================================================================
# BLOCOS DO EXAME FÍSICO
# =============================================================================

def bloco_inspecao_geral(dados):
    _bloco('BLOCO 1 — Inspeção Geral')
    print('  Observe ambas as maos com o paciente em repouso e depois em movimento.\n')

    _tecnica([
        'EDEMA / ASSIMETRIA: compare lado afetado com contralateral.',
        'Edema fusiforme de dedos (dedo em salsicha) = artrite psoriásica ou reativa.',
        'Edema difuso de MCF/punhos = artrite inflamatória.',
    ])
    dados['edema_maos']        = sn('  Edema visível na mão ou punho? ')
    dados['edema_simetrico']   = sn('  Edema simétrico (ambas as maos)? ') if dados['edema_maos'] else False

    _tecnica([
        'DEFORMIDADES: verifique desvio ulnar dos dedos (AR avancada),',
        'abaulamento na base do polegar (rizartrose CMC),',
        'hiperextensao de IFD com flexao de IFP (dedo de pescoço de cisne).',
    ])
    dados['deformidade_visivel'] = sn('  Deformidade articular visível? ')

    _tecnica([
        'ATROFIA TENAR: compare o volume da eminência tenar (base do polegar)',
        'com o lado contralateral. Achatamento = STC moderado/grave.',
        'Atrofia hipotenar: suspeita de neuropatia ulnar.',
    ])
    dados['atrofia_tenar']     = sn('  Atrofia da eminência tenar visível? ')
    dados['atrofia_hipotenar'] = sn('  Atrofia da eminência hipotenar visível? ')

    _tecnica([
        'NODULOS: Heberden (IFD — ponta dos dedos) = OA; Bouchard (IFP — meio) = OA ou AR.',
        'Nodulos subcutâneos sobre MCF ou olécrano = nódulos reumatoides.',
    ])
    dados['nodulos_heberden_exame'] = sn('  Nódulos de Heberden (IFD) presentes? ')
    dados['nodulos_bouchard_exame'] = sn('  Nódulos de Bouchard (IFP) presentes? ')

    if dados.get('atrofia_tenar'):
        print('\n  ALERTA: Atrofia tenar ao exame = STC moderado/grave. Encaminhamento urgente.')


def bloco_palpacao_trauma(dados):
    """Bloco de palpação para suspeita de fratura do escafoide."""
    _bloco('BLOCO 2A — Palpação: Trauma (Escafoide)')

    _tecnica([
        'TABAQUEIRA ANATOMICA: com o polegar do paciente em extensao,',
        'identifique a depressao entre os tendoes do extensor curto (APL)',
        'e extensor longo do polegar (EPL). Palpe o fundo dessa depressao.',
        'POSITIVO: dor à palpacao firme = suspeita forte de fratura do escafoide.',
        'Sensibilidade ~90%, especificidade ~40% (alta S, baixa E).',
        'IMPORTANTE: XR inicial normal nao exclui fratura (falso-negativo: 30%)!',
    ])
    dados['tabaqueira_positiva'] = sn('  Dor à palpacao da tabaqueira anatomica? ')

    _tecnica([
        'COMPRESSAO AXIAL DO POLEGAR: segure o polegar em extensao neutra',
        'e comprima axialmente em direcao ao punho (telescoping test).',
        'POSITIVO: dor na tabaqueira = suspeita adicional de fratura do escafoide.',
    ])
    dados['compressao_axial_polegar_positiva'] = sn('  Dor à compressao axial do polegar em direcao ao punho? ')

    _tecnica([
        'TUBERCULO DO ESCAFOIDE (palmar): palpe o tuberculo do escafoide',
        'na face volar (palmar) do punho, distal ao ligamento transverso.',
        'Positivo: dor adicional confirma suspeita.',
    ])
    dados['tuberculo_escafoide_palmar'] = sn('  Dor à palpacao do tuberculo do escafoide (face palmar)? ')

    if dados['tabaqueira_positiva']:
        print('\n  CONDUTA: Imobilizar com tala de polegar mesmo com XR normal.')
        print('  Repetir XR em 10-14 dias ou solicitar RM/cintilografia.')


def bloco_neurologico(dados):
    _bloco('BLOCO 2B — Testes Neurológicos (STC / Neuropatia Ulnar)')

    _tecnica([
        'DURKAN (compressao do canal do carpo): com o paciente relaxado,',
        'comprima o canal do carpo com os polegares por 30 segundos.',
        'POSITIVO: reproducao de parestesia nos dedos polegar/indicador/medio.',
        'Sensibilidade 64%, Especificidade 83% (melhor teste individual para STC).',
    ])
    dados['durkan_positivo'] = sn('  Durkan positivo (parestesia reproduzida com compressao)? ')

    _tecnica([
        'PHALEN: paciente flete ambos os punhos a 90o e mantém por 60 segundos',
        '(dorsos das maos encostados um no outro — posicao invertida de rezar).',
        'POSITIVO: parestesia em polegar/indicador/medio em < 60 segundos.',
        'Sensibilidade 68%, Especificidade 73%.',
    ])
    dados['phalen_positivo'] = sn('  Phalen positivo (parestesia em < 60s de flexao do punho)? ')

    _tecnica([
        'TINEL: percuta sobre o canal do carpo (punho palmar) com o dedo.',
        'POSITIVO: choques eletricos / parestesia irradiados para os dedos.',
        'Sensibilidade 50%, Especificidade 77%. Menos util isolado.',
    ])
    dados['tinel_positivo'] = sn('  Sinal de Tinel positivo (choques ao percutir o canal do carpo)? ')

    _tecnica([
        'SINAL DE FROMENT (neuropatia ulnar): peca ao paciente para segurar',
        'uma folha de papel entre polegar e indicador (pinça lateral).',
        'POSITIVO: o polegar flete a IFP para compensar (fraqueza do adutor do',
        'polegar = inervacao ulnar). Indica lesao do nervo ulnar.',
    ])
    dados['froment_positivo'] = sn('  Sinal de Froment positivo (IFP do polegar flete ao pincar papel)? ')

    if dados.get('durkan_positivo') and dados.get('phalen_positivo'):
        print('\n  Durkan + Phalen ambos positivos: especificidade alta para STC.')


def bloco_tendíneo_articular(dados):
    _bloco('BLOCO 2C — Testes Tendíneos e Articulares')

    _tecnica([
        'FINKELSTEIN (De Quervain): peca ao paciente para fechar o polegar',
        'dentro do punho (polegar dentro dos outros dedos) e desviar o punho',
        'em direcao ao ulnar (para o lado do mínimo).',
        'POSITIVO: dor intensa na face dorsorradial do punho.',
        'Especificidade 100% para tenossinovite de De Quervain.',
        'ATENCAO: diferenciar de rizartrose (dor distal, na CMC) — testar separadamente.',
    ])
    dados['finkelstein_positivo'] = sn('  Finkelstein positivo (dor dorsorradial com desvio ulnar)? ')

    _tecnica([
        'PALPACAO DA POLIA A1 (dedo em gatilho): com o dedo estendido,',
        'palpe firmemente a regiao da polia A1: na palma da mao,',
        'na dobra proximal de cada dedo (nível da cabeca do metacarpo).',
        'POSITIVO: nodulo palpável e doloroso. Peca para fletir e estender o dedo.',
        'Estalido ou travamento = confirmacao de dedo em gatilho.',
    ])
    dados['polia_a1_dor_nodulo']   = sn('  Nodulo doloroso palpável na polia A1 (base do dedo na palma)? ')
    dados['gatilho_bloqueio_ativo'] = sn('  Estalido ou bloqueio ao fletir/estender o dedo no exame? ')

    _tecnica([
        'AXIAL GRIND TEST (rizartrose CMC): segure o 1o metacarpo do polegar,',
        'aplique compressao axial suave em direcao ao trapézio e rode o metacarpo.',
        'POSITIVO: dor ou crepitacao na articulacao CMC do polegar.',
        'Sensibilidade 30%, Especificidade 97% (teste muito especifico quando positivo).',
    ])
    dados['grind_test_positivo'] = sn('  Axial grind test positivo (dor/crepitacao na CMC do polegar)? ')

    _tecnica([
        'TRACTION SHIFT TEST (rizartrose): aplique tracao axial no polegar,',
        'depois rode e comprima. Dor + subluxacao da CMC ao comprimir.',
        'Sensibilidade 67%, Especificidade 100%.',
    ])
    dados['traction_shift_positivo'] = sn('  Traction shift test positivo? ')


def bloco_reumatologico(dados):
    _bloco('BLOCO 2D — Exame Reumatológico')

    _tecnica([
        'SQUEEZE TEST (MCF): comprima transversalmente as MCF de toda a mao.',
        'POSITIVO: dor à compressao = edema sinovial das MCFs = sinal sensivel de AR.',
    ])
    dados['squeeze_mcf_positivo'] = sn('  Dor à compressao transversal das MCFs (squeeze test)? ')

    _tecnica([
        'SINOVITE MCF / PUNHO: palpe cada MCF e a interlinha do punho.',
        'Sinovite = edema fusiforme mole, quente, sensível, simetrico.',
        'Diferenciar de OA (nodulos Heberden/Bouchard: osseos, firmes, frios).',
    ])
    dados['sinovite_mcf_punho']   = sn('  Sinovite palpável em MCF ou punho (edema mole e quente)? ')
    dados['ifd_poupadas_exame']   = sn('  IFD poupadas (sem edema nem nodulos nas pontas dos dedos)? ')

    _tecnica([
        'PRESS TEST (TFCC / ulnar do punho): peca ao paciente para apoiar',
        'as maos na cadeira e se levantar levemente. POSITIVO: dor focal no',
        'punho ulnar (complexo fibrocartilaginoso triangular — TFCC).',
    ])
    dados['press_test_positivo']  = sn('  Press test positivo (dor ulnar ao apoiar o peso)? ')

    if dados.get('sinovite_mcf_punho') and dados.get('ifd_poupadas_exame'):
        print('\n  Padrao sugestivo de artrite reumatoide — solicitar VHS, PCR, FR, Anti-CCP.')


# =============================================================================
# SALVAR
# =============================================================================

def salvar_completo(dados, pasta='dados_pacientes'):
    os.makedirs(pasta, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome = os.path.join(pasta, f'mao_punho_completo_{timestamp}.json')
    with open(nome, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f'\n  Dicionário completo salvo em: {nome}')
    return nome


# =============================================================================
# MAIN
# =============================================================================

def coletar_objetivo_mao_punho(caminho_subjetivo=None):
    print('\n' + '='*54)
    print('  SYMPTOPY — Exame Físico: Mão, Punho e Dedos')
    print('='*54)
    print('  Técnica resumida antes de cada teste.')
    print('  Registre os achados conforme examina.\n')

    subjetivo = carregar_subjetivo(caminho_subjetivo)
    dados     = subjetivo.copy()

    bloco_inspecao_geral(dados)

    padrao = dados.get('padrao_clinico', '')
    if padrao == 'trauma':
        bloco_palpacao_trauma(dados)
    elif padrao == 'neurologico':
        bloco_neurologico(dados)
    elif padrao == 'mecanico':
        bloco_tendíneo_articular(dados)
    elif padrao == 'reumatologico':
        bloco_reumatologico(dados)
    else:
        # fallback — exame completo
        bloco_palpacao_trauma(dados)
        bloco_neurologico(dados)
        bloco_tendíneo_articular(dados)
        bloco_reumatologico(dados)

    arquivo = salvar_completo(dados)
    print('\n  Próximo: runner.py -> engine -> diagnóstico\n')
    return dados, arquivo


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    coletar_objetivo_mao_punho()
