# modules/raciocinio/ivas/runner.py
# Formatação e exibição dos resultados — IVAS / Faringite

import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from modules.raciocinio.ivas.engine_ivas import interpretar_ivas

_LABEL = {
    'ivas_emergencia':    'EMERGENCIA FARINGEA / CERVICAL',
    'ivas_mononucleose':  'MONONUCLEOSE INFECCIOSA (EBV) — SUSPEITA',
    'ivas_influenza':     'INFLUENZA — SUSPEITA',
    'ivas_gas':           'FARINGITE — AVALIACAO GAS (Estreptococo Grupo A)',
    'ivas_rinossinusite': 'RINOSSINUSITE AGUDA',
    'ivas_laringite':     'LARINGITE AGUDA',
    'ivas_viral':         'IVAS VIRAL / FARINGITE VIRAL',
}

_SCORE_LABEL = {
    -1: 'McIsaac -1 — Probabilidade GAS < 7%  → sem teste, sem ATB',
     0: 'McIsaac  0 — Probabilidade GAS  7-13% → sem teste, sem ATB',
     1: 'McIsaac  1 — Probabilidade GAS  7-13% → sem teste, sem ATB',
     2: 'McIsaac  2 — Probabilidade GAS 21-38% → realizar RADT',
     3: 'McIsaac  3 — Probabilidade GAS 21-38% → realizar RADT',
     4: 'McIsaac  4 — Probabilidade GAS 51-70% → RADT ou tratar',
     5: 'McIsaac  5 — Probabilidade GAS 51-70% → RADT ou tratar',
}


# =============================================================================
# BOXES DE ALERTA
# =============================================================================

def _box_emergencia(tipo):
    w = 56
    nomes = {
        'abscesso_peritonsilar': 'ABSCESSO PERITONSILAR — ENCAMINHAR URGENTE',
        'epiglotite':            'EPIGLOTITE — NAO MANIPULAR VIA AEREA',
        'ludwig':                'ANGINA DE LUDWIG — CIRURGIA URGENTE',
    }
    titulo = nomes.get(tipo, 'EMERGENCIA — VIA AEREA EM RISCO')
    return [
        '╔' + '═' * w + '╗',
        '║' + f'  !! {titulo} !!'.center(w) + '║',
        '║     Acionar especialidade / SAMU imediatamente        ║',
        '║     Monitorar via aerea — risco de obstrucao          ║',
        '╚' + '═' * w + '╝',
    ]


def _box_mono():
    w = 56
    return [
        '╔' + '═' * w + '╗',
        '║   !! MONONUCLEOSE — AMOXICILINA/AMPICILINA PROIBIDAS ║',
        '║   Rash em 80-100% dos casos com aminopenicilina       ║',
        '║   Restrição de esportes de contato: 4-6 SEMANAS       ║',
        '╚' + '═' * w + '╝',
    ]


def _box_atb_condicional(atb_rec, atb_alt):
    """Box de receita condicional — RADT aguardado.

    Mostra doses completas com instrução 'SE RADT POSITIVO' para que o médico
    já saiba exatamente o que prescrever sem precisar reconsultar o sistema.
    """
    w = 56

    def _linha(txt):
        chunks = _chunk(txt, w - 2)
        resultado = []
        for c in chunks:
            resultado.append('║  ' + c.ljust(w - 2) + '║')
        return resultado

    linhas = [
        '╔' + '═' * w + '╗',
        '║' + '  RECEITA CONDICIONAL — SE RADT POSITIVO'.center(w) + '║',
        '╠' + '═' * w + '╣',
    ]
    linhas += _linha(atb_rec['medicamento'])
    linhas += _linha(f'Dose: {atb_rec["dose"]}')
    linhas += _linha(f'Via:  {atb_rec["via"]}')
    linhas += _linha(f'Duracao: {atb_rec["duracao"]}')
    if atb_rec.get('nota'):
        linhas += _linha(f'Nota: {atb_rec["nota"]}')
    if atb_alt:
        linhas.append('╠' + '─' * w + '╣')
        linhas += _linha(f'Alternativo: {atb_alt["medicamento"]}')
        linhas += _linha(f'Dose: {atb_alt["dose"]} por {atb_alt["duracao"]}')
    linhas.append('╠' + '─' * w + '╣')
    linhas += _linha('!! 10 dias OBRIGATORIOS — cursos menores nao erradicam GAS')
    linhas.append('╚' + '═' * w + '╝')
    return linhas


def _box_atb(atb):
    """Box de prescrição para GAS confirmado / tratamento empírico."""
    w = 56

    def _linha(txt):
        # garante w-2 chars de conteúdo após '║  ' e antes de '║'
        chunks = _chunk(txt, w - 2)
        resultado = []
        for c in chunks:
            resultado.append('║  ' + c.ljust(w - 2) + '║')
        return resultado

    linhas = [
        '╔' + '═' * w + '╗',
        '║' + '  PRESCRICAO — FARINGITE GAS'.center(w) + '║',
        '╠' + '═' * w + '╣',
    ]
    linhas += _linha(atb['medicamento'])
    linhas += _linha(f'Dose: {atb["dose"]}')
    linhas += _linha(f'Via:  {atb["via"]}')
    linhas += _linha(f'Duracao: {atb["duracao"]}')
    if atb.get('nota'):
        linhas += _linha(f'Nota: {atb["nota"]}')
    linhas.append('╠' + '─' * w + '╣')
    linhas += _linha('!! 10 dias OBRIGATORIOS — cursos menores nao erradicam GAS')
    linhas.append('╚' + '═' * w + '╝')
    return linhas


