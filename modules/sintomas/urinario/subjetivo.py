# modules/sintomas/urinario/subjetivo.py
# Anamnese dirigida — Queixas Urinárias (Disúria + Hematúria) — Adulto
#
# Fluxo de perguntas:
#   BLOCO 0 — Triagem demográfica  (sexo · idade · gestante · tabagismo)
#             ↳ porta todos os blocos seguintes
#   BLOCO 1 — Red flags / emergência  (separar PA/PS antes de qualquer raciocínio)
#   BLOCO 2 — Queixa principal  (disúria | hematúria | ambos)
#   BLOCO 3 — Sintomas urinários locais
#   BLOCO 4 — Sintomas sistêmicos  (febre · calafrio · dor lombar → pielonefrite)
#   BLOCO 5F — Sintomas genitais FEMININOS  (corrimento · prurido · lesão · dispareunia)
#   BLOCO 5M — Sintomas genitais / prostáticos MASCULINOS  (descarga · hesitância · perineal)
#   BLOCO 6 — Risco IST  (ambos os sexos se sintomas genitais)
#   BLOCO 7 — Fatores de risco / complicadores  (DM · imunossupressão · cateter · ATB recente)
#   BLOCO 8 — Caracterização da hematúria  (só se hematúria reportada)
#   BLOCO 9 — EAS  (se resultado disponível no momento)
#
# Convenções de código:
#   sn(prompt)          → bool  (s/n)
#   _int(prompt)        → int
#   _escolha(prompt, opcoes) → str
#   _alerta(msg)        → imprime aviso em destaque

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
    print(f'\n{"─" * 56}')
    print(f'  {titulo}')
    print(f'{"─" * 56}')


def _alerta(msg):
    print(f'\n  ⚠️  {msg}')


def _int(prompt, minimo=0, maximo=150):
    while True:
        try:
            val = int(input(prompt).strip())
            if minimo <= val <= maximo:
                return val
            print(f'  Digite entre {minimo} e {maximo}.')
        except ValueError:
            print('  Digite um número inteiro.')


def _escolha(prompt, opcoes):
    """Apresenta opções numeradas e retorna o valor escolhido."""
    for i, op in enumerate(opcoes, 1):
        print(f'  {i}. {op[1]}')
    while True:
        try:
            idx = int(input(prompt).strip())
            if 1 <= idx <= len(opcoes):
                return opcoes[idx - 1][0]
        except ValueError:
            pass
        print(f'  Digite um número de 1 a {len(opcoes)}.')


# =============================================================================
# BLOCO 0 — TRIAGEM DEMOGRÁFICA
# (porta todos os blocos seguintes)
# =============================================================================

def _bloco_demografico(dados):
    _bloco('BLOCO 0 — Triagem Demográfica')
    print('  Estas informações filtram as perguntas seguintes.\n')

    # Sexo — porta para blocos 5F vs 5M
    dados['sexo'] = _escolha(
        '  Sexo biológico: ',
        [('F', 'Feminino'), ('M', 'Masculino')],
    )

    # Idade — gate de risco para neoplasia e prostatite
    dados['idade'] = _int('  Idade (anos): ', 14, 120)
    idade = dados['idade']

    # Gestante — só pergunta para mulheres em idade fértil
    if dados['sexo'] == 'F' and 14 <= idade <= 55:
        dados['gestante'] = sn('  Gestante (sabe que está grávida)? [s/n] ')
        if dados['gestante']:
            _alerta('Gestante: cultura obrigatória antes do ATB. '
                    'ATBs com restrições importantes serão aplicadas.')
    else:
        dados['gestante'] = False

    # Peri / pós-menopausa — relevante para vaginite atrófica e risco de ITU
    if dados['sexo'] == 'F' and idade >= 40:
        dados['peri_pos_menopausa'] = sn(
            '  Peri ou pós-menopausa (menstruação irregular ou ausente ≥ 12 meses)? [s/n] '
        )
    else:
        dados['peri_pos_menopausa'] = False

    # Tabagismo — principal fator de risco para Ca bexiga; eleva estratificação hematúria
    dados['tabagismo'] = sn('  Tabagismo atual ou ex-fumante? [s/n] ')
    if dados['tabagismo']:
        print('  (Tabagismo: principal fator de risco para carcinoma de bexiga.)')

    # Exposição ocupacional a carcinógenos urinários
    if dados['tabagismo'] or idade >= 40:
        dados['exposicao_ocupacional'] = sn(
            '  Exposição ocupacional a corantes, borracha, plástico, solventes '
            'ou pesticidas? [s/n] '
        )
    else:
        dados['exposicao_ocupacional'] = False

    # Radioterapia pélvica prévia
    dados['radioterapia_pelvica'] = sn('  Radioterapia pélvica prévia? [s/n] ')

    # Alerta: 1º episódio em jovem (18-21a) → JAMA 2024 recomenda avaliação médica antes
    if dados['sexo'] == 'F' and 14 <= idade <= 21:
        dados['primeiro_episodio_jovem'] = sn(
            '  É o 1º episódio de ITU na vida (nunca teve antes)? [s/n] '
        )
        if dados['primeiro_episodio_jovem']:
            _alerta('1º episódio em paciente jovem — avaliação médica presencial '
                    'recomendada antes de tratar empiricamente (JAMA 2024).')
    else:
        dados['primeiro_episodio_jovem'] = False


