# red_flags_msk.py
# Camada compartilhada — Red Flags universais para qualquer queixa MSK
# Base: Open Evidence 2026 / OARSI / ACR / NICE
# Usado por: joelho, ombro, quadril, tornozelo, mao_punho, coluna, dor_difusa

def avaliar_red_flags_msk(dados):
    flags = []

    # --- INFECÇÃO ARTICULAR ---
    if dados.get('febre'):
        flags.append({
            'categoria': 'infeccao',
            'achado': 'febre',
            'acao': 'Artrocentese imediata + hemocultura. Não infiltrar antes de excluir artrite séptica.',
            'urgencia': 'emergencia'
        })
    if dados.get('imunossupressao') or dados.get('uso_drogas_iv') or dados.get('bacteremia_recente'):
        flags.append({
            'categoria': 'infeccao',
            'achado': 'fator_de_risco_para_artrite_septica',
            'acao': 'Alto risco de artrite séptica. Artrocentese e avaliação urgente.',
            'urgencia': 'emergencia'
        })

    # --- MALIGNIDADE ---
    if dados.get('historico_cancer'):
        flags.append({
            'categoria': 'malignidade',
            'achado': 'historico_de_cancer',
            'acao': 'Solicitar imagem. Encaminhar para avaliação oncológica se suspeita.',
            'urgencia': 'urgente'
        })
    if dados.get('perda_de_peso_inexplicada'):
        flags.append({
            'categoria': 'malignidade',
            'achado': 'perda_de_peso_inexplicada',
            'acao': 'Investigar causa sistêmica. Hemograma, VHS, PCR, imagem.',
            'urgencia': 'urgente'
        })
    if dados.get('dor_noturna_sem_alivio'):
        flags.append({
            'categoria': 'malignidade_ou_infeccao',
            'achado': 'dor_noturna_persistente_em_repouso',
            'acao': 'Não atribuir a causa mecânica. Investigar com imagem e labs.',
            'urgencia': 'urgente'
        })

    # --- FRATURA ---
    if dados.get('trauma_significativo'):
        flags.append({
            'categoria': 'fratura',
            'achado': 'trauma_significativo',
            'acao': 'Aplicar Regras de Ottawa. Solicitar radiografia.',
            'urgencia': 'urgente'
        })
    if dados.get('idade_acima_70') and dados.get('dor_nova'):
        flags.append({
            'categoria': 'fratura',
            'achado': 'idade_acima_de_70_com_dor_nova',
            'acao': 'Alta probabilidade de fratura por fragilidade. Radiografia obrigatória.',
            'urgencia': 'urgente'
        })
    if dados.get('uso_cronico_corticoide') or dados.get('osteoporose'):
        flags.append({
            'categoria': 'fratura',
            'achado': 'risco_aumentado_de_fratura_ossea',
            'acao': 'Considerar fratura mesmo com trauma mínimo. Radiografia.',
            'urgencia': 'urgente'
        })

    # --- SÍNDROME DA CAUDA EQUINA (emergência absoluta) ---
    ces_sinais = [
        dados.get('anestesia_em_sela'),
        dados.get('retencao_urinaria'),
        dados.get('incontinencia_fecal'),
        dados.get('fraqueza_bilateral_mmii')
    ]
    if any(ces_sinais):
        flags.append({
            'categoria': 'cauda_equina',
            'achado': 'sindrome_da_cauda_equina',
            'acao': 'EMERGÊNCIA. RM imediata + neurocirurgia. Não aguardar.',
            'urgencia': 'emergencia_absoluta'
        })

    # --- HEMARTROSE (trauma vascular ou coagulopatia) ---
    if dados.get('hemartrose_imediata'):
        flags.append({
            'categoria': 'trauma_vascular_ou_coagulopatia',
            'achado': 'hemartrose_imediata_apos_trauma',
            'acao': 'Suspeitar de ruptura de LCA ou fratura osteocondral. Imagem urgente.',
            'urgencia': 'urgente'
        })

    # --- DÉFICIT NEUROLÓGICO PROGRESSIVO ---
    if dados.get('deficit_neurologico_progressivo'):
        flags.append({
            'categoria': 'compressao_neurologica',
            'achado': 'deficit_neurologico_progressivo',
            'acao': 'RM urgente. Avaliação neurocirúrgica se progressão rápida.',
            'urgencia': 'urgente'
        })

    # --- ARTRITE INFLAMATÓRIA SISTÊMICA ---
    if dados.get('rigidez_matinal_acima_60min') and dados.get('articulacoes_multiplas'):
        flags.append({
            'categoria': 'artrite_inflamatoria',
            'achado': 'padrao_inflamatorio_sistemico',
            'acao': 'Solicitar FR, anti-CCP, VHS, PCR, hemograma. Encaminhar reumatologia.',
            'urgencia': 'eletivo_prioritario'
        })

    tem_emergencia = any(f['urgencia'] in ['emergencia', 'emergencia_absoluta'] for f in flags)
    tem_urgente = any(f['urgencia'] == 'urgente' for f in flags)

    return {
        'flags': flags,
        'tem_red_flag': len(flags) > 0,
        'tem_emergencia': tem_emergencia,
        'tem_urgente': tem_urgente,
        'prosseguir_avaliacao_rotina': len(flags) == 0
    }


