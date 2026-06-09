"""
Gera referência clínica SymptoPy — Excel de Protocolos
Cobre todos os 40 módulos: etiologia + clínica + tratamento + red flags
"""

from openpyxl import Workbook
from openpyxl.styles import (Font, PatternFill, Alignment, Border, Side,
                              GradientFill)
from openpyxl.utils import get_column_letter

wb = Workbook()


def _darken(hex_color):
    r = max(0, int(hex_color[0:2], 16) - 8)
    g = max(0, int(hex_color[2:4], 16) - 8)
    b = max(0, int(hex_color[4:6], 16) - 8)
    return f'{r:02X}{g:02X}{b:02X}'

# ─────────────────────────────────────────────────────────────────────────────
# PALETA
# ─────────────────────────────────────────────────────────────────────────────
C_BG_DARK   = '0D1117'   # fundo escuro
C_HDR_BLUE  = '0D2137'   # cabeçalho azul escuro
C_HDR_TEXT  = 'C9D1D9'   # texto cabeçalho
C_ACCENT    = '58A6FF'   # azul claro
C_RED       = 'FF6B6B'   # alerta vermelho
C_YELLOW    = 'F0B429'   # amarelo atenção
C_GREEN     = '3FB950'   # verde OK
C_BAND1     = '161B22'   # linha par
C_BAND2     = '0D1117'   # linha ímpar
C_WHITE     = 'C9D1D9'   # texto corpo

# Sistemas — cores
C_SYS = {
    'Respiratório':     '1C4966',
    'Cardiovascular':   '5C1B1B',
    'Gastro/Abdominal': '1C3D1C',
    'Infectologia':     '3D2B00',
    'MSK':              '2D1C4E',
    'Neurologia':       '1C3D40',
    'Urologia':         '1C2D3D',
    'ORL':              '3D1C2D',
    'Oftalmo':          '1C3D30',
    'Hematologia':      '3D1C1C',
    'Dermatologia':     '2D3D1C',
    'Geral':            '252525',
}

def hdr_fill(hex_color):
    return PatternFill('solid', fgColor=hex_color)

def body_fill(hex_color):
    return PatternFill('solid', fgColor=hex_color)

def font(bold=False, color=C_WHITE, size=10, italic=False):
    return Font(name='Consolas', bold=bold, color=color, size=size, italic=italic)

def center():
    return Alignment(horizontal='center', vertical='center', wrap_text=True)

def left():
    return Alignment(horizontal='left', vertical='top', wrap_text=True)

thin = Side(style='thin', color='30363D')
thick = Side(style='medium', color='58A6FF')
border_thin  = Border(left=thin, right=thin, top=thin, bottom=thin)
border_thick = Border(left=thick, right=thick, top=thick, bottom=thick)


# ─────────────────────────────────────────────────────────────────────────────
# DADOS — 40 módulos
# ─────────────────────────────────────────────────────────────────────────────
# Colunas: Sistema | Queixa/Módulo | Etiologia/Diagnóstico | Clínica-Chave |
#          Exames Iniciais | Tratamento 1ª Linha | Red Flags / Alarme |
#          Encaminhamento | Fonte/Guideline

