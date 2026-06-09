# modules/raciocinio/urinario/engine_urinario.py
# Motor de raciocínio clínico — Queixas Urinárias (Disúria + Hematúria)
#
# Baseado em:
#   IDSA/ESCMID Guidelines 2011 (cystitis/pyelonephritis)
#   IDSA Complicated UTI 2010
#   AUA Microhematuria Guidelines 2020
#   CDC STI Treatment Guidelines 2021
#   JAMA Triage Algorithm for Adult Women with UTI Symptoms (2024)
#   Ministério da Saúde BR — RENAME / SUS availability
#
# Ponto de entrada único: interpretar_queixa_urinaria(dados)
#
# Estrutura de `dados`:
#   queixa_principal   : 'disuria' | 'hematuria' | 'ambos'
#   sexo               : 'F' | 'M'
#   idade              : int
#   gestante           : bool
#   peri_pos_menopausa : bool
#   primeiro_episodio_jovem : bool  (18–21 anos, 1º episódio de ITU)
#   # sintomas urinários
#   disuria, frequencia, urgencia, nocturia, dor_suprapubica : bool
#   hematuria_macro, hematuria_micro : bool
#   # sintomas sistêmicos → sugerem ITU alta ou sepse
#   febre, calafrio, nausea_vomito, dor_lombar, ppd_positivo : bool
#   alteracao_mental, hipotensao : bool
#   # sintomas genitais
#   secrecao_uretral, secrecao_vaginal, prurido_genital : bool
#   lesao_genital : bool          (úlcera / vesículas → herpes)
#   dispareunia   : bool
#   corrimento_tipo : 'grumoso_branco' | 'acinzentado' | 'amarelo_esverdeado' | None
#   # sintomas obstrutivos (homem)
#   hesitancia, jato_fraco, gotejamento_terminal, dor_perineal : bool
#   retencao_urinaria : bool
#   # características da hematúria
#   hematuria_indolor  : bool    (→ risco Ca bexiga)
#   hematuria_colicativa : bool  (→ calculose)
#   hematuria_fumaca   : bool    (cola-colored → glomerular)
#   # fatores de risco / complicadores
#   itu_recorrente     : bool    (≥3/ano ou ≥2/6 meses)
#   atb_recente_30d    : bool    (ATB para ITU nos últimos 30 dias)
#   atb_fl_smx_3m      : bool    (FQ/SMX-TMP/cefalosporina ampla < 3 meses)
#   cateter, imunossupressao, diabetes, drc : bool
#   obstrucao_urinaria, litíase_previa : bool
#   ist_risco          : bool    (parceiro novo / múltiplos / IST prévia)
#   tabagismo          : bool
#   exposicao_ocupacional : bool (corantes, borracha → risco Ca bexiga)
#   radioterapia_pelvica  : bool
#   # exame físico
#   toque_prostatico : 'normal' | 'doloroso_boggoso' | 'nodular' | None
#   # EAS (se disponível)
#   eas_disponivel, eas_piuria, eas_nitritos, eas_hemacias : bool
#   eas_cilindros, eas_proteinuria, eas_hemacias_dismorfica : bool
#   eas_hemacias_hpf   : int     (RBC/HPF)

# =============================================================================
# PRESCRIÇÕES PADRÃO
# =============================================================================

