# modules/raciocinio/orl/engine_rinossinusite.py
# Motor de raciocínio clínico — Obstrução Nasal / Rinossinusite
#
# Hierarquia STEP:
#   STEP 1  Red flag orbital (celulite orbitária/subperiosteal) → PS urgente
#   STEP 1  Red flag meníngeo (meningite/abscesso intracraniano) → PS imediato
#   STEP 2  RSA Bacteriana (≥10d sem melhora OU double-sickening) → ATB 5–7d
#   STEP 2  IVAS viral (< 7d, sem critérios RSAB) → sintomático
#   STEP 2  Rinite alérgica → anti-histamínico + corticoide nasal
#   STEP 3  RSC (≥ 12 semanas) → ORL + TC seios
#   STEP 3  Quadro intermediário (7–28d sem critério RSAB) → reavaliação 2–3d
#
# Fontes:
#   - AAO-HNS Clinical Practice Guideline — ABRS 2025
#     (critérios: ≥10d sem melhora OU double-sickening; duração 5–7d)
#   - JAMA 2026: amox e amox-clav eficácia equivalente em RSAB não grave
#   - EPOS 2020 / Bousquet 2021: rinite alérgica e RSC
#   - Open Evidence / American Family Physician 2025 (fluxo RSAB)


# =============================================================================
# HELPERS
# =============================================================================

def _rx(linha, medicamento, prescricoes, nota=None):
    return {'linha': linha, 'medicamento': medicamento,
            'prescricoes': prescricoes, 'nota': nota}


def _p(quantidade, unidade, posologia):
    return {'quantidade': quantidade, 'unidade': unidade, 'posologia': posologia}


def _achados(dados) -> list:
    a = []
    d = dados.get('duracao_sintomas', '')
    if d:
        a.append(f'duração: {d}')
    if dados.get('obstrucao_nasal'):
        a.append('obstrução nasal')
    if dados.get('rinorreia'):
        tipo = dados.get('rinorreia_tipo', '')
        a.append(f'rinorreia ({tipo.lower()})' if tipo else 'rinorreia')
    if dados.get('gotejamento_pos_nasal'):
        a.append('gotejamento pós-nasal')
    if dados.get('dor_facial'):
        loc = dados.get('dor_facial_loc', '')
        a.append(f'dor facial ({loc.lower()})' if loc else 'dor facial')
    if dados.get('febre'):
        a.append(f'febre ({dados.get("temperatura_grau", "")})')
    if dados.get('double_sickening'):
        a.append('DOUBLE SICKENING')
    if dados.get('espirros_salva'):
        a.append('espirros em salva')
    if dados.get('prurido_nasal_ocular'):
        a.append('prurido nasal/ocular')
    if dados.get('hiposmia_anosmia'):
        a.append('hiposmia/anosmia')
    if dados.get('edema_periorbital'):
        a.append('EDEMA PERIORBITAL')
    if dados.get('diplopia'):
        a.append('DIPLOPIA')
    if dados.get('rigidez_nucal'):
        a.append('RIGIDEZ NUCAL')
    return a


# =============================================================================
# STEP 1 — RED FLAG ORBITAL (PS URGENTE)
# =============================================================================

def _resultado_red_flag_orbital(dados) -> dict:
    sinais = []
    if dados.get('edema_periorbital'): sinais.append('edema/eritema periorbital')
    if dados.get('diplopia'):          sinais.append('diplopia')
    if dados.get('proptose'):          sinais.append('proptose')

    raciocinio = (
        f'Rinossinusite com: {", ".join(sinais)} '
        '→ extensão orbitária até prova em contrário. '
        'Progressão clássica: RSA etmoidal → celulite pré-septal → celulite orbitária → '
        'abscesso subperiosteal → abscesso orbitário → trombose seio cavernoso. '
        'TC seios paranasais + órbitas com contraste é obrigatória. '
        'ATB IV (ceftriaxona ± metronidazol) + oftalmologia e ORL urgentes. '
        'Abscesso subperiosteal: drenagem cirúrgica. '
        'NÃO manejar ambulatorialmente — risco de cegueira e extensão intracraniana.'
    )
    return {
        'tipo': 'orl', 'subtipo': 'rinossinusite',
        'categoria': 'orl_rinossinusite_complicacao_orbital',
        'diagnostico': 'Complicação Orbitária de RSA — PS Imediato',
        'urgencia': 'emergencia', 'raciocinio': raciocinio,
        'achados': _achados(dados),
        'red_flags': ['Extensão orbitária de RSA — celulite/abscesso orbitário'],
        'exames': [],
        'conduta': [
            'PS IMEDIATO — TC seios + órbitas com contraste',
            'ATB IV: Ceftriaxona 2g IV 12/12h ± Metronidazol 500mg IV 8/8h',
            'Avaliação conjunta: ORL + Oftalmologia',
            'NÃO prescrever ATB oral e dispensar — progressão pode ser rápida',
        ],
        'prescricoes_estruturadas': [],
        'orientacoes': {},
        'encaminhar': 'PS — ORL + Oftalmologia urgentes',
        'retorno': '',
    }


