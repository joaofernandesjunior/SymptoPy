# runner_ombro.py — Resultado completo de dor no ombro
# Carrega JSON (subjetivo + objetivo) → engine → imprime
# Rodar da raiz: python3 -m modules.raciocinio.musculoesqueletico.ombro.core.runner_ombro
# Ou com caminho: python3 -m ... dados_pacientes/ombro_completo_XXXXXX.json

import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
from modules.raciocinio.musculoesqueletico.ombro.core.engine_ombro import interpretar_ombro

SEP  = '=' * 55
SEP2 = '─' * 55


# =============================================================================
# CARREGAR JSON
# =============================================================================

def carregar_dados(caminho=None):
    if caminho:
        with open(caminho, encoding='utf-8') as f:
            return json.load(f)

    pasta = 'dados_pacientes'
    arquivos = [f for f in os.listdir(pasta) if f.startswith('ombro_completo_')]
    if not arquivos:
        arquivos = [f for f in os.listdir(pasta) if f.startswith('ombro_subjetivo_')]
    if not arquivos:
        raise FileNotFoundError(
            'Nenhum dado de ombro encontrado em dados_pacientes/.\n'
            'Rode subjetivo_ombro.py e objetivo_ombro.py primeiro.'
        )
    arquivos.sort(reverse=True)
    caminho = os.path.join(pasta, arquivos[0])
    print(f'  Carregando: {caminho}\n')
    with open(caminho, encoding='utf-8') as f:
        return json.load(f)


# =============================================================================
# IMPRESSÃO
# =============================================================================

def imprimir_resultado(resultado, dados):
    print(f'\n{SEP}')
    print('  SYMPTOPY — Resultado: Dor no Ombro')
    print(SEP)

    idade = dados.get('idade', '?')
    lado  = 'direito' if dados.get('lado_direito') else \
            'esquerdo' if dados.get('lado_esquerdo') else 'bilateral'
    dor   = 'nova' if dados.get('dor_nova') else 'crônica/recorrente'
    print(f'  Paciente: {idade} anos | Ombro: {lado} | Dor: {dor}')

    # --- RED FLAG EMERGÊNCIA ---
    if resultado['categoria'] == 'red_flag_emergencia':
        print(f'\n  ⚠️  RED FLAG DE EMERGÊNCIA')
        print(SEP2)
        for f in resultado['red_flags']['flags']:
            print(f"  [{f['urgencia'].upper()}] {f['achado']}")
            print(f"  → {f['acao']}")
        print('\n  Interromper avaliação de rotina. Conduta imediata acima.')
        return

    # --- RED FLAG CARDIOVASCULAR ---
    if resultado['categoria'] == 'red_flag_cardiovascular':
        print(f'\n  ⚠️  POSSÍVEL DOR REFERIDA CARDÍACA')
        print(SEP2)
        print(f"  {resultado['mensagem']}")
        print('  → ECG e troponina se indicado antes de tratar ombro.')
        return

    # --- PADRÃO INFLAMATÓRIO ---
    if resultado['categoria'] == 'padrao_inflamatorio':
        print(f'\n  ⚠️  PADRÃO INFLAMATÓRIO')
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

    # Alerta de trauma (não bloqueia — diagnóstico continua abaixo)
    if resultado.get('alerta_trauma'):
        print(f'\n  ⚠️  TRAUMA PRESENTE')
        print(SEP2)
        print(f"  → {resultado['alerta_trauma']}")

    # Padrão e mecanismo
    print(f'\n  PADRÃO / MECANISMO')
    print(SEP2)
    padrao    = resultado['padrao']['padrao'].upper()
    mecanismo = resultado['mecanismo']['mecanismo_dominante'].upper()
    print(f'  Padrão:    {padrao}')
    print(f'  Mecanismo: {mecanismo}')
    if resultado['mecanismo']['alerta_nociplastico']:
        print('  ⚠️  Alerta nociplástico — AINE e infiltração têm eficácia limitada')

    # Hipóteses prováveis
    if resultado['hipoteses_provaveis']:
        print(f'\n  DIAGNÓSTICO PROVÁVEL')
        print(SEP2)
        for h in resultado['hipoteses_provaveis']:
            nome = h['hipotese'].replace('_', ' ').upper()
            print(f"  [{h['forca'].upper()}] {nome} (score {h['score']})")
            print(f"  Achados: {', '.join(h['positivos'][:4])}")

            print(f'\n  1. CONDUTA')
            for c in h['conduta']:
                print(f'     → {c}')

            print(f'\n  2. IMAGEM')
            print(f'     → {h["imagem"]}')

            if h.get('encaminhar'):
                print(f'\n  3. ENCAMINHAR')
                print(f'     → {h["encaminhar"]}')

            print(f'\n  4. FISIOTERAPIA')
            print(f'     → {h["fisioterapia"]}')

            print(f'\n  5. INFILTRAÇÃO')
            if h['candidato_infiltracao']:
                print(f'     ✅ Candidato: {h["motivo_infiltracao"]}')
                if h.get('sito_injecao'):
                    print(f'     Sítio: {h["sito_injecao"]}')
                if h['bloqueios_seguranca']:
                    print(f'     Bloqueios de segurança:')
                    for b in h['bloqueios_seguranca']:
                        print(f'       ⛔ {b}')
                print(f'     → Para prosseguir: abrir módulo de procedimentos')
            else:
                print(f'     ❌ {h["motivo_infiltracao"]}')
                for b in h['bloqueios_seguranca']:
                    print(f'       ⛔ {b}')
            print()

    # Hipóteses possíveis
    if resultado['hipoteses_possiveis']:
        print(f'  TAMBÉM CONSIDERAR')
        print(SEP2)
        for h in resultado['hipoteses_possiveis']:
            nome = h['hipotese'].replace('_', ' ')
            print(f"  [{h['forca'].upper()}] {nome} (score {h['score']})")
            if h['positivos']:
                print(f"         {', '.join(h['positivos'][:3])}")

    # Hipóteses de exclusão
    if resultado['hipoteses_exclusao']:
        print(f'\n  EXCLUIR ATIVAMENTE')
        print(SEP2)
        for e in resultado['hipoteses_exclusao']:
            print(f'    ? {e.replace("_", " ")}')

    # Alertas farmacológicos
    if resultado.get('alertas_farmacologicos'):
        print(f'\n  ALERTAS FARMACOLÓGICOS')
        print(SEP2)
        print(resultado['alertas_farmacologicos'])

    # Red flags urgentes não bloqueantes
    flags_urgentes = [
        f for f in resultado['red_flags']['flags']
        if f['urgencia'] == 'urgente'
    ]
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
    dados     = carregar_dados(caminho)
    resultado = interpretar_ombro(dados)
    imprimir_resultado(resultado, dados)
    return resultado


if __name__ == '__main__':
    caminho = sys.argv[1] if len(sys.argv) > 1 else None
    rodar(caminho)