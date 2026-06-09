# modules/sintomas/consciencia/subjetivo.py
# Anamnese — Alteração do Nível de Consciência (ANC)
#
# BLOCO 0 — Dados do paciente + contexto
# BLOCO 1 — Glasgow (E + V + M) + onset
# BLOCO 2 — AEIOU TIPS (causas reversíveis primeiro)
# BLOCO 3 — Exame físico dirigido (sinais vitais, pupilas, foco neurológico)
# BLOCO 4 — Exames disponíveis (glicemia, toxicologia, TC)

import json, os, sys
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from utils.perguntas import sn

def _bloco(t):
    print(f'\n{"─"*56}\n  {t}\n{"─"*56}')

def _int(p, mn=0, mx=999):
    while True:
        try:
            v = int(input(p).strip())
            if mn <= v <= mx: return v
            print(f'  {mn}–{mx}.')
        except ValueError: print('  Número inteiro.')

def _float(p):
    while True:
        try: return float(input(p).strip().replace(',','.'))
        except ValueError: print('  Número.')

def _escolha(p, ops):
    for i,(v,l) in enumerate(ops,1): print(f'  {i}. {l}')
    while True:
        try:
            idx=int(input(p).strip())
            if 1<=idx<=len(ops): return ops[idx-1][0]
            print(f'  1–{len(ops)}.')
        except ValueError: print('  Número.')


