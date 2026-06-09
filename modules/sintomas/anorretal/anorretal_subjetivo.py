# modules/sintomas/anorretal/anorretal_subjetivo.py
import json, os, tempfile

def coletar_subjetivo_anorretal(dados_preenchidos=None):
    dados = dados_preenchidos.copy() if dados_preenchidos else {}

    def _bool(prompt, chave):
        while True:
            r = input(f'  {prompt} [s/n]: ').strip().lower()
            if r in ('s','sim','y','yes'): dados[chave]=True; return True
            if r in ('n','nao','não','no'): dados[chave]=False; return False
            print('  → s ou n.')

    def _int(prompt, chave, obrigatorio=False):
        while True:
            r = input(f'  {prompt}: ').strip()
            if not r and not obrigatorio: return None
            try: dados[chave]=int(r); return dados[chave]
            except ValueError: print('  → número inteiro.')

    print('\n' + '═'*60)
    print('  SANGRAMENTO ANORRETAL / PRURIDO ANAL — Adulto')
    print('═'*60)

    if not dados.get('idade'):
        try: dados['idade'] = int(input('  Idade: ').strip())
        except: dados['idade'] = 0

    # BLOCO 1 — Queixa principal
    print('\n[1/5] QUEIXA PRINCIPAL')
    _bool('Sangramento retal como queixa principal?', 'sangramento_principal')
    if dados.get('sangramento_principal'):
        _bool('Sangramento novo (primeira vez)?', 'sangramento_novo')
        _bool('Sangue apenas no papel / na superfície das fezes (não misturado)?', 'sangramento_no_papel')
        _bool('Sangramento em jato ou gotejamento ao defecar?', 'sangramento_gotejamento')
        _bool('Sangue misturado às fezes (cor escura / dentro do bolo fecal)?', 'sangue_misturado_fezes')
    _bool('Prurido perianal como queixa principal?', 'prurido_perianal')
    _bool('Dor intensa durante e após a defecação?', 'dor_durante_defecacao')
    _bool('Saída de tecido pelo ânus (prolapso)?', 'prolapso_anorretal')

    # BLOCO 2 — Red flags
    print('\n[2/5] SINAIS DE ALARME')
    _bool('Perda de peso involuntária?', 'perda_peso_involuntaria')
    _bool('Alteração de hábito intestinal por mais de 4 semanas?', 'mudanca_habito_intestinal_4sem')
    _bool('História familiar de câncer colorretal ou DII?', 'historia_familiar_ccr')
    _bool('Anemia confirmada em exame de sangue?', 'anemia_ferropriva_confirmada')

    # BLOCO 3 — Hemorroida / fissura
    print('\n[3/5] CARACTERIZAÇÃO')
    _bool('Prolapso que reduz espontaneamente?', 'prolapso_reducao_espontanea')
    _bool('Prolapso que necessita redução manual?', 'prolapso_reducao_manual')
    _bool('Prolapso irredutível?', 'prolapso_irredutivel')
    _bool('Nódulo externo doloroso de início súbito (hemorroida trombosada)?', 'hemorroida_trombosada_externa')
    if dados.get('hemorroida_trombosada_externa'):
        _int('Há quantas horas iniciou o nódulo?', 'horas_desde_trombose', obrigatorio=True)
    if dados.get('dor_durante_defecacao'):
        _int('Há quantas semanas dura a dor?', 'duracao_fissura_semanas')

    # BLOCO 4 — Prurido
    print('\n[4/5] PRURIDO ANAL (se presente)')
    if dados.get('prurido_perianal'):
        _bool('Sangramento significativo associado ao prurido?', 'sangramento_significativo')
        _bool('Suspeita de oxiuros (criança em casa, prurido noturno)?', 'oxiuros_suspeita')
        _bool('Lesão branca ou esbranquiçada ao redor do ânus?', 'candida_perianal')
        _bool('Placas eritematosas / psoríase conhecida?', 'psoríase_perianal')
        _bool('Escape fecal / incontinência?', 'incontinencia_fecal')
        _bool('Uso de tetraciclina, colchicina ou quinidina?', 'medicamento_causador')
        _bool('Consumo excessivo de café, chocolate ou condimentados?', 'gatilho_dietetico')

    # BLOCO 5 — Contexto
    print('\n[5/5] CONTEXTO')
    _bool('Constipação crônica?', 'constipacao_cronica')
    _bool('Gravidez ou pós-parto recente?', 'gestante_ou_posparto')
    _bool('DII conhecida (Crohn ou RCUI)?', 'dii_conhecida')
    _bool('Anoscopia/retossigmoidoscopia prévia realizada?', 'anoscopia_previa')

    fd, arq = tempfile.mkstemp(suffix='.json', prefix='anorretal_')
    os.close(fd)
    with open(arq, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print('\n  ✓ Dados salvos.\n')
    return dados, arq