_RX = {
    # ── Cistite feminina ─────────────────────────────────────────────────────
    'nitrofurantoina_5d': {
        'linha': '1ª linha',
        'medicamento': 'Nitrofurantoína 100mg',
        'prescricoes': [{'quantidade': 15, 'unidade': 'comprimidos',
                         'posologia': '1cp VO 8/8h por 5 dias'}],
        'nota': 'Tomar com alimentos (↓ náusea). Contraindicado: CrCl < 30 mL/min.',
    },
    'nitrofurantoina_7d': {
        'linha': '1ª linha',
        'medicamento': 'Nitrofurantoína 100mg',
        'prescricoes': [{'quantidade': 21, 'unidade': 'comprimidos',
                         'posologia': '1cp VO 8/8h por 7 dias'}],
        'nota': 'Tomar com alimentos. Contraindicado CrCl < 30 mL/min. '
                'Na gestação: evitar após 36ª semana.',
    },
    'fosfomicina': {
        'linha': 'Alt — dose única',
        'medicamento': 'Fosfomicina trometamol 3g',
        'prescricoes': [{'quantidade': 1, 'unidade': 'sachê',
                         'posologia': 'Dissolver em água, tomar dose única à noite'}],
        'nota': 'SUS: disponibilidade regional variável. '
                'Eficácia ligeiramente menor que nitrofurantoína na cistite.',
    },
    'smxtmp_3d': {
        'linha': 'Alt — somente se cultura sensível',
        'medicamento': 'Sulfametoxazol+Trimetoprim 400/80mg',
        'prescricoes': [{'quantidade': 6, 'unidade': 'comprimidos',
                         'posologia': '2cp VO 12/12h por 3 dias'}],
        'nota': '⚠️ Resistência ~30% no Brasil — NÃO usar empiricamente. '
                'Reservar para cultura com sensibilidade confirmada.',
    },
    'smxtmp_14d': {
        'linha': 'Alt — somente se cultura sensível',
        'medicamento': 'Sulfametoxazol+Trimetoprim 400/80mg',
        'prescricoes': [{'quantidade': 28, 'unidade': 'comprimidos',
                         'posologia': '2cp VO 12/12h por 14 dias'}],
        'nota': 'Usar apenas com cultura comprovada. Pielonefrite / ITU masculina.',
    },
    # ── Cistite gestante ─────────────────────────────────────────────────────
    'amoxiclav_gestante': {
        'linha': '1ª linha — gestante',
        'medicamento': 'Amoxicilina+Clavulanato 500/125mg',
        'prescricoes': [{'quantidade': 21, 'unidade': 'comprimidos',
                         'posologia': '1cp VO 8/8h por 7 dias'}],
        'nota': 'Seguro em toda a gestação. Ajustar após resultado da urocultura.',
    },
    # ── Pielonefrite / ITU complicada ────────────────────────────────────────
    'cipro_7d': {
        'linha': '1ª linha — pielonefrite ambulatorial',
        'medicamento': 'Ciprofloxacino 500mg',
        'prescricoes': [{'quantidade': 14, 'unidade': 'comprimidos',
                         'posologia': '1cp VO 12/12h por 7 dias'}],
        'nota': 'Cultura obrigatória antes de iniciar. Ajustar conforme antibiograma. '
                'Retorno se sem melhora em 48–72h.',
    },
    'cipro_14d': {
        'linha': '1ª linha — ITU masculina',
        'medicamento': 'Ciprofloxacino 500mg',
        'prescricoes': [{'quantidade': 28, 'unidade': 'comprimidos',
                         'posologia': '1cp VO 12/12h por 14 dias'}],
        'nota': 'Cultura obrigatória. Homem: qualquer ITU é complicada.',
    },
    'cipro_6sem': {
        'linha': '1ª linha — prostatite aguda',
        'medicamento': 'Ciprofloxacino 500mg',
        'prescricoes': [{'quantidade': 84, 'unidade': 'comprimidos',
                         'posologia': '1cp VO 12/12h por 6 semanas'}],
        'nota': 'Completar curso completo mesmo com melhora precoce. '
                'Interrupção aumenta risco de prostatite crônica.',
    },
    'levo_5d': {
        'linha': 'Alt — pielonefrite (esquema curto)',
        'medicamento': 'Levofloxacino 750mg',
        'prescricoes': [{'quantidade': 5, 'unidade': 'comprimidos',
                         'posologia': '1cp VO 1x/dia por 5 dias'}],
        'nota': 'Alternativa ao ciprofloxacino para pielonefrite não complicada.',
    },
    # ── IST ──────────────────────────────────────────────────────────────────
    'ceftriaxona_ist': {
        'linha': '1ª linha — gonorreia',
        'medicamento': 'Ceftriaxona 500mg (pó para solução injetável)',
        'prescricoes': [{'quantidade': 1, 'unidade': 'ampola',
                         'posologia': '500mg IM dose única — diluir em 2 mL lidocaína 1% (IM glúteo)'}],
        'nota': 'Administrar na própria UBS. Não diluir em soro fisiológico (dor intensa).',
    },
    'doxiciclina_7d': {
        'linha': '1ª linha — clamídia / cobertura dual',
        'medicamento': 'Doxiciclina 100mg',
        'prescricoes': [{'quantidade': 14, 'unidade': 'comprimidos',
                         'posologia': '1cp VO 12/12h por 7 dias'}],
        'nota': 'Tomar com copo cheio d\'água; não deitar por 30 min. '
                'Superior à azitromicina para clamídia genital (IDSA/CDC 2021). '
                'Contraindicado na gestação.',
    },
    'azitro_1g': {
        'linha': 'Alt — clamídia (se doxiciclina contraindicada)',
        'medicamento': 'Azitromicina 500mg',
        'prescricoes': [{'quantidade': 2, 'unidade': 'comprimidos',
                         'posologia': '2cp VO dose única (1g) — tomar de uma vez'}],
        'nota': 'Reservar para gestantes ou intolerância à doxiciclina. '
                'Menor eficácia que doxiciclina para clamídia.',
    },
    'metro_dose_unica': {
        'linha': '1ª linha — tricomoníase',
        'medicamento': 'Metronidazol 400mg',
        'prescricoes': [{'quantidade': 5, 'unidade': 'comprimidos',
                         'posologia': '5cp VO dose única (2g) — tomar de uma vez'}],
        'nota': 'Evitar álcool por 24h. Tratar parceiro simultaneamente (mesmo assintomático).',
    },
    # ── Vaginose bacteriana ──────────────────────────────────────────────────
    'metro_bv': {
        'linha': '1ª linha — vaginose bacteriana',
        'medicamento': 'Metronidazol 400mg',
        'prescricoes': [{'quantidade': 14, 'unidade': 'comprimidos',
                         'posologia': '1cp VO 12/12h por 7 dias'}],
        'nota': 'Preferível à dose única (menor taxa de recidiva). '
                'Evitar álcool. Parceiro: NÃO tratar rotineiramente.',
    },
    # ── Candidíase ───────────────────────────────────────────────────────────
    'fluconazol': {
        'linha': '1ª linha — candidíase vaginal',
        'medicamento': 'Fluconazol 150mg',
        'prescricoes': [{'quantidade': 1, 'unidade': 'cápsula',
                         'posologia': '1 cápsula VO dose única'}],
        'nota': '⚠️ Contraindicado na gestação (teratogênico). '
                'Na gestante usar clotrimazol vaginal 100mg × 7 dias (via vaginal).',
    },
    'fluconazol_recorrente': {
        'linha': 'Profilaxia — candidíase recorrente (≥4 episódios/ano)',
        'medicamento': 'Fluconazol 150mg',
        'prescricoes': [{'quantidade': 26, 'unidade': 'cápsulas',
                         'posologia': '1 cápsula VO 1x/semana por 6 meses'}],
        'nota': 'Iniciar após tratamento do episódio agudo. '
                'Reavaliação ao término dos 6 meses para suspenção tentativa.',
    },
    # ── Herpes genital ───────────────────────────────────────────────────────
    'aciclovir_primario': {
        'linha': '1ª linha — herpes genital, 1º episódio',
        'medicamento': 'Aciclovir 400mg',
        'prescricoes': [{'quantidade': 21, 'unidade': 'comprimidos',
                         'posologia': '1cp VO 8/8h por 7 dias'}],
        'nota': 'Iniciar o mais precocemente possível. Não cura — reduz duração e gravidade. '
                'Solicitar sorologias HIV + sífilis.',
    },
    'aciclovir_recorrente': {
        'linha': 'Episódio recorrente',
        'medicamento': 'Aciclovir 400mg',
        'prescricoes': [{'quantidade': 15, 'unidade': 'comprimidos',
                         'posologia': '1cp VO 8/8h por 5 dias'}],
        'nota': 'Iniciar ao 1º sinal do pródromo (queimação/prurido) para máximo benefício.',
    },
    'aciclovir_supressao': {
        'linha': 'Supressão — ≥6 recorrências/ano',
        'medicamento': 'Aciclovir 400mg',
        'prescricoes': [{'quantidade': 60, 'unidade': 'comprimidos',
                         'posologia': '1cp VO 12/12h — uso contínuo (reavaliar a cada 12 meses)'}],
        'nota': 'Reduz recorrências em ~70–80%. Reavaliação anual para tentativa de suspensão.',
    },
    # ── HPB ──────────────────────────────────────────────────────────────────
    'tamsulosina': {
        'linha': '1ª linha — HPB / STUI moderado',
        'medicamento': 'Tamsulosina 0,4mg',
        'prescricoes': [{'quantidade': 30, 'unidade': 'comprimidos',
                         'posologia': '1cp VO 1x/dia, após a mesma refeição diariamente'}],
        'nota': 'Melhora de sintomas em 2–4 semanas. '
                'Pode causar hipotensão ortostática — avisar paciente.',
    },
    # ── Profilaxia ITU recorrente ─────────────────────────────────────────────
    'nitrofurantoina_profilaxia': {
        'linha': 'Profilaxia contínua — ITU recorrente',
        'medicamento': 'Nitrofurantoína 100mg',
        'prescricoes': [{'quantidade': 30, 'unidade': 'comprimidos',
                         'posologia': '1cp VO ao deitar, 1x/dia — uso contínuo'}],
        'nota': 'Reavaliar necessidade a cada 6 meses. '
                'Alternativa pós-coital: 1cp após relação sexual.',
    },
}


# =============================================================================
# RED FLAGS — Emergência (verificados antes de qualquer hipótese)
# =============================================================================

def _avaliar_red_flags(dados):
    flags = []

    # Sepse urinária / pielonefrite grave
    if dados.get('febre') and (dados.get('calafrio') or dados.get('nausea_vomito')):
        flags.append({
            'achado': 'Febre + calafrio ou vômito — pielonefrite / sepse urinária provável',
            'urgencia': 'emergencia',
            'acao': 'Avaliação presencial imediata. Sinais vitais, hidratação IV se intolerância oral.',
        })

    if dados.get('alteracao_mental') or dados.get('hipotensao'):
        flags.append({
            'achado': 'Alteração do estado mental / hipotensão — sepse grave',
            'urgencia': 'emergencia',
            'acao': 'SAMU (192) ou PA imediatamente. Sepse urinária grave.',
        })

    # Retenção urinária
    if dados.get('retencao_urinaria'):
        flags.append({
            'achado': 'Retenção urinária aguda',
            'urgencia': 'emergencia',
            'acao': 'PA/PS urgente — cateterismo vesical de alívio.',
        })

    # Hematúria + retenção (tamponamento vesical)
    if dados.get('hematuria_macro') and dados.get('retencao_urinaria'):
        flags.append({
            'achado': 'Hematúria macroscópica + retenção — tamponamento vesical',
            'urgencia': 'emergencia',
            'acao': 'Urologia urgente. Cateter de 3 vias para lavagem vesical.',
        })

    # Gestante com sinais de ITU alta
    if dados.get('gestante') and dados.get('febre') and (
            dados.get('ppd_positivo') or dados.get('dor_lombar')):
        if not any(f['acao'].startswith('Avaliação presencial') for f in flags):
            flags.append({
                'achado': 'Pielonefrite em gestante — alto risco materno-fetal',
                'urgencia': 'emergencia',
                'acao': 'Obstetrícia urgente — internação indicada.',
            })

    return flags


