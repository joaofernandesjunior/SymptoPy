# modules/sintomas/tosse/subjetivo.py
# Anamnese — Tosse
# Roteador 0: Imunossupressão (filtro de segurança antes de tudo)
# Roteador 1: Duração — Aguda (<3sem) | Subaguda (3–8sem) | Crônica (≥8sem)
# Crônica: Algoritmo de Irwin sequencial (IECA → UACS → Asma → DRGE/LPR → TB → Neoplasia)
# Rodar da raiz: python -m modules.sintomas.tosse.subjetivo

import json
import os
import sys
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from utils.perguntas import sn


# =============================================================================
# AUXILIARES
# =============================================================================

def _bloco(titulo):
    print(f'\n{"─"*54}')
    print(f'  {titulo}')
    print(f'{"─"*54}')


def perguntar_int(prompt, minimo=0, maximo=9999):
    while True:
        try:
            val = int(input(prompt).strip())
            if minimo <= val <= maximo:
                return val
            print(f'  Digite um valor entre {minimo} e {maximo}.')
        except ValueError:
            print('  Digite um número inteiro.')


def perguntar_float(prompt):
    while True:
        try:
            return float(input(prompt).strip().replace(',', '.'))
        except ValueError:
            print('  Digite um número (ex: 0.75 ou 75).')


def perguntar_texto(prompt):
    return input(prompt).strip()


# =============================================================================
# ROTEADOR 0 — FILTRO DE IMUNOSSUPRESSÃO
# (Executa antes de qualquer roteamento por duração)
# =============================================================================

def _bloco_imunossupressao(dados):
    _bloco('ROTEADOR 0 — Filtro de Imunossupressão')
    print('  Este filtro é executado antes do roteamento por duração.')
    print('  Imunossupressão muda completamente o leque diagnóstico.\n')

    dados['hiv_diagnosticado'] = sn('  HIV diagnosticado? ')
    if dados['hiv_diagnosticado']:
        dados['hiv_em_tarv']     = sn('  Em TARV (tratamento antirretroviral)? ')
        dados['cd4_conhecido']   = sn('  CD4 conhecido (resultado recente)? ')
        if dados['cd4_conhecido']:
            dados['cd4_valor']   = perguntar_int('  CD4 (células/mm³): ', 0, 2000)
        else:
            dados['cd4_valor']   = None
    else:
        dados['hiv_em_tarv']   = False
        dados['hiv_testado_recente'] = sn('  Testou para HIV nos últimos 12 meses? ')
        if not dados['hiv_testado_recente']:
            dados['hiv_fatores_risco'] = sn(
                '  Fatores de risco para HIV (parceiros múltiplos, UDI, MSM, transfusão)? '
            )
        else:
            dados['hiv_fatores_risco'] = False

    dados['corticoide_cronico']      = sn('  Uso crônico de corticosteroide (> 3 meses)? ')
    dados['imunossupressao_outro']   = sn('  Outra imunossupressão (transplante, quimioterapia, biológico)? ')
    dados['contato_tb']              = sn('  Contato confirmado com caso de tuberculose? ')

    # Flag consolidada para o engine
    dados['imunossuprimido'] = any([
        dados['hiv_diagnosticado'],
        dados['corticoide_cronico'],
        dados['imunossupressao_outro'],
    ])

    if dados['imunossuprimido']:
        print('\n  ALERTA: paciente imunossuprimido — a avaliação deve considerar')
        print('  PCP, TB, MAC e fungos mesmo com apresentação atípica.')


# =============================================================================
# ROTEADOR 1 — DURAÇÃO E CARÁTER GERAL
# =============================================================================

def _bloco_duracao_carater(dados):
    _bloco('ROTEADOR 1 — Duração e Caráter da Tosse')
    dados['duracao_semanas'] = perguntar_int('  Duração da tosse (em semanas): ', 0, 520)
    dados['tosse_produtiva'] = sn('  Tosse produtiva (com expectoração)? ')
    if dados['tosse_produtiva']:
        dados['expectoracao_purulenta'] = sn('  Expectoração purulenta (amarela/verde/espessa)? ')
    else:
        dados['expectoracao_purulenta'] = False
    dados['hemoptise']       = sn('  Hemoptise (sangue no escarro)? ')
    dados['dispneia_assoc']  = sn('  Dispneia associada? ')
    if dados['dispneia_assoc']:
        dados['dispneia_progressiva'] = sn('  Dispneia progressiva aos esforços (piora gradual)? ')
    else:
        dados['dispneia_progressiva'] = False
    dados['febre']           = sn('  Febre? ')
    if dados['febre']:
        dados['febre_alta']  = sn('  Febre alta (≥38.5 °C)? ')
    else:
        dados['febre_alta']  = False

    if dados['hemoptise']:
        print('\n  RED FLAG: hemoptise — TB, neoplasia e bronquiectasia são prioritárias.')


