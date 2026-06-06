# modules/raciocinio/consciencia/engine_consciencia.py
# Motor — Alteração do Nível de Consciência (ANC)
#
# Correções aplicadas (2026-06-01):
#   [C1] Tiamina ANTES da glicose se etilismo/desnutrição — paradoxo Wernicke resolvido
#   [C2] Choque hemodinâmico como STEP 0 (antes do neurológico)
#   [C3] Glasgow ≤ 8: proteção de VA roda EM PARALELO com causas reversíveis
#   [C4] Meningite: sequência explícita hemocult → ATB+Dexa → TC → PL
#   [C5] Status epilepticus: hidantalização (fenitoína) após benzodiazepínico
#   [C6] Hipóxia: alerta narcose CO₂ em DPOC + gasometria
#
# Hierarquia:
#   STEP 0 — Hemodinâmica (choque → mata antes do neurológico)
#   STEP 1 — Causas metabólicas reversíveis (hipo/hipóxia/opioide)
#            EM PARALELO com proteção de VA se Glasgow ≤ 8
#   STEP 2 — Causa neurológica (epilepsia, AVC, meningite, TCE)
#   STEP 3 — Tóxico/metabólico (intoxicações, encefalopatia, álcool)
#   STEP 4 — Psicogênico (exclusão)


def _glasgow_grau(g):
    if g >= 14: return 'normal_ou_leve'
    if g >= 9:  return 'moderado'
    return 'grave'  # ≤ 8 → risco real de aspiração e apneia


def _aviso_iot(g):
    """Retorna linhas de alerta de proteção de VA se Glasgow ≤ 8."""
    if g <= 8:
        return [
            '══ PROTEÇÃO DE VIAS AÉREAS (em paralelo) ══',
            'Glasgow ≤ 8 — preparar material de IOT enquanto trata causa reversível',
            'Tratar causa reversível PRIMEIRO (hipo/hipóxia/opioide) — pode evitar IOT',
            'Se sem resposta em 3–5 min → IOT + SAMU',
            '',
        ]
    return []


