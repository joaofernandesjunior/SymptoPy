# prontuario/dispatcher.py
# Roteador central — único lugar onde módulos novos são registrados
# Para adicionar módulo novo: adicionar entrada em MODULOS_QUEIXA
# main.py nunca precisa mudar

import json
from modules.raciocinio.motores.integrador import interpretar_dispneia
from modules.raciocinio.vertigem_dx import interpretar_vertigem
from modules.raciocinio.cefaleia_dx import interpretar_cefaleia

MODULOS_QUEIXA = {
    # --- módulos legados ---
    'dispneia': {
        'tipo': 'legado', 'chave': 'dispneia',
        'interpreta': interpretar_dispneia,
        'args': lambda subj, obj, admissao, paciente: (subj, obj, admissao, paciente)
    },
    'vertigem': {
        'tipo': 'legado', 'chave': 'vertigem',
        'interpreta': interpretar_vertigem,
        'args': lambda subj, obj, admissao, paciente: (subj, obj)
    },
    'cefaleia': {
        'tipo': 'legado', 'chave': 'cefaleia',
        'interpreta': interpretar_cefaleia,
        'args': lambda subj, obj, admissao, paciente: (subj, obj)
    },

    # --- módulos orgânicos ---
    'tosse':              {'tipo': 'organico', 'modulo': 'tosse'},
    'tosse cronica':      {'tipo': 'organico', 'modulo': 'tosse'},
    'tosse seca':         {'tipo': 'organico', 'modulo': 'tosse'},
    'tosse com catarro':  {'tipo': 'organico', 'modulo': 'tosse'},
    'tosse com sangue':   {'tipo': 'organico', 'modulo': 'tosse'},

    'fadiga':             {'tipo': 'organico', 'modulo': 'fadiga'},
    'cansaco':            {'tipo': 'organico', 'modulo': 'fadiga'},
    'fadiga cronica':     {'tipo': 'organico', 'modulo': 'fadiga'},
    'me/sfc':             {'tipo': 'organico', 'modulo': 'fadiga'},
    'exaustao cronica':   {'tipo': 'organico', 'modulo': 'fadiga'},

    'diarreia':              {'tipo': 'organico', 'modulo': 'diarreia'},
    'diarreia aguda':        {'tipo': 'organico', 'modulo': 'diarreia'},
    'diarreia cronica':      {'tipo': 'organico', 'modulo': 'diarreia'},
    'diarreia com sangue':   {'tipo': 'organico', 'modulo': 'diarreia'},
    'diarreia do viajante':  {'tipo': 'organico', 'modulo': 'diarreia'},
    'gastroenterite':        {'tipo': 'organico', 'modulo': 'diarreia'},
    'enterite':              {'tipo': 'organico', 'modulo': 'diarreia'},

    # --- módulos ivas (viral puro: resfriado, gripe) ---
    'ivas':                  {'tipo': 'organico', 'modulo': 'ivas'},
    'resfriado':             {'tipo': 'organico', 'modulo': 'ivas'},
    'gripe':                 {'tipo': 'organico', 'modulo': 'ivas'},
    'influenza':             {'tipo': 'organico', 'modulo': 'ivas'},
    # --- módulos ORL: rinossinusite (sintoma-guia: obstrução nasal/sinusite) ---
    'sinusite':              {'tipo': 'orl', 'modulo': 'rinossinusite'},
    'rinossinusite':         {'tipo': 'orl', 'modulo': 'rinossinusite'},
    'obstrucao nasal':       {'tipo': 'orl', 'modulo': 'rinossinusite'},
    'obstrução nasal':       {'tipo': 'orl', 'modulo': 'rinossinusite'},
    'entupimento nasal':     {'tipo': 'orl', 'modulo': 'rinossinusite'},
    'nariz entupido':        {'tipo': 'orl', 'modulo': 'rinossinusite'},
    'coriza':                {'tipo': 'orl', 'modulo': 'rinossinusite'},
    'rinite':                {'tipo': 'orl', 'modulo': 'rinossinusite'},
    'rinite alergica':       {'tipo': 'orl', 'modulo': 'rinossinusite'},
    'rinite alérgica':       {'tipo': 'orl', 'modulo': 'rinossinusite'},
    'polipose nasal':        {'tipo': 'orl', 'modulo': 'rinossinusite'},
    'polipos nasais':        {'tipo': 'orl', 'modulo': 'rinossinusite'},

    # --- módulos ORL: otalgia (sintoma-guia: dor de ouvido) ---
    'otalgia':               {'tipo': 'orl', 'modulo': 'otalgia'},
    'dor de ouvido':         {'tipo': 'orl', 'modulo': 'otalgia'},
    'dor no ouvido':         {'tipo': 'orl', 'modulo': 'otalgia'},
    'dor ouvido':            {'tipo': 'orl', 'modulo': 'otalgia'},
    'otite':                 {'tipo': 'orl', 'modulo': 'otalgia'},
    'otite media':           {'tipo': 'orl', 'modulo': 'otalgia'},
    'otite média':           {'tipo': 'orl', 'modulo': 'otalgia'},
    'otite externa':         {'tipo': 'orl', 'modulo': 'otalgia'},
    'oma':                   {'tipo': 'orl', 'modulo': 'otalgia'},
    'mastoidite':            {'tipo': 'orl', 'modulo': 'otalgia'},
    'ouvido':                {'tipo': 'orl', 'modulo': 'otalgia'},
    'ouvido entupido':       {'tipo': 'orl', 'modulo': 'otalgia'},
    'zumbido':               {'tipo': 'orl', 'modulo': 'otalgia'},
    'tinnitus':              {'tipo': 'orl', 'modulo': 'otalgia'},

    # --- módulos oftalmo ---
    'olho vermelho':             {'tipo': 'oftalmo', 'modulo': 'olho_vermelho'},
    'olho vermelho agudo':       {'tipo': 'oftalmo', 'modulo': 'olho_vermelho'},
    'conjuntivite':              {'tipo': 'oftalmo', 'modulo': 'olho_vermelho'},
    'conjuntivite alergica':     {'tipo': 'oftalmo', 'modulo': 'olho_vermelho'},
    'conjuntivite alérgica':     {'tipo': 'oftalmo', 'modulo': 'olho_vermelho'},
    'conjuntivite bacteriana':   {'tipo': 'oftalmo', 'modulo': 'olho_vermelho'},
    'conjuntivite viral':        {'tipo': 'oftalmo', 'modulo': 'olho_vermelho'},
    'dor ocular':                {'tipo': 'oftalmo', 'modulo': 'olho_vermelho'},
    'dor no olho':               {'tipo': 'oftalmo', 'modulo': 'olho_vermelho'},
    'dor olho':                  {'tipo': 'oftalmo', 'modulo': 'olho_vermelho'},
    'olho':                      {'tipo': 'oftalmo', 'modulo': 'olho_vermelho'},
    'uveite':                    {'tipo': 'oftalmo', 'modulo': 'olho_vermelho'},
    'uveíte':                    {'tipo': 'oftalmo', 'modulo': 'olho_vermelho'},
    'glaucoma':                  {'tipo': 'oftalmo', 'modulo': 'olho_vermelho'},
    'glaucoma agudo':            {'tipo': 'oftalmo', 'modulo': 'olho_vermelho'},
    'hordeoleo':                 {'tipo': 'oftalmo', 'modulo': 'olho_vermelho'},
    'hordeolo':                  {'tipo': 'oftalmo', 'modulo': 'olho_vermelho'},
    'hordéolo':                  {'tipo': 'oftalmo', 'modulo': 'olho_vermelho'},
    'orzolho':                   {'tipo': 'oftalmo', 'modulo': 'olho_vermelho'},
    'hemorragia subconjuntival': {'tipo': 'oftalmo', 'modulo': 'olho_vermelho'},
    'hemorragia no olho':        {'tipo': 'oftalmo', 'modulo': 'olho_vermelho'},
    'celulite periorbitaria':    {'tipo': 'oftalmo', 'modulo': 'olho_vermelho'},
    'celulite periorbitária':    {'tipo': 'oftalmo', 'modulo': 'olho_vermelho'},
    'ceratite':                  {'tipo': 'oftalmo', 'modulo': 'olho_vermelho'},
    'queratite':                 {'tipo': 'oftalmo', 'modulo': 'olho_vermelho'},
    'ulcera cornea':             {'tipo': 'oftalmo', 'modulo': 'olho_vermelho'},
    'úlcera córnea':             {'tipo': 'oftalmo', 'modulo': 'olho_vermelho'},
    'trauma ocular':             {'tipo': 'oftalmo', 'modulo': 'olho_vermelho'},
    'oftalmo':                   {'tipo': 'oftalmo', 'modulo': 'olho_vermelho'},

    # --- módulos ORL: odinofagia (sintoma-guia: dor de garganta) ---
    'odinofagia':                   {'tipo': 'orl', 'modulo': 'odinofagia'},
    'dor de garganta':              {'tipo': 'orl', 'modulo': 'odinofagia'},
    'garganta':                     {'tipo': 'orl', 'modulo': 'odinofagia'},
    'faringite':                    {'tipo': 'orl', 'modulo': 'odinofagia'},
    'faringoamigdalite':            {'tipo': 'orl', 'modulo': 'odinofagia'},
    'amigdalite':                   {'tipo': 'orl', 'modulo': 'odinofagia'},
    'amigdalas':                    {'tipo': 'orl', 'modulo': 'odinofagia'},
    'amígdalas':                    {'tipo': 'orl', 'modulo': 'odinofagia'},
    'tonsilas':                     {'tipo': 'orl', 'modulo': 'odinofagia'},
    'abscesso amigdaliano':         {'tipo': 'orl', 'modulo': 'odinofagia'},
    'abscesso periamigdaliano':     {'tipo': 'orl', 'modulo': 'odinofagia'},
    'mononucleose':                 {'tipo': 'orl', 'modulo': 'odinofagia'},
    'ebv':                          {'tipo': 'orl', 'modulo': 'odinofagia'},
    'strep':                        {'tipo': 'orl', 'modulo': 'odinofagia'},
    'rouquidao':                    {'tipo': 'orl', 'modulo': 'odinofagia'},
    'rouquidão':                    {'tipo': 'orl', 'modulo': 'odinofagia'},
    'disfonia':                     {'tipo': 'orl', 'modulo': 'odinofagia'},

    # --- módulos febre ---
    'febre':                      {'tipo': 'febre', 'modulo': 'febre'},
    'febre sem foco':             {'tipo': 'febre', 'modulo': 'febre'},
    'febre sem causa':            {'tipo': 'febre', 'modulo': 'febre'},
    'febre de origem obscura':    {'tipo': 'febre', 'modulo': 'febre'},
    'fuo':                        {'tipo': 'febre', 'modulo': 'febre'},
    'febre prolongada':           {'tipo': 'febre', 'modulo': 'febre'},
    'febre aguda':                {'tipo': 'febre', 'modulo': 'febre'},
    'febre alta':                 {'tipo': 'febre', 'modulo': 'febre'},
    'febril':                     {'tipo': 'febre', 'modulo': 'febre'},
    'temperatura alta':           {'tipo': 'febre', 'modulo': 'febre'},

    # --- módulos consciência / ANC ---
    'alteracao de consciencia':      {'tipo': 'consciencia', 'modulo': 'consciencia'},
    'alteração de consciência':      {'tipo': 'consciencia', 'modulo': 'consciencia'},
    'rebaixamento':                  {'tipo': 'consciencia', 'modulo': 'consciencia'},
    'rebaixamento de consciencia':   {'tipo': 'consciencia', 'modulo': 'consciencia'},
    'nao acorda':                    {'tipo': 'consciencia', 'modulo': 'consciencia'},
    'nível de consciencia':          {'tipo': 'consciencia', 'modulo': 'consciencia'},
    'nivel de consciencia':          {'tipo': 'consciencia', 'modulo': 'consciencia'},
    'glasgow':                       {'tipo': 'consciencia', 'modulo': 'consciencia'},
    'coma':                          {'tipo': 'consciencia', 'modulo': 'consciencia'},
    'confusao aguda':                {'tipo': 'consciencia', 'modulo': 'consciencia'},
    'delirium':                      {'tipo': 'consciencia', 'modulo': 'consciencia'},
    'hipoglicemia':                  {'tipo': 'consciencia', 'modulo': 'consciencia'},
    'overdose':                      {'tipo': 'consciencia', 'modulo': 'consciencia'},
    'intoxicacao':                   {'tipo': 'consciencia', 'modulo': 'consciencia'},
    'intoxicação':                   {'tipo': 'consciencia', 'modulo': 'consciencia'},
    'encefalopatia':                 {'tipo': 'consciencia', 'modulo': 'consciencia'},

    # --- módulos linfadenopatia ---
    'linfadenopatia':              {'tipo': 'linfadenopatia', 'modulo': 'linfadenopatia'},
    'linfonodo aumentado':         {'tipo': 'linfadenopatia', 'modulo': 'linfadenopatia'},
    'ganglio aumentado':           {'tipo': 'linfadenopatia', 'modulo': 'linfadenopatia'},
    'ingua':                       {'tipo': 'linfadenopatia', 'modulo': 'linfadenopatia'},
    'inguа':                       {'tipo': 'linfadenopatia', 'modulo': 'linfadenopatia'},
    'nodulo cervical':             {'tipo': 'linfadenopatia', 'modulo': 'linfadenopatia'},
    'nodulo no pescoco':           {'tipo': 'linfadenopatia', 'modulo': 'linfadenopatia'},
    'nodulo no pescoço':           {'tipo': 'linfadenopatia', 'modulo': 'linfadenopatia'},
    'bola no pescoco':             {'tipo': 'linfadenopatia', 'modulo': 'linfadenopatia'},
    'bola no pescoço':             {'tipo': 'linfadenopatia', 'modulo': 'linfadenopatia'},
    'inchaço no pescoco':          {'tipo': 'linfadenopatia', 'modulo': 'linfadenopatia'},
    'adenopatia':                  {'tipo': 'linfadenopatia', 'modulo': 'linfadenopatia'},
    'linfonodo supraclavicular':   {'tipo': 'linfadenopatia', 'modulo': 'linfadenopatia'},
    'mononucleose':                {'tipo': 'linfadenopatia', 'modulo': 'linfadenopatia'},
    'bola na axila':               {'tipo': 'linfadenopatia', 'modulo': 'linfadenopatia'},
    'nodulo axilar':               {'tipo': 'linfadenopatia', 'modulo': 'linfadenopatia'},

    # --- módulos sono / transtornos do sono ---
    'insonia':                       {'tipo': 'sono', 'modulo': 'sono'},
    'insônia':                       {'tipo': 'sono', 'modulo': 'sono'},
    'dificuldade para dormir':       {'tipo': 'sono', 'modulo': 'sono'},
    'nao consigo dormir':            {'tipo': 'sono', 'modulo': 'sono'},
    'nao durmo':                     {'tipo': 'sono', 'modulo': 'sono'},
    'sono':                          {'tipo': 'sono', 'modulo': 'sono'},
    'disturbio do sono':             {'tipo': 'sono', 'modulo': 'sono'},
    'distúrbio do sono':             {'tipo': 'sono', 'modulo': 'sono'},
    'transtorno do sono':            {'tipo': 'sono', 'modulo': 'sono'},
    'apneia':                        {'tipo': 'sono', 'modulo': 'sono'},
    'apneia do sono':                {'tipo': 'sono', 'modulo': 'sono'},
    'aos':                           {'tipo': 'sono', 'modulo': 'sono'},
    'ronco':                         {'tipo': 'sono', 'modulo': 'sono'},
    'ronca muito':                   {'tipo': 'sono', 'modulo': 'sono'},
    'sindrome das pernas inquietas': {'tipo': 'sono', 'modulo': 'sono'},
    'spi':                           {'tipo': 'sono', 'modulo': 'sono'},
    'pernas inquietas':              {'tipo': 'sono', 'modulo': 'sono'},
    'bruxismo':                      {'tipo': 'sono', 'modulo': 'sono'},
    'ranger dentes':                 {'tipo': 'sono', 'modulo': 'sono'},
    'aperta dentes noite':           {'tipo': 'sono', 'modulo': 'sono'},
    'narcolepsia':                   {'tipo': 'sono', 'modulo': 'sono'},
    'sonolencia excessiva':          {'tipo': 'sono', 'modulo': 'sono'},
    'sonolência excessiva':          {'tipo': 'sono', 'modulo': 'sono'},
    'sonambulismo':                  {'tipo': 'sono', 'modulo': 'sono'},
    'pesadelos':                     {'tipo': 'sono', 'modulo': 'sono'},
    'pesadelos recorrentes':         {'tipo': 'sono', 'modulo': 'sono'},
    'fase atrasada do sono':         {'tipo': 'sono', 'modulo': 'sono'},
    'desmame benzo':                 {'tipo': 'sono', 'modulo': 'sono'},
    'dependencia benzo':             {'tipo': 'sono', 'modulo': 'sono'},

    # --- módulos anemia ---
    'anemia':                        {'tipo': 'anemia', 'modulo': 'anemia'},
    'hemograma alterado':            {'tipo': 'anemia', 'modulo': 'anemia'},
    'retorno hemograma':             {'tipo': 'anemia', 'modulo': 'anemia'},
    'interpretar hemograma':         {'tipo': 'anemia', 'modulo': 'anemia'},
    'resultado hemograma':           {'tipo': 'anemia', 'modulo': 'anemia'},
    'anemia ferropriva':             {'tipo': 'anemia', 'modulo': 'anemia'},
    'anemia ferropénica':            {'tipo': 'anemia', 'modulo': 'anemia'},
    'deficiencia de ferro':          {'tipo': 'anemia', 'modulo': 'anemia'},
    'deficiência de ferro':          {'tipo': 'anemia', 'modulo': 'anemia'},
    'deficiencia de b12':            {'tipo': 'anemia', 'modulo': 'anemia'},
    'deficiência de b12':            {'tipo': 'anemia', 'modulo': 'anemia'},
    'anemia megaloblastica':         {'tipo': 'anemia', 'modulo': 'anemia'},
    'anemia megaloblástica':         {'tipo': 'anemia', 'modulo': 'anemia'},
    'anemia hemolitica':             {'tipo': 'anemia', 'modulo': 'anemia'},
    'anemia hemolítica':             {'tipo': 'anemia', 'modulo': 'anemia'},
    'anemia de doenca cronica':      {'tipo': 'anemia', 'modulo': 'anemia'},
    'anemia de doença crônica':      {'tipo': 'anemia', 'modulo': 'anemia'},
    'talassemia':                    {'tipo': 'anemia', 'modulo': 'anemia'},
    'traço talassemico':             {'tipo': 'anemia', 'modulo': 'anemia'},
    'hb baixa':                      {'tipo': 'anemia', 'modulo': 'anemia'},
    'hemoglobina baixa':             {'tipo': 'anemia', 'modulo': 'anemia'},
    'palidez':                       {'tipo': 'anemia', 'modulo': 'anemia'},

    # --- módulos gota ---
    'gota':                       {'tipo': 'gota', 'modulo': 'gota'},
    'artrite por cristais':       {'tipo': 'gota', 'modulo': 'gota'},
    'ataque de gota':             {'tipo': 'gota', 'modulo': 'gota'},
    'crise de gota':              {'tipo': 'gota', 'modulo': 'gota'},
    'podagra':                    {'tipo': 'gota', 'modulo': 'gota'},
    'hiperuricemia':              {'tipo': 'gota', 'modulo': 'gota'},
    'acido urico alto':           {'tipo': 'gota', 'modulo': 'gota'},
    'ácido úrico alto':           {'tipo': 'gota', 'modulo': 'gota'},
    'artrite gotosa':             {'tipo': 'gota', 'modulo': 'gota'},
    'tophi':                      {'tipo': 'gota', 'modulo': 'gota'},
    'tofo':                       {'tipo': 'gota', 'modulo': 'gota'},

    # --- módulos asma ---
    'asma':                  {'tipo': 'asma', 'modulo': 'asma'},
    'crise de asma':         {'tipo': 'asma', 'modulo': 'asma'},
    'crise asmatica':        {'tipo': 'asma', 'modulo': 'asma'},
    'crise asmática':        {'tipo': 'asma', 'modulo': 'asma'},
    'broncoespasmo':         {'tipo': 'asma', 'modulo': 'asma'},
    'chiado':                {'tipo': 'asma', 'modulo': 'asma'},
    'chieira':               {'tipo': 'asma', 'modulo': 'asma'},
    'sibilos':               {'tipo': 'asma', 'modulo': 'asma'},
    'retorno asma':          {'tipo': 'asma', 'modulo': 'asma'},
    'controle asma':         {'tipo': 'asma', 'modulo': 'asma'},
    'acompanhamento asma':   {'tipo': 'asma', 'modulo': 'asma'},

    # --- módulos dpoc ---
    'dpoc':                  {'tipo': 'dpoc', 'modulo': 'dpoc'},
    'epoc':                  {'tipo': 'dpoc', 'modulo': 'dpoc'},
    'enfisema':              {'tipo': 'dpoc', 'modulo': 'dpoc'},
    'bronquite cronica':     {'tipo': 'dpoc', 'modulo': 'dpoc'},
    'bronquite crônica':     {'tipo': 'dpoc', 'modulo': 'dpoc'},
    'crise de dpoc':         {'tipo': 'dpoc', 'modulo': 'dpoc'},
    'exacerbacao dpoc':      {'tipo': 'dpoc', 'modulo': 'dpoc'},
    'exacerbação dpoc':      {'tipo': 'dpoc', 'modulo': 'dpoc'},
    'retorno dpoc':          {'tipo': 'dpoc', 'modulo': 'dpoc'},
    'controle dpoc':         {'tipo': 'dpoc', 'modulo': 'dpoc'},

    # --- módulos síncope ---
    'sincope':               {'tipo': 'sincope', 'modulo': 'sincope'},
    'síncope':               {'tipo': 'sincope', 'modulo': 'sincope'},
    'desmaio':               {'tipo': 'sincope', 'modulo': 'sincope'},
    'perda de consciencia':  {'tipo': 'sincope', 'modulo': 'sincope'},
    'perda de consciência':  {'tipo': 'sincope', 'modulo': 'sincope'},
    'apagou':                {'tipo': 'sincope', 'modulo': 'sincope'},
    'pre sincope':           {'tipo': 'sincope', 'modulo': 'sincope'},
    'pre-sincope':           {'tipo': 'sincope', 'modulo': 'sincope'},
    'pré-síncope':           {'tipo': 'sincope', 'modulo': 'sincope'},
    'hipotensao ortostatica':{'tipo': 'sincope', 'modulo': 'sincope'},
    'hipotensão ortostática':{'tipo': 'sincope', 'modulo': 'sincope'},

    # --- módulos anorretal ---
    'sangramento anorretal': {'tipo': 'anorretal', 'modulo': 'anorretal'},
    'sangramento retal':     {'tipo': 'anorretal', 'modulo': 'anorretal'},
    'sangue no banheiro':    {'tipo': 'anorretal', 'modulo': 'anorretal'},
    'hemorroida':            {'tipo': 'anorretal', 'modulo': 'anorretal'},
    'hemorróida':            {'tipo': 'anorretal', 'modulo': 'anorretal'},
    'fissura anal':          {'tipo': 'anorretal', 'modulo': 'anorretal'},
    'prurido anal':          {'tipo': 'anorretal', 'modulo': 'anorretal'},
    'coceira no anus':       {'tipo': 'anorretal', 'modulo': 'anorretal'},
    'coceira no ânus':       {'tipo': 'anorretal', 'modulo': 'anorretal'},
    'dor ao defecar':        {'tipo': 'anorretal', 'modulo': 'anorretal'},
    'prolapso retal':        {'tipo': 'anorretal', 'modulo': 'anorretal'},
    'hemorroida trombosada': {'tipo': 'anorretal', 'modulo': 'anorretal'},

    # --- módulos edema ---
    'edema':                 {'tipo': 'edema', 'modulo': 'edema'},
    'edema de mmii':         {'tipo': 'edema', 'modulo': 'edema'},
    'perna inchada':         {'tipo': 'edema', 'modulo': 'edema'},
    'inchaço nas pernas':    {'tipo': 'edema', 'modulo': 'edema'},
    'tornozelo inchado':     {'tipo': 'edema', 'modulo': 'edema'},
    'tvp':                   {'tipo': 'edema', 'modulo': 'edema'},
    'trombose':              {'tipo': 'edema', 'modulo': 'edema'},
    'insuficiencia venosa':  {'tipo': 'edema', 'modulo': 'edema'},
    'linfedema':             {'tipo': 'edema', 'modulo': 'edema'},

    # --- módulos icterícia ---
    'ictericia':             {'tipo': 'ictericia', 'modulo': 'ictericia'},
    'icterícia':             {'tipo': 'ictericia', 'modulo': 'ictericia'},
    'pele amarela':          {'tipo': 'ictericia', 'modulo': 'ictericia'},
    'olhos amarelos':        {'tipo': 'ictericia', 'modulo': 'ictericia'},
    'amarelao':              {'tipo': 'ictericia', 'modulo': 'ictericia'},
    'amarelão':              {'tipo': 'ictericia', 'modulo': 'ictericia'},
    'hepatite':              {'tipo': 'ictericia', 'modulo': 'ictericia'},
    'colangite':             {'tipo': 'ictericia', 'modulo': 'ictericia'},
    'bilirrubina alta':      {'tipo': 'ictericia', 'modulo': 'ictericia'},
    'gilbert':               {'tipo': 'ictericia', 'modulo': 'ictericia'},

    # --- módulos arboviroses ---
    'dengue':                {'tipo': 'organico', 'modulo': 'arboviroses'},
    'febre dengue':          {'tipo': 'organico', 'modulo': 'arboviroses'},
    'chikungunya':           {'tipo': 'organico', 'modulo': 'arboviroses'},
    'zika':                  {'tipo': 'organico', 'modulo': 'arboviroses'},
    'arbovirose':            {'tipo': 'organico', 'modulo': 'arboviroses'},
    'arboviroses':           {'tipo': 'organico', 'modulo': 'arboviroses'},
    'febre exantematica':    {'tipo': 'organico', 'modulo': 'arboviroses'},
    'sindrome febril aguda': {'tipo': 'organico', 'modulo': 'arboviroses'},

    # --- módulos MSK ---
    'dor no joelho': {'tipo': 'msk', 'modulo': 'joelho'},
    'joelho':        {'tipo': 'msk', 'modulo': 'joelho'},
    'dor no ombro':  {'tipo': 'msk', 'modulo': 'ombro'},
    'ombro':         {'tipo': 'msk', 'modulo': 'ombro'},

    # futuros — descomentar quando prontos:
    # 'dor no quadril':   {'tipo': 'msk', 'modulo': 'quadril'},
    # 'dor no tornozelo': {'tipo': 'msk', 'modulo': 'tornozelo_pe'},
    'lombalgia':        {'tipo': 'msk', 'modulo': 'coluna'},
    'dor nas costas':   {'tipo': 'msk', 'modulo': 'coluna'},

    'fibromialgia':       {'tipo': 'msk', 'modulo': 'fibromialgia'},
    'dor difusa':         {'tipo': 'msk', 'modulo': 'fibromialgia'},
    'dor cronica':        {'tipo': 'msk', 'modulo': 'fibromialgia'},
    'dor no corpo todo':  {'tipo': 'msk', 'modulo': 'fibromialgia'},

    'dor no quadril':     {'tipo': 'msk', 'modulo': 'quadril'},
    'quadril':            {'tipo': 'msk', 'modulo': 'quadril'},
    'dor quadril':        {'tipo': 'msk', 'modulo': 'quadril'},

    'mao':                {'tipo': 'msk', 'modulo': 'mao_punho'},
    'punho':              {'tipo': 'msk', 'modulo': 'mao_punho'},
    'dor na mao':         {'tipo': 'msk', 'modulo': 'mao_punho'},
    'dor no punho':       {'tipo': 'msk', 'modulo': 'mao_punho'},
    'dor no dedo':        {'tipo': 'msk', 'modulo': 'mao_punho'},
    'tunel do carpo':     {'tipo': 'msk', 'modulo': 'mao_punho'},
    'dedo em gatilho':    {'tipo': 'msk', 'modulo': 'mao_punho'},
    'de quervain':        {'tipo': 'msk', 'modulo': 'mao_punho'},

    'tornozelo':          {'tipo': 'msk', 'modulo': 'tornozelo_pe'},
    'dor no tornozelo':   {'tipo': 'msk', 'modulo': 'tornozelo_pe'},
    'entorse':            {'tipo': 'msk', 'modulo': 'tornozelo_pe'},
    'entorse de tornozelo': {'tipo': 'msk', 'modulo': 'tornozelo_pe'},
    'dor no pe':          {'tipo': 'msk', 'modulo': 'tornozelo_pe'},
    'dor no pé':          {'tipo': 'msk', 'modulo': 'tornozelo_pe'},
    'pe':                 {'tipo': 'msk', 'modulo': 'tornozelo_pe'},
    'fasciite plantar':   {'tipo': 'msk', 'modulo': 'tornozelo_pe'},

    # --- módulos gastro / abdominal ---
    'dor abdominal':            {'tipo': 'organico', 'modulo': 'gastro'},
    'dor no abdome':            {'tipo': 'organico', 'modulo': 'gastro'},
    'dor de barriga':           {'tipo': 'organico', 'modulo': 'gastro'},
    'abdome':                   {'tipo': 'organico', 'modulo': 'gastro'},
    'gastro':                   {'tipo': 'organico', 'modulo': 'gastro'},
    'gastroabdominal':          {'tipo': 'organico', 'modulo': 'gastro'},
    'colica':                   {'tipo': 'organico', 'modulo': 'gastro'},
    'cólica':                   {'tipo': 'organico', 'modulo': 'gastro'},
    'azia':                     {'tipo': 'organico', 'modulo': 'gastro'},
    'queimacao':                {'tipo': 'organico', 'modulo': 'gastro'},
    'queimação':                {'tipo': 'organico', 'modulo': 'gastro'},
    'dispepsia':                {'tipo': 'organico', 'modulo': 'gastro'},
    'gastrite':                 {'tipo': 'organico', 'modulo': 'gastro'},
    'ulcera':                   {'tipo': 'organico', 'modulo': 'gastro'},
    'úlcera':                   {'tipo': 'organico', 'modulo': 'gastro'},
    'h pylori':                 {'tipo': 'organico', 'modulo': 'gastro'},
    'helicobacter':             {'tipo': 'organico', 'modulo': 'gastro'},
    'sii':                      {'tipo': 'organico', 'modulo': 'gastro'},
    'intestino irritavel':      {'tipo': 'organico', 'modulo': 'gastro'},
    'intestino irritável':      {'tipo': 'organico', 'modulo': 'gastro'},
    'constipacao':              {'tipo': 'organico', 'modulo': 'gastro'},
    'constipação':              {'tipo': 'organico', 'modulo': 'gastro'},
    'prisao de ventre':         {'tipo': 'organico', 'modulo': 'gastro'},
    'prisão de ventre':         {'tipo': 'organico', 'modulo': 'gastro'},
    'colica biliar':            {'tipo': 'organico', 'modulo': 'gastro'},
    'cólica biliar':            {'tipo': 'organico', 'modulo': 'gastro'},
    'vesícula':                 {'tipo': 'organico', 'modulo': 'gastro'},
    'vesicula':                 {'tipo': 'organico', 'modulo': 'gastro'},
    'diverticulite':            {'tipo': 'organico', 'modulo': 'gastro'},
    'dip':                      {'tipo': 'organico', 'modulo': 'gastro'},
    'nausea':                   {'tipo': 'organico', 'modulo': 'gastro'},
    'náusea':                   {'tipo': 'organico', 'modulo': 'gastro'},
    'vomito':                   {'tipo': 'organico', 'modulo': 'gastro'},
    'vômito':                   {'tipo': 'organico', 'modulo': 'gastro'},
    'parasitose':               {'tipo': 'organico', 'modulo': 'gastro'},
    'vermes':                   {'tipo': 'organico', 'modulo': 'gastro'},
    'giardia':                  {'tipo': 'organico', 'modulo': 'gastro'},
    'giardíase':                {'tipo': 'organico', 'modulo': 'gastro'},

    # --- módulos palpitação ---
    'palpitacao':               {'tipo': 'palpitacao', 'modulo': 'palpitacao'},
    'palpitação':               {'tipo': 'palpitacao', 'modulo': 'palpitacao'},
    'coracao acelerado':        {'tipo': 'palpitacao', 'modulo': 'palpitacao'},
    'coração acelerado':        {'tipo': 'palpitacao', 'modulo': 'palpitacao'},
    'taquicardia':              {'tipo': 'palpitacao', 'modulo': 'palpitacao'},
    'arritmia':                 {'tipo': 'palpitacao', 'modulo': 'palpitacao'},
    'fibrilacao atrial':        {'tipo': 'palpitacao', 'modulo': 'palpitacao'},
    'fibrilação atrial':        {'tipo': 'palpitacao', 'modulo': 'palpitacao'},
    'fa':                       {'tipo': 'palpitacao', 'modulo': 'palpitacao'},
    'flutter atrial':           {'tipo': 'palpitacao', 'modulo': 'palpitacao'},
    'flutter':                  {'tipo': 'palpitacao', 'modulo': 'palpitacao'},
    'extrassistolia':           {'tipo': 'palpitacao', 'modulo': 'palpitacao'},
    'extrassistoles':           {'tipo': 'palpitacao', 'modulo': 'palpitacao'},
    'extrassístoles':           {'tipo': 'palpitacao', 'modulo': 'palpitacao'},
    'batida extra':             {'tipo': 'palpitacao', 'modulo': 'palpitacao'},
    'batimento extra':          {'tipo': 'palpitacao', 'modulo': 'palpitacao'},
    'tsv':                      {'tipo': 'palpitacao', 'modulo': 'palpitacao'},
    'taquicardia supraventricular': {'tipo': 'palpitacao', 'modulo': 'palpitacao'},
    'wpw':                      {'tipo': 'palpitacao', 'modulo': 'palpitacao'},
    'wolff parkinson white':    {'tipo': 'palpitacao', 'modulo': 'palpitacao'},
    'pre-excitacao':            {'tipo': 'palpitacao', 'modulo': 'palpitacao'},
    'coracao irregular':        {'tipo': 'palpitacao', 'modulo': 'palpitacao'},
    'coração irregular':        {'tipo': 'palpitacao', 'modulo': 'palpitacao'},
    'coracao disparado':        {'tipo': 'palpitacao', 'modulo': 'palpitacao'},
    'coração disparado':        {'tipo': 'palpitacao', 'modulo': 'palpitacao'},

    # --- módulos hemorragia digestiva ---
    'hematêmese':                {'tipo': 'hemorragia', 'modulo': 'hemorragia'},
    'hematemese':                {'tipo': 'hemorragia', 'modulo': 'hemorragia'},
    'vomito com sangue':         {'tipo': 'hemorragia', 'modulo': 'hemorragia'},
    'vômito com sangue':         {'tipo': 'hemorragia', 'modulo': 'hemorragia'},
    'vomitou sangue':            {'tipo': 'hemorragia', 'modulo': 'hemorragia'},
    'melena':                    {'tipo': 'hemorragia', 'modulo': 'hemorragia'},
    'fezes pretas':              {'tipo': 'hemorragia', 'modulo': 'hemorragia'},
    'fezes escuras':             {'tipo': 'hemorragia', 'modulo': 'hemorragia'},
    'borra de cafe':             {'tipo': 'hemorragia', 'modulo': 'hemorragia'},
    'borra de café':             {'tipo': 'hemorragia', 'modulo': 'hemorragia'},
    'hematoquezia':              {'tipo': 'hemorragia', 'modulo': 'hemorragia'},
    'sangue nas fezes':          {'tipo': 'hemorragia', 'modulo': 'hemorragia'},
    'sangramento retal':         {'tipo': 'hemorragia', 'modulo': 'hemorragia'},
    'sangue no vaso':            {'tipo': 'hemorragia', 'modulo': 'hemorragia'},
    'sangue ao evacuar':         {'tipo': 'hemorragia', 'modulo': 'hemorragia'},
    'hemorragia digestiva':      {'tipo': 'hemorragia', 'modulo': 'hemorragia'},
    'hda':                       {'tipo': 'hemorragia', 'modulo': 'hemorragia'},
    'hdb':                       {'tipo': 'hemorragia', 'modulo': 'hemorragia'},
    'hemorragia alta':           {'tipo': 'hemorragia', 'modulo': 'hemorragia'},
    'hemorragia baixa':          {'tipo': 'hemorragia', 'modulo': 'hemorragia'},
    'sangramento digestivo':     {'tipo': 'hemorragia', 'modulo': 'hemorragia'},
    'varizes esofagicas':        {'tipo': 'hemorragia', 'modulo': 'hemorragia'},
    'varizes esofágicas':        {'tipo': 'hemorragia', 'modulo': 'hemorragia'},
    'cirrose sangrando':         {'tipo': 'hemorragia', 'modulo': 'hemorragia'},
    'ulcera sangrando':          {'tipo': 'hemorragia', 'modulo': 'hemorragia'},
    'hemorroida sangrando':      {'tipo': 'hemorragia', 'modulo': 'hemorragia'},
    'fissura anal':              {'tipo': 'hemorragia', 'modulo': 'hemorragia'},
    'sangue no papel higienico': {'tipo': 'hemorragia', 'modulo': 'hemorragia'},

    # --- módulos celulite / erisipela ---
    'celulite':                  {'tipo': 'celulite', 'modulo': 'celulite'},
    'erisipela':                 {'tipo': 'celulite', 'modulo': 'celulite'},
    'infeccao de pele':          {'tipo': 'celulite', 'modulo': 'celulite'},
    'infecção de pele':          {'tipo': 'celulite', 'modulo': 'celulite'},
    'pele inflamada':            {'tipo': 'celulite', 'modulo': 'celulite'},
    'pele vermelha':             {'tipo': 'celulite', 'modulo': 'celulite'},
    'perna vermelha':            {'tipo': 'celulite', 'modulo': 'celulite'},
    'vermelhidao na perna':      {'tipo': 'celulite', 'modulo': 'celulite'},
    'vermelhidão na perna':      {'tipo': 'celulite', 'modulo': 'celulite'},
    'mancha vermelha crescendo': {'tipo': 'celulite', 'modulo': 'celulite'},
    'pele quente':               {'tipo': 'celulite', 'modulo': 'celulite'},
    'bolha na pele':             {'tipo': 'celulite', 'modulo': 'celulite'},
    'infeccao no pe':            {'tipo': 'celulite', 'modulo': 'celulite'},
    'infecção no pé':            {'tipo': 'celulite', 'modulo': 'celulite'},
    'pe diabetico infectado':    {'tipo': 'celulite', 'modulo': 'celulite'},
    'pé diabético infectado':    {'tipo': 'celulite', 'modulo': 'celulite'},
    'linfangite':                {'tipo': 'celulite', 'modulo': 'celulite'},
    'estria vermelha':           {'tipo': 'celulite', 'modulo': 'celulite'},
    'fasciite':                  {'tipo': 'celulite', 'modulo': 'celulite'},
    'fasciite necrotizante':     {'tipo': 'celulite', 'modulo': 'celulite'},
    'necrotizante':              {'tipo': 'celulite', 'modulo': 'celulite'},
    'abscesso':                  {'tipo': 'celulite', 'modulo': 'celulite'},
    'furuncolo':                 {'tipo': 'celulite', 'modulo': 'celulite'},
    'furúnculo':                 {'tipo': 'celulite', 'modulo': 'celulite'},
    'antraz':                    {'tipo': 'celulite', 'modulo': 'celulite'},
    'inchaço inflamado':         {'tipo': 'celulite', 'modulo': 'celulite'},

    # --- módulos urinários ---
    'disuria':                  {'tipo': 'organico', 'modulo': 'urinario'},
    'disuría':                  {'tipo': 'organico', 'modulo': 'urinario'},
    'ardencia ao urinar':       {'tipo': 'organico', 'modulo': 'urinario'},
    'itu':                      {'tipo': 'organico', 'modulo': 'urinario'},
    'infeccao urinaria':        {'tipo': 'organico', 'modulo': 'urinario'},
    'infecção urinaria':        {'tipo': 'organico', 'modulo': 'urinario'},
    'infecção urinária':        {'tipo': 'organico', 'modulo': 'urinario'},
    'cistite':                  {'tipo': 'organico', 'modulo': 'urinario'},
    'pielonefrite':             {'tipo': 'organico', 'modulo': 'urinario'},
    'hematuria':                {'tipo': 'organico', 'modulo': 'urinario'},
    'hematúria':                {'tipo': 'organico', 'modulo': 'urinario'},
    'sangue na urina':          {'tipo': 'organico', 'modulo': 'urinario'},
    'urina com sangue':         {'tipo': 'organico', 'modulo': 'urinario'},
    'queixa urinaria':          {'tipo': 'organico', 'modulo': 'urinario'},
    'queixa urinária':          {'tipo': 'organico', 'modulo': 'urinario'},
    'urinario':                 {'tipo': 'organico', 'modulo': 'urinario'},
    'urinário':                 {'tipo': 'organico', 'modulo': 'urinario'},
    'prostatite':               {'tipo': 'organico', 'modulo': 'urinario'},
    'uretrite':                 {'tipo': 'organico', 'modulo': 'urinario'},
    'corrimento uretral':       {'tipo': 'organico', 'modulo': 'urinario'},
    'frequencia urinaria':      {'tipo': 'organico', 'modulo': 'urinario'},
    'frequência urinária':      {'tipo': 'organico', 'modulo': 'urinario'},
    'polaciuria':               {'tipo': 'organico', 'modulo': 'urinario'},
    'polaciúria':               {'tipo': 'organico', 'modulo': 'urinario'},
    'sintomas urinarios':       {'tipo': 'organico', 'modulo': 'urinario'},
    'sintomas urinários':       {'tipo': 'organico', 'modulo': 'urinario'},
}


