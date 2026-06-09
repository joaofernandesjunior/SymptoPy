# modules/sintomas/sono/subjetivo.py
# Anamnese dirigida — Transtornos do Sono — Adulto
#
# BLOCO 0 — Queixa principal e padrão (tipo: insônia / hipersonia / parassonia / movimentos)
# BLOCO 1 — Caracterização da insônia (início, manutenção, despertar precoce) + duração + ISI
# BLOCO 2 — Causas comportamentais (tela, café, álcool, horários, turno)
# BLOCO 3 — Sintomas noturnos (ronco/apneia → STOP-BANG, ranger dentes, urge pernas, parassonias)
# BLOCO 4 — Sintomas diurnos (Epworth, cataplexia, paralisia, alucinações)
# BLOCO 5 — Contexto clínico (dor, noctúria, psiquiátrico, medicamentos, doenças crônicas)
# BLOCO 6 — Exame físico guiado (IMC, circunferência cervical, Mallampati, masseter/ATM)
#
# Scores gerados:
#   isi_score (0–28), stopbang_score (0–8), epworth_score (0–24)
#   spi_criterios (0–4), narcolepsia_suspeita, bruxismo_suspeita
#   sfas_suspeita, tcr_rem_suspeita, desmame_benzo, parassonia_nrem
#
# Rodar: python -m modules.sintomas.sono.subjetivo

import json
import os
import sys
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from utils.perguntas import sn


# =============================================================================
# AUXILIARES
# =============================================================================

def _bloco(titulo):
    print(f'\n{"─" * 58}')
    print(f'  {titulo}')
    print(f'{"─" * 58}')


def _alerta(msg):
    print(f'\n  ⚠️  {msg}')


def _int(prompt, minimo=0, maximo=999):
    while True:
        try:
            val = int(input(prompt).strip())
            if minimo <= val <= maximo:
                return val
            print(f'  Digite entre {minimo} e {maximo}.')
        except ValueError:
            print('  Digite um número inteiro.')


def _float(prompt):
    while True:
        try:
            return float(input(prompt).strip().replace(',', '.'))
        except ValueError:
            print('  Digite um número (ex: 1.72).')


def _escolha(prompt, opcoes):
    """opcoes = lista de (valor, label)"""
    for i, (_, label) in enumerate(opcoes, 1):
        print(f'  {i}. {label}')
    while True:
        try:
            idx = int(input(prompt).strip())
            if 1 <= idx <= len(opcoes):
                return opcoes[idx - 1][0]
            print(f'  Digite 1–{len(opcoes)}.')
        except ValueError:
            print('  Digite um número.')


def _isi_item(descricao, rotulo):
    """ISI: pergunta 0–4 com escala descrita."""
    print(f'\n  {descricao}')
    print('  0=Nenhuma  1=Leve  2=Moderada  3=Grave  4=Muitíssimo grave')
    return _int(f'  {rotulo}: ', 0, 4)


def _epworth_item(situacao):
    """Epworth: 0=nunca, 1=raramente, 2=às vezes, 3=frequentemente."""
    print(f'  {situacao}')
    print('  0=Nunca  1=Raramente  2=Às vezes  3=Frequentemente')
    return _int('  Chance de cochilar: ', 0, 3)


# =============================================================================
# COLETOR PRINCIPAL
# =============================================================================

