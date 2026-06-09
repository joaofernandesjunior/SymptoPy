# modules/sintomas/musculoesqueletico/tornozelo_pe/subjetivo.py
# Anamnese — Dor no Tornozelo e Pé
# Roteador clínico: trauma (Ottawa) vs. não-trauma (localização)
# Rodar da raiz: python -m modules.sintomas.musculoesqueletico.tornozelo_pe.subjetivo

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


def _bloco_roteador_trauma(dados):
    _bloco('BLOCO 1 — Roteador: Trauma ou Não-Trauma?')
    print('  A presença de trauma define o algoritmo de Ottawa.\n')
    dados['trauma_recente'] = sn('  Houve traumatismo, entorse ou torção recente? ')


def _bloco_ottawa(dados):
    """Critérios de Ottawa — aplicar apenas se trauma presente."""
    _bloco('BLOCO 2A — Regras de Ottawa (Trauma)')
    print('  Indicam necessidade de RX se qualquer critério presente.')
    print('  Sensibilidade ~99% para fratura (evita RX desnecessário).\n')

    print('  --- TORNOZELO (RX de tornozelo indicado se positivo) ---')
    dados['dor_maleolo_posterior_lateral'] = sn(
        '  Dor à palpação nos 6 cm posteriores/inferiores do maléolo lateral? '
    )
    dados['dor_maleolo_posterior_medial'] = sn(
        '  Dor à palpação nos 6 cm posteriores/inferiores do maléolo medial? '
    )
    dados['incapaz_apoio_4_passos'] = sn(
        '  Incapaz de apoiar o pé e dar 4 passos (imediatamente e na consulta)? '
    )

    print('\n  --- PÉ (RX de pé indicado se positivo) ---')
    dados['dor_navicular'] = sn(
        '  Dor à palpação na base do 5o metatarso (lateral do médiopé)? '
    )
    dados['dor_base_5o_meta'] = sn(
        '  Dor à palpação no osso navicular (dorso medial do pé)? '
    )

    dados['ottawa_positivo'] = any([
        dados['dor_maleolo_posterior_lateral'],
        dados['dor_maleolo_posterior_medial'],
        dados['incapaz_apoio_4_passos'],
        dados['dor_navicular'],
        dados['dor_base_5o_meta'],
    ])

    if dados['ottawa_positivo']:
        print('\n  OTTAWA POSITIVO: RX indicado para excluir fratura.')
    else:
        print('\n  Ottawa negativo: fratura improvável (S ~99%). Prosseguir com tratamento.')

    # Características do entorse
    _bloco('BLOCO 2B — Características do Entorse')
    dados['mecanismo_inversao'] = sn('  Mecanismo de inversão (torção para dentro)? ')
    dados['edema_maleo_lateral'] = sn('  Edema / equimose lateral ao tornozelo? ')
    dados['ja_entorces_previos'] = sn('  Episódios de entorse recorrentes no mesmo tornozelo? ')


def _bloco_localizacao_nao_trauma(dados):
    """Roteador por localização para quadros não-traumáticos."""
    _bloco('BLOCO 2 — Localização da Dor (Sem Trauma)')
    print('  A localização direciona diretamente a hipótese principal.\n')
    print('  1) Calcanhar plantar (sola do pé / calcanhar abaixo)')
    print('     -> Fasciite plantar / esporao de calcâneo')
    print('  2) Posterior ao tornozelo (tendão de Aquiles)')
    print('     -> Tendinopatia de Aquiles / bursite retrocalcânea')
    print('  3) Antepé / espaço entre dedos (queimação 3-4o dedos)')
    print('     -> Neuroma de Morton')
    print('  4) Tornozelo / maléolos (sem trauma)')
    print('     -> Artrite, OA, instabilidade crônica')
    while True:
        op = input('\n  Localização (1/2/3/4): ').strip()
        if op in ('1', '2', '3', '4'):
            break
        print('  Digite 1, 2, 3 ou 4.')
    dados['localizacao_dor'] = {
        '1': 'calcanhar_plantar',
        '2': 'posterior_aquiles',
        '3': 'antepé_morton',
        '4': 'tornozelo_articular',
    }[op]


def _bloco_fasciite(dados):
    _bloco('BLOCO 3A — Fasciite Plantar')
    print('  Dor plantar no calcanhar, pior nos primeiros passos pela manhã.\n')
    dados['dor_primeiro_passo_manha'] = sn('  Dor intensa nos primeiros passos ao levantar pela manhã? ')
    dados['dor_melhora_caminhar']     = sn('  A dor melhora após alguns minutos de caminhada? ')
    dados['dor_piora_fim_dia']        = sn('  Piora novamente ao fim do dia ou após longo período em pé? ')
    dados['uso_calcado_inadequado']   = sn('  Usa calçados sem suporte (chinelo, sapatilha, calcanhar alto)? ')
    dados['sobrepeso_obesidade']      = sn('  Sobrepeso ou obesidade? ')
    dados['atividade_fisica_impacto'] = sn('  Atividade física de impacto (corrida, salto)? ')
    print('\n  Prognóstico: ~75% resolvem em 12 meses com tratamento conservador.')
    print('  Média de resolução: 725 dias (informar o paciente!)')


