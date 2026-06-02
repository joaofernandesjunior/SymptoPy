# modules/raciocinio/linfadenopatia/engine_linfadenopatia.py
# Motor de raciocínio clínico — Linfadenopatia em Adultos
#
# Fontes:
#   AAFP 2016 (Lymphadenopathy), ASH guidelines
#   Open Evidence 2026 (lymphadenopathy algorithm)
#
# Hierarquia:
#   1. Red flags → encaminhamento urgente hematologia/oncologia
#   2. Localização supraclavicular/epitroclear/poplíteo → biópsiar sempre
#   3. Generalizada sem causa → investigação completa
#   4. Diagnóstico específico (EBV, cat-scratch, TB, bacteriana)
#   5. Decisão de biópsia vs. observação (algoritmo AAFP)


# =============================================================================
# UTILITÁRIOS
# =============================================================================

_LOCAIS_SEMPRE_BIOPSIA = {'supraclavicular', 'epitroclear', 'popliteo'}


def _red_flags(dados):
    flags = []
    if dados.get('b_symptoms') or dados.get('febre_sem_foco'):
        flags.append('Sintomas B (febre/sudorese noturna/perda de peso)')
    if dados.get('localizacao') in _LOCAIS_SEMPRE_BIOPSIA:
        flags.append(f'Localização {dados["localizacao"]} — sempre patológico')
    if dados.get('textura') == 'duro_fixo':
        flags.append('Consistência dura, pétrea ou fixa')
    if dados.get('crescimento_rapido'):
        flags.append('Crescimento rápido (> 1 cm em < 2 semanas)')
    if dados.get('esplenomegalia'):
        flags.append('Esplenomegalia ao exame')
    if dados.get('alargamento_mediastino'):
        flags.append('Alargamento de mediastino ao RX')
    if dados.get('hemoptise'):
        flags.append('Hemoptise')
    if dados.get('pancitopenia') or dados.get('blastos'):
        flags.append('Pancitopenia ou blastos no hemograma')
    ldh = dados.get('ldh_valor')
    if ldh and ldh > 400:
        flags.append(f'LDH marcadamente elevado ({ldh} U/L)')
    if dados.get('idade', 0) > 40 and not _tem_causa_infecciosa_clara(dados):
        flags.append('Idade > 40 anos com adenopatia sem causa infecciosa clara')
    return flags


def _tem_causa_infecciosa_clara(dados):
    return any([
        dados.get('faringite_recente'),
        dados.get('problema_dental'),
        dados.get('infeccao_pele_cab'),
        dados.get('infeccao_mmss'),
        dados.get('infeccao_mmii'),
        dados.get('pele_sobre_linfonodo') and dados.get('doloroso'),
        dados.get('vacina_recente_ax'),
        dados.get('monospot_positivo'),
        dados.get('exposicao_gato'),
    ])


def _biopsia_indicada(dados):
    """Critérios AAFP 2016 para biópsia."""
    loc       = dados.get('localizacao', '')
    tamanho   = dados.get('tamanho_cm', 0)
    duracao   = dados.get('duracao_semanas', 0)
    textura   = dados.get('textura', '')
    idade     = dados.get('idade', 0)
    bs        = dados.get('b_symptoms', False)
    atb_sem_melhora = dados.get('atb_em_uso') and not dados.get('melhora_atb') and dados.get('atb_duracao', 0) >= 14
    pancito   = dados.get('pancitopenia') or dados.get('blastos')
    generaliz = loc == 'generalizado'

    return any([
        loc in _LOCAIS_SEMPRE_BIOPSIA,
        bs,
        (tamanho > 2 and duracao > 4),
        textura == 'duro_fixo',
        (idade > 40 and not _tem_causa_infecciosa_clara(dados)),
        atb_sem_melhora,
        pancito,
        (generaliz and not _tem_causa_infecciosa_clara(dados)),
    ])


# =============================================================================
# DIAGNÓSTICOS ESPECÍFICOS
# =============================================================================

