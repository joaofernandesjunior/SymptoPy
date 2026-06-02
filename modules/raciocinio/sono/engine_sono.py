# modules/raciocinio/sono/engine_sono.py
# Motor de raciocínio clínico — Transtornos do Sono
#
# Fontes:
#   AASM 2017 (bruxismo, insônia), ICSD-3, AASM Clinical Practice Guidelines 2017
#   Ashton Protocol (desmame BZD), AASM STOP-BANG 2022
#   Notion "Sono — Insônia, AOS e SPI" (João — 2026-05-30)
#
# Hierarquia de decisão:
#   1. Red flags (TCR-REM > 50 → Parkinson, cataplexia → narcolepsia, Epworth + adormeceu dirigindo)
#   2. AOS suspeita (STOP-BANG ≥ 3)
#   3. Narcolepsia suspeita (cataplexia + hipersonia + fenômenos de REM)
#   4. SPI (4 critérios)
#   5. Bruxismo do sono
#   6. Desmame de benzodiazepínico (já em uso)
#   7. Síndrome da Fase Atrasada (SFAS)
#   8. Parassonias
#   9. Insônia primária → subclassificar por causa (comportamental / psiquiátrica / crônica)

# =============================================================================
# UTILITÁRIOS
# =============================================================================

def _isi_grau(score):
    if score <= 7:   return 'sem_clinica'
    if score <= 14:  return 'leve'
    if score <= 21:  return 'moderada'
    return 'grave'


def _eficiencia_sono(dados):
    cama  = dados.get('horas_cama', 0)
    sono  = dados.get('horas_sono', 0)
    if cama <= 0:
        return None
    return round((sono / cama) * 100)


def _bruxismo_criterios(dados):
    """Retorna número de critérios de bruxismo do sono presentes."""
    return sum([
        dados.get('ranger_dentes', False),
        dados.get('dor_mandibula_manha', False),
        dados.get('cefaleia_temporal_manha', False),
        dados.get('desgaste_dentario', False) or dados.get('desgaste_incisal', False),
        dados.get('dor_atm', False),
        dados.get('masseter_hipertrofia', False),
    ])


def _narcolepsia_score(dados):
    """0–4 pontos de suspeita de narcolepsia."""
    return sum([
        dados.get('cataplexia', False),
        dados.get('alucinacao_adormecer', False),
        dados.get('paralisia_sono', False),
        dados.get('sono_diurno_irresistivel', False),
    ])


def _n_fatores_comportamentais(dados):
    fatores = [
        dados.get('tela_na_cama', False),
        dados.get('alcool_para_dormir', False),
        dados.get('cama_escritorio', False),
        dados.get('exercicio_noturno', False),
        not dados.get('horario_cama_fixo', True),
        dados.get('cochilo_diurno', False) and dados.get('cochilo_duracao_min', 0) > 30,
    ]
    return sum(fatores)


# =============================================================================
# PLANOS ESTRUTURADOS
# =============================================================================

def _cbti_prescricao(dados):
    horas_sono = dados.get('horas_sono', 6)
    janela = max(horas_sono + 0.5, 5.5)
    return {
        'restricao_sono': (
            f'Janela de sono prescrita: {janela:.1f}h por noite\n'
            '    • Definir horário FIXO de acordar e contar para trás\n'
            '    • Não deitar antes do horário prescrito, mesmo com sono\n'
            '    • Após 1–2 semanas com eficiência > 85%: expandir 15 min/semana'
        ),
        'controle_estimulo': (
            'Cama = APENAS sono e sexo\n'
            '    • Se não dormir em 20 min: levantar, fazer algo calmo, voltar só com sono\n'
            '    • Celular fora do quarto — regra não negociável'
        ),
        'higiene': (
            'Horário fixo de acordar TODOS os dias (incluindo fim de semana)\n'
            '    • Sem cafeína após 14h\n'
            '    • Sem tela 60 min antes de dormir\n'
            '    • Quarto: escuro + silencioso + 18–20°C\n'
            '    • Sem exercício físico após 18h'
        ),
        'reestruturacao_cognitiva': (
            'Identificar e desafiar catastrofização:\n'
            '    "Se não dormir 8h estou destruído" → mantém arousal → piora a insônia\n'
            '    Diário de sono: anotar horário deitar/acordar + qualidade (1–10) por 2 semanas'
        ),
    }