def _bloco_aquiles(dados):
    _bloco('BLOCO 3B — Tendinopatia de Aquiles')
    print('  Dor 2-6 cm proximal à inserção do tendão (zona de hipovascularização).\n')
    dados['dor_2_6cm_insercao']         = sn('  Dor localizada 2-6 cm acima da inserção no calcâneo? ')
    dados['dor_insercao_calcahar']      = sn('  Dor na própria inserção do tendão no calcâneo? ')
    dados['rigidez_manha_aquiles']      = sn('  Rigidez matinal no tornozelo / calcanhar? ')
    dados['piora_corrida_salto']        = sn('  Piora com corrida, salto ou subida de escadas? ')
    dados['corticosteroide_previo']     = sn('  Infiltração com corticosteroide prévia no tendão? ')
    dados['uso_quinolona']              = sn('  Uso de fluoroquinolona (ciprofloxacino, levofloxacino)? ')

    if dados['corticosteroide_previo']:
        print('\n  ALERTA: Corticosteroide intra-tendinoso: CONTRAINDICADO — risco de ruptura!')
    if dados['uso_quinolona']:
        print('\n  ALERTA: Quinolona associada a tendinopatia/ruptura de Aquiles.')


def _bloco_morton(dados):
    _bloco('BLOCO 3C — Neuroma de Morton')
    print('  Fibrose perineural entre metatarsos — tipicamente 3o-4o espaço.\n')
    dados['queimacao_entre_dedos']   = sn('  Dor em queimação ou formigamento entre o 3o e 4o dedos? ')
    dados['piora_calcado_estreito']  = sn('  Piora com calçados estreitos ou salto alto? ')
    dados['alivio_tirar_calcado']    = sn('  Alívio ao tirar o sapato e massagear o pé? ')
    dados['irradiacao_para_dedos']   = sn('  Irradiação para os dedos adjacentes? ')


def _bloco_tornozelo_articular(dados):
    _bloco('BLOCO 3D — Dor Articular no Tornozelo (Sem Trauma)')
    dados['rigidez_manha']          = sn('  Rigidez matinal > 30 minutos? ')
    dados['edema_bilateral']        = sn('  Edema bilateral ou em múltiplas articulações? ')
    dados['historico_artrite']      = sn('  Histórico de artrite (reumatoide, gotosa, reativa)? ')
    dados['febre_sistemica']        = sn('  Febre associada? ')
    dados['limitacao_adl']          = sn('  Limitação em atividades do dia a dia? ')


# =============================================================================
# SALVAR
# =============================================================================

def salvar_dicionario(dados, pasta='dados_pacientes'):
    os.makedirs(pasta, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome = os.path.join(pasta, f'tornozelo_pe_subjetivo_{timestamp}.json')
    with open(nome, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f'\n  Dicionário salvo em: {nome}')
    return nome


# =============================================================================
# MAIN
# =============================================================================

def coletar_subjetivo_tornozelo_pe(dados_preenchidos=None):
    print('\n' + '='*54)
    print('  SYMPTOPY — Anamnese: Dor no Tornozelo e Pé')
    print('='*54)
    print('  Responda s (sim) ou n (não) para cada pergunta.')

    dados = dados_preenchidos.copy() if dados_preenchidos else {}

    _bloco_identificacao(dados)
    _bloco_roteador_trauma(dados)

    if dados['trauma_recente']:
        _bloco_ottawa(dados)
    else:
        _bloco_localizacao_nao_trauma(dados)
        loc = dados.get('localizacao_dor', '')
        if loc == 'calcanhar_plantar':
            _bloco_fasciite(dados)
        elif loc == 'posterior_aquiles':
            _bloco_aquiles(dados)
        elif loc == 'antepé_morton':
            _bloco_morton(dados)
        elif loc == 'tornozelo_articular':
            _bloco_tornozelo_articular(dados)

    arquivo = salvar_dicionario(dados)
    print('\n  Próximo: objetivo.py (Exame físico do tornozelo/pé)\n')
    return dados, arquivo


if __name__ == '__main__':
    import sys as _sys
    _sys.stdout.reconfigure(encoding='utf-8')
    coletar_subjetivo_tornozelo_pe()
