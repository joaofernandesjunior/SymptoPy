print('===== Low Back Pain =====')

def yes_no(prompt):
    while True:
        ans = input(prompt).lower().strip()
        if ans in ['y', 'n']:
            return ans
        print('Invalid answer. Please enter y or n.')

results = []

ces_score = 0
infection_score = 0
fracture_score = 0

ces_positive = []
ces_negative = []

inf_positive = []
inf_negative = [] 


fracture_positive = []
fracture_negative = []

subjective_positive = []
subjective_negative = []

found_specific = False

while True:
    dor = yes_no('Does the patient have back pain? [y/n] ')
    if dor not in ['y','n']:
        print('Invalid answer')
    else: 
        break
if dor == 'n':
    print('No back pain. End of program.')
    exit()
else:
    ur = yes_no('Does the patient have urinary retention? [y/n] ')
    if ur == 'y':
        ces_score += 2
        ces_positive.append('urinary retention')
    else:
        ces_negative.append('urinary retention')
    
    sa = yes_no('Does the patient have saddle anesthesia? [y/n] ')
    if sa == 'y':
        ces_score += 2
        ces_positive.append('saddle anesthesia')
    else:
        ces_negative.append('saddle anesthesia')
   
    blw = yes_no('Does the patient have bilateral leg weakness? [y/n] ')
    if blw == 'y':
        ces_score += 1
        ces_positive.append('bilateral leg weakness')
    else:
        ces_negative.append('bilateral leg weakness')
   
    bs = yes_no('Does the patient have bilateral sciatica? [y/n] ')
    if bs == 'y':
        ces_score += 1
        ces_positive.append('bilateral sciatica')
    else: 
        ces_negative.append('bilateral sciatica')

    if ces_score >= 2:
        results.append('Immediate MRI to rule out cauda equina syndrome')
        found_specific = True
    
    else:

        rsp = yes_no('Does the patient have recent spine procedure or instrumentation? [y/n] ')
        if rsp == 'y':
            infection_score += 2
            inf_positive.append('spine procedure or instrumentation')
        else:
            inf_negative.append('spine procedure or instrumentation')
    
        sib = yes_no('Does the patient have recent skin infection or bacteremia? [y/n] ')
        if sib == 'y':
            infection_score += 2
            inf_positive.append('skin infection or bacteremia')
        else:
            inf_negative.append('skin infection or bacteremia')
    
        fvr = yes_no('Does the patient have fever? [y/n] ')
        if fvr == 'y':
            infection_score += 1
            inf_positive.append('fever')
        else:
            inf_negative.append('fever')
    
        imnsp = yes_no('Is the patient immunosuppressed? [y/n] ')
        if imnsp == 'y':
            infection_score += 1
            inf_positive.append('immunosuppression')
        else:
            inf_negative.append('immunosuppression')
        
        uti = yes_no('Does the patient have recent urinary tract infection? [y/n] ')
        if uti == 'y':
            infection_score += 1
            inf_positive.append('urinary tract infection') 
        else:
            inf_negative.append('urinary tract infection')

        if infection_score >= 2:

            results.append('Order ESR/CRP + Labs + MRI to evaluate possible spinal infection')
            found_specific = True
        
        elif infection_score == 1: 

            results.append('Consider ESR/CRP if symptoms persist or clinical suspicion remains')
        
        cancer = yes_no('Does the patient have active cancer or history of cancer? [y/n] ')

        if cancer == 'y':
            results.append('Consider malignancy workup / MRI due to cancer history')
            found_specific = True
        else:
            trm = yes_no('Is there a history of trauma? [y/n] ')
            if trm == 'y':
                fracture_score += 3
                fracture_positive.append('history of trauma')
            else: 
                fracture_negative.append('history of trauma')       

            age70 = yes_no('Is the patient age 70 or older? [y/n] ')

            if age70 == 'y':
                fracture_score += 2
                fracture_positive.append('age ≥70')
            else:
                fracture_negative.append('age ≥70')

            female = yes_no('Is the patient female? [y/n] ')

            if female == 'y':
                fracture_score += 1
                fracture_positive.append('female sex')
            else:
                fracture_negative.append('female sex')

            steroids = yes_no('Does the patient use corticosteroids chronically? [y/n] ')

            if steroids == 'y':
                fracture_score += 2
                fracture_positive.append('chronic corticosteroid use')
            else:
                fracture_negative.append('chronic corticosteroid use')

            osteoporosis = yes_no('Does the patient have a history of osteoporosis? [y/n] ')

            if osteoporosis == 'y':
                fracture_score += 2
                fracture_positive.append('history of osteoporosis')
            else:
                fracture_negative.append('history of osteoporosis')

            if fracture_score >= 4:
                results.append('Recommend spine radiograph to evaluate possible compression fracture')
                found_specific = True

            elif fracture_score >= 2:
                results.append('Consider spine radiograph if clinically appropriate')
                    
                below_knee = yes_no('Does the pain radiate below the knee? [y/n] ')

                slr = yes_no('Is the straight-leg raise test positive? [y/n] ')

                weakness = yes_no('Is there focal motor weakness? [y/n] ')

                if (below_knee == 'y' and slr == 'y') or weakness == 'y':

                    results.append('Pattern consistent with lumbar radiculopathy')
                    results.append('Consider MRI if severe or progressive neurologic findings')
                    found_specific = True
                else:
                    bilateral = yes_no('Are symptoms bilateral? [y/n] ')

                    walking = yes_no('Are symptoms worse with walking or standing? [y/n] ')

                    sitting = yes_no('Are symptoms relieved by sitting? [y/n] ')

                    flexion = yes_no('Are symptoms relieved by forward flexion? [y/n] ')

                    if bilateral == 'y' and walking == 'y' and (sitting == 'y' or flexion == 'y'):
                            results.append('Pattern consistent with lumbar spinal stenosis')
                            found_specific = True
                        
                    else:
                        flank = yes_no('Is there flank pain? [y/n] ')

                        dysuria = yes_no('Is there dysuria? [y/n] ')

                        hematuria = yes_no('Is there hematuria? [y/n] ')

                        urinary_fever = yes_no('Is there fever with urinary symptoms? [y/n] ')

                        if flank == 'y' or dysuria == 'y' or hematuria == 'y' or urinary_fever == 'y':
                            results.append('Consider non-spinal renal or urinary cause of back pain')
                            found_specific = True

                        else: 
                            if not found_specific:
                                results.append('Likely mechanical or nonspecific low back pain')


