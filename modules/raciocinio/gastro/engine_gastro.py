# modules/raciocinio/gastro/engine_gastro.py
# Motor de raciocínio clínico — Dor Abdominal e Queixas GI
#
# Cobertura: red flags cirúrgicas, dispepsia/PUD, H. pylori (V Consenso Br 2025),
#            cólica biliar, SII (C/D/M), constipação funcional, diverticulite,
#            isquemia mesentérica, DIP (CDC STI 2021), gravidez ectópica,
#            celíaca, IBD, parasitoses (helmintos + protozoários + amebíase),
#            náuseas/vômitos, dor inespecífica.
#
# Fontes:
#   - V Consenso Brasileiro H. pylori (SBAD 2025) — quádrupla bismuto 1ª linha
#   - CDC STI Treatment Guidelines 2021 — DIP
#   - JAMA 2024 — Diverticulite ambulatorial
#   - Open Evidence 2025 — SII, constipação, parasitoses, antiespasmódicos
#   - Maastricht VI 2022 — H. pylori resistência à claritromicina


# =============================================================================
# HELPERS — PRESCRIÇÕES ESTRUTURADAS
# =============================================================================

def _rx(linha, medicamento, prescricoes, nota=None):
    """Cria entrada padronizada de prescrição (padrão SymptoPy)."""
    return {'linha': linha, 'medicamento': medicamento,
            'prescricoes': prescricoes, 'nota': nota}


def _p(quantidade, unidade, posologia):
    return {'quantidade': quantidade, 'unidade': unidade, 'posologia': posologia}


# =============================================================================
# HELPERS — ACHADOS CLÍNICOS
# =============================================================================

def _achados_principais(dados):
    """Extrai lista de achados clínicos positivos para o #Análise."""
    achados = []
    loc_label = {
        'epigastrico': 'dor epigástrica', 'fsd': 'dor em FSD', 'fid': 'dor em FID',
        'fie': 'dor em FIE', 'hipogastrico_pelvico': 'dor pélvica',
        'periumbilical': 'dor periumbilical', 'difuso': 'dor difusa',
    }
    if dados.get('localizacao') in loc_label:
        achados.append(loc_label[dados['localizacao']])

    car_label = {'colica': 'caráter cólico', 'queimacao': 'queimação / azia',
                 'constante': 'dor constante', 'distensao': 'distensão',
                 'aguda_subita': 'início súbito'}
    if dados.get('carater') in car_label:
        achados.append(car_label[dados['carater']])

    if dados.get('febre'):    achados.append(f'febre ({dados["febre_grau"]})')
    if dados.get('nausea'):   achados.append('náuseas')
    if dados.get('vomito'):   achados.append('vômitos')
    if dados.get('hematemese'): achados.append('hematêmese')
    if dados.get('melena'):   achados.append('melena')
    if dados.get('hematoquezia'): achados.append('hematoquezia')
    if dados.get('muco_fezes'): achados.append('muco nas fezes')
    if dados.get('esteatorreia'): achados.append('esteatorreia')
    if dados.get('peritonismo'): achados.append('peritonismo')
    if dados.get('murphy_positivo'): achados.append('Murphy positivo')
    if dados.get('mcburney_positivo'): achados.append('McBurney positivo')
    if dados.get('fie_dolorosa'): achados.append('FIE dolorosa')
    if dados.get('perda_peso'): achados.append('perda de peso involuntária')
    if dados.get('ictericia'): achados.append('icterícia')
    if dados.get('piora_gorduroso'): achados.append('piora com gordurosos')
    if dados.get('piora_gluten'): achados.append('piora com glúten')
    if dados.get('alivio_evacuacao'): achados.append('alívio após evacuar')
    if dados.get('corrimento_purulento'): achados.append('corrimento purulento')
    if dados.get('atraso_menstrual'): achados.append('atraso menstrual')
    return achados


# =============================================================================
# RED FLAGS — EMERGÊNCIA IMEDIATA
# =============================================================================

def _check_emergencia(dados):
    """Retorna True se qualquer flag de emergência estiver presente."""
    if dados.get('peritonismo'):                              return True
    if dados.get('obstipacao_total') and dados.get('rha_ausentes'): return True
    if dados.get('hematemese') or dados.get('melena'):        return True
    if dados.get('hematoquezia') and dados.get('intensidade') in ('intensa', 'catastrofica'): return True
    if dados.get('dor_catastrofica') and dados.get('inicio_subito'): return True
    if dados.get('fid_dolorosa') and dados.get('febre'):      return True
    if dados.get('murphy_positivo') and dados.get('febre'):   return True
    if dados.get('fie_dolorosa') and dados.get('febre') and dados.get('peritonismo'): return True
    if (dados.get('risco_isquemia_mesenterica') and
            dados.get('intensidade') in ('intensa', 'catastrofica') and
            dados.get('abdome_flacido')):                     return True
    if dados.get('suspeita_ectopica'):                        return True
    return False