def _dx_ebv(dados):
    return {
        'categoria': 'ebv_mononucleose',
        'diagnostico': 'Mononucleose Infecciosa (EBV)',
        'padrao': 'Tríade: febre + faringite + adenopatia cervical posterior',
        'exames': [
            'Monospot (heterofilia) — sensib. 87%, especif. 91%',
            'Se monospot negativo + alta suspeita: EBV VCA IgM/IgG (mais sensível)',
            'Hemograma: > 40% linfócitos + > 10% atípicos',
            'Transaminases (eleva em 80% dos casos)',
        ],
        'tratamento': {
            'suporte': 'Repouso, hidratação, AINEs/paracetamol para febre e dor',
            'esporte': 'Proibir contato físico por 3 semanas (risco de ruptura esplênica)',
            'antibiotico': '⚠️  NUNCA amoxicilina/ampicilina → rash maculopapular em 80–100%',
            'corticoide': (
                'NÃO indicado de rotina\n'
                'Indicar APENAS: obstrução de via aérea por amígdalas / plaquetopenia grave com sangramento / anemia hemolítica\n'
                'Dose: Prednisona 1 mg/kg/dia (máx 60 mg) × 5–7 dias → desmame'
            ),
        },
        'encaminhamento': None,
        'biopsia': False,
    }


def _dx_cat_scratch(dados):
    return {
        'categoria': 'doenca_arranhadura_gato',
        'diagnostico': 'Doença da Arranhadura do Gato (Bartonella henselae)',
        'padrao': 'Arranhadura de gato + adenopatia axilar/cervical 1–3 semanas após',
        'exames': [
            'Sorologia Bartonella henselae IgM/IgG (se diagnóstico incerto)',
            'Hemograma (geralmente normal)',
        ],
        'tratamento': {
            'suporte': 'Autolimitado em imunocompetentes — reassurance + observação é aceitável',
            'farmacologico': (
                'Azitromicina 500 mg VO D1 → 250 mg D2–D5\n'
                'Reduz volume do linfonodo em ~50% aos 30 dias'
            ),
        },
        'encaminhamento': None,
        'biopsia': False,
    }


def _dx_bacteriana(dados):
    loc = dados.get('localizacao', '')
    return {
        'categoria': 'linfadenite_bacteriana',
        'diagnostico': f'Linfadenite Bacteriana ({loc})',
        'padrao': 'Linfonodo doloroso + eritema/calor/flutuação + fonte infecciosa no território de drenagem',
        'exames': [
            'Hemograma (leucocitose com desvio à esquerda)',
            'PCR/VHS',
            'Cultura de material se flutuação/drenagem',
        ],
        'tratamento': {
            'primeira_linha': (
                'Amoxicilina-clavulanato 875/125 mg VO 12/12h × 10 dias\n'
                'OU Cefalexina 500 mg VO 6/6h × 10 dias'
            ),
            'mrsa': (
                'Se MRSA suspeito (sem melhora ou hospitalar):\n'
                'Clindamicina 300–450 mg VO 8/8h × 10 dias\n'
                'OU TMP-SMX DS VO 12/12h × 10 dias'
            ),
            'reavaliacao': 'Reassessar em 2–4 semanas — sem melhora → biópsia',
        },
        'encaminhamento': None,
        'biopsia': False,
    }


def _dx_tb(dados):
    return {
        'categoria': 'tb_linfadenopatia',
        'diagnostico': 'Linfadenite Tuberculosa (Escrófula) — suspeita',
        'padrao': 'IGRA/PPD positivo + fator de risco + adenopatia cervical crônica',
        'exames': [
            'IGRA (QuantiFERON-TB Gold) se não realizado',
            'RX tórax (TB pulmonar associada?)',
            'PAAF → baciloscopia + cultura de BAAR + histopatologia',
            'Se PAAF não diagnóstica: biópsia excisional',
        ],
        'tratamento': {
            'conduta': 'Encaminhar infectologia — esquema RIPE × 6–9 meses',
            'notificacao': '⚠️  Notificação compulsória obrigatória',
        },
        'encaminhamento': 'Infectologia — urgente',
        'biopsia': True,
    }


