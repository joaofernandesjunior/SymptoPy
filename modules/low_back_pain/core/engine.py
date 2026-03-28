# 1. funções auxiliares

def mostrar_resultado(nome_bloco, resultado):
    print(f'--- {nome_bloco} ---')
    print(f"Score: {resultado['score']}")
    print(f"Alert: {resultado['alert']}")
    if 'stage' in resultado:
        print(f"Stage: {resultado['stage']}")
    print(f"Action: {resultado['action'] or 'No immediate action triggered'}")
    print('Positive findings:', ', '.join(resultado['positive']) or 'None')
    print('Negative findings:', ', '.join(resultado['negative']) or 'None')
    print()

# 2. blocos clínicos

def avaliar_cauda_equina(dados):
    ces_score = 0
    ces_positive = []
    ces_negative = []

    if dados['urinary_retention']:
        ces_score += 2
        ces_positive.append('urinary retention')
    else:
        ces_negative.append('urinary retention')

    if dados['bowel_dysfunction']:
        ces_score += 2
        ces_positive.append('bowel dysfunction')
    else:
        ces_negative.append('bowel dysfunction')

    if dados['reduced_perianal_sensation']:
        ces_score += 3
        ces_positive.append('reduced perianal sensation')
    else:
        ces_negative.append('reduced perianal sensation')

    if dados['saddle_anesthesia']:
        ces_score += 3
        ces_positive.append('saddle anesthesia')
    else:
        ces_negative.append('saddle anesthesia')

    if dados['bilateral_leg_weakness']:
        ces_score += 2
        ces_positive.append('bilateral leg weakness')
    else:
        ces_negative.append('bilateral leg weakness')

    if dados['bilateral_sciatica']:
        ces_score += 2
        ces_positive.append('bilateral sciatica')
    else:
        ces_negative.append('bilateral sciatica')

    suspeita = ces_score >= 3

    return {
        'score': ces_score,
        'positive': ces_positive,
        'negative': ces_negative,
        'stage': 'urgent_mri' if suspeita else 'observe',
        'action': 'Urgent MRI and emergency evaluation for suspected cauda equina syndrome' if suspeita else None,
        'alert': suspeita,
        'suspeita_ces': suspeita
    }

def avaliar_infeccao(dados):
    infection_score = 0
    infection_positive = []
    infection_negative = []
    if dados['fever']:
        infection_score += 1
        infection_positive.append('fever')
    else:
        infection_negative.append('fever')

    if dados['immunosuppression']:
        infection_score += 2
        infection_positive.append('immunosuppression')
    else:
        infection_negative.append('immunosuppression')

    if dados['recent_bacterial_infection']:
        infection_score += 3
        infection_positive.append('recent bacterial infection')
    else:
        infection_negative.append('recent bacterial infection')

    if dados['recent_spinal_procedure']:
        infection_score += 2
        infection_positive.append('recent spinal procedure')
    else:
        infection_negative.append('recent spinal procedure')

    if dados['indwelling_catheter_dialysis']:
        infection_score += 3
        infection_positive.append('indwelling catheter / dialysis')
    else:
        infection_negative.append('indwelling catheter / dialysis')

    suspeita = infection_score >= 2

    return {
    'score': infection_score,
    'positive': infection_positive,
    'negative': infection_negative,
    'stage': 'order_pcr' if suspeita else 'observe',
    'action': 'Order ESR/CRP. If elevated, strongly consider urgent MRI/referral.' if suspeita else None,
    'alert': suspeita,
    'suspeita_infeccao': suspeita
}


def avaliar_fratura(dados):
    fracture_score = 0
    fracture_positive = []
    fracture_negative = []

    if dados['major_trauma']:
        fracture_score += 3
        fracture_positive.append('major trauma')
    else:
        fracture_negative.append('major trauma')

    if dados['minor_trauma']:
        fracture_score += 2
        fracture_positive.append('minor trauma')
    else:
        fracture_negative.append('minor trauma')

    if dados['age_70_or_more']:
        fracture_score += 3
        fracture_positive.append('age 70 or more')
    else:
        fracture_negative.append('age 70 or more')

    if dados['osteoporosis']:
        fracture_score += 2
        fracture_positive.append('osteoporosis')
    else:
        fracture_negative.append('osteoporosis')

    if dados['chronic_steroid_use']:
        fracture_score += 2
        fracture_positive.append('chronic steroid use')
    else:
        fracture_negative.append('chronic steroid use')

    suspeita = fracture_score >= 3

    return {
        'score': fracture_score,
        'positive': fracture_positive,
        'negative': fracture_negative,
        'stage': 'consider_imaging' if suspeita else 'observe',
        'action': 'Consider spinal X-ray or other appropriate imaging to evaluate possible vertebral fracture' if suspeita else None,
        'alert': suspeita,
        'suspeita_fratura': suspeita
        }