def coletar_subjetivo_consciencia(dados_preenchidos=None):
    sys.stdout.reconfigure(encoding='utf-8')
    dados = dados_preenchidos or {}

    print('\n'+'='*56)
    print('  ALTERAÇÃO DO NÍVEL DE CONSCIÊNCIA')
    print('='*56)
    print('  ⚠️  Se instabilidade hemodinâmica imediata → chamar PS/SAMU')

    # ── Bloco 0: Contexto ────────────────────────────────────────────
    _bloco('BLOCO 0 — Contexto clínico')
    dados['idade']  = _int('  Idade: ', 0, 120)
    dados['dm']     = sn('  Diabético (em uso de insulina ou hipoglicemiante)? ')
    dados['epilepsia_previa'] = sn('  Epiléptico conhecido? ')
    dados['alcool_drogas']    = sn('  Uso de álcool ou drogas conhecido ou suspeito? ')
    dados['psiq_previa']      = sn('  Transtorno psiquiátrico prévio relevante? ')
    dados['avc_previo']       = sn('  AVC ou TCE prévio? ')
    dados['medicamentos_risco'] = sn('  Usa opioides, BZD, antiepiléticos, insulina ou outros de risco? ')
    dados['medicamentos_quais'] = input('  Quais? ').strip() if dados['medicamentos_risco'] else ''

    dados['onset'] = _escolha('  Início da alteração: ', [
        ('subito',      'Súbito (segundos a minutos)'),
        ('subagudo',    'Subagudo (horas)'),
        ('progressivo', 'Progressivo (dias)'),
        ('flutuante',   'Flutuante / intermitente'),
    ])
    dados['testemunhado'] = sn('  Houve testemunha? ')
    if dados['testemunhado']:
        dados['convulsao_obs']   = sn('  Testemunha viu movimentos convulsivos? ')
        dados['trauma_obs']      = sn('  Houve queda ou trauma na cabeça? ')
        dados['ingestao_obs']    = sn('  Suspeita de ingestão de substância? ')
    else:
        dados['convulsao_obs'] = dados['trauma_obs'] = dados['ingestao_obs'] = False

    # ── Bloco 1: Glasgow ─────────────────────────────────────────────
    _bloco('BLOCO 1 — Escala de Coma de Glasgow (ECG)')
    print('  OLHOS (E):')
    print('  4=Espontâneo  3=À voz  2=À dor  1=Nenhum')
    e = _int('  E: ', 1, 4)
    print('  VERBAL (V):')
    print('  5=Orientado  4=Confuso  3=Palavras  2=Sons  1=Nenhum')
    v = _int('  V: ', 1, 5)
    print('  MOTOR (M):')
    print('  6=Obedece  5=Localiza  4=Flexão normal  3=Flexão anormal  2=Extensão  1=Nenhum')
    m = _int('  M: ', 1, 6)
    dados['glasgow_e'] = e
    dados['glasgow_v'] = v
    dados['glasgow_m'] = m
    dados['glasgow_total'] = e + v + m
    print(f'  Glasgow total: {dados["glasgow_total"]}/15')
    if dados['glasgow_total'] <= 8:
        print('  ⚠️  Glasgow ≤ 8 — vias aéreas comprometidas, considerar IOT')

    # ── Bloco 2: AEIOU TIPS ──────────────────────────────────────────
    _bloco('BLOCO 2 — AEIOU TIPS (causas reversíveis)')

    print('  [A — Álcool / Acidose]')
    dados['alcool_halito']   = sn('  Hálito alcoólico? ')
    dados['acidose_suspeita']= sn('  Suspeita de acidose (diabético + vômitos, insuficiência renal)? ')

    print('\n  [E — Epilepsia / Encefalopatia]')
    dados['pos_ictal']       = sn('  Suspeita de estado pós-ictal (epiléptico + convulsão relatada)? ')
    dados['encefalopatia']   = sn('  Encefalopatia hepática suspeita (hepatopata + asterixis)? ')

    print('\n  [I — Insulina / Intoxicação]')
    dados['glicemia_disponivel'] = sn('  Glicemia capilar disponível? ')
    dados['glicemia'] = _float('  Glicemia (mg/dL): ') if dados['glicemia_disponivel'] else None
    dados['intoxicacao_suspeita'] = sn('  Intoxicação suspeita (overdose, exposição a tóxico)? ')
    if dados['intoxicacao_suspeita']:
        dados['intox_tipo'] = _escolha('  Tipo mais provável: ', [
            ('opioide',        'Opioide (morfina, codeína, heroína, tramadol)'),
            ('benzo',          'Benzodiazepínico / sedativo-hipnótico'),
            ('alcool_intox',   'Álcool (intoxicação aguda grave)'),
            ('antidepressivo', 'Antidepressivo tricíclico / outros'),
            ('organofosforado','Organofosforado (agrotóxico)'),
            ('co',             'Monóxido de carbono (CO)'),
            ('desconhecido',   'Desconhecido'),
        ])
    else:
        dados['intox_tipo'] = ''

    print('\n  [O — Overdose / Oxigênio]')
    dados['hipoxia']    = sn('  SpO₂ disponível e < 92%? ')
    dados['spo2']       = _float('  SpO₂ (%): ') if dados['hipoxia'] else None

    print('\n  [U — Uremia]')
    dados['renal_cronico'] = sn('  DRC conhecida ou uremia suspeita? ')

    print('\n  [T — Trauma]')
    dados['trauma_cabeca']  = sn('  TCE recente (horas a dias)? ')
    dados['anticoagulante'] = sn('  Usa anticoagulante (risco de hematoma subdural)? ')
    if dados['trauma_cabeca']:
        dados['lucido_intervalo'] = sn('  Houve intervalo lúcido após o trauma? ')
    else:
        dados['lucido_intervalo'] = False

    print('\n  [I — Infecção]')
    dados['febre']           = sn('  Febre presente? ')
    dados['rigidez_nuca']    = sn('  Rigidez de nuca? ')
    dados['fotofobia']       = sn('  Fotofobia / cefaleia intensa? ')
    dados['foco_infeccioso'] = sn('  Foco infeccioso sistêmico grave (sepse suspeita)? ')

    print('\n  [P — Psiquiátrico / Psicogênico]')
    dados['dissociativo']   = sn('  Suspeita de crise dissociativa (psiquiátrico + movimentos atípicos + olhos fechados à abertura passiva)? ')

    print('\n  [S — Stroke / Sangramento]')
    dados['deficit_focal']   = sn('  Déficit focal novo (hemiplegia, afasia, desvio de rima)? ')
    dados['cefaleia_intensa'] = sn('  Cefaleia "a pior da vida" de início súbito? ')
    dados['pupilas_aniso']   = sn('  Anisocoria (pupilas assimétricas)? ')
    dados['hipertensao_grave']= sn('  PA ≥ 180/120 mmHg? ')

    # ── Bloco 3: Exame físico ────────────────────────────────────────
    _bloco('BLOCO 3 — Sinais vitais e exame neurológico')
    dados['pa_sistolica'] = _int('  PA sistólica (mmHg): ', 0, 300)
    dados['fc']           = _int('  FC (bpm): ', 0, 300)
    dados['fr']           = _int('  FR (ipm): ', 0, 60)
    dados['temp']         = _float('  Temperatura (°C): ')

    dados['pupila_diametro'] = _escolha('  Pupilas: ', [
        ('mioticas',   'Miose bilateral (puntiformes) — opioide, organofosforado, ponte'),
        ('midriase',   'Midríase bilateral — simpaticomiméticos, hipóxia grave'),
        ('anisocoria', 'Anisocoria — herniação, AVC, TCE'),
        ('normais',    'Normais e simétricas'),
    ])
    dados['reflexo_pupilar'] = sn('  Reflexo fotomotor presente bilateralmente? ')
    dados['asterixis']       = sn('  Asterixis (flapping tremor) presente? ')
    dados['rigidez_descer']  = sn('  Rigidez de decorticação ou descerebração? ')
    dados['babinski']        = sn('  Babinski presente? ')

    # ── Salvar ───────────────────────────────────────────────────────
    ts    = datetime.now().strftime('%Y%m%d_%H%M%S')
    pasta = os.path.join(os.path.dirname(__file__),'..','..','..','dados_pacientes')
    os.makedirs(pasta, exist_ok=True)
    arq   = os.path.join(pasta, f'consciencia_{ts}.json')
    with open(arq,'w',encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f'\n  Glasgow: {dados["glasgow_total"]}/15 | Glicemia: {dados.get("glicemia","não coletada")}')
    print(f'  [Salvo: {arq}]')
    return dados, arq

if __name__ == '__main__':
    coletar_subjetivo_consciencia()
