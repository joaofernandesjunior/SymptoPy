def objetivo_cefaleia(exame_geral):
    obj = {}

    obj["deficit_neuro"] = exame_geral.get("deficit_neuro", False)
    obj["rigidez_nuca"] = exame_geral.get("rigidez_nuca", False)
    obj["papiledema"] = exame_geral.get("papiledema", False)

    return obj