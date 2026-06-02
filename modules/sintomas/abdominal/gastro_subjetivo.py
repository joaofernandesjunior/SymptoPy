# modules/sintomas/abdominal/gastro_subjetivo.py
# Anamnese dirigida — Dor Abdominal e Queixas GI (Adulto)
#
# Cobre: red flags cirúrgicas, dispepsia/PUD, H. pylori, cólica biliar,
#        SII (C/D/M), constipação funcional, diverticulite, isquemia mesentérica,
#        DIP, gravidez ectópica, doença celíaca, IBD, parasitoses, GECA, náuseas.
#
# Retorna: (dados: dict, arquivo_json: str)
# Padrão: igual a urinario/subjetivo.py — salva JSON e retorna (dados, path)

import json
import os
import sys
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))


# =============================================================================
# PERSISTÊNCIA
# =============================================================================

def _salvar(dados, pasta='dados_pacientes'):
    os.makedirs(pasta, exist_ok=True)
    ts   = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome = os.path.join(pasta, f'gastro_subjetivo_{ts}.json')
    with open(nome, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f'\n  Dados salvos: {nome}')
    return nome


# =============================================================================
# PONTO DE ENTRADA PRINCIPAL
# =============================================================================

def coletar_subjetivo_abdominal(dados_preenchidos=None):
    """
    Coleta anamnese dirigida para dor abdominal e queixas GI.

    Parâmetros
    ----------
    dados_preenchidos : dict, opcional
        Dados demográficos já coletados (idade, sexo) para não repetir.

    Retorna
    -------
    (dados: dict, arquivo_json: str)
    """
    sys.stdout.reconfigure(encoding='utf-8')

    print('\n' + '=' * 56)
    print('  SYMPTOPY — Anamnese: Dor Abdominal / Queixas GI')
    print('=' * 56)
    print('  Digite o número da opção. Multi-seleção: ex. 1 3 5\n')

    dados = dict(dados_preenchidos) if dados_preenchidos else {}

    # ═══════════════════════════════════════════════════════════════
    # BLOCO 0 — DADOS BÁSICOS
    # ═══════════════════════════════════════════════════════════════
    print('\n── BLOCO 0: Dados Básicos ──')

    if 'sexo_feminino' not in dados:
        sexo = input('Sexo biológico:\n  1 Feminino\n  2 Masculino\n→ ').strip()
        dados['sexo_feminino'] = (sexo == '1')

    if 'idade' not in dados:
        try:
            dados['idade'] = int(input('\nIdade: ').strip())
        except ValueError:
            dados['idade'] = 0
    dados['idoso'] = dados.get('idade', 0) >= 60

    # ═══════════════════════════════════════════════════════════════
    # BLOCO 1 — LOCALIZAÇÃO
    # ═══════════════════════════════════════════════════════════════
    print("""
── BLOCO 1: Localização Principal da Dor ──
  1  Epigástrio (boca do estômago / acima do umbigo)
  2  Hipocôndrio direito / FSD (abaixo das costelas à direita)
  3  Fossa ilíaca direita / FID (baixo abdôme à direita)
  4  Fossa ilíaca esquerda / FIE (baixo abdôme à esquerda)
  5  Hipogástrio / região pélvica (baixo centro)
  6  Periumbilical (ao redor do umbigo)
  7  Difuso / todo o abdôme
  8  Lombar com irradiação para a virilha (→ cólica renal — módulo urinário)""")
    loc = input('→ ').strip()
    dados['localizacao'] = {
        '1': 'epigastrico', '2': 'fsd',    '3': 'fid',
        '4': 'fie',         '5': 'hipogastrico_pelvico',
        '6': 'periumbilical', '7': 'difuso', '8': 'lombar_renal',
    }.get(loc, 'difuso')

    # ═══════════════════════════════════════════════════════════════
    # BLOCO 2 — CARÁTER E INTENSIDADE
    # ═══════════════════════════════════════════════════════════════
    print("""
── BLOCO 2: Caráter da Dor ──
  1  Cólica / espasmo (vem e passa, vem e passa)
  2  Constante / pressão / aperto
  3  Queimação / azia / ardor
  4  Distensão / inchaço / plenitude pós-refeição
  5  Facada / aguda de início súbito e intenso
  6  Difusa / leve / mal-definida""")
    car = input('→ ').strip()
    dados['carater'] = {
        '1': 'colica', '2': 'constante', '3': 'queimacao',
        '4': 'distensao', '5': 'aguda_subita', '6': 'difusa_leve',
    }.get(car, 'difusa_leve')
    dados['inicio_subito'] = dados['carater'] == 'aguda_subita'

    print("""
Intensidade:
  1  Leve — consegue falar normalmente e trabalhar
  2  Moderada — atrapalha atividades do dia
  3  Intensa — não consegue ficar quieto / vai ao PS
  4  Catastrófica — pior dor da vida, início abrupto""")
    intens = input('→ ').strip()
    dados['intensidade']      = {'1': 'leve', '2': 'moderada',
                                  '3': 'intensa', '4': 'catastrofica'}.get(intens, 'moderada')
    dados['dor_catastrofica'] = dados['intensidade'] == 'catastrofica'

    # ═══════════════════════════════════════════════════════════════
    # BLOCO 3 — RELAÇÃO COM ALIMENTAÇÃO
    # ═══════════════════════════════════════════════════════════════
    print("""
── BLOCO 3: Relação com Alimentação ──
  1  Piora após refeição (qualquer)
  2  Piora especificamente após gordurosos / frituras
  3  Piora em jejum / alivia após comer
  4  Piora após glúten (pão, macarrão, biscoito)
  5  Piora após laticínios (leite, queijo, iogurte)
  6  Sem relação clara com alimentação""")
    alim = input('→ ').strip()
    dados['relacao_alimentar'] = {
        '1': 'piora_pos_refeicao', '2': 'piora_gorduroso',
        '3': 'piora_jejum',        '4': 'piora_gluten',
        '5': 'piora_lactose',      '6': 'sem_relacao',
    }.get(alim, 'sem_relacao')
    dados['piora_gorduroso'] = dados['relacao_alimentar'] == 'piora_gorduroso'
    dados['piora_gluten']    = dados['relacao_alimentar'] == 'piora_gluten'
    dados['piora_lactose']   = dados['relacao_alimentar'] == 'piora_lactose'

    # ═══════════════════════════════════════════════════════════════
    # BLOCO 4 — HÁBITO INTESTINAL
    # ═══════════════════════════════════════════════════════════════
    print("""
── BLOCO 4: Hábito Intestinal Atual ──
  1  Normal para mim
  2  Constipação (< 3 evacuações/semana ou fezes duras / esforço)
  3  Diarreia (fezes líquidas ou amolecidas, > 3×/dia)
  4  Alternância — às vezes constipa, às vezes diarreia
  5  Sem evacuar E sem passar gases há > 24h""")
    habi = input('→ ').strip()
    dados['habito_intestinal'] = {
        '1': 'normal', '2': 'constipacao', '3': 'diarreia',
        '4': 'alternancia', '5': 'sem_evacuacao_gases',
    }.get(habi, 'normal')
    dados['obstipacao_total'] = dados['habito_intestinal'] == 'sem_evacuacao_gases'

    # ═══════════════════════════════════════════════════════════════
    # BLOCO 5 — CARACTERÍSTICAS DAS FEZES (condicional)
    # ═══════════════════════════════════════════════════════════════
    if dados['habito_intestinal'] in ('diarreia', 'alternancia', 'constipacao'):
        print("""
── BLOCO 5: Características das Fezes ──
  1  Duras / ressecadas / em cíbalos (bolinhas)
  2  Amolecidas / pastosas
  3  Líquidas / aquosas
  4  Com sangue vivo / vermelho (hematoquezia)
  5  Com muco (geleia transparente ou branca)
  6  Sangue escuro / alcatroado — melena (sangue digerido)
  7  Gordurosas / oleosas / difícil limpar (esteatorreia)
  8  Aspecto normal para mim""")
        fezes = input('→ ').strip()
        dados['fezes'] = {
            '1': 'duras', '2': 'amolecidas', '3': 'liquidas',
            '4': 'hematoquezia', '5': 'muco', '6': 'melena',
            '7': 'esteatorreia', '8': 'normal',
        }.get(fezes, 'normal')
    else:
        dados['fezes'] = 'normal'

    dados['hematoquezia'] = dados['fezes'] == 'hematoquezia'
    dados['muco_fezes']   = dados['fezes'] == 'muco'
    dados['melena']       = dados['fezes'] == 'melena'
    dados['esteatorreia'] = dados['fezes'] == 'esteatorreia'
    dados['sangue_fezes'] = dados['hematoquezia'] or dados['melena']

    # ═══════════════════════════════════════════════════════════════
    # BLOCO 6 — FEBRE E SINTOMAS SISTÊMICOS
    # ═══════════════════════════════════════════════════════════════
    print("""
── BLOCO 6: Febre ──
  1  Não / temperatura normal (< 37,5°C)
  2  Febrícula / subfebril (37,5–38°C)
  3  Febre moderada (38–39°C)
  4  Febre alta (> 39°C / calafrios, tremores)""")
    feb = input('→ ').strip()
    dados['febre_grau'] = {'1': 'sem', '2': 'baixa',
                            '3': 'moderada', '4': 'alta'}.get(feb, 'sem')
    dados['febre']      = dados['febre_grau'] != 'sem'
    dados['febre_alta'] = dados['febre_grau'] == 'alta'

    print("""
Náuseas e/ou vômitos?
  1  Não
  2  Náusea sem vômito
  3  Vômito alimentar (conteúdo gástrico normal)
  4  Vômito em borra de café / escuro (sangue digerido)
  5  Hematêmese — vômito com sangue vivo""")
    nv = input('→ ').strip()
    dados['nausea']     = nv in ('2', '3', '4', '5')
    dados['vomito']     = nv in ('3', '4', '5')
    dados['hematemese'] = nv in ('4', '5')

    # ═══════════════════════════════════════════════════════════════
    # BLOCO 7 — SINAIS DE ALARME SISTÊMICOS (multi-seleção)
    # ═══════════════════════════════════════════════════════════════
    print("""
── BLOCO 7: Sinais de Alarme (ex: 1 3) ──
  1  Perda de peso involuntária (> 5% em 6 meses sem tentar)
  2  Anorexia / sem apetite há dias
  3  Icterícia (pele ou olhos amarelados)
  4  Distensão abdominal marcante / abdôme visivelmente inflado
  5  Nenhum dos acima""")
    alarm_raw = input('→ ').strip().split()
    dados['perda_peso'] = '1' in alarm_raw
    dados['anorexia']   = '2' in alarm_raw
    dados['ictericia']  = '3' in alarm_raw   # sem acento — padrão Python
    dados['distensao']  = '4' in alarm_raw

    # ═══════════════════════════════════════════════════════════════
    # BLOCO 8 — EXAME FÍSICO ABDOMINAL
    # ═══════════════════════════════════════════════════════════════
    print("""
── BLOCO 8: Palpação Abdominal ──
  1  Abdôme flácido, indolor à palpação superficial
  2  Sensível à palpação, sem defesa (dói mas não contrai)
  3  Defesa muscular voluntária (paciente contrai ao palpar)
  4  Defesa involuntária / rigidez (abdôme em tábua — não cede)
  5  Blumberg positivo (dor ao descomprimir bruscamente)""")
    ef = input('→ ').strip()
    dados['blumberg_positivo'] = ef == '5'
    dados['rigidez']           = ef == '4'
    dados['defesa']            = ef in ('3', '4', '5')
    dados['abdome_flacido']    = ef in ('1', '2')
    dados['peritonismo']       = dados['blumberg_positivo'] or dados['rigidez']

    print("""
Ruídos hidroaéreos (peristaltismo)?
  1  Presentes e normais
  2  Aumentados / borborígmos intensos
  3  Diminuídos / hipoativos
  4  Ausentes — silêncio abdominal""")
    rha = input('→ ').strip()
    dados['rha_ausentes']   = rha == '4'
    dados['rha_diminuidos'] = rha in ('3', '4')

    print("""
Sinal de Murphy (FSD)?
  1  Não pesquisado / não aplicável
  2  Negativo
  3  Positivo — parada inspiratória ao palpar FSD""")
    dados['murphy_positivo'] = input('→ ').strip() == '3'

    print("""
FID (fossa ilíaca direita)?
  1  Sem dor em FID
  2  Sensível em FID à palpação
  3  Muito doloroso — McBurney positivo + dor à descompressão""")
    mcb = input('→ ').strip()
    dados['mcburney_positivo'] = mcb == '3'
    dados['fid_dolorosa']      = mcb in ('2', '3')

    print("""
FIE (fossa ilíaca esquerda)?
  1  Sem dor em FIE
  2  Sensível em FIE à palpação
  3  Muito doloroso em FIE""")
    fie_ef = input('→ ').strip()
    dados['fie_dolorosa'] = fie_ef in ('2', '3')

    # ═══════════════════════════════════════════════════════════════
    # BLOCO 9 — COMORBIDADES E CONTEXTO (multi-seleção)
    # ═══════════════════════════════════════════════════════════════
    print("""
── BLOCO 9: Comorbidades Relevantes (ex: 1 3) ──
  1  Fibrilação atrial (FA) ou outra arritmia cardíaca
  2  Vasculopatia / aterosclerose / IAM prévio / bypass
  3  Uso regular de AINE, AAS ou anti-inflamatório
  4  Antibiótico nos últimos 4 meses
  5  Etilismo / uso regular de álcool
  6  Imunossuprimido (HIV, corticoide crônico, quimio)
  7  Diverticulose conhecida (colonoscopia anterior)
  8  Nenhuma""")
    comorb = input('→ ').strip().split()
    dados['fa_arritmia']     = '1' in comorb
    dados['vasculopata']     = '2' in comorb
    dados['uso_aine']        = '3' in comorb
    dados['atb_recente']     = '4' in comorb
    dados['etilismo']        = '5' in comorb
    dados['imunossuprimido'] = '6' in comorb
    dados['diverticulose']   = '7' in comorb

    # Flag isquemia mesentérica: idoso + cardiopata/vasculopata
    # No engine: + intensidade intensa/catastrófica + abdôme flácido
    dados['risco_isquemia_mesenterica'] = (
        dados['idoso'] and (dados['fa_arritmia'] or dados['vasculopata'])
    )

    # ═══════════════════════════════════════════════════════════════
    # BLOCO 10 — CONTEXTO EPIDEMIOLÓGICO (multi-seleção)
    # ═══════════════════════════════════════════════════════════════
    print("""
── BLOCO 10: Contexto Epidemiológico (ex: 1 2) ──
  1  Viagem recente a área endêmica (Nordeste/Norte BR, exterior)
  2  Outros casos iguais no mesmo ambiente (surto coletivo)
  3  Consumo de água de poço / rio / não tratada
  4  Contato com animais de fazenda / fezes de animais
  5  Nenhum""")
    epi = input('→ ').strip().split()
    dados['viagem_endemica']  = '1' in epi
    dados['surto_coletivo']   = '2' in epi
    dados['agua_nao_tratada'] = '3' in epi
    dados['contato_animal']   = '4' in epi
    dados['suspeita_parasitose'] = (
        dados['viagem_endemica'] or dados['agua_nao_tratada'] or dados['contato_animal']
    )

    # ═══════════════════════════════════════════════════════════════
    # BLOCO 11 — H. PYLORI E HISTÓRICO GI
    # ═══════════════════════════════════════════════════════════════
    print("""
── BLOCO 11: H. pylori e Histórico Digestivo ──
  1  Nunca testou / desconhece
  2  Positivo — nunca tratou
  3  Positivo — fez eradicação, confirmou negativo (breath test / antígeno fecal)
  4  Positivo — fez tratamento, mas sem teste de cura""")
    hp = input('→ ').strip()
    dados['hp_positivo']     = hp == '2'
    dados['hp_eradicado']    = hp == '3'
    dados['hp_sem_cura']     = hp == '4'
    dados['hp_desconhecido'] = hp == '1'

    print("""
Episódios anteriores semelhantes?
  1  Primeira vez
  2  Recorrente — episódios que vêm e passam
  3  Crônico — tenho isso faz meses/anos""")
    epis = input('→ ').strip()
    dados['primeira_vez'] = epis == '1'
    dados['recorrente']   = epis == '2'
    dados['cronico']      = epis == '3'

    # ═══════════════════════════════════════════════════════════════
    # BLOCO 12 — DURAÇÃO
    # ═══════════════════════════════════════════════════════════════
    print("""
── BLOCO 12: Duração dos Sintomas Atuais ──
  1  Horas (< 24h) — onset agudo
  2  Dias (1–7 dias)
  3  Semanas (1–4 semanas)
  4  Meses (1–3 meses)
  5  Mais de 3 meses""")
    dur = input('→ ').strip()
    dados['duracao'] = {
        '1': 'horas', '2': 'dias', '3': 'semanas',
        '4': 'meses_1_3', '5': 'meses_mais_3',
    }.get(dur, 'dias')
    dados['duracao_cronica'] = dados['duracao'] in ('meses_1_3', 'meses_mais_3')

    # ═══════════════════════════════════════════════════════════════
    # BLOCO 13 — SAÚDE DA MULHER (só se sexo feminino)
    # ═══════════════════════════════════════════════════════════════
    if dados['sexo_feminino']:
        dados['idade_fertil'] = 12 <= dados.get('idade', 0) <= 50

        print('\n── BLOCO 13: Saúde da Mulher ──')

        if dados['idade_fertil']:
            print("""Atraso menstrual?
  1  Não — menstruação dentro do prazo habitual
  2  Sim — ciclo atrasado
  3  Ciclo irregular / não sei""")
            am = input('→ ').strip()
            dados['atraso_menstrual'] = am == '2'

            if dados['atraso_menstrual']:
                print("""Teste de gravidez (β-hCG urina ou sangue)?
  1  Não fez
  2  Negativo
  3  Positivo""")
                tg = input('→ ').strip()
                dados['teste_gravid']       = {'1': 'nao_fez', '2': 'negativo',
                                               '3': 'positivo'}.get(tg, 'nao_fez')
                dados['gravida_confirmada'] = tg == '3'
            else:
                dados['teste_gravid']       = None
                dados['gravida_confirmada'] = False
        else:
            dados['atraso_menstrual']   = False
            dados['teste_gravid']       = None
            dados['gravida_confirmada'] = False

        print("""
Dor pélvica / baixo ventre?
  1  Não
  2  Cólica habitual de menstruação (dismenorreia habitual)
  3  Dor nova ou mais intensa que o usual — moderada
  4  Dor intensa / aguda — diferente de qualquer vez anterior""")
        dp = input('→ ').strip()
        dados['dor_pelvica']           = dp in ('2', '3', '4')
        dados['dor_pelvica_aguda']     = dp == '4'
        dados['dismenorreia_habitual'] = dp == '2'

        print("""
Corrimento vaginal?
  1  Não
  2  Sim — aspecto normal / leve aumento
  3  Sim — purulento / amarelo-esverdeado / odor fétido""")
        corr = input('→ ').strip()
        dados['corrimento']           = corr in ('2', '3')
        dados['corrimento_purulento'] = corr == '3'

        # DIP: febre + corrimento purulento + dor pélvica nova/intensa
        dados['suspeita_dip'] = (
            dados['febre'] and
            dados['corrimento_purulento'] and
            dados['dor_pelvica'] and
            not dados['dismenorreia_habitual']
        )
        # Gravidez ectópica: atraso + dor pélvica aguda intensa
        # β-hCG negativo NÃO exclui ectópica precoce
        dados['suspeita_ectopica'] = (
            dados['atraso_menstrual'] and
            dados['dor_pelvica_aguda'] and
            dados['intensidade'] in ('intensa', 'catastrofica')
        )
    else:
        for k in ('idade_fertil', 'atraso_menstrual', 'gravida_confirmada',
                  'dor_pelvica', 'dor_pelvica_aguda', 'dismenorreia_habitual',
                  'corrimento', 'corrimento_purulento', 'suspeita_dip', 'suspeita_ectopica'):
            dados[k] = False
        dados['teste_gravid'] = None

    # ═══════════════════════════════════════════════════════════════
    # BLOCO 14 — PADRÃO FUNCIONAL / CRÔNICO
    # Gate: duração crônica OU (semanas + pelo menos 1 alarme)
    # Rationale: Crohn pode apresentar como 3-4 semanas de diarreia
    # + emagrecimento — não podemos perder esse paciente por skip.
    # ═══════════════════════════════════════════════════════════════
    _alarme_presente = dados.get('perda_peso') or dados.get('sangue_fezes') or dados.get('febre')
    _entrar_bloco14  = (
        dados['duracao_cronica'] or
        dados['cronico'] or
        dados['recorrente'] or
        (dados['duracao'] == 'semanas' and _alarme_presente)
    )

    if _entrar_bloco14:
        print("""
── BLOCO 14: Padrão Crônico / Funcional ──
A dor alivia após evacuar?
  1  Sim — bastante
  2  Parcialmente
  3  Não / sem relação""")
        aliv = input('→ ').strip()
        dados['alivio_evacuacao'] = aliv in ('1', '2')

        print("""
Inchaço / distensão abdominal após refeição?
  1  Sim — frequente e intenso
  2  Ocasional / leve
  3  Não""")
        dist_func = input('→ ').strip()
        dados['distensao_pos_refeicao'] = dist_func in ('1', '2')

        print("""
Melhora ao retirar algum alimento específico?
  1  Sim — glúten (pão, macarrão, biscoito)
  2  Sim — laticínios
  3  Sim — leguminosas (feijão, lentilha)
  4  Sem relação clara""")
        mel = input('→ ').strip()
        dados['melhora_sem_gluten']  = mel == '1'
        dados['melhora_sem_lactose'] = mel == '2'

        print("""
Manifestações FORA do intestino associadas? (ex: 1 3)
  1  Dor / inchaço articular
  2  Lesões de pele (eritema nodoso, manchas)
  3  Olho vermelho / uveíte
  4  Aftas frequentes na boca
  5  Nenhuma""")
        extra = input('→ ').strip().split()
        dados['artrite_extra']    = '1' in extra
        dados['lesao_pele_extra'] = '2' in extra
        dados['uveite_extra']     = '3' in extra
        dados['aftas_extra']      = '4' in extra
        dados['manifestacoes_extraintestinais'] = any(
            dados[k] for k in ('artrite_extra', 'lesao_pele_extra',
                                'uveite_extra', 'aftas_extra')
        )
    else:
        for k in ('alivio_evacuacao', 'distensao_pos_refeicao',
                  'melhora_sem_gluten', 'melhora_sem_lactose',
                  'artrite_extra', 'lesao_pele_extra', 'uveite_extra',
                  'aftas_extra', 'manifestacoes_extraintestinais'):
            dados[k] = False

    # ═══════════════════════════════════════════════════════════════
    # FLAGS DERIVADAS
    # ═══════════════════════════════════════════════════════════════

    # C. diff: só alerta de texto — não diagnóstico
    dados['alerta_cdiff'] = (
        dados.get('atb_recente') and
        dados.get('habito_intestinal') == 'diarreia'
    )

    # IBD: EXIGE diarreia (constipação → SII-C, não IBD)
    dados['suspeita_ibd'] = (
        dados.get('duracao_cronica') and
        dados.get('habito_intestinal') in ('diarreia', 'alternancia') and
        (dados.get('perda_peso') or dados.get('sangue_fezes') or
         dados.get('manifestacoes_extraintestinais'))
    )

    # Celíaca: piora com glúten + melhora sem glúten + contexto
    dados['suspeita_celiaca'] = (
        (dados.get('piora_gluten') or dados.get('melhora_sem_gluten')) and
        dados.get('duracao_cronica')
    )

    # ═══════════════════════════════════════════════════════════════
    # RESUMO — FLAGS DETECTADAS
    # ═══════════════════════════════════════════════════════════════
    print('\n' + '─' * 56)
    print('  RESUMO — Flags Detectadas')
    print('─' * 56)
    alertas = []
    if dados.get('peritonismo'):
        alertas.append('🔴 PERITONISMO — Encaminhar PS imediato')
    if dados.get('obstipacao_total'):
        alertas.append('🔴 SEM FEZES/GASES — suspeita de obstrução')
    if dados.get('hematemese') or dados.get('melena'):
        alertas.append('🔴 SANGRAMENTO GI ALTO — Encaminhar PS imediato')
    if dados.get('suspeita_ectopica'):
        alertas.append('🔴 GRAVIDEZ ECTÓPICA SUSPEITA — Emergência')
    if dados.get('risco_isquemia_mesenterica') and dados.get('intensidade') in ('intensa', 'catastrofica'):
        alertas.append('🔴 RISCO ISQUEMIA MESENTÉRICA — Idoso cardiopata + dor intensa')
    if dados.get('suspeita_dip'):
        alertas.append('🟡 DIP suspeita')
    if dados.get('alerta_cdiff'):
        alertas.append('⚠️  ATB recente + diarreia — considerar C. difficile')
    if dados.get('suspeita_ibd'):
        alertas.append('🟡 IBD suspeita — pedir calprotectina fecal')
    if dados.get('suspeita_celiaca'):
        alertas.append('🟡 Doença celíaca suspeita — NÃO retirar glúten antes do exame')

    if alertas:
        for a in alertas:
            print(f'  {a}')
    else:
        print('  Nenhum flag de emergência identificado.')

    arquivo = _salvar(dados)
    return dados, arquivo


# =============================================================================
# CLI STANDALONE
# =============================================================================

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    dados, arquivo = coletar_subjetivo_abdominal()
    print(f'\n  Subjetivo coletado: {arquivo}')
