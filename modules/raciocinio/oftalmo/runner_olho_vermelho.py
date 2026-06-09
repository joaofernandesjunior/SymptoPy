# modules/raciocinio/oftalmo/runner_olho_vermelho.py
import json, os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from modules.raciocinio.oftalmo.engine_olho_vermelho import interpretar_olho_vermelho

_LABEL = {
    'oft_trauma_ocular':              '🔴 Trauma Ocular — PS Imediato',
    'oft_glaucoma_agudo':             '🔴 Glaucoma Agudo — PS Imediato',
    'oft_endoftalmite':               '🔴 Endoftalmite Pós-Operatória — Oftalmo Emergência',
    'oft_ulcera_cornea':              '🔴 Úlcera de Córnea (Lente) — Oftalmo Urgente',
    'oft_uveite_glaucoma_suspeito':   '🔴 Ciliary Flush — Uveíte/Glaucoma — Oftalmo Urgente',
    'oft_celulite_orbitaria':         '🔴 Celulite Orbitária — PS Urgente',
    'oft_celulite_preseptal':         '🟡 Celulite Pré-Septal — ATB Oral + Retorno 24–48h',
    'oft_hordeoleo':                  '🟢 Hordéolo (Orzolho) — Compressa Morna',
    'oft_hemorragia_subconj':         '⚪ Hemorragia Subconjuntival — Evolução Espontânea',
    'oft_conjuntivite_bacteriana':    '🟢 Conjuntivite Bacteriana — Tobramicina 7d',
    'oft_conjuntivite_viral':         '🟡 Conjuntivite Viral (Adenovírus) — Isolamento',
    'oft_conjuntivite_alergica':      '🟢 Conjuntivite Alérgica — Cetotifeno',
    'oft_olho_vermelho_inespecifico': '⚪ Olho Vermelho — Oftalmo Eletivo',
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
    linhas   = ['=' * 60, '  RESULTADO — OLHO VERMELHO', '=' * 60]

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

    enc = resultado.get('encaminhar')
    if enc and urgencia in ('emergencia', 'urgente'):
        linhas.append(f'\n  → ENCAMINHAR: {enc}')

    rf = resultado.get('red_flags', [])
    if rf:
        linhas.append('\n  🚨 Red Flags:')
        for r in rf:
            linhas.append(f'  ⚠️  {r}')

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

    for med in resultado.get('prescricoes_estruturadas', []):
        if not any(l.startswith('\n  Prescrições') for l in linhas):
            linhas.append('\n  Prescrições:')
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
                linhas.append(f'\n  [{titulo}]')
                for sub in valor.split('\n'):
                    sub = sub.strip()
                    if sub:
                        linhas.append(f'  {sub}')

    dias = resultado.get('dias_atestado')
    if dias:
        linhas.append(f'\n  Atestado: {dias} dias')

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
    from modules.sintomas.oftalmo.olho_vermelho_subjetivo import coletar_subjetivo_olho_vermelho
    dados, _ = coletar_subjetivo_olho_vermelho()
    resultado = interpretar_olho_vermelho(dados)
    saida = _formatar(resultado)
    print(saida)
    _clipboard(saida)
    return resultado


def rodar_com_json(arquivo_json):
    with open(arquivo_json, encoding='utf-8') as f:
        dados = json.load(f)
    resultado = interpretar_olho_vermelho(dados)
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
