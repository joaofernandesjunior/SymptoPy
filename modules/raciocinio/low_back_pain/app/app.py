import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3]))

import csv
from datetime import datetime
import streamlit as st

from modules.low_back_pain.core.engine import interpretar_lombalgia

st.set_page_config(page_title="Low Back Pain Tool", layout="wide")

st.title("Low Back Pain Clinical Decision Tool")
st.write("Primary care support for low back pain evaluation")

# -----------------------------
# RED FLAGS
# -----------------------------
st.header("Red Flags")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Cauda Equina")
    urinary_retention = st.checkbox("Urinary retention")
    bowel_dysfunction = st.checkbox("Bowel dysfunction")
    saddle_anesthesia = st.checkbox("Saddle anesthesia")
    reduced_perianal_sensation = st.checkbox("Reduced perianal sensation")
    bilateral_leg_weakness = st.checkbox("Bilateral leg weakness")
    bilateral_sciatica = st.checkbox("Bilateral sciatica")

with col2:
    st.subheader("Infection")
    fever = st.checkbox("Fever")
    immunosuppression = st.checkbox("Immunosuppression")
    recent_bacterial_infection = st.checkbox("Recent infection")
    recent_spinal_procedure = st.checkbox("Recent spinal procedure")
    indwelling_catheter_dialysis = st.checkbox("Catheter / dialysis")

with col3:
    st.subheader("Fracture / Malignancy")
    major_trauma = st.checkbox("Major trauma")
    minor_trauma = st.checkbox("Minor trauma")
    age_70_or_more = st.checkbox("Age ≥70")
    osteoporosis = st.checkbox("Osteoporosis")
    chronic_steroid_use = st.checkbox("Chronic steroid use")

    history_of_cancer = st.checkbox("History of cancer")
    unexplained_weight_loss = st.checkbox("Weight loss")
    night_pain_or_rest_pain = st.checkbox("Night/rest pain")

# -----------------------------
# HORIZONTAL
# -----------------------------
st.header("Spinal Syndromes")

col4, col5 = st.columns(2)

with col4:
    st.subheader("Radiculopathy")
    dermatomal_leg_pain_below_knee = st.checkbox("Dermatomal leg pain below knee")
    crossed_slr = st.checkbox("Crossed SLR")
    focal_neurologic_deficit = st.checkbox("Neurologic deficit")
    positive_slr = st.checkbox("Positive SLR")
    leg_pain_worse_than_back = st.checkbox("Leg pain > back pain")
    pain_with_cough_sneeze = st.checkbox("Pain with cough/sneeze")
    age_30_50 = st.checkbox("Age 30-50")

with col5:
    st.subheader("Stenosis")
    neurogenic_claudication = st.checkbox("Neurogenic claudication")
    relief_with_flexion = st.checkbox("Relief with flexion")
    bilateral_leg_symptoms = st.checkbox("Bilateral symptoms")
    age_over_60 = st.checkbox("Age >60")
    poor_balance = st.checkbox("Poor balance")
    pain_with_extension = st.checkbox("Pain with extension")
    sensory_deficit = st.checkbox("Sensory deficit")

# -----------------------------
# VISCERAL
# -----------------------------
st.header("Non-spinal clues")

gi_symptoms = st.checkbox("GI symptoms")
gu_symptoms = st.checkbox("GU symptoms")
gynecologic_symptoms = st.checkbox("Gynecologic symptoms")
abdominal_bruit = st.checkbox("Abdominal bruit")
aaa_risk_factors = st.checkbox("AAA risk factors")

# -----------------------------
# BOTÃO
# -----------------------------
def gerar_texto_clinico(resultado):
    texto = "Patient reports low back pain"

    red_flags = resultado['resultado_red_flags']

    # Caso RED FLAG
    if resultado['categoria'] == 'red_flag':
        diagnostico = resultado['diagnostico_principal']

        if red_flags['ces']['alert']:
            bloco = red_flags['ces']
            plano = "Urgent MRI and emergency evaluation for suspected cauda equina syndrome."
        elif red_flags['infeccao']['alert']:
            bloco = red_flags['infeccao']
            plano = "Order ESR/CRP. If elevated, strongly consider urgent MRI/referral."
        elif red_flags['fratura']['alert']:
            bloco = red_flags['fratura']
            plano = "Consider spinal X-ray or other appropriate imaging to evaluate possible vertebral fracture."
        elif red_flags['malignidade']['alert']:
            bloco = red_flags['malignidade']
            plano = "Consider imaging and further evaluation for possible malignancy."
        else:
            bloco = {'positive': [], 'negative': []}
            plano = "Clinical follow-up."

        positivos = bloco['positive']
        negativos = bloco['negative'][:6]

        if positivos:
            texto += " associated with " + ", ".join(positivos) + ".\n"
        else:
            texto += ".\n"

        if negativos:
            texto += "Denies " + ", ".join(negativos) + ".\n"

        texto += f"\nClinical impression: {diagnostico}.\n"
        texto += f"Plan: {plano}"
        return texto

    # Caso NON-SPINAL
    if resultado['categoria'] == 'non_spinal':
        visceral = resultado['resultado_visceral']['resultado_visceral']
        positivos = visceral['positive']

        if positivos:
            texto += " associated with " + ", ".join(positivos) + ".\n"
        else:
            texto += ".\n"

        texto += "Denies major spinal red flags.\n"
        texto += f"\nClinical impression: {resultado['diagnostico_principal']}.\n"
        texto += f"Plan: {resultado['resultado_visceral']['action']}"
        return texto


    # Caso HORIZONTAL
    horizontal = resultado['resultado_horizontal']
    diagnostico = horizontal['diagnostico_principal']

    if horizontal['resultado_radiculopatia']['alert']:
        bloco_principal = horizontal['resultado_radiculopatia']
    elif horizontal['resultado_estenose']['alert']:
        bloco_principal = horizontal['resultado_estenose']
    else:
        bloco_principal = None

    if bloco_principal and bloco_principal['positive']:
        texto += " associated with " + ", ".join(bloco_principal['positive']) + ".\n"
    else:
        texto += ".\n"

    # Negativas documentais dos red flags
    
    negativas_importantes = [
    'urinary retention',
    'saddle anesthesia',
    'fever',
    'recent bacterial infection',
    'major trauma',
    'history of cancer',
    'unexplained weight loss',
    'night/rest pain'
]
    
    negativas_red_flags = []

    for nome_bloco in ['ces', 'infeccao', 'fratura', 'malignidade']:
        for item in red_flags[nome_bloco]['negative']:
            if item in negativas_importantes:
                negativas_red_flags.append(item)

    negativas_red_flags = list(dict.fromkeys(negativas_red_flags))

    if negativas_red_flags:
        texto += "Denies " + ", ".join(negativas_red_flags[:10]) + ".\n"

    texto += f"\nClinical impression: {diagnostico}.\n"
    texto += f"Plan: {horizontal['action']}"
    return texto


