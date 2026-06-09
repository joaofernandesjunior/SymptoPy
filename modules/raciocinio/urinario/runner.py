# modules/raciocinio/urinario/runner.py
# Orquestra: subjetivo → engine → impressão clínica
#
# Uso direto (CLI):
#   python -m modules.raciocinio.urinario.runner
#   python -m modules.raciocinio.urinario.runner dados_pacientes/urinario_subjetivo_*.json

import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from modules.raciocinio.urinario.engine_urinario import interpretar_queixa_urinaria

# ─── Labels legíveis por categoria ───────────────────────────────────────────
_LABEL = {
    'cistite_simples':              'CISTITE NÃO COMPLICADA — tratamento empírico sem cultura',
    'cistite_complicada':           'CISTITE COMPLICADA — cultura obrigatória',
    'cistite_gestante':             'CISTITE NA GESTANTE — cultura + ATB seguro',
    'cistite_recorrente':           'CISTITE RECORRENTE — investigar + profilaxia',
    'pielonefrite_ambulatorial':    'PIELONEFRITE — tratamento ambulatorial',
    'pielonefrite_emergencia':      'PIELONEFRITE — CRITÉRIOS DE INTERNAÇÃO → PA/PS',
    'itu_masculina':                'ITU MASCULINA — sempre complicada',
    'prostatite_aguda':             'PROSTATITE AGUDA BACTERIANA',
    'prostatite_cronica':           'PROSTATITE CRÔNICA / CPPS',
    'hpb_stui':                     'HPB — Sintomas do Trato Urinário Inferior',
    'uretrite_ist':                 'URETRITE / IST — cobertura dual gonorreia + clamídia',
    'vaginite_candida':             'CANDIDÍASE VULVOVAGINAL',
    'vaginite_bv':                  'VAGINOSE BACTERIANA',
    'vaginite_atrofica':            'SÍNDROME GENITURINÁRIA DA MENOPAUSA',
    'herpes_genital':               'HERPES GENITAL',
    'sd_uretral':                   'SÍNDROME URETRAL — investigação necessária',
    'hematuria_macro_emergencia':   'HEMATÚRIA MACROSCÓPICA — EMERGÊNCIA',
    'hematuria_macro_urgente':      'HEMATÚRIA MACROSCÓPICA — encaminhar urologia ≤ 2 semanas',
    'hematuria_macro_itu':          'HEMATÚRIA MACROSCÓPICA + ITU — tratar e repetir EAS',
    'hematuria_macro_calculose':    'HEMATÚRIA — cálculo urinário provável',
    'hematuria_micro_glomerular':   'HEMATÚRIA MICROSCÓPICA — padrão GLOMERULAR → nefrologia',
    'hematuria_micro_alto_risco':   'HEMATÚRIA MICROSCÓPICA — ALTO RISCO → urologia',
    'hematuria_micro_moderado_risco': 'HEMATÚRIA MICROSCÓPICA — risco moderado',
    'hematuria_micro_baixo_risco':  'HEMATÚRIA MICROSCÓPICA — baixo risco → seguimento APS',
    'hematuria_nao_confirmada':     'HEMATÚRIA NÃO CONFIRMADA — repetir EAS',
    'red_flag_urinario':            'RED FLAG — ENCAMINHAMENTO IMEDIATO',
}

_COR_URGENCIA = {
    'emergencia': '🔴',
    'urgente':    '🟡',
    'eletivo':    '🟢',
}


def _formatar(resultado) -> str:
    cat      = resultado.get('categoria', '')
    urgencia = resultado.get('urgencia')
    linhas   = []

    linhas.append('=' * 56)
    linhas.append('  RESULTADO — QUEIXA URINÁRIA')
    linhas.append('=' * 56)

    icone = _COR_URGENCIA.get(urgencia, '⚪')
    label = _LABEL.get(cat, cat.upper())
    linhas.append(f'\n  {icone}  {label}')
    linhas.append(f'  Diagnóstico: {resultado.get("diagnostico", "")}')
    linhas.append(f'  Força: {resultado.get("forca", "").upper()}')

    if urgencia:
        linhas.append(f'  Urgência: {urgencia.upper()}')

    # Red flags
    for flag in resultado.get('red_flags', []):
        linhas.append(f'\n  ⚠️  {flag.get("achado", "")}')
        linhas.append(f'     → {flag.get("acao", "")}')

    # Achados positivos
    achados = resultado.get('achados', [])
    if achados:
        linhas.append('\n  Achados:')
        for a in achados:
            linhas.append(f'  • {a}')

    # Encaminhamento (imediato → no topo)
    enc = resultado.get('encaminhar')
    if enc and urgencia in ('emergencia', 'urgente'):
        linhas.append(f'\n  → ENCAMINHAR: {enc}')

    # Exames
    exames = resultado.get('exames', [])
    if exames:
        linhas.append('\n  Solicitar:')
        for e in exames:
            linhas.append(f'  • {e}')

    # Conduta
    conduta = resultado.get('conduta', [])
    if conduta:
        linhas.append('\n  Conduta:')
        for c in conduta:
            linhas.append(f'  • {c}')

    # Prescrições
    prescricoes = resultado.get('prescricoes_estruturadas', [])
    if prescricoes:
        linhas.append('\n  Prescrições:')
        for med in prescricoes:
            linha = med.get('linha', '')
            nome  = med.get('medicamento', '')
            if linha:
                linhas.append(f'\n  [{linha}]')
            linhas.append(f'  {nome}')
            for p in med.get('prescricoes', []):
                linhas.append(
                    f'    {p["quantidade"]} {p["unidade"]} — {p["posologia"]}'
                )
            if med.get('nota'):
                linhas.append(f'    Obs.: {med["nota"]}')

    # Encaminhamento eletivo (ao final)
    if enc and urgencia not in ('emergencia', 'urgente'):
        linhas.append(f'\n  Encaminhamento eletivo: {enc}')

    # Retorno
    retorno = resultado.get('retorno', '')
    if retorno:
        linhas.append(f'\n  Retorno: {retorno}')

    linhas.append('\n' + '=' * 56)
    return '\n'.join(linhas)


def _clipboard(texto):
    try:
        import subprocess
        proc = subprocess.Popen(['clip'], stdin=subprocess.PIPE)
        proc.communicate(texto.encode('utf-8'))
        print('  [Resultado copiado para o clipboard]')
    except Exception:
        pass


def rodar_com_coleta():
    """Coleta anamnese interativamente e processa com o engine."""
    from modules.sintomas.urinario.subjetivo import coletar_subjetivo_urinario
    dados, _ = coletar_subjetivo_urinario()
    resultado = interpretar_queixa_urinaria(dados)
    saida = _formatar(resultado)
    print(saida)
    _clipboard(saida)
    return resultado


def rodar_com_json(arquivo_json):
    """Carrega dados de um JSON e processa com o engine."""
    with open(arquivo_json, encoding='utf-8') as f:
        dados = json.load(f)
    resultado = interpretar_queixa_urinaria(dados)
    saida = _formatar(resultado)
    print(saida)
    _clipboard(saida)
    return resultado


# Alias para o dispatcher (padrão dos módulos orgânicos)
rodar = rodar_com_json


# =============================================================================
# CLI
# =============================================================================

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')

    if len(sys.argv) > 1:
        # Recebeu caminho de JSON como argumento
        rodar_com_json(sys.argv[1])
    else:
        # Coleta interativa
        rodar_com_coleta()