# =============================================================================
# STEP 1 — RED FLAG MENÍNGEO (PS IMEDIATO)
# =============================================================================

def _resultado_red_flag_meningeo(dados) -> dict:
    sinais = []
    if dados.get('rigidez_nucal'):         sinais.append('rigidez nucal')
    if dados.get('cefaleia_intensa'):       sinais.append('cefaleia de forte intensidade')
    if dados.get('alteracao_consciencia'): sinais.append('alteração do nível de consciência')

    raciocinio = (
        f'Rinossinusite com: {", ".join(sinais)} '
        '→ complicação intracraniana até prova em contrário. '
        'Diferencial: meningite bacteriana, empiema subdural, abscesso intracraniano, '
        'trombose do seio cavernoso. '
        'TC crânio com contraste + punção lombar (se sem sinais de HIC). '
        'ATB empírico IV imediato (ceftriaxona + vancomicina + dexametasona). '
        'Não aguardar exames para iniciar ATB se meningite clinicamente provável.'
    )
    return {
        'tipo': 'orl', 'subtipo': 'rinossinusite',
        'categoria': 'orl_rinossinusite_complicacao_meningea',
        'diagnostico': 'Complicação Intracraniana de RSA — Emergência',
        'urgencia': 'emergencia', 'raciocinio': raciocinio,
        'achados': _achados(dados),
        'red_flags': ['Complicação intracraniana suspeita — meningite/abscesso cerebral'],
        'exames': [],
        'conduta': [
            'SAMU / PS — emergência neurológica',
            'ATB IV imediato: Ceftriaxona 2g IV 12/12h + Vancomicina + Dexametasona 0,15 mg/kg',
            'TC crânio com contraste; punção lombar após excluir HIC',
            'Neurocirurgia + ORL + Neurologia',
        ],
        'prescricoes_estruturadas': [],
        'orientacoes': {},
        'encaminhar': 'SAMU / PS — emergência',
        'retorno': '',
    }


# =============================================================================
# STEP 2A — RSA BACTERIANA (RSAB) — ATB 5–7 DIAS
# =============================================================================