# =============================================================================
# BLOCO 1 — RED FLAGS / EMERGÊNCIA
# (verificar antes de qualquer outra pergunta clínica)
# =============================================================================

def _bloco_red_flags(dados):
    _bloco('BLOCO 1 — Red Flags — Encaminhamento Imediato')
    print('  Qualquer positivo = avaliação presencial imediata / PA/PS.\n')

    dados['hipotensao']      = sn('  Hipotensão (tontura grave, quase desmaio, PA muito baixa)? [s/n] ')
    dados['alteracao_mental']= sn('  Confusão mental, desorientação ou rebaixamento de consciência? [s/n] ')
    dados['retencao_urinaria']= sn('  Não consegue urinar há horas (bexiga cheia e retendo)? [s/n] ')

    dados['sinais_emergencia'] = any([
        dados['hipotensao'],
        dados['alteracao_mental'],
        dados['retencao_urinaria'],
    ])

    if dados['sinais_emergencia']:
        _alerta('ENCAMINHAMENTO IMEDIATO — PA/PS agora.')
        print('  Não prosseguir com anamnese completa — estabilizar e transferir.\n')


# =============================================================================
# BLOCO 2 — QUEIXA PRINCIPAL
# =============================================================================

def _bloco_queixa(dados):
    _bloco('BLOCO 2 — Queixa Principal')

    print('  Qual a queixa que trouxe o paciente?\n')
    dados['queixa_principal'] = _escolha(
        '  Escolha: ',
        [
            ('disuria',   'Dor / ardência ao urinar (disúria)'),
            ('hematuria', 'Sangue na urina (hematúria)'),
            ('ambos',     'Ambos — dor ao urinar E sangue na urina'),
        ],
    )


# =============================================================================
# BLOCO 3 — SINTOMAS URINÁRIOS LOCAIS
# =============================================================================

