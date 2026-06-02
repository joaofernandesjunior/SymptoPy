# ui/soap_preview.py
# Gera o texto do SOAP a partir do resultado do engine + dados do paciente.
# Usado tanto para o painel de preview (tempo real) quanto para o modal final.

import datetime
from ui.theme import ACCENT, GREEN, RED, YELLOW, TEXT_DIM, TEXT


def _fmt_rx(rx_list: list) -> str:
    """Formata lista de prescricoes_estruturadas em texto limpo."""
    if not rx_list:
        return ''
    linhas = []
    for rx in rx_list:
        if not isinstance(rx, dict):
            continue
        med  = rx.get('medicamento', '')
        nota = rx.get('nota', '')
        pres = rx.get('prescricoes', [])
        linha_rx = f'  • {med}'
        if pres and isinstance(pres, list):
            for p in pres:
                if isinstance(p, dict):
                    qtd  = p.get('quantidade', '')
                    uni  = p.get('unidade', '')
                    pos  = p.get('posologia', '')
                    linha_rx += f' — {qtd} {uni} — {pos}'
        if nota:
            linha_rx += f'\n    ↳ {nota}'
        linhas.append(linha_rx)
    return '\n'.join(linhas)


def build_soap(patient: dict, resultado: dict | None, form_data: dict,
               schema_key: str = None) -> str:
    """
    Retorna string do SOAP completo.
    """
    hoje  = datetime.date.today().strftime('%d/%m/%Y')
    nome  = patient.get('nome', 'Paciente') or 'Paciente'
    idade = patient.get('idade', '')
    sexo  = patient.get('sexo', '')
    qp    = patient.get('queixa_principal', '')

    linhas = []

    # ── Cabeçalho ─────────────────────────────────────────────────────────────
    sexo_str = 'M' if sexo == 'masculino' else 'F' if sexo == 'feminino' else ''
    linhas.append(f'Paciente: {nome}, {idade}a, {sexo_str} — {hoje}')
    if qp:
        linhas.append(f'QP: {qp}')
    linhas.append('')

    if not resultado:
        linhas.append('S: Aguardando dados...')
        linhas.append('\nO: Aguardando dados...')
        linhas.append('\n#Análise: —')
        linhas.append('\n#Plano: —')
        return '\n'.join(linhas)

    err = resultado.get('_error')
    if err:
        linhas.append(f'[ERRO NO ENGINE]: {err}')
        return '\n'.join(linhas)

    # ── S: Subjetivo ─────────────────────────────────────────────────────────
    linhas.append('S:')
    _build_subjetivo(linhas, resultado, form_data, schema_key=schema_key)
    linhas.append('')

    # ── O: Objetivo ──────────────────────────────────────────────────────────
    linhas.append('O:')
    _build_objetivo(linhas, form_data, patient)
    linhas.append('')

    # ── #Análise ──────────────────────────────────────────────────────────────
    linhas.append('#Análise:')
    diag   = resultado.get('diagnostico', '')
    rac    = resultado.get('raciocinio', '')
    cat    = resultado.get('categoria', '')
    score_n= resultado.get('score_nome')
    score_v= resultado.get('score_valor')

    if diag:
        linhas.append(f'  {diag}')
    if score_n is not None and score_v is not None:
        linhas.append(f'  {score_n}: {score_v} pontos.')
    if rac:
        linhas.append(f'  {rac}')
    linhas.append('')

    # ── #Plano ────────────────────────────────────────────────────────────────
    linhas.append('#Plano:')
    conduta = resultado.get('conduta', '')
    if isinstance(conduta, str) and conduta:
        for frase in conduta.split('. '):
            frase = frase.strip()
            if frase:
                linhas.append(f'  • {frase}.')
    elif isinstance(conduta, list):
        for item in conduta:
            linhas.append(f'  • {item}')

    exames = resultado.get('exames', '')
    if isinstance(exames, list):
        exames = ', '.join(exames)
    if exames:
        linhas.append(f'\n  Exames: {exames}')

    rx_list = resultado.get('prescricoes_estruturadas', [])
    if rx_list:
        linhas.append('\n  Prescrição:')
        linhas.append(_fmt_rx(rx_list))

    enc = resultado.get('encaminhamento', '') or resultado.get('encaminhar', '')
    if enc:
        linhas.append(f'\n  Encaminhamento: {enc}')

    return '\n'.join(linhas)


