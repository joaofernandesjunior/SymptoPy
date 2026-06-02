# modules/raciocinio/tosse/runner.py

import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from modules.raciocinio.tosse.engine_tosse import interpretar_tosse


def _sep(c='─', n=54):
    print(c * n)


def _formatar_resultado(resultado) -> str:
    """Constrói o texto de saída como string (para imprimir e copiar)."""
    categoria  = resultado.get('categoria', '')
    linhas     = []

    linhas.append('=' * 54)
    linhas.append('  RESULTADO — TOSSE')
    linhas.append('=' * 54)

    # ── Red flags / imunossupressão ────────────────────────────────────
    flags = resultado.get('red_flags', {}).get('flags', [])
    if flags:
        linhas.append('─' * 54)
        for f in flags:
            linhas.append(f'\n  [{f["urgencia"].upper()}] {f["achado"]}')
            linhas.append(f'  Conduta: {f["acao"]}')

    # ── PCP — emergência ───────────────────────────────────────────────
    if categoria == 'tosse_pcp_suspeita':
        linhas.append('─' * 54)
        linhas.append(f'\n  [URGENTE] {resultado.get("hipotese", "")}')
        for p in resultado.get('positivos', []):
            linhas.append(f'    + {p}')
        linhas.append('\n  Conduta:')
        for item in resultado.get('conduta', []):
            linhas.append(f'  • {item}')
        linhas.append('=' * 54)
        return '\n'.join(linhas)

    # ── Aguda — resultado direto ───────────────────────────────────────
    if categoria in ('tosse_aguda_viral', 'tosse_aguda_bacteriana', 'tosse_pertussis_suspeita'):
        linhas.append('─' * 54)
        linhas.append(f'\n  {resultado.get("hipotese", "")}')
        for p in resultado.get('positivos', []):
            linhas.append(f'    + {p}')
        linhas.append('\n  Conduta:')
        for item in resultado.get('conduta', []):
            linhas.append(f'  • {item}')
        if resultado.get('alerta_influenza'):
            linhas.append('\n  ALERTA: síndrome gripal sem vacinação — considerar Oseltamivir se < 48h de evolução.')
        if resultado.get('internacao'):
            linhas.append('\n  INTERNAÇÃO: avaliar CURB-65 e decisão hospitalar.')
        enc = resultado.get('encaminhar', '')
        if enc:
            linhas.append(f'\n  Encaminhamento: {enc}')
        linhas.append('=' * 54)
        return '\n'.join(linhas)

    # ── Subaguda ───────────────────────────────────────────────────────
    if categoria == 'tosse_subaguda_pos_infecciosa':
        linhas.append('─' * 54)
        linhas.append(f'\n  {resultado.get("hipotese", "")}')
        for p in resultado.get('positivos', []):
            linhas.append(f'    + {p}')
        linhas.append('\n  Conduta:')
        for item in resultado.get('conduta', []):
            linhas.append(f'  • {item}')
        if resultado.get('alerta_pertussis'):
            linhas.append('\n  ALERTA: acessos paroxísticos — pertussis a excluir (Azitromicina + PCR nasofaringe).')
        linhas.append('=' * 54)
        return '\n'.join(linhas)

    # ── Crônica — múltiplas hipóteses ─────────────────────────────────
    provaveis = resultado.get('hipoteses_provaveis', [])
    possiveis  = resultado.get('hipoteses_possiveis', [])

    label = {
        'tosse_ieca':               'TOSSE POR IECA',
        'tosse_uacs':               'UACS — GOTEJAMENTO PÓS-NASAL',
        'tosse_asma_variante':      'ASMA / TOSSE VARIANTE DE ASMA',
        'tosse_drge_lpr':           'DRGE / LPR',
        'tosse_tb_suspeita':        'TUBERCULOSE — SUSPEITA',
        'tosse_pneumonia_atipica':  'PNEUMONIA ATÍPICA',
        'tosse_neoplasia_suspeita': 'SUSPEITA DE NEOPLASIA PULMONAR',
        'investigar_tosse_cronica': 'TOSSE CRÔNICA — INVESTIGAR',
    }.get(categoria, categoria.upper())

    linhas.append(f'\n  TOSSE CRÔNICA — {label}')

    # Espirometria
    espiro = resultado.get('espirometria', {})
    if espiro.get('realizada'):
        linhas.append('─' * 54)
        linhas.append(f'\n  ESPIROMETRIA: {espiro["conclusao"]}')
        linhas.append(f'  VEF1/CVF pré: {espiro["vef1_cvf_pre"]} | VEF1/CVF pós: {espiro["vef1_cvf_pos"]} | ΔVeF1: {espiro["delta_vef1_pct"]}%')
        if espiro.get('laudo_medico'):
            linhas.append(f'  Laudo: {espiro["laudo_medico"]}')

    if not provaveis and not possiveis:
        linhas.append('─' * 54)
        linhas.append(f'\n  {resultado.get("mensagem", "Dados insuficientes.")}')
        linhas.append('=' * 54)
        return '\n'.join(linhas)

    if provaveis:
        linhas.append('\n  HIPÓTESES PROVÁVEIS:')
        for h in provaveis:
            linhas.append('─' * 54)
            linhas.append(f'\n  [{h["forca"].upper()}] {h["hipotese"]} (score {h["score"]})')
            for p in h.get('positivos', []):
                linhas.append(f'    + {p}')

            nf = h.get('conduta_nao_farmacologica', [])
            if nf:
                linhas.append('\n  Não-farmacológico:')
                for item in nf:
                    linhas.append(f'  • {item}')

            farm = h.get('farmacologico', [])
            if farm:
                linhas.append('\n  Farmacológico:')
                for item in farm:
                    linhas.append(f'  • {item}')

            enc = h.get('encaminhar', '')
            if enc:
                linhas.append(f'\n  Encaminhamento: {enc}')

            img = h.get('imagem', '')
            if img:
                linhas.append(f'  Imagem: {img}')

            if h.get('espiro_sugerida'):
                linhas.append('\n  SUGESTÃO: espirometria com prova broncodilatadora para confirmar.')

    if possiveis:
        linhas.append('─' * 54)
        linhas.append('\n  HIPÓTESES POSSÍVEIS (baixa força):')
        for h in possiveis:
            linhas.append(f'  • {h["hipotese"]} (score {h["score"]})')

    linhas.append('=' * 54)
    return '\n'.join(linhas)


def _copiar_clipboard(texto):
    """Copia o resultado para o clipboard do Windows."""
    try:
        import subprocess
        proc = subprocess.Popen(['clip'], stdin=subprocess.PIPE)
        proc.communicate(texto.encode('utf-8'))
        print('\n  [Impressão automática copiada para o clipboard]')
    except Exception:
        pass


def rodar(arquivo_json):
    sys.stdout.reconfigure(encoding='utf-8')
    with open(arquivo_json, encoding='utf-8') as f:
        dados = json.load(f)
    resultado   = interpretar_tosse(dados)
    texto_saida = _formatar_resultado(resultado)
    print(texto_saida)
    _copiar_clipboard(texto_saida)
    return resultado