def _resultado_rsab(dados) -> dict:
    double_sick = dados.get('double_sickening', False)
    grave       = dados.get('sindrome_grave_rsab', False)
    risco       = dados.get('risco_rsab_grave', False)
    alergia     = dados.get('alergia_betalactamico', False)
    alergia_t1  = dados.get('alergia_tipo_1', False)
    dias        = dados.get('duracao_dias_aprox', 14)

    # Critério que disparou RSAB
    if grave:
        criterio_texto = 'síndrome grave de início (febre ≥39°C + secreção purulenta unilateral + dor facial)'
    elif double_sick:
        criterio_texto = 'piora bifásica (double sickening — melhora inicial seguida de agravamento)'
    else:
        criterio_texto = f'sintomas por {dias} dias sem melhora (critério ≥ 10 dias — AAO-HNS 2025)'

    # Risco alto → Amox-Clav de entrada
    motivos_risco = []
    if dados.get('atb_recente_30d'):   motivos_risco.append('ATB no último mês')
    if dados.get('imunossuprimido'):   motivos_risco.append('imunossuprimido')
    if dados.get('idade', 25) > 65:    motivos_risco.append('idade > 65 anos')
    if dados.get('idade', 25) < 2:     motivos_risco.append('idade < 2 anos')
    if grave:                          motivos_risco.append('síndrome grave')

    usar_amoxclav = risco or grave
    usar_corticoide_nasal = True  # sempre adjuvante em RSAB

    raciocinio = (
        f'RSA bacteriana: {criterio_texto}. '
        + (f'Fatores de risco para resistência/falha: {", ".join(motivos_risco)}. ' if motivos_risco else '') +
        ('Amoxicilina-Clavulanato 1ª linha (cobertura de beta-lactamase). '
         if usar_amoxclav else
         'Amoxicilina e amox-clavulanato têm eficácia equivalente em RSAB não grave (JAMA 2026). '
         'Amoxicilina 875mg preferida: menor custo, menor impacto na microbiota. ') +
        'Duração: 5–7 dias (AAO-HNS 2025 — encurtou de 10–14d para 5–7d). '
        'Corticoide nasal: adjuvante — reduz edema de mucosa, NÃO é substituto de ATB.'
    )

    prescricoes = []

    if alergia:
        if alergia_t1:
            # Anafilaxia — evitar qualquer beta-lactâmico
            # Guard: Doxiciclina contraindicada < 8 anos (quelação óssea/dental)
            if dados.get('idade', 25) < 8:
                prescricoes.append(
                    _rx('1ª linha (alergia GRAVE, < 8 anos — doxiciclina proibida)',
                        'Clindamicina 8–10mg/kg/dose',
                        [_p('frasco conforme peso', 'suspensão VO',
                            '3×/dia (8/8h) × 7 dias — calcular pelo peso')],
                        'Doxiciclina CONTRAINDICADA em < 8 anos (quelação de Ca ósseo/dental). '
                        'Clindamicina: cobertura de S. pneumoniae incluindo cepas resistentes à penicilina. '
                        'Suspensão 75mg/5mL. Ex.: 20kg → 160–200mg/dose → 10–13mL 3×/dia.')
                )
            else:
                prescricoes.append(
                    _rx('1ª linha (alergia GRAVE/anafilática a penicilina)',
                        'Doxiciclina 100mg',
                        [_p('14', 'comprimidos', '1 comp VO 12/12h × 7 dias')],
                        'Tomar com copo cheio de água — evitar deitar por 30min (risco esofagite). '
                        'Evitar sol intenso (fotossensibilidade). '
                        'Atividade contra S. pneumoniae e H. influenzae — cobertura aceitável para RSAB.')
                )
        else:
            # Alergia não anafilática — pode usar cefalosporina
            prescricoes.append(
                _rx('1ª linha (alergia não anafilática a penicilina)',
                    'Cefuroxima 500mg',
                    [_p('14', 'comprimidos', '1 comp VO 12/12h × 7 dias')],
                    'Reação cruzada penicilina-cefalosporina < 2% em alergia não anafilática. '
                    'Se preferência por dose única diária: Cefixima 400mg 1×/dia × 7 dias.')
            )
    elif usar_amoxclav:
        prescricoes.append(
            _rx('1ª linha — alto risco (ATB recente / imuno / grave)',
                'Amoxicilina-Clavulanato 875/125mg',
                [_p('14', 'comprimidos', '1 comp VO 12/12h × 5–7 dias')],
                'Tomar junto às refeições (reduz náusea). '
                'Cobertura: S. pneumoniae, H. influenzae e M. catarrhalis beta-lactamase (+).')
        )
    else:
        prescricoes.append(
            _rx('1ª linha (sem fatores de risco)',
                'Amoxicilina 875mg',
                [_p('14', 'comprimidos', '1 comp VO 12/12h × 5–7 dias')],
                'Cobre S. pneumoniae e a maioria dos H. influenzae. '
                'Eficácia equivalente ao amox-clav em RSAB não grave (JAMA 2026). '
                'Trocar para Amox-Clav se sem melhora em 48–72h.')
        )

    # Corticoide nasal — sempre adjuvante
    prescricoes.append(
        _rx('Adjuvante — corticoide nasal intranasal',
            'Mometasona furoato 50mcg/dose spray nasal',
            [_p('1', 'frasco', '2 puffs em cada narina, 1×/dia (manhã) × 14–21 dias')],
            'Reduz edema de mucosa e melhora sintomas nasais. '
            'NÃO substitui o ATB. Aplicar inclinando cabeça levemente para frente. '
            'Alternativa: Budesonida 32mcg/dose, mesma posologia.')
    )

    # Lavagem nasal salina — sempre
    prescricoes.append(
        _rx('Higiene nasal — lavagem salina',
            'Soro fisiológico 0,9% spray nasal (ou solução isotônica nasal)',
            [_p('1', 'frasco', '2–3 sprays em cada narina, 3–4×/dia')],
            'Hidrata mucosa, remove secreção e crostas. '
            'Preferir irrigação alta (seringa/neti pot) se tolerado — maior eficácia na higiene. '
            'Usar antes do corticoide nasal.')
    )

    # Descongestionante nasal — máx 5 dias
    if dados.get('obstrucao_nasal') and not dados.get('duracao_cronica'):
        prescricoes.append(
            _rx('Descongestionante nasal tópico (máx 5 dias!)',
                'Oximetazolina 0,05% spray nasal',
                [_p('1', 'frasco', '1–2 sprays em cada narina, 2×/dia × máx 5 dias')],
                '⚠️  NÃO usar por mais de 5 dias — efeito rebote (rinite medicamentosa). '
                'Alivia obstrução aguda; sem efeito no processo inflamatório.')
        )

    orientacoes = {
        'hidratacao': (
            'Beber pelo menos 2–2,5L de líquidos por dia: água, chás, caldos. '
            'Hidratação adequada fluidifica as secreções e facilita drenagem dos seios.'
        ),
        'vapor_e_calor': (
            'Inalação de vapor (ducha quente, bacia com água quente) por 10–15 min, 2–3×/dia. '
            'Compressas mornas sobre a face (fronte/maçãs do rosto) aliviam a pressão. '
            'Dormir com cabeceira elevada 30–45° (fronha extra) melhora drenagem noturna.'
        ),
        'lavagem_nasal': (
            'Lavar o nariz com soro fisiológico ANTES de aplicar o spray de corticoide. '
            'Para lavagem alta: seringa de 20mL ou neti pot com SF morno — '
            'solução entra por uma narina e sai pela outra.'
        ),
        'atb': (
            'Tomar o antibiótico até o FIM do curso mesmo com melhora precoce. '
            'Se aparecer diarreia intensa ou rash cutâneo — parar e retornar.'
        ),
        'sinais_de_alerta': [
            'Inchaço ao redor do olho (vermelhidão, dor ao mover o olho) → PS imediato',
            'Visão dupla ou olho "saltado" para fora → PS imediato',
            'Rigidez do pescoço, confusão mental, cefaleia muito intensa → SAMU',
            'Febre muito alta (> 39,5°C) que não cede com antitérmico',
            'Piora progressiva após 48–72h de antibiótico',
        ],
    }

    return {
        'tipo': 'orl', 'subtipo': 'rinossinusite',
        'categoria': 'orl_rsab',
        'diagnostico': 'Rinossinusite Aguda Bacteriana — ATB 5–7 dias',
        'urgencia': None, 'raciocinio': raciocinio,
        'achados': _achados(dados), 'red_flags': [],
        'exames': [],
        'conduta': [
            f'ATB {"amox-clav" if usar_amoxclav else "amoxicilina"} × 5–7 dias (AAO-HNS 2025)',
            'Corticoide nasal adjuvante × 14–21 dias',
            'Lavagem salina 3–4×/dia',
            'Reavaliação em 48–72h se sem melhora ou piora',
        ],
        'prescricoes_estruturadas': prescricoes,
        'orientacoes': orientacoes,
        'encaminhar': 'ORL se: falha de 2 cursos de ATB, suspeita de complicação ou RSC (> 12 semanas)',
        'retorno': 'Retorno em 48–72h se sem melhora. Retornar ao protocolo viral se piora em < 7d.',
    }


