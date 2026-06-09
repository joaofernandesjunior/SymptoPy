def sn(pergunta):
    resp = input(pergunta).strip().lower()
    return resp == 's'


def coletar_dispneia():
    disp = {}


    disp['dias_inicio'] = int(input('dias de inicio: '))
    if disp['dias_inicio'] < 7: 
        disp['inicio_agudo'] = True
    else: 
        disp['inicio_agudo'] = False

    disp['piora_progressiva'] = sn('teve priora progressiva? [s/n] ')
    
    disp['repouso'] = sn('dispneia em repouso? [s/n] ')
    
    disp['febre'] = sn('febre? [s/n] ')
    
    disp['tosse'] = sn('tosse? [s/n] ')
    
    disp['chiado'] = sn('chiado? [s/n] ')

    disp['dor_tx'] = sn('dor toracica? [s/n] ')

    disp['dor_pleura'] = sn('dor pleuritica? [s/n] ')
    
    disp['hemoptise'] = sn('hemoptise? [s/n] ')
    
    disp['sincope'] = sn('sincope? [s/n] ')
    
    disp['ortopneia'] = sn('ortopneia? [s/n] ')
    
    disp['dpn'] = sn('dpn? [s/n] ')
    
    disp['tosse_noturna'] = sn('tosse noturna? [s/n] ')
    
    disp['dispneia_esforcos'] = sn('dispneia aos esforços? [s/n] ')
    
    return disp
    


