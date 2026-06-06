# modules/raciocinio/palpitacao/engine_palpitacao.py
# Motor de raciocínio clínico — Palpitação — Adulto
#
# Hierarquia STEP:
#   STEP 1  Instabilidade hemodinâmica / Síncope + arritmia grave
#   STEP 1  WPW (delta wave) → NUNCA verapamil/digoxina
#   STEP 1  Taquicardia QRS largo (TV vs TSV aberrante) → PS
#   STEP 1  Brugada + síncope / QT longo + síncope → PS
#   STEP 2  Flutter atrial → Cardio urgente
#   STEP 2  FA nova < 48h elegível → cardioversão química (Propafenona)
#   STEP 2  FA nova não elegível → controle FC + anticoag
#   STEP 2  FA crônica → Metoprolol + DOAC se CHA₂DS₂-VASc indicado
#   STEP 2  TSV paroxística → Valsalva + Metoprolol profilático
#   STEP 3  Extrassistolia benigna → ECG + Holter + tranquilizar
#   STEP 3  Causa secundária → hipertireoidismo / anemia / ansiedade / fármaco
#   STEP 3  Inespecífico → Holter 24h eletivo
#
# Fontes:
#   - AHA/ACC/HRS 2023 Guideline for Diagnosis and Management of Atrial Fibrillation
#   - SBC Diretriz de Arritmias Cardíacas 2023
#   - AHA/ACC Guideline on Management of Patients with SVT 2015 (reafirmado 2023)
#   - ESC Guidelines for the Management of Ventricular Arrhythmias 2022
#   - Flecainide/Propafenone pill-in-the-pocket: Alboni et al. NEJM 2004
#   - Open Evidence 2024


# =============================================================================
# HELPERS
# =============================================================================

def _rx(linha, medicamento, prescricoes, nota=None):
    return {'linha': linha, 'medicamento': medicamento,
            'prescricoes': prescricoes, 'nota': nota}


def _p(quantidade, unidade, posologia):
    return {'quantidade': quantidade, 'unidade': unidade, 'posologia': posologia}


def _achados(dados) -> list:
    a = []
    ritmo = dados.get('ritmo_percebido', '')
    ecg   = dados.get('ecg_ritmo', 'desconhecido')

    _MAP_RITMO = {
        'acelerado_regular':   'coração acelerado e regular',
        'acelerado_irregular': 'coração acelerado e irregular',
        'batida_extra':        'batida extra / flip',
        'pausa':               'sensação de pausa / coração para',
        'forte_mas_normal':    'batimento forte com ritmo normal',
        'indeterminado':       'palpitação de difícil caracterização',
    }
    if ritmo:
        a.append(_MAP_RITMO.get(ritmo, ritmo))

    if dados.get('instabilidade_hemodinamica'):
        a.append('INSTABILIDADE HEMODINÂMICA')
    if dados.get('sincope'):
        a.append('síncope associada')
    if dados.get('presincope'):
        a.append('pré-síncope')
    if dados.get('dor_toracica'):
        a.append('dor torácica associada')
    if dados.get('dispneia_grave'):
        a.append('dispneia em repouso')
    if dados.get('inicio_subito'):
        a.append('início súbito')
    if dados.get('termino_subito'):
        a.append('término súbito')
    if dados.get('duracao_episodio'):
        _DUR = {
            'segundos':    'duração: segundos',
            'minutos':     'duração: minutos',
            'horas':       'duração: horas',
            'persistente': 'episódio persistente/contínuo',
        }
        a.append(_DUR.get(dados['duracao_episodio'], ''))
    if dados.get('fa_conhecida'):
        a.append('FA conhecida')
    if dados.get('cardiopatia_estrutural'):
        a.append('cardiopatia estrutural')
    if ecg not in ('desconhecido', 'normal', 'sinusal', ''):
        _MAP_ECG = {
            'fa':           'ECG: FA confirmada',
            'flutter':      'ECG: flutter atrial',
            'tsv':          'ECG: TSV (QRS estreito)',
            'tsv_qrs_largo':'ECG: taquicardia QRS largo',
            'wpw':          'ECG: pré-excitação (WPW)',
            'extrassist':   'ECG: extrassístoles',
            'outro':        'ECG: outro achado',
        }
        if ecg in _MAP_ECG:
            a.append(_MAP_ECG[ecg])
    if dados.get('ecg_qt_longo'):
        a.append('QTc prolongado')
    if dados.get('ecg_brugada'):
        a.append('padrão Brugada')
    if dados.get('ecg_bve'):
        a.append('BRE novo')
    if dados.get('morte_subita_familiar'):
        a.append('história familiar de morte súbita')
    return [x for x in a if x]


def _score_str(dados) -> str:
    score = dados.get('cha2ds2_score')
    if score is None:
        return ''
    sexo_f = dados.get('sexo_feminino', False)
    limiar = 3 if sexo_f else 2
    ind = 'indicada' if score >= limiar else 'não indicada de rotina'
    return f'CHA₂DS₂-VASc = {score} → anticoagulação {ind}'


def _doac_prescricao(dados) -> list:
    """
    Retorna prescrições estruturadas dos DOACs (1ª linha FA não valvar).

    Hierarquia baseada em evidências (real-world, n > 500k + meta-análises 2023):
      1ª linha  — Apixabana: melhor net clinical benefit (HR sangramento major 0.76 vs VKA;
                  80.3% probabilidade de ser o melhor para AVC + 91.3% menor sangramento).
      Alternativo — Rivaroxabana: posologia 1×/dia favorece adesão, mas real-world mostra
                  HR 1.11 de sangramento major vs VKA — inferior à apixabana.
    Fonte: ARISTOTLE, ROCKET-AF, meta-análise multinacional 2022 (n 527.226).
    """
    rxs = []
    rxs.append(_rx(
        'DOAC 1ª linha',
        'Apixabana',
        [_p('60 comprimidos', '5 mg',
            '1 comprimido VO 2×/dia — manhã e noite. '
            'Reduzir para 2,5 mg 2×/dia se ≥2 dos critérios: '
            'idade ≥80 anos, peso ≤60 kg ou creatinina ≥1,5 mg/dL')],
        nota=(
            'Melhor perfil de segurança entre os DOACs (menor risco de sangramento major e '
            'intracraniano). Preferir em ≥75 anos — rivaroxabana nessa faixa etária tem HR de '
            'sangramento ≈1.0 vs VKA (sem benefício), enquanto apixabana mantém HR 0.76. '
            'Monitorar função renal anualmente (ajuste se CrCl < 25 mL/min).'
        ),
    ))
    rxs.append(_rx(
        'DOAC alternativo (posologia 1×/dia — melhor adesão)',
        'Rivaroxabana',
        [_p('30 comprimidos', '20 mg', '1 comprimido VO 1×/dia com a principal refeição')],
        nota=(
            'Opção quando adesão a regime 2×/dia é problema clínico relevante. '
            'Real-world: HR sangramento major 1.11 vs VKA (vs HR 0.76 da apixabana). '
            'Tomar com a principal refeição (biodisponibilidade cai 29% em jejum). '
            'Reduzir para 15 mg/dia se CrCl 15–50 mL/min. Evitar se CrCl < 15 mL/min.'
        ),
    ))
    return rxs


# =============================================================================
# STEP 1 — INSTABILIDADE HEMODINÂMICA
# =============================================================================

