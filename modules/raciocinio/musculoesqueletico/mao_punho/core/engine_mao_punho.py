# modules/raciocinio/musculoesqueletico/mao_punho/core/engine_mao_punho.py
# Motor de raciocínio clínico — Mão, Punho e Dedos
# Categorias únicas: trauma_escafoide_suspeito | tunel_do_carpo |
#                    de_quervain | dedo_em_gatilho | rizartrose_thumb_cmc |
#                    suspeita_artrite_reumatoide | avaliacao_mao_punho

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
from modules.raciocinio.musculoesqueletico.red_flags_msk import aplicar_trava_idoso_aine


# =============================================================================
# RED FLAGS (transversais)
# =============================================================================

def _avaliar_red_flags(dados):
    flags = []

    if dados.get('atrofia_tenar') or dados.get('atrofia_tenar_percebida'):
        flags.append({
            'achado': 'Atrofia tenar — síndrome do túnel do carpo moderada/grave',
            'urgencia': 'urgente',
            'acao': (
                'Encaminhamento urgente para cirurgia de mao (liberacao do carpo). '
                'EMG/ENMG pode ser solicitada pelo cirurgiao, nao necessária na APS classica.'
            ),
        })

    if dados.get('tabaqueira_positiva') and dados.get('mecanismo_queda_mao_espalmada'):
        flags.append({
            'achado': 'Tabaqueira anatomica positiva após trauma — fratura do escafoide a excluir',
            'urgencia': 'urgente',
            'acao': (
                'Imobilizar com tala de polegar MESMO se XR normal (falso-negativo: 30%). '
                'Repetir XR em 10-14 dias ou solicitar RM/cintilografia. '
                'Nao tratar como entorse sem imobilizacao.'
            ),
        })

    return {'flags': flags} if flags else {}


# =============================================================================
# TRAUMA — ESCAFOIDE
# =============================================================================

def _avaliar_trauma_escafoide(dados):
    score = 0
    positivos = []

    if dados.get('tabaqueira_positiva'):
        score += 5
        positivos.append('Tabaqueira anatomica positiva (S ~90%)')
    if dados.get('mecanismo_queda_mao_espalmada'):
        score += 3
        positivos.append('Mecanismo de queda FOOSH (queda com mao espalmada)')
    if dados.get('compressao_axial_polegar_positiva'):
        score += 3
        positivos.append('Compressao axial do polegar reproduz dor (telescoping positivo)')
    if dados.get('tuberculo_escafoide_palmar'):
        score += 2
        positivos.append('Dor no tuberculo do escafoide (face palmar)')
    if dados.get('edema_punho_pos_trauma'):
        score += 1
        positivos.append('Edema do punho pos-trauma')
    if dados.get('limitacao_movimento_trauma'):
        score += 1
        positivos.append('Limitacao de movimento pos-trauma')

    if score >= 8:
        forca = 'alta'
    elif score >= 5:
        forca = 'moderada'
    else:
        forca = 'baixa'

    return {
        'categoria': 'trauma_escafoide_suspeito',
        'hipotese': 'Fratura do Escafoide (suspeita)',
        'score': score,
        'forca': forca,
        'positivos': positivos,
        'conduta_nao_farmacologica': [
            'Imobilizar com tala de polegar (thumb spica) IMEDIATAMENTE',
            'Solicitar RX em incidencias especificas: PA em desvio ulnar, obliquo pronado',
            'Se XR normal e suspeita mantida: repetir XR em 10-14 dias',
            'Se ainda negativo e suspeita persistente: RM ou cintilografia ossea',
            'NAO dispensar como entorse sem imobilizacao (risco de necrose avascular)',
        ],
        'farmacologico': [
            'Paracetamol 500-1000mg 6/6h (analgesia durante imobilizacao)',
            'AINE curto prazo se sem contraindicacao: ibuprofeno 400mg 8/8h',
        ],
        'encaminhar': 'Ortopedia / cirurgia de mao para seguimento e confirmacao diagnostica',
        'imagem': 'RX inicialmente; RM se negativo e suspeita clinica mantida',
    }


# =============================================================================
# TUNEL DO CARPO (STC)
# =============================================================================

