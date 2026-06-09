# modules/sintomas/oftalmo/olho_vermelho_subjetivo.py
# Sintoma-guia: Olho Vermelho
#
# Cobre: Conjuntivite (bacteriana/viral/alérgica), Hordéolo, Calázio,
#        Hemorragia subconjuntival, Blefarite, Celulite pré-septal.
#        Red flags: Glaucoma agudo, Úlcera de córnea (esp. lente de contato → Pseudomonas),
#        Uveíte anterior (ciliary flush), Celulite orbitária, Trauma penetrante.
#
# ⚠️  LENTE DE CONTATO + DOR + OLHO VERMELHO = STEP 1 IMEDIATO
#     Pseudomonas pode perfurar a córnea em 24–48h.
#
# Retorna: (dados: dict, arquivo_json: str)

import json
import os
import sys
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))


def _ask(prompt, opts=None, default=None):
    if opts:
        print(f'\n  {prompt}')
        for i, o in enumerate(opts, 1):
            print(f'    {i}. {o}')
        while True:
            raw = input('  → ').strip()
            if raw == '' and default is not None:
                return default
            if raw.isdigit() and 1 <= int(raw) <= len(opts):
                return opts[int(raw) - 1]
            print(f'  ⚠️  Digite um número de 1 a {len(opts)}.')
    else:
        raw = input(f'\n  {prompt}\n  → ').strip()
        return raw if raw else default


def _sim_nao(prompt, default='nao'):
    raw = input(f'\n  {prompt} (s/n) → ').strip().lower()
    if raw in ('s', 'sim', 'y', 'yes'):
        return True
    if raw in ('n', 'nao', 'não', 'no'):
        return False
    return default == 'sim'


def _input_num(prompt, inteiro=False):
    while True:
        raw = input(f'\n  {prompt}: ').strip()
        try:
            return int(raw) if inteiro else float(raw)
        except ValueError:
            print('  ⚠️  Digite um número.')


# =============================================================================
# COLETA PRINCIPAL
# =============================================================================

