# analgesicos.py
# Perfil farmacológico e alertas por comorbidade para analgésicos
# Base: Open Evidence 2026 / VA Guidelines / FDA / Lancet / NEJM PRECISION trial
#
# Usado por: engine MSK, engine clínico, qualquer módulo que sugira analgesia
# Interface pública: avaliar_analgesia(medicamento, comorbidades, idade, medicacoes)
#
# Medicamentos cobertos:
#   AINEs não seletivos  → ibuprofen, diclofenaco, naproxeno
#   COX-2 preferencial   → nimesulida, meloxicam
#   COX-2 seletivo       → celecoxibe
#   Paracetamol
#   AINE tópico          → diclofenaco gel, cetoprofeno gel
#   Tramadol
#   Duloxetina
#   Gabapentina / Pregabalina
#   Corticoide injetável


# =============================================================================
# 1. PERFIS POR MEDICAMENTO
#    Cada perfil define alertas por comorbidade:
#    'CI'       = contraindicado
#    'CUIDADO'  = usar com cautela + orientação
#    'PREFERIR' = mais seguro neste contexto
#    None       = sem alerta específico
# =============================================================================

PERFIS = {

    # ------------------------------------------------------------------
    # AINEs NÃO SELETIVOS (ibuprofeno, diclofenaco, naproxeno)
    # ------------------------------------------------------------------
    'aine_oral': {
        'nome_display': 'AINE oral (ibuprofeno / diclofenaco / naproxeno)',
        'opcoes': ['ibuprofeno', 'diclofenaco', 'naproxeno'],
        'comorbidades': {
            'drc_egfr_menor_30':        ('CI',      'Contraindicado. Risco de IRA, hipercalemia, retenção hídrica. Usar paracetamol.'),
            'drc_egfr_30_60':           ('CUIDADO', 'Usar com extrema cautela. Menor dose, menor duração. Naproxeno preferível ao ibuprofeno. Monitorar SCr, K+, PA semanalmente no início.'),
            'drc_egfr_maior_60':        ('CUIDADO', 'Monitorar função renal se fatores de risco (idade >65, IC, diurético, IECA/BRA).'),
            'ulcera_ativa':             ('CI',      'Contraindicado. Risco 4-6x maior de complicações. Usar COX-2 + IBP se AINE essencial.'),
            'ulcera_historico':         ('CUIDADO', 'IBP obrigatório. Preferir COX-2 seletivo. Tratar H. pylori antes.'),
            'cirrose':                  ('CI',      'Contraindicado. Risco de síndrome hepatorrenal, sangramento GI, retenção hídrica.'),
            'ic':                       ('CI',      'Contraindicado. Risco 10x de descompensação de IC. Usar paracetamol.'),
            'has':                      ('CUIDADO', 'AINEs antagonizam anti-hipertensivos. Monitorar PA. Naproxeno pode ser mais seguro. Preferir AINE tópico.'),
            'anticoagulado':            ('CUIDADO', 'Risco de sangramento aumentado. IBP obrigatório. Preferir COX-2 + IBP. Evitar se possível.'),
            'diabetes':                 ('CUIDADO', 'Monitorar função renal. Risco aumentado de eventos renais.'),
            'idade_acima_65':           ('CUIDADO', 'IBP obrigatório se AINE oral. Preferir AINE tópico como primeira escolha. Risco GI/renal/CV aumentado.'),
            'gestacao_1_2_trimestre':   ('CUIDADO', 'Evitar se possível. Uso de curta duração somente se benefício supera risco.'),
            'gestacao_3_trimestre':     ('CI',      'Contraindicado. Risco de fechamento prematuro do ducto arterioso e oligodrâmnio.'),
            'epilepsia':                (None,      'Sem contraindicação específica. AINEs não reduzem limiar convulsivo.'),
            'depressao_ssri_snri':      ('CUIDADO', 'Risco de sangramento GI 1.5-2x aumentado. Recomendar IBP.'),
        },
        'diferencas_entre_opcoes': {
            'naproxeno':    'Menor risco CV. Maior risco GI. Preferir se doença CV presente. Pode interferir menos com AAS.',
            'ibuprofeno':   'Risco CV/GI moderado. Pode antagonizar efeito antiagregante do AAS — usar AAS primeiro.',
            'diclofenaco':  'COX-2 seletivo em doses terapêuticas. Risco CV similar ao celecoxibe. Maior risco renal entre os não seletivos.',
        },
        'interacoes_importantes': [
            'IECA/BRA → reduz efeito anti-hipertensivo + nefrotoxicidade',
            'Diuréticos → reduz efeito diurético + risco renal',
            'Warfarina/DOAC → risco de sangramento GI e intracraniano — IBP obrigatório',
            'AAS antiagregante → ibuprofeno antagoniza efeito; preferir naproxeno ou celecoxibe',
            'SSRIs/SNRIs → risco GI 1.5-2x — IBP recomendado',
        ],
        'monitoramento_cronico': {
            'PA':          'Aferir a cada 2-4 semanas no início, depois a cada 3 meses',
            'SCr_eGFR':    'Basalmente e 1-2 semanas após início, depois a cada 3-6 meses',
            'K+':          'A cada 3-6 meses se usando IECA/BRA',
            'hemograma':   'A cada 6-12 meses se uso crônico > 3 meses (sangramento oculto)',
        },
    },

    # ------------------------------------------------------------------
    # COX-2 PREFERENCIAL (nimesulida, meloxicam)
    # ------------------------------------------------------------------
    'cox2_preferencial': {
        'nome_display': 'COX-2 preferencial (nimesulida / meloxicam)',
        'opcoes': ['nimesulida', 'meloxicam'],
        'comorbidades': {
            'drc_egfr_menor_30':        ('CI',      'Contraindicado. Mesmo risco renal que AINEs não seletivos.'),
            'drc_egfr_30_60':           ('CUIDADO', 'Sem vantagem renal sobre não seletivos. Usar com extrema cautela.'),
            'ulcera_ativa':             ('CUIDADO', 'Menor risco GI que não seletivos, mas ainda significativo. IBP recomendado.'),
            'cirrose':                  ('CI',      'Nimesulida: CONTRAINDICADA — risco hepatotóxico 2.1x, 45% necessitaram transplante ou morreram. Meloxicam: usar com cautela, monitorar TGO/TGP.'),
            'ic':                       ('CI',      'Contraindicado. Risco CV similar aos não seletivos.'),
            'has':                      ('CUIDADO', 'Monitorar PA. Meloxicam: segurança CV similar ao celecoxibe.'),
            'idade_acima_65':           ('CUIDADO', 'IBP recomendado. Preferir AINE tópico.'),
            'gestacao_3_trimestre':     ('CI',      'Contraindicado — igual aos não seletivos.'),
        },
        'diferencas_entre_opcoes': {
            'nimesulida': '⚠️  ALERTA HEPÁTICO: RR 2.10 de lesão hepática aguda grave. OR 10.69 em doses altas. OR 12.55 com uso > 30 dias. Um terço desenvolve hepatotoxicidade em < 15 dias. Evitar se alternativa disponível. Se usar: limitar a < 15 dias, menor dose, monitorar TGO/TGP.',
            'meloxicam':  'Menor risco hepático que nimesulida. Segurança CV similar ao celecoxibe. Preferível à nimesulida na maioria dos casos.',
        },
        'interacoes_importantes': [
            'Mesmas que AINEs não seletivos para interações renais e cardiovasculares',
            'Nimesulida + qualquer hepatotóxico → evitar combinação',
        ],
    },

    # ------------------------------------------------------------------
    # COX-2 SELETIVO (celecoxibe)
    # ------------------------------------------------------------------
    'cox2_seletivo': {
        'nome_display': 'COX-2 seletivo (celecoxibe)',
        'comorbidades': {
            'drc_egfr_menor_30':        ('CI',      'Contraindicado. Sem vantagem renal sobre não seletivos.'),
            'drc_egfr_30_60':           ('PREFERIR','Menor taxa de eventos renais que ibuprofeno (HR 0.61). Similar ao naproxeno.'),
            'ulcera_ativa':             ('PREFERIR', 'Menor risco GI. IBP ainda recomendado se fatores de risco presentes.'),
            'ic':                       ('CI',      'Dobra o risco de hospitalização por IC.'),
            'doenca_cv':                ('PREFERIR', 'PRECISION trial: não inferior em risco CV vs naproxeno/ibuprofeno. 35-40% menor risco CV vs outros AINEs pós-IAM.'),
            'anticoagulado':            ('PREFERIR', 'Menor risco de sangramento que não seletivos. IBP ainda recomendado.'),
            'idade_acima_65':           ('PREFERIR', 'Menos eventos GI. IBP ainda recomendado.'),
            'gestacao_3_trimestre':     ('CI',      'Contraindicado — igual a todos os AINEs.'),
        },
        'interacoes_importantes': [
            'Fluconazol → duplica níveis de celecoxibe (inibição CYP2C9) — reduzir dose 50%',
            'Lítio → aumenta níveis de lítio — monitorar',
            'Warfarina → menor risco que não seletivos, mas IBP recomendado e monitorar INR',
            'AAS → reduz benefício GI do celecoxibe — IBP obrigatório se combinados',
        ],
    },

    # ------------------------------------------------------------------
    # PARACETAMOL
    # ------------------------------------------------------------------
    'paracetamol': {
        'nome_display': 'Paracetamol (acetaminofeno)',
        'dose_maxima': {
            'normal':           '4g/dia (3g/dia preferível para uso crônico)',
            'hepatico_leve':    '2g/dia (evitar em doença hepática alcoólica)',
            'hepatico_grave':   'Contraindicado',
            'alcool_cronico':   '2g/dia máximo',
            'drc_qualquer':     '4g/dia — sem ajuste, analgésico mais seguro em DRC',
        },
        'comorbidades': {
            'drc_egfr_menor_30':        ('PREFERIR', 'Analgésico mais seguro em DRC. Sem ajuste de dose necessário.'),
            'drc_egfr_30_60':           ('PREFERIR', 'Seguro. Preferir sobre AINEs.'),
            'cirrose_compensada':        ('CUIDADO', 'Máximo 2g/dia. Evitar em doença hepática alcoólica.'),
            'cirrose_descompensada':     ('CI',      'Contraindicado. Alto risco de hepatotoxicidade.'),
            'alcool_cronico':            ('CUIDADO', 'Máximo 2g/dia. Risco aumentado de hepatotoxicidade.'),
            'ic':                       ('PREFERIR', 'Sem retenção hídrica. Alternativa segura aos AINEs.'),
            'idade_acima_65':           ('PREFERIR', 'Analgésico de primeira linha. Sem ajuste de dose.'),
            'gestacao':                 ('PREFERIR', 'Analgésico mais seguro na gestação — todos os trimestres.'),
        },
        'monitoramento_cronico': {
            'TGO_TGP': 'Se uso crônico > 3g/dia ou fatores de risco hepáticos — a cada 6-12 meses',
        },
        'interacoes_importantes': [
            'Warfarina → potencializa efeito anticoagulante em doses > 2g/dia — monitorar INR',
            'Álcool → hepatotoxicidade sinérgica',
            'Isoniazida → hepatotoxicidade aumentada',
        ],
    },

    # ------------------------------------------------------------------
    # AINE TÓPICO (diclofenaco gel, cetoprofeno gel)
    # ------------------------------------------------------------------
    'aine_topico': {
        'nome_display': 'AINE tópico (diclofenaco gel / cetoprofeno gel)',
        'comorbidades': {
            'drc_qualquer':             ('PREFERIR', 'Absorção sistêmica mínima. Seguro em qualquer estágio de DRC.'),
            'ulcera_ativa':             ('PREFERIR', 'Significativamente menos eventos GI que AINEs orais.'),
            'cirrose':                  ('PREFERIR', 'Exposição sistêmica mínima.'),
            'ic':                       ('PREFERIR', 'Menor risco CV que AINEs orais.'),
            'idade_acima_65':           ('PREFERIR', 'Primeira linha em idosos. Eficácia similar ao oral com perfil de segurança superior.'),
            'multiplas_comorbidades':   ('PREFERIR', 'Menor mortalidade por todas as causas vs AINEs orais e paracetamol em pacientes com múltiplas comorbidades.'),
        },
        'indicacoes_preferencias': [
            'OA de joelho, ombro, mão — evidência equiparável ao oral',
            'Paciente com ≥1 fator de risco sistêmico',
            'Paciente idoso > 65 anos',
            'DRC qualquer estágio',
            'Doença GI prévia',
        ],
        'notas': 'Aplicar 3-4x/dia na área dolorosa. Lavar mãos após aplicação. Evitar exposição solar na área (cetoprofeno — fotossensibilidade).',
    },

    # ------------------------------------------------------------------
    # TRAMADOL
    # ------------------------------------------------------------------
    'tramadol': {
        'nome_display': 'Tramadol',
        'dose_maxima_por_egfr': {
            'egfr_maior_60':    '400mg/dia',
            'egfr_30_60':       '200-300mg/dia — monitorar acúmulo',
            'egfr_15_30':       '200mg/dia a cada 12h',
            'egfr_menor_15':    '100mg/dia pós-diálise',
        },
        'comorbidades': {
            'drc_egfr_menor_30':        ('CUIDADO', 'Ajuste obrigatório: intervalo de 12h, máximo 200mg/dia.'),
            'cirrose':                  ('CUIDADO', 'Metabolismo reduzido — eficácia pode ser menor. Aumentar intervalo.'),
            'epilepsia':                ('CI',      'CONTRAINDICADO. Reduz limiar convulsivo. Risco aumentado com SSRIs/SNRIs.'),
            'depressao_ssri_snri':      ('CI',      'CONTRAINDICADO. Risco EXCEPCIONAL de síndrome serotoninérgica (ROR 95.94, IC 88.9-103.5). Sintomas: alteração mental, instabilidade autonômica, hiperreflexia, rigidez. Início: horas a dias. Conduta: suspender imediatamente, benzodiazepínico, ciproheptadina.'),
            'idade_acima_65':           ('CUIDADO', 'Iniciar dose baixa. Risco aumentado de quedas e confusão.'),
            'gestacao':                 ('CUIDADO', 'Evitar se possível. Síndrome de abstinência neonatal.'),
            'uso_antidepressivo_triciclico': ('CUIDADO', 'Risco de síndrome serotoninérgica e convulsões. Evitar combinação.'),
        },
        'interacoes_importantes': [
            '⚠️  SSRIs/SNRIs → síndrome serotoninérgica (ROR 95.94) — CONTRAINDICADO',
            '⚠️  MAOIs → síndrome serotoninérgica grave — aguardar 14 dias após suspensão do IMAO',
            'CYP2D6 inibidores (fluoxetina, paroxetina, bupropiona) → reduz conversão ao metabólito ativo + paradoxalmente aumenta risco serotoninérgico',
            'Antidepressivos tricíclicos → convulsão + síndrome serotoninérgica',
            'Carbamazepina → reduz eficácia do tramadol (indução CYP3A4)',
        ],
        'alerta_especial': 'SÍNDROME SEROTONINÉRGICA: risco excepcional com qualquer serotonérgico. Considerar antes de prescrever se o paciente usa antidepressivo.',
    },

    # ------------------------------------------------------------------
    # DULOXETINA
    # ------------------------------------------------------------------
    'duloxetina': {
        'nome_display': 'Duloxetina',
        'indicacoes_msk': [
            'Dor nociplástica (sensibilização central)',
            'Dor neuropática MSK',
            'OA de joelho com componente central (evidência moderada)',
            'Lombalgia crônica',
            'Fibromialgia',
        ],
        'dose_maxima_por_egfr': {
            'egfr_maior_30':    '60mg/dia — sem ajuste',
            'egfr_menor_30':    'CONTRAINDICADO — aumento 100% no AUC, acúmulo de metabólito',
        },
        'comorbidades': {
            'drc_egfr_menor_30':        ('CI',      'Contraindicado. Acúmulo 100% de AUC. Risco de toxicidade.'),
            'cirrose_qualquer':          ('CI',      'Contraindicado. Aumento 5x no AUC, meia-vida 3x maior. Risco de falência hepática (às vezes fatal).'),
            'doenca_hepatica_cronica':   ('CI',      'Contraindicado. Risco de falência hepática.'),
            'alcool_cronico':            ('CI',      'Contraindicado. Hepatotoxicidade sinérgica.'),
            'has':                       ('CUIDADO', 'Monitorar PA. Pode elevar PA 2-3 mmHg.'),
            'depressao_ssri_snri':       ('CI',      'Contraindicado — síndrome serotoninérgica.'),
            'epilepsia':                 ('CUIDADO', 'Pode reduzir limiar convulsivo.'),
            'idade_acima_65':            ('CUIDADO', 'Risco aumentado de quedas, hipotensão ortostática, hiponatremia.'),
            'gestacao_3_trimestre':      ('CUIDADO', 'Evitar no 3º trimestre. Complicações neonatais.'),
        },
        'interacoes_importantes': [
            '⚠️  SSRIs/SNRIs/MAOIs → síndrome serotoninérgica — CONTRAINDICADO',
            'Aguardar 14 dias após IMAO; 5 semanas após fluoxetina',
            'CYP1A2 inibidores (fluvoxamina, ciprofloxacino) → aumento 5x nos níveis de duloxetina',
            'AINEs/anticoagulantes → risco de sangramento aumentado — considerar IBP',
            'Tioridazina → prolongamento de QT — CONTRAINDICADO',
            'Álcool → hepatotoxicidade',
        ],
        'monitoramento': {
            'PA':      'A cada consulta inicialmente, depois a cada 3 meses',
            'TGO_TGP': 'Se surgir sintomas — não rotineiro',
            'Sódio':   'A cada 6 meses em idosos (risco de hiponatremia)',
        },
    },

    # ------------------------------------------------------------------
    # GABAPENTINA / PREGABALINA
    # ------------------------------------------------------------------
    'gabapentina_pregabalina': {
        'nome_display': 'Gabapentina / Pregabalina',
        'indicacoes_msk': [
            'Dor neuropática (radiculopatia, neuropatia periférica)',
            'Componente neuropático em MSK crônico',
        ],
        'dose_por_egfr': {
            'egfr_maior_60':    'Gabapentina até 3600mg/dia | Pregabalina até 600mg/dia',
            'egfr_30_60':       'Gabapentina até 1800mg/dia | Pregabalina 300mg/dia (333mg TID)',
            'egfr_15_30':       'Gabapentina 300-700mg/dia | Pregabalina 150mg/dia',
            'egfr_menor_15':    'Gabapentina 100-300mg pós-diálise | Pregabalina contraindicada',
        },
        'comorbidades': {
            'drc_egfr_menor_60':        ('CUIDADO', 'Eliminação renal obrigatória. Ajuste de dose baseado no CrCl. Alto risco de toxicidade se não ajustado.'),
            'drc_dialise':              ('CUIDADO', 'Gabapentina pós-diálise. Evitar pregabalina. Alto risco de AEM, quedas e fraturas.'),
            'ic':                       ('CUIDADO', 'Pode causar edema periférico.'),
            'idade_acima_65':           ('CUIDADO', 'Iniciar dose baixa (gabapentina ≤ 300mg/dia, pregabalina ≤ 75mg/dia). Alto risco de quedas e fraturas.'),
            'uso_opioides':             ('CUIDADO', 'Depressão respiratória e risco aumentado de mortalidade, especialmente em diálise. Evitar combinação.'),
            'gestacao':                 ('CUIDADO', 'Risco teratogênico. Evitar se possível.'),
        },
        'interacoes_importantes': [
            'Opioides → depressão do SNC + depressão respiratória — mortalidade aumentada em diálise',
            'Benzodiazepínicos → sedação aumentada + risco de quedas — evitar em idosos',
            'Álcool → depressão do SNC',
            'Antiácidos → reduzem absorção da gabapentina em 20-25% — separar por 2 horas',
            'Morfina → aumenta níveis de gabapentina em 44% — monitorar toxicidade',
        ],
        'monitoramento': {
            'funcao_renal': 'Basalmente e a cada 6-12 meses; mais frequente se DRC',
            'avaliacao_clinica': 'A cada consulta: risco de queda, estado mental, edema',
        },
    },

    # ------------------------------------------------------------------
    # CORTICOIDE INJETÁVEL
    # ------------------------------------------------------------------
    'corticoide_injetavel': {
        'nome_display': 'Corticoide injetável (triancinolona / betametasona / metilprednisolona)',
        'doses_por_local': {
            'joelho_intraarticular':    'Triancinolona 20mg + lidocaína 1% 3-4mL | Betametasona 6mg | Agulha 25G 1.5-2"',
            'subacromia_ombro':         'Triancinolona 20-40mg + lidocaína 1% 4-6mL | Betametasona 6mg | Agulha 25G 1.5-2"',
            'glenoumeral':              'Triancinolona 20mg + lidocaína 1% 4-6mL | Betametasona 6mg | Agulha 22 ou 25G 1.5-2"',
            'ac_joint':                 'Triancinolona 10-20mg + lidocaína 1% 0.5-1mL | Betametasona 3-6mg | Agulha 25G 1-1.5"',
            'bursa_anserina':           'Triancinolona 20mg + lidocaína 1% 3-4mL | Betametasona 6mg | Agulha 25G 1.5-2"',
            'bursa_trocanterica':       'Triancinolona 20mg + lidocaína 1% 4-6mL | Betametasona 6mg | Agulha 22G 1.5-2"',
        },
        'comorbidades': {
            'diabetes':                 ('CUIDADO', 'Monitorar glicemia diariamente por 5-7 dias. Pico em 24-72h pós-injeção. Pode atingir > 250mg/dL. Risco maior em HbA1c elevada e injeção no joelho (maior risco que ombro).'),
            'imunossupressao':          ('CI_RELATIVA', 'Contraindicado se infecção ativa. Risco aumentado de infecção. Adiar se possível.'),
            'osteoporose':              ('CUIDADO', 'Limitar dose cumulativa: máximo 200mg de triancinolona/ano em mulheres pós-menopausa. Considerar DEXA se múltiplas injeções planejadas.'),
            'articulacao_prostetica':   ('CI',      'Contraindicado. Alto risco de infecção da prótese.'),
            'infeccao_local_sistemica': ('CI',      'Contraindicado absoluto.'),
            'anticoagulado':            ('CUIDADO', 'Risco aumentado de sangramento. Considerar suspensão temporária se possível.'),
            'idade_acima_65':           ('CUIDADO', 'Maior risco de efeitos sistêmicos e perda de densidade óssea.'),
            'gestacao':                 ('CUIDADO', 'Absorção sistêmica ocorre. Avaliar risco/benefício.'),
        },
        'efeitos_sistemicos': {
            'hiperglicemia':    'Onset: 24-72h. Duração: 5-7 dias. Elevação média 37-80mg/dL; pode atingir >250-300mg/dL.',
            'dmpa_ossea':       'Limiar de risco: > 200mg triancinolona/ano em pós-menopausa. Máximo recomendado: 400mg/3 anos.',
            'supressao_adrenal':'Efeitos sistêmicos podem durar semanas. Sem casos de insuficiência adrenal clínica reportados, mas supressão bioquímica documentada.',
        },
        'frequencia_maxima': 'Intervalo mínimo 6 semanas entre injeções no mesmo sítio. Máximo 3-4 injeções/ano por articulação.',
        'aftercare': [
            'Repouso relativo 24-48h pós-injeção',
            'Gelo local 15-20min se necessário',
            'Flare pós-injeção possível em 2-10% — analgésico simples e gelo por 24-48h',
            'Sinais de alarme infeccioso: febre, rubor progressivo, calor intenso, secreção — retornar imediatamente',
            'Diabéticos: monitorar glicemia diariamente por 5-7 dias',
        ],
        'contraindicacoes_absolutas': [
            'Infecção ativa local ou sistêmica',
            'Articulação protética',
            'Fratura não consolidada no sítio',
            'Suspeita de artrite séptica — aspirar primeiro',
        ],
    },
}