# =============================================================================
# DISÚRIA — Detecção de pielonefrite (tem prioridade sobre cistite)
# =============================================================================

def _tem_pielonefrite(dados):
    """Febre + dor lombar/PPD = ITU alta até prova em contrário."""
    return dados.get('febre') and (dados.get('ppd_positivo') or dados.get('dor_lombar'))


def _cistite_eh_complicada(dados):
    """Qualquer fator que torne a cistite 'complicada' (precisa de cultura)."""
    return any([
        dados.get('gestante'),
        dados.get('diabetes'),
        dados.get('imunossupressao'),
        dados.get('cateter'),
        dados.get('drc'),
        dados.get('obstrucao_urinaria'),
        dados.get('itu_recorrente'),
        dados.get('atb_recente_30d'),
        dados.get('atb_fl_smx_3m'),
    ])


# =============================================================================
# CISTITE FEMININA
# =============================================================================

def _avaliar_cistite_feminina(dados):
    """
    Fluxo JAMA 2024:
      3b (fatores de risco) → cultura obrigatória (cistite complicada)
      sem fatores → tratamento empírico OK (cistite simples)
    """
    recorrente = dados.get('itu_recorrente')
    gestante   = dados.get('gestante')
    complicada = _cistite_eh_complicada(dados)

    # ── Cistite na gestante ────────────────────────────────────────────────
    if gestante:
        return {
            'tipo': 'urinario',
            'categoria': 'cistite_gestante',
            'diagnostico': 'Cistite na gestante',
            'forca': 'alta',
            'achados': [
                'Sintomas de cistite em paciente gestante',
                'ITU na gestação = sempre complicada — cultura obrigatória',
            ],
            'conduta': [
                'Solicitar urocultura + antibiograma ANTES de iniciar ATB',
                'Iniciar tratamento empírico enquanto aguarda cultura',
                'Test of cure obrigatório: repetir urocultura 1–2 sem após término do ATB',
                'Triagem mensal de bacteriúria assintomática pelo restante da gestação',
                'Encaminhar pré-natal de alto risco se ITU de repetição',
            ],
            'prescricoes_estruturadas': [
                _RX['amoxiclav_gestante'],
                {   # Nitrofurantoína como alt (até 36 sem)
                    'linha': 'Alt (até 36ª semana)',
                    'medicamento': 'Nitrofurantoína 100mg',
                    'prescricoes': [{'quantidade': 21, 'unidade': 'comprimidos',
                                     'posologia': '1cp VO 8/8h por 7 dias'}],
                    'nota': 'EVITAR após 36ª semana (risco hemolítico no RN). '
                            'Ajustar conforme antibiograma.',
                },
            ],
            'exames': [
                'Urocultura + antibiograma (obrigatório antes do ATB)',
                'EAS (apoio diagnóstico)',
                'Urocultura de controle 1–2 semanas após término do tratamento',
            ],
            'encaminhar': None,
            'urgencia': None,
            'retorno': 'Em 48–72h se piora. Retorno para test of cure em 1–2 semanas.',
        }

    # ── Cistite recorrente ─────────────────────────────────────────────────
    if recorrente:
        return {
            'tipo': 'urinario',
            'categoria': 'cistite_recorrente',
            'diagnostico': 'Cistite de repetição (≥ 3 episódios/ano)',
            'forca': 'alta',
            'achados': [
                'ITU recorrente — definição: ≥3/ano ou ≥2/6 meses',
                'Investigar fatores predisponentes antes de profilaxia',
            ],
            'conduta': [
                'Tratar episódio atual com urocultura (ver prescrição abaixo)',
                'Investigar: resíduo pós-miccional, glicemia/HbA1c, exame ginecológico '
                '(vaginite atrófica pós-menopausa), anatomia urinária',
                'Orientar: hidratação ≥ 2L/dia, micção pós-coital, higiene anterior-posterior',
                'Considerar profilaxia contínua ou pós-coital após 2º episódio',
            ],
            'prescricoes_estruturadas': [
                _RX['nitrofurantoina_5d'],
                _RX['nitrofurantoina_profilaxia'],
            ],
            'exames': [
                'Urocultura + antibiograma (obrigatório no episódio atual)',
                'Glicemia em jejum / HbA1c (rastrear DM)',
                'Resíduo pós-miccional por USG (se sintomas obstrutivos)',
                'USG rins e vias urinárias (se anomalia estrutural suspeita)',
            ],
            'encaminhar': 'Urologia eletivo se falha de profilaxia ou anomalia na USG',
            'urgencia': None,
            'retorno': 'Em 48–72h se piora. Agendamento para investigação das causas.',
        }

    # ── Cistite complicada (sem gestação, sem recorrência) ─────────────────
    if complicada:
        fatores = []
        if dados.get('diabetes'):         fatores.append('DM')
        if dados.get('imunossupressao'):  fatores.append('imunossupressão')
        if dados.get('cateter'):          fatores.append('cateter urinário')
        if dados.get('drc'):              fatores.append('DRC / rim único')
        if dados.get('obstrucao_urinaria'): fatores.append('obstrução urinária')
        if dados.get('atb_recente_30d'):  fatores.append('ATB para ITU < 30 dias')
        if dados.get('atb_fl_smx_3m'):    fatores.append('FQ/SMX-TMP < 3 meses')

        return {
            'tipo': 'urinario',
            'categoria': 'cistite_complicada',
            'diagnostico': 'Cistite complicada',
            'forca': 'alta',
            'achados': [
                f'Fator(es) complicador(es): {", ".join(fatores)}',
                'Cultura obrigatória — risco elevado de resistência',
            ],
            'conduta': [
                'Solicitar urocultura + antibiograma ANTES de iniciar ATB',
                'Iniciar cobertura empírica por 7 dias enquanto aguarda cultura',
                'Ajustar ATB conforme antibiograma',
                'Orientar retorno em 48–72h se sem melhora',
            ],
            'prescricoes_estruturadas': [
                _RX['nitrofurantoina_7d'],   # 1ª linha empírica (se CrCl OK)
                _RX['smxtmp_14d'],           # alt se cultura sensível
            ],
            'exames': [
                'Urocultura + antibiograma (obrigatório antes do ATB)',
                'EAS com sedimento',
                'Creatinina + eGFR (ajuste de dose e elegibilidade nitrofurantoína)',
            ],
            'encaminhar': None,
            'urgencia': None,
            'retorno': 'Em 48–72h para reavaliação. Test of cure não necessário se sintomas '
                       'resolverem (exceto gestante).',
        }

    # ── Cistite simples (sem fatores de risco — fluxo JAMA 3b → NÃO) ──────
    return {
        'tipo': 'urinario',
        'categoria': 'cistite_simples',
        'diagnostico': 'Cistite não complicada',
        'forca': 'alta',
        'achados': [
            'Disúria + frequência / urgência / dor suprapúbica',
            'Sem febre, sem PPD positivo, sem dor lombar',
            'Sem fatores complicadores — tratamento empírico sem cultura (JAMA 2024 / IDSA)',
        ],
        'conduta': [
            'Orientar hidratação ≥ 2L/dia',
            'Informar que sintomas devem melhorar em 24–48h',
            'Retornar se não houver melhora em 48h ou se surgirem febre/calafrio/dor lombar',
        ],
        'prescricoes_estruturadas': [
            _RX['nitrofurantoina_5d'],
            _RX['fosfomicina'],
            _RX['smxtmp_3d'],   # apenas se cultura disponível e sensível
        ],
        'exames': [
            'EAS: opcional (diagnóstico clínico suficiente com ≥2 sintomas típicos)',
            'Urocultura: NÃO necessária em apresentação típica sem fatores de risco',
        ],
        'encaminhar': None,
        'urgencia': None,
        'retorno': 'Retornar se sem melhora em 48h ou surgir febre / dor lombar.',
    }


