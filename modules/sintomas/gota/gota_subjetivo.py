# modules/sintomas/gota/gota_subjetivo.py
# Coleta de subjetivo — Gota / Artrite por Cristais de Urato
# Escopo: adulto ambulatorial

import json, os, tempfile


def coletar_subjetivo_gota(dados_preenchidos=None):
    """Coleta dados do subjetivo de gota em blocos.

    Returns:
        (dados: dict, arquivo_json: str)
    """
    dados = dados_preenchidos.copy() if dados_preenchidos else {}

    def _bool(prompt, chave):
        while True:
            r = input(f'  {prompt} [s/n]: ').strip().lower()
            if r in ('s', 'sim', 'y', 'yes'):
                dados[chave] = True
                return True
            if r in ('n', 'nao', 'não', 'no'):
                dados[chave] = False
                return False
            print('  → Digite s ou n.')

    def _float(prompt, chave, obrigatorio=False):
        while True:
            r = input(f'  {prompt}: ').strip().replace(',', '.')
            if not r and not obrigatorio:
                return None
            try:
                dados[chave] = float(r)
                return dados[chave]
            except ValueError:
                print('  → Digite um número (ex: 6.5).')

    def _int(prompt, chave, obrigatorio=False):
        while True:
            r = input(f'  {prompt}: ').strip()
            if not r and not obrigatorio:
                return None
            try:
                dados[chave] = int(r)
                return dados[chave]
            except ValueError:
                print('  → Digite um número inteiro.')

    def _texto(prompt, chave):
        r = input(f'  {prompt}: ').strip()
        if r:
            dados[chave] = r
        return r

    print('\n' + '═' * 60)
    print('  GOTA / ARTRITE POR CRISTAIS — Adulto Ambulatorial')
    print('═' * 60)

    # Idade
    idade = dados.get('idade', 0)
    if not idade:
        try:
            idade = int(input('  Idade do paciente (anos): ').strip())
            dados['idade'] = idade
        except ValueError:
            idade = 0

    # Sexo
    if 'sexo_masculino' not in dados:
        while True:
            s = input('  Sexo [M/F]: ').strip().upper()
            if s in ('M', 'MASCULINO'):
                dados['sexo_masculino'] = True
                break
            elif s in ('F', 'FEMININO'):
                dados['sexo_masculino'] = False
                break
            print('  → Digite M ou F.')

    # ──────────────────────────────────────────────────────────────
    # BLOCO 1 — Apresentação atual
    # ──────────────────────────────────────────────────────────────
    print('\n[1/6] APRESENTAÇÃO ATUAL')

    ataque_atual = _bool(
        'Paciente está em ataque articular AGORA (articulação quente/inchada/dolorosa)?',
        'ataque_atual'
    )

    if ataque_atual:
        _texto('Articulação(ões) afetada(s) [ex: 1ª MTF direita, tornozelo, joelho]', 'articulacoes')
        _int('Número de articulações afetadas', 'n_articulacoes_afetadas', obrigatorio=True)
        _bool('Início do ataque em menos de 24 horas?', 'inicio_em_1_dia')
        _bool('Vermelhidão (eritema) articular presente?', 'vermelhidao')

    _bool(
        'Tophi visíveis (nódulos duros sob a pele — cotovelos, dedos, tendão de Aquiles)?',
        'tophi_presentes'
    )

    # ──────────────────────────────────────────────────────────────
    # BLOCO 2 — Red flags (artrite séptica)
    # ──────────────────────────────────────────────────────────────
    print('\n[2/6] SINAIS DE ALARME')
    print('  (Artrite séptica e gota podem coexistir — confirme sempre)')

    _bool('Febre ≥ 38,5°C?', 'febre_385')
    _bool('Aparência tóxica / comprometimento sistêmico intenso?', 'aparencia_toxica')
    _bool('Imunossupressão (HIV, quimio, transplante, biológico)?', 'imunossupressao')

    # ──────────────────────────────────────────────────────────────
    # BLOCO 3 — Score diagnóstico (Dutch 2010 / Janssens)
    # ──────────────────────────────────────────────────────────────
    print('\n[3/6] DIAGNÓSTICO — SCORE DE JANSSENS (Dutch 2010)')

    _bool(
        'Episódio articular semelhante prévio (mesmo padrão de dor e inchaço)?',
        'ataque_previo'
    )
    _bool(
        '1ª articulação metatarsofalangeana afetada (base do dedão do pé — podagra)?',
        'articulacao_mtf1'
    )
    _bool('Hipertensão arterial ou doença cardiovascular?', 'has_ou_cardiovascular')

    _float(
        'Ácido úrico sérico (mg/dL) — se disponível [Enter = não sabe]',
        'urato_mgdl'
    )

    # ──────────────────────────────────────────────────────────────
    # BLOCO 4 — Histórico de gota
    # ──────────────────────────────────────────────────────────────
    print('\n[4/6] HISTÓRICO')

    _int(
        'Quantos ataques de gota no último ano (incluindo este, se for o caso)?',
        'n_ataques_ano', obrigatorio=True
    )
    _bool('Diagnóstico de gota já confirmado anteriormente?', 'gota_confirmada_previa')
    _bool(
        'Imagem (RX ou ultrassom) já com erosões ou duplo contorno sugestivo de gota?',
        'dano_radiografico'
    )
    _bool('Cálculo renal (urolitíase) prévio ou atual?', 'urolitiase')

    # ──────────────────────────────────────────────────────────────
    # BLOCO 5 — Função renal e medicações relevantes
    # ──────────────────────────────────────────────────────────────
    print('\n[5/6] FUNÇÃO RENAL E MEDICAÇÕES')

    egfr = _float('eGFR atual (mL/min/1.73m²) [Enter = não sabe]', 'egfr')
    if egfr is None:
        _float(
            'Creatinina sérica (mg/dL) — se eGFR não disponível [Enter = pular]',
            'creatinina'
        )

    _bool('Em uso de anticoagulante (warfarina, apixabana, rivaroxabana)?', 'anticoagulado')
    _bool('Insuficiência cardíaca?', 'icc')
    _bool('Úlcera péptica ativa?', 'dpud')
    _bool('Diabetes mellitus descontrolado?', 'dm_descontrolado')
    _bool(
        'Uso de claritromicina, eritromicina, cetoconazol, ciclosporina, tacrolimo ou verapamil?',
        'inibidor_cyp3a4_pgp'
    )

    # ──────────────────────────────────────────────────────────────
    # BLOCO 6 — ULT atual e etnia (HLA-B*5801)
    # ──────────────────────────────────────────────────────────────
    print('\n[6/6] TRATAMENTO HIPOURICEMIANTE')

    ja_usa = _bool('Já usa alopurinol ou febuxostat?', 'ja_usa_ult')
    if ja_usa:
        _texto('Qual medicamento (alopurinol / febuxostat)?', 'qual_ult')
        _float(
            'Último ácido úrico sérico em uso (mg/dL) [Enter = não sabe]',
            'urato_atual_mgdl'
        )

    _bool(
        'Origem coreana, chinesa Han ou tailandesa? '
        '(triagem HLA-B*5801 antes de alopurinol)',
        'origem_alto_risco_hlab5801'
    )

    # ──────────────────────────────────────────────────────────────
    # Salvar
    # ──────────────────────────────────────────────────────────────
    fd, arquivo = tempfile.mkstemp(suffix='.json', prefix='gota_')
    os.close(fd)
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    print('\n  ✓ Dados salvos.\n')
    return dados, arquivo