# =============================================================================
# STEP 2B — IVAS VIRAL (< 7 dias, sem critérios RSAB)
# =============================================================================

def _resultado_ivas_viral(dados) -> dict:
    dias = dados.get('duracao_dias_aprox', 3)
    raciocinio = (
        f'Sintomas nasais há {dias} dias (< 7 dias), sem double sickening, sem síndrome grave. '
        'Quadro compatível com IVAS viral (rinovírus, coronavírus, adenovírus). '
        'Sinusite radiológica existe em > 87% das IVAS virais — IMAGEM NÃO DISTINGUE viral de bacteriana. '
        'ATB não reduz duração, não previne complicações bacterianas e aumenta resistência. '
        'Tratamento: sintomático. '
        'Reavaliação em 7–10 dias: se sintomas persistirem ≥ 10 dias sem melhora → RSAB.'
    )
    prescricoes = [
        _rx('Higiene nasal (essencial)',
            'Soro fisiológico 0,9% spray nasal',
            [_p('1', 'frasco', '2–3 sprays em cada narina, 4–6×/dia ou após cada assoada')],
            'Principal medida sintomática. Hidrata mucosa, remove vírus e secreção.'),
        _rx('Descongestionante tópico (máx 3–5 dias!)',
            'Oximetazolina 0,05% spray nasal',
            [_p('1', 'frasco', '1–2 sprays em cada narina, 2×/dia × máx 5 dias')],
            '⚠️  Usar somente se obstrução muito intensa interferindo no sono. '
            'NÃO usar por mais de 5 dias — efeito rebote. '
            'Em < 6 anos: usar formulação 0,025% sob orientação pediátrica.'),
        _rx('Analgesia/antitérmico PRN',
            'Paracetamol 750mg',
            [_p('20', 'comprimidos', '1 comp VO 6/6h PRN (máx 3g/dia) × 5 dias')],
            'Para dor facial, cefaleia e febre. '
            'Ibuprofeno 600mg 8/8h é alternativa se sem contraindicação gástrica.'),
    ]

    orientacoes = {
        'atb_nao': (
            'NÃO precisa de antibiótico agora — gripe/resfriado é causado por vírus, '
            'e antibiótico não age contra vírus. '
            'Você receberá uma data de retorno: se os sintomas NÃO melhorarem até lá, '
            'voltaremos a avaliar se há infecção bacteriana sobreposta.'
        ),
        'hidratacao_e_repouso': (
            'Beber bastante líquido (água, sucos, chás) e descansar. '
            'O corpo combate o vírus por conta própria — repouso acelera a recuperação.'
        ),
        'higiene_respiratoria': (
            'Cobrir a boca ao tossir/espirrar. Lavar as mãos frequentemente. '
            'Evitar tocar olhos, nariz e boca. '
            'Evitar aglomerações se possível durante a fase aguda.'
        ),
        'sinais_de_alerta': [
            'Melhora seguida de piora (double sickening) → pode ser infecção bacteriana',
            'Sintomas sem melhora após 10 dias',
            'Febre alta persistente (> 39°C por > 3 dias)',
            'Dor facial intensa e localizada',
            'Inchaço ao redor do olho → PS imediato',
        ],
    }

    return {
        'tipo': 'orl', 'subtipo': 'rinossinusite',
        'categoria': 'orl_ivas_viral',
        'diagnostico': 'IVAS Viral — Sintomático (sem indicação de ATB)',
        'urgencia': None, 'raciocinio': raciocinio,
        'achados': _achados(dados), 'red_flags': [],
        'exames': [],
        'conduta': [
            'Sem antibiótico — viral < 7d sem critérios RSAB',
            'Lavagem nasal salina 4–6×/dia',
            'Descongestionante tópico se obstrução grave (máx 5 dias)',
            'Reavaliação em 7–10 dias se não melhorar',
        ],
        'prescricoes_estruturadas': prescricoes,
        'orientacoes': orientacoes,
        'encaminhar': None,
        'retorno': 'Retornar em 7–10 dias SE sem melhora — reavaliar critério de RSAB (≥ 10 dias).',
    }