def coletar_subjetivo_olho_vermelho(dados_preenchidos: dict = None) -> tuple:
    dados = dict(dados_preenchidos or {})

    if 'idade' not in dados:
        dados['idade'] = _input_num('Idade do paciente (anos)', inteiro=True)
    if 'sexo' not in dados:
        dados['sexo'] = _ask('Sexo biológico', ['M', 'F'])

    print('\n' + '=' * 60)
    print('  AVALIAÇÃO — OLHO VERMELHO')
    print('=' * 60)

    # ─── BLOCO 1 — Lateralidade e duração ─────────────────────────────────
    print('\n  [ Bloco 1 — Localização e duração ]')

    dados['lateralidade'] = _ask(
        'Qual olho está vermelho?',
        ['Olho direito', 'Olho esquerdo', 'Ambos os olhos (bilateral)'],
    )
    dados['bilateral'] = ('Ambos' in dados['lateralidade'])

    dur_raw = _ask(
        'Há quanto tempo com olho vermelho?',
        ['< 24 horas', '24–72 horas', '3–7 dias', '> 1 semana'],
    )
    dados['duracao_sintomas'] = dur_raw
    dados['duracao_dias_aprox'] = {
        '< 24 horas': 0.5, '24–72 horas': 2, '3–7 dias': 5, '> 1 semana': 10,
    }.get(dur_raw, 2)

    # ─── BLOCO 2 — TIPO DE ERITEMA — gate ciliary flush ───────────────────
    print('\n  [ Bloco 2 — Distribuição da vermelhidão ]')
    print('  ⚠️  Pergunta crítica — observe o olho antes de responder.')
    print('      Conjuntivite: difusa, + intensa nas bordas (longe da córnea).')
    print('      Uveíte/Glaucoma: HALO vermelho AO REDOR da córnea/íris, bordas mais claras.')

    eritema_raw = _ask(
        'Como está a vermelhidão?',
        [
            'Difusa — branco do olho todo vermelho, bordas mais intensas',
            'Mancha localizada — ponto vermelho brilhante (como sangue)',
            'Pericorneal (ciliary flush) — anel vermelho intenso AO REDOR da íris, periferia mais clara',
            'Palpebral — inchaço/vermelhidão das pálpebras (não do globo)',
        ],
    )
    dados['eritema_tipo']      = eritema_raw
    dados['ciliary_flush']     = 'Pericorneal' in eritema_raw   # alta gravidade
    dados['hemorragia_subconj'] = 'sangue' in eritema_raw.lower() or 'Mancha' in eritema_raw
    dados['eritema_difuso']    = 'Difusa' in eritema_raw
    dados['eritema_palpebral'] = 'Palpebral' in eritema_raw

    if dados['ciliary_flush']:
        print('\n  🔴 CILIARY FLUSH identificado — suspeita de uveíte anterior ou glaucoma agudo.')
        print('     Prosseguir avaliação com prioridade máxima.')

    # ─── BLOCO 3 — Dor + fotofobia + fenômenos visuais ────────────────────
    print('\n  [ Bloco 3 — Dor, fotofobia e fenômenos visuais ]')

    dados['dor_ocular'] = _sim_nao('Dor no(s) olho(s)?')
    if dados['dor_ocular']:
        dor_int = _ask(
            'Intensidade da dor:',
            ['Leve (desconforto/ardência)', 'Moderada (incomoda mas tolera)', 'Intensa (difícil tolerar)'],
        )
        dados['dor_intensidade'] = dor_int
        dados['dor_intensa']     = ('Intensa' in dor_int)
        dados['dor_ao_mover_olho'] = _sim_nao('Dor piora ao mover o olho?')
    else:
        dados['dor_intensidade']   = 'ausente'
        dados['dor_intensa']       = False
        dados['dor_ao_mover_olho'] = False

    dados['fotofobia']       = _sim_nao('Fotofobia (desconforto/dor ao olhar para luz)?')
    dados['halos_coloridos'] = _sim_nao('Halos coloridos (tipo arco-íris) ao redor de luzes à noite?')
    dados['visao_turva']     = _sim_nao('Visão turva, embaçada ou borrada?')
    dados['prurido_ocular']  = _sim_nao('Coceira / prurido intenso nos olhos?')
    dados['lacrimejamento']  = _sim_nao('Lacrimejamento excessivo?')

    # Sensação de corpo estranho (não necessariamente trauma)
    dados['corpo_estranho_sensacao'] = _sim_nao('Sensação de areia / corpo estranho no olho?')

    # ─── BLOCO 4 — Secreção ocular ────────────────────────────────────────
    print('\n  [ Bloco 4 — Secreção ocular ]')

    dados['secrecao'] = _sim_nao('Secreção no(s) olho(s)?')
    if dados['secrecao']:
        tipo_sec = _ask(
            'Tipo de secreção:',
            [
                'Purulenta / mucopurulenta (amarelada/esverdeada, espessa)',
                'Mucosa (esbranquiçada, filante)',
                'Aquosa / serosa (clara e líquida)',
            ],
        )
        dados['secrecao_tipo']      = tipo_sec
        dados['secrecao_purulenta'] = 'Purulenta' in tipo_sec
        dados['secrecao_aquosa']    = 'Aquosa'    in tipo_sec
        dados['palpebra_grudada']   = _sim_nao('Pálpebra(s) colada(s) ao acordar?')
    else:
        dados['secrecao_tipo']      = None
        dados['secrecao_purulenta'] = False
        dados['secrecao_aquosa']    = False
        dados['palpebra_grudada']   = False

    # ─── BLOCO 5 — LENTE DE CONTATO + TRAUMA ──────────────────────────────
    print('\n  [ Bloco 5 — Lente de contato e trauma ]')
    print('  ⚠️  Lente de contato + dor + olho vermelho = EMERGÊNCIA até prova em contrário.')
    print('      Pseudomonas aeruginosa pode perfurar a córnea em 24–48h.')

    dados['lente_de_contato'] = _sim_nao('Usa lente de contato (de qualquer tipo)?')
    if dados['lente_de_contato']:
        dados['dormiu_com_lente']  = _sim_nao('Dormiu com a lente ou usou por mais de 8h contínuas?')
        dados['lente_uso_irregular'] = _sim_nao('Usa a lente por mais tempo que o indicado (ex: mensal por 2 meses)?')
    else:
        dados['dormiu_com_lente']    = False
        dados['lente_uso_irregular'] = False

    dados['trauma_ocular'] = _sim_nao('Trauma ocular (batida, projétil, produto químico, corpo estranho)?')
    if dados['trauma_ocular']:
        tipo_trauma = _ask(
            'Tipo de trauma:',
            ['Contuso (soco, bola, queda)', 'Perfurante / penetrante', 'Químico (ácido ou álcali)',
             'Corpo estranho (lascas, madeira, metal)'],
        )
        dados['trauma_tipo']        = tipo_trauma
        dados['trauma_penetrante']  = 'Perfurante' in tipo_trauma
        dados['trauma_quimico']     = 'Químico'    in tipo_trauma
        dados['corpo_estranho_real'] = 'Corpo estranho' in tipo_trauma
    else:
        dados['trauma_tipo']        = None
        dados['trauma_penetrante']  = False
        dados['trauma_quimico']     = False
        dados['corpo_estranho_real'] = False

    # ─── BLOCO 6 — Sintomas sistêmicos + contexto epidemiológico ──────────
    print('\n  [ Bloco 6 — Sintomas sistêmicos e contexto ]')

    dados['febre']                 = _sim_nao('Febre presente?')
    dados['edema_palpebral']       = _sim_nao('Inchaço das pálpebras?')
    if dados['edema_palpebral']:
        dados['limitacao_motilidade'] = _sim_nao(
            'Dificuldade ou dor ao mover o olho (para cima, baixo, lados)?'
        )
        dados['proptose'] = _sim_nao('Olho parece projetado para fora (comparar com o outro)?')
    else:
        dados['limitacao_motilidade'] = False
        dados['proptose']             = False

    dados['nausea_vomito']          = _sim_nao('Náusea ou vômito associado?')
    dados['contato_conjuntivite']   = _sim_nao(
        'Contato com pessoa com "olho vermelho" / conjuntivite nos últimos 7 dias?'
    )
    dados['adenopatia_preauricular'] = _sim_nao(
        'Gânglio (caroço) palpável na frente da orelha (pré-auricular)?'
    )

    # ─── BLOCO 7 — Componente alérgico ────────────────────────────────────
    print('\n  [ Bloco 7 — Componente alérgico ]')

    dados['rinite_alergica_concomitante'] = _sim_nao(
        'Coriza, espirros ou nariz entupido junto com o olho vermelho?'
    )
    dados['rinite_alergica_conhecida']    = _sim_nao(
        'Rinite alérgica já diagnosticada ou alergia conhecida?'
    )
    dados['piora_sazonal_ocular']         = _sim_nao(
        'Piora em certas épocas (primavera/pólen) ou exposição a pó/animal de estimação?'
    )

    # ─── BLOCO 8 — Pós-cirúrgico + contexto social ────────────────────────
    print('\n  [ Bloco 8 — Cirurgia e contexto social ]')

    dados['pos_cirurgico_ocular'] = _sim_nao('Cirurgia ocular nos últimos 6 meses (catarata, LASIK, PRK)?')
    dados['necessita_atestado']   = _sim_nao('Paciente precisa de atestado para trabalho ou escola?')
    dados['profissional_saude']   = _sim_nao(
        'Profissional de saúde, educador ou manipulador de alimentos?'
    )
    dados['pio_mmhg']             = None   # reservado para tonômetro futuro

    # ─── FLAGS DERIVADAS ──────────────────────────────────────────────────

    # Glaucoma agudo (tríade clássica)
    dados['glaucoma_agudo_suspeito'] = (
        dados.get('halos_coloridos') and
        dados.get('dor_intensa') and
        dados.get('visao_turva')
    )

    # Úlcera de córnea / ceratite por Pseudomonas (lente + dor + fotofobia)
    # ⚠️ Gate de lente de contato: mesmo dor moderada é STEP 1
    dados['ulcera_cornea_suspeita'] = (
        dados.get('lente_de_contato') and
        dados.get('dor_ocular') and
        (dados.get('fotofobia') or dados.get('visao_turva') or dados.get('corpo_estranho_sensacao'))
    )

    # Uveíte anterior (ciliary flush + dor/fotofobia — mesmo sem outros critérios)
    dados['uveite_suspeita'] = (
        dados.get('ciliary_flush') and
        (dados.get('dor_ocular') or dados.get('fotofobia'))
    )

    # Celulite orbitária (com limitação de motilidade ou proptose)
    dados['celulite_orbitaria_suspeita'] = (
        dados.get('edema_palpebral') and
        (dados.get('limitacao_motilidade') or dados.get('proptose'))
    )

    # Celulite pré-septal (edema + febre, SEM limitação de motilidade)
    dados['celulite_preseptal_suspeita'] = (
        dados.get('edema_palpebral') and
        dados.get('febre') and
        not dados.get('celulite_orbitaria_suspeita')
    )

    # Pós-cirúrgico com olho vermelho → endoftalmite até prova em contrário
    dados['endoftalmite_suspeita'] = (
        dados.get('pos_cirurgico_ocular') and
        dados.get('dor_ocular') and
        dados.get('visao_turva')
    )

    # Conjuntivite bacteriana
    dados['conjuntivite_bacteriana_suspeita'] = (
        dados.get('secrecao_purulenta') and
        dados.get('palpebra_grudada') and
        not dados.get('ciliary_flush') and
        not dados.get('lente_de_contato') and
        not dados.get('pos_cirurgico_ocular')
    )

    # Conjuntivite viral — adenovírus (epidêmica)
    dados['conjuntivite_viral_suspeita'] = (
        not dados.get('secrecao_purulenta') and
        not dados.get('ciliary_flush') and
        (
            dados.get('bilateral') or
            dados.get('adenopatia_preauricular') or
            dados.get('contato_conjuntivite')
        ) and
        (dados.get('secrecao_aquosa') or dados.get('lacrimejamento'))
    )

    # Conjuntivite alérgica (prurido dominante)
    dados['conjuntivite_alergica_suspeita'] = (
        dados.get('prurido_ocular') and
        not dados.get('secrecao_purulenta') and
        not dados.get('ciliary_flush') and
        (
            dados.get('rinite_alergica_concomitante') or
            dados.get('rinite_alergica_conhecida') or
            dados.get('piora_sazonal_ocular')
        )
    )

    # Hordéolo / calázio (eritema palpebral localizado)
    dados['hordeoleo_suspeito'] = (
        dados.get('eritema_palpebral') and
        dados.get('dor_ocular') and
        not dados.get('febre') and
        not dados.get('celulite_preseptal_suspeita')
    )

    # ─── Salvar JSON ──────────────────────────────────────────────────────
    os.makedirs('dados_pacientes', exist_ok=True)
    ts  = datetime.now().strftime('%Y%m%d_%H%M%S')
    arq = os.path.join('dados_pacientes', f'olho_vermelho_subjetivo_{ts}.json')
    with open(arq, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    print(f'\n  [Dados salvos: {arq}]')
    return dados, arq


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    dados, arq = coletar_subjetivo_olho_vermelho()
    print(f'\nGlaucoma agudo: {dados.get("glaucoma_agudo_suspeito")}')
    print(f'Úlcera (lente de contato): {dados.get("ulcera_cornea_suspeita")}')
    print(f'Ciliary flush / Uveíte: {dados.get("ciliary_flush")} / {dados.get("uveite_suspeita")}')
    print(f'Conjuntivite bacteriana: {dados.get("conjuntivite_bacteriana_suspeita")}')
    print(f'Conjuntivite viral: {dados.get("conjuntivite_viral_suspeita")}')
    print(f'Conjuntivite alérgica: {dados.get("conjuntivite_alergica_suspeita")}')