def _bloco_sintomas_urinarios(dados):
    _bloco('BLOCO 3 — Sintomas Urinários Locais')

    queixa = dados.get('queixa_principal', 'disuria')

    if queixa in ('disuria', 'ambos'):
        dados['disuria']         = sn('  Ardência / dor ao urinar (disúria)? [s/n] ')
        dados['frequencia']      = sn('  Urinar muito mais vezes que o normal (polaciúria)? [s/n] ')
        dados['urgencia']        = sn('  Urgência — vontade súbita e difícil de segurar? [s/n] ')
        dados['nocturia']        = sn('  Acorda à noite para urinar? [s/n] ')
        dados['dor_suprapubica'] = sn('  Dor ou pressão na barriga baixa (supra-púbica)? [s/n] ')
    else:
        dados['disuria']         = False
        dados['frequencia']      = False
        dados['urgencia']        = False
        dados['nocturia']        = False
        dados['dor_suprapubica'] = False

    if queixa in ('hematuria', 'ambos'):
        dados['hematuria_macro'] = sn('  Urina visivelmente vermelha ou cor de "coca-cola"? [s/n] ')
        if not dados['hematuria_macro']:
            dados['hematuria_micro'] = sn(
                '  Sangue detectado no EAS (exame de urina), mas urina de cor normal? [s/n] '
            )
        else:
            dados['hematuria_micro'] = False
    else:
        dados['hematuria_macro'] = False
        dados['hematuria_micro'] = False

    # Mudança de cor / odor SEM hematúria e sem sintomas de cistite
    if not dados['hematuria_macro'] and not dados['hematuria_micro'] and \
            not dados['disuria'] and not dados['frequencia']:
        dados['mudanca_cor_odor_apenas'] = sn(
            '  Apenas mudança de cor ou odor da urina, sem outros sintomas? [s/n] '
        )
        if dados.get('mudanca_cor_odor_apenas'):
            _alerta('Mudança de cor/odor SEM sintomas de cistite: '
                    'causas comuns incluem alimentação (beterraba), '
                    'medicamentos (rifampicina) e hidratação. '
                    'Não requer ATB — orientar e observar.')
    else:
        dados['mudanca_cor_odor_apenas'] = False


# =============================================================================
# BLOCO 4 — SINTOMAS SISTÊMICOS
# (febre + dor lombar = pielonefrite até prova em contrário)
# =============================================================================

def _bloco_sistemicos(dados):
    _bloco('BLOCO 4 — Sintomas Sistêmicos')
    print('  Febre + dor lombar = pielonefrite até prova em contrário.\n')

    dados['febre']       = sn('  Febre (temperatura ≥ 37,8°C ou sensação clara de febre)? [s/n] ')
    dados['calafrio']    = sn('  Calafrio / tremores (rigor)? [s/n] ') if dados['febre'] else False
    dados['nausea_vomito'] = sn('  Náusea ou vômito? [s/n] ')
    dados['dor_lombar']  = sn('  Dor na região lombar (costolateral, "nos rins")? [s/n] ')
    dados['ppd_positivo']= sn('  Punho-percussão dorsal positivo (doloroso ao bater levemente '
                               'no flanco)? [s/n] ') if dados.get('dor_lombar') else False

    if dados['febre'] and (dados['dor_lombar'] or dados['ppd_positivo']):
        _alerta('Febre + dor lombar / PPD positivo → PIELONEFRITE provável. '
                'Se vômito intratável ou calafrio → PA/PS (pode não tolerar ATB oral).')


# =============================================================================
# BLOCO 5F — SINTOMAS GENITAIS FEMININOS
# =============================================================================

def _bloco_genital_feminino(dados):
    _bloco('BLOCO 5F — Sintomas Genitais (Feminino)')
    print('  Distingue cistite de vaginite / IST — muda completamente a conduta.\n')

    dados['secrecao_vaginal'] = sn('  Corrimento vaginal (diferente do habitual)? [s/n] ')
    if dados['secrecao_vaginal']:
        print('\n  Como é o corrimento?')
        dados['corrimento_tipo'] = _escolha(
            '  Escolha o mais parecido: ',
            [
                ('grumoso_branco',       'Branco grumoso, tipo "queijo cottage" — prurido intenso'),
                ('acinzentado',          'Acinzentado / homogêneo — odor de peixe'),
                ('amarelo_esverdeado',   'Amarelo-esverdeado / purulento — IST?'),
                ('claro_sem_caracteristica', 'Claro / aquoso / sem característica especial'),
            ],
        )
        if dados['corrimento_tipo'] == 'grumoso_branco':
            print('  (Padrão: candidíase vulvovaginal.)')
        elif dados['corrimento_tipo'] == 'acinzentado':
            print('  (Padrão: vaginose bacteriana — pH elevado, odor de aminas.)')
        elif dados['corrimento_tipo'] == 'amarelo_esverdeado':
            _alerta('Corrimento purulento — suspeita de IST (gonorreia / clamídia / tricomoníase).')
    else:
        dados['corrimento_tipo'] = None

    dados['prurido_genital'] = sn('  Prurido / coceira genital intensa? [s/n] ')
    dados['lesao_genital']   = sn('  Lesão genital visível (úlcera, bolhas/vesículas, ferida)? [s/n] ')
    if dados['lesao_genital']:
        _alerta('Lesão genital + disúria → considerar herpes genital '
                '(disúria por irritação periuretral, não por ITU).')

    dados['dispareunia'] = sn('  Dor durante a relação sexual (dispareunia)? [s/n] ')

    # Vaginite atrófica — só relevante em peri/pós-menopausa
    if dados.get('peri_pos_menopausa'):
        dados['ressecamento_vaginal'] = sn(
            '  Ressecamento vaginal / sensação de queimação sem infecção (pós-menopausa)? [s/n] '
        )
    else:
        dados['ressecamento_vaginal'] = False


