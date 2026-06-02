# ui/schemas.py
# Definição de campos por módulo para a interface web.
#
# Para adicionar um módulo novo:
#   1. Adicione uma entrada em MODULE_SCHEMAS com o nome do módulo (igual ao dispatcher)
#   2. Defina os blocos e campos
#   3. Pronto — a interface renderiza automaticamente
#
# Tipos de campo:
#   bool     → checkbox
#   select   → selectbox com opções
#   number   → number_input (obrigatório digitar)
#   text     → text_input
#
# Propriedades opcionais:
#   depends_on: 'chave'  → só aparece se o campo indicado for True/truthy
#   flag: 'red'          → destaca o campo em vermelho (red flag clínico)
#   flag: 'yellow'       → destaca em amarelo (atenção)
#   negative: True       → quando desmarcado, aparece em "Nega:" no SOAP
#   default              → valor padrão (None = não perguntado ainda)
#
# Sistema de 3 estados para bool:
#   None  → campo não foi ainda respondido (não aparece no SOAP)
#   True  → positivo (aparece em achados)
#   False → explicitamente negado (aparece em "Nega: ..." no SOAP)
#
# Campos com flag='red' ou negative=True geram negativas pertinentes quando False.
# Campos sem negative não geram negativa quando desmarcados.

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS DE CAMPO
# ─────────────────────────────────────────────────────────────────────────────

def _bool(key, label, flag=None, depends_on=None, default=None, negative=None, help=None):
    """
    default=None  → campo começa "não perguntado" (sem tick e sem negativa)
    negative=True → quando False, aparece em "Nega:" do SOAP
    help=...      → tooltip (ⓘ) explicando a manobra / o achado
    Campos com flag='red' têm negative=True automaticamente.
    """
    f = {'key': key, 'type': 'bool', 'label': label, 'default': default}
    if flag:       f['flag'] = flag
    if depends_on: f['depends_on'] = depends_on
    if help:       f['help'] = help
    # Red flags geram negativa automaticamente; ou pode ser definido explicitamente
    neg = negative if negative is not None else (flag == 'red')
    if neg:        f['negative'] = True
    return f

def _num(key, label, min_val=0, max_val=999, step=1, default=None, depends_on=None, flag=None, help=None):
    f = {'key': key, 'type': 'number', 'label': label,
         'min': min_val, 'max': max_val, 'step': step, 'default': default}
    if flag:       f['flag'] = flag
    if depends_on: f['depends_on'] = depends_on
    if help:       f['help'] = help
    return f

def _sel(key, label, options, default=None, depends_on=None):
    return {'key': key, 'type': 'select', 'label': label,
            'options': options, 'default': default or options[0][0],
            **(({'depends_on': depends_on}) if depends_on else {})}

def _block(title, fields, flag=None):
    b = {'title': title, 'fields': fields}
    if flag: b['flag'] = flag
    return b


# ─────────────────────────────────────────────────────────────────────────────
# SCHEMAS DOS MÓDULOS
# ─────────────────────────────────────────────────────────────────────────────