def _dx_hiv_primario(dados):
    return {
        'categoria': 'hiv_infeccao_primaria',
        'diagnostico': 'Infecção Aguda por HIV — Síndrome Retroviral Aguda',
        'padrao': 'Adenopatia generalizada + comportamento de risco + síndrome mono-like',
        'exames': [
            'HIV Ag/Ab 4ª geração (detecta antes da soroconversão completa)',
            'Carga viral HIV se teste reagente',
            'CBC, transaminases, RPR',
        ],
        'tratamento': {
            'conduta': 'Encaminhar serviço de HIV/infectologia imediatamente',
            'urgencia': 'Início de TARV precoce melhora desfechos — não aguardar CD4',
        },
        'encaminhamento': 'Infectologia / SAE — urgente',
        'biopsia': False,
    }


def _dx_hernia_inguinal(dados):
    abaixo = dados.get('abaixo_lig_inguinal', False)
    tipo   = 'Femoral' if abaixo else 'Inguinal'
    escroto = dados.get('extensao_escrotal', False)
    return {
        'categoria': f'hernia_{tipo.lower()}_suspeita',
        'diagnostico': f'Hérnia {tipo} Suspeita',
        'padrao': (
            f'Massa {"abaixo" if abaixo else "acima"} do ligamento inguinal · '
            f'{"Redutível" if dados.get("redutivel") else "Não redutível"} · '
            f'{"Extensão escrotal" if escroto else "Sem extensão escrotal"}'
        ),
        'exames': [
            'Exame físico com manobra de Valsalva e palpação do anel inguinal',
            'Ultrassonografia inguinal (diferencia hérnia de linfonodo/lipoma/hidrocele)',
            'Se dúvida diagnóstica ou irredutível → cirurgia',
        ],
        'tratamento': {
            'conduta': (
                f'Encaminhar cirurgia geral — hérnia {tipo.lower()} tem indicação cirúrgica\n'
                f'{"⚠️  Hérnia femoral: maior risco de encarceramento — encaminhar com maior urgência" if abaixo else ""}'
                '\nOrientar: evitar esforço físico intenso até avaliação cirúrgica'
            ),
            'nao_operar': (
                'Hérnia inguinal assintomática em adulto: vigilância aceitável se ≥ 60 anos e baixo risco cirúrgico\n'
                'Criança: operar eletivamente (risco de encarceramento é maior em < 1 ano)'
            ),
            'urgencia': (
                '⚠️  Encarceramento (irredutível + dor + defesa): PS imediato\n'
                'Estrangulamento (dor intensa + vômito + febre): cirurgia de emergência'
            ),
        },
        'encaminhamento': f'Cirurgia geral{"" if not abaixo else " — com prioridade (femoral)"}',
        'biopsia': False,
    }


def _dx_hernia_diferencial_incerto(dados):
    """Quando não há critérios suficientes para distinguir."""
    return {
        'categoria': 'massa_inguinal_diferencial',
        'diagnostico': 'Massa Inguinal — Diferencial Incerto (linfonodo vs. hérnia)',
        'padrao': 'Massa inguinal sem critérios definitivos para hérnia ou linfadenopatia',
        'exames': [
            'Ultrassonografia inguinal — exame de escolha para diferenciação',
            '  → Linfonodo: estrutura oval, hilo ecogênico, sem peristaltismo',
            '  → Hérnia: conteúdo intestinal com peristaltismo, expansível ao Valsalva',
            '  → Hidrocele: anecogênica, transillumina',
            'Hemograma + PCR se suspeita inflamatória/infecciosa',
        ],
        'tratamento': {
            'conduta': 'Solicitar US inguinal antes de qualquer conduta\nRetornar com resultado para reclassificação',
        },
        'encaminhamento': 'Cirurgia geral se hernia confirmada | Hematologia se linfoma suspeito',
        'biopsia': False,
    }


