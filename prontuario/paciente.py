def coletar_paciente():
    paciente = {}

    paciente['nome'] = input('Nome: ').strip()
    paciente['idade'] = input('Idade: ').strip()
    paciente['sexo'] = input('Sexo (m/f): ').strip().lower()
    paciente['profissao'] = input('Profissão: ').strip()
    paciente['procedencia'] = input('Procedência: ').strip()
    paciente['rg_hc'] = input('RG HC: ').strip()

    paciente['contexto_social'] = input('Contexto social: ').strip()
    paciente['chv'] = input('Condições e hábitos de vida: ').strip()

    paciente['comorbidades'] = input('Comorbidades (ex: DRC, HAS, DM2, FA, DPOC, cirrose): ').strip()
    paciente['medicacoes'] = input('Medicações de uso contínuo (separar por vírgula; ex: losartana 50mg 1-0-1, espironolactona 25mg 1-0-0, metformina 850mg 1-0-1): ').strip()
    paciente['alergias'] = input('Alergias: ').strip()
    paciente['cirurgias_previas'] = input('Cirurgias prévias: ').strip()
    paciente['internamentos'] = input('Internamentos: ').strip()
    return paciente