# modules/sintomas/diarreia/subjetivo.py
# Anamnese — Diarreia no Adulto (PA / APS)
#
# Blocos:
#   0. Caracterização (duração, frequência, caráter das fezes, febre)
#   1. Imunossupressão (filtro de segurança — expande espectro diagnóstico)
#   2. Red flags / Sepse (hipotensão, torpor, peritonite)
#   3. Desidratação clínica (sem objetivo.py — baseada em sintomas)
#   4. Contexto epidemiológico (ATB, internação, viagem, surto alimentar)
#   [AGUDA ≤14d] 5. Gatilhos específicos (lactose, AINEs, metformina)
#   [CRÔNICA >14d] 6. Alarmes orgânicos + calprotectina + medicamentos
#
# Rodar da raiz: python -m modules.sintomas.diarreia.subjetivo

import json
import os
import sys
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from utils.perguntas import sn


# =============================================================================
# AUXILIARES
# =============================================================================

def _bloco(titulo):
    print(f'\n{"─"*54}')
    print(f'  {titulo}')
    print(f'{"─"*54}')


def _perg_int(prompt, minimo=0, maximo=9999):
    while True:
        try:
            val = int(input(prompt).strip())
            if minimo <= val <= maximo:
                return val
            print(f'  Digite um valor entre {minimo} e {maximo}.')
        except ValueError:
            print('  Digite um número inteiro.')


def _perg_float(prompt):
    while True:
        try:
            return float(input(prompt).strip().replace(',', '.'))
        except ValueError:
            print('  Digite um número (ex: 3.5).')


def _perg_texto(prompt):
    return input(prompt).strip()


# =============================================================================
# BLOCO 0 — CARACTERIZAÇÃO
# =============================================================================

def _bloco_caracterizacao(dados):
    _bloco('BLOCO 0 — Caracterização da Diarreia')
    print('  Diarreia = ≥ 3 evacuações amolecidas ou líquidas em 24 horas.\n')

    dados['duracao_dias']       = _perg_int('  Duração (em dias): ', 0, 3650)
    dados['evacuacoes_por_dia'] = _perg_int('  Número de evacuações por dia (média): ', 1, 50)

    dados['fezes_aquosas']        = sn('  Fezes aquosas (água com cor)? ')
    dados['fezes_sanguinolentas'] = sn('  Sangue visível nas fezes (hematoquesia)? ')
    dados['fezes_mucosas']        = sn('  Muco visível nas fezes? ')
    dados['fezes_gordurosas']     = sn('  Fezes gordurosas/oleosas (flutuam, mancham o vaso)? ')

    dados['febre']      = sn('  Febre? ')
    dados['febre_38_5'] = sn('  Febre ≥ 38.5°C (termômetro ou sensação clara)? ') if dados['febre'] else False

    dados['nausea_vomito'] = sn('  Náusea ou vômito? ')
    if dados['nausea_vomito']:
        dados['vomito_incoercivel'] = sn('  Vômito incoercível (não consegue manter líquidos)? ')
    else:
        dados['vomito_incoercivel'] = False

    dados['dor_abdominal'] = sn('  Dor abdominal? ')
    if dados['dor_abdominal']:
        dados['dor_abdominal_intensa'] = sn('  Dor intensa (impede atividades normais)? ')
        dados['dor_melhora_evacuacao'] = sn('  Dor melhora após evacuar? ')
        dados['dor_piora_estresse']    = sn('  Dor piora com estresse emocional? ')
    else:
        dados['dor_abdominal_intensa'] = False
        dados['dor_melhora_evacuacao'] = False
        dados['dor_piora_estresse']    = False

    dados['tenesmo'] = sn('  Tenesmo (urgência fecal, sensação de esvaziamento incompleto)? ')

    # Alertas imediatos ao clínico
    if dados['fezes_sanguinolentas'] and not dados['febre_38_5']:
        print('\n  ATENÇÃO: sangue sem febre — suspeita de STEC (E. coli O157).')
        print('  Não usar ATB nem antidiarreicos até resultado de microbiologia.')
    if dados['fezes_sanguinolentas'] and dados['febre_38_5']:
        print('\n  ATENÇÃO: disenteria — investigar Shigella / Campylobacter / Salmonella.')


# =============================================================================
# BLOCO 1 — IMUNOSSUPRESSÃO
# =============================================================================

def _bloco_imunossupressao(dados):
    _bloco('BLOCO 1 — Filtro de Imunossupressão')
    print('  Imunossupressão expande o espectro para patógenos oportunistas.\n')

    dados['hiv_diagnosticado'] = sn('  HIV diagnosticado? ')
    if dados['hiv_diagnosticado']:
        dados['hiv_em_tarv']   = sn('  Em TARV (antirretroviral)? ')
        dados['cd4_conhecido'] = sn('  CD4 recente disponível? ')
        dados['cd4_valor']     = _perg_int('  CD4 (células/mm³): ', 0, 2000) if dados['cd4_conhecido'] else None
    else:
        dados['hiv_em_tarv']   = False
        dados['cd4_conhecido'] = False
        dados['cd4_valor']     = None

    dados['transplante_quimio_biologico'] = sn(
        '  Transplante de órgão, quimioterapia ativa ou biológico imunossupressor? '
    )
    dados['corticoide_cronico'] = sn('  Uso crônico de corticosteroide (> 3 meses)? ')

    dados['imunossuprimido'] = any([
        dados['hiv_diagnosticado'],
        dados['transplante_quimio_biologico'],
        dados['corticoide_cronico'],
    ])

    if dados['imunossuprimido']:
        print('\n  ALERTA: espectro diagnóstico ampliado — oportunistas possíveis.')


