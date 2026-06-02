# modules/sintomas/edema/edema_subjetivo.py
import json, os, tempfile

def coletar_subjetivo_edema(dados_preenchidos=None):
    dados = dados_preenchidos.copy() if dados_preenchidos else {}

    def _bool(prompt, chave):
        while True:
            r = input(f'  {prompt} [s/n]: ').strip().lower()
            if r in ('s','sim','y','yes'): dados[chave]=True; return True
            if r in ('n','nao','não','no'): dados[chave]=False; return False
            print('  → s ou n.')

    def _float(prompt, chave):
        while True:
            r = input(f'  {prompt}: ').strip().replace(',','.')
            if not r: return None
            try: dados[chave]=float(r); return dados[chave]
            except: print('  → número (ex: 6.5).')

    def _escolha(prompt, chave, opcoes):
        print(f'  {prompt}')
        for k,v in opcoes.items(): print(f'    [{k}] {v}')
        while True:
            r = input('  Opção: ').strip().lower()
            if r in opcoes: dados[chave]=r; return r
            print(f'  → {list(opcoes.keys())}')

    print('\n' + '═'*60)
    print('  EDEMA DE MEMBROS INFERIORES — Adulto Ambulatorial')
    print('═'*60)

    if not dados.get('idade'):
        try: dados['idade'] = int(input('  Idade: ').strip())
        except: dados['idade'] = 0

    # BLOCO 1 — Características do edema
    print('\n[1/5] CARACTERIZAÇÃO DO EDEMA')
    _escolha('Lateralidade:', 'lateralidade', {'unilateral':'Unilateral (só um lado)','bilateral':'Bilateral (ambos os lados)'})
    _bool('Edema de início agudo (< 72 horas)?', 'inicio_agudo')
    dados['cronico'] = not dados.get('inicio_agudo', False)
    _bool('Edema não depressível (não forma cacifo) — borrachudo/duro?', 'edema_nao_depressivel')
    _bool('Edema facial também presente?', 'edema_facial')

    # BLOCO 2 — Red flags DVT / celulite (unilateral)
    if dados.get('lateralidade') == 'unilateral':
        print('\n[2/5] AVALIAÇÃO DE TVP / CELULITE')
        _bool('Dor na panturrilha ou na coxa?', 'dor_trajeto_venoso')
        _bool('Calor e vermelhidão no membro afetado?', 'eritema_calor_local')
        if dados.get('eritema_calor_local'):
            _bool('Porta de entrada visível (ferida, micose) ou infecção prévia?', 'porta_entrada_ou_infeccao')
        _bool('Edema de toda a perna (não apenas tornozelo)?', 'edema_toda_perna')
        _bool('Panturrilha sintomática > 3 cm que a contralateral?', 'edema_panturrilha_assim')
        _bool('Veias superficiais colaterais (não varicosas) visíveis?', 'veias_colaterais')
        _bool('TVP prévia documentada?', 'tvp_previa')
        _bool('Câncer ativo em tratamento?', 'cancer_ativo')
        _bool('Imobilização prolongada ou cirurgia grande recente (< 12 semanas)?', 'repouso_cirurgia_recente')
        _bool('Diagnóstico alternativo parece mais provável que TVP?', 'diagnostico_alternativo')
    else:
        print('\n[2/5] CAUSAS SISTÊMICAS — BILATERAL')

    # BLOCO 3 — Causas sistêmicas
    print('\n[3/5] SINTOMAS SISTÊMICOS')
    _bool('Dispneia aos esforços ou ortopneia (piora deitado)?', 'dispneia_esforco')
    _bool('BNP/NT-proBNP elevado (se disponível)?', 'bnp_elevado')
    _bool('Proteinúria pesada (espuma na urina, >3,5 g/dia)?', 'proteinuria_pesada')
    _bool('Cirrose hepática conhecida?', 'cirrose_conhecida')
    _bool('Ascite presente?', 'ascite')
    _bool('Icterícia ou albumina baixa por doença hepática?', 'ictericia')
    _bool('Hiperpigmentação ou lipodermatoesclerose nas pernas?', 'hiperpigmentacao_pernas')
    _bool('Varizes visíveis?', 'varizes')
    _bool('Pele espessada/mixedema pré-tibial?', 'mixedema_pretibial')
    _bool('TSH elevado confirmado?', 'tsh_elevado')
    if dados.get('tsh_elevado'):
        _float('Valor do TSH (mUI/L)?', 'tsh_valor')
    _bool('Cirurgia de linfonodos (axila/inguinal) ou radioterapia prévia?', 'cirurgia_linfonodos')

    # BLOCO 4 — Medicamentos
    print('\n[4/5] MEDICAMENTOS')
    _bool('Bloqueador de canal de cálcio (anlodipino, nifedipino)?', 'usa_bcc')
    _bool('AINE regularmente?', 'usa_aine')
    _bool('Corticoide sistêmico?', 'usa_corticoide')
    _bool('Gabapentina ou pregabalina?', 'usa_gabapentina')
    _bool('Pioglitazona ou similar?', 'usa_tiazolidiona')
    _bool('Hormônio (estrogênio, testosterona)?', 'usa_hormonio')

    # BLOCO 5 — Comorbidades
    print('\n[5/5] COMORBIDADES')
    _bool('Hipoalbuminemia por desnutrição?', 'hipoalbuminemia')
    _bool('Sinais sistêmicos de doença (febre, emagrecimento)?', 'sinais_sistemicos')
    _bool('Apneia do sono (STOP-BANG ≥ 3 ou diagnóstico confirmado)?', 'apneia_sono')

    fd, arq = tempfile.mkstemp(suffix='.json', prefix='edema_')
    os.close(fd)
    with open(arq, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print('\n  ✓ Dados salvos.\n')
    return dados, arq
