# tests/test_palpitacao.py
# Smoke tests — módulo Palpitação
# Executar: python tests/test_palpitacao.py

import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.raciocinio.palpitacao.engine_palpitacao import analisar_palpitacao


def test(nome, dados, esperado_cat, esperado_urgencia=None,
         contem=None, nao_contem=None, nao_prescricao=None):
    """
    contem/nao_contem: pesquisa em rx + conduta + raciocinio (texto todo).
    nao_prescricao: pesquisa SOMENTE nos campos 'medicamento' das prescricoes_estruturadas.
    """
    r = analisar_palpitacao(dados)
    cat = r.get('categoria', '')
    urg = r.get('urgencia', '')
    rx_txt   = str(r.get('prescricoes_estruturadas', ''))
    cond_txt = str(r.get('conduta', ''))
    rac_txt  = r.get('raciocinio', '')
    full_txt = (rx_txt + cond_txt + rac_txt).lower()

    # nomes de medicamentos prescritos (campo 'medicamento' de cada rx)
    meds_prescritos = [
        m.get('medicamento', '').lower()
        for m in r.get('prescricoes_estruturadas', [])
    ]

    ok = True
    erros = []
    if cat != esperado_cat:
        ok = False
        erros.append(f'  cat={cat!r} esperado={esperado_cat!r}')
    if esperado_urgencia and urg != esperado_urgencia:
        ok = False
        erros.append(f'  urgencia={urg!r} esperado={esperado_urgencia!r}')
    for c in (contem or []):
        if c.lower() not in full_txt:
            ok = False
            erros.append(f'  falta: {c!r}')
    for nc in (nao_contem or []):
        if nc.lower() in full_txt:
            ok = False
            erros.append(f'  nao deveria conter: {nc!r}')
    for np_ in (nao_prescricao or []):
        if any(np_.lower() in m for m in meds_prescritos):
            ok = False
            erros.append(f'  nao deveria estar prescrito: {np_!r}')

    status = 'OK  ' if ok else 'FAIL'
    print(f'[{status}] {nome}')
    for e in erros:
        print(e)
    return ok


resultados = []

# 01 — Instabilidade hemodinâmica → PS imediato / SAMU
resultados.append(test(
    '01_instabilidade_hemodinamica',
    {
        'instabilidade_hemodinamica': True, 'sincope': True, 'dispneia_grave': True,
        'ritmo_percebido': 'acelerado_irregular', 'ecg_ritmo': 'desconhecido',
    },
    'pal_instabilidade_hemodinamica', 'emergencia',
    contem=['SAMU', 'cardioversão'],
))

# 02 — WPW → NUNCA verapamil/digoxina
resultados.append(test(
    '02_wpw_contraind_verapamil',
    {
        'ecg_ritmo': 'wpw', 'ecg_wpw': True, 'wpw_suspeita': True,
        'instabilidade_hemodinamica': False, 'ritmo_percebido': 'acelerado_regular',
        'sincope': False, 'tv_suspeita': False, 'brugada_suspeito': False,
        'qt_longo_suspeito': False,
    },
    'pal_wpw', 'emergencia',
    contem=['Verapamil', 'Digoxina', 'ablação'],
))

# 03 — TV QRS largo → PS (nunca verapamil)
resultados.append(test(
    '03_tv_qrs_largo',
    {
        'ecg_ritmo': 'tsv_qrs_largo', 'ecg_tsv_largo': True, 'tv_suspeita': True,
        'instabilidade_hemodinamica': False, 'wpw_suspeita': False,
        'ritmo_percebido': 'acelerado_regular', 'sincope': False,
        'brugada_suspeito': False, 'qt_longo_suspeito': False,
    },
    'pal_tv_qrs_largo', 'emergencia',
    contem=['verapamil'],
))

# 04 — Brugada + síncope → PS/eletrofisiologia
resultados.append(test(
    '04_brugada_sincope',
    {
        'ecg_brugada': True, 'brugada_suspeito': True, 'sincope': True,
        'instabilidade_hemodinamica': False, 'wpw_suspeita': False, 'tv_suspeita': False,
        'ritmo_percebido': 'acelerado_regular', 'qt_longo_suspeito': False,
    },
    'pal_brugada_sincope', 'emergencia',
    contem=['DAI', 'Flecainida'],
))

# 05 — QT longo + síncope → Torsades / MgSO4
resultados.append(test(
    '05_qt_longo_torsades',
    {
        'ecg_qt_longo': True, 'qt_longo_suspeito': True, 'sincope': True,
        'instabilidade_hemodinamica': False, 'wpw_suspeita': False, 'tv_suspeita': False,
        'brugada_suspeito': False, 'ritmo_percebido': 'acelerado_irregular',
    },
    'pal_qt_longo_sincope', 'emergencia',
    contem=['Magnésio'],
))