def _rx_trazodona():
    return 'Trazodona 50 mg VO à noite (30 min antes de dormir) — sem dependência, sem tolerância'


def _rx_benzo_desmame(dados):
    benzo   = dados.get('benzo_qual', 'benzodiazepínico')
    dose    = dados.get('benzo_dose', '')
    semanas = dados.get('benzo_semanas', 0)
    return {
        'protocolo': (
            f'Desmame gradual de {benzo} {dose} (em uso há {semanas} semanas)\n'
            '    Protocolo Ashton simplificado: reduzir 10% da dose a cada 2 semanas\n'
            '    NÃO suspender abruptamente — risco de convulsão em doses altas'
        ),
        'ponte': (
            'Iniciar Trazodona 50 mg ao deitar 1–2 semanas ANTES de começar o desmame\n'
            '    Melatonina 2 mg de liberação prolongada como suporte adicional'
        ),
        'abstinencia': (
            'Rebote (semanas 1–2): piora da insônia é esperada — não é falha\n'
            '    Abstinência prolongada (> 4 semanas): ansiedade, parestesias, irritabilidade\n'
            '    Se > 40 mg equivalente diazepam: considerar internação + diazepam de troca'
        ),
    }


# =============================================================================
# CLASSIFICADORES PRINCIPAIS
# =============================================================================