# =============================================================================
# STEP 2C — RINITE ALÉRGICA
# =============================================================================

def _resultado_rinite_alergica(dados) -> dict:
    tem_atb_indicado = dados.get('rsab_criterio', False)  # RSA bacteriana coexistente?
    usa_corticoide   = dados.get('corticoide_nasal_uso', False)
    sazonal          = dados.get('piora_sazonal', False)
    alergenos        = dados.get('alergenos_conhecidos', False)

    raciocinio = (
        'Espirros em salva + rinorreia clara + sem febre + '
        + ('alergia conhecida' if alergenos else 'piora sazonal/exposicional')
        + ' → rinite alérgica. '
        'Mediada por IgE: alérgenos (pólen, ácaro, epitélio animal, mofo) → '
        'histamina e leucotrienos → edema, hipersecreção, prurido. '
        'Corticoide nasal intranasal é o tratamento mais eficaz — superior a anti-histamínico isolado. '
        + ('Já em uso de corticoide nasal — avaliar técnica de aplicação e adesão. '
           if usa_corticoide else '') +
        'Anti-histamínico oral controla prurido e espirros, pouco efeito na obstrução. '
        'Terapia combinada (corticoide + anti-histamínico) para sintomas moderados-graves.'
    )

    prescricoes = [
        _rx('Corticoide nasal intranasal (1ª linha — rinite)',
            'Mometasona furoato 50mcg/dose spray nasal',
            [_p('1', 'frasco', '2 puffs em cada narina, 1×/dia (manhã) — uso contínuo')],
            'Efeito máximo em 1–2 semanas de uso regular. '
            'Não parar ao melhorar — usar continuamente durante exposição. '
            'Alternativa: Budesonida 32mcg/dose, Fluticasona 50mcg/dose, mesma posologia.'),
        _rx('Anti-histamínico de 2ª geração (não sedativo)',
            'Loratadina 10mg',
            [_p('30', 'comprimidos', '1 comp VO 1×/dia (manhã) — uso contínuo ou PRN')],
            'Alternativas: Cetirizina 10mg 1×/dia, Bilastina 20mg 1×/dia, Fexofenadina 180mg 1×/dia. '
            'Tomar de manhã. Bilastina e fexofenadina têm menos efeito sedativo residual.'),
    ]

    if dados.get('prurido_nasal_ocular') and not dados.get('corticoide_nasal_uso'):
        prescricoes.append(
            _rx('Se prurido ocular predominante',
                'Cetotifeno 0,025% colírio (ou Olopatadina 0,1%)',
                [_p('1', 'frasco', '1 gota em cada olho, 2×/dia PRN')],
                'Anti-histamínico tópico ocular — para conjuntivite alérgica associada.')
        )

    # Lavagem salina sempre
    prescricoes.append(
        _rx('Higiene nasal',
            'Soro fisiológico 0,9% spray nasal (ou solução salina hipertônica 2,3%)',
            [_p('1', 'frasco', '2–3 sprays em cada narina, 3–4×/dia')],
            'Usar ANTES do corticoide nasal. '
            'Solução hipertônica pode reduzir mais o edema — tolerar ardência inicial.')
    )

    orientacoes = {
        'controle_de_alergenos': (
            'Controle de ácaros: capa antiácaro em travesseiros e colchão, '
            'lavagem de roupas de cama semanalmente com água > 60°C, '
            'tapetes e cortinas grossas fora do quarto. '
            + ('Filtro HEPA no quarto pode ajudar em alergia ao pólen. '
               if sazonal else '') +
            'Evitar contato direto com pet se alergia a epitélio animal.'
        ),
        'tecnica_spray': (
            'Aplicar o spray nasal inclinando a cabeça levemente para frente (não para trás). '
            'Apontar o bico em direção à lateral do nariz (não ao septo). '
            'Inspirar suavemente pelo nariz ao aplicar. '
            'Não assoar o nariz por 15 minutos após a aplicação.'
        ),
        'sinais_de_alerta': [
            'Febre + piora da secreção (purulenta) → pode ser RSA bacteriana',
            'Sangramento nasal frequente com corticoide (verificar técnica)',
            'Falta de ar ou chiado no peito → asma alérgica associada — investigar',
            'Sem melhora após 4 semanas de tratamento regular',
        ],
    }

    exames = [
        'Teste cutâneo (prick test) ou IgE específica (RAST) — alergologista — se dúvida diagnóstica ou candidato a imunoterapia',
    ]

    return {
        'tipo': 'orl', 'subtipo': 'rinossinusite',
        'categoria': 'orl_rinite_alergica',
        'diagnostico': 'Rinite Alérgica — Anti-histamínico + Corticoide Nasal',
        'urgencia': None, 'raciocinio': raciocinio,
        'achados': _achados(dados), 'red_flags': [],
        'exames': exames,
        'conduta': [
            'Corticoide nasal intranasal diário (mometasona/budesonida)',
            'Anti-histamínico de 2ª geração (loratadina/cetirizina)',
            'Controle de exposição a alérgenos',
        ],
        'prescricoes_estruturadas': prescricoes,
        'orientacoes': orientacoes,
        'encaminhar': 'Alergologista (eletivo) — prick test + imunoterapia se refratária ou grave',
        'retorno': 'Retorno em 4 semanas para reavaliação de resposta. Controle periódico se crônica.',
    }