# =============================================================================
# BLOCO 5M — SINTOMAS GENITAIS / PROSTÁTICOS MASCULINOS
# =============================================================================

def _bloco_genital_masculino(dados):
    _bloco('BLOCO 5M — Sintomas Genitais / Prostáticos (Masculino)')
    print('  Todo ITU em homem é complicada — investigar próstata.\n')

    dados['secrecao_uretral'] = sn('  Secreção pelo pênis (além da urina)? [s/n] ')
    if dados['secrecao_uretral']:
        _alerta('Secreção uretral + risco IST → considerar gonorreia / clamídia. '
                'Tratamento sindrômico dual mesmo sem cultura.')

    # Sintomas prostáticos / obstrutivos
    dados['hesitancia']            = sn('  Dificuldade para iniciar o jato de urina (hesitância)? [s/n] ')
    dados['jato_fraco']            = sn('  Jato de urina fraco ou fino? [s/n] ')
    dados['gotejamento_terminal']  = sn('  Gotejamento no final da micção? [s/n] ')
    dados['dor_perineal']          = sn('  Dor na região entre o escroto e o ânus (períneo)? [s/n] ')

    if dados['dor_perineal']:
        print('\n  Dor perineal: considerar prostatite.')
        dados['toque_prostatico'] = _escolha(
            '  Toque retal realizado? Próstata: ',
            [
                ('normal',            'Normal — sem dor, sem aumento'),
                ('doloroso_boggoso',  'Dolorosa e amolecida ao toque (boggosa)'),
                ('nodular',           'Nodular ou endurecida — suspeita de Ca próstata'),
                ('nao_realizado',     'Toque não realizado'),
            ],
        )
        if dados['toque_prostatico'] == 'doloroso_boggoso' and dados.get('febre'):
            _alerta('Próstata dolorosa + febre = prostatite aguda. '
                    'NÃO realizar massagem prostática (risco de bacteremia).')
        if dados['toque_prostatico'] == 'nodular':
            _alerta('Próstata nodular → suspeita Ca próstata — encaminhar urologia.')
    else:
        dados['toque_prostatico'] = None

    # HPB sintomático
    if dados['hesitancia'] or dados['jato_fraco'] or dados['gotejamento_terminal']:
        print('\n  Sintomas obstrutivos presentes — calcular IPSS:')
        print('    IPSS 0–7 = leve  |  8–19 = moderado  |  ≥20 = grave')
        dados['ipss_grave'] = sn('  IPSS ≥ 20 (sintomas graves) ou retenção prévia? [s/n] ')
        if dados['ipss_grave']:
            _alerta('IPSS grave ou retenção → encaminhamento urologia urgente.')
    else:
        dados['ipss_grave'] = False


# =============================================================================
# BLOCO 6 — RISCO IST
# (perguntado para ambos os sexos se houver secreção ou lesão)
# =============================================================================

