# modules/sintomas/fadiga/subjetivo.py
# Anamnese — Fadiga Crônica
#
# Sequência de blocos:
#   0. Caracterização geral (duração, onset, redução de atividade)
#   1. Red flags clínicos (7 flags)
#   2. Painel laboratorial (exit strategy)
#   3. PEM — mal-estar pós-esforço (critério central ME/SFC)
#   4. Sono
#   5. Cognitivo e ortostase
#   6. STOP-BANG (8 itens — AAFP 2022)
#   7. Humor — PHQ-2 + GAD-2 (AAFP 2023)
#
# Rodar da raiz: python -m modules.sintomas.fadiga.subjetivo

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
    print(f'\n{"─"*54}')
    print(f'  {titulo}')
    print(f'{"─"*54}')


def _perg_float(prompt):
    while True:
        try:
            return float(input(prompt).strip().replace(',', '.'))
        except ValueError:
            print('  Digite um número (ex: 12.5).')


def _perg_int(prompt, minimo=0, maximo=9999):
    while True:
        try:
            val = int(input(prompt).strip())
            if minimo <= val <= maximo:
                return val
            print(f'  Digite um valor entre {minimo} e {maximo}.')
        except ValueError:
            print('  Digite um número inteiro.')


def _perg_escala(prompt, minimo=0, maximo=3):
    """Escala numérica com validação (usado para PHQ-2/GAD-2, 0–3 cada)."""
    while True:
        try:
            val = int(input(prompt).strip())
            if minimo <= val <= maximo:
                return val
            print(f'  Digite um número de {minimo} a {maximo}.')
        except ValueError:
            print('  Digite um número inteiro.')


# =============================================================================
# BLOCO 0 — CARACTERIZAÇÃO GERAL
# =============================================================================

def _bloco_caracterizacao(dados):
    _bloco('BLOCO 0 — Caracterização da Fadiga')
    print('  "Fadiga" = cansaço persistente que não melhora com repouso.\n')

    dados['duracao_meses'] = _perg_int(
        '  Duração da fadiga (em meses): ', 0, 360
    )
    dados['fadiga_nova_onset'] = sn(
        '  Início definido (a fadiga começou em determinado momento, não é lifelong)? '
    )
    dados['reducao_atividade_substancial'] = sn(
        '  Redução substancial (≥50%) nas atividades habituais (trabalho, escola, vida social)? '
    )
    dados['inicio_pos_infeccao'] = sn(
        '  A fadiga começou após uma infecção (gripe, COVID-19, mononucleose)? '
    )

    # Peso — usado tanto para red flag quanto para STOP-BANG
    dados['perda_peso_involuntaria'] = sn('  Perda de peso involuntária? ')
    if dados['perda_peso_involuntaria']:
        dados['perda_peso_pct'] = _perg_float(
            '  Percentual de perda em relação ao peso habitual (ex: 6.5 para 6,5%): '
        )
    else:
        dados['perda_peso_pct'] = 0.0


# =============================================================================
# BLOCO 1 — RED FLAGS
# =============================================================================

def _bloco_red_flags(dados):
    _bloco('BLOCO 1 — Red Flags')
    print('  Presença de qualquer item redireciona para investigação urgente.\n')

    # perda_peso_involuntaria já coletado no bloco 0
    dados['febre_persistente']       = sn('  Febre persistente ou recorrente sem foco claro? ')
    dados['linfadenopatia_fixa']     = sn('  Linfonodo endurecido, fixo ou > 2 cm? ')
    dados['deficit_neurologico_focal'] = sn(
        '  Déficit neurológico focal (fraqueza assimétrica, parestesia localizada, ataxia)? '
    )
    dados['dor_toracica_esforco']    = sn('  Dor torácica ao esforço ou dispneia progressiva? ')
    dados['hepatoesplenomegalia']    = sn('  Hepatoesplenomegalia ao exame físico? ')
    dados['ideacao_suicida_ativa']   = sn('  Ideação suicida ativa? ')

    # Alertas imediatos ao clínico
    flags_urgentes = [k for k in (
        'ideacao_suicida_ativa', 'deficit_neurologico_focal', 'dor_toracica_esforco'
    ) if dados.get(k)]
    if flags_urgentes:
        print('\n  ALERTA IMEDIATO — ação urgente necessária antes de prosseguir.')


# =============================================================================
# BLOCO 2 — PAINEL LABORATORIAL
# =============================================================================