def _resultado_instabilidade(dados) -> dict:
    sinais = []
    if dados.get('sincope'):       sinais.append('síncope')
    if dados.get('dispneia_grave'): sinais.append('dispneia grave')
    if dados.get('sudorese_fria'): sinais.append('sudorese fria')
    if dados.get('confusao_mental'): sinais.append('confusão mental')
    if dados.get('dor_toracica'): sinais.append('dor torácica')

    raciocinio = (
        f'Palpitação com instabilidade hemodinâmica ({", ".join(sinais)}). '
        'Paciente instável durante taquiarritmia = indicação de cardioversão elétrica sincronizada emergencial '
        '(independente do ritmo de base). '
        'Protocolo ACLS: O₂, acesso venoso, monitorização contínua (SpO₂, PA, ECG), '
        'desfibrilador disponível. '
        'Não tentar manobras vagais nem antiarrítmicos em paciente instável.'
    )
    return {
        'tipo': 'palpitacao', 'subtipo': 'palpitacao',
        'categoria': 'pal_instabilidade_hemodinamica',
        'diagnostico': 'Taquiarritmia com Instabilidade Hemodinâmica — SAMU/PS Imediato',
        'urgencia': 'emergencia',
        'raciocinio': raciocinio,
        'achados': _achados(dados),
        'red_flags': ['Instabilidade hemodinâmica durante palpitação — cardioversão elétrica emergencial'],
        'exames': [],
        'conduta': [
            'SAMU 192 imediatamente ou transferência monitorada para PS',
            'Não tentar cardioversão química em paciente instável',
            'Oxigênio suplementar + acesso venoso periférico calibroso',
            'ECG 12 derivações se disponível sem atrasar transporte',
        ],
        'prescricoes_estruturadas': [],
        'orientacoes': {},
        'encaminhar': 'SAMU 192 / PS — emergência cardiovascular',
        'retorno': '',
        'dias_atestado': 1,
    }


# =============================================================================
# STEP 1 — WPW (PRÉ-EXCITAÇÃO)
# =============================================================================

def _resultado_wpw(dados) -> dict:
    raciocinio = (
        'ECG com onda delta (pré-excitação) → Síndrome de Wolff-Parkinson-White (WPW). '
        'Na FA associada ao WPW, o impulso pode conduzir pela via acessória com velocidade '
        'muito alta → fibrilação ventricular e morte súbita. '
        'CONTRAINDICAÇÃO ABSOLUTA: Verapamil, Diltiazem e Digoxina — bloqueiam o nó AV mas '
        'não a via acessória → aceleram a condução pela via acessória → FV → PCR. '
        'Conduta: PS para cardioversão elétrica ou Procainamida/Amiodarona IV se estável. '
        'Ablação por cateter é o tratamento definitivo (encaminhamento eletrofisiologia).'
    )
    return {
        'tipo': 'palpitacao', 'subtipo': 'palpitacao',
        'categoria': 'pal_wpw',
        'diagnostico': 'WPW (Pré-Excitação) — PS Urgente',
        'urgencia': 'emergencia',
        'raciocinio': raciocinio,
        'achados': _achados(dados),
        'red_flags': [
            'WPW — CONTRAINDICAÇÃO ABSOLUTA: Verapamil, Diltiazem, Digoxina',
            'Risco de FV e morte súbita se bloqueador do nó AV for administrado',
        ],
        'exames': ['ECG 12 derivações (confirmar delta wave)', 'Holter 24h (avaliar carga de pré-excitação)'],
        'conduta': [
            'Encaminhar PS urgente para avaliação e cardioversão se necessário',
            'NÃO usar verapamil, diltiazem ou digoxina — risco de FV letal',
            'Referência eletrofisiologia para ablação por cateter (cura > 95%)',
        ],
        'prescricoes_estruturadas': [],
        'orientacoes': {
            'alerta_wpw': (
                'Você tem uma via elétrica acessória no coração (síndrome de WPW). '
                'NUNCA use Verapamil, Diltiazem (Cardizem) ou Digoxina — '
                'esses remédios podem causar um ritmo fatal. '
                'Sempre informe qualquer médico ou pronto-socorro sobre o WPW antes de receber qualquer medicação.'
            ),
        },
        'encaminhar': 'PS urgente + eletrofisiologia eletivo (ablação por cateter)',
        'retorno': '',
        'dias_atestado': 1,
    }


# =============================================================================
# STEP 1 — TAQUICARDIA QRS LARGO (TV SUSPEITA)
# =============================================================================

def _resultado_tv_qrs_largo(dados) -> dict:
    cardiopatia = dados.get('cardiopatia_estrutural', False)
    raciocinio = (
        'Taquicardia de QRS largo (> 120 ms) durante palpitação. '
        'Diagnóstico diferencial: taquicardia ventricular (TV) vs TSV com aberrância de condução. '
        + ('Cardiopatia estrutural presente → TV até prova em contrário (VPP > 90%). ' if cardiopatia
           else 'Sem cardiopatia estrutural conhecida → diferenciação TV vs TSV aberrante requer critérios de Brugada (ECG). ')
        + 'Na dúvida, tratar como TV (mais seguro). '
        'Paciente estável: PS para manejo antiarrítmico IV. '
        'Instável: cardioversão elétrica sincronizada imediata. '
        'NÃO usar verapamil em taquicardia QRS largo — pode precipitar FV em TV.'
    )
    return {
        'tipo': 'palpitacao', 'subtipo': 'palpitacao',
        'categoria': 'pal_tv_qrs_largo',
        'diagnostico': 'Taquicardia de QRS Largo — TV vs TSV Aberrante — PS Imediato',
        'urgencia': 'emergencia',
        'raciocinio': raciocinio,
        'achados': _achados(dados),
        'red_flags': [
            'Taquicardia QRS largo — TV suspeita',
            'NUNCA usar verapamil em taquicardia de QRS largo (risco de FV)',
        ],
        'exames': ['ECG 12 derivações em taquicardia', 'ECG em ritmo sinusal (comparação)', 'Ecocardiograma'],
        'conduta': [
            'Encaminhar PS imediatamente — possível TV',
            'Se instável: cardioversão elétrica sincronizada',
            'Se estável em PS: Amiodarona 150 mg IV ou Procainamida IV sob monitorização',
            'NÃO usar verapamil em taquicardia QRS largo',
            'Holter e ecocardiograma após estabilização',
        ],
        'prescricoes_estruturadas': [],
        'orientacoes': {},
        'encaminhar': 'PS imediato + cardiologia/eletrofisiologia',
        'retorno': '',
        'dias_atestado': 1,
    }


# =============================================================================
# STEP 1 — BRUGADA + SÍNCOPE
# =============================================================================

def _resultado_brugada(dados) -> dict:
    raciocinio = (
        'Padrão Brugada tipo 1 no ECG (supra ST em V1–V2 com morfologia de BRD incompleto) '
        'associado a síncope → risco elevado de morte súbita por fibrilação ventricular. '
        'Síndrome de Brugada é channelopatia (SCN5A — canal de sódio). '
        'Síncope + padrão Brugada espontâneo = provável episódio de FV auto-revertida. '
        'DAI indicado: padrão tipo 1 ESPONTÂNEO + síncope (ESC 2022 — única combinação com evidência consistente). '
        'Padrão tipo 1 apenas INDUZIDO por fármaco (Ajmalina/Flecainida) + síncope: '
        'indicação de DAI não é automática — decisão do eletrofisiologista após EEF. '
        'Evitar antiarrítmicos classe IC (flecainida, propafenona) e classe IA (quinidina exceto '
        'protocolo específico) — podem desmascarar ou agravar o padrão.'
    )
    return {
        'tipo': 'palpitacao', 'subtipo': 'palpitacao',
        'categoria': 'pal_brugada_sincope',
        'diagnostico': 'Síndrome de Brugada + Síncope — PS / Eletrofisiologia Urgente',
        'urgencia': 'emergencia',
        'raciocinio': raciocinio,
        'achados': _achados(dados),
        'red_flags': [
            'Padrão Brugada + síncope — alto risco de morte súbita',
            'Evitar Flecainida, Propafenona, Ajmalina, Procainamida',
        ],
        'exames': [
            'ECG 12 derivações (leads V1–V2 em posição alta)',
            'Ecocardiograma (excluir cardiopatia estrutural)',
            'Teste provocativo com Ajmalina/Flecainida (só em centro especializado)',
            'Triagem familiar',
        ],
        'conduta': [
            'Encaminhar PS urgente + eletrofisiologia',
            'DAI: indicado se padrão tipo 1 ESPONTÂNEO + síncope (ESC 2022 Class I)',
            'Evitar hipertermia (agrava o padrão de Brugada)',
            'Triagem de familiares de primeiro grau',
        ],
        'prescricoes_estruturadas': [],
        'orientacoes': {
            'brugada_alerta': (
                'Você tem uma síndrome elétrica do coração (Brugada). '
                'Febre alta pode desencadear arritmias — tratar febre precocemente com paracetamol. '
                'Evitar medicações sem consultar cardiologista (inclusive remédios para gripe e anestésicos). '
                'Carregar sempre um cartão informativo sobre Brugada.'
            ),
        },
        'encaminhar': 'PS urgente + eletrofisiologia (avaliar DAI)',
        'retorno': '',
        'dias_atestado': 1,
    }


