# alertas.py — Interface pública central de alertas farmacológicos
# Qualquer módulo do SymptoPy importa daqui:
#
#   from apoio_clinico.medicamentos.alertas import gerar_alertas_farmacologicos
#
# Não importa se é MSK, clínico geral, crônico ou GO —
# a chamada é sempre a mesma. Este arquivo roteia para o módulo certo.

from apoio_clinico.medicamentos.analgesicos import (
    avaliar_analgesia,
    formatar_alertas,
)

# Futuros módulos entram aqui quando prontos:
# from apoio_clinico.medicamentos.antibioticos import avaliar_antibiotico
# from apoio_clinico.medicamentos.cardiovasculares import avaliar_cardiovascular
# from apoio_clinico.medicamentos.psiquiatricos import avaliar_psiquiatrico

# Mapeamento de classe para função avaliadora
_ROTEADOR = {
    'aine_oral':              avaliar_analgesia,
    'cox2_preferencial':      avaliar_analgesia,
    'cox2_seletivo':          avaliar_analgesia,
    'paracetamol':            avaliar_analgesia,
    'aine_topico':            avaliar_analgesia,
    'tramadol':               avaliar_analgesia,
    'duloxetina':             avaliar_analgesia,
    'gabapentina_pregabalina':avaliar_analgesia,
    'corticoide_injetavel':   avaliar_analgesia,
    # 'amoxicilina':          avaliar_antibiotico,   # quando pronto
    # 'metoprolol':           avaliar_cardiovascular, # quando pronto
}


def gerar_alertas_farmacologicos(medicamentos, comorbidades_str,
                                  idade, medicacoes_str='', sito_injecao=None):
    """
    Interface única para qualquer módulo do SymptoPy.

    Parâmetros:
        medicamentos     : lista de strings — chaves dos medicamentos sugeridos
                           ex: ['aine_oral', 'corticoide_injetavel']
        comorbidades_str : string livre do prontuário
                           ex: "HAS, DRC eGFR 45, DM2"
        idade            : int
        medicacoes_str   : string livre do prontuário
                           ex: "sertralina 50mg 1-0-0, losartana 50mg 1-0-1"
        sito_injecao     : str opcional — para dose de corticoide
                           ex: 'joelho_intraarticular', 'subacromia_ombro'

    Retorna:
        texto formatado com alertas prontos para o runner imprimir
    """
    # Agrupar medicamentos por função avaliadora
    grupos = {}
    nao_reconhecidos = []
    for med in medicamentos:
        fn = _ROTEADOR.get(med)
        if fn is None:
            nao_reconhecidos.append(med)
            continue
        if fn not in grupos:
            grupos[fn] = []
        grupos[fn].append(med)

    # Rodar cada grupo
    resultado_completo = {}
    for fn, meds in grupos.items():
        resultado = fn(
            medicamentos=meds,
            comorbidades_str=comorbidades_str,
            idade=idade,
            medicacoes_str=medicacoes_str,
            sito_injecao=sito_injecao,
        )
        resultado_completo.update(resultado)

    # Alertar sobre não reconhecidos
    for med in nao_reconhecidos:
        resultado_completo[med] = {
            'nome': med,
            'erro': f'Medicamento "{med}" ainda não cadastrado nos perfis.',
            'contraindicacoes': [], 'cautelas': [], 'preferencias': [],
            'sem_alerta': False, 'interacoes': [], 'dose_sitio': None, 'aftercare': [],
        }

    return formatar_alertas(resultado_completo)