def _chunk(texto, largura):
    """Divide texto longo em linhas de no máximo `largura` caracteres."""
    palavras = texto.split()
    linhas, atual = [], ''
    for p in palavras:
        if len(atual) + len(p) + 1 <= largura:
            atual = (atual + ' ' + p).strip()
        else:
            if atual:
                linhas.append(atual)
            atual = p
    if atual:
        linhas.append(atual)
    return linhas or ['']


# =============================================================================
# RECEITUÁRIO — formato "receita de gaveta" (sem boxes)
# =============================================================================

def _formatar_rx(atb, prefixo='Prescreva:'):
    """Formata ATB como receita de gaveta médica — nome, quantidade, posologia."""
    linhas = [f'\n  {prefixo}']
    nome = atb.get('medicamento', '')
    for i, p in enumerate(atb.get('prescricoes', [])):
        if i > 0:
            linhas.append('  ou')
        qtd  = str(p['quantidade'])
        uni  = p['unidade']
        fill = max(3, 54 - len(nome) - len(qtd) - len(uni))
        linhas.append(f'  {nome} {"-" * fill} {qtd} {uni}')
        linhas.append(f'    {p["posologia"]}')
    if atb.get('nota'):
        linhas.append(f'    * {atb["nota"]}')
    return linhas


# =============================================================================
# FORMATAÇÃO PRINCIPAL
# =============================================================================

def _formatar_resultado(resultado):
    categoria = resultado.get('categoria', '')
    linhas = []

    linhas.append('=' * 58)
    linhas.append('  RESULTADO — IVAS / FARINGITE')
    linhas.append('=' * 58)

    label = _LABEL.get(categoria, categoria.upper())
    linhas.append(f'\n  {label}')

    # Score McIsaac (sempre mostrar, salvo emergência pura)
    score = resultado.get('score_mcisaac')
    if score is not None:
        linhas.append(f'\n  {_SCORE_LABEL.get(score, f"McIsaac {score}")}')

    # Critérios usados — raciocínio clínico explícito
    criterios_str = resultado.get('criterios_usados')
    if criterios_str:
        linhas.append(f'  {criterios_str}')

    linhas.append('')

    # ── Boxes de alerta ──────────────────────────────────────────────────────
    if categoria == 'ivas_emergencia':
        tipo = resultado.get('emergencia_tipo', '')
        linhas.extend(_box_emergencia(tipo))
        sinais = resultado.get('sinais_presentes', '')
        if sinais:
            linhas.append(f'\n  Sinais identificados: {sinais}')

    if categoria == 'ivas_mononucleose' and resultado.get('amoxicilina_contraindicada'):
        linhas.extend(_box_mono())

    # ── Conduta ──────────────────────────────────────────────────────────────
    linhas.append('\n  Conduta:')
    for item in resultado.get('conduta', []):
        if item == '':
            linhas.append('')
        elif item.startswith('---'):
            linhas.append(f'\n  {item}')
        else:
            linhas.append(f'  • {item}')

    # ── Receita (GAS) — receituário de gaveta ────────────────────────────────
    if categoria == 'ivas_gas':
        rec           = resultado.get('recomendacao_atb', '')
        atb_principal = resultado.get('atb_prescrito') or resultado.get('atb_recomendado')
        atb_alt       = resultado.get('atb_alternativo')
        if atb_principal and rec != 'nao_tratar':
            prefixo = 'Se RADT positivo — Prescreva:' if rec == 'indicar_radt' else 'Receita:'
            linhas.extend(_formatar_rx(atb_principal, prefixo))
            if atb_alt:
                linhas.extend(_formatar_rx(atb_alt, 'Alternativo:'))
            linhas.append('\n  !! 10 dias obrigatórios — cursos menores não erradicam GAS')

    # ── Exames ───────────────────────────────────────────────────────────────
    exames = resultado.get('exames', [])
    if exames:
        linhas.append('\n  Exames:')
        for ex in exames:
            if ex.startswith('  '):
                linhas.append(f'  {ex}')
            else:
                linhas.append(f'  • {ex}')

    # ── Sinais de retorno ────────────────────────────────────────────────────
    retorno = resultado.get('sinais_retorno', [])
    if retorno:
        linhas.append('\n  Retorno imediato se:')
        for s in retorno:
            linhas.append(f'  - {s}')

    # ── Internação ───────────────────────────────────────────────────────────
    if resultado.get('internacao'):
        linhas.append('\n  !! INTERNACAO / REFERENCIA URGENTE INDICADA !!')

    linhas.append('\n' + '=' * 58)
    return '\n'.join(linhas)


def _copiar_clipboard(texto):
    try:
        import subprocess
        proc = subprocess.Popen(['clip'], stdin=subprocess.PIPE)
        proc.communicate(texto.encode('utf-8'))
        print('\n  [Impressao copiada para o clipboard]')
    except Exception:
        pass


def rodar(arquivo_json):
    sys.stdout.reconfigure(encoding='utf-8')
    with open(arquivo_json, encoding='utf-8') as f:
        dados = json.load(f)
    resultado   = interpretar_ivas(dados)
    texto_saida = _formatar_resultado(resultado)
    print(texto_saida)
    _copiar_clipboard(texto_saida)
    return resultado