# =============================================================================
# STEP 1 — QT LONGO + SÍNCOPE (TORSADES DE POINTES)
# =============================================================================

def _resultado_qt_longo_sincope(dados) -> dict:
    uso_antiarr = dados.get('uso_antiarritmico', False)
    raciocinio = (
        'QTc prolongado + síncope → suspeita de Torsades de Pointes (TdP), '
        'forma polimórfica de taquicardia ventricular característica do QT longo. '
        + ('Paciente em uso de antiarrítmico — QT longo adquirido (fármaco-induzido) possível. ' if uso_antiarr else '')
        + 'QT longo congênito (LQTS 1, 2, 3 — channelopatias) ou adquirido '
        '(drogas — sotalol, quinidina, antidepressivos, macrolídeos, haloperidol; '
        'distúrbios eletrolíticos — hipocalemia, hipomagnesemia). '
        'Tratamento TdP: Sulfato de Magnésio 2g IV em 1–2 min. '
        'Suspender todos os fármacos que prolongam o QT. '
        'Correção de eletrólitos. Cardio/eletrofisiologia urgente.'
    )
    return {
        'tipo': 'palpitacao', 'subtipo': 'palpitacao',
        'categoria': 'pal_qt_longo_sincope',
        'diagnostico': 'QT Longo + Síncope — Torsades de Pointes Suspeita — PS Imediato',
        'urgencia': 'emergencia',
        'raciocinio': raciocinio,
        'achados': _achados(dados),
        'red_flags': [
            'QT longo + síncope — Torsades de Pointes suspeita',
            'Suspender TODOS os fármacos que prolongam o QT imediatamente',
        ],
        'exames': [
            'ECG 12 derivações (medir QTc manualmente)',
            'Eletrólitos: K⁺, Mg²⁺, Ca²⁺ (hipocalemia e hipomagnesemia pioram QT)',
            'Triagem genética (LQTS congênito)',
        ],
        'conduta': [
            'PS imediato — risco de FV',
            'Sulfato de Magnésio 2g IV em 1–2 min (tratamento TdP)',
            'Suspender imediatamente todos os fármacos que prolongam o QT',
            'Corrigir hipocalemia e hipomagnesemia',
            'Eletrofisiologia para definir etiologia (congênito vs adquirido)',
        ],
        'prescricoes_estruturadas': [],
        'orientacoes': {
            'qt_longo_alerta': (
                'Você tem o intervalo QT do coração prolongado. '
                'Muitos remédios comuns podem agravar essa condição e causar arritmia grave. '
                'Nunca tome medicamentos novos sem verificar com seu cardiologista. '
                'Site de referência: crediblemeds.org (lista de fármacos que prolongam QT).'
            ),
        },
        'encaminhar': 'PS imediato + eletrofisiologia',
        'retorno': '',
        'dias_atestado': 1,
    }


# =============================================================================
# STEP 1 — SÍNCOPE + PALPITAÇÃO SEM CAUSA EVIDENTE
# =============================================================================

def _resultado_sincope_arritmia(dados) -> dict:
    raciocinio = (
        'Síncope associada a palpitação sem causa claramente benigna identificada. '
        'A combinação síncope + palpitação aumenta muito a probabilidade de arritmia grave '
        'como TV, FV ou bloqueio AV de alto grau. '
        'Score CSRS (Canadian Syncope Risk Score) indica avaliação hospitalar. '
        'ECG 12 derivações obrigatório. Holter ou loop recorder pode ser necessário. '
        'Não liberar sem investigação cardiológica.'
    )
    red_flags = ['Síncope + palpitação — arritmia grave até prova em contrário']
    if dados.get('morte_subita_familiar'):
        red_flags.append('História familiar de morte súbita em < 40 anos')
    if dados.get('cardiopatia_estrutural'):
        red_flags.append('Cardiopatia estrutural — TV muito mais provável')

    return {
        'tipo': 'palpitacao', 'subtipo': 'palpitacao',
        'categoria': 'pal_sincope_arritmia',
        'diagnostico': 'Síncope + Palpitação — Investigação Urgente (PS/Cardio)',
        'urgencia': 'urgente',
        'raciocinio': raciocinio,
        'achados': _achados(dados),
        'red_flags': red_flags,
        'exames': [
            'ECG 12 derivações (obrigatório — agora)',
            'Glicemia capilar (excluir hipoglicemia)',
            'Holter 24–48h ou loop recorder implantável',
            'Ecocardiograma (estrutural)',
            'Teste ergométrico se síncope ao esforço',
        ],
        'conduta': [
            'Não liberar sem ECG — mesmo se assintomático agora',
            'Encaminhar PS ou cardiologia urgente no mesmo dia',
            'Holter ou loop recorder para documentar ritmo durante episódio futuro',
        ],
        'prescricoes_estruturadas': [],
        'orientacoes': {
            'sincope_cuidados': (
                'Enquanto a causa da palpitação com desmaio não for investigada, evite '
                'dirigir, trabalhar em altura ou operar máquinas perigosas. '
                'Se palpitação começar novamente, deite-se imediatamente e chame alguém.'
            ),
        },
        'encaminhar': 'PS ou cardiologia urgente (mesmo dia)',
        'retorno': '',
        'dias_atestado': 1,
    }


# =============================================================================
# STEP 2A — FLUTTER ATRIAL
# =============================================================================

def _resultado_flutter(dados) -> dict:
    raciocinio = (
        'ECG com ondas F em serrilhado (rate 250–350 bpm) → flutter atrial. '
        'Flutter clássico: condução AV 2:1 → FC ~150 bpm regular. '
        'Difere da FA pela regularidade e ondas F características em D2, D3, aVF. '
        'Flutter é menos responsivo ao controle de FC do que FA. '
        'Cardioversão elétrica é altamente eficaz (baixa energia: 50–100 J). '
        'Ablação por cateter (istmo cavo-tricuspídeo): cura em > 95% dos casos — '
        'preferível à FA pois é curável. '
        'Anticoagulação: mesmas indicações do CHA₂DS₂-VASc que na FA.'
    )
    rxs = []
    if dados.get('anticoagulacao_indicada'):
        rxs = _doac_prescricao(dados)

    return {
        'tipo': 'palpitacao', 'subtipo': 'palpitacao',
        'categoria': 'pal_flutter',
        'diagnostico': 'Flutter Atrial — Cardiologia Urgente + Ablação',
        'urgencia': 'urgente',
        'raciocinio': raciocinio,
        'achados': _achados(dados),
        'red_flags': [],
        'exames': [
            'ECG 12 derivações (confirmar flutter — ondas F em serrilhado)',
            'Ecocardiograma (FE, trombos, tamanho átrio)',
            'TSH (excluir hipertireoidismo como gatilho)',
            'Função renal (para escolha de DOAC)',
        ],
        'conduta': [
            'Encaminhar cardiologia urgente — flutter não responde bem a fármacos de controle FC',
            'Cardioversão elétrica (50–100 J, alta eficácia no flutter)',
            'Ablação por cateter do istmo cavo-tricuspídeo (cura > 95%)',
            _score_str(dados) or 'Avaliar CHA₂DS₂-VASc para anticoagulação',
        ],
        'prescricoes_estruturadas': rxs,
        'orientacoes': {
            'flutter_info': (
                'O flutter atrial é um ritmo cardíaco acelerado que geralmente pode ser curado '
                'com um procedimento chamado ablação por cateter (queimada de um ponto no coração). '
                'Enquanto aguarda avaliação, evite esforços intensos e use anticoagulante conforme orientado.'
            ),
        },
        'encaminhar': 'Cardiologia urgente (ablação por cateter)',
        'retorno': '48–72h ou PS se piora',
        'dias_atestado': 2,
    }


# =============================================================================
# STEP 2B — FA NOVA ELEGÍVEL A CARDIOVERSÃO QUÍMICA
# =============================================================================

