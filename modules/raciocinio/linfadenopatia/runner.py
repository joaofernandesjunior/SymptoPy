# modules/raciocinio/linfadenopatia/runner.py

import json, os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from modules.raciocinio.linfadenopatia.engine_linfadenopatia import interpretar_linfadenopatia

_URGENCIA = {
    'linfoma_suspeito', 'neoplasia_metastatica', 'tb_linfadenopatia',
    'hiv_infeccao_primaria',
}


def _formatar(r) -> str:
    cat   = r.get('categoria', '')
    linhas = ['=' * 56, '  LINFADENOPATIA — RESULTADO', '=' * 56]

    # Urgência
    if cat in _URGENCIA or r.get('biopsia'):
        linhas.append('\n  ⚠️  ENCAMINHAMENTO INDICADO')

    linhas.append(f'\n  Diagnóstico: {r.get("diagnostico", "")}')
    padrao = r.get('padrao', '')
    if padrao:
        linhas.append(f'  Padrão: {padrao}')

    # Red flags
    flags = r.get('red_flags', [])
    if flags:
        linhas += ['', '  Red flags presentes:']
        for f in flags: linhas.append(f'  ⚑ {f}')

    # Motivo biópsia
    motivos = r.get('motivo_biopsia', [])
    if motivos:
        linhas += ['', '  Critérios para biópsia:']
        for m in motivos: linhas.append(f'  • {m}')

    # Exames
    exames = r.get('exames', [])
    if exames:
        linhas += ['', '  Exames:']
        for e in exames: linhas.append(f'  • {e}')

    # Tratamento
    trat = r.get('tratamento', {})
    if trat:
        linhas += ['', '  Conduta:']
        for chave, valor in trat.items():
            linhas.append(f'\n  [{chave.replace("_"," ").upper()}]')
            for linha in str(valor).split('\n'):
                linhas.append(f'    {linha.strip()}')

    # Encaminhamento
    enc = r.get('encaminhamento')
    if enc:
        linhas += ['', f'  Encaminhamento: {enc}']

    # Retorno (reativo)
    ret = r.get('retorno')
    if ret:
        linhas += ['', f'  Retorno: {ret}']

    linhas.append('\n' + '=' * 56)
    return '\n'.join(linhas)


def _clip(texto):
    try:
        import subprocess
        p = subprocess.Popen(['clip'], stdin=subprocess.PIPE)
        p.communicate(texto.encode('utf-8'))
    except Exception: pass


def rodar(arquivo_json):
    sys.stdout.reconfigure(encoding='utf-8')
    with open(arquivo_json, encoding='utf-8') as f:
        dados = json.load(f)
    r = interpretar_linfadenopatia(dados)
    t = _formatar(r)
    print(t)
    _clip(t)
    return r