DADOS = [
    # ── RESPIRATÓRIO ──────────────────────────────────────────────────────────
    ['Respiratório','Dispneia','Asma (crise)','Sibilos expiratórios, dispneia paroxística, tosse noturna, reversibilidade ao BD','Pico-fluxo, SpO₂','Salbutamol 2,5 mg NEB + ipratrópio; corticoide sistêmico se moderada-grave','SpO₂ <92%, fala em palavras, uso de musculatura acessória, silêncio torácico','PS se grave; pneumo se refratário','GINA 2025'],
    ['Respiratório','Dispneia','DPOC (exacerbação)','Piora dispneia + ↑ volume/purulência escarro (critérios Anthonisen), tabagismo','SpO₂, gasometria, Rx tórax','Salbutamol + ipratrópio NEB; prednisona 40 mg × 5d; ATB se ≥2 critérios Anthonisen','SpO₂ <88%, confusão mental, FR >30, uso de músculos acessórios','PS/internação; pneumo ambulatorial','GOLD 2026'],
    ['Respiratório','Dispneia','TEP','Dispneia súbita + dor pleurítica + taquicardia; Wells ≥2 + D-dímero','D-dímero, AngioTC tórax, ECG (S1Q3T3)','Anticoagulação imediata (HBPM ou rivaroxabana); trombólise se instável','Instabilidade hemodinâmica, síncope, hipóxia grave','PS urgente','ESC 2019'],
    ['Respiratório','Dispneia','Pneumonia','Febre + tosse produtiva + crepitantes + opacidade Rx','Rx tórax, hemograma, PCR','Amoxicilina 875 mg 12/12h × 5–7d; azitromicina se atípica; CURB-65 ≥3 → IV','SpO₂ <92%, FR >30, confusão, PA <90/60','PS se CURB-65 ≥2-3; pneumo','BTS / ATS-IDSA'],
    ['Respiratório','Tosse','Tosse aguda viral','Tosse < 3 sem, IVAS prévia, afebril ou febre baixa','Clínico','Mel de abelha, codeína se intratável; não indicar ATB rotineiro','Hemoptise, perda de peso, febre > 3 sem, SpO₂ ↓','Não requer','Cochrane / BTS'],
    ['Respiratório','Tosse','Tosse crônica — UACS','Tosse >8 sem, gotejamento pós-nasal, clareamento de garganta','Clínico; Rx seios se suspeita sinusite','Anti-histamínico de 1ª geração + descongestionante; corticoide nasal','Hemoptise, perda peso, disfagia, adenopatia','Pneumo; ORL se rinossinusite','Irwin Algorithm'],
    ['Respiratório','Tosse','Tosse crônica — DRGE/LPR','Tosse pós-prandial, posicional, azia; piora ao deitar','Endoscopia, pHmetria se inconclusivo','IBP 2×/dia × 8–12 sem; elevação cabeceira, dieta','Disfagia, odinofagia, hematêmese','Gastro','Irwin Algorithm'],
    ['Respiratório','Tosse','Tosse crônica — IECA','Tosse seca persistente em uso de IECA (captopril, enalapril)','Clínico + suspensão teste','Trocar IECA por BRA (losartana/valsartana); resolução em 1–4 sem','—','Cardiologista / clínico','Cochrane'],
    ['Respiratório','Asma','Asma controlada (retorno)','Tosse noturna, sibilos, restrição de atividades; ACT < 20 = não controlada','PFE, espirometria','Step-up GINA: SABA + ICS/LABA; controle de gatilhos; vacina influenza','Crise grave, SpO₂ <92%','Pneumo','GINA 2025'],
    ['Respiratório','DPOC','DPOC estável (retorno)','Dispneia crônica progressiva, tosse crônica, tabagismo; CAT score','Espirometria (obrigatória), CAT, mMRC','LAMA ± LABA; vacinação; reabilitação pulmonar; cessação tabagismo','Exacerbação frequente (≥2/ano)','Pneumo; reabilitação','GOLD 2026'],

    # ── CARDIOVASCULAR ────────────────────────────────────────────────────────
    ['Cardiovascular','Palpitação','FA nova (< 48h)','Palpitação irregular, "coração disparado", dispneia; FA no ECG','ECG 12 derivações, TSH, hemograma','Controle FC: metoprolol 25–50 mg VO; cardioversão química: propafenona 300 mg (sem cardiopatia)','Instabilidade hemodinâmica → cardioversão elétrica imediata','Cardiologia; DOAC se CHA₂DS₂-VASc ≥2','AHA/ACC/HRS 2023'],
    ['Cardiovascular','Palpitação','FA crônica','Histórico FA, ECG confirma; CHA₂DS₂-VASc para risco tromboembólico','ECG, ecocardiograma, função renal/hepática','Controle FC: metoprolol; anticoagulação: apixabana 5 mg 12/12h (1ª linha) ou rivaroxabana','Síncope, IC descompensada, AVC','Cardiologia','AHA/ACC/HRS 2023'],
    ['Cardiovascular','Palpitação','TSV paroxística','Início/término súbito, FC 150–250 bpm regular; ECG: taquicardia QRS estreito','ECG durante crise','Valsalva modificada (supino + pernas elevadas); adenosina 6 mg IV; metoprolol profilático','WPW associado (NUNCA verapamil/digoxina)','Eletrofisiologia; ablação','AHA/ACC SVT 2015'],
    ['Cardiovascular','Palpitação','WPW','Delta wave no ECG, taquicardia pré-excitação','ECG, Holter, estudo eletrofisiológico','Ablação por radiofrequência (curativa); NUNCA verapamil ou digoxina na FA + WPW','FA + WPW = emergência → cardioversão','Eletrofisiologia urgente','AHA/ACC SVT 2015'],
    ['Cardiovascular','Síncope','Síncope vasovagal','Pródromo (calor, náusea, visão turva), gatilho ortostático; ECG normal','ECG 12d, glicemia, hemograma','Manobras físicas (cruzar pernas, apertar mãos), hidratação, evitar gatilhos','Sem pródromo, esforço, cardiopatia, QT longo, Brugada','Cardiologia se CSRS ≥3; holter','ESC 2018'],
    ['Cardiovascular','Síncope','Síncope cardíaca','Sem pródromo, durante esforço, cardiopatia prévia; ECG anormal','ECG, ecocardiograma, Holter 24h','Tratar causa (ablação, CDI, marca-passo)','Alto risco: Brugada, QT longo, BRE novo, FA rápida','Cardiologia urgente','ESC 2018'],
    ['Cardiovascular','Edema MMII','ICC descompensada','Edema bilateral mole, dispneia, ortopneia, DPN, crepitantes bilaterais','Rx tórax, BNP/NT-proBNP, ECG, eco','Furosemida IV/VO; espironolactona; IECA/BRA; restrição hídrica','Anasarca, SpO₂ ↓, arritmia grave','Cardiologia / internação','AHA ICC 2022'],
    ['Cardiovascular','Edema MMII','TVP','Edema unilateral + dor + empastamento panturrilha; Wells ≥2','Eco-Doppler venoso; D-dímero','Rivaroxabana 15 mg 12/12h × 21d → 20 mg/dia; ou apixabana','TEP (dispneia súbita + dor pleurítica)','Angiologia/vascular','ESC-ERS 2019'],

    # ── GASTRO/ABDOMINAL ──────────────────────────────────────────────────────
    ['Gastro/Abdominal','Dor Abdominal','Úlcera péptica / H. pylori','Epigastralgia em queimação, melhora com antiácidos; H. pylori+','Endoscopia; teste respiratório; antígeno fecal HP','Omeprazol 20 mg + amoxicilina 1g + claritromicina 500 mg (ou quadrupla bismuto 14d)','Melena, hematêmese, rigidez abdominal','Gastro; cirurgia se perfuração','V Consenso Brasileiro 2025'],
    ['Gastro/Abdominal','Dor Abdominal','Apendicite aguda','Dor migratória periumbilical → FID; Alvarado ≥7; febre; Blumberg+','Hemograma, PCR; US abdome; TC se dúvida','Cirurgia urgente (laparoscopia); ATB profilático pré-op','Rigidez abdominal, febre alta, Blumberg+','Cirurgia urgente','JAMA 2018'],
    ['Gastro/Abdominal','Dor Abdominal','Cólica biliar / colecistite','Dor cólica FSD pós-gordurosa, irradiação escápula; Murphy+','US abdome; hemograma; TGO/TGP/bilirrubinas','Analgesia (dipirona + escopolamina); colecistectomia eletiva; ATB se colecistite aguda','Febre, icterícia, colangite (tríade de Charcot) → PS','Cirurgia; gastro se coledocolitíase','ACG 2020'],
    ['Gastro/Abdominal','Dor Abdominal','SII (Cólon Irritável)','Dor crônica + alteração hábito + alívio com evacuação; Roma IV+','Clínico; hemograma, TSH, calprotectina para excluir orgânico','Fibra, probióticos; SII-C: linaclotida; SII-D: loperamida, rifaximina; TCC','Perda peso, sangue nas fezes, febre, <45 anos + histórico familiar CCR','Gastro se refratário','Roma IV'],
    ['Gastro/Abdominal','Dor Abdominal','Diverticulite aguda','Dor FIE + febre + ↑ leucócitos; TC confirma','TC abdome com contraste','ATB oral (amoxicilina-clavulanato 875 mg 12/12h × 7–10d) se não complicada; internação se abscesso/perfuração','Peritonite, pneumoperitônio, abscesso','Cirurgia se complicada','JAMA 2024'],
    ['Gastro/Abdominal','Diarreia','GECA viral','Diarreia aquosa, náusea/vômito, autolimitada < 5d, afebril ou febre baixa','Clínico; EAS se persistente','Soro de reidratação oral; dieta BRAT; zinco em < 5 anos; evitar antiperistálticos','Sinais de choque, sangue nas fezes, febre alta, imunossuprimido','Ambulatório; PS se desidratação grave','OMS 2023'],
    ['Gastro/Abdominal','Diarreia','C. difficile','Diarreia aquosa pós-ATB, cólica abdominal; PCR C. diff +','PCR C. diff; colonoscopia se megacólon suspeito','Vancomicina VO 125 mg 6/6h × 10d; fidaxomicina se recorrência; EVITAR metronidazol como 1ª linha','Megacólon tóxico (abdome timpânico + febre + leucocitose > 25k)','Gastro; cirurgia se megacólon','IDSA 2021'],
    ['Gastro/Abdominal','Diarreia','Parasitose (Giardia/Ameba)','Diarreia crônica, esteatorreia, flatulência; viagem, água não tratada','EPS × 3; antígeno fecal; ELISA','Giardia: metronidazol 500 mg 8/8h × 7d; Ameba: metronidazol + paromomicina (luminal)','Ameba invasiva (febre + sangue + dor)','Não requer em geral','PAHO'],
    ['Gastro/Abdominal','HDA','HDA baixo risco (GBS 0–1)','Hematêmese/melena, GBS 0–1: Hb >13, BUN <18, PAS >110, sem síncope/cirrose/ICC','Hemograma, BUN, Cr, tipagem','Alta; IBP VO; endoscopia eletiva < 2 semanas','Ressangramento (nova hematêmese, queda Hb, instabilidade)','Gastro ambulatorial','ACG 2023; BSG 2021'],
    ['Gastro/Abdominal','HDA','HDA não-variceal (GBS ≥2)','Hematêmese/melena, GBS ≥2; sem estigmas de hepatopatia','Hemograma, coagulação, BUN/Cr, tipagem + prova cruzada','IBP IV 80 mg bolus → 8 mg/h; eritromicina 250 mg IV pré-endoscopia; endoscopia < 24h','Instabilidade, Hb < 7 sem melhora','Gastro/internação; endoscopia urgente','ACG 2023; BSG 2021'],
    ['Gastro/Abdominal','HDA','HDA variceal','Hematêmese + cirrose + estigmas de HTP; varizes em endoscopia','Hemograma, coagulação, TGO/TGP, albumina','Octreotida 50 mcg IV + ceftriaxona 1g/dia IMEDIATAMENTE; endoscopia < 12h; ligadura elástica','Sangramento maciço incontrolável → balão Sengstaken-Blakemore','Gastro urgente; hepatologia; TIPS se refratário','ACG 2023; BSG 2021'],
    ['Gastro/Abdominal','HDB','HDB — Hemorroida','Sangue vivo no papel/vaso, sem dor abdominal; anuscopia confirma','Anuscopia; colonoscopia se > 40 anos','Tópico (hidrocortisona + lidocaína); fibra; grau III–IV: ligadura elástica','Sangramento maciço, Oakland > 8','Coloproctologia se grau III–IV','ACG 2023; AGA 2023'],
    ['Gastro/Abdominal','HDB','HDB — Fissura Anal','Dor intensa à evacuação + sangue vivo no papel; exame anuscopia','Clínico + anuscopia','Nitroglicerina 0,2–0,4% pomada 2×/dia × 6–8 sem (1ª linha); fibra + amolecedor fezes','Esfincterotomia: fissura crônica refratária','Coloproctologia se refratário','AGA 2023'],
    ['Gastro/Abdominal','HDB','HDB — Diverticular','Idoso + hematoquezia indolor + alto volume; Oakland > 8 → internação','Colonoscopia pós-preparo; AngioTC se instável','80–90% autolimitado; colonoscopia hemostática; embolização se refratário','Oakland > 8, instabilidade hemodinâmica → AngioTC urgente','Gastro/internação; cirurgia se refratário','ACG 2023; AGA 2023'],
    ['Gastro/Abdominal','Icterícia','Hepatite viral aguda (A/E)','Icterícia + fadiga + náusea + hepatomegalia dolorosa; anti-HAV IgM +','TGO/TGP (> 10× ULN), bilirrubinas, TP/INR, anti-HAV IgM','Suporte; repouso; evitar hepatotóxicos; notificação compulsória (hepatite A)','INR > 1,5, encefalopatia hepática → insuficiência hepática aguda','Gastro/hepatologia; internação se INR ↑','AASLD/EASL'],
    ['Gastro/Abdominal','Icterícia','Coledocolitíase / Colangite','Tríade de Charcot (febre + dor FSD + icterícia); TGO/TGP/FA/GGT ↑','US abdome; CPRE urgente se colangite','ATB IV (piperacilina-tazobactam); CPRE urgente; colecistectomia eletiva','Sepse biliar, Pêntade de Reynolds (confusão + choque + Charcot)','Cirurgia / endoscopia urgente','ASGE 2019'],

    # ── INFECTOLOGIA ──────────────────────────────────────────────────────────
    ['Infectologia','Febre','Febre sem foco (adulto)','Febre ≥ 38°C, sem foco óbvio; avaliar tempo, viagem, imunossupressão, epidemiologia','Hemograma, PCR, EAS, Rx tórax; hemoculturas × 2 se internação','Sintomático (dipirona/paracetamol); ATB empírico APENAS se imunocompromiso ou sepse','Febre > 3 sem sem causa = FOI → investigação ampla; sinais de sepse','Internação se FOI ou sepse','Harrison; AFP 2022'],
    ['Infectologia','Arboviroses','Dengue (grupo B–D)','Febre aguda + cefaleia + mialgias + exantema; NS1 + em < 5d; leucopenia','Hemograma (leucopenia + plaquetopenia), NS1, dengue IgM','Hidratação oral/IV; dipirona; PROIBIDO AAS e AINE; monitorar plaquetas','Sinais de alarme: dor abdominal intensa, vômitos incoercíveis, sangramentos, ↑ hematócrito','PS se sinais de alarme; dengue grave → UTI','MS Brasil 2025'],
    ['Infectologia','Arboviroses','Chikungunya','Febre + artralgia intensa e simétrica (artrite) + exantema; NS1 − por padrão','Hemograma, PCR-CHIK (PCR na 1ª sem)','Analgesia: paracetamol + codeína; AINE apenas após excluir dengue (NS1 −); corticoide se artrite grave crônica','Cardite, encefalite, manifestações neurológicas graves','Reumatologia se artrite crônica','MS Brasil 2025'],
    ['Infectologia','IVAS','Faringoamigdalite (GAS)','Centor ≥3: exsudato + linfonodomegalia + febre + sem tosse; TRA +','TRA (teste rápido de antígeno); sem necessidade de cultura de rotina','Penicilina Benzatina IM DU (1ª linha); amoxicilina 500 mg 8/8h × 10d; alergia anafilática: azitromicina','Abscesso periamigdaliano: trismo + desvio úvula + voz de batata','ORL se abscesso; PS se emergência','IDSA / SBP 2023'],
    ['Infectologia','IVAS','Rinossinusite aguda bacteriana','≥ 10 dias sem melhora OU double-sickening; sem red flags neurológicos/orbitários','Clínico; TC seios apenas se RSC ou complicação suspeita','Amoxicilina 875 mg 12/12h × 5–7d; amox-clav se risco; corticoide nasal adjuvante','Edema periorbitário, diplopia, proptose, rigidez nucal → PS imediato','ORL se RSC (≥12 sem) ou complicação','AAO-HNS 2025'],
    ['Infectologia','IVAS','Otite Média Aguda','Otalgia ± febre ± otorreia; critérios AAFP para ATB vs watchful waiting','Otoscopia','< 6m ou bilateral ou febre ≥ 39°C ou otalgia > 48h: amoxicilina 80–90 mg/kg/dia × 5–7d; WW com receita de resgate','Mastoidite (dor retroauricular + febre persistente)','ORL se falha × 2 ou mastoidite','AAP/AAFP 2022'],
    ['Infectologia','IVAS','Otite Externa','Dor + trago + canal edematoso + descarga; sem febre sistêmica','Otoscopia','Ciprofloxacino 0,3% + dexametasona gotas 2×/dia × 7d; manter canal seco','OE maligna (DM + dor intensa + tecido de granulação) → PS IV antipseudomonal','ORL se refratário','AAO-HNS 2023'],
    ['Infectologia','Celulite','Celulite não complicada (0 SIRS)','Eritema difuso + calor + edema; sem borda nítida; sem sistêmica','Clínico (sem exames rotineiros)','Cefalexina 500 mg 6/6h × 5d; erisipela: amoxicilina; alergia anafilática: clindamicina','Crepitação, necrose, dor desproporcional → fasciite','Não requer','IDSA 2014'],
    ['Infectologia','Celulite','Celulite grave (≥2 SIRS) / Erisipela bolhosa','≥ 2 critérios SIRS: febre >38,5°C + taquicardia; bolhas tensas ou hemorrágicas','Hemograma, PCR, lactato','Cefazolina 1–2 g IV q8h; MRSA suspeito: vancomicina 15–20 mg/kg IV','LRINEC ≥6, crepitação, pele violácea → fasciite necrotizante → cirurgia emergência','Internação; cirurgia se fasciite','IDSA 2014'],
    ['Infectologia','Celulite','Fasciite Necrotizante','Dor desproporcional + crepitação ± necrose ± LRINEC ≥6; progressão rápida','CBC, BMP, CRP, lactato, LRINEC; TC (não atrasar cirurgia)','Vancomicina + piperacilina-tazobactam IV; desbridamento cirúrgico urgente','Qualquer sinal clínico sobrepõe LRINEC — não esperar score para operar','Cirurgia urgente','IDSA 2014'],

    # ── MSK ───────────────────────────────────────────────────────────────────
    ['MSK','Lombalgia','Lombalgia mecânica inespecífica','Dor lombar sem irradiação; exacerbada por movimento; sem déficit neurológico; Rx/RM normal','Clínico; Rx ou RM apenas se red flags','AINEs × 5–7d (ibuprofeno 600 mg 8/8h); calor local; manter atividade','Cauda equina: bexiga/intestino + déficit bilateral → PS imediato','Fisioterapia; ortopedia se persistente > 6 sem','NICE 2023; ACP 2017'],
    ['MSK','Lombalgia','Hérnia discal com radiculopatia','Dor irradiada para membros + parestesia + Lasègue+ (L4-S1); RM confirma','RM (padrão-ouro); clínico inicial','AINEs; pregabalina se neuropático; fisioterapia; infiltração; cirurgia se falha 6–12 sem','Síndrome da cauda equina → cirurgia urgente','Ortopedia / neurocirurgia','ESC Spine 2020'],
    ['MSK','Joelho','Lesão meniscal','Dor na linha do joelho + McMurray + Thessaly; mecanismo torção','RM joelho','RICE; AINEs; fisioterapia; artroscopia se bloqueio ou falha clínica','Bloqueio articular (incapacidade de extensão) → ortopedia urgente','Ortopedia','AAOS 2021'],
    ['MSK','Joelho','Gonartrose (OA joelho)','Dor difusa, rigidez matinal < 30 min, crepitação, ↑ com atividade; Rx (pinçamento, osteófitos)','Rx joelho (AP + perfil + hôrschuch)','Paracetamol 1g 8/8h; AINE tópico (diclofenaco gel); fisioterapia; infiltração corticoide; artroplastia se refratário','Joelho muito frio, vermelho, monoartrite aguda → artrite séptica/gota → PS','Ortopedia se cirúrgico','EULAR 2019; ACR 2020'],
    ['MSK','Ombro','Tendinopatia manguito rotador','Dor ao movimento ativo > passivo; sinal do arco doloroso; drop arm test +','Clínico; US ombro','AINEs × 5d; fisioterapia rotineira (fortalecimento); infiltração corticoide se persistente','Fraqueza progressiva, perda de rotação externa → ruptura completa','Ortopedia se ruptura completa','AAOS 2020'],
    ['MSK','Coluna','Red flags lombares (sistêmicos)','Dor > 50 anos de início, febre, perda de peso, histórico Ca, não melhora com repouso','RM urgente (ou TC se contra-indicação)','Tratar causa específica; suspender AINEs','Qualquer déficit neurológico progressivo ou cauda equina','Ortopedia / oncologia urgente','ESC Spine 2020'],
    ['MSK','Fibromialgia','Fibromialgia','Dor difusa > 3 meses, fadiga, sono não-reparador, ACR 2016: WPI ≥7 + SS ≥5','Clínico; excluir hipotireoidismo, AR, LES','Exercício aeróbico (evidência A); amitriptilina 10–25 mg noite; duloxetina se humor','—','Reumatologia; fisioterapia','ACR 2016 / EULAR 2017'],
    ['MSK','Gota','Gota aguda','Monoartrite aguda + dor intensa + calor + eritema; pododáctilo 1ª MTF (podagra); hiperuricemia','Ácido úrico, hemograma, função renal; aspiração articular (cristais bifringentes)','AINEs (naproxeno 500 mg 12/12h) ou colchicina 1 mg + 0,5 mg 1h depois; corticoide se contraindicação','Artrite séptica (febre alta, bacteremia)','Reumatologia para profilaxia (alopurinol)','ACR 2020; EULAR 2022'],
    ['MSK','Tornozelo','Entorse tornozelo','Torção + dor + edema; Ottawa −: não raio-x; Ottawa +: fratura possível','Ottawa Rules; Rx se positivo','RICE (repouso, gelo, compressão, elevação) × 48h; AINEs; fisioterapia','Ottawa +, incapacidade de apoio total → Rx','Ortopedia se fratura / instabilidade crônica','AAFP 2022'],

    # ── NEUROLOGIA ────────────────────────────────────────────────────────────
    ['Neurologia','Cefaleia','Enxaqueca sem aura','Cefaleia pulsátil unilateral + náusea/vômito + foto/fonofobia; dura 4–72h; critérios ICHD-3','Clínico; RM apenas se red flags','Triptan (sumatriptana 100 mg VO); AINE (ibuprofeno 600 mg); antieméticos; profilaxia se ≥4 crises/mês','Pior cefaleia da vida, início explosivo, febre + rigidez nucal → excluir HSA/meningite → PS','Neurologia se refratária','ICHD-3 / AAN'],
    ['Neurologia','Cefaleia','Cefaleia tensional','Dor opressiva bilateral, leve-moderada, não piora com atividade, sem náusea/vômito','Clínico','Paracetamol 1g ou AAS 500 mg; evitar analgésico > 15d/mês; TCC + biofeedback para crônica','Cefaleia nova > 50 anos; déficit focal; papiledema','Neurologia se crônica refratária','ICHD-3'],
    ['Neurologia','Cefaleia','Cefaleia em salvas','Dor orbital unilateral excruciante, curta (15–180 min), lacrimejamento + ptose; circadiana','Clínico; RM para excluir lesão','O₂ 100% 15 L/min × 15 min (1ª linha); sumatriptana SC 6 mg; verapamil profilático','Nova cefaleia orbital com olho vermelho e halos → glaucoma agudo → PS','Neurologia','ICHD-3 / EHF'],
    ['Neurologia','Vertigem','VPPB (canal posterior)','Vertigem posicional breve, Dix-Hallpike +; sem déficit neurológico','Clínico (Dix-Hallpike)','Manobra de Epley (1ª linha); betaistina se não-VPPB; evitar anti-histamínicos crônicos','Diplopia, disfagia, ataxia, déficit motor → AVC cerebelo → PS','Otorrino se refratário','Cochrane 2019; AAO-HNS 2017'],
    ['Neurologia','Vertigem','Síndrome vestibular central','Vertigem contínua + HINTS+: HI negativo + nistagmo verticial/torcional + skew deviation','RM com difusão (padrão-ouro); TC tem baixa sensibilidade no AVC cerebelo em < 72h','Tratar causa (AVC: AAS + estatina; excluir dissecção vertebral)','Qualquer deficit neurológico focal com vertigem = AVC até prova em contrário','PS/AVC urgente','HINTS Study'],
    ['Neurologia','Consciência','ANC / Rebaixamento (AEIOU TIPS)','Confusão, agitação, rebaixamento; AEIOU TIPS: álcool, epilepsia, insulina, opiáceos, uremia, trauma, infecção, psíquico, stroke','Glicemia capilar (IMEDIATO), TC crânio, ECG, hemograma, EAS, TSH, triagem toxicológica','Naloxona se opiáceo suspeito; tiamina + glicose IV; tratar causa específica','Glicemia < 40 → glicose IV imediata; Glasgow ≤ 8 → via aérea','PS / UTI urgente','Harrison; ACEP'],
    ['Neurologia','Síncope','Síncope de alto risco (cardíaca)','Síncope com esforço, sem pródromo, QT longo, Brugada, BRE novo, cardiopatia estrutural','ECG 12d, ecocardiograma, Holter, monitorização','Tratar causa (CDI, ablação, marca-passo)','Qualquer sinal de cardiopatia estrutural','Cardiologia urgente','ESC 2018'],

    # ── UROLOGIA ─────────────────────────────────────────────────────────────
    ['Urologia','Queixa Urinária','Cistite simples (mulher)','Disúria + polaciúria + urgência, sem febre; EAS leucocitúria','EAS + urocultura (coleta antes de ATB)','Nitrofurantoína 100 mg 12/12h × 5d (1ª linha); fosfomicina 3g DU; cotrimoxazol × 3d','Febre, lombalgia, calafrio → pielonefrite','Não requer','JAMA 2024; IDSA'],
    ['Urologia','Queixa Urinária','Pielonefrite aguda','Febre alta + calafrio + dor lombar + disúria; punho-percussão +','EAS, urocultura, hemograma, PCR','Ceftriaxona 1–2 g IV/dia (grave) ou ciprofloxacino 500 mg 12/12h VO × 7–10d (leve-mod)','Sepse urinária, abscesso renal, cálculo obstrutivo','Internação se grave; urologia se cálculo','IDSA 2011'],
    ['Urologia','Queixa Urinária','ITU masculina / Prostatite aguda','Disúria + prostatismo + febre; próstata dolorosa ao TR; PSA elevado agudamente','EAS, urocultura, hemograma','Ciprofloxacino 500 mg 12/12h × 14–28d; ceftriaxona IM se grave; evitar sondagem vesical','Retenção urinária, sepse, abscesso prostático → internação','Urologia','EAU 2023'],
    ['Urologia','Queixa Urinária','Hematúria microscópica (micro-hematúria)','≥ 3 hemácias/campo; assintomática; risco de Ca urotélio','EAS + urocultura; US vias urinárias; cistoscopia (> 35 anos ou risco)','Tratar causa reversível (ITU, cálculo); cistoscopia + TC urograma se persiste','Hematúria macroscópica isolada = malignidade até prova em contrário → urologista urgente','Urologia','AUA 2020'],

    # ── ORL / OFTALMO ─────────────────────────────────────────────────────────
    ['ORL','Odinofagia','Faringoamigdalite viral','Centor 0–1; eritema faríngeo leve; sem exsudato; autolimitada','Clínico; TRA se incerteza','Sintomático: paracetamol, mel, gargarejos; mel + limão; NUNCA ATB','Estridor, disfagia grave, voz de batata + desvio úvula → abscesso periamigdaliano → PS','Não requer','IDSA 2023'],
    ['ORL','Odinofagia','Abscesso periamigdaliano','Trismo + voz de batata + sialorreia + desvio úvula; Centor 4','Clínico; punção confirmação','Punção/drenagem + penicilina G cristalina IV; ou amoxicilina-clavulanato VO se drenagem possível','Estridor, dificuldade respiratória → via aérea emergência','ORL / PS urgente','IDSA 2023'],
    ['ORL','Rouquidão','Laringite aguda','Rouquidão após IVAS; voz rouca; sem disfagia','Clínico (laringoscopia apenas se persistente)','Repouso vocal; hidratação; nebulização; evitar esteroides rotineiros','Rouquidão > 3 semanas → rastrear Ca laringe → laringoscopia urgente','ORL se > 3 sem','AAO-HNS 2018'],
    ['Oftalmo','Olho Vermelho','Conjuntivite bacteriana','Olho vermelho + secreção purulenta bilateral; sem dor, sem ↓AV','Clínico','Colírio tobramicina ou ciprofloxacino 4×/dia × 5–7d; higiene palpebral','Dor intensa, ↓AV, fotofobia, hifema → urgência oftalmológica','Oftalmo se não melhora em 48h','AAO 2023'],
    ['Oftalmo','Olho Vermelho','Conjuntivite viral (adenoviral)','Olho vermelho + secreção aquosa + folículos palpebral; adenopatia pré-auricular; altamente contagiosa','Clínico','Suporte: lágrima artificial, compressa fria, higiene; ISOLAMENTO; sem ATB','Ceratite subepitelial pontilhada (pode reduzir AV)','Oftalmo se ↓AV','AAO 2023'],
    ['Oftalmo','Olho Vermelho','Glaucoma agudo de ângulo fechado','Dor ocular súbita + halos + ↓AV + pupila em midríase + PIO > 35 mmHg; náusea/vômito','PIO (tonometria); biomicroscopia','Acetazolamida 500 mg IV; timolol 0,5% colírio; iridotomia a laser (definitiva)','EMERGÊNCIA OFTALMOLÓGICA — pode causar cegueira permanente em horas','Oftalmo urgente','AAO 2023'],

    # ── HEMATOLOGIA ───────────────────────────────────────────────────────────
    ['Hematologia','Anemia','Anemia ferropriva (IDA)','Fadiga + palidez + pica; Hb ↓, VCM ↓, RDW ↑, ferritina < 30; índice Mentzer > 13','Hemograma, ferritina, ferro sérico, TIBC','Sulfato ferroso 15–20 mg Fe elementar em dias alternados (Cochrane 2021 — melhor absorção); tratar causa de base','Pancitopenia, blasto, esplenomegalia → urgência hematológica','Hematologia se refratário; gastro se perda crônica suspeita','WHO 2011; Cochrane 2021'],
    ['Hematologia','Anemia','Anemia megaloblástica (B12/Folato)','Fadiga + glossite + parestesias (B12); macrocitose; VCM > 100','B12 sérica, folato, hemograma (macrócitos + hipersegmentação)','B12 < 200: cianocobalamina VO 1000–2000 mcg/dia (ou IM se neurológico/má absorção); ácido fólico 1–5 mg/dia','Deficiência B12 + déficit neurológico → neuropatia subaguda → IM obrigatório','Hematologia; gastro (doença celíaca / gastrite atrófica)','BCSH 2014; AFP 2021'],
    ['Hematologia','Anemia','Anemia hemolítica','Fadiga + icterícia + esplenomegalia; Hb ↓, RPI > 2,5, ↑ LDH, ↓ haptoglobina; Coombs','Hemograma completo, reticulócitos, LDH, haptoglobina, Coombs direto/indireto','AHAI: corticoide (prednisona 1 mg/kg/dia); transfusão se Hb < 7; rituximabe se refratário','Crise hemolítica aguda (Hb < 6, taquicardia, instabilidade)','Hematologia urgente','ASH 2021'],
    ['Hematologia','Linfadenopatia','Linfadenopatia reativa','Linfonodo < 2 cm, mole, móvel, doloroso; contexto infeccioso próximo','Hemograma, PCR, sorologias (EBV, CMV, Toxoplasma)','Tratar infecção de base; observação × 4–6 semanas','Linfonodo > 2 cm, pétreo, fixo, supraclavicular, B-symptoms → malignidade','Hematologia / oncologia','AAFP 2016; ASH'],
    ['Hematologia','Linfadenopatia','Linfoma suspeito','Linfonodo > 2 cm + pétreo + fixo ± esplenomegalia ± febre/sudorese noturna/perda peso (B-symptoms)','Hemograma, LDH, β2-microglobulina, biopsia linfonodal (padrão-ouro)','Não iniciar tratamento antes de biópsia; excisional preferível a PAAF','Linfonodomegalia mediastinal com dispneia (síndrome da veia cava superior)','Hematologia/oncologia urgente','AAFP 2016'],

    # ── GERAL / OUTROS ────────────────────────────────────────────────────────
    ['Geral','Fadiga','Fadiga crônica / ME-SFC','Fadiga > 6 meses + PEM (piora pós-esforço) + sono não-reparador + disfunção cognitiva; excluir orgânico','TSH, hemograma, glicemia, EAS, ferritina, VitD, sorologia EBV','Manejo do sono; redução do esforço (pacing); amitriptilina 10–25 mg noite; evitar exercício intenso (piora)','Déficit neurológico focal, dor torácica, febre persistente → excluir orgânico','Clínico / reumatologia / neurologia','AASM; ME-SFC Guidelines'],
    ['Geral','Fadiga','Fadiga por hipotireoidismo','Fadiga + ganho de peso + frio + constipação + TSH ↑','TSH, T4 livre','Levotiroxina 1,6 mcg/kg/dia (início com 25–50 mcg se > 60a ou DCV)','Coma mixedematoso (hipotermia + confusão)','Endocrinologia','ATA 2014'],
    ['Geral','Sono','Insônia crônica','Dificuldade iniciar/manter sono > 3×/sem > 3 meses + prejuízo diurno; ISI ≥ 10','ISI, STOP-BANG, Epworth; PSG se SAOS suspeita','TCC-I (1ª linha — acesso); melatonina 0,5–5 mg; evitar BZD crônicos (dependência, quedas)','Sonolência excessiva diurna + ronco + pausas → SAOS → PSG','Medicina do sono; psicologia TCC-I','AASM; ICSD-3'],
    ['Geral','Sono','Apneia Obstrutiva do Sono (SAOS)','STOP-BANG ≥ 3; ronco + pausas respiratórias + sonolência diurna; Epworth > 10','PSG (padrão-ouro); poligrafia domiciliar (alternativa)','CPAP (1ª linha grave); aparelho intraoral (leve–moderada); perda de peso','AHI > 30 + DCV/HTN não controlada → CPAP urgente','Pneumo/medicina do sono','AASM 2021; ICSD-3'],
    ['Geral','Icterícia','Icterícia obstrutiva (neoplásica)','Icterícia progressiva indolor + perda de peso + fezes acólicas + urina escura; CA páncreas suspeito','TC abdome com contraste; CA 19-9; bilirrubina direta ↑','Drenagem biliar (CPRE ou percutânea) se obstrução; oncologia','Colangite associada → ATB IV + drenagem urgente','Oncologia / cirurgia hepato-biliar-pancreática','ESMO 2023'],
    ['Geral','Edema MMII','Insuficiência venosa crônica','Edema bilateral vespertino + varizes + hiperpigmentação + dermatite de estase; crônico','Eco-Doppler venoso; excluir TVP se unilateral agudo','Meias de compressão (20–30 mmHg); flavonoides; elevação MMII; fleboextração se indicada','Úlcera varicosa infeccionada; ↑ agudo unilateral → TVP','Angiologia/vascular','ESC Veins 2018'],
]

