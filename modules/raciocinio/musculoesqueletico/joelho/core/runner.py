# runner.py — Executa o diagnóstico completo de dor no joelho
# Carrega JSON completo (subjetivo + objetivo) → engine → imprime resultado
# Rodar da raiz: python3 -m modules.raciocinio.musculoesqueletico.joelho.core.runner

import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
from modules.raciocinio.musculoesqueletico.joelho.core.engine import interpretar_joelho


# =============================================================================
# CARREGAR JSON
# =============================================================================

def carregar_dados(caminho=None):
    if caminho:
        with open(caminho, encoding='utf-8') as f:
            return json.load(f)

    pasta = 'dados_pacientes'
    arquivos = [f for f in os.listdir(pasta) if f.startswith('joelho_completo_')]
    if not arquivos:
        # Fallback: tenta subjetivo se objetivo ainda não foi feito
        arquivos = [f for f in os.listdir(pasta) if f.startswith('joelho_subjetivo_')]
    if not arquivos:
        raise FileNotFoundError('Nenhum dado encontrado em dados_pacientes/. '
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
    print('  SYMPTOPY — Resultado: Dor no Joelho')
    print(SEP)

    idade = dados.get('idade', '?')
    dor   = 'nova' if dados.get('dor_nova') else 'crônica/recorrente'
    print(f'  Paciente: {idade} anos | Dor: {dor}')

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

    # Ottawa
    if resultado.get('ottawa') and resultado['ottawa']['indicar_radiografia']:
        print(f'\n  📋 OTTAWA — IMAGEM INDICADA')
        print(SEP2)
        print(f"  {resultado['ottawa']['acao']}")
        for c in resultado['ottawa']['criterios_positivos']:
            print(f'    + {c}')

    # Padrão e mecanismo
    print(f'\n  PADRÃO / MECANISMO')
    print(SEP2)
    padrao   = resultado['padrao']['padrao'].upper()
    mecanismo= resultado['mecanismo']['mecanismo_dominante'].upper()
    print(f'  Padrão:   {padrao}')
    print(f'  Mecanismo:{mecanismo}')
    if resultado['mecanismo']['alerta_nociplastico']:
        print('  ⚠️  Alerta nociplástico — AINE e infiltração têm eficácia limitada')

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

            print(f'\n  2. IMAGEM')
            print(f'     → {h["imagem"]}')

            encaminhar = next((c for c in h['conduta'] if 'encaminhar' in c.lower()), None)
            if encaminhar:
                print(f'\n  3. ENCAMINHAR')
                print(f'     → {encaminhar}')

            print(f'\n  4. INFILTRAÇÃO')
            if h['candidato_infiltracao']:
                print(f'     ✅ Candidato: {h["motivo_infiltracao"]}')
                print(f'     Tipo sugerido: {h["tipo_sugerido"]}')
                if h['bloqueios_seguranca']:
                    print(f'     Bloqueios de segurança:')
                    for b in h['bloqueios_seguranca']:
                        print(f'       ⛔ {b}')
                print(f'     → Para prosseguir: abrir módulo de procedimentos')
            else:
                print(f'     ❌ Não candidato: {h["motivo_infiltracao"]}')
                if h['bloqueios_seguranca']:
                    for b in h['bloqueios_seguranca']:
                        print(f'       ⛔ {b}')

            print()

    # Hipóteses possíveis
    if resultado['hipoteses_possiveis']:
        print(f'  TAMBÉM CONSIDERAR')
        print(SEP2)
        for h in resultado['hipoteses_possiveis']:
            print(f"  [{h['forca'].upper()}] {h['hipotese'].replace('_',' ')} (score {h['score']})")
            print(f"         {', '.join(h['positivos'])}")

    # Hipóteses de exclusão
    if resultado['hipoteses_exclusao']:
        print(f'\n  EXCLUIR ATIVAMENTE')
        print(SEP2)
        for e in resultado['hipoteses_exclusao']:
            print(f'    ? {e.replace("_"," ")}')

    # Red flags presentes mas não bloqueantes
    flags_urgentes = [f for f in resultado['red_flags']['flags']
                      if f['urgencia'] == 'urgente']
    if flags_urgentes:
        print(f'\n  ⚠️  RED FLAGS URGENTES (não emergência)')
        print(SEP2)
        for f in flags_urgentes:
            print(f"  [{f['urgencia'].upper()}] {f['achado']}: {f['acao']}")

    print(SEP)


# =============================================================================
# MAIN
# =============================================================================

def rodar(caminho=None):
    dados    = carregar_dados(caminho)
    resultado= interpretar_joelho(dados)
    imprimir_resultado(resultado, dados)
    return resultado


if __name__ == '__main__':
    caminho = sys.argv[1] if len(sys.argv) > 1 else None
    rodar(caminho)