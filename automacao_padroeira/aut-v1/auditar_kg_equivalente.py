#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auditoria do cálculo de "Kg Equivalente" (Refeição e Sobremesa/Doces).

Valida a extração + conversão aplicada por cortex_padroeira_async._parsear_fechamento
sobre um arquivo de fechamento real (default: fechamentos/fechamento_caixa_2026-07-23.txt)
 e exibe a memória de cálculo completa.

Uso:
    python3 auditar_kg_equivalente.py [DATA_ISO]   # DATA_ISO ex.: 2026-07-23
"""
import os
import re
import sys
from datetime import datetime

import config_precos as cp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _fnum(padrao: str, texto: str, flags: int = 0):
    m = re.search(padrao, texto, flags)
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", "."))
    except ValueError:
        return None


def _somar_kg(padrao: str, texto: str) -> float:
    soma = 0.0
    for v in re.findall(padrao, texto):
        try:
            soma += float(v.replace(",", "."))
        except ValueError:
            continue
    return soma


def auditar(data_iso: str) -> dict:
    caminho = os.path.join(BASE_DIR, "fechamentos", f"fechamento_caixa_{data_iso}.txt")
    if not os.path.exists(caminho):
        raise FileNotFoundError(caminho)
    texto = open(caminho, encoding="utf-8").read()

    dt = datetime.strptime(data_iso, "%Y-%m-%d").date()
    vkg = cp.valor_kg_dia(dt)
    nome_dia = dt.strftime("%A")

    peso_buf = _somar_kg(r"REFEICAO QUILO\s+KG\s+([\d.,]+)", texto)
    peso_sob = _somar_kg(r"SOBREMESA QUILO\s+KG\s+([\d.,]+)", texto)
    qtd_av = _fnum(r"REFEICAO A VONTADE\s+UN\s+([\d.,]+)", texto) or 0.0
    qtd_ts = _fnum(r"REFEICAO TO SAVE\s+UN\s+([\d.,]+)", texto) or 0.0
    val_exec = _fnum(r"PRATOS EXECUTIVOS\s+[\d.,]+\s+([\d.,]+)", texto) or 0.0
    val_doces = _fnum(r"\bDOCES\s+[\d.,]+\s+([\d.,]+)", texto) or 0.0

    ref_quilo_rs = peso_buf * vkg
    av_rs = qtd_av * cp.REFEICAO_A_VONTADE
    ts_rs = qtd_ts * cp.REFEICAO_TO_SAVE
    fat_ref = ref_quilo_rs + av_rs + ts_rs + val_exec
    kg_eq_ref = fat_ref / vkg

    sob_quilo_rs = peso_sob * vkg
    fat_sob = sob_quilo_rs + val_doces
    kg_eq_sob = fat_sob / vkg

    print("=" * 72)
    print(f"AUDITORIA DE KG EQUIVALENTE — {data_iso} ({nome_dia})")
    print("=" * 72)
    print(f"VALOR_KG_DIA = R$ {vkg:.2f}  (config: {cp.REFEICAO_KG_PADRAO if dt.weekday()!=5 else cp.REFEICAO_KG_SABADOS})")
    print()
    print("REFEIÇÃO (linha 3 do Diário)")
    print(f"  Refeição Quilo : {peso_buf:.3f} KG x {vkg:.2f} = R$ {ref_quilo_rs:,.2f}".replace(",", "."))
    print(f"  A Vontade      : {qtd_av:.0f} UN  x {cp.REFEICAO_A_VONTADE:.2f} = R$ {av_rs:,.2f}".replace(",", "."))
    print(f"  To Save        : {qtd_ts:.0f} UN  x {cp.REFEICAO_TO_SAVE:.2f} = R$ {ts_rs:,.2f}".replace(",", "."))
    print(f"  Executivos (R$):                       R$ {val_exec:,.2f}".replace(",", "."))
    print(f"  ------------------------------------------------  R$ {fat_ref:,.2f}".replace(",", "."))
    print(f"  Kg Equivalente Refeição = {fat_ref:,.2f} / {vkg:.2f} = {kg_eq_ref:.2f} kg".replace(",", "."))
    print()
    print("SOBREMESA / DOCES (linha 4 do Diário)")
    print(f"  Sobremesa Quilo: {peso_sob:.3f} KG x {vkg:.2f} = R$ {sob_quilo_rs:,.2f}".replace(",", "."))
    print(f"  Doces (R$)     :                       R$ {val_doces:,.2f}".replace(",", "."))
    print(f"  ------------------------------------------------  R$ {fat_sob:,.2f}".replace(",", "."))
    print(f"  Kg Equivalente Sobremesa = {fat_sob:,.2f} / {vkg:.2f} = {kg_eq_sob:.2f} kg".replace(",", "."))
    print("=" * 72)

    return {
        "data": data_iso, "vkg": vkg,
        "peso_buf": peso_buf, "peso_sob": peso_sob,
        "qtd_av": qtd_av, "qtd_ts": qtd_ts,
        "val_exec": val_exec, "val_doces": val_doces,
        "kg_eq_ref": round(kg_eq_ref, 2), "kg_eq_sob": round(kg_eq_sob, 2),
    }


if __name__ == "__main__":
    data = sys.argv[1] if len(sys.argv) > 1 else "2026-07-23"
    res = auditar(data)
    # Casos conhecidos de validação
    if data == "2026-07-23":
        ok_ref = abs(res["kg_eq_ref"] - 89.25) < 0.01
        ok_sob = abs(res["kg_eq_sob"] - 10.54) < 0.02  # tolerância p/ arredondamento do centavo
        print(f"\nVALIDAÇÃO (caso 23/07/2026):")
        print(f"  Refeição 89,25 kg -> {res['kg_eq_ref']:.2f} kg  [{'OK' if ok_ref else 'FALHOU'}]")
        print(f"  Sobremesa ~10,54 kg -> {res['kg_eq_sob']:.2f} kg  [{'OK' if ok_sob else 'FALHOU'}]")
        sys.exit(0 if (ok_ref and ok_sob) else 1)