# ─────────────────────────────────────────────────────────────────────────────
# SHEET 1 — REFERÊNCIA CLÍNICA PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

ws = wb.active
ws.title = 'Referência Clínica'
ws.sheet_view.showGridLines = False
ws.sheet_properties.tabColor = '58A6FF'

COLUNAS = [
    ('Sistema',          22),
    ('Queixa / Módulo',  22),
    ('Diagnóstico / Etiologia', 30),
    ('Clínica-Chave / Sintomas', 42),
    ('Exames Iniciais',  30),
    ('Tratamento 1ª Linha', 44),
    ('Red Flags / Alarme', 38),
    ('Encaminhamento',   28),
    ('Fonte / Guideline', 22),
]

# Linha 1: Título grande
ws.merge_cells('A1:I1')
ws['A1'] = 'SYMPTOOPY — REFERÊNCIA CLÍNICA DE PROTOCOLOS'
ws['A1'].font = Font(name='Consolas', bold=True, color=C_ACCENT, size=16)
ws['A1'].fill = body_fill(C_BG_DARK)
ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
ws.row_dimensions[1].height = 36

# Linha 2: subtítulo
ws.merge_cells('A2:I2')
ws['A2'] = '40 módulos clínicos  |  ACG · BSG · IDSA · AHA · GINA · GOLD · ESC · AAO · AASM  |  Adulto'
ws['A2'].font = Font(name='Consolas', italic=True, color='666E7A', size=10)
ws['A2'].fill = body_fill(C_BG_DARK)
ws['A2'].alignment = Alignment(horizontal='center', vertical='center')
ws.row_dimensions[2].height = 20