def _resultado_emergencia(dados):
    """Determina a emergência específica e monta o resultado."""
    if dados.get('suspeita_ectopica'):
        cat       = 'gastro_emergencia_ectopica'
        diag      = 'Gravidez Ectópica Suspeita — EMERGÊNCIA CIRÚRGICA'
        raciocinio = (
            'Mulher em idade fértil com atraso menstrual + dor pélvica aguda de alta intensidade '
            '→ gravidez ectópica até prova em contrário. '
            'β-hCG negativo NÃO exclui ectópica precoce (nível abaixo do limiar do teste). '
            'Conduta: US transvaginal + dosagem sérica de β-hCG em PS imediato.'
        )

    elif (dados.get('risco_isquemia_mesenterica') and
          dados.get('intensidade') in ('intensa', 'catastrofica') and
          dados.get('abdome_flacido')):
        cat       = 'gastro_emergencia_isquemia_mesenterica'
        diag      = 'Isquemia Mesentérica Suspeita — EMERGÊNCIA VASCULAR'
        raciocinio = (
            'Idoso com FA/vasculopatia + dor abdominal desproporcional ao exame físico '
            '(intensidade intensa/catastrófica + abdôme flácido sem peritonismo) → '
            'isquemia mesentérica aguda. '
            '"Silêncio clínico" do abdôme é sinal de alerta, não de tranquilidade. '
            'TC com angioTC mesentérica é padrão-ouro. Cirurgia vascular imediata.'
        )

    elif dados.get('hematemese') or dados.get('melena'):
        cat       = 'gastro_emergencia_sangramento_gi'
        diag      = 'Sangramento Digestivo Alto — PS imediato'
        raciocinio = (
            'Hematêmese ou melena → sangramento digestivo alto ativo (acima do ângulo de Treitz). '
            'Causas prováveis: PUD, varizes esofágicas, Mallory-Weiss. '
            'Endoscopia de urgência após estabilização hemodinâmica.'
        )

    elif dados.get('hematoquezia') and dados.get('intensidade') in ('intensa', 'catastrofica'):
        cat       = 'gastro_emergencia_sangramento_gi'
        diag      = 'Sangramento GI Baixo Ativo — PS imediato'
        raciocinio = (
            'Hematoquezia volumosa e intensa → sangramento GI baixo ativo. '
            'Causas: divertículo, angiodisplasia, colite isquêmica, neoplasia. '
            'Estabilizar + colonoscopia de urgência.'
        )

    elif dados.get('fid_dolorosa') and dados.get('febre') and not dados.get('fie_dolorosa'):
        mc = 'positivo' if dados.get('mcburney_positivo') else 'a confirmar'
        cat       = 'gastro_emergencia_apendicite'
        diag      = 'Apendicite Aguda Suspeita — PS imediato'
        raciocinio = (
            f'Dor em FID + febre + McBurney {mc} → suspeita de apendicite aguda. '
            'TC abdôme e pelve com contraste: sensibilidade 98-99%. '
            'Não atrasar com exames ambulatoriais — risco de perfuração.'
        )

    elif dados.get('murphy_positivo') and dados.get('febre'):
        cat       = 'gastro_emergencia_colecistite'
        diag      = 'Colecistite Aguda — PS imediato'
        raciocinio = (
            'Murphy positivo + febre → colecistite aguda (inflamação da vesícula). '
            'Diferença da cólica biliar: Murphy negativo + afebril + dor < 6h. '
            'US abdominal + cirurgia em PS.'
        )

    elif dados.get('fie_dolorosa') and dados.get('febre') and dados.get('peritonismo'):
        cat       = 'gastro_emergencia_diverticulite_complicada'
        diag      = 'Diverticulite Complicada — PS imediato'
        raciocinio = (
            'FIE + febre + peritonismo (Blumberg/rigidez) → diverticulite complicada '
            '(abscesso, perfuração ou fístula). '
            'TC abdôme e pelve confirma. Internação + cirurgia.'
        )

    elif dados.get('obstipacao_total'):
        cat       = 'gastro_emergencia_obstrucao'
        diag      = 'Obstrução Intestinal — PS imediato'
        raciocinio = (
            'Ausência de evacuação e flatos há > 24h '
            + ('+ ruídos hidroaéreos ausentes ' if dados.get('rha_ausentes') else '') +
            '→ obstrução intestinal mecânica. '
            'Causas frequentes: brida (cirurgia prévia), hérnia encarcerada, neoplasia. '
            'Raio-X/TC urgente.'
        )

    else:
        cat       = 'gastro_emergencia_peritonite'
        diag      = 'Peritonite / Abdôme Agudo — PS imediato'
        raciocinio = (
            'Sinais peritoneais (defesa/rigidez/Blumberg+) ou dor catastrófica de início súbito '
            '→ abdôme agudo de provável causa cirúrgica. '
            'PS imediato. Nada via oral. Não atrasar com analgesia diagnóstica.'
        )

    return {
        'tipo': 'gastro', 'categoria': cat, 'diagnostico': diag,
        'urgencia': 'emergencia', 'raciocinio': raciocinio,
        'achados': _achados_principais(dados), 'red_flags': [diag],
        'exames': [], 'conduta': [
            'NADA VIA ORAL',
            'Encaminhar PA/PS imediatamente',
            'Não atrasar com exames ambulatoriais',
        ],
        'prescricoes_estruturadas': [], 'orientacoes': {},
        'encaminhar': 'PA/PS imediato', 'retorno': '',
        'alerta_cdiff': False,
    }


# =============================================================================
# DIP — Doença Inflamatória Pélvica (CDC STI 2021)
# =============================================================================

def _resultado_dip(dados):
    raciocinio = (
        'Mulher sexualmente ativa com febre + corrimento purulento + dor pélvica nova/intensa '
        '→ DIP (Doença Inflamatória Pélvica) por critério clínico (CDC 2021). '
        'Baixo limiar para tratamento — sequelas graves se não tratada (infertilidade, dor crônica). '
        'Cobertura empírica: N. gonorrhoeae + C. trachomatis + anaeróbios. '
        'Retorno em 72h — sem melhora → internação.'
    )
    exames = [
        'Swab cervical para Neisseria gonorrhoeae e Chlamydia trachomatis (cultura + NAAT)',
        'β-hCG para excluir gravidez ectópica',
        'Hemograma + PCR',
        'US transvaginal (excluir abscesso tubo-ovariano)',
    ]
    prescricoes = [
        _rx('Cobertura gram-negativa', 'Ceftriaxona 500mg',
            [_p('1', 'ampola', 'IM dose única — aplicar na consulta')]),
        _rx('Cobertura clamídia + anaeróbios', 'Doxiciclina 100mg + Metronidazol 500mg',
            [
                _p('28', 'comp. doxiciclina',  '1 comp VO 12/12h × 14 dias'),
                _p('28', 'comp. metronidazol', '1 comp VO 12/12h × 14 dias'),
            ],
            'EVITAR álcool. Retorno em 72h — febre persistente ou piora da dor → internação.'),
    ]
    orientacoes = {
        'conduta_parceiro': 'Tratar parceiro(s) sexual(is) — gonorreia/clamídia são ISTs.',
        'abstinencia':      'Abstinência sexual até completar o tratamento E cura do parceiro.',
        'retorno_72h':      'Retornar em 72h para reavaliar. Sem melhora → internação.',
        'reteste':          'Reteste para clamídia/gonorreia em 3 meses após tratamento.',
        'sinais_de_alerta': [
            'Febre que não cede em 72h',
            'Piora da dor',
            'Náuseas/vômitos — não consegue tomar comprimidos',
            'Suspeita de gravidez',
        ],
    }
    internacao_criteria = [
        'Critérios de internação: gravidez, abscesso tubo-ovariano, febre > 38,5°C, '
        'incapacidade de tomar VO, ausência de melhora em 72h de tratamento ambulatorial.'
    ]
    return {
        'tipo': 'gastro', 'categoria': 'gastro_dip', 'diagnostico': 'DIP — Doença Inflamatória Pélvica',
        'urgencia': 'urgente', 'raciocinio': raciocinio,
        'achados': _achados_principais(dados), 'red_flags': [],
        'exames': exames, 'conduta': internacao_criteria,
        'prescricoes_estruturadas': prescricoes, 'orientacoes': orientacoes,
        'encaminhar': 'Ginecologia (eletivo para seguimento; urgente se sem melhora em 72h)',
        'retorno': 'Retorno obrigatório em 72h para avaliar resposta clínica.',
        'alerta_cdiff': False,
    }


# =============================================================================
# DIVERTICULITE AMBULATORIAL (JAMA 2024)
# =============================================================================

def _check_diverticulite(dados):
    return (dados.get('fie_dolorosa') and
            dados.get('febre') and
            not dados.get('peritonismo'))


