# modules/raciocinio/musculoesqueletico/tornozelo_pe/core/engine_tornozelo_pe.py
# Motor de raciocínio clínico — Dor no Tornozelo e Pé
# Categorias únicas: trauma_ottawa_positivo | entorse_tornozelo |
#                    fasciite_plantar | tendinopatia_aquiles | morton_neuroma

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
from modules.raciocinio.musculoesqueletico.red_flags_msk import aplicar_trava_idoso_aine


# =============================================================================
# RED FLAGS (transversais — verificados antes de qualquer hipótese)
# =============================================================================

def _avaliar_red_flags(dados):
    flags = []

    if dados.get('thompson_positivo'):
        flags.append({
            'achado': 'Sinal de Thompson positivo — suspeita de ruptura do tendão de Aquiles',
            'urgencia': 'emergencia',
            'acao': 'Encaminhamento imediato a ortopedia. CONTRAINDICADO: corticosteroide local.',
        })

    if dados.get('deformidade_visivel') and dados.get('trauma_recente'):
        flags.append({
            'achado': 'Deformidade óssea visível após trauma',
            'urgencia': 'emergencia',
            'acao': 'Suspeita de fratura com desvio — PS ortopédico urgente.',
        })

    if dados.get('sinais_flogisticos') and dados.get('febre_sistemica'):
        flags.append({
            'achado': 'Sinais flogísticos + febre — artrite séptica a descartar',
            'urgencia': 'emergencia',
            'acao': 'Hemocultura, artrocentese diagnóstica, antibioticoterapia precoce. PS urgente.',
        })

    return {'flags': flags} if flags else {}


# =============================================================================
# ALERTA TRANSVERSAL — Corticosteroide Aquiles
# =============================================================================

def _alerta_corticosteroide_aquiles(dados):
    """Bloqueio de CSI para Aquiles — risco de ruptura."""
    if dados.get('dor_zona_critica_aquiles') or dados.get('dor_insercao_aquiles'):
        return {
            'alerta': True,
            'mensagem': (
                'CORTICOSTEROIDE INTRA-TENDINOSO: CONTRAINDICADO no tendão de Aquiles. '
                'Risco de ruptura espontânea. Usar apenas Alfredson protocol.'
            ),
        }
    return {'alerta': False}


# =============================================================================
# TRAUMA — Ottawa Rules
# =============================================================================

def _avaliar_trauma(dados):
    """Trauma presente: Ottawa positivo = RX; negativo = entorse."""
    ottawa = any([
        dados.get('ottawa_positivo'),
        dados.get('ottawa_exame_positivo'),
        dados.get('palpacao_maleolo_lateral_positiva'),
        dados.get('palpacao_maleolo_medial_positiva'),
        dados.get('palpacao_base_5o_meta_positiva'),
        dados.get('palpacao_navicular_positiva'),
        dados.get('incapaz_apoio_exame'),
        dados.get('incapaz_apoio_4_passos'),
    ])

    if ottawa:
        return {
            'categoria': 'trauma_ottawa_positivo',
            'achados_positivos': _listar_ottawa_positivos(dados),
            'conduta': [
                'Solicitar RX de tornozelo (AP, perfil, mortise) e/ou pé conforme ponto positivo',
                'Imobilização provisória até laudo radiológico',
                'Se fratura confirmada: avaliar cirurgia vs. imobilização com ortopedia',
                'Analgesia: paracetamol 1g 6/6h ± ibuprofeno 400mg 8/8h (se sem contraindicação)',
            ],
            'encaminhar': 'Ortopedia se fratura confirmada',
        }
    else:
        return {
            'categoria': 'entorse_tornozelo',
            'forca': 'alta',
            'achados_positivos': _listar_entorse_positivos(dados),
            'conduta_nao_farmacologica': [
                'RICE nas primeiras 48h: repouso relativo, gelo 15-20min/vez, compressão, elevação',
                'Mobilização precoce funcional (não imobilizar rigidamente)',
                'Órtese funcional semi-rígida por 4-6 semanas (superior ao gesso)',
                'Fisioterapia: propriocepção e reforço peroniero (iniciar em 3-5 dias)',
                'Retorno gradual às atividades conforme tolerância',
            ],
            'farmacologico': [
                'Paracetamol 500-1000mg 6/6h por 5-7 dias (1a escolha)',
                'AINE (ibuprofeno 400mg 8/8h) por 5-7 dias se necessário para controle de edema/dor',
            ],
            'alerta_instabilidade': (
                'Entorses repetidos: risco de instabilidade crônica — fisioterapia de reforço obrigatória'
                if dados.get('ja_entorces_previos') else ''
            ),
            'imagem': 'RX apenas se Ottawa positivo (critérios não preenchidos aqui)',
        }


