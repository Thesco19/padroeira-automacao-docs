#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
teste_fechar_codigo.py — exercita a funcao REAL _fechar_dia() do bot
bot_reconciliation.py, sem Telegram (bot morto / polling bloqueado pelo
webhook) e sem entrar no Saurus.

Truca datetime.now() para 27/08/2026 para que _fechar_dia() leia o
fechamento_caixa_2026-08-27.txt (em cache) e reconstrua o historico do dia,
exatamente o caminho do /fechar. Confere o registro retornado e re-salva o
historico (idempotente) via _salvar_historico_faturamento().

ATENCAO: importar bot_reconciliation.py trunca reconciliation.log (FileHandler
mode="w"); o log forense ja foi backupeado antes de rodar.
"""
import importlib.util
import os
import sys
from datetime import datetime

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # aut-v1
sys.path.insert(0, WORK)

FAKE_HOJE = datetime(2026, 8, 27, 23, 59, 0)


def _carregar(modulo, caminho):
    spec = importlib.util.spec_from_file_location(modulo, caminho)
    m = importlib.util.module_from_spec(spec)
    sys.modules[modulo] = m
    spec.loader.exec_module(m)
    return m


bot = _carregar("bot_reconciliation", os.path.join(WORK, "bot_reconciliation.py"))

# Truca datetime.now() para 27/08/2026 (bot_reconciliation faz from datetime import datetime)
bot.datetime.now = lambda: FAKE_HOJE

print("=== Chamando bot._fechar_dia() (caminho real do /fechar, hoje=27/08) ===")
reg = bot.asyncio.run(bot._fechar_dia())

print("erro:", reg.get("erro"))
print("data:", reg.get("data"), "| aamm:", reg.get("aamm"))
print("entrou_saurus:", reg.get("entrou_saurus"), "| do_cache:", reg.get("do_cache"))
print("--- msg gerada (seria enviada ao Telegram) ---")
print(reg.get("msg"))
print("---" )

# Re-salva no historico (idempotente) e confere
if not reg.get("erro"):
    salvou = bot._salvar_historico_faturamento(reg)
    print(f"[HISTORICO] re-salvou: {salvou} -> {bot.HIST_FILE}")
    import json
    h = json.load(open(bot.HIST_FILE))
    print("historico atual:", list(h.keys()))

print("\n=== RESUMO ===")
ok = (not reg.get("erro")) and reg.get("do_cache") and (reg.get("aamm") == "2608")
print("CAMINHO /fechar OK:" , ok)
sys.exit(0 if ok else 1)
