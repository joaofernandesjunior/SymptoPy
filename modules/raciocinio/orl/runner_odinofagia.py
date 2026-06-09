# modules/raciocinio/orl/runner_odinofagia.py
# Orquestrador: odinofagia_subjetivo → engine → impressão clínica
#
# Uso direto (CLI):
#   python -m modules.raciocinio.orl.runner_odinofagia
#   python -m modules.raciocinio.orl.runner_odinofagia dados_pacientes/odinofagia_subjetivo_*.json

import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from modules.raciocinio.orl.engine_odinofagia import interpretar_odinofagia

# ─── Labels legíveis por categoria ───────────────────────────────────────────
_LABEL = {
    'orl_emergencia_respiratoria':       '🔴 OBSTRUÇÃO VIA AÉREA — PS IMEDIATO',
    'orl_abscesso_periamigdaliano':      '🔴 ABSCESSO PERIAMIGDALIANO — PS Urgente',
    'orl_mononucleose':                  '🟡 Mononucleose Infecciosa (EBV) — SEM amoxicilina',
    'orl_faringoamigdalite_bacteriana':  '🟢 Faringoamigdalite Bacteriana (GAS) — ATB',
    'orl_faringoamigdalite_test_treat':  '🟡 Faringoamigdalite — Fazer TRA (Centor 2)',
    'orl_faringoamigdalite_viral':       '⚪ Faringoamigdalite Viral — Sintomático',
    'orl_disfonia_cronica':              '🟡 Disfonia ≥ 3 Semanas — Encaminhar ORL',
}


def _rx(med: dict) -> list:
    """Formata prescrição estruturada em linhas."""
    linhas = []
    lb = med.get('linha', '')
    if lb:
        linhas.append(f'\n  [{lb}]')
    linhas.append(f'  {med.get("medicamento", "")}')
    for p in med.get('prescricoes', []):
        linhas.append(f'    {p["quantidade"]} {p["unidade"]} — {p["posologia"]}')
    if med.get('nota'):
        linhas.append(f'    ⚠️  {med["nota"]}')
    return linhas


def _formatar(resultado: dict) -> str:
    cat      = resultado.get('categoria', '')
    urgencia = resultado.get('urgencia')
    linhas   = []

    linhas.append('=' * 60)
    linhas.append('  RESULTADO — DOR DE GARGANTA / ODINOFAGIA')
    linhas.append('=' * 60)

    label = _LABEL.get(cat, resultado.get('diagnostico', cat).upper())
    linhas.append(f'\n  {label}')
    linhas.append(f'  Diagnóstico: {resultado.get("diagnostico", "")}')
    if urgencia:
        linhas.append(f'  Urgência: {urgencia.upper()}')

    # Raciocínio
    raciocinio = resultado.get('raciocinio', '')
    if raciocinio:
        linhas.append('\n  Raciocínio:')
        for frase in raciocinio.split('. '):
            frase = frase.strip()
            if frase:
                linhas.append(f'  • {frase}{"." if not frase.endswith(".") else ""}')

    # Achados
    achados = resultado.get('achados', [])
    if achados:
        linhas.append('\n  Achados: ' + ' | '.join(achados))

    # Encaminhamento urgente
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
            linhas.extend(_rx(med))

    # Orientações
    orientacoes = resultado.get('orientacoes', {})
    if orientacoes:
        linhas.append('\n  #Orientações ao Paciente:')
        for chave, valor in orientacoes.items():
            if chave == 'sinais_de_alerta':
                linhas.append('  ⚠️  Retornar imediatamente se:')
                for s in valor:
                    linhas.append(f'      • {s}')
            elif isinstance(valor, str):
                titulo = chave.replace('_', ' ').title()
                linhas.append(f'  [{titulo}]')
                for sub in valor.split('\n'):
                    sub = sub.strip()
                    if sub:
                        linhas.append(f'  {sub}')

    # Encaminhamento eletivo
    if enc and urgencia not in ('emergencia', 'urgente'):
        linhas.append(f'\n  Encaminhamento eletivo: {enc}')

    # Retorno
    retorno = resultado.get('retorno', '')
    if retorno:
        linhas.append(f'\n  Retorno: {retorno}')

    linhas.append('\n' + '=' * 60)
    return '\n'.join(linhas)


def _clipboard(texto: str):
    try:
        import subprocess
        proc = subprocess.Popen(['clip'], stdin=subprocess.PIPE)
        proc.communicate(texto.encode('utf-8'))
        print('  [Resultado copiado para o clipboard]')
    except Exception:
        pass


def rodar_com_coleta():
    from modules.sintomas.orl.odinofagia_subjetivo import coletar_subjetivo_odinofagia
    dados, _ = coletar_subjetivo_odinofagia()
    resultado = interpretar_odinofagia(dados)
    saida = _formatar(resultado)
    print(saida)
    _clipboard(saida)
    return resultado


def rodar_com_json(arquivo_json: str):
    with open(arquivo_json, encoding='utf-8') as f:
        dados = json.load(f)
    resultado = interpretar_odinofagia(dados)
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
        rodar_com_json(sys.argv[1])
    else:
        rodar_com_coleta()