# =============================================================================
# 2. FUNÇÃO AUXILIAR — parsear comorbidades do texto livre do paciente
# =============================================================================

def _parsear_comorbidades(comorbidades_str, idade, medicacoes_str=''):
    """
    Converte string de comorbidades (como registrada no prontuário) em flags.
    Tolerante a variações de escrita.
    """
    c = (comorbidades_str or '').lower()
    m = (medicacoes_str or '').lower()

    flags = set()

    # DRC
    if 'drc' in c or 'renal' in c or 'rim' in c:
        flags.add('drc_qualquer')
        if 'egfr' in c or 'tfg' in c:
            import re
            nums = re.findall(r'\d+', c)
            if nums:
                egfr = int(nums[0])
                if egfr < 15:   flags.add('drc_egfr_menor_15'); flags.add('drc_dialise')
                elif egfr < 30: flags.add('drc_egfr_menor_30')
                elif egfr < 60: flags.add('drc_egfr_30_60'); flags.add('drc_egfr_menor_60')
                else:           flags.add('drc_egfr_maior_60')
        else:
            flags.add('drc_egfr_menor_60')  # conservador se eGFR não especificado

    # Hepático
    if 'cirrose' in c:
        flags.add('cirrose_qualquer')
        if 'descomp' in c: flags.add('cirrose_descompensada')
        else:              flags.add('cirrose_compensada')
    if 'hepat' in c and 'cirrose' not in c:
        flags.add('doenca_hepatica_cronica')

    # Cardiovascular
    if 'has' in c or 'hipertens' in c:
        flags.add('has')
    if any(x in c for x in ['ic ', 'insuficiencia cardiaca', 'insufficiency cardiac']):
        flags.add('ic')
    if any(x in c for x in ['iam', 'infarto', 'coronar', 'dac ']):
        flags.add('doenca_cv')

    # GI
    if any(x in c for x in ['ulcera', 'úlcera', 'gastrite', 'gerd', 'refluxo']):
        if 'ativa' in c or 'ativo' in c:
            flags.add('ulcera_ativa')
        else:
            flags.add('ulcera_historico')

    # Endócrino
    if 'diabet' in c or 'dm2' in c or 'dm1' in c: flags.add('diabetes')
    if 'hipo' in c and 'tireo' in c: flags.add('hipotireoidismo')

    # Neurológico / psiquiátrico
    if any(x in c for x in ['epilep', 'convuls', 'crise', 'seizure']):
        flags.add('epilepsia')

    # Medicações — anticoagulação, SSRIs
    if any(x in m for x in ['warfar', 'rivaroxa', 'apixab', 'dabigatr', 'heparin']):
        flags.add('anticoagulado')
    if any(x in m for x in ['sertral', 'fluoxet', 'escitalo', 'paroxet', 'venlafa',
                              'duloxet', 'desvenlaf', 'clomipram', 'amitriptilin']):
        flags.add('depressao_ssri_snri')

    # Álcool
    if any(x in c for x in ['alcool', 'álcool', 'etilis', 'alcoolismo']):
        flags.add('alcool_cronico')

    # Gestação
    if any(x in c for x in ['gesta', 'gravida', 'grávi', 'prenha']):
        flags.add('gestacao')
        if '3' in c and ('trimest' in c or 'sem' in c):
            flags.add('gestacao_3_trimestre')
        elif '1' in c or '2' in c:
            flags.add('gestacao_1_2_trimestre')

    # Imunossupressão
    if any(x in c for x in ['imunossuprim', 'hiv', 'transplant', 'quimio']):
        flags.add('imunossupressao')

    # Osteoporose
    if 'osteopor' in c:
        flags.add('osteoporose')

    # Prótese
    if any(x in c for x in ['protese', 'prótese', 'artroplast']):
        flags.add('articulacao_prostetica')

    # Idade
    if idade >= 65: flags.add('idade_acima_65')
    if idade >= 70: flags.add('idade_acima_70')

    return flags


