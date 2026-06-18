"""
SymptoPy — Interface Web
Cyber-Minimalista | SOAP Completo em Tempo Real | Streamlit

Rodar: streamlit run interface.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from ui.theme import CSS
from ui.schemas import MODULE_SCHEMAS, KEYWORD_TO_SCHEMA
from ui.engine_bridge import run_engine
from ui.prontuario_builder import build_full_soap
from modules.transversal.interacoes import verificar_interacoes
from modules.transversal.perfil_paciente import PERFIL_VAZIO

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title='SymptoPy', page_icon='⚕',
                   layout='wide', initial_sidebar_state='collapsed')
st.markdown(CSS, unsafe_allow_html=True)
st.markdown("""
<style>
header, footer, #MainMenu,
[data-testid="stHeader"], [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"] { display: none !important; }
.block-container { padding-top: 0.5rem !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────────────────────────────────────
COMORBIDADES_COMUNS = [
    'HAS', 'DM2', 'DRC', 'DPOC', 'ICC', 'FA', 'Cirrose',
    'Asma', 'Hipotireoidismo', 'Dislipidemia', 'Obesidade',
    'AVC prévio', 'IAM prévio', 'Neoplasia ativa', 'Demência',
    'Depressão/Ansiedade', 'Tabagismo', 'Etilismo',
]

SISTEMAS_EF = [
    ('neuro',       'Neurológico'),
    ('pneumo',      'Respiratório'),
    ('cardio',      'Cardiovascular'),
    ('abdome',      'Abdome'),
    ('mmii',        'MMII'),
    ('pele',        'Pele/Mucosas'),
    ('orofaringe',  'Orofaringe'),
    ('eliminacoes', 'Eliminações'),
]


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
def _init_state():
    defaults = {
        'patient': {
            'nome': '', 'idade': 30, 'sexo': 'masculino',
            'queixa_principal': '', 'queixa_key': None, 'queixa_display': '',
            'profissao': '', 'procedencia': '', 'rg_hc': '',
            'contexto_social': '', 'chv': '',
            'comorbidades_sel': [], 'comorbidades_free': '',
            'medicacoes': '', 'alergias': '', 'cirurgias_previas': '',
            'internamentos': '', 'institucionalizado': False, 'acamado': False,
        },
        'consult': {
            'hma': '', 'pa': '', 'fc': '', 'fr': '',
            'sato2': '', 'temperatura': '', 'glicemia': '',
            'exames_complementares': '',
        },
        'exam': {'estado_geral': ''},
        'form_data': {},
        'resultado': None,
        'soap_txt': '',
        'show_modal': False,
        'perfil_farmaco': {
            'egfr': None,
            'anticoagulado': False,
            'tipo_anticoagulante': None,
            'isrs_em_uso': False,
            'imao_em_uso': False,
            'antipsicótico_em_uso': False,
            'qt_longo_conhecido': False,
            'hepatopatia': False,
        },
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()


# ─────────────────────────────────────────────────────────────────────────────
# DISPATCHER
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def _load_dispatcher_keys() -> list[str]:
    try:
        from prontuario.dispatcher import MODULOS_QUEIXA
        return sorted(MODULOS_QUEIXA.keys())
    except Exception:
        return list(KEYWORD_TO_SCHEMA.keys())

ALL_QUEIXAS = _load_dispatcher_keys()


@st.cache_data
def _build_queixa_options():
    """
    Lista limpa de queixas principais (uma por módulo), agrupada por sistema.
    Retorna (display_labels, {display: schema_key}).
    Variações ('tosse seca', 'tosse produtiva') NÃO aparecem aqui — todas
    resolvem para o mesmo módulo via _resolve_schema na digitação livre.
    """
    by_sys = {}
    for skey, sch in MODULE_SCHEMAS.items():
        sis = sch.get('sistema', 'Outros')
        by_sys.setdefault(sis, []).append((sch.get('label', skey), skey))
    labels, mapping = [], {}
    for sis in sorted(by_sys):
        for label, skey in sorted(by_sys[sis]):
            disp = f'{sis} · {label}'
            labels.append(disp)
            mapping[disp] = skey
    return labels, mapping


QUEIXA_LABELS, QUEIXA_MAP = _build_queixa_options()


def _resolve_schema(queixa_raw: str):
    q = queixa_raw.strip().lower()
    if q in KEYWORD_TO_SCHEMA:
        return KEYWORD_TO_SCHEMA[q]
    try:
        from prontuario.dispatcher import MODULOS_QUEIXA
        entry = MODULOS_QUEIXA.get(q)
        if entry:
            for cand in (entry.get('modulo', ''), entry.get('tipo', '')):
                if cand in MODULE_SCHEMAS:
                    return cand
    except Exception:
        pass
    for kw, sk in KEYWORD_TO_SCHEMA.items():
        if kw in q or q in kw:
            return sk
    return None


# ─────────────────────────────────────────────────────────────────────────────
# VITAIS → form_data (para engines que precisam de pas/fc/temp numéricos)
# ─────────────────────────────────────────────────────────────────────────────
def _merge_vitals(form: dict, consult: dict):
    """Injeta vitais parseados no form_data como default (campo do bloco vence)."""
    pa = consult.get('pa', '')
    if pa and '/' in pa:
        try:
            form.setdefault('pas', int(pa.split('/')[0].strip()))
            form.setdefault('pad', int(pa.split('/')[1].strip()))
        except (ValueError, IndexError):
            pass
    for src, dst in [('fc', 'fc'), ('fr', 'fr')]:
        v = consult.get(src, '')
        if v:
            try:
                form.setdefault(dst, int(float(v)))
            except ValueError:
                pass
    temp = consult.get('temperatura', '')
    if temp:
        try:
            t = float(temp)
            form.setdefault('temp_celsius', t)
            form.setdefault('temperatura', t)
        except ValueError:
            pass
    sat = consult.get('sato2', '')
    if sat:
        try:
            s = float(sat)
            form.setdefault('spo2', s)
            form.setdefault('sato2', s)
        except ValueError:
            pass


# ─────────────────────────────────────────────────────────────────────────────
# RENDER FIELD (3 estados)
# ─────────────────────────────────────────────────────────────────────────────
def render_field(field: dict, form: dict) -> bool:
    """Renderiza um campo. Retorna True se o widget foi exibido (dep satisfeita)."""
    key, ftype, label = field['key'], field['type'], field['label']
    flag, dep_on, default = field.get('flag'), field.get('depends_on'), field.get('default')
    help_txt = field.get('help')

    if dep_on and not form.get(dep_on):
        # Campo oculto (dependência não satisfeita): não documentar como negativa.
        if ftype == 'bool':
            form[key] = None
        else:
            form.setdefault(key, default)
        return False

    disp = label
    if flag == 'red':    disp = f'🔴 {label}'
    elif flag == 'yellow': disp = f'🟡 {label}'
    wkey = f'field_{key}'

    if ftype == 'bool':
        cur = form.get(key)
        # Marcado = achado positivo (True); desmarcado = negativa pertinente (False).
        # O app lembra o que perguntar, então o não-marcado conta como investigado e negado.
        form[key] = st.checkbox(disp, value=(cur is True), key=wkey, help=help_txt)
        return True
    elif ftype == 'select':
        opts = field.get('options', [])
        labels, values = [o[1] for o in opts], [o[0] for o in opts]
        cur = form.get(key, default or values[0])
        idx = values.index(cur) if cur in values else 0
        sel = st.selectbox(disp, labels, index=idx, key=wkey, help=help_txt)
        form[key] = values[labels.index(sel)]
    elif ftype == 'number':
        min_v, max_v, step = field.get('min', 0), field.get('max', 999), field.get('step', 1)
        cur = form.get(key, default)
        if cur is None: cur = min_v
        is_float = isinstance(step, float) or isinstance(min_v, float)
        if is_float:
            form[key] = st.number_input(disp, float(min_v), float(max_v),
                                        float(cur), float(step), key=wkey, help=help_txt)
        else:
            form[key] = st.number_input(disp, int(min_v), int(max_v),
                                        int(cur), int(step), key=wkey, help=help_txt)
    elif ftype == 'text':
        form[key] = st.text_input(disp, value=form.get(key, ''), key=wkey, help=help_txt)
    return True


def render_block(block: dict, form: dict, schema_key: str = ''):
    flag = block.get('flag')
    cls = 'block-header red' if flag == 'red' else 'block-header'
    st.markdown(f'<div class="{cls}">{block["title"]}</div>', unsafe_allow_html=True)
    for field in block['fields']:
        render_field(field, form)


# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="symp-header">
    <span class="symp-logo">⚕ SYMPTOOPY</span>
    <span class="symp-tagline">SISTEMA DE APOIO CLÍNICO · ADULTO · PA / APS</span>
</div>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# SEÇÃO 1 — IDENTIFICAÇÃO DO PACIENTE
# ═════════════════════════════════════════════════════════════════════════════
P = st.session_state.patient

c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 3, 1])
with c1:
    P['nome'] = st.text_input('Paciente', value=P['nome'],
                              placeholder='Nome (opcional)', label_visibility='collapsed')
with c2:
    P['idade'] = int(st.number_input('Idade', 0, 120, P['idade'], label_visibility='collapsed'))
with c3:
    s_opts, s_lbl = ['masculino', 'feminino'], ['♂ M', '♀ F']
    sel = st.selectbox('Sexo', s_lbl, index=s_opts.index(P['sexo']), label_visibility='collapsed')
    P['sexo'] = s_opts[s_lbl.index(sel)]
with c4:
    qd = ['— Selecionar queixa —'] + QUEIXA_LABELS
    cur_disp = P.get('queixa_display', '')
    idx = qd.index(cur_disp) if cur_disp in qd else 0
    qsel = st.selectbox('Queixa', qd, index=idx, label_visibility='collapsed',
                        placeholder='Buscar queixa...')
    if qsel != '— Selecionar queixa —':
        sk = QUEIXA_MAP.get(qsel)
        P['queixa_display'] = qsel
        P['queixa_principal'] = MODULE_SCHEMAS.get(sk, {}).get('label', qsel)
        if sk != P.get('queixa_key'):
            P['queixa_key'] = sk
            st.session_state.form_data = {}
            st.session_state.resultado = None
    else:
        P['queixa_principal'], P['queixa_key'], P['queixa_display'] = '', None, ''
with c5:
    if st.button('🗑 Limpar', use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# Dados completos do paciente (expander)
with st.expander('▤  DADOS COMPLETOS DO PACIENTE  (ocupação · procedência · comorbidades · medicações)'):
    d1, d2, d3 = st.columns(3)
    with d1:
        P['profissao']   = st.text_input('Ocupação', value=P['profissao'])
        P['procedencia'] = st.text_input('Procedência', value=P['procedencia'])
        P['rg_hc']       = st.text_input('RG / HC', value=P['rg_hc'])
    with d2:
        P['institucionalizado'] = st.checkbox(
            '🟡 Institucionalizado (ILPI/asilo) — risco de colonização', value=P['institucionalizado'])
        P['acamado']            = st.checkbox('Acamado / restrito ao leito', value=P['acamado'])
        P['contexto_social']    = st.text_input('Contexto social (livre)', value=P['contexto_social'])
        P['chv']                = st.text_input('Hábitos de vida (CHV)', value=P['chv'])
    with d3:
        P['alergias']          = st.text_input('Alergias', value=P['alergias'], placeholder='nega')
        P['cirurgias_previas'] = st.text_input('Cirurgias prévias', value=P['cirurgias_previas'], placeholder='nega')
        P['internamentos']     = st.text_input('Internamentos', value=P['internamentos'], placeholder='nega')

    st.markdown('<div class="block-header">Comorbidades</div>', unsafe_allow_html=True)
    P['comorbidades_sel'] = st.multiselect('Comorbidades comuns',
                                           COMORBIDADES_COMUNS, default=P['comorbidades_sel'],
                                           label_visibility='collapsed')
    P['comorbidades_free'] = st.text_input('Outras comorbidades (livre)', value=P['comorbidades_free'])
    P['medicacoes'] = st.text_area('Medicações de uso contínuo', value=P['medicacoes'],
                                   placeholder='losartana 50mg 1-0-1, metformina 850mg 1-0-1', height=70)

PF = st.session_state.perfil_farmaco
with st.expander('💊  PERFIL FARMACOLÓGICO  (comorbidades que afetam prescrição)'):
    pf1, pf2 = st.columns(2)
    with pf1:
        egfr_raw = st.number_input(
            'eGFR (mL/min/1.73m²) — 0 = não informado',
            min_value=0.0, max_value=200.0,
            value=float(PF['egfr']) if PF['egfr'] is not None else 0.0,
            step=1.0, key='pf_egfr')
        PF['egfr'] = egfr_raw if egfr_raw > 0 else None
        PF['hepatopatia'] = st.checkbox(
            'Hepatopatia (cirrose / hepatite crônica)', value=PF['hepatopatia'], key='pf_hepato')
        PF['qt_longo_conhecido'] = st.checkbox(
            'QT longo conhecido', value=PF['qt_longo_conhecido'], key='pf_qt')
    with pf2:
        PF['anticoagulado'] = st.checkbox(
            'Anticoagulado', value=PF['anticoagulado'], key='pf_anticoag')
        if PF['anticoagulado']:
            tipo_opts = ['warfarina', 'doac']
            tipo_lbl  = ['Warfarina / acenocumarol', 'DOAC (apixabana, rivaroxabana...)']
            cur_tipo  = PF.get('tipo_anticoagulante') or 'warfarina'
            idx_tipo  = tipo_opts.index(cur_tipo) if cur_tipo in tipo_opts else 0
            sel_tipo  = st.selectbox('Tipo', tipo_lbl, index=idx_tipo, key='pf_tipo_anticoag')
            PF['tipo_anticoagulante'] = tipo_opts[tipo_lbl.index(sel_tipo)]
        else:
            PF['tipo_anticoagulante'] = None
        PF['isrs_em_uso'] = st.checkbox(
            'ISRS em uso', value=PF['isrs_em_uso'], key='pf_isrs')
        PF['imao_em_uso'] = st.checkbox(
            'IMAO em uso', value=PF['imao_em_uso'], key='pf_imao')
        PF['antipsicótico_em_uso'] = st.checkbox(
            'Antipsicótico em uso', value=PF['antipsicótico_em_uso'], key='pf_antipsic')

st.markdown('<hr>', unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# LAYOUT PRINCIPAL — Dois painéis
# ═════════════════════════════════════════════════════════════════════════════
schema_key = P.get('queixa_key')
schema     = MODULE_SCHEMAS.get(schema_key) if schema_key else None
form       = st.session_state.form_data
C          = st.session_state.consult
EX         = st.session_state.exam

col_left, col_right = st.columns([1, 1], gap='medium')

# ── PAINEL ESQUERDO ──────────────────────────────────────────────────────────
with col_left:
    st.markdown('<div class="panel-title">◈ COLETA CLÍNICA</div>', unsafe_allow_html=True)

    if not schema:
        qp = P.get('queixa_principal', '')
        if qp:
            st.markdown(f'<div style="color:#F0B429;font-size:0.82rem;padding:1rem 0;">'
                        f'⚡ Módulo <b>"{qp}"</b> ainda não tem formulário visual.</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#8B949E;font-size:0.85rem;padding:2rem 0;">'
                        'Selecione uma queixa acima para iniciar a coleta.</div>',
                        unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="font-size:0.7rem;color:#8B949E;">{schema.get("sistema","")}</div>'
                    f'<div style="font-size:0.95rem;color:#E6EDF3;font-weight:bold;'
                    f'margin-bottom:8px;">{schema.get("label", schema_key)}</div>',
                    unsafe_allow_html=True)

        # HMA
        st.markdown('<div class="block-header">HMA</div>', unsafe_allow_html=True)
        C['hma'] = st.text_area('HMA', value=C['hma'], height=70, label_visibility='collapsed',
                                placeholder='História da moléstia atual...')

        # Sinais Vitais
        st.markdown('<div class="block-header">Sinais Vitais</div>', unsafe_allow_html=True)
        v1, v2, v3 = st.columns(3)
        with v1:
            C['pa'] = st.text_input('PA (mmHg)', value=C['pa'], placeholder='120/80')
            C['sato2'] = st.text_input('SatO₂ (%)', value=C['sato2'], placeholder='98')
        with v2:
            C['fc'] = st.text_input('FC (bpm)', value=C['fc'], placeholder='75')
            C['temperatura'] = st.text_input('Temp (°C)', value=C['temperatura'], placeholder='36.5')
        with v3:
            C['fr'] = st.text_input('FR (ipm)', value=C['fr'], placeholder='16')
            C['glicemia'] = st.text_input('HGT (mg/dL)', value=C['glicemia'], placeholder='90')
        n1, n2 = st.columns(2)
        with n1:
            C['o2_suplementar'] = st.checkbox('O₂ suplementar', value=C.get('o2_suplementar', False))
        with n2:
            C['consciencia_alterada'] = st.checkbox('Consciência alterada (ACVPU < A)',
                                                    value=C.get('consciencia_alterada', False))

        # Exame Físico Geral
        with st.expander('🩺  EXAME FÍSICO GERAL  (desmarque o que estiver alterado)'):
            EX['estado_geral'] = st.text_input(
                'Estado geral', value=EX.get('estado_geral', ''),
                placeholder='BEG, corado, hidratado, orientado, afebril')
            for skey, slabel in SISTEMAS_EF:
                normal = st.checkbox(f'{slabel} normal', value=EX.get(f'{skey}_normal', True),
                                     key=f'ef_{skey}')
                EX[f'{skey}_normal'] = normal
                if not normal:
                    EX[f'{skey}_alt'] = st.text_input(
                        f'↳ {slabel} — descreva', value=EX.get(f'{skey}_alt', ''),
                        key=f'ef_alt_{skey}')

        # Blocos da queixa específica
        st.markdown('<div class="block-header" style="border-left-color:#00F0FF;color:#00F0FF;">'
                    'COLETA DIRIGIDA</div>', unsafe_allow_html=True)
        for block in schema.get('blocks', []):
            render_block(block, form, schema_key)

        # Exames complementares
        st.markdown('<div class="block-header">Exames Complementares</div>', unsafe_allow_html=True)
        C['exames_complementares'] = st.text_area(
            'Exames', value=C['exames_complementares'], height=60,
            label_visibility='collapsed', placeholder='Resultados de exames disponíveis...')

        st.markdown('<hr>', unsafe_allow_html=True)
        st.caption('▲ O SOAP à direita atualiza ao vivo conforme você preenche — '
                   'sem botão.')


# ── PAINEL DIREITO — SOAP COMPLETO ───────────────────────────────────────────
with col_right:
    st.markdown('<div class="panel-title">◈ SOAP COMPLETO — TEMPO REAL</div>', unsafe_allow_html=True)

    if not schema:
        st.markdown('<div style="color:#8B949E;font-size:0.8rem;padding:2rem 0;">'
                    'O prontuário completo aparecerá aqui após a análise.</div>',
                    unsafe_allow_html=True)
    else:
        # NEWS2 ao vivo — calculado direto dos vitais do cabeçalho
        from modules.transversal.news2 import calcular_news2, texto_news2
        _n2 = calcular_news2(C)
        if _n2 and _n2['banda'] in ('medio', 'alto', 'baixo_medio'):
            _cor = {'alto': '#FF6B6B', 'medio': '#F0B429', 'baixo_medio': '#F0B429'}[_n2['banda']]
            st.markdown(
                f'<div style="border:1px solid {_cor};border-left:3px solid {_cor};'
                f'border-radius:4px;padding:0.5rem 0.8rem;margin-bottom:8px;'
                f'font-size:0.8rem;color:{_cor};">'
                f'{texto_news2(_n2)}</div>',
                unsafe_allow_html=True)

        # SOAP REATIVO — recalcula a cada mudança (sem botão).
        # Vitais entram numa cópia transitória (engine_form), então mudanças no
        # cabeçalho propagam sempre e o form_data persistente fica só com a coleta.
        engine_form = dict(form)
        _merge_vitals(engine_form, C)
        resultado = run_engine(schema_key, engine_form,
                               {**P, 'idade': P['idade'], 'sexo': P['sexo']})
        perfil = {**PERFIL_VAZIO, **st.session_state.perfil_farmaco, 'idade': P['idade']}
        resultado = verificar_interacoes(resultado, perfil)

        # Receita híbrida — seletor de opções com a recomendada pré-marcada.
        # A escolha do médico injeta a prescrição correspondente antes do SOAP.
        op = resultado.get('opcoes_prescricao') if resultado else None
        if op and op.get('opcoes'):
            opcoes = op['opcoes']
            labels = [o['label'] + ('  ⭐' if o.get('recomendado') else '') for o in opcoes]
            rec_idx = next((i for i, o in enumerate(opcoes) if o.get('recomendado')), 0)
            wkey = f'rxopt_{schema_key}'
            st.markdown(f'<div style="font-size:0.72rem;color:#00F0FF;letter-spacing:1px;'
                        f'margin:4px 0;">⚕ {op["grupo"].upper()} — ⭐ sugerida; troque se quiser</div>',
                        unsafe_allow_html=True)
            sel = st.radio(op['grupo'], labels, index=rec_idx, key=wkey,
                           label_visibility='collapsed')
            escolha = opcoes[labels.index(sel)]
            # injeta a opção escolhida + eventuais prescrições fixas (sintomáticos)
            resultado['prescricoes_estruturadas'] = (
                escolha['rx'] + resultado.get('prescricoes_fixas', []))

        st.session_state.resultado = resultado

        if not resultado or resultado.get('_error'):
            st.markdown('<div class="soap-block soap-dim">Selecione a queixa e preencha a '
                        'coleta — o SOAP aparece aqui ao vivo.</div>',
                        unsafe_allow_html=True)
        else:
            soap_txt = build_full_soap(P, C, EX, engine_form, schema_key, resultado)
            st.session_state.soap_txt = soap_txt
            # Badge de urgência
            urg = resultado.get('urgencia', '')
            badges = {
                'emergencia':          ('⚠ EMERGÊNCIA — PS IMEDIATO', 'badge-emergency'),
                'internacao':          ('⚡ INTERNAÇÃO INDICADA', 'badge-urgente'),
                'urgente':             ('⚡ URGENTE — HOJE', 'badge-urgente'),
                'ambulatorio_urgente': ('↩ RETORNO 48H', 'badge-urgente'),
                'ambulatorio':         ('✓ AMBULATÓRIO / ALTA', 'badge-aps'),
                'eletivo':             ('📅 ELETIVO', 'badge-eletivo'),
            }
            if urg in badges:
                txt, cls = badges[urg]
                st.markdown(f'<div class="badge {cls}" style="font-size:0.85rem;'
                            f'padding:4px 12px;margin-bottom:8px;">{txt}</div>',
                            unsafe_allow_html=True)

            # Handoff — fecha o loop da triagem (dispneia → módulo dedicado)
            prox = resultado.get('proximo_modulo')
            prox_schema = MODULE_SCHEMAS.get(prox) if prox else None
            if prox_schema:
                prox_label = prox_schema.get('label', prox)
                st.info(f'Triagem aponta para **{prox_label}** — '
                        f'os sinais vitais e comorbidades do cabeçalho já seguem junto.')
                if st.button(f'▶  CONTINUAR NO MÓDULO: {prox_label}',
                             use_container_width=True, type='primary'):
                    # Troca o módulo ativo carregando o contexto do cabeçalho
                    disp = next((d for d, k in QUEIXA_MAP.items() if k == prox), None)
                    P['queixa_key'] = prox
                    P['queixa_display'] = disp or ''
                    P['queixa_principal'] = prox_label
                    st.session_state.form_data = {}
                    st.session_state.resultado = None
                    st.rerun()

            # Alertas de segurança em destaque
            alertas = resultado.get('alertas_seguranca', [])
            if alertas:
                items_html = ''.join(
                    f'<div class="interact-alert-item">⚠ {a}</div>' for a in alertas)
                st.markdown(
                    f'<div class="interact-box">'
                    f'<div class="interact-box-title">Alertas de Segurança</div>'
                    f'{items_html}</div>',
                    unsafe_allow_html=True)

            # Colorize
            html = soap_txt
            for sec in ['S:', 'O:', '#Análise:', '#Plano:', '#Receitas:']:
                html = html.replace(f'\n{sec}', f'\n<span class="soap-section">{sec}</span>')
            html = html.replace('⚠️', '<span class="soap-alert">⚠️</span>')
            html = html.replace('Nega:', '<span class="soap-dim">Nega:</span>')
            st.markdown(f'<div class="soap-block">{html}</div>', unsafe_allow_html=True)

            st.markdown('')
            if st.button('📋  COPIAR SOAP COMPLETO', use_container_width=True):
                st.session_state.show_modal = True
                st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# MODAL — copiar
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.show_modal and st.session_state.get('soap_txt'):
    with st.expander('📋 SOAP COMPLETO — Copiar e colar no prontuário', expanded=True):
        st.text_area('', value=st.session_state.soap_txt, height=520, label_visibility='collapsed')
        if st.button('✕ Fechar'):
            st.session_state.show_modal = False
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div style="text-align:center;color:#30363D;font-size:0.65rem;margin-top:1rem;'
            'letter-spacing:1px;">SYMPTOOPY · 40 MÓDULOS · ACG · BSG · IDSA · AHA · GINA · '
            'GOLD · ESC · AASM</div>', unsafe_allow_html=True)
