# modules/sintomas/orl/otalgia_subjetivo.py
# Sintoma-guia: Dor de Ouvido / Otalgia
#
# Cobre: OMA (watchful waiting vs amoxicilina/amox-clav), Otite Externa Aguda,
#        Mastoidite aguda (red flag → PS), DTM leve.
#
# Retorna: (dados: dict, arquivo_json: str)

import json
import os
import sys
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _ask(prompt, opts=None, default=None):
    if opts:
        print(f'\n  {prompt}')
        for i, o in enumerate(opts, 1):
            print(f'    {i}. {o}')
        while True:
            raw = input('  → ').strip()
            if raw == '' and default is not None:
                return default
            if raw.isdigit() and 1 <= int(raw) <= len(opts):
                return opts[int(raw) - 1]
            print(f'  ⚠️  Digite um número de 1 a {len(opts)}.')
    else:
        raw = input(f'\n  {prompt}\n  → ').strip()
        return raw if raw else default


def _sim_nao(prompt, default='nao'):
    raw = input(f'\n  {prompt} (s/n) → ').strip().lower()
    if raw in ('s', 'sim', 'y', 'yes'):
        return True
    if raw in ('n', 'nao', 'não', 'no'):
        return False
    return default == 'sim'


def _input_num(prompt, inteiro=False):
    while True:
        raw = input(f'\n  {prompt}: ').strip()
        try:
            return int(raw) if inteiro else float(raw)
        except ValueError:
            print('  ⚠️  Digite um número.')


# =============================================================================
# COLETA PRINCIPAL
# =============================================================================

