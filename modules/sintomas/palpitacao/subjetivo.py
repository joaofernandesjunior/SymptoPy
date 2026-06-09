# modules/sintomas/palpitacao/subjetivo.py
# Anamnese dirigida — Palpitação — Adulto
#
# BLOCO 0 — Demográfico (idade, sexo, comorbidades cardíacas)
# BLOCO 1 — Red flags (síncope, dor torácica, dispneia grave, instabilidade)
# BLOCO 2 — Caracterização da palpitação (ritmo percebido, duração, padrão)
# BLOCO 3 — Gatilhos e contexto
# BLOCO 4 — Histórico cardíaco e familiar
# BLOCO 5 — Causas secundárias (tireoide, anemia, ansiedade, fármacos)
# BLOCO 6 — ECG disponível?
# BLOCO 7 — CHA₂DS₂-VASc (ativado só se FA suspeita)
#
# Flags derivadas geradas:
#   sincope_palpitacao, dor_toracica_palpitacao, instabilidade_hemodinamica
#   fa_suspeita, tsv_suspeita, extrassistolia_suspeita
#   wpw_suspeita, qt_longo_suspeito
#   causa_secundaria_suspeita (hipertireoidismo, anemia, ansiedade, farmaco)
#   cha2ds2_score, anticoagulacao_indicada

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


def _escolha(prompt, opcoes):
    for i, (val, label) in enumerate(opcoes, 1):
        print(f'  {i}. {label}')
    while True:
        try:
            idx = int(input(prompt).strip())
            if 1 <= idx <= len(opcoes):
                return opcoes[idx - 1][0]
        except ValueError:
            pass
        print(f'  Digite de 1 a {len(opcoes)}.')


# =============================================================================
# BLOCO 0 — DEMOGRÁFICO
# =============================================================================

def _bloco_demografico(dados):
    _bloco('BLOCO 0 — Dados Demográficos')

    if not dados.get('idade'):
        dados['idade'] = _int('  Idade (anos): ', 18, 120)

    print()
    dados['sexo_feminino'] = _escolha(
        '  Sexo: ',
        [('false', 'Masculino'), ('true', 'Feminino')]
    ) == 'true'

    dados['gestante'] = False
    if dados['sexo_feminino']:
        dados['gestante'] = sn('  Gestante? ')

    # Comorbidades relevantes para FA / arritmia
    dados['cardiopatia_estrutural'] = sn(
        '  Cardiopatia estrutural conhecida? (IC, cardiomiopatia, valvopatia, IAM prévio) '
    )
    dados['has'] = sn('  Hipertensão arterial sistêmica (HAS)? ')
    dados['dm']  = sn('  Diabetes mellitus? ')
    dados['avc_previo'] = sn('  AVC, AIT ou embolia prévia? ')
    dados['doenca_vascular'] = sn(
        '  Doença vascular? (IAM prévio, arteriopatia periférica, placa aórtica) '
    )


# =============================================================================
# BLOCO 1 — RED FLAGS / EMERGÊNCIA
# =============================================================================

def _bloco_red_flags(dados):
    _bloco('BLOCO 1 — Sinais de Alarme')
    print('  (Identificar instabilidade antes de qualquer outra pergunta)\n')

    dados['sincope']            = sn('  Perda de consciência (síncope) durante ou após a palpitação? ')
    dados['presincope']         = sn('  Tontura intensa / "quase desmaio" (pré-síncope)? ')
    dados['dor_toracica']       = sn('  Dor ou pressão no peito associada? ')
    dados['dispneia_grave']     = sn('  Falta de ar intensa / dispneia em repouso? ')
    dados['sudorese_fria']      = sn('  Sudorese fria ou palidez intensa? ')
    dados['confusao_mental']    = sn('  Confusão mental ou rebaixamento de consciência? ')

    # Instabilidade hemodinâmica: qualquer um dos acima
    dados['instabilidade_hemodinamica'] = any([
        dados['sincope'], dados['dispneia_grave'],
        dados['sudorese_fria'], dados['confusao_mental'],
    ])

    dados['sincope_palpitacao']    = dados['sincope']
    dados['dor_toracica_palpitacao'] = dados['dor_toracica']

    if dados['instabilidade_hemodinamica']:
        _alerta('INSTABILIDADE HEMODINÂMICA — conduta de emergência indicada. '
                'Continuar anamnese brevemente e encaminhar PS.')
    elif dados['sincope']:
        _alerta('Síncope + palpitação = alto risco de arritmia grave. '
                'Não liberar sem ECG e avaliação cardiológica.')


# =============================================================================
# BLOCO 2 — CARACTERIZAÇÃO DA PALPITAÇÃO
# =============================================================================

