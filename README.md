# SymptoPy

A Python-driven clinical reasoning engine designed to structure diagnostic thinking through modular syndromic pathways.

---

## Overview

SymptoPy is a lightweight decision-support system aimed at **primary care environments**, where rapid and safe clinical reasoning is critical.

Inspired by:

- Symptom to Diagnosis (S2D)
- Evidence-based clinical flowcharts
- OpenEvidence-assisted literature review
- Real-world frontline medical experience

The goal is to:

- Reduce cognitive overload  
- Improve diagnostic safety  
- Prevent missed critical conditions  
- Standardize clinical reasoning  

---

## Architecture

SymptoPy is built around a **modular system**, where each clinical syndrome is an independent diagnostic engine.

modules/
├── low_back_pain/
├── chest_pain/ (future)
├── dyspnea/ (future)


Each module contains:

- `core/` → clinical reasoning engine  
- `app/` → Streamlit interface  
- `tests/` → validation cases  
- `README.md` → module-specific documentation  

---

## Current Modules

### Low Back Pain
Focus on:

- Red flag detection (CES, infection, malignancy, fracture)
- Radiculopathy vs stenosis differentiation
- Identification of nonspecific mechanical pain
- Detection of non-spinal causes (GI/GU/vascular)

---

## Philosophy

SymptoPy is **not a diagnostic replacement tool**.

It is designed to:

- Support clinicians  
- Improve consistency  
- Reduce missed diagnoses  
- Assist in documentation  

---

## ⚠️ Disclaimer

This tool is intended for **educational and support purposes only**.  
Clinical decisions must always be made by a qualified healthcare professional.

---

## Future Directions

- Additional syndromes (chest pain, dyspnea, headache)
- Reasoning transparency layer
- Clinical validation datasets
- Possible ML-assisted weighting refinement

---

## 👨‍⚕️ Author

Developed with a focus on real-world primary care challenges, aiming to bridge medicine and practical software solutions.