def _rodar_palpitacao(modulo_nome, admissao, paciente):
    """Módulo Palpitação — subjetivo + engine + runner."""

    if modulo_nome == 'palpitacao':
        from modules.sintomas.palpitacao.subjetivo import coletar_subjetivo_palpitacao
        from modules.raciocinio.palpitacao.runner_palpitacao import rodar

        try:
            dados_iniciais = {'idade': int(paciente.get('idade', 0))}
        except (ValueError, TypeError):
            dados_iniciais = {}

        dados, arquivo_subj = coletar_subjetivo_palpitacao(dados_iniciais or None)
        resultado = rodar(arquivo_subj)
        with open(arquivo_subj, encoding='utf-8') as f:
            admissao['dados_organico'] = json.load(f)
        admissao['modulo_organico'] = 'palpitacao'
        return resultado

    print(f'\n  Módulo Palpitação "{modulo_nome}" ainda não implementado.')
    return None


def _rodar_msk(modulo_nome, admissao, paciente):
    """Importação lazy dos módulos MSK. Salva dados_msk no admissao para o texto.py."""

    if modulo_nome == 'joelho':
        from modules.sintomas.musculoesqueletico.joelho.subjetivo import coletar_subjetivo_joelho
        from modules.sintomas.musculoesqueletico.joelho.objetivo import coletar_objetivo_joelho
        from modules.raciocinio.musculoesqueletico.joelho.core.runner import rodar

        _, arquivo_subj = coletar_subjetivo_joelho()
        _, arquivo_obj  = coletar_objetivo_joelho(arquivo_subj)
        resultado = rodar(arquivo_obj)
        with open(arquivo_obj, encoding='utf-8') as f:
            admissao['dados_msk'] = json.load(f)
        admissao['modulo_msk'] = 'joelho'
        return resultado

    if modulo_nome == 'ombro':
        from modules.sintomas.musculoesqueletico.ombro.subjetivo import coletar_subjetivo_ombro
        from modules.sintomas.musculoesqueletico.ombro.objetivo import coletar_objetivo_ombro
        from modules.raciocinio.musculoesqueletico.ombro.core.runner import rodar

        _, arquivo_subj = coletar_subjetivo_ombro()
        _, arquivo_obj  = coletar_objetivo_ombro(arquivo_subj)
        resultado = rodar(arquivo_obj)
        with open(arquivo_obj, encoding='utf-8') as f:
            admissao['dados_msk'] = json.load(f)
        admissao['modulo_msk'] = 'ombro'
        return resultado

    if modulo_nome == 'coluna':
        from modules.sintomas.musculoesqueletico.coluna.subjetivo import coletar_subjetivo_coluna
        from modules.sintomas.musculoesqueletico.coluna.objetivo import coletar_objetivo_coluna
        from modules.raciocinio.musculoesqueletico.coluna.core.runner import rodar

        try:
            idade_inicial = {'idade': int(paciente.get('idade', 0))}
        except (ValueError, TypeError):
            idade_inicial = {}

        _, arquivo_subj = coletar_subjetivo_coluna(idade_inicial)
        dados, arquivo_obj = coletar_objetivo_coluna(arquivo_subj)
        resultado = rodar(arquivo_obj)
        with open(arquivo_obj, encoding='utf-8') as f:
            admissao['dados_msk'] = json.load(f)
        admissao['modulo_msk'] = 'coluna'
        return resultado

    if modulo_nome == 'fibromialgia':
        from modules.sintomas.musculoesqueletico.fibromialgia.subjetivo import coletar_subjetivo_fibromialgia
        from modules.raciocinio.musculoesqueletico.fibromialgia.core.runner import rodar

        try:
            idade_inicial = {'idade': int(paciente.get('idade', 0))}
        except (ValueError, TypeError):
            idade_inicial = {}

        _, arquivo_subj = coletar_subjetivo_fibromialgia(idade_inicial)
        resultado = rodar(arquivo_subj)
        with open(arquivo_subj, encoding='utf-8') as f:
            admissao['dados_msk'] = json.load(f)
        admissao['modulo_msk'] = 'fibromialgia'
        return resultado

    if modulo_nome == 'quadril':
        from modules.sintomas.musculoesqueletico.quadril.subjetivo import coletar_subjetivo_quadril
        from modules.sintomas.musculoesqueletico.quadril.objetivo import coletar_objetivo_quadril
        from modules.raciocinio.musculoesqueletico.quadril.core.runner import rodar

        try:
            idade_inicial = {'idade': int(paciente.get('idade', 0))}
        except (ValueError, TypeError):
            idade_inicial = {}

        _, arquivo_subj = coletar_subjetivo_quadril(idade_inicial)
        dados, arquivo_obj = coletar_objetivo_quadril(arquivo_subj)
        resultado = rodar(arquivo_obj)
        with open(arquivo_obj, encoding='utf-8') as f:
            admissao['dados_msk'] = json.load(f)
        admissao['modulo_msk'] = 'quadril'
        return resultado

    if modulo_nome == 'mao_punho':
        from modules.sintomas.musculoesqueletico.mao_punho.subjetivo import coletar_subjetivo_mao_punho
        from modules.sintomas.musculoesqueletico.mao_punho.objetivo import coletar_objetivo_mao_punho
        from modules.raciocinio.musculoesqueletico.mao_punho.core.runner import rodar

        try:
            idade_inicial = {'idade': int(paciente.get('idade', 0))}
        except (ValueError, TypeError):
            idade_inicial = {}

        _, arquivo_subj = coletar_subjetivo_mao_punho(idade_inicial)
        _, arquivo_obj  = coletar_objetivo_mao_punho(arquivo_subj)
        resultado = rodar(arquivo_obj)
        with open(arquivo_obj, encoding='utf-8') as f:
            admissao['dados_msk'] = json.load(f)
        admissao['modulo_msk'] = 'mao_punho'
        return resultado

    if modulo_nome == 'tornozelo_pe':
        from modules.sintomas.musculoesqueletico.tornozelo_pe.subjetivo import coletar_subjetivo_tornozelo_pe
        from modules.sintomas.musculoesqueletico.tornozelo_pe.objetivo import coletar_objetivo_tornozelo_pe
        from modules.raciocinio.musculoesqueletico.tornozelo_pe.core.runner import rodar

        try:
            idade_inicial = {'idade': int(paciente.get('idade', 0))}
        except (ValueError, TypeError):
            idade_inicial = {}

        _, arquivo_subj = coletar_subjetivo_tornozelo_pe(idade_inicial)
        _, arquivo_obj  = coletar_objetivo_tornozelo_pe(arquivo_subj)
        resultado = rodar(arquivo_obj)
        with open(arquivo_obj, encoding='utf-8') as f:
            admissao['dados_msk'] = json.load(f)
        admissao['modulo_msk'] = 'tornozelo_pe'
        return resultado

    print(f'\n  Módulo "{modulo_nome}" ainda não implementado.')
    return None