# =============================================================================
# STEP 3A — RSC (≥ 12 SEMANAS) — ENCAMINHAMENTO ORL
# =============================================================================

def _resultado_rsc(dados) -> dict:
    polipos = dados.get('polipos_conhecidos', False)
    hiposmia = dados.get('hiposmia_anosmia', False)

    raciocinio = (
        f'Sintomas rinossinusais por {dados.get("duracao_sintomas", "≥ 12 semanas")} '
        '→ rinossinusite crônica (RSC, definição EPOS 2020: ≥ 12 semanas sem resolução). '
        + ('Polipose nasal conhecida: RSC tipo 2 (eosinofílica) — '
           'responde mal a ATB, necessita corticoide nasal de alta dose ou cirurgia. '
           if polipos else '') +
        ('Hiposmia/anosmia associada sugere envolvimento etmoidal/infundibular — '
         'pior prognóstico sem drenagem cirúrgica. '
         if hiposmia else '') +
        'TC seios paranasais (sem contraste) é o padrão para planejamento cirúrgico. '
        'ORL para avaliação: corticoide nasal de longa duração vs FESS (cirurgia endoscópica). '
        'ATB longa não é indicado rotineiramente em RSC sem exacerbação aguda.'
    )

    prescricoes = [
        _rx('Corticoide nasal intranasal (bridge até ORL)',
            'Mometasona furoato 50mcg/dose spray nasal',
            [_p('1–2', 'frascos', '2 puffs em cada narina, 2×/dia — uso contínuo')],
            'Dose máxima (400mcg/dia) indicada em RSC com pólipos. '
            'Efeito sistêmico mínimo com uso correto. '
            'Manter até reavaliação ORL.'),
        _rx('Higiene nasal — lavagem alta volume',
            'Solução salina isotônica (250–500mL)',
            [_p('1', 'kit irrigação nasal', 'Irrigação de alto volume (neti pot / squeeze bottle) — 1–2×/dia')],
            'Higiene de alto volume é mais eficaz que spray na RSC. '
            'Preparar com água filtrada/fervida morna + 1/4 colher de sal + pitada de bicarbonato. '
            'Kits prontos (NeilMed, Sinomarin) são alternativas práticas.'),
    ]

    orientacoes = {
        'sinais_que_precisam_ps': (
            'Procurar PS se: inchaço ao redor dos olhos, visão dupla, cefaleia muito intensa, '
            'rigidez do pescoço ou confusão mental — complicações, mesmo na RSC, são emergências.'
        ),
        'sinais_de_alerta': [
            'Inchaço/vermelhidão periorbital → PS imediato',
            'Cefaleia de forte intensidade com rigidez nucal',
            'Epistaxe frequente ou intensa',
            'Assimetria dos seios na imagem (suspeita neoplásica)',
        ],
    }

    exames = [
        'TC seios paranasais (sem contraste) — padrão para RSC; solicitar antes do ORL',
        'Endoscopia nasal (ORL)' if not polipos else 'Endoscopia nasal — confirma pólipos (ORL)',
    ]

    return {
        'tipo': 'orl', 'subtipo': 'rinossinusite',
        'categoria': 'orl_rsc' + ('_polipose' if polipos else ''),
        'diagnostico': 'Rinossinusite Crônica' + (' com Polipose' if polipos else '') + ' — Encaminhamento ORL',
        'urgencia': None, 'raciocinio': raciocinio,
        'achados': _achados(dados), 'red_flags': [],
        'exames': exames,
        'conduta': [
            'Solicitar TC seios paranasais (sem contraste)',
            'Encaminhar ORL (eletivo) com imagem',
            'Corticoide nasal de dose plena enquanto aguarda consulta',
            'Lavagem nasal de alto volume 1–2×/dia',
        ],
        'prescricoes_estruturadas': prescricoes,
        'orientacoes': orientacoes,
        'encaminhar': 'ORL — eletivo com TC seios em mãos',
        'retorno': 'Retorno em 4 semanas ou antes se piora aguda (febre + rinorreia purulenta).',
    }


