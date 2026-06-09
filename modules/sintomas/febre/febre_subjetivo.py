# modules/sintomas/febre/febre_subjetivo.py
# Coleta de subjetivo — Febre sem Foco
# Escopo: adulto imunocompetente, ambulatório

import json, os, tempfile


def coletar_subjetivo_febre(dados_preenchidos=None):
    """Coleta dados do subjetivo de febre em blocos.

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
                print('  → Digite um número (ex: 38.5).')

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

    def _escolha(prompt, chave, opcoes: dict):
        print(f'  {prompt}')
        for k, v in opcoes.items():
            print(f'    [{k}] {v}')
        while True:
            r = input('  Opção: ').strip().lower()
            if r in opcoes:
                dados[chave] = r
                return r
            print(f'  → Opções válidas: {list(opcoes.keys())}')

    def _texto(prompt, chave):
        r = input(f'  {prompt}: ').strip()
        if r:
            dados[chave] = r
        return r

    print('\n' + '═' * 60)
    print('  FEBRE SEM FOCO — Adulto Imunocompetente (Ambulatório)')
    print('═' * 60)

    # Guard etário — módulo exclusivo para adultos
    idade = dados.get('idade', 0)
    if not idade:
        try:
            idade = int(input('  Idade do paciente (anos): ').strip())
            dados['idade'] = idade
        except ValueError:
            idade = 0
    if idade > 0 and idade < 18:
        print(f'\n  ⚠️  ATENÇÃO: Paciente pediátrico ({idade} anos).')
        print('  Este módulo é exclusivo para adultos (≥ 18 anos).')
        print('  Crianças < 3 meses → PS imediato.')
        print('  Crianças ≥ 3 meses → algoritmo pediátrico específico (não implementado).')
        confirmar = input('\n  Prosseguir mesmo assim? [s/N]: ').strip().lower()
        if confirmar not in ('s', 'sim'):
            raise SystemExit('Módulo encerrado — paciente pediátrico.')

    # ──────────────────────────────────────────────────────────────
    # BLOCO 1 — Temperatura e duração
    # ──────────────────────────────────────────────────────────────
    print('\n[1/7] TEMPERATURA E DURAÇÃO')
    _float('Temperatura máxima registrada (°C) [Enter = não sabe]', 'temperatura_max')
    if 'temperatura_max' not in dados:
        dados['temperatura_max'] = 38.5   # assumir febre presente (paciente veio com febre)

    _int('Há quantos dias com febre?', 'dias_febre', obrigatorio=True)

    _bool('Calafrio com rigor (tremor intenso)?', 'calafrio_rigor')
    _bool('Sudorese noturna intensa?', 'sudorese_noturna')

    # ──────────────────────────────────────────────────────────────
    # BLOCO 2 — Red flags (checar SEMPRE em primeiro lugar)
    # ──────────────────────────────────────────────────────────────
    print('\n[2/7] SINAIS DE ALARME')
    print('  (Responda com sinceridade — determinam encaminhamento imediato)')

    _bool('Petéquias ou púrpura (manchas vermelhas/roxas que não somem à pressão)?', 'peticuias_purpura')
    _bool('Rigidez de nuca (dificuldade de encostar o queixo no peito)?', 'rigidez_nuca')
    _bool('Hipotensão (PA sistólica < 90 mmHg ou tontura intensa ao levantar)?', 'hipotensao')
    _bool('Frequência cardíaca ≥ 120 bpm em repouso?', 'taquicardia_fc_120')
    _bool('Alteração de consciência (confusão, desorientação, sonolência excessiva)?', 'alt_consciencia')
    _bool('Aparência geral comprometida (parece muito grave clinicamente)?', 'aparencia_toxica')

    # ──────────────────────────────────────────────────────────────
    # BLOCO 3 — Imunidade
    # ──────────────────────────────────────────────────────────────
    print('\n[3/7] ESTADO IMUNOLÓGICO')

    _bool('Imunossupressão grave (HIV avançado, quimioterapia, transplante, biológico)?', 'imunossupressao_grave')
    _bool('Corticoide sistêmico em dose alta (≥ 20 mg/dia por ≥ 2 semanas)?', 'corticoide_cronico_alto')
    _bool('Asplenia (esplenectomia cirúrgica ou anemia falciforme)?', 'asplenia')
    _bool('Neutropenia conhecida (ANC < 500)?', 'neutropenia')

    # ──────────────────────────────────────────────────────────────
    # BLOCO 4 — Foco sintomático
    # ──────────────────────────────────────────────────────────────
    print('\n[4/7] SINTOMAS LOCALIZATÓRIOS')
    print('  (Identificar se existe foco que direcione para outro módulo)')

    _bool('Odinofagia ou dor de garganta como queixa principal?', 'foco_faringeo')
    _bool('Tosse, dispneia ou dor torácica?', 'foco_respiratorio')
    _bool('Disúria, polaciúria ou dor lombar/flanco?', 'foco_urinario')
    _bool('Diarreia, vômito ou dor abdominal?', 'foco_gi')
    _bool('Lesão de pele, celulite ou abscesso?', 'foco_pele_partes_moles')
    _bool('Artralgia ou artrite (articulação quente/inchada)?', 'artralgia_artrite')

    tem_exantema = _bool('Rash ou exantema?', 'exantema')
    if tem_exantema:
        _escolha('Tipo de exantema:', 'exantema_tipo', {
            'maculopapular': 'Maculopapular (manchas e pápulas difusas)',
            'petequial':     'Petequial (pontos vermelhos que não somem)',
            'vesicular':     'Vesicular (bolhinhas)',
            'eritema_migrans': 'Eritema migrans / em alvo (anel expansivo)',
            'outro':         'Outro / não identificado',
        })

    # ──────────────────────────────────────────────────────────────
    # BLOCO 5 — Contexto epidemiológico
    # ──────────────────────────────────────────────────────────────
    print('\n[5/7] CONTEXTO EPIDEMIOLÓGICO')

    viagem = _bool('Viagem recente a área endêmica (malária, dengue, febre tifoide)?', 'viagem_area_endemica')
    if viagem:
        _texto('Destino da viagem (país/região)', 'destino_viagem')

    _bool('Contato com animais (fazenda, morcego, roedor, cão/gato com doença)?', 'contato_animal')
    _bool('Picada de carrapato ou inseto nas últimas semanas?', 'picada_carrapato_inseto')
    _bool('Internação hospitalar nos últimos 30 dias?', 'internacao_recente_30d')
    _bool('Uso de antibiótico nos últimos 3 meses?', 'uso_atb_recente')
    _bool('Contato com caso de tuberculose?', 'contato_tb')

    # ──────────────────────────────────────────────────────────────
    # BLOCO 6 — Exames disponíveis
    # ──────────────────────────────────────────────────────────────
    print('\n[6/7] EXAMES (se já disponíveis)')

    tem_labs = _bool('Há exames laboratoriais recentes disponíveis?', 'labs_disponiveis')
    if tem_labs:
        _float('Leucócitos (células/mm³, ex: 12000) [Enter = não]', 'leucocitos')
        _float('Neutrófilos absolutos — ANC (ex: 1500) [Enter = não]', 'neutrofilos_abs')
        _float('PCR (mg/L, ex: 45.0) [Enter = não]', 'pcr_mgL')
        _float('VHS (mm/h, ex: 60) [Enter = não]', 'vhs')
        _bool('Hemoculturas coletadas?', 'hemoculturas_feitas')

    # ──────────────────────────────────────────────────────────────
    # BLOCO 7 — Comorbidades relevantes para risco
    # ──────────────────────────────────────────────────────────────
    print('\n[7/7] COMORBIDADES')

    _bool('Diabetes mellitus?', 'dm')
    _bool('Doença renal crônica?', 'drc')
    _bool('Insuficiência cardíaca?', 'icc')
    _bool('Cirrose hepática?', 'cirrose')

    # ──────────────────────────────────────────────────────────────
    # Salvar
    # ──────────────────────────────────────────────────────────────
    fd, arquivo = tempfile.mkstemp(suffix='.json', prefix='febre_')
    os.close(fd)
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    print('\n  ✓ Dados salvos.\n')
    return dados, arquivo