# Linha 3: cabeçalho
ws.row_dimensions[3].height = 36
for col_idx, (nome, largura) in enumerate(COLUNAS, start=1):
    c = ws.cell(row=3, column=col_idx, value=nome.upper())
    c.font = Font(name='Consolas', bold=True, color=C_HDR_TEXT, size=10)
    c.fill = hdr_fill(C_HDR_BLUE)
    c.alignment = center()
    c.border = Border(bottom=Side(style='medium', color=C_ACCENT),
                      left=thin, right=thin, top=thin)
    ws.column_dimensions[get_column_letter(col_idx)].width = largura

# Dados
sistema_atual = None
row_num = 4
for dados_row in DADOS:
    sistema = dados_row[0]
    row_num_excel = row_num
    ws.row_dimensions[row_num].height = 56

    # Cor da linha por sistema
    bg_hex = C_SYS.get(sistema, C_BAND1)
    bg_alt = _darken(bg_hex) if sistema == sistema_atual else bg_hex
    fill_row = body_fill(bg_hex)

    for col_idx, valor in enumerate(dados_row, start=1):
        c = ws.cell(row=row_num, column=col_idx, value=valor)
        c.fill = fill_row
        c.border = border_thin
        c.alignment = left()

        # Fontes por coluna
        if col_idx == 1:  # Sistema
            c.font = Font(name='Consolas', bold=True, color=C_ACCENT, size=9)
            c.alignment = center()
        elif col_idx == 3:  # Diagnóstico
            c.font = Font(name='Consolas', bold=True, color='E2E8F0', size=9)
        elif col_idx == 7:  # Red flags
            c.font = Font(name='Consolas', bold=True, color=C_RED, size=9)
        elif col_idx == 6:  # Tratamento
            c.font = Font(name='Consolas', color=C_GREEN, size=9)
        elif col_idx == 9:  # Fonte
            c.font = Font(name='Consolas', italic=True, color='8B949E', size=9)
        else:
            c.font = Font(name='Consolas', color=C_WHITE, size=9)

    sistema_atual = sistema
    row_num += 1