# =============================================================================
# BLOCO 2 — RED FLAGS / SEPSE
# =============================================================================

def _bloco_red_flags(dados):
    _bloco('BLOCO 2 — Red Flags / Sepse')
    print('  Qualquer sinal de sepse indica encaminhamento imediato ao PA/UE.\n')

    dados['hipotensao_conhecida']     = sn('  Hipotensão (PA baixa, desmaio, tontura grave ao levantar)? ')
    dados['alteracao_consciencia']    = sn('  Torpor, confusão mental ou rebaixamento de consciência? ')
    dados['extremidades_frias']       = sn('  Extremidades frias ou cianose? ')
    dados['dor_abdominal_peritoneal'] = sn('  Dor abdominal com rigidez (barriga dura à palpação)? ')

    dados['sinais_sepse'] = any([
        dados['hipotensao_conhecida'],
        dados['alteracao_consciencia'],
        dados['extremidades_frias'],
        dados['dor_abdominal_peritoneal'],
    ])

    if dados['sinais_sepse']:
        print('\n  ALERTA IMEDIATO: sinais de sepse — encaminhar PA/UE agora.')


# =============================================================================
# BLOCO 3 — DESIDRATAÇÃO CLÍNICA
# =============================================================================

def _bloco_desidratacao(dados):
    _bloco('BLOCO 3 — Desidratação Clínica')
    print('  Avaliação baseada em sintomas — sem necessidade de pesar.\n')

    dados['oliguria']          = sn('  Oligúria — urina escura ou menos de 3× ao dia? ')
    dados['tontura_ortostase'] = sn('  Tontura ou escurecimento visual ao levantar? ')
    dados['sede_intensa']      = sn('  Sede intensa e persistente? ')
    dados['mucosas_ressecadas']= sn('  Boca seca, lábios rachados? ')
    dados['olhos_fundos']      = sn('  Olhos fundos (auto-referido ou observado)? ')

    # Classificação clínica
    grave    = dados['hipotensao_conhecida'] or dados['alteracao_consciencia'] or dados['olhos_fundos']
    moderada = dados['oliguria'] or dados['tontura_ortostase'] or (
        dados['sede_intensa'] and dados['mucosas_ressecadas']
    )
    leve     = dados['sede_intensa'] or dados['mucosas_ressecadas']

    if grave:
        dados['desidratacao_grau'] = 'grave'
        print('\n  Desidratação GRAVE — IV obrigatório. Encaminhar PA/UE imediatamente.')
    elif moderada:
        dados['desidratacao_grau'] = 'moderada'
        print('\n  Desidratação MODERADA — SRO 100 mL/kg em 4h; reavaliação em 4h.')
    elif leve:
        dados['desidratacao_grau'] = 'leve'
        print('\n  Desidratação LEVE — SRO 50 mL/kg em 4h.')
    else:
        dados['desidratacao_grau'] = 'sem'
        print('\n  Sem desidratação significativa — SRO de manutenção (10 mL/kg/evacuação).')


# =============================================================================
# BLOCO 4 — CONTEXTO EPIDEMIOLÓGICO
# =============================================================================

def _bloco_contexto(dados):
    _bloco('BLOCO 4 — Contexto Epidemiológico')

    dados['atb_recente_3m']     = sn('  Antibiótico nos últimos 3 meses? ')
    dados['qual_atb_recente']   = _perg_texto('  Qual ATB? (Enter para pular) ') if dados['atb_recente_3m'] else ''
    dados['internacao_recente_3m'] = sn('  Internação ou procedimento hospitalar nos últimos 3 meses? ')

    dados['viagem_recente'] = sn('  Viagem internacional nos últimos 30 dias? ')
    if dados['viagem_recente']:
        dados['destino_viagem'] = _perg_texto('  Destino (país / região): ')
        destino_lower           = dados['destino_viagem'].lower()
        dados['viagem_asia']    = any(
            p in destino_lower for p in [
                'india', 'tailandia', 'thai', 'asia', 'vietnam', 'viet',
                'cambodja', 'cambodia', 'bangladesh', 'paquistao', 'nepal',
                'myanmar', 'laos', 'sri lanka',
            ]
        )
    else:
        dados['destino_viagem'] = ''
        dados['viagem_asia']    = False

    dados['surto_alimentar'] = sn('  Pelo menos mais 1 pessoa doente após a mesma refeição? ')
    if dados['surto_alimentar']:
        dados['alimento_suspeito'] = _perg_texto('  Alimento suspeito (frango, frutos do mar, maionese...): ')
        dados['incubacao_horas']   = _perg_int('  Horas entre a refeição e início da diarreia: ', 0, 120)
    else:
        dados['alimento_suspeito'] = ''
        dados['incubacao_horas']   = 0

    dados['contato_caso_diarreia'] = sn('  Contato próximo com outra pessoa com diarreia? ')