def coletar_subjetivo_otalgia(dados_preenchidos: dict = None) -> tuple:
    """
    Coleta anamnese de dor de ouvido / otalgia.
    Retorna (dados: dict, arquivo_json: str).
    """
    dados = dict(dados_preenchidos or {})

    if 'idade' not in dados:
        dados['idade'] = _input_num('Idade do paciente (anos)', inteiro=True)
    if 'sexo' not in dados:
        dados['sexo'] = _ask('Sexo biológico', ['M', 'F'])

    idade = dados['idade']
    crianca = idade < 18
    crianca_pequena = idade < 2  # 0-23 meses

    print('\n' + '=' * 60)
    print('  AVALIAÇÃO — DOR DE OUVIDO / OTALGIA')
    print('=' * 60)

    # ─── BLOCO 1 — Localização e duração ──────────────────────────────────────
    print('\n  [ Bloco 1 — Localização e duração ]')

    dados['lateralidade'] = _ask(
        'Qual ouvido?',
        ['Direito', 'Esquerdo', 'Bilateral'],
    )
    dados['bilateral'] = (dados['lateralidade'] == 'Bilateral')

    dados['duracao_dor'] = _ask(
        'Há quanto tempo está com dor no ouvido?',
        ['< 24 horas', '24–48 horas', '> 48 horas', '> 7 dias'],
    )
    dados['otalgia_mais_48h'] = dados['duracao_dor'] in ('> 48 horas', '> 7 dias')

    # ─── BLOCO 2 — Red flags de Mastoidite (antes de tudo) ────────────────────
    print('\n  [ Bloco 2 — Red flags de Mastoidite ]')
    print('  (Mastoidite = emergência — responda com atenção)')

    dados['dor_retroauricular']   = _sim_nao('Dor ou vermelhidão ATRÁS do ouvido (sobre o osso mastóide)?')
    dados['pavilhao_projetado']   = _sim_nao('Ouvido projetado para frente e para baixo (comparar com o outro)?')
    dados['flutuacao_retroaur']   = _sim_nao('Inchaço / flutuação palpável atrás do ouvido?')

    # ─── BLOCO 3 — Febre ──────────────────────────────────────────────────────
    print('\n  [ Bloco 3 — Febre ]')

    dados['febre'] = _sim_nao('Febre presente (≥ 37,8°C)?')
    if dados['febre']:
        temp_raw = _ask(
            'Temperatura máxima medida:',
            ['< 38°C', '38–38,9°C', '≥ 39°C'],
        )
        dados['temperatura_grau'] = temp_raw
        dados['febre_alta']       = (temp_raw == '≥ 39°C')
        dados['febre_mais_72h_atb'] = False
        if dados.get('dor_retroauricular') or dados.get('pavilhao_projetado'):
            dados['febre_mais_72h_atb'] = _sim_nao(
                'Está em uso de antibiótico há > 72h e a febre persiste?'
            )
    else:
        dados['temperatura_grau']   = 'afebril'
        dados['febre_alta']         = False
        dados['febre_mais_72h_atb'] = False

    # ─── BLOCO 4 — Sintomas otológicos ────────────────────────────────────────
    print('\n  [ Bloco 4 — Sintomas otológicos ]')

    dados['trago_positivo']      = _sim_nao('Dor ao puxar o pavilhão auricular ou pressionar o trago (bico do ouvido)?')
    dados['otorreia']            = _sim_nao('Secreção saindo do ouvido (otorreia)?')
    if dados['otorreia']:
        dados['otorreia_tipo'] = _ask(
            'Tipo de secreção:',
            ['Purulenta (amarela/verde)', 'Aquosa/serosa', 'Sanguinolenta'],
        )
        dados['otorreia_purulenta'] = (dados['otorreia_tipo'] == 'Purulenta (amarela/verde)')
    else:
        dados['otorreia_tipo']      = None
        dados['otorreia_purulenta'] = False

    dados['hipoagusia']       = _sim_nao('Diminuição da audição no ouvido afetado?')
    dados['ouvido_cheio']     = _sim_nao('Sensação de ouvido cheio / entupido / pressão?')
    dados['zumbido_associado'] = _sim_nao('Zumbido associado?')

    # ─── BLOCO 5 — Contexto para OMA vs Otite Externa ─────────────────────────
    print('\n  [ Bloco 5 — Contexto ]')

    dados['iras_recente']     = _sim_nao('Resfriado / gripe / coriza nas últimas 2 semanas?')
    dados['banho_piscina']    = _sim_nao('Banho de piscina, praia ou mergulho recente?')
    dados['uso_cotonete']     = _sim_nao('Uso frequente de cotonete ou tampões de ouvido?')
    dados['diabetes']         = _sim_nao('Diabetes mellitus ou imunodeficiência conhecida?')
    dados['atb_recente_30d']  = _sim_nao('Uso de antibiótico nos últimos 30 dias?')

    # Crianças: contexto específico para OMA
    if crianca:
        print('\n  [ Bloco 5B — Contexto pediátrico ]')
        dados['conjuntivite_purulenta'] = _sim_nao(
            'Conjuntivite purulenta (olho vermelho com secreção) concomitante?'
        )
        dados['oma_recorrente'] = _sim_nao('Histórico de otite média de repetição?')
        dados['seguimento_incerto'] = _sim_nao(
            'Difícil acesso ao retorno em 48–72h (distância, trabalho, etc.)?'
        )
    else:
        dados['conjuntivite_purulenta'] = False
        dados['oma_recorrente']         = False
        dados['seguimento_incerto']     = False

    # ─── BLOCO 6 — Otoscopia (se disponível) ──────────────────────────────────
    print('\n  [ Bloco 6 — Otoscopia ]')
    print('  (Responda com base no otoscópio, se disponível. Se não: marque "Não avaliado")')

    mt_raw = _ask(
        'Membrana timpânica (MT):',
        ['Não avaliada / sem otoscópio', 'Normal (translúcida, côncava)',
         'Hiperemiada (vermelha)', 'Abaulada', 'Com efusão (nível líquido)',
         'Perfurada'],
    )
    dados['mt_status'] = mt_raw
    dados['mt_abaulada']   = ('Abaulada' in mt_raw)
    dados['mt_hiperemia']  = ('Hiperemiada' in mt_raw) or ('Abaulada' in mt_raw)
    dados['mt_perfurada']  = ('Perfurada' in mt_raw)
    dados['mt_efusao']     = ('efusão' in mt_raw)

    canal_raw = _ask(
        'Canal auditivo externo:',
        ['Não avaliado', 'Normal', 'Hiperemiado e edemaciado',
         'Com debris / descamação', 'Muito edemaciado (estenótico)'],
    )
    dados['canal_status']   = canal_raw
    dados['canal_edema']    = ('edema' in canal_raw.lower() or 'Hiperemiado' in canal_raw)
    dados['canal_estenose'] = ('estenótico' in canal_raw)

    # ─── BLOCO 7 — DTM (mandíbula) ────────────────────────────────────────────
    print('\n  [ Bloco 7 — Disfunção da Articulação Temporomandibular (DTM) ]')

    dados['dor_mastigacao']  = _sim_nao('Dor piora ao mastigar ou abrir a boca?')
    dados['dor_matinal']     = _sim_nao('Dor pior ao acordar (melhora ao longo do dia)?')
    dados['bruxismo']        = _sim_nao('Range os dentes durante o sono (bruxismo)?')
    dados['click_mandibula'] = _sim_nao('Estalos ou clicks ao abrir / fechar a boca?')
    dados['limitacao_abertura'] = _sim_nao('Dificuldade para abrir a boca completamente?')
    dados['dor_temporal']    = _sim_nao('Dor irradiada para a têmpora / cabeça?')

    # ─── BLOCO 8 — Intensidade da dor ─────────────────────────────────────────
    print('\n  [ Bloco 8 — Intensidade ]')
    intensidade_raw = _ask(
        'Intensidade da dor no ouvido (geral):',
        ['Leve (incomoda, mas tolera bem)',
         'Moderada (interfere nas atividades)',
         'Intensa (muito difícil de tolerar)'],
    )
    dados['intensidade_dor'] = intensidade_raw
    dados['otalgia_grave']   = ('Intensa' in intensidade_raw)

    # ─── Flags derivadas ──────────────────────────────────────────────────────

    # Mastoidite: dor retroauricular OU pavilhão projetado OU febre persistindo com ATB
    dados['mastoidite_suspeita'] = any([
        dados.get('dor_retroauricular'),
        dados.get('pavilhao_projetado'),
        dados.get('flutuacao_retroaur'),
        dados.get('febre_mais_72h_atb'),
    ])

    # OE: trago positivo OU canal edemaciado (exposição à água, cotonete)
    dados['otite_externa_suspeita'] = (
        dados.get('trago_positivo') or
        dados.get('canal_edema') or
        (dados.get('banho_piscina') and dados.get('otalgia_grave'))
    )

    # OMA: contexto de IRAS + febre/MT alterada/efusão; exclui OE por trago negativo
    dados['oma_suspeita'] = (
        not dados.get('trago_positivo') and
        (
            dados.get('iras_recente') or
            dados.get('ouvido_cheio') or
            dados.get('hipoagusia')
        ) and
        (
            dados.get('febre') or
            dados.get('mt_abaulada') or
            dados.get('mt_hiperemia') or
            dados.get('mt_efusao') or
            dados.get('otorreia_purulenta')
        )
    )

    # OMA — indicação de tratar imediatamente (sem watchful waiting)
    dados['oma_tratar_imediato'] = any([
        idade < 0.5,                                         # < 6 meses
        (crianca_pequena and dados.get('bilateral')),        # bilateral < 2 anos
        dados.get('febre_alta'),                             # ≥ 39°C
        dados.get('otalgia_mais_48h'),                       # otalgia > 48h
        dados.get('otorreia_purulenta'),                     # otorreia
        dados.get('seguimento_incerto'),                     # sem retorno garantido
        dados.get('conjuntivite_purulenta'),                 # conjuntivite + OMA
        dados.get('oma_recorrente') and dados.get('atb_recente_30d'),  # recorrente c/ ATB recente
    ])

    # OE maligna: DM/imuno + canal muito edemaciado/granulação
    dados['oe_maligna_suspeita'] = (
        dados.get('diabetes') and
        (dados.get('canal_estenose') or dados.get('canal_edema')) and
        dados.get('otalgia_grave')
    )

    # DTM: ≥ 2 critérios clínicos
    dtm_criterios = sum([
        dados.get('dor_mastigacao', False),
        dados.get('dor_matinal', False),
        dados.get('bruxismo', False),
        dados.get('click_mandibula', False),
        dados.get('limitacao_abertura', False),
    ])
    dados['dtm_suspeita']    = (dtm_criterios >= 2 and not dados.get('febre'))
    dados['dtm_criterios_n'] = dtm_criterios

    # ─── Salvar JSON ──────────────────────────────────────────────────────────
    os.makedirs('dados_pacientes', exist_ok=True)
    ts  = datetime.now().strftime('%Y%m%d_%H%M%S')
    arq = os.path.join('dados_pacientes', f'otalgia_subjetivo_{ts}.json')
    with open(arq, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    print(f'\n  [Dados salvos: {arq}]')
    return dados, arq


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    dados, arq = coletar_subjetivo_otalgia()
    print(f'\nMastoidite: {dados.get("mastoidite_suspeita")}')
    print(f'OMA: {dados.get("oma_suspeita")} | Tratar imediato: {dados.get("oma_tratar_imediato")}')
    print(f'OE: {dados.get("otite_externa_suspeita")} | Maligna: {dados.get("oe_maligna_suspeita")}')
    print(f'DTM: {dados.get("dtm_suspeita")} ({dados.get("dtm_criterios_n")} critérios)')