# Freeze panes
ws.freeze_panes = 'A4'

# Auto-filter
ws.auto_filter.ref = f'A3:I{row_num - 1}'


# ─────────────────────────────────────────────────────────────────────────────
# SHEET 2 — ANTIBIÓTICOS DE REFERÊNCIA
# ─────────────────────────────────────────────────────────────────────────────

ws2 = wb.create_sheet('Antibióticos')
ws2.sheet_view.showGridLines = False
ws2.sheet_properties.tabColor = C_GREEN

ATB_COLUNAS = [
    ('Indicação / Situação', 32),
    ('1ª Linha', 36),
    ('Alternativa (Alergia/Falha)', 32),
    ('Duração', 16),
    ('Via', 10),
    ('Observações Críticas', 36),
]

# Título
ws2.merge_cells('A1:F1')
ws2['A1'] = 'SYMPTOOPY — GUIA DE ANTIBIOTICOTERAPIA'
ws2['A1'].font = Font(name='Consolas', bold=True, color=C_GREEN, size=14)
ws2['A1'].fill = body_fill(C_BG_DARK)
ws2['A1'].alignment = Alignment(horizontal='center', vertical='center')
ws2.row_dimensions[1].height = 32

for col_idx, (nome, largura) in enumerate(ATB_COLUNAS, start=1):
    c = ws2.cell(row=2, column=col_idx, value=nome.upper())
    c.font = Font(name='Consolas', bold=True, color=C_HDR_TEXT, size=10)
    c.fill = hdr_fill(C_HDR_BLUE)
    c.alignment = center()
    c.border = Border(bottom=Side(style='medium', color=C_GREEN), left=thin, right=thin, top=thin)
    ws2.column_dimensions[get_column_letter(col_idx)].width = largura
ws2.row_dimensions[2].height = 30