# =============================================================================
# 3. FUNÇÃO PRINCIPAL — avaliar analgesia
# =============================================================================

def avaliar_analgesia(medicamentos, comorbidades_str, idade,
                      medicacoes_str='', sito_injecao=None):
    """
    Parâmetros:
        medicamentos     : lista de chaves de PERFIS
                           ex: ['aine_oral', 'paracetamol', 'corticoide_injetavel']
        comorbidades_str : string do prontuário (ex: "HAS, DRC, DM2")
        idade            : int
        medicacoes_str   : string do prontuário (ex: "sertralina 50mg 1-0-0")
        sito_injecao     : str opcional para corticoide
                           ex: 'joelho_intraarticular', 'subacromia_ombro'

    Retorna:
        dict com alertas por medicamento, organizados por nível de urgência
    """
    flags = _parsear_comorbidades(comorbidades_str, idade, medicacoes_str)
    resultado = {}

    for med in medicamentos:
        perfil = PERFIS.get(med)
        if not perfil:
            resultado[med] = {'erro': f'Medicamento "{med}" não encontrado nos perfis.'}
            continue

        alertas_ci       = []
        alertas_cuidado  = []
        alertas_preferir = []
        sem_alerta       = True

        comorbidades_perfil = perfil.get('comorbidades', {})

        for flag in flags:
            if flag in comorbidades_perfil:
                nivel, mensagem = comorbidades_perfil[flag]
                sem_alerta = False
                if nivel in ('CI', 'CI_RELATIVA'):
                    alertas_ci.append((flag, mensagem))
                elif nivel == 'CUIDADO':
                    alertas_cuidado.append((flag, mensagem))
                elif nivel == 'PREFERIR':
                    alertas_preferir.append((flag, mensagem))

        # Dose de corticoide por sítio
        dose_info = None
        if med == 'corticoide_injetavel' and sito_injecao:
            dose_info = perfil.get('doses_por_local', {}).get(sito_injecao)

        resultado[med] = {
            'nome':             perfil.get('nome_display', med),
            'contraindicacoes': alertas_ci,
            'cautelas':         alertas_cuidado,
            'preferencias':     alertas_preferir,
            'sem_alerta':       sem_alerta,
            'interacoes':       perfil.get('interacoes_importantes', []),
            'dose_sitio':       dose_info,
            'aftercare':        perfil.get('aftercare', []),
        }

    return resultado