def avaliar_malignidade(dados):
    malignancy_score = 0
    malignancy_positive = []
    malignancy_negative = []

    if dados['history_of_cancer']:
        malignancy_score += 3
        malignancy_positive.append('history of cancer')
    else:
        malignancy_negative.append('history of cancer')

    if dados['unexplained_weight_loss']:
        malignancy_score += 2
        malignancy_positive.append('unexplained weight loss')
    else:
        malignancy_negative.append('unexplained weight loss')

    if dados['night_pain_or_rest_pain']:
        malignancy_score += 2
        malignancy_positive.append('night/rest pain')
    else:
        malignancy_negative.append('night/rest pain')

    suspeita = malignancy_score >= 3

    return {
        'score': malignancy_score,
        'positive': malignancy_positive,
        'negative': malignancy_negative,
        'stage': 'consider_imaging' if suspeita else 'observe',
        'action': 'Consider imaging and evaluation for possible malignancy' if suspeita else None,
        'alert': suspeita,
        'suspeita_malignidade': suspeita
    }

def avaliar_radiculopatia(dados):
    rad_score = 0
    rad_positive = []
    rad_negative = []

    if dados['dermatomal_leg_pain_below_knee']:
        rad_score += 3
        rad_positive.append('dermatomal leg pain below knee')
    else:
        rad_negative.append('dermatomal leg pain below knee')

    if dados['crossed_slr']:
        rad_score += 3
        rad_positive.append('positive crossed SLR')
    else:
        rad_negative.append('positive crossed SLR')

    if dados['focal_neurologic_deficit']:
        rad_score += 2
        rad_positive.append('focal neurologic deficit')
    else:
        rad_negative.append('focal neurologic deficit')

    if dados['positive_slr']:
        rad_score += 2
        rad_positive.append('positive SLR')
    else:
        rad_negative.append('positive SLR')

    if dados['leg_pain_worse_than_back']:
        rad_score += 2
        rad_positive.append('leg pain worse than back pain')
    else:
        rad_negative.append('leg pain worse than back pain')

    if dados['pain_with_cough_sneeze']:
        rad_score += 1
        rad_positive.append('pain with cough/sneeze')
    else:
        rad_negative.append('pain with cough/sneeze')

    if dados['age_30_50']:
        rad_score += 1
        rad_positive.append('age 30-50')
    else:
        rad_negative.append('age 30-50')

    suspeita = rad_score >= 5

    return {
        'score': rad_score,
        'positive': rad_positive,
        'negative': rad_negative,
        'stage': 'radiculopathy_pathway' if suspeita else 'observe',
        'action': 'Conservative management for radiculopathy. Consider MRI if progressive deficit or no improvement.' if suspeita else None,
        'alert': suspeita,
        'suspeita_radiculopatia': suspeita
    }

def avaliar_estenose(dados):
    estenose_score = 0
    estenose_positive = []
    estenose_negative = []

    if dados['neurogenic_claudication']:
        estenose_score += 4
        estenose_positive.append('neurogenic claudication')
    else:
        estenose_negative.append('neurogenic claudication')

    if dados['relief_with_flexion']:
        estenose_score += 3
        estenose_positive.append('relief with sitting/flexion')
    else:
        estenose_negative.append('relief with sitting/flexion')

    if dados['bilateral_leg_symptoms']:
        estenose_score += 2
        estenose_positive.append('bilateral leg symptoms')
    else:
        estenose_negative.append('bilateral leg symptoms')

    if dados['age_over_60']:
        estenose_score += 2
        estenose_positive.append('age over 60')
    else:
        estenose_negative.append('age over 60')

    if dados['poor_balance']:
        estenose_score += 1
        estenose_positive.append('poor balance')
    else:
        estenose_negative.append('poor balance')

    if dados['pain_with_extension']:
        estenose_score += 1
        estenose_positive.append('pain worse with extension')
    else:
        estenose_negative.append('pain worse with extension')

    if dados['sensory_deficit']:
        estenose_score += 1
        estenose_positive.append('sensory deficit')
    else:
        estenose_negative.append('sensory deficit')

    suspeita = estenose_score >= 6

    return {
        'score': estenose_score,
        'positive': estenose_positive,
        'negative': estenose_negative,
        'stage': 'stenosis_pathway' if suspeita else 'observe',
        'action': 'Conservative management (flexion-based therapy). Consider imaging if severe or refractory.' if suspeita else None,
        'alert': suspeita,
        'suspeita_estenose': suspeita
    }

