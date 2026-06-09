# modules/raciocinio/arboviroses/runner.py
# Formatação e exibição dos resultados — Arboviroses

import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from modules.raciocinio.arboviroses.engine_arboviroses import interpretar_arboviroses

_LABEL = {
    'arboviral_grupo_d':     'DENGUE GRAVE / CHOQUE — GRUPO D',
    'arboviral_grupo_c':     'DENGUE COM SINAIS DE ALARME — GRUPO C',
    'arboviral_grupo_b':     'DENGUE PROVAVEL — GRUPO B (Condicao Especial)',
    'arboviral_grupo_a':     'DENGUE PROVAVEL — GRUPO A (Ambulatorial)',
    'chikungunya_suspeita':  'CHIKUNGUNYA SUSPEITA',
    'zika_suspeita':         'ZIKA SUSPEITA',
    'arboviral_indiferenciada': 'SINDROME FEBRIL — Arboviral indiferenciada',
}

_ALARME_LABEL = {
    'dor_abdominal_intensa':   'Dor abdominal intensa (referida ou a palpacao) e continua',
    'vomitos_persistentes':    'Vomitos persistentes',
    'acumulo_liquidos':        'Acumulo de liquidos (ascite, derrame pleural, pericardico)',
    'hipotensao_postural':     'Hipotensao postural e/ou lipotimia',
    'hepatomegalia_referida':  'Hepatomegalia dolorosa > 2 cm abaixo do rebordo costal',
    'sangramento_mucosa':      'Sangramento de mucosa',
    'letargia_irritabilidade': 'Letargia e/ou irritabilidade',
    'aumento_hematocrito':     'Aumento progressivo do hematocrito (>= 10% em relacao anterior)',
}

_COMORBIDADE_LABEL = {
    'gestante':           'Gestante',
    'diabetes':           'Diabetes mellitus',
    'has_cardiovascular': 'HAS / doenca cardiovascular',
    'hematologica':       'Doenca hematologica',
    'drc':                'Doenca renal cronica',
    'doenca_hepatica':    'Doenca hepatica previa',
    'obesidade_grave':    'Obesidade grave (IMC > 40)',
    'extremo_idade':      'Extremo de idade (< 2 anos ou > 60 anos)',
    'risco_social':       'Risco social',
}


def _box_aine():
    w = 56
    return [
        '╔' + '═' * w + '╗',
        '║   !! AINE E AAS CONTRAINDICADOS — DENGUE SUSPEITA !! ║',
        '║   Ibuprofeno / Nimesulida / Diclofenaco / Cetoprofeno ║',
        '║   Piroxicam / AAS — HEMORRAGIA GRAVE / Reye (<18 a.) ║',
        '║   Usar: Dipirona 500-1000 mg  |  Para max 3 g/dia    ║',
        '╚' + '═' * w + '╝',
    ]


def _box_observacao_grupo_b():
    w = 56
    return [
        '╔' + '═' * w + '╗',
        '║    !! OBSERVACAO SUPERVISIONADA — GRUPO B (4-6h) !!  ║',
        '║  INICIAR HIDRATACAO ORAL IMEDIATAMENTE NA POLTRONA   ║',
        '║  NAO aguardar hemograma sem oferecer liquidos         ║',
        '║  Hemograma + NS1/IgM: coletar na ADMISSAO            ║',
        '╚' + '═' * w + '╝',
    ]


def _box_emergencia():
    w = 56
    return [
        '╔' + '═' * w + '╗',
        '║          !! EMERGENCIA — DENGUE GRAVE / CHOQUE !!     ║',
        '║     Expansao IV 20 mL/kg em 20 MINUTOS                ║',
        '║     Chamar equipe / acionar suporte avancado           ║',
        '╚' + '═' * w + '╝',
    ]


def _box_zika_gestante():
    w = 56
    return [
        '╔' + '═' * w + '╗',
        '║       !! ZIKA EM GESTANTE — NOTIFICACAO IMEDIATA !!   ║',
        '║     Risco de microcefalia fetal                        ║',
        '║     Encaminhar pre-natal alto risco URGENTE            ║',
        '╚' + '═' * w + '╝',
    ]