def salvar_caso_csv(dados, resultado):
    arquivo = 'lombalgia_cases.csv'

    cabecalho = ['timestamp', 'diagnostico_principal', 'categoria']

    for chave in dados.keys():
        cabecalho.append(chave)

    escrever_cabecalho = False

    try:
        with open(arquivo, 'r', newline='', encoding='utf-8') as f:
            pass
    except FileNotFoundError:
        escrever_cabecalho = True

    linha = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'diagnostico_principal': resultado['diagnostico_principal'],
        'categoria': resultado['categoria']
    }

    for chave, valor in dados.items():
        linha[chave] = valor

    with open(arquivo, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=cabecalho)
        if escrever_cabecalho:
            writer.writeheader()
        writer.writerow(linha)


if st.button("Evaluate patient"):

    dados = {
        # (mantém seu dicionário exatamente igual)
        'urinary_retention': urinary_retention,
        'bowel_dysfunction': bowel_dysfunction,
        'reduced_perianal_sensation': reduced_perianal_sensation,
        'saddle_anesthesia': saddle_anesthesia,
        'bilateral_leg_weakness': bilateral_leg_weakness,
        'bilateral_sciatica': bilateral_sciatica,

        'fever': fever,
        'immunosuppression': immunosuppression,
        'recent_bacterial_infection': recent_bacterial_infection,
        'recent_spinal_procedure': recent_spinal_procedure,
        'indwelling_catheter_dialysis': indwelling_catheter_dialysis,

        'major_trauma': major_trauma,
        'minor_trauma': minor_trauma,
        'age_70_or_more': age_70_or_more,
        'osteoporosis': osteoporosis,
        'chronic_steroid_use': chronic_steroid_use,

        'history_of_cancer': history_of_cancer,
        'unexplained_weight_loss': unexplained_weight_loss,
        'night_pain_or_rest_pain': night_pain_or_rest_pain,

        'dermatomal_leg_pain_below_knee': dermatomal_leg_pain_below_knee,
        'crossed_slr': crossed_slr,
        'focal_neurologic_deficit': focal_neurologic_deficit,
        'positive_slr': positive_slr,
        'leg_pain_worse_than_back': leg_pain_worse_than_back,
        'pain_with_cough_sneeze': pain_with_cough_sneeze,
        'age_30_50': age_30_50,

        'neurogenic_claudication': neurogenic_claudication,
        'relief_with_flexion': relief_with_flexion,
        'bilateral_leg_symptoms': bilateral_leg_symptoms,
        'age_over_60': age_over_60,
        'poor_balance': poor_balance,
        'pain_with_extension': pain_with_extension,
        'sensory_deficit': sensory_deficit,

        'gi_symptoms': gi_symptoms,
        'gu_symptoms': gu_symptoms,
        'gynecologic_symptoms': gynecologic_symptoms,
        'abdominal_bruit': abdominal_bruit,
        'aaa_risk_factors': aaa_risk_factors
    }

    st.session_state['dados'] = dados
    st.session_state['resultado'] = interpretar_lombalgia(dados)


# -----------------------------
# RESULTADOS (FORA DO BOTÃO)
# -----------------------------
if 'resultado' in st.session_state:

    resultado = st.session_state['resultado']

    st.divider()

    st.subheader("Diagnosis")
    st.success(resultado['diagnostico_principal'])

    st.subheader("Suggested action")
    if 'resultado_horizontal' in resultado:
        st.write(resultado['resultado_horizontal']['action'])
    elif 'resultado_visceral' in resultado:
        st.write(resultado['resultado_visceral']['action'])
    else:
        st.write("Follow red flag pathway")

    if resultado['categoria'] == 'red_flag':
        st.error("RED FLAG DETECTED")

    st.divider()

    if st.button("Generate clinical note"):
        texto = gerar_texto_clinico(resultado)

        st.subheader("Clinical Note")
        st.text_area("Copy this:", texto, height=200)

