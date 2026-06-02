# mecanico_inflamatorio.py
# Camada compartilhada — Diferenciação padrão mecânico vs inflamatório
# Base: Open Evidence 2026 / ACR / EULAR
# Essa distinção precede o diagnóstico específico — muda raciocínio e conduta

def classificar_padrao(dados):
    score_mecanico = 0
    score_inflamatorio = 0
    achados_mecanicos = []
    achados_inflamatorios = []

    # --- PADRÃO MECÂNICO ---
    if dados.get('rigidez_matinal_menos_30min'):
        score_mecanico += 2
        achados_mecanicos.append('rigidez matinal < 30 minutos')
    if dados.get('piora_com_atividade'):
        score_mecanico += 2
        achados_mecanicos.append('piora com atividade/carga')
    if dados.get('melhora_com_repouso'):
        score_mecanico += 2
        achados_mecanicos.append('melhora com repouso')
    if dados.get('inicio_insidioso_com_uso'):
        score_mecanico += 1
        achados_mecanicos.append('início insidioso relacionado a uso/esforço')
    if dados.get('sem_calor_ou_eritema'):
        score_mecanico += 1
        achados_mecanicos.append('sem calor ou eritema articular')
    if dados.get('crepitacao'):
        score_mecanico += 1
        achados_mecanicos.append('crepitação ao movimento')

    # --- PADRÃO INFLAMATÓRIO ---
    if dados.get('rigidez_matinal_acima_60min'):
        score_inflamatorio += 3
        achados_inflamatorios.append('rigidez matinal > 60 minutos')
    if dados.get('piora_com_repouso'):
        score_inflamatorio += 2
        achados_inflamatorios.append('piora com repouso prolongado')
    if dados.get('melhora_com_atividade_leve'):
        score_inflamatorio += 2
        achados_inflamatorios.append('melhora com atividade leve')
    if dados.get('calor_ou_eritema_articular'):
        score_inflamatorio += 2
        achados_inflamatorios.append('calor ou eritema articular')
    if dados.get('articulacoes_multiplas_afetadas'):
        score_inflamatorio += 2
        achados_inflamatorios.append('múltiplas articulações afetadas')
    if dados.get('sintomas_sistemicos'):
        score_inflamatorio += 2
        achados_inflamatorios.append('sintomas sistêmicos (febre, fadiga, perda de peso)')
    if dados.get('envolvimento_simetrico'):
        score_inflamatorio += 2
        achados_inflamatorios.append('envolvimento simétrico')

    # --- CLASSIFICAÇÃO ---
    if score_inflamatorio >= 5:
        padrao = 'inflamatorio'
    elif score_mecanico >= 4:
        padrao = 'mecanico'
    else:
        padrao = 'indeterminado'

    # --- EXAMES SUGERIDOS ---
    exames = []
    if padrao == 'inflamatorio':
        exames = ['VHS', 'PCR', 'Hemograma completo', 'FR', 'Anti-CCP', 'Ácido úrico']
        if dados.get('idade_acima_50') and dados.get('articulacoes_multiplas_afetadas'):
            exames.append('Considerar: perfil tireoidiano (hipotireoidismo)')
    elif padrao == 'mecanico':
        exames = ['Radiografia simples se indicado por Ottawa ou clínica']

    conduta_padrao = {
        'mecanico': [
            'AINEs ou paracetamol para controle sintomático',
            'Fisioterapia e fortalecimento muscular',
            'Redução de carga e adaptações ergonômicas',
            'Considerar infiltração se falha conservadora'
        ],
        'inflamatorio': [
            'Não iniciar corticoide sem diagnóstico etiológico',
            'Solicitar exames laboratoriais (VHS, PCR, FR, anti-CCP)',
            'Encaminhar reumatologia se padrão inflamatório confirmado',
            'AINEs para alívio sintomático enquanto investiga'
        ],
        'indeterminado': [
            'Reavaliar com mais história e exame físico detalhado',
            'Solicitar PCR e VHS para distinguir padrões'
        ]
    }

    return {
        'padrao': padrao,
        'score_mecanico': score_mecanico,
        'score_inflamatorio': score_inflamatorio,
        'achados_mecanicos': achados_mecanicos,
        'achados_inflamatorios': achados_inflamatorios,
        'exames_sugeridos': exames,
        'conduta_padrao': conduta_padrao[padrao],
        'alerta_inflamatorio': score_inflamatorio >= 5
    }


if __name__ == '__main__':
    caso_ar = {
        'rigidez_matinal_menos_30min': False,
        'rigidez_matinal_acima_60min': True,
        'piora_com_atividade': False,
        'piora_com_repouso': True,
        'melhora_com_repouso': False,
        'melhora_com_atividade_leve': True,
        'inicio_insidioso_com_uso': False,
        'sem_calor_ou_eritema': False,
        'calor_ou_eritema_articular': True,
        'crepitacao': False,
        'articulacoes_multiplas_afetadas': True,
        'sintomas_sistemicos': True,
        'envolvimento_simetrico': True,
        'idade_acima_50': False
    }
    resultado = classificar_padrao(caso_ar)
    print(f"Padrão: {resultado['padrao'].upper()}")
    print(f"Achados inflamatórios: {resultado['achados_inflamatorios']}")
    print(f"Exames: {resultado['exames_sugeridos']}")
