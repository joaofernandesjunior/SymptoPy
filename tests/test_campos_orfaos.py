# tests/test_campos_orfaos.py
# Pente-fino estrutural: garante que todo campo bool do schema é lido por
# ALGUÉM (engine, subjetivo ou preprocessor). Um campo órfão = o médico marca
# e nada acontece no SOAP — foi o bug da tosse (estertores) e do WPW.
# Rodar: python tests/test_campos_orfaos.py

import sys, os, inspect, importlib
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ui.schemas import MODULE_SCHEMAS
import prontuario.texto as T
from ui.preprocessors import PREPROCESSORS

# Órfãos tolerados (documentados): campos sem consumidor por decisão de projeto.
_TOLERADOS = {
    # 'modulo': {'campo1', 'campo2'},
}

_subj_map = dict((n, f) for n, f, _ in T.SINTOMAS_REGISTRADOS)


def _src(x):
    try:
        return inspect.getsource(x) if callable(x) else inspect.getsource(importlib.import_module(x))
    except Exception:
        return ''


def _schema_bool_keys(mod):
    out = []
    def walk(blocks):
        for b in blocks:
            if isinstance(b, dict):
                if b.get('type') == 'bool':
                    out.append(b['key'])
                for sk in ('fields', 'items'):
                    if sk in b:
                        walk(b[sk])
                if 'groups' in b:
                    for g in b['groups']:
                        walk(g.get('fields', []))
    walk(MODULE_SCHEMAS[mod].get('blocks', []))
    return out


def main():
    total_orfaos = 0
    for mod in sorted(MODULE_SCHEMAS):
        blob = _src(MODULE_SCHEMAS[mod].get('engine'))
        if _subj_map.get(mod):
            blob += _src(_subj_map[mod])
        if PREPROCESSORS.get(mod):
            blob += _src(PREPROCESSORS[mod])
        orfaos = [k for k in _schema_bool_keys(mod)
                  if k not in blob and k not in _TOLERADOS.get(mod, set())]
        if orfaos:
            total_orfaos += len(orfaos)
            print(f'[FAIL] {mod}: campos órfãos (ninguém lê) → {orfaos}')

    print()
    if total_orfaos == 0:
        print('OK — nenhum campo órfão. Todo bool do schema é consumido.')
        return 0
    print(f'{total_orfaos} campo(s) órfão(s) — ligue ao engine/subjetivo ou adicione a _TOLERADOS.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
