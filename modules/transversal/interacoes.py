"""
Camada transversal de interações medicamentosas e ajuste de dose.

Uso:
    resultado = verificar_interacoes(resultado_engine, perfil)
    # resultado['alertas_seguranca'] agora inclui os avisos de interação

Não modifica prescrições — apenas acrescenta alertas.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Helpers de detecção de medicamento
# ---------------------------------------------------------------------------

_AINES = ('ibuprofeno', 'naproxeno', 'diclofenaco', 'piroxicam', 'meloxicam',
          'cetoprofeno', 'indometacina', 'nimesulida', 'tenoxicam', 'etoricoxibe',
          'celecoxibe')

_AAS_ANALGÉSICO = ('ácido acetilsalicílico', 'aas', 'aspirina')

_DOACS = ('apixabana', 'rivaroxabana', 'dabigatrana', 'edoxabana')

_FLUOROQUINOLONAS = ('ciprofloxacino', 'levofloxacino', 'moxifloxacino',
                     'norfloxacino', 'ofloxacino')

_BENZOS = ('diazepam', 'clonazepam', 'alprazolam', 'lorazepam', 'bromazepam',
           'midazolam', 'nitrazepam', 'flunitrazepam', 'clobazam', 'oxazepam')

_ANTI_HIST_SEDATIVOS = ('difenidramina', 'prometazina', 'hidroxizina',
                        'clorfeniramina', 'dexclorfeniramina')

_ANTIESPASMODICOS = ('escopolamina', 'oxibutinina', 'diciclomina', 'hioscina')


def _contem(med: str, termos: tuple) -> bool:
    return any(t in med for t in termos)


def _é_aine(med: str) -> bool:
    return _contem(med, _AINES)


# ---------------------------------------------------------------------------
# Checadores individuais
# ---------------------------------------------------------------------------

def _checar_drc(med: str, perfil: dict) -> list[str]:
    alertas = []
    egfr = perfil.get('egfr')
    if egfr is None:
        return alertas

    if 'metformina' in med:
        if egfr < 30:
            alertas.append(
                'INTERAÇÃO DRC — Metformina: SUSPENDER com eGFR < 30 mL/min '
                '(risco de acidose lática).'
            )
        elif egfr < 45:
            alertas.append(
                'INTERAÇÃO DRC — Metformina: cautela com eGFR 30–45 mL/min; '
                'reduzir dose e monitorar função renal.'
            )

    if _é_aine(med) and egfr < 60:
        alertas.append(
            f'INTERAÇÃO DRC — {med.title()}: CONTRAINDICADO com eGFR < 60 mL/min '
            '(piora da função renal, retenção hídrica e hiperpotassemia).'
        )

    if 'nitrofurantoína' in med and egfr < 45:
        alertas.append(
            'INTERAÇÃO DRC — Nitrofurantoína: INEFICAZ e TÓXICA com eGFR < 45 mL/min; '
            'usar alternativa (fosfomicina ou cefalexina).'
        )

    if 'colchicina' in med and egfr < 30:
        alertas.append(
            'INTERAÇÃO DRC — Colchicina: CONTRAINDICADA com eGFR < 30 mL/min '
            '(risco de miopatia e neuropatia graves).'
        )

    if 'gabapentina' in med:
        if egfr < 60:
            alertas.append(
                'INTERAÇÃO DRC — Gabapentina: ajuste de dose obrigatório com eGFR < 60 mL/min '
                '(consultar tabela de ajuste; risco de sedação e encefalopatia).'
            )

    if _contem(med, _DOACS) and egfr < 15:
        alertas.append(
            f'INTERAÇÃO DRC — {med.title()}: CONTRAINDICADO com eGFR < 15 mL/min '
            '(acúmulo com risco hemorrágico grave).'
        )

    return alertas


def _checar_anticoagulado(med: str, perfil: dict) -> list[str]:
    alertas = []
    if not perfil.get('anticoagulado'):
        return alertas

    tipo = (perfil.get('tipo_anticoagulante') or '').lower()
    é_warfarina = tipo == 'warfarina'
    é_doac = tipo == 'doac'

    if _é_aine(med):
        alertas.append(
            f'INTERAÇÃO ANTICOAGULANTE — {med.title()} + anticoagulante: risco hemorrágico '
            'GI grave (AINE + anticoagulação = combinação de alto risco; evitar ou usar IBP).'
        )

    if _contem(med, _AAS_ANALGÉSICO):
        alertas.append(
            'INTERAÇÃO ANTICOAGULANTE — AAS dose analgésica + anticoagulante: risco '
            'hemorrágico GI grave; se necessário AAS, usar apenas dose antiagregante (100 mg) '
            'com gastroproteção.'
        )

    if 'metronidazol' in med and é_warfarina:
        alertas.append(
            'INTERAÇÃO ANTICOAGULANTE — Metronidazol + warfarina: inibe CYP2C9, '
            'elevar INR significativamente; monitorar INR em 3–5 dias ou usar alternativo.'
        )

    if 'azitromicina' in med and é_warfarina:
        alertas.append(
            'INTERAÇÃO ANTICOAGULANTE — Azitromicina + warfarina: pode elevar INR '
            'moderadamente; monitorar INR ao término do curso.'
        )

    if 'fluconazol' in med and é_doac:
        alertas.append(
            'INTERAÇÃO ANTICOAGULANTE — Fluconazol + DOAC: inibe CYP3A4/P-gp, '
            'aumenta muito o nível plasmático do DOAC; considerar alternativo antifúngico '
            'ou suspender DOAC temporariamente sob orientação especializada.'
        )

    if 'claritromicina' in med and é_doac:
        alertas.append(
            'INTERAÇÃO ANTICOAGULANTE — Claritromicina + DOAC: inibidor potente de P-gp, '
            'VETO — substituir por azitromicina ou amoxicilina quando possível.'
        )

    return alertas


def _checar_serotonina(med: str, perfil: dict) -> list[str]:
    alertas = []
    isrs = perfil.get('isrs_em_uso', False)
    imao = perfil.get('imao_em_uso', False)

    if not (isrs or imao):
        return alertas

    if 'tramadol' in med and isrs:
        alertas.append(
            'INTERAÇÃO SEROTONINÉRGICA — Tramadol + ISRS: risco de síndrome '
            'serotoninérgica (agitação, hipertermia, clonus); preferir paracetamol '
            'ou opioide puro (codeína em dose baixa).'
        )

    if _contem(med, ('sumatriptano', 'zolmitriptano', 'rizatriptano', 'nartriptano',
                     'triptano', 'almotriptano', 'eletriptano', 'frovatriptano')) and isrs:
        alertas.append(
            'INTERAÇÃO SEROTONINÉRGICA — Triptano + ISRS: risco de síndrome '
            'serotoninérgica; usar com cautela e orientar paciente sobre sinais de alerta.'
        )

    if 'linezolida' in med and isrs:
        alertas.append(
            'INTERAÇÃO SEROTONINÉRGICA — Linezolida + ISRS: VETO ABSOLUTO — '
            'linezolida é inibidor de MAO; risco de síndrome serotoninérgica grave/fatal.'
        )

    if imao:
        serotoninérgicos = ('tramadol', 'sumatriptano', 'zolmitriptano', 'rizatriptano',
                            'triptano', 'fluoxetina', 'sertralina', 'escitalopram',
                            'paroxetina', 'venlafaxina', 'duloxetina', 'linezolida',
                            'amitriptilina', 'clomipramina', 'meperidina', 'fentanil')
        if _contem(med, serotoninérgicos):
            alertas.append(
                f'INTERAÇÃO SEROTONINÉRGICA — {med.title()} + IMAO: VETO ABSOLUTO — '
                'risco de síndrome serotoninérgica grave/fatal.'
            )

    return alertas


def _checar_qt(med: str, perfil: dict) -> list[str]:
    alertas = []
    qt_risco = perfil.get('qt_longo_conhecido', False) or perfil.get('antipsicótico_em_uso', False)

    if not qt_risco:
        return alertas

    if 'azitromicina' in med:
        alertas.append(
            'INTERAÇÃO QT — Azitromicina + QT longo/antipsicótico: risco de Torsades de '
            'Pointes; preferir amoxicilina ou doxiciclina quando possível.'
        )

    if _contem(med, _FLUOROQUINOLONAS):
        alertas.append(
            f'INTERAÇÃO QT — {med.title()} + QT longo/antipsicótico: fluoroquinolonas '
            'prolongam QT; risco de Torsades de Pointes — preferir beta-lactâmico.'
        )

    if 'ondansetrona' in med:
        alertas.append(
            'INTERAÇÃO QT — Ondansetrona + QT longo/antipsicótico: dose máxima 8 mg IV '
            'por dose (não 16–32 mg); monitorar ECG se necessário.'
        )

    return alertas


def _checar_hepatopatia(med: str, perfil: dict) -> list[str]:
    alertas = []
    if not perfil.get('hepatopatia'):
        return alertas

    if 'paracetamol' in med or 'acetaminofeno' in med:
        alertas.append(
            'INTERAÇÃO HEPATOPATIA — Paracetamol: dose máxima 2 g/dia (não 4 g) em '
            'hepatopatia crônica; evitar em insuficiência hepática grave (Child C).'
        )

    if _é_aine(med):
        alertas.append(
            f'INTERAÇÃO HEPATOPATIA — {med.title()}: CONTRAINDICADO em hepatopatia '
            '(risco de sangramento GI por coagulopatia + piora da função renal por síndrome '
            'hepatorrenal).'
        )

    if 'metronidazol' in med:
        alertas.append(
            'INTERAÇÃO HEPATOPATIA — Metronidazol: cautela — acúmulo por metabolismo '
            'hepático reduzido; reduzir dose ou prolongar intervalo.'
        )

    if _contem(med, ('atorvastatina', 'sinvastatina', 'rosuvastatina', 'lovastatina',
                     'pravastatina', 'fluvastatina', 'pitavastatina', 'estatina')):
        alertas.append(
            f'INTERAÇÃO HEPATOPATIA — {med.title()}: monitorar transaminases — estatinas '
            'são contraindicadas em doença hepática ativa; verificar se indicação se mantém.'
        )

    return alertas


def _checar_beers(med: str, perfil: dict) -> list[str]:
    alertas = []
    idade = perfil.get('idade')
    if not (idade and idade >= 65):
        return alertas

    if _contem(med, _BENZOS):
        alertas.append(
            f'BEERS — {med.title()}: benzodiazepínico em idoso ≥ 65 anos → risco aumentado '
            'de queda, fratura e delirium; evitar sempre que possível.'
        )

    if _contem(med, _ANTI_HIST_SEDATIVOS):
        alertas.append(
            f'BEERS — {med.title()}: anti-histamínico sedativo em idoso ≥ 65 anos → '
            'efeito anticolinérgico causa delirium, retenção urinária e quedas; evitar.'
        )

    if _é_aine(med):
        alertas.append(
            f'BEERS — {med.title()}: AINE em idoso ≥ 65 anos → risco aumentado de '
            'sangramento GI, insuficiência renal aguda e eventos cardiovasculares; '
            'preferir paracetamol.'
        )

    if _contem(med, _ANTIESPASMODICOS):
        alertas.append(
            f'BEERS — {med.title()}: anticolinérgico/antiespasmódico em idoso ≥ 65 anos → '
            'risco de delirium, boca seca, retenção urinária e constipação grave.'
        )

    if 'glibenclamida' in med:
        alertas.append(
            'BEERS — Glibenclamida: sulfonilureia de ação prolongada em idoso ≥ 65 anos → '
            'risco de hipoglicemia prolongada grave; preferir glipizida ou gliclazida.'
        )

    return alertas


# ---------------------------------------------------------------------------
# Função pública
# ---------------------------------------------------------------------------

def verificar_interacoes(resultado: dict, perfil: dict) -> dict:
    """
    Recebe resultado de qualquer engine + perfil do paciente.
    Acrescenta alertas em resultado['alertas_seguranca'].
    NÃO modifica prescrições — só alerta.
    Retorna resultado enriquecido.
    """
    alertas = list(resultado.get('alertas_seguranca', []))
    rxs = resultado.get('prescricoes_estruturadas', [])
    meds = [rx.get('medicamento', '').lower() for rx in rxs]

    for med in meds:
        alertas += _checar_drc(med, perfil)
        alertas += _checar_anticoagulado(med, perfil)
        alertas += _checar_serotonina(med, perfil)
        alertas += _checar_qt(med, perfil)
        alertas += _checar_hepatopatia(med, perfil)
        alertas += _checar_beers(med, perfil)

    resultado['alertas_seguranca'] = alertas
    return resultado