# 06 — Flutter atrial → cardiologia urgente + ablação istmo
resultados.append(test(
    '06_flutter_atrial',
    {
        'ecg_ritmo': 'flutter', 'fa_suspeita': False, 'fa_conhecida': False,
        'instabilidade_hemodinamica': False, 'wpw_suspeita': False, 'tv_suspeita': False,
        'brugada_suspeito': False, 'sincope': False, 'qt_longo_suspeito': False,
        'ritmo_percebido': 'acelerado_regular', 'extrassistolia_suspeita': False,
        'tsv_suspeita': False,
    },
    'pal_flutter', 'urgente',
    contem=['ablação', 'istmo cavo-tricuspídeo'],
))

# 07 — FA nova elegível → Propafenona 300mg
resultados.append(test(
    '07_fa_nova_cardioversao_propafenona',
    {
        'fa_suspeita': True, 'fa_conhecida': False, 'cardiopatia_estrutural': False,
        'duracao_episodio': 'horas', 'ecg_bve': False,
        'instabilidade_hemodinamica': False, 'wpw_suspeita': False, 'tv_suspeita': False,
        'brugada_suspeito': False, 'sincope': False, 'qt_longo_suspeito': False,
        'ecg_ritmo': 'fa', 'extrassistolia_suspeita': False, 'tsv_suspeita': False,
        'cha2ds2_score': 1, 'anticoagulacao_indicada': False, 'sexo_feminino': False,
    },
    'pal_fa_nova_cardioversao', 'urgente',
    contem=['Propafenona', '300 mg'],
))

# 08 — FA nova + cardiopatia → Metoprolol + Apixabana 1ª linha (SEM Propafenona)
resultados.append(test(
    '08_fa_nova_controle_fc_cardiopatia',
    {
        'fa_suspeita': True, 'fa_conhecida': False, 'cardiopatia_estrutural': True,
        'duracao_episodio': 'horas', 'ecg_bve': False,
        'instabilidade_hemodinamica': False, 'wpw_suspeita': False, 'tv_suspeita': False,
        'brugada_suspeito': False, 'sincope': False, 'qt_longo_suspeito': False,
        'ecg_ritmo': 'fa', 'extrassistolia_suspeita': False, 'tsv_suspeita': False,
        'cha2ds2_score': 3, 'anticoagulacao_indicada': True, 'sexo_feminino': False,
    },
    'pal_fa_nova_controle_fc', 'urgente',
    contem=['Metoprolol', 'Apixabana'],   # Apixabana agora 1ª linha (evidência real-world)
    nao_prescricao=['propafenona'],        # NÃO prescrita (só mencionada como contraindicação)
))

# 09 — FA crônica → Metoprolol + Apixabana 1ª linha + Rivaroxabana alternativo
resultados.append(test(
    '09_fa_cronica',
    {
        'fa_suspeita': False, 'fa_conhecida': True, 'cardiopatia_estrutural': False,
        'instabilidade_hemodinamica': False, 'wpw_suspeita': False, 'tv_suspeita': False,
        'brugada_suspeito': False, 'sincope': False, 'qt_longo_suspeito': False,
        'ecg_ritmo': 'fa', 'extrassistolia_suspeita': False, 'tsv_suspeita': False,
        'cha2ds2_score': 2, 'anticoagulacao_indicada': True, 'sexo_feminino': False,
    },
    'pal_fa_cronica', 'aps',
    contem=['Metoprolol', 'Apixabana', 'Rivaroxabana'],  # ambos presentes — 1ª e alternativo
))

# 10 — TSV paroxística → Valsalva + Metoprolol + menção adenosina
resultados.append(test(
    '10_tsv_valsalva_metoprolol',
    {
        'tsv_suspeita': True, 'ecg_ritmo': 'tsv',
        'ritmo_percebido': 'acelerado_regular', 'inicio_subito': True, 'termino_subito': True,
        'instabilidade_hemodinamica': False, 'wpw_suspeita': False, 'tv_suspeita': False,
        'brugada_suspeito': False, 'sincope': False, 'qt_longo_suspeito': False,
        'fa_suspeita': False, 'fa_conhecida': False, 'extrassistolia_suspeita': False,
    },
    'pal_tsv_paroxistica', 'aps',
    contem=['Valsalva', 'Metoprolol', 'adenosina'],
))