def _resultado_fa_nova_cardioversao(dados) -> dict:
    score_txt = _score_str(dados)
    anticoag  = dados.get('anticoagulacao_indicada', False)
    score_val = dados.get('cha2ds2_score', 0)

    raciocinio = (
        'FA de início provável < 48h, sem cardiopatia estrutural conhecida, sem IC, sem estenose mitral, '
        'sem WPW → elegível à cardioversão química com Propafenona 300mg VO (pill-in-the-pocket). '
        'Eficácia da Propafenona: ~73% de reversão para sinusal (JACC Electrophysiology 2022). '
        'PROTOCOLO DE SEGURANÇA (AHA/ACC 2023): Administrar bloqueador do nó AV (Metoprolol 25–50mg VO) '
        '30 min ANTES da Propafenona — previne condução AV 1:1 se FA converter a flutter '
        '(flutter 300 bpm com condução 1:1 → FC 300 → colapso). '
        'Primeira dose sempre em ambiente monitorado. '
        'Não usar Propafenona se: cardiopatia estrutural (IC, HVE significativa, IAM prévio), '
        'DPOC grave, bradicardia ou PR longo. '
        + (f'{score_txt}. ' if score_txt else '')
        + ('Anticoagulação com DOAC iniciada imediatamente e mantida ≥4 semanas após cardioversão '
           '(risco de trombo atrial ainda presente). ' if anticoag else
           'CHA₂DS₂-VASc baixo — anticoagulação após cardioversão por 4 semanas se episódio > 12h.')
    )

    rxs = [
        _rx(
            '1ª linha — cardioversão química',
            'Propafenona',
            [_p('1 comprimido', '300 mg',
                '300 mg VO dose única em observação — '
                'se não converter em 2h: +150 mg (máx 600 mg total). '
                'Administrar com o paciente sentado, monitorado (PA + ECG)')],
            nota=(
                'PROTOCOLO: Metoprolol 25–50mg VO 30 min ANTES da Propafenona '
                '(previne flutter 1:1 com FC 300 — risco de colapso). '
                'Contraindicado em: cardiopatia estrutural (IC, cardiomiopatia, IAM prévio), '
                'DPOC grave, estenose mitral significativa, WPW, bradicardia sinusal (FC < 50). '
                'Primeira dose SEMPRE em ambiente monitorado (risco de hipotensão, bradiarritmia, flutter 1:1). '
                'Se FA > 48h ou duração desconhecida: não cardiovertir sem anticoagulação prévia 3 semanas '
                'ou ECOTE negativo para trombo.'
            ),
        ),
    ]
    if anticoag:
        rxs += _doac_prescricao(dados)

    return {
        'tipo': 'palpitacao', 'subtipo': 'palpitacao',
        'categoria': 'pal_fa_nova_cardioversao',
        'diagnostico': 'FA Nova < 48h — Cardioversão Química com Propafenona',
        'urgencia': 'urgente',
        'raciocinio': raciocinio,
        'achados': _achados(dados),
        'red_flags': [],
        'exames': [
            'ECG 12 derivações (confirmar FA, avaliar WPW, QT)',
            'Ecocardiograma (FE, tamanho átrio, valvopatia)',
            'TSH + T4 livre (hipertireoidismo como gatilho)',
            'Função renal e eletrólitos (K⁺, Mg²⁺)',
            'Hemograma (anemia como gatilho)',
        ],
        'conduta': [
            'Metoprolol 25–50mg VO → aguardar 30 min → Propafenona 300mg VO (sequência obrigatória)',
            'Monitorar ECG e PA durante e por ≥ 2h após a dose',
            'Se não reverter: encaminhar PS para cardioversão elétrica',
            score_txt or 'Calcular CHA₂DS₂-VASc para anticoagulação',
            'Manter anticoagulação ≥4 semanas após cardioversão (independente do score)',
            'Encaminhar Cardiologia eletivo para investigação da causa',
        ],
        'prescricoes_estruturadas': rxs,
        'orientacoes': {
            'fa_orientacao': (
                'Você teve um episódio de fibrilação atrial (ritmo irregular do coração). '
                'O remédio foi dado para tentar normalizar o ritmo. '
                'Se sentir tontura forte, falta de ar ou desmaio durante a observação, informe imediatamente.'
            ),
            'retorno_urgente': (
                'Retorne imediatamente ao PS se: novo episódio de palpitação irregular, '
                'falta de ar, tontura intensa ou dor no peito.'
            ),
        },
        'encaminhar': 'Cardiologia eletivo (após estabilização)',
        'retorno': '48–72h',
        'dias_atestado': 2,
    }


# =============================================================================
# STEP 2C — FA NOVA NÃO ELEGÍVEL A CARDIOVERSÃO (cardiopatia / duração incerta)
# =============================================================================

def _resultado_fa_nova_controle_fc(dados) -> dict:
    cardiopatia = dados.get('cardiopatia_estrutural', False)
    duracao     = dados.get('duracao_episodio', '')
    score_txt   = _score_str(dados)
    anticoag    = dados.get('anticoagulacao_indicada', False)

    motivo = []
    if cardiopatia:
        motivo.append('cardiopatia estrutural (Propafenona contraindicada)')
    if duracao in ('horas', 'persistente') and not cardiopatia:
        motivo.append('duração incerta ou > 48h (cardioversão sem anticoagulação inadequada)')

    raciocinio = (
        f'FA aguda — não elegível à cardioversão química imediata: {"; ".join(motivo) or "critérios ausentes"}. '
        'Estratégia: controle de frequência + anticoagulação. '
        'Alvo de FC: < 80 bpm em repouso (controle estrito melhora sintomas). '
        'Metoprolol succinato é a primeira escolha (beta-bloqueador). '
        'Se FA > 48h ou duração desconhecida: anticoagular ≥3 semanas ANTES de qualquer cardioversão eletiva, '
        'ou realizar ECOTE para excluir trombo atrial antes. '
        + (f'{score_txt}. ' if score_txt else '')
        + 'Cardioversão eletiva pode ser planejada com cardio após anticoagulação adequada.'
    )

    rxs = [
        _rx(
            '1ª linha — controle de FC',
            'Metoprolol succinato',
            [_p('30 comprimidos', '50 mg', '1 comprimido VO 1×/dia (podendo titular até 100–200 mg/dia)')],
            nota=(
                'Alvo: FC < 80 bpm em repouso. '
                'Contraindicado em: asma brônquica, bradicardia sinusal (FC < 50), '
                'bloqueio AV 2º/3º grau sem marcapasso, choque cardiogênico. '
                'Em cardiopatia com IC com FE reduzida: preferir Bisoprolol ou Carvedilol.'
            ),
        ),
    ]
    if anticoag:
        rxs += _doac_prescricao(dados)

    return {
        'tipo': 'palpitacao', 'subtipo': 'palpitacao',
        'categoria': 'pal_fa_nova_controle_fc',
        'diagnostico': 'FA — Controle de Frequência + Anticoagulação',
        'urgencia': 'urgente',
        'raciocinio': raciocinio,
        'achados': _achados(dados),
        'red_flags': ['Cardiopatia estrutural — avaliar IC descompensada' if cardiopatia else ''],
        'exames': [
            'ECG 12 derivações',
            'Ecocardiograma (FE, tamanho átrio — essencial em cardiopatia)',
            'TSH + T4 livre',
            'Função renal e eletrólitos',
            'Hemograma',
            'ECOTE se cardioversão eletiva planejada sem anticoag prévia 3 semanas',
        ],
        'conduta': [
            'Metoprolol succinato 50mg 1×/dia — titular para FC < 80 bpm',
            score_txt or 'Calcular CHA₂DS₂-VASc para anticoagulação',
            'Anticoagulação 3 semanas antes de cardioversão eletiva (se FA > 48h)',
            'Encaminhar Cardiologia para cardioversão eletiva e investigação',
        ],
        'prescricoes_estruturadas': rxs,
        'orientacoes': {
            'fa_controle_fc': (
                'Seu coração está em um ritmo irregular chamado fibrilação atrial. '
                'O remédio vai ajudar a controlar a velocidade do coração. '
                'Use o anticoagulante todos os dias — ele reduz o risco de AVC pela FA.'
            ),
            'sinais_retorno': (
                'Procure PS se: falta de ar progressiva, inchaço nas pernas, tontura intensa, '
                'dor no peito ou coração acelerando acima de 120 bpm.'
            ),
        },
        'encaminhar': 'Cardiologia (urgente se cardiopatia; eletivo se estável)',
        'retorno': '7 dias',
        'dias_atestado': 2,
    }


