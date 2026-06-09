# tests/test_consciencia.py
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__),'..'))
from modules.raciocinio.consciencia.engine_consciencia import interpretar_consciencia

def _base():
    return {
        'idade': 40, 'dm': False, 'epilepsia_previa': False,
        'alcool_drogas': False, 'psiq_previa': False, 'avc_previo': False,
        'medicamentos_risco': False, 'medicamentos_quais': '',
        'onset': 'subito', 'testemunhado': False,
        'convulsao_obs': False, 'trauma_obs': False, 'ingestao_obs': False,
        'glasgow_e': 4, 'glasgow_v': 5, 'glasgow_m': 6, 'glasgow_total': 15,
        'glicemia_disponivel': False, 'glicemia': None,
        'intoxicacao_suspeita': False, 'intox_tipo': '',
        'alcool_halito': False, 'acidose_suspeita': False,
        'pos_ictal': False, 'encefalopatia': False,
        'hipoxia': False, 'spo2': None,
        'renal_cronico': False,
        'trauma_cabeca': False, 'anticoagulante': False, 'lucido_intervalo': False,
        'febre': False, 'rigidez_nuca': False, 'fotofobia': False, 'foco_infeccioso': False,
        'dissociativo': False,
        'deficit_focal': False, 'cefaleia_intensa': False,
        'pupilas_aniso': False, 'hipertensao_grave': False,
        'pupila_diametro': 'normais', 'reflexo_pupilar': True,
        'asterixis': False, 'rigidez_descer': False, 'babinski': False,
        'pa_sistolica': 120, 'fc': 80, 'fr': 16, 'temp': 36.8,
    }

def _run(n, d, e):
    r = interpretar_consciencia(d)
    cat = r.get('categoria','')
    ok = cat == e
    print(f'  {"OK" if ok else "XX"} [{n}] -> {cat}  (esp: {e})')
    if not ok: print(f'      {r.get("diagnostico","")}')
    return ok

CASOS = [
    ('hipoglicemia',      {**_base(), 'dm': True, 'glicemia_disponivel': True, 'glicemia': 42, 'glasgow_total': 10}, 'hipoglicemia'),
    ('hipoxia',           {**_base(), 'hipoxia': True, 'spo2': 85, 'glasgow_total': 11}, 'hipoxia_grave'),
    ('overdose_opioide',  {**_base(), 'intoxicacao_suspeita': True, 'intox_tipo': 'opioide', 'pupila_diametro': 'mioticas', 'glasgow_total': 8}, 'overdose_opioide'),
    ('pos_ictal',         {**_base(), 'epilepsia_previa': True, 'pos_ictal': True, 'glasgow_total': 12}, 'pos_ictal'),
    ('status_epilepticus',{**_base(), 'convulsao_obs': True, 'glasgow_total': 9}, 'status_epilepticus'),
    ('avc',               {**_base(), 'deficit_focal': True, 'onset': 'subito', 'glasgow_total': 13}, 'avc_sangramento'),
    ('cefaleia_trovao',   {**_base(), 'cefaleia_intensa': True, 'glasgow_total': 12}, 'avc_sangramento'),
    ('meningite',         {**_base(), 'febre': True, 'rigidez_nuca': True, 'glasgow_total': 11}, 'meningite_encefalite'),
    ('tce_intervalo',     {**_base(), 'trauma_cabeca': True, 'lucido_intervalo': True, 'glasgow_total': 10}, 'tce_hematoma'),
    ('intox_benzo',       {**_base(), 'intoxicacao_suspeita': True, 'intox_tipo': 'benzo', 'glasgow_total': 10}, 'intoxicacao_benzo'),
    ('intox_co',          {**_base(), 'intoxicacao_suspeita': True, 'intox_tipo': 'co', 'glasgow_total': 12}, 'intoxicacao_co'),
    ('intox_organofosforado', {**_base(), 'intoxicacao_suspeita': True, 'intox_tipo': 'organofosforado', 'glasgow_total': 9}, 'intoxicacao_organofosforado'),
    ('encefalopatia_hepatica', {**_base(), 'encefalopatia': True, 'asterixis': True, 'glasgow_total': 13}, 'encefalopatia_metabolica'),
    ('alcool_agudo',      {**_base(), 'alcool_halito': True, 'alcool_drogas': True, 'glasgow_total': 11}, 'intoxicacao_alcool'),
    ('dissociativo',      {**_base(), 'dissociativo': True, 'psiq_previa': True, 'glasgow_total': 14}, 'crise_dissociativa'),
]

CASOS += [
    # 16. Choque séptico — PA baixa + febre + foco
    ('choque_septico',
     {**_base(), 'pa_sistolica': 82, 'fc': 128, 'febre': True, 'foco_infeccioso': True,
      'glasgow_total': 13},
     'choque_hemodinamico'),

    # 17. Hipoglicemia em etilista — tiamina primeiro
    ('hipoglicemia_etilista',
     {**_base(), 'dm': True, 'alcool_drogas': True, 'alcool_halito': True,
      'glicemia_disponivel': True, 'glicemia': 38, 'glasgow_total': 9},
     'hipoglicemia'),
]


def main():
    print('\n'+'='*56)
    print('  SMOKE TESTS — ENGINE CONSCIÊNCIA')
    print('='*56)
    res = [_run(n,d,e) for n,d,e in CASOS]
    print(f'\n  Resultado: {sum(res)}/{len(res)} OK')
    print('='*56)
    return all(res)

if __name__ == '__main__':
    sys.exit(0 if main() else 1)