def extract_pertinent_negatives(schema_key: str, form_data: dict) -> list[str]:
    """
    Percorre o schema do módulo e retorna lista de labels das negativas pertinentes.
    Um campo é negativa pertinente quando:
      - field['negative'] is True (ou flag='red' que seta negative automaticamente)
      - form_data[key] is False  (explicitamente negado — não None)
    """
    try:
        from ui.schemas import MODULE_SCHEMAS
        schema = MODULE_SCHEMAS.get(schema_key, {})
        negs = []
        for block in schema.get('blocks', []):
            for field in block.get('fields', []):
                if field.get('type') != 'bool':
                    continue
                if not field.get('negative'):
                    continue
                key = field['key']
                # False = explicitamente negado; None = não perguntado
                if form_data.get(key) is False:
                    # Remove prefixos visuais do label
                    label = field['label']
                    for prefix in ('⚠ ', '🔴 ', '🟡 ', '⚠ CREPITAÇÃO', '⚠'):
                        label = label.replace(prefix, '').strip()
                    negs.append(label.lower())
        return negs
    except Exception:
        return []


def _build_subjetivo(linhas: list, resultado: dict, form_data: dict,
                     schema_key: str = None):
    """Extrai achados positivos + negativas pertinentes para o Subjetivo."""
    achados = resultado.get('achados', [])

    if achados:
        linhas.append('  ' + '; '.join(str(a) for a in achados if a) + '.')

    # Negativas pertinentes do schema
    negs = extract_pertinent_negatives(schema_key or '', form_data)
    if negs:
        linhas.append(f'  Nega: {", ".join(negs)}.')


def _build_objetivo(linhas: list, form_data: dict, patient: dict):
    """Monta linha de sinais vitais do formulário."""
    parts = []
    if form_data.get('pas'): parts.append(f'PA {form_data["pas"]} mmHg')
    if form_data.get('fc'):  parts.append(f'FC {form_data["fc"]} bpm')
    temp = form_data.get('temperatura') or form_data.get('temp_celsius')
    if temp: parts.append(f'T {temp}°C')

    if parts:
        linhas.append('  SV: ' + ' | '.join(parts))
    else:
        linhas.append('  SV: ___/___ mmHg | ___ bpm | T ___°C | SpO₂ ___% | HGT ___ mg/dL')

    linhas.append('  EG: Aguardando preenchimento.')
    linhas.append('  EF dirigido: Aguardando preenchimento.')


def build_soap_html(patient: dict, resultado: dict | None, form_data: dict,
                    schema_key: str = None) -> str:
    """
    Retorna HTML colorido para exibição no painel direito (preview).
    """
    texto = build_soap(patient, resultado, form_data, schema_key=schema_key)
    if not resultado or resultado.get('_error'):
        return f'<div class="soap-block soap-dim">{texto}</div>'

    urgencia = resultado.get('urgencia', '')
    badge_html, badge_color = _badge(urgencia)

    html = texto
    html = html.replace('S:', f'<span class="soap-section">S:</span>')
    html = html.replace('O:', f'<span class="soap-section">O:</span>')
    html = html.replace('#Análise:', f'<span class="soap-section">#Análise:</span>')
    html = html.replace('#Plano:', f'<span class="soap-section">#Plano:</span>')
    html = html.replace('  Prescrição:', f'  <span class="soap-rx">Prescrição:</span>')
    html = html.replace('  Encaminhamento:', f'  <span class="soap-flag">Encaminhamento:</span>')
    html = html.replace('⚠', f'<span class="soap-alert">⚠</span>')

    return f'{badge_html}<div class="soap-block">{html}</div>'


def _badge(urgencia: str) -> tuple[str, str]:
    MAP = {
        'emergencia':          ('<div class="badge badge-emergency" style="margin-bottom:8px;font-size:0.85rem;padding:4px 12px;">⚠ EMERGÊNCIA — PS IMEDIATO</div>', 'red'),
        'internacao':          ('<div class="badge badge-urgente" style="margin-bottom:8px;font-size:0.85rem;padding:4px 12px;">⚡ INTERNAÇÃO INDICADA</div>', 'yellow'),
        'urgente':             ('<div class="badge badge-urgente" style="margin-bottom:8px;font-size:0.85rem;padding:4px 12px;">⚡ URGENTE — CONSULTA HOJE</div>', 'yellow'),
        'ambulatorio_urgente': ('<div class="badge badge-urgente" style="margin-bottom:8px;font-size:0.85rem;padding:4px 12px;">↩ RETORNO EM 48H</div>', 'yellow'),
        'ambulatorio':         ('<div class="badge badge-aps" style="margin-bottom:8px;font-size:0.85rem;padding:4px 12px;">✓ AMBULATÓRIO / ALTA</div>', 'green'),
        'eletivo':             ('<div class="badge badge-eletivo" style="margin-bottom:8px;font-size:0.85rem;padding:4px 12px;">📅 ELETIVO</div>', 'blue'),
    }
    return MAP.get(urgencia, ('', 'blue'))