def _rodar_organico(modulo_nome, admissao, paciente):
    """Módulos orgânicos: apenas subjetivo + runner (sem objetivo.py dedicado)."""

    if modulo_nome == 'tosse':
        from modules.sintomas.tosse.subjetivo import coletar_subjetivo_tosse
        from modules.raciocinio.tosse.runner import rodar

        try:
            idade_inicial = {'idade': int(paciente.get('idade', 0))}
        except (ValueError, TypeError):
            idade_inicial = {}

        dados, arquivo_subj = coletar_subjetivo_tosse(idade_inicial)
        resultado = rodar(arquivo_subj)
        with open(arquivo_subj, encoding='utf-8') as f:
            admissao['dados_organico'] = json.load(f)
        admissao['modulo_organico'] = 'tosse'
        return resultado

    if modulo_nome == 'fadiga':
        from modules.sintomas.fadiga.subjetivo import coletar_subjetivo_fadiga
        from modules.raciocinio.fadiga.runner import rodar

        try:
            idade_inicial = {'idade': int(paciente.get('idade', 0))}
        except (ValueError, TypeError):
            idade_inicial = {}

        dados, arquivo_subj = coletar_subjetivo_fadiga(idade_inicial)
        resultado = rodar(arquivo_subj)
        with open(arquivo_subj, encoding='utf-8') as f:
            admissao['dados_organico'] = json.load(f)
        admissao['modulo_organico'] = 'fadiga'
        return resultado

    if modulo_nome == 'diarreia':
        from modules.sintomas.diarreia.subjetivo import coletar_subjetivo_diarreia
        from modules.raciocinio.diarreia.runner import rodar

        try:
            idade_inicial = {'idade': int(paciente.get('idade', 0))}
        except (ValueError, TypeError):
            idade_inicial = {}

        dados, arquivo_subj = coletar_subjetivo_diarreia(idade_inicial)
        resultado = rodar(arquivo_subj)
        with open(arquivo_subj, encoding='utf-8') as f:
            admissao['dados_organico'] = json.load(f)
        admissao['modulo_organico'] = 'diarreia'
        return resultado

    if modulo_nome == 'ivas':
        from modules.sintomas.ivas.subjetivo import coletar_subjetivo_ivas
        from modules.raciocinio.ivas.runner import rodar

        try:
            dados_iniciais = {'idade': int(paciente.get('idade', 0))}
        except (ValueError, TypeError):
            dados_iniciais = {}

        dados, arquivo_subj = coletar_subjetivo_ivas(dados_iniciais or None)
        resultado = rodar(arquivo_subj)
        with open(arquivo_subj, encoding='utf-8') as f:
            admissao['dados_organico'] = json.load(f)
        admissao['modulo_organico'] = 'ivas'
        return resultado

    if modulo_nome == 'arboviroses':
        from modules.sintomas.arboviroses.subjetivo import coletar_subjetivo_arboviroses
        from modules.raciocinio.arboviroses.runner import rodar

        try:
            dados_iniciais = {'peso_kg': float(paciente.get('peso', 0) or 0)}
        except (ValueError, TypeError):
            dados_iniciais = {}

        dados, arquivo_subj = coletar_subjetivo_arboviroses(dados_iniciais or None)
        resultado = rodar(arquivo_subj)
        with open(arquivo_subj, encoding='utf-8') as f:
            admissao['dados_organico'] = json.load(f)
        admissao['modulo_organico'] = 'arboviroses'
        return resultado

    if modulo_nome == 'gastro':
        from modules.sintomas.abdominal.gastro_subjetivo import coletar_subjetivo_abdominal
        from modules.raciocinio.gastro.runner import rodar

        try:
            dados_iniciais = {'idade': int(paciente.get('idade', 0))}
        except (ValueError, TypeError):
            dados_iniciais = {}

        dados, arquivo_subj = coletar_subjetivo_abdominal(dados_iniciais or None)
        resultado = rodar(arquivo_subj)
        with open(arquivo_subj, encoding='utf-8') as f:
            admissao['dados_organico'] = json.load(f)
        admissao['modulo_organico'] = 'gastro'
        return resultado

    if modulo_nome == 'urinario':
        from modules.sintomas.urinario.subjetivo import coletar_subjetivo_urinario
        from modules.raciocinio.urinario.runner import rodar

        try:
            dados_iniciais = {'idade': int(paciente.get('idade', 0))}
        except (ValueError, TypeError):
            dados_iniciais = {}

        dados, arquivo_subj = coletar_subjetivo_urinario(dados_iniciais or None)
        resultado = rodar(arquivo_subj)
        with open(arquivo_subj, encoding='utf-8') as f:
            admissao['dados_organico'] = json.load(f)
        admissao['modulo_organico'] = 'urinario'
        return resultado

    print(f'\n  Módulo orgânico "{modulo_nome}" ainda não implementado.')
    return None