MODULE_SCHEMAS = {

    # ── CELULITE / ERISIPELA ─────────────────────────────────────────────────
    'celulite': {
        'label': 'Celulite / Erisipela',
        'sistema': 'Infectologia',
        'blocks': [
            _block('Localização + Evolução', [
                _sel('localizacao', 'Localização', [
                    ('mmii_unilateral','MMII unilateral'), ('mmii_bilateral','MMII bilateral'),
                    ('face','Face'), ('pe','Pé'), ('mao_braco','Mão/Braço'),
                    ('tronco','Tronco'), ('outro','Outro'),
                ]),
                _sel('tempo_evolucao', 'Tempo de evolução', [
                    ('horas','< 24h'), ('um_a_dois_dias','1–2 dias'),
                    ('tres_a_cinco_dias','3–5 dias'), ('mais_cinco_dias','> 5 dias'),
                ]),
            ]),
            _block('Porta de Entrada', [
                _bool('tinea_pedis',       'Tinea pedis / micose interdigital', negative=True),
                _bool('ferida_ulcera',     'Ferida, úlcera ou fissura',         negative=True),
                _bool('uso_drogas_iv',     'Uso de drogas IV',        flag='red'),
                _bool('trauma_penetrante', 'Trauma penetrante',                 negative=True),
                _bool('pe_diabetico',      'Pé diabético',            flag='yellow', negative=True),
                _bool('mordedura_animal',  'Mordedura / imersão em água'),
            ]),
            _block('Hemodinâmica + SIRS', [
                _bool('febre',      'Febre > 38°C',                 negative=True),
                _num ('temp_celsius','Temperatura (°C)', 36.0, 42.0, 0.1, depends_on='febre'),
                _bool('taquicardia','FC > 90 bpm',                  negative=True),
                _bool('taquipneia', 'FR > 20 ipm',                  negative=True),
                _bool('hipotensao', 'Hipotensão / instabilidade', flag='red'),
            ]),
            _block('Sinais Locais', [
                _bool('borda_nitida',         'Borda bem demarcada (erisipela)'),
                _bool('flutuacao',            'Flutuação / abscesso'),
                _bool('bolhas',               'Bolhas tensas'),
                _bool('bolhas_hemorragicas',  'Bolhas hemorrágicas / necróticas', flag='red'),
                _bool('crepitacao',           '⚠ CREPITAÇÃO',       flag='red'),
                _bool('necrose',              '⚠ Necrose / pele violácea', flag='red'),
                _bool('dor_desproporcional',  '⚠ Dor desproporcional ao EF', flag='red'),
                _bool('progressao_rapida',    'Progressão rápida apesar de ATB', flag='red'),
                _bool('linfangite',           'Estria vermelha subindo',        negative=True),
            ]),
            _block('Comorbidades', [
                _bool('diabetes',       'Diabetes mellitus'),
                _bool('imunossupressao','Imunossupressão / quimioterapia', flag='yellow'),
                _bool('neutropenia',    'Neutropenia',                     flag='red'),
                _bool('linfedema',      'Linfedema'),
                _bool('insuf_venosa',   'Insuficiência venosa crônica'),
                _bool('malignidade',    'Malignidade ativa',               flag='yellow'),
            ]),
            _block('Risco MRSA', [
                _bool('mrsa_colonizacao',        'MRSA conhecido / prévio'),
                _bool('mrsa_internacao_recente', 'Internação recente < 3 meses'),
                _bool('drenagem_purulenta',      'Drenagem purulenta'),
                _bool('falha_beta_lactamico',    'Falha em beta-lactâmico recente'),
            ]),
            _block('Histórico + Alergias', [
                _num ('episodios_anteriores','Episódios no último ano', 0, 20, 1, 0),
                _sel ('alergia_penicilina','Alergia a Penicilina', [
                    ('nenhuma','Nenhuma'),
                    ('nao_anafilatica','Não anafilática (rash)'),
                    ('anafilatica','Anafilática (urticária/choque)'),
                ]),
            ]),
            _block('Labs para LRINEC (se disponíveis)', [
                _num('pcr',        'PCR (mg/L)',     0, 999, 1),
                _num('leucocitos', 'Leucócitos (/μL)',0,100000,100),
                _num('hb',         'Hemoglobina (g/dL)',0,25,0.1),
                _num('sodio',      'Sódio (mEq/L)', 110,165,1),
                _num('creatinina', 'Creatinina (mg/dL)',0,30,0.1),
                _num('glicemia',   'Glicemia (mg/dL)',0,999,1),
            ]),
        ],
        'engine': 'modules.raciocinio.celulite.engine_celulite',
        'engine_fn': 'analisar_celulite',
    },

    # ── HEMORRAGIA DIGESTIVA ─────────────────────────────────────────────────
    'hemorragia': {
        'label': 'Hemorragia Digestiva (HDA / HDB)',
        'sistema': 'Gastro/Abdominal',
        'blocks': [
            _block('Tipo de Sangramento', [
                _sel('tipo_sangramento', 'Como se apresenta?', [
                    ('hematemese',   'Hematêmese — vômito com sangue vivo'),
                    ('borra_cafe',   'Hematêmese em borra de café'),
                    ('melena',       'Melena — fezes pretas/alcatronadas'),
                    ('hematoquezia', 'Hematoquezia — sangue vivo nas fezes'),
                    ('marrom_escuro','Fezes marrom-escuras'),
                    ('papel_apenas', 'Sangue apenas no papel higiênico'),
                ]),
            ]),
            _block('Hemodinâmica', [
                _num ('pas',  'PA sistólica (mmHg)', 50, 250, 1, 120, flag='red'),
                _num ('fc',   'FC (bpm)',             30, 200, 1, 75),
                _bool('sincope',          'Síncope / pré-síncope', flag='red'),
                _bool('palidez_sudorese', 'Palidez extrema / sudorese fria'),
            ]),
            _block('HDA — Glasgow-Blatchford (se melena/hematêmese)', [
                _num ('bun', 'BUN (mg/dL — 0 se indisponível)', 0, 500, 1, 0),
                _num ('hb',  'Hemoglobina (g/dL)', 3, 25, 0.1, 13.0),
                _sel ('sexo','Sexo', [('masculino','Masculino'),('feminino','Feminino')]),
                _bool('hepatopatia_gbs', 'Hepatopatia / cirrose / HTP'),
                _bool('icc',             'Insuficiência cardíaca (ICC)'),
            ]),
            _block('HDA — Risco Variceal', [
                _bool('cirrose',         'Cirrose conhecida',         flag='yellow'),
                _bool('estigmas_htpor',  'Estigmas de HTP (ascite, spider nevi, esplenomegalia)'),
                _bool('varizes_previas', 'Varizes esofágicas prévias'),
                _bool('alcool_cronico',  'Uso crônico de álcool'),
            ]),
            _block('HDB — Oakland Score (se hematoquezia)', [
                _num ('idade',     'Idade (anos)',    18, 100, 1, 40),
                _bool('lgib_previo','Internação prévia por HDB'),
                _bool('dre_sangue','Toque retal com sangue no dedo'),
            ]),
            _block('HDB — Pistas Etiológicas', [
                _bool('dor_evacuacao',   'Dor à evacuação / dor anal (fissura?)'),
                _bool('papel_apenas',    'Sangue só no papel (hemorroida?)'),
                _bool('diarreia_sangue', 'Diarreia com sangue (colite?)'),
                _bool('dor_abdominal',   'Dor abdominal associada'),
                _bool('febre',           'Febre'),
                _bool('atb_recente',     'Antibiótico nos últimos 3 meses (C. diff?)'),
                _bool('mudanca_habito',  'Mudança de hábito intestinal',  flag='red'),
                _bool('perda_peso',      'Perda de peso não intencional', flag='red'),
                _bool('dii_conhecida',   'DII conhecida (Crohn/RCUI)'),
                _bool('dcv_dm',          'DM / aterosclerose / vasculopatia'),
                _bool('pos_polipectomia','Polipectomia recente (< 30 dias)'),
            ]),
            _block('Anticoagulação', [
                _bool('anticoagulado', 'Em uso de anticoagulante', flag='yellow'),
                _sel ('anticoagulante','Qual anticoagulante?', [
                    ('varfarina','Varfarina'),('apixabana','Apixabana'),
                    ('rivaroxabana','Rivaroxabana'),('dabigatrana','Dabigatrana'),
                    ('hbpm','HBPM'),('outro','Outro'),
                ], depends_on='anticoagulado'),
            ]),
            _block('Contexto HDA', [
                _bool('aine_asa',    'Uso de AINE / AAS'),
                _bool('hp_conhecido','H. pylori conhecido'),
                _bool('pud_previo',  'Úlcera péptica prévia'),
                _bool('dcv',         'Doença cardiovascular (IAM/AVC prévio)', flag='yellow'),
            ]),
        ],
        'engine': 'modules.raciocinio.hemorragia.engine_hemorragia',
        'engine_fn': 'analisar_hemorragia',
    },

    # ── PALPITAÇÃO ───────────────────────────────────────────────────────────
    'palpitacao': {
        'label': 'Palpitação / Arritmia',
        'sistema': 'Cardiovascular',
        'blocks': [
            _block('Emergência — Verificar Primeiro', [
                _bool('instabilidade_hemodinamica','⚠ INSTABILIDADE HEMODINÂMICA', flag='red'),
                _bool('sincope',         '⚠ Síncope associada',                   flag='red'),
                _bool('dispneia_grave',  'Dispneia em repouso',                    flag='red'),
                _bool('dor_toracica',    'Dor torácica associada',                 flag='yellow'),
            ]),
            _block('Caracterização do Ritmo', [
                _sel('ritmo_percebido','Como sente?', [
                    ('acelerado_regular',   'Coração acelerado e regular'),
                    ('acelerado_irregular', 'Coração acelerado e irregular (FA?)'),
                    ('batida_extra',        'Batida extra / flip (extrassistolia?)'),
                    ('pausa',              'Pausa / coração para'),
                    ('forte_mas_normal',   'Forte mas ritmo normal'),
                    ('indeterminado',      'Difícil caracterizar'),
                ]),
                _bool('inicio_subito',   'Início súbito'),
                _bool('termino_subito',  'Término súbito'),
                _sel ('duracao_episodio','Duração', [
                    ('segundos','Segundos'),('minutos','Minutos'),
                    ('horas','Horas'),('persistente','Persistente/contínuo'),
                ]),
            ]),
            _block('ECG', [
                _sel('ecg_ritmo','Ritmo no ECG', [
                    ('desconhecido','Não realizado / desconhecido'),
                    ('normal',     'Normal / sinusal'),
                    ('fa',         'FA — Fibrilação atrial'),
                    ('flutter',    'Flutter atrial'),
                    ('tsv',        'TSV — QRS estreito'),
                    ('tsv_qrs_largo','Taquicardia QRS largo'),
                    ('wpw',        'Delta wave / WPW'),
                    ('extrassist', 'Extrassistolia'),
                    ('qt_longo',   'QT longo'),
                    ('brugada',    'Brugada pattern'),
                ]),
                _bool('ecg_bve',         'BVE / BCRE'),
                _bool('ecg_wpw',         'Delta wave confirmada'),
                _bool('ecg_qt_longo',    'QT longo confirmado'),
                _bool('ecg_brugada',     'Brugada confirmado', flag='red'),
            ]),
            _block('Histórico Cardíaco', [
                _bool('fa_suspeita',         'FA — suspeita neste episódio'),
                _bool('fa_conhecida',        'FA — diagnóstico prévio'),
                _bool('cardiopatia_estrutural','Cardiopatia estrutural conhecida', flag='yellow'),
                _bool('wpw_suspeita',        'WPW suspeito',                      flag='red'),
                _bool('tv_suspeita',         'TV suspeita',                       flag='red'),
                _bool('brugada_suspeito',    'Brugada suspeito',                  flag='red'),
                _bool('qt_longo_suspeito',   'QT longo suspeito',                 flag='red'),
                _bool('tsv_suspeita',        'TSV paroxística'),
                _bool('extrassistolia_suspeita','Extrassistolia benigna'),
                _bool('morte_subita_familiar','Morte súbita familiar'),
            ]),
            _block('Causas Secundárias', [
                _bool('causa_secundaria_suspeita','Causa secundária suspeita'),
                _bool('sintomas_tireoide',    'Sintomas de tireoide (perda peso, calor, tremor)'),
                _bool('sintomas_anemia',      'Sintomas de anemia'),
                _bool('sintomas_ansiedade',   'Ansiedade / ataques de pânico'),
                _bool('gatilho_estresse',     'Gatilho emocional / estresse'),
                _bool('uso_cocaina_estimulante','Uso de cocaína / estimulante', flag='red'),
                _bool('uso_simpaticomimatico','Uso de simpaticomiméticos / cafeína'),
            ]),
            _block('Anticoagulação (se FA)', [
                _num ('cha2ds2_score','CHA₂DS₂-VASc score', 0, 9, 1, 0),
                _bool('anticoagulacao_indicada','Anticoagulação já indicada'),
                _bool('sexo_feminino','Sexo feminino'),
            ]),
        ],
        'engine': 'modules.raciocinio.palpitacao.engine_palpitacao',
        'engine_fn': 'analisar_palpitacao',
    },

    # ── URINÁRIO ─────────────────────────────────────────────────────────────
    'urinario': {
        'label': 'Queixa Urinária (ITU / Pielonefrite)',
        'sistema': 'Urologia',
        'blocks': [
            _block('Sintomas Urinários', [
                _bool('disuria',         'Disúria / ardência ao urinar'),
                _bool('urgencia_miccional','Urgência miccional'),
                _bool('polaciuria',      'Polaciúria (frequência aumentada)'),
                _bool('hematuria',       'Hematúria (sangue na urina)'),
                _bool('hematuria_macroscopica','Hematúria macroscópica visível', flag='yellow'),
                _bool('descarga_uretral','Descarga uretral / corrimento'),
            ]),
            _block('Sinais Sistêmicos', [
                _bool('febre',       'Febre',                           flag='yellow'),
                _bool('calafrio',    'Calafrio / tremores',             flag='yellow'),
                _bool('ppd_positivo','Punho-percussão lombar positiva', flag='yellow'),
                _bool('dor_lombar',  'Dor lombar / flancos'),
                _bool('nausea_vomito','Náusea / vômito'),
            ]),
            _block('Contexto', [
                _sel ('sexo','Sexo', [
                    ('feminino','Feminino'),
                    ('masculino','Masculino'),
                ]),
                _num ('idade','Idade (anos)', 18, 100, 1, 35),
                _bool('gestante',        'Gestante',               flag='yellow'),
                _bool('dm',              'Diabetes mellitus'),
                _bool('imunossuprimido', 'Imunossuprimido'),
                _bool('sonda_vesical',   'Sonda vesical',          flag='yellow'),
                _bool('itu_recorrente',  'ITU recorrente (≥2/ano)'),
                _bool('parceiro_risco',  'Parceiro com DST / relação desprotegida'),
            ]),
            _block('Alergias', [
                _sel ('alergia_atb','Alergia a antibiótico', [
                    ('nenhuma','Nenhuma'),
                    ('sulfa','Sulfa / SMX-TMP'),
                    ('quinolona','Quinolonas'),
                    ('beta_lactamico','Beta-lactâmico'),
                ]),
            ]),
        ],
        'engine': 'modules.raciocinio.urinario.engine_urinario',
        'engine_fn': 'interpretar_queixa_urinaria',
    },

    # ── IVAS ─────────────────────────────────────────────────────────────────
    'ivas': {
        'label': 'IVAS / Faringoamigdalite',
        'sistema': 'Infectologia',
        'blocks': [
            _block('Queixa Principal', [
                _bool('odinofagia',    'Odinofagia (dor de garganta)'),
                _bool('coriza',        'Coriza / obstrução nasal'),
                _bool('tosse',         'Tosse'),
                _bool('rouquidao',     'Rouquidão'),
                _bool('otalgia',       'Otalgia (dor de ouvido)'),
            ]),
            _block('Critérios de Centor', [
                _bool('exsudato',      'Exsudato em amígdalas',              flag='yellow'),
                _bool('linfonodos',    'Linfonodomegalia cervical anterior',  flag='yellow'),
                _bool('febre',         'Febre (história ou aferida)'),
                _bool('sem_tosse',     'Ausência de tosse'),
            ]),
            _block('Red Flags', [
                _bool('trismo',        '⚠ Trismo (dificuldade abrir boca)', flag='red'),
                _bool('voz_batata',    '⚠ Voz de batata quente',           flag='red'),
                _bool('desvio_uvula',  '⚠ Desvio da úvula',                flag='red'),
                _bool('estridor',      '⚠ Estridor / dificuldade respirar', flag='red'),
                _bool('sialorreia',    '⚠ Sialorreia',                      flag='red'),
                _bool('rouquidao_3sem','Rouquidão > 3 semanas',             flag='yellow'),
            ]),
            _block('Contexto', [
                _num ('idade','Idade (anos)', 3, 100, 1, 25),
                _bool('alergia_penicilina','Alergia à Penicilina'),
                _bool('fra_previo',       'Febre Reumática prévia',        flag='yellow'),
                _bool('imunossuprimido',  'Imunossuprimido'),
                _bool('mononucleose_suspeita','Mononucleose suspeita (esplenomegalia, fadiga extrema)'),
            ]),
        ],
        'engine': 'modules.raciocinio.ivas.engine_ivas',
        'engine_fn': 'interpretar_ivas',
    },

    # ── SÍNCOPE ──────────────────────────────────────────────────────────────
    'sincope': {
        'label': 'Síncope / Pré-síncope',
        'sistema': 'Cardiovascular',
        'blocks': [
            _block('1 · O Episódio', [
                _bool('perda_consciencia_completa','Perda COMPLETA de consciência (não só tontura)'),
                _bool('recuperacao_rapida',        'Recuperação rápida e espontânea (< 1 min, sem confusão)'),
                _bool('sincope_esforco',           '⚠ Durante ou logo após esforço físico', flag='red',
                      help='Síncope ao esforço = red flag cardíaco (estenose aórtica, CMHO). Exige investigação.'),
                _bool('sintomas_ao_levantar',      'Ao levantar da cama / sentar (ortostática?)'),
                _bool('mordedura_lingua',          'Mordida LATERAL de língua (sugere convulsão)',
                      help='Mordida lateral → convulsão; mordida na ponta → síncope. Lateral é mais específica de crise.'),
                _bool('incontinencia',             'Incontinência urinária/fecal no episódio'),
                _bool('pos_convulsao',             'Confusão prolongada após (pós-ictal > 30s)'),
            ]),
            _block('2 · Pródromo e Gatilho', [
                _bool('prodrome_nausea_diaforese','Náusea / suor frio antes (pródromo vagal)'),
                _bool('prodrome_visual',          'Escurecimento / visão turva antes'),
                _bool('prodrome_calor',           'Sensação de calor / rubor antes'),
                _bool('gatilho_posicional',       'De pé prolongado / ambiente quente e lotado'),
                _bool('gatilho_emocional',        'Emoção intensa como gatilho'),
                _bool('gatilho_dor_flebotomia',   'Dor / visão de sangue / punção como gatilho'),
                _bool('gatilho_miccao',           'Após urinar (situacional)'),
                _bool('gatilho_defecacao',        'Após defecar (situacional)'),
                _bool('gatilho_tosse_deglut',     'Após tossir / deglutir (situacional)'),
                _bool('gatilho_carotideo',        'Ao virar pescoço / colarinho apertado (seio carotídeo)'),
            ]),
            _block('3 · Sinais de Alarme (red flags)', [
                _bool('sincope_com_dor_toracica',  '⚠ Dor torácica associada', flag='red'),
                _bool('sincope_com_dispneia',      '⚠ Dispneia associada', flag='red'),
                _bool('palpitacao_antes',          '⚠ Palpitações imediatamente antes', flag='red'),
                _bool('doenca_estrutural_cardiaca','⚠ Cardiopatia estrutural (IC, EAo, DAC, CMHO)', flag='red'),
                _bool('historia_familiar_morte_subita','⚠ Morte súbita familiar 1º grau < 50a', flag='red'),
                _bool('deficit_focal',             '⚠ Déficit neurológico focal após', flag='red'),
            ]),
            _block('4 · ECG e Pressão Arterial', [
                _bool('ecg_realizado',     'ECG já realizado'),
                _bool('ecg_qtc_maior_480', '⚠ QTc > 480 ms', flag='red', depends_on='ecg_realizado'),
                _bool('ecg_qrs_maior_130', 'QRS > 130 ms', depends_on='ecg_realizado'),
                _bool('ecg_brugada',       '⚠ Padrão Brugada (ST V1-V3)', flag='red', depends_on='ecg_realizado'),
                _bool('ecg_preexcitacao',  '⚠ Pré-excitação (WPW)', flag='red', depends_on='ecg_realizado'),
                _bool('ecg_bav3',          '⚠ BAV 3º grau ou BRE novo', flag='red', depends_on='ecg_realizado'),
                _bool('ecg_arritmia_vent', '⚠ Arritmia ventricular documentada', flag='red', depends_on='ecg_realizado'),
                _bool('pa_ortostatica_medida','PA ortostática medida (deitado→1min→3min)'),
                _bool('queda_pas_20',      'Queda PAS ≥ 20 mmHg ao ortostatismo', depends_on='pa_ortostatica_medida'),
                _bool('queda_pad_10',      'Queda PAD ≥ 10 mmHg ao ortostatismo', depends_on='pa_ortostatica_medida'),
                _bool('pa_anormal',        'PAS ≤ 90 ou > 180 mmHg no episódio', flag='yellow'),
                _bool('troponina_elevada', '⚠ Troponina elevada (se coletada)', flag='red'),
            ]),
            _block('5 · Histórico e Medicações', [
                _bool('predisposicao_vasovagal',     'Episódios vasovagais prévios documentados'),
                _bool('medicamento_hipotensor_em_uso','Anti-hipertensivo / diurético / alfa-bloqueador'),
                _bool('diabetes',                    'Diabetes (neuropatia autonômica)'),
                _bool('parkinson',                   'Doença de Parkinson (disautonomia)'),
                _bool('desidratacao_clinica',        'Sinais de desidratação'),
                _bool('doenca_cardiaca_conhecida',   'Doença cardíaca/arritmia conhecida', flag='yellow'),
            ]),
        ],
        'engine': 'modules.raciocinio.sincope.engine_sincope',
        'engine_fn': 'interpretar_sincope',
    },

    # ── FEBRE SEM FOCO ───────────────────────────────────────────────────────
    'febre': {
        'label': 'Febre sem Foco',
        'sistema': 'Infectologia',
        'blocks': [
            _block('1 · Temperatura e Duração', [
                _num ('temperatura_max','Temperatura máxima (°C)', 36.0, 42.5, 0.1, 38.5),
                _num ('dias_febre',     'Há quantos dias com febre?', 0, 365, 1, 2,
                      help='< 7d aguda · 7–21d subaguda · > 21d (3 sem) = FOI / origem indeterminada.'),
                _bool('calafrio_rigor',   'Calafrio com rigor (tremor intenso)'),
                _bool('sudorese_noturna', 'Sudorese noturna intensa', flag='yellow'),
            ]),
            _block('2 · Sinais de Alarme (checar primeiro)', [
                _bool('peticuias_purpura','⚠ Petéquias / púrpura (não somem à pressão)', flag='red'),
                _bool('rigidez_nuca',     '⚠ Rigidez de nuca', flag='red'),
                _bool('hipotensao',       '⚠ Hipotensão (PAS < 90 / tontura ao levantar)', flag='red'),
                _bool('taquicardia_fc_120','⚠ FC ≥ 120 bpm em repouso', flag='red'),
                _bool('alt_consciencia',  '⚠ Alteração de consciência', flag='red'),
                _bool('aparencia_toxica', '⚠ Aparência toxêmica (parece muito grave)', flag='red'),
            ]),
            _block('3 · Estado Imunológico', [
                _bool('imunossupressao_grave','Imunossupressão grave (HIV avançado/QT/transplante)', flag='red'),
                _bool('corticoide_cronico_alto','Corticoide alto (≥ 20 mg/d ≥ 2 sem)', flag='yellow'),
                _bool('asplenia',         'Asplenia (esplenectomia / falciforme)', flag='yellow'),
                _bool('neutropenia',      '⚠ Neutropenia (ANC < 500)', flag='red'),
            ]),
            _block('4 · Sintomas Localizatórios (busca de foco)', [
                _bool('foco_faringeo',    'Odinofagia / dor de garganta'),
                _bool('foco_respiratorio','Tosse / dispneia / dor torácica'),
                _bool('foco_urinario',    'Disúria / polaciúria / dor lombar'),
                _bool('foco_gi',          'Diarreia / vômito / dor abdominal'),
                _bool('foco_pele_partes_moles','Lesão de pele / celulite / abscesso'),
                _bool('artralgia_artrite','Artralgia / artrite (articulação quente)'),
                _bool('exantema',         'Rash / exantema'),
                _sel ('exantema_tipo',    'Tipo de exantema', [
                    ('maculopapular','Maculopapular'), ('petequial','Petequial'),
                    ('vesicular','Vesicular'), ('eritema_migrans','Eritema migrans/alvo'),
                    ('outro','Outro'),
                ], depends_on='exantema'),
            ]),
            _block('5 · Contexto Epidemiológico', [
                _bool('viagem_area_endemica','Viagem a área endêmica (malária/dengue/tifoide)'),
                _bool('contato_animal',   'Contato com animais (fazenda/morcego/roedor)'),
                _bool('picada_carrapato_inseto','Picada de carrapato/inseto (semanas)'),
                _bool('internacao_recente_30d','Internação nos últimos 30 dias'),
                _bool('uso_atb_recente',  'Antibiótico nos últimos 3 meses'),
                _bool('contato_tb',       'Contato com tuberculose'),
            ]),
            _block('6 · Exames (se disponíveis)', [
                _bool('labs_disponiveis', 'Há exames laboratoriais recentes'),
                _num ('leucocitos',       'Leucócitos (/mm³)', 0, 100000, 100, default=None, depends_on='labs_disponiveis'),
                _num ('neutrofilos_abs',  'Neutrófilos absolutos / ANC', 0, 50000, 100, default=None, depends_on='labs_disponiveis'),
                _num ('pcr_mgL',          'PCR (mg/L)', 0, 600, 1, default=None, depends_on='labs_disponiveis'),
                _num ('vhs',              'VHS (mm/h)', 0, 150, 1, default=None, depends_on='labs_disponiveis'),
                _bool('hemoculturas_feitas','Hemoculturas coletadas', depends_on='labs_disponiveis'),
            ]),
            _block('7 · Comorbidades', [
                _num ('idade','Idade (anos)', 18, 110, 1, 35),
                _bool('dm',     'Diabetes mellitus'),
                _bool('drc',    'Doença renal crônica'),
                _bool('icc',    'Insuficiência cardíaca'),
                _bool('cirrose','Cirrose hepática', flag='yellow'),
            ]),
        ],
        'engine': 'modules.raciocinio.febre.engine_febre',
        'engine_fn': 'interpretar_febre',
    },

    # ── CEFALEIA ─────────────────────────────────────────────────────────────
    'cefaleia': {
        'label': 'Cefaleia',
        'sistema': 'Neurologia',
        'blocks': [
            _block('Red Flags — Verificar Primeiro', [
                _bool('pior_da_vida',     '⚠ Pior cefaleia da vida (thunderclap)', flag='red'),
                _bool('inicio_subito',    '⚠ Início explosivo ("tiro")',           flag='red'),
                _bool('febre',            '⚠ Febre associada',                     flag='red'),
                _bool('rigidez_nucal',    '⚠ Rigidez de nuca',                     flag='red'),
                _bool('deficit_focal',    '⚠ Déficit neurológico focal',           flag='red'),
                _bool('papiledema',       '⚠ Papiledema / visão dupla',            flag='red'),
                _bool('pos_trauma',       '⚠ Pós-trauma craniano',                 flag='red'),
                _bool('imunossuprimido',  'Imunossuprimido',                        flag='yellow'),
            ]),
            _block('Caracterização', [
                _sel ('tipo_dor','Tipo da dor', [
                    ('pulsatil_unilateral','Pulsátil unilateral (enxaqueca?)'),
                    ('opressiva_bilateral','Opressiva bilateral (tensional?)'),
                    ('orbital_unilateral', 'Orbital unilateral excruciante (salvas?)'),
                    ('difusa',             'Difusa / sem padrão claro'),
                ]),
                _sel ('intensidade','Intensidade (EVA)', [
                    ('leve','1–3 — Leve'), ('moderada','4–6 — Moderada'),
                    ('intensa','7–10 — Intensa'),
                ]),
                _sel ('duracao_cefaleia','Duração', [
                    ('minutos','15–180 min (salvas?)'),('horas','4–72h (enxaqueca?)'),
                    ('dias','Dias (tensional crônica?)'),
                ]),
            ]),
            _block('Sintomas Associados', [
                _bool('nausea_vomito',   'Náusea / vômito'),
                _bool('foto_fonofobia',  'Fotofobia + fonofobia'),
                _bool('lacrimejamento',  'Lacrimejamento / olho vermelho ipsilateral'),
                _bool('aura',            'Aura visual / sensitiva antes da dor'),
                _bool('piora_esforco',   'Piora com esforço'),
                _bool('acorda_noite',    'Acorda do sono por dor (salvas?)'),
            ]),
            _block('Contexto', [
                _num ('frequencia_mes','Episódios por mês', 0, 30, 1, 2),
                _bool('uso_analgesico_excessivo','Uso de analgésico > 10–15 dias/mês', flag='yellow'),
                _bool('historico_enxaqueca','Histórico pessoal/familiar de enxaqueca'),
            ]),
        ],
        'engine': 'modules.raciocinio.cefaleia_dx',
        'engine_fn': 'interpretar_cefaleia',
        'legacy': True,
    },

    # ── VERTIGEM ─────────────────────────────────────────────────────────────
    'vertigem': {
        'label': 'Vertigem / Tontura',
        'sistema': 'Neurologia',
        'blocks': [
            _block('Tipo de Sensação', [
                _bool('sensacao_rotatoria',  'Rotatória (sensação de girar)'),
                _bool('desequilibrio',       'Instabilidade / desequilíbrio'),
                _bool('sensacao_pre_sincope','Pré-síncope / "apagamento"'),
            ]),
            _block('Gatilho + Padrão Temporal', [
                _bool('gatilho_mudar_posicao','Desencadeada ao mudar de posição (VPPB?)'),
                _bool('gatilho_espontaneo',  'Surge espontaneamente'),
                _bool('continuo',            'Contínua / constante'),
                _bool('recorrente',          'Episódios recorrentes'),
                _bool('duracao_segundos_minutos','Dura segundos a minutos'),
                _bool('duracao_horas',       'Dura horas (Menière?)'),
                _bool('duracao_dias',        'Dura dias (neurite?)'),
            ]),
            _block('Red Flags — AVC de Fossa Posterior', [
                _bool('incapaz_de_andar', '⚠ ATAXIA SEVERA — não fica de pé sem apoio', flag='red'),
                _bool('deficit_focal',    '⚠ Déficit neurológico focal', flag='red'),
                _bool('diplopia',         '⚠ Diplopia', flag='red'),
                _bool('disartria',        '⚠ Disartria', flag='red'),
                _bool('fraqueza',         '⚠ Fraqueza em membro', flag='red'),
                _bool('parestesias',      '⚠ Parestesias', flag='red'),
                _bool('cefaleia',         'Cefaleia associada', flag='yellow'),
                _bool('hints_preocupante','⚠ HINTS sugestivo de central (HI normal + nistagmo multi + skew)', flag='red'),
            ]),
            _block('Exame + Ortostase', [
                _bool('dix_hallpike_positivo', 'Dix-Hallpike positivo (VPPB)'),
                _bool('roll_test_positivo',    'Roll test positivo (canal horizontal)'),
                _bool('ortostatismo_sugestivo','Hipotensão ortostática sugestiva'),
            ]),
            _block('Sintomas Cocleares / Associados', [
                _bool('zumbido',            'Zumbido / tinitus'),
                _bool('perda_auditiva',     'Perda auditiva'),
                _bool('plenitude_auricular','Plenitude auricular'),
                _bool('sincope',            'Síncope associada', flag='yellow'),
            ]),
        ],
        'engine': 'modules.raciocinio.vertigem_dx',
        'engine_fn': 'interpretar_vertigem',
        'legacy': True,
    },

    # ── DIARREIA ─────────────────────────────────────────────────────────────
    'diarreia': {
        'label': 'Diarreia Aguda',
        'sistema': 'Gastro/Abdominal',
        'blocks': [
            _block('Caracterização', [
                _sel ('duracao_diarreia','Duração', [
                    ('aguda','Aguda (< 14 dias)'),
                    ('persistente','Persistente (14–30 dias)'),
                    ('cronica','Crônica (> 30 dias)'),
                ]),
                _num ('episodios_dia','Episódios / dia', 1, 20, 1, 4),
                _bool('sangue_fezes',  '⚠ Sangue nas fezes',   flag='red'),
                _bool('muco_fezes',    'Muco nas fezes'),
                _bool('febre',         'Febre'),
                _bool('dor_abdominal', 'Dor abdominal'),
            ]),
            _block('Desidratação', [
                _bool('vomito',        'Vômito associado'),
                _bool('nao_tolera_vo', '⚠ Não tolera VO (vômito incoercível)', flag='red'),
                _bool('oliguria',      'Oligúria / urina escura'),
                _bool('taquicardia',   'Taquicardia / hipotensão',             flag='red'),
            ]),
            _block('Contexto Epidemiológico', [
                _bool('viagem_recente',  'Viagem recente para área endêmica'),
                _bool('atb_recente',     'Antibiótico recente (C. diff?)'),
                _bool('comida_suspeita', 'Refeição suspeita (intoxicação?)'),
                _bool('contacto_caso',   'Contacto com caso semelhante'),
                _bool('agua_nao_tratada','Água não tratada'),
                _bool('imunossuprimido', 'Imunossuprimido',              flag='yellow'),
            ]),
        ],
        'engine': 'modules.raciocinio.diarreia.engine_diarreia',
        'engine_fn': 'interpretar_diarreia',
    },

    # ── ARBOVIROSES ──────────────────────────────────────────────────────────
    'arboviroses': {
        'label': 'Arboviroses (Dengue / Chik / Zika)',
        'sistema': 'Infectologia',
        'blocks': [
            _block('Apresentação', [
                _num ('temperatura','Temperatura (°C)', 37.0, 42.0, 0.1, 38.5),
                _num ('dias_febre','Dias de febre', 1, 14, 1, 3),
                _bool('mialgia',     'Mialgia intensa ("quebradura")'),
                _bool('artralgia',   'Artralgia / artrite (Chikungunya?)'),
                _bool('cefaleia',    'Cefaleia retroorbital'),
                _bool('exantema',    'Exantema / manchas vermelhas'),
                _bool('prurido',     'Prurido'),
            ]),
            _block('Sinais de Alarme — Dengue', [
                _bool('dor_abdominal_intensa','⚠ Dor abdominal intensa ou contínua', flag='red'),
                _bool('vomito_persistente',   '⚠ Vômito persistente',               flag='red'),
                _bool('acumulo_liquidos',     '⚠ Acúmulo de líquidos (ascite/derrame)',flag='red'),
                _bool('sangramento',          '⚠ Sangramento espontâneo',            flag='red'),
                _bool('letargia',             '⚠ Letargia / agitação',               flag='red'),
                _bool('hipotensao_sinais',    '⚠ Hipotensão / sinais de choque',     flag='red'),
            ]),
            _block('Labs (se disponíveis)', [
                _num ('plaquetas','Plaquetas (/mm³)', 0, 500000, 1000, None),
                _num ('hematocrito','Hematócrito (%)', 20, 60, 1, None),
                _bool('ns1_positivo','NS1 positivo (dengue)'),
                _bool('leuco_normal_baixo','Leucócitos normais ou baixos'),
            ]),
            _block('Contexto', [
                _bool('gestante',     'Gestante',                       flag='yellow'),
                _bool('area_endemica','Área endêmica / viagem endêmica'),
                _num ('peso_kg','Peso (kg)', 30, 150, 1, 70),
            ]),
        ],
        'engine': 'modules.raciocinio.arboviroses.engine_arboviroses',
        'engine_fn': 'interpretar_arboviroses',
    },

    # ── GASTRO / DOR ABDOMINAL ───────────────────────────────────────────────
    'gastro': {
        'label': 'Dor Abdominal / Queixa GI',
        'sistema': 'Gastro/Abdominal',
        'blocks': [
            _block('Localização + Caráter', [
                _sel('localizacao', 'Localização principal', [
                    ('epigastrico',          'Epigástrio (boca do estômago)'),
                    ('fsd',                  'HCD / FSD (costelas à direita)'),
                    ('fid',                  'FID (baixo abdôme à direita)'),
                    ('fie',                  'FIE (baixo abdôme à esquerda)'),
                    ('hipogastrico_pelvico', 'Hipogástrio / pelve'),
                    ('periumbilical',        'Periumbilical'),
                    ('difuso',               'Difuso / todo o abdôme'),
                ]),
                _sel('carater', 'Caráter da dor', [
                    ('colica',       'Cólica / espasmo (vem e passa)'),
                    ('constante',    'Constante / pressão'),
                    ('queimacao',    'Queimação / azia / ardor'),
                    ('distensao',    'Distensão / plenitude pós-refeição'),
                    ('aguda_subita', 'Facada / início súbito intenso'),
                    ('difusa_leve',  'Difusa / leve / mal-definida'),
                ]),
                _sel('intensidade', 'Intensidade', [
                    ('leve',        'Leve — fala normalmente'),
                    ('moderada',    'Moderada — atrapalha atividades'),
                    ('intensa',     'Intensa — vai ao PA'),
                    ('catastrofica','Catastrófica — pior dor da vida'),
                ]),
                _sel('duracao', 'Duração', [
                    ('horas',      'Horas'),
                    ('dias',       'Dias (< 1 semana)'),
                    ('semanas',    'Semanas'),
                    ('meses_1_3',  '1–3 meses'),
                    ('meses_mais_3','> 3 meses'),
                ]),
            ]),
            _block('Red Flags Cirúrgicos', [
                _bool('dor_catastrofica',   '⚠ Dor catastrófica / pior da vida',       flag='red'),
                _bool('blumberg_positivo',  '⚠ Blumberg + / defesa muscular / rigidez', flag='red'),
                _bool('rha_diminuidos',     '⚠ RHÁ diminuídos / silêncio abdominal',   flag='red'),
                _bool('hematemese',         '⚠ Hematêmese',                            flag='red'),
                _bool('hematoquezia',       '⚠ Hematoquezia / melena',                 flag='red'),
                _bool('risco_isquemia_mesenterica', '⚠ Dor desproporcional + vasculopata/FA (isquemia?)', flag='red'),
            ]),
            _block('Sintomas Associados', [
                _bool('febre_alta',      'Febre alta (> 38,5°C)'),
                _bool('febre',           'Febre (qualquer grau)'),
                _bool('nausea_vomito',   'Náusea / vômito'),
                _bool('perda_peso',      'Perda de peso',      flag='yellow'),
                _bool('piora_gorduroso', 'Piora com gordura (cólica biliar?)'),
                _bool('piora_lactose',   'Piora com lactose'),
                _bool('alivio_evacuacao','Alívio com evacuação (SII?)'),
            ]),
            _block('Hábito Intestinal + Fezes', [
                _sel('habito_intestinal', 'Hábito intestinal', [
                    ('normal',            'Normal'),
                    ('diarreia',          'Diarreia'),
                    ('constipacao',       'Constipação'),
                    ('alternancia',       'Alternância diarreia/constipação'),
                    ('sem_evacuacao_gases','Obstipação total + parada de gases'),
                ]),
                _bool('sangue_fezes',  'Sangue nas fezes',  flag='yellow'),
                _bool('muco_fezes',    'Muco nas fezes'),
                _bool('esteatorreia',  'Fezes gordurosas / flutuantes'),
            ]),
            _block('Exame Físico', [
                _bool('murphy_positivo',   'Murphy + (dor FSD à inspiração)'),
                _bool('mcburney_positivo', 'McBurney + (dor FID à palpação)'),
                _bool('fie_dolorosa',      'FIE dolorosa à palpação'),
                _bool('peritonismo',       'Peritonismo / Blumberg +', flag='red'),
            ]),
            _block('Contexto', [
                _num ('idade',   'Idade', 14, 100, 1, 35),
                _bool('sexo_feminino', 'Sexo feminino'),
                _bool('idoso',         'Idoso (≥ 60 anos)'),
                _bool('imunossuprimido','Imunossuprimido',       flag='yellow'),
                _bool('hp_desconhecido','H. pylori desconhecido / não tratado'),
                _bool('duracao_cronica','Duração crônica (> 4 semanas)'),
                _bool('primeira_vez',  'Primeiro episódio'),
            ]),
            _block('Contexto GI', [
                _bool('suspeita_dip',     'Suspeita de DIP (corrimento + febre + dor pélvica)'),
                _bool('suspeita_ectopica','⚠ Atraso menstrual + dor pélvica lateral', flag='red'),
                _bool('suspeita_parasitose','Parasitose suspeita (água não tratada / viagem)'),
                _bool('suspeita_ibd',     'IBD suspeita (diarreia crônica + sangue + jovem)'),
            ]),
        ],
        'engine': 'modules.raciocinio.gastro.engine_gastro',
        'engine_fn': 'interpretar_queixa_gastro',
    },

    # ── EDEMA MMII (espelho exato do coletar_subjetivo_edema do CLI) ──────────
    'edema': {
        'label': 'Edema de MMII',
        'sistema': 'Cardiovascular',
        'blocks': [
            _block('1 · Caracterização do Edema', [
                _sel ('lateralidade','Lateralidade', [
                    ('unilateral','Unilateral (só um lado)'),
                    ('bilateral','Bilateral (ambos os lados)'),
                ]),
                _bool('inicio_agudo',         'Início agudo (< 72h)'),
                _bool('edema_nao_depressivel','Edema NÃO depressível (borrachudo/duro — não forma cacifo)',
                      help='Pressione o polegar sobre a tíbia por 5s. Se NÃO afunda (sem cacifo) = '
                           'não depressível → sugere linfedema/mixedema.'),
                _bool('edema_facial',         'Edema facial também presente'),
            ]),
            _block('2 · TVP / Celulite (membro unilateral) — Wells', [
                _bool('dor_trajeto_venoso',      'Dor na panturrilha/coxa (trajeto venoso)', help='Wells +1'),
                _bool('eritema_calor_local',     'Calor e vermelhidão no membro'),
                _bool('porta_entrada_ou_infeccao','Porta de entrada (ferida/micose) ou infecção prévia',
                      help='Com eritema+calor → favorece celulite sobre TVP.'),
                _bool('edema_toda_perna',        'Edema de TODA a perna (não só tornozelo)', help='Wells +1'),
                _bool('edema_panturrilha_assim', 'Panturrilha > 3 cm maior que a contralateral', help='Wells +1. Medir 10 cm abaixo da tuberosidade tibial.'),
                _bool('veias_colaterais',        'Veias superficiais colaterais (não varicosas)', help='Wells +1'),
                _bool('tvp_previa',              'TVP prévia documentada', help='Wells +1'),
                _bool('cancer_ativo',            'Câncer ativo em tratamento', help='Wells +1', flag='yellow'),
                _bool('repouso_cirurgia_recente','Imobilização/cirurgia grande recente (< 12 sem)', help='Wells +1'),
                _bool('diagnostico_alternativo', 'Diagnóstico alternativo MAIS provável que TVP', help='Wells −2'),
            ]),
            _block('3 · Sintomas Sistêmicos (bilateral)', [
                _bool('dispneia_esforco',     'Dispneia aos esforços / ortopneia (cardíaco?)', flag='yellow'),
                _bool('bnp_elevado',          'BNP / NT-proBNP elevado (se disponível)'),
                _bool('proteinuria_pesada',   'Proteinúria pesada (espuma na urina, > 3,5 g/dia)'),
                _bool('cirrose_conhecida',    'Cirrose hepática conhecida'),
                _bool('ascite',               'Ascite presente'),
                _bool('ictericia',            'Icterícia / albumina baixa hepática'),
                _bool('hiperpigmentacao_pernas','Hiperpigmentação / lipodermatoesclerose nas pernas'),
                _bool('varizes',              'Varizes visíveis'),
                _bool('mixedema_pretibial',   'Pele espessada / mixedema pré-tibial'),
                _bool('tsh_elevado',          'TSH elevado confirmado'),
                _num ('tsh_valor',            'Valor do TSH (mUI/L)', 0.0, 100.0, 0.1, default=None, depends_on='tsh_elevado'),
                _bool('cirurgia_linfonodos',  'Cirurgia de linfonodos (axila/inguinal) ou radioterapia prévia'),
            ]),
            _block('4 · Medicamentos (causadores de edema)', [
                _bool('usa_bcc',         'Bloqueador de canal de cálcio (anlodipino, nifedipino)'),
                _bool('usa_aine',        'AINE regularmente'),
                _bool('usa_corticoide',  'Corticoide sistêmico'),
                _bool('usa_gabapentina', 'Gabapentina / pregabalina'),
                _bool('usa_tiazolidiona','Pioglitazona ou similar'),
                _bool('usa_hormonio',    'Hormônio (estrogênio, testosterona)'),
            ]),
            _block('5 · Comorbidades', [
                _bool('hipoalbuminemia', 'Hipoalbuminemia por desnutrição'),
                _bool('sinais_sistemicos','Sinais sistêmicos (febre, emagrecimento)', flag='yellow'),
                _bool('apneia_sono',     'Apneia do sono (STOP-BANG ≥ 3 ou confirmada)'),
            ]),
        ],
        'engine': 'modules.raciocinio.edema.engine_edema',
        'engine_fn': 'interpretar_edema',
    },

    # ── TOSSE ────────────────────────────────────────────────────────────────
    'tosse': {
        'label': 'Tosse', 'sistema': 'Respiratório',
        'blocks': [
            _block('Caracterização', [
                _num ('duracao_semanas', 'Duração (semanas)', 0, 104, 1, 1),
                _bool('tosse_produtiva',   'Tosse produtiva (com catarro)'),
                _bool('expectoracao_purulenta', 'Expectoração purulenta'),
                _bool('tosse_paroxistica',  'Tosse em acessos / paroxística'),
                _bool('piora_noturna_madrugada', 'Piora noturna / madrugada'),
            ]),
            _block('Red Flags', [
                _bool('hemoptise',          '⚠ Hemoptise', flag='red'),
                _bool('perda_peso_involuntaria', '⚠ Perda de peso', flag='red'),
                _bool('dispneia_progressiva','⚠ Dispneia progressiva', flag='red'),
                _bool('dor_toracica_persistente', 'Dor torácica persistente', flag='yellow'),
                _bool('saturacao_baixa',    '⚠ SpO₂ baixa', flag='red'),
                _bool('sudorese_noturna',   'Sudorese noturna', flag='yellow'),
                _bool('febre_alta',         'Febre alta'),
            ]),
            _block('Pistas Etiológicas', [
                _bool('piora_pos_prandial', 'Piora pós-prandial / pirose (DRGE?)'),
                _bool('piora_deitado_drge', 'Piora ao deitar (DRGE?)'),
                _bool('gotejamento_pos_nasal', 'Gotejamento pós-nasal (UACS?)', negative=True),
                _bool('sensacao_gotejamento','Sensação de secreção na garganta'),
                _bool('chiado_episodico',   'Chiado episódico (asma?)'),
                _bool('piora_exercicio',    'Piora ao exercício / frio'),
                _bool('uso_ieca',           'Em uso de IECA (captopril/enalapril)'),
                _bool('tosse_inicio_apos_ieca', 'Tosse iniciou após IECA'),
            ]),
            _block('Infecção / Contágio', [
                _bool('infeccao_recente_precedeu', 'IVAS recente precedeu'),
                _bool('contato_tb',          'Contato com tuberculose', flag='yellow'),
                _bool('contato_pertussis',   'Contato com coqueluche'),
                _bool('vomito_pos_tosse',    'Vômito após acesso de tosse'),
            ]),
            _block('Contexto', [
                _num ('idade', 'Idade', 0, 120, 1, 35),
                _bool('tabagismo_ativo',     'Tabagismo ativo', flag='yellow'),
                _bool('asma_diagnosticada',  'Asma diagnosticada'),
                _bool('dpoc',                'DPOC'),
                _bool('imunossuprimido',     'Imunossuprimido', flag='yellow'),
                _bool('alergia_penicilina',  'Alergia à penicilina'),
            ]),
        ],
        'engine': 'modules.raciocinio.tosse.engine_tosse', 'engine_fn': 'interpretar_tosse',
    },

    # ── ASMA ─────────────────────────────────────────────────────────────────
    'asma': {
        'label': 'Asma (crise / controle)', 'sistema': 'Respiratório',
        'blocks': [
            _block('Tipo de Consulta', [
                _sel('consulta_tipo', 'Apresentação', [
                    ('exacerbacao', 'Crise / exacerbação aguda'),
                    ('rotina',      'Controle / rotina'),
                ]),
            ]),
            _block('Gravidade da Crise (red flags)', [
                _bool('nao_consegue_falar',   '⚠ Não consegue falar', flag='red'),
                _bool('fala_palavras_apenas', '⚠ Fala em palavras apenas', flag='red'),
                _bool('torax_silencioso',     '⚠ Tórax silencioso', flag='red'),
                _bool('sonolencia_confusao',  '⚠ Sonolência / confusão', flag='red'),
                _bool('uso_musculatura_acessoria', 'Uso de musculatura acessória', flag='yellow'),
                _bool('fr_maior_30',          'FR > 30 ipm', flag='yellow'),
                _bool('fc_maior_120',         'FC > 120 bpm'),
                _num ('spo2', 'SpO₂ (%)', 50, 100, 1, 96),
                _num ('pefr_percentual', 'PFE (% do previsto)', 0, 150, 1, default=None),
            ]),
            _block('Controle (se rotina)', [
                _num ('exacerbacao_ultimo_ano', 'Exacerbações no último ano', 0, 20, 1, 0),
                _num ('step_atual', 'Step GINA atual', 1, 5, 1, 1),
                _bool('tecnica_inalacao_correta', 'Técnica inalatória correta'),
                _bool('adesao_medicacao',     'Boa adesão à medicação'),
                _num ('eosinofilos', 'Eosinófilos (cél/μL)', 0, 5000, 10, default=None),
            ]),
        ],
        'engine': 'modules.raciocinio.asma.engine_asma', 'engine_fn': 'interpretar_asma',
    },

    # ── DPOC ─────────────────────────────────────────────────────────────────
    'dpoc': {
        'label': 'DPOC (exacerbação / controle)', 'sistema': 'Respiratório',
        'blocks': [
            _block('Tipo de Consulta', [
                _sel('consulta_tipo', 'Apresentação', [
                    ('exacerbacao', 'Exacerbação aguda'),
                    ('rotina',      'Controle / rotina'),
                ]),
            ]),
            _block('Critérios de Anthonisen (exacerbação)', [
                _bool('piora_dispneia',       'Piora da dispneia'),
                _bool('aumento_volume_escarro','Aumento do volume de escarro'),
                _bool('escarro_purulento',    'Escarro purulento'),
            ]),
            _block('Gravidade (red flags)', [
                _bool('falencia_respiratoria','⚠ Falência respiratória', flag='red'),
                _bool('alt_consciencia',      '⚠ Alteração de consciência', flag='red'),
                _bool('hipotensao_exac',      '⚠ Hipotensão', flag='red'),
                _num ('spo2', 'SpO₂ (%)', 50, 100, 1, 92),
            ]),
            _block('Controle (se rotina)', [
                _num ('cat_score', 'CAT score', 0, 40, 1, default=None),
                _num ('mmrc', 'mMRC', 0, 4, 1, default=None),
                _num ('exacerbacoes_ultimo_ano', 'Exacerbações/ano', 0, 20, 1, 0),
                _num ('fev1_percentual', 'VEF1 (% previsto)', 0, 150, 1, default=None),
                _num ('eosinofilos', 'Eosinófilos (cél/μL)', 0, 5000, 10, default=None),
            ]),
            _block('Contexto', [
                _num ('idade', 'Idade', 30, 110, 1, 65),
                _bool('tabagismo_ativo', 'Tabagismo ativo', flag='yellow'),
                _bool('ex_tabagista',    'Ex-tabagista'),
            ]),
        ],
        'engine': 'modules.raciocinio.dpoc.engine_dpoc', 'engine_fn': 'interpretar_dpoc',
    },

    # ── ANORRETAL ────────────────────────────────────────────────────────────
    'anorretal': {
        'label': 'Sangramento Anorretal / Prurido', 'sistema': 'Gastro/Abdominal',
        'blocks': [
            _block('Sangramento', [
                _bool('sangramento_novo',       'Sangramento (queixa atual)'),
                _bool('sangramento_no_papel',   'Sangue no papel'),
                _bool('sangramento_gotejamento','Gotejamento no vaso'),
                _bool('sangramento_sem_dor',    'Sangramento SEM dor'),
                _bool('sangue_misturado_fezes', '⚠ Sangue misturado às fezes', flag='red'),
                _bool('sangramento_significativo', 'Sangramento significativo / volumoso', flag='yellow'),
            ]),
            _block('Dor / Fissura', [
                _bool('dor_durante_defecacao', 'Dor intensa à evacuação (fissura?)'),
                _num ('duracao_fissura_semanas', 'Duração da fissura (semanas)', 0, 52, 1, 0),
                _bool('fissura_cronica_confirmada', 'Fissura crônica confirmada'),
            ]),
            _block('Hemorroida / Prolapso', [
                _bool('hemorroida_trombosada_externa', 'Hemorroida trombosada externa'),
                _num ('horas_desde_trombose', 'Horas desde a trombose', 0, 336, 1, default=None),
                _bool('prolapso_anorretal',     'Prolapso anorretal'),
                _bool('prolapso_reducao_espontanea', 'Prolapso reduz espontaneamente'),
                _bool('prolapso_reducao_manual','Prolapso reduz manualmente'),
                _bool('prolapso_irredutivel',   '⚠ Prolapso irredutível', flag='red'),
                _bool('prurido_perianal',       'Prurido perianal'),
            ]),
            _block('Red Flags Neoplasia', [
                _bool('mudanca_habito_intestinal_4sem', '⚠ Mudança de hábito intestinal', flag='red'),
                _bool('perda_peso_involuntaria','⚠ Perda de peso', flag='red'),
                _bool('historia_familiar_ccr', 'História familiar de CCR', flag='yellow'),
                _bool('historia_pessoal_ccr',  'História pessoal de CCR', flag='yellow'),
                _bool('anemia_ferropriva_confirmada', 'Anemia ferropriva confirmada', flag='yellow'),
            ]),
            _block('Contexto', [
                _num ('idade', 'Idade', 18, 100, 1, 45),
            ]),
        ],
        'engine': 'modules.raciocinio.anorretal.engine_anorretal', 'engine_fn': 'interpretar_anorretal',
    },

    # ── ICTERÍCIA ────────────────────────────────────────────────────────────
    'ictericia': {
        'label': 'Icterícia', 'sistema': 'Gastro/Abdominal',
        'blocks': [
            _block('Apresentação', [
                _bool('ictericia',          'Icterícia presente'),
                _bool('dor_hcd',            'Dor em hipocôndrio direito'),
                _bool('colica_biliar',      'Cólica biliar'),
                _bool('ictericia_flutuante','Icterícia flutuante'),
            ]),
            _block('Red Flags', [
                _bool('febre',              'Febre (colangite?)', flag='yellow'),
                _bool('hipotensao',         '⚠ Hipotensão', flag='red'),
                _bool('alt_consciencia',    '⚠ Alteração de consciência', flag='red'),
                _bool('encefalopatia_hepatica', '⚠ Encefalopatia hepática', flag='red'),
                _bool('inr_maior_1_5',      '⚠ INR > 1,5', flag='red'),
                _bool('perda_peso_involuntaria','Perda de peso', flag='yellow'),
            ]),
            _block('Etiologia', [
                _bool('uso_alcool_excessivo','Uso de álcool excessivo'),
                _bool('uso_hepatotoxicos',  'Uso de hepatotóxicos'),
                _bool('medicamento_hepatotoxico','Medicamento hepatotóxico'),
                _bool('medicamento_colestatico','Medicamento colestático'),
                _bool('suplem_herbal',      'Suplemento herbal'),
                _bool('hepatite_viral_suspeita','Hepatite viral suspeita'),
                _bool('hepatite_b_hbsag',   'HBsAg positivo'),
                _bool('contato_hepatite_b', 'Contato com hepatite B'),
                _bool('viagem_area_endemica','Viagem para área endêmica'),
                _bool('gilbert_previamente_diagnosticado', 'Gilbert previamente diagnosticado'),
                _bool('ductos_dilatados_us','Ductos dilatados no US (obstrução)', flag='yellow'),
            ]),
            _block('Labs (se disponíveis)', [
                _num ('bilirrubina_direta',  'Bilirrubina direta (mg/dL)', 0, 50, 0.1, default=None),
                _num ('bilirrubina_indireta','Bilirrubina indireta (mg/dL)', 0, 50, 0.1, default=None),
                _num ('ast_u_l', 'AST/TGO (U/L)', 0, 5000, 1, default=None),
                _num ('alt_u_l', 'ALT/TGP (U/L)', 0, 5000, 1, default=None),
                _num ('alp_u_l', 'FA (U/L)', 0, 2000, 1, default=None),
                _num ('ggt_u_l', 'GGT (U/L)', 0, 2000, 1, default=None),
            ]),
        ],
        'engine': 'modules.raciocinio.ictericia.engine_ictericia', 'engine_fn': 'interpretar_ictericia',
    },

    # ── GOTA ─────────────────────────────────────────────────────────────────
    'gota': {
        'label': 'Gota / Artrite por Cristais', 'sistema': 'MSK',
        'blocks': [
            _block('Apresentação', [
                _bool('ataque_atual',       'Ataque agudo atual'),
                _num ('n_articulacoes_afetadas', 'Nº de articulações afetadas', 0, 20, 1, 1),
                _bool('tophi_presentes',    'Tofos presentes'),
                _bool('gota_confirmada_previa', 'Gota confirmada previamente'),
                _num ('n_ataques_ano', 'Ataques no último ano', 0, 50, 1, 0),
            ]),
            _block('Diferencial — Artrite Séptica', [
                _bool('febre_385',          '⚠ Febre > 38,5°C', flag='red'),
                _bool('aparencia_toxica',   '⚠ Aparência toxêmica', flag='red'),
            ]),
            _block('Comorbidades (afetam tratamento)', [
                _bool('drc',                'DRC', flag='yellow'),
                _num ('egfr', 'eGFR (mL/min)', 0, 150, 1, default=None),
                _bool('dpud',               'Doença ulcerosa péptica'),
                _bool('icc',                'ICC'),
                _bool('anticoagulado',      'Anticoagulado', flag='yellow'),
                _bool('dm_descontrolado',   'DM descontrolado'),
                _bool('imunossupressao',    'Imunossupressão'),
                _bool('inibidor_cyp3a4_pgp','Uso de inibidor CYP3A4/P-gp'),
            ]),
            _block('Manejo Crônico (ULT)', [
                _bool('ja_usa_ult',         'Já usa hipouricemiante (alopurinol etc.)'),
                _num ('urato_atual_mgdl', 'Urato sérico (mg/dL)', 0, 20, 0.1, default=None),
                _bool('urolitiase',         'Urolitíase'),
                _bool('origem_alto_risco_hlab5801', 'Origem de alto risco HLA-B*5801'),
            ]),
            _block('Contexto', [
                _num ('idade', 'Idade', 18, 100, 1, 50),
            ]),
        ],
        'engine': 'modules.raciocinio.gota.engine_gota', 'engine_fn': 'interpretar_gota',
    },

    # ── ANEMIA ───────────────────────────────────────────────────────────────
    'anemia': {
        'label': 'Anemia / Hemograma', 'sistema': 'Hematologia',
        'blocks': [
            _block('Hemograma Básico', [
                _num ('hb',  'Hemoglobina (g/dL)', 2, 22, 0.1, 10.0),
                _num ('mcv', 'VCM (fL)', 50, 130, 1, 85),
                _num ('rdw', 'RDW (%)', 10, 30, 0.1, default=None),
                _num ('wbc', 'Leucócitos (/μL)', 0, 100000, 100, default=None),
                _num ('plt', 'Plaquetas (/μL)', 0, 1000000, 1000, default=None),
                _sel ('sexo', 'Sexo', [('masculino','Masculino'),('feminino','Feminino')]),
            ]),
            _block('Reticulócitos / Cinética de Ferro', [
                _num ('retic_pct', 'Reticulócitos (%)', 0, 30, 0.1, default=None),
                _num ('ht', 'Hematócrito (%)', 10, 60, 1, default=None),
                _num ('ferritina', 'Ferritina (ng/mL)', 0, 2000, 1, default=None),
                _num ('sat_transf', 'Sat. transferrina (%)', 0, 100, 1, default=None),
            ]),
            _block('Macrocítica / Outros', [
                _num ('b12', 'Vitamina B12 (pg/mL)', 0, 2000, 1, default=None),
                _num ('folato', 'Folato (ng/mL)', 0, 40, 0.1, default=None),
                _num ('creatinina', 'Creatinina (mg/dL)', 0, 20, 0.1, default=None),
                _num ('tsh', 'TSH (mU/L)', 0, 100, 0.1, default=None),
                _bool('hba2_elevada',  'HbA2 elevada (eletroforese)'),
                _bool('hbf_elevada',   'HbF elevada'),
            ]),
            _block('Clínica / Contexto', [
                _bool('sangramento_ativo', '⚠ Sangramento ativo', flag='red'),
                _bool('sintomas_dispneia', 'Dispneia'),
                _bool('sintomas_palpitacao','Palpitação'),
                _bool('sintomas_neurologico','Sintomas neurológicos (B12?)'),
                _bool('ictericia',         'Icterícia (hemólise?)'),
                _bool('esplenomegalia',    'Esplenomegalia'),
                _bool('gestante',          'Gestante'),
                _bool('doenca_cronica',    'Doença crônica/inflamatória'),
                _bool('vegetariano_vegano','Vegetariano/vegano'),
                _bool('alcool',            'Etilismo'),
                _bool('gastro_cirurgia',   'Cirurgia gástrica prévia'),
            ]),
        ],
        'engine': 'modules.raciocinio.anemia.engine_anemia', 'engine_fn': 'interpretar_anemia',
    },

    # ── LINFADENOPATIA ───────────────────────────────────────────────────────
    'linfadenopatia': {
        'label': 'Linfadenopatia', 'sistema': 'Hematologia',
        'blocks': [
            _block('Caracterização', [
                _sel ('localizacao', 'Localização', [
                    ('cervical','Cervical'), ('supraclavicular','Supraclavicular'),
                    ('axilar','Axilar'), ('inguinal','Inguinal'),
                    ('generalizada','Generalizada'), ('outro','Outro'),
                ]),
                _num ('tamanho_cm', 'Tamanho (cm)', 0.0, 15.0, 0.1, 1.0),
                _num ('duracao_semanas', 'Duração (semanas)', 0, 104, 1, 2),
                _sel ('textura', 'Textura', [
                    ('mole_movel','Mole e móvel'), ('firme','Firme'),
                    ('petreo_fixo','Pétreo e fixo'),
                ]),
                _bool('doloroso',         'Doloroso'),
                _bool('multiplos_nodulos','Múltiplos nódulos'),
            ]),
            _block('Red Flags (B-symptoms / malignidade)', [
                _bool('b_symptoms',         '⚠ B-symptoms (febre+sudorese+perda peso)', flag='red'),
                _bool('crescimento_rapido', '⚠ Crescimento rápido', flag='red'),
                _bool('alargamento_mediastino', '⚠ Alargamento de mediastino', flag='red'),
                _bool('esplenomegalia',     'Esplenomegalia', flag='yellow'),
                _bool('pancitopenia',       '⚠ Pancitopenia', flag='red'),
                _bool('blastos',            '⚠ Blastos no sangue', flag='red'),
                _bool('pele_sobre_linfonodo','Alteração de pele sobre o linfonodo'),
            ]),
            _block('Pistas Infecciosas', [
                _bool('faringite_recente',  'Faringite recente'),
                _bool('sindrome_mono',      'Síndrome mononucleose-like'),
                _bool('monospot_positivo',  'Monospot positivo'),
                _bool('exposicao_gato',     'Exposição a gato (arranhadura?)'),
                _bool('problema_dental',    'Problema dental'),
                _bool('risco_tb',           'Risco de tuberculose'),
                _bool('comportamento_risco_hiv', 'Comportamento de risco HIV'),
                _bool('infeccao_pele_cab',  'Infecção de pele/couro cabeludo'),
                _bool('infeccao_mmss',      'Infecção em MMSS'),
                _bool('infeccao_mmii',      'Infecção em MMII'),
            ]),
            _block('Inguinal — diferencial hérnia', [
                _bool('redutivel',          'Redutível'),
                _bool('aumenta_valsalva',   'Aumenta com Valsalva'),
                _bool('abaixo_lig_inguinal','Abaixo do ligamento inguinal'),
                _bool('extensao_escrotal',  'Extensão escrotal'),
            ]),
            _block('Contexto', [
                _num ('idade', 'Idade', 0, 100, 1, 35),
                _bool('tabagismo', 'Tabagismo'),
                _bool('medicamentos_culpados', 'Medicamento causador (fenitoína etc.)'),
                _bool('vacina_recente_ax', 'Vacina recente no braço'),
            ]),
        ],
        'engine': 'modules.raciocinio.linfadenopatia.engine_linfadenopatia',
        'engine_fn': 'interpretar_linfadenopatia',
    },

    # ── SONO / INSÔNIA ───────────────────────────────────────────────────────
    'sono': {
        'label': 'Sono / Insônia', 'sistema': 'Geral',
        'blocks': [
            _block('Queixa Predominante', [
                _bool('dificuldade_iniciar', 'Dificuldade de iniciar/manter sono (insônia)'),
                _num ('noites_por_semana', 'Noites/semana com sintoma', 0, 7, 1, 3),
                _num ('duracao_semanas', 'Duração (semanas)', 0, 260, 1, 12),
                _num ('isi_score', 'ISI (Índice de Gravidade de Insônia)', 0, 28, 1, default=None),
            ]),
            _block('Apneia (STOP-BANG)', [
                _bool('sb_ronco',        'Ronco alto'),
                _bool('sb_cansaco_diurno','Cansaço diurno'),
                _bool('sb_apneia_observada','Pausas respiratórias observadas'),
                _bool('sb_pressao_alta', 'Pressão alta'),
                _bool('sb_imc_35',       'IMC > 35'),
                _bool('sb_idade_50',     'Idade > 50'),
                _bool('sb_pescoco_40',   'Circunferência cervical > 40 cm'),
                _bool('sb_masculino',    'Sexo masculino'),
                _num ('epworth_score', 'Epworth (sonolência)', 0, 24, 1, default=None),
            ]),
            _block('Pistas Específicas', [
                _bool('spi_criterios',   'Critérios de pernas inquietas (SPI)'),
                _bool('ranger_dentes',   'Range os dentes (bruxismo?)'),
                _bool('dor_mandibula_manha','Dor mandibular matinal'),
                _bool('cataplexia',      'Cataplexia (narcolepsia?)', flag='yellow'),
                _bool('sono_diurno_irresistivel', 'Sono diurno irresistível'),
                _bool('pesadelos_freq',  'Pesadelos frequentes'),
                _bool('sonambulismo',    'Sonambulismo'),
                _bool('turno_irregular', 'Trabalho em turnos / horário irregular'),
            ]),
            _block('Benzodiazepínico / Comorbidade', [
                _bool('benzo_em_uso',    'Em uso de benzodiazepínico', flag='yellow'),
                _num ('benzo_semanas', 'Tempo de uso (semanas)', 0, 520, 1, default=None),
                _bool('depressao_ansiedade','Depressão / ansiedade'),
                _bool('alcool_para_dormir','Usa álcool para dormir'),
            ]),
        ],
        'engine': 'modules.raciocinio.sono.engine_sono', 'engine_fn': 'interpretar_sono',
    },

    # ── FADIGA ───────────────────────────────────────────────────────────────
    'fadiga': {
        'label': 'Fadiga Crônica', 'sistema': 'Geral',
        'blocks': [
            _block('Caracterização', [
                _num ('duracao_meses', 'Duração (meses)', 0, 120, 1, 6),
                _bool('pem_presente',  'Mal-estar pós-esforço (PEM)'),
                _bool('sono_nao_reparador','Sono não reparador'),
                _bool('reducao_atividade_substancial', 'Redução substancial de atividade'),
                _bool('brain_fog',     'Névoa cognitiva (brain fog)'),
                _bool('intolerancia_ortostatica','Intolerância ortostática'),
            ]),
            _block('Red Flags', [
                _bool('perda_peso_involuntaria','⚠ Perda de peso', flag='red'),
                _bool('febre_persistente',     '⚠ Febre persistente', flag='red'),
                _bool('linfadenopatia_fixa',   '⚠ Linfadenopatia fixa', flag='red'),
                _bool('deficit_neurologico_focal','⚠ Déficit neurológico focal', flag='red'),
                _bool('dor_toracica_esforco',  '⚠ Dor torácica ao esforço', flag='red'),
                _bool('ideacao_suicida_ativa', '⚠ Ideação suicida ativa', flag='red'),
                _bool('hepatoesplenomegalia',  'Hepatoesplenomegalia', flag='yellow'),
            ]),
            _block('Humor / Apneia', [
                _num ('phq2_total', 'PHQ-2 (depressão)', 0, 6, 1, default=None),
                _num ('gad2_total', 'GAD-2 (ansiedade)', 0, 6, 1, default=None),
                _bool('sb_ronco',         'Ronco (apneia?)'),
                _bool('sb_apneia_observada','Pausas respiratórias'),
                _bool('sb_cansaco_diurno','Sonolência diurna'),
            ]),
            _block('Labs (se disponíveis)', [
                _num ('tsh', 'TSH (mU/L)', 0, 100, 0.1, default=None),
                _num ('hemoglobina', 'Hemoglobina (g/dL)', 2, 22, 0.1, default=None),
                _num ('ferritina', 'Ferritina (ng/mL)', 0, 2000, 1, default=None),
                _num ('glicemia_jejum', 'Glicemia jejum (mg/dL)', 0, 500, 1, default=None),
                _num ('hba1c', 'HbA1c (%)', 3.0, 18.0, 0.1, default=None),
            ]),
            _block('Contexto', [
                _bool('sexo_feminino', 'Sexo feminino'),
            ]),
        ],
        'engine': 'modules.raciocinio.fadiga.engine_fadiga', 'engine_fn': 'interpretar_fadiga',
    },

    # ── CONSCIÊNCIA / ANC ────────────────────────────────────────────────────
    'consciencia': {
        'label': 'Alteração de Consciência (ANC)', 'sistema': 'Neurologia',
        'blocks': [
            _block('Avaliação Inicial', [
                _num ('glasgow_total', 'Glasgow', 3, 15, 1, 15),
                _num ('glicemia', 'Glicemia capilar (mg/dL)', 0, 600, 1, 90),
                _num ('spo2', 'SpO₂ (%)', 50, 100, 1, 97),
                _num ('pa_sistolica', 'PA sistólica (mmHg)', 40, 260, 1, 120),
                _num ('fc', 'FC (bpm)', 20, 220, 1, 75),
                _bool('febre', 'Febre'),
            ]),
            _block('AEIOU TIPS — Pistas', [
                _bool('alcool_drogas',     'Álcool / drogas'),
                _bool('alcool_halito',     'Hálito etílico'),
                _bool('intoxicacao_suspeita','Intoxicação suspeita', flag='yellow'),
                _bool('epilepsia_previa',  'Epilepsia prévia'),
                _bool('convulsao_obs',     'Convulsão observada'),
                _bool('pos_ictal',         'Estado pós-ictal'),
                _bool('trauma_cabeca',     '⚠ Trauma de cabeça', flag='red'),
                _bool('foco_infeccioso',   'Foco infeccioso'),
                _bool('renal_cronico',     'DRC (uremia?)'),
                _bool('encefalopatia',     'Encefalopatia (hepática?)'),
                _bool('psiq_previa',       'História psiquiátrica'),
            ]),
            _block('Red Flags Neurológicos', [
                _bool('deficit_focal',     '⚠ Déficit neurológico focal', flag='red'),
                _bool('rigidez_nuca',      '⚠ Rigidez de nuca', flag='red'),
                _bool('cefaleia_intensa',  '⚠ Cefaleia intensa', flag='red'),
                _bool('pupilas_aniso',     '⚠ Anisocoria', flag='red'),
                _bool('fotofobia',         'Fotofobia'),
                _bool('lucido_intervalo',  'Intervalo lúcido (HED?)', flag='red'),
                _bool('hipertensao_grave', 'Hipertensão grave'),
                _bool('hipoxia',           'Hipóxia'),
            ]),
            _block('Contexto', [
                _bool('medicamentos_risco','Uso de medicamentos de risco (opioide/BZD)'),
                _bool('dpoc_conhecido',    'DPOC (carbonarcose?)'),
                _bool('desnutricao',       'Desnutrição (tiamina?)'),
            ]),
        ],
        'engine': 'modules.raciocinio.consciencia.engine_consciencia',
        'engine_fn': 'interpretar_consciencia',
    },

    # ── ODINOFAGIA (ORL) ─────────────────────────────────────────────────────
    'odinofagia': {
        'label': 'Odinofagia / Dor de Garganta', 'sistema': 'ORL',
        'blocks': [
            _block('Emergência / Abscesso', [
                _bool('estridor',        '⚠ Estridor', flag='red'),
                _bool('dificuldade_respiratoria', '⚠ Dificuldade respiratória', flag='red'),
                _bool('trismo',          '⚠ Trismo (não abre a boca)', flag='red'),
                _bool('sialorreia',      '⚠ Sialorreia', flag='red'),
                _bool('voz_batata',      '⚠ Voz de batata quente', flag='red'),
                _bool('desvio_uvula',    '⚠ Desvio da úvula', flag='red'),
                _bool('disfagia_saliva', '⚠ Não engole nem saliva', flag='red'),
            ]),
            _block('Critérios de Centor', [
                _bool('febre',                'Febre'),
                _bool('exsudato_amigdaliano', 'Exsudato amigdaliano'),
                _bool('adenopatia_cervical_ant','Adenopatia cervical anterior'),
                _bool('tosse',                'Tosse presente'),
            ]),
            _block('Mononucleose', [
                _bool('adenopatia_generalizada','Adenopatia generalizada (axila/virilha)'),
                _bool('rash_apos_amox',  'Rash após amoxicilina'),
            ]),
            _block('Rouquidão', [
                _bool('rouquidao',          'Rouquidão associada'),
                _bool('rouquidao_cronica',  'Rouquidão > 3 semanas', flag='yellow'),
            ]),
            _block('Contexto / Alergia', [
                _num ('idade', 'Idade', 3, 100, 1, 25),
                _bool('atb_recente_30d',      'ATB nos últimos 30 dias'),
                _bool('alergia_penicilina',   'Alergia à penicilina'),
                _bool('alergia_penicilina_grave', 'Reação grave/anafilática', flag='yellow'),
            ]),
        ],
        'engine': 'modules.raciocinio.orl.engine_odinofagia', 'engine_fn': 'interpretar_odinofagia',
    },

    # ── OTALGIA (ORL) ────────────────────────────────────────────────────────
    'otalgia': {
        'label': 'Otalgia / Dor de Ouvido', 'sistema': 'ORL',
        'blocks': [
            _block('Mastoidite (red flag)', [
                _bool('dor_retroauricular', '⚠ Dor retroauricular', flag='red'),
                _bool('pavilhao_projetado', '⚠ Pavilhão projetado', flag='red'),
                _bool('flutuacao_retroaur', '⚠ Flutuação retroauricular', flag='red'),
                _bool('febre_mais_72h_atb', 'Febre persiste > 72h com ATB', flag='yellow'),
            ]),
            _block('Otite Externa', [
                _bool('trago_positivo',  'Dor à tração do trago / pavilhão'),
                _bool('canal_edema',     'Canal auditivo edemaciado'),
                _bool('canal_estenose',  'Canal estenosado / com granulação'),
                _bool('banho_piscina',   'Exposição a água / piscina'),
                _bool('otalgia_grave',   'Otalgia intensa'),
            ]),
            _block('Otite Média (OMA)', [
                _bool('iras_recente',    'IVAS recente precedeu'),
                _bool('ouvido_cheio',    'Sensação de ouvido cheio'),
                _bool('hipoagusia',      'Hipoacusia'),
                _bool('febre',           'Febre'),
                _bool('mt_abaulada',     'MT abaulada'),
                _bool('mt_hiperemia',    'MT hiperemiada'),
                _bool('mt_efusao',       'Efusão atrás da MT'),
                _bool('otorreia_purulenta','Otorreia purulenta'),
            ]),
            _block('Tratar Imediato (sem watchful waiting)', [
                _bool('febre_alta',       'Febre ≥ 39°C'),
                _bool('bilateral',        'Bilateral'),
                _bool('otalgia_mais_48h', 'Otalgia > 48h'),
                _bool('seguimento_incerto','Seguimento incerto'),
                _bool('conjuntivite_purulenta','Conjuntivite purulenta associada'),
                _bool('oma_recorrente',   'OMA de repetição'),
                _bool('atb_recente_30d',  'ATB nos últimos 30 dias'),
            ]),
            _block('DTM', [
                _bool('dor_mastigacao',  'Dor à mastigação'),
                _bool('dor_matinal',     'Dor matinal mandibular'),
                _bool('bruxismo',        'Bruxismo'),
                _bool('click_mandibula', 'Click mandibular'),
                _bool('limitacao_abertura','Limitação de abertura bucal'),
            ]),
            _block('Contexto', [
                _num ('idade', 'Idade', 0, 100, 1, 25),
                _bool('diabetes', 'Diabetes (risco OE maligna)', flag='yellow'),
            ]),
        ],
        'engine': 'modules.raciocinio.orl.engine_otalgia', 'engine_fn': 'interpretar_otalgia',
    },

    # ── RINOSSINUSITE (ORL) ──────────────────────────────────────────────────
    'rinossinusite': {
        'label': 'Rinossinusite / Obstrução Nasal', 'sistema': 'ORL',
        'blocks': [
            _block('Red Flags — Complicações (PS imediato)', [
                _bool('edema_periorbital',  '⚠ Edema periorbital', flag='red'),
                _bool('diplopia',           '⚠ Diplopia', flag='red'),
                _bool('proptose',           '⚠ Proptose', flag='red'),
                _bool('rigidez_nucal',      '⚠ Rigidez nucal', flag='red'),
                _bool('cefaleia_intensa',   '⚠ Cefaleia intensa', flag='red'),
                _bool('alteracao_consciencia','⚠ Alteração de consciência', flag='red'),
            ]),
            _block('Caracterização', [
                _num ('duracao_dias_aprox', 'Duração (dias)', 0, 120, 1, 5),
                _bool('obstrucao_nasal',    'Obstrução nasal'),
                _bool('rinorreia_purulenta','Rinorreia purulenta'),
                _bool('rinorreia_clara',    'Rinorreia clara'),
                _bool('dor_facial',         'Dor / pressão facial'),
                _bool('dor_facial_unilateral','Dor facial unilateral'),
                _bool('hiposmia_anosmia',   'Hiposmia / anosmia'),
                _bool('febre',              'Febre'),
                _bool('febre_alta',         'Febre alta (≥ 39°C)'),
                _bool('double_sickening',   'Double-sickening (piora bifásica)', flag='yellow'),
            ]),
            _block('Componente Alérgico', [
                _bool('espirros_salva',     'Espirros em salva'),
                _bool('prurido_nasal_ocular','Prurido nasal/ocular'),
                _bool('piora_sazonal',      'Piora sazonal'),
                _bool('alergenos_conhecidos','Rinite alérgica conhecida'),
                _bool('polipos_conhecidos', 'Pólipos nasais conhecidos'),
                _bool('corticoide_nasal_uso','Já usa corticoide nasal'),
            ]),
            _block('Contexto / Alergia', [
                _num ('idade', 'Idade', 0, 100, 1, 30),
                _bool('atb_recente_30d',      'ATB no último mês'),
                _bool('imunossuprimido',      'Imunossuprimido', flag='yellow'),
                _bool('alergia_betalactamico','Alergia a beta-lactâmico'),
                _bool('alergia_tipo_1',       'Reação grave/anafilática', flag='yellow'),
            ]),
        ],
        'engine': 'modules.raciocinio.orl.engine_rinossinusite', 'engine_fn': 'interpretar_rinossinusite',
    },

    # ── OLHO VERMELHO (Oftalmo) ──────────────────────────────────────────────
    'olho_vermelho': {
        'label': 'Olho Vermelho', 'sistema': 'Oftalmo',
        'blocks': [
            _block('Red Flags — Emergência Oftalmológica', [
                _bool('dor_intensa',       '⚠ Dor ocular intensa', flag='red'),
                _bool('visao_turva',       '⚠ Visão turva / ↓ acuidade', flag='red'),
                _bool('halos_coloridos',   '⚠ Halos coloridos (glaucoma?)', flag='red'),
                _bool('fotofobia',         'Fotofobia', flag='yellow'),
                _bool('ciliary_flush',     '⚠ Ciliary flush (injeção perilímbica)', flag='red'),
                _bool('lente_de_contato',  '⚠ Usa lente de contato', flag='red'),
                _bool('pos_cirurgico_ocular','⚠ Pós-cirúrgico ocular recente', flag='red'),
                _bool('trauma_quimico',    '⚠ Trauma químico', flag='red'),
            ]),
            _block('Pálpebra / Órbita', [
                _bool('edema_palpebral',    'Edema palpebral'),
                _bool('limitacao_motilidade','⚠ Limitação de motilidade ocular', flag='red'),
                _bool('proptose',           '⚠ Proptose', flag='red'),
                _bool('eritema_palpebral',  'Eritema palpebral localizado'),
                _bool('febre',              'Febre'),
            ]),
            _block('Secreção / Padrão', [
                _bool('secrecao_purulenta', 'Secreção purulenta'),
                _bool('palpebra_grudada',   'Pálpebra grudada ao acordar'),
                _bool('secrecao_aquosa',    'Secreção aquosa'),
                _bool('lacrimejamento',     'Lacrimejamento'),
                _bool('bilateral',          'Bilateral'),
                _bool('adenopatia_preauricular','Adenopatia pré-auricular'),
                _bool('contato_conjuntivite','Contato com conjuntivite'),
                _bool('dor_ocular',         'Dor ocular (leve/moderada)'),
                _bool('corpo_estranho_sensacao','Sensação de corpo estranho'),
            ]),
            _block('Alérgico', [
                _bool('prurido_ocular',     'Prurido ocular'),
                _bool('rinite_alergica_concomitante','Rinite alérgica concomitante'),
                _bool('rinite_alergica_conhecida','Rinite alérgica conhecida'),
                _bool('piora_sazonal_ocular','Piora sazonal'),
            ]),
            _block('Contexto', [
                _num ('idade', 'Idade', 0, 100, 1, 30),
                _num ('pio_mmhg', 'PIO (mmHg, se tonômetro)', 0, 80, 1, default=None),
            ]),
        ],
        'engine': 'modules.raciocinio.oftalmo.engine_olho_vermelho', 'engine_fn': 'interpretar_olho_vermelho',
    },

    # ── MSK: JOELHO ──────────────────────────────────────────────────────────
    'joelho': {
        'label': 'Dor no Joelho', 'sistema': 'MSK',
        'blocks': [
            _block('Red Flags', [
                _bool('febre',                '⚠ Febre', flag='red'),
                _bool('calor_intenso_local',  '⚠ Calor intenso / monoartrite aguda', flag='red'),
                _bool('derrame_horas_apos_trauma','Derrame em horas após trauma (hemartrose)', flag='yellow'),
            ]),
            _block('Trauma / Mecanismo', [
                _bool('trauma',               'Houve trauma'),
                _bool('trauma_torcao_recente','Torção recente'),
                _bool('travamento_ou_estalido','Travamento / estalido'),
                _bool('dificuldade_flexao_completa','Não flexiona/estende completamente'),
            ]),
            _block('Padrão da Dor', [
                _bool('dor_mecanica',         'Dor mecânica (piora com uso)'),
                _bool('inicio_insidioso',     'Início insidioso'),
                _bool('rigidez_matinal_menos_30min','Rigidez matinal < 30 min'),
                _bool('piora_escadas_ou_agachamento','Piora ao subir escada / agachar'),
                _bool('dor_anterior_joelho',  'Dor anterior (patelofemoral?)'),
                _bool('dor_linha_articular',  'Dor na linha articular (menisco?)'),
                _bool('sinal_do_cinema',      'Dor ao ficar muito tempo sentado'),
            ]),
            _block('Manobras (exame)', [
                _bool('mcmurray_positivo',    'McMurray positivo'),
                _bool('squat_unipodal_positivo','Agachamento unipodal doloroso'),
                _bool('derrame_articular',    'Derrame articular'),
                _bool('crepitacao',           'Crepitação'),
                _bool('massa_fossa_poplitea',  'Massa em fossa poplítea (Baker?)'),
            ]),
            _block('Contexto', [
                _num ('idade', 'Idade', 10, 100, 1, 45),
                _bool('obesidade_ou_oa_associada','Obesidade / OA associada'),
                _bool('trabalho_ajoelhado',   'Trabalho ajoelhado'),
            ]),
        ],
        'engine': 'modules.raciocinio.musculoesqueletico.joelho.core.engine',
        'engine_fn': 'interpretar_joelho',
    },

    # ── MSK: OMBRO ───────────────────────────────────────────────────────────
    'ombro': {
        'label': 'Dor no Ombro', 'sistema': 'MSK',
        'blocks': [
            _block('Red Flags', [
                _bool('sinal_trauma_importante','⚠ Trauma importante / deformidade', flag='red'),
                _bool('red_flag_cardiovascular','⚠ Suspeita cardiovascular (dor referida)', flag='red'),
                _bool('atrofia_muscular',     'Atrofia muscular', flag='yellow'),
            ]),
            _block('Padrão', [
                _bool('dor_noturna',          'Dor noturna'),
                _bool('piora_overhead',       'Piora com elevação acima da cabeça'),
                _bool('dor_virou_rigidez',    'Evoluiu para rigidez (capsulite?)'),
                _bool('rom_passivo_limitado', 'ADM passiva limitada'),
                _bool('atividade_overhead_repetitiva','Atividade overhead repetitiva'),
            ]),
            _block('Manobras — Impacto / Manguito', [
                _bool('neer_positivo',        'Neer positivo'),
                _bool('hawkins_kennedy_positivo','Hawkins-Kennedy positivo'),
                _bool('arco_doloroso_positivo','Arco doloroso (60-120°)'),
                _bool('empty_can_positivo',   'Empty can / Jobe positivo'),
                _bool('drop_arm_positivo',    'Drop arm positivo (ruptura?)', flag='yellow'),
                _bool('fraqueza_rotacao_externa','Fraqueza de rotação externa'),
                _bool('external_rotation_lag_positivo','External rotation lag'),
            ]),
            _block('Manobras — Biceps / AC / Instabilidade', [
                _bool('speed_positivo',       'Speed positivo (bíceps)'),
                _bool('yergason_positivo',    'Yergason positivo'),
                _bool('cross_arm_positivo',   'Cross-arm positivo (AC)'),
                _bool('dor_palpacao_ac',      'Dor à palpação AC'),
                _bool('obrien_positivo',      'O\'Brien positivo (SLAP)'),
                _bool('apprehension_positivo','Apprehension positivo (instabilidade)'),
            ]),
            _block('Contexto', [
                _num ('idade', 'Idade', 14, 100, 1, 50),
                _bool('diabetes',             'Diabetes (risco capsulite)'),
                _bool('hipotireoidismo',      'Hipotireoidismo'),
            ]),
        ],
        'engine': 'modules.raciocinio.musculoesqueletico.ombro.core.engine_ombro',
        'engine_fn': 'interpretar_ombro',
    },

    # ── MSK: COLUNA / LOMBALGIA ──────────────────────────────────────────────
    'coluna': {
        'label': 'Lombalgia / Dor nas Costas', 'sistema': 'MSK',
        'blocks': [
            _block('Red Flags', [
                _bool('historico_cancer',     '⚠ História de câncer', flag='red'),
                _bool('perda_de_peso_inexplicada','⚠ Perda de peso inexplicada', flag='red'),
                _bool('febre',                '⚠ Febre', flag='red'),
                _bool('dor_noturna_sem_alivio','⚠ Dor noturna sem alívio', flag='red'),
                _bool('trauma_significativo',  '⚠ Trauma significativo', flag='red'),
                _bool('uso_drogas_iv',        '⚠ Uso de drogas IV', flag='red'),
                _bool('imunossupressao',      'Imunossupressão', flag='yellow'),
                _bool('uso_cronico_corticoide','Uso crônico de corticoide', flag='yellow'),
                _bool('osteoporose',          'Osteoporose'),
                _bool('giordano_positivo',    'Giordano positivo (renal?)', flag='yellow'),
            ]),
            _block('Padrão da Dor', [
                _bool('dor_mecanica',         'Dor mecânica (piora movimento)'),
                _bool('melhora_com_repouso',  'Melhora com repouso'),
                _bool('piora_com_repouso',    'Piora com repouso (inflamatória?)'),
                _bool('rigidez_matinal_acima_60min','Rigidez matinal > 60 min'),
                _bool('inicio_insidioso',     'Início insidioso'),
                _num ('eva_dor', 'EVA (0-10)', 0, 10, 1, default=None),
            ]),
            _block('Radiculopatia', [
                _bool('dor_irradiada_mmii',   'Dor irradiada para MMII'),
                _bool('distribuicao_dermatomal','Distribuição dermatomal'),
                _bool('queimacao_ou_choque_eletrico','Queimação / choque elétrico'),
                _bool('lasegue_positivo',     'Lasègue positivo'),
                _bool('claudicacao_neurogenica','Claudicação neurogênica (estenose?)'),
            ]),
            _block('Contexto', [
                _num ('idade', 'Idade', 14, 100, 1, 45),
                _bool('dor_nova',             'Dor nova (primeiro episódio)'),
                _bool('bacteremia_recente',   'Bacteremia / infecção recente', flag='yellow'),
            ]),
        ],
        'engine': 'modules.raciocinio.musculoesqueletico.coluna.core.engine_coluna',
        'engine_fn': 'interpretar_coluna',
    },

    # ── MSK: QUADRIL ─────────────────────────────────────────────────────────
    'quadril': {
        'label': 'Dor no Quadril', 'sistema': 'MSK',
        'blocks': [
            _block('Red Flags', [
                _bool('febre_sistemica',      '⚠ Febre sistêmica', flag='red'),
                _bool('nao_suporta_peso',     '⚠ Não suporta peso', flag='red'),
                _bool('historico_cancer',     '⚠ História de câncer', flag='red'),
                _bool('dor_noturna_intensa',  'Dor noturna intensa', flag='yellow'),
                _bool('trauma_recente',       'Trauma recente'),
                _bool('uso_corticoide_cronico','Uso crônico de corticoide (NAV?)', flag='yellow'),
                _bool('osteoporose',          'Osteoporose'),
                _bool('encurtamento_rotacao_externa','Encurtamento + rotação externa (fratura?)', flag='red'),
            ]),
            _block('Localização + Manobras', [
                _sel ('localizacao_dor', 'Localização da dor', [
                    ('inguinal','Inguinal (articular)'),
                    ('lateral','Lateral (trocantérica/bursite)'),
                    ('posterior','Posterior (glútea/lombar)'),
                ]),
                _bool('faber_positivo',       'FABER positivo'),
                _bool('fadir_positivo',       'FADIR positivo (impacto?)'),
            ]),
            _block('Contexto', [
                _bool('uso_alcool_cronico',   'Etilismo crônico (NAV?)'),
            ]),
        ],
        'engine': 'modules.raciocinio.musculoesqueletico.quadril.core.engine_quadril',
        'engine_fn': 'interpretar_quadril',
    },

    # ── MSK: MÃO / PUNHO ─────────────────────────────────────────────────────
    'mao_punho': {
        'label': 'Dor na Mão / Punho', 'sistema': 'MSK',
        'blocks': [
            _block('Red Flags / Trauma', [
                _bool('edema_punho_pos_trauma','Edema pós-trauma', flag='yellow'),
                _bool('dor_tabaqueira_anatomica','⚠ Dor na tabaqueira anatômica (escafoide?)', flag='red'),
                _bool('mecanismo_queda_mao_espalmada','Queda com mão espalmada'),
                _bool('deformidade_visivel',  'Deformidade visível'),
            ]),
            _block('Túnel do Carpo (mediano)', [
                _bool('parestesia_noturna',   'Parestesia noturna'),
                _bool('parestesia_territorio_mediano','Parestesia território mediano'),
                _bool('alivio_sacudir_mao',   'Alívio ao sacudir a mão'),
                _bool('phalen_positivo',      'Phalen positivo'),
                _bool('tinel_positivo',       'Tinel positivo'),
                _bool('durkan_positivo',      'Durkan positivo'),
                _bool('atrofia_tenar',        'Atrofia tenar', flag='yellow'),
            ]),
            _block('De Quervain / Dedo em Gatilho / Rizartrose', [
                _bool('dor_radial_punho',     'Dor radial do punho'),
                _bool('finkelstein_positivo', 'Finkelstein positivo (De Quervain)'),
                _bool('piora_movimento_polegar','Piora ao mover o polegar'),
                _bool('gatilho_bloqueio_ativo','Dedo em gatilho / bloqueio'),
                _bool('polia_a1_dor_nodulo',  'Dor/nódulo na polia A1'),
                _bool('grind_test_positivo',  'Grind test positivo (rizartrose)'),
            ]),
            _block('Inflamatório (artrite)', [
                _bool('rigidez_matinal_prolongada','Rigidez matinal prolongada'),
                _bool('acometimento_simetrico','Acometimento simétrico'),
                _bool('sinovite_mcf_punho',   'Sinovite MCF/punho'),
                _bool('sintomas_sistemicos',  'Sintomas sistêmicos'),
            ]),
            _block('Contexto', [
                _bool('gestante_pos_parto',   'Gestante / pós-parto'),
                _bool('diabetes_mellitus',    'Diabetes'),
                _bool('trabalho_manual_repetitivo','Trabalho manual repetitivo'),
                _bool('historico_artrite',    'Histórico de artrite'),
            ]),
        ],
        'engine': 'modules.raciocinio.musculoesqueletico.mao_punho.core.engine_mao_punho',
        'engine_fn': 'interpretar_mao_punho',
    },

    # ── MSK: TORNOZELO / PÉ ──────────────────────────────────────────────────
    'tornozelo_pe': {
        'label': 'Dor no Tornozelo / Pé', 'sistema': 'MSK',
        'blocks': [
            _block('Trauma + Ottawa', [
                _bool('trauma_recente',       'Trauma recente'),
                _bool('mecanismo_inversao',   'Mecanismo de inversão'),
                _bool('incapaz_apoio_4_passos','⚠ Incapaz de dar 4 passos', flag='red'),
                _bool('palpacao_maleolo_lateral_positiva','Dor maléolo lateral (Ottawa)'),
                _bool('palpacao_maleolo_medial_positiva','Dor maléolo medial (Ottawa)'),
                _bool('palpacao_base_5o_meta_positiva','Dor base 5º metatarso (Ottawa)'),
                _bool('palpacao_navicular_positiva','Dor navicular (Ottawa)'),
                _bool('edema_tornozelo',      'Edema'),
                _bool('equimose_visivel',     'Equimose'),
            ]),
            _block('Tendão de Aquiles', [
                _bool('dor_insercao_aquiles', 'Dor na inserção do Aquiles'),
                _bool('dor_zona_critica_aquiles','Dor na zona crítica (2-6 cm)'),
                _bool('thompson_positivo',    '⚠ Thompson positivo (ruptura?)', flag='red'),
                _bool('espessamento_nodulo_aquiles','Espessamento/nódulo'),
            ]),
            _block('Fascite Plantar / Neuroma', [
                _bool('dor_tuberosidade_medial_calc','Dor no calcâneo medial'),
                _bool('dor_primeiro_passo_manha','Dor no primeiro passo da manhã'),
                _bool('dor_espaco_3_4_interdigital','Dor 3º-4º espaço interdigital'),
                _bool('mulder_positivo',      'Mulder positivo (neuroma de Morton)'),
                _bool('queimacao_entre_dedos','Queimação entre os dedos'),
            ]),
            _block('Contexto', [
                _bool('uso_quinolona',        'Uso de quinolona (risco tendão)', flag='yellow'),
                _bool('sobrepeso_obesidade',  'Sobrepeso / obesidade'),
                _bool('sinais_flogisticos',   'Sinais flogísticos', flag='yellow'),
                _bool('febre_sistemica',      '⚠ Febre sistêmica', flag='red'),
            ]),
        ],
        'engine': 'modules.raciocinio.musculoesqueletico.tornozelo_pe.core.engine_tornozelo_pe',
        'engine_fn': 'interpretar_tornozelo_pe',
    },

    # ── MSK: FIBROMIALGIA ────────────────────────────────────────────────────
    'fibromialgia': {
        'label': 'Dor Difusa / Fibromialgia', 'sistema': 'MSK',
        'blocks': [
            _block('Critérios', [
                _bool('duracao_sintomas_3_meses','Dor difusa > 3 meses'),
                _bool('flags_inflamatorios_exclusao','Sinais inflamatórios/sistêmicos (excluir)', flag='yellow'),
            ]),
            _block('Sintomas Somáticos (SSS)', [
                _bool('sss_fadiga',           'Fadiga'),
                _bool('sss_sono',             'Sono não reparador'),
                _bool('sss_cognitivo',        'Queixa cognitiva (fibro fog)'),
                _bool('sss_cefaleia',         'Cefaleia'),
                _bool('sss_dor_abdominal',    'Dor abdominal'),
                _bool('sss_depressao',        'Depressão'),
            ]),
            _block('Sintoma Predominante', [
                _sel ('sintoma_predominante', 'Predomínio', [
                    ('dor',      'Dor'),
                    ('fadiga',   'Fadiga'),
                    ('sono',     'Sono'),
                    ('humor',    'Humor / depressão'),
                ]),
            ]),
        ],
        'engine': 'modules.raciocinio.musculoesqueletico.fibromialgia.core.engine_fibromialgia',
        'engine_fn': 'interpretar_fibromialgia',
    },

}

