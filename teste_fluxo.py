import json

def parsear_payload(arquivo: str) -> dict:
    try:
        with open(arquivo, 'r') as f:
            payload = json.load(f)
            return payload
    except json.JSONDecodeError as e:
        print(f"Erro ao parsear JSON: {e}")
        return None
    except FileNotFoundError:
        print("Arquivo não encontrado")
        return None

def main():
    arquivo = 'payload_teste.json'
    payload = parsear_payload(arquivo)
    if payload:
        print(payload)

if __name__ == '__main__':
    main()
