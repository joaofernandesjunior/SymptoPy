# test_subjetivo.py — testa o subjetivo injetando dados direto, sem input()
# Valida que o dicionário final tem as chaves corretas para o engine
# Rodar: python3 -m modules.sintomas.musculoesqueletico.joelho.test_subjetivo

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from modules.sintomas.musculoesqueletico.joelho.subjetivo import completar_chaves_padrao
from modules.raciocinio.musculoesqueletico.joelho.core.engine import interpretar_joelho

def montar_caso(overrides):
    """Monta dicionário base com todos False e aplica overrides."""
    base = {
        'idade': 30, 'idade_acima_55': False, 'idade_acima_50': False,
        'idade_acima_45': False, 'idade_acima_40': False, 'idade_abaixo_40': True,
        'febre': False, 'perda_de_peso_inexplicada': False, 'dor_noturna_sem_alivio': False,
        'historico_cancer': False, 'imunossupressao': False, 'uso_cronico_corticoide': False,
        'deficit_neurologico_progressivo': False, 'hemartrose_imediata': False,
        'trauma_significativo': False, 'osteoporose': False, 'idade_acima_70': False,
        'dor_nova': True, 'red_flag_sistemica': False, 'sinal_trauma_importante': False,
        'red_flag_presente': False,
        'trauma_agudo': False, 'sensibilidade_isolada_patela': False,
        'sensibilidade_cabeca_fibula': False, 'incapaz_flexao_90': False,
        'incapaz_suportar_peso': False, 'trauma_torcao_recente': False,
        'derrame_horas_apos_trauma': False, 'trauma': False,
        'trauma_ou_sobrecarga_recente': False,
        'inicio_insidioso': False, 'dor_mecanica': False, 'melhora_com_repouso': False,
        'dor_localizada': False, 'rigidez_matinal_menos_30min': False,
        'rigidez_matinal_acima_60min': False, 'piora_com_atividade': False,
        'piora_com_movimento_ou_carga': False, 'inicio_insidioso_com_uso': False,
        'sem_sintomas_neurologicos': True, 'formigamento_ou_dormencia': False,
        'deficit_sensorial_ou_reflexo': False, 'piora_noturna_caracteristica': False,
        'dor_generalizada_ou_difusa': False,
        'articulacoes_multiplas_afetadas': False, 'articulacoes_multiplas': False,
        'calor_ou_eritema_articular': False, 'sem_calor_ou_eritema': True,
        'sintomas_sistemicos': False, 'melhora_com_atividade_leve': False,
        'piora_com_repouso': False, 'envolvimento_simetrico': False,
        'dor_anterior_joelho': False, 'dor_linha_articular': False,
        'massa_fossa_poplitea': False, 'relato_derrame': False,
        'sinal_do_cinema': False, 'piora_escadas_ou_agachamento': False,
        'travamento_ou_estalido': False,
        'inchaço_sobre_patela': False, 'trabalho_ajoelhado': False,
        'dor_medial_abaixo_linha_articular': False, 'dor_cruzar_pernas': False,
        'obesidade_ou_oa_associada': False,
        'dificuldade_flexao_completa': False, 'oa_ou_lesao_meniscal_conhecida': False,
    }
    base.update(overrides)
    completar_chaves_padrao(base)
    return base


CASOS = {
    'OA CLASSICA (58F)': {
        'idade': 58, 'idade_acima_55': True, 'idade_acima_50': True,
        'idade_acima_45': True, 'idade_acima_40': True, 'idade_abaixo_40': False,
        'inicio_insidioso': True, 'dor_mecanica': True, 'melhora_com_repouso': True,
        'rigidez_matinal_menos_30min': True, 'dor_localizada': True,
        'piora_com_atividade': True, 'piora_com_movimento_ou_carga': True,
        'inicio_insidioso_com_uso': True, 'sem_calor_ou_eritema': True,
        'obesidade_ou_oa_associada': True,
    },
    'LESAO MENISCAL (28M, torção)': {
        'idade': 28, 'idade_abaixo_40': True,
        'trauma_agudo': True, 'trauma': True, 'trauma_torcao_recente': True,
        'trauma_ou_sobrecarga_recente': True,
        'dor_linha_articular': True, 'travamento_ou_estalido': True,
        'derrame_horas_apos_trauma': True, 'dor_mecanica': True,
        'piora_com_atividade': True, 'dor_localizada': True,
    },
    'SDPF (22F, jovem)': {
        'idade': 22, 'idade_abaixo_40': True,
        'dor_anterior_joelho': True, 'sinal_do_cinema': True,
        'piora_escadas_ou_agachamento': True, 'dor_mecanica': True,
        'piora_com_atividade': True, 'dor_localizada': True,
        'inicio_insidioso': True,
    },
    'RED FLAG SEPTICA': {
        'febre': True, 'imunossupressao': True,
        'red_flag_sistemica': True, 'red_flag_presente': True,
        'calor_ou_eritema_articular': True, 'sem_calor_ou_eritema': False,
    },
}

if __name__ == '__main__':
    for nome, overrides in CASOS.items():
        dados = montar_caso(overrides)
        resultado = interpretar_joelho(dados)

        print(f'\n{"="*55}')
        print(f'CASO: {nome}')
        print('='*55)
        print(f'Categoria: {resultado["categoria"]}')

        if resultado['categoria'] == 'red_flag_emergencia':
            for f in resultado['red_flags']['flags']:
                print(f"  [{f['urgencia'].upper()}] {f['achado']}: {f['acao']}")

        elif resultado['categoria'] == 'padrao_inflamatorio':
            print(f"  Padrão: {resultado['padrao']['padrao']}")
            print(f"  Exames: {resultado['padrao']['exames_sugeridos']}")

        else:
            if resultado.get('ottawa'):
                print(f"  Ottawa: {resultado['ottawa']['acao']}")
            print(f"  Padrão: {resultado['padrao']['padrao']}")
            print(f"  Mecanismo: {resultado['mecanismo']['mecanismo_dominante']}")
            if resultado['hipoteses_provaveis']:
                print('  Hipóteses prováveis:')
                for h in resultado['hipoteses_provaveis']:
                    print(f"    [{h['forca'].upper()}] {h['hipotese']} (score {h['score']})")
                    for c in h['conduta']:
                        print(f"      → {c}")
            if resultado['hipoteses_possiveis']:
                print('  Hipóteses possíveis:')
                for h in resultado['hipoteses_possiveis']:
                    print(f"    [{h['forca'].upper()}] {h['hipotese']} (score {h['score']})")
            if resultado['hipoteses_exclusao']:
                print(f"  Exclusão: {resultado['hipoteses_exclusao']}")