ATB_DADOS = [
    # Indicação | 1ª linha | Alternativa | Duração | Via | Observação
    ['Faringoamigdalite bacteriana (GAS)','Penicilina Benzatina 1.200.000 UI','Amoxicilina 500 mg 8/8h  OU  Cefalexina 500 mg 6/6h','Benzatina: DU\nAmox: 10d','IM / VO','Alergia anafilática → Azitromicina 500 mg D1 + 250 mg D2-5'],
    ['Rinossinusite aguda bacteriana','Amoxicilina 875 mg 12/12h','Amox-Clav 875/125 mg 12/12h  OU  Cefuroxima 500 mg 12/12h','5–7 dias','VO','Alergia tipo I → Doxiciclina 100 mg 12/12h'],
    ['Otite Média Aguda (criança > 2a)','Amoxicilina 80–90 mg/kg/dia ÷ 12h','Amox-Clav suspensão 90 mg/kg/dia','5–7 dias','VO','< 6m, bilateral, febre ≥39°C → tratar imediatamente; watchful waiting com receita de resgate'],
    ['Otite Externa','Ciprofloxacino 0,3% + Dexametasona gotas','Polimixina B + neomicina gotas','7 dias','Tópico','OE maligna (DM) → ciprofloxacino IV + ORL'],
    ['Cistite simples (mulher)','Nitrofurantoína 100 mg 12/12h','Fosfomicina 3 g DU  OU  Cotrimoxazol 960 mg 12/12h','5 dias (nitro)\nDU (fosfo)\n3 dias (cotri)','VO','Resistência local > 20% → evitar cotrimoxazol; fluoroquinolonas reservar para pielonefrite'],
    ['Pielonefrite aguda (ambulatorial)','Ciprofloxacino 500 mg 12/12h','Cefuroxima 500 mg 12/12h','7–10 dias','VO','Se sepse → ceftriaxona IV → internação'],
    ['Pielonefrite aguda (grave / internação)','Ceftriaxona 1–2 g 1×/dia','Piperacilina-tazobactam 4,5 g q6h (risco ESBL)','7–14 dias','IV','Urocultura antes de iniciar ATB; escalonar conforme antibiograma'],
    ['Celulite não complicada (0 SIRS)','Cefalexina 500 mg 6/6h','Clindamicina 300–450 mg 8/8h','5 dias','VO','Erisipela: amoxicilina 500 mg 8/8h; MRSA suspeito: SMX-TMP DS 1 cp 12/12h'],
    ['Celulite grave (≥2 SIRS)','Cefazolina 1–2 g q8h','Vancomicina 15–20 mg/kg q8-12h (MRSA)','7–14 dias','IV','Fasciite → Vanco + Pip-Tazo + cirurgia; NÃO aguardar LRINEC se clinicamente suspeito'],
    ['Pneumonia comunitária (leve — ambulatorial)','Amoxicilina 875 mg 12/12h','Azitromicina 500 mg/dia (atípica suspeita)','5–7 dias','VO','CURB-65 ≥ 2 → considerar internação; cobertura dupla se atípica suspeita'],
    ['Pneumonia comunitária (moderada — internação)','Amoxicilina-clavulanato IV + Azitromicina','Ceftriaxona 1–2 g/dia + Azitromicina 500 mg/dia','5–7 dias','IV','CURB-65 ≥ 3: UTI + cobertura antipseudomonal se fatores de risco'],
    ['C. difficile (1º episódio)','Vancomicina 125 mg VO 6/6h','Fidaxomicina 200 mg 12/12h (recorrência)','10 dias','VO','NÃO usar metronidazol como 1ª linha; EVITAR antiperistálticos'],
    ['Diverticulite aguda não complicada','Amoxicilina-clavulanato 875/125 mg 12/12h','Metronidazol 500 mg 8/8h + ciprofloxacino 500 mg 12/12h','7–10 dias','VO','Complicada (abscesso/perfuração) → internação + piperacilina-tazobactam IV'],
    ['Sangramento varicoso (profilaxia ATB)','Ceftriaxona 1 g 1×/dia','Norfloxacino 400 mg 12/12h VO','7 dias','IV/VO','Iniciar IMEDIATAMENTE na admissão; reduz mortalidade em cirróticos'],
    ['DIP (Doença Inflamatória Pélvica)','Ceftriaxona 500 mg IM DU + Doxiciclina 100 mg 12/12h + Metronidazol 500 mg 12/12h','Ofloxacino 400 mg 12/12h + Metronidazol 500 mg 12/12h','14 dias','IM + VO','CDC STI 2021; parceiro(s) sexual(is) tratar; internação se abscesso'],
    ['Giardia','Metronidazol 500 mg 8/8h','Tinidazol 2 g DU','7 dias (metro)\nDU (tini)','VO','Tratar contactantes sintomáticos; coprocultura pós-tratamento se persistir'],
    ['Dengue grave (profilaxia infecção secundária)','NÃO usar ATB profilático em dengue','—','—','—','PROIBIDO AAS e AINEs; corticoide não indicado rotineiramente; suporte hídrico'],
    ['Erisipela (estreptocócica clássica)','Amoxicilina 500 mg 8/8h','Penicilina Benzatina 1.200.000 UI DU (se adesão duvidosa)','5–7 dias\nDU (benz)','VO/IM','Profilaxia recorrência (≥3/ano): Penicilina VK 250–500 mg/dia × 12 meses'],
]

for i, row_data in enumerate(ATB_DADOS, start=3):
    bg = C_BAND1 if i % 2 == 0 else C_BAND2
    ws2.row_dimensions[i].height = 52
    for col_idx, valor in enumerate(row_data, start=1):
        c = ws2.cell(row=i, column=col_idx, value=valor)
        c.fill = body_fill(bg)
        c.border = border_thin
        c.alignment = left()
        if col_idx == 2:
            c.font = Font(name='Consolas', bold=True, color=C_GREEN, size=9)
        elif col_idx == 6:
            c.font = Font(name='Consolas', italic=True, color=C_YELLOW, size=9)
        else:
            c.font = Font(name='Consolas', color=C_WHITE, size=9)

ws2.freeze_panes = 'A3'
ws2.auto_filter.ref = f'A2:F{len(ATB_DADOS) + 2}'


# ─────────────────────────────────────────────────────────────────────────────
# SHEET 3 — SCORES CLÍNICOS
# ─────────────────────────────────────────────────────────────────────────────

ws3 = wb.create_sheet('Scores Clínicos')
ws3.sheet_view.showGridLines = False
ws3.sheet_properties.tabColor = C_YELLOW

def score_hdr(ws_obj, row, title, color=C_ACCENT):
    ws_obj.merge_cells(start_row=row, start_column=1, end_row=row, end_column=3)
    c = ws_obj.cell(row=row, column=1, value=f'▶  {title}')
    c.font = Font(name='Consolas', bold=True, color=color, size=11)
    c.fill = body_fill(C_HDR_BLUE)
    c.alignment = Alignment(horizontal='left', vertical='center')
    ws_obj.row_dimensions[row].height = 24

def score_row(ws_obj, row, variavel, pontos, interpretacao=''):
    ws_obj.row_dimensions[row].height = 20
    for col_idx, (val, w) in enumerate([(variavel, 40), (pontos, 12), (interpretacao, 38)], start=1):
        c = ws_obj.cell(row=row, column=col_idx, value=val)
        c.fill = body_fill(C_BAND1 if row % 2 == 0 else C_BAND2)
        c.border = border_thin
        c.alignment = left()
        if col_idx == 2:
            c.font = Font(name='Consolas', bold=True, color=C_YELLOW, size=9)
        elif col_idx == 3 and val:
            c.font = Font(name='Consolas', italic=True, color=C_GREEN, size=9)
        else:
            c.font = Font(name='Consolas', color=C_WHITE, size=9)
    ws3.column_dimensions['A'].width = 40
    ws3.column_dimensions['B'].width = 12
    ws3.column_dimensions['C'].width = 38

r = 1
ws3.merge_cells('A1:C1')
ws3['A1'] = 'SYMPTOOPY — SCORES E CRITÉRIOS CLÍNICOS DE REFERÊNCIA'
ws3['A1'].font = Font(name='Consolas', bold=True, color=C_YELLOW, size=14)
ws3['A1'].fill = body_fill(C_BG_DARK)
ws3['A1'].alignment = Alignment(horizontal='center', vertical='center')
ws3.row_dimensions[1].height = 32
r += 1