def _bloco_ist(dados):
    tem_secrecao = dados.get('secrecao_vaginal') or dados.get('secrecao_uretral')
    tem_lesao    = dados.get('lesao_genital')
    if not (tem_secrecao or tem_lesao):
        dados['ist_risco'] = False
        return

    _bloco('BLOCO 6 — Risco de IST')
    print('  Avaliar exposição para orientar tratamento sindrômico.\n')

    dados['parceiro_novo']        = sn('  Parceiro sexual novo nos últimos 3 meses? [s/n] ')
    dados['multiplos_parceiros']  = sn('  Múltiplos parceiros sexuais no último ano? [s/n] ')
    dados['ist_previa']           = sn('  IST prévia (gonorreia, clamídia, sífilis, herpes)? [s/n] ')
    dados['sem_preservativo']     = sn('  Relações sem preservativo recentes? [s/n] ')

    dados['ist_risco'] = any([
        dados['parceiro_novo'],
        dados['multiplos_parceiros'],
        dados['ist_previa'],
        dados['sem_preservativo'],
    ])

    if dados['ist_risco']:
        _alerta('Risco de IST — tratamento sindrômico simultâneo gonorreia + clamídia. '
                'Testar HIV + sífilis. Notificação compulsória.')
    else:
        dados['ist_risco'] = False   # sem risco identificado → não rotear para IST


# =============================================================================
# BLOCO 7 — FATORES DE RISCO / COMPLICADORES
# =============================================================================

def _bloco_fatores_risco(dados):
    _bloco('BLOCO 7 — Fatores de Risco e Complicadores')
    print('  Determinam se a ITU é complicada (cultura obrigatória).\n')

    idade = dados.get('idade', 30)
    sexo  = dados.get('sexo', 'F')

    dados['itu_recorrente']  = sn('  ITU recorrente (≥ 3 episódios no último ano ou ≥ 2 em 6 meses)? [s/n] ')
    dados['atb_recente_30d'] = sn('  Usou antibiótico para ITU nos últimos 30 dias? [s/n] ')
    dados['atb_fl_smx_3m']   = sn(
        '  Usou fluoroquinolona (cipro, levo), SMX-TMP (bactrim) ou cefalosporina ampla '
        'nos últimos 3 meses? [s/n] '
    )
    dados['cateter']         = sn('  Cateter urinário (sonda vesical) no momento ou na última semana? [s/n] ')
    dados['diabetes']        = sn('  Diabetes mellitus? [s/n] ')
    dados['imunossupressao'] = sn(
        '  Imunossupressão (HIV/AIDS, transplante, quimioterapia, corticosteroide crônico, biológico)? [s/n] '
    )
    dados['drc'] = sn('  Doença renal crônica estágio 4–5 ou rim único? [s/n] ')
    dados['obstrucao_urinaria'] = sn(
        '  Obstrução urinária conhecida (cálculo bloqueando, tumor, estenose)? [s/n] '
    )
    dados['litíase_previa'] = sn('  Histórico de cálculo renal (litíase)? [s/n] ')

    # Flag: cistite complicada se qualquer fator presente
    complicada = any([
        dados.get('gestante'),
        dados['itu_recorrente'],
        dados['atb_recente_30d'],
        dados['atb_fl_smx_3m'],
        dados['cateter'],
        dados['diabetes'],
        dados['imunossupressao'],
        dados['drc'],
        dados['obstrucao_urinaria'],
        sexo == 'M',
    ])

    if complicada and (dados.get('disuria') or dados.get('frequencia')):
        _alerta('ITU complicada — urocultura obrigatória antes de iniciar ATB.')

    # Herpes: perguntar se há lesão (episódio prévio?)
    if dados.get('lesao_genital'):
        dados['herpes_primeiro_episodio'] = sn(
            '  Primeira vez com esta lesão genital (nunca teve antes)? [s/n] '
        )
    else:
        dados['herpes_primeiro_episodio'] = True  # default — não relevante sem lesão

    # Candidíase recorrente — só se prurido + grumoso_branco
    if dados.get('prurido_genital') and dados.get('corrimento_tipo') == 'grumoso_branco':
        dados['candidíase_recorrente'] = sn(
            '  Candidíase recorrente (≥ 4 episódios no último ano)? [s/n] '
        )
    else:
        dados['candidíase_recorrente'] = False


# =============================================================================
# BLOCO 8 — CARACTERIZAÇÃO DA HEMATÚRIA
# (só se hematúria macro ou micro reportada)
# =============================================================================

