# ui/preprocessors.py
# Pré-processadores que computam flags DERIVADAS a partir de campos crus,
# replicando a lógica dos coletores de subjetivo do CLI.
#
# Engines de ORL/oftalmo LEEM flags como 'oma_suspeita', 'centor_score',
# 'glaucoma_agudo_suspeito' — que o coletor CLI computa. Aqui replicamos
# essa computação para a interface web.
#
# Cada função recebe e devolve o dict de dados (form_data merged).


def _centor_age(idade) -> int:
    try:
        idade = float(idade)
    except (TypeError, ValueError):
        return 0
    if idade < 15:
        return 1
    if idade >= 45:
        return -1
    return 0


def pre_odinofagia(d: dict) -> dict:
    idade = d.get('idade', 30) or 30
    d['centor_score'] = (
        (1 if d.get('febre') else 0) +
        (1 if d.get('exsudato_amigdaliano') else 0) +
        (1 if d.get('adenopatia_cervical_ant') else 0) +
        (1 if not d.get('tosse') else 0) +
        _centor_age(idade)
    )
    d['abscesso_suspeito'] = any([
        d.get('trismo'), d.get('sialorreia'), d.get('voz_batata'),
        d.get('desvio_uvula'), d.get('disfagia_saliva'),
    ])
    d['emergencia_respiratoria'] = bool(
        d.get('estridor') or d.get('dificuldade_respiratoria')
    )
    try:
        ia = float(idade)
    except (TypeError, ValueError):
        ia = 30
    d['mononucleose_suspeita'] = bool(
        d.get('exsudato_amigdaliano') and
        d.get('adenopatia_generalizada') and
        15 <= ia <= 35
    )
    return d


def pre_otalgia(d: dict) -> dict:
    idade = d.get('idade', 30) or 30
    try:
        idade = float(idade)
    except (TypeError, ValueError):
        idade = 30
    crianca_pequena = idade < 2
    d['otalgia_grave'] = bool(d.get('otalgia_grave'))  # já vem como checkbox

    d['mastoidite_suspeita'] = any([
        d.get('dor_retroauricular'), d.get('pavilhao_projetado'),
        d.get('flutuacao_retroaur'), d.get('febre_mais_72h_atb'),
    ])
    d['otite_externa_suspeita'] = bool(
        d.get('trago_positivo') or d.get('canal_edema') or
        (d.get('banho_piscina') and d.get('otalgia_grave'))
    )
    d['oma_suspeita'] = bool(
        not d.get('trago_positivo') and
        (d.get('iras_recente') or d.get('ouvido_cheio') or d.get('hipoagusia')) and
        (d.get('febre') or d.get('mt_abaulada') or d.get('mt_hiperemia') or
         d.get('mt_efusao') or d.get('otorreia_purulenta'))
    )
    d['oma_tratar_imediato'] = any([
        idade < 0.5,
        (crianca_pequena and d.get('bilateral')),
        d.get('febre_alta'), d.get('otalgia_mais_48h'),
        d.get('otorreia_purulenta'), d.get('seguimento_incerto'),
        d.get('conjuntivite_purulenta'),
        d.get('oma_recorrente') and d.get('atb_recente_30d'),
    ])
    d['oe_maligna_suspeita'] = bool(
        d.get('diabetes') and
        (d.get('canal_estenose') or d.get('canal_edema')) and
        d.get('otalgia_grave')
    )
    dtm = sum([
        bool(d.get('dor_mastigacao')), bool(d.get('dor_matinal')),
        bool(d.get('bruxismo')), bool(d.get('click_mandibula')),
        bool(d.get('limitacao_abertura')),
    ])
    d['dtm_criterios_n'] = dtm
    d['dtm_suspeita'] = bool(dtm >= 2 and not d.get('febre'))
    return d


def pre_rinossinusite(d: dict) -> dict:
    idade = d.get('idade', 30) or 30
    try:
        idade = float(idade)
    except (TypeError, ValueError):
        idade = 30
    dur = d.get('duracao_dias_aprox', 0) or 0

    d['sindrome_grave_rsab'] = bool(
        d.get('febre_alta') and d.get('rinorreia_purulenta') and
        d.get('dor_facial_unilateral') and dur >= 3
    )
    d['red_flag_orbital'] = any([
        d.get('edema_periorbital'), d.get('diplopia'), d.get('proptose'),
    ])
    d['red_flag_meningeo'] = any([
        d.get('rigidez_nucal'), d.get('cefaleia_intensa'),
        d.get('alteracao_consciencia'),
    ])
    d['risco_rsab_grave'] = any([
        d.get('atb_recente_30d'), d.get('imunossuprimido'),
        idade < 2 or idade > 65,
        d.get('double_sickening') and dur >= 10,
    ])
    d['rsab_criterio'] = bool(
        dur >= 10 or bool(d.get('double_sickening')) or
        bool(d.get('sindrome_grave_rsab'))
    )
    if dur < 7 and not d.get('double_sickening') and not d.get('sindrome_grave_rsab'):
        d['rsab_criterio'] = False
    d['rinite_alergica_suspeita'] = bool(
        d.get('espirros_salva') and d.get('rinorreia_clara') and
        not d.get('febre') and
        (d.get('prurido_nasal_ocular') or d.get('piora_sazonal') or
         d.get('alergenos_conhecidos'))
    )
    return d