# GBS
score_hdr(ws3, r, 'GLASGOW-BLATCHFORD SCORE (GBS) — Hemorragia Digestiva Alta'); r += 1
score_row(ws3, r, 'BUN 18,2–22,3 mg/dL', '+2'); r += 1
score_row(ws3, r, 'BUN 22,4–27,9 mg/dL', '+3'); r += 1
score_row(ws3, r, 'BUN 28–69,9 mg/dL', '+4'); r += 1
score_row(ws3, r, 'BUN ≥ 70 mg/dL', '+6'); r += 1
score_row(ws3, r, 'Hb (homem) 12–12,9 g/dL', '+1'); r += 1
score_row(ws3, r, 'Hb (homem) 10–11,9 g/dL', '+3'); r += 1
score_row(ws3, r, 'Hb (homem) < 10 g/dL', '+6'); r += 1
score_row(ws3, r, 'Hb (mulher) 10–11,9 g/dL', '+1'); r += 1
score_row(ws3, r, 'Hb (mulher) < 10 g/dL', '+6'); r += 1
score_row(ws3, r, 'PAS 100–109 mmHg', '+1'); r += 1
score_row(ws3, r, 'PAS 90–99 mmHg', '+2'); r += 1
score_row(ws3, r, 'PAS < 90 mmHg', '+3'); r += 1
score_row(ws3, r, 'FC ≥ 100 bpm', '+1'); r += 1
score_row(ws3, r, 'Melena', '+1'); r += 1
score_row(ws3, r, 'Síncope', '+2'); r += 1
score_row(ws3, r, 'Hepatopatia conhecida', '+2'); r += 1
score_row(ws3, r, 'ICC', '+2'); r += 1
score_row(ws3, r, '── INTERPRETAÇÃO ──', '', ''); r += 1
score_row(ws3, r, 'GBS 0–1', 'Muito baixo', 'Alta segura + endoscopia eletiva'); r += 1
score_row(ws3, r, 'GBS 2–6', 'Moderado', 'Internação + endoscopia < 24h'); r += 1
score_row(ws3, r, 'GBS ≥ 7', 'Alto', 'Alta probabilidade de intervenção endoscópica'); r += 1
r += 1

# Oakland
score_hdr(ws3, r, 'OAKLAND SCORE — Hemorragia Digestiva Baixa (LGIB)'); r += 1
score_row(ws3, r, 'Idade 40–69 anos', '+3'); r += 1
score_row(ws3, r, 'Idade ≥ 70 anos', '+5'); r += 1
score_row(ws3, r, 'Sexo masculino', '+1'); r += 1
score_row(ws3, r, 'Internação prévia por LGIB', '+4'); r += 1
score_row(ws3, r, 'Toque retal com sangue', '+1'); r += 1
score_row(ws3, r, 'FC 90–119 bpm', '+1'); r += 1
score_row(ws3, r, 'FC ≥ 120 bpm', '+3'); r += 1
score_row(ws3, r, 'PAS 90–119 mmHg', '+2'); r += 1
score_row(ws3, r, 'PAS < 90 mmHg', '+5'); r += 1
score_row(ws3, r, 'Hb 9–11,9 g/dL', '+4'); r += 1
score_row(ws3, r, 'Hb < 9 g/dL', '+7'); r += 1
score_row(ws3, r, '── INTERPRETAÇÃO ──', '', ''); r += 1
score_row(ws3, r, 'Oakland ≤ 8', 'Baixo risco', 'Alta segura + colonoscopia eletiva (2–4 sem)'); r += 1
score_row(ws3, r, 'Oakland > 8', 'Alto risco', 'Internação + colonoscopia'); r += 1
r += 1

# LRINEC
score_hdr(ws3, r, 'LRINEC SCORE — Fasciite Necrotizante', C_RED); r += 1
score_row(ws3, r, 'PCR > 150 mg/L', '+2'); r += 1
score_row(ws3, r, 'Leucócitos > 25.000/μL', '+2'); r += 1
score_row(ws3, r, 'Leucócitos 15.000–25.000/μL', '+1'); r += 1
score_row(ws3, r, 'Hb < 11 g/dL', '+2'); r += 1
score_row(ws3, r, 'Hb 11–13,5 g/dL', '+1'); r += 1
score_row(ws3, r, 'Na < 135 mEq/L', '+2'); r += 1
score_row(ws3, r, 'Creatinina > 1,6 mg/dL', '+2'); r += 1
score_row(ws3, r, 'Glicemia > 180 mg/dL', '+1'); r += 1
score_row(ws3, r, '── INTERPRETAÇÃO ──', '', ''); r += 1
score_row(ws3, r, 'LRINEC ≥ 6', 'Alto risco', '⚠️ Score NÃO substitui julgamento clínico'); r += 1
score_row(ws3, r, 'LRINEC ≥ 8', 'Muito alto', 'Sensibilidade baixa (49–75%) — clínica SEMPRE prevalece'); r += 1
r += 1

# SIRS
score_hdr(ws3, r, 'CRITÉRIOS SIRS — Celulite / Sepse'); r += 1
score_row(ws3, r, 'Temperatura > 38°C ou < 36°C', '1 critério'); r += 1
score_row(ws3, r, 'FC > 90 bpm', '1 critério'); r += 1
score_row(ws3, r, 'FR > 20 ipm', '1 critério'); r += 1
score_row(ws3, r, 'Leucócitos > 12.000 ou < 4.000/μL', '1 critério'); r += 1
score_row(ws3, r, '── INTERPRETAÇÃO ──', '', ''); r += 1
score_row(ws3, r, '0 SIRS', 'Leve', 'Celulite: ATB oral + alta'); r += 1
score_row(ws3, r, '1 SIRS', 'Moderado', 'ATB oral + retorno 48h obrigatório'); r += 1
score_row(ws3, r, '≥ 2 SIRS', 'Grave', 'Internação + ATB IV'); r += 1
r += 1

# Ottawa
score_hdr(ws3, r, 'REGRAS DE OTTAWA — Tornozelo e Pé'); r += 1
score_row(ws3, r, 'TORNOZELO: dor na zona A (maléolo lateral posterior 6 cm)', 'Rx indica', 'Zona A ou B positiva → solicitar Rx tornozelo'); r += 1
score_row(ws3, r, 'TORNOZELO: dor na zona B (maléolo medial posterior 6 cm)', 'Rx indica', ''); r += 1
score_row(ws3, r, 'PÉ: dor na base do 5º metatarso (zona C)', 'Rx indica', 'Zona C ou D positiva → solicitar Rx pé'); r += 1
score_row(ws3, r, 'PÉ: dor sobre o navicular (zona D)', 'Rx indica', ''); r += 1
score_row(ws3, r, 'Incapacidade de apoiar peso (4 passos)', 'Rx indica', 'Sensibilidade 96–99% para fratura'); r += 1
r += 1

# Centor
score_hdr(ws3, r, 'CRITÉRIOS DE CENTOR — Faringoamigdalite'); r += 1
score_row(ws3, r, 'Exsudato em amígdalas', '+1'); r += 1
score_row(ws3, r, 'Linfonodomegalia cervical anterior', '+1'); r += 1
score_row(ws3, r, 'Febre (história ou aferida)', '+1'); r += 1
score_row(ws3, r, 'Ausência de tosse', '+1'); r += 1
score_row(ws3, r, 'Idade 3–14 anos', '+1'); r += 1
score_row(ws3, r, 'Idade ≥ 45 anos', '-1'); r += 1
score_row(ws3, r, '── INTERPRETAÇÃO ──', '', ''); r += 1
score_row(ws3, r, 'Centor 0–1', 'Viral', 'Sintomático; sem ATB'); r += 1
score_row(ws3, r, 'Centor 2', 'Incerto', 'TRA; tratar se positivo'); r += 1
score_row(ws3, r, 'Centor ≥ 3', 'Bacteriano provável', 'ATB (Penicilina Benzatina 1ª linha)'); r += 1
r += 1

# CHA2DS2-VASc
score_hdr(ws3, r, 'CHA₂DS₂-VASc — Risco Tromboembólico na FA'); r += 1
score_row(ws3, r, 'C — Insuficiência cardíaca congestiva', '+1'); r += 1
score_row(ws3, r, 'H — Hipertensão arterial', '+1'); r += 1
score_row(ws3, r, 'A — Idade ≥ 75 anos', '+2'); r += 1
score_row(ws3, r, 'D — Diabetes mellitus', '+1'); r += 1
score_row(ws3, r, 'S — AVC / AIT prévio', '+2'); r += 1
score_row(ws3, r, 'V — Doença vascular (IAM, placa, DAP)', '+1'); r += 1
score_row(ws3, r, 'A — Idade 65–74 anos', '+1'); r += 1
score_row(ws3, r, 'Sc — Sexo feminino', '+1'); r += 1
score_row(ws3, r, '── INTERPRETAÇÃO ──', '', ''); r += 1
score_row(ws3, r, 'Homem ≥ 2 / Mulher ≥ 3', 'DOAC indicado', 'Apixabana 5 mg 12/12h (1ª linha) ou Rivaroxabana 20 mg/dia'); r += 1
score_row(ws3, r, 'Homem = 1 / Mulher = 2', 'Individualizar', 'Discutir risco-benefício'); r += 1
score_row(ws3, r, 'Homem = 0 / Mulher ≤ 1', 'Baixo risco', 'Sem anticoagulação'); r += 1
r += 1