# =============================================================================
# PIELONEFRITE
# =============================================================================

def _avaliar_pielonefrite(dados):
    """
    Ambulatorial se: tolera VO, sem hemodynamic compromise, não gestante,
                     não imunossuprimido, sem obstrução.
    PA/PS se: vômito intratável, sepse, gestante, imunossuprimido.
    """
    criterios_internacao = any([
        dados.get('nausea_vomito'),      # não tolera VO
        dados.get('calafrio'),           # rigor → risco de bacteremia
        dados.get('hipotensao'),
        dados.get('alteracao_mental'),
        dados.get('gestante'),
        dados.get('imunossupressao'),
        dados.get('obstrucao_urinaria'),
        dados.get('drc'),
        dados.get('cateter'),
    ])

    if criterios_internacao:
        motivos = []
        if dados.get('nausea_vomito'):      motivos.append('intolerância oral')
        if dados.get('calafrio'):            motivos.append('rigor / bacteremia provável')
        if dados.get('gestante'):            motivos.append('gestante')
        if dados.get('imunossupressao'):     motivos.append('imunossupressão')
        if dados.get('obstrucao_urinaria'): motivos.append('obstrução urinária')

        return {
            'tipo': 'urinario',
            'categoria': 'pielonefrite_emergencia',
            'diagnostico': 'Pielonefrite — critérios de internação',
            'forca': 'alta',
            'achados': [
                f'Febre + dor lombar / PPD positivo → pielonefrite provável',
                f'Critério(s) de internação: {", ".join(motivos) if motivos else "presente(s)"}',
            ],
            'conduta': [
                'Encaminhar PA/PS imediatamente',
                'Se ATB IV disponível e transfer demorado: '
                'Ceftriaxona 1g IV OU Gentamicina 5 mg/kg IV (dose única) antes do transfer',
                'Acesso venoso periférico + SF 500 mL se hipotensão',
                'Coletar urocultura E hemoculturas (2 pares) se possível antes do ATB',
            ],
            'prescricoes_estruturadas': [],
            'exames': [
                'Hemoculturas (2 pares) antes do ATB — no PS',
                'Urocultura antes do ATB',
                'Hemograma + PCR + creatinina + ionograma',
                'USG rins e vias urinárias (excluir abscesso/obstrução)',
            ],
            'encaminhar': 'PA/PS imediatamente',
            'urgencia': 'emergencia',
            'retorno': 'Seguimento ambulatorial após alta hospitalar.',
        }

    # ── Pielonefrite ambulatorial ──────────────────────────────────────────
    return {
        'tipo': 'urinario',
        'categoria': 'pielonefrite_ambulatorial',
        'diagnostico': 'Pielonefrite não complicada — ambulatorial',
        'forca': 'alta',
        'achados': [
            'Febre + dor lombar / PPD positivo → pielonefrite',
            'Tolera via oral, sem sinais de sepse, sem comorbidades graves',
            'Critérios para tratamento ambulatorial preenchidos',
        ],
        'conduta': [
            'Solicitar urocultura + antibiograma ANTES de iniciar ATB',
            '⚠️ Resistência de E. coli a quinolonas > 20% em centros urbanos no Brasil: '
            'administrar Ceftriaxona 1g IM/IV em dose única no PA ANTES da alta, '
            'garantindo cobertura enquanto aguarda urocultura',
            'Após dose de ataque: liberar com ciprofloxacino VO (ver prescrição)',
            'Ajustar ATB conforme antibiograma em 48–72h',
            'Orientar retorno imediato se: piora da febre, vômito, não conseguir tomar ATB',
            'Hidratação oral ≥ 2L/dia',
            'Repouso relativo nas primeiras 48h',
            'USG rins: não rotineiro — solicitar se sem melhora em 72h',
        ],
        'prescricoes_estruturadas': [
            {
                'linha': 'Dose de ataque no PA (antes da alta)',
                'medicamento': 'Ceftriaxona 1g',
                'prescricoes': [{'quantidade': 1, 'unidade': 'ampola IV/IM',
                                 'posologia': 'dose única agora — administrar antes de liberar'}],
                'nota': 'Indicado se resistência local a quinolonas >10-20% ou desconhecida '
                        '(padrão recomendado em centros urbanos do Brasil). '
                        'Garante cobertura enquanto aguarda urocultura.',
            },
            _RX['cipro_7d'],
            _RX['levo_5d'],
            _RX['smxtmp_14d'],   # apenas se cultura sensível
        ],
        'exames': [
            'Urocultura + antibiograma (obrigatório antes do ATB)',
            'EAS com sedimento',
            'Hemograma + PCR (opcional — se dúvida diagnóstica)',
            'Creatinina (baseline)',
        ],
        'encaminhar': None,
        'urgencia': 'urgente',   # presencial hoje, não PS
        'retorno': 'Contato / retorno em 48–72h para confirmar melhora. '
                   'Sem melhora → PA/PS (suspeita de obstrução ou abscesso).',
    }


# =============================================================================
# UTI MASCULINA / PROSTATITE / HPB
# =============================================================================