def _bloco_caracterizacao(dados):
    _bloco('BLOCO 2 — Caracterização da Palpitação')

    # Ritmo percebido pelo paciente
    print('  Como o paciente descreve a palpitação?')
    dados['ritmo_percebido'] = _escolha(
        '  Escolha: ',
        [
            ('acelerado_regular',    'Coração acelerado e REGULAR — batimento rápido e constante'),
            ('acelerado_irregular',  'Coração acelerado e IRREGULAR — "bagunçado", descompassado'),
            ('batida_extra',         'Batida EXTRA / flip / "falta um batimento" — depois volta ao normal'),
            ('pausa',                '"Pausa" ou "coração para" por um instante'),
            ('forte_mas_normal',     'Batimento FORTE mas ritmo normal — nota o próprio coração'),
            ('indeterminado',        'Paciente não consegue descrever bem'),
        ]
    )

    # Início e término
    print()
    dados['inicio_subito'] = sn('  Início súbito (de repente, sem aviso)? ')
    dados['termino_subito'] = sn('  Término súbito (para de uma hora para outra)? ')

    # Duração de cada episódio
    print('\n  Duração de cada episódio:')
    dados['duracao_episodio'] = _escolha(
        '  Escolha: ',
        [
            ('segundos',   'Segundos (< 30s)'),
            ('minutos',    'Minutos (1–30 min)'),
            ('horas',      'Horas (> 30 min)'),
            ('persistente', 'Persistente / contínua (está agora ou dura dias)'),
        ]
    )

    # Padrão
    dados['primeiro_episodio'] = sn('  Primeiro episódio na vida? ')
    if not dados['primeiro_episodio']:
        dados['frequencia_episodios'] = _escolha(
            '  Frequência dos episódios: ',
            [
                ('raro',      'Raramente (< 1×/mês)'),
                ('mensal',    'Mensal (1–3×/mês)'),
                ('semanal',   'Semanal ou mais'),
                ('diario',    'Diário ou quase todos os dias'),
            ]
        )
    else:
        dados['frequencia_episodios'] = 'primeiro'

    # Palpitação em repouso vs esforço
    dados['em_repouso']  = sn('  Ocorre em repouso (sem atividade)? ')
    dados['ao_esforco']  = sn('  Piora ou ocorre ao esforço? ')


# =============================================================================
# BLOCO 3 — GATILHOS E CONTEXTO
# =============================================================================

def _bloco_gatilhos(dados):
    _bloco('BLOCO 3 — Gatilhos e Contexto')

    dados['gatilho_cafeina_alcool']  = sn('  Após cafeína, energético ou álcool? ')
    dados['gatilho_estresse']        = sn('  Em situação de estresse / ansiedade intensa / ataque de pânico? ')
    dados['gatilho_pos_refeicao']    = sn('  Após refeições? ')
    dados['gatilho_exercicio']       = sn('  Durante ou imediatamente após exercício físico? ')
    dados['gatilho_decubito']        = sn('  Ao deitar (especialmente sobre o lado esquerdo)? ')

    # Fármacos relevantes
    dados['uso_simpaticomimatico']   = sn(
        '  Uso de salbutamol (bombinha), pseudoefedrina, anfetamina ou outro estimulante? '
    )
    dados['uso_hormonio_tireoidiano'] = sn('  Em uso de levotiroxina (hormônio da tireoide)? ')
    dados['uso_antiarritmico']        = sn('  Em uso de antiarrítmico, digoxina ou antidepressivo tricíclico? ')
    dados['uso_cocaina_estimulante']  = sn('  Uso (mesmo que ocasional) de cocaína, crack ou MDMA? ')


# =============================================================================
# BLOCO 4 — HISTÓRICO CARDÍACO E FAMILIAR
# =============================================================================

def _bloco_historico(dados):
    _bloco('BLOCO 4 — Histórico Cardíaco e Familiar')

    dados['fa_conhecida']     = sn('  FA (fibrilação atrial) já diagnosticada anteriormente? ')
    dados['taquicardia_previa'] = sn('  Taquicardia paroxística supraventricular (TSV) prévia diagnosticada? ')
    dados['ecg_previo_normal'] = sn('  ECG prévio normal (sem alterações)? ')

    dados['morte_subita_familiar'] = sn(
        '  Morte súbita em familiar < 40 anos (pai, mãe, irmão)? '
    )
    dados['cardiomiopatia_familiar'] = sn(
        '  Cardiomiopatia hipertrófica ou síndrome de Brugada na família? '
    )

    if dados['morte_subita_familiar'] or dados['cardiomiopatia_familiar']:
        _alerta('Histórico familiar de morte súbita / cardiopatia hereditária — '
                'encaminhar Cardiologia mesmo sem sintomas graves.')


# =============================================================================
# BLOCO 5 — CAUSAS SECUNDÁRIAS
# =============================================================================

