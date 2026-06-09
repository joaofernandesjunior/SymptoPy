# modules/sintomas/musculoesqueletico/tornozelo_pe/objetivo.py
# Exame físico dirigido — Dor no Tornozelo e Pé
# Técnica resumida antes de cada questão para facilitar execução
# Rodar da raiz: python -m modules.sintomas.musculoesqueletico.tornozelo_pe.objetivo

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
    arquivos = [f for f in os.listdir(pasta) if f.startswith('tornozelo_pe_subjetivo_')]
    if not arquivos:
        raise FileNotFoundError('Nenhum subjetivo de tornozelo/pé encontrado. Rode subjetivo.py primeiro.')
    arquivos.sort(reverse=True)
    caminho = os.path.join(pasta, arquivos[0])
    print(f'  Carregando: {caminho}')
    with open(caminho, encoding='utf-8') as f:
        return json.load(f)


# =============================================================================
# BLOCOS DO EXAME FÍSICO
# =============================================================================

def bloco_inspecao(dados):
    _bloco('BLOCO 1 — Inspeção Geral')
    print('  Observe com o paciente em pé e depois em repouso.\n')

    _tecnica([
        'EDEMA / EQUIMOSE: compare os tornozelos. Edema perimaleoloar difuso',
        'sugere entorse ou artrite. Equimose lateral em 24-48h: entorse de tornozelo.',
    ])
    dados['edema_tornozelo']  = sn('  Edema peri-maleolar ou do pé visível? ')
    dados['equimose_visivel'] = sn('  Equimose presente? ')

    _tecnica([
        'DEFORMIDADE: valgismo ou varismo excessivo do retropé — avaliar em pé.',
        'Pé plano (arco plantar ausente) associado a fasciite plantar.',
        'Pé cavo (arco aumentado): sobrecarga no 5o metatarso e Aquiles.',
    ])
    dados['deformidade_visivel'] = sn('  Deformidade óssea ou postural visível? ')
    dados['pe_plano_valgismo']   = sn('  Pé plano ou valgismo do calcâneo? ')


def bloco_palpacao_ottawa(dados, subjetivo):
    """Palpação dirigida dos pontos de Ottawa — apenas se trauma presente."""
    _bloco('BLOCO 2A — Palpação Ottawa (Trauma)')
    print('  Aplicar palpação firme e pontual. Positivo = dor reprodutível.\n')

    _tecnica([
        'MALEOLO LATERAL: palpe a face posterior e inferior do maléolo lateral',
        '(fíbula distal), nos 6 cm proximais. Positivo: dor à compressão digital firme.',
        'Sensibilidade ~99% para fratura de fíbula.',
    ])
    dados['palpacao_maleolo_lateral_positiva'] = sn('  Dor à palpação nos 6 cm posteriores do maléolo lateral? ')

    _tecnica([
        'MALEOLO MEDIAL: palpe a face posterior e inferior da tíbia distal,',
        'nos 6 cm proximais. Positivo: dor à palpação = considerar fratura de tíbia.',
    ])
    dados['palpacao_maleolo_medial_positiva'] = sn('  Dor à palpação nos 6 cm posteriores do maléolo medial? ')

    _tecnica([
        'BASE DO 5o METATARSO: palpe a tuberosidade na face lateral do médiopé',
        '(proeminência óssea lateral). Dor = suspeita de fratura de Jones.',
    ])
    dados['palpacao_base_5o_meta_positiva'] = sn('  Dor à palpação na base do 5o metatarso? ')

    _tecnica([
        'OSSO NAVICULAR: palpe o dorso medial do pé, entre tornozelo e antepé.',
        'Dor = suspeita de fratura de estresse do navicular.',
    ])
    dados['palpacao_navicular_positiva'] = sn('  Dor à palpação no navicular? ')

    _tecnica([
        'CAPACIDADE DE APOIO: peça ao paciente para dar 4 passos na consulta.',
        'Incapaz = Ottawa positivo para qualquer local afetado.',
    ])
    dados['incapaz_apoio_exame'] = sn('  Incapaz de apoiar o pé e dar 4 passos agora? ')

    dados['ottawa_exame_positivo'] = any([
        dados['palpacao_maleolo_lateral_positiva'],
        dados['palpacao_maleolo_medial_positiva'],
        dados['palpacao_base_5o_meta_positiva'],
        dados['palpacao_navicular_positiva'],
        dados['incapaz_apoio_exame'],
    ])

    _tecnica([
        'LIGAMENTOS LATERAIS: palpe o ATFL (anterior ao maléolo lateral)',
        'e o CFL (abaixo do maléolo). Dor pontual = lesão ligamentar lateral.',
    ])
    dados['dor_ligamentos_laterais'] = sn('  Dor à palpação do ATFL ou CFL? ')


