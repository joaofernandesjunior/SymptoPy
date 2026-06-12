# ui/engine_bridge.py
# Chama o engine correto a partir do nome do módulo + dados do formulário.
# Retorna o dict de resultado padronizado, ou None se não implementado.

import importlib


# ── Urgência — normalização central ──────────────────────────────────────────
# Vários engines codificam a emergência só na CATEGORIA e não preenchem o campo
# 'urgencia' → o badge da UI saía vazio justamente nos casos mais graves.
# Regras conservadoras: só inferem quando 'urgencia' está ausente.

_PADROES_EMERGENCIA = (
    'emergencia', 'sepse', 'instavel', 'choque', 'fasciite',
    '_grupo_d', 'cauda_equina', 'status_epilepticus', 'avc_',
    'tce_', 'meningite', 'overdose', 'hipoxia_grave', 'hipoglicemia',
)
_PADROES_URGENTE = (
    'red_flag', '_grupo_c', 'crise_grave', 'mastoidite', 'abscesso',
    'dvt_alto_risco', 'pancitopenia', 'internacao', 'exacerbacao_moderada',
    'linfoma_suspeito', 'neoplasia_metastatica', 'pielonefrite',
)

# Valores fora do vocabulário do badge → equivalente padrão
_ALIAS_URGENCIA = {
    'tratar_imediatamente': 'emergencia',
    'emergencia_absoluta':  'emergencia',
    'atenção':              'urgente',
    'atencao':              'urgente',
    'eletivo_prioritario':  'urgente',
    'aps':                  'ambulatorio',
    'encaminhar_neurologia':      'eletivo',
    'encaminhar_neurologia_sono': 'eletivo',
}


def _normalizar_urgencia(resultado: dict) -> dict:
    """Preenche/normaliza resultado['urgencia'] a partir da categoria."""
    if not isinstance(resultado, dict):
        return resultado
    urg = resultado.get('urgencia')
    if urg:
        resultado['urgencia'] = _ALIAS_URGENCIA.get(urg, urg)
        return resultado
    cat = str(resultado.get('categoria') or '')
    if any(p in cat for p in _PADROES_EMERGENCIA):
        resultado['urgencia'] = 'emergencia'
    elif any(p in cat for p in _PADROES_URGENTE):
        resultado['urgencia'] = 'urgente'
    return resultado


def run_engine(schema_key: str, form_data: dict, patient_data: dict) -> dict | None:
    """
    schema_key  : chave do MODULE_SCHEMAS (ex: 'celulite', 'palpitacao')
    form_data   : dict com todos os valores do formulário
    patient_data: dict com nome, idade, sexo, etc.
    Retorna o resultado do engine ou None se falhar.
    """
    from ui.schemas import MODULE_SCHEMAS
    schema = MODULE_SCHEMAS.get(schema_key)
    if not schema:
        return None

    module_path = schema.get('engine')
    fn_name     = schema.get('engine_fn')
    if not module_path or not fn_name:
        return None

    # Mescla dados do paciente no form_data para engines que precisam de idade/sexo
    merged = {**patient_data, **form_data}

    # Cabeçalho do paciente sempre prevalece sobre campos repetidos nos schemas
    for k in ('idade', 'sexo', 'peso_kg', 'gestante'):
        if patient_data.get(k) is not None:
            merged[k] = patient_data[k]

    # Remove chaves com valor None — campos numéricos opcionais não preenchidos.
    # Assim os engines usam seus próprios defaults em dados.get(k, default),
    # em vez de receberem None e quebrarem em comparações. (Cópia: não afeta o
    # form_data original usado pelos renderers de subjetivo / negativas.)
    merged = {k: v for k, v in merged.items() if v is not None}

    # Pré-processador: computa flags derivadas (centor_score, oma_suspeita, etc.)
    # para módulos cujo engine LÊ flags que o coletor CLI calculava.
    try:
        from ui.preprocessors import PREPROCESSORS
        pre = PREPROCESSORS.get(schema_key)
        if pre:
            merged = pre(merged)
    except Exception:
        pass

    # Engine legado (cefaleia, vertigem) tem assinatura diferente
    is_legacy = schema.get('legacy', False)

    try:
        mod = importlib.import_module(module_path)
        fn  = getattr(mod, fn_name)

        if is_legacy:
            # Engines legados recebem (subjetivo, objetivo) como dicts separados
            resultado = fn(merged, merged)
        else:
            resultado = fn(merged)

        return _normalizar_urgencia(resultado)

    except Exception as e:
        return {'_error': str(e), 'tipo': schema_key, 'categoria': 'erro_engine',
                'diagnostico': f'Erro no engine: {e}', 'urgencia': 'indefinido'}


def urgency_badge(urgencia: str) -> str:
    """Retorna HTML de badge colorido para a urgência."""
    MAP = {
        'emergencia':          ('<span class="badge badge-emergency">⚠ EMERGÊNCIA</span>', 'red'),
        'internacao':          ('<span class="badge badge-urgente">⚡ INTERNAÇÃO</span>',  'yellow'),
        'urgente':             ('<span class="badge badge-urgente">⚡ URGENTE</span>',      'yellow'),
        'ambulatorio_urgente': ('<span class="badge badge-urgente">↩ RETORNO 48H</span>',  'yellow'),
        'ambulatorio':         ('<span class="badge badge-aps">✓ AMBULATÓRIO</span>',      'green'),
        'eletivo':             ('<span class="badge badge-eletivo">📅 ELETIVO</span>',      'blue'),
    }
    return MAP.get(urgencia, ('<span class="badge badge-eletivo">—</span>', 'blue'))
