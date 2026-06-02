# modules/sintomas/dpoc/dpoc_subjetivo.py
import json, os, tempfile

def coletar_subjetivo_dpoc(dados_preenchidos=None):
    dados = dados_preenchidos.copy() if dados_preenchidos else {}

    def _bool(prompt, chave):
        while True:
            r = input(f'  {prompt} [s/n]: ').strip().lower()
            if r in ('s','sim','y','yes'): dados[chave]=True; return True
            if r in ('n','nao','não','no'): dados[chave]=False; return False
            print('  → s ou n.')

    def _int(prompt, chave, obrigatorio=False):
        while True:
            r = input(f'  {prompt}: ').strip()
            if not r and not obrigatorio: return None
            try: dados[chave]=int(r); return dados[chave]
            except: print('  → número inteiro.')

    def _float(prompt, chave):
        while True:
            r = input(f'  {prompt}: ').strip().replace(',','.')
            if not r: return None
            try: dados[chave]=float(r); return dados[chave]
            except: print('  → número.')

    def _escolha(prompt, chave, opcoes):
        print(f'  {prompt}')
        for k,v in opcoes.items(): print(f'    [{k}] {v}')
        while True:
            r = input('  Opção: ').strip().lower()
            if r in opcoes: dados[chave]=r; return r
            print(f'  → {list(opcoes.keys())}')

    print('\n' + '═'*60)
    print('  DPOC — Adulto Ambulatorial (GOLD 2026)')
    print('═'*60)

    if not dados.get('idade'):
        try: dados['idade'] = int(input('  Idade: ').strip())
        except: dados['idade'] = 0

    # BLOCO 1 — Tipo de consulta
    print('\n[1/5] TIPO DE CONSULTA')
    _escolha('Consulta de rotina ou piora aguda?', 'consulta_tipo', {
        'exacerbacao': 'Piora aguda — mais falta de ar, mais escarro, mudança de cor',
        'rotina':      'Rotina / controle — acompanhamento da DPOC',
    })

    if dados.get('consulta_tipo') == 'exacerbacao':
        # ── EXACERBAÇÃO ─────────────────────────────────────────────────────
        print('\n[2/5] CARACTERIZAÇÃO DA EXACERBAÇÃO (Critérios de Anthonisen)')
        _bool('Piora da dispneia em relação ao basal?', 'piora_dispneia')
        _bool('Aumento do volume de escarro?', 'aumento_volume_escarro')
        _bool('Escarro mais purulento / amarelo/esverdeado?', 'escarro_purulento')

        print('\n[3/5] GRAVIDADE')
        _float('SpO₂ (%) — se disponível [Enter = pular]', 'spo2')
        _bool('Alteração de consciência / confusão?', 'alt_consciencia')
        _bool('Hipotensão (PA sistólica < 90 mmHg)?', 'hipotensao_exac')
        _bool('Falência respiratória iminente (uso intenso de musculatura acessória)?', 'falencia_respiratoria')
        _bool('Febre presente?', 'febre_exac')

    else:
        # ── ROTINA ──────────────────────────────────────────────────────────
        print('\n[2/5] SINTOMAS (GOLD ABE)')
        print('  CAT Score — assinale quantos se aplicam (cada um = ~2 pontos):')
        _bool('Tosse frequente?', 'cat_tosse')
        _bool('Produção de escarro a maioria dos dias?', 'cat_escarro')
        _bool('Aperto/pressão no peito frequente?', 'cat_aperto')
        _bool('Falta de ar ao subir lances de escada / esforço leve?', 'cat_dispneia_leve')
        _bool('Limitação importante de atividades em casa?', 'cat_atividade')
        _bool('Não sai de casa por causa do DPOC?', 'cat_confianca')
        _bool('Sono ruim por DPOC?', 'cat_sono')
        _bool('Sem energia / muito cansado?', 'cat_energia')

        # Calcular CAT aproximado
        cat_chaves = ['cat_tosse','cat_escarro','cat_aperto','cat_dispneia_leve',
                      'cat_atividade','cat_confianca','cat_sono','cat_energia']
        cat_aprox = sum(2 for k in cat_chaves if dados.get(k))
        dados['cat_score'] = cat_aprox

        _escolha('mMRC — dispneia?', 'mmrc', {
            '0': 'Dispneia só com exercício intenso',
            '1': 'Dispneia ao andar rápido / subir ladeira',
            '2': 'Anda mais devagar que contemporâneos ou para para descansar',
            '3': 'Para para descansar após ~100m em terreno plano',
            '4': 'Muito dispneico para sair de casa',
        })
        try: dados['mmrc'] = int(dados.get('mmrc', 0))
        except: dados['mmrc'] = 0

        print('\n[3/5] EXACERBAÇÕES E ESPIROMETRIA')
        _int('Quantas exacerbações moderadas/graves no último ano?', 'exacerbacoes_ultimo_ano', obrigatorio=True)
        _bool('Alguma hospitalização por DPOC no último ano?', 'hospitalizacao_ultimo_ano')
        _float('VEF1 (% do previsto) — se espirometria disponível [Enter = pular]', 'fev1_percentual')
        _float('Eosinófilos no sangue (cél/μL) — se disponível [Enter = pular]', 'eosinofilos')
        _bool('Já diagnosticado com deficiência de alfa-1 antitripsina?', 'alfa1_diagnosticado')

    print('\n[4/5] TABAGISMO E TRATAMENTO')
    _bool('Tabagista ativo?', 'tabagismo_ativo')
    if dados.get('tabagismo_ativo'):
        _int('Carga tabágica (maços-ano = cigarros/dia ÷ 20 × anos)', 'carga_tabagica')
    else:
        _bool('Ex-tabagista?', 'ex_tabagista')

    print('\n[5/5] VACINAÇÃO E COMORBIDADES')
    _bool('Vacinado contra influenza (último ano)?', 'vacina_influenza')
    _bool('Vacinado contra pneumococo?', 'vacina_pneumococo')
    _bool('Vacinado contra RSV (se ≥ 60 anos)?', 'vacina_rsv')
    _bool('Doença cardiovascular associada?', 'doenca_cv')
    _bool('Enfisema predominantemente basal em imagem?', 'enfisema_predominio_basal')
    _bool('História familiar de DPOC / enfisema precoce?', 'historia_familiar_dpoc')

    fd, arq = tempfile.mkstemp(suffix='.json', prefix='dpoc_')
    os.close(fd)
    with open(arq, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print('\n  ✓ Dados salvos.\n')
    return dados, arq