def coletar_subjetivo_sono(dados_preenchidos=None):
    sys.stdout.reconfigure(encoding='utf-8')
    dados = dados_preenchidos or {}

    print('\n' + '=' * 58)
    print('  TRANSTORNOS DO SONO — ANAMNESE DIRIGIDA')
    print('=' * 58)

    # ── BLOCO 0: Queixa principal ────────────────────────────────────
    _bloco('BLOCO 0 — Queixa principal')
    dados['queixa_principal'] = _escolha('  Qual é o problema principal? ', [
        ('insonia',       'Dificuldade de dormir (insônia)'),
        ('hipersonia',    'Sono excessivo durante o dia'),
        ('parassonia',    'Comportamento estranho à noite (sonambulismo, pesadelos, movimentos)'),
        ('movimentos',    'Movimentos involuntários nas pernas à noite'),
        ('ronco_apneia',  'Ronco / pausas respiratórias'),
        ('bruxismo',      'Ranger ou apertar dentes à noite'),
        ('misto',         'Mais de um problema'),
    ])

    # ── BLOCO 1: Insônia — tipo + ISI ───────────────────────────────
    _bloco('BLOCO 1 — Caracterização do sono')

    dados['dificuldade_iniciar'] = sn('  Dificuldade de INICIAR o sono (demora > 30 min para adormecer)? ')
    if dados['dificuldade_iniciar']:
        dados['latencia_min'] = _int('  Quanto tempo demora (minutos)? ', 0, 300)
    else:
        dados['latencia_min'] = 0

    dados['dificuldade_manter'] = sn('  Acorda DURANTE a noite e tem dificuldade de voltar a dormir? ')
    if dados['dificuldade_manter']:
        dados['despertares_noite'] = _int('  Quantas vezes acorda por noite em média? ', 0, 20)
    else:
        dados['despertares_noite'] = 0

    dados['despertar_precoce'] = sn('  Acorda muito cedo (2–3h antes do desejado) e não dorme mais? ')

    dados['horas_cama'] = _int('  Quantas horas fica na cama por noite? ', 0, 24)
    dados['horas_sono'] = _int('  Quantas horas realmente dorme? ', 0, 24)

    dados['duracao_semanas'] = _int('  Há quantas semanas isso acontece? ', 0, 520)
    dados['noites_por_semana'] = _int('  Quantas noites por semana são afetadas? ', 0, 7)
    dados['so_em_casa'] = sn('  O problema ocorre SÓ em casa (não em hotéis/outros lugares)? ')

    # ISI — Índice de Gravidade da Insônia
    print('\n  ── Índice de Gravidade da Insônia (ISI) ──')
    print('  Avalie as ÚLTIMAS 2 SEMANAS:')
    isi1 = _isi_item('Gravidade da dificuldade de INICIAR o sono', 'Iniciar')
    isi2 = _isi_item('Gravidade da dificuldade de MANTER o sono', 'Manter')
    isi3 = _isi_item('Gravidade do DESPERTAR PRECOCE', 'Despertar precoce')
    isi4 = _isi_item('Satisfação atual com o sono', 'Insatisfação')
    isi5 = _isi_item('Interferência do sono na vida diária (fadiga, concentração, humor)', 'Interferência')
    isi6 = _isi_item('Quanto o problema de sono é PERCEPTÍVEL pelos outros?', 'Perceptível')
    isi7 = _isi_item('Quanto você está PREOCUPADO/ANGUSTIADO com o problema de sono?', 'Angústia')
    dados['isi_score'] = isi1 + isi2 + isi3 + isi4 + isi5 + isi6 + isi7

    # Fase atrasada — suspeita
    dados['horario_dormir_habitual'] = input('  Que horas costuma adormecer (quando consegue)? Ex: 02:00 → ').strip()
    dados['horario_acordar_habitual'] = input('  Que horas costuma acordar? Ex: 10:00 → ').strip()
    dados['dorme_bem_horario_proprio'] = sn('  Se pudesse escolher o horário livremente, dormiria bem? ')

    # ── BLOCO 2: Causas comportamentais ─────────────────────────────
    _bloco('BLOCO 2 — Fatores comportamentais')
    dados['tela_na_cama'] = sn('  Usa celular/tablet/TV na cama? ')
    if dados['tela_na_cama']:
        dados['tela_horario'] = input('  Até que horas usa tela antes de dormir? Ex: 23:30 → ').strip()
    else:
        dados['tela_horario'] = ''

    dados['cafe_horario'] = input('  Último café/chá/energético do dia (horário)? Ex: 17:00 → ').strip()
    dados['alcool_para_dormir'] = sn('  Usa álcool para ajudar a dormir? ')
    dados['cochilo_diurno']     = sn('  Dorme durante o dia (cochilo)? ')
    if dados['cochilo_diurno']:
        dados['cochilo_duracao_min'] = _int('  Duração do cochilo (minutos)? ', 0, 300)
        dados['cochilo_horario']     = input('  Horário do cochilo? Ex: 14:00 → ').strip()
    else:
        dados['cochilo_duracao_min'] = 0
        dados['cochilo_horario']     = ''

    dados['exercicio_noturno']   = sn('  Faz exercício físico após as 18h? ')
    dados['turno_irregular']     = sn('  Trabalha em turnos ou tem horários muito irregulares? ')
    dados['cama_escritorio']     = sn('  Usa a cama para trabalho, séries ou celular (além de dormir)? ')
    dados['horario_cama_fixo']   = sn('  Tem horário fixo para acordar (incluindo fim de semana)? ')

    # ── BLOCO 3: Sintomas noturnos ───────────────────────────────────
    _bloco('BLOCO 3 — Sintomas noturnos')

    # STOP-BANG
    print('  [STOP-BANG — rastreio de Apneia Obstrutiva do Sono]')
    sb_s = sn('  S — Ronca ALTO (incomoda quem está no quarto)? ')
    sb_t = sn('  T — Sente cansaço / sonolência frequente durante o dia? ')
    sb_o = sn('  O — Alguém observou PAUSAS respiratórias durante o sono? ')
    sb_p = sn('  P — Tem pressão alta (ou trata hipertensão)? ')
    sb_b = dados.get('imc', 0) > 35  # calculado do exame físico — default False por ora
    sb_b_resp = sn('  B — IMC > 35 kg/m²? ')
    sb_b = sb_b_resp
    sb_a = dados.get('idade', 0) > 50
    sb_a_resp = sn('  A — Idade > 50 anos? ')
    sb_a = sb_a_resp
    sb_n = sn('  N — Circunferência de pescoço > 40 cm (F) ou > 43 cm (M)? ')
    sb_g = _escolha('  G — Sexo biológico: ', [('M', 'Masculino'), ('F', 'Feminino')]) == 'M'
    dados['stopbang_score'] = sum([sb_s, sb_t, sb_o, sb_p, sb_b, sb_a, sb_n, sb_g])
    dados['stopbang_itens'] = {
        'ronco': sb_s, 'cansaco': sb_t, 'apneia_obs': sb_o, 'has': sb_p,
        'imc35': sb_b, 'idade50': sb_a, 'pescoco': sb_n, 'masculino': sb_g,
    }
    if dados['stopbang_score'] >= 3:
        _alerta(f'STOP-BANG = {dados["stopbang_score"]}/8 — Alto risco para AOS')

    # Bruxismo
    print('\n  [Bruxismo do sono]')
    dados['ranger_dentes'] = sn('  Parceiro/familiar ouve ranger de dentes à noite? ')
    dados['dor_mandibula_manha'] = sn('  Acorda com dor ou rigidez na mandíbula? ')
    dados['cefaleia_temporal_manha'] = sn('  Cefaleia temporal (têmporas) ao acordar? ')
    dados['desgaste_dentario'] = sn('  Dentista já comentou sobre desgaste dos dentes? ')
    dados['dor_atm'] = sn('  Dor na articulação do maxilar (ATM) ao mastigar? ')
    dados['isrs_em_uso'] = sn('  Usa antidepressivo (ISRS — sertralina, fluoxetina, escitalopram)? ')

    # SPI — Síndrome das Pernas Inquietas
    print('\n  [SPI — Síndrome das Pernas Inquietas]')
    dados['spi_urge_mover']  = sn('  Urge incontrolável de mover as pernas à noite? ')
    dados['spi_piora_repouso'] = sn('  Piora quando está deitado ou sentado (repouso)? ') if dados['spi_urge_mover'] else False
    dados['spi_melhora_movimento'] = sn('  Melhora ao se levantar e andar? ') if dados['spi_urge_mover'] else False
    dados['spi_piora_noite'] = sn('  Piora predominantemente à noite ou ao final do dia? ') if dados['spi_urge_mover'] else False
    dados['spi_criterios'] = sum([
        dados['spi_urge_mover'], dados['spi_piora_repouso'],
        dados['spi_melhora_movimento'], dados['spi_piora_noite'],
    ])

    # Parassonias
    print('\n  [Parassonias]')
    dados['sonambulismo']       = sn('  Já andou dormindo ou fez coisas sem acordar? ')
    dados['terror_noturno']     = sn('  Episódios de grito/agitação intensa sem acordar (parceiro relata)? ')
    dados['pesadelos_freq']     = sn('  Pesadelos frequentes que acordam e lembra do conteúdo? ')
    dados['pesadelos_trauma']   = sn('  Pesadelos relacionados a evento traumático? ') if dados['pesadelos_freq'] else False
    dados['tcr_rem_age_sonhos'] = sn('  Parceiro relata chutes, socos ou gritos agindo os sonhos? ')
    if dados['tcr_rem_age_sonhos']:
        dados['idade_tcr'] = _int('  Idade atual do paciente (para avaliar risco pré-Parkinson): ', 18, 110)
    else:
        dados['idade_tcr'] = 0

    # ── BLOCO 4: Sintomas diurnos + Narcolepsia ──────────────────────
    _bloco('BLOCO 4 — Sintomas diurnos')

    # Epworth
    print('  [Escala de Epworth — chance de cochilar em cada situação]')
    ep_items = [
        'Sentado lendo',
        'Assistindo TV',
        'Sentado inativo em lugar público (cinema, reunião)',
        'Como passageiro em carro por 1h sem parada',
        'Deitado para descansar à tarde',
        'Sentado conversando com alguém',
        'Sentado após almoço sem álcool',
        'Em carro, parado no trânsito por alguns minutos',
    ]
    epworth_total = sum(_epworth_item(item) for item in ep_items)
    dados['epworth_score'] = epworth_total
    if epworth_total >= 10:
        _alerta(f'Epworth = {epworth_total}/24 — Sonolência diurna significativa')

    # Narcolepsia
    print('\n  [Rastreio de Narcolepsia]')
    dados['cataplexia']          = sn('  Já teve perda súbita de força muscular desencadeada por emoção (riso, susto)? ')
    dados['alucinacao_adormecer']= sn('  Alucinações vívidas AO ADORMECER (hipnagógicas)? ')
    dados['paralisia_sono']      = sn('  Acorda sem conseguir mover (paralisia do sono)? ')
    dados['sono_diurno_irresistivel'] = sn('  Ataques de sono irresistíveis durante o dia (mesmo em locais inadequados)? ')

    # ── BLOCO 5: Contexto clínico ────────────────────────────────────
    _bloco('BLOCO 5 — Contexto clínico')
    dados['dor_cronica_noturna']  = sn('  Dor crônica que piora à noite e interfere no sono? ')
    dados['nocturia']             = sn('  Acorda para urinar? ')
    if dados['nocturia']:
        dados['nocturia_vezes'] = _int('  Quantas vezes por noite? ', 1, 10)
    else:
        dados['nocturia_vezes'] = 0

    dados['depressao_ansiedade']  = sn('  Tem diagnóstico ou suspeita de depressão ou ansiedade? ')
    dados['phq2_humor']           = _int('  PHQ-2: Pouco interesse/prazer nas coisas? (0=nunca, 3=quase todo dia) ', 0, 3)
    dados['phq2_deprimido']       = _int('  PHQ-2: Sentiu-se para baixo/deprimido/sem esperança? (0–3) ', 0, 3)
    dados['phq2_score']           = dados['phq2_humor'] + dados['phq2_deprimido']

    dados['benzo_em_uso']         = sn('  Usa benzodiazepínico ou zolpidem para dormir atualmente? ')
    if dados['benzo_em_uso']:
        dados['benzo_qual']       = input('  Qual medicamento? ').strip()
        dados['benzo_dose']       = input('  Dose? ').strip()
        dados['benzo_semanas']    = _int('  Há quantas semanas usa? ', 1, 520)
    else:
        dados['benzo_qual']  = ''
        dados['benzo_dose']  = ''
        dados['benzo_semanas'] = 0

    dados['medicamentos_sono_atrapalham'] = sn(
        '  Usa corticoide, betabloqueador, estimulante ou diurético? (podem piorar sono) '
    )
    dados['hipotireoidismo']      = sn('  Tem hipotireoidismo ou não sabe se tem? ')
    dados['tsh_disponivel']       = sn('  TSH disponível? ')
    dados['tsh_valor']            = _float('  TSH (mUI/L): ') if dados['tsh_disponivel'] else None
    dados['ferritina_disponivel'] = sn('  Ferritina disponível (relevante para SPI)? ')
    dados['ferritina_valor']      = _float('  Ferritina (ng/mL): ') if dados['ferritina_disponivel'] else None

    # ── BLOCO 6: Exame físico guiado ────────────────────────────────
    _bloco('BLOCO 6 — Exame físico dirigido')
    dados['peso_kg']    = _float('  Peso (kg): ')
    dados['altura_m']   = _float('  Altura (m): ')
    dados['imc']        = round(dados['peso_kg'] / (dados['altura_m'] ** 2), 1)
    print(f'  IMC calculado: {dados["imc"]} kg/m²')

    dados['circunferencia_cervical_cm'] = _float('  Circunferência cervical (cm): ')
    dados['mallampati'] = _int('  Mallampati (1–4, 0=não avaliado): ', 0, 4)
    dados['masseter_hipertrofia'] = sn('  Hipertrofia de masseter visível/palpável? ')
    dados['atm_dor_palpacao']    = sn('  Dor à palpação da ATM? ')
    dados['abertura_bucal_mm']   = _int('  Abertura bucal máxima (mm, normal > 40): ', 0, 80)
    dados['desgaste_incisal']    = sn('  Desgaste nas superfícies incisais/cúspides? ')

    # ── Salvar ───────────────────────────────────────────────────────
    ts    = datetime.now().strftime('%Y%m%d_%H%M%S')
    pasta = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'dados_pacientes')
    os.makedirs(pasta, exist_ok=True)
    arquivo = os.path.join(pasta, f'sono_{ts}.json')
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    print(f'\n  [Dados salvos: {arquivo}]')
    print(f'  ISI: {dados["isi_score"]}/28  |  STOP-BANG: {dados["stopbang_score"]}/8  |  Epworth: {dados["epworth_score"]}/24')
    return dados, arquivo


if __name__ == '__main__':
    coletar_subjetivo_sono()
