# modules/sintomas/musculoesqueletico/fibromialgia/subjetivo.py
# Anamnese de Fibromialgia / Dor Crônica Difusa — ACR 2016
# Rodar da raiz: python -m modules.sintomas.musculoesqueletico.fibromialgia.subjetivo

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


def perguntar_0_3(rotulo):
    """Escala 0–3: 0=Nenhum, 1=Leve, 2=Moderado, 3=Grave."""
    print(f'\n  {rotulo}')
    print('  0) Nenhum   1) Leve   2) Moderado   3) Grave')
    while True:
        try:
            val = int(input('  Opção (0–3): ').strip())
            if 0 <= val <= 3:
                return val
            print('  Digite 0, 1, 2 ou 3.')
        except ValueError:
            print('  Digite 0, 1, 2 ou 3.')


# =============================================================================
# BLOCOS
# =============================================================================

def _bloco_identificacao(dados):
    _bloco('IDENTIFICAÇÃO')
    if isinstance(dados.get('idade'), int) and dados['idade'] > 0:
        print(f'  Idade: {dados["idade"]} anos (herdada da identificação do paciente)')
    else:
        dados['idade'] = perguntar_int('  Idade do paciente: ', 0, 120)

    while True:
        eva = perguntar_int('  EVA de dor global (0–10): ', 0, 10)
        break
    dados['eva_dor'] = eva


def _bloco_wpi(dados):
    _bloco('BLOCO 1 — WPI: Índice de Dor Difusa (ACR 2016)')
    print('  Marque s para cada área com dor nos ÚLTIMOS 3 MESES.\n')

    print('  ── Membro Superior Esquerdo ──────────────────────────')
    dados['ombro_esquerdo']     = sn('  Ombro esquerdo? ')
    dados['braco_esquerdo_sup'] = sn('  Braço esq. superior (ombro → cotovelo)? ')
    dados['braco_esquerdo_inf'] = sn('  Braço esq. inferior (cotovelo → punho)? ')
    dados['mao_punho_esquerdo'] = sn('  Mão / punho esquerdo? ')

    print('\n  ── Membro Superior Direito ───────────────────────────')
    dados['ombro_direito']      = sn('  Ombro direito? ')
    dados['braco_direito_sup']  = sn('  Braço dir. superior? ')
    dados['braco_direito_inf']  = sn('  Braço dir. inferior? ')
    dados['mao_punho_direito']  = sn('  Mão / punho direito? ')

    print('\n  ── Membro Inferior Esquerdo ──────────────────────────')
    dados['quadril_nadega_esquerdo'] = sn('  Quadril / nádega esquerda? ')
    dados['coxa_esquerda']           = sn('  Coxa esquerda? ')
    dados['perna_esquerda']          = sn('  Perna esquerda (joelho → tornozelo)? ')
    dados['tornozelo_pe_esquerdo']   = sn('  Tornozelo / pé esquerdo? ')

    print('\n  ── Membro Inferior Direito ───────────────────────────')
    dados['quadril_nadega_direito'] = sn('  Quadril / nádega direito? ')
    dados['coxa_direita']           = sn('  Coxa direita? ')
    dados['perna_direita']          = sn('  Perna direita? ')
    dados['tornozelo_pe_direito']   = sn('  Tornozelo / pé direito? ')

    print('\n  ── Região Axial ──────────────────────────────────────')
    dados['pescoco']        = sn('  Pescoço / cervical? ')
    dados['dorso_superior'] = sn('  Dorso superior / escapular? ')
    dados['lombar']         = sn('  Lombar? ')
    dados['torax']          = sn('  Tórax / região anterior do peito? ')
    dados['abdome']         = sn('  Abdome? ')

    print('\n  ── Regiões Extra (contam no WPI total, não no critério de regiões) ──')
    dados['mandibula_esquerda'] = sn('  Mandíbula / ATM esquerda? ')
    dados['mandibula_direita']  = sn('  Mandíbula / ATM direita? ')


def _bloco_sss(dados):
    _bloco('BLOCO 2 — SSS: Escala de Gravidade de Sintomas')

    print('  Parte 1 — Gravidade nas ÚLTIMAS 2 SEMANAS')
    dados['sss_fadiga']    = perguntar_0_3('Fadiga / cansaço:')
    dados['sss_sono']      = perguntar_0_3('Sono não-reparador (acorda sem descansar):')
    dados['sss_cognitivo'] = perguntar_0_3('Sintomas cognitivos (memória / concentração):')

    print('\n  Parte 2 — Presença de sintomas somáticos adicionais (últimas semanas)')
    dados['sss_cefaleia']      = sn('  Cefaleia frequente? ')
    dados['sss_dor_abdominal'] = sn('  Dor abdominal ou cólica? ')
    dados['sss_depressao']     = sn('  Humor deprimido / depressão? ')


def _bloco_criterios_exclusao(dados):
    _bloco('BLOCO 3 — Critério de Tempo e Exclusão')
    dados['duracao_sintomas_3_meses']     = sn(
        '  Esses sintomas difusos estão presentes há pelo menos 3 meses? '
    )
    dados['flags_inflamatorios_exclusao'] = sn(
        '  Sinais sugestivos de causa secundária?\n'
        '  (febre, perda de peso, sinovite franca, eritema/calor articular) '
    )

    _bloco('BLOCO 4 — Sintoma Predominante')
    print('  Qual sintoma mais impacta sua qualidade de vida hoje?\n')
    print('  1) Dor  (intensidade e distribuição)')
    print('  2) Fadiga  (cansaço persistente)')
    print('  3) Sono não-reparador')
    print('  4) Humor / Depressão')
    while True:
        op = input('  Opção (1–4): ').strip()
        if op in ('1', '2', '3', '4'):
            break
        print('  Digite 1, 2, 3 ou 4.')
    dados['sintoma_predominante'] = {'1': 'dor', '2': 'fadiga', '3': 'sono', '4': 'humor'}[op]


# =============================================================================
# SALVAR
# =============================================================================

def salvar_dicionario(dados, pasta='dados_pacientes'):
    os.makedirs(pasta, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome = os.path.join(pasta, f'fibromialgia_subjetivo_{timestamp}.json')
    with open(nome, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f'\n  ✅ Dicionário salvo em: {nome}')
    return nome


# =============================================================================
# MAIN
# =============================================================================

def coletar_subjetivo_fibromialgia(dados_preenchidos=None):
    print('\n' + '='*54)
    print('  SYMPTOPY — Fibromialgia / Dor Crônica Difusa')
    print('  Critérios ACR 2016 | JAMA 2021 | EULAR | Cochrane 2025')
    print('='*54)
    print('  Responda s (sim) ou n (não) para cada pergunta.')

    dados = dados_preenchidos.copy() if dados_preenchidos else {}

    _bloco_identificacao(dados)
    _bloco_wpi(dados)
    _bloco_sss(dados)
    _bloco_criterios_exclusao(dados)

    arquivo = salvar_dicionario(dados)
    return dados, arquivo


if __name__ == '__main__':
    coletar_subjetivo_fibromialgia()