def _listar_ottawa_positivos(dados):
    achados = []
    if dados.get('palpacao_maleolo_lateral_positiva') or dados.get('dor_maleolo_posterior_lateral'):
        achados.append('Dor nos 6 cm posteriores do maléolo lateral')
    if dados.get('palpacao_maleolo_medial_positiva') or dados.get('dor_maleolo_posterior_medial'):
        achados.append('Dor nos 6 cm posteriores do maléolo medial')
    if dados.get('palpacao_base_5o_meta_positiva') or dados.get('dor_base_5o_meta'):
        achados.append('Dor na base do 5o metatarso')
    if dados.get('palpacao_navicular_positiva') or dados.get('dor_navicular'):
        achados.append('Dor no osso navicular')
    if dados.get('incapaz_apoio_exame') or dados.get('incapaz_apoio_4_passos'):
        achados.append('Incapaz de apoiar e dar 4 passos')
    return achados


def _listar_entorse_positivos(dados):
    achados = ['Ottawa negativo — fratura improvável (S ~99%)']
    if dados.get('mecanismo_inversao'):
        achados.append('Mecanismo de inversão (lesão típica do ATFL)')
    if dados.get('dor_ligamentos_laterais'):
        achados.append('Dor à palpação do ATFL/CFL')
    if dados.get('edema_tornozelo'):
        achados.append('Edema peri-maleolar presente')
    if dados.get('equimose_visivel'):
        achados.append('Equimose presente')
    return achados


# =============================================================================
# FASCIITE PLANTAR
# =============================================================================

def _avaliar_fasciite(dados):
    score = 0
    positivos = []

    if dados.get('dor_tuberosidade_medial_calc'):
        score += 4
        positivos.append('Dor à palpação da tuberosidade medial do calcâneo (achado patognomônico)')
    if dados.get('dor_primeiro_passo_manha'):
        score += 3
        positivos.append('Dor nos primeiros passos pela manha (startup pain)')
    if dados.get('dor_dorsiflexao_passiva'):
        score += 2
        positivos.append('Windlass test positivo (dorsiflexao passiva piora a dor)')
    if dados.get('dor_fascia_proximal'):
        score += 2
        positivos.append('Dor ao percurso da fascia proximal')
    if dados.get('dor_melhora_caminhar'):
        score += 1
        positivos.append('Dor melhora após aquecimento (padrão fasciítico)')
    if dados.get('uso_calcado_inadequado'):
        score += 1
        positivos.append('Calçado sem suporte')
    if dados.get('sobrepeso_obesidade'):
        score += 1
        positivos.append('Sobrepeso / obesidade (fator de risco mecânico)')
    if dados.get('pe_plano_valgismo'):
        score += 1
        positivos.append('Pé plano ou valgismo (biomecânica de risco)')

    if score >= 7:
        forca = 'alta'
    elif score >= 4:
        forca = 'moderada'
    else:
        forca = 'baixa'

    return {
        'hipotese': 'Fasciite Plantar',
        'score': score,
        'forca': forca,
        'positivos': positivos,
        'conduta_nao_farmacologica': [
            'Exercícios de alongamento da fascia plantar: 3 séries de 10 repetições, 3x/dia',
            'Rodar uma garrafa gelada sob o pé (10-15 min): analgesia + alongamento',
            'Órtese prefabricada (palmilha com suporte de arco) — NAO personalizada inicialmente',
            'Trocar calçados inadequados (chinelo, sapatilha rasa, salto alto)',
            'Fisioterapia: alongamento, fortalecimento intrínseco, onda de choque (refratário)',
        ],
        'farmacologico': [
            'AINE oral: ibuprofeno 400mg 8/8h por 2-4 semanas (fase aguda)',
            'Infiltração de corticosteroide: considerar se refratário (max 1-2x; risco de ruptura da fascia)',
        ],
        'prognostico': (
            'Prognóstico: ~75% resolvem espontaneamente em 12 meses. '
            'Média de resolução: 725 dias — informar o paciente sobre curso prolongado!'
        ),
        'encaminhar': 'Ortopedia / Fisiatria se sem melhora em 3-6 meses',
    }


