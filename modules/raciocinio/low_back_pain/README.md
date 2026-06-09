# Low Back Pain Clinical Decision Tool

A lightweight clinical decision support tool designed for **primary care evaluation of low back pain**, with focus on **early identification of serious conditions and efficient diagnostic reasoning**.

---

## Overview

Low back pain is one of the most common complaints in primary care, yet it carries the risk of missing serious conditions such as:

- Cauda equina syndrome  
- Spinal infection  
- Vertebral fracture  
- Malignancy  

This project was built to support clinicians in:

- Rapidly identifying **red flags**
- Structuring clinical reasoning
- Avoiding missed diagnoses
- Generating structured clinical documentation

---

## Clinical Design Philosophy

This tool is NOT intended to replace clinical judgment.

Instead, it acts as:

> A **cognitive support system** to assist physicians in remembering critical diagnostic pathways and documenting reasoning clearly.

---

## Methodology

The clinical logic is based on:

- Evidence-based medical literature  
- Diagnostic reasoning frameworks (e.g. *Symptom to Diagnosis*)  
- Sensitivity and specificity-driven feature weighting  
- Adaptation to **real-world primary care settings**, including low-resource environments  

---

## Architecture

### 1. Vertical Red Flag Screening
- Cauda equina syndrome
- Infection
- Fracture
- Malignancy

Immediate prioritization based on severity

---

### 2. Horizontal Diagnostic Flow
- Lumbar radiculopathy
- Lumbar spinal stenosis
- Nonspecific mechanical low back pain (default)

Modular scoring systems for each condition

---

### 3. Non-Spinal (Visceral) Screening
- GI, GU, gynecologic symptoms
- Abdominal bruit
- AAA risk factors

Redirects to appropriate diagnostic pathways

---

## Clinical Output

The system generates:

- Structured diagnostic suggestion
- Recommended action
- Automatically generated **clinical note (SOAP-style Subjective)**

Example:

Patient reports low back pain associated with dermatomal leg pain below knee.
Denies urinary retention, saddle anesthesia, fever.

Clinical impression: Likely lumbar radiculopathy.
Plan: Conservative management. Consider MRI if progression.


---

## Goal

To improve:

- Diagnostic safety  
- Clinical efficiency  
- Documentation quality  

Especially in:

- Primary care  
- Emergency settings  
- Low-resource environments  

---

## Disclaimer

This tool is intended for **clinical support only**.

It does NOT replace:
- Clinical judgment
- Physical examination
- Medical responsibility

---

## Future Improvements

- Enhanced clinical note generation with reasoning explanation  
- Integration with other syndrome modules (GI, GU, gynecology)  
- Risk factor engine (comorbidities, medications, demographics)  
- Data-driven validation using real-world cases  

---

## Author

Developed as an independent clinical tool combining:

- Medical training  
- Software development  
- Evidence-based reasoning  

---

## Tech Stack

- Python  
- Streamlit  
- Modular clinical logic engine  

---

## Status

✅ Functional prototype  
🚧 Continuous refinement  

---