# =============================================================================
# 4. FORMATADOR PARA O RUNNER
# =============================================================================

def formatar_alertas(resultado_analgesia):
    """
    Converte o resultado de avaliar_analgesia em texto para o runner.
    """
    linhas = []
    for med, dados in resultado_analgesia.items():
        if 'erro' in dados:
            linhas.append(f'  ⚠️  {dados["erro"]}')
            continue

        linhas.append(f'\n  [{dados["nome"]}]')

        if dados['contraindicacoes']:
            for flag, msg in dados['contraindicacoes']:
                linhas.append(f'    ⛔ CONTRAINDICADO ({flag.upper()}): {msg}')

        if dados['cautelas']:
            for flag, msg in dados['cautelas']:
                linhas.append(f'    ⚠️  CAUTELA ({flag.upper()}): {msg}')

        if dados['preferencias']:
            for flag, msg in dados['preferencias']:
                linhas.append(f'    ✅ PREFERIR ({flag.upper()}): {msg}')

        if dados['sem_alerta']:
            linhas.append('    ✅ Sem alertas para o perfil deste paciente.')

        if dados['dose_sitio']:
            linhas.append(f'    📋 Dose: {dados["dose_sitio"]}')

        if dados['interacoes']:
            linhas.append('    Interações a considerar:')
            for i in dados['interacoes'][:3]:  # top 3 mais relevantes
                linhas.append(f'      - {i}')

    return '\n'.join(linhas)


