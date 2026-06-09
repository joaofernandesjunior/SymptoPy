def sn(pergunta):
    while True:
        resp = input(pergunta).strip().lower()
        if resp in ("s", "n"):
            return resp == "s"
        print("Digite s ou n.")