def _bloco_laboratorial(dados):
    _bloco('BLOCO 2 — Painel Laboratorial (Exit Strategy)')
    print('  Preencha os resultados disponíveis. Deixe em branco (Enter) se não realizado.')
    print('  Painel recomendado: CBC, Ferritina, TSH, HbA1c, Glicemia, Cr, ALT/AST, PCR')
    print('  (NICE 2021 / AAFP 2023 — Grau D)\n')

    dados['labs_disponiveis'] = sn('  Exames laboratoriais disponíveis para análise? ')
    if not dados['labs_disponiveis']:
        dados['sexo_feminino'] = sn('  Paciente do sexo feminino? ')
        return

    dados['sexo_feminino'] = sn('  Paciente do sexo feminino (para corte de Hb)? ')

    def _lab_float(prompt):
        raw = input(prompt).strip().replace(',', '.')
        if raw == '':
            return None
        try:
            return float(raw)
        except ValueError:
            return None

    print()
    dados['hemoglobina']    = _lab_float('  Hemoglobina (g/dL) — Enter para pular: ')
    dados['ferritina']      = _lab_float('  Ferritina (ng/mL) — Enter para pular: ')
    dados['tsh']            = _lab_float('  TSH (mIU/L) — Enter para pular: ')
    dados['hba1c']          = _lab_float('  HbA1c (%) — Enter para pular: ')
    dados['glicemia_jejum'] = _lab_float('  Glicemia de jejum (mg/dL) — Enter para pular: ')
    dados['creatinina']     = _lab_float('  Creatinina (mg/dL) — Enter para pular: ')
    dados['alt']            = _lab_float('  ALT (U/L) — Enter para pular: ')


# =============================================================================
# BLOCO 3 — PEM (Mal-Estar Pós-Esforço) — critério central IOM 2015
# =============================================================================

def _bloco_pem(dados):
    _bloco('BLOCO 3 — PEM: Mal-Estar Pós-Esforço (IOM 2015 — Critério Central)')
    print('  PEM = piora dos sintomas após esforço físico ou cognitivo mínimo.')
    print('  O crash pode ocorrer 12–72h APÓS o esforço (retardado — não imediato).\n')

    dados['pem_presente'] = sn(
        '  Ocorre piora significativa após esforço mínimo (físico ou mental)? '
    )
    if dados['pem_presente']:
        dados['pem_delay_horas'] = sn(
            '  A piora ocorre com atraso (horas após o esforço, não imediatamente)? '
        )
        dados['pem_dias_recuperacao'] = _perg_int(
            '  Dias necessários para recuperação após um crash: ', 0, 30
        )
        dados['pem_pior_cognitivo']   = sn(
            '  PEM também desencadeado por esforço cognitivo (ler, conversar, tela)? '
        )
    else:
        dados['pem_delay_horas']      = False
        dados['pem_dias_recuperacao'] = 0
        dados['pem_pior_cognitivo']   = False


# =============================================================================
# BLOCO 4 — SONO
# =============================================================================

def _bloco_sono(dados):
    _bloco('BLOCO 4 — Sono')
    print('  Sono não-reparador é critério central IOM 2015 (distinto de insônia).\n')

    dados['sono_nao_reparador'] = sn(
        '  Acorda cansado mesmo após horas adequadas de sono (sono não-reparador)? '
    )
    dados['insonia']            = sn('  Dificuldade para iniciar ou manter o sono? ')
    dados['hipersonia']         = sn('  Sonolência excessiva durante o dia? ')


# =============================================================================
# BLOCO 5 — COGNITIVO E ORTOSTASE
# =============================================================================

def _bloco_cognitivo_ortostase(dados):
    _bloco('BLOCO 5 — Brain Fog e Intolerância Ortostática (IOM 2015 — Critério Adicional)')
    print('  Pelo menos 1 dos 2 itens é obrigatório para fechar critérios IOM.\n')

    dados['brain_fog'] = sn(
        '  Brain fog — comprometimento cognitivo (dificuldade de concentração, memória, processamento)? '
    )
    dados['intolerancia_ortostatica'] = sn(
        '  Intolerância ortostática — piora dos sintomas de pé (tontura, palpitações, fraqueza)? '
    )

    if dados['brain_fog']:
        dados['brain_fog_piora_esforco'] = sn(
            '  O brain fog piora após esforço cognitivo (leitura, conversa, tela)? '
        )
    else:
        dados['brain_fog_piora_esforco'] = False

    if dados['intolerancia_ortostatica']:
        dados['taquicardia_ortostase'] = sn(
            '  Taquicardia ao ficar de pé (palpitações, coração acelerado ao levantar)? '
        )
    else:
        dados['taquicardia_ortostase'] = False


# =============================================================================
# BLOCO 6 — STOP-BANG (Apneia Obstrutiva do Sono)
# =============================================================================