# =============================================================================
# BLOCO 5 — ESPECÍFICO AGUDA (≤ 14 dias)
# =============================================================================

def _bloco_especifico_aguda(dados):
    _bloco('BLOCO 5 — Investigação Aguda Específica')
    print('  Gatilhos que modificam a conduta em diarreia de início recente.\n')

    dados['piora_com_lacteos']    = sn('  Piora após laticínios (leite, queijo, iogurte)? ')
    dados['uso_aine_recente']     = sn('  Anti-inflamatório recente (ibuprofeno, diclofenaco, AAS)? ')
    dados['metformina_dose_alta'] = sn('  Metformina em dose ≥ 2 g/dia recentemente iniciada ou aumentada? ')


# =============================================================================
# BLOCO 6 — ESPECÍFICO CRÔNICA / PERSISTENTE (> 14 dias)
# =============================================================================

def _bloco_especifico_cronica(dados):
    _bloco('BLOCO 6 — Investigação Crônica / Persistente')
    print('  Alarmes para doença orgânica grave e investigação dirigida.\n')

    # Alarmes oncológicos e inflamatórios
    dados['perda_peso_involuntaria'] = sn('  Perda de peso involuntária? ')
    dados['perda_peso_kg']           = _perg_float('  Quantos kg (aproximado): ') if dados['perda_peso_involuntaria'] else 0.0
    dados['anemia_sintomas']         = sn('  Palidez, fraqueza intensa ou anemia confirmada? ')
    dados['hematochezia_cronica']    = sn('  Sangue crônico ou recorrente nas fezes (semanas/meses)? ')
    dados['hf_ccr_primeiro_grau']    = sn('  Familiar de 1º grau com câncer colorretal ou DII? ')
    dados['nocturna']                = sn('  Diarreia noturna (acorda à noite para evacuar)? ')

    # Padrão funcional (SII)
    dados['piora_com_gluten']  = sn('  Piora com glúten (pão, macarrão, trigo)? ')
    dados['piora_estresse']    = dados.get('dor_piora_estresse', False) or sn(
        '  Diarreia piora claramente com estresse emocional? '
    )

    # Medicamentos
    dados['medicamentos_suspeitos_diarreia'] = sn(
        '  Medicamentos que causam diarreia: metformina, IPP, laxativo, colchicina, ATB crônico? '
    )
    dados['quais_medicamentos_suspeitos'] = (
        _perg_texto('  Quais medicamentos? ') if dados['medicamentos_suspeitos_diarreia'] else ''
    )

    # Calprotectina fecal
    dados['calprotectina_disponivel'] = sn('  Resultado de calprotectina fecal disponível? ')
    if dados['calprotectina_disponivel']:
        dados['calprotectina_valor'] = _perg_float('  Valor da calprotectina (mcg/g): ')
    else:
        dados['calprotectina_valor'] = None

    # Antecedentes digestivos
    dados['sii_diagnosticada']        = sn('  Síndrome do Intestino Irritável (SII) já diagnosticada? ')
    dados['dii_diagnosticada']        = sn('  Doença Inflamatória Intestinal (Crohn/RCU) conhecida? ')
    dados['doenca_celiaca_conhecida'] = sn('  Doença celíaca já diagnosticada? ')
    dados['cirurgia_abdominal_previa']= sn('  Cirurgia abdominal prévia (gastrectomia, colectomia)? ')


# =============================================================================
# SALVAR
# =============================================================================

def _salvar(dados, pasta='dados_pacientes'):
    os.makedirs(pasta, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome = os.path.join(pasta, f'diarreia_subjetivo_{timestamp}.json')
    with open(nome, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f'\n  Dicionário salvo em: {nome}')
    return nome


# =============================================================================
# MAIN
# =============================================================================

def coletar_subjetivo_diarreia(dados_preenchidos=None):
    print('\n' + '=' * 54)
    print('  SYMPTOPY — Anamnese: Diarreia no Adulto')
    print('=' * 54)
    print('  Responda s (sim) ou n (não) para cada pergunta.\n')

    dados = dados_preenchidos.copy() if dados_preenchidos else {}

    _bloco_caracterizacao(dados)
    _bloco_imunossupressao(dados)
    _bloco_red_flags(dados)
    _bloco_desidratacao(dados)
    _bloco_contexto(dados)

    duracao = dados.get('duracao_dias', 0)
    if duracao <= 14:
        _bloco_especifico_aguda(dados)
    else:
        _bloco_especifico_cronica(dados)

    arquivo = _salvar(dados)
    print('\n  Próximo: engine_diarreia.py → raciocínio clínico\n')
    return dados, arquivo


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    coletar_subjetivo_diarreia()