def _avaliar_stc(dados):
    score = 0
    positivos = []

    if dados.get('durkan_positivo'):
        score += 4
        positivos.append('Durkan positivo (S 64%, E 83%) — melhor teste isolado')
    if dados.get('phalen_positivo'):
        score += 3
        positivos.append('Phalen positivo (S 68%, E 73%)')
    if dados.get('parestesia_territorio_mediano') or dados.get('parestesia_noturna'):
        score += 3
        positivos.append('Parestesia noturna em territorio mediano (polegar/indicador/medio)')
    if dados.get('alivio_sacudir_mao'):
        score += 2
        positivos.append('Alívio ao sacudir a mao (flick sign — patognomônico de STC)')
    if dados.get('tinel_positivo'):
        score += 1
        positivos.append('Tinel positivo (S 50%, E 77%)')
    if dados.get('piora_trabalho_computador') or dados.get('uso_vibracoes'):
        score += 1
        positivos.append('Fator ocupacional (teclado/mouse/vibracoes)')
    if dados.get('diabetes_mellitus') or dados.get('obesidade') or dados.get('gestante_ou_puerpera'):
        score += 1
        positivos.append('Fator de risco presente (diabetes/obesidade/gravidez)')
    if dados.get('fraqueza_pinca_oponencia'):
        score += 2
        positivos.append('Fraqueza de pinça ou oponência — STC moderado/grave')

    if score >= 10:
        forca = 'alta'
    elif score >= 6:
        forca = 'moderada'
    else:
        forca = 'baixa'

    grave = dados.get('atrofia_tenar') or dados.get('atrofia_tenar_percebida') or dados.get('fraqueza_pinca_oponencia')

    conduta_tala = (
        'Tala noturna em posicao NEUTRA do punho — NESTE caso encaminhamento urgente '
        'é prioritário, tala serve de suporte até a cirurgia.'
        if grave else
        'Tala noturna em posicao NEUTRA do punho por 6 semanas (nao em extensao). '
        'Evitar tala diurna — risco de postura compensatoria. '
        'Evidencia: 100% vs 25% de melhora vs sem tratamento em 4 semanas.'
    )

    return {
        'hipotese': 'Síndrome do Túnel do Carpo (STC)',
        'score': score,
        'forca': forca,
        'positivos': positivos,
        'alerta_grave': grave,
        'conduta_nao_farmacologica': [
            conduta_tala,
            'Exercicios de deslizamento neural (nerve gliding): 6 posicoes, 2x/dia',
            'Exercicios de deslizamento tendíneo: posicoes reta/gancho/punho/table top',
            'Modificacao ergonomica: altura de teclado, posicionamento do mouse',
            'Tecnica de Madenci (massagem) como complemento ao uso de tala',
        ],
        'farmacologico': [
            'AINE oral curto prazo: ibuprofeno 400mg 8/8h por 2-4 semanas',
            'Infiltracao de corticosteroide no canal do carpo: alivia sintomas (temporario)',
            'Nao indicar EMG/ENMG em APS classica — solicitar se duvida diagnostica ou pre-cirurgia',
        ],
        'encaminhar': (
            'Cirurgia de mao URGENTE — atrofia tenar / fraqueza grave'
            if grave else
            'Cirurgia de mao se falha apos 6 semanas de tratamento conservador'
        ),
        'imagem': 'USG do nervo mediano: S 81%, E 84% — util se diagnostico incerto',
    }


# =============================================================================
# DE QUERVAIN
# =============================================================================