def _classificar_insonia(dados, isi_grau, efic, n_comp):
    phq2 = dados.get('phq2_score', 0)
    depressao = dados.get('depressao_ansiedade', False) or phq2 >= 3
    turno = dados.get('turno_irregular', False)
    benzo = dados.get('benzo_em_uso', False)
    dor   = dados.get('dor_cronica_noturna', False)
    tsh_alto = (dados.get('tsh_valor') or 0) > 4.5
    duracao_cr = dados.get('duracao_semanas', 0) >= 12
    noites_cr  = dados.get('noites_por_semana', 0) >= 3

    # Desmame BZD — prioridade antes de tratar insônia primária
    if benzo and dados.get('benzo_semanas', 0) >= 4:
        return {
            'categoria': 'desmame_benzo',
            'diagnostico': 'Insônia por Uso Crônico de Benzodiazepínico / Zolpidem',
            'isi_grau': isi_grau,
            'cbti': _cbti_prescricao(dados),
            'desmame': _rx_benzo_desmame(dados),
            'conduta': [
                'Iniciar CBT-I paralelamente ao desmame — obrigatório',
                'Trazodona 50 mg como ponte durante o desmame',
                f'Reduzir {dados.get("benzo_qual", "BZD")} 10% a cada 2 semanas',
                'Retorno em 2 semanas para monitorar síndrome de abstinência',
            ],
        }

    # Hipotireoidismo
    if tsh_alto:
        return {
            'categoria': 'insonia_hipotireoidismo',
            'diagnostico': f'Insônia secundária a Hipotireoidismo (TSH {dados.get("tsh_valor")} mUI/L)',
            'isi_grau': isi_grau,
            'conduta': [
                'Levotiroxina — dose conforme TSH e peso; insônia tende a resolver',
                'Não tratar insônia com hipnótico antes de corrigir TSH',
                'Solicitar T4 livre + anti-TPO se ainda não colhidos',
            ],
        }

    # Dor crônica
    if dor:
        return {
            'categoria': 'insonia_dor',
            'diagnostico': 'Insônia secundária a Dor Crônica Noturna',
            'isi_grau': isi_grau,
            'conduta': [
                'Tratar a dor de base — insônia é consequência',
                'Amitriptilina 10–25 mg à noite (dupla ação: analgésico + sedativo)',
                'Gabapentina 100–300 mg à noite se dor neuropática',
                'CBT-I como suporte independente da causa da dor',
            ],
        }

    # Psiquiátrica
    if depressao:
        return {
            'categoria': 'insonia_psiquiatrica',
            'diagnostico': 'Insônia em contexto de Depressão/Ansiedade',
            'isi_grau': isi_grau,
            'phq2': phq2,
            'cbti': _cbti_prescricao(dados),
            'conduta': [
                'PHQ-9 completo para estadiar gravidade da depressão',
                'Mirtazapina 15 mg à noite: indicada quando há insônia + depressão + perda de peso',
                'Sertralina 50 mg pela manhã + trazodona 50 mg à noite: depressão moderada-grave',
                'ISRS pode piorar insônia inicialmente (semanas 1–2) — avisar paciente',
                'CBT-I como pilar não farmacológico concomitante',
                'Retorno em 3–4 semanas com PHQ-9',
            ],
        }

    # Turno de trabalho
    if turno:
        return {
            'categoria': 'insonia_turno',
            'diagnostico': 'Distúrbio do Sono por Turno de Trabalho',
            'isi_grau': isi_grau,
            'conduta': [
                'Modafinil 200 mg antes do turno noturno (FDA-aprovado para shift work)',
                'Higiene de sono adaptada ao turno: blackout total durante sono diurno',
                'Melatonina 2–5 mg antes de dormir no dia (após turno noturno)',
                'Evitar luz forte ao sair do plantão (óculos de filtro de luz azul)',
            ],
        }

    # Comportamental — muitos fatores corrigíveis
    if n_comp >= 3:
        return {
            'categoria': 'insonia_comportamental',
            'diagnostico': f'Insônia Comportamental ({n_comp} fatores comportamentais identificados)',
            'isi_grau': isi_grau,
            'eficiencia_sono': efic,
            'cbti': _cbti_prescricao(dados),
            'conduta': [
                'CBT-I é o único tratamento necessário neste caso',
                'Não iniciar hipnótico — causa é comportamental e reversível',
                'Retorno em 3 semanas com diário de sono',
                f'Eficiência de sono atual: {efic}% (meta: > 85%)',
            ],
        }

    # Insônia crônica primária
    if duracao_cr and noites_cr:
        return {
            'categoria': 'insonia_cronica_primaria',
            'diagnostico': f'Insônia Crônica Primária — {_isi_grau_label(isi_grau)}',
            'isi_grau': isi_grau,
            'eficiencia_sono': efic,
            'cbti': _cbti_prescricao(dados),
            'conduta': [
                'CBT-I — 1ª linha (superior a qualquer medicamento a longo prazo)',
                _rx_trazodona() + ' — ponte durante as primeiras 4 semanas de CBT-I',
                'Doxepina 3–6 mg (se insônia de manutenção refratária — única FDA para uso prolongado)',
                f'ISI basal: {dados.get("isi_score", "?")}/28 — repetir em 4 semanas (resposta: queda ≥ 6 pts)',
                'NÃO prescrever: benzodiazepínico ou zolpidem de longa data',
            ],
        }

    # Insônia subaguda / leve
    return {
        'categoria': 'insonia_subaguda',
        'diagnostico': 'Insônia Subaguda / Leve',
        'isi_grau': isi_grau,
        'cbti': _cbti_prescricao(dados),
        'conduta': [
            'CBT-I princípios básicos — geralmente suficiente',
            'Melatonina 1–5 mg 30–60 min antes de dormir (insônia de início)',
            'Não medicar com hipnótico em insônia < 4 semanas sem causa clara',
            'Retorno se persistir > 3 meses → ISI para estadiar gravidade',
        ],
    }


def _isi_grau_label(grau):
    return {'sem_clinica': 'sem significância clínica', 'leve': 'Leve',
            'moderada': 'Moderada', 'grave': 'Grave'}.get(grau, grau)


# =============================================================================
# ENGINE PRINCIPAL
# =============================================================================

