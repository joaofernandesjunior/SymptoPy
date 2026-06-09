# prontuario/admissao.py
# Coleta dados de admissão — ordem clínica correta:
# queixa → HMA → sinais vitais → exame físico geral → subjetivo específico → objetivo específico
# Para adicionar queixa nova: só adicionar entrada no dispatcher e em texto.py

from prontuario.objetivo import coletar_objetivo
from utils.perguntas import sn

def coletar_admissao():
    admissao = {}

    admissao['queixa_principal'] = input('Queixa principal (usar sintoma cru: dispneia, febre, dor abdominal, cefaleia): ').strip()
    admissao['hma'] = input('HMA: ').strip()

    # Sinais vitais — antes do exame físico
    admissao['pa']          = input('PA: ').strip()
    admissao['fc']          = input('FC: ').strip()
    admissao['fr']          = input('FR: ').strip()
    admissao['sato2']       = input('Saturação O2: ').strip()
    admissao['temperatura'] = input('Temperatura: ').strip()
    admissao['glicemia']    = input('Glicemia capilar: ').strip()

    # Exame físico geral — vem aqui, antes do módulo específico
    admissao['objetivo'] = coletar_objetivo()

    # Subjetivo e objetivo específicos ficam vazios aqui
    # São preenchidos pelo dispatcher após a admissão
    admissao['subjetivo_especifico'] = {}
    admissao['objetivo_especifico']  = {}

    # Módulos legados (dispneia, vertigem, cefaleia) ainda preenchem aqui
    # para manter compatibilidade — dispatcher vai ler daqui
    queixa = admissao['queixa_principal'].lower()

    if queixa == 'dispneia':
        from modules.sintomas.dispneia.dispneia_subjetivo import coletar_dispneia
        from modules.sintomas.dispneia.dispneia_objetivo import coletar_objetivo_dispneia
        admissao['subjetivo_especifico']['dispneia'] = coletar_dispneia()
        admissao['objetivo_especifico']['dispneia']  = coletar_objetivo_dispneia()

    elif queixa == 'vertigem':
        from modules.sintomas.vertigem.vertigem_subjetivo import coletar_subjetivo_vertigem
        from modules.sintomas.vertigem.vertigem_objetivo import coletar_objetivo_vertigem
        admissao['subjetivo_especifico']['vertigem'] = coletar_subjetivo_vertigem()
        admissao['objetivo_especifico']['vertigem']  = coletar_objetivo_vertigem()

    elif queixa == 'cefaleia':
        from modules.sintomas.cefaleia.cefaleia_subjetivo import coletar_subjetivo_cefaleia
        from modules.sintomas.cefaleia.cefaleia_objetivo import objetivo_cefaleia
        admissao['subjetivo_especifico']['cefaleia'] = coletar_subjetivo_cefaleia()
        exame_cefaleia = {
            'deficit_neuro': sn('Déficit neurológico focal ao exame? [s/n] '),
            'rigidez_nuca':  sn('Rigidez de nuca ao exame? [s/n] '),
            'papiledema':    sn('Papiledema ao exame? [s/n] '),
        }
        admissao['objetivo_especifico']['cefaleia'] = objetivo_cefaleia(exame_cefaleia)

    # Módulos MSK — subjetivo e objetivo são coletados pelo dispatcher
    # depois da admissão, então ficam vazios aqui. O resultado MSK
    # chega em admissao['analise_automatica'] e admissao['dados_msk']

    admissao['exames_complementares'] = input('Exames complementares: ').strip()
    # Análise e Plano são gerados automaticamente pelo módulo clínico
    admissao['analise'] = ''
    admissao['plano']   = ''

    return admissao