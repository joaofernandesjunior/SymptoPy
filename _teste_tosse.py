import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')
from modules.raciocinio.tosse.engine_tosse import interpretar_tosse

ok = lambda label, cat, resultado: (
    print(f'  OK  {label}: {resultado["categoria"]}') or True
    if resultado['categoria'] == cat
    else (print(f'  FALHOU  {label}: esperado={cat}, obtido={resultado["categoria"]}') or False)
)

print('=' * 54)
print('  TESTES — ENGINE TOSSE')
print('=' * 54)
resultados = []

# 1. PCP (prioridade máxima)
r1 = interpretar_tosse({
    'hiv_diagnosticado': True, 'hiv_em_tarv': False, 'cd4_conhecido': True, 'cd4_valor': 80,
    'corticoide_cronico': False, 'imunossupressao_outro': False, 'imunossuprimido': True,
    'contato_tb': False, 'duracao_semanas': 5,
    'tosse_produtiva': False, 'hemoptise': False,
    'dispneia_assoc': True, 'dispneia_progressiva': True,
    'febre': True, 'febre_alta': False,
})
resultados.append(ok('PCP', 'tosse_pcp_suspeita', r1))

# 2. Aguda viral
r2 = interpretar_tosse({
    'hiv_diagnosticado': False, 'hiv_testado_recente': True, 'hiv_fatores_risco': False,
    'corticoide_cronico': False, 'imunossupressao_outro': False, 'imunossuprimido': False,
    'contato_tb': False, 'duracao_semanas': 1,
    'tosse_produtiva': False, 'hemoptise': False,
    'dispneia_assoc': False, 'dispneia_progressiva': False,
    'febre': True, 'febre_alta': False,
    'coriza_espirros': True, 'odinofagia': True, 'dor_pleuritica': False,
    'tosse_paroxistica': False, 'guincho_inspiratorio': False, 'vomito_pos_tosse': False,
    'contato_pertussis': False, 'estertores_ausculta': False, 'saturacao_baixa': False,
    'mialgia_intensa': False, 'vacinado_influenza': True,
    'expectoracao_purulenta': False,
})
resultados.append(ok('Viral', 'tosse_aguda_viral', r2))

# 3. Pneumonia bacteriana
r3 = interpretar_tosse({
    'hiv_diagnosticado': False, 'hiv_testado_recente': True, 'hiv_fatores_risco': False,
    'corticoide_cronico': False, 'imunossupressao_outro': False, 'imunossuprimido': False,
    'contato_tb': False, 'duracao_semanas': 1,
    'tosse_produtiva': True, 'hemoptise': False,
    'dispneia_assoc': True, 'dispneia_progressiva': False,
    'febre': True, 'febre_alta': True,
    'coriza_espirros': False, 'odinofagia': False, 'dor_pleuritica': True,
    'tosse_paroxistica': False, 'guincho_inspiratorio': False, 'vomito_pos_tosse': False,
    'contato_pertussis': False, 'estertores_ausculta': True, 'saturacao_baixa': True,
    'mialgia_intensa': False, 'vacinado_influenza': True,
    'expectoracao_purulenta': True,
})
resultados.append(ok('Bacteriana', 'tosse_aguda_bacteriana', r3))

# 4. Pertussis
r4 = interpretar_tosse({
    'hiv_diagnosticado': False, 'hiv_testado_recente': True, 'hiv_fatores_risco': False,
    'corticoide_cronico': False, 'imunossupressao_outro': False, 'imunossuprimido': False,
    'contato_tb': False, 'duracao_semanas': 2,
    'tosse_produtiva': False, 'hemoptise': False,
    'dispneia_assoc': False, 'dispneia_progressiva': False,
    'febre': False, 'febre_alta': False,
    'coriza_espirros': False, 'odinofagia': False, 'dor_pleuritica': False,
    'tosse_paroxistica': True, 'guincho_inspiratorio': True, 'vomito_pos_tosse': True,
    'contato_pertussis': True, 'estertores_ausculta': False, 'saturacao_baixa': False,
    'mialgia_intensa': False, 'vacinado_influenza': True,
    'expectoracao_purulenta': False,
})
resultados.append(ok('Pertussis', 'tosse_pertussis_suspeita', r4))