# =============================================================================
# TENDINOPATIA DE AQUILES
# =============================================================================

def _avaliar_aquiles(dados):
    score = 0
    positivos = []

    if dados.get('dor_zona_critica_aquiles'):
        score += 4
        positivos.append('Dor na zona crítica (2-6 cm da insercao) — padrão de tendinopatia de corpo')
    if dados.get('espessamento_nodulo_aquiles'):
        score += 3
        positivos.append('Espessamento focal ou nódulo no tendão (tendinose)')
    if dados.get('dor_2_6cm_insercao') or dados.get('rigidez_manha_aquiles'):
        score += 2
        positivos.append('Rigidez matinal no tendão de Aquiles')
    if dados.get('piora_corrida_salto') or dados.get('piora_corrida_salto'):
        score += 2
        positivos.append('Piora com carga (corrida, salto, escadas)')
    if dados.get('dor_insercao_aquiles') or dados.get('dor_insercao_calcahar'):
        score += 2
        positivos.append('Dor insercional (distinguir: fisioterapia específica diferente)')
    if dados.get('uso_quinolona'):
        score += 1
        positivos.append('Uso de fluoroquinolona (fator de risco para ruptura)')

    if score >= 7:
        forca = 'alta'
    elif score >= 4:
        forca = 'moderada'
    else:
        forca = 'baixa'

    insercional = dados.get('dor_insercao_aquiles') and not dados.get('dor_zona_critica_aquiles')

    conduta_ft = (
        'Tendinopatia INSERCIONAL: evitar Alfredson clássico com calcanhar abaixo do nível. '
        'Usar exercício isométrico ou isotônico sem declínio.'
        if insercional else
        'Protocolo de Alfredson (eccentric loading): 3x15 repetições, 2x/dia, 12 semanas. '
        'Exercício: descer o calcanhar abaixo do degrau (excêntrico). '
        'Aumento gradual de carga. Dor leve durante o exercício é aceitável.'
    )

    return {
        'hipotese': 'Tendinopatia de Aquiles',
        'score': score,
        'forca': forca,
        'positivos': positivos,
        'alerta_csi': (
            'CONTRAINDICADO: infiltracao de corticosteroide intra-tendinoso. '
            'Risco de ruptura espontânea do tendão de Aquiles.'
        ),
        'conduta_nao_farmacologica': [
            conduta_ft,
            'Modificação de atividade: reduzir impacto transitoriamente (não imobilizar)',
            'Calçado com salto discretamente elevado (heel lift 5-10 mm) para aliviar tensão',
        ],
        'farmacologico': [
            'AINE oral curto prazo: ibuprofeno 400mg 8/8h por 5-7 dias (fase aguda)',
            'Sem corticosteroide local (contraindicado no tendão)',
        ],
        'fisioterapia': 'Reabilitação excêntrica por 12 semanas — padrão ouro (NNT ~2)',
        'encaminhar': 'Ortopedia se ruptura (Thompson +) ou refratário > 6 meses',
        'imagem': 'USG tendão ou RM se dúvida diagnóstica ou suspeita de ruptura parcial',
    }


# =============================================================================
# NEUROMA DE MORTON
# =============================================================================

def _avaliar_morton(dados):
    score = 0
    positivos = []

    if dados.get('mulder_positivo'):
        score += 5
        positivos.append('Sinal de Mulder positivo (S 62-86%, E ~95%)')
    if dados.get('queimacao_entre_dedos') or dados.get('dor_espaco_3_4_interdigital'):
        score += 3
        positivos.append('Queimacao/formigamento no espaco 3-4o intermetatarsal')
    if dados.get('piora_calcado_estreito'):
        score += 2
        positivos.append('Piora com calçado estreito ou salto alto')
    if dados.get('alivio_tirar_calcado'):
        score += 2
        positivos.append('Alivio ao tirar o sapato e massagear o pé')
    if dados.get('irradiacao_para_dedos') or dados.get('hipoestesia_dedos_adjacentes'):
        score += 1
        positivos.append('Irradiação ou hipoestesia nos dedos adjacentes')

    if score >= 8:
        forca = 'alta'
    elif score >= 4:
        forca = 'moderada'
    else:
        forca = 'baixa'

    return {
        'hipotese': 'Neuroma de Morton',
        'score': score,
        'forca': forca,
        'positivos': positivos,
        'conduta_nao_farmacologica': [
            'Modificação de calçado: bico largo, sem salto alto (medida primária)',
            'Palmilha metatarsal (metatarsal pad): posicionar proximal à cabeça do 3o-4o metatarso',
            'Evitar calçados de bico fino por tempo indeterminado',
        ],
        'farmacologico': [
            'Infiltração de corticosteroide (CSI): 1a linha aceitável (Depo-Medrol 40mg + anestésico)',
            'Repetir em 4-6 semanas se resposta parcial (máximo 3 infiltrações)',
            'AINE oral: ibuprofeno 400mg 8/8h por 2 semanas para controle de dor',
        ],
        'encaminhar': 'Ortopedia / cirurgia do pé se refratário a 2-3 infiltrações',
        'imagem': 'USG ou RM antepé para confirmação se dúvida ou cirurgia planejada',
    }


