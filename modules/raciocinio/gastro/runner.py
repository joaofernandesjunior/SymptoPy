# modules/raciocinio/gastro/runner.py
# Orquestra: subjetivo JSON → engine → impressão clínica
#
# Uso direto (CLI):
#   python -m modules.raciocinio.gastro.runner
#   python -m modules.raciocinio.gastro.runner dados_pacientes/gastro_subjetivo_*.json

import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from modules.raciocinio.gastro.engine_gastro import interpretar_queixa_gastro

# ─── Labels legíveis por categoria ───────────────────────────────────────────
_LABEL = {
    'gastro_emergencia_peritonite':           '🔴 PERITONITE / ABDÔME AGUDO — PS imediato',
    'gastro_emergencia_obstrucao':            '🔴 OBSTRUÇÃO INTESTINAL — PS imediato',
    'gastro_emergencia_sangramento_gi':       '🔴 SANGRAMENTO GI ATIVO — PS imediato',
    'gastro_emergencia_apendicite':           '🔴 APENDICITE SUSPEITA — PS imediato',
    'gastro_emergencia_colecistite':          '🔴 COLECISTITE AGUDA — PS imediato',
    'gastro_emergencia_isquemia_mesenterica': '🔴 ISQUEMIA MESENTÉRICA — PS vascular urgente',
    'gastro_emergencia_ectopica':             '🔴 GRAVIDEZ ECTÓPICA SUSPEITA — Emergência',
    'gastro_emergencia_diverticulite_complicada': '🔴 DIVERTICULITE COMPLICADA — PS imediato',
    'gastro_dip':                             '🟡 DIP — Doença Inflamatória Pélvica',
    'gastro_diverticulite_ambulatorial':      '🟡 Diverticulite Ambulatorial',
    'gastro_ibd_suspeita':                    '🟡 IBD Suspeita (Crohn / Retocolite)',
    'gastro_celiaca_suspeita':                '🟡 Doença Celíaca Suspeita',
    'gastro_cdiff_suspeita':                  '⚠️  C. difficile — Pesquisar toxina',
    'gastro_parasitose_ameba':                '🟢 Amebíase Intestinal',
    'gastro_parasitose_helminto':             '🟢 Helmintose',
    'gastro_parasitose_protozoa':             '🟢 Giardíase',
    'gastro_colica_biliar':                   '🟢 Cólica Biliar',
    'gastro_dispepsia_hp_positivo':           '🟢 Dispepsia — Erradicação H. pylori',
    'gastro_dispepsia_hp_testandteat':        '🟢 Dispepsia — Test-and-Treat H. pylori',
    'gastro_dispepsia_funcional':             '🟢 Dispepsia Funcional',
    'gastro_sii_c':                           '🟢 SII-C — Intestino Irritável / Constipação',
    'gastro_sii_d':                           '🟢 SII-D — Intestino Irritável / Diarreia',
    'gastro_sii_m':                           '🟢 SII-M — Intestino Irritável Misto',
    'gastro_constipacao_funcional':           '🟢 Constipação Funcional',
    'gastro_intolerancia_lactose':            '🟢 Intolerância à Lactose',
    'gastro_nausea_vomito':                   '🟢 Náusea / Vômito — Sintomático',
    'gastro_inespecifico':                    '⚪ Dor Abdominal — Em Investigação',
}


def _formatar(resultado) -> str:
    cat      = resultado.get('categoria', '')
    urgencia = resultado.get('urgencia')
    linhas   = []

    linhas.append('=' * 60)
    linhas.append('  RESULTADO — QUEIXA GASTROINTESTINAL')
    linhas.append('=' * 60)

    label = _LABEL.get(cat, resultado.get('diagnostico', cat).upper())
    linhas.append(f'\n  {label}')
    linhas.append(f'  Diagnóstico: {resultado.get("diagnostico", "")}')
    if urgencia:
        linhas.append(f'  Urgência: {urgencia.upper()}')

    # Raciocínio clínico
    raciocinio = resultado.get('raciocinio', '')
    if raciocinio:
        linhas.append('\n  Raciocínio:')
        for linha in raciocinio.split('. '):
            linha = linha.strip()
            if linha:
                linhas.append(f'  • {linha}{"." if not linha.endswith(".") else ""}')

    # Achados
    achados = resultado.get('achados', [])
    if achados:
        linhas.append('\n  Achados: ' + ' | '.join(achados))

    # Alerta C. diff
    if resultado.get('alerta_cdiff'):
        linhas.append('\n  ⚠️  ATB recente + diarreia → considerar C. difficile')
        linhas.append('     Solicitar: pesquisa de toxina A/B nas fezes')
        linhas.append('     Não prescrever loperamida até excluir colite por C. diff')

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

    # Prescrições estruturadas
    prescricoes = resultado.get('prescricoes_estruturadas', [])
    if prescricoes:
        linhas.append('\n  Prescrições:')
        for med in prescricoes:
            linha_label = med.get('linha', '')
            if linha_label:
                linhas.append(f'\n  [{linha_label}]')
            linhas.append(f'  {med.get("medicamento", "")}')
            for p in med.get('prescricoes', []):
                linhas.append(
                    f'    {p["quantidade"]} {p["unidade"]} — {p["posologia"]}'
                )
            if med.get('nota'):
                linhas.append(f'    ⚠️  {med["nota"]}')

    # Orientações ao paciente
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
                for sublinha in valor.split('\n'):
                    sublinha = sublinha.strip()
                    if sublinha:
                        linhas.append(f'  {sublinha}')

    # Encaminhamento eletivo
    if enc and urgencia not in ('emergencia', 'urgente'):
        linhas.append(f'\n  Encaminhamento eletivo: {enc}')

    # Retorno
    retorno = resultado.get('retorno', '')
    if retorno:
        linhas.append(f'\n  Retorno: {retorno}')

    linhas.append('\n' + '=' * 60)
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
    from modules.sintomas.abdominal.gastro_subjetivo import coletar_subjetivo_abdominal
    dados, _ = coletar_subjetivo_abdominal()
    resultado = interpretar_queixa_gastro(dados)
    saida = _formatar(resultado)
    print(saida)
    _clipboard(saida)
    return resultado


def rodar_com_json(arquivo_json):
    """Carrega dados de um JSON e processa com o engine."""
    with open(arquivo_json, encoding='utf-8') as f:
        dados = json.load(f)
    resultado = interpretar_queixa_gastro(dados)
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