def _formatar_resultado(resultado):
    categoria = resultado.get('categoria', '')
    linhas = []

    linhas.append('=' * 58)
    linhas.append('  RESULTADO — ARBOVIROSES (DENGUE / CHIKUNGUNYA / ZIKA)')
    linhas.append('=' * 58)

    label = _LABEL.get(categoria, categoria.upper())
    grupo = resultado.get('grupo_dengue', '')
    linhas.append(f'\n  {label}' + (f' [Grupo {grupo}]' if grupo else ''))

    # Boxes de alerta prioritárias
    if categoria == 'arboviral_grupo_d':
        linhas.append('')
        linhas.extend(_box_emergencia())

    if resultado.get('aine_contraindicado'):
        linhas.append('')
        linhas.extend(_box_aine())

    if resultado.get('alerta_gestante_zika'):
        linhas.append('')
        linhas.extend(_box_zika_gestante())

    # Critérios diagnósticos usados (fechamento clínico)
    criterios = resultado.get('criterios_usados', [])
    if criterios:
        linhas.append('')
        for c in criterios:
            linhas.append(f'  {c}')

    # Chikungunya — nota sobre AINE
    if categoria == 'chikungunya_suspeita' and not resultado.get('aine_contraindicado'):
        linhas.append(f'\n  Nota: {resultado.get("aine_msg", "")}')

    # Sinais de choque presentes
    sinais_choque = resultado.get('sinais_choque', [])
    if sinais_choque:
        linhas.append('\n  Sinais de choque identificados:')
        nomes = {
            'hipotensao_severa': 'Hipotensao severa (PA <= 90/60)',
            'pulso_filiforme':   'Pulso filiforme',
            'tec_maior_3s':      'TEC > 3 segundos',
            'sudorese_fria':     'Sudorese fria / extremidades frias',
        }
        for s in sinais_choque:
            linhas.append(f'  !! {nomes.get(s, s)}')

    # Sinais de alarme
    alarmes = resultado.get('sinais_alarme', [])
    if alarmes:
        linhas.append('\n  Sinais de alarme presentes:')
        for a in alarmes:
            linhas.append(f'  - {_ALARME_LABEL.get(a, a)}')

    # Comorbidades
    comorbs = resultado.get('comorbidades', [])
    if comorbs:
        linhas.append('\n  Condicoes especiais (Grupo B):')
        for c in comorbs:
            linhas.append(f'  - {_COMORBIDADE_LABEL.get(c, c)}')
    if resultado.get('prova_laco'):
        linhas.append('  - Prova do Laco positiva')

    # Fase cronica Chikungunya
    if categoria == 'chikungunya_suspeita':
        meses = resultado.get('artralgia_meses', 0)
        fase  = 'Cronica (> 3 meses)' if resultado.get('fase_cronica') else 'Aguda'
        linhas.append(f'\n  Fase: {fase}' + (f' — {meses} meses de artralgia' if meses else ''))
        if resultado.get('edema_articular'):
            linhas.append('  Edema articular presente')

    # Hidratação
    hid = resultado.get('hidratacao', {})
    if hid:
        linhas.append('\n  Hidratacao:')
        if categoria == 'arboviral_grupo_d':
            linhas.append(f'  IV: {hid["iv_grupo_d_ml"]} mL em 20 min (20 mL/kg — {hid["peso_kg"]:.0f} kg)')
        elif categoria == 'arboviral_grupo_c':
            linhas.append(f'  IV: {hid["iv_grupo_c_ml"]} mL em 60 min (10 mL/kg — {hid["peso_kg"]:.0f} kg)')
        elif categoria in ('arboviral_grupo_b', 'arboviral_grupo_a',
                           'chikungunya_suspeita', 'zika_suspeita'):
            linhas.append(f'  Oral: {hid["oral_ml_dia"]} mL/dia (60 mL/kg — {hid["peso_kg"]:.0f} kg)')

    # Gestação Zika
    if resultado.get('alerta_gestante_zika') and resultado.get('semanas_gestacao'):
        linhas.append(f'\n  Gestacao: {resultado["semanas_gestacao"]} semanas')

    # Grupo B — box de observação supervisionada
    if resultado.get('observacao_ubs'):
        linhas.append('')
        linhas.extend(_box_observacao_grupo_b())

    # Conduta
    linhas.append('\n  Conduta:')
    for item in resultado.get('conduta', []):
        linhas.append(f'  • {item}')

    # Exames
    exames = resultado.get('exames', [])
    if exames:
        linhas.append('\n  Exames:')
        for ex in exames:
            linhas.append(f'  • {ex}')

    # Sinais de retorno
    retorno = resultado.get('sinais_retorno', [])
    if retorno:
        linhas.append('\n  Sinais de retorno imediato:')
        for s in retorno:
            linhas.append(f'  - {s}')

    # Prescrição de observação — Grupo B
    rx_obs = resultado.get('prescricao_observacao')
    if rx_obs:
        w = 56
        linhas.append('')
        linhas.append('╔' + '═' * w + '╗')
        linhas.append('║' + ' PRESCRICAO DE OBSERVACAO — DENGUE GRUPO B'.center(w) + '║')
        linhas.append('╠' + '═' * w + '╣')
        linhas.append('║  SINTOMATICOS:' + ' ' * (w - 15) + '║')
        for s in rx_obs.get('sintomaticos', []):
            linhas.append('║  ' + s.ljust(w - 2) + '║')
        linhas.append('╠' + '─' * w + '╣')
        linhas.append('║  HIDRATACAO SUPERVISIONADA:' + ' ' * (w - 27) + '║')
        for h in rx_obs.get('hidratacao_supervisionada', []):
            linhas.append('║  ' + h.ljust(w - 2) + '║')
        linhas.append('╠' + '─' * w + '╣')
        linhas.append('║  LABORATORIO (coletar na admissao):' + ' ' * (w - 35) + '║')
        for l in rx_obs.get('laboratorio_urgente', []):
            linhas.append('║  ' + l.ljust(w - 2) + '║')
        linhas.append('╠' + '─' * w + '╣')
        linhas.append('║  ENFERMAGEM — monitorar a cada hora:' + ' ' * (w - 36) + '║')
        for e in rx_obs.get('monitoramento_enfermagem', []):
            linhas.append('║  ' + e.ljust(w - 2) + '║')
        linhas.append('╚' + '═' * w + '╝')

    # Receita de alta — Grupo A
    receita = resultado.get('receita_alta')
    if receita:
        w = 56
        linhas.append('')
        linhas.append('╔' + '═' * w + '╗')
        linhas.append('║' + '  RECEITA DE ALTA — DENGUE GRUPO A'.center(w) + '║')
        linhas.append('╠' + '═' * w + '╣')
        for m in receita.get('medicamentos', []):
            if m == '':
                linhas.append('║' + ' ' * w + '║')
            else:
                linhas.append('║  ' + m.ljust(w - 2) + '║')
        linhas.append('╠' + '─' * w + '╣')
        for h in receita.get('hidratacao_prescrita', []):
            linhas.append('║  ' + h.ljust(w - 2) + '║')
        linhas.append('╠' + '─' * w + '╣')
        for o in receita.get('orientacoes_alta', []):
            linhas.append('║  ' + o.ljust(w - 2) + '║')
        linhas.append('╚' + '═' * w + '╝')

    # Internação
    if resultado.get('internacao'):
        linhas.append('\n  !! INTERNACAO INDICADA !!')
    if resultado.get('uti'):
        linhas.append('  !! UTI / SALA DE EMERGENCIA !!')

    linhas.append('\n' + '=' * 58)
    return '\n'.join(linhas)


def _copiar_clipboard(texto):
    try:
        import subprocess
        proc = subprocess.Popen(['clip'], stdin=subprocess.PIPE)
        proc.communicate(texto.encode('utf-8'))
        print('\n  [Impressao automatica copiada para o clipboard]')
    except Exception:
        pass


def rodar(arquivo_json):
    sys.stdout.reconfigure(encoding='utf-8')
    with open(arquivo_json, encoding='utf-8') as f:
        dados = json.load(f)
    resultado   = interpretar_arboviroses(dados)
    texto_saida = _formatar_resultado(resultado)
    print(texto_saida)
    _copiar_clipboard(texto_saida)
    return resultado
