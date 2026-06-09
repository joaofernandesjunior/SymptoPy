# tests/test_linfadenopatia.py
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from modules.raciocinio.linfadenopatia.engine_linfadenopatia import interpretar_linfadenopatia

def _base():
    return {
        'idade': 28, 'sexo': 'F', 'tabagismo': False, 'imunossupressao': False,
        'hiv_conhecido': False, 'localizacao': 'cervical', 'tamanho_cm': 1.5,
        'textura': 'mole_movel', 'doloroso': True, 'duracao_semanas': 2,
        'crescimento_rapido': False, 'pele_sobre_linfonodo': False,
        'febre_sem_foco': False, 'sudorese_noturna': False, 'perda_peso': False,
        'b_symptoms': False, 'esplenomegalia': False, 'hemoptise': False,
        'alargamento_mediastino': False, 'hc_disponivel': False,
        'pancitopenia': False, 'blastos': False, 'anemia_inexplicada': False,
        'ldh_disponivel': False, 'ldh_valor': None,
        'faringite_recente': False, 'problema_dental': False, 'infeccao_pele_cab': False,
        'infeccao_mmss': False, 'exposicao_gato': False, 'papula_inoculacao': False,
        'vacina_recente_ax': False, 'alteracao_mama': False,
        'infeccao_mmii': False, 'contato_sexual_recente': False, 'sintomas_ists': False,
        'sindrome_mono': False, 'monospot_feito': False, 'monospot_positivo': False,
        'risco_tb': False, 'igra_feito': False, 'igra_positivo': False,
        'hiv_testado': True, 'hiv_positivo': False, 'comportamento_risco_hiv': False,
        'atb_em_uso': False, 'atb_duracao': 0, 'melhora_atb': False,
        'medicamentos_culpados': False,
    }

def _run(nome, dados, esperado):
    r = interpretar_linfadenopatia(dados)
    cat = r.get('categoria', '')
    ok  = cat == esperado
    print(f'  {"OK" if ok else "XX"} [{nome}] -> {cat}  (esperado: {esperado})')
    if not ok: print(f'      diag: {r.get("diagnostico","")}')
    return ok

CASOS = [
    # 1. Supraclavicular → sempre biópsiar (metastático em tabagista > 50)
    ('supraclavicular_metastatico',
     {**_base(), 'localizacao': 'supraclavicular', 'textura': 'duro_fixo',
      'idade': 58, 'tabagismo': True},
     'neoplasia_metastatica'),

    # 2. Supraclavicular em jovem → linfoma
    ('supraclavicular_linfoma',
     {**_base(), 'localizacao': 'supraclavicular', 'textura': 'borrachoso', 'idade': 25},
     'linfoma_suspeito'),

    # 3. Sintomas B → linfoma urgente
    ('b_symptoms_linfoma',
     {**_base(), 'b_symptoms': True, 'febre_sem_foco': True, 'sudorese_noturna': True,
      'perda_peso': True, 'textura': 'borrachoso', 'localizacao': 'cervical'},
     'linfoma_suspeito'),

    # 4. EBV — tríade
    ('ebv_mononucleose',
     {**_base(), 'sindrome_mono': True, 'monospot_positivo': True},
     'ebv_mononucleose'),

    # 5. Cat-scratch disease
    ('cat_scratch',
     {**_base(), 'localizacao': 'axilar', 'exposicao_gato': True,
      'papula_inoculacao': True},
     'doenca_arranhadura_gato'),

    # 6. TB — IGRA positivo + risco
    ('tb_linfadenopatia',
     {**_base(), 'risco_tb': True, 'igra_feito': True, 'igra_positivo': True,
      'duracao_semanas': 8},
     'tb_linfadenopatia'),

    # 7. IST inguinal
    ('ist_inguinal',
     {**_base(), 'localizacao': 'inguinal', 'contato_sexual_recente': True,
      'sintomas_ists': True},
     'ist_linfadenopatia_inguinal'),

    # 8. HIV primário — risco + generalizado + não testado
    ('hiv_primario',
     {**_base(), 'localizacao': 'generalizado', 'hiv_testado': False,
      'comportamento_risco_hiv': True},
     'hiv_infeccao_primaria'),

    # 9. Biópsia indicada — > 2 cm + > 4 sem + > 40 anos
    ('biopsia_linfoma',
     {**_base(), 'tamanho_cm': 2.5, 'duracao_semanas': 6, 'idade': 45,
      'textura': 'borrachoso'},
     'linfoma_suspeito'),

    # 10. Reativo — jovem, cervical, mole, faringite, < 2 semanas
    ('reativo_faringite',
     {**_base(), 'faringite_recente': True, 'doloroso': True},
     'linfadenopatia_reativa'),

    # 11. Bacteriana — pele inflamada + fonte clara
    ('bacteriana',
     {**_base(), 'infeccao_mmss': True, 'localizacao': 'axilar',
      'doloroso': True, 'pele_sobre_linfonodo': True},
     'linfadenite_bacteriana'),

    # 12. Hérnia inguinal — Valsalva + redutível
    ('hernia_inguinal',
     {**_base(), 'localizacao': 'inguinal', 'aumenta_valsalva': True,
      'redutivel': True, 'sons_intestinais': False, 'abaixo_lig_inguinal': False,
      'extensao_escrotal': False, 'multiplos_nodulos': False, 'piora_esforco': True,
      'contato_sexual_recente': False, 'sintomas_ists': False, 'infeccao_mmii': False},
     'hernia_inguinal_suspeita'),

    # 13. Hérnia femoral — abaixo do ligamento, não múltipla
    ('hernia_femoral',
     {**_base(), 'localizacao': 'inguinal', 'aumenta_valsalva': True,
      'redutivel': False, 'sons_intestinais': False, 'abaixo_lig_inguinal': True,
      'extensao_escrotal': False, 'multiplos_nodulos': False, 'piora_esforco': True,
      'contato_sexual_recente': False, 'sintomas_ists': False, 'infeccao_mmii': False},
     'hernia_femoral_suspeita'),

    # 14. Linfonodo inguinal benigno — múltiplos, moles, < 2 cm, sem Valsalva
    ('linfonodo_inguinal_benigno',
     {**_base(), 'localizacao': 'inguinal', 'aumenta_valsalva': False,
      'redutivel': False, 'sons_intestinais': False, 'abaixo_lig_inguinal': False,
      'extensao_escrotal': False, 'multiplos_nodulos': True, 'piora_esforco': False,
      'tamanho_cm': 1.2, 'doloroso': True, 'textura': 'mole_movel',
      'contato_sexual_recente': False, 'sintomas_ists': False, 'infeccao_mmii': False},
     'linfadenopatia_inguinal_benigna'),
]

def main():
    print('\n' + '='*56)
    print('  SMOKE TESTS — ENGINE LINFADENOPATIA')
    print('='*56)
    res = [_run(n, d, e) for n, d, e in CASOS]
    print(f'\n  Resultado: {sum(res)}/{len(res)} OK')
    print('='*56)
    return all(res)

if __name__ == '__main__':
    sys.exit(0 if main() else 1)