# ── Mapeamento de keywords do dispatcher → schema ─────────────────────────
# Permite que ao selecionar qualquer keyword do dispatcher, encontremos o schema certo.
KEYWORD_TO_SCHEMA = {
    # celulite
    'celulite': 'celulite', 'erisipela': 'celulite', 'fasciite': 'celulite',
    'abscesso': 'celulite', 'infeccao de pele': 'celulite', 'linfangite': 'celulite',
    # hemorragia
    'hematêmese': 'hemorragia', 'hematemese': 'hemorragia', 'melena': 'hemorragia',
    'hematoquezia': 'hemorragia', 'sangue nas fezes': 'hemorragia',
    'hemorragia digestiva': 'hemorragia', 'hda': 'hemorragia', 'hdb': 'hemorragia',
    'fissura anal': 'hemorragia', 'hemorroida sangrando': 'hemorragia',
    # palpitacao
    'palpitacao': 'palpitacao', 'palpitação': 'palpitacao',
    'fibrilacao atrial': 'palpitacao', 'arritmia': 'palpitacao',
    'taquicardia': 'palpitacao', 'extrassistolia': 'palpitacao',
    # urinario
    'disuria': 'urinario', 'itu': 'urinario', 'cistite': 'urinario',
    'pielonefrite': 'urinario', 'hematuria': 'urinario', 'urinario': 'urinario',
    # ivas / orl
    'odinofagia': 'ivas', 'dor de garganta': 'ivas', 'ivas': 'ivas',
    'faringite': 'ivas', 'amigdalite': 'ivas', 'resfriado': 'ivas',
    # sincope
    'sincope': 'sincope', 'síncope': 'sincope', 'desmaio': 'sincope',
    'perda de consciencia': 'sincope',
    # febre
    'febre': 'febre', 'febre sem foco': 'febre', 'febril': 'febre',
    # cefaleia
    'cefaleia': 'cefaleia', 'dor de cabeca': 'cefaleia', 'enxaqueca': 'cefaleia',
    # vertigem
    'vertigem': 'vertigem', 'tontura': 'vertigem',
    # diarreia
    'diarreia': 'diarreia', 'gastroenterite': 'diarreia',
    # arboviroses
    'dengue': 'arboviroses', 'chikungunya': 'arboviroses',
    'arbovirose': 'arboviroses', 'arboviroses': 'arboviroses',
    # edema
    'edema': 'edema', 'perna inchada': 'edema', 'tvp': 'edema',
    # gastro
    'abdome': 'gastro', 'dor abdominal': 'gastro', 'gastro': 'gastro',
    'gastroabdominal': 'gastro', 'dor de barriga': 'gastro', 'colica': 'gastro',
    'cólica': 'gastro', 'azia': 'gastro', 'dispepsia': 'gastro', 'gastrite': 'gastro',
    'dor no abdome': 'gastro', 'sii': 'gastro', 'nausea': 'gastro', 'vomito': 'gastro',
    'constipacao': 'gastro', 'diverticulite': 'gastro', 'ulcera': 'gastro',
    'h pylori': 'gastro', 'helicobacter': 'gastro',
    # tosse
    'tosse': 'tosse', 'tosse seca': 'tosse', 'tosse com catarro': 'tosse',
    'tosse cronica': 'tosse', 'tosse com sangue': 'tosse',
    # asma
    'asma': 'asma', 'crise de asma': 'asma', 'crise asmatica': 'asma',
    'broncoespasmo': 'asma', 'chieira': 'asma', 'sibilos': 'asma',
    'controle asma': 'asma', 'retorno asma': 'asma',
    # dpoc
    'dpoc': 'dpoc', 'epoc': 'dpoc', 'enfisema': 'dpoc', 'bronquite cronica': 'dpoc',
    'exacerbacao dpoc': 'dpoc', 'crise de dpoc': 'dpoc', 'controle dpoc': 'dpoc',
    # anorretal
    'sangramento anorretal': 'anorretal', 'sangramento retal': 'anorretal',
    'hemorroida': 'anorretal', 'fissura anal': 'hemorragia', 'prurido anal': 'anorretal',
    'coceira no anus': 'anorretal', 'dor ao defecar': 'anorretal', 'prolapso retal': 'anorretal',
    # ictericia
    'ictericia': 'ictericia', 'icterícia': 'ictericia', 'pele amarela': 'ictericia',
    'olhos amarelos': 'ictericia', 'hepatite': 'ictericia', 'colangite': 'ictericia',
    'bilirrubina alta': 'ictericia', 'gilbert': 'ictericia',
    # gota
    'gota': 'gota', 'artrite por cristais': 'gota', 'ataque de gota': 'gota',
    'crise de gota': 'gota', 'podagra': 'gota', 'hiperuricemia': 'gota',
    'acido urico alto': 'gota', 'artrite gotosa': 'gota', 'tofo': 'gota',
    # anemia
    'anemia': 'anemia', 'hemograma alterado': 'anemia', 'retorno hemograma': 'anemia',
    'anemia ferropriva': 'anemia', 'deficiencia de ferro': 'anemia',
    'deficiencia de b12': 'anemia', 'talassemia': 'anemia', 'hb baixa': 'anemia',
    'hemoglobina baixa': 'anemia', 'palidez': 'anemia',
    # linfadenopatia
    'linfadenopatia': 'linfadenopatia', 'linfonodo aumentado': 'linfadenopatia',
    'ganglio aumentado': 'linfadenopatia', 'ingua': 'linfadenopatia',
    'adenopatia': 'linfadenopatia', 'nodulo cervical': 'linfadenopatia',
    'bola no pescoco': 'linfadenopatia', 'bola na axila': 'linfadenopatia',
    # sono
    'insonia': 'sono', 'insônia': 'sono', 'sono': 'sono', 'dificuldade para dormir': 'sono',
    'apneia': 'sono', 'apneia do sono': 'sono', 'ronco': 'sono', 'bruxismo': 'sono',
    'pernas inquietas': 'sono', 'sonolencia excessiva': 'sono', 'disturbio do sono': 'sono',
    'narcolepsia': 'sono', 'pesadelos': 'sono',
    # fadiga
    'fadiga': 'fadiga', 'cansaco': 'fadiga', 'fadiga cronica': 'fadiga',
    'me/sfc': 'fadiga', 'exaustao cronica': 'fadiga',
    # consciencia
    'alteracao de consciencia': 'consciencia', 'rebaixamento': 'consciencia',
    'rebaixamento de consciencia': 'consciencia', 'nao acorda': 'consciencia',
    'glasgow': 'consciencia', 'coma': 'consciencia', 'confusao aguda': 'consciencia',
    'delirium': 'consciencia', 'hipoglicemia': 'consciencia', 'intoxicacao': 'consciencia',
    'overdose': 'consciencia', 'encefalopatia': 'consciencia',
    # odinofagia
    'odinofagia': 'odinofagia', 'dor de garganta': 'odinofagia', 'garganta': 'odinofagia',
    'faringite': 'odinofagia', 'faringoamigdalite': 'odinofagia', 'amigdalite': 'odinofagia',
    'mononucleose': 'odinofagia', 'rouquidao': 'odinofagia', 'disfonia': 'odinofagia',
    # otalgia
    'otalgia': 'otalgia', 'dor de ouvido': 'otalgia', 'dor no ouvido': 'otalgia',
    'otite': 'otalgia', 'otite media': 'otalgia', 'otite externa': 'otalgia',
    'oma': 'otalgia', 'mastoidite': 'otalgia', 'ouvido': 'otalgia', 'zumbido': 'otalgia',
    # rinossinusite
    'sinusite': 'rinossinusite', 'rinossinusite': 'rinossinusite',
    'obstrucao nasal': 'rinossinusite', 'nariz entupido': 'rinossinusite',
    'coriza': 'rinossinusite', 'rinite': 'rinossinusite', 'rinite alergica': 'rinossinusite',
    'polipose nasal': 'rinossinusite',
    # olho_vermelho
    'olho vermelho': 'olho_vermelho', 'conjuntivite': 'olho_vermelho',
    'dor ocular': 'olho_vermelho', 'dor no olho': 'olho_vermelho', 'olho': 'olho_vermelho',
    'uveite': 'olho_vermelho', 'glaucoma': 'olho_vermelho', 'hordeolo': 'olho_vermelho',
    'ceratite': 'olho_vermelho', 'queratite': 'olho_vermelho', 'trauma ocular': 'olho_vermelho',
    'hemorragia subconjuntival': 'olho_vermelho',
    # MSK
    'dor no joelho': 'joelho', 'joelho': 'joelho',
    'dor no ombro': 'ombro', 'ombro': 'ombro',
    'lombalgia': 'coluna', 'dor nas costas': 'coluna', 'dor lombar': 'coluna',
    'dor no quadril': 'quadril', 'quadril': 'quadril',
    'mao': 'mao_punho', 'punho': 'mao_punho', 'dor na mao': 'mao_punho',
    'dor no punho': 'mao_punho', 'tunel do carpo': 'mao_punho',
    'dedo em gatilho': 'mao_punho', 'de quervain': 'mao_punho',
    'tornozelo': 'tornozelo_pe', 'dor no tornozelo': 'tornozelo_pe',
    'entorse': 'tornozelo_pe', 'dor no pe': 'tornozelo_pe', 'pe': 'tornozelo_pe',
    'fasciite plantar': 'tornozelo_pe',
    'fibromialgia': 'fibromialgia', 'dor difusa': 'fibromialgia',
    'dor cronica': 'fibromialgia', 'dor no corpo todo': 'fibromialgia',
}