# =============================================================================
# STEP 2D — FA CRÔNICA (CONHECIDA OU ESTABELECIDA)
# =============================================================================

def _resultado_fa_cronica(dados) -> dict:
    score_txt = _score_str(dados)
    anticoag  = dados.get('anticoagulacao_indicada', False)
    score_val = dados.get('cha2ds2_score', 0)

    raciocinio = (
        'FA crônica ou recorrente conhecida. '
        'Estratégia de longo prazo: controle de frequência + anticoagulação (se indicada). '
        + (f'{score_txt}. ' if score_txt else '')
        + 'Metoprolol succinato é a primeira escolha para controle de FC em FA crônica. '
        'DOACs são superiores à warfarina para FA não valvar — '
        'menor risco de AVC hemorrágico, sem necessidade de monitorização de INR. '
        'Hierarquia por net clinical benefit (real-world n > 500k + ARISTOTLE): '
        'Apixabana 1ª linha (HR sangramento major 0.76 vs VKA) > '
        'Rivaroxabana alternativo (HR 1.11 — posologia 1×/dia mas mais sangramento) > Dabigatrana. '
        'Warfarina ainda indicada em FA valvar (estenose mitral moderada/grave, prótese metálica). '
        'Avaliar reversão de fatores desencadeantes: hipertireoidismo, HAS descontrolada, apneia do sono.'
    )

    rxs = [
        _rx(
            'Controle de FC',
            'Metoprolol succinato',
            [_p('30 comprimidos', '50 mg', '1 comprimido VO 1×/dia — titular até FC < 80 bpm em repouso')],
            nota='Alternativa: Bisoprolol 5–10mg 1×/dia (melhor tolerância em idosos).',
        ),
    ]
    if anticoag:
        rxs += _doac_prescricao(dados)

    return {
        'tipo': 'palpitacao', 'subtipo': 'palpitacao',
        'categoria': 'pal_fa_cronica',
        'diagnostico': 'FA Crônica — Controle de FC + Anticoagulação',
        'urgencia': 'aps',
        'raciocinio': raciocinio,
        'achados': _achados(dados),
        'red_flags': [],
        'exames': [
            'ECG 12 derivações',
            'Ecocardiograma (se não realizado nos últimos 12 meses)',
            'TSH (anual ou se piora)',
            'Função renal (para ajuste de DOAC — anual)',
            'Holter (se sintomas de descontrole de FC)',
        ],
        'conduta': [
            'Metoprolol succinato 50mg 1×/dia — alvo FC < 80 bpm',
            score_txt or 'Calcular CHA₂DS₂-VASc (anticoagulação)',
            'Encaminhar cardiologia para reavaliação de ritmo vs frequência e ablação se candidato',
            'Pesquisar e tratar fatores desencadeantes (HAS, apneia do sono, obesidade, álcool)',
        ],
        'prescricoes_estruturadas': rxs,
        'orientacoes': {
            'fa_cronica': (
                'A fibrilação atrial crônica é manejável. '
                'Use os remédios todos os dias — o anticoagulante é fundamental para prevenir AVC. '
                'Meça a pressão arterial regularmente e evite álcool (principal gatilho de FA). '
                'Se o coração acelerar muito ou surgirem novos sintomas, procure atendimento.'
            ),
        },
        'encaminhar': 'Cardiologia (eletivo — manutenção) ou urgente se descontrole',
        'retorno': '30 dias',
        'dias_atestado': 1,
    }


# =============================================================================
# STEP 2E — TSV PAROXÍSTICA
# =============================================================================

def _resultado_tsv_paroxistica(dados) -> dict:
    historico = dados.get('taquicardia_previa', False)
    raciocinio = (
        'Taquicardia paroxística de início e término súbitos, QRS estreito, FC geralmente '
        '150–250 bpm → taquicardia supraventricular paroxística (TSV). '
        'Mecanismo mais comum: reentrada no nó AV (TRNAV) ou por via acessória oculta (TRAV). '
        'Manobra de Valsalva modificada: paciente em decúbito, força de valsalva 15 segundos, '
        'depois elevar MMII 45° por 15 segundos → eficácia ~43% (superior ao posicionamento tradicional). '
        'Se refratária: adenosina IV 6mg em bolus rápido (PS) → 12mg se necessário. '
        'Profilaxia: Metoprolol succinato reduz recorrências. '
        + ('Episódios recorrentes — referência eletrofisiologia para ablação (cura > 95%). ' if historico else '')
        + 'EXCLUIR WPW no ECG em ritmo sinusal antes de tratar cronicamente.'
    )
    return {
        'tipo': 'palpitacao', 'subtipo': 'palpitacao',
        'categoria': 'pal_tsv_paroxistica',
        'diagnostico': 'TSV Paroxística — Valsalva + Metoprolol Profilático',
        'urgencia': 'aps',
        'raciocinio': raciocinio,
        'achados': _achados(dados),
        'red_flags': ['Excluir WPW (pré-excitação) no ECG antes de iniciar verapamil/betabloqueador'],
        'exames': [
            'ECG 12 derivações em ritmo sinusal (excluir pré-excitação / WPW)',
            'ECG 12 derivações durante taquicardia (se disponível)',
            'Holter 24h (documentar episódios e frequência)',
            'Ecocardiograma (excluir cardiopatia estrutural)',
        ],
        'conduta': [
            'Instruir manobra de Valsalva modificada (técnica e posicionamento — ver orientações)',
            'Iniciar Metoprolol succinato 25–50mg 1×/dia como profilaxia',
            'Se novo episódio não reverter com Valsalva: PS para adenosina IV',
            'Encaminhar eletrofisiologia se episódios frequentes (ablação por cateter cura > 95%)',
        ],
        'prescricoes_estruturadas': [
            _rx(
                'Profilaxia TSV',
                'Metoprolol succinato',
                [_p('30 comprimidos', '25 mg', '1 comprimido VO 1×/dia (titular até 50–100 mg conforme tolerância)')],
                nota=(
                    'Iniciar com dose baixa e aumentar conforme FC (alvo: 55–65 bpm em repouso). '
                    'Alternativa: Verapamil 120–240mg/dia (NUNCA se WPW suspeito). '
                    'Encaminhar eletrofisiologia para ablação se preferência por cura definitiva.'
                ),
            ),
        ],
        'orientacoes': {
            'valsalva_tecnica': (
                'MANOBRA DE VALSALVA MODIFICADA — Como fazer durante o episódio:\n'
                '1. Sente-se ou deite-se.\n'
                '2. Sopre forte por uma seringa de 10 mL fechada (ou como se tentasse mover o êmbolo), '
                'por 15 segundos.\n'
                '3. IMEDIATAMENTE deite-se e eleve as pernas a 45° por 15 segundos.\n'
                '4. Então sente-se novamente.\n'
                'Se o coração não normalizar em 2 tentativas: vá ao pronto-socorro.\n'
                'NÃO use esta manobra se tiver dor no peito, dificuldade para respirar ou tontura forte.'
            ),
            'quando_ps': (
                'Vá ao PS se: palpitação durar > 30 minutos, não reverter com Valsalva, '
                'ou se aparecer tontura forte, falta de ar ou dor no peito.'
            ),
        },
        'encaminhar': 'Eletrofisiologia eletivo (ablação se recorrente)',
        'retorno': '30 dias',
        'dias_atestado': 0,
    }


# =============================================================================
# STEP 3A — EXTRASSISTOLIA BENIGNA
# =============================================================================

