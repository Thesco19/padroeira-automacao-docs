#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ponto de entrada principal da automação (pasta lab-a).

Este script simplesmente delega a execução para o motor assíncrono
definido em `async_reconciliation_v2.py`. Ele pode ser invocado
diretamente:

    python -m lab-a.main

ou, após instalação do pacote, como entry‑point definido no
`pyproject.toml`/`setup.cfg`.
"""

import asyncio
import sys
from pathlib import Path

# Garantir que o diretório raiz do projeto esteja no PYTHONPATH
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from async_reconciliation_v2 import main as async_main

def run():
    """Executa a rotina de reconciliação assíncrona."""
    asyncio.run(async_main())

if __name__ == "__main__":
    run()
