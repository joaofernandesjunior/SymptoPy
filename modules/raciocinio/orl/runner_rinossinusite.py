# modules/raciocinio/orl/runner_rinossinusite.py
import json, os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from modules.raciocinio.orl.engine_rinossinusite import interpretar_rinossinusite

_LABEL = {
    'orl_rinossinusite_complicacao_orbital':  '🔴 Complicação Orbitária de RSA — PS Imediato',
    'orl_rinossinusite_complicacao_meningea': '🔴 Complicação Intracraniana de RSA — SAMU',
    'orl_rsab':                               '🟡 Rinossinusite Aguda Bacteriana — ATB 5–7d',
    'orl_ivas_viral':                         '🟢 IVAS Viral — Sintomático (sem ATB)',
    'orl_rinite_alergica':                    '🟢 Rinite Alérgica — Anti-hist. + Corticoide Nasal',
    'orl_rsc':                                '🔵 Rinossinusite Crônica — Encam. ORL',
    'orl_rsc_polipose':                       '🔵 RSC com Polipose — Encam. ORL urgente',
    'orl_rinossinusite_intermediario':        '⚪ Rinossinusite — Observação Ativa 48–72h',
}


def _rx_fmt(med):
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


def _formatar(resultado):
    cat      = resultado.get('categoria', '')
    urgencia = resultado.get('urgencia')
    linhas   = ['=' * 60, '  RESULTADO — OBSTRUÇÃO NASAL / RINOSSINUSITE', '=' * 60]
    label    = _LABEL.get(cat, resultado.get('diagnostico', cat).upper())
    linhas.append(f'\n  {label}')
    linhas.append(f'  Diagnóstico: {resultado.get("diagnostico", "")}')
    if urgencia:
        linhas.append(f'  Urgência: {urgencia.upper()}')
    rac = resultado.get('raciocinio', '')
    if rac:
        linhas.append('\n  Raciocínio:')
        for f in rac.split('. '):
            f = f.strip()
            if f:
                linhas.append(f'  • {f}{"." if not f.endswith(".") else ""}')
    ach = resultado.get('achados', [])
    if ach:
        linhas.append('\n  Achados: ' + ' | '.join(ach))
    enc = resultado.get('encaminhar')
    if enc and urgencia in ('emergencia', 'urgente'):
        linhas.append(f'\n  → ENCAMINHAR: {enc}')
    exames = resultado.get('exames', [])
    if exames:
        linhas.append('\n  Solicitar:')
        for e in exames:
            linhas.append(f'  • {e}')
    conduta = resultado.get('conduta', [])
    if conduta:
        linhas.append('\n  Conduta:')
        for c in conduta:
            linhas.append(f'  • {c}')
    rx_list = resultado.get('prescricoes_estruturadas', [])
    if rx_list:
        linhas.append('\n  Prescrições:')
        for med in rx_list:
            linhas.extend(_rx_fmt(med))
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
    if enc and urgencia not in ('emergencia', 'urgente'):
        linhas.append(f'\n  Encaminhamento eletivo: {enc}')
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
        print('  [Copiado para clipboard]')
    except Exception:
        pass


def rodar_com_coleta():
    from modules.sintomas.orl.rinossinusite_subjetivo import coletar_subjetivo_rinossinusite
    dados, _ = coletar_subjetivo_rinossinusite()
    resultado = interpretar_rinossinusite(dados)
    saida = _formatar(resultado)
    print(saida)
    _clipboard(saida)
    return resultado


def rodar_com_json(arquivo_json):
    with open(arquivo_json, encoding='utf-8') as f:
        dados = json.load(f)
    resultado = interpretar_rinossinusite(dados)
    saida = _formatar(resultado)
    print(saida)
    _clipboard(saida)
    return resultado


rodar = rodar_com_json

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    if len(sys.argv) > 1:
        rodar_com_json(sys.argv[1])
    else:
        rodar_com_coleta()