def bloco_palpacao_fasciite(dados):
    _bloco('BLOCO 2B — Palpação: Fasciite Plantar')

    _tecnica([
        'TUBEROSIDADE MEDIAL DO CALCÂNEO: com polegar firme, palpe o centro',
        'da sola do calcanhar, ligeiramente medial. É o ponto de inserção da fascia.',
        'POSITIVO: dor pontual reprodutível = maior achado de fasciite plantar.',
        'Sensibilidade ~80%, especificidade ~89%.',
    ])
    dados['dor_tuberosidade_medial_calc'] = sn('  Dor à palpação da tuberosidade medial do calcâneo? ')

    _tecnica([
        'FASCIA PLANTAR PROXIMAL: com o pé em extensao (dedos dorsiflexionados),',
        'palpe a faixa fibrosa ao longo da sola, partindo do calcâneo.',
        'Positivo: dor ao percurso da fascia (distingue de neurite de Baxter).',
    ])
    dados['dor_fascia_proximal'] = sn('  Dor à palpação ao longo da fascia plantar proximal? ')

    _tecnica([
        'DORSIFLEXAO PASSIVA DO PE: leve extensao dos dedos + dorsiflexao do tornozelo.',
        'Tensiona a fascia plantar. Piora da dor = confirma fasciite.',
    ])
    dados['dor_dorsiflexao_passiva'] = sn('  Dor com dorsiflexao passiva do pé (windlass test)? ')


def bloco_palpacao_aquiles(dados):
    _bloco('BLOCO 2C — Palpação: Tendão de Aquiles')

    _tecnica([
        'ZONA CRITICA (2-6 cm): palpe o tendão de Aquiles entre 2 e 6 cm',
        'acima da inserção no calcâneo. Esta zona é hipovascularizada.',
        'POSITIVO: dor ou espessamento neste ponto = tendinopatia de corpo.',
        'Distinguir da dor na inserção (tendinopatia insercional — conduta diferente).',
    ])
    dados['dor_zona_critica_aquiles']    = sn('  Dor ou espessamento no Aquiles, 2-6 cm acima do calcâneo? ')
    dados['dor_insercao_aquiles']        = sn('  Dor na própria inserção do tendão no calcâneo? ')

    _tecnica([
        'ESPESSAMENTO / NODULO: compare os dois tendões. Espessamento focal',
        'ou nódulo palpável = degeneração tendinosa (tendinose).',
    ])
    dados['espessamento_nodulo_aquiles'] = sn('  Espessamento focal ou nódulo palpável no tendão? ')

    _tecnica([
        'SINAL DE THOMPSON (ruptura): paciente em decúbito ventral, pernas fora da maca.',
        'Comprima a panturrilha. POSITIVO: ausência de flexão plantar = ruptura do Aquiles.',
        'Se suspeita de ruptura: encaminhamento urgente a ortopedia.',
    ])
    dados['thompson_positivo'] = sn('  Sinal de Thompson positivo (sem flexão plantar ao comprimir a panturrilha)? ')

    if dados['thompson_positivo']:
        print('\n  ALERTA: Suspeita de ruptura do Aquiles — ortopedia urgente!')


