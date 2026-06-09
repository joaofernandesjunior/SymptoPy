def sn(pergunta):
    while True:
        resp = input(pergunta).strip().lower()
        if resp in ('s', 'n'):
            return resp == 's'
        print('  Digite s ou n.')


_NORMAL = {
    'neuro':       'Glasgow 15, pupilas isocóricas e fotorreagentes, força preservada bilateralmente, sem déficit focal, sem rigidez de nuca',
    'pneumo':      'eupneico em AA, expansibilidade simétrica, MV+ bilateral, sem ruídos adventícios',
    'cardio':      'BRNF 2T sem sopros, pulsos periféricos cheios e simétricos, perfusão capilar < 3s, sem turgência jugular',
    'abdome':      'plano, RHA+, indolor à palpação superficial e profunda, sem sinais de peritonite, sem visceromegalias',
    'mmii':        'sem edema, panturrilhas livres, sem sinais flogísticos, sem lesões cutâneas',
    'pele':        'mucosas coradas e hidratadas, sem lesões, sem rash, sem petéquias, sem icterícia',
    'orofaringe':  'corada, sem hiperemia, sem exsudato, amígdalas sem hipertrofia ou assimetria',
    'eliminacoes': 'diurese preservada, evacuação normal, dieta VO aceita',
}

_SISTEMAS = [
    ('neuro',       'Neuro normal?          [s/n] ', 'Neuro — descreva a alteração: '),
    ('pneumo',      'Pneumo normal?         [s/n] ', 'Pneumo — descreva a alteração: '),
    ('cardio',      'Cardio normal?         [s/n] ', 'Cardio — descreva a alteração: '),
    ('abdome',      'Abdome normal?         [s/n] ', 'Abdome — descreva a alteração: '),
    ('mmii',        'MMII normais?          [s/n] ', 'MMII — descreva a alteração: '),
    ('pele',        'Pele/mucosas normais?  [s/n] ', 'Pele/mucosas — descreva a alteração: '),
    ('orofaringe',  'Orofaringe normal?     [s/n] ', 'Orofaringe — descreva: '),
    ('eliminacoes', 'Eliminações normais?   [s/n] ', 'Eliminações — descreva a alteração: '),
]


def coletar_objetivo():
    objetivo = {}

    print('\n' + '='*50)
    print('  EXAME FÍSICO GERAL')
    print('='*50)
    print('  s = normal (frase padrão inserida automaticamente)')
    print('  n = alterado (você descreve brevemente)\n')

    objetivo['estado_geral'] = input(
        '  Estado geral (ex: BEG, corado, hidratado, orientado, afebril): '
    ).strip()

    for chave, pergunta_sn, pergunta_alt in _SISTEMAS:
        if sn(f'  {pergunta_sn}'):
            objetivo[chave] = _NORMAL[chave]
        else:
            objetivo[chave] = input(f'  {pergunta_alt}').strip()

    return objetivo