def _resultado_diverticulite(dados):
    # ATB indicado apenas se critérios presentes (AGA 2021 / ACP 2022 / Cochrane 2022)
    criterios_atb = []
    if dados.get('febre_alta'):       criterios_atb.append('febre persistente > 38,5°C')
    if dados.get('idoso'):            criterios_atb.append('idade > 80 anos')
    if dados.get('imunossuprimido'):  criterios_atb.append('imunossupressão')
    if dados.get('diverticulose'):    criterios_atb.append('diverticulose conhecida com complicação prévia')
    # Critérios adicionais de evidência
    usa_atb = bool(criterios_atb)

    if usa_atb:
        raciocinio = (
            'Dor em FIE + febre + abdôme SEM peritonismo → diverticulite não complicada. '
            f'ATB indicado por: {", ".join(criterios_atb)}. '
            'TC recomendada para confirmar diagnóstico e excluir complicação.'
        )
    else:
        raciocinio = (
            'Dor em FIE + febre + abdôme SEM peritonismo → diverticulite não complicada. '
            'AGA 2021 / ACP 2022 / Cochrane 2022: ATB NÃO superior à observação em '
            'imunocompetentes sem sepse, sem febre >38,5°C, sem comorbidades graves, '
            'com acompanhamento ambulatorial garantido. '
            'Manejo sintomático é seguro — 95% dos casos resolvem sem ATB. '
            'TC recomendada se 1ª crise ou dúvida diagnóstica (S 98-99%).'
        )

    conduta = [
        'Solicitar TC abdôme e pelve com contraste IV (confirmar diagnóstico + excluir complicação)',
        'Dieta líquida clara 1-2 dias → avançar conforme tolerância',
        'Analgesia: Dipirona 500mg VO 6/6h PRN',
        'Retorno em 48-72h — piora → PS (internação + ATB IV)',
    ]
    if not usa_atb:
        conduta.append(
            'Sem ATB nesta apresentação — instruir retorno imediato se: '
            'febre > 38,5°C persistente, piora da dor, vômitos incoercíveis ou rigidez abdominal'
        )
    if usa_atb:
        conduta.append('ATB indicado pelos critérios acima — ver prescrição')

    prescricoes = []
    if usa_atb:
        prescricoes = [
            _rx('1ª linha (diverticulite com indicação de ATB)', 'Amoxicilina-Clavulanato 875/125mg',
                [_p('14', 'comprimidos', '1 comp VO 12/12h × 4–7 dias')],
                'Tomar com alimento. Duração 4–7 dias é suficiente (vs 10d anterior). Retorno 48-72h.'),
            _rx('Alternativa', 'Cefalexina 500mg + Metronidazol 500mg',
                [
                    _p('14', 'comp. cefalexina', '1 comp VO 12/12h × 7 dias'),
                    _p('21', 'comp. metro',       '1 comp VO 8/8h × 7 dias'),
                ],
                'Evitar ciprofloxacino como 1ª linha — resistência crescente e risco de tendinopatia.'),
        ]
    else:
        prescricoes = [
            _rx('Analgesia (sem ATB)', 'Dipirona 500mg',
                [_p('20', 'comprimidos', '1 comp VO 6/6h PRN')],
                'Sem ATB nesta apresentação. Retorno em 48h. Se febre >38,5°C persistir → iniciar ATB.'),
        ]
    orientacoes = {
        'alimentacao': (
            'Dias 1-2: líquidos claros apenas (água, caldo, chá, gelatina). '
            'Dia 3-4: dieta branda (arroz, frango cozido, sopa). '
            'Semana 2: retornar gradualmente à dieta normal. '
            'Após resolução: dieta rica em fibras PREVINE recorrência.'
        ),
        'sinais_de_alerta': [
            'Febre > 38,5°C ou febre que não cede',
            'Piora da dor abdominal',
            'Não consegue beber líquidos / vômitos',
            'Rigidez ou dor à descompressão (Blumberg)',
            'Sem melhora em 48-72h',
        ],
    }
    return {
        'tipo': 'gastro', 'categoria': 'gastro_diverticulite_ambulatorial',
        'diagnostico': 'Diverticulite Aguda Não Complicada — Manejo Ambulatorial',
        'urgencia': 'urgente', 'raciocinio': raciocinio,
        'achados': _achados_principais(dados), 'red_flags': [],
        'exames': ['TC abdôme e pelve com contraste IV', 'Hemograma + PCR + VHS'],
        'conduta': conduta,
        'prescricoes_estruturadas': prescricoes, 'orientacoes': orientacoes,
        'encaminhar': 'Cirurgia eletiva se ≥2 episódios ou episódio grave (sigmoidectomia)',
        'retorno': 'Retorno em 48-72h obrigatório. Colonoscopia eletiva 6-8 sem após resolução.',
        'alerta_cdiff': False,
    }


# =============================================================================
# IBD — Doença Inflamatória Intestinal (suspeita)
# =============================================================================

def _check_ibd(dados):
    # Exige diarreia (não constipação) — SII-C com artrite não é IBD
    return dados.get('suspeita_ibd', False)


def _resultado_ibd(dados):
    raciocinio = (
        'Diarreia crônica (> 3 meses) '
        + ('+ perda de peso involuntária ' if dados.get('perda_peso') else '') +
        ('+ sangue nas fezes ' if dados.get('sangue_fezes') else '') +
        ('+ manifestações extraintestinais (artrite/uveíte/eritema nodoso/aftas) ' if dados.get('manifestacoes_extraintestinais') else '') +
        '→ suspeita de DII (Crohn ou Retocolite). '
        'Calprotectina fecal > 50 µg/g distingue DII de SII funcional com S 93%, E 96%. '
        'Encaminhar com exames prontos para colonoscopia com ileoscopia e biópsias.'
    )
    carta = (
        'Encaminhar gastroenterologia com: '
        'calprotectina fecal + hemograma + PCR + VHS + albumina + Fe sérico. '
        'Suspeita de DII: colonoscopia com ileoscopia e biópsias (padrão-ouro).'
    )
    return {
        'tipo': 'gastro', 'categoria': 'gastro_ibd_suspeita',
        'diagnostico': 'Doença Inflamatória Intestinal Suspeita (Crohn / Retocolite)',
        'urgencia': 'urgente', 'raciocinio': raciocinio,
        'achados': _achados_principais(dados), 'red_flags': [],
        'exames': [
            'Calprotectina fecal (> 50 µg/g → IBD; < 50 → funcional/SII)',
            'Hemograma + PCR + VHS + albumina',
            'Ferro sérico + ferritina + B12 + folato',
            'Sorologias: ASCA, ANCA-p (se disponível)',
        ],
        'conduta': [
            carta,
            '⚠️  VETO AINE / AAS — pode desencadear flare grave de DII.',
            'Analgesia: paracetamol/dipirona exclusivamente.',
            'Não iniciar corticoide sem diagnóstico histológico confirmado.',
        ],
        'prescricoes_estruturadas': [], 'orientacoes': {
            'sinais_de_alerta': [
                'Febre > 38°C',
                'Sangue vivo nas fezes em grande quantidade',
                'Dor abdominal intensa e contínua',
                'Desidratação (tontura, urina escura)',
            ],
        },
        'encaminhar': 'Gastroenterologia — prioridade urgente',
        'retorno': 'Após resultado da calprotectina fecal + exames.',
        'alerta_cdiff': dados.get('alerta_cdiff', False),
    }


# =============================================================================
# CELÍACA — Doença Celíaca (suspeita)
# =============================================================================

def _check_celiaca(dados):
    return dados.get('suspeita_celiaca', False)


