# SymptoPy

A Python-driven clinical reasoning engine designed to structure diagnostic thinking through syndromic flowcharts.

## Overview

SymptoPy transforms clinical reasoning into a structured, step-by-step decision process using binary inputs (yes/no questions), inspired by:

- Symptom to Diagnosis (S2D)
- Evidence-based clinical flowcharts
- OpenEvidence-assisted literature exploration
- Real-world clinical experience

The goal is to reduce cognitive overload, standardize reasoning, and improve diagnostic clarity.

---

## Current Module

### Low Back Pain Diagnostic Engine

This module evaluates low back pain through a hierarchical approach:

1. **Emergency conditions (hard gates)**
   - Cauda equina syndrome

2. **Serious pathology screening**
   - Spinal infection
   - Malignancy (cancer history)
   - Compression fracture

3. **Pattern recognition**
   - Lumbar radiculopathy
   - Spinal stenosis
   - Visceral (renal/urinary) causes

4. **Fallback**
   - Mechanical / nonspecific low back pain

---

## Features

- Structured yes/no clinical questioning
- Red flag detection
- Weighted scoring systems
- Pattern-based diagnosis (not only scores)
- Automatic clinical output:
  - Clinical Impression
  - Red Flag Summary
  - Subjective (ready-to-use text)


## Example Output
===== CLINICAL IMPRESSION =====

Pattern consistent with lumbar radiculopathy

===== RED FLAG SUMMARY =====
CES negative findings: ...
Infectious risk factors absent: ...

===== SUBJECTIVE =====
Patient with low back pain associated with ...
Denies ...

## Philosophy

This tool is not meant to replace clinical judgment.

It is designed to:

- Support structured thinking
- Reduce missed red flags
- Improve efficiency in repetitive assessments
- Serve as a personal clinical reasoning assistant
- Help to improve the medical dec
- Support clinical decision-making where advanced imaging or complex labs are unavailable, focusing on high-probability clinical clusters
- Improve referral accuracy, ensuring that specialized resources are directed to the cases that truly require them

---

## Future Directions

- Expand to other syndromes (chest pain, dyspnea, abdominal pain)
- Build graphical interface (Streamlit)
- Modularize diagnostic branches
- Improve narrative clinical output
- Integrate probabilistic reasoning

---

## Disclaimer

This project is for educational and personal use only.  
It should not be used as a standalone medical decision-making tool.

---

## Author

Joao Fernandes de Souza Junior  
Medical student building tools for structured clinical reasoning and decision support.