def _interpretar_consciencia_core(dados):
    g       = dados.get('glasgow_total', 15)
    glicemia= dados.get('glicemia')
    spo2    = dados.get('spo2')
    pupilas = dados.get('pupila_diametro', 'normais')
    iot_alerta = g <= 8
    etilista = dados.get('alcool_drogas') or dados.get('alcool_halito')
    dpoc     = dados.get('dpoc_conhecido', False)  # campo opcional no subjetivo

    # ══════════════════════════════════════════════════════════════════
    # STEP 0 — CHOQUE HEMODINÂMICO [C2]
    # Hipoperfusão cerebral primária — mata antes do neurológico
    # ══════════════════════════════════════════════════════════════════
    pa = dados.get('pa_sistolica', 120)
    fc = dados.get('fc', 80)
    choque_hemo = (pa < 90) or (fc > 120 and pa < 100)
    foco_sepse  = dados.get('foco_infeccioso') or dados.get('febre')

    if choque_hemo:
        tipo_choque = (
            'Séptico (febre + foco infeccioso)' if foco_sepse
            else 'Hipovolêmico / Cardiogênico'
        )
        return {
            'categoria': 'choque_hemodinamico',
            'diagnostico': f'Choque {tipo_choque} — Hipoperfusão Cerebral',
            'glasgow': g, 'iot_alerta': iot_alerta,
            'urgencia': 'emergencia',
            'conduta': _aviso_iot(g) + [
                f'PA {pa} mmHg + FC {fc} bpm — CHOQUE — ressuscitar antes de investigar causa neurológica',
                'Acesso venoso calibroso (≥ 18G) × 2 + coleta de exames + Ringer lactato 500 mL em bolus',
                'Meta imediata: PA sistólica > 90 mmHg + perfusão (TEC < 2s)',
                '',
                'Se Choque Séptico:' if foco_sepse else 'Se Choque Hipovolêmico:',
                '  ATB empírico em até 1h: Ceftriaxona 2 g IV + Metronidazol 500 mg IV' if foco_sepse
                else '  Identificar e controlar fonte de sangramento',
                '  Norepinefrina 0,1–0,3 µg/kg/min se PA não responde a volume (droga vasoativa)' if foco_sepse else '',
                '  Hemocultura × 2 ANTES do ATB — não atrasar ATB por aguardar culturas' if foco_sepse else '',
                '',
                'Glicemia capilar imediata (hipoglicemia pode coexistir)',
                'SAMU — internação em UTI',
            ],
            'exames': [
                'Lactato sérico (> 2 mmol/L = hipoperfusão)',
                'Hemograma, hemocultura × 2, PCR, procalcitonina',
                'Ureia, creatinina, bilirrubinas',
                'Coagulograma (CIVD?)',
                'ECG + ecocardiograma se choque cardiogênico suspeito',
            ],
            'encaminhamento': 'PS / UTI — emergência',
        }

    # ══════════════════════════════════════════════════════════════════
    # STEP 1 — CAUSAS METABÓLICAS REVERSÍVEIS
    # Correm EM PARALELO com proteção de VA se Glasgow ≤ 8 [C3]
    # ══════════════════════════════════════════════════════════════════

    # ── 1a. HIPOGLICEMIA [C1 — Tiamina antes da glicose se etilista] ─
    if glicemia is not None and glicemia < 60:
        tiamina_primeiro = etilista or dados.get('desnutricao', False)
        conduta_glicose = [
            f'TRATAR AGORA — glicemia {glicemia} mg/dL',
        ]
        if tiamina_primeiro:
            conduta_glicose += [
                '⚠️  ETILISTA / DESNUTRIDO — TIAMINA ANTES DA GLICOSE:',
                '  Tiamina 100–300 mg IV (bolus lento 10 min) ANTES do soro glicosado',
                '  Glicose após tiamina — nunca o contrário (risco de Wernicke irreversível)',
                '',
            ]
        conduta_glicose += [
            'Consciente / deglute: Glicose 15–20 g VO (suco + açúcar)',
            'Inconsciente ou Glasgow ≤ 8:',
            '  → Glicose 50% 50 mL IV em bolus (25 g)',
            '  → Sem acesso venoso: Glucagon 1 mg IM/SC',
            'Repetir glicemia em 15 min — meta > 100 mg/dL',
            'Se Glasgow não melhora após normalização da glicemia → investigar outra causa',
            'Não liberar até glicemia estável ≥ 30 min',
        ]
        return {
            'categoria': 'hipoglicemia',
            'diagnostico': f'Hipoglicemia (glicemia {glicemia} mg/dL)'
                           + (' — Etilista: Tiamina PRIMEIRO' if tiamina_primeiro else ''),
            'glasgow': g, 'iot_alerta': iot_alerta,
            'urgencia': 'tratar_imediatamente',
            'conduta': _aviso_iot(g) + conduta_glicose,
            'exames': ['Glicemia seriada', 'Eletrólitos, ureia, creatinina se persistir'],
            'encaminhamento': 'PS se: sem melhora após correção, hipoglicemia recorrente, causa não identificada',
        }

    # ── 1b. HIPÓXIA GRAVE [C6 — Narcose CO₂ em DPOC] ────────────────
    if dados.get('hipoxia') and spo2 and spo2 < 90:
        alerta_dpoc = (
            ['⚠️  DPOC CONHECIDO — cuidado com O₂ alto fluxo:',
             '  Hipercapnia crônica: drive ventilatório é a hipóxia',
             '  O₂ excessivo pode piorar retenção de CO₂ → narcose hipercápnica',
             '  Meta SpO₂: 88–92% (não 94–98% como em não-DPOC)',
             '  Ventilação não-invasiva (VNI) é preferível ao O₂ alto fluxo',
             '  Gasometria arterial urgente — PaCO₂ > 50 com pH < 7,35 = falência ventilatória',
             '']
            if dpoc else []
        )
        return {
            'categoria': 'hipoxia_grave',
            'diagnostico': f'Hipóxia Grave (SpO₂ {spo2}%){" — DPOC" if dpoc else ""}',
            'glasgow': g, 'iot_alerta': iot_alerta,
            'urgencia': 'emergencia',
            'conduta': _aviso_iot(g) + alerta_dpoc + [
                f'SpO₂ {spo2}% — EMERGÊNCIA RESPIRATÓRIA',
                'Não-DPOC: O₂ alto fluxo — máscara com reservatório 10–15 L/min, meta SpO₂ ≥ 94%',
                'DPOC: máscara Venturi 28% → meta SpO₂ 88–92% + gasometria arterial',
                'Identificar causa: broncoespasmo → salbutamol / TEP → heparina / EAP → furosemida + nitrato',
                'Glasgow ≤ 8 → IOT ou VNI + SAMU',
            ],
            'exames': ['Gasometria arterial urgente', 'RX tórax', 'ECG', 'D-dímero se TEP suspeito'],
            'encaminhamento': 'PS / UTI — emergência',
        }

    # ── 1c. OVERDOSE DE OPIOIDE ───────────────────────────────────────
    if (dados.get('intox_tipo') == 'opioide' or
            (dados.get('intoxicacao_suspeita') and pupilas == 'mioticas'
             and dados.get('medicamentos_risco'))):
        return {
            'categoria': 'overdose_opioide',
            'diagnostico': 'Overdose de Opioide — Tríade: miose + depressão respiratória + rebaixamento',
            'glasgow': g, 'iot_alerta': iot_alerta,
            'urgencia': 'emergencia',
            'conduta': _aviso_iot(g) + [
                'NALOXONA — antídoto específico:',
                '  0,4–2 mg IV/IM/SC — repetir a cada 2–3 min até resposta (máx 10 mg)',
                '  Intranasal: 4 mg (spray) — alternativa sem acesso venoso',
                '  Meia-vida curta (30–90 min): monitorar rebote sedação — pode precisar infusão contínua',
                'O₂ suplementar + suporte de vias aéreas',
                'Remover fentanil transdérmico se presente',
                'SAMU — observação ≥ 4–6h obrigatória',
            ],
            'exames': ['Glicemia', 'Toxicológico urinário', 'ECG (QTc)', 'Hemogasometria'],
            'encaminhamento': 'PS obrigatório — risco de nova depressão após efeito da naloxona',
        }

    # ══════════════════════════════════════════════════════════════════
    # STEP 2 — CAUSA NEUROLÓGICA
    # ══════════════════════════════════════════════════════════════════

    # ── 2a. STATUS EPILEPTICUS / PÓS-ICTAL [C5 — Hidantalização] ────
    if dados.get('convulsao_obs') or dados.get('pos_ictal'):
        if dados.get('epilepsia_previa') and not dados.get('convulsao_obs'):
            return {
                'categoria': 'pos_ictal',
                'diagnostico': 'Estado Pós-Ictal — Epiléptico Conhecido',
                'glasgow': g, 'iot_alerta': iot_alerta,
                'urgencia': 'urgente',
                'conduta': [
                    'Decúbito lateral — proteger vias aéreas',
                    'Monitorar até recuperação completa (20–60 min habitual)',
                    'Glicemia imediata',
                    'Verificar: tomou a medicação? Fator precipitante (privação sono, álcool, febre)?',
                    'SE não melhora em 30 min ou crise > 5 min → status epilepticus → protocolo abaixo',
                ],
                'exames': ['Glicemia', 'Nível sérico do antiepiléptico em uso', 'Eletrólitos'],
                'encaminhamento': 'PS se: primeira crise, duração > 5 min, recuperação incompleta',
            }

        # Status epilepticus — protocolo sequencial com hidantalização [C5]
        return {
            'categoria': 'status_epilepticus',
            'diagnostico': 'Status Epilepticus / Primeira Crise — Protocolo de Emergência',
            'glasgow': g, 'iot_alerta': iot_alerta,
            'urgencia': 'emergencia',
            'conduta': _aviso_iot(g) + [
                'SAMU — emergência neurológica',
                'Proteger de traumatismo, NÃO segurar à força, NÃO colocar objeto na boca',
                'Decúbito lateral, O₂ suplementar',
                'Glicemia IMEDIATA — hipoglicemia causa convulsão',
                '',
                '── FASE 1 (0–5 min): BENZODIAZEPÍNICO ──',
                'Diazepam 10 mg IV lento (ou Midazolam 10 mg IM se sem acesso)',
                '  Alternativa retal: Diazepam 0,5 mg/kg em criança',
                '  Pode repetir 1× após 5 min se persistir',
                '',
                '── FASE 2 (5–20 min): HIDANTALIZAÇÃO [C5] ──',
                'Fenitoína (Hidantal) 15–20 mg/kg IV — infundir em 20 min (máx 50 mg/min)',
                '  Monitorar ECG durante infusão (risco de arritmia e hipotensão)',
                '  Alternativa mais segura: Ácido Valpróico 25–45 mg/kg IV em 5 min',
                '  Objetivo: evitar recorrência na ambulância/pós-crise',
                '',
                '── FASE 3 (> 20 min): STATUS REFRATÁRIO ──',
                'IOT + Midazolam ou Propofol em infusão contínua — UTI',
            ],
            'exames': ['Glicemia urgente', 'Eletrólitos, cálcio, magnésio', 'Hemograma', 'TC crânio'],
            'encaminhamento': 'PS / UTI neurológica — emergência',
        }

    # ── 2b. AVC / HEMORRAGIA INTRACRANIANA ───────────────────────────
    if dados.get('deficit_focal') or dados.get('cefaleia_intensa') or dados.get('pupilas_aniso'):
        hemorragico = dados.get('cefaleia_intensa') or dados.get('pupilas_aniso') or dados.get('hipertensao_grave')
        return {
            'categoria': 'avc_sangramento',
            'diagnostico': f'{"Hemorragia Intracraniana Suspeita" if hemorragico else "AVC Isquêmico / AIT Suspeito"}',
            'glasgow': g, 'iot_alerta': iot_alerta,
            'urgencia': 'emergencia',
            'conduta': _aviso_iot(g) + [
                'SAMU — janela trombólise AVC isquêmico: 4,5h',
                'NÃO dar AAS antes de TC (excluir hemorragia)',
                'NÃO tratar PA agressivamente (exceto > 220/120 em isquêmico)',
                'Cabeceira 0–30° (AVC isquêmico) / 30° se rebaixamento',
                'Glicemia: corrigir hipo e hiperglicemia',
                'TC de crânio SEM contraste — urgente',
                'Se anticoagulado + hemorragia: reverter imediatamente',
                '  Varfarina → Vitamina K 10 mg IV + CCP',
                '  DOAC → idarucizumabe (dabigatrana) / andexanet alfa (Xa)',
            ] + (['⚠️  ANISOCORIA → herniação → IOT + Manitol 1 g/kg IV + neurocirurgia urgente'] if dados.get('pupilas_aniso') else []),
            'exames': ['TC crânio s/ contraste urgente', 'Hemograma', 'Coagulograma', 'Glicemia', 'ECG'],
            'encaminhamento': 'PS / UTI neurológica — código AVC',
        }

    # ── 2c. MENINGITE / ENCEFALITE [C4 — Sequência explícita] ────────
    if dados.get('febre') and (dados.get('rigidez_nuca') or dados.get('fotofobia')):
        gl_baixo = g <= 12 or dados.get('deficit_focal')
        return {
            'categoria': 'meningite_encefalite',
            'diagnostico': 'Meningite / Encefalite Bacteriana Suspeita',
            'glasgow': g, 'iot_alerta': iot_alerta,
            'urgencia': 'emergencia',
            'conduta': _aviso_iot(g) + [
                '── SEQUÊNCIA OBRIGATÓRIA [C4] ──',
                '1. Hemocultura × 2 — colher ANTES do ATB (não atrasa mais que 5 min)',
                '2. ATB IMEDIATO — não esperar TC nem PL:',
                '   Ceftriaxona 2 g IV + Dexametasona 10 mg IV',
                '   + Aciclovir 10 mg/kg IV se encefalite suspeita (herpes, febre + comportamento)',
                '   + Ampicilina 2 g IV se > 50 anos ou imunossuprimido (Listeria)',
                '3. TC de crânio — OBRIGATÓRIO antes da PL se:',
                f'   {"⚠️  INDICADO AGORA — Glasgow ≤ 12 ou déficit focal presente" if gl_baixo else "   Glasgow > 12 sem déficit: pode ir direto à PL se TC não disponível rapidamente"}',
                '   Risco de herniação amigdaliana se hipertensão intracraniana não reconhecida',
                '4. Punção Lombar — SOMENTE após TC afastar herniação',
                '   LCR: citologia, proteína, glicose, cultura, Gram',
                '',
                'Isolamento respiratório (meningococo) — máscara cirúrgica',
                'Notificação compulsória (meningite bacteriana)',
                'SAMU — UTI',
            ],
            'exames': [
                'Hemocultura × 2 (antes ATB)',
                'TC crânio urgente',
                'LCR após TC: citologia, proteína, glicose, cultura, Gram',
                'Hemograma, PCR, procalcitonina, glicemia',
            ],
            'encaminhamento': 'PS / UTI — não atrasar ATB por nenhum exame',
        }

    # ── 2d. TCE / HEMATOMA ────────────────────────────────────────────
    if dados.get('trauma_cabeca'):
        return {
            'categoria': 'tce_hematoma',
            'diagnostico': f'TCE {"— Intervalo Lúcido (hematoma extradural?)" if dados.get("lucido_intervalo") else "com Rebaixamento"}',
            'glasgow': g, 'iot_alerta': iot_alerta,
            'urgencia': 'emergencia',
            'conduta': _aviso_iot(g) + [
                'TC de crânio SEM contraste — urgente',
                'Imobilizar coluna cervical se mecanismo grave',
                '⚠️  Intervalo lúcido → hematoma extradural → neurocirurgia urgente' if dados.get('lucido_intervalo') else '',
                'Anticoagulado + TCE → reverter coagulação ANTES da TC',
                'Cabeceira 30° se sem hipotensão',
                'Glasgow ≤ 8 → IOT + controle PaCO₂ 35–40 mmHg',
            ],
            'exames': ['TC crânio urgente', 'Coagulograma', 'Hemograma', 'Glicemia'],
            'encaminhamento': 'PS / neurocirurgia — emergência',
        }

    # ══════════════════════════════════════════════════════════════════
    # STEP 3 — TÓXICO / METABÓLICO
    # ══════════════════════════════════════════════════════════════════

    if dados.get('intoxicacao_suspeita'):
        tipo = dados.get('intox_tipo', 'desconhecido')
        conduta_map = {
            'benzo': [
                'Flumazenil 0,2 mg IV lento — repetir até 1 mg total',
                '⚠️  Cuidado em dependentes crônicos: pode precipitar convulsão',
                'Suporte de VA — efeito dura 1–2h, BZD tem meia-vida longa',
            ],
            'organofosforado': [
                'TOXÍNDROME COLINÉRGICO: miose + broncospasmo + hipersecreção + bradicardia',
                'Atropina 2–4 mg IV — repetir a cada 5–10 min até secar secreções',
                'Pralidoxima 1–2 g IV em 15–30 min — eficaz apenas se precoce (< 24h)',
                'EPI: luvas + avental — risco de contaminação do socorrista',
                'SAMU — UTI',
            ],
            'co': [
                'Retirar do ambiente imediatamente',
                'O₂ 100% por máscara com reservatório (desloca CO da Hb)',
                'Oxigênio hiperbárico se: Glasgow < 15, perda de consciência, gestante, COHb > 25%',
                'SAMU',
            ],
            'antidepressivo': [
                'Tricíclico: risco de arritmia (QRS > 100ms) + hipotensão + convulsão',
                'Bicarbonato de sódio 8,4% 1–2 mEq/kg IV se QRS alargado ou arritmia',
                'NÃO: flumazenil (convulsão), fisostigmina',
                'Carvão ativado 1 g/kg VO se < 1h da ingestão e deglutição preservada',
                'SAMU — monitorização cardíaca contínua',
            ],
            'alcool_intox': [
                'Posição lateral — risco de broncoaspiração',
                'Glicemia imediata',
                'Tiamina 100 mg IV/IM ANTES de qualquer soro glicosado',
                'Hidratação venosa se desidratado',
            ],
        }
        conduta = conduta_map.get(tipo, [
            'Substância desconhecida — suporte ABCDE',
            'Centro de Toxicologia: 0800 722 6001',
            'Carvão ativado 1 g/kg VO se < 1h da ingestão e deglutição preservada',
            'SAMU',
        ])
        return {
            'categoria': f'intoxicacao_{tipo}',
            'diagnostico': f'Intoxicação — {tipo.replace("_"," ").title()}',
            'glasgow': g, 'iot_alerta': iot_alerta,
            'urgencia': 'emergencia',
            'conduta': _aviso_iot(g) + conduta,
            'exames': ['Glicemia', 'ECG', 'Toxicológico urinário', 'Hemogasometria'],
            'encaminhamento': 'PS — observação obrigatória',
        }

    if dados.get('encefalopatia') or dados.get('renal_cronico') or dados.get('acidose_suspeita'):
        causa = ('hepática' if dados.get('encefalopatia')
                 else 'urêmica' if dados.get('renal_cronico')
                 else 'metabólica/acidótica')
        return {
            'categoria': 'encefalopatia_metabolica',
            'diagnostico': f'Encefalopatia {causa.title()}',
            'glasgow': g, 'iot_alerta': iot_alerta,
            'urgencia': 'urgente',
            'conduta': [
                'Asterixis (flapping tremor) = encefalopatia metabólica até prova em contrário',
                'Hepática: Lactulose 30 mL VO/SNG 6/6h → meta 2–3 evacuações/dia',
                '  Rifaximina 550 mg 12/12h se lactulose insuficiente',
                '  Tratar precipitante: sangramento GI, infecção, constipação, PBE',
                'Urêmica: eletrólitos + nefrologia / diálise de urgência',
                'Corrigir distúrbios iônicos (Na, K, Ca, Mg)',
                'Glicemia seriada',
            ],
            'exames': ['Amônia sérica', 'Ureia + creatinina', 'Eletrólitos',
                       'Hemogasometria', 'Hemograma', 'Bilirrubinas'],
            'encaminhamento': 'PS — internação na maioria dos casos',
        }

    if dados.get('alcool_halito') or dados.get('alcool_drogas'):
        return {
            'categoria': 'intoxicacao_alcool',
            'diagnostico': 'Intoxicação Alcoólica Aguda Grave',
            'glasgow': g, 'iot_alerta': iot_alerta,
            'urgencia': 'urgente',
            'conduta': _aviso_iot(g) + [
                'Posição lateral de segurança — risco de broncoaspiração',
                'Glicemia IMEDIATA',
                'Tiamina 100 mg IV/IM ANTES de soro glicosado (Wernicke)',
                'Hidratação venosa se desidratado',
                'Não liberar até sobriedade completa — responsabilidade médico-legal',
                'Glasgow ≤ 8 → PS',
            ],
            'exames': ['Glicemia', 'Eletrólitos', 'Hemograma'],
            'encaminhamento': 'PS se Glasgow ≤ 8 ou sem melhora em 2–3h',
        }

    # ══════════════════════════════════════════════════════════════════
    # STEP 4 — PSICOGÊNICO (exclusão)
    # ══════════════════════════════════════════════════════════════════
    if dados.get('dissociativo') and dados.get('psiq_previa'):
        return {
            'categoria': 'crise_dissociativa',
            'diagnostico': 'Crise Dissociativa / Pseudocrise — Diagnóstico de EXCLUSÃO',
            'glasgow': g, 'iot_alerta': False,
            'urgencia': 'eletivo',
            'conduta': [
                'Sinais sugestivos: olhos fechados com resistência à abertura passiva,',
                '  movimentos assincrônicos, responsividade variável, sem confusão pós-ictal',
                'NÃO medicar com BZD empiricamente',
                'Ambiente calmo — sem reforço do episódio',
                'EEG de vídeo-monitorização: padrão-ouro diagnóstico',
                'Encaminhar psiquiatria para TCC',
            ],
            'exames': ['Glicemia', 'TC crânio se primeira vez', 'EEG (eletivo)'],
            'encaminhamento': 'Psiquiatria — após exclusão orgânica',
        }

    # ── Sem causa identificada ────────────────────────────────────────
    return {
        'categoria': 'anc_indefinida',
        'diagnostico': f'ANC Sem Causa Identificada (Glasgow {g}/15) — Investigação Completa',
        'glasgow': g, 'iot_alerta': iot_alerta,
        'urgencia': 'emergencia' if g <= 8 else 'urgente',
        'conduta': _aviso_iot(g) + [
            'ABCDE: VA → respiração → circulação → glicemia → temperatura',
            'Glicemia capilar IMEDIATA se não coletada',
            'O₂ suplementar (SpO₂ meta > 94% / 88–92% em DPOC)',
            'Acesso venoso + coleta de exames',
            'NÃO administrar sedativo antes do diagnóstico',
            'Centro de Toxicologia: 0800 722 6001',
            'SAMU se Glasgow ≤ 8',
        ],
        'exames': [
            'Glicemia capilar urgente',
            'Hemograma, ureia, creatinina, eletrólitos, glicose sérica',
            'Amônia, bilirrubinas, transaminases',
            'Toxicológico urinário',
            'ECG',
            'TC crânio sem contraste',
            'Hemogasometria + lactato',
        ],
        'encaminhamento': 'PS — todo Glasgow < 13 sem causa clara merece TC e observação',
    }