# =============================================================================
# STEP 3B — QUADRO INTERMEDIÁRIO (7–28d sem critério RSAB)
# =============================================================================

def _resultado_intermediario(dados) -> dict:
    dias = dados.get('duracao_dias_aprox', 10)
    raciocinio = (
        f'Sintomas nasais há ~{dias} dias. '
        'Sem critério definitivo para RSAB (< 10 dias de duração sem double-sickening) '
        'e sem característica de rinite alérgica. '
        'Maioria dos quadros de 7–9 dias ainda resolve espontaneamente. '
        'Observação ativa por mais 2–3 dias antes de iniciar ATB é racional. '
        'Reavaliação presencial ou por teleconsulta em 48–72h para decidir sobre RSAB.'
    )

    prescricoes = [
        _rx('Higiene nasal',
            'Soro fisiológico 0,9% spray nasal',
            [_p('1', 'frasco', '2–3 sprays em cada narina, 4×/dia')],
            None),
        _rx('Descongestionante tópico se obstrução intensa (máx 5 dias)',
            'Oximetazolina 0,05% spray nasal',
            [_p('1', 'frasco', '1–2 sprays em cada narina, 2×/dia × máx 5 dias')],
            '⚠️  Não ultrapassar 5 dias — rinite medicamentosa.'),
        _rx('Analgesia PRN',
            'Paracetamol 750mg',
            [_p('10', 'comprimidos', '1 comp VO 6/6h PRN (máx 3g/dia)')],
            'Para dor facial e cefaleia.'),
    ]

    orientacoes = {
        'observacao_ativa': (
            'Seus sintomas ainda podem melhorar sem antibiótico. '
            'Vamos esperar mais 2–3 dias. '
            'Se não houver melhora ou piorar, retorne — poderá ser necessário antibiótico.'
        ),
        'sinais_de_alerta': [
            'Piora depois de melhora inicial (double sickening) → retornar imediatamente',
            'Febre alta (> 39°C) com dor facial intensa',
            'Inchaço ao redor do olho → PS imediato',
        ],
    }

    return {
        'tipo': 'orl', 'subtipo': 'rinossinusite',
        'categoria': 'orl_rinossinusite_intermediario',
        'diagnostico': 'Rinossinusite — Observação Ativa (sem ATB agora)',
        'urgencia': None, 'raciocinio': raciocinio,
        'achados': _achados(dados), 'red_flags': [],
        'exames': [],
        'conduta': [
            'Observação ativa 48–72h sem ATB',
            'Lavagem nasal salina + descongestionante tópico PRN',
            'Reavaliação em 48–72h — iniciar RSAB se persistir ou piorar',
        ],
        'prescricoes_estruturadas': prescricoes,
        'orientacoes': orientacoes,
        'encaminhar': None,
        'retorno': 'Retorno OBRIGATÓRIO em 48–72h para decidir sobre ATB.',
    }