def _bloco_hematuria(dados):
    if not (dados.get('hematuria_macro') or dados.get('hematuria_micro')):
        return

    _bloco('BLOCO 8 — Caracterização da Hematúria')

    if dados.get('hematuria_macro'):
        dados['hematuria_indolor'] = sn(
            '  Hematúria SEM dor (indolor — veio do nada, sem cólica)? [s/n] '
        )
        if dados['hematuria_indolor']:
            _alerta('Hematúria macroscópica indolor → neoplasia de bexiga até prova em contrário '
                    '(especialmente ≥35 anos, tabagistas). Encaminhar urologia em ≤ 2 semanas.')

        dados['hematuria_colicativa'] = sn(
            '  Hematúria associada a cólica / dor em flanco (tipo "cálculo")? [s/n] '
        )
        dados['hematuria_fumaca'] = sn(
            '  Urina cor de "coca-cola" / chá escuro / fumacenta (não vermelha viva)? [s/n] '
        )
        if dados['hematuria_fumaca']:
            _alerta('Urina cor de "coca-cola" → padrão de hematúria glomerular '
                    '(IgA nefropatia, pós-estreptocócica). Solicitar proteinúria + função renal.')

        dados['hematuria_pos_esforco'] = sn(
            '  Hematúria apareceu após exercício intenso? [s/n] '
        )
    else:
        dados['hematuria_indolor']     = False
        dados['hematuria_colicativa']  = False
        dados['hematuria_fumaca']      = False
        dados['hematuria_pos_esforco'] = False

    if dados.get('hematuria_micro'):
        dados['eas_hemacias_hpf'] = _int(
            '  Hemácias no EAS (células por campo — HPF): ', 0, 9999
        )
    else:
        dados['eas_hemacias_hpf'] = 0


# =============================================================================
# BLOCO 9 — EAS (se disponível)
# =============================================================================

def _bloco_eas(dados):
    _bloco('BLOCO 9 — EAS (Exame de Urina) — Resultados')
    print('  Preencher apenas se o resultado já estiver disponível.\n')

    dados['eas_disponivel'] = sn('  Resultado do EAS disponível agora? [s/n] ')
    if not dados['eas_disponivel']:
        dados['eas_piuria']             = False
        dados['eas_nitritos']           = False
        dados['eas_hemacias']           = False
        dados['eas_cilindros']          = False
        dados['eas_proteinuria']        = False
        dados['eas_hemacias_dismorfica']= False
        return

    dados['eas_piuria']   = sn('  Leucocitúria / piúria (leucócitos ++ ou mais)? [s/n] ')
    dados['eas_nitritos'] = sn('  Nitritos positivos? [s/n] ')
    dados['eas_hemacias'] = sn('  Hemácias no EAS (hematúria microscópica no exame)? [s/n] ')

    if dados['eas_hemacias'] and not dados.get('hematuria_micro'):
        dados['hematuria_micro'] = True   # EAS confirma o que o paciente não referiu

    dados['eas_cilindros']   = sn('  Cilindros hemáticos ou granulosos no EAS? [s/n] ')
    dados['eas_proteinuria'] = sn('  Proteinúria (proteína ≥ 1+ no EAS)? [s/n] ')

    if dados['eas_cilindros'] or dados['eas_proteinuria']:
        _alerta('Cilindros e/ou proteinúria → padrão glomerular. '
                'Solicitar razão proteína/creatinina. Encaminhar nefrologia.')

    if dados['eas_piuria'] and dados['eas_nitritos']:
        print('\n  EAS: leucocitúria + nitritos → alta probabilidade de ITU.')
    elif dados['eas_piuria'] and not dados['eas_nitritos']:
        print('\n  EAS: leucocitúria sem nitritos — ITU possível '
              '(nitritos negativos não excluem — Enterococcus e Staphylococcus não produzem).')
    elif not dados['eas_piuria'] and not dados['eas_nitritos']:
        print('\n  EAS: sem leucocitúria e sem nitritos → ITU menos provável '
              '(VPN 78–98%). Considerar diagnóstico alternativo.')

    dados['eas_hemacias_dismorfica'] = sn(
        '  Hemácias dismórficas no sedimento (acantócitos / disfigured RBCs)? [s/n] '
    ) if dados['eas_hemacias'] else False


# =============================================================================
# PERSISTÊNCIA
# =============================================================================

def _salvar(dados, pasta='dados_pacientes'):
    os.makedirs(pasta, exist_ok=True)
    ts   = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome = os.path.join(pasta, f'urinario_subjetivo_{ts}.json')
    with open(nome, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f'\n  Dados salvos: {nome}')
    return nome