# =============================================================================
# PENTE FINO — alertas de segurança transversais
# =============================================================================

def _enriquecer_consciencia(resultado: dict, dados: dict) -> dict:
    """Adiciona alertas_seguranca ao resultado (renderizados no topo do #Plano)."""
    alertas = []
    cat = resultado.get('categoria', '')

    # Glasgow ≤ 8: proteção de VA sempre explícita
    g = dados.get('glasgow_total', 15)
    if g <= 8:
        alertas.append(
            '🔴 GLASGOW ≤ 8 — risco de aspiração e apneia: preparar material de IOT '
            'enquanto trata causas reversíveis. Chamar SAMU 192.'
        )

    # Meningite: ATB antes da TC se houver instabilidade
    if cat == 'anc_meningite':
        alertas.append(
            '⚠️ Meningite bacteriana: Dexametasona 0,15 mg/kg IV + ATB ANTES da TC '
            'se sinais de herniação (anisocoria, postura em extensão, Babinski bilateral). '
            'NÃO atrasar ATB para aguardar neuroimagem'
        )

    # Tiamina ANTES da glicose em etilista / desnutrido
    if dados.get('alcool_drogas') or dados.get('alcool_halito') or dados.get('desnutricao'):
        alertas.append(
            '⚠️ Etilismo/desnutrição: administrar Tiamina 100 mg IV ANTES da glicose — '
            'glicose sem tiamina pode precipitar encefalopatia de Wernicke irreversível'
        )

    # DPOC + hipóxia: meta SpO₂ 88-92%
    if dados.get('dpoc_conhecido') and dados.get('hipoxia'):
        alertas.append(
            '⚠️ DPOC + hipóxia: O₂ titulado — meta SpO₂ 88-92% (não > 94%). '
            'Hiperóxia suprime drive hipóxico → narcose por CO₂'
        )

    # Intoxicação: não sedativos antes do diagnóstico
    if dados.get('intoxicacao_suspeita'):
        alertas.append(
            '⚠️ Intoxicação suspeita: NÃO administrar sedativos/BZD antes de identificar '
            'o agente. Ligue para Centro de Toxicologia: 0800 722 6001'
        )

    resultado['alertas_seguranca'] = alertas
    return resultado


def interpretar_consciencia(dados: dict) -> dict:
    """Ponto de entrada público — core + pente fino."""
    return _enriquecer_consciencia(_interpretar_consciencia_core(dados), dados)