def _resultado_extrassistolia(dados) -> dict:
    cardiopatia  = dados.get('cardiopatia_estrutural', False)
    ecg_ritmo    = dados.get('ecg_ritmo', '')
    ritmo_perc   = dados.get('ritmo_percebido', '')

    raciocinio = (
        'Palpitação do tipo batida extra, flip ou pausa com retomada do ritmo — '
        'padrão clássico de extrassistolia (supraventricular ou ventricular). '
        'Na ausência de cardiopatia estrutural e com ECG sem alterações isquêmicas ou de repolarização, '
        'extrassistolia é benigna em mais de 95% dos casos. '
        + ('Cardiopatia estrutural presente — avaliar carga de extrassistolia (Holter) e função ventricular, '
           'pois taquicardia ventricular não sustentada (TVNS) pode coexistir. '
           if cardiopatia else
           'Sem cardiopatia estrutural — prognóstico excelente. ')
        + 'Gatilhos comuns: cafeína, álcool, estresse, privação de sono, hipocalemia. '
        'Tratar principalmente os sintomas e a ansiedade gerada. '
        'Beta-bloqueador apenas se sintomas frequentes e incapacitantes.'
    )
    conduta = [
        'Tranquilizar o paciente — extrassistolia benigna não aumenta mortalidade sem cardiopatia',
        'Orientar redução de cafeína, álcool, estresse e privação de sono',
        'Holter 24h eletivo para quantificar carga (> 10% complexos = monitorar mais)',
        'Ecocardiograma se não realizado (excluir cardiopatia estrutural)',
    ]
    if cardiopatia:
        conduta.append('Encaminhar cardiologia — cardiopatia + extrassistolia requer Holter + eco + avaliação de TVNS')

    rxs = []
    if not cardiopatia:
        rxs = [
            _rx(
                'Se sintomas muito incapacitantes',
                'Metoprolol succinato',
                [_p('30 comprimidos', '25 mg', '1 comprimido VO 1×/dia (titulável)')],
                nota='Usar apenas se sintomas frequentes e incapacitantes. Não indicado de rotina para extrassistolia benigna.',
            ),
        ]
    return {
        'tipo': 'palpitacao', 'subtipo': 'palpitacao',
        'categoria': 'pal_extrassistolia',
        'diagnostico': 'Extrassistolia — Holter Eletivo + Tranquilizar',
        'urgencia': 'eletivo',
        'raciocinio': raciocinio,
        'achados': _achados(dados),
        'red_flags': ['Cardiopatia estrutural + extrassistolia — excluir TVNS' if cardiopatia else ''],
        'exames': [
            'ECG 12 derivações (avaliar ectopia, isquemia, QT)',
            'Holter 24h eletivo (quantificar carga de extrassístoles)',
            'Ecocardiograma (FE e estrutura)',
            'Eletrólitos: K⁺, Mg²⁺',
        ],
        'conduta': conduta,
        'prescricoes_estruturadas': rxs,
        'orientacoes': {
            'extrassistolia_info': (
                'As "batidas extras" que você sente são chamadas extrassístoles. '
                'Na grande maioria dos casos, são benignas e não indicam problema sério no coração. '
                'Reduzir cafeína (café, energético, chá preto), álcool e estresse costuma diminuir os episódios. '
                'O exame Holter vai verificar a quantidade dessas batidas extras ao longo de 24 horas.'
            ),
        },
        'encaminhar': 'Cardiologia eletivo (se cardiopatia ou carga alta no Holter > 10%)',
        'retorno': '30–60 dias (com resultado do Holter)',
        'dias_atestado': 0,
    }


# =============================================================================
# STEP 3B — HIPERTIREOIDISMO
# =============================================================================

def _resultado_hipertireoidismo(dados) -> dict:
    uso_levotirox = dados.get('uso_hormonio_tireoidiano', False)
    raciocinio = (
        'Palpitação com sinais sistêmicos sugestivos de excesso de hormônio tireoidiano: '
        'perda de peso, tremor, intolerância ao calor, sudorese, diarreia. '
        + ('Paciente em uso de Levotiroxina — suspeitar de dose excessiva (TSH suprimido). ' if uso_levotirox else '')
        + 'Hipertireoidismo é causa secundária tratável e reversível de palpitação e arritmias (inclusive FA). '
        'TSH + T4 livre: TSH suprimido + T4 elevado confirma. '
        'Propranolol controla sintomas adrenérgicos rapidamente (inclusive palpitação). '
        'Tratamento definitivo: metimazol ou propiltiouracila (endocrinologia).'
    )
    return {
        'tipo': 'palpitacao', 'subtipo': 'palpitacao',
        'categoria': 'pal_hipertireoidismo',
        'diagnostico': 'Palpitação por Hipertireoidismo Suspeito',
        'urgencia': 'aps',
        'raciocinio': raciocinio,
        'achados': _achados(dados),
        'red_flags': [],
        'exames': [
            'TSH + T4 livre (urgente — resultado em 24–48h)',
            'T3 livre (se TSH suprimido com T4 normal)',
            'ECG (avaliar FA por tireotoxicose)',
            'Anticorpos anti-TPO e anti-TSI (TRAb) se TSH suprimido',
        ],
        'conduta': [
            'TSH + T4 livre — aguardar resultado antes de tratar definitivamente',
            'Propranolol para controle sintomático imediato (palpitação, tremor, ansiedade)',
            'Encaminhar endocrinologia se hipertireoidismo confirmado',
            'Se Levotiroxina em dose alta: reduzir dose e repetir TSH em 4–6 semanas',
        ],
        'prescricoes_estruturadas': [
            _rx(
                'Controle sintomático',
                'Propranolol',
                [_p('30 comprimidos', '40 mg', '1 comprimido VO 2–3×/dia (até controle dos sintomas)')],
                nota=(
                    'Propranolol não trata o hipertireoidismo, apenas controla os sintomas adrenérgicos '
                    '(palpitação, tremor, ansiedade, taquicardia). '
                    'Contraindicado em: asma, DPOC grave, bradicardia. '
                    'Suspender quando função tireoidiana normalizar.'
                ),
            ),
        ],
        'orientacoes': {
            'tireoidismo_info': (
                'Seus sintomas podem ser causados pela tireoide funcionando acima do normal. '
                'O exame de sangue vai confirmar. '
                'Enquanto isso, o remédio vai ajudar a controlar os sintomas. '
                'Evite excesso de cafeína e alimentos ricos em iodo (frutos do mar em excesso).'
            ),
        },
        'encaminhar': 'Endocrinologia (se TSH suprimido confirmado)',
        'retorno': '7–14 dias (com resultado de TSH + T4L)',
        'dias_atestado': 0,
    }


# =============================================================================
# STEP 3C — ANEMIA
# =============================================================================

def _resultado_anemia(dados) -> dict:
    raciocinio = (
        'Palpitação com sintomas sugestivos de anemia: palidez, cansaço intenso, '
        'fraqueza progressiva, sangramento recente ou crônico. '
        'Anemia causa palpitação por débito cardíaco aumentado compensatório '
        '(aumento da FC e contratilidade para manter DO₂). '
        'Hemograma + reticulócitos + ferro sérico/ferritina para etiologia. '
        'Anemia ferropriva é a mais comum — investigar causa do sangramento (endoscopia, colonoscopia). '
        'Anemia por deficiência de B12/folato, hemolítica ou por doença crônica — '
        'cada uma com tratamento específico.'
    )
    return {
        'tipo': 'palpitacao', 'subtipo': 'palpitacao',
        'categoria': 'pal_anemia',
        'diagnostico': 'Palpitação por Anemia Suspeita',
        'urgencia': 'aps',
        'raciocinio': raciocinio,
        'achados': _achados(dados),
        'red_flags': [],
        'exames': [
            'Hemograma completo com reticulócitos',
            'Ferro sérico + ferritina + saturação de transferrina',
            'B12 e ácido fólico',
            'LDH + bilirrubina indireta (hemólise)',
            'Pesquisa de sangramento: sangue oculto nas fezes',
            'Endoscopia e colonoscopia se anemia ferropriva sem causa óbvia',
        ],
        'conduta': [
            'Hemograma urgente para quantificar anemia',
            'Investigar etiologia (ferropriva, carencial, hemolítica)',
            'Sulfato ferroso VO se anemia ferropriva confirmada',
            'Tratar causa de base (sangramento, etc.)',
        ],
        'prescricoes_estruturadas': [
            _rx(
                'Se anemia ferropriva confirmada',
                'Sulfato ferroso',
                [_p('90 comprimidos', '40 mg de ferro elementar',
                    '1 comprimido VO 2–3×/dia, em jejum (1h antes das refeições) — '
                    'administrar com vitamina C para melhorar absorção')],
                nota=(
                    'Apenas se anemia ferropriva confirmada por exames. '
                    'Efeitos adversos: constipação, náusea (tomar com pequena quantidade de alimento se necessário). '
                    'Reavaliação do hemograma em 4 semanas.'
                ),
            ),
        ],
        'orientacoes': {
            'anemia_info': (
                'A palpitação pode ser causada por anemia (falta de sangue/hemoglobina). '
                'O exame de sangue vai confirmar. '
                'Se o hemograma mostrar anemia, será preciso investigar a causa — '
                'pode ser falta de ferro, vitaminas ou um sangramento que está passando despercebido.'
            ),
        },
        'encaminhar': 'Gastroenterologia/Hematologia se anemia sem causa óbvia',
        'retorno': '14–30 dias (com resultado de hemograma)',
        'dias_atestado': 0,
    }