def _dx_linfonodo_inguinal_benigno(dados):
    """Linfonodos inguinais benignos — achado frequente."""
    return {
        'categoria': 'linfadenopatia_inguinal_benigna',
        'diagnostico': 'Linfonodomegalia Inguinal Benigna / Reativa',
        'padrao': (
            'Múltiplos linfonodos moles, móveis, sem Valsalva positivo · '
            f'Sem sintomas B · < 2 cm · {dados.get("duracao_semanas", "?")} semanas'
        ),
        'exames': [
            'Hemograma (geralmente normal)',
            'VDRL/RPR + HIV se história sexual relevante',
            'Ultrassonografia se dúvida com hérnia ou tamanho > 1,5 cm',
        ],
        'tratamento': {
            'conduta': (
                'Observação 4 semanas\n'
                'Linfonodos inguinais de até 1,5–2 cm são achado frequente em adultos jovens '
                '(drenagem de MMII, genitais, ânus — qualquer microtrauma pode reativá-los)\n'
                'Orientar: não há necessidade de tratamento se causa reativa identificada'
            ),
            'retorno': 'Se crescimento, endurecimento, sintomas B ou > 4 semanas sem melhora → biópsia',
        },
        'encaminhamento': None,
        'biopsia': False,
    }


def _dx_ist(dados):
    return {
        'categoria': 'ist_linfadenopatia_inguinal',
        'diagnostico': 'Linfadenopatia Inguinal por IST',
        'padrao': 'Adenopatia inguinal + contato sexual + sintomas genitais',
        'exames': [
            'VDRL/RPR (sífilis)',
            'PCR para Chlamydia/Gonorreia (urina ou swab)',
            'HSV PCR se úlcera genital',
            'HIV Ag/Ab 4ª geração',
            'Considerar LGV (Chlamydia sorotipos L1–L3) se adenopatia bulhosa',
        ],
        'tratamento': {
            'sifilis': 'Penicilina G Benzatina 2,4 milhões UI IM DU (primária)',
            'lgv': 'Doxiciclina 100 mg VO 12/12h × 21 dias',
            'herpes': 'Aciclovir 400 mg VO 8/8h × 7–10 dias (1ª crise)',
        },
        'encaminhamento': None,
        'biopsia': False,
    }


def _dx_linfoma(dados):
    loc = dados.get('localizacao', '')
    idade = dados.get('idade', 0)
    hodgkin = (15 <= idade <= 35) or idade > 60
    return {
        'categoria': 'linfoma_suspeito',
        'diagnostico': f'Linfoma {"Hodgkin" if hodgkin else "Não-Hodgkin"} — Suspeito',
        'padrao': (
            'Linfonodo borrachoso, não doloroso, progressivo'
            + (' + sintomas B' if dados.get('b_symptoms') else '')
            + f' — {"Hodgkin: bimodal 15–35 e > 60 anos" if hodgkin else "LNH: adultos > 60 anos"}'
        ),
        'exames': [
            'Hemograma com diferencial',
            'LDH, β2-microglobulina',
            'VHS, PCR',
            'Ácido úrico, função hepática/renal',
            'RX tórax (alargamento de mediastino?)',
        ],
        'tratamento': {
            'conduta': 'ENCAMINHAR HEMATOLOGIA/ONCOLOGIA com urgência — todos os exames em mãos',
            'biopsia': 'Biópsia excisional preferida (preserva arquitetura) — não PAAF isolada',
            'atencao': '⚠️  NÃO prescrever corticoide antes da biópsia — mascara o diagnóstico histológico',
        },
        'encaminhamento': 'Hematologia/oncologia — urgente (1 semana)',
        'biopsia': True,
    }