# =============================================================================
# TRAVA DE SEGURANÇA — AINE sistêmico em idosos (≥ 60 anos)
# =============================================================================

_AINE_KW = [
    'AINE', 'Ibuprofeno', 'Naproxeno', 'Etoricoxibe',
    'Diclofenaco VO', 'Diclofenaco oral', 'Meloxicam',
    'Celecoxibe', 'Piroxicam',
]

def aplicar_trava_idoso_aine(hipoteses_list, dados):
    """
    Veta AINE sistêmico em pacientes ≥ 60 anos.

    Escaneia as chaves 'conduta' E 'farmacologico' de cada hipótese (engines
    diferentes usam chaves diferentes) e remove itens que contenham palavras-
    chave de AINEs orais. Insere no topo da chave modificada um alerta
    explícito + analgesia segura (Paracetamol / Dipirona).

    Aceita tanto listas de hipóteses aninhadas (joelho, coluna, ombro, quadril)
    quanto listas com um único dict-resultado (tornozelo_pe, mao_punho).

    Opera in-place e retorna a lista para uso fluente.
    Referência: Beers Criteria 2023 / STOPP v3 / AGS.
    """
    if not dados.get('idade_acima_60'):
        return hipoteses_list

    _kw_lower = [kw.lower() for kw in _AINE_KW]   # comparação case-insensitive

    _VETO = (
        '⚠️  AINE SISTÊMICO VETADO — idade ≥ 60 anos: risco agudo de '
        'lesão renal (DRC agudizada) e sangramento digestivo alto (HDA). '
        'Evitar mesmo por período curto sem protetor gástrico e sem avaliação de função renal.'
    )
    _ANALG = (
        'Analgesia segura: Paracetamol 500–1000 mg VO 6/6h (máx 3 g/dia) '
        'OU Dipirona 500–1000 mg VO 6/6h (máx 4 g/dia).'
    )

    for h in hipoteses_list:
        chave_alerta = None   # primeira chave onde AINEs foram encontrados

        for chave in ('conduta', 'farmacologico'):
            itens = h.get(chave)
            if not itens:
                continue
            nova       = []
            achou_aqui = False
            for item in itens:
                il = item.lower()
                if any(kw in il for kw in _kw_lower):
                    achou_aqui = True   # silencia — não adiciona
                else:
                    nova.append(item)
            if achou_aqui:
                h[chave] = nova
                if chave_alerta is None:
                    chave_alerta = chave   # registra onde inserir o alerta

        if chave_alerta:
            h[chave_alerta].insert(0, _VETO)
            h[chave_alerta].insert(1, _ANALG)

    return hipoteses_list


if __name__ == '__main__':
    caso_septico = {
        'febre': True,
        'imunossupressao': True,
        'dor_noturna_sem_alivio': False,
        'historico_cancer': False,
        'perda_de_peso_inexplicada': False,
        'trauma_significativo': False,
        'idade_acima_70': False,
        'dor_nova': False,
        'uso_cronico_corticoide': False,
        'osteoporose': False,
        'anestesia_em_sela': False,
        'retencao_urinaria': False,
        'incontinencia_fecal': False,
        'fraqueza_bilateral_mmii': False,
        'hemartrose_imediata': False,
        'deficit_neurologico_progressivo': False,
        'rigidez_matinal_acima_60min': False,
        'articulacoes_multiplas': False,
        'bacteremia_recente': False,
        'uso_drogas_iv': False
    }

    resultado = avaliar_red_flags_msk(caso_septico)
    print('=== CASO SÉPTICO ===')
    for f in resultado['flags']:
        print(f"[{f['urgencia'].upper()}] {f['achado']}: {f['acao']}")
    print(f"Emergência: {resultado['tem_emergencia']}")
    print(f"Prosseguir rotina: {resultado['prosseguir_avaliacao_rotina']}")