# =============================================================================
# BLOCO AGUDA (<3 semanas)
# =============================================================================

def _bloco_aguda(dados):
    _bloco('BLOCO AGUDA — Investigação (<3 semanas)')

    dados['coriza_espirros']       = sn('  Coriza e espirros associados (quadro de IVRS)? ')
    dados['odinofagia']            = sn('  Dor de garganta (odinofagia)? ')
    dados['dor_pleuritica']        = sn('  Dor pleurítica (piora ao respirar / tossir)? ')
    dados['tosse_paroxistica']     = sn('  Tosse em acessos paroxísticos intensos? ')
    if dados['tosse_paroxistica']:
        dados['guincho_inspiratorio'] = sn('  Guincho inspiratório ("whoop") após os acessos? ')
        dados['vomito_pos_tosse']     = sn('  Vômito após os episódios de tosse? ')
        dados['contato_pertussis']    = sn('  Contato com caso suspeito de coqueluche? ')
    else:
        dados['guincho_inspiratorio'] = False
        dados['vomito_pos_tosse']     = False
        dados['contato_pertussis']    = False

    dados['estertores_ausculta']   = sn('  Estertores crepitantes à ausculta (consolidação)? ')
    dados['saturacao_baixa']       = sn('  Saturação de O₂ < 94%? ')

    # Influenza
    dados['mialgia_intensa']       = sn('  Mialgia intensa e início abrupto (síndrome gripal)? ')
    dados['vacinado_influenza']    = sn('  Vacinado contra influenza (última dose < 12 meses)? ')


# =============================================================================
# BLOCO SUBAGUDA (3–8 semanas)
# =============================================================================

def _bloco_subaguda(dados):
    _bloco('BLOCO SUBAGUDA — Investigação (3–8 semanas)')
    print('  Causa mais comum: tosse pós-infecciosa (hiper-reatividade transitória).')
    print('  Bordetella pertussis pode se apresentar nessa janela.\n')

    dados['infeccao_recente_precedeu'] = sn('  A tosse foi precedida por IVRS/gripe nas últimas 8 semanas? ')
    dados['tosse_paroxistica']         = dados.get('tosse_paroxistica') or sn(
        '  Tosse em acessos paroxísticos (sugere pertussis tardio)? '
    )
    dados['chiado_novo']               = sn('  Chiado novo ou piora de chiado já existente? ')
    dados['piora_progressiva']         = sn('  Tosse em piora progressiva (ao invés de melhorar)? ')

    if dados['piora_progressiva']:
        print('\n  ATENÇÃO: subaguda em piora — investigar como crônica.')


# =============================================================================
# BLOCO CRÔNICA — IRWIN SEQUENCIAL (≥8 semanas)
# =============================================================================

def _bloco_cronica_ieca(dados):
    _bloco('CRÔNICA — Passo 1: IECA')
    print('  IECA causa tosse seca em 10–15% dos usuários.')
    print('  Pode aparecer semanas a meses após início do medicamento.\n')
    dados['uso_ieca'] = sn('  Usa IECA (enalapril, captopril, ramipril, lisinopril)? ')
    if dados['uso_ieca']:
        dados['ieca_qual'] = perguntar_texto('  Qual IECA? ')
        dados['tosse_inicio_apos_ieca'] = sn('  A tosse iniciou após começar o IECA? ')
        print('\n  Conduta: suspender IECA e substituir por ARA-II.')
        print('  Tosse some em 1–4 semanas — diagnóstico confirmado retrospectivamente.')
    else:
        dados['ieca_qual']             = ''
        dados['tosse_inicio_apos_ieca'] = False


