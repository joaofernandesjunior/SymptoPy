# tests/test_interacoes.py
# Smoke tests — camada transversal de interações medicamentosas
# Rodar: python tests/test_interacoes.py

import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.transversal.interacoes import verificar_interacoes
from modules.transversal.perfil_paciente import PERFIL_VAZIO


def _resultado(meds: list[str]) -> dict:
    """Monta resultado mínimo com lista de prescrições."""
    return {
        'alertas_seguranca': [],
        'prescricoes_estruturadas': [
            {'medicamento': m} for m in meds
        ],
    }


def _tem_alerta(resultado: dict, *termos: str) -> bool:
    alertas = resultado.get('alertas_seguranca', [])
    return any(
        all(t.lower() in a.lower() for t in termos)
        for a in alertas
    )


def _run(nome: str, passou: bool) -> bool:
    status = 'OK  ' if passou else 'FAIL'
    print(f'[{status}] {nome}')
    return passou


CASOS = []


def _testar():
    resultados = []

    # 1. Metformina + eGFR 25 → alerta DRC (suspender)
    perfil = {**PERFIL_VAZIO, 'egfr': 25}
    r = verificar_interacoes(_resultado(['Metformina 500 mg']), perfil)
    resultados.append(_run(
        'DRC: metformina + eGFR 25 → alerta suspender',
        _tem_alerta(r, 'metformina', 'suspender')
    ))

    # 1b. Metformina + eGFR 38 → alerta cautela
    perfil = {**PERFIL_VAZIO, 'egfr': 38}
    r = verificar_interacoes(_resultado(['Metformina 500 mg']), perfil)
    resultados.append(_run(
        'DRC: metformina + eGFR 38 → alerta cautela',
        _tem_alerta(r, 'metformina', 'cautela')
    ))

    # 2. Ibuprofeno + warfarina → alerta hemorrágico
    perfil = {**PERFIL_VAZIO, 'anticoagulado': True, 'tipo_anticoagulante': 'warfarina'}
    r = verificar_interacoes(_resultado(['Ibuprofeno 600 mg']), perfil)
    resultados.append(_run(
        'Anticoagulante: ibuprofeno + warfarina → risco hemorrágico GI',
        _tem_alerta(r, 'ibuprofeno', 'hemorrágico')
    ))

    # 3. Tramadol + ISRS em uso → alerta serotoninérgico
    perfil = {**PERFIL_VAZIO, 'isrs_em_uso': True}
    r = verificar_interacoes(_resultado(['Tramadol 50 mg']), perfil)
    resultados.append(_run(
        'Serotonina: tramadol + ISRS → síndrome serotoninérgica',
        _tem_alerta(r, 'tramadol', 'seroto')
    ))

    # 4. Azitromicina + QT longo → alerta Torsades
    perfil = {**PERFIL_VAZIO, 'qt_longo_conhecido': True}
    r = verificar_interacoes(_resultado(['Azitromicina 500 mg']), perfil)
    resultados.append(_run(
        'QT: azitromicina + QT longo → risco Torsades',
        _tem_alerta(r, 'azitromicina', 'torsades')
    ))

    # 5. Benzodiazepínico + 72 anos → alerta Beers
    perfil = {**PERFIL_VAZIO, 'idade': 72}
    r = verificar_interacoes(_resultado(['Diazepam 5 mg']), perfil)
    resultados.append(_run(
        'Beers: diazepam + 72 anos → risco queda/fratura',
        _tem_alerta(r, 'diazepam', 'beers')
    ))

    # 6. Paracetamol + hepatopatia → dose máxima 2 g
    perfil = {**PERFIL_VAZIO, 'hepatopatia': True}
    r = verificar_interacoes(_resultado(['Paracetamol 750 mg']), perfil)
    resultados.append(_run(
        'Hepatopatia: paracetamol → dose máxima 2 g/dia',
        _tem_alerta(r, 'paracetamol', '2 g')
    ))

    # 7. Perfil vazio → zero alertas (smoke test de regressão)
    perfil = {**PERFIL_VAZIO}
    r = verificar_interacoes(_resultado(['Amoxicilina 500 mg', 'Paracetamol 500 mg']), perfil)
    sem_alertas = len(r.get('alertas_seguranca', [])) == 0
    resultados.append(_run(
        'Regressão: perfil vazio → zero alertas',
        sem_alertas
    ))

    # --- Casos adicionais de cobertura ---

    # 8. Nitrofurantoína + eGFR 40 → ineficaz/tóxica
    perfil = {**PERFIL_VAZIO, 'egfr': 40}
    r = verificar_interacoes(_resultado(['Nitrofurantoína 100 mg']), perfil)
    resultados.append(_run(
        'DRC: nitrofurantoína + eGFR 40 → ineficaz',
        _tem_alerta(r, 'nitrofurantoína', 'ineficaz')
    ))

    # 9. Colchicina + eGFR 20 → contraindicada
    perfil = {**PERFIL_VAZIO, 'egfr': 20}
    r = verificar_interacoes(_resultado(['Colchicina 0,5 mg']), perfil)
    resultados.append(_run(
        'DRC: colchicina + eGFR 20 → contraindicada',
        _tem_alerta(r, 'colchicina', 'contraindicada')
    ))

    # 10. Metronidazol + warfarina → INR sobe
    perfil = {**PERFIL_VAZIO, 'anticoagulado': True, 'tipo_anticoagulante': 'warfarina'}
    r = verificar_interacoes(_resultado(['Metronidazol 400 mg']), perfil)
    resultados.append(_run(
        'Anticoagulante: metronidazol + warfarina → INR',
        _tem_alerta(r, 'metronidazol', 'inr')
    ))

    # 11. Claritromicina + DOAC → VETO
    perfil = {**PERFIL_VAZIO, 'anticoagulado': True, 'tipo_anticoagulante': 'doac'}
    r = verificar_interacoes(_resultado(['Claritromicina 500 mg']), perfil)
    resultados.append(_run(
        'Anticoagulante: claritromicina + DOAC → VETO',
        _tem_alerta(r, 'claritromicina', 'veto')
    ))

    # 12. Linezolida + ISRS → VETO absoluto
    perfil = {**PERFIL_VAZIO, 'isrs_em_uso': True}
    r = verificar_interacoes(_resultado(['Linezolida 600 mg']), perfil)
    resultados.append(_run(
        'Serotonina: linezolida + ISRS → VETO absoluto',
        _tem_alerta(r, 'linezolida', 'veto')
    ))

    # 13. Levofloxacino + antipsicótico em uso → QT
    perfil = {**PERFIL_VAZIO, 'antipsicótico_em_uso': True}
    r = verificar_interacoes(_resultado(['Levofloxacino 500 mg']), perfil)
    resultados.append(_run(
        'QT: levofloxacino + antipsicótico → Torsades',
        _tem_alerta(r, 'levofloxacino', 'torsades')
    ))

    # 14. AINE em hepatopatia → contraindicado
    perfil = {**PERFIL_VAZIO, 'hepatopatia': True}
    r = verificar_interacoes(_resultado(['Naproxeno 500 mg']), perfil)
    resultados.append(_run(
        'Hepatopatia: naproxeno → contraindicado',
        _tem_alerta(r, 'naproxeno', 'contraindicado')
    ))

    # 15. Prometazina + 68 anos → Beers delirium
    perfil = {**PERFIL_VAZIO, 'idade': 68}
    r = verificar_interacoes(_resultado(['Prometazina 25 mg']), perfil)
    resultados.append(_run(
        'Beers: prometazina + 68 anos → delirium',
        _tem_alerta(r, 'prometazina', 'delirium')
    ))

    # 16. Alertas pré-existentes são preservados
    perfil = {**PERFIL_VAZIO, 'egfr': 20}
    resultado_base = {
        'alertas_seguranca': ['Alerta pré-existente do engine'],
        'prescricoes_estruturadas': [{'medicamento': 'Metformina 500 mg'}],
    }
    r = verificar_interacoes(resultado_base, perfil)
    preservou = 'Alerta pré-existente do engine' in r.get('alertas_seguranca', [])
    resultados.append(_run(
        'Regressão: alertas pré-existentes são preservados',
        preservou
    ))

    return resultados


if __name__ == '__main__':
    print('=' * 60)
    print('INTERAÇÕES MEDICAMENTOSAS — testes de regressão')
    print('=' * 60)

    resultados = _testar()
    passou = sum(resultados)
    total = len(resultados)

    print()
    print('=' * 60)
    print(f'{passou}/{total} testes passaram')
    if passou < total:
        sys.exit(1)
