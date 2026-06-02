def sn(pergunta):
    resp = input(pergunta).strip().lower()
    return resp == 's'

def coletar_objetivo_dispneia():
    disp_obj = {}

    # gravidade
    disp_obj['musculatura_acessoria'] = sn('usa musculatura acessoria? [s/n] ')
    disp_obj['fala_entrecortada'] = sn('fala entrecortada? [s/n] ')

    # cardio/vascular
    disp_obj['jvd'] = sn('veia jugular distendida? [s/n] ')
    disp_obj['edema_bilateral_mmii'] = sn('edema bilateral? [s/n] ')
    disp_obj['edema_unilateral_perna'] = sn('edema unilateral? [s/n] ')

    return disp_obj