def _resultado_celiaca(dados):
    raciocinio = (
        'Piora com glúten'
        + (' + melhora sem glúten' if dados.get('melhora_sem_gluten') else '') +
        (' + esteatorreia' if dados.get('esteatorreia') else '') +
        (' + aftas recorrentes' if dados.get('aftas_extra') else '') +
        (' + artrite' if dados.get('artrite_extra') else '') +
        ' → doença celíaca suspeita. '
        'Anti-tTG IgA é o exame de triagem (S 95%, E 95%). '
        'ATENÇÃO: falso-negativo se deficiência de IgA (1:300 na população) — dosar IgA sérica total simultaneamente.'
    )
    return {
        'tipo': 'gastro', 'categoria': 'gastro_celiaca_suspeita',
        'diagnostico': 'Doença Celíaca — Suspeita (aguardar sorologia antes de excluir glúten)',
        'urgencia': 'eletivo', 'raciocinio': raciocinio,
        'achados': _achados_principais(dados), 'red_flags': [],
        'exames': [
            '⚠️  NÃO retirar o glúten antes de colher o exame — falso-negativo se dieta sem glúten',
            'Anti-tTG IgA (Antitransglutaminase tecidual IgA)',
            'IgA sérica total (para excluir deficiência de IgA e falso-negativo do anti-tTG)',
            'Hemograma (anemia ferropriva + macrocítica frequente)',
            'Ferro sérico + ferritina + B12 + folato',
        ],
        'conduta': [
            'Manter glúten na dieta até colher o exame',
            'Se anti-tTG positivo → endoscopia digestiva alta com biópsias do duodeno (confirmatório)',
            'Se anti-tTG negativo + IgA deficiente → anti-DGP IgG (antideaminado gliadina)',
            'Se anti-tTG negativo + IgA normal + sintomas persistem → investigar SII / intolerância ao glúten não celíaca',
        ],
        'prescricoes_estruturadas': [], 'orientacoes': {
            'importante': (
                'NÃO iniciar dieta sem glúten antes do resultado do exame. '
                'Se retirar o glúten por conta própria, o anti-tTG pode vir falso-negativo '
                'e o diagnóstico fica comprometido.'
            ),
            'sinais_de_alerta': [
                'Perda de peso progressiva',
                'Anemia persistente sem causa',
                'Diarreia que não melhora',
            ],
        },
        'encaminhar': 'Gastroenterologia (se anti-tTG positivo — endoscopia + biópsia)',
        'retorno': 'Retorno com resultado dos exames.',
        'alerta_cdiff': dados.get('alerta_cdiff', False),
    }


# =============================================================================
# PARASITOSES
# =============================================================================

def _check_parasitose(dados):
    return dados.get('suspeita_parasitose', False)


def _resultado_parasitose(dados):
    habi = dados.get('habito_intestinal', '')
    fezes = dados.get('fezes', '')
    tem_sangue = dados.get('sangue_fezes', False)
    tem_muco   = dados.get('muco_fezes', False)

    # Amebíase: diarreia com sangue/muco + contexto endêmico
    if tem_sangue or tem_muco:
        cat  = 'gastro_parasitose_ameba'
        diag = 'Amebíase Intestinal — Suspeita (E. histolytica)'
        raciocinio = (
            'Diarreia com sangue/muco + contexto epidemiológico (viagem endêmica / água não tratada) '
            '→ amebíase invasiva por E. histolytica até prova em contrário. '
            'Metronidazol 500mg é o amebicida tecidual disponível no Brasil. '
            'Paromomicina luminal: indisponível na rede — referenciar infectologia se falha.'
        )
        prescricoes = [
            _rx('Amebicida tecidual', 'Metronidazol 500mg',
                [_p('21', 'comprimidos', '1 comp VO 8/8h × 7 dias')],
                'EVITAR álcool durante e 48h após. Se não melhorar em 5 dias → encaminhar infectologia.'),
        ]
        exames = [
            'Coproparasitológico seriado × 3 amostras (intervalo 2-3 dias)',
            'Antígeno fecal para E. histolytica (ELISA) — mais sensível',
            'Hemograma + PCR',
        ]

    # Helmintoses: contexto + quadro clássico (cólica periumbilical, eliminação de vermes, prurido anal)
    elif (dados.get('carater') == 'colica' and
          dados.get('localizacao') in ('periumbilical', 'difuso')):
        cat  = 'gastro_parasitose_helminto'
        diag = 'Helmintose — Tratamento Empírico (Ascaris / Oxiúros)'
        raciocinio = (
            'Cólica periumbilical/difusa + contexto epidemiológico '
            '→ helmintose (Ascaris / Oxiúros / Ancilóstoma). '
            'Tratamento empírico com Albendazol é seguro e custo-efetivo. '
            'Oxiúros: tratar toda a família.'
        )
        prescricoes = [
            _rx('Anthelmíntico', 'Albendazol 400mg',
                [_p('1', 'comprimido', '1 comp VO dose única')],
                'Para oxiúros: repetir dose em 2-3 semanas. Tratar todos da família simultaneamente.'),
        ]
        exames = [
            'Coproparasitológico seriado × 3 amostras (se tratamento empírico falhar)',
            'Hemograma (eosinofilia > 500/µL sugere helmintos)',
        ]

    # Giardia / protozoários: diarreia explosiva + flatulência + distensão + contexto
    else:
        cat  = 'gastro_parasitose_protozoa'
        diag = 'Giardíase — Tratamento Empírico'
        raciocinio = (
            'Diarreia aquosa/explosiva + flatulência fétida + distensão abdominal + contexto epidemiológico '
            '→ Giardia lamblia provável. '
            'Nitazoxanida (Annita) 3 dias tem 85% de cura com melhor tolerância que Metronidazol. '
            'Metronidazol 5 dias é alternativa disponível no SUS.'
        )
        prescricoes = [
            _rx('1ª escolha (varejo)', 'Nitazoxanida (Annita) 500mg',
                [_p('6', 'comprimidos', '1 comp VO 12/12h × 3 dias')]),
            _rx('Alternativa (SUS)', 'Metronidazol 250mg',
                [_p('10', 'comprimidos', '1 comp VO 8/8h × 5 dias')],
                'EVITAR álcool durante e 48h após.'),
        ]
        exames = [
            'Coproparasitológico seriado × 3 amostras (indicado se diarreia > 7 dias)',
            'Antígeno fecal Giardia (ELISA) — mais sensível que coproparasitológico',
        ]

    orientacoes = {
        'higiene':          'Lavar as mãos com sabão após usar banheiro e antes de comer. Lavar frutas e verduras.',
        'agua':             'Beber apenas água filtrada ou fervida.',
        'familia':          'Oxiúros: tratar toda a família mesmo sem sintomas — carreamento assintomático é comum.',
        'sinais_de_alerta': ['Desidratação grave', 'Sangue nas fezes em grande quantidade', 'Febre alta'],
    }

    return {
        'tipo': 'gastro', 'categoria': cat, 'diagnostico': diag,
        'urgencia': None, 'raciocinio': raciocinio,
        'achados': _achados_principais(dados), 'red_flags': [],
        'exames': exames, 'conduta': ['Hidratação oral adequada', 'Higiene das mãos rigorosa'],
        'prescricoes_estruturadas': prescricoes, 'orientacoes': orientacoes,
        'encaminhar': None,
        'retorno': 'Retorno se sem melhora em 5-7 dias após tratamento.',
        'alerta_cdiff': dados.get('alerta_cdiff', False),
    }


# =============================================================================
# CÓLICA BILIAR
# =============================================================================

def _check_colica_biliar(dados):
    return (dados.get('localizacao') == 'fsd' and
            dados.get('piora_gorduroso') and
            not dados.get('murphy_positivo') and
            not dados.get('febre'))