def _avaliar_de_quervain(dados):
    score = 0
    positivos = []

    if dados.get('finkelstein_positivo'):
        score += 6
        positivos.append('Finkelstein positivo (Especificidade 100% para De Quervain)')
    if dados.get('dor_radial_punho') or dados.get('dor_tabaqueira_anatomica'):
        score += 2
        positivos.append('Dor dorsorradial do punho (1o compartimento extensor)')
    if dados.get('piora_movimento_polegar'):
        score += 2
        positivos.append('Piora ao mover o polegar (pincar, segurar, desvio)')
    if dados.get('uso_smartphone_intenso'):
        score += 1
        positivos.append('Uso intenso de smartphone (associacao OR 2.89 em jovens)')
    if dados.get('trabalho_manual_repetitivo'):
        score += 1
        positivos.append('Trabalho manual repetitivo (OR 2.89 para De Quervain)')
    if dados.get('gestante_pos_parto') or dados.get('gestante_ou_puerpera'):
        score += 1
        positivos.append('Gestante / pos-parto (fator de risco hormonal/mecanico)')

    if score >= 8:
        forca = 'alta'
    elif score >= 4:
        forca = 'moderada'
    else:
        forca = 'baixa'

    return {
        'hipotese': 'Tenossinovite de De Quervain',
        'score': score,
        'forca': forca,
        'positivos': positivos,
        'conduta_nao_farmacologica': [
            'Tala Thumb Spica: imobiliza polegar + punho. Usar COMBINADA com infiltracao',
            '(sucesso: tala + infiltracao 90% vs infiltracao isolada 66% vs tala isolada 47%)',
            'Modificacao de atividade: reduzir uso de smartphone, evitar movimentos repetitivos de polegar',
        ],
        'farmacologico': [
            'Infiltracao de corticosteroide no 1o compartimento extensor: 1a linha',
            '72% de sucesso na 1a infiltracao; 66% na 2a; 61% na 3a',
            'AINE oral: ibuprofeno 400mg 8/8h por 2 semanas (adjuvante)',
        ],
        'encaminhar': 'Cirurgia (liberacao do 1o compartimento extensor) se falha apos 6 semanas de tratamento',
    }


# =============================================================================
# DEDO EM GATILHO
# =============================================================================

def _avaliar_dedo_em_gatilho(dados):
    score = 0
    positivos = []

    if dados.get('gatilho_bloqueio_ativo'):
        score += 5
        positivos.append('Bloqueio ou estalido ativo ao fletir/estender o dedo')
    if dados.get('polia_a1_dor_nodulo'):
        score += 4
        positivos.append('Nodulo doloroso palpável na polia A1 (palma, base do dedo)')
    if dados.get('estalido_bloqueio_dedo'):
        score += 3
        positivos.append('Historia de travamento ou estalido ao mover o dedo')
    if dados.get('nodulo_palpavel_palma'):
        score += 2
        positivos.append('Nodulo percebido pelo paciente na palma')
    if dados.get('diabetes_mellitus'):
        score += 1
        positivos.append('Diabetes mellitus (prevalencia de 20% de dedo em gatilho em DM)')

    if score >= 8:
        forca = 'alta'
    elif score >= 5:
        forca = 'moderada'
    else:
        forca = 'baixa'

    dm = dados.get('diabetes_mellitus')

    return {
        'hipotese': 'Dedo em Gatilho (Tenossinovite Estenosante)',
        'score': score,
        'forca': forca,
        'positivos': positivos,
        'alerta_diabetes': dm,
        'conduta_nao_farmacologica': [
            'Tala de extensao do dedo afetado durante a noite (repouso da polia)',
            'Exercicios suaves de deslizamento tendíneo',
            'Modificacao de atividade: reduzir apreensoes forcadas',
        ],
        'farmacologico': [
            'Infiltracao de corticosteroide na bainha tendínea da polia A1: 1a linha',
            f'{"ALERTA DM: menor eficacia e risco de hiperglicemia — monitorar glicemia apos infiltracao." if dm else "Taxa de recidiva: 22% vs 0.4% cirurgia (RR 19.53 — cirurgia muito superior a longo prazo)."}',
            'AINE oral curto prazo como adjuvante para dor',
        ],
        'encaminhar': (
            'Cirurgia precoce considerada em DM insulino-dependente (melhor resposta).'
            if dm else
            'Cirurgia (liberacao da polia A1) se recorrente ou sem resposta a 2-3 infiltracoes.'
        ),
    }


# =============================================================================
# RIZARTROSE THUMB CMC
# =============================================================================