def _rodar_orl(modulo_nome, admissao, paciente):
    """Módulos ORL — padrão sintoma-guia (subjetivo + engine + runner)."""

    if modulo_nome == 'odinofagia':
        from modules.sintomas.orl.odinofagia_subjetivo import coletar_subjetivo_odinofagia
        from modules.raciocinio.orl.runner_odinofagia import rodar

        try:
            dados_iniciais = {'idade': int(paciente.get('idade', 0))}
        except (ValueError, TypeError):
            dados_iniciais = {}

        dados, arquivo_subj = coletar_subjetivo_odinofagia(dados_iniciais or None)
        resultado = rodar(arquivo_subj)
        with open(arquivo_subj, encoding='utf-8') as f:
            admissao['dados_organico'] = json.load(f)
        admissao['modulo_organico'] = 'odinofagia'
        return resultado

    if modulo_nome == 'otalgia':
        from modules.sintomas.orl.otalgia_subjetivo import coletar_subjetivo_otalgia
        from modules.raciocinio.orl.runner_otalgia import rodar

        try:
            dados_iniciais = {'idade': int(paciente.get('idade', 0))}
        except (ValueError, TypeError):
            dados_iniciais = {}

        dados, arquivo_subj = coletar_subjetivo_otalgia(dados_iniciais or None)
        resultado = rodar(arquivo_subj)
        with open(arquivo_subj, encoding='utf-8') as f:
            admissao['dados_organico'] = json.load(f)
        admissao['modulo_organico'] = 'otalgia'
        return resultado

    if modulo_nome == 'rinossinusite':
        from modules.sintomas.orl.rinossinusite_subjetivo import coletar_subjetivo_rinossinusite
        from modules.raciocinio.orl.runner_rinossinusite import rodar

        try:
            dados_iniciais = {'idade': int(paciente.get('idade', 0))}
        except (ValueError, TypeError):
            dados_iniciais = {}

        dados, arquivo_subj = coletar_subjetivo_rinossinusite(dados_iniciais or None)
        resultado = rodar(arquivo_subj)
        with open(arquivo_subj, encoding='utf-8') as f:
            admissao['dados_organico'] = json.load(f)
        admissao['modulo_organico'] = 'rinossinusite'
        return resultado

    print(f'\n  Módulo ORL "{modulo_nome}" ainda não implementado.')
    return None


