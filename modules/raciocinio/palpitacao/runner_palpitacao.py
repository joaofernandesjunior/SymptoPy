# modules/raciocinio/palpitacao/runner_palpitacao.py
import json, os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from modules.raciocinio.palpitacao.engine_palpitacao import analisar_palpitacao

_LABEL = {
    'pal_instabilidade_hemodinamica': '🔴 Instabilidade Hemodinâmica — SAMU/PS Imediato',
    'pal_wpw':                        '🔴 WPW (Pré-Excitação) — PS Urgente | ⚠️ NUNCA Verapamil/Digoxina',
    'pal_tv_qrs_largo':               '🔴 Taquicardia QRS Largo — TV Suspeita — PS Imediato',
    'pal_brugada_sincope':            '🔴 Brugada + Síncope — PS / Eletrofisiologia Urgente',
    'pal_qt_longo_sincope':           '🔴 QT Longo + Síncope — Torsades Suspeita — PS Imediato',
    'pal_sincope_arritmia':           '🟠 Síncope + Palpitação — Investigação Urgente',
    'pal_flutter':                    '🟠 Flutter Atrial — Cardiologia Urgente',
    'pal_fa_nova_cardioversao':       '🟡 FA Nova < 48h — Cardioversão Química (Propafenona)',
    'pal_fa_nova_controle_fc':        '🟡 FA — Controle de FC + Anticoagulação',
    'pal_fa_cronica':                 '🟢 FA Crônica — Metoprolol + DOAC',
    'pal_tsv_paroxistica':            '🟢 TSV Paroxística — Valsalva + Metoprolol Profilático',
    'pal_extrassistolia':             '⚪ Extrassistolia — Holter Eletivo + Tranquilizar',
    'pal_hipertireoidismo':           '🟡 Palpitação por Hipertireoidismo — TSH + Propranolol',
    'pal_anemia':                     '🟡 Palpitação por Anemia — Hemograma + Causa',
    'pal_ansiedade_panico':           '🟢 Transtorno do Pânico — ISRS + TCC',
    'pal_farmaco_estimulante':        '🟡 Palpitação por Fármaco/Estimulante — Cessar Agente',
    'pal_inespecifico':               '⚪ Palpitação Inespecífica — Holter 24h Eletivo',
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
    urgencia = resultado.get('urgencia', '')
    linhas   = ['=' * 62, '  RESULTADO — PALPITAÇÃO', '=' * 62]

    label = _LABEL.get(cat, resultado.get('diagnostico', cat).upper())
    linhas.append(f'\n  {label}')
    linhas.append(f'  Diagnóstico: {resultado.get("diagnostico", "")}')
    if urgencia:
        linhas.append(f'  Urgência: {urgencia.upper()}')

    rac = resultado.get('raciocinio', '')
    if rac:
        linhas.append('\n  Raciocínio:')
        for frase in rac.split('. '):
            frase = frase.strip()
            if frase:
                linhas.append(f'  • {frase}{"." if not frase.endswith(".") else ""}')

    ach = resultado.get('achados', [])
    if ach:
        linhas.append('\n  Achados: ' + ' | '.join(ach))

    rf = resultado.get('red_flags', [])
    rf = [r for r in rf if r]  # filtrar strings vazias
    if rf:
        linhas.append('\n  🚨 Red Flags:')
        for r in rf:
            linhas.append(f'  ⚠️  {r}')

    enc = resultado.get('encaminhar')
    if enc and urgencia in ('emergencia', 'urgente'):
        linhas.append(f'\n  → ENCAMINHAR: {enc}')

    exames = resultado.get('exames', [])
    if exames:
        linhas.append('\n  Solicitar:')
        for e in exames:
            linhas.append(f'  • {e}')

    conduta = resultado.get('conduta', [])
    conduta = [c for c in conduta if c]  # filtrar strings vazias
    if conduta:
        linhas.append('\n  Conduta:')
        for c in conduta:
            linhas.append(f'  • {c}')

    for med in resultado.get('prescricoes_estruturadas', []):
        if not any('Prescrições' in l for l in linhas):
            linhas.append('\n  Prescrições:')
        linhas.extend(_rx_fmt(med))

    orientacoes = resultado.get('orientacoes', {})
    if orientacoes:
        linhas.append('\n  Orientações ao Paciente:')
        for chave, valor in orientacoes.items():
            titulo = chave.replace('_', ' ').title()
            linhas.append(f'\n  [{titulo}]')
            for sub in valor.split('\n'):
                sub = sub.strip()
                if sub:
                    linhas.append(f'  {sub}')

    dias = resultado.get('dias_atestado')
    if dias:
        linhas.append(f'\n  Atestado: {dias} dia(s)')

    if enc and urgencia not in ('emergencia', 'urgente'):
        linhas.append(f'\n  Encaminhamento: {enc}')

    retorno = resultado.get('retorno', '')
    if retorno:
        linhas.append(f'\n  Retorno: {retorno}')

    linhas.append('\n' + '=' * 62)
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
    from modules.sintomas.palpitacao.subjetivo import coletar_subjetivo_palpitacao
    dados, _ = coletar_subjetivo_palpitacao()
    resultado = analisar_palpitacao(dados)
    saida = _formatar(resultado)
    print(saida)
    _clipboard(saida)
    return resultado


def rodar_com_json(arquivo_json):
    with open(arquivo_json, encoding='utf-8') as f:
        dados = json.load(f)
    resultado = analisar_palpitacao(dados)
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
