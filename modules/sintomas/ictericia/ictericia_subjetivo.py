# modules/sintomas/ictericia/ictericia_subjetivo.py
import json, os, tempfile

def coletar_subjetivo_ictericia(dados_preenchidos=None):
    dados = dados_preenchidos.copy() if dados_preenchidos else {}

    def _bool(prompt, chave):
        while True:
            r = input(f'  {prompt} [s/n]: ').strip().lower()
            if r in ('s','sim','y','yes'): dados[chave]=True; return True
            if r in ('n','nao','não','no'): dados[chave]=False; return False
            print('  → s ou n.')

    def _float(prompt, chave):
        while True:
            r = input(f'  {prompt}: ').strip().replace(',','.')
            if not r: return None
            try: dados[chave]=float(r); return dados[chave]
            except: print('  → número.')

    print('\n' + '═'*60)
    print('  ICTERÍCIA — Adulto Ambulatorial')
    print('═'*60)

    if not dados.get('idade'):
        try: dados['idade'] = int(input('  Idade: ').strip())
        except: dados['idade'] = 0

    # BLOCO 1 — Emergência
    print('\n[1/5] SINAIS DE ALARME')
    _bool('Febre + dor no hipocôndrio direito + icterícia (tríade de Charcot)?', 'dor_hcd')
    dados['febre'] = dados.get('dor_hcd', False) and _bool('Febre presente?', 'febre_sim') if not dados.get('dor_hcd') else True
    dados['ictericia'] = True   # paciente tem icterícia
    _bool('Hipotensão ou alteração de consciência junto com icterícia?', 'hipotensao')
    _bool('Confusão mental / encefalopatia hepática?', 'alt_consciencia')
    _bool('Perda de peso involuntária associada?', 'perda_peso_involuntaria')
    _bool('INR > 1,5 (se disponível)?', 'inr_maior_1_5')
    _bool('Encefalopatia confirmada?', 'encefalopatia_hepatica')

    # BLOCO 2 — Padrão clínico
    print('\n[2/5] PADRÃO DA ICTERÍCIA')
    _bool('Icterícia flutuante (aparece e desaparece)?', 'ictericia_flutuante')
    _bool('Icterícia progressiva e persistente?', 'ictericia_progressiva')
    _bool('Urina escura (cor de chá/coca-cola)?', 'urina_escura')
    _bool('Fezes claras / acólicas?', 'fezes_acolicas')
    _bool('Prurido cutâneo intenso?', 'prurido_cutaneo')
    _bool('Cólica biliar (dor HCD em cólica após gordurosos)?', 'colica_biliar')

    # BLOCO 3 — Labs se disponíveis
    print('\n[3/5] EXAMES (se disponíveis)')
    _bool('Exames laboratoriais disponíveis?', 'labs_disponiveis')
    if dados.get('labs_disponiveis'):
        _float('Bilirrubina direta (mg/dL)?', 'bilirrubina_direta')
        _float('Bilirrubina indireta (mg/dL)?', 'bilirrubina_indireta')
        _float('ALT/TGP (U/L)?', 'alt_u_l')
        _float('AST/TGO (U/L)?', 'ast_u_l')
        _float('FA / ALP (U/L)?', 'alp_u_l')
        _float('GGT (U/L)?', 'ggt_u_l')
        _bool('US abdominal já realizado?', 'us_realizado')
        if dados.get('us_realizado'):
            _bool('US: ductos biliares dilatados?', 'ductos_dilatados_us')
        _bool('AMA positivo (colangite biliar primária)?', 'ama_positivo')

    # BLOCO 4 — Etiologia
    print('\n[4/5] HISTÓRICO ETIOLÓGICO')
    _bool('Uso excessivo de álcool?', 'uso_alcool_excessivo')
    _bool('Medicamentos hepatotóxicos ou suplementos herbal?', 'medicamento_hepatotoxico')
    dados['suplem_herbal'] = dados.get('medicamento_hepatotoxico', False)
    if dados.get('medicamento_hepatotoxico'):
        _bool('Medicamento com padrão colestático (esteroides anabolizantes, contraceptivos, eritromicina)?', 'medicamento_colestatico')
    _bool('Episódio sugestivo de hepatite viral aguda (sintomas sistêmicos, febre, mialgia)?', 'hepatite_viral_suspeita')
    _bool('Contato com caso de hepatite B ou A?', 'contato_hepatite_b')
    dados['hepatite_a_suspeita'] = dados.get('contato_hepatite_b', False)
    _bool('Comportamento de risco para HCV (uso IV de drogas, transfusão pré-1992)?', 'hepatite_c_suspeita')
    _bool('Doença autoimune conhecida (tireoidite, artrite reumatoide, LES)?', 'doenca_autoimune_conhecida')
    _bool('Fatores de risco para esteatose (obesidade, DM2, dislipidemia)?', 'steatose_fatores_risco')
    _bool('DII conhecida (Crohn, RCUI)?', 'dii_conhecida')
    _bool('Icterícia leve recorrente (desde jovem, sem outros sintomas) — possível Gilbert?', 'gilbert_previamente_diagnosticado')

    # BLOCO 5 — Contexto
    print('\n[5/5] CONTEXTO')
    _bool('Viagem recente a área endêmica de hepatite A/E?', 'viagem_area_endemica')
    _bool('Cirrose ou doença hepática crônica já conhecida?', 'cirrose_conhecida')

    fd, arq = tempfile.mkstemp(suffix='.json', prefix='ictericia_')
    os.close(fd)
    with open(arq, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print('\n  ✓ Dados salvos.\n')
    return dados, arq
