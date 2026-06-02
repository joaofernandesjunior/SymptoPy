# regras_ottawa.py
# Camada compartilhada — Regras de Ottawa para indicação de radiografia
# Base: Open Evidence 2026 / Ottawa Rules (Stiell et al.)
# Cobre: joelho e tornozelo (as mais validadas na APS/UPA)

def ottawa_joelho(dados):
    """
    Regras de Ottawa para Joelho
    Indicação de radiografia após trauma agudo.
    Sensibilidade próxima de 100% para fratura clinicamente significativa.
    """
    criterios_positivos = []

    if dados.get('idade_acima_55'):
        criterios_positivos.append('idade >= 55 anos')
    if dados.get('sensibilidade_isolada_patela'):
        criterios_positivos.append('sensibilidade isolada na patela (sem outra dor óssea)')
    if dados.get('sensibilidade_cabeca_fibula'):
        criterios_positivos.append('sensibilidade na cabeça da fíbula')
    if dados.get('incapaz_flexao_90'):
        criterios_positivos.append('incapacidade de fletir o joelho a 90°')
    if dados.get('incapaz_suportar_peso'):
        criterios_positivos.append('incapacidade de suportar peso (4 passos) no local e na consulta')

    indicar_rx = len(criterios_positivos) > 0

    return {
        'regra': 'Ottawa Joelho',
        'criterios_positivos': criterios_positivos,
        'indicar_radiografia': indicar_rx,
        'acao': 'Solicitar Rx de joelho AP e perfil' if indicar_rx else 'Radiografia não indicada por critérios de Ottawa',
        'nota': 'Sensibilidade ~100% para fratura. Se nenhum critério: fratura improvável.'
    }


def ottawa_tornozelo(dados):
    """
    Regras de Ottawa para Tornozelo e Pé
    Divide em zona do tornozelo e zona do pé médio.
    """
    criterios_tornozelo = []
    criterios_pe = []

    # Zona do tornozelo
    if dados.get('dor_na_zona_maleolar') and dados.get('sensibilidade_posterior_maleolo_lateral'):
        criterios_tornozelo.append('sensibilidade nos 6cm posteriores do maléolo lateral')
    if dados.get('dor_na_zona_maleolar') and dados.get('sensibilidade_posterior_maleolo_medial'):
        criterios_tornozelo.append('sensibilidade nos 6cm posteriores do maléolo medial')
    if dados.get('incapaz_suportar_peso_tornozelo'):
        criterios_tornozelo.append('incapacidade de suportar peso (4 passos)')

    # Zona do pé médio
    if dados.get('dor_no_pe_medio') and dados.get('sensibilidade_base_5o_metatarso'):
        criterios_pe.append('sensibilidade na base do 5º metatarso')
    if dados.get('dor_no_pe_medio') and dados.get('sensibilidade_navicular'):
        criterios_pe.append('sensibilidade no osso navicular')
    if dados.get('incapaz_suportar_peso_pe'):
        criterios_pe.append('incapacidade de suportar peso (4 passos)')

    indicar_rx_tornozelo = len(criterios_tornozelo) > 0
    indicar_rx_pe = len(criterios_pe) > 0

    return {
        'regra': 'Ottawa Tornozelo e Pé',
        'criterios_tornozelo': criterios_tornozelo,
        'criterios_pe': criterios_pe,
        'indicar_rx_tornozelo': indicar_rx_tornozelo,
        'indicar_rx_pe': indicar_rx_pe,
        'acao_tornozelo': 'Solicitar Rx de tornozelo AP, perfil e mortise' if indicar_rx_tornozelo else 'Rx de tornozelo não indicado',
        'acao_pe': 'Solicitar Rx de pé AP e oblíquo' if indicar_rx_pe else 'Rx de pé não indicado',
        'nota': 'Sensibilidade ~96-99% para fratura clinicamente significativa.'
    }


if __name__ == '__main__':
    caso_joelho = {
        'idade_acima_55': True,
        'sensibilidade_isolada_patela': False,
        'sensibilidade_cabeca_fibula': False,
        'incapaz_flexao_90': True,
        'incapaz_suportar_peso': False
    }
    print(ottawa_joelho(caso_joelho))

    caso_tornozelo = {
        'dor_na_zona_maleolar': True,
        'sensibilidade_posterior_maleolo_lateral': True,
        'sensibilidade_posterior_maleolo_medial': False,
        'incapaz_suportar_peso_tornozelo': False,
        'dor_no_pe_medio': False,
        'sensibilidade_base_5o_metatarso': False,
        'sensibilidade_navicular': False,
        'incapaz_suportar_peso_pe': False
    }
    print(ottawa_tornozelo(caso_tornozelo))