# Wells DVT
score_hdr(ws3, r, 'WELLS SCORE — TVP (Trombose Venosa Profunda)'); r += 1
score_row(ws3, r, 'Neoplasia ativa', '+1'); r += 1
score_row(ws3, r, 'Imobilização / cirurgia recente (< 4 sem)', '+1'); r += 1
score_row(ws3, r, 'Paralisia ou paresia de MMII', '+1'); r += 1
score_row(ws3, r, 'Empastamento panturrilha (> 3 cm que contralateral)', '+1'); r += 1
score_row(ws3, r, 'Veias superficiais colaterais', '+1'); r += 1
score_row(ws3, r, 'Edema com cacifo em toda a perna', '+1'); r += 1
score_row(ws3, r, 'Dor ao longo do trajeto venoso profundo', '+1'); r += 1
score_row(ws3, r, 'Diagnóstico alternativo tão provável quanto TVP', '-2'); r += 1
score_row(ws3, r, '── INTERPRETAÇÃO ──', '', ''); r += 1
score_row(ws3, r, '≤ 1', 'Baixa probabilidade', 'D-dímero; se negativo → excluído'); r += 1
score_row(ws3, r, '2–6', 'Probabilidade moderada', 'Eco-Doppler venoso'); r += 1
score_row(ws3, r, '≥ 3', 'Alta probabilidade', 'Eco-Doppler + anticoagular empiricamente'); r += 1

ws3.freeze_panes = 'A2'


# ─────────────────────────────────────────────────────────────────────────────
# SHEET 4 — ÍNDICE DOS MÓDULOS
# ─────────────────────────────────────────────────────────────────────────────

ws4 = wb.create_sheet('Índice de Módulos')
ws4.sheet_view.showGridLines = False
ws4.sheet_properties.tabColor = '8B949E'

ws4.merge_cells('A1:E1')
ws4['A1'] = 'SYMPTOOPY — 40 MÓDULOS CLÍNICOS IMPLEMENTADOS'
ws4['A1'].font = Font(name='Consolas', bold=True, color=C_ACCENT, size=14)
ws4['A1'].fill = body_fill(C_BG_DARK)
ws4['A1'].alignment = Alignment(horizontal='center', vertical='center')
ws4.row_dimensions[1].height = 32

INDICE_COLS = [('Módulo', 28), ('Sistema', 20), ('Score/Algoritmo', 28), ('Status', 12), ('Guideline', 22)]
for col_idx, (nome, larg) in enumerate(INDICE_COLS, start=1):
    c = ws4.cell(row=2, column=col_idx, value=nome.upper())
    c.font = Font(name='Consolas', bold=True, color=C_HDR_TEXT, size=10)
    c.fill = hdr_fill(C_HDR_BLUE)
    c.alignment = center()
    c.border = Border(bottom=Side(style='medium', color=C_ACCENT), left=thin, right=thin, top=thin)
    ws4.column_dimensions[get_column_letter(col_idx)].width = larg
ws4.row_dimensions[2].height = 28

MODULOS = [
    ['Dispneia',              'Respiratório',     'Integrador multissíndrome',    '✅','BTS / ATS-IDSA'],
    ['Tosse',                 'Respiratório',     'Algoritmo Irwin (aguda/crônica)','✅','Cochrane / BTS'],
    ['Asma',                  'Respiratório',     'GINA 2025 step-up/down',       '✅','GINA 2025'],
    ['DPOC',                  'Respiratório',     'GOLD 2026 ABCD + CAT/mMRC',    '✅','GOLD 2026'],
    ['Palpitação',            'Cardiovascular',   'ECG + CHA₂DS₂-VASc',          '✅','AHA/ACC/HRS 2023'],
    ['Síncope',               'Cardiovascular',   'CSRS + ESC 2018',              '✅','ESC 2018'],
    ['Edema MMII',            'Cardiovascular',   'Wells + AHA',                  '✅','ESC 2019'],
    ['Hemorragia Digestiva',  'Gastro/Abdominal', 'GBS (HDA) + Oakland (HDB)',    '✅','ACG 2023; BSG 2021'],
    ['Gastro/Abdominal',      'Gastro/Abdominal', 'V Consenso H. pylori 2025',    '✅','ACG / JAMA 2024'],
    ['Diarreia',              'Gastro/Abdominal', 'OMS + IDSA 2021 (C. diff)',    '✅','OMS; IDSA 2021'],
    ['Icterícia',             'Gastro/Abdominal', 'AASLD / EASL / ACG',           '✅','AASLD / EASL'],
    ['Sangramento Anorretal', 'Gastro/Abdominal', 'Goligher + ACG',               '✅','ACG 2023'],
    ['Febre sem Foco',        'Infectologia',     'AAFP + Harrison',              '✅','AAFP 2022'],
    ['Arboviroses',           'Infectologia',     'Protocolo MS Brasil 2025',     '✅','MS Brasil 2025'],
    ['IVAS',                  'Infectologia',     'AAO-HNS + IDSA',               '✅','IDSA 2023'],
    ['ORL — Odinofagia',      'Infectologia/ORL', 'Centor + IDSA 2023',           '✅','IDSA 2023'],
    ['ORL — Otalgia',         'Infectologia/ORL', 'AAP/AAFP 2022',                '✅','AAP/AAFP 2022'],
    ['ORL — Rinossinusite',   'Infectologia/ORL', 'AAO-HNS 2025',                 '✅','AAO-HNS 2025'],
    ['Celulite / Erisipela',  'Infectologia',     'SIRS + LRINEC + IDSA 2014',    '✅','IDSA 2014'],
    ['Urinário',              'Urologia',         'JAMA 2024 + AUA 2020',         '✅','JAMA 2024; AUA 2020'],
    ['Cefaleia',              'Neurologia',       'ICHD-3 + AAN',                 '✅','ICHD-3 / AAN'],
    ['Vertigem',              'Neurologia',       'HINTS + AAO-HNS 2017',         '✅','Cochrane 2019'],
    ['Consciência / ANC',     'Neurologia',       'AEIOU TIPS + Glasgow',         '✅','Harrison / ACEP'],
    ['Linfadenopatia',        'Hematologia',      'AAFP 2016 + ASH',              '✅','AAFP 2016; ASH'],
    ['Anemia',                'Hematologia',      'WHO 2011 + Cochrane 2021',     '✅','WHO 2011'],
    ['Joelho',                'MSK',              'Ottawa + AAOS 2021',           '✅','AAOS 2021'],
    ['Ombro',                 'MSK',              'AAOS 2020',                    '✅','AAOS 2020'],
    ['Coluna / Lombalgia',    'MSK',              'Red flags + ESC Spine 2020',   '✅','NICE 2023; ACP 2017'],
    ['Fibromialgia',          'MSK',              'ACR 2016 (WPI + SS)',          '✅','ACR 2016 / EULAR 2017'],
    ['Gota',                  'MSK',              'Dutch 2010 + ACR 2020',        '✅','ACR 2020; EULAR 2022'],
    ['Quadril',               'MSK',              'Red flags + AAOS',             '✅','AAOS'],
    ['Tornozelo / Pé',        'MSK',              'Ottawa Rules + AAFP 2022',     '✅','AAFP 2022'],
    ['Mão / Punho',           'MSK',              'Phalen + Tinel + AAOS',        '✅','AAOS'],
    ['Olho Vermelho',         'Oftalmo',          'AAO 2023',                     '✅','AAO 2023'],
    ['Fadiga',                'Geral',            'Algoritmo etiológico APS',     '✅','AASM / ME-SFC'],
    ['Sono / Insônia',        'Geral',            'ISI + STOP-BANG + Epworth',    '✅','AASM; ICSD-3'],
    ['Asma (episód.-crônico)','Respiratório',     'GINA 2025 crise + controle',   '✅','GINA 2025'],
    ['DPOC (episód.-crônico)','Respiratório',     'GOLD 2026 exacerb.+ rotina',   '✅','GOLD 2026'],
    ['Gota (aguda + crônica)','MSK',              'Dutch 2010 + ACR 2020',        '✅','ACR 2020'],
    ['Síncope (CSRS)',        'Cardiovascular',   'CSRS + ESC 2018',              '✅','ESC 2018'],
]

for i, row_data in enumerate(MODULOS, start=3):
    bg = C_BAND1 if i % 2 == 0 else C_BAND2
    ws4.row_dimensions[i].height = 22
    for col_idx, valor in enumerate(row_data, start=1):
        c = ws4.cell(row=i, column=col_idx, value=valor)
        c.fill = body_fill(bg)
        c.border = border_thin
        c.alignment = left()
        if col_idx == 1:
            c.font = Font(name='Consolas', bold=True, color=C_ACCENT, size=9)
        elif col_idx == 4:
            c.font = Font(name='Consolas', bold=True, color=C_GREEN, size=10)
            c.alignment = center()
        else:
            c.font = Font(name='Consolas', color=C_WHITE, size=9)

ws4.freeze_panes = 'A3'

# ─────────────────────────────────────────────────────────────────────────────
# Background escuro para todas as sheets
# ─────────────────────────────────────────────────────────────────────────────
for sheet in [ws, ws2, ws3, ws4]:
    sheet.sheet_view.showGridLines = False

# ─────────────────────────────────────────────────────────────────────────────
# SALVAR
# ─────────────────────────────────────────────────────────────────────────────
OUTPUT = r'C:\Users\Joao\Desktop\SymptoPy_Referencia_Clinica.xlsx'
wb.save(OUTPUT)
print(f'Salvo: {OUTPUT}')