def _avaliar_urinario_masculino(dados):
    """Todo ITU em homem é complicada. Primeiro excluir prostatite."""

    # ── Prostatite aguda ────────────────────────────────────────────────────
    if dados.get('febre') and dados.get('dor_perineal') and \
            dados.get('toque_prostatico') == 'doloroso_boggoso':
        criterios_internacao = any([
            dados.get('retencao_urinaria'),
            dados.get('imunossupressao'),
            dados.get('nausea_vomito'),
        ])
        return {
            'tipo': 'urinario',
            'categoria': 'prostatite_aguda',
            'diagnostico': 'Prostatite aguda bacteriana',
            'forca': 'alta',
            'achados': [
                'Febre + dor perineal/suprapúbica + próstata dolorosa ao toque',
                '⚠️ NÃO realizar massagem prostática vigorosa (risco de bacteremia)',
                'Internação indicada se: retenção urinária, imunossupressão ou sepse',
            ],
            'conduta': [
                'Urocultura + hemoculturas antes do ATB',
                'Resíduo pós-miccional (USG) se sintomas obstrutivos',
                'PSA: NÃO solicitar agora — elevado durante infecção (falso-positivo). '
                'Reavaliação 4–6 semanas após tratamento',
                'α-bloqueador (tamsulosina) para sintomas obstrutivos',
                'PA/PS se retenção urinária ou sepse',
            ],
            'prescricoes_estruturadas': [
                _RX['cipro_6sem'],
                {
                    'linha': 'Adjuvante — sintomas obstrutivos',
                    'medicamento': 'Tamsulosina 0,4mg',
                    'prescricoes': [{'quantidade': 42, 'unidade': 'comprimidos',
                                     'posologia': '1cp VO 1x/dia por 6 semanas'}],
                    'nota': 'Alivia disúria obstrutiva. Suspender após término do ATB se assintomático.',
                },
            ],
            'exames': [
                'Urocultura + antibiograma (obrigatório)',
                'Hemoculturas se febre alta / calafrio',
                'USG próstata + resíduo pós-miccional',
                'Hemograma + PCR + creatinina',
                'PSA: AGUARDAR 4–6 semanas após cura (solicitar para rastreamento etário)',
            ],
            'encaminhar': 'PA/PS se retenção, sepse ou imunossupressão' if criterios_internacao
                          else 'Urologia eletivo após cura (avaliar HPB subjacente)',
            'urgencia': 'emergencia' if criterios_internacao else 'urgente',
            'retorno': 'Contato em 48–72h. Retorno para cultura de controle em 4–6 semanas.',
        }

    # ── Prostatite crônica / CPPS ───────────────────────────────────────────
    if dados.get('dor_perineal') and not dados.get('febre'):
        return {
            'tipo': 'urinario',
            'categoria': 'prostatite_cronica',
            'diagnostico': 'Prostatite crônica / Síndrome de dor pélvica crônica (CPPS)',
            'forca': 'moderada',
            'achados': [
                'Dor pélvica/perineal crônica sem febre',
                'CPPS: diagnóstico de exclusão após afastar bacteriana (cultura negativa)',
            ],
            'conduta': [
                'Urocultura para distinguir Categoria II (bacteriana) de III (CPPS)',
                'Categoria II (cultura +): fluoroquinolona 4–6 semanas',
                'Categoria III (CPPS): α-bloqueador + fisioterapia pélvica '
                '(superior a antibiótico isolado)',
                'Encaminhar urologia para classificação NIH e tratamento dirigido',
            ],
            'prescricoes_estruturadas': [
                _RX['tamsulosina'],
            ],
            'exames': [
                'Urocultura + antibiograma (excluir Categoria II)',
                'EAS com sedimento',
                'USG próstata',
                'PSA (rastreamento etário — não diagnóstico de prostatite)',
            ],
            'encaminhar': 'Urologia eletivo — CPPS requer manejo especializado prolongado',
            'urgencia': 'eletivo',
            'retorno': 'Retorno em 4–6 semanas com resultado de cultura.',
        }

    # ── HPB / STUI ─────────────────────────────────────────────────────────
    if dados.get('hesitancia') or dados.get('jato_fraco') or dados.get('gotejamento_terminal'):
        ipss_grave = dados.get('ipss_grave', False)   # score ≥20 se disponível
        return {
            'tipo': 'urinario',
            'categoria': 'hpb_stui',
            'diagnostico': 'HPB — Sintomas do Trato Urinário Inferior (STUI)',
            'forca': 'moderada',
            'achados': [
                'Hesitância / jato fraco / gotejamento terminal em homem adulto',
                'PSA deve ser solicitado para rastreamento (≥50 anos, expectativa de vida > 10 anos)',
            ],
            'conduta': [
                'Aplicar IPSS: 1–7 leve (vigiar) | 8–19 moderado (tratar) | ≥20 grave (urologia)',
                'Orientar: reduzir líquidos à noite, cafeína e álcool',
                'Aferir resíduo pós-miccional por USG',
            ],
            'prescricoes_estruturadas': [
                _RX['tamsulosina'],
            ],
            'exames': [
                'PSA (rastreamento — não durante ITU ativa)',
                'USG próstata + resíduo pós-miccional',
                'Urofluxometria (se disponível)',
                'Creatinina + EAS (excluir ITU associada)',
            ],
            'encaminhar': 'Urologia urgente se: retenção urinária, ITU recorrente, hematúria, '
                          'hidronefrose ou creatinina elevada' if ipss_grave
                          else 'Urologia eletivo se falha após 3–6 meses de α-bloqueador',
            'urgencia': 'urgente' if ipss_grave else 'eletivo',
            'retorno': 'Retorno em 4–6 semanas para avaliar resposta ao α-bloqueador.',
        }

    # ── ITU masculina simples (cistite complicada por definição) ────────────
    return {
        'tipo': 'urinario',
        'categoria': 'itu_masculina',
        'diagnostico': 'ITU masculina (sempre complicada)',
        'forca': 'alta',
        'achados': [
            'Sintomas de cistite em paciente do sexo masculino',
            'Qualquer ITU em homem = complicada — cultura obrigatória',
            'Avaliar próstata ao toque retal se sintomas sugestivos',
        ],
        'conduta': [
            'Coletar urocultura ANTES de iniciar ATB',
            'Toque retal para avaliar próstata (prostatite?)',
            'Se não melhora em 7 dias: considerar prostatite — estender para 4–6 semanas',
            'USG rins + bexiga + próstata (1º episódio em jovem ou ITU recorrente)',
        ],
        'prescricoes_estruturadas': [
            _RX['cipro_14d'],
            _RX['smxtmp_14d'],
        ],
        'exames': [
            'Urocultura + antibiograma (obrigatório)',
            'EAS com sedimento',
            'PSA: aguardar 4–6 semanas após tratamento (se indicado por idade)',
            'USG rins, bexiga e próstata (1º episódio ou ITU recorrente)',
        ],
        'encaminhar': 'Urologia eletivo — 1º episódio em jovem (<50 anos) ou ITU recorrente',
        'urgencia': None,
        'retorno': 'Retorno em 48–72h. Se febre surgir ou piorar → PA/PS.',
    }


# =============================================================================
# URETRITE / IST
# =============================================================================

def _avaliar_uretrite_ist(dados):
    """
    Cobertura dual gonorreia + clamídia (tratamento sindrômico).
    Notificação compulsória. Testar HIV + sífilis.
    """
    return {
        'tipo': 'urinario',
        'categoria': 'uretrite_ist',
        'diagnostico': 'Uretrite / IST (gonorreia + clamídia — cobertura dual)',
        'forca': 'alta',
        'achados': [
            'Secreção uretral / vaginal purulenta ou mucopurulenta',
            'Risco de IST presente (parceiro novo / múltiplos / IST prévia)',
            'Tratamento sindrômico sem aguardar cultura (PCDT MS 2022)',
        ],
        'conduta': [
            'Tratamento sindrômico simultâneo gonorreia + clamídia',
            'Notificação compulsória (SINAN — IST notificável)',
            'Testar HIV + sífilis (VDRL + FTA-ABS ou TPHA)',
            'Convocar e tratar parceiro(s) sexual(is) — mesmo assintomáticos',
            'Abstinência sexual por 7 dias após tratamento + resolução de sintomas',
            'Oferecer PrEP / PEP se indicado',
        ],
        'prescricoes_estruturadas': [
            _RX['ceftriaxona_ist'],
            _RX['doxiciclina_7d'],
        ],
        'exames': [
            'VDRL + FTA-ABS (sífilis)',
            'HIV (rápido ou ELISA)',
            'Cultura de secreção uretral/cervical se disponível (guia resistência)',
            'PCR/NAAT para Chlamydia trachomatis e N. gonorrhoeae (se disponível)',
            'Hepatite B e C (rastreamento no contexto de IST)',
        ],
        'encaminhar': None,
        'urgencia': None,
        'retorno': 'Test of cure: não rotineiro se sintomas resolvem. '
                   'Retornar se sintomas persistirem após 7 dias.',
    }


# =============================================================================
# VAGINITE / CONDIÇÕES VAGINAIS
# =============================================================================