def _bloco_causas_secundarias(dados):
    _bloco('BLOCO 5 — Causas Secundárias')
    print('  (Avaliar hipertireoidismo, anemia, ansiedade, fármacos)\n')

    # Hipertireoidismo
    dados['sintomas_tireoide'] = sn(
        '  Perda de peso, tremor, intolerância ao calor, sudorese excessiva ou diarreia? '
        '(sugestivo de hipertireoidismo) '
    )

    # Anemia
    dados['sintomas_anemia'] = sn(
        '  Palidez, cansaço intenso, fraqueza progressiva, sangramento recente? '
        '(sugestivo de anemia) '
    )

    # Ansiedade / Pânico
    dados['sintomas_ansiedade'] = sn(
        '  Palpitação acompanhada de medo intenso, falta de ar, formigamento, '
        'sensação de morte iminente? (sugestivo de pânico) '
    )

    # Hipoglicemia
    dados['diabetes_ou_insulina'] = dados.get('dm', False) or sn(
        '  Diabético em uso de insulina ou sulfonilureia? '
    )
    dados['sintomas_hipoglicemia'] = False
    if dados['diabetes_ou_insulina']:
        dados['sintomas_hipoglicemia'] = sn(
            '  Tremor, suor frio, confusão junto com a palpitação? (sugestivo de hipoglicemia) '
        )

    # Composite flag
    dados['causa_secundaria_suspeita'] = any([
        dados['sintomas_tireoide'],
        dados['sintomas_anemia'],
        dados['sintomas_ansiedade'],
        dados['sintomas_hipoglicemia'],
        dados['uso_simpaticomimatico'],
        dados['uso_hormonio_tireoidiano'],
        dados['uso_cocaina_estimulante'],
    ])


# =============================================================================
# BLOCO 6 — ECG DISPONÍVEL
# =============================================================================

def _bloco_ecg(dados):
    _bloco('BLOCO 6 — ECG')

    dados['ecg_disponivel'] = sn('  ECG realizado agora (ou resultado disponível)? ')

    if not dados['ecg_disponivel']:
        dados['ecg_ritmo']    = 'desconhecido'
        dados['ecg_fc']       = None
        dados['ecg_fa']       = False
        dados['ecg_wpw']      = False
        dados['ecg_qt_longo'] = False
        dados['ecg_brugada']  = False
        dados['ecg_bve']      = False
        return

    print('\n  Achados no ECG:')
    dados['ecg_ritmo'] = _escolha(
        '  Ritmo: ',
        [
            ('sinusal',    'Sinusal (normal)'),
            ('fa',         'Fibrilação Atrial — ausência de ondas P, RR irregular'),
            ('flutter',    'Flutter Atrial — ondas F em serrilhado, RR regular ou regular/irregular'),
            ('tsv',        'TSV — taquicardia regular de QRS estreito, P retrógrada ou ausente'),
            ('tsv_qrs_largo', 'Taquicardia de QRS largo (TV vs TSV aberrante)'),
            ('wpw',        'Pré-excitação (delta wave) — WPW suspeito'),
            ('extrassist', 'Ritmo sinusal + extrassístoles'),
            ('normal',     'Normal / sinusal sem alterações'),
            ('outro',      'Outro achado'),
        ]
    )

    dados['ecg_fc'] = _int('  FC no ECG (bpm): ', 20, 300)

    dados['ecg_fa']       = dados['ecg_ritmo'] in ('fa', 'flutter')
    dados['ecg_wpw']      = dados['ecg_ritmo'] == 'wpw'
    dados['ecg_tsv_largo'] = dados['ecg_ritmo'] == 'tsv_qrs_largo'

    dados['ecg_qt_longo'] = sn('  QTc prolongado (> 450ms H / > 460ms M)? ')
    dados['ecg_brugada']  = sn('  Padrão Brugada (supra ST tipo 1 em V1-V2)? ')
    dados['ecg_bve']      = sn('  Bloqueio de ramo esquerdo (BRE) novo? ')


# =============================================================================
# BLOCO 7 — CHA₂DS₂-VASc (só se FA suspeita ou confirmada)
# =============================================================================