def _rodar_oftalmo(modulo_nome, admissao, paciente):
    """Módulos Oftalmo — padrão sintoma-guia (subjetivo + engine + runner)."""

    if modulo_nome == 'olho_vermelho':
        from modules.sintomas.oftalmo.olho_vermelho_subjetivo import coletar_subjetivo_olho_vermelho
        from modules.raciocinio.oftalmo.runner_olho_vermelho import rodar

        try:
            dados_iniciais = {'idade': int(paciente.get('idade', 0))}
        except (ValueError, TypeError):
            dados_iniciais = {}

        dados, arquivo_subj = coletar_subjetivo_olho_vermelho(dados_iniciais or None)
        resultado = rodar(arquivo_subj)
        with open(arquivo_subj, encoding='utf-8') as f:
            admissao['dados_organico'] = json.load(f)
        admissao['modulo_organico'] = 'olho_vermelho'
        return resultado

    print(f'\n  Módulo Oftalmo "{modulo_nome}" ainda não implementado.')
    return None


def _rodar_asma(modulo_nome, admissao, paciente):
    if modulo_nome == 'asma':
        from modules.sintomas.asma.asma_subjetivo import coletar_subjetivo_asma
        from modules.raciocinio.asma.runner_asma import rodar
        try: dados_iniciais = {'idade': int(paciente.get('idade', 0))}
        except: dados_iniciais = {}
        dados, arquivo = coletar_subjetivo_asma(dados_iniciais or None)
        resultado = rodar(arquivo)
        with open(arquivo, encoding='utf-8') as f:
            admissao['dados_organico'] = json.load(f)
        admissao['modulo_organico'] = 'asma'
        return resultado
    return None


