#!/usr/bin/env python3
"""Teste do regex de extração dos dados do Saurus contra o fechamento_caixa.txt de mock."""

import re

with open("fechamento_caixa.txt", "r", encoding="utf-8") as f:
    conteudo = f.read()

print("--- Conteudo do arquivo ---")
print(conteudo)
print("--- Testes de Regex ---")

# Format real: DINHEIRO: R$ 1.250,00
dinheiro = re.search(r"DINHEIRO:\s+R\$\s+([\d\.,]+)", conteudo)
credito = re.search(r"CR[ÉE]DITO:\s+R\$\s+([\d\.,]+)", conteudo)
debito = re.search(r"D[ÉE]BITO:\s+R\$\s+([\d\.,]+)", conteudo)
total = re.search(r"TOTAL:\s+R\$\s+([\d\.,]+)", conteudo)
clientes = re.search(r"Total de clientes:\s+(\d+)", conteudo)
peso_buf = re.search(r"Buf:\s+R\$\s+([\d\.,]+)", conteudo)
peso_sob = re.search(r"Sob:\s+R\$\s+([\d\.,]+)", conteudo)

print("Dinheiro:", dinheiro.group(1) if dinheiro else "NAO")
print("Credito:", credito.group(1) if credito else "NAO")
print("Debito:", debito.group(1) if debito else "NAO")
print("Total:", total.group(1) if total else "NAO")
print("Clientes:", clientes.group(1) if clientes else "NAO")
print("Peso Buf:", peso_buf.group(1) if peso_buf else "NAO")
print("Peso Sob:", peso_sob.group(1) if peso_sob else "NAO")