def _avaliar_vaginite(dados):
    tipo = dados.get('corrimento_tipo', '')
    lesao = dados.get('lesao_genital')
    prurido = dados.get('prurido_genital')
    pos_meno = dados.get('peri_pos_menopausa')

    # ── Herpes genital (lesão + disúria) ───────────────────────────────────
    if lesao:
        primeiro = dados.get('herpes_primeiro_episodio', True)
        rx = _RX['aciclovir_primario'] if primeiro else _RX['aciclovir_recorrente']
        return {
            'tipo': 'urinario',
            'categoria': 'herpes_genital',
            'diagnostico': 'Herpes genital — {} episódio'.format(
                '1º' if primeiro else 'episódio recorrente'),
            'forca': 'moderada',
            'achados': [
                'Lesão genital (vesículas / úlceras dolorosas) + disúria',
                'Disúria por lesão cutânea periuretral — não ITU',
            ],
            'conduta': [
                'Diagnóstico clínico — confirmação laboratorial opcional na APS',
                'Orientar: herpes não tem cura, mas antiviral reduz duração / frequência',
                'Informar contágio mesmo sem lesão visível (período assintomático)',
                'Oferecer teste HIV + sífilis',
                'Se ≥6 recorrências/ano: oferecer supressão (ver aciclovir contínuo)',
            ],
            'prescricoes_estruturadas': [rx],
            'exames': [
                'HIV + sífilis (contexto de IST)',
                'Swab de lesão para PCR HSV (se disponível e diagnóstico incerto)',
            ],
            'encaminhar': 'DST/Ginecologia se gestante (risco de herpes neonatal)',
            'urgencia': None,
            'retorno': 'Retornar se lesões não cicatrizarem em 2 semanas ou piora dos sintomas.',
        }

    # ── Candidíase ─────────────────────────────────────────────────────────
    if prurido and tipo == 'grumoso_branco':
        gestante = dados.get('gestante')
        recorrente = dados.get('candidíase_recorrente', False)
        prescricoes = []
        if gestante:
            prescricoes.append({
                'linha': '1ª linha — gestante (via tópica)',
                'medicamento': 'Clotrimazol creme vaginal 100mg',
                'prescricoes': [{'quantidade': 7, 'unidade': 'aplicadores',
                                  'posologia': '1 aplicador via vaginal ao deitar × 7 dias'}],
                'nota': 'Fluconazol oral é CONTRAINDICADO na gestação. Uso tópico é seguro.',
            })
        else:
            prescricoes.append(_RX['fluconazol'])
            if recorrente:
                prescricoes.append(_RX['fluconazol_recorrente'])

        return {
            'tipo': 'urinario',
            'categoria': 'vaginite_candida',
            'diagnostico': 'Candidíase vulvovaginal',
            'forca': 'alta',
            'achados': [
                'Corrimento branco grumoso ("queijo cottage") + prurido vaginal',
                'pH vaginal < 4,5 (se disponível)',
                'Disúria por irritação periuretral — não ITU',
            ],
            'conduta': [
                'Diagnóstico clínico suficiente com apresentação típica',
                'Orientar: evitar sabonetes íntimos e roupas sintéticas apertadas',
                'Parceiro: tratar somente se candidíase peniana sintomática',
                'Rastrear DM se candidíase recorrente ou refratária',
            ],
            'prescricoes_estruturadas': prescricoes,
            'exames': [
                'Swab vaginal + KOH (se disponível — confirma hifas)',
                'Glicemia em jejum se ≥2 episódios/ano (rastrear DM)',
            ],
            'encaminhar': None,
            'urgencia': None,
            'retorno': 'Retornar se sem melhora em 72h (considerar espécie não-albicans).',
        }

    # ── Vaginose bacteriana ─────────────────────────────────────────────────
    if tipo == 'acinzentado' or (dados.get('secrecao_vaginal') and not prurido):
        return {
            'tipo': 'urinario',
            'categoria': 'vaginite_bv',
            'diagnostico': 'Vaginose bacteriana',
            'forca': 'moderada',
            'achados': [
                'Corrimento acinzentado homogêneo + odor de "peixe" (aminas)',
                'pH > 4,5 — flora de Gardnerella / anaeróbios (não é IST)',
            ],
            'conduta': [
                'Diagnóstico: ≥3 critérios de Amsel (corrimento, pH > 4,5, clue cells, '
                'amina test positivo)',
                'Parceiro: NÃO tratar rotineiramente (não é IST convencional)',
                'Evitar duchas vaginais (destroem flora normal)',
                'Se gestante: tratar (associada a parto prematuro)',
            ],
            'prescricoes_estruturadas': [_RX['metro_bv']],
            'exames': [
                'pH vaginal (papel pH ou fita — diagnóstico imediato)',
                'Bacterioscopia com Gram (critério de Nugent se disponível)',
            ],
            'encaminhar': None,
            'urgencia': None,
            'retorno': 'Retornar se recidiva em 3 meses (BV recorrente — considerar bórico).',
        }

    # ── Vaginite atrófica (genitourinary syndrome of menopause) ────────────
    if pos_meno and (dados.get('dispareunia') or dados.get('secrecao_vaginal')):
        return {
            'tipo': 'urinario',
            'categoria': 'vaginite_atrofica',
            'diagnostico': 'Síndrome geniturinária da menopausa (vaginite atrófica)',
            'forca': 'moderada',
            'achados': [
                'Peri / pós-menopausa + dispareunia + ressecamento vaginal / disúria',
                'Epitélio vaginal atrófico por hipoestrogenismo',
            ],
            'conduta': [
                'Estrogênio vaginal tópico: opção de 1ª linha (absorção sistêmica mínima)',
                'Alternativa não hormonal: hidratante vaginal 2–3×/semana (higiene + lubrificante)',
                'Orientar: não há contraindicação do estrogênio tópico em mulheres '
                'com história de Ca de mama, segundo dados mais recentes — discutir com '
                'oncologista em casos específicos',
                'Atividade sexual regular melhora trofismo vaginal',
            ],
            'prescricoes_estruturadas': [
                {
                    'linha': '1ª linha — hormonal tópica',
                    'medicamento': 'Estradiol creme vaginal 0,01%',
                    'prescricoes': [{'quantidade': 1, 'unidade': 'bisnaga',
                                     'posologia': '1 aplicador vaginal ao deitar '
                                                  '× 2 semanas (indução), '
                                                  'depois 2–3×/semana (manutenção)'}],
                    'nota': 'Absorção sistêmica mínima. Seguro na maioria das mulheres. '
                            'Disponível no SUS mediante solicitação (componente especializado).',
                },
            ],
            'exames': [
                'Colpocitologia (Papanicolau) em dia — excluir Ca colo / Ca endométrio',
                'FSH + estradiol se diagnóstico de menopausa incerto',
            ],
            'encaminhar': 'Ginecologia se não responder a estrogênio tópico após 3 meses',
            'urgencia': None,
            'retorno': 'Retorno em 6–8 semanas para avaliar resposta.',
        }

    # Fallback — corrimento sem caracterização suficiente
    return {
        'tipo': 'urinario',
        'categoria': 'sd_uretral',
        'diagnostico': 'Síndrome uretral / Queixa genital sem diagnóstico definido',
        'forca': 'baixa',
        'achados': ['Sintomas genitais sem padrão específico — investigação necessária'],
        'conduta': [
            'Exame ginecológico / urológico presencial para caracterizar secreção',
            'Colher pH vaginal, bacterioscopia e urocultura',
            'Excluir IST antes de tratar sintomaticamente',
        ],
        'prescricoes_estruturadas': [],
        'exames': [
            'Swab vaginal + bacterioscopia',
            'Urocultura + EAS',
            'VDRL + HIV (rastreamento IST)',
        ],
        'encaminhar': None,
        'urgencia': None,
        'retorno': 'Retorno com resultado dos exames.',
    }


# =============================================================================
# ROUTER — DISÚRIA
# =============================================================================

def _avaliar_disuria(dados):
    """Roteador principal para queixas de disúria."""
    sexo    = dados.get('sexo', 'F')
    ist     = dados.get('ist_risco') and (
                  dados.get('secrecao_uretral') or dados.get('secrecao_vaginal'))
    vaginal = (sexo == 'F') and (
                  dados.get('prurido_genital') or dados.get('lesao_genital') or
                  dados.get('secrecao_vaginal') or dados.get('corrimento_tipo') or
                  dados.get('peri_pos_menopausa'))

    # 1. Pielonefrite primeiro (sintomas sistêmicos)
    if _tem_pielonefrite(dados):
        return _avaliar_pielonefrite(dados)

    # 2. IST — ambos os sexos com descarga + risco
    if ist:
        return _avaliar_uretrite_ist(dados)

    # 3. Condição vaginal / genital (feminino)
    if vaginal:
        return _avaliar_vaginite(dados)

    # 4. Fluxo masculino
    if sexo == 'M':
        return _avaliar_urinario_masculino(dados)

    # 5. Cistite feminina (fluxo padrão)
    return _avaliar_cistite_feminina(dados)