# =============================================================================
# STEP 3D — ANSIEDADE / PÂNICO
# =============================================================================

def _resultado_ansiedade_panico(dados) -> dict:
    raciocinio = (
        'Palpitação associada a medo intenso, falta de ar, formigamento, sensação de morte iminente '
        '→ padrão compatível com transtorno do pânico. '
        'A palpitação no pânico é real (taquicardia sinusal por adrenalina), mas benigna. '
        'Critérios DSM-5 para ataque de pânico: ≥4 de 13 sintomas, pico em < 10 min. '
        'Excluir primeiro causas orgânicas: ECG, TSH, glicemia. '
        'Tratamento de primeira linha: ISRS + TCC (terapia cognitivo-comportamental). '
        'Benzodiazepínico apenas a curto prazo se crise intensa — evitar uso crônico (dependência).'
    )
    rxs = [
        _rx(
            'Tratamento de primeira linha (longo prazo)',
            'Sertralina',
            [_p('30 comprimidos', '50 mg', '1 comprimido VO 1×/dia (iniciar com 25 mg/dia na 1ª semana)')],
            nota=(
                'ISRS de primeira escolha para transtorno do pânico e ansiedade generalizada. '
                'Efeito pleno em 4–8 semanas — informar ao paciente. '
                'Alternativas: Escitalopram 10mg, Paroxetina 20mg. '
                'Encaminhar psicologia/psiquiatria para TCC concomitante.'
            ),
        ),
        _rx(
            'Crise aguda (uso pontual — máx 4 semanas)',
            'Clonazepam',
            [_p('30 comprimidos', '0,5 mg', '0,5–1 mg VO se/quando — máximo 2mg/dia. '
                'Usar apenas durante crises incapacitantes enquanto ISRS não faz efeito')],
            nota=(
                'Benzodiazepínico — risco de dependência com uso crônico. '
                'Usar pelo menor tempo possível (idealmente < 4 semanas). '
                'Não prescever sem acompanhamento. '
                'Contraindicado em apneia do sono grave.'
            ),
        ),
    ]
    return {
        'tipo': 'palpitacao', 'subtipo': 'palpitacao',
        'categoria': 'pal_ansiedade_panico',
        'diagnostico': 'Palpitação por Transtorno do Pânico / Ansiedade',
        'urgencia': 'aps',
        'raciocinio': raciocinio,
        'achados': _achados(dados),
        'red_flags': [],
        'exames': [
            'ECG 12 derivações (excluir arritmia antes de atribuir ao pânico)',
            'TSH + T4 livre (excluir hipertireoidismo)',
            'Glicemia de jejum (excluir hipoglicemia)',
            'Hemograma (excluir anemia)',
        ],
        'conduta': [
            'Excluir causas orgânicas com exames antes de fechar diagnóstico de pânico',
            'Iniciar ISRS (Sertralina 50mg ou Escitalopram 10mg)',
            'Encaminhar psicologia para TCC (melhor resultado a longo prazo)',
            'Psiquiatria se crises frequentes não controladas com ISRS + TCC',
        ],
        'prescricoes_estruturadas': rxs,
        'orientacoes': {
            'panico_info': (
                'Os ataques de pânico são muito reais — o coração acelera de verdade por adrenalina. '
                'Mas não são perigosos para o coração. '
                'Com o tratamento certo (remédio + terapia), a grande maioria das pessoas melhora muito. '
                'Durante uma crise: respiração lenta e profunda (4 segundos inspira, 4 retém, 4 expira), '
                'não hiperventile, fique num ambiente seguro.'
            ),
        },
        'encaminhar': 'Psicologia/Psiquiatria (TCC + acompanhamento)',
        'retorno': '30 dias',
        'dias_atestado': 0,
    }


# =============================================================================
# STEP 3E — FÁRMACO / ESTIMULANTE
# =============================================================================

def _resultado_farmaco_estimulante(dados) -> dict:
    farmacos = []
    if dados.get('uso_cocaina_estimulante'):  farmacos.append('cocaína / crack / MDMA')
    if dados.get('uso_simpaticomimatico'):    farmacos.append('simpatomiméticos (salbutamol, pseudoefedrina, anfetamina)')
    if dados.get('uso_hormonio_tireoidiano'): farmacos.append('levotiroxina (possível dose alta)')
    if dados.get('uso_antiarritmico'):        farmacos.append('antiarrítmico ou tricíclico (efeito pró-arrítmico)')

    raciocinio = (
        f'Palpitação diretamente relacionada ao uso de: {", ".join(farmacos) or "substância estimulante"}. '
        'Cocaína e estimulantes causam palpitação por liberação maciça de catecolaminas → '
        'vasoespasmo coronariano, taquicardia sinusal, FA, TV. '
        'ECG obrigatório — cocaína pode causar supradesnivelamento de ST (infarto induzido por espasmo). '
        'Simpatomiméticos inalatórios: taquicardia sinusal geralmente benigna, '
        'mas reviar dose e frequência de uso. '
        'Conduta: cessar o uso + orientação + ECG + afastar arritmia subjacente.'
    )
    red_flags = []
    if dados.get('uso_cocaina_estimulante'):
        red_flags.append('Cocaína — ECG obrigatório (risco de infarto por vasoespasmo coronariano)')

    return {
        'tipo': 'palpitacao', 'subtipo': 'palpitacao',
        'categoria': 'pal_farmaco_estimulante',
        'diagnostico': 'Palpitação Induzida por Fármaco / Estimulante',
        'urgencia': 'aps',
        'raciocinio': raciocinio,
        'achados': _achados(dados),
        'red_flags': red_flags,
        'exames': [
            'ECG 12 derivações (obrigatório — excluir ST, QT, arritmia)',
            'Troponina se dor torácica ou cocaína (espasmo coronariano)',
            'TSH se levotiroxina em dose suspeita',
        ],
        'conduta': [
            'Cessar ou ajustar o agente causador',
            'ECG para afastar arritmia ou isquemia subjacente',
            'Encaminhar CAPS/Psicossocial se uso de cocaína/estimulante ilícito',
            'Revisão de dose de levotiroxina se TSH suprimido',
        ],
        'prescricoes_estruturadas': [],
        'orientacoes': {
            'farmaco_info': (
                'A substância que você usou pode acelerar o coração e causar arritmias. '
                'É fundamental parar o uso para que os episódios cessem. '
                'Se tiver dor no peito junto com a palpitação após uso de cocaína, '
                'procure o PS imediatamente — pode ser um infarto por espasmo do vaso.'
            ),
        },
        'encaminhar': 'CAPS/Apoio psicossocial se uso de substâncias ilícitas',
        'retorno': '14–30 dias',
        'dias_atestado': 0,
    }


# =============================================================================
# STEP 3F — INESPECÍFICO
# =============================================================================

