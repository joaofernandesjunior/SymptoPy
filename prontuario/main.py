# prontuario/main.py
# Prontuário Básico V2 — arquitetura com dispatcher central
# Para adicionar novos módulos: editar prontuario/dispatcher.py
# Este arquivo não precisa mudar quando novos módulos entram

from prontuario.paciente import coletar_paciente
from prontuario.admissao import coletar_admissao
from prontuario.texto import gerar_texto_prontuario
from prontuario.comorbidades.drc import tem_drc, coletar_complemento_drc, avaliar_drc
from prontuario.dispatcher import despachar


def main():
    print('=== PRONTUÁRIO BÁSICO V2 ===')

    # --- identificação e admissão ---
    paciente = coletar_paciente()
    admissao = coletar_admissao()

    # --- análise automática — suporta múltiplas queixas ---
    # Todo o roteamento está em prontuario/dispatcher.py
    # Não adicione lógica aqui — adicione entradas no dispatcher
    admissao['analises_automaticas'] = []

    queixa_atual = admissao['queixa_principal']
    while queixa_atual:
        resultado = despachar(queixa=queixa_atual, admissao=admissao, paciente=paciente)
        if resultado is not None:
            admissao['analises_automaticas'].append({
                'queixa':    queixa_atual,
                'resultado': resultado,
            })
            # compat: última análise fica também em analise_automatica
            admissao['analise_automatica'] = resultado

        resp = input('\n  Adicionar outra queixa à admissão? [s/n] ').strip().lower()
        if resp != 's':
            break
        queixa_atual = input('  Queixa: ').strip()

    # --- módulos complementares por comorbidade ---
    admissao['comorbidades_automaticas']   = {}
    admissao['comorbidades_complementares'] = {}

    if tem_drc(paciente['comorbidades']):
        abrir = input('\nAbrir perguntas complementares de DRC? [s/n] ').strip().lower() == 's'
        if abrir:
            admissao['comorbidades_complementares']['drc'] = coletar_complemento_drc()
        resultado_drc = avaliar_drc(paciente, admissao)
        if resultado_drc:
            admissao['comorbidades_automaticas']['drc'] = resultado_drc

    # --- texto final ---
    texto_final = gerar_texto_prontuario(paciente, admissao)
    print('\n=== TEXTO FINAL ===\n')
    print(texto_final)


if __name__ == '__main__':
    main()