def _bloco_cronica_uacs(dados):
    _bloco('CRÔNICA — Passo 2: UACS (Gotejamento Pós-Nasal)')
    print('  Causa mais comum de tosse crônica (~40%).')
    print('  Anti-histamínico de 1ª geração — NÃO loratadina (sem efeito sobre UACS).\n')

    dados['sensacao_gotejamento']    = sn('  Sensação de gotejamento ou secreção descendo pela garganta? ')
    dados['clearing_frequente']      = sn('  Pigarro / "limpeza" frequente da garganta? ')
    dados['piora_deitado_noturno']   = sn('  Piora da tosse ao deitar (drena mais deitado)? ')
    dados['rinite_sinusite_assoc']   = sn('  Rinite ou sinusite diagnosticada ou frequente? ')
    dados['voz_anasalada']           = sn('  Voz nasalada / obstrução nasal? ')
    dados['descarga_posterior_vista']= sn('  Descarga posterior visível ao exame da orofaringe? ')


def _bloco_cronica_asma(dados):
    _bloco('CRÔNICA — Passo 3: Asma / Variante Tosse')
    print('  30% dos asmáticos têm tosse como único sintoma (cough variant asthma).')
    print('  Espirometria normal NÃO exclui asma — pode ser intermitente/leve.\n')

    dados['piora_noturna_madrugada'] = sn('  Piora da tosse à noite ou madrugada? ')
    dados['piora_exercicio']         = sn('  Piora com exercício físico? ')
    dados['piora_frio_odores']       = sn('  Piora com ar frio, odores fortes ou irritantes? ')
    dados['chiado_episodico']        = sn('  Chiado episódico (mesmo que raro)? ')
    dados['historia_atopia']         = sn('  História de rinite alérgica, eczema ou alergia? ')
    dados['asma_diagnosticada']      = sn('  Asma já diagnosticada previamente? ')
    dados['dpoc_diagnosticado']      = sn('  DPOC diagnosticado? ')
    dados['tabagismo_ativo']         = sn('  Tabagismo ativo? ')
    if dados['tabagismo_ativo'] or dados.get('tabagismo_maco_ano', 0) > 0:
        if 'tabagismo_maco_ano' not in dados or dados.get('tabagismo_maco_ano', 0) == 0:
            dados['tabagismo_maco_ano'] = perguntar_int(
                '  Carga tabágica (maços-ano = maços/dia × anos): ', 0, 200
            )
    else:
        if 'tabagismo_maco_ano' not in dados:
            dados['tabagismo_maco_ano'] = 0

    # Espirometria — bloco opcional
    _bloco_espirometria(dados)


def _bloco_espirometria(dados):
    _bloco('ESPIROMETRIA (opcional — preencher se disponível)')
    print('  O laudo automático do espirômetro já fornece a interpretação.')
    print('  Aqui registramos os valores-chave para o raciocínio do motor.\n')

    dados['espiro_realizada'] = sn('  Espirometria realizada? ')
    if not dados['espiro_realizada']:
        dados['vef1_cvf_pre']    = None
        dados['vef1_cvf_pos']    = None
        dados['delta_vef1_pct']  = None
        dados['laudo_espiro']    = ''
        return

    dados['vef1_cvf_pre']  = perguntar_float('  VEF1/CVF pré-BD (ex: 0.68): ')
    dados['vef1_cvf_pos']  = perguntar_float('  VEF1/CVF pós-BD (ex: 0.74 — ou 0 se não fez): ')
    dados['delta_vef1_pct']= perguntar_float('  Variação VEF1 pós-BD em % (ex: 14 — ou 0 se não fez): ')
    dados['laudo_espiro']  = perguntar_texto('  Resumo do laudo automático (opcional, Enter para pular): ')


def _bloco_cronica_drge(dados):
    _bloco('CRÔNICA — Passo 4: DRGE / LPR')
    print('  LPR (refluxo laringofaríngeo) pode causar tosse SEM pirose.')
    print('  Rouquidão matinal + globus + tosse pós-prandial = LPR silencioso.\n')

    dados['pirose_regurgitacao']     = sn('  Pirose ou regurgitação ácida? ')
    dados['piora_pos_prandial']      = sn('  Piora da tosse após refeições? ')
    dados['piora_deitado_drge']      = sn('  Piora ao deitar (refluxo noturno)? ')
    dados['rouquidao_matinal']       = sn('  Rouquidão matinal (clareamento da voz ao longo do dia)? ')
    dados['globus_faringeo']         = sn('  Sensação de "caroço" na garganta (globus)? ')
    dados['tosse_sem_pirose']        = (
        dados['rouquidao_matinal'] or dados['globus_faringeo']
    ) and not dados['pirose_regurgitacao']

    if dados['tosse_sem_pirose']:
        print('\n  ATENÇÃO: LPR silencioso — tosse sem pirose. Trial com IBP 2×/dia por 8 semanas.')


