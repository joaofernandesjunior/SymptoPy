from modules.low_back_pain.core.engine import interpretar_lombalgia

def rodar_testes():
    casos = [
        {
            "nome": "CES clássico",
            "dados": {
                'urinary_retention': True,
                'saddle_anesthesia': True,
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

                'gi_symptoms': False,
                'gu_symptoms': False,
                'gynecologic_symptoms': False,
                'abdominal_bruit': False,
                'aaa_risk_factors': False
            },
            "esperado": "Cauda equina"
        }
    ]

    for caso in casos:
        resultado = interpretar_lombalgia(caso["dados"])
        print(f"\n--- {caso['nome']} ---")
        print("Esperado:", caso["esperado"])
        print("Obtido:", resultado["diagnostico_principal"])