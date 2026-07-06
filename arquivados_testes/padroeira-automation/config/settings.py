"""
Configurações do Projeto Padroeira Automation
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

# Caminhos
PASTA_LAB = BASE_DIR
PASTA_VENDAS_ORIGEM = "/home/teco/Nuvens/Box/Padroeira/Padroeira vendas"
PASTA_RESTAURANTE_ANO = "/home/teco/Nuvens/Box/Padroeira/Restaurante/A2026"

# Token Telegram (nunca commitar)
TOKEN_TELEGRAM = os.getenv("TOKEN_TELEGRAM", "SEU_TOKEN_AQUI")

# Configurações de execução
HEADLESS = False
AAMM_ATUAL = "2606"  # Junho/2026 - atualizar conforme necessário