def interpretar_fluxo_horizontal(dados):
    resultado_rad = avaliar_radiculopatia(dados)
    resultado_estenose = avaliar_estenose(dados)

    if resultado_rad['alert'] and not resultado_estenose['alert']:
        return {
            'diagnostico_principal': 'Likely lumbar radiculopathy',
            'categoria': 'horizontal_spinal',
            'resultado_radiculopatia': resultado_rad,
            'resultado_estenose': resultado_estenose,
            'suspeita_mecanica': False,
            'action': resultado_rad['action']
        }

    if resultado_estenose['alert'] and not resultado_rad['alert']:
        return {
            'diagnostico_principal': 'Likely lumbar spinal stenosis',
            'categoria': 'horizontal_spinal',
            'resultado_radiculopatia': resultado_rad,
            'resultado_estenose': resultado_estenose,
            'suspeita_mecanica': False,
            'action': resultado_estenose['action']
        }

    if resultado_rad['alert'] and resultado_estenose['alert']:
        if resultado_rad['score'] > resultado_estenose['score']:
            principal = 'Likely lumbar radiculopathy'
            action = resultado_rad['action']
        elif resultado_estenose['score'] > resultado_rad['score']:
            principal = 'Likely lumbar spinal stenosis'
            action = resultado_estenose['action']
        else:
            principal = 'Mixed spinal pattern: radiculopathy and stenosis both possible'
            action = 'Consider clinical correlation and targeted imaging if needed'

        return {
            'diagnostico_principal': principal,
            'categoria': 'horizontal_spinal',
            'resultado_radiculopatia': resultado_rad,
            'resultado_estenose': resultado_estenose,
            'suspeita_mecanica': False,
            'action': action
        }

    return {
        'diagnostico_principal': 'Likely nonspecific mechanical low back pain',
        'categoria': 'horizontal_spinal',
        'resultado_radiculopatia': resultado_rad,
        'resultado_estenose': resultado_estenose,
        'suspeita_mecanica': True,
        'action': 'Likely nonspecific mechanical low back pain. Consider conservative treatment with analgesia, short-term muscle relaxant if appropriate, and follow-up.' 
    }

def avaliar_visceral(dados):
    
    gatilhos = []

    if dados['gi_symptoms']:
        gatilhos.append('GI symptoms')

    if dados['gu_symptoms']:
        gatilhos.append('GU symptoms')

    if dados['gynecologic_symptoms']:
        gatilhos.append('gynecologic symptoms')

    if dados['abdominal_bruit']:
        gatilhos.append('abdominal bruit')

    if dados['aaa_risk_factors']:
        gatilhos.append('AAA risk factors')

    suspeita = len(gatilhos) > 0

    return {
        'positive': gatilhos,
        'stage': 'redirect_to_other_module' if suspeita else 'observe',
        'action': 'Redirect to appropriate module: abdominal pain / dysuria / hematuria pathways' if suspeita else None,
        'alert': suspeita,
        'suspeita_visceral': suspeita
    }

def interpretar_visceral(dados):
    resultado_visceral = avaliar_visceral(dados)

    if resultado_visceral['alert']:
        return {
            'diagnostico_principal': 'Possible non-spinal cause of low back pain',
            'categoria': 'non_spinal',
            'resultado_visceral': resultado_visceral,
            'action': 'Redirect evaluation to the appropriate syndrome module (abdominal pain / dysuria / hematuria / gynecologic pathway).'
        }

    return {
        'diagnostico_principal': 'No strong non-spinal clue identified',
        'categoria': 'observe',
        'resultado_visceral': resultado_visceral,
        'action': None
    }

# 3. agregadores

def avaliar_red_flags(dados):
    return {
        'ces': avaliar_cauda_equina(dados),
        'infeccao': avaliar_infeccao(dados),
        'fratura': avaliar_fratura(dados),
        'malignidade': avaliar_malignidade(dados)
    }