def _resultado_colica_biliar(dados):
    raciocinio = (
        'Dor em FSD + piora com gordurosos + Murphy negativo + afebril '
        '→ cólica biliar (colecistolitíase sintomática). '
        'Diferença de colecistite: Murphy+ + febre + dor > 6h. '
        'US abdominal confirma cálculos. '
        'Encaminhar eletivo para colecistectomia após 2ª crise ou crise grave.'
    )
    prescricoes = [
        _rx('Alívio de cólica', 'Buscapan 10mg + Dipirona 500mg',
            [_p('20', 'comp. de cada',
                '1 comp. de cada VO 6/6h se cólica — PRN (máx 4 doses/dia)')],
            '⚠️  Suspender e buscar PS se febre > 38°C, dor persistir > 6h ou icterícia.'),
    ]
    orientacoes = {
        'alimentacao': (
            'Evitar: gordurosos, frituras, carnes gordas (picanha, costela), queijos amarelos, ovos fritos, creme de leite. '
            'Preferir: grelhados, cozidos, legumes, frutas. '
            'Refeições menores e mais frequentes. '
            'Perda de peso gradual se sobrepeso — perda RÁPIDA aumenta risco de novos cálculos.'
        ),
        'sinais_de_alerta': [
            'Febre (> 38°C) — pode ser colecistite aguda',
            'Dor que não melhora após 6h',
            'Pele ou olhos amarelados (icterícia)',
            'Fezes claras / urina escura (cálculo no ducto biliar)',
        ],
    }
    return {
        'tipo': 'gastro', 'categoria': 'gastro_colica_biliar',
        'diagnostico': 'Cólica Biliar — Colecistolitíase Sintomática',
        'urgencia': 'eletivo', 'raciocinio': raciocinio,
        'achados': _achados_principais(dados), 'red_flags': [],
        'exames': ['US abdominal total (confirmar cálculos + vias biliares)'],
        'conduta': ['Analgesia e antiespasmódico PRN durante crises'],
        'prescricoes_estruturadas': prescricoes, 'orientacoes': orientacoes,
        'encaminhar': 'Cirurgia — colecistectomia eletiva (≥ 2 episódios ou episódio grave)',
        'retorno': 'Retorno com resultado do US abdominal. PS se febre ou dor > 6h.',
        'alerta_cdiff': False,
    }


# =============================================================================
# DISPEPSIA / H. PYLORI (V Consenso Brasileiro 2025)
# =============================================================================

def _check_dispepsia(dados):
    # Se padrão SII (crônico + alívio ao evacuar + hábito alterado) → não é dispepsia
    if (dados.get('duracao_cronica') and
            dados.get('alivio_evacuacao') and
            dados.get('habito_intestinal') in ('diarreia', 'constipacao', 'alternancia')):
        return False
    return (dados.get('localizacao') in ('epigastrico', 'difuso') and
            dados.get('carater') in ('queimacao', 'constante', 'distensao', 'colica') and
            not dados.get('febre'))


def _resultado_dispepsia(dados):
    hp_pos = dados.get('hp_positivo') or dados.get('hp_sem_cura')
    hp_desco = dados.get('hp_desconhecido')
    hp_erad = dados.get('hp_eradicado')

    if hp_pos:
        cat  = 'gastro_dispepsia_hp_positivo'
        diag = 'Dispepsia / PUD — H. pylori positivo → Eradicação'
        raciocinio = (
            'Epigastralgia com H. pylori confirmado positivo'
            + (' (sem teste de cura após tratamento anterior)' if dados.get('hp_sem_cura') else '') +
            ' → eradicação indicada. '
            'V Consenso Brasileiro de H. pylori (SBAD 2025): quádrupla com bismuto é 1ª linha '
            '(alta resistência à claritromicina no Brasil). '
            'IBP 40mg 12/12h + bismuto + tetraciclina + metronidazol × 14 dias. '
            'Teste de cura obrigatório: breath test ou antígeno fecal 4 semanas após ATB '
            '(e ≥ 2 semanas após parar IBP).'
        )
        prescricoes = [
            _rx('1ª linha — Quádrupla com Bismuto × 14 dias (V Consenso Br 2025)',
                'Omeprazol 40mg',
                [_p('28', 'cápsulas', '1 cáps VO 12/12h, 30min antes do café e do jantar × 14 dias')]),
            _rx('', 'Subcitrato de Bismuto Coloidal 120mg',
                [_p('112', 'comprimidos',
                    '2 comp VO 4×/dia — antes do café, almoço, jantar e ao deitar × 14 dias')],
                'Fezes e língua podem escurecer — NORMAL, não é sangue.'),
            _rx('', 'Tetraciclina 500mg',
                [_p('56', 'cápsulas', '1 cáps VO 6/6h (4×/dia) × 14 dias')],
                'Fotossensibilidade — evitar sol direto. Pode tomar com alimento.'),
            _rx('', 'Metronidazol 500mg',
                [_p('42', 'comprimidos', '1 comp VO 8/8h × 14 dias')],
                'EVITAR álcool durante o tratamento e 48h após.'),
            _rx('Alternativa (bismuto/tetraciclina indisponíveis) — Concomitante × 14 dias',
                'Omeprazol 40mg + Amoxicilina 500mg + Claritromicina 500mg + Metronidazol 500mg',
                [
                    _p('28', 'cáps. omeprazol',    '1 cáps VO 12/12h × 14 dias'),
                    _p('56', 'comp. amoxicilina',   '2 comp de 500mg VO 12/12h (= 1g) × 14 dias'),
                    _p('28', 'comp. claritromicina', '1 comp VO 12/12h × 14 dias'),
                    _p('28', 'comp. metronidazol',  '1 comp VO 12/12h × 14 dias'),
                ],
                'Mais efeitos colaterais que a quádrupla — tomar junto às refeições.'),
        ]
        exames = [
            'Teste de cura: breath test (13C-ureia) OU antígeno fecal — '
            '4 semanas após ATB e ≥ 2 semanas após parar IBP',
        ]
        encaminhar = 'EDA se > 45 anos, alarm features, ou falha na 2ª eradicação'

    elif hp_desco:
        cat  = 'gastro_dispepsia_hp_testandteat'
        diag = 'Dispepsia — Test-and-Treat para H. pylori'
        raciocinio = (
            'Epigastralgia sem alarme + H. pylori nunca testado + < 45-50 anos '
            '→ estratégia test-and-treat. '
            'Teste não invasivo de preferência: breath test (13C-ureia) ou antígeno fecal. '
            'Evitar sorologias — não distingue infecção ativa de passada. '
            'Se positivo → eradicação (V Consenso Br 2025: quádrupla bismuto). '
            'Se negativo → IBP empírico 4 semanas (dispepsia funcional).'
        )
        prescricoes = []
        exames = [
            'Breath test (13C-ureia) — preferência (parar IBP 2 semanas antes)',
            'OU antígeno fecal H. pylori — alternativa se breath test indisponível',
            'NÃO pedir sorologia (falso-positivo por infecção passada)',
        ]
        encaminhar = 'EDA se > 45-50 anos ou persistência após test-and-treat'

    else:  # hp_eradicado ou histórico negativo
        cat  = 'gastro_dispepsia_funcional'
        diag = 'Dispepsia Funcional (H. pylori negativo / eradicado)'
        raciocinio = (
            'Epigastralgia com queimação / plenitude pós-prandial / saciedade precoce '
            'sem alarme + H. pylori ' +
            ('eradicado' if hp_erad else 'negativo') +
            ' → dispepsia funcional (critérios Roma IV). '
            'IBP em jejum 4 semanas. '
            'Se persistir: procinético (domperidona) para plenitude/saciedade. '
            'EDA: indicada se > 45-50 anos ou alarm features.'
        )
        prescricoes = [
            _rx('Supressor ácido', 'Omeprazol 20mg',
                [_p('28', 'cápsulas',
                    '1 cáps VO em jejum 30min antes do café × 28 dias')],
                'Retornar se sem melhora em 4 semanas → testar H. pylori ou EDA.'),
        ]
        exames = ['EDA se > 45 anos, perda de peso, disfagia, hematemese ou anemia']
        encaminhar = 'EDA se idade > 45-50 anos ou alarm features'

    orientacoes = {
        'alimentacao': (
            'Evitar: café, álcool, AINE/AAS, frituras, temperos fortes (pimenta, curry), '
            'cítricos (limão, laranja, abacaxi), chocolate, bebidas gasosas. '
            'Fazer refeições menores e mais frequentes (5-6×/dia em vez de 3 grandes). '
            'Não deitar nas 2-3h após a refeição.'
        ),
        'posicional':    'Elevar a cabeceira da cama 15-20cm (calços sob as pernas da cama — não só travesseiro).',
        'sinais_de_alerta': [
            'Vômito com sangue ou escuro (borra de café)',
            'Fezes pretas e alcatroadas (melena)',
            'Perda de peso involuntária',
            'Dificuldade para engolir',
            'Dor que acorda à noite',
        ],
    }

    return {
        'tipo': 'gastro', 'categoria': cat, 'diagnostico': diag,
        'urgencia': None, 'raciocinio': raciocinio,
        'achados': _achados_principais(dados), 'red_flags': [],
        'exames': exames,
        'conduta': [
            'Suspender AINE / AAS se em uso',
            'Evitar álcool e tabaco',
        ] + ([f'Uso de AINE — fator de risco para PUD identificado'] if dados.get('uso_aine') else []),
        'prescricoes_estruturadas': prescricoes, 'orientacoes': orientacoes,
        'encaminhar': encaminhar,
        'retorno': 'Retorno em 4-6 semanas para avaliar resposta.',
        'alerta_cdiff': False,
    }