def _avaliar_rizartrose(dados):
    score = 0
    positivos = []

    if dados.get('grind_test_positivo'):
        score += 5
        positivos.append('Axial grind test positivo (E 97% para rizartrose CMC)')
    if dados.get('traction_shift_positivo'):
        score += 5
        positivos.append('Traction shift test positivo (E 100%)')
    if dados.get('dor_base_polegar_cmC') or dados.get('piora_pincar_girar'):
        score += 3
        positivos.append('Dor na base do polegar ao pincar/girar')
    if dados.get('proeminencia_dorsal_polegar') or dados.get('deformidade_visivel'):
        score += 2
        positivos.append('Proeminencia dorsal na CMC do polegar (sinal radiologico classico)')
    if dados.get('pos_menopausa_feminino'):
        score += 1
        positivos.append('Feminino pos-menopausa (~33% prevalencia radiologica)')
    if dados.get('dor_cronica'):
        score += 1
        positivos.append('Quadro cronico (OA e progressiva)')

    if score >= 10:
        forca = 'alta'
    elif score >= 5:
        forca = 'moderada'
    else:
        forca = 'baixa'

    return {
        'hipotese': 'Rizartrose do Polegar (Artrose CMC)',
        'score': score,
        'forca': forca,
        'positivos': positivos,
        'conduta_nao_farmacologica': [
            'Tala para CMC do polegar: melhora dor (SMD 0.70) e funcao (SMD 0.42) em 3-12 meses',
            'Exercicios de fortalecimento do polegar (banda elastica, pinça com Thera-Band)',
            'Adaptacao de atividades: evitar pinça de precisao forcada, usar utensilios adaptados',
        ],
        'farmacologico': [
            'AINE oral: ibuprofeno 400mg 8/8h por 2-4 semanas (1a linha para dor)',
            'Infiltracao de corticosteroide na CMC: alivia dor temporariamente (nao altera progressao)',
            'Capsaicina topica ou diclofenaco gel como alternativa menos sistemica',
        ],
        'encaminhar': 'Ortopedia se sem resposta ao conservador (multiplas opcoes cirurgicas disponíveis)',
        'imagem': 'RX da CMC do polegar: incidencias de Robert e lateral — confirma diagnostico',
    }


# =============================================================================
# ARTRITE REUMATOIDE (SUSPEITA)
# =============================================================================

def _avaliar_suspeita_ar(dados):
    score = 0
    positivos = []

    if dados.get('rigidez_matinal_prolongada') or dados.get('rigidez_matinal_>30'):
        score += 4
        positivos.append('Rigidez matinal > 30 minutos (criterio de classificacao ACR/EULAR)')
    if dados.get('sinovite_mcf_punho') or dados.get('mcf_punho_afetados'):
        score += 4
        positivos.append('Sinovite de MCF e/ou punhos (distribuicao classica de AR)')
    if dados.get('acometimento_simetrico'):
        score += 3
        positivos.append('Acometimento simetrico bilateral')
    if dados.get('ifd_poupadas_exame') or dados.get('ifd_preservadas'):
        score += 2
        positivos.append('IFD poupadas (distingue AR de OA/psoriasica)')
    if dados.get('squeeze_mcf_positivo'):
        score += 2
        positivos.append('Squeeze test MCF positivo (edema sinovial)')
    if dados.get('sintomas_sistemicos'):
        score += 1
        positivos.append('Fadiga / mal-estar sistemico associado')
    if dados.get('historico_artrite'):
        score += 1
        positivos.append('Historia pessoal ou familiar de artrite reumatoide')

    if score >= 12:
        forca = 'alta'
    elif score >= 7:
        forca = 'moderada'
    else:
        forca = 'baixa'

    return {
        'hipotese': 'Suspeita de Artrite Reumatoide',
        'score': score,
        'forca': forca,
        'positivos': positivos,
        'conduta_nao_farmacologica': [
            'Educacao sobre protecao articular e conservacao de energia',
            'Terapia ocupacional: adaptacao de utensilios, treino de AVD',
            'Exercicios de mobilidade dentro dos limites de conforto',
        ],
        'farmacologico': [
            'AINE oral como ponte enquanto aguarda avaliacao reumatologica',
            'NAO iniciar DMARD (Metotrexato, Hidroxicloroquina) sem confirmacao reumatologica',
        ],
        'workup': [
            'VHS e PCR (marcadores inflamatorios)',
            'Fator Reumatoide (FR)',
            'Anti-CCP (anti-peptideo citrulinado ciclico) — maior especificidade para AR',
            'Hemograma completo, funcao renal e hepatica (baseline pre-DMARD)',
            'RX maos e punhos: erosoes precoces sao indicativas',
        ],
        'encaminhar': 'Reumatologia (nao urgente, mas prioritario — DMARD precoce melhora prognostico)',
    }


# =============================================================================
# INTEGRAÇÃO — INTERPRETA
# =============================================================================