def _dx_metastatico(dados):
    loc = dados.get('localizacao', '')
    primario = {
        'supraclavicular': 'Esquerda → TGI (gástrico, pâncreas), pulmão, mama; Direita → pulmão, esôfago',
        'axilar': 'Mama, pulmão, melanoma de MMSS',
        'cervical': 'Cabeça e pescoço (orofaringe, tireoide, parótida), pulmão',
        'inguinal': 'Genitais, bexiga, reto, melanoma de MMII',
    }.get(loc, 'Buscar tumor primário conforme localização')

    return {
        'categoria': 'neoplasia_metastatica',
        'diagnostico': 'Adenopatia Metastática — Tumor Primário a Identificar',
        'padrao': f'Linfonodo duro, fixo, indolor, > 40 anos, tabagismo | {primario}',
        'exames': [
            'RX tórax + TC tórax/abdome/pelve',
            'Endoscopia alta e/ou colonoscopia se TGI suspeito',
            'Mamografia se mulher (axilar/supraclavicular)',
            'PSA se homem > 50 anos',
        ],
        'tratamento': {
            'conduta': 'Encaminhar oncologia — biópsia excisional para diagnóstico histológico',
        },
        'encaminhamento': 'Oncologia — urgente',
        'biopsia': True,
    }


# =============================================================================
# ENGINE PRINCIPAL
# =============================================================================

def interpretar_linfadenopatia(dados):
    flags   = _red_flags(dados)
    loc     = dados.get('localizacao', '')
    tamanho = dados.get('tamanho_cm', 0)
    duracao = dados.get('duracao_semanas', 0)
    textura = dados.get('textura', '')
    idade   = dados.get('idade', 0)
    bs      = dados.get('b_symptoms', False)
    biopsia = _biopsia_indicada(dados)

    # ── 1. Linfonodo supraclavicular/epitroclear/poplíteo → sempre biópsiar
    if loc in _LOCAIS_SEMPRE_BIOPSIA:
        # Tenta definir se metastático ou linfoma
        if textura == 'duro_fixo' or idade > 50 or dados.get('tabagismo'):
            return {**_dx_metastatico(dados), 'red_flags': flags}
        return {**_dx_linfoma(dados), 'red_flags': flags}

    # ── 2. Red flags → encaminhamento urgente
    if len(flags) >= 2 or bs or dados.get('pancitopenia') or dados.get('blastos'):
        if textura == 'duro_fixo' or idade > 50:
            return {**_dx_metastatico(dados), 'red_flags': flags}
        return {**_dx_linfoma(dados), 'red_flags': flags}

    # ── 3. HIV primário (generalizado + risco)
    if (loc == 'generalizado' or dados.get('comportamento_risco_hiv')) and not dados.get('hiv_testado'):
        return {**_dx_hiv_primario(dados), 'red_flags': flags}

    # ── 4. Mononucleose (EBV) — tríade ou monospot+
    if dados.get('sindrome_mono') or dados.get('monospot_positivo'):
        return {**_dx_ebv(dados), 'red_flags': flags}

    # ── 5. Arranhadura de gato
    if dados.get('exposicao_gato') and loc == 'axilar':
        return {**_dx_cat_scratch(dados), 'red_flags': flags}

    # ── 6. TB
    if dados.get('igra_positivo') or (dados.get('risco_tb') and duracao > 4):
        return {**_dx_tb(dados), 'red_flags': flags}

    # ── 7. Diferencial inguinal: hérnia vs. linfonodo ────────────────
    if loc == 'inguinal':
        valsalva   = dados.get('aumenta_valsalva', False)
        redutivel  = dados.get('redutivel', False)
        sons_int   = dados.get('sons_intestinais', False)
        multiplos  = dados.get('multiplos_nodulos', False)

        # Hérnia — critérios positivos
        if valsalva and (redutivel or sons_int or dados.get('extensao_escrotal')):
            return {**_dx_hernia_inguinal(dados), 'red_flags': flags}

        # Hérnia femoral — abaixo do ligamento sem múltiplos nódulos
        if dados.get('abaixo_lig_inguinal') and not multiplos:
            return {**_dx_hernia_inguinal(dados), 'red_flags': flags}

        # Diferencial incerto — Valsalva positivo mas sem outros critérios
        if valsalva and not multiplos and not dados.get('contato_sexual_recente'):
            return {**_dx_hernia_diferencial_incerto(dados), 'red_flags': flags}

        # Múltiplos + mole + sem Valsalva → linfonodo benigno/reativo
        if multiplos and not valsalva and not dados.get('contato_sexual_recente') and tamanho < 2:
            return {**_dx_linfonodo_inguinal_benigno(dados), 'red_flags': flags}

    # ── 7b. IST inguinal
    if loc == 'inguinal' and dados.get('contato_sexual_recente'):
        return {**_dx_ist(dados), 'red_flags': flags}

    # ── 8. Bacteriana com fonte clara + características inflamatórias
    if _tem_causa_infecciosa_clara(dados) and dados.get('doloroso') and dados.get('pele_sobre_linfonodo'):
        return {**_dx_bacteriana(dados), 'red_flags': flags}

    # ── 9. Biópsia indicada sem diagnóstico específico
    if biopsia:
        # Suspeita predominante: linfoma vs. metástase
        if textura == 'duro_fixo' or (idade > 50 and dados.get('tabagismo')):
            return {**_dx_metastatico(dados), 'red_flags': flags, 'motivo_biopsia': _motivo_biopsia(dados)}
        return {**_dx_linfoma(dados), 'red_flags': flags, 'motivo_biopsia': _motivo_biopsia(dados)}

    # ── 10. Observação — causa infecciosa provável, baixo risco
    causa = _causa_reativa_provavel(dados)
    return {
        'categoria': 'linfadenopatia_reativa',
        'diagnostico': f'Linfadenopatia Reativa — provavelmente {causa}',
        'red_flags': flags,
        'biopsia': False,
        'padrao': (
            f'Local: {loc} | Tamanho: {tamanho} cm | Duração: {duracao} semanas\n'
            f'Textura: {textura} | Doloroso: {dados.get("doloroso")} | Idade: {idade} anos'
        ),
        'exames': [
            'Hemograma com diferencial',
            'Monospot se tríade infecciosa (febre + faringite + adenopatia)',
            'VHS, PCR',
        ],
        'tratamento': {
            'conduta': (
                f'Observar 2–4 semanas — tratar causa infecciosa identificada\n'
                f'Reassessar: se não melhorar ou crescer → solicitar hemograma + LDH + biópsia'
            ),
            'atb': 'Não prescrever antibiótico empírico para a adenopatia isolada',
        },
        'encaminhamento': None,
        'retorno': 'Retornar em 4 semanas ou antes se: crescimento, sintomas B, novos linfonodos',
    }