def _bloco_cronica_tb_atipica(dados):
    _bloco('CRÔNICA — Passo 5: TB / Pneumonia Atípica')
    print('  TB começa insidiosa — tosse ≥3 semanas é critério de suspeita do PNCT.')
    print('  Pneumonia atípica: início arrastado, sem febrão, "walking pneumonia".\n')

    dados['tosse_3_semanas_mais']    = dados.get('duracao_semanas', 0) >= 3
    dados['perda_peso_involuntaria'] = sn('  Perda de peso involuntária? ')
    if dados['perda_peso_involuntaria']:
        dados['perda_peso_kg']       = perguntar_int('  Quantos kg (aproximado): ', 0, 80)
    else:
        dados['perda_peso_kg']       = 0
    dados['sudorese_noturna']        = sn('  Sudorese noturna (encharca o pijama)? ')
    dados['inicio_insidioso_progressivo'] = sn(
        '  Início insidioso e progressivo (sem evento agudo claro)? '
    )
    dados['sem_febre_alta_quadro_prolongado'] = not dados.get('febre_alta') and dados.get('duracao_semanas', 0) >= 3
    dados['dispneia_progressiva_esforco'] = dados.get('dispneia_progressiva', False)


def _bloco_cronica_neoplasia(dados):
    _bloco('CRÔNICA — Passo 6: Suspeita de Neoplasia Pulmonar')
    print('  Maior risco: tabagismo >20 maços-ano, >45 anos, mudança no padrão da tosse.\n')

    if 'tabagismo_maco_ano' not in dados:
        dados['tabagismo_maco_ano'] = perguntar_int(
            '  Carga tabágica (maços-ano): ', 0, 200
        )

    dados['mudanca_padrao_tosse']    = sn('  Mudança no padrão habitual da tosse (mais intensa, diferente)? ')
    dados['adenopatia_percebida']    = sn('  Nódulo ou inchaço no pescoço / axila / supraclavicular? ')
    dados['dor_toracica_persistente']= sn('  Dor torácica persistente (não pleurítica, constante)? ')
    dados['rouquidao_persistente']   = sn('  Rouquidão persistente (> 3 semanas)? ')
    dados['disfagia']                = sn('  Dificuldade para engolir? ')

    idade = dados.get('idade', 0)
    dados['perfil_neoplasia'] = (
        dados.get('tabagismo_maco_ano', 0) >= 20
        and idade >= 45
    )

    if dados['perfil_neoplasia']:
        print('\n  ALERTA: perfil de alto risco — RX tórax + avaliação urgente.')


# =============================================================================
# SALVAR
# =============================================================================

def salvar_dicionario(dados, pasta='dados_pacientes'):
    os.makedirs(pasta, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome = os.path.join(pasta, f'tosse_subjetivo_{timestamp}.json')
    with open(nome, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f'\n  Dicionário salvo em: {nome}')
    return nome


# =============================================================================
# MAIN
# =============================================================================

def coletar_subjetivo_tosse(dados_preenchidos=None):
    print('\n' + '='*54)
    print('  SYMPTOPY — Anamnese: Tosse')
    print('='*54)
    print('  Responda s (sim) ou n (não) para cada pergunta.')

    dados = dados_preenchidos.copy() if dados_preenchidos else {}

    _bloco_imunossupressao(dados)
    _bloco_duracao_carater(dados)

    semanas = dados.get('duracao_semanas', 0)

    if semanas < 3:
        _bloco_aguda(dados)
    elif semanas < 8:
        _bloco_subaguda(dados)
        # Subaguda em piora investiga como crônica
        if dados.get('piora_progressiva'):
            print('\n  Investigando como crônica por piora progressiva...')
            _bloco_cronica_ieca(dados)
            _bloco_cronica_uacs(dados)
            _bloco_cronica_asma(dados)
            _bloco_cronica_drge(dados)
            _bloco_cronica_tb_atipica(dados)
            _bloco_cronica_neoplasia(dados)
    else:
        _bloco_cronica_ieca(dados)
        _bloco_cronica_uacs(dados)
        _bloco_cronica_asma(dados)
        _bloco_cronica_drge(dados)
        _bloco_cronica_tb_atipica(dados)
        _bloco_cronica_neoplasia(dados)

    arquivo = salvar_dicionario(dados)
    print('\n  Próximo: engine_tosse.py → diagnóstico\n')
    return dados, arquivo


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    coletar_subjetivo_tosse()