def pre_olho_vermelho(d: dict) -> dict:
    d['glaucoma_agudo_suspeito'] = bool(
        d.get('halos_coloridos') and d.get('dor_intensa') and d.get('visao_turva')
    )
    d['ulcera_cornea_suspeita'] = bool(
        d.get('lente_de_contato') and d.get('dor_ocular') and
        (d.get('fotofobia') or d.get('visao_turva') or d.get('corpo_estranho_sensacao'))
    )
    d['uveite_suspeita'] = bool(
        d.get('ciliary_flush') and (d.get('dor_ocular') or d.get('fotofobia'))
    )
    d['celulite_orbitaria_suspeita'] = bool(
        d.get('edema_palpebral') and
        (d.get('limitacao_motilidade') or d.get('proptose'))
    )
    d['celulite_preseptal_suspeita'] = bool(
        d.get('edema_palpebral') and d.get('febre') and
        not d['celulite_orbitaria_suspeita']
    )
    d['endoftalmite_suspeita'] = bool(
        d.get('pos_cirurgico_ocular') and d.get('dor_ocular') and d.get('visao_turva')
    )
    d['conjuntivite_bacteriana_suspeita'] = bool(
        d.get('secrecao_purulenta') and d.get('palpebra_grudada') and
        not d.get('ciliary_flush') and not d.get('lente_de_contato') and
        not d.get('pos_cirurgico_ocular')
    )
    d['conjuntivite_viral_suspeita'] = bool(
        not d.get('secrecao_purulenta') and not d.get('ciliary_flush') and
        (d.get('bilateral') or d.get('adenopatia_preauricular') or
         d.get('contato_conjuntivite')) and
        (d.get('secrecao_aquosa') or d.get('lacrimejamento'))
    )
    d['conjuntivite_alergica_suspeita'] = bool(
        d.get('prurido_ocular') and not d.get('secrecao_purulenta') and
        not d.get('ciliary_flush') and
        (d.get('rinite_alergica_concomitante') or
         d.get('rinite_alergica_conhecida') or d.get('piora_sazonal_ocular'))
    )
    d['hordeoleo_suspeito'] = bool(
        d.get('eritema_palpebral') and d.get('dor_ocular') and
        not d.get('febre') and not d['celulite_preseptal_suspeita']
    )
    return d


def pre_edema(d: dict) -> dict:
    # cronico = não agudo (espelha o coletor do CLI)
    d['cronico'] = not d.get('inicio_agudo', False)
    return d


def pre_sincope(d: dict) -> dict:
    # neuropatia autonômica inferida de diabetes/parkinson (engine lê a flag)
    if d.get('diabetes') or d.get('parkinson'):
        d['neuropatia_autonomica'] = True
    return d


def pre_msk(d: dict) -> dict:
    """
    Flags derivados compartilhados dos módulos MSK (espelha os coletores CLI):
      - faixas etárias (idade >= N) lidas direto pelos engines
      - Ottawa tornozelo (any das palpações) + FABER/FADIR realizados (quadril)
    """
    try:
        idade = int(d.get('idade', 0) or 0)
    except (ValueError, TypeError):
        idade = 0
    d['idade_abaixo_40'] = idade < 40
    d['idade_acima_40']  = idade >= 40
    d['idade_acima_45']  = idade >= 45
    d['idade_acima_50']  = idade >= 50
    d['idade_acima_55']  = idade >= 55
    d['idade_acima_60']  = idade >= 60
    d['idade_acima_70']  = idade >= 70

    # Ottawa tornozelo/pé — positivo se qualquer critério de palpação/apoio
    if any(k in d for k in ('dor_maleolo_posterior_lateral', 'dor_navicular',
                            'dor_base_5o_meta', 'incapaz_apoio_4_passos')):
        ott = any([
            d.get('dor_maleolo_posterior_lateral'), d.get('dor_maleolo_posterior_medial'),
            d.get('incapaz_apoio_4_passos'), d.get('dor_navicular'), d.get('dor_base_5o_meta'),
            d.get('palpacao_maleolo_lateral_positiva'), d.get('palpacao_maleolo_medial_positiva'),
            d.get('palpacao_base_5o_meta_positiva'), d.get('palpacao_navicular_positiva'),
        ])
        d['ottawa_positivo'] = ott
        d['ottawa_exame_positivo'] = ott
        d['ottawa'] = ott

    # FABER/FADIR — marcar como realizados quando o achado foi avaliado (quadril)
    if 'faber_positivo' in d: d['faber_realizado'] = True
    if 'fadir_positivo' in d: d['fadir_realizado'] = True

    # trauma_agudo é alias de trauma (joelho)
    if d.get('trauma') and 'trauma_agudo' not in d:
        d['trauma_agudo'] = True
    return d


