# modules/raciocinio/fadiga/runner.py

import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from modules.raciocinio.fadiga.engine_fadiga import interpretar_fadiga


def _sep(c='─', n=54):
    print(c * n)


def _get_contraindicado_box():
    """Retorna bloco visual de alerta GET contraindicado."""
    return [
        '╔' + '═' * 52 + '╗',
        '║  ⛔ GET (GRADED EXERCISE THERAPY) CONTRAINDICADO  ║',
        '║     NICE 2021 — CONTRAINDICACAO ABSOLUTA           ║',
        '║     Exercício gradual piora ME/SFC (NICE 2021)     ║',
        '╚' + '═' * 52 + '╝',
    ]


def _formatar_resultado(resultado) -> str:
    categoria = resultado.get('categoria', '')
    linhas    = []

    linhas.append('=' * 54)
    linhas.append('  RESULTADO — FADIGA CRONICA')
    linhas.append('=' * 54)

    # ── 1. Red flags ─────────────────────────────────────────────────
    if categoria == 'fadiga_red_flags':
        flags = resultado.get('red_flags', {}).get('flags', [])
        linhas.append('\n  RED FLAGS IDENTIFICADOS — investigacao urgente')
        for f in flags:
            linhas.append('─' * 54)
            linhas.append(f'  [{f["urgencia"].upper()}] {f["achado"]}')
            linhas.append(f'  Conduta: {f["acao"]}')
        for item in resultado.get('conduta', []):
            linhas.append(f'  • {item}')
        linhas.append('=' * 54)
        return '\n'.join(linhas)

    # ── 2. Causa secundária laboratorial ─────────────────────────────
    if categoria == 'fadiga_secundaria_laboratorial':
        lab = resultado.get('lab', {})
        achados = lab.get('achados', [])
        linhas.append('\n  EXIT STRATEGY — Causa secundaria identificada')
        linhas.append('  Tratar antes de prosseguir algoritmo de fadiga primaria\n')
        for a in achados:
            linhas.append('─' * 54)
            linhas.append(f'  [{a["lab"]}] {a["achado"]}')
            linhas.append(f'  Tratamento: {a["tratamento"]}')
            if a.get('encaminhar'):
                linhas.append(f'  Encaminhar: {a["encaminhar"]}')
        linhas.append('─' * 54)
        for item in resultado.get('conduta', []):
            linhas.append(f'  • {item}')
        linhas.append('=' * 54)
        return '\n'.join(linhas)

    # ── 3. Apneia do sono ─────────────────────────────────────────────
    if categoria == 'fadiga_secundaria_apneia':
        sb = resultado.get('stopbang', 0)
        linhas.append(f'\n  STOP-BANG = {sb}/8 — ALTO RISCO para Apneia Obstrutiva do Sono')
        linhas.append('─' * 54)
        linhas.append('\n  Conduta:')
        for item in resultado.get('conduta', []):
            linhas.append(f'  • {item}')
        linhas.append('=' * 54)
        return '\n'.join(linhas)

    # ── 4. Causa psiquiátrica ─────────────────────────────────────────
    if categoria == 'fadiga_secundaria_psiquiatrica':
        phq2 = resultado.get('phq2', 0)
        gad2 = resultado.get('gad2', 0)
        linhas.append('\n  TRIAGEM POSITIVA — Transtorno de Humor / Ansiedade')
        if phq2 >= 3:
            linhas.append(f'  PHQ-2 = {phq2}/6 → POSITIVO para depressao')
        if gad2 >= 3:
            linhas.append(f'  GAD-2 = {gad2}/6 → POSITIVO para ansiedade')
        linhas.append('─' * 54)
        alerta = resultado.get('alerta', '')
        if alerta:
            linhas.append(f'\n  NOTA: {alerta}')
        linhas.append('\n  Conduta:')
        for item in resultado.get('conduta', []):
            linhas.append(f'  • {item}')
        linhas.append('=' * 54)
        return '\n'.join(linhas)

    # ── 5. ME/SFC ─────────────────────────────────────────────────────
    if categoria == 'fadiga_me_sfc':
        criterios = resultado.get('criterios', {})
        linhas.append('\n  ENCEFALOMIELITE MIALGICA / SINDROME DE FADIGA CRONICA')
        linhas.append('  Criterios IOM 2015 — COMPLETOS')
        linhas.append('─' * 54)

        # Resumo dos critérios
        dur = criterios.get('duracao', 0)
        linhas.append(f'\n  Duracao: {dur} meses (>= 6 meses ✓)')
        linhas.append('  Tríade obrigatória: reducao atividade + PEM + sono nao-reparador ✓')
        if criterios.get('brain_fog'):
            linhas.append('  Critério adicional: Brain fog ✓')
        if criterios.get('ortostase'):
            linhas.append('  Critério adicional: Intolerancia ortostatica ✓')

        # PHQ-2/GAD-2 / STOP-BANG residuais
        phq2 = resultado.get('phq2', 0)
        gad2 = resultado.get('gad2', 0)
        sb   = resultado.get('stopbang', 0)
        if phq2 >= 3 or gad2 >= 3:
            linhas.append(f'\n  NOTA: PHQ-2 = {phq2}, GAD-2 = {gad2} — comorbidade psiquiatrica')
            linhas.append('  (comorbidade nao exclui ME/SFC; PEM esta presente)')
        if sb >= 3:
            linhas.append(f'  STOP-BANG = {sb}/8 — investigar AOS concomitante')

        linhas.append('')
        # Box de contraindicação GET
        for linha in _get_contraindicado_box():
            linhas.append(linha)

        linhas.append('\n  Conduta — Pacing (gestao do envelope de energia):')
        for item in resultado.get('conduta', []):
            linhas.append(f'  • {item}')
        linhas.append('=' * 54)
        return '\n'.join(linhas)

    # ── 6. Fadiga idiopática / subaguda ──────────────────────────────
    if categoria == 'fadiga_idiopatica_subaguda':
        criterios = resultado.get('criterios', {})
        faltando  = criterios.get('faltando', [])
        dur       = criterios.get('duracao', 0)
        nice_poss = criterios.get('nice_possivel', False)

        linhas.append('\n  FADIGA — Criterios IOM 2015 INCOMPLETOS')
        linhas.append('─' * 54)

        if nice_poss:
            linhas.append(f'\n  NICE 2021 POSSIVEL: {dur} meses (NICE aceita >= 4 meses)')
            linhas.append('  Aguardar completar 6 meses para criterios IOM completos.\n')

        if faltando:
            linhas.append('  Criterios faltando:')
            for c in faltando:
                linhas.append(f'  - {c}')

        if resultado.get('lab_pendente'):
            linhas.append('\n  ATENÇÃO: painel laboratorial nao realizado — solicitar primeiro.')

        phq2 = resultado.get('phq2', 0)
        gad2 = resultado.get('gad2', 0)
        sb   = resultado.get('stopbang', 0)
        if phq2 >= 3 or gad2 >= 3:
            linhas.append(f'\n  PHQ-2 = {phq2}, GAD-2 = {gad2} — rastrear transtorno de humor')
        if sb >= 3:
            linhas.append(f'  STOP-BANG = {sb}/8 — risco intermediario/alto de AOS')

        linhas.append('\n  Conduta:')
        for item in resultado.get('conduta', []):
            linhas.append(f'  • {item}')

        msg = resultado.get('mensagem', '')
        if msg:
            linhas.append(f'\n  {msg}')

        linhas.append('=' * 54)
        return '\n'.join(linhas)

    # Fallback
    linhas.append(f'\n  Categoria: {categoria}')
    for item in resultado.get('conduta', []):
        linhas.append(f'  • {item}')
    linhas.append('=' * 54)
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
    resultado   = interpretar_fadiga(dados)
    texto_saida = _formatar_resultado(resultado)
    print(texto_saida)
    _copiar_clipboard(texto_saida)
    return resultado
