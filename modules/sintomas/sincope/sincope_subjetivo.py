# modules/sintomas/sincope/sincope_subjetivo.py
import json, os, tempfile

def coletar_subjetivo_sincope(dados_preenchidos=None):
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
    print('  SÍNCOPE / PERDA DE CONSCIÊNCIA — Adulto Ambulatorial')
    print('═'*60)

    if not dados.get('idade'):
        try: dados['idade'] = int(input('  Idade: ').strip())
        except: dados['idade'] = 0

    # BLOCO 1 — Evento
    print('\n[1/5] O EPISÓDIO')
    _bool('Perda completa de consciência (não apenas tontura ou escurecimento)?', 'perda_consciencia_completa')
    _bool('Recuperação rápida e espontânea (segundos a < 1 min, sem confusão prolongada)?', 'recuperacao_rapida')
    _bool('Ocorreu durante ou imediatamente após esforço físico?', 'sincope_esforco')
    _bool('Ocorreu ao levantar da cama ou ao sentar?', 'sintomas_ao_levantar')
    _bool('Mordida de língua lateral (sugere crise convulsiva)?', 'mordedura_lingua')
    _bool('Incontinência urinária ou fecal durante o episódio?', 'incontinencia')
    _bool('Confusão prolongada após o episódio (pós-ictal > 30s)?', 'pos_convulsao')

    # BLOCO 2 — Pródromo e gatilho
    print('\n[2/5] PRÓDROMO E GATILHO')
    _bool('Havia náusea, suor frio ou sensação de calor antes de desmaiar?', 'prodrome_nausea_diaforese')
    _bool('Houve escurecimento visual ou visão turva antes da perda de consciência?', 'prodrome_visual')
    _bool('Sensação de calor/rubor?', 'prodrome_calor')
    _bool('Estava de pé por tempo prolongado ou em ambiente quente/lotado?', 'gatilho_posicional')
    _bool('Emoção intensa, dor ou visão de sangue como gatilho?', 'gatilho_emocional')
    _bool('Após urinar, defecar ou tossir intensamente?', 'gatilho_miccao')
    _bool('Ao virar o pescoço ou usar colarinho apertado?', 'gatilho_carotideo')

    # BLOCO 3 — Red flags cardíacos
    print('\n[3/5] SINAIS DE ALARME')
    _bool('Dor torácica ou dispneia associada ao episódio?', 'sincope_com_dor_toracica')
    _bool('Palpitações imediatamente antes da síncope?', 'palpitacao_antes')
    _bool('Cardiopatia estrutural conhecida (IC, estenose aórtica, DAC, CMHO)?', 'doenca_estrutural_cardiaca')
    _bool('Morte súbita em familiar de 1º grau com menos de 50 anos?', 'historia_familiar_morte_subita')
    _bool('Déficit neurológico focal após o episódio?', 'deficit_focal')

    # BLOCO 4 — ECG e PA
    print('\n[4/5] ECG E PRESSÃO ARTERIAL')
    ecg = _bool('ECG já realizado?', 'ecg_realizado')
    if ecg:
        _bool('ECG: QTc > 480 ms?', 'ecg_qtc_maior_480')
        _bool('ECG: QRS > 130 ms?', 'ecg_qrs_maior_130')
        _bool('ECG: padrão Brugada (supradesnivelamento ST V1-V3)?', 'ecg_brugada')
        _bool('ECG: pré-excitação (WPW)?', 'ecg_preexcitacao')
        _bool('ECG: BAV de 3º grau ou BRE novo?', 'ecg_bav3')
        _bool('ECG: arritmia ventricular documentada?', 'ecg_arritmia_vent')

    _bool('PA medida em ortostatismo (deitado → de pé 1 e 3 min)?', 'pa_ortostatica_medida')
    if dados.get('pa_ortostatica_medida'):
        _bool('Queda da PA sistólica ≥ 20 mmHg ao ortostatismo?', 'queda_pas_20')
        _bool('Queda da PA diastólica ≥ 10 mmHg ao ortostatismo?', 'queda_pad_10')
    _bool('PA sistólica ≤ 90 ou > 180 mmHg no episódio?', 'pa_anormal')
    _bool('Troponina elevada (se coletada)?', 'troponina_elevada')

    # BLOCO 5 — Histórico e medicações
    print('\n[5/5] HISTÓRICO E MEDICAÇÕES')
    _bool('Episódios vasovagais prévios documentados?', 'predisposicao_vasovagal')
    _bool('Em uso de anti-hipertensivos, diuréticos ou alfa-bloqueadores?', 'medicamento_hipotensor_em_uso')
    _bool('Diabetes ou doença de Parkinson (neuropatia autonômica)?', 'diabetes')
    _bool('Sinais clínicos de desidratação?', 'desidratacao_clinica')
    _bool('Doença cardíaca estrutural ou arritmia conhecida?', 'doenca_cardiaca_conhecida')

    fd, arq = tempfile.mkstemp(suffix='.json', prefix='sincope_')
    os.close(fd)
    with open(arq, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print('\n  ✓ Dados salvos.\n')
    return dados, arq