# =============================================================================
# SII — Síndrome do Intestino Irritável (Roma IV)
# =============================================================================

def _check_sii(dados):
    return (dados.get('duracao_cronica') and
            dados.get('habito_intestinal') in ('diarreia', 'constipacao', 'alternancia') and
            dados.get('alivio_evacuacao') and
            not dados.get('perda_peso') and
            not dados.get('sangue_fezes') and
            not dados.get('febre'))


def _resultado_sii(dados):
    habi = dados.get('habito_intestinal', 'alternancia')
    if habi == 'constipacao':
        subtipo = 'C'
        cat     = 'gastro_sii_c'
        diag    = 'SII-C — Síndrome do Intestino Irritável com Constipação'
        raciocinio = (
            'Dor abdominal crônica (> 3 meses) + constipação predominante + alívio após evacuar '
            '→ SII-C (Roma IV). '
            'Sem alarm features. '
            'Trimebutina (antiespasmódico modulador da motilidade) + osmótico (Macrogol) + low-FODMAP.'
        )
        prescricoes = [
            _rx('Antiespasmódico', 'Trimebutina (Muvinor) 200mg',
                [_p('42', 'comprimidos', '1 comp VO 3×/dia antes das refeições × 2-4 semanas')]),
            _rx('Osmótico', 'Macrogol (PEG 4000) 10g',
                [_p('30', 'sachês', '1-2 sachês dissolvidos em 200mL água, 1×/dia')],
                'Iniciar com 1 sachê. Ajustar conforme resposta.'),
        ]
    elif habi == 'diarreia':
        subtipo = 'D'
        cat     = 'gastro_sii_d'
        diag    = 'SII-D — Síndrome do Intestino Irritável com Diarreia'
        raciocinio = (
            'Dor abdominal crônica (> 3 meses) + diarreia predominante + alívio após evacuar '
            '→ SII-D (Roma IV). '
            'Sem alarm features. '
            '⚠️  Buscapan VETADO se muco/sangue — aqui ausentes, antiespasmódico PRN liberado. '
            'Trimebutina (contínuo) + Loperamida (PRN para crises).'
        )
        prescricoes = [
            _rx('Antiespasmódico', 'Trimebutina (Muvinor) 200mg',
                [_p('42', 'comprimidos', '1 comp VO 3×/dia antes das refeições × 2-4 semanas')]),
            _rx('Antidiarreico PRN', 'Loperamida 2mg',
                [_p('20', 'cápsulas', '1-2 cáps VO após episódio diarreico — máx 8 cáps/dia')],
                'PRN apenas — não usar de forma contínua.'),
        ]
    else:
        subtipo = 'M'
        cat     = 'gastro_sii_m'
        diag    = 'SII-M — Síndrome do Intestino Irritável Misto'
        raciocinio = (
            'Dor abdominal crônica (> 3 meses) + alternância diarreia/constipação + alívio após evacuar '
            '→ SII-M (Roma IV). '
            'Trimebutina (modulador bidirecional da motilidade GI). '
            'Ajustar osmótico ou antidiarreico conforme sintoma predominante.'
        )
        prescricoes = [
            _rx('Antiespasmódico / modulador motilidade', 'Trimebutina (Muvinor) 200mg',
                [_p('42', 'comprimidos', '1 comp VO 3×/dia antes das refeições × 2-4 semanas')],
                'Avaliar em 4 semanas: se C predomina → adicionar Macrogol; se D predomina → Loperamida PRN.'),
        ]

    orientacoes = {
        'alimentacao': (
            f'SII-{subtipo} — Dieta low-FODMAP:\n'
            'EVITAR: trigo/centeio/cevada (pão, macarrão convencional), cebola, alho, '
            'maçã, pera, melancia, mel, sorbitol/manitol (adoçantes), leguminosas (feijão, lentilha), '
            'lactose (se intolerante). \n'
            'PREFERIR: arroz, batata, frango, peixe, banana, mirtilo, cenoura, abobrinha, '
            'aveia, quinoa, lácteos sem lactose.\n'
            'Fibras: meta 25g/dia. Água: 30-35mL/kg/dia (≈ 2-2,5L).\n'
            'Fase de reintrodução: após 4-6 semanas strict, reintroduzir 1 alimento/vez '
            'para identificar gatilho individual.'
        ),
        'estilo_de_vida': (
            'Estresse é gatilho importante — técnicas de relaxamento, exercício regular. '
            'Atividade física 30min/dia melhora trânsito intestinal e reduz dor.'
        ),
        'sinais_de_alerta': [
            'Sangue nas fezes',
            'Perda de peso involuntária',
            'Acordar à noite com diarreia (IBD até excluir)',
            'Febre',
            'Sintomas iniciando após 50 anos (colonoscopia)',
        ],
    }

    return {
        'tipo': 'gastro', 'categoria': cat, 'diagnostico': diag,
        'urgencia': None, 'raciocinio': raciocinio,
        'achados': _achados_principais(dados), 'red_flags': [],
        'exames': [
            'Hemograma + PCR (excluir IBD se dúvida)',
            'Calprotectina fecal (IBD vs SII — indicada se dúvida)',
            'TSH (hipotireoidismo como causa de constipação)',
        ],
        'conduta': ['Acompanhar diário alimentar para identificar gatilhos individuais'],
        'prescricoes_estruturadas': prescricoes, 'orientacoes': orientacoes,
        'encaminhar': 'Gastroenterologia se refratário após 8-12 semanas de tratamento',
        'retorno': 'Retorno em 4-6 semanas.',
        'alerta_cdiff': dados.get('alerta_cdiff', False),
    }