def interpretar_sono(dados):
    isi       = dados.get('isi_score', 0)
    stopbang  = dados.get('stopbang_score', 0)
    epworth   = dados.get('epworth_score', 0)
    spi_crit  = dados.get('spi_criterios', 0)
    narco     = _narcolepsia_score(dados)
    brux_crit = _bruxismo_criterios(dados)
    isi_grau  = _isi_grau(isi)
    efic      = _eficiencia_sono(dados)
    n_comp    = _n_fatores_comportamentais(dados)

    # ── RED FLAG 1: TCR-REM > 50 anos → marcador pré-Parkinson ──────
    if dados.get('tcr_rem_age_sonhos') and dados.get('idade_tcr', 0) >= 50:
        return {
            'categoria': 'tcr_rem_pre_parkinson',
            'diagnostico': 'Transtorno Comportamental do Sono REM — Marcador de Sinucleinopatia',
            'urgencia': 'encaminhar_neurologia',
            'conduta': [
                'ENCAMINHAR NEUROLOGIA — TCR-REM em > 50 anos: 80–90% desenvolve Parkinson/DLB em 10–15 anos',
                'Rastrear: anosmia, constipação, hipotensão ortostática (sinais precoces)',
                'Enquanto aguarda: Clonazepam 0,25–0,5 mg à noite (reduz lesão ao parceiro)',
                'Segurança no quarto: remover objetos pontiagudos, barreira na cama',
                'PSG com vídeo para confirmação diagnóstica',
            ],
        }

    # ── RED FLAG 2: Narcolepsia suspeita ─────────────────────────────
    if narco >= 2:
        return {
            'categoria': 'narcolepsia_suspeita',
            'diagnostico': f'Narcolepsia Suspeita ({narco}/4 critérios)',
            'criterios': {
                'cataplexia': dados.get('cataplexia'),
                'alucinacao_hipnagogica': dados.get('alucinacao_adormecer'),
                'paralisia_sono': dados.get('paralisia_sono'),
                'sono_diurno_irresistivel': dados.get('sono_diurno_irresistivel'),
            },
            'urgencia': 'encaminhar_neurologia_sono',
            'conduta': [
                'Encaminhar medicina do sono / neurologia para PSG + MSLT confirmatório',
                'Enquanto aguarda confirmação:',
                '  Modafinil 200 mg pela manhã (sonolência) — Schedule IV',
                '  Para cataplexia (se presente): Imipramina 75–100 mg/dia',
                'Orientar: NÃO dirigir até diagnóstico confirmado',
                'Medidas comportamentais: 2 cochilos programados de 20 min/dia melhoram função',
            ],
        }

    # ── AOS suspeita (STOP-BANG ≥ 3) ─────────────────────────────────
    if stopbang >= 3:
        imc  = dados.get('imc', 0)
        circ = dados.get('circunferencia_cervical_cm', 0)
        mall = dados.get('mallampati', 0)
        sexo_m = dados.get('stopbang_itens', {}).get('masculino', False)
        circ_limite = 43 if sexo_m else 40
        return {
            'categoria': 'aos_suspeita',
            'diagnostico': f'Apneia Obstrutiva do Sono — Alto Risco (STOP-BANG {stopbang}/8)',
            'stopbang': stopbang,
            'epworth': epworth,
            'imc': imc,
            'circunferencia_cervical': circ,
            'mallampati': mall,
            'risco_grave': stopbang >= 5 or (stopbang >= 3 and epworth >= 10),
            'conduta': [
                f'Solicitar polissonografia (ou poligrafia doméstica se disponível)',
                f'Encaminhar pneumologia / medicina do sono',
                f'STOP-BANG {stopbang}/8 | Epworth {epworth}/24 | IMC {imc} | Pescoço {circ} cm',
                'NÃO prescrever BZD, zolpidem ou opioides — risco de depressão respiratória em AOS',
                'Perda de peso: única intervenção que pode curar a AOS',
                'Posição lateral: AOS posicional → treino com travesseiro nas costas',
                'Evitar álcool e sedativos à noite',
                'Se IAH ≥ 15 confirmado → CPAP (titulado pelo especialista)',
            ] + (['⚠️  JÁ ADORMECEU DIRIGINDO — ORIENTAR NÃO DIRIGIR até diagnóstico'] if epworth >= 15 else []),
        }

    # ── SPI — 4 critérios ────────────────────────────────────────────
    if spi_crit == 4:
        ferritina = dados.get('ferritina_valor')
        ferr_baixa = ferritina is not None and ferritina < 50
        return {
            'categoria': 'spi',
            'diagnostico': 'Síndrome das Pernas Inquietas — 4 critérios obrigatórios presentes',
            'ferritina': ferritina,
            'conduta': [
                '1º passo: ferritina + ferro sérico + B12 + creatinina + glicemia (excluir causas)'
                if ferritina is None else
                f'Ferritina = {ferritina} ng/mL' + (' → REPOR FERRO (meta > 75 ng/mL)' if ferr_baixa else ' — adequada'),
                'Se ferritina < 50: Sulfato ferroso 300 mg 2x/dia em jejum × 3 meses',
                'Se ferro normal ou persistência: Pramipexol 0,125 mg 2–3h antes de dormir',
                '  → Pode aumentar para 0,25 mg após 1 semana',
                'Alternativa: Gabapentina 300 mg 2h antes de dormir (SPI + dor neuropática)',
                '⚠️  Augmentation (piora paradoxal com dopaminérgico): reduzir dose ou trocar para gabapentina',
                'Evitar: metoclopramida, haloperidol, ISRS (pioram SPI)',
                'Encaminhar neurologia se augmentation ou SPI na gravidez',
            ],
        }

    # ── Bruxismo do sono ─────────────────────────────────────────────
    if brux_crit >= 2:
        isrs = dados.get('isrs_em_uso', False)
        aos_coexiste = stopbang >= 3
        return {
            'categoria': 'bruxismo_sono',
            'diagnostico': f'Bruxismo do Sono ({brux_crit}/6 critérios)',
            'criterios_presentes': {
                'ranger_dentes': dados.get('ranger_dentes'),
                'dor_mandibula': dados.get('dor_mandibula_manha'),
                'cefaleia_temporal': dados.get('cefaleia_temporal_manha'),
                'desgaste': dados.get('desgaste_dentario') or dados.get('desgaste_incisal'),
                'dor_atm': dados.get('dor_atm'),
                'masseter': dados.get('masseter_hipertrofia'),
            },
            'isrs_associado': isrs,
            'aos_coexiste': aos_coexiste,
            'conduta': _conduta_bruxismo(dados, isrs, aos_coexiste),
        }

    # ── Fase atrasada do sono ────────────────────────────────────────
    if dados.get('dorme_bem_horario_proprio') and dados.get('dificuldade_iniciar'):
        return {
            'categoria': 'sfas',
            'diagnostico': 'Síndrome da Fase Atrasada do Sono (SFAS)',
            'conduta': [
                'Fototerapia: 10.000 lux IMEDIATAMENTE ao acordar × 30 min (lâmpada dedicada — não tela)',
                '  → Início: 2–4 semanas para adiantar fase; manutenção 3–5x/semana',
                'Melatonina 0,5 mg (dose baixa — ação cronobiológica, não sedativa)',
                '  → Tomar 5–6h ANTES do horário DESEJADO de adormecer',
                '  → Ex: quer dormir às 23h → tomar às 17–18h',
                'Combinação: fototerapia matinal + melatonina tarde = abordagem mais eficaz',
                'Obrigatório evitar: luz brilhante após 21h, cochilo compensatório, irregularidade no fim de semana',
                'NÃO prescrever hipnótico — não é insônia, é dessincronização circadiana',
            ],
        }

    # ── Parassonias NREM ─────────────────────────────────────────────
    if dados.get('sonambulismo') or dados.get('terror_noturno'):
        return {
            'categoria': 'parassonia_nrem',
            'diagnostico': 'Parassonia NREM (Terror Noturno / Sonambulismo)',
            'conduta': [
                'Tranquilizar: benigno em crianças, tende a remitir',
                'Segurança ambiental: janelas/portas com trava, remover objetos cortantes',
                'Tratar privação de sono (principal fator precipitante)',
                'Se recorrente em adulto: Clonazepam 0,25–0,5 mg ao deitar',
                'Investigar AOS coexistente — microdespertares de AOS precipitam parassonias NREM',
                'PSG se episódios frequentes + risco de lesão + adulto',
            ],
        }

    # ── Pesadelos + TEPT ─────────────────────────────────────────────
    if dados.get('pesadelos_freq') and dados.get('pesadelos_trauma'):
        return {
            'categoria': 'pesadelos_tept',
            'diagnostico': 'Pesadelos Recorrentes — Investigar TEPT',
            'conduta': [
                'PCL-5 ou CAPS-5 para rastrear TEPT',
                'Prazosina 1–4 mg ao deitar (1ª linha farmacológica para pesadelos de TEPT)',
                '  → Iniciar 1 mg, titular semanalmente; monitorar hipotensão ortostática',
                'Encaminhar psicologia/psiquiatria para Terapia de Reprocessamento (EMDR) / TCC-TEPT',
                'Sertralina 50–200 mg (1ª linha para TEPT global, não específico para pesadelos)',
            ],
        }

    # ── Sem diagnóstico específico — insônia como queixa predominante
    return _classificar_insonia(dados, isi_grau, efic, n_comp)