def _resultado_inespecifico(dados) -> dict:
    raciocinio = (
        'Palpitação sem características de alto risco, sem causa secundária evidente, '
        'sem documentação de arritmia. '
        'Diagnóstico de palpitação inespecífica — causa mais comum: taquicardia sinusal fisiológica '
        '(ansiedade, cafeína, descondicionamento), extrassistolia esporádica não captada ou '
        'aumento da percepção do próprio ritmo cardíaco (hipervigilância). '
        'ECG normal não exclui arritmia paroxística. '
        'Holter 24–48h ou gravador de eventos (loop recorder) se episódios frequentes. '
        'Se episódios muito raros: Holter de uso prolongado (30 dias) ou loop recorder implantável.'
    )
    return {
        'tipo': 'palpitacao', 'subtipo': 'palpitacao',
        'categoria': 'pal_inespecifico',
        'diagnostico': 'Palpitação Inespecífica — Holter 24h Eletivo',
        'urgencia': 'eletivo',
        'raciocinio': raciocinio,
        'achados': _achados(dados),
        'red_flags': [],
        'exames': [
            'ECG 12 derivações',
            'Holter 24–48h (documentar ritmo durante episódio)',
            'TSH + T4 livre (causas secundárias)',
            'Hemograma (anemia)',
            'Glicemia de jejum',
            'Ecocardiograma (se não realizado)',
        ],
        'conduta': [
            'Holter 24h eletivo — solicitar para próxima consulta',
            'Excluir causas secundárias com TSH + hemograma',
            'Orientar diário de episódios (data, hora, duração, gatilho)',
            'Retorno com resultados para reavaliação',
        ],
        'prescricoes_estruturadas': [],
        'orientacoes': {
            'inespecifico_info': (
                'A palpitação que você sentiu precisa de investigação para definir a causa. '
                'O exame Holter vai registrar o ritmo do seu coração por 24 horas — '
                'é importante usá-lo em um dia comum, com suas atividades habituais, '
                'para tentar capturar o episódio. '
                'Anote num caderninho sempre que sentir a palpitação (hora, o que estava fazendo, duração).'
            ),
        },
        'encaminhar': 'Cardiologia eletivo se Holter mostra arritmia ou sintomas progressivos',
        'retorno': '30–60 dias (com resultado do Holter)',
        'dias_atestado': 0,
    }


# =============================================================================
# ENGINE PRINCIPAL
# =============================================================================

def _analisar_palpitacao_core(dados: dict) -> dict:
    """
    Recebe o dict de dados do subjetivo e retorna o resultado clínico.
    Hierarquia STEP: 1 (emergência) → 2 (urgente/APS) → 3 (eletivo).
    """

    # ── Leitura dos flags principais ─────────────────────────────────────────
    instab        = dados.get('instabilidade_hemodinamica', False)
    sincope       = dados.get('sincope', False)
    wpw           = dados.get('wpw_suspeita', False)
    tv            = dados.get('tv_suspeita', False)
    brugada       = dados.get('brugada_suspeito', False)
    qt_longo      = dados.get('qt_longo_suspeito', False)
    fa_suspeita   = dados.get('fa_suspeita', False)
    fa_conhecida  = dados.get('fa_conhecida', False)
    flutter_ecg   = dados.get('ecg_ritmo', '') == 'flutter'
    tsv           = dados.get('tsv_suspeita', False)
    extrassist    = dados.get('extrassistolia_suspeita', False)
    causa_sec     = dados.get('causa_secundaria_suspeita', False)
    cardiopatia   = dados.get('cardiopatia_estrutural', False)
    duracao       = dados.get('duracao_episodio', '')

    # ── STEP 1 — EMERGÊNCIA ──────────────────────────────────────────────────

    # 1a. Instabilidade hemodinâmica: qualquer taquiarritmia com PA baixa /
    #     síncope / dispneia grave / confusão → cardioversão elétrica
    if instab:
        return _resultado_instabilidade(dados)

    # 1b. WPW confirmado no ECG (delta wave)
    if wpw:
        return _resultado_wpw(dados)

    # 1c. Taquicardia de QRS largo (TV vs TSV aberrante)
    if tv:
        return _resultado_tv_qrs_largo(dados)

    # 1d. Padrão Brugada + síncope → FV auto-revertida
    if brugada and sincope:
        return _resultado_brugada(dados)

    # 1e. QT longo + síncope → Torsades de Pointes provável
    if qt_longo and sincope:
        return _resultado_qt_longo_sincope(dados)

    # 1f. Síncope + palpitação sem arritmia claramente benigna identificada
    #     (não extrassistolia, não causa secundária pura, não TSV documentada)
    if sincope and not (extrassist and not cardiopatia) and not (causa_sec and not fa_suspeita):
        return _resultado_sincope_arritmia(dados)

    # ── STEP 2 — URGENTE / APS MESMA CONSULTA ────────────────────────────────

    # 2a. Flutter atrial confirmado → ablação por cateter
    if flutter_ecg:
        return _resultado_flutter(dados)

    # 2b–c. FA nova ou suspeita
    if fa_suspeita and not fa_conhecida:
        # Elegível a cardioversão química: sem cardiopatia + episódio provável < 48h
        elegivel = (
            not cardiopatia and
            duracao in ('minutos', 'horas') and   # "horas" = provável < 48h como 1ª crise
            not dados.get('ecg_bve', False)        # BRE novo indica cardiopatia não mapeada
        )
        if elegivel:
            return _resultado_fa_nova_cardioversao(dados)
        else:
            return _resultado_fa_nova_controle_fc(dados)

    # 2d. FA crônica/conhecida → controle FC + anticoagulação
    if fa_conhecida or (fa_suspeita and fa_conhecida):
        return _resultado_fa_cronica(dados)

    # 2e. TSV paroxística (sem WPW — já tratado no STEP 1)
    if tsv:
        return _resultado_tsv_paroxistica(dados)

    # ── STEP 3 — APS ELETIVO ─────────────────────────────────────────────────

    # 3a. Extrassistolia
    if extrassist:
        return _resultado_extrassistolia(dados)

    # 3b–e. Causa secundária (avaliar em ordem de probabilidade)
    if causa_sec:
        # Hipertireoidismo: sintomas sistêmicos + tireoidiano
        if dados.get('sintomas_tireoide') or dados.get('uso_hormonio_tireoidiano'):
            return _resultado_hipertireoidismo(dados)

        # Cocaína / estimulante: risco de evento coronariano
        if dados.get('uso_cocaina_estimulante') or dados.get('uso_simpaticomimatico'):
            return _resultado_farmaco_estimulante(dados)

        # Anemia: fadiga + palidez
        if dados.get('sintomas_anemia'):
            return _resultado_anemia(dados)

        # Ansiedade / pânico: medo intenso + palpitação
        if dados.get('sintomas_ansiedade') or dados.get('gatilho_estresse'):
            return _resultado_ansiedade_panico(dados)

    # 3f. Inespecífico
    return _resultado_inespecifico(dados)


# =============================================================================
# PENTE FINO — alertas de segurança transversais
# =============================================================================

def _enriquecer_palpitacao(resultado: dict, dados: dict) -> dict:
    """Adiciona alertas_seguranca ao resultado (renderizados no topo do #Plano)."""
    alertas = []
    cat = resultado.get('categoria', '')

    # WPW: verapamil/diltiazem/digoxina são contraindicados absolutos
    if cat == 'pal_wpw':
        alertas.append(
            '🔴 WPW CONFIRMADO — NUNCA usar Verapamil, Diltiazem ou Digoxina: '
            'podem precipitar condução exclusiva pela via acessória → fibrilação ventricular letal'
        )

    # QT longo + fármaco que prolonga QT
    if cat == 'pal_qt_longo_sincope' or dados.get('qt_longo_suspeito'):
        alertas.append(
            '⚠️ QT longo: revisar TODOS os fármacos em uso (antipsicóticos, macrolídeos, '
            'fluoroquinolonas, antidepressivos TCA) e suspender os que prolongam QTc'
        )

    # Propafenona em FA: nunca sem bloquear o nó AV primeiro
    if cat == 'pal_fa_nova_cardioversao':
        alertas.append(
            '⚠️ Propafenona (pill-in-the-pocket): administrar Metoprolol 25–50 mg VO '
            '30 min ANTES — previne flutter 1:1 com condução rápida caso o ritmo passe '
            'por flutter antes de cardioverter'
        )

    # Instabilidade hemodinâmica → nunca fazer nada oral/ambulatorial
    if cat == 'pal_instabilidade_hemodinamica':
        alertas.append(
            '🔴 INSTABILIDADE HEMODINÂMICA — cardioversão elétrica sincronizada imediata; '
            'NÃO tentar cardioversão química; acionar SAMU 192'
        )

    # DOAC + inibidor potente de P-gp/CYP3A4
    if dados.get('uso_inibidor_pgp_cyp3a4'):
        alertas.append(
            '⚠️ Inibidor de P-gp/CYP3A4 em uso (amiodarona, verapamil, cetoconazol, '
            'ritonavir) → aumenta nível de DOAC: reduzir dose ou ajustar conforme bula'
        )

    resultado['alertas_seguranca'] = alertas
    return resultado


def analisar_palpitacao(dados: dict) -> dict:
    """Ponto de entrada público — core + pente fino."""
    return _enriquecer_palpitacao(_analisar_palpitacao_core(dados), dados)
