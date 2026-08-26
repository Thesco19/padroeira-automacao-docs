import datetime

def registrar_fato(fato):
    print(f"Fato registrado: {fato} às {datetime.datetime.now().strftime('%H:%M')}")

# Registrar o fato
fato = "Integração do Aider com a memória do Santuário validada com sucesso"
registrar_fato(fato)