def _conduta_bruxismo(dados, isrs, aos_coexiste):
    linhas = [
        '── Não farmacológico (sempre — 1ª linha):',
        'Placa oclusal RÍGIDA (acrílico duro) — superior à mole, encaminhar dentista/protesista',
        '  • Mole alivia sintomas mas não reduz atividade muscular (evidência inferior)',
        'Fisioterapia mandibular: abertura máxima 10s × 5 rep, 2x/dia + calor local 15 min',
        'Reduzir cafeína (especialmente à tarde) e álcool noturno',
        'Manejo de estresse: exercício físico, TCC, mindfulness',
        '',
        '── Farmacológico:',
        '1ª linha: Ciclobenzaprina 5–10 mg VO ao deitar',
        '  • Iniciar 5 mg; aumentar para 10 mg após 1 semana se necessário',
        '  • Duração: 2–4 semanas (tolerância com uso crônico)',
        '  • Evitar: > 65 anos, glaucoma, HPB, IRC grave, uso de IMAO',
        '  • Interações: álcool, BZD, tramadol',
        '',
        '2ª linha (ansiedade proeminente ou idoso): Clonazepam 0,5–1 mg ao deitar',
        '  • Risco de dependência > 4 semanas — uso consciente',
        '',
        '3ª linha (refratário + hipertrofia de masseter): Toxina botulínica — encaminhar',
        '  • 25–50 U por masseter (botox), efeito em 1–2 sem, dura 3–6 meses',
        '  • Encaminhar: neurologista ou dentista especialista em DTM',
    ]

    if isrs:
        linhas += [
            '',
            '⚠️  ISRS em uso — ISRS pode ser causa do bruxismo:',
            '  • Tentar: Buspirona 5–10 mg 2x/dia (reduz bruxismo induzido por ISRS sem trocar AD)',
            '  • Alternativa: trocar fluoxetina/sertralina por mirtazapina ou duloxetina',
            '  • NÃO suspender ISRS abruptamente',
        ]

    if aos_coexiste:
        linhas += [
            '',
            '⚠️  AOS coexistente — bruxismo frequentemente é microdespertar por apneia:',
            '  • Tratar AOS primeiro (CPAP pode resolver bruxismo em 50% dos casos)',
        ]

    linhas += [
        '',
        'Red flags → dentista urgente:',
        '  Fratura dentária, mobilidade dentária, travamento de mandíbula, dor intensa refratária',
    ]
    return linhas