# =============================================================================
# PONTO DE ENTRADA PRINCIPAL
# =============================================================================

def coletar_subjetivo_urinario(dados_preenchidos=None):
    """
    Coleta anamnese dirigida para queixas urinárias.

    Parâmetros
    ----------
    dados_preenchidos : dict, opcional
        Dados já coletados (demográficos da admissão geral) para não repetir.

    Retorna
    -------
    (dados: dict, arquivo_json: str)
    """
    sys.stdout.reconfigure(encoding='utf-8')

    print('\n' + '=' * 56)
    print('  SYMPTOPY — Anamnese: Queixas Urinárias')
    print('  (Disúria · Hematúria)')
    print('=' * 56)
    print('  Responda s (sim) / n (não) ou escolha o número.\n')

    dados = dict(dados_preenchidos) if dados_preenchidos else {}

    # ── Blocos universais ─────────────────────────────────────────────────────
    _bloco_demografico(dados)

    # Encerrar cedo se red flag grave já confirmada
    _bloco_red_flags(dados)
    if dados.get('sinais_emergencia'):
        print('\n  ⚠️  Anamnese interrompida — encaminhar PA/PS imediatamente.')
        arquivo = _salvar(dados)
        return dados, arquivo

    _bloco_queixa(dados)
    _bloco_sintomas_urinarios(dados)
    _bloco_sistemicos(dados)

    # ── Blocos condicionais por sexo ──────────────────────────────────────────
    if dados.get('sexo') == 'F':
        _bloco_genital_feminino(dados)
    else:
        _bloco_genital_masculino(dados)
        # Homem pode ter secreção uretral — marcar para bloco IST
        if not dados.get('secrecao_uretral'):
            dados['secrecao_vaginal'] = False
            dados['lesao_genital']    = dados.get('lesao_genital', False)

    # ── Bloco IST (ambos se risco identificado) ───────────────────────────────
    _bloco_ist(dados)

    # ── Fatores de risco ──────────────────────────────────────────────────────
    _bloco_fatores_risco(dados)

    # ── Blocos condicionais por queixa ────────────────────────────────────────
    if dados.get('hematuria_macro') or dados.get('hematuria_micro'):
        _bloco_hematuria(dados)

    # ── EAS (sempre ao final se disponível) ──────────────────────────────────
    _bloco_eas(dados)

    # ── Resumo de bandeiras antes de salvar ──────────────────────────────────
    print('\n' + '─' * 56)
    print('  RESUMO — Sinais de Atenção Identificados')
    print('─' * 56)

    alertas = []
    if dados.get('gestante'):
        alertas.append('GESTANTE → cultura obrigatória + ATBs restritos')
    if dados.get('febre') and (dados.get('ppd_positivo') or dados.get('dor_lombar')):
        alertas.append('PIELONEFRITE provável → avaliar critérios de internação')
    if dados.get('ist_risco'):
        alertas.append('RISCO IST → tratamento dual + notificação + testar parceiro')
    if dados.get('hematuria_macro') and dados.get('hematuria_indolor') and dados.get('idade', 0) >= 35:
        alertas.append('HEMATÚRIA MACROSCÓPICA INDOLOR ≥35 anos → urologia em ≤ 2 sem')
    if dados.get('eas_cilindros') or dados.get('eas_proteinuria'):
        alertas.append('EAS GLOMERULAR → nefrologia')
    if dados.get('toque_prostatico') == 'nodular':
        alertas.append('PRÓSTATA NODULAR → Ca próstata? Urologia')
    if dados.get('ipss_grave'):
        alertas.append('IPSS GRAVE / RETENÇÃO → urologia urgente')

    if alertas:
        for a in alertas:
            print(f'  ⚠️  {a}')
    else:
        print('  ✓  Sem bandeiras de encaminhamento imediato identificadas.')

    arquivo = _salvar(dados)
    print('\n  Próximo passo: engine_urinario.py → raciocínio clínico\n')
    return dados, arquivo


if __name__ == '__main__':
    coletar_subjetivo_urinario()