def _motivo_biopsia(dados):
    motivos = []
    if dados.get('localizacao') in _LOCAIS_SEMPRE_BIOPSIA:
        motivos.append(f'Localização {dados["localizacao"]} (sempre patológico)')
    if dados.get('b_symptoms'):
        motivos.append('Sintomas B presentes')
    if dados.get('tamanho_cm', 0) > 2 and dados.get('duracao_semanas', 0) > 4:
        motivos.append(f'Tamanho {dados["tamanho_cm"]} cm por {dados["duracao_semanas"]} semanas')
    if dados.get('textura') == 'duro_fixo':
        motivos.append('Consistência dura/fixa')
    if dados.get('idade', 0) > 40 and not _tem_causa_infecciosa_clara(dados):
        motivos.append('Idade > 40 sem causa infecciosa clara')
    if dados.get('atb_em_uso') and not dados.get('melhora_atb'):
        motivos.append('Sem resposta ao antibiótico em 2 semanas')
    if dados.get('pancitopenia') or dados.get('blastos'):
        motivos.append('Alteração no hemograma (pancitopenia/blastos)')
    return motivos


def _causa_reativa_provavel(dados):
    if dados.get('faringite_recente') or dados.get('sindrome_mono'):
        return 'infecção de vias aéreas superiores / EBV'
    if dados.get('problema_dental'):
        return 'origem dentária'
    if dados.get('infeccao_mmss'):
        return 'infecção do membro superior'
    if dados.get('infeccao_mmii'):
        return 'infecção do membro inferior'
    if dados.get('vacina_recente_ax'):
        return 'reação pós-vacinal'
    if dados.get('medicamentos_culpados'):
        return 'reação medicamentosa'
    return 'causa infecciosa/reativa inespecífica'