def pre_gastro(d: dict) -> dict:
    """
    Computa flags derivadas do gastro — espelha as derivações do coletor CLI
    (gastro_subjetivo.py) que o engine lê mas que a UI expõe como selects/bools.
    """
    try:
        idade = int(d.get('idade', 0) or 0)
    except (ValueError, TypeError):
        idade = 0
    d['idoso'] = idade >= 60

    # Caráter → flags booleanas
    d['inicio_subito']   = d.get('carater') == 'aguda_subita'
    d['dor_catastrofica'] = d.get('intensidade') == 'catastrofica'

    # Relação alimentar → flags individuais
    rel = d.get('relacao_alimentar', 'sem_relacao')
    d.setdefault('piora_gorduroso', rel == 'piora_gorduroso')
    d.setdefault('piora_gluten',    rel == 'piora_gluten')
    d.setdefault('piora_lactose',   rel == 'piora_lactose')
    # melhora_sem_gluten/lactose podem reforçar piora_gluten/lactose
    if d.get('melhora_sem_gluten'):  d['piora_gluten']  = True
    if d.get('melhora_sem_lactose'): d['piora_lactose'] = True

    # Habito intestinal
    hab = d.get('habito_intestinal', 'normal')
    d['obstipacao_total'] = hab == 'sem_evacuacao_gases'

    # Febre
    grau = d.get('febre_grau', 'sem')
    d['febre']      = grau != 'sem'
    d['febre_alta'] = grau == 'alta'

    # Sangue nas fezes (booleans diretos no schema)
    d['sangue_fezes'] = bool(d.get('hematoquezia')) or bool(d.get('melena'))

    # Exame físico
    d['peritonismo']   = bool(d.get('blumberg_positivo')) or bool(d.get('rigidez'))
    d['defesa']        = d['peritonismo']
    d['abdome_flacido'] = not d['peritonismo']

    # Risco isquemia mesentérica: idoso + FA ou vasculopatia
    d['risco_isquemia_mesenterica'] = bool(
        d.get('idoso') and (d.get('fa_arritmia') or d.get('vasculopata'))
    )

    # Parasitoses
    d['suspeita_parasitose'] = bool(
        d.get('viagem_endemica') or d.get('agua_nao_tratada') or d.get('contato_animal')
    )

    # H. pylori
    hp = d.get('hp_status', 'desconhecido')
    d['hp_positivo']     = hp == 'positivo'
    d['hp_eradicado']    = hp == 'eradicado'
    d['hp_sem_cura']     = hp == 'sem_cura'
    d['hp_desconhecido'] = hp == 'desconhecido'

    # Duração + episódios
    dur = d.get('duracao', 'dias')
    d['duracao_cronica'] = dur in ('meses_1_3', 'meses_mais_3')
    ep = d.get('episodios', 'primeira_vez')
    d['primeira_vez'] = ep == 'primeira_vez'
    d['recorrente']   = ep == 'recorrente'
    d['cronico']      = ep == 'cronico' or d['duracao_cronica']

    # C. difficile
    d['alerta_cdiff'] = bool(d.get('atb_recente') and hab == 'diarreia')

    # Manifestações extraintestinais
    d['manifestacoes_extraintestinais'] = any(
        d.get(k) for k in ('artrite_extra', 'lesao_pele_extra', 'uveite_extra', 'aftas_extra')
    )

    # IBD suspeita: diarreia crônica + alarm feature
    d['suspeita_ibd'] = bool(
        d.get('duracao_cronica') and
        hab in ('diarreia', 'alternancia') and
        (d.get('perda_peso') or d.get('sangue_fezes') or d.get('manifestacoes_extraintestinais'))
    )

    # Celíaca: piora/melhora com glúten + crônico
    d['suspeita_celiaca'] = bool(
        (d.get('piora_gluten') or d.get('melhora_sem_gluten')) and d.get('duracao_cronica')
    )

    # Saúde da mulher
    if d.get('sexo_feminino'):
        d['suspeita_dip'] = bool(
            d.get('febre') and d.get('corrimento_purulento') and
            d.get('dor_pelvica') and not d.get('dismenorreia_habitual')
        )
        d['suspeita_ectopica'] = bool(
            d.get('atraso_menstrual') and d.get('dor_pelvica_aguda') and
            d.get('intensidade') in ('intensa', 'catastrofica')
        )
    else:
        d['suspeita_dip']     = False
        d['suspeita_ectopica'] = False
        for k in ('atraso_menstrual', 'corrimento_purulento', 'dor_pelvica',
                  'dor_pelvica_aguda', 'dismenorreia_habitual'):
            d.setdefault(k, False)

    return d