# =============================================================================
# CONSTIPAÇÃO FUNCIONAL (Roma IV)
# =============================================================================

def _check_constipacao(dados):
    return (dados.get('habito_intestinal') == 'constipacao' and
            not dados.get('febre') and
            not dados.get('sangue_fezes') and
            not dados.get('alivio_evacuacao'))  # se alivia evacuando → SII-C


def _resultado_constipacao(dados):
    raciocinio = (
        'Constipação (< 3 evacuações/semana, fezes duras, esforço) sem alarm features '
        '→ constipação funcional (Roma IV). '
        'Excluir causas secundárias: hipotireoidismo (pedir TSH), medicamentos (opioides, '
        'bloqueadores de cálcio, anticolinérgicos), DM. '
        'Tratar com fibras + hidratação + atividade física + osmótico.'
    )
    prescricoes = [
        _rx('Laxativo osmótico (1ª linha)', 'Macrogol (PEG 4000) 10g',
            [_p('30', 'sachês', '1-2 sachês dissolvidos em 200mL água, 1×/dia')],
            'Uso contínuo permitido — sem risco de dependência ou cólon catártico.'),
        _rx('Osmótico alternativo', 'Lactulose 10g/15mL',
            [_p('1', 'frasco 120mL', '15-30mL VO 1×/dia')],
            'Pode causar flatulência — preferir Macrogol se disponível.'),
        _rx('Resgate (máx 5 dias)', 'Bisacodil 5mg',
            [_p('10', 'comprimidos', '1-2 comp VO à noite — máx 5 dias consecutivos')],
            'NÃO usar cronicamente — risco de cólon catártico.'),
    ]
    orientacoes = {
        'alimentacao': (
            'Fibras: meta 25g/dia. Boas fontes:\n'
            '• Ameixa: 3-5 unidades/dia (ou suco de ameixa 150mL)\n'
            '• Pera ou maçã COM casca\n'
            '• Aveia: 1-2 col. sopa/dia (vitamina, iogurte, mingau)\n'
            '• Brócolis, couve, cenoura\n'
            '• Pão integral (de verdade — ver fibras no rótulo)\n'
            '• Feijão / lentilha (se bem tolerado)\n'
            'Aumentar fibra GRADUALMENTE para evitar flatulência.'
        ),
        'hidratacao':   'Água: 8-10 copos/dia (2-2,5L). Aumentar água É OBRIGATÓRIO ao aumentar fibra.',
        'rotina':       (
            'Horário fixo: tentar evacuar todo dia 20-30min após café da manhã ou almoço '
            '(reflexo gastrocólico). Não ignorar a vontade. '
            'Posição: pés apoiados em banquinho — posição de cócoras facilita.'
        ),
        'exercicio':    'Caminhada 30min/dia aumenta o trânsito intestinal.',
        'sinais_de_alerta': [
            'Sangue nas fezes',
            'Constipação de início novo em > 50 anos (colonoscopia)',
            'Perda de peso involuntária',
            'Fezes finas como lápis (mass lesion)',
            'Sem melhora em 4 semanas com fibra + laxativo',
        ],
    }
    return {
        'tipo': 'gastro', 'categoria': 'gastro_constipacao_funcional',
        'diagnostico': 'Constipação Funcional',
        'urgencia': None, 'raciocinio': raciocinio,
        'achados': _achados_principais(dados), 'red_flags': [],
        'exames': [
            'TSH (excluir hipotireoidismo)',
            'Glicemia de jejum (DM pode causar dismotilidade)',
            'Hemograma (anemia pode coexistir)',
        ],
        'conduta': ['Revisar medicamentos que causam constipação (opioides, Ca-bloqueadores, ferro)'],
        'prescricoes_estruturadas': prescricoes, 'orientacoes': orientacoes,
        'encaminhar': 'Gastroenterologia se refratária após 8-12 semanas',
        'retorno': 'Retorno em 4-6 semanas.',
        'alerta_cdiff': False,
    }


# =============================================================================
# INTOLERÂNCIA À LACTOSE
# =============================================================================

def _check_lactose(dados):
    return (dados.get('piora_lactose') or dados.get('melhora_sem_lactose'))


def _resultado_lactose(dados):
    raciocinio = (
        'Sintomas GI (distensão, cólica, diarreia) associados a laticínios '
        '→ intolerância à lactose. '
        'Diagnóstico empírico: exclusão 4 semanas + reintrodução gradual para confirmar. '
        'Alternativa diagnóstica: teste de hidrogênio expirado (padrão-ouro, raro na APS).'
    )
    return {
        'tipo': 'gastro', 'categoria': 'gastro_intolerancia_lactose',
        'diagnostico': 'Intolerância à Lactose — Diagnóstico Empírico',
        'urgencia': None, 'raciocinio': raciocinio,
        'achados': _achados_principais(dados), 'red_flags': [],
        'exames': ['Nenhum exame necessário para triagem — diagnóstico por exclusão empírica'],
        'conduta': [
            'Excluir laticínios por 4 semanas (leite, queijo fresco, iogurte convencional)',
            'Se sintomas cessam → confirma intolerância à lactose',
            'Reintroduzir gradualmente: queijos duros (menor lactose) → iogurte → leite',
            'Substitutos permitidos: leite sem lactose, bebida de soja/amêndoa/aveia, queijos maturados',
        ],
        'prescricoes_estruturadas': [], 'orientacoes': {
            'alimentacao': (
                'EVITAR (rica em lactose): leite integral/desnatado, queijo fresco/ricota/cottage, '
                'iogurte convencional, sorvete, creme de leite, manteiga. '
                'PERMITIDO: leite sem lactose, bebida vegetal (soja/amêndoa/aveia), '
                'queijos maturados (parmesão, suíço, cheddar — lactose degradada durante maturação), '
                'iogurte grego (menor lactose). '
                'Lactase suplementar (ex: LactAid) pode ser usada em situações pontuais.'
            ),
            'sinais_de_alerta': ['Sintomas persistentes mesmo sem lactose — pensar SII ou celíaca'],
        },
        'encaminhar': None,
        'retorno': 'Retorno em 4-6 semanas para reavaliar resposta à exclusão.',
        'alerta_cdiff': False,
    }


# =============================================================================
# NÁUSEA / VÔMITO
# =============================================================================

