#!/usr/bin/env python3
"""
Script para registrar um fato usando a ferramenta
`mcp_local-server_memorizar_fato`.

Fato a ser registrado:
"Integração do Aider rodando com Cerebras gpt-oss-120b e memória do Santuário validada com sucesso"
"""

import subprocess
import sys


def memorizar_fato():
    fato = (
        "Integração do Aider rodando com Cerebras gpt-oss-120b e memória do "
        "Santuário validada com sucesso"
    )
    try:
        # Executa a ferramenta de memória local passando o fato como argumento
        subprocess.run(
            ["mcp_local-server_memorizar_fato", fato],
            check=True,
        )
        print("Fato registrado com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao registrar o fato: {e}", file=sys.stderr)
        sys.exit(e.returncode)


if __name__ == "__main__":
    memorizar_fato()