def _bloco_cha2ds2(dados):
    _bloco('BLOCO 7 — Risco Tromboembólico (CHA₂DS₂-VASc)')
    print('  (Calculado para definir necessidade de anticoagulação na FA)\n')

    score = 0
    idade = dados.get('idade', 0)

    # C — Insuficiência Cardíaca ou FE reduzida
    ic = dados.get('cardiopatia_estrutural', False)
    if ic:
        score += 1
        print('  [+1] Cardiopatia estrutural / IC / FE reduzida')

    # H — HAS
    if dados.get('has'):
        score += 1
        print('  [+1] HAS')

    # A₂ — Idade ≥ 75
    if idade >= 75:
        score += 2
        print('  [+2] Idade ≥ 75 anos')
    elif 65 <= idade < 75:
        score += 1
        print('  [+1] Idade 65–74 anos')

    # D — DM
    if dados.get('dm'):
        score += 1
        print('  [+1] Diabetes mellitus')

    # S₂ — AVC/AIT/embolia prévia
    if dados.get('avc_previo'):
        score += 2
        print('  [+2] AVC / AIT / embolia prévia')

    # V — Doença vascular
    if dados.get('doenca_vascular'):
        score += 1
        print('  [+1] Doença vascular (IAM / arteriopatia / placa aórtica)')

    # Sc — Sexo feminino (só conta se score ≥ 1 por outros critérios)
    sexo_f = dados.get('sexo_feminino', False)
    if sexo_f and score >= 1:
        score += 1
        print('  [+1] Sexo feminino')

    dados['cha2ds2_score'] = score

    # Limiar de anticoagulação
    limiar = 3 if sexo_f else 2
    dados['anticoagulacao_indicada'] = score >= limiar

    # Borderline (Class 2a AHA/ACC 2023): H=1 ou F=2 — considerar anticoag. com base em fatores adicionais
    dados['anticoagulacao_borderline'] = (
        (not sexo_f and score == 1) or (sexo_f and score == 2)
    )

    if dados['anticoagulacao_indicada']:
        _alerta(f'CHA₂DS₂-VASc = {score} → Anticoagulação oral indicada — Class I (DOAC de preferência).')
    elif dados['anticoagulacao_borderline']:
        print(f'\n  CHA₂DS₂-VASc = {score} → Borderline — AHA/ACC 2023 Class 2a: '
              'razoável anticoagular considerando fatores clínicos adicionais '
              '(fragilidade, risco de queda, preferência do paciente).')
    else:
        print(f'\n  CHA₂DS₂-VASc = {score} → Anticoagulação não indicada de rotina.')


# =============================================================================
# FLAGS DERIVADAS
# =============================================================================

def _calcular_flags(dados):
    ritmo = dados.get('ritmo_percebido', '')
    ecg   = dados.get('ecg_ritmo', 'desconhecido')

    # FA suspeita: irregular + persistente/horas, ou ECG confirma
    dados['fa_suspeita'] = (
        dados.get('ecg_fa') or
        (ritmo == 'acelerado_irregular' and
         dados.get('duracao_episodio') in ('horas', 'persistente'))
    )

    # TSV suspeita: acelerado regular + início e fim súbitos
    dados['tsv_suspeita'] = (
        ecg in ('tsv', 'tsv_qrs_largo') or
        (ritmo == 'acelerado_regular' and
         dados.get('inicio_subito') and
         dados.get('termino_subito'))
    )

    # Extrassistolia suspeita
    dados['extrassistolia_suspeita'] = (
        ecg == 'extrassist' or
        ritmo in ('batida_extra', 'pausa')
    )

    # WPW suspeito
    dados['wpw_suspeita'] = dados.get('ecg_wpw', False)

    # QT longo suspeito
    dados['qt_longo_suspeito'] = (
        dados.get('ecg_qt_longo', False) or
        dados.get('uso_antiarritmico', False) and dados.get('sincope')
    )

    # Brugada suspeito
    dados['brugada_suspeito'] = dados.get('ecg_brugada', False)

    # Taquicardia de QRS largo suspeita (TV vs TSV aberrante)
    dados['tv_suspeita'] = (
        dados.get('ecg_tsv_largo', False) or
        (dados.get('cardiopatia_estrutural') and dados.get('tsv_suspeita'))
    )


# =============================================================================
# PONTO DE ENTRADA
# =============================================================================

def coletar_subjetivo_palpitacao(dados_iniciais=None):
    dados = dict(dados_iniciais or {})
    dados.setdefault('_modulo', 'palpitacao')
    dados.setdefault('_data', datetime.now().isoformat())

    _bloco_demografico(dados)
    _bloco_red_flags(dados)
    _bloco_caracterizacao(dados)
    _bloco_gatilhos(dados)
    _bloco_historico(dados)
    _bloco_causas_secundarias(dados)
    _bloco_ecg(dados)

    # CHA₂DS₂-VASc só se FA suspeita/confirmada
    _calcular_flags(dados)
    if dados.get('fa_suspeita') or dados.get('fa_conhecida'):
        _bloco_cha2ds2(dados)

    # Salvar JSON
    pasta = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'dados_sessao')
    os.makedirs(pasta, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    arquivo = os.path.join(pasta, f'palpitacao_{ts}.json')
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    print(f'\n  [Salvo em {arquivo}]')
    return dados, arquivo


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    coletar_subjetivo_palpitacao()
