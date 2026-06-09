# modules/sintomas/asma/asma_subjetivo.py
import json, os, tempfile

def coletar_subjetivo_asma(dados_preenchidos=None):
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
            except: print('  → número inteiro.')

    def _float(prompt, chave):
        while True:
            r = input(f'  {prompt}: ').strip().replace(',','.')
            if not r: return None
            try: dados[chave]=float(r); return dados[chave]
            except: print('  → número.')

    def _escolha(prompt, chave, opcoes):
        print(f'  {prompt}')
        for k,v in opcoes.items(): print(f'    [{k}] {v}')
        while True:
            r = input('  Opção: ').strip().lower()
            if r in opcoes: dados[chave]=r; return r
            print(f'  → {list(opcoes.keys())}')

    print('\n' + '═'*60)
    print('  ASMA — Adulto Ambulatorial (GINA 2025)')
    print('═'*60)

    if not dados.get('idade'):
        try: dados['idade'] = int(input('  Idade: ').strip())
        except: dados['idade'] = 0

    # BLOCO 1 — Tipo de consulta
    print('\n[1/5] TIPO DE CONSULTA')
    _escolha('Consulta de rotina ou piora aguda?', 'consulta_tipo', {
        'crise':  'Piora aguda — chiado, falta de ar, aperto no peito',
        'rotina': 'Rotina / controle — avaliação do controle da asma',
    })

    if dados.get('consulta_tipo') == 'crise':
        # ── CRISE ───────────────────────────────────────────────────────────
        print('\n[2/5] GRAVIDADE DA CRISE (GINA 2025)')
        print('  Avalie o pior parâmetro presente:')
        _bool('Sonolência, confusão ou incapacidade de falar?', 'sonolencia_confusao')
        dados['nao_consegue_falar'] = dados.get('sonolencia_confusao', False)
        _bool('Tórax silencioso (sem sibilos audíveis — exaustão)?', 'torax_silencioso')
        _bool('Fala apenas palavras isoladas (não consegue completar frases)?', 'fala_palavras_apenas')
        _bool('Frequência respiratória > 30 irpm?', 'fr_maior_30')
        _bool('Frequência cardíaca > 120 bpm?', 'fc_maior_120')
        _bool('Uso de musculatura acessória visível?', 'uso_musculatura_acessoria')
        _float('SpO₂ (%) na oximetria de pulso [Enter = não disponível]', 'spo2')
        _float('PEFR ou VEF1 — % do previsto [Enter = não disponível]', 'pefr_percentual')

        print('\n[3/5] HISTÓRICO DA CRISE')
        _bool('Já usou salbutamol antes de vir? Quantas vezes? (responda s se sim)', 'usou_saba_antes')
        _bool('Usa corticoide inalatório regularmente?', 'usa_ics_regular')
        _bool('Tomou prednisona nos últimos 3 meses?', 'ocs_recente')
        _bool('Internação por asma no último ano?', 'internacao_asma_ano')
        _bool('Alergia ou contraindicação a salbutamol?', 'contraindicacao_saba')

    else:
        # ── ROTINA ──────────────────────────────────────────────────────────
        print('\n[2/5] CONTROLE DA ASMA (últimas 4 semanas)')
        _bool('Sintomas diurnos (chiado, tosse, aperto) mais de 2×/semana?', 'sintomas_diurnos_mais_2sem')
        _bool('Acorda à noite por asma?', 'despertar_noturno')
        _bool('Usa salbutamol de resgate mais de 2×/semana (exceto pré-exercício)?', 'saba_mais_2sem')
        _bool('Alguma limitação de atividade por asma?', 'limitacao_atividade')
        _bool('Exacerbação que precisou de prednisona ou PS no último ano?', 'exacerbacao_ultimo_ano')

        print('\n[3/5] TRATAMENTO ATUAL (GINA Step)')
        _escolha('Qual é o tratamento atual?', 'step_atual', {
            '1': 'Só salbutamol SOS (sem controller)',
            '2': 'ICS baixa dose diário OU ICS/Formoterol SOS',
            '3': 'ICS/LABA baixa-média dose (MART ou fixo)',
            '4': 'ICS/LABA média dose (MART ou fixo)',
            '5': 'ICS/LABA alta dose ± LAMA — já em especialista',
        })
        try: dados['step_atual'] = int(dados.get('step_atual', 2))
        except: dados['step_atual'] = 2

        _bool('Técnica inalatória correta verificada?', 'tecnica_inalacao_correta')
        _bool('Usa o medicamento todos os dias conforme prescrito?', 'adesao_medicacao')
        _float('Eosinófilos no sangue (cél/μL) — se disponível [Enter = pular]', 'eosinofilos')
        _bool('Espirometria com obstrução reversível já documentada?', 'espirometria_positiva')

    print('\n[4/5] GATILHOS E COMORBIDADES')
    _bool('Rinite alérgica?', 'rinite_alergica')
    _bool('DRGE / pirose?', 'drge')
    _bool('Obesidade (IMC > 30)?', 'obesidade')
    _bool('Usa AINE ou AAS regularmente?', 'usa_aine_aas')
    _bool('Usa betabloqueador?', 'usa_betabloqueador')
    _bool('Exposição ocupacional a irritantes?', 'exposicao_ocupacional')

    print('\n[5/5] VACINAÇÃO')
    _bool('Vacinado contra influenza (último ano)?', 'vacina_influenza')
    _bool('Vacinado contra pneumococo?', 'vacina_pneumococo')

    fd, arq = tempfile.mkstemp(suffix='.json', prefix='asma_')
    os.close(fd)
    with open(arq, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print('\n  ✓ Dados salvos.\n')
    return dados, arq