# 5. IECA
r5 = interpretar_tosse({
    'hiv_diagnosticado': False, 'hiv_testado_recente': True, 'hiv_fatores_risco': False,
    'corticoide_cronico': False, 'imunossupressao_outro': False, 'imunossuprimido': False,
    'contato_tb': False, 'duracao_semanas': 12,
    'tosse_produtiva': False, 'hemoptise': False,
    'dispneia_assoc': False, 'dispneia_progressiva': False,
    'febre': False, 'febre_alta': False,
    'uso_ieca': True, 'ieca_qual': 'Enalapril', 'tosse_inicio_apos_ieca': True,
    'sensacao_gotejamento': False, 'clearing_frequente': False, 'piora_deitado_noturno': False,
    'rinite_sinusite_assoc': False, 'voz_anasalada': False, 'descarga_posterior_vista': False,
    'piora_noturna_madrugada': False, 'piora_exercicio': False, 'piora_frio_odores': False,
    'chiado_episodico': False, 'historia_atopia': False, 'asma_diagnosticada': False,
    'dpoc_diagnosticado': False, 'tabagismo_ativo': False, 'tabagismo_maco_ano': 0,
    'espiro_realizada': False,
    'pirose_regurgitacao': False, 'piora_pos_prandial': False, 'piora_deitado_drge': False,
    'rouquidao_matinal': False, 'globus_faringeo': False, 'tosse_sem_pirose': False,
    'perda_peso_involuntaria': False, 'perda_peso_kg': 0,
    'sudorese_noturna': False, 'inicio_insidioso_progressivo': False,
    'sem_febre_alta_quadro_prolongado': True, 'dispneia_progressiva_esforco': False,
    'mudanca_padrao_tosse': False, 'adenopatia_percebida': False,
    'dor_toracica_persistente': False, 'rouquidao_persistente': False, 'disfagia': False,
    'idade': 55,
})
resultados.append(ok('IECA', 'tosse_ieca', r5))

# 6. UACS
r6 = interpretar_tosse({
    'hiv_diagnosticado': False, 'hiv_testado_recente': True, 'hiv_fatores_risco': False,
    'corticoide_cronico': False, 'imunossupressao_outro': False, 'imunossuprimido': False,
    'contato_tb': False, 'duracao_semanas': 10,
    'tosse_produtiva': False, 'hemoptise': False,
    'dispneia_assoc': False, 'dispneia_progressiva': False,
    'febre': False, 'febre_alta': False,
    'uso_ieca': False, 'ieca_qual': '', 'tosse_inicio_apos_ieca': False,
    'sensacao_gotejamento': True, 'clearing_frequente': True, 'piora_deitado_noturno': True,
    'rinite_sinusite_assoc': True, 'voz_anasalada': True, 'descarga_posterior_vista': True,
    'piora_noturna_madrugada': False, 'piora_exercicio': False, 'piora_frio_odores': False,
    'chiado_episodico': False, 'historia_atopia': False, 'asma_diagnosticada': False,
    'dpoc_diagnosticado': False, 'tabagismo_ativo': False, 'tabagismo_maco_ano': 0,
    'espiro_realizada': False,
    'pirose_regurgitacao': False, 'piora_pos_prandial': False, 'piora_deitado_drge': False,
    'rouquidao_matinal': False, 'globus_faringeo': False, 'tosse_sem_pirose': False,
    'perda_peso_involuntaria': False, 'perda_peso_kg': 0,
    'sudorese_noturna': False, 'inicio_insidioso_progressivo': False,
    'sem_febre_alta_quadro_prolongado': True, 'dispneia_progressiva_esforco': False,
    'mudanca_padrao_tosse': False, 'adenopatia_percebida': False,
    'dor_toracica_persistente': False, 'rouquidao_persistente': False, 'disfagia': False,
    'idade': 38,
})
resultados.append(ok('UACS', 'tosse_uacs', r6))