def bloco_morton(dados):
    _bloco('BLOCO 2D — Testes: Neuroma de Morton')

    _tecnica([
        'SINAL DE MULDER (click de Mulder): com o pé do paciente relaxado,',
        'comprima transversalmente o antepé entre polegar e dedos (squeeze test),',
        'enquanto o outro polegar pressiona o 3o-4o espaco interdigital na sola.',
        'POSITIVO: clique palpável + reprodução da dor ou queimação = Neuroma de Morton.',
        'Sensibilidade 62-86%, especificidade ~95%.',
    ])
    dados['mulder_positivo'] = sn('  Sinal de Mulder positivo (clique + dor ao comprimir o antepé)? ')

    _tecnica([
        'COMPRESSAO INTERDIGITAL: palpe o espaco entre o 3o e 4o metatarso',
        'na sola e no dorso. Dor localizada ou formigamento nos dedos = suspeita.',
    ])
    dados['dor_espaco_3_4_interdigital'] = sn('  Dor à palpação no espaco 3o-4o intermetatarsal? ')
    dados['hipoestesia_dedos_adjacentes'] = sn('  Hipoestesia no 3o ou 4o dedo (teste de toque)? ')


def bloco_tornozelo_articular(dados):
    _bloco('BLOCO 2E — Exame Articular do Tornozelo')

    _tecnica([
        'ADM ATIVA: peça dorsiflexao (puxar o pé para cima) e flexao plantar.',
        'Normal: dorsiflexao ~20°, flexao plantar ~50°.',
        'Limitacao dolorosa de toda a ADM: suspeita de artrite ou OA.',
    ])
    dados['limitacao_adm_tornozelo']   = sn('  Limitacao ou dor em toda a amplitude de movimento? ')
    dados['crepitacao_tornozelo']      = sn('  Crepitação palpável ao mover o tornozelo? ')

    _tecnica([
        'PALPACAO ARTICULAR: palpe a interlinha articular tibiotársica (anterior ao tornozelo)',
        'e subastragalina (abaixo do tornozelo, lateral e medial).',
        'Dor difusa em toda a interlinha = artrite ou OA avancada.',
    ])
    dados['dor_interlinha_tornozelo']  = sn('  Dor difusa à palpação da interlinha articular? ')
    dados['sinais_flogisticos']        = sn('  Calor, rubor ou aumento de volume articular? ')


# =============================================================================
# SALVAR
# =============================================================================

def salvar_completo(dados, pasta='dados_pacientes'):
    os.makedirs(pasta, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome = os.path.join(pasta, f'tornozelo_pe_completo_{timestamp}.json')
    with open(nome, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f'\n  Dicionário completo salvo em: {nome}')
    return nome


# =============================================================================
# MAIN
# =============================================================================

def coletar_objetivo_tornozelo_pe(caminho_subjetivo=None):
    print('\n' + '='*54)
    print('  SYMPTOPY — Exame Físico: Dor no Tornozelo e Pé')
    print('='*54)
    print('  Técnica resumida antes de cada teste.')
    print('  Registre os achados conforme examina.\n')

    subjetivo = carregar_subjetivo(caminho_subjetivo)
    dados     = subjetivo.copy()

    bloco_inspecao(dados)

    if dados.get('trauma_recente'):
        bloco_palpacao_ottawa(dados, subjetivo)
    else:
        loc = dados.get('localizacao_dor', '')
        if loc == 'calcanhar_plantar':
            bloco_palpacao_fasciite(dados)
        elif loc == 'posterior_aquiles':
            bloco_palpacao_aquiles(dados)
        elif loc == 'antepé_morton':
            bloco_morton(dados)
        elif loc == 'tornozelo_articular':
            bloco_tornozelo_articular(dados)
        else:
            # fallback — exame completo
            bloco_palpacao_fasciite(dados)
            bloco_palpacao_aquiles(dados)
            bloco_morton(dados)
            bloco_tornozelo_articular(dados)

    arquivo = salvar_completo(dados)
    print('\n  Próximo: runner.py -> engine -> diagnóstico\n')
    return dados, arquivo


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    coletar_objetivo_tornozelo_pe()