# =============================================================================
# PONTO DE ENTRADA PRINCIPAL
# =============================================================================

def interpretar_rinossinusite(dados: dict) -> dict:
    """
    Motor de raciocínio clínico — Obstrução Nasal / Rinossinusite.

    STEP 1: Red flag orbital → PS imediato (celulite orbitária)
    STEP 1: Red flag meníngeo → PS emergência
    STEP 2: RSAB (≥10d OU double-sickening OU grave) → ATB 5–7d
    STEP 2: IVAS viral (< 7d sem critérios) → sintomático
    STEP 2: Rinite alérgica → anti-histamínico + corticoide nasal
    STEP 3: RSC (≥ 12 semanas) → ORL + TC seios
    STEP 3: Intermediário (7–28d sem critério) → observação ativa 48–72h
    """

    # ── STEP 1 — Red flags ──────────────────────────────────────────────────
    if dados.get('red_flag_orbital'):
        return _resultado_red_flag_orbital(dados)

    if dados.get('red_flag_meningeo'):
        return _resultado_red_flag_meningeo(dados)

    # ── STEP 3 — RSC (crônica ≥ 12 semanas) — antes do RSAB para evitar
    #            prescrição de ATB curto em paciente crônico
    if dados.get('duracao_cronica'):
        return _resultado_rsc(dados)

    # ── STEP 2A — RSAB: gate EXPLÍCITO (AAO-HNS 2025) ──────────────────────
    # Defesa em profundidade: não confiar só em rsab_criterio pré-computado.
    # Rinite alérgica e IVAS viral (< 10d) NÃO podem escorregar para RSAB a
    # menos que um dos três critérios abaixo esteja explicitamente presente.
    _rsab_duracao   = dados.get('duracao_dias_aprox', 0) >= 10          # ≥ 10 dias sem melhora
    _rsab_sickening = bool(dados.get('double_sickening'))               # piora bifásica
    _rsab_grave     = bool(dados.get('sindrome_grave_rsab'))             # febre ≥39°C + pus + dor facial 3-4d
    _rsab_gate      = _rsab_duracao or _rsab_sickening or _rsab_grave

    if _rsab_gate:
        return _resultado_rsab(dados)

    # ── STEP 2B — IVAS viral (<7d sem gate RSAB) ────────────────────────────
    if dados.get('duracao_dias_aprox', 5) < 7 and not _rsab_gate:
        # Verificar rinite alérgica antes de concluir como viral puro
        if dados.get('rinite_alergica_suspeita'):
            return _resultado_rinite_alergica(dados)
        return _resultado_ivas_viral(dados)

    # ── STEP 2C — Rinite alérgica (após excluir RSAB explicitamente) ────────
    if dados.get('rinite_alergica_suspeita'):
        return _resultado_rinite_alergica(dados)

    # ── STEP 3B — Quadro intermediário (7–9d sem critério RSAB) ─────────────
    return _resultado_intermediario(dados)