# 11 — Extrassistolia benigna → Holter + tranquilizar
resultados.append(test(
    '11_extrassistolia_benigna',
    {
        'extrassistolia_suspeita': True, 'ecg_ritmo': 'extrassist',
        'ritmo_percebido': 'batida_extra', 'cardiopatia_estrutural': False,
        'instabilidade_hemodinamica': False, 'wpw_suspeita': False, 'tv_suspeita': False,
        'brugada_suspeito': False, 'sincope': False, 'qt_longo_suspeito': False,
        'fa_suspeita': False, 'fa_conhecida': False, 'tsv_suspeita': False,
        'causa_secundaria_suspeita': False,
    },
    'pal_extrassistolia', 'eletivo',
    contem=['Holter', 'benigna'],
))

# 12 — Hipertireoidismo → TSH + Propranolol
resultados.append(test(
    '12_hipertireoidismo_tsh_propranolol',
    {
        'sintomas_tireoide': True, 'causa_secundaria_suspeita': True,
        'uso_hormonio_tireoidiano': False,
        'instabilidade_hemodinamica': False, 'wpw_suspeita': False, 'tv_suspeita': False,
        'brugada_suspeito': False, 'sincope': False, 'qt_longo_suspeito': False,
        'fa_suspeita': False, 'fa_conhecida': False, 'extrassistolia_suspeita': False,
        'tsv_suspeita': False,
    },
    'pal_hipertireoidismo', 'aps',
    contem=['TSH', 'Propranolol'],
))

# 13 — Pânico/ansiedade → ISRS (Sertralina) + TCC
resultados.append(test(
    '13_panico_isrs_tcc',
    {
        'sintomas_ansiedade': True, 'gatilho_estresse': True, 'causa_secundaria_suspeita': True,
        'sintomas_tireoide': False, 'uso_cocaina_estimulante': False,
        'uso_simpaticomimatico': False, 'sintomas_anemia': False,
        'instabilidade_hemodinamica': False, 'wpw_suspeita': False, 'tv_suspeita': False,
        'brugada_suspeito': False, 'sincope': False, 'qt_longo_suspeito': False,
        'fa_suspeita': False, 'fa_conhecida': False, 'extrassistolia_suspeita': False,
        'tsv_suspeita': False,
    },
    'pal_ansiedade_panico', 'aps',
    contem=['Sertralina', 'TCC'],
))

# 14 — Cocaína → ECG obrigatório + risco vasoespasmo
resultados.append(test(
    '14_cocaina_ecg_espasmo',
    {
        'uso_cocaina_estimulante': True, 'causa_secundaria_suspeita': True,
        'sintomas_tireoide': False,
        'instabilidade_hemodinamica': False, 'wpw_suspeita': False, 'tv_suspeita': False,
        'brugada_suspeito': False, 'sincope': False, 'qt_longo_suspeito': False,
        'fa_suspeita': False, 'fa_conhecida': False, 'extrassistolia_suspeita': False,
        'tsv_suspeita': False,
    },
    'pal_farmaco_estimulante', 'aps',
    contem=['cocaína', 'ECG'],
))

# 15 — Inespecífico → Holter 24h eletivo
resultados.append(test(
    '15_inespecifico_holter',
    {
        'instabilidade_hemodinamica': False, 'wpw_suspeita': False, 'tv_suspeita': False,
        'brugada_suspeito': False, 'sincope': False, 'qt_longo_suspeito': False,
        'fa_suspeita': False, 'fa_conhecida': False, 'tsv_suspeita': False,
        'extrassistolia_suspeita': False, 'causa_secundaria_suspeita': False,
        'ritmo_percebido': 'indeterminado', 'ecg_ritmo': 'normal',
    },
    'pal_inespecifico', 'eletivo',
    contem=['Holter'],
))

# 16 — TRAVA CRÍTICA: Propafenona NUNCA em cardiopatia estrutural
resultados.append(test(
    '16_trava_propafenona_contraindicada_cardiopatia',
    {
        'fa_suspeita': True, 'fa_conhecida': False, 'cardiopatia_estrutural': True,
        'duracao_episodio': 'minutos', 'ecg_bve': False,
        'instabilidade_hemodinamica': False, 'wpw_suspeita': False, 'tv_suspeita': False,
        'brugada_suspeito': False, 'sincope': False, 'qt_longo_suspeito': False,
        'ecg_ritmo': 'fa', 'extrassistolia_suspeita': False, 'tsv_suspeita': False,
        'cha2ds2_score': 3, 'anticoagulacao_indicada': True, 'sexo_feminino': False,
    },
    'pal_fa_nova_controle_fc',
    nao_prescricao=['propafenona'],  # NÃO prescrita quando há cardiopatia estrutural
))

total = len(resultados)
passou = sum(resultados)
print(f'\n{"=" * 50}')
print(f'{passou}/{total} testes passaram')
if passou < total:
    sys.exit(1)