# =============================================================================
# HEMATÚRIA
# =============================================================================

def _avaliar_hematuria(dados):
    macro   = dados.get('hematuria_macro')
    micro   = dados.get('hematuria_micro')
    idade   = dados.get('idade', 0)
    fumaca  = dados.get('hematuria_fumaca')
    colica  = dados.get('hematuria_colicativa')
    indolor = dados.get('hematuria_indolor')
    febre   = dados.get('febre')

    # Sinais de glomerulopatia — nefrologia urgente
    glomerular = any([
        fumaca,                            # cola-colored urine → glomerular
        dados.get('eas_cilindros'),
        dados.get('eas_hemacias_dismorfica'),
        dados.get('eas_proteinuria'),
    ])

    if glomerular:
        return {
            'tipo': 'urinario',
            'categoria': 'hematuria_micro_glomerular',
            'diagnostico': 'Hematúria com padrão glomerular',
            'forca': 'alta',
            'achados': list(filter(None, [
                'Urina cor de "coca-cola" / fumacenta' if fumaca else None,
                'Cilindros hemáticos no EAS' if dados.get('eas_cilindros') else None,
                'Hemácias dismórficas no EAS' if dados.get('eas_hemacias_dismorfica') else None,
                'Proteinúria associada' if dados.get('eas_proteinuria') else None,
            ])),
            'conduta': [
                'Solicitar perfil nefrológico completo enquanto aguarda vaga em nefrologia',
                'Controlar PA (alvo < 130/80 mmHg)',
                'Evitar AINEs — nefrotóxicos em glomerulopatia',
                'Se IgA nefropatia suspeita (jovem + hematúria pós-IVAS): '
                'calcular razão proteína/creatinina urinária',
            ],
            'prescricoes_estruturadas': [],
            'exames': [
                'EAS com sedimento (hematúria + cilindros + dismorfismo)',
                'Razão proteína/creatinina urinária (amostra isolada)',
                'Creatinina + eGFR',
                'Hemograma + PCR',
                'Complemento C3 e C4 (excluir pós-infecciosa, lúpus)',
                'ANA / anti-dsDNA se suspeita de lúpus',
                'ASLO (pós-infecciosa)',
                'PA seriada',
            ],
            'encaminhar': 'Nefrologia — urgente se creatinina elevada ou proteinúria > 1g/dia; '
                          'eletivo se função renal preservada',
            'urgencia': 'urgente',
            'retorno': 'Monitorar PA e função renal semanalmente enquanto aguarda nefrologia.',
        }

    # Hematúria macroscópica
    if macro:
        # Com ITU — tratar e repetir EAS
        if febre or dados.get('disuria') or dados.get('frequencia'):
            return {
                'tipo': 'urinario',
                'categoria': 'hematuria_macro_itu',
                'diagnostico': 'Hematúria macroscópica no contexto de ITU',
                'forca': 'alta',
                'achados': [
                    'Hematúria macroscópica + sintomas de cistite',
                    'Causa mais provável: cistite hemorrágica',
                    'Obrigatório: repetir EAS 6 semanas após cura para excluir Ca',
                ],
                'conduta': [
                    'Tratar ITU (ver fluxo de cistite)',
                    'Repetir EAS + urocultura 6 semanas após término do ATB',
                    'Se hematúria persistir após cura: encaminhar urologia (excluir Ca bexiga)',
                ],
                'prescricoes_estruturadas': [],   # usar resultado de _avaliar_cistite_feminina
                'exames': [
                    'Urocultura + antibiograma',
                    'EAS (agora + controle em 6 semanas)',
                    'USG vias urinárias se hematúria não resolver após ATB',
                ],
                'encaminhar': 'Urologia se hematúria persistir após tratamento da ITU',
                'urgencia': None,
                'retorno': 'Retorno em 6 semanas com EAS de controle.',
            }

        # Cólica + calculose — manejo ambulatorial
        if colica or dados.get('litíase_previa'):
            return {
                'tipo': 'urinario',
                'categoria': 'hematuria_macro_calculose',
                'diagnostico': 'Hematúria macroscópica — cálculo urinário provável',
                'forca': 'moderada',
                'achados': [
                    'Hematúria macroscópica + dor colicativa em flanco',
                    'Litíase prévia ou calculose no contexto clínico',
                ],
                'conduta': [
                    'Analgesia: Dipirona 1g VO 6/6h ± Ibuprofeno 400mg VO 8/8h (anti-espástico)',
                    'Hidratação oral intensa ≥ 3L/dia (facilita expulsão)',
                    'Tamsulosina 0,4mg/dia × 4 semanas: terapia expulsiva para cálculos '
                    '5–10 mm no ureter distal (NNT ~7)',
                    'Filtrar urina (coletor ou gaze) para capturar o cálculo — análise mineral',
                    'Retorno imediato se: febre (obstrução infectada = emergência), '
                    'dor incontrolável, anúria, rim único',
                ],
                'prescricoes_estruturadas': [
                    {
                        'linha': 'Analgesia — cólica',
                        'medicamento': 'Dipirona 1000mg',
                        'prescricoes': [{'quantidade': 20, 'unidade': 'comprimidos',
                                         'posologia': '2cp VO 6/6h conforme dor'}],
                        'nota': 'Se dor severa não controlada: PA para analgesia IV.',
                    },
                    _RX['tamsulosina'],
                ],
                'exames': [
                    'USG rins e vias urinárias (confirmar cálculo, excluir obstrução)',
                    'EAS (hematúria + leucocitúria? → excluir infecção associada)',
                    'Creatinina (função renal)',
                    'Urina 24h (oxalato, cálcio, ácido úrico — após episódio agudo, '
                    'para investigar litíase recorrente)',
                ],
                'encaminhar': 'Urologia urgente se: febre + obstrução, anúria, rim único, '
                              'cálculo > 10mm (improvável expulsão espontânea)',
                'urgencia': None,
                'retorno': 'Retorno em 4 semanas. USG controle para confirmar expulsão.',
            }

        # Macro sem causa óbvia → risco de neoplasia
        alto_risco_neoplasia = any([
            idade >= 35,
            dados.get('tabagismo'),
            dados.get('exposicao_ocupacional'),
            dados.get('radioterapia_pelvica'),
            indolor,
        ])

        return {
            'tipo': 'urinario',
            'categoria': 'hematuria_macro_urgente',
            'diagnostico': 'Hematúria macroscópica sem causa aparente — '
                           'neoplasia a excluir' if alto_risco_neoplasia
                           else 'Hematúria macroscópica — investigação necessária',
            'forca': 'alta',
            'achados': list(filter(None, [
                'Hematúria macroscópica sem ITU ativa, sem cólica',
                f'Idade ≥ 35 anos — risco aumentado de Ca bexiga' if idade >= 35 else None,
                'Tabagismo — principal fator de risco para Ca bexiga' if dados.get('tabagismo') else None,
                'Hematúria indolor — característica mais preocupante (Ca bexiga)' if indolor else None,
            ])),
            'conduta': [
                'Solicitar workup inicial enquanto encaminha para urologia',
                'Encaminhar urologia em até 2 semanas (critério de referência prioritária)',
                'Informar o paciente sobre a necessidade de investigação para excluir neoplasia',
            ],
            'prescricoes_estruturadas': [],
            'exames': [
                'Urocultura (excluir ITU)',
                'EAS com sedimento',
                'USG rins + bexiga (1ª imagem — excluir massa)',
                'Creatinina + eGFR',
                'PSA se homem ≥ 50 anos',
                'Citologia urinária (se disponível — Ca bexiga)',
            ],
            'encaminhar': 'Urologia — em até 2 semanas (critério de urgência moderada)',
            'urgencia': 'urgente',
            'retorno': 'Acompanhar resultado de exames e confirmar agendamento urológico.',
        }

    # Hematúria microscópica
    if micro or dados.get('eas_hemacias'):
        hpf = dados.get('eas_hemacias_hpf', 5)
        tabagismo = dados.get('tabagismo')
        alto_risco = any([
            idade >= 60,
            tabagismo,
            dados.get('exposicao_ocupacional'),
            hpf >= 25,
        ])
        moderado_risco = any([
            35 <= idade < 60,
            10 <= hpf < 25,
        ])

        if alto_risco:
            return {
                'tipo': 'urinario',
                'categoria': 'hematuria_micro_alto_risco',
                'diagnostico': 'Hematúria microscópica — alto risco (AUA 2020)',
                'forca': 'alta',
                'achados': list(filter(None, [
                    f'{hpf} hemácias/campo no EAS',
                    'Idade ≥ 60 anos' if idade >= 60 else None,
                    'Tabagismo' if tabagismo else None,
                    '≥ 25 RBC/campo' if hpf >= 25 else None,
                ])),
                'conduta': [
                    'Excluir causas transitórias (repetir EAS após afastar menstruação, exercício, cateterismo)',
                    'Solicitar workup completo ambulatorial',
                    'Encaminhar urologia para cistoscopia + TC urografia',
                ],
                'prescricoes_estruturadas': [],
                'exames': [
                    'Repetir EAS (2ª amostra — confirmar persistência)',
                    'Urocultura (excluir ITU ativa)',
                    'USG rins + bexiga',
                    'Creatinina + eGFR',
                    'Razão proteína/creatinina urinária',
                    'Citologia urinária',
                ],
                'encaminhar': 'Urologia — cistoscopia + TC urografia (protocolo AUA alto risco)',
                'urgencia': 'urgente',
                'retorno': 'Confirmar resultado dos exames e agendamento urológico.',
            }

        if moderado_risco:
            return {
                'tipo': 'urinario',
                'categoria': 'hematuria_micro_moderado_risco',
                'diagnostico': 'Hematúria microscópica — risco moderado (AUA 2020)',
                'forca': 'moderada',
                'achados': [
                    f'{hpf} hemácias/campo',
                    f'Idade {idade} anos',
                ],
                'conduta': [
                    'Repetir EAS em 6–12 semanas (excluir causa transitória)',
                    'Solicitar USG e citologia',
                    'Encaminhar urologia se persistente',
                ],
                'prescricoes_estruturadas': [],
                'exames': [
                    'EAS de controle (6–12 semanas)',
                    'USG rins + bexiga',
                    'Creatinina + eGFR',
                    'Razão proteína/creatinina urinária',
                    'Citologia urinária (opcional — compartilhar decisão)',
                ],
                'encaminhar': 'Urologia eletivo se hematúria persistir em 2 amostras',
                'urgencia': 'eletivo',
                'retorno': 'Retorno em 6–12 semanas com EAS de controle.',
            }

        # Baixo risco — monitorar na APS
        return {
            'tipo': 'urinario',
            'categoria': 'hematuria_micro_baixo_risco',
            'diagnostico': 'Hematúria microscópica — baixo risco (AUA 2020)',
            'forca': 'baixa',
            'achados': [
                f'{hpf} hemácias/campo',
                f'Paciente {idade} anos sem fatores de risco',
                'IgA nefropatia é causa comum em jovens (hematúria pós-IVAS, '
                'transitória, sem proteinúria)',
            ],
            'conduta': [
                'Excluir causas transitórias (menstruação, exercício intenso, relação sexual)',
                'Monitorar com EAS seriados na APS',
                'Se desenvolver proteinúria, hipertensão ou piora da função renal: '
                'encaminhar nefrologia',
            ],
            'prescricoes_estruturadas': [],
            'exames': [
                'EAS seriado (a cada 6–12 meses)',
                'Creatinina + eGFR',
                'PA seriada',
                'Razão proteína/creatinina urinária (uma vez)',
                'USG rins (uma vez — excluir massa)',
            ],
            'encaminhar': 'Nefrologia se: proteinúria, HAS, função renal em queda. '
                          'Urologia eletivo se cistoscopia solicitada (decisão compartilhada)',
            'urgencia': None,
            'retorno': 'EAS de controle em 6 meses. Medir PA a cada consulta.',
        }

    # Sem hematúria confirmada
    return {
        'tipo': 'urinario',
        'categoria': 'hematuria_nao_confirmada',
        'diagnostico': 'Hematúria não confirmada',
        'forca': 'baixa',
        'achados': ['Queixa de hematúria sem confirmação em EAS'],
        'conduta': [
            'Coletar EAS em 2ª amostra (mid-stream, fora de menstruação / exercício)',
            'Se EAS normal em 2 amostras: orientar sobre causas de alteração de cor '
            '(beterraba, rifampicina, pimentão)',
        ],
        'prescricoes_estruturadas': [],
        'exames': ['EAS com sedimento (2ª amostra em período adequado)'],
        'encaminhar': None,
        'urgencia': None,
        'retorno': 'Retorno com resultado do EAS.',
    }


