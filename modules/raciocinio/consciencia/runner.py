# modules/raciocinio/consciencia/runner.py
import json, os, sys
sys.path.append(os.path.join(os.path.dirname(__file__),'..','..','..'))
from modules.raciocinio.consciencia.engine_consciencia import interpretar_consciencia

_URG = {'emergencia': '🔴 EMERGÊNCIA', 'urgente': '🟠 URGENTE', 'eletivo': '🟢 Eletivo'}

def _fmt(r) -> str:
    cat = r.get('categoria','')
    linhas = ['='*56, '  ALTERAÇÃO DO NÍVEL DE CONSCIÊNCIA', '='*56]
    linhas.append(f'\n  {_URG.get(r.get("urgencia",""),"")}'
                  f' | Glasgow {r.get("glasgow","?")}/15')
    if r.get('iot_alerta'):
        linhas.append('  ⚠️  GLASGOW ≤ 8 — AVALIAR IOT / SAMU')
    linhas.append(f'\n  Diagnóstico: {r.get("diagnostico","")}')
    linhas.append('')
    for c in r.get('conduta',[]):
        if c: linhas.append(f'  {"  " if c.startswith("  ") else "• "}{c}')
    exames = r.get('exames',[])
    if exames:
        linhas += ['', '  Exames:']
        for e in exames: linhas.append(f'  • {e}')
    enc = r.get('encaminhamento')
    if enc: linhas += ['', f'  Encaminhamento: {enc}']
    linhas.append('\n'+'='*56)
    return '\n'.join(linhas)

def _clip(t):
    try:
        import subprocess
        p = subprocess.Popen(['clip'], stdin=subprocess.PIPE)
        p.communicate(t.encode('utf-8'))
    except: pass

def rodar(arq):
    sys.stdout.reconfigure(encoding='utf-8')
    with open(arq, encoding='utf-8') as f: dados = json.load(f)
    r = interpretar_consciencia(dados)
    t = _fmt(r)
    print(t); _clip(t)
    return r