def pre_sono(d: dict) -> dict:
    """
    Computa flags derivadas do sono — principalmente stopbang_itens (dict esperado
    pelo engine) e idade_tcr default a partir de idade do paciente.
    """
    # stopbang_itens: engine acessa .get('masculino', False) deste dict
    d['stopbang_itens'] = {'masculino': bool(d.get('masculino_stopbang', False))}

    # benzo_qual: engine espera string; select com '' = não usa
    if not d.get('benzo_qual'):
        d['benzo_qual'] = 'benzodiazepínico'

    # idade_tcr default = idade do paciente
    if not d.get('idade_tcr'):
        try:
            d['idade_tcr'] = int(d.get('idade', 0) or 0)
        except (ValueError, TypeError):
            d['idade_tcr'] = 0

    # horas_cama/sono devem ser float para _eficiencia_sono
    for k in ('horas_cama', 'horas_sono'):
        try:
            d[k] = float(d.get(k) or 0)
        except (ValueError, TypeError):
            d[k] = 0.0

    return d


def pre_hemorragia(d: dict) -> dict:
    """
    Computa flags derivadas da hemorragia digestiva:
      - ramo: 'ugib' (HDA) ou 'lgib' (HDB) a partir de tipo_sangramento
      - melena: bool (engine usa como critério do GBS)
    """
    ts = d.get('tipo_sangramento', '')
    # Mapeamento tipo → ramo
    if ts in ('hematoquezia', 'papel_apenas', 'marrom_escuro'):
        d.setdefault('ramo', 'lgib')
    else:
        d.setdefault('ramo', 'ugib')

    # melena como bool para o GBS score
    d['melena'] = ts in ('melena', 'borra_cafe', 'marrom_escuro')

    # sincope: o schema usa 'sincope' como bool direto ✅ (já vem correto)
    return d


def pre_urinario(d: dict) -> dict:
    """Converte sexo do cabeçalho ('masculino'/'feminino') para o formato do engine ('M'/'F')."""
    sexo = d.get('sexo', '')
    if sexo == 'feminino':
        d['sexo'] = 'F'
    elif sexo == 'masculino':
        d['sexo'] = 'M'
    return d


def pre_vertigem(d: dict) -> dict:
    """
    O engine legado de vertigem usa obj["chave"] (acesso direto, não .get()),
    então garante que TODOS os campos do schema existam com default False.
    """
    _campos_bool = (
        'sensacao_rotatoria', 'desequilibrio', 'sensacao_pre_sincope',
        'gatilho_mudar_posicao', 'gatilho_espontaneo',
        'continuo', 'recorrente',
        'duracao_segundos_minutos', 'duracao_horas', 'duracao_dias',
        'incapaz_de_andar', 'deficit_focal', 'diplopia', 'disartria',
        'fraqueza', 'parestesias', 'cefaleia',
        'hints_preocupante', 'dix_hallpike_positivo',
        'roll_test_positivo', 'canal_horizontal',
        'ortostatismo_sugestivo',
        'zumbido', 'perda_auditiva', 'plenitude_auricular', 'sincope',
    )
    for chave in _campos_bool:
        d.setdefault(chave, False)
    return d


PREPROCESSORS = {
    'odinofagia':    pre_odinofagia,
    'otalgia':       pre_otalgia,
    'rinossinusite': pre_rinossinusite,
    'olho_vermelho': pre_olho_vermelho,
    'edema':         pre_edema,
    'sincope':       pre_sincope,
    'gastro':        pre_gastro,
    'sono':          pre_sono,
    'hemorragia':    pre_hemorragia,
    'joelho':        pre_msk,
    'ombro':         pre_msk,
    'coluna':        pre_msk,
    'quadril':       pre_msk,
    'mao_punho':     pre_msk,
    'tornozelo_pe':  pre_msk,
    'fibromialgia':  pre_msk,
    'urinario':      pre_urinario,
    'vertigem':      pre_vertigem,
}
