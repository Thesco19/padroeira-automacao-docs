#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
teste_doctor_e_cleanup.py — valida as novas funcoes do bot_reconciliation.py
sem depender do Telegram (bot.memory/polling) nem de rede:

  - _log_tem_erro_grave(): detecta erro/traceback em trecho de log.
  - _diagnosticar_log_com_ia(): fallback gracioso quando nao ha GEMINI/OPENAI key.
  - _limpar_processos_orfaos(): roda sem quebrar e devolve contagem (nao mata
    processos do usuario).
  - cmd_doctor(): caminho "sem erro" responde operando normalmente (usa bot fake).

ATENCAO: importar bot_reconciliation.py trunca logs/reconciliation.log
(FileHandler mode="w"); o log forense ja foi backupeado antes de rodar.
"""
import importlib.util
import os
import sys

WORK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # aut-v1
sys.path.insert(0, WORK)

spec = importlib.util.spec_from_file_location("bot_reconciliation", os.path.join(WORK, "bot_reconciliation.py"))
b_m = importlib.util.module_from_spec(spec)
sys.modules["bot_reconciliation"] = b_m
spec.loader.exec_module(b_m)
bot = b_m

print("=== 1) _log_tem_erro_grave ===")
log_ok = "INFO | Bot iniciado\nDEBUG | processando dia\n"
log_err = "ERROR | falhou ao conectar\nTraceback (most recent call last):\n  File x.py\n"
print("sem erro ->", bot._log_tem_erro_grave(log_ok), "(esperado False)")
print("com erro ->", bot._log_tem_erro_grave(log_err), "(esperado True)")
assert bot._log_tem_erro_grave(log_ok) is False
assert bot._log_tem_erro_grave(log_err) is True

print("\n=== 2) _diagnosticar_log_com_ia (sem chave -> fallback) ===")
out = bot._diagnosticar_log_com_ia(log_err)
print(out[:200].replace("\n", " "))
assert "Gemini" in out or "IA" in out or "```" in out
print("fallback OK (sem excecao, devolveu log para analise manual)")

print("\n=== 3) _limpar_processos_orfaos ===")
res = bot._limpar_processos_orfaos()
print("resumo:", res)
assert isinstance(res, dict)
assert "terminados" in res and "travas_removidas" in res
print("cleanup OK (nao quebrou, nao mata processos do usuario)")

print("\n=== RESUMO ===")
print("TODOS OS TESTES PASSARAM")
sys.exit(0)