# =============================================================================
# INTEGRACAO — INTERPRETA
# =============================================================================

def interpretar_tornozelo_pe(dados):
    """Ponto de entrada principal. Retorna dict com categoria e resultado."""

    red_flags = _avaliar_red_flags(dados)
    alerta_aquiles = _alerta_corticosteroide_aquiles(dados)

    if red_flags.get('flags'):
        return {
            'categoria': 'red_flag_tornozelo_pe',
            'red_flags': red_flags,
            'alerta_aquiles': alerta_aquiles,
        }

    # ── Trauma ─────────────────────────────────────────────────────────────
    if dados.get('trauma_recente'):
        resultado = _avaliar_trauma(dados)
        resultado['red_flags']      = red_flags
        resultado['alerta_aquiles'] = alerta_aquiles
        # Trava de segurança — AINE vetado em ≥ 60 anos
        # (_avaliar_trauma retorna dict plano com 'conduta' ou 'farmacologico')
        aplicar_trava_idoso_aine([resultado], dados)
        return resultado

    # ── Não-trauma: por localização ────────────────────────────────────────
    loc = dados.get('localizacao_dor', '')

    if loc == 'calcanhar_plantar':
        h         = _avaliar_fasciite(dados)
        provaveis = [h] if h['forca'] in ('alta', 'moderada') else []
        possiveis = [h] if h['forca'] == 'baixa' else []
        # Trava de segurança — AINE vetado em ≥ 60 anos
        aplicar_trava_idoso_aine(provaveis, dados)
        aplicar_trava_idoso_aine(possiveis, dados)
        return {
            'categoria': 'fasciite_plantar',
            'hipoteses_provaveis': provaveis,
            'hipoteses_possiveis': possiveis,
            'red_flags': red_flags,
            'alerta_aquiles': alerta_aquiles,
        }

    if loc == 'posterior_aquiles':
        h         = _avaliar_aquiles(dados)
        provaveis = [h] if h['forca'] in ('alta', 'moderada') else []
        possiveis = [h] if h['forca'] == 'baixa' else []
        # Trava de segurança — AINE vetado em ≥ 60 anos
        aplicar_trava_idoso_aine(provaveis, dados)
        aplicar_trava_idoso_aine(possiveis, dados)
        return {
            'categoria': 'tendinopatia_aquiles',
            'hipoteses_provaveis': provaveis,
            'hipoteses_possiveis': possiveis,
            'red_flags': red_flags,
            'alerta_aquiles': alerta_aquiles,
        }

    if loc == 'antepé_morton':
        h         = _avaliar_morton(dados)
        provaveis = [h] if h['forca'] in ('alta', 'moderada') else []
        possiveis = [h] if h['forca'] == 'baixa' else []
        # Trava de segurança — AINE vetado em ≥ 60 anos
        aplicar_trava_idoso_aine(provaveis, dados)
        aplicar_trava_idoso_aine(possiveis, dados)
        return {
            'categoria': 'morton_neuroma',
            'hipoteses_provaveis': provaveis,
            'hipoteses_possiveis': possiveis,
            'red_flags': red_flags,
            'alerta_aquiles': alerta_aquiles,
        }

    # Fallback — localização tornozelo articular ou não definida
    return {
        'categoria': 'avaliacao_tornozelo_pe',
        'red_flags': red_flags,
        'alerta_aquiles': alerta_aquiles,
        'hipoteses_provaveis': [],
        'hipoteses_possiveis': [],
        'mensagem': 'Localização inespecífica — realizar exame físico completo e considerar OA de tornozelo, artrite ou instabilidade crônica.',
    }