def interpretar_mao_punho(dados):
    """Ponto de entrada principal."""

    red_flags = _avaliar_red_flags(dados)
    padrao    = dados.get('padrao_clinico', '')

    # ── Red flags críticas (emergência) ─────────────────────────────────
    flags_criticas = [f for f in red_flags.get('flags', []) if f['urgencia'] == 'emergencia']
    if flags_criticas:
        return {
            'categoria': 'red_flag_mao_punho',
            'red_flags': {'flags': flags_criticas},
        }

    # ── Trauma ──────────────────────────────────────────────────────────
    if padrao == 'trauma':
        resultado = _avaliar_trauma_escafoide(dados)
        resultado['red_flags'] = red_flags
        # Trava de segurança — AINE vetado em ≥ 60 anos (dict plano com 'farmacologico')
        aplicar_trava_idoso_aine([resultado], dados)
        return resultado

    # ── Neurológico — determinar STC vs ulnar ───────────────────────────
    if padrao == 'neurologico':
        stc = _avaliar_stc(dados)
        resultado = {
            'categoria': 'tunel_do_carpo',
            'red_flags': red_flags,
        }
        if stc['forca'] in ('alta', 'moderada'):
            resultado['hipoteses_provaveis'] = [stc]
            resultado['hipoteses_possiveis'] = []
        else:
            resultado['hipoteses_provaveis'] = []
            resultado['hipoteses_possiveis'] = [stc]

        # Trava de segurança — AINE vetado em ≥ 60 anos
        aplicar_trava_idoso_aine(resultado['hipoteses_provaveis'], dados)
        aplicar_trava_idoso_aine(resultado['hipoteses_possiveis'], dados)

        if dados.get('froment_positivo') or dados.get('parestesia_territorio_ulnar'):
            resultado['alerta_ulnar'] = (
                'Sinal de Froment positivo / parestesia ulnar: considerar neuropatia ulnar. '
                'Solicitar ENMG para diferenciar e localizar compressao.'
            )
        return resultado

    # ── Mecânico — múltiplas hipóteses por score ────────────────────────
    if padrao == 'mecanico':
        hipoteses = []

        dq = _avaliar_de_quervain(dados)
        if dq['score'] >= 4:
            hipoteses.append(('de_quervain', dq))

        gt = _avaliar_dedo_em_gatilho(dados)
        if gt['score'] >= 5:
            hipoteses.append(('dedo_em_gatilho', gt))

        rz = _avaliar_rizartrose(dados)
        if rz['score'] >= 5:
            hipoteses.append(('rizartrose_thumb_cmc', rz))

        hipoteses.sort(key=lambda x: x[1]['score'], reverse=True)

        if not hipoteses:
            return {
                'categoria': 'avaliacao_mao_punho',
                'red_flags': red_flags,
                'hipoteses_provaveis': [],
                'hipoteses_possiveis': [],
                'mensagem': 'Dados insuficientes para hipótese de força moderada ou alta. Reavaliar com exame físico.',
            }

        categoria_principal = hipoteses[0][0]
        provaveis  = [h for _, h in hipoteses if h['forca'] in ('alta', 'moderada')]
        possiveis  = [h for _, h in hipoteses if h['forca'] == 'baixa']

        # Trava de segurança — AINE vetado em ≥ 60 anos
        aplicar_trava_idoso_aine(provaveis, dados)
        aplicar_trava_idoso_aine(possiveis, dados)

        return {
            'categoria': categoria_principal,
            'red_flags': red_flags,
            'hipoteses_provaveis': provaveis,
            'hipoteses_possiveis': possiveis,
        }

    # ── Reumatológico ───────────────────────────────────────────────────
    if padrao == 'reumatologico':
        ar       = _avaliar_suspeita_ar(dados)
        provaveis = [ar] if ar['forca'] in ('alta', 'moderada') else []
        possiveis = [ar] if ar['forca'] == 'baixa' else []
        # Trava de segurança — AINE vetado em ≥ 60 anos
        aplicar_trava_idoso_aine(provaveis, dados)
        aplicar_trava_idoso_aine(possiveis, dados)
        return {
            'categoria': 'suspeita_artrite_reumatoide',
            'red_flags': red_flags,
            'hipoteses_provaveis': provaveis,
            'hipoteses_possiveis': possiveis,
        }

    # ── Fallback ────────────────────────────────────────────────────────
    return {
        'categoria': 'avaliacao_mao_punho',
        'red_flags': red_flags,
        'hipoteses_provaveis': [],
        'hipoteses_possiveis': [],
        'mensagem': 'Padrão clínico não definido — realizar anamnese direcionada.',
    }
