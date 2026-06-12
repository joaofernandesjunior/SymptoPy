# ui/prontuario_builder.py
# Monta os dicts `paciente` e `admissao` no formato que o CLI usa
# e chama gerar_texto_prontuario() — o gerador de SOAP COMPLETO do texto.py.
#
# Isso reaproveita TODA a lógica rica: CID-10, negativas pertinentes,
# #Análise com justificativa, #Plano com condutas e prescrições estruturadas,
# alertas de comorbidade (DRC).

from prontuario.texto import gerar_texto_prontuario
from prontuario.objetivo import _NORMAL

try:
    from prontuario.comorbidades.drc import avaliar_drc
except Exception:
    avaliar_drc = None


# Mapa sexo interface → formato esperado pelo texto.py ('m'/'f')
def _sexo_curto(sexo: str) -> str:
    return {'masculino': 'm', 'feminino': 'f'}.get(sexo, sexo[:1].lower() if sexo else '')


def build_paciente(patient_full: dict) -> dict:
    """Converte os campos da interface no dict `paciente` do CLI."""
    # Junta comorbidades selecionadas (checkboxes) + texto livre
    comorb_list = list(patient_full.get('comorbidades_sel', []))
    comorb_free = (patient_full.get('comorbidades_free', '') or '').strip()
    if comorb_free:
        comorb_list.append(comorb_free)
    comorbidades = ', '.join(comorb_list) if comorb_list else ''

    # Contexto social: institucionalização + texto livre
    social_parts = []
    if patient_full.get('institucionalizado'):
        social_parts.append('Institucionalizado (ILPI/asilo) — risco de colonização por germes resistentes')
    if patient_full.get('acamado'):
        social_parts.append('Acamado / restrito ao leito')
    social_free = (patient_full.get('contexto_social', '') or '').strip()
    if social_free:
        social_parts.append(social_free)
    contexto_social = '. '.join(social_parts)

    return {
        'nome':             patient_full.get('nome', ''),
        'idade':            str(patient_full.get('idade', '')),
        'sexo':             _sexo_curto(patient_full.get('sexo', '')),
        'profissao':        patient_full.get('profissao', ''),
        'procedencia':      patient_full.get('procedencia', ''),
        'rg_hc':            patient_full.get('rg_hc', ''),
        'contexto_social':  contexto_social,
        'chv':              patient_full.get('chv', ''),
        'comorbidades':     comorbidades,
        'medicacoes':       patient_full.get('medicacoes', ''),
        'alergias':         patient_full.get('alergias', ''),
        'cirurgias_previas':patient_full.get('cirurgias_previas', ''),
        'internamentos':    patient_full.get('internamentos', ''),
    }


def build_objetivo(exam_data: dict) -> dict:
    """
    Monta o dict objetivo (8 sistemas + estado geral).
    exam_data tem por sistema: '{sistema}_normal' (bool) e '{sistema}_alt' (texto).
    """
    objetivo = {'estado_geral': exam_data.get('estado_geral', '')}
    sistemas = ['neuro', 'pneumo', 'cardio', 'abdome',
                'mmii', 'pele', 'orofaringe', 'eliminacoes']
    for s in sistemas:
        is_normal = exam_data.get(f'{s}_normal', True)
        if is_normal:
            objetivo[s] = _NORMAL[s]
        else:
            objetivo[s] = exam_data.get(f'{s}_alt', '').strip() or _NORMAL[s]
    return objetivo


def build_admissao(consult: dict, exam_data: dict, form_data: dict,
                   schema_key: str, resultado: dict | None,
                   paciente: dict) -> dict:
    """
    Monta o dict `admissao` completo no formato do CLI.
    """
    # NEWS2 — triagem objetiva calculada dos sinais vitais (substitui qSOFA)
    try:
        from modules.transversal.news2 import calcular_news2, texto_news2
        news2_txt = texto_news2(calcular_news2(consult))
    except Exception:
        news2_txt = ''

    admissao = {
        'news2':                 news2_txt,
        'queixa_principal':      consult.get('queixa_principal', ''),
        'hma':                   consult.get('hma', ''),
        'pa':                    consult.get('pa', ''),
        'fc':                    consult.get('fc', ''),
        'fr':                    consult.get('fr', ''),
        'sato2':                 consult.get('sato2', ''),
        'temperatura':           consult.get('temperatura', ''),
        'glicemia':              consult.get('glicemia', ''),
        'objetivo':              build_objetivo(exam_data),
        'exames_complementares': consult.get('exames_complementares', ''),
        'subjetivo_especifico':  {},
        'objetivo_especifico':   {},
        'analise':               '',
        'plano':                 '',
    }

    # Resultado do engine → análises automáticas (rota #Análise e #Plano)
    if resultado and not resultado.get('_error'):
        admissao['analises_automaticas'] = [{'resultado': resultado}]
    else:
        admissao['analises_automaticas'] = []

    # Dados do formulário → renderer de subjetivo específico do módulo
    if schema_key and form_data:
        admissao['dados_por_modulo'] = {schema_key: form_data}
        admissao['modulo_organico'] = schema_key
        admissao['dados_organico'] = form_data

    # Comorbidade automática — DRC (alertas + medicações em atenção + red flags)
    if avaliar_drc:
        try:
            drc = avaliar_drc(paciente, admissao)
            if drc:
                admissao['comorbidades_automaticas'] = {'drc': drc}
        except Exception:
            pass

    return admissao


def build_full_soap(patient_full: dict, consult: dict, exam_data: dict,
                    form_data: dict, schema_key: str,
                    resultado: dict | None) -> str:
    """
    Pipeline completo: monta paciente + admissao e gera o SOAP COMPLETO
    usando o gerador oficial do texto.py.
    """
    paciente = build_paciente(patient_full)
    admissao = build_admissao(consult, exam_data, form_data,
                              schema_key, resultado, paciente)
    try:
        return gerar_texto_prontuario(paciente, admissao)
    except Exception as e:
        import traceback
        return f'[ERRO ao gerar SOAP]: {e}\n\n{traceback.format_exc()}'
