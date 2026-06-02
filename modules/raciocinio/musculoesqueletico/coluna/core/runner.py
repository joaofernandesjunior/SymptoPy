# runner.py — Executa o diagnóstico completo de dor lombar (coluna)
# Carrega JSON completo (subjetivo + objetivo) → engine_coluna → imprime resultado
# Rodar da raiz: python -m modules.raciocinio.musculoesqueletico.coluna.core.runner

import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
from modules.raciocinio.musculoesqueletico.coluna.core.engine_coluna import interpretar_coluna


# =============================================================================
# CARREGAR JSON
# =============================================================================

def carregar_dados(caminho=None):
    if caminho:
        with open(caminho, encoding='utf-8') as f:
            return json.load(f)

    pasta = 'dados_pacientes'
    arquivos = [f for f in os.listdir(pasta) if f.startswith('coluna_completo_')]
    if not arquivos:
        # Fallback: tenta subjetivo se objetivo ainda não foi feito
        arquivos = [f for f in os.listdir(pasta) if f.startswith('coluna_subjetivo_')]
    if not arquivos:
        raise FileNotFoundError('Nenhum dado de coluna encontrado em dados_pacientes/. '
                                'Rode subjetivo.py e objetivo.py primeiro.')
    arquivos.sort(reverse=True)
    caminho = os.path.join(pasta, arquivos[0])
    print(f'  Carregando: {caminho}\n')
    with open(caminho, encoding='utf-8') as f:
        return json.load(f)


# =============================================================================
# IMPRESSÃO DO RESULTADO
# =============================================================================

SEP  = '=' * 55
SEP2 = '─' * 55

def imprimir_resultado(resultado, dados):
    print(f'\n{SEP}')
    print('  SYMPTOPY — Resultado: Dor Lombar (Coluna)')
    print(SEP)

    idade = dados.get('idade', '?')
    dor   = 'nova' if dados.get('dor_nova') else 'crônica/recorrente'
    eva   = dados.get('eva_dor', '?')
    print(f'  Paciente: {idade} anos | Dor: {dor} (EVA: {eva}/10)')

    # --- RED FLAG ---
    if resultado['categoria'] == 'red_flag_emergencia':
        print(f'\n  {"⚠️  RED FLAG DE EMERGÊNCIA":^51}')
        print(SEP2)
        for f in resultado['red_flags']['flags']:
            print(f"  [{f['urgencia'].upper()}] {f['achado']}")
            print(f"  → {f['acao']}")
        print('\n  Interromper avaliação de rotina. Conduta imediata acima.')
        return

    # --- PADRÃO INFLAMATÓRIO ---
    if resultado['categoria'] == 'padrao_inflamatorio':
        print(f'\n  ⚠️  PADRÃO INFLAMATÓRIO IDENTIFICADO')
        print(SEP2)
        p = resultado['padrao']
        print(f"  Achados: {', '.join(p['achados_inflamatorios'])}")
        print(f'\n  Exames sugeridos:')
        for e in p['exames_sugeridos']:
            print(f'    → {e}')
        print(f'\n  Conduta:')
        for c in p['conduta_padrao']:
            print(f'    → {c}')
        return

    # --- AVALIAÇÃO COMPLETA ---

    # Padrão e mecanismo
    print(f'\n  PADRÃO / MECANISMO')
    print(SEP2)
    padrao    = resultado['padrao']['padrao'].upper()
    mecanismo = resultado['mecanismo']['mecanismo_dominante'].upper()
    print(f'  Padrão:   {padrao}')
    print(f'  Mecanismo:{mecanismo}')
    if resultado['mecanismo']['alerta_nociplastico']:
        print('  ⚠️  Alerta nociplástico — AINE e infiltrações têm eficácia muito limitada')

    # Hipóteses prováveis
    if resultado['hipoteses_provaveis']:
        print(f'\n  DIAGNÓSTICO PROVÁVEL')
        print(SEP2)
        for h in resultado['hipoteses_provaveis']:
            print(f"  [{h['forca'].upper()}] {h['hipotese'].replace('_',' ').upper()} (score {h['score']})")
            print(f"  Achados positivos: {', '.join(h['positivos'])}")

            print(f'\n  1. CONDUTA BASE')
            for c in h['conduta']:
                print(f'     → {c}')

            print(f'\n  2. FISIOTERAPIA E EXERCÍCIOS')
            print(f'     → {h["fisioterapia"]}')

            print(f'\n  3. IMAGEM')
            print(f'     → {h["imagem"]}')

            if h.get('encaminhar'):
                print(f'\n  4. CRITÉRIOS DE ENCAMINHAMENTO')
                print(f'     → {h["encaminhar"]}')
            print()

    # Hipóteses possíveis
    if resultado['hipoteses_possiveis']:
        print(f'  TAMBÉM CONSIDERAR')
        print(SEP2)
        for h in resultado['hipoteses_possiveis']:
            print(f"  [{h['forca'].upper()}] {h['hipotese'].replace('_',' ').upper()} (score {h['score']})")
            print(f"         Achados: {', '.join(h['positivos'])}")

    # Hipóteses de exclusão
    if resultado['hipoteses_exclusao']:
        print(f'\n  EXCLUIR ATIVAMENTE')
        print(SEP2)
        for e in resultado['hipoteses_exclusao']:
            print(f'    ? {e.replace("_"," ")}')

    # Alertas Farmacológicos
    if resultado.get('alertas_farmacologicos'):
        print(f'\n  ALERTAS FARMACOLÓGICOS')
        print(SEP2)
        print(resultado['alertas_farmacologicos'])

    # Red flags de menor gravidade presentes
    flags_urgentes = [f for f in resultado['red_flags']['flags'] if f['urgencia'] == 'urgente']
    if flags_urgentes:
        print(f'\n  ⚠️  ALERTAS CLÍNICOS ADICIONAIS')
        print(SEP2)
        for f in flags_urgentes:
            print(f"  [{f['urgencia'].upper()}] {f['achado']}: {f['acao']}")

    print(SEP)


# =============================================================================
# MAIN
# =============================================================================

def rodar(caminho=None):
    dados     = carregar_dados(caminho)
    resultado = interpretar_coluna(dados)
    imprimir_resultado(resultado, dados)
    return resultado


if __name__ == '__main__':
    caminho = sys.argv[1] if len(sys.argv) > 1 else None
    rodar(caminho)