print('\n===== CLINICAL IMPRESSION =====')
for r in results:
    print('-', r)

print('\n===== RED FLAG SUMMARY =====')

if len(ces_positive) > 0:
    print('CES positive findings:', ', '.join(ces_positive) + '.')
if len(ces_negative) > 0:
    print('CES negative findings:', ', '.join(ces_negative) + '.')

if len(inf_positive) > 0:
    print('Infectious red flags:', ', '.join(inf_positive) + '.')
if len(inf_negative) > 0:
    print('Infectious risk factors absent:', ', '.join(inf_negative) + '.')

if len(fracture_positive) > 0:
    print('Fracture risk factors present:', ', '.join(fracture_positive) + '.')
if len(fracture_negative) > 0:
    print('Fracture risk factors absent:', ', '.join(fracture_negative) + '.')

subjective_positive.extend(ces_positive)
subjective_positive.extend(inf_positive)
subjective_positive.extend(fracture_positive)

subjective_negative.extend(ces_negative)
subjective_negative.extend(inf_negative)
subjective_negative.extend(fracture_negative)

print('\n===== SUBJECTIVE =====')

if len(subjective_positive) > 0:
    print('Patient with low back pain associated with ' + ', '.join(subjective_positive) + '.')

if len(subjective_negative) > 0:
    print('Denies ' + ', '.join(subjective_negative) + '.')