def _rodar_dpoc(modulo_nome, admissao, paciente):
    if modulo_nome == 'dpoc':
        from modules.sintomas.dpoc.dpoc_subjetivo import coletar_subjetivo_dpoc
        from modules.raciocinio.dpoc.runner_dpoc import rodar
        try: dados_iniciais = {'idade': int(paciente.get('idade', 0))}
        except: dados_iniciais = {}
        dados, arquivo = coletar_subjetivo_dpoc(dados_iniciais or None)
        resultado = rodar(arquivo)
        with open(arquivo, encoding='utf-8') as f:
            admissao['dados_organico'] = json.load(f)
        admissao['modulo_organico'] = 'dpoc'
        return resultado
    return None


def _rodar_sincope(modulo_nome, admissao, paciente):
    if modulo_nome == 'sincope':
        from modules.sintomas.sincope.sincope_subjetivo import coletar_subjetivo_sincope
        from modules.raciocinio.sincope.runner_sincope import rodar
        try: dados_iniciais = {'idade': int(paciente.get('idade', 0))}
        except: dados_iniciais = {}
        dados, arquivo = coletar_subjetivo_sincope(dados_iniciais or None)
        resultado = rodar(arquivo)
        with open(arquivo, encoding='utf-8') as f:
            admissao['dados_organico'] = json.load(f)
        admissao['modulo_organico'] = 'sincope'
        return resultado
    return None


