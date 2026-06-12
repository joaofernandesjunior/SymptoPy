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

def _sel(key, label, options, default=None, depends_on=None, help=None):
    f = {'key': key, 'type': 'select', 'label': label,
         'options': options, 'default': default or options[0][0]}
    if depends_on: f['depends_on'] = depends_on
    if help:       f['help'] = help
    return f

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
        'label': 'Queixa Urinária (ITU / Pielonefrite / Hematúria)',
        'sistema': 'Urologia',
        'blocks': [
            _block('1 · Queixa Principal + Sexo/Idade', [
                _sel ('queixa_principal','Queixa principal', [
                    ('disuria','Disúria / sintomas urinários'),
                    ('hematuria','Hematúria (sangue na urina)'),
                    ('ambos','Ambos'),
                ]),
            ]),
            _block('2 · Sintomas Irritativos / Baixos', [
                _bool('disuria',            'Disúria / ardência ao urinar'),
                _bool('frequencia',         'Polaciúria / frequência aumentada'),
                _bool('hesitancia',         'Hesitância (demora para iniciar)'),
                _bool('jato_fraco',         'Jato urinário fraco'),
                _bool('gotejamento_terminal','Gotejamento terminal'),
                _bool('retencao_urinaria',  'Retenção urinária', flag='yellow'),
                _bool('obstrucao_urinaria', 'Obstrução urinária', flag='yellow'),
                _bool('ipss_grave',         'IPSS grave (sintomas prostáticos intensos)'),
            ]),
            _block('3 · Sinais Sistêmicos / Pielonefrite (red flags)', [
                _bool('febre',          'Febre', flag='yellow'),
                _bool('calafrio',       'Calafrio com tremor', flag='yellow'),
                _bool('dor_lombar',     'Dor lombar / flanco'),
                _bool('ppd_positivo',   'Punho-percussão lombar (Giordano) positiva', flag='yellow',
                      help='Percussão com a borda da mão na loja renal. Dor = sinal de pielonefrite.'),
                _bool('nausea_vomito',  'Náusea / vômito'),
                _bool('hipotensao',     '⚠ Hipotensão (sepse urinária?)', flag='red'),
                _bool('alteracao_mental','⚠ Alteração mental (sepse no idoso?)', flag='red'),
            ]),
            _block('4 · Próstata / Masculino', [
                _sel ('toque_prostatico','Toque prostático (TR)', [
                    ('','— Não realizado'),
                    ('normal','Normal'),
                    ('doloroso_boggoso','Doloroso e amolecido/boggy (prostatite aguda)'),
                    ('nodular','Nodular endurecido (rastrear neoplasia)'),
                ], help='⚠️ Na prostatite aguda, NÃO fazer massagem prostática vigorosa (risco de bacteremia).'),
                _bool('dor_perineal',    'Dor perineal / pélvica'),
            ]),
            _block('5 · Genital / IST', [
                _bool('secrecao_uretral', 'Secreção uretral'),
                _bool('secrecao_vaginal', 'Secreção vaginal'),
                _sel ('corrimento_tipo',  'Tipo de corrimento', [
                    ('','— Nenhum / não se aplica'),
                    ('grumoso_branco','Grumoso branco (candidíase)'),
                    ('acinzentado','Acinzentado fétido (vaginose)'),
                    ('amarelo_esverdeado','Amarelo-esverdeado (tricomonas/IST)'),
                ]),
                _bool('prurido_genital',  'Prurido genital'),
                _bool('lesao_genital',    'Lesão genital (úlcera/vesícula)'),
                _bool('dispareunia',      'Dispareunia'),
                _bool('herpes_primeiro_episodio','Primeiro episódio de herpes', flag='yellow'),
                _bool('ist_risco',        'Risco de IST (parceiro novo/desprotegido)'),
            ]),
            _block('6 · Hematúria', [
                _bool('hematuria_macro',  'Hematúria macroscópica (visível)', flag='yellow'),
                _bool('hematuria_micro',  'Hematúria microscópica (só no EAS)'),
                _bool('hematuria_indolor','⚠ Hematúria indolor (neoplasia até prova contrária)', flag='red',
                      help='Hematúria macroscópica INDOLOR em > 35a = câncer urotelial até prova em contrário.'),
                _bool('hematuria_colicativa','Hematúria com cólica (litíase?)'),
                _bool('hematuria_fumaca', 'Urina cor de "fumaça"/coca-cola (glomerular?)'),
            ]),
            _block('7 · Contexto / Fatores de Risco', [
                _bool('gestante',        'Gestante', flag='yellow'),
                _bool('diabetes',        'Diabetes mellitus'),
                _bool('drc',             'Doença renal crônica', flag='yellow'),
                _bool('imunossupressao', 'Imunossupressão', flag='yellow'),
                _bool('cateter',         'Cateter / sonda vesical', flag='yellow'),
                _bool('itu_recorrente',  'ITU recorrente (≥ 2/ano)'),
                _bool('peri_pos_menopausa','Peri/pós-menopausa'),
                _bool('atb_recente_30d', 'ATB nos últimos 30 dias'),
                _bool('atb_fl_smx_3m',   'Quinolona/SMX-TMP nos últimos 3 meses'),
                _bool('tabagismo',       'Tabagismo (risco Ca urotelial)'),
                _bool('exposicao_ocupacional','Exposição ocupacional (aminas/corantes)'),
                _bool('radioterapia_pelvica','Radioterapia pélvica prévia'),
            ]),
            _block('8 · EAS / Urina (se disponível)', [
                _bool('eas_hemacias',        'EAS com hemácias'),
                _num ('eas_hemacias_hpf',    'Hemácias por campo (HPF)', 0, 200, 1, default=None),
                _bool('eas_hemacias_dismorfica','Hemácias dismórficas (glomerular)'),
                _bool('eas_proteinuria',     'Proteinúria no EAS'),
                _bool('eas_cilindros',       'Cilindros hemáticos (glomerular)'),
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
            _block('1 · Caracterização', [
                _num ('dias_sintomas',  'Dias de sintomas', 0, 60, 1, 3),
                _bool('odinofagia_severa','Odinofagia intensa'),
                _bool('tosse_presente', 'Tosse presente'),
                _bool('febre_38',       'Febre ≥ 38°C'),
                _bool('febre_alta_39',  'Febre alta ≥ 39°C'),
                _bool('mialgia_intensa','Mialgia intensa (influenza?)'),
                _bool('inicio_subito_horas','Início súbito (horas — influenza?)'),
            ]),
            _block('2 · Critérios de Centor (faringite)', [
                _bool('exsudato_tonsilar',     'Exsudato tonsilar', flag='yellow'),
                _bool('linfadenopatia_anterior','Linfonodos cervicais ANTERIORES dolorosos', flag='yellow'),
                _bool('linfadenopatia_posterior','Linfonodos cervicais POSTERIORES (mononucleose?)'),
            ]),
            _block('3 · Emergência de Vias Aéreas (red flags)', [
                _bool('trismo',             '⚠ Trismo (não abre a boca)', flag='red'),
                _bool('voz_abafada',        '⚠ Voz abafada / "batata quente"', flag='red'),
                _bool('sialorreia',         '⚠ Sialorreia (não engole saliva)', flag='red'),
                _bool('estridor',           '⚠ Estridor', flag='red'),
                _bool('dificuldade_respiratoria','⚠ Dificuldade respiratória', flag='red'),
                _bool('edema_submandibular','⚠ Edema submandibular (Ludwig?)', flag='red'),
                _bool('assimetria_tonsilar','⚠ Assimetria tonsilar (abscesso peritonsilar?)', flag='red'),
            ]),
            _block('4 · Rinossinusite / Laringite', [
                _bool('dor_facial',        'Dor/pressão facial'),
                _bool('descarga_purulenta','Descarga nasal purulenta'),
                _bool('sintomas_10_dias',  'Sintomas ≥ 10 dias sem melhora'),
                _bool('duplo_agravamento', 'Duplo agravamento (piora após melhora)'),
                _bool('rouquidao_predominante','Rouquidão predominante (laringite?)'),
            ]),
            _block('5 · Mononucleose', [
                _bool('esplenomegalia_referida','Esplenomegalia referida', flag='yellow'),
            ]),
            _block('6 · Teste Rápido (RADT/Strep)', [
                _bool('radt_realizado', 'RADT realizado'),
                _bool('radt_positivo',  'RADT positivo', depends_on='radt_realizado'),
                _bool('radt_disponivel','RADT disponível no serviço', default=True),
            ]),
            _block('7 · Alergia / Comorbidades', [
                _bool('alergia_penicilina',  'Alergia à penicilina'),
                _bool('alergia_anafilatica', 'Reação anafilática (grave)', flag='yellow', depends_on='alergia_penicilina'),
                _bool('historico_fra',       'Febre reumática prévia', flag='yellow'),
                _bool('aderencia_preocupa',  'Adesão preocupante (favorece benzatina IM)'),
                _bool('gestante',            'Gestante', flag='yellow'),
                _bool('diabetes',            'Diabetes'),
                _bool('imunossupressao',     'Imunossupressão', flag='yellow'),
                _bool('asma_dpoc',           'Asma / DPOC'),
                _bool('doenca_cardiovascular','Doença cardiovascular'),
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
            _block('Red Flags (SNOOP) — Verificar Primeiro', [
                _bool('pior_da_vida',     '⚠ "Pior cefaleia da vida"', flag='red',
                      help='Cefaleia súbita e intensíssima ("thunderclap"/em trovoada), atingindo o pico em segundos. '
                           'Suspeitar de hemorragia subaracnóidea (HSA) — TC + punção lombar.'),
                _bool('inicio_subito',    '⚠ Início explosivo/súbito (pico em segundos)', flag='red'),
                _bool('inicio_esforco_sexo','⚠ Começou em esforço/atividade sexual/Valsalva', flag='red',
                      help='Cefaleia desencadeada por esforço ou orgasmo pode ser HSA ou trombose — investigar.'),
                _bool('febre',            '⚠ Febre associada', flag='red'),
                _bool('rigidez_nuca',     '⚠ Rigidez de nuca', flag='red',
                      help='Febre + rigidez de nuca + cefaleia = meningite até prova em contrário.'),
                _bool('confusao',         '⚠ Confusão / alteração de consciência', flag='red'),
                _bool('deficit_focal',    '⚠ Déficit neurológico focal (relatado)', flag='red'),
                _bool('deficit_neuro',    '⚠ Déficit neurológico ao exame', flag='red'),
                _bool('papiledema',       '⚠ Papiledema ao fundo de olho', flag='red',
                      help='Papiledema = edema do disco óptico por hipertensão intracraniana (tumor, trombose, HIC idiopática).'),
                _bool('progressiva',      '⚠ Cefaleia progressiva (piora ao longo de dias/semanas)', flag='red'),
                _bool('idade_maior_50_nova','⚠ Cefaleia NOVA em paciente > 50 anos', flag='red',
                      help='Cefaleia de início recente após os 50a → excluir arterite temporal (VHS/PCR) e lesão expansiva.'),
                _bool('trauma',           '⚠ Pós-trauma craniano', flag='red'),
                _bool('cancer',           'História de câncer', flag='yellow'),
                _bool('imunossupressao',  'Imunossupressão', flag='yellow'),
            ]),
            _block('Padrão — Enxaqueca', [
                _bool('pulsatil',           'Dor pulsátil/latejante'),
                _bool('localizacao_unilateral','Unilateral (um lado da cabeça)'),
                _bool('piora_atividade',    'Piora com atividade física rotineira'),
                _bool('nausea',             'Náusea / vômito'),
                _bool('fotofobia',          'Fotofobia (luz incomoda)',
                      help='Fotofobia = desconforto à luz. Critério de enxaqueca.'),
                _bool('fonofobia',          'Fonofobia (som incomoda)',
                      help='Fonofobia = desconforto a sons. Critério de enxaqueca.'),
                _bool('aura',               'Aura antes da dor (visual/sensitiva)',
                      help='Aura = sintoma neurológico reversível que precede a dor (escotomas/zigue-zague luminoso, '
                           'formigamento). Dura 5–60 min.'),
            ]),
            _block('Padrão — Tensional', [
                _bool('pressao',            'Dor em pressão/aperto ("faixa na cabeça")',
                      help='Cefaleia tensional: dor opressiva bilateral, leve-moderada, SEM piora com esforço, '
                           'SEM náusea/fotofobia.'),
            ]),
            _block('Padrão — Cluster (em salvas)', [
                _bool('lacrimejamento',     'Lacrimejamento / olho vermelho do MESMO lado',
                      help='Sintomas autonômicos ipsilaterais (lacrimejamento, olho vermelho, congestão nasal, ptose) '
                           'acompanham a cefaleia em salvas.'),
                _bool('rinorreia',          'Congestão/corrimento nasal do mesmo lado'),
                _bool('agitacao',           'Agitação/inquietude durante a crise',
                      help='Na cefaleia em salvas o paciente fica AGITADO (anda, não para) — diferente da enxaqueca, '
                           'em que prefere ficar imóvel no escuro.'),
            ]),
            _block('Contexto / Secundária', [
                _num ('frequencia_mes','Episódios por mês', 0, 30, 1, 2),
                _bool('uso_analgesico_excessivo','Uso de analgésico > 10–15 dias/mês', flag='yellow',
                      help='Cefaleia por uso excessivo de medicação (rebote) — tratar com desmame do analgésico.'),
                _bool('nova_medicacao',     'Iniciou medicação nova recentemente (ex.: nitrato)'),
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
                _bool('gatilho_mudar_posicao','Desencadeada ao mudar de posição (deitar/virar na cama)',
                      help='Vertigem que SÓ surge ao mudar de posição e dura segundos = VPPB (vertigem posicional '
                           'paroxística benigna), causa mais comum. Cristais soltos no labirinto.'),
                _bool('gatilho_espontaneo',  'Surge espontaneamente (sem gatilho)'),
                _bool('continuo',            'Contínua / constante (dura o tempo todo)'),
                _bool('recorrente',          'Episódios que vão e voltam'),
                _bool('duracao_segundos_minutos','Cada episódio dura segundos a minutos (VPPB)'),
                _bool('duracao_horas',       'Cada episódio dura horas (Menière?)',
                      help='Vertigem de horas + zumbido + perda auditiva flutuante = doença de Menière (hidropisia endolinfática).'),
                _bool('duracao_dias',        'Dura dias contínuos (neurite vestibular?)',
                      help='Vertigem contínua por dias após virose, sem perda auditiva = neurite vestibular.'),
            ]),
            _block('Red Flags — AVC de Fossa Posterior', [
                _bool('incapaz_de_andar', '⚠ ATAXIA SEVERA — não consegue ficar de pé/andar sem apoio', flag='red',
                      help='Ataxia = incoordenação/desequilíbrio. NÃO conseguir ficar de pé sem apoio é o sinal '
                           'isolado MAIS forte de AVC cerebelar — encaminhar mesmo se o resto parecer benigno.'),
                _bool('deficit_focal',    '⚠ Déficit neurológico focal (fraqueza/dormência localizada)', flag='red'),
                _bool('diplopia',         '⚠ Visão dupla (diplopia)', flag='red'),
                _bool('disartria',        '⚠ Fala arrastada (disartria)', flag='red',
                      help='Disartria = dificuldade de articular a fala. Sinal de tronco/cerebelo.'),
                _bool('fraqueza',         '⚠ Fraqueza em membro', flag='red'),
                _bool('parestesias',      '⚠ Dormência/formigamento (parestesias)', flag='red'),
                _bool('cefaleia',         'Cefaleia súbita associada', flag='yellow',
                      help='Cefaleia occipital súbita + vertigem pode indicar dissecção de artéria vertebral / AVC cerebelar.'),
                _bool('hints_preocupante','⚠ HINTS sugestivo de CENTRAL', flag='red',
                      help='HINTS = 3 testes oculares (Head Impulse, Nystagmus, Test of Skew) na vertigem CONTÍNUA. '
                           'Padrão CENTRAL (preocupante) = impulso cefálico NORMAL + nistagmo que muda de direção + '
                           'skew (desalinhamento vertical dos olhos). Mais sensível que RM nas primeiras 48h.'),
            ]),
            _block('Exame + Ortostase', [
                _bool('dix_hallpike_positivo', 'Dix-Hallpike positivo (confirma VPPB de canal posterior)',
                      help='Manobra de Dix-Hallpike: deitar o paciente rápido com a cabeça virada 45° e pendente. '
                           'Surgir vertigem + nistagmo após latência = VPPB de canal posterior → tratar com Epley.'),
                _bool('roll_test_positivo',    'Roll test positivo (VPPB de canal horizontal)',
                      help='Roll test (supine roll): deitado, girar a cabeça para cada lado. Positivo = VPPB de canal horizontal.'),
                _bool('canal_horizontal',      'Acometimento do canal horizontal',
                      help='VPPB de canal horizontal — tratada com manobra de Lempert/BBQ (não Epley).'),
                _bool('ortostatismo_sugestivo','Tontura ao levantar (sugere hipotensão ortostática)'),
            ]),
            _block('Sintomas Cocleares / Associados', [
                _bool('zumbido',            'Zumbido / chiado (tinnitus)',
                      help='Tinnitus = zumbido. Junto com perda auditiva e vertigem aponta para causa periférica/labiríntica (Menière).'),
                _bool('perda_auditiva',     'Perda auditiva'),
                _bool('plenitude_auricular','Sensação de ouvido cheio/tampado (plenitude auricular)'),
                _bool('sincope',            'Síncope associada', flag='yellow'),
            ]),
        ],
        'engine': 'modules.raciocinio.vertigem_dx',
        'engine_fn': 'interpretar_vertigem',
        'legacy': True,
    },

    # ── DIARREIA ─────────────────────────────────────────────────────────────
    'diarreia': {
        'label': 'Diarreia',
        'sistema': 'Gastro/Abdominal',
        'blocks': [
            _block('1 · Caracterização', [
                _num ('duracao_dias',   'Duração (dias)', 0, 365, 1, 2,
                      help='< 14d aguda · 14–30d persistente · > 30d crônica.'),
                _bool('fezes_sanguinolentas','⚠ Fezes com sangue (disenteria)', flag='red'),
                _bool('nausea',         'Náusea'),
                _bool('vomito',         'Vômito'),
                _bool('febre',          'Febre'),
                _bool('febre_38_5',     'Febre ≥ 38,5°C'),
                _bool('nocturna',       'Diarreia noturna (desperta — orgânica?)', flag='yellow'),
            ]),
            _block('2 · Desidratação', [
                _sel ('desidratacao_grau','Grau de desidratação', [
                    ('sem','Sem desidratação'),
                    ('leve','Leve'),
                    ('moderada','Moderada'),
                    ('grave','Grave'),
                ]),
                _bool('sede_intensa',     'Sede intensa'),
                _bool('mucosas_ressecadas','Mucosas ressecadas'),
                _bool('olhos_fundos',     'Olhos fundos'),
                _bool('oliguria',         'Oligúria / urina escura'),
                _bool('tontura_ortostase','Tontura ao levantar (ortostase)'),
            ]),
            _block('3 · Red Flags — Sepse / Grave', [
                _bool('sinais_sepse',          '⚠ Sinais de sepse', flag='red'),
                _bool('hipotensao_conhecida',  '⚠ Hipotensão', flag='red'),
                _bool('alteracao_consciencia', '⚠ Alteração de consciência', flag='red'),
                _bool('extremidades_frias',    '⚠ Extremidades frias / má perfusão', flag='red'),
                _bool('dor_abdominal_peritoneal','⚠ Dor abdominal com peritonismo', flag='red'),
            ]),
            _block('4 · Contexto Epidemiológico', [
                _bool('viagem_recente',  'Viagem recente'),
                _bool('viagem_asia',     'Viagem para Ásia/Sudeste asiático'),
                _bool('surto_alimentar', 'Surto / refeição coletiva suspeita'),
                _bool('alimento_suspeito','Alimento específico suspeito'),
                _num ('incubacao_horas', 'Tempo de incubação (horas, se conhecido)', 0, 168, 1, default=None),
                _bool('atb_recente_3m',  'Antibiótico nos últimos 3 meses (C. diff?)', flag='yellow'),
                _bool('internacao_recente_3m','Internação nos últimos 3 meses'),
            ]),
            _block('5 · Crônica / Funcional (pistas)', [
                _bool('dor_melhora_evacuacao','Dor melhora ao evacuar (SII?)'),
                _bool('piora_estresse',   'Piora com estresse'),
                _bool('piora_com_gluten', 'Piora com glúten (celíaca?)'),
                _bool('piora_com_lacteos','Piora com lácteos (intolerância?)'),
                _bool('perda_peso_involuntaria','⚠ Perda de peso involuntária', flag='red'),
                _bool('hematochezia_cronica','Hematoquezia crônica', flag='yellow'),
                _bool('hf_ccr_primeiro_grau','História familiar de CCR 1º grau', flag='yellow'),
                _bool('anemia_sintomas',  'Sintomas de anemia'),
            ]),
            _block('6 · Imunossupressão / Fármacos / Contexto', [
                _bool('imunossuprimido', 'Imunossuprimido', flag='yellow'),
                _bool('hiv_diagnosticado','HIV diagnosticado'),
                _bool('corticoide_cronico','Corticoide crônico'),
                _bool('transplante_quimio_biologico','Transplante / quimio / biológico', flag='yellow'),
                _bool('uso_aine_recente', 'AINE recente'),
                _bool('metformina_dose_alta','Metformina dose alta'),
                _bool('medicamentos_suspeitos_diarreia','Outro medicamento suspeito'),
            ]),
        ],
        'engine': 'modules.raciocinio.diarreia.engine_diarreia',
        'engine_fn': 'interpretar_diarreia',
    },

    # ── ARBOVIROSES ──────────────────────────────────────────────────────────
    'arboviroses': {
        'label': 'Arboviroses (Dengue / Chikungunya / Zika)',
        'sistema': 'Infectologia',
        'blocks': [
            _block('1 · Quadro Febril', [
                _bool('febre_presente',   'Febre presente'),
                _bool('febre_alta',       'Febre alta (≥ 39°C)'),
                _num ('dias_febre',       'Dias de febre', 0, 21, 1, 3),
                _bool('inicio_subito',    'Início súbito'),
                _bool('dor_retroorbitaria','Dor retro-orbitária'),
                _bool('mialgia_intensa',  'Mialgia intensa ("febre quebra-ossos")'),
                _bool('area_endemica',    'Área endêmica / surto local'),
            ]),
            _block('2 · Exantema / Conjuntiva (Zika)', [
                _bool('exantema_presente',     'Exantema / manchas vermelhas'),
                _bool('exantema_pruriginoso',  'Exantema pruriginoso (sugere Zika)'),
                _bool('conjuntivite_nao_purulenta','Conjuntivite não purulenta (sugere Zika)'),
            ]),
            _block('3 · Artralgia (Chikungunya)', [
                _bool('artralgia_presente',     'Artralgia presente'),
                _bool('artralgia_incapacitante','Artralgia incapacitante'),
                _bool('artralgia_simetrica',    'Artralgia simétrica'),
                _bool('edema_articular',        'Edema articular'),
                _bool('artralgia_meses',        'Artralgia persistente por meses (crônica)'),
            ]),
            _block('4 · Sinais de Alarme — Dengue (MS 2025)', [
                _bool('dor_abdominal_intensa', '⚠ Dor abdominal intensa e contínua', flag='red'),
                _bool('vomitos_persistentes',  '⚠ Vômitos persistentes', flag='red'),
                _bool('acumulo_liquidos',      '⚠ Acúmulo de líquidos (ascite/derrame)', flag='red'),
                _bool('hipotensao_postural',   '⚠ Hipotensão postural / lipotimia', flag='red'),
                _bool('hepatomegalia_referida','⚠ Hepatomegalia dolorosa > 2 cm', flag='red'),
                _bool('sangramento_mucosa',    '⚠ Sangramento de mucosa', flag='red'),
                _bool('letargia_irritabilidade','⚠ Letargia / irritabilidade', flag='red'),
                _bool('aumento_hematocrito',   '⚠ Aumento progressivo do hematócrito (≥ 10%)', flag='red'),
                _bool('prova_laco_positiva',   'Prova do laço positiva'),
            ]),
            _block('5 · Sinais de Choque — Dengue Grave (Grupo D)', [
                _bool('hipotensao_severa', '🔴 Hipotensão severa', flag='red'),
                _bool('pulso_filiforme',   '🔴 Pulso filiforme', flag='red'),
                _bool('tec_maior_3s',      '🔴 Tempo de enchimento capilar > 3s', flag='red'),
                _bool('sudorese_fria',     '🔴 Sudorese fria / extremidades frias', flag='red'),
            ]),
            _block('6 · Comorbidades / Risco (Grupo B)', [
                _bool('gestante',          'Gestante', flag='yellow'),
                _num ('semanas_gestacao',  'Semanas de gestação', 0, 42, 1, default=None, depends_on='gestante'),
                _bool('diabetes',          'Diabetes mellitus'),
                _bool('has_cardiovascular','HAS / doença cardiovascular'),
                _bool('hematologica',      'Doença hematológica (falciforme/plaquetopenia)'),
                _bool('drc',               'Doença renal crônica'),
                _bool('doenca_hepatica',   'Doença hepática prévia'),
                _bool('obesidade_grave',   'Obesidade grave (IMC > 40)'),
                _bool('extremo_idade',     'Extremo de idade (< 2 ou > 60 anos)'),
                _bool('risco_social',      'Risco social (mora só / sem acesso a UBS)'),
            ]),
            _block('7 · Laboratório / Contexto', [
                _sel ('ns1_resultado', 'NS1 (dengue)', [
                    ('nao_realizado','Não realizado'),
                    ('positivo','Positivo'),
                    ('negativo','Negativo'),
                ]),
                _num ('peso_kg', 'Peso (kg) — p/ cálculo de hidratação', 2, 200, 1, 70),
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
                    # valor 'crise' — é o que o engine_asma reconhece (≠ dpoc, que usa 'exacerbacao')
                    ('crise',  'Crise / exacerbação aguda'),
                    ('rotina', 'Controle / rotina'),
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
            _block('Emergência / Abscesso (red flags)', [
                _bool('estridor',        '⚠ Estridor', flag='red',
                      help='Som agudo na INSPIRAÇÃO por obstrução de via aérea alta. Emergência — risco de asfixia.'),
                _bool('dificuldade_respiratoria', '⚠ Dificuldade respiratória', flag='red'),
                _bool('trismo',          '⚠ Trismo (não consegue abrir a boca)', flag='red',
                      help='Dificuldade/impossibilidade de abrir a boca por espasmo do masseter. Sugere abscesso peritonsilar.'),
                _bool('sialorreia',      '⚠ Sialorreia (baba — não engole a saliva)', flag='red',
                      help='Acúmulo de saliva porque engolir dói/obstrui. Sinal de abscesso ou epiglotite.'),
                _bool('voz_batata',      '⚠ Voz "de batata quente" (abafada)', flag='red',
                      help='Voz abafada, como quem fala com algo quente na boca. Indica massa/abscesso na orofaringe.'),
                _bool('desvio_uvula',    '⚠ Desvio da úvula para um lado', flag='red',
                      help='A "campainha" no fundo da garganta empurrada para o lado oposto = abscesso peritonsilar.'),
                _bool('disfagia_saliva', '⚠ Não consegue engolir nem a própria saliva', flag='red'),
            ]),
            _block('Critérios de Centor (probabilidade de estreptococo)', [
                _bool('febre',                'Febre', help='Centor: febre conta +1 ponto.'),
                _bool('exsudato_amigdaliano', 'Exsudato/placas nas amígdalas',
                      help='Pus/placas brancas sobre as amígdalas. Centor +1.'),
                _bool('adenopatia_cervical_ant','Gânglios cervicais ANTERIORES dolorosos',
                      help='Linfonodos aumentados/doloridos na frente do pescoço. Centor +1.'),
                _bool('tosse',                'Tosse presente',
                      help='AUSÊNCIA de tosse pontua no Centor (+1). Tosse presente sugere causa viral.'),
            ]),
            _block('Mononucleose (EBV)', [
                _bool('adenopatia_generalizada','Gânglios aumentados também em axila/virilha',
                      help='Adenopatia difusa (não só pescoço) + faringite em jovem 15-25a sugere mononucleose.'),
                _bool('esplenomegalia_referida','Baço aumentado / dor no QSE',
                      help='Esplenomegalia na mono contraindica esportes de contato (risco de ruptura).'),
                _bool('rash_apos_amox',  'Rash após tomar amoxicilina',
                      help='Erupção cutânea após amoxicilina na mono (não é alergia) — pista retrospectiva de EBV.'),
            ]),
            _block('Rouquidão', [
                _bool('rouquidao',          'Rouquidão associada'),
                _bool('rouquidao_cronica',  'Rouquidão > 3 semanas', flag='yellow',
                      help='Rouquidão persistente > 3 semanas, sobretudo em tabagista, exige rastrear câncer de laringe.'),
            ]),
            _block('Contexto / Alergia', [
                _num ('temperatura_grau', 'Temperatura (°C)', 35.0, 42.0, 0.1, default=None),
                _bool('atb_recente_30d',      'ATB nos últimos 30 dias'),
                _bool('alergia_penicilina',   'Alergia à penicilina'),
                _bool('alergia_penicilina_grave', 'Reação foi grave/anafilática', flag='yellow', depends_on='alergia_penicilina',
                      help='Anafilaxia/urticária/edema → evitar TODOS beta-lactâmicos; usar azitromicina.'),
            ]),
        ],
        'engine': 'modules.raciocinio.orl.engine_odinofagia', 'engine_fn': 'interpretar_odinofagia',
    },

    # ── OTALGIA (ORL) ────────────────────────────────────────────────────────
    'otalgia': {
        'label': 'Otalgia / Dor de Ouvido', 'sistema': 'ORL',
        'blocks': [
            _block('Mastoidite (red flag)', [
                _bool('dor_retroauricular', '⚠ Dor ATRÁS da orelha', flag='red',
                      help='Dor/edema sobre o osso mastoide (atrás do pavilhão) = mastoidite, complicação da otite média.'),
                _bool('pavilhao_projetado', '⚠ Orelha "empurrada" para frente', flag='red',
                      help='O pavilhão auricular projetado/deslocado para fora é sinal clássico de mastoidite.'),
                _bool('flutuacao_retroaur', '⚠ Abaulamento com flutuação atrás da orelha', flag='red',
                      help='Coleção/abscesso subperiosteal — flutuação à palpação atrás da orelha.'),
                _bool('febre_mais_72h_atb', 'Febre persiste > 72h mesmo com ATB', flag='yellow'),
            ]),
            _block('Otite Externa (OE)', [
                _bool('trago_positivo',  'Dor ao apertar/tracionar o trago',
                      help='Trago = a saliência cartilaginosa na frente do canal auditivo. Dor ao pressioná-lo/puxar o '
                           'pavilhão indica otite EXTERNA (inflamação do canal), não média.'),
                _bool('canal_edema',     'Canal auditivo edemaciado/estreitado'),
                _bool('canal_estenose',  'Canal estreitado com tecido de granulação', flag='yellow',
                      help='Granulação no assoalho do canal + diabético/idoso → suspeitar otite externa MALIGNA (osteomielite de base de crânio).'),
                _bool('banho_piscina',   'Exposição a água/piscina ("ouvido de nadador")'),
                _bool('otalgia_grave',   'Otalgia intensa'),
            ]),
            _block('Otite Média Aguda (OMA)', [
                _bool('iras_recente',    'Resfriado/IVAS precedeu'),
                _bool('ouvido_cheio',    'Sensação de ouvido cheio/tampado'),
                _bool('hipoagusia',      'Hipoacusia (perda auditiva)',
                      help='Hipoacusia = diminuição da audição.'),
                _bool('febre',           'Febre'),
                _bool('mt_abaulada',     'Membrana timpânica ABAULADA', flag='yellow',
                      help='MT = membrana timpânica (tímpano). Abaulamento (saliência) à otoscopia = pus no ouvido médio, '
                           'sinal mais específico de OMA.'),
                _bool('mt_hiperemia',    'Tímpano hiperemiado (vermelho)',
                      help='Hiperemia isolada é inespecífica (pode ser só choro/febre) — vale com abaulamento.'),
                _bool('mt_efusao',       'Líquido/efusão atrás do tímpano'),
                _bool('mt_perfurada',    'Tímpano perfurado'),
                _bool('otorreia',        'Otorreia (secreção saindo do ouvido)',
                      help='Otorreia = saída de secreção pelo conduto auditivo.'),
                _bool('otorreia_purulenta','Otorreia PURULENTA (pus)'),
            ]),
            _block('Tratar Imediato (sem observação/"watchful waiting")', [
                _bool('febre_alta',       'Febre ≥ 39°C'),
                _bool('bilateral',        'Bilateral (os dois ouvidos)'),
                _bool('otalgia_mais_48h', 'Dor há mais de 48h'),
                _bool('seguimento_incerto','Retorno/seguimento não garantido'),
                _bool('conjuntivite_purulenta','Conjuntivite purulenta junto (síndrome otite-conjuntivite)'),
                _bool('oma_recorrente',   'Otite de repetição'),
                _bool('atb_recente_30d',  'ATB nos últimos 30 dias'),
            ]),
            _block('DTM — Disfunção Temporomandibular (causa NÃO otológica)', [
                _bool('dor_mastigacao',  'Dor ao mastigar',
                      help='DTM = disfunção da articulação temporomandibular (mandíbula). Causa comum de "dor de ouvido" '
                           'sem doença no ouvido — dor referida.'),
                _bool('dor_matinal',     'Dor mandibular ao acordar'),
                _bool('bruxismo',        'Range/aperta os dentes (bruxismo)'),
                _bool('click_mandibula', 'Estalo na mandíbula ao abrir a boca'),
                _bool('limitacao_abertura','Dificuldade/limitação de abrir a boca'),
                _bool('dor_temporal',    'Dor na região temporal'),
            ]),
            _block('Contexto', [
                _num ('temperatura_grau', 'Temperatura (°C)', 35.0, 42.0, 0.1, default=None),
                _sel ('lateralidade', 'Lado', [('','—'),('direita','Direita'),('esquerda','Esquerda'),('bilateral','Bilateral')]),
                _bool('diabetes', 'Diabetes (risco de otite externa maligna)', flag='yellow'),
            ]),
        ],
        'engine': 'modules.raciocinio.orl.engine_otalgia', 'engine_fn': 'interpretar_otalgia',
    },

    # ── RINOSSINUSITE (ORL) ──────────────────────────────────────────────────
    'rinossinusite': {
        'label': 'Rinossinusite / Obstrução Nasal', 'sistema': 'ORL',
        'blocks': [
            _block('Red Flags — Complicações (PS imediato)', [
                _bool('edema_periorbital',  '⚠ Inchaço/vermelhidão ao redor do olho', flag='red',
                      help='Edema periorbital = complicação orbitária da sinusite (celulite orbitária). Emergência.'),
                _bool('diplopia',           '⚠ Visão dupla (diplopia)', flag='red',
                      help='Diplopia + sinusite = invasão orbitária comprometendo músculos oculares. PS imediato.'),
                _bool('proptose',           '⚠ Olho "saltado" para fora (proptose)', flag='red',
                      help='Proptose = protrusão do globo ocular. Sinal de abscesso/celulite orbitária.'),
                _bool('rigidez_nucal',      '⚠ Rigidez de nuca', flag='red',
                      help='Pescoço duro para fletir = sinal meníngeo. Sinusite pode complicar com meningite/abscesso cerebral.'),
                _bool('cefaleia_intensa',   '⚠ Cefaleia muito intensa / "pior da vida"', flag='red'),
                _bool('alteracao_consciencia','⚠ Confusão / sonolência', flag='red'),
            ]),
            _block('Caracterização', [
                _num ('duracao_dias_aprox', 'Duração dos sintomas (dias)', 0, 120, 1, 5,
                      help='< 10 dias → quase sempre viral. ≥ 10 dias sem melhora → considerar bacteriana (RSAB).'),
                _bool('obstrucao_nasal',    'Nariz entupido / obstrução'),
                _bool('rinorreia_purulenta','Secreção nasal purulenta (amarelo-esverdeada)',
                      help='Rinorreia = coriza/secreção nasal. Purulenta isolada NÃO confirma bactéria (vírus também causa).'),
                _bool('rinorreia_clara',    'Secreção nasal clara/aquosa'),
                _bool('dor_facial',         'Dor/pressão na face (seios da face)'),
                _bool('dor_facial_unilateral','Dor facial em UM lado só',
                      help='Dor facial unilateral + febre + purulência sugere rinossinusite bacteriana.'),
                _bool('hiposmia_anosmia',   'Redução/perda do olfato (hiposmia/anosmia)',
                      help='Hiposmia = olfato diminuído; anosmia = ausência de olfato.'),
                _bool('febre',              'Febre'),
                _bool('febre_alta',         'Febre alta (≥ 39°C)'),
                _bool('double_sickening',   '"Double-sickening" — piorou depois de ter melhorado', flag='yellow',
                      help='Piora bifásica: o paciente estava melhorando do resfriado e voltou a piorar. '
                           'Forte indício de infecção bacteriana secundária (RSAB).'),
            ]),
            _block('Componente Alérgico', [
                _bool('espirros_salva',     'Espirros em salva (crises de vários seguidos)'),
                _bool('prurido_nasal_ocular','Coceira no nariz e nos olhos'),
                _bool('piora_sazonal',      'Piora em certas estações/ambientes'),
                _bool('alergenos_conhecidos','Rinite alérgica já conhecida'),
                _bool('polipos_conhecidos', 'Pólipos nasais conhecidos'),
                _bool('corticoide_nasal_uso','Já usa corticoide nasal (spray)'),
            ]),
            _block('Contexto / Alergia', [
                _bool('atb_recente_30d',      'ATB no último mês'),
                _bool('imunossuprimido',      'Imunossuprimido', flag='yellow',
                      help='Imunossuprimido + sinusite → atenção para sinusite fúngica invasiva (mucormicose). Emergência.'),
                _bool('alergia_betalactamico','Alergia a penicilina/cefalosporina'),
                _bool('alergia_tipo_1',       'Reação foi grave/anafilática', flag='yellow', depends_on='alergia_betalactamico',
                      help='Tipo I (anafilaxia/urticária) → evitar todos beta-lactâmicos; usar doxiciclina.'),
            ]),
            _block('Cronicidade / Complemento', [
                _bool('duracao_cronica',    'Sintomas há ≥ 12 semanas (rinossinusite CRÔNICA)', flag='yellow',
                      help='RSC = rinossinusite crônica (≥ 12 semanas). Manejo distinto: corticoide nasal prolongado, '
                           'investigar pólipos/alergia, encaminhar ORL — não é caso de antibiótico curto.'),
                _bool('gotejamento_pos_nasal','Gotejamento pós-nasal (secreção escorrendo na garganta)'),
                _bool('rinorreia',          'Rinorreia (coriza) presente'),
            ]),
        ],
        'engine': 'modules.raciocinio.orl.engine_rinossinusite', 'engine_fn': 'interpretar_rinossinusite',
    },

    # ── OLHO VERMELHO (Oftalmo) ──────────────────────────────────────────────
    'olho_vermelho': {
        'label': 'Olho Vermelho', 'sistema': 'Oftalmo',
        'blocks': [
            _block('Red Flags — Emergência Oftalmológica', [
                _bool('dor_intensa',       '⚠ Dor ocular intensa (não só ardência)', flag='red',
                      help='Dor PROFUNDA/intensa difere de ardência leve. Sugere uveíte, glaucoma agudo ou ceratite — não conjuntivite.'),
                _bool('visao_turva',       '⚠ Visão embaçada / queda da acuidade', flag='red',
                      help='Conjuntivite NÃO baixa a visão. Visão turva = sinal de alarme (córnea, câmara anterior, glaucoma).'),
                _bool('halos_coloridos',   '⚠ Vê halos coloridos ao redor de luzes', flag='red',
                      help='Halos = edema de córnea por pressão intraocular alta → glaucoma agudo de ângulo fechado.'),
                _bool('fotofobia',         'Fotofobia (luz incomoda muito)', flag='yellow',
                      help='Fotofobia = dor/desconforto à luz. Forte em uveíte e ceratite.'),
                _bool('ciliary_flush',     '⚠ Vermelhidão em ANEL ao redor da íris (ciliary flush)', flag='red',
                      help='Ciliary flush = injeção (vermelhidão) concentrada ao redor da córnea/íris (perilímbica). '
                           'Indica doença intraocular séria (uveíte, glaucoma, ceratite) — diferente da vermelhidão difusa da conjuntivite.'),
                _bool('lente_de_contato',  '⚠ Usa lente de contato', flag='red',
                      help='Lente de contato + olho vermelho doloroso = ceratite (úlcera de córnea), muitas vezes por Pseudomonas. Risco de perfuração.'),
                _bool('dormiu_com_lente',  'Dormiu com a lente de contato', flag='red'),
                _bool('lente_uso_irregular','Uso/higiene irregular da lente'),
                _bool('pos_cirurgico_ocular','⚠ Cirurgia ocular recente', flag='red',
                      help='Pós-operatório recente + dor + baixa visão = endoftalmite (infecção intraocular). Emergência.'),
                _bool('trauma_quimico',    '⚠ Trauma químico (respingo de produto)', flag='red',
                      help='Queimadura química = IRRIGAR ABUNDANTEMENTE na hora, antes de qualquer outra coisa.'),
                _bool('trauma_penetrante', '⚠ Trauma penetrante / corpo estranho de alta energia', flag='red'),
            ]),
            _block('Pálpebra / Órbita', [
                _bool('edema_palpebral',    'Inchaço da pálpebra'),
                _bool('limitacao_motilidade','⚠ Dor/limitação ao mover o olho', flag='red',
                      help='Dor à movimentação ocular + proptose = celulite ORBITÁRIA (atrás do septo). Emergência, ≠ celulite pré-septal.'),
                _bool('proptose',           '⚠ Olho saltado (proptose)', flag='red'),
                _bool('eritema_palpebral',  'Vermelhidão localizada na pálpebra (terçol?)'),
                _bool('febre',              'Febre'),
            ]),
            _block('Secreção / Padrão (conjuntivite)', [
                _bool('secrecao_purulenta', 'Secreção purulenta (pus amarelo)',
                      help='Secreção purulenta + pálpebras coladas = conjuntivite bacteriana.'),
                _bool('palpebra_grudada',   'Pálpebras coladas/grudadas ao acordar'),
                _bool('secrecao_aquosa',    'Secreção aquosa/clara'),
                _bool('lacrimejamento',     'Lacrimejamento'),
                _bool('bilateral',          'Os dois olhos'),
                _bool('adenopatia_preauricular','Gânglio dolorido à frente da orelha',
                      help='Adenopatia pré-auricular (linfonodo na frente da orelha) acompanha conjuntivite VIRAL (adenovírus).'),
                _bool('contato_conjuntivite','Contato com alguém com conjuntivite'),
                _bool('dor_ocular',         'Ardência/desconforto leve a moderado'),
                _bool('corpo_estranho_sensacao','Sensação de areia/corpo estranho'),
                _bool('hemorragia_subconj', 'Mancha vermelha de sangue no branco do olho',
                      help='Hemorragia subconjuntival = sangue sob a conjuntiva. Assusta mas é benigna se isolada, sem dor nem baixa visão.'),
            ]),
            _block('Alérgico', [
                _bool('prurido_ocular',     'Coceira nos olhos (prurido)',
                      help='Prurido (coceira) é o sintoma DOMINANTE da conjuntivite alérgica.'),
                _bool('rinite_alergica_concomitante','Rinite/coriza alérgica junto'),
                _bool('rinite_alergica_conhecida','Rinite alérgica conhecida'),
                _bool('piora_sazonal_ocular','Piora em certas estações'),
            ]),
            _block('Contexto', [
                _sel ('lateralidade', 'Lado', [('','—'),('direito','Direito'),('esquerdo','Esquerdo'),('bilateral','Bilateral')]),
                _bool('profissional_saude', 'Profissional de saúde (risco conjuntivite viral/surto)'),
                _num ('pio_mmhg', 'PIO — pressão intraocular (mmHg, se tonômetro)', 0, 80, 1, default=None,
                      help='PIO = pressão intraocular. Normal 10–21 mmHg. > 30–40 com dor/halos = glaucoma agudo.'),
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
                _bool('obesidade_ou_oa_associada','Obesidade / OA associada'),
                _bool('trabalho_ajoelhado',   'Trabalho ajoelhado'),
            ]),
            _block('Achados Complementares', [
                _bool('dor_medial_abaixo_linha_articular','Dor medial ABAIXO da linha articular (pata de ganso / bursite anserina)'),
                _bool('dor_palpacao_facetas_patelares','Dor à palpação das facetas patelares (patelofemoral)'),
                _bool('dor_cruzar_pernas',     'Dor ao cruzar as pernas (patelofemoral)'),
                _bool('transiluminacao_positiva','Transiluminação positiva (cisto de Baker / massa cística)'),
                _bool('oa_ou_lesao_meniscal_conhecida','OA ou lesão meniscal já conhecida'),
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
                _bool('diabetes',             'Diabetes (risco capsulite)'),
                _bool('hipotireoidismo',      'Hipotireoidismo'),
            ]),
            _block('Localização da Dor + Palpação', [
                _bool('dor_subacromia_lateral',   'Dor subacromial/lateral (manguito/impacto)'),
                _bool('dor_palpacao_subacromia',  'Dor à palpação subacromial'),
                _bool('dor_anterior_bicipital',   'Dor anterior bicipital'),
                _bool('dor_palpacao_sulco_bicipital','Dor à palpação do sulco bicipital'),
                _bool('dor_superior_ac',          'Dor superior na articulação AC'),
                _bool('deformidade_ac',           'Deformidade AC (degrau/tecla de piano)'),
                _bool('dor_posterior',            'Dor posterior'),
            ]),
            _block('Movimento / Função', [
                _bool('fraqueza_abducao',         'Fraqueza de abdução'),
                _bool('dificuldade_alcance_posterior','Dificuldade de alcance posterior (mão nas costas)'),
                _bool('piora_adducao_cruzada',    'Piora à adução cruzada (cross-body — AC)'),
                _bool('piora_deceleracao',        'Piora na desaceleração do arremesso (SLAP/instabilidade)'),
                _bool('sensacao_dando_tranco',    'Sensação de "dar tranco"/subluxação (instabilidade)'),
            ]),
            _block('Contexto Adicional', [
                _bool('atleta_arremessador',      'Atleta arremessador'),
                _bool('trauma_ac_previo',         'Trauma prévio na AC'),
                _bool('cirurgia_ou_imobilizacao_previa','Cirurgia/imobilização prévia (capsulite?)'),
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
                _bool('dor_nova',             'Dor nova (primeiro episódio)'),
                _bool('bacteremia_recente',   'Bacteremia / infecção recente', flag='yellow'),
            ]),
            _block('Padrão / Exame Complementar', [
                _bool('dor_cronica',              'Dor crônica (> 12 semanas)'),
                _bool('dor_generalizada_ou_difusa','Dor generalizada/difusa (considerar fibromialgia)'),
                _bool('melhora_com_atividade_leve','Melhora com atividade leve (inflamatório)'),
                _bool('preferencia_direcional_extensao','Melhora em extensão (estenose/McKenzie)'),
                _bool('preferencia_direcional_flexao','Melhora em flexão (hérnia/McKenzie)'),
                _bool('espasmo_muscular_paravertebral','Espasmo muscular paravertebral'),
                _bool('dor_palpacao_processos_espinhosos','Dor à palpação dos processos espinhosos', flag='yellow',
                      help='Dor à percussão de processo espinhoso → red flag de fratura/infecção/neoplasia.'),
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
            _block('Escafoide / Trauma (complemento)', [
                _bool('tuberculo_escafoide_palmar','Dor no tubérculo do escafoide (palmar)', flag='yellow',
                      help='Escafoide: dor na tabaqueira + tubérculo + compressão axial = imobilizar mesmo com Rx normal.'),
                _bool('compressao_axial_polegar_positiva','Compressão axial do polegar dolorosa (escafoide)'),
                _bool('tabaqueira_positiva',      'Dor na tabaqueira anatômica'),
                _bool('limitacao_movimento_trauma','Limitação de movimento pós-trauma'),
            ]),
            _block('Túnel do Carpo / Ulnar (complemento)', [
                _bool('parestesia_territorio_ulnar','Parestesia em território ulnar (4º-5º dedos)'),
                _bool('froment_positivo',         'Sinal de Froment positivo (n. ulnar)',
                      help='Froment: paciente segura papel entre polegar e indicador; flexão do polegar = fraqueza adutora ulnar.'),
                _bool('atrofia_tenar_percebida',  'Atrofia tenar percebida pelo paciente'),
                _bool('fraqueza_pinca_oponencia', 'Fraqueza de pinça/oponência'),
            ]),
            _block('Dedo em Gatilho / Rizartrose / De Quervain (complemento)', [
                _bool('estalido_bloqueio_dedo',   'Estalido/bloqueio do dedo (gatilho)'),
                _bool('nodulo_palpavel_palma',    'Nódulo palpável na palma (polia A1)'),
                _bool('proeminencia_dorsal_polegar','Proeminência dorsal na base do polegar'),
                _bool('piora_pincar_girar',       'Piora ao pinçar/girar (rizartrose)'),
                _bool('traction_shift_positivo',  'Traction-shift positivo (rizartrose)'),
            ]),
            _block('Inflamatório / Padrão (complemento)', [
                _bool('squeeze_mcf_positivo',     'Squeeze test MCF positivo (sinovite)',
                      help='Compressão transversal das MCF/MTF dolorosa = sinovite inflamatória (AR).'),
                _bool('mcf_punho_afetados',       'MCF e punho afetados (padrão AR)'),
                _bool('ifd_poupadas_exame',       'IFD poupadas ao exame (a favor de AR)'),
                _bool('ifd_preservadas',          'IFD preservadas (relato)'),
            ]),
            _block('Contexto Ocupacional / Risco (complemento)', [
                _bool('pos_menopausa_feminino',   'Feminina pós-menopausa'),
                _bool('gestante_ou_puerpera',     'Gestante / puérpera'),
                _bool('obesidade',                'Obesidade'),
                _bool('piora_trabalho_computador','Piora com trabalho no computador'),
                _bool('uso_smartphone_intenso',   'Uso intenso de smartphone'),
                _bool('uso_vibracoes',            'Exposição a vibração (ferramentas)'),
                _bool('dor_cronica',              'Dor crônica'),
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
            _block('Ottawa — Palpação (complemento)', [
                _sel ('localizacao_dor', 'Localização principal da dor', [
                    ('', '— Não especificada'),
                    ('tornozelo','Tornozelo'), ('retropé','Retropé/calcâneo'),
                    ('mediopé','Mediopé'), ('antepé','Antepé'),
                ]),
                _bool('dor_maleolo_posterior_lateral','Dor borda posterior maléolo LATERAL (Ottawa)'),
                _bool('dor_maleolo_posterior_medial', 'Dor borda posterior maléolo MEDIAL (Ottawa)'),
                _bool('dor_base_5o_meta',  'Dor na base do 5º metatarso (Ottawa)'),
                _bool('dor_navicular',     'Dor no navicular (Ottawa)'),
                _bool('incapaz_apoio_exame','Incapaz de apoiar peso ao exame'),
                _bool('deformidade_visivel','Deformidade visível', flag='yellow'),
            ]),
            _block('Entorse / Ligamentos (complemento)', [
                _bool('dor_ligamentos_laterais','Dor nos ligamentos laterais (talofibular)'),
                _bool('ja_entorces_previos','Entorses recorrentes no mesmo tornozelo'),
            ]),
            _block('Aquiles / Fascite / Neuroma (complemento)', [
                _bool('dor_insercao_calcahar','Dor na inserção do Aquiles no calcâneo'),
                _bool('dor_2_6cm_insercao', 'Dor 2–6 cm acima da inserção (tendinopatia do corpo)'),
                _bool('rigidez_manha_aquiles','Rigidez matinal do Aquiles'),
                _bool('dor_fascia_proximal', 'Dor na fáscia plantar proximal (calcâneo medial)'),
                _bool('dor_melhora_caminhar','Dor melhora ao caminhar (fascite/tendinopatia)'),
                _bool('irradiacao_para_dedos','Irradiação para os dedos (neuroma)'),
                _bool('hipoestesia_dedos_adjacentes','Hipoestesia entre dedos adjacentes (neuroma)'),
                _bool('piora_calcado_estreito','Piora com calçado estreito (neuroma)'),
                _bool('alivio_tirar_calcado','Alívio ao tirar o calçado'),
            ]),
            _block('Mecânico / Contexto (complemento)', [
                _bool('dor_dorsiflexao_passiva','Dor à dorsiflexão passiva'),
                _bool('pe_plano_valgismo',  'Pé plano / valgismo'),
                _bool('piora_corrida_salto','Piora com corrida/salto'),
                _bool('uso_calcado_inadequado','Uso de calçado inadequado'),
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

    # ── GASTRO / DOR ABDOMINAL ───────────────────────────────────────────────
    'gastro': {
        'label': 'Dor Abdominal / Queixas GI', 'sistema': 'Gastrointestinal',
        'blocks': [
            _block('Localização + Caráter + Duração', [
                _sel('localizacao', 'Localização da dor', [
                    ('epigastrico',           'Epigástrio (boca do estômago)'),
                    ('fsd',                   'FSD / hipocôndrio direito'),
                    ('fid',                   'FID (baixo abdôme à direita)'),
                    ('fie',                   'FIE (baixo abdôme à esquerda)'),
                    ('hipogastrico_pelvico',  'Hipogástrio / pélvico'),
                    ('periumbilical',         'Periumbilical'),
                    ('difuso',                'Difuso / todo o abdôme'),
                    ('lombar_renal',          'Lombar → virilha (cólica renal)'),
                ]),
                _sel('carater', 'Caráter da dor', [
                    ('colica',      'Cólica / espasmo (vem e vai)'),
                    ('queimacao',   'Queimação / azia / ardor'),
                    ('constante',   'Constante / pressão'),
                    ('distensao',   'Distensão / plenitude pós-refeição'),
                    ('aguda_subita','⚠ Facada / início súbito intenso'),
                    ('difusa_leve', 'Difusa / leve / mal-definida'),
                ]),
                _sel('intensidade', 'Intensidade', [
                    ('leve',         'Leve — trabalha normalmente'),
                    ('moderada',     'Moderada — atrapalha atividades'),
                    ('intensa',      'Intensa — vai ao PS'),
                    ('catastrofica', '⚠ Catastrófica — pior dor da vida'),
                ]),
                _sel('duracao', 'Duração dos sintomas', [
                    ('horas',        'Horas (< 24h)'),
                    ('dias',         'Dias (1–7 dias)'),
                    ('semanas',      'Semanas (1–4 semanas)'),
                    ('meses_1_3',    'Meses (1–3 meses)'),
                    ('meses_mais_3', 'Mais de 3 meses'),
                ]),
                _sel('episodios', 'Padrão temporal', [
                    ('primeira_vez', 'Primeira vez'),
                    ('recorrente',   'Recorrente (vem e passa)'),
                    ('cronico',      'Crônico — tenho há meses/anos'),
                ]),
            ]),
            _block('Hábito Intestinal', [
                _sel('habito_intestinal', 'Hábito intestinal atual', [
                    ('normal',              'Normal para mim'),
                    ('constipacao',         'Constipação (fezes duras / esforço)'),
                    ('diarreia',            'Diarreia (≥ 3×/dia / líquida)'),
                    ('alternancia',         'Alternância constipação / diarreia'),
                    ('sem_evacuacao_gases', '⚠ Sem evacuar E sem gases > 24h'),
                ]),
                _bool('hematoquezia',   '⚠ Sangue vivo nas fezes (hematoquezia)', flag='red'),
                _bool('melena',         '⚠ Fezes pretas / alcatroadas (melena)',   flag='red'),
                _bool('muco_fezes',     'Muco nas fezes',    negative=True),
                _bool('esteatorreia',   'Fezes gordurosas / oleosas (esteatorreia)',
                      negative=True, help='Fezes brilhantes, oleosas, difíceis de limpar → má-absorção de gordura (celíaca, IBD, insuficiência pancreática).'),
                _bool('alivio_evacuacao','Dor alivia após evacuar', negative=True),
            ]),
            _block('Sintomas Associados', [
                _sel('febre_grau', 'Febre', [
                    ('sem',      'Sem febre'),
                    ('baixa',    'Febrícula (37,5–38°C)'),
                    ('moderada', 'Febre moderada (38–39°C)'),
                    ('alta',     'Febre alta (> 39°C / calafrios)'),
                ]),
                _bool('nausea',     'Náuseas',   negative=True),
                _bool('vomito',     'Vômito',    negative=True),
                _bool('hematemese', '⚠ Hematêmese (vômito com sangue)', flag='red'),
                _bool('perda_peso', '⚠ Perda de peso involuntária (> 5% em 6 meses)', flag='yellow'),
                _bool('anorexia',   'Anorexia / sem apetite', negative=True),
                _bool('ictericia',  '⚠ Icterícia (pele / olhos amarelos)', flag='yellow',
                      help='Icterícia + dor em FSD = colecistite / colangite / litíase de vias biliares. Icterícia + emagrecimento = neoplasia até prova em contrário.'),
            ]),
            _block('Relação com Alimentação', [
                _sel('relacao_alimentar', 'Relação com alimentação', [
                    ('sem_relacao',       'Sem relação clara'),
                    ('piora_gorduroso',   'Piora com gordurosos / frituras'),
                    ('piora_gluten',      'Piora com glúten (pão, macarrão, biscoito)'),
                    ('piora_lactose',     'Piora com laticínios'),
                    ('piora_pos_refeicao','Piora após qualquer refeição'),
                    ('piora_jejum',       'Piora em jejum / alivia após comer'),
                ]),
                _bool('melhora_sem_gluten',  'Melhora ao retirar glúten',    negative=True),
                _bool('melhora_sem_lactose', 'Melhora ao retirar laticínios', negative=True),
            ]),
            _block('Exame Físico Abdominal', [
                _bool('murphy_positivo',   '⚠ Murphy positivo (FSD)', flag='yellow',
                      help='Parada inspiratória ao palpar o hipocôndrio direito durante inspiração profunda → sinal de colecistite aguda (S 65%, E 87%).'),
                _bool('fid_dolorosa',      'FID dolorosa à palpação', flag='yellow'),
                _bool('mcburney_positivo', '⚠ McBurney positivo (apendicite?)', flag='red',
                      help='Dor no 1/3 externo da linha entre umbigo e EIAD direita → sinal de apendicite (S 50–94%, E 75–86%). TC tem S 98–99%.'),
                _bool('fie_dolorosa',      'FIE dolorosa à palpação', flag='yellow'),
                _bool('blumberg_positivo', '⚠ Blumberg positivo (peritonismo)', flag='red',
                      help='Dor que AUMENTA ao soltar bruscamente após compressão profunda → irritação peritoneal. Peritonite até prova em contrário.'),
                _bool('rigidez',           '⚠ Rigidez involuntária / abdôme em tábua', flag='red'),
                _bool('rha_ausentes',      '⚠ Ruídos hidroaéreos ausentes', flag='yellow',
                      help='Silêncio abdominal + obstipação total → obstrução intestinal ou peritonite. Na isquemia mesentérica: abdôme flácido com dor desproporcional.'),
            ]),
            _block('H. pylori + Histórico', [
                _sel('hp_status', 'Status H. pylori', [
                    ('desconhecido', 'Desconhecido / nunca testou'),
                    ('positivo',     'Positivo — nunca tratou'),
                    ('eradicado',    'Eradicado — teste de cura confirmado negativo'),
                    ('sem_cura',     'Tratado — sem teste de cura'),
                ]),
                _bool('uso_aine',      'Uso de AINE / AAS / anti-inflamatório', flag='yellow'),
                _bool('atb_recente',   'Antibiótico nos últimos 4 meses', flag='yellow',
                      help='ATB recente + diarreia → alerta C. difficile: solicitar pesquisa de toxina A/B; não usar loperamida.'),
                _bool('etilismo',      'Etilismo / uso regular de álcool'),
            ]),
            _block('Contexto / Comorbidades', [
                _bool('fa_arritmia',    'Fibrilação atrial / arritmia', flag='yellow'),
                _bool('vasculopata',    'Vasculopatia / aterosclerose / IAM prévio', flag='yellow'),
                _bool('imunossuprimido','Imunossuprimido', flag='yellow'),
                _bool('diverticulose',  'Diverticulose conhecida'),
                _bool('viagem_endemica','Viagem a área endêmica (Nordeste / Norte / exterior)'),
                _bool('agua_nao_tratada','Consumo de água não tratada / poço / rio'),
                _bool('contato_animal', 'Contato com animais de fazenda / fezes'),
            ]),
            _block('Padrão Crônico / Funcional', [
                _bool('distensao_pos_refeicao','Distensão abdominal após refeição', negative=True),
                _bool('artrite_extra',         'Dor / inchaço articular associado', negative=True),
                _bool('lesao_pele_extra',      'Lesões de pele (eritema nodoso / manchas)', negative=True),
                _bool('uveite_extra',          'Olho vermelho / uveíte', negative=True),
                _bool('aftas_extra',           'Aftas recorrentes na boca', negative=True),
            ]),
            _block('Saúde da Mulher', [
                _bool('sexo_feminino',      'Paciente do sexo feminino (ativa os campos abaixo)'),
                _bool('atraso_menstrual',   '⚠ Atraso menstrual', flag='yellow',
                      depends_on='sexo_feminino'),
                _bool('dor_pelvica',        'Dor pélvica / baixo ventre', negative=True,
                      depends_on='sexo_feminino'),
                _bool('dor_pelvica_aguda',  '⚠ Dor pélvica intensa / nova (diferente do habitual)', flag='red',
                      depends_on='dor_pelvica'),
                _bool('dismenorreia_habitual','Dor habitual de menstruação (dismenorreia conhecida)',
                      depends_on='dor_pelvica'),
                _bool('corrimento_purulento','⚠ Corrimento purulento / amarelo-esverdeado', flag='yellow',
                      depends_on='sexo_feminino'),
            ]),
        ],
        'engine': 'modules.raciocinio.gastro.engine_gastro',
        'engine_fn': 'interpretar_queixa_gastro',
    },

    # ── TRANSTORNOS DO SONO ──────────────────────────────────────────────────
    'sono': {
        'label': 'Transtornos do Sono', 'sistema': 'Sono / Neurologia',
        'blocks': [
            _block('ISI — Índice de Gravidade da Insônia', [
                _num('isi_score', 'ISI total (0–28)', min_val=0, max_val=28, default=0,
                     help='Insomnia Severity Index: 0–7 sem clínica | 8–14 leve | 15–21 moderada | 22–28 grave. Aplicar 7 perguntas sobre dificuldade de iniciar, manter e acordar cedo, satisfação, impacto diurno.'),
                _num('duracao_semanas', 'Duração da insônia (semanas)', min_val=0, max_val=520, default=0),
                _num('noites_por_semana', 'Noites afetadas / semana (0–7)', min_val=0, max_val=7, default=0),
                _num('horas_cama',  'Horas na cama por noite', min_val=0, max_val=16, step=1, default=8),
                _num('horas_sono',  'Horas de sono efetivo', min_val=0, max_val=16, step=1, default=6),
            ]),
            _block('AOS — STOP-BANG', [
                _num('stopbang_score', 'STOP-BANG score total (0–8)', min_val=0, max_val=8, default=0,
                     help='S=Ronco alto | T=Cansado diurno | O=Apneia observada | P=Pressão alta | B=IMC>35 | A=Idade>50 | N=Pescoço>40(F)/43(M) cm | G=Masculino. ≥3 = alto risco AOS.'),
                _num('epworth_score', 'Escala de Epworth (0–24)', min_val=0, max_val=24, default=0,
                     help='Sonolência em 8 situações (0–3 cada). > 10 = sonolência diurna excessiva. > 15 = pode adormecer dirigindo → não dirigir.'),
                _bool('masculino_stopbang', 'Masculino (item G do STOP-BANG)'),
                _num('imc', 'IMC (kg/m²)', min_val=10, max_val=80, step=1, default=None),
                _num('circunferencia_cervical_cm', 'Circunferência cervical (cm)', min_val=25, max_val=70, default=None),
            ]),
            _block('SPI — Síndrome das Pernas Inquietas', [
                _num('spi_criterios', 'Critérios de SPI presentes (0–4)', min_val=0, max_val=4, default=0,
                     help='Critérios IRLSSG: 1) Urgência de mover as pernas; 2) Piora em repouso; 3) Alívio ao mover; 4) Piora à noite / noturno. Todos os 4 devem estar presentes.'),
                _num('ferritina_valor', 'Ferritina (ng/mL)', min_val=0, max_val=1000, default=None,
                     help='Ferritina < 50 ng/mL → repor ferro (meta > 75 ng/mL). Reposição de ferro resolve SPI em 50–60% quando ferritina baixa.'),
            ]),
            _block('Narcolepsia (rastrear)', [
                _bool('cataplexia', '⚠ Cataplexia (fraqueza súbita por emoção)', flag='yellow',
                      help='Perda súbita e breve do tônus muscular desencadeada por emoção intensa (riso, surpresa, raiva). Patognomônica de narcolepsia tipo 1.'),
                _bool('alucinacao_adormecer',    'Alucinação hipnagógica (ao adormecer)'),
                _bool('paralisia_sono',          'Paralisia do sono (acorda sem conseguir mover)'),
                _bool('sono_diurno_irresistivel','Sono diurno irresistível / ataques de sono'),
            ]),
            _block('TCR-REM / Parassonias', [
                _bool('tcr_rem_age_sonhos', '⚠ Age os sonhos fisicamente (soco / grita / cai da cama)', flag='yellow',
                      help='Ausência de atonia muscular no REM → Transtorno Comportamental do REM. Em > 50 anos: 80–90% desenvolve Parkinson / DLB em 10–15 anos.'),
                _bool('sonambulismo',    'Sonambulismo (NREM)',  negative=True),
                _bool('terror_noturno', 'Terror noturno (NREM)', negative=True),
                _bool('pesadelos_freq', 'Pesadelos frequentes',  negative=True),
                _bool('pesadelos_trauma','Pesadelos relacionados a trauma (TEPT?)', depends_on='pesadelos_freq'),
            ]),
            _block('Bruxismo do Sono', [
                _bool('ranger_dentes',          'Range os dentes durante o sono',         negative=True),
                _bool('dor_mandibula_manha',     'Dor na mandíbula ao acordar',            negative=True),
                _bool('cefaleia_temporal_manha', 'Cefaleia temporal matinal',              negative=True),
                _bool('desgaste_dentario',       'Desgaste dentário (confirmado)',          negative=True),
                _bool('dor_atm',                 'Dor na ATM (articulação temporomandibular)', negative=True),
                _bool('masseter_hipertrofia',    'Hipertrofia do masseter',                negative=True),
                _bool('isrs_em_uso',             'ISRS em uso (pode causar bruxismo)', flag='yellow'),
            ]),
            _block('Síndrome da Fase Atrasada (SFAS)', [
                _bool('dorme_bem_horario_proprio','Dorme bem no horário que prefere (ex: 2–10h)'),
                _bool('dificuldade_iniciar',      'Dificuldade de adormecer no horário "normal"'),
            ]),
            _block('Fatores Comportamentais', [
                _bool('tela_na_cama',       'Usa tela (celular/tablet/TV) na cama antes de dormir', negative=True),
                _bool('alcool_para_dormir', 'Usa álcool para dormir',                flag='yellow', negative=True),
                _bool('cama_escritorio',    'Usa a cama para trabalho / escritório',               negative=True),
                _bool('exercicio_noturno',  'Exercício físico após 18h',                           negative=True),
                _bool('horario_cama_fixo',  'Horário fixo de acordar (inclusive fim de semana)',   negative=True),
                _bool('cochilo_diurno',     'Cochilo diurno',                                      negative=True),
                _num('cochilo_duracao_min', 'Duração do cochilo (min)', min_val=0, max_val=240, default=0,
                     depends_on='cochilo_diurno'),
            ]),
            _block('Contexto Clínico', [
                _bool('depressao_ansiedade', 'Depressão / ansiedade (diagnosticada ou suspeita)', flag='yellow'),
                _num('phq2_score', 'PHQ-2 score (0–6)', min_val=0, max_val=6, default=0,
                     help='PHQ-2: "Nas últimas 2 semanas, com que frequência sentiu: (1) Humor deprimido / desesperança; (2) Pouco interesse / prazer?" 0=nunca a 3=quase todos os dias. ≥3 → triagem positiva.'),
                _bool('turno_irregular',    'Trabalho em turno noturno ou irregular', flag='yellow'),
                _bool('dor_cronica_noturna','Dor crônica que piora à noite',          flag='yellow'),
                _num('tsh_valor', 'TSH (mUI/L) — se coletado', min_val=0, max_val=50, step=1, default=None,
                     help='TSH > 4,5 mUI/L → hipotireoidismo; tratar a causa antes de prescrever hipnótico.'),
                _bool('benzo_em_uso', '⚠ Benzodiazepínico / zolpidem em uso crônico', flag='yellow'),
                _sel('benzo_qual', 'Benzodiazepínico em uso', [
                    ('',             '— Não se aplica'),
                    ('clonazepam',   'Clonazepam'),
                    ('alprazolam',   'Alprazolam'),
                    ('diazepam',     'Diazepam'),
                    ('lorazepam',    'Lorazepam'),
                    ('nitrazepam',   'Nitrazepam'),
                    ('zolpidem',     'Zolpidem'),
                    ('outro_benzo',  'Outro'),
                ], depends_on='benzo_em_uso'),
                _num('benzo_dose', 'Dose diária (mg)', min_val=0, max_val=100, default=None,
                     depends_on='benzo_em_uso'),
                _num('benzo_semanas', 'Em uso há quantas semanas?', min_val=0, max_val=520, default=0,
                     depends_on='benzo_em_uso'),
            ]),
        ],
        'engine': 'modules.raciocinio.sono.engine_sono',
        'engine_fn': 'interpretar_sono',
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
