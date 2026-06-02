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


PREPROCESSORS = {
    'odinofagia':    pre_odinofagia,
    'otalgia':       pre_otalgia,
    'rinossinusite': pre_rinossinusite,
    'olho_vermelho': pre_olho_vermelho,
    'edema':         pre_edema,
    'sincope':       pre_sincope,
}