def _rodar_anorretal(modulo_nome, admissao, paciente):
    if modulo_nome == 'anorretal':
        from modules.sintomas.anorretal.anorretal_subjetivo import coletar_subjetivo_anorretal
        from modules.raciocinio.anorretal.runner_anorretal import rodar
        try: dados_iniciais = {'idade': int(paciente.get('idade', 0))}
        except: dados_iniciais = {}
        dados, arquivo = coletar_subjetivo_anorretal(dados_iniciais or None)
        resultado = rodar(arquivo)
        with open(arquivo, encoding='utf-8') as f:
            admissao['dados_organico'] = json.load(f)
        admissao['modulo_organico'] = 'anorretal'
        return resultado
    return None


def _rodar_edema(modulo_nome, admissao, paciente):
    if modulo_nome == 'edema':
        from modules.sintomas.edema.edema_subjetivo import coletar_subjetivo_edema
        from modules.raciocinio.edema.runner_edema import rodar
        try: dados_iniciais = {'idade': int(paciente.get('idade', 0))}
        except: dados_iniciais = {}
        dados, arquivo = coletar_subjetivo_edema(dados_iniciais or None)
        resultado = rodar(arquivo)
        with open(arquivo, encoding='utf-8') as f:
            admissao['dados_organico'] = json.load(f)
        admissao['modulo_organico'] = 'edema'
        return resultado
    return None


def _rodar_ictericia(modulo_nome, admissao, paciente):
    if modulo_nome == 'ictericia':
        from modules.sintomas.ictericia.ictericia_subjetivo import coletar_subjetivo_ictericia
        from modules.raciocinio.ictericia.runner_ictericia import rodar
        try: dados_iniciais = {'idade': int(paciente.get('idade', 0))}
        except: dados_iniciais = {}
        dados, arquivo = coletar_subjetivo_ictericia(dados_iniciais or None)
        resultado = rodar(arquivo)
        with open(arquivo, encoding='utf-8') as f:
            admissao['dados_organico'] = json.load(f)
        admissao['modulo_organico'] = 'ictericia'
        return resultado
    return None


def _rodar_gota(modulo_nome, admissao, paciente):
    """Módulo Gota / Artrite por Cristais — subjetivo + engine + runner."""

    if modulo_nome == 'gota':
        from modules.sintomas.gota.gota_subjetivo import coletar_subjetivo_gota
        from modules.raciocinio.gota.runner_gota import rodar

        try:
            dados_iniciais = {'idade': int(paciente.get('idade', 0))}
        except (ValueError, TypeError):
            dados_iniciais = {}

        dados, arquivo_subj = coletar_subjetivo_gota(dados_iniciais or None)
        resultado = rodar(arquivo_subj)
        with open(arquivo_subj, encoding='utf-8') as f:
            admissao['dados_organico'] = json.load(f)
        admissao['modulo_organico'] = 'gota'
        return resultado

    print(f'\n  Módulo Gota "{modulo_nome}" ainda não implementado.')
    return None


def _rodar_consciencia(modulo_nome, admissao, paciente):
    if modulo_nome == 'consciencia':
        from modules.sintomas.consciencia.subjetivo import coletar_subjetivo_consciencia
        from modules.raciocinio.consciencia.runner import rodar
        dados, arq = coletar_subjetivo_consciencia()
        resultado  = rodar(arq)
        with open(arq, encoding='utf-8') as f:
            admissao['dados_organico'] = json.load(f)
        admissao['modulo_organico'] = 'consciencia'
        return resultado
    return None


def _rodar_linfadenopatia(modulo_nome, admissao, paciente):
    if modulo_nome == 'linfadenopatia':
        from modules.sintomas.linfadenopatia.subjetivo import coletar_subjetivo_linfadenopatia
        from modules.raciocinio.linfadenopatia.runner import rodar
        dados, arq = coletar_subjetivo_linfadenopatia()
        resultado  = rodar(arq)
        with open(arq, encoding='utf-8') as f:
            admissao['dados_organico'] = json.load(f)
        admissao['modulo_organico'] = 'linfadenopatia'
        return resultado
    return None


def _rodar_sono(modulo_nome, admissao, paciente):
    """Módulo Transtornos do Sono — subjetivo + engine + runner."""
    if modulo_nome == 'sono':
        from modules.sintomas.sono.subjetivo import coletar_subjetivo_sono
        from modules.raciocinio.sono.runner import rodar
        dados, arquivo_subj = coletar_subjetivo_sono()
        resultado = rodar(arquivo_subj)
        with open(arquivo_subj, encoding='utf-8') as f:
            admissao['dados_organico'] = json.load(f)
        admissao['modulo_organico'] = 'sono'
        return resultado
    print(f'\n  Módulo Sono "{modulo_nome}" ainda não implementado.')
    return None


def _rodar_anemia(modulo_nome, admissao, paciente):
    """Módulo Anemia — interpretação de hemograma + engine + runner."""

    if modulo_nome == 'anemia':
        from modules.sintomas.anemia.subjetivo import coletar_subjetivo_anemia
        from modules.raciocinio.anemia.runner import rodar

        dados, arquivo_subj = coletar_subjetivo_anemia()
        resultado = rodar(arquivo_subj)
        with open(arquivo_subj, encoding='utf-8') as f:
            admissao['dados_organico'] = json.load(f)
        admissao['modulo_organico'] = 'anemia'
        return resultado

    print(f'\n  Módulo Anemia "{modulo_nome}" ainda não implementado.')
    return None


def _rodar_hemorragia(modulo_nome, admissao, paciente):
    if modulo_nome == 'hemorragia':
        from modules.sintomas.hemorragia.subjetivo import coletar_subjetivo_hemorragia
        from modules.raciocinio.hemorragia.runner import rodar
        try: dados_iniciais = {'idade': int(paciente.get('idade', 0)),
                               'sexo': paciente.get('sexo', 'masculino')}
        except: dados_iniciais = {}
        dados, arquivo = coletar_subjetivo_hemorragia(dados_iniciais or None)
        resultado = rodar(arquivo)
        with open(arquivo, encoding='utf-8') as f:
            admissao['dados_organico'] = json.load(f)
        admissao['modulo_organico'] = 'hemorragia'
        return resultado
    return None


def _rodar_celulite(modulo_nome, admissao, paciente):
    if modulo_nome == 'celulite':
        from modules.sintomas.celulite.subjetivo import coletar_subjetivo_celulite
        from modules.raciocinio.celulite.runner import rodar
        try: dados_iniciais = {'idade': int(paciente.get('idade', 0))}
        except: dados_iniciais = {}
        dados, arquivo = coletar_subjetivo_celulite(dados_iniciais or None)
        resultado = rodar(arquivo)
        with open(arquivo, encoding='utf-8') as f:
            admissao['dados_organico'] = json.load(f)
        admissao['modulo_organico'] = 'celulite'
        return resultado
    return None


def _rodar_febre(modulo_nome, admissao, paciente):
    """Módulo Febre sem Foco — subjetivo + engine + runner."""

    if modulo_nome == 'febre':
        from modules.sintomas.febre.febre_subjetivo import coletar_subjetivo_febre
        from modules.raciocinio.febre.runner_febre import rodar

        try:
            dados_iniciais = {'idade': int(paciente.get('idade', 0))}
        except (ValueError, TypeError):
            dados_iniciais = {}

        dados, arquivo_subj = coletar_subjetivo_febre(dados_iniciais or None)
        resultado = rodar(arquivo_subj)
        with open(arquivo_subj, encoding='utf-8') as f:
            admissao['dados_organico'] = json.load(f)
        admissao['modulo_organico'] = 'febre'
        return resultado

    print(f'\n  Módulo Febre "{modulo_nome}" ainda não implementado.')
    return None


# ──────────────────────────────────────────────────────────────────────────────
# MATCHING DE QUEIXA — 3 passes (exato → substring → token-overlap)
# ──────────────────────────────────────────────────────────────────────────────