def _bloco_stopbang(dados):
    _bloco('BLOCO 6 — STOP-BANG (Triagem para Apneia Obstrutiva do Sono)')
    print('  Score 0–8: 0–2 baixo risco | 3–4 intermediário | ≥5 alto risco (AOS)')
    print('  (AAFP 2022 — Grau B)\n')

    dados['sb_ronco']           = sn('  S — Ronco alto (audível a distância)? ')
    dados['sb_cansaco_diurno']  = sn('  T — Cansaço/sonolência diurna frequente? ')
    dados['sb_apneia_observada']= sn('  O — Alguém observou paradas respiratórias durante o sono? ')
    dados['sb_pressao_alta']    = sn('  P — Pressão arterial alta (HAS diagnosticada)? ')
    dados['sb_imc_35']          = sn('  B — IMC > 35 kg/m²? ')
    dados['sb_idade_50']        = sn('  A — Idade > 50 anos? ')
    dados['sb_pescoco_40']      = sn('  N — Circunferência cervical > 40 cm? ')
    dados['sb_masculino']       = sn('  G — Sexo masculino? ')

    dados['stopbang_total'] = sum([
        bool(dados['sb_ronco']),
        bool(dados['sb_cansaco_diurno']),
        bool(dados['sb_apneia_observada']),
        bool(dados['sb_pressao_alta']),
        bool(dados['sb_imc_35']),
        bool(dados['sb_idade_50']),
        bool(dados['sb_pescoco_40']),
        bool(dados['sb_masculino']),
    ])

    risco = (
        'ALTO' if dados['stopbang_total'] >= 5
        else 'INTERMEDIÁRIO' if dados['stopbang_total'] >= 3
        else 'BAIXO'
    )
    print(f'\n  STOP-BANG = {dados["stopbang_total"]}/8 — Risco {risco}')


# =============================================================================
# BLOCO 7 — HUMOR (PHQ-2 + GAD-2)
# =============================================================================

def _bloco_humor(dados):
    _bloco('BLOCO 7 — Triagem de Humor (PHQ-2 / GAD-2)')
    print('  Nas últimas 2 semanas, com que frequência o paciente foi incomodado por:')
    print('  0 = Nenhum dia | 1 = Vários dias | 2 = Mais da metade dos dias | 3 = Quase todo dia')
    print('  PHQ-2 ≥ 3 → triagem POSITIVA para depressão (AAFP 2023 — Grau A)')
    print('  GAD-2 ≥ 3 → triagem POSITIVA para ansiedade  (AAFP 2023 — Grau A)\n')

    dados['phq2_1'] = _perg_escala(
        '  PHQ-2 item 1 — Pouco interesse ou prazer em fazer as coisas (0–3): '
    )
    dados['phq2_2'] = _perg_escala(
        '  PHQ-2 item 2 — Sentir-se deprimido, sem esperança (0–3): '
    )
    dados['phq2_total'] = dados['phq2_1'] + dados['phq2_2']

    dados['gad2_1'] = _perg_escala(
        '  GAD-2 item 1 — Sentir-se nervoso, ansioso ou no limite (0–3): '
    )
    dados['gad2_2'] = _perg_escala(
        '  GAD-2 item 2 — Não conseguir parar de se preocupar (0–3): '
    )
    dados['gad2_total'] = dados['gad2_1'] + dados['gad2_2']

    if dados['phq2_total'] >= 3:
        print(f'\n  PHQ-2 = {dados["phq2_total"]}/6 — POSITIVO para depressão → aplicar PHQ-9 completo')
    if dados['gad2_total'] >= 3:
        print(f'  GAD-2 = {dados["gad2_total"]}/6 — POSITIVO para ansiedade → aplicar GAD-7 completo')


# =============================================================================
# SALVAR
# =============================================================================

def _salvar(dados, pasta='dados_pacientes'):
    os.makedirs(pasta, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome = os.path.join(pasta, f'fadiga_subjetivo_{timestamp}.json')
    with open(nome, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f'\n  Dicionário salvo em: {nome}')
    return nome


# =============================================================================
# MAIN
# =============================================================================

def coletar_subjetivo_fadiga(dados_preenchidos=None):
    print('\n' + '=' * 54)
    print('  SYMPTOPY — Anamnese: Fadiga Crônica')
    print('=' * 54)
    print('  Responda s (sim) ou n (não) para cada pergunta.')
    print('  Escalas numéricas: digite o número e pressione Enter.\n')

    dados = dados_preenchidos.copy() if dados_preenchidos else {}

    _bloco_caracterizacao(dados)
    _bloco_red_flags(dados)
    _bloco_laboratorial(dados)
    _bloco_pem(dados)
    _bloco_sono(dados)
    _bloco_cognitivo_ortostase(dados)
    _bloco_stopbang(dados)
    _bloco_humor(dados)

    arquivo = _salvar(dados)
    print('\n  Próximo: engine_fadiga.py → raciocínio clínico\n')
    return dados, arquivo


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    coletar_subjetivo_fadiga()