# =============================================================================
# PONTO DE ENTRADA PRINCIPAL
# =============================================================================

def interpretar_queixa_urinaria(dados):
    """
    Interpreta queixas urinárias (disúria e/ou hematúria).

    Parâmetros
    ----------
    dados : dict  — ver cabeçalho do módulo para campos esperados

    Retorna
    -------
    dict com:
        tipo                   : 'urinario'
        categoria              : str
        diagnostico            : str
        forca                  : 'alta' | 'moderada' | 'baixa'
        achados                : list[str]
        conduta                : list[str]
        prescricoes_estruturadas : list[dict]   ← para renderer _plano_urinario()
        exames                 : list[str]
        encaminhar             : str | None
        urgencia               : 'emergencia' | 'urgente' | 'eletivo' | None
        red_flags              : list[dict]
        retorno                : str
    """
    # 1. Red flags — têm prioridade absoluta
    red_flags = _avaliar_red_flags(dados)
    if red_flags:
        urgencia_max = 'emergencia'
        acoes = '\n'.join(f['acao'] for f in red_flags)
        return {
            'tipo': 'urinario',
            'categoria': 'red_flag_urinario',
            'diagnostico': 'Sinal de alarme urinário — avaliação imediata',
            'forca': 'alta',
            'achados': [f['achado'] for f in red_flags],
            'conduta': [f['acao'] for f in red_flags],
            'prescricoes_estruturadas': [],
            'exames': [],
            'encaminhar': 'PA/PS imediatamente',
            'urgencia': urgencia_max,
            'red_flags': red_flags,
            'retorno': 'Seguimento ambulatorial após avaliação presencial.',
        }

    # 2. Roteamento por queixa
    queixa = dados.get('queixa_principal', 'disuria')

    # Hematúria pura (sem sintomas de ITU)
    if queixa == 'hematuria' and not dados.get('disuria') and not dados.get('frequencia'):
        resultado = _avaliar_hematuria(dados)
        resultado['red_flags'] = []
        return resultado

    # Disúria com ou sem hematúria
    resultado = _avaliar_disuria(dados)
    resultado['red_flags'] = []

    # Se também tem hematúria macroscópica sem explicação pela disúria → adicionar nota
    if dados.get('hematuria_macro') and resultado.get('categoria') == 'cistite_simples':
        resultado['conduta'].append(
            'Repetir EAS após 6 semanas do término do ATB para confirmar resolução da hematúria '
            '(excluir neoplasia subjacente).'
        )

    return resultado