# Stopwords PT-BR ignoradas no cálculo de overlap semântico
_STOPWORDS = frozenset({
    'de', 'do', 'da', 'dos', 'das', 'no', 'na', 'nos', 'nas', 'num', 'numa',
    'em', 'com', 'o', 'a', 'os', 'as', 'e', 'é', 'um', 'uma', 'uns', 'umas',
    'ao', 'aos', 'se', 'por', 'para', 'que', 'não', 'mais', 'bem', 'há',
    'meu', 'minha', 'meus', 'minhas', 'seu', 'sua', 'está', 'estou',
    'tenho', 'sinto', 'tô', 'to', 'muito', 'bastante', 'forte', 'leve',
})


def _sig(texto: str) -> frozenset:
    """Tokens significativos (sem stopwords)."""
    return frozenset(t for t in texto.lower().split() if t not in _STOPWORDS)


def _match_queixa(queixa: str):
    """
    Roteamento em 3 passes — tolerante a palavras extras e paráfrases.

    Passe 1 — Exato         'dor de ouvido'    → match direto
    Passe 2 — Substring     'minha dor de ouvido direito'
                            ← 'dor de ouvido' ⊂ input → match, prefere keyword mais longa
    Passe 3 — Token-overlap 'ouvido doendo há 2 dias'
                            ← sig_tokens ∩ sig_tokens('dor no ouvido') score > 1
                            Ativa apenas se input tem ≥ 2 tokens significativos
                            e há vencedor único (sem empate → ambíguo → None).

    Retorna (modulo_dict | None, keyword_matched | '').
    """
    chave = queixa.strip().lower()

    # ── Passe 1: exato ───────────────────────────────────────────────────────
    if chave in MODULOS_QUEIXA:
        return MODULOS_QUEIXA[chave], chave

    # ── Passe 2: keyword conhecida é substring do input ──────────────────────
    melhor_kw, melhor_mod = '', None
    for kw in MODULOS_QUEIXA:
        if kw in chave and len(kw) > len(melhor_kw):
            melhor_kw, melhor_mod = kw, MODULOS_QUEIXA[kw]
    if melhor_mod:
        return melhor_mod, melhor_kw

    # ── Passe 3: token-overlap semântico (score > 1, vencedor único) ─────────
    tokens_in = _sig(chave)
    if len(tokens_in) < 2:           # input de 1 token: não arrisca match fuzzy
        return None, ''

    scores: dict[str, int] = {}
    for kw in MODULOS_QUEIXA:
        s = len(tokens_in & _sig(kw))
        if s > 1:
            scores[kw] = s

    if not scores:
        return None, ''

    max_score = max(scores.values())
    vencedores = [kw for kw, s in scores.items() if s == max_score]

    if len(vencedores) == 1:
        kw = vencedores[0]
        return MODULOS_QUEIXA[kw], kw

    # Empate: ambíguo — informa ao usuário sem auto-rotear
    print(f'\n  ⚠️  Queixa ambígua — você quis dizer?')
    for i, kw in enumerate(vencedores[:5], 1):
        print(f'    {i}. {kw}')
    return None, ''


def despachar(queixa, admissao, paciente):
    chave  = queixa.strip().lower()
    modulo, kw_match = _match_queixa(chave)

    if modulo is None:
        if not kw_match:             # ambíguo já imprimiu opções acima
            print(f'\n  Queixa "{queixa}" não reconhecida.')
            _sugerir_similares(chave)
        return None

    if kw_match and kw_match != chave:
        print(f'\n  [Queixa interpretada como: "{kw_match}"]')

    if modulo['tipo'] == 'legado':
        subj = admissao['subjetivo_especifico'].get(modulo['chave'], {})
        obj  = admissao['objetivo_especifico'].get(modulo['chave'], {})
        args = modulo['args'](subj, obj, admissao, paciente)
        return modulo['interpreta'](*args)

    if modulo['tipo'] == 'msk':
        resultado = _rodar_msk(modulo['modulo'], admissao, paciente)
        if resultado is not None:
            admissao.setdefault('dados_por_modulo', {})[modulo['modulo']] = admissao.get('dados_msk', {})
        return resultado

    if modulo['tipo'] == 'organico':
        resultado = _rodar_organico(modulo['modulo'], admissao, paciente)
        if resultado is not None:
            admissao.setdefault('dados_por_modulo', {})[modulo['modulo']] = admissao.get('dados_organico', {})
        return resultado

    if modulo['tipo'] == 'orl':
        resultado = _rodar_orl(modulo['modulo'], admissao, paciente)
        if resultado is not None:
            admissao.setdefault('dados_por_modulo', {})[modulo['modulo']] = admissao.get('dados_organico', {})
        return resultado

    if modulo['tipo'] == 'oftalmo':
        resultado = _rodar_oftalmo(modulo['modulo'], admissao, paciente)
        if resultado is not None:
            admissao.setdefault('dados_por_modulo', {})[modulo['modulo']] = admissao.get('dados_organico', {})
        return resultado

    if modulo['tipo'] == 'palpitacao':
        resultado = _rodar_palpitacao(modulo['modulo'], admissao, paciente)
        if resultado is not None:
            admissao.setdefault('dados_por_modulo', {})[modulo['modulo']] = admissao.get('dados_organico', {})
        return resultado

    if modulo['tipo'] == 'asma':
        resultado = _rodar_asma(modulo['modulo'], admissao, paciente)
        if resultado is not None:
            admissao.setdefault('dados_por_modulo', {})[modulo['modulo']] = admissao.get('dados_organico', {})
        return resultado

    if modulo['tipo'] == 'dpoc':
        resultado = _rodar_dpoc(modulo['modulo'], admissao, paciente)
        if resultado is not None:
            admissao.setdefault('dados_por_modulo', {})[modulo['modulo']] = admissao.get('dados_organico', {})
        return resultado

    if modulo['tipo'] == 'sincope':
        resultado = _rodar_sincope(modulo['modulo'], admissao, paciente)
        if resultado is not None:
            admissao.setdefault('dados_por_modulo', {})[modulo['modulo']] = admissao.get('dados_organico', {})
        return resultado

    if modulo['tipo'] == 'anorretal':
        resultado = _rodar_anorretal(modulo['modulo'], admissao, paciente)
        if resultado is not None:
            admissao.setdefault('dados_por_modulo', {})[modulo['modulo']] = admissao.get('dados_organico', {})
        return resultado

    if modulo['tipo'] == 'edema':
        resultado = _rodar_edema(modulo['modulo'], admissao, paciente)
        if resultado is not None:
            admissao.setdefault('dados_por_modulo', {})[modulo['modulo']] = admissao.get('dados_organico', {})
        return resultado

    if modulo['tipo'] == 'ictericia':
        resultado = _rodar_ictericia(modulo['modulo'], admissao, paciente)
        if resultado is not None:
            admissao.setdefault('dados_por_modulo', {})[modulo['modulo']] = admissao.get('dados_organico', {})
        return resultado

    if modulo['tipo'] == 'gota':
        resultado = _rodar_gota(modulo['modulo'], admissao, paciente)
        if resultado is not None:
            admissao.setdefault('dados_por_modulo', {})[modulo['modulo']] = admissao.get('dados_organico', {})
        return resultado

    if modulo['tipo'] == 'febre':
        resultado = _rodar_febre(modulo['modulo'], admissao, paciente)
        if resultado is not None:
            admissao.setdefault('dados_por_modulo', {})[modulo['modulo']] = admissao.get('dados_organico', {})
        return resultado

    if modulo['tipo'] == 'consciencia':
        resultado = _rodar_consciencia(modulo['modulo'], admissao, paciente)
        if resultado is not None:
            admissao.setdefault('dados_por_modulo', {})[modulo['modulo']] = admissao.get('dados_organico', {})
        return resultado

    if modulo['tipo'] == 'linfadenopatia':
        resultado = _rodar_linfadenopatia(modulo['modulo'], admissao, paciente)
        if resultado is not None:
            admissao.setdefault('dados_por_modulo', {})[modulo['modulo']] = admissao.get('dados_organico', {})
        return resultado

    if modulo['tipo'] == 'sono':
        resultado = _rodar_sono(modulo['modulo'], admissao, paciente)
        if resultado is not None:
            admissao.setdefault('dados_por_modulo', {})[modulo['modulo']] = admissao.get('dados_organico', {})
        return resultado

    if modulo['tipo'] == 'anemia':
        resultado = _rodar_anemia(modulo['modulo'], admissao, paciente)
        if resultado is not None:
            admissao.setdefault('dados_por_modulo', {})[modulo['modulo']] = admissao.get('dados_organico', {})
        return resultado

    if modulo['tipo'] == 'celulite':
        resultado = _rodar_celulite(modulo['modulo'], admissao, paciente)
        if resultado is not None:
            admissao.setdefault('dados_por_modulo', {})[modulo['modulo']] = admissao.get('dados_organico', {})
        return resultado

    if modulo['tipo'] == 'hemorragia':
        resultado = _rodar_hemorragia(modulo['modulo'], admissao, paciente)
        if resultado is not None:
            admissao.setdefault('dados_por_modulo', {})[modulo['modulo']] = admissao.get('dados_organico', {})
        return resultado

    return None


def _sugerir_similares(queixa: str):
    """Sugere até 5 queixas com algum token em comum (sem stopwords)."""
    tokens_in = _sig(queixa)
    similares = [kw for kw in MODULOS_QUEIXA if tokens_in & _sig(kw)]
    # ordena por score decrescente
    similares.sort(key=lambda kw: len(tokens_in & _sig(kw)), reverse=True)
    if similares:
        print(f'  Você quis dizer: {", ".join(similares[:5])}?')
    else:
        # fallback: mostra as categorias (sem enumerar 168 keywords)
        cats = sorted({v.get('modulo', v.get('chave', '')) for v in MODULOS_QUEIXA.values()})
        print(f'  Módulos disponíveis: {", ".join(cats)}')