# =============================================================================
# TESTE
# =============================================================================

if __name__ == '__main__':
    casos = [
        {
            'nome': 'Paciente OA — 68 anos, HAS, DRC eGFR 45',
            'medicamentos': ['aine_oral', 'aine_topico', 'paracetamol', 'corticoide_injetavel'],
            'comorbidades': 'HAS, DRC eGFR 45',
            'idade': 68,
            'medicacoes': 'losartana 50mg',
            'sito': 'joelho_intraarticular',
        },
        {
            'nome': 'Dor neuropática — 55 anos, cirrose, usa sertralina',
            'medicamentos': ['tramadol', 'duloxetina', 'gabapentina_pregabalina'],
            'comorbidades': 'cirrose compensada',
            'idade': 55,
            'medicacoes': 'sertralina 50mg 1-0-0',
            'sito': None,
        },
        {
            'nome': 'Ombro — 42 anos, sem comorbidades',
            'medicamentos': ['aine_oral', 'aine_topico', 'paracetamol', 'corticoide_injetavel'],
            'comorbidades': 'nega',
            'idade': 42,
            'medicacoes': 'nega',
            'sito': 'subacromia_ombro',
        },
    ]

    SEP = '=' * 60
    for caso in casos:
        print(f'\n{SEP}')
        print(f'CASO: {caso["nome"]}')
        print(SEP)
        resultado = avaliar_analgesia(
            medicamentos=caso['medicamentos'],
            comorbidades_str=caso['comorbidades'],
            idade=caso['idade'],
            medicacoes_str=caso['medicacoes'],
            sito_injecao=caso['sito'],
        )
        print(formatar_alertas(resultado))