def _resultado_nausea(dados):
    raciocinio = (
        'Náusea'
        + (' e vômito' if dados.get('vomito') else '') +
        ' sem causa específica identificada → manejo sintomático. '
        'Ondansetrona preferida (menos efeitos extrapiramidais). '
        'Metoclopramida: cuidado em > 65 anos (risco de distonia aguda/acatisia). '
        'Domperidona: alternativa com menor efeito sobre SNC.'
    )
    prescricoes = [
        _rx('Antiemético — 1ª escolha', 'Ondansetrona 8mg',
            [_p('10', 'comprimidos', '1 comp VO/SL de 8/8h PRN — máx 24mg/dia')],
            'Preferência em gestantes e idosos. Cuidado em QT longo congênito.'),
        _rx('Alternativa (procinético)', 'Domperidona 10mg',
            [_p('30', 'comprimidos', '1 comp VO 3×/dia, 15min antes das refeições')],
            'Menor risco de EPS que metoclopramida. Evitar em arritmias / QT longo.'),
    ]
    return {
        'tipo': 'gastro', 'categoria': 'gastro_nausea_vomito',
        'diagnostico': 'Náusea / Vômito — Sintomático',
        'urgencia': None, 'raciocinio': raciocinio,
        'achados': _achados_principais(dados), 'red_flags': [],
        'exames': ['Avaliar causa subjacente (glicemia, ureia/creat, US abdominal se persistente)'],
        'conduta': [
            'Hidratação oral: pequenos goles de água gelada / suco de gengibre / chá de gengibre',
            'Refeições pequenas e frequentes, frias ou temperatura ambiente (odor forte piora)',
            'Evitar deitar imediatamente após comer',
        ],
        'prescricoes_estruturadas': prescricoes, 'orientacoes': {
            'sinais_de_alerta': [
                'Sangue no vômito',
                'Desidratação (boca seca, tontura, urina escura)',
                'Sem conseguir manter líquidos por > 24h',
                'Dor abdominal intensa associada',
            ],
        },
        'encaminhar': None,
        'retorno': 'Se sem melhora em 48h ou surgir alarm feature.',
        'alerta_cdiff': False,
    }


# =============================================================================
# INESPECÍFICO
# =============================================================================

def _resultado_inespecifico(dados):
    raciocinio = (
        'Dor abdominal '
        + (f'em {dados.get("localizacao", "difusa")} ' if dados.get('localizacao') else '') +
        'sem padrão diagnóstico definido. '
        'Sem alarm features. Sintomático e retorno para reavaliação.'
    )
    prescricoes = [
        _rx('Analgesia / antiespasmódico PRN', 'Buscapan 10mg + Dipirona 500mg',
            [_p('20', 'comp. de cada', '1 comp. de cada VO 6/6h PRN se dor')],
            '⚠️  Suspender se febre > 38°C, sangue nas fezes ou piora progressiva.'),
    ]
    return {
        'tipo': 'gastro', 'categoria': 'gastro_inespecifico',
        'diagnostico': 'Dor Abdominal — Investigação em Andamento',
        'urgencia': None, 'raciocinio': raciocinio,
        'achados': _achados_principais(dados), 'red_flags': [],
        'exames': [
            'Hemograma + PCR',
            'TGO / TGP / GGT / bilirrubinas (excluir hepato-biliar)',
            'Amilase + lipase (excluir pancreatite)',
            'US abdominal total',
        ],
        'conduta': ['Dieta branda enquanto dura a dor', 'Analgesia PRN'],
        'prescricoes_estruturadas': prescricoes, 'orientacoes': {
            'sinais_de_alerta': [
                'Febre',
                'Piora da dor',
                'Sangue nas fezes',
                'Vômito incoercível',
                'Sem melhora em 48-72h',
            ],
        },
        'encaminhar': None,
        'retorno': 'Retorno em 48-72h para reavaliação. PS se piora.',
        'alerta_cdiff': dados.get('alerta_cdiff', False),
    }


# =============================================================================
# PONTO DE ENTRADA PRINCIPAL
# =============================================================================

def _interpretar_gastro_core(dados: dict) -> dict:
    """
    Motor principal de raciocínio clínico — Dor Abdominal / Queixas GI.

    Ordem de prioridade:
    1. Red flags → PS imediato
    2. DIP (mulher)
    3. Diverticulite ambulatorial
    4. IBD suspeita
    5. Celíaca suspeita
    6. Parasitoses
    7. Cólica biliar
    8. Dispepsia / H. pylori
    9. SII (C / D / M)
    10. Constipação funcional
    11. Intolerância à lactose
    12. Náusea / vômito
    13. Inespecífico
    """
    # 1. Red flags — PS imediato
    if _check_emergencia(dados):
        return _resultado_emergencia(dados)

    # 2. DIP
    if dados.get('suspeita_dip'):
        return _resultado_dip(dados)

    # 3. Diverticulite ambulatorial
    if _check_diverticulite(dados):
        return _resultado_diverticulite(dados)

    # 4. IBD suspeita
    if _check_ibd(dados):
        return _resultado_ibd(dados)

    # 5. Celíaca suspeita
    if _check_celiaca(dados):
        return _resultado_celiaca(dados)

    # 6. Parasitoses (contexto epidemiológico)
    if _check_parasitose(dados):
        return _resultado_parasitose(dados)

    # 7. Cólica biliar
    if _check_colica_biliar(dados):
        return _resultado_colica_biliar(dados)

    # 8. Dispepsia / H. pylori
    if _check_dispepsia(dados):
        return _resultado_dispepsia(dados)

    # 9. SII
    if _check_sii(dados):
        return _resultado_sii(dados)

    # 10. Constipação funcional
    if _check_constipacao(dados):
        return _resultado_constipacao(dados)

    # 11. Intolerância à lactose
    if _check_lactose(dados):
        return _resultado_lactose(dados)

    # 12. Náusea/vômito
    if dados.get('nausea') or dados.get('vomito'):
        return _resultado_nausea(dados)

    # 13. Inespecífico
    return _resultado_inespecifico(dados)


# =============================================================================
# PENTE FINO — alertas de segurança transversais
# =============================================================================

def _enriquecer_gastro(resultado: dict, dados: dict) -> dict:
    """Adiciona alertas_seguranca ao resultado (renderizados no topo do #Plano)."""
    alertas = []
    cat = resultado.get('categoria', '')

    # C. diff: ATB recente + diarreia — não usar loperamida
    if dados.get('alerta_cdiff'):
        alertas.append(
            '⚠️ ATB recente + diarreia → solicitar toxina C. difficile nas fezes; '
            'NÃO usar loperamida até excluir colite por C. diff'
        )

    # IBD: AINE absolutamente proibido
    if cat == 'gastro_ibd_suspeita' and dados.get('uso_aine'):
        alertas.append(
            '🔴 VETO AINE / AAS em curso — suspender imediatamente; '
            'pode desencadear flare grave de DII'
        )

    # Celíaca: não retirar glúten antes do exame
    if cat == 'gastro_celiaca_suspeita':
        alertas.append(
            '⚠️ NÃO retirar glúten antes de colher o anti-tTG IgA — '
            'dieta sem glúten gera falso-negativo garantido'
        )

    # DIP: retorno 72h é obrigatório
    if cat == 'gastro_dip':
        alertas.append(
            '⚠️ DIP: retorno obrigatório em 72h — sem melhora = internação + ATB IV. '
            'Parceiro(s) deve(m) ser tratado(s) concomitantemente'
        )

    # Metronidazol: álcool proibido durante e 48h após
    rxs = resultado.get('prescricoes_estruturadas', [])
    if any('etronidazol' in rx.get('medicamento', '') for rx in rxs):
        alertas.append(
            '⚠️ Metronidazol: PROIBIR álcool durante o tratamento e por 48h após '
            '(reação antabuse: náusea, rubor, taquicardia)'
        )

    # Dispepsia + AINE em uso → risco de PUD
    if cat.startswith('gastro_dispepsia') and dados.get('uso_aine'):
        alertas.append(
            '⚠️ AINE em uso → fator de risco para PUD/gastrite. '
            'Suspender AINE ou adicionar IBP protetor enquanto em uso'
        )

    resultado['alertas_seguranca'] = alertas
    return resultado


def interpretar_queixa_gastro(dados: dict) -> dict:
    """Ponto de entrada público — core + pente fino."""
    return _enriquecer_gastro(_interpretar_gastro_core(dados), dados)