# 7. TB suspeita
r7 = interpretar_tosse({
    'hiv_diagnosticado': False, 'hiv_testado_recente': False, 'hiv_fatores_risco': True,
    'corticoide_cronico': False, 'imunossupressao_outro': False, 'imunossuprimido': False,
    'contato_tb': True, 'duracao_semanas': 8,
    'tosse_produtiva': True, 'hemoptise': True,
    'dispneia_assoc': True, 'dispneia_progressiva': True,
    'febre': True, 'febre_alta': False,
    'uso_ieca': False, 'ieca_qual': '', 'tosse_inicio_apos_ieca': False,
    'sensacao_gotejamento': False, 'clearing_frequente': False, 'piora_deitado_noturno': False,
    'rinite_sinusite_assoc': False, 'voz_anasalada': False, 'descarga_posterior_vista': False,
    'piora_noturna_madrugada': False, 'piora_exercicio': False, 'piora_frio_odores': False,
    'chiado_episodico': False, 'historia_atopia': False, 'asma_diagnosticada': False,
    'dpoc_diagnosticado': False, 'tabagismo_ativo': False, 'tabagismo_maco_ano': 0,
    'espiro_realizada': False,
    'pirose_regurgitacao': False, 'piora_pos_prandial': False, 'piora_deitado_drge': False,
    'rouquidao_matinal': False, 'globus_faringeo': False, 'tosse_sem_pirose': False,
    'perda_peso_involuntaria': True, 'perda_peso_kg': 6,
    'sudorese_noturna': True, 'inicio_insidioso_progressivo': True,
    'sem_febre_alta_quadro_prolongado': True, 'dispneia_progressiva_esforco': True,
    'mudanca_padrao_tosse': False, 'adenopatia_percebida': False,
    'dor_toracica_persistente': False, 'rouquidao_persistente': False, 'disfagia': False,
    'idade': 32,
})
resultados.append(ok('TB', 'tosse_tb_suspeita', r7))

# 8. Neoplasia
r8 = interpretar_tosse({
    'hiv_diagnosticado': False, 'hiv_testado_recente': True, 'hiv_fatores_risco': False,
    'corticoide_cronico': False, 'imunossupressao_outro': False, 'imunossuprimido': False,
    'contato_tb': False, 'duracao_semanas': 16,
    'tosse_produtiva': False, 'hemoptise': True,
    'dispneia_assoc': True, 'dispneia_progressiva': True,
    'febre': False, 'febre_alta': False,
    'uso_ieca': False, 'ieca_qual': '', 'tosse_inicio_apos_ieca': False,
    'sensacao_gotejamento': False, 'clearing_frequente': False, 'piora_deitado_noturno': False,
    'rinite_sinusite_assoc': False, 'voz_anasalada': False, 'descarga_posterior_vista': False,
    'piora_noturna_madrugada': False, 'piora_exercicio': False, 'piora_frio_odores': False,
    'chiado_episodico': False, 'historia_atopia': False, 'asma_diagnosticada': False,
    'dpoc_diagnosticado': False, 'tabagismo_ativo': True, 'tabagismo_maco_ano': 30,
    'espiro_realizada': False,
    'pirose_regurgitacao': False, 'piora_pos_prandial': False, 'piora_deitado_drge': False,
    'rouquidao_matinal': False, 'globus_faringeo': False, 'tosse_sem_pirose': False,
    'perda_peso_involuntaria': True, 'perda_peso_kg': 8,
    'sudorese_noturna': False, 'inicio_insidioso_progressivo': True,
    'sem_febre_alta_quadro_prolongado': True, 'dispneia_progressiva_esforco': True,
    'mudanca_padrao_tosse': True, 'adenopatia_percebida': True,
    'dor_toracica_persistente': True, 'rouquidao_persistente': True, 'disfagia': False,
    'idade': 58,
})
resultados.append(ok('Neoplasia', 'tosse_neoplasia_suspeita', r8))

print()
passou = all(resultados)
print(f'  {"8/8 testes passaram!" if passou else f"{sum(resultados)}/8 passaram."}')
if not passou:
    sys.exit(1)