def interpretar_lombalgia(dados):
    red_flags = avaliar_red_flags(dados)

    if red_flags['ces']['alert']:
        return {
            'diagnostico_principal': 'Cauda equina syndrome suspected',
            'categoria': 'red_flag',
            'resultado_red_flags': red_flags,
            'proximo_bloco': None
        }

    if red_flags['infeccao']['alert']:
        return {
            'diagnostico_principal': 'Possible spinal infection',
            'categoria': 'red_flag',
            'resultado_red_flags': red_flags,
            'proximo_bloco': None
        }

    if red_flags['malignidade']['alert']:
        return {
            'diagnostico_principal': 'Possible malignancy',
            'categoria': 'red_flag',
            'resultado_red_flags': red_flags,
            'proximo_bloco': None
        }

    if red_flags['fratura']['alert']:
        return {
            'diagnostico_principal': 'Possible vertebral fracture',
            'categoria': 'red_flag',
            'resultado_red_flags': red_flags,
            'proximo_bloco': None
        }

    resultado_visceral = interpretar_visceral(dados)

    if resultado_visceral['resultado_visceral']['alert']:
        return {
            'diagnostico_principal': resultado_visceral['diagnostico_principal'],
            'categoria': resultado_visceral['categoria'],
            'resultado_red_flags': red_flags,
            'resultado_visceral': resultado_visceral,
            'proximo_bloco': 'non_spinal_module'
        }

    resultado_horizontal = interpretar_fluxo_horizontal(dados)

    return {
        'diagnostico_principal': resultado_horizontal['diagnostico_principal'],
        'categoria': resultado_horizontal['categoria'],
        'resultado_red_flags': red_flags,
        'resultado_horizontal': resultado_horizontal,
        'proximo_bloco': None
    }

# 4. bloco de teste

if __name__ == '__main__':
    caso_base = {
        'urinary_retention': False,
        'bowel_dysfunction': False,
        'reduced_perianal_sensation': False,
        'saddle_anesthesia': False,
        'bilateral_leg_weakness': False,
        'bilateral_sciatica': False,

        'fever': False,
        'immunosuppression': False,
        'recent_bacterial_infection': False,
        'recent_spinal_procedure': False,
        'indwelling_catheter_dialysis': False,

        'major_trauma': False,
        'minor_trauma': False,
        'age_70_or_more': False,
        'osteoporosis': False,
        'chronic_steroid_use': False,

        'history_of_cancer': False,
        'unexplained_weight_loss': False,
        'night_pain_or_rest_pain': False,

        'dermatomal_leg_pain_below_knee': False,
        'crossed_slr': False,
        'focal_neurologic_deficit': False,
        'positive_slr': False,
        'leg_pain_worse_than_back': False,
        'pain_with_cough_sneeze': False,
        'age_30_50': False,

        'neurogenic_claudication': False,
        'relief_with_flexion': False,
        'bilateral_leg_symptoms': False,
        'age_over_60': False,
        'poor_balance': False,
        'pain_with_extension': False,
        'sensory_deficit': False,

        'abdominal_symptoms': False,
        'urinary_symptoms': False,
        'gynecologic_symptoms': False,
        'pain_not_mechanical': False
    }

    caso_ces = caso_base.copy()
    caso_ces.update({
        'urinary_retention': True,
        'saddle_anesthesia': True
    })

    caso_infeccao = caso_base.copy()
    caso_infeccao.update({
        'fever': True,
        'recent_bacterial_infection': True
    })

    caso_fratura = caso_base.copy()
    caso_fratura.update({
        'minor_trauma': True,
        'age_70_or_more': True
    })

    caso_malignidade = caso_base.copy()
    caso_malignidade.update({
        'history_of_cancer': True
    })

    caso_radiculopatia = caso_base.copy()
    caso_radiculopatia.update({
        'dermatomal_leg_pain_below_knee': True,
        'crossed_slr': True,
        'focal_neurologic_deficit': True,
        'positive_slr': True,
        'leg_pain_worse_than_back': True,
        'pain_with_cough_sneeze': True,
        'age_30_50': True
    })

    caso_estenose = caso_base.copy()
    caso_estenose.update({
        'neurogenic_claudication': True,
        'relief_with_flexion': True,
        'bilateral_leg_symptoms': True,
        'age_over_60': True,
        'poor_balance': True,
        'pain_with_extension': True
    })

    caso_mecanica = caso_base.copy()

    casos = {
        'CES': caso_ces,
        'INFECCAO': caso_infeccao,
        'FRATURA': caso_fratura,
        'MALIGNIDADE': caso_malignidade,
        'RADICULOPATIA': caso_radiculopatia,
        'ESTENOSE': caso_estenose,
        'MECANICA': caso_mecanica
    }

    for nome, caso in casos.items():
        print(f'===== {nome} =====')
        resultado = interpretar_lombalgia(caso)
        print(resultado)
        print()