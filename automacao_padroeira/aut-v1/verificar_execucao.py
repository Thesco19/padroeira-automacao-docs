#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificação Pós-Execução - Córtex Padroeira
=============================================

Checagem determinística (sem LLM/agente) do que uma rodada do pipeline
realmente fez. Roda depois de cada execução e imprime um relatório;
retorna código de saída != 0 se algo parecer errado, pra poder ser
encadeado num cron/CI simples.

Uso:
    python3 verificar_execucao.py --aamm 2608 --desde "2026-08-13T00:00:00"
"""

import argparse
import sqlite3
import sys
from datetime import datetime, date

from backup_padroeira import DB_PATH

DATA_MINIMA = date(2026, 6, 1)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verificação pós-execução")
    parser.add_argument("--aamm", required=True, help="Mês verificado, formato AAMM")
    parser.add_argument("--desde", required=True, help="Timestamp ISO da execução (ex: saída do log)")
    args = parser.parse_args()

    problemas = []
    aamm_prefixo = f"20{args.aamm[:2]}-{args.aamm[2:]}-"

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # 1) Snapshots criados nesta execução
    snaps = conn.execute(
        "SELECT arquivo_original, criado_em FROM snapshots WHERE criado_em >= ? ORDER BY criado_em",
        (args.desde,),
    ).fetchall()
    esperados = {"Movto_cx2.xlsx"} | {f"Movto_diario.{args.aamm}.xlsx"}
    encontrados = {s["arquivo_original"] for s in snaps}
    faltando = esperados - encontrados
    print(f"[1] Snapshots desde {args.desde}: {len(snaps)} — {sorted(encontrados)}")
    if faltando:
        problemas.append(f"Snapshot faltando para: {faltando}")

    # 2) Divergências / checkup do mês
    divs = conn.execute(
        "SELECT status, COUNT(*) as qtd FROM divergencias WHERE data_iso LIKE ? GROUP BY status",
        (f"{aamm_prefixo}%",),
    ).fetchall()
    print(f"[2] Divergências do mês {args.aamm}:")
    total_dias = 0
    for row in divs:
        print(f"     {row['status']}: {row['qtd']}")
        total_dias += row["qtd"]
    if total_dias == 0:
        problemas.append(f"Nenhuma divergência registrada para {args.aamm} — pipeline rodou mesmo?")

    # 3) Escopo: nada antes de 2026-06-01
    fora_escopo = conn.execute(
        "SELECT data_iso FROM divergencias WHERE data_iso < ?",
        (DATA_MINIMA.isoformat(),),
    ).fetchall()
    if fora_escopo:
        problemas.append(
            f"{len(fora_escopo)} registro(s) com data anterior a {DATA_MINIMA.isoformat()}: "
            f"{[r['data_iso'] for r in fora_escopo]}"
        )
    else:
        print(f"[3] Escopo ok: nenhum registro anterior a {DATA_MINIMA.isoformat()}.")

    # 4) Dias que precisariam de alerta — pra conferir manualmente se o Telegram chegou
    precisa_reconf = conn.execute(
        "SELECT data_iso, valor_caixa, valor_computado, divergencia, alertado_em "
        "FROM divergencias WHERE status = 'precisa_reconferencia' AND data_iso LIKE ?",
        (f"{aamm_prefixo}%",),
    ).fetchall()
    if precisa_reconf:
        print(f"[4] {len(precisa_reconf)} dia(s) precisam de reconferência manual:")
        for r in precisa_reconf:
            alerta = "alertado" if r["alertado_em"] else "⚠️ SEM ALERTA REGISTRADO"
            print(f"     {r['data_iso']}: diff={r['divergencia']} ({alerta})")
            if not r["alertado_em"]:
                problemas.append(f"{r['data_iso']} precisa reconferência mas não tem alerta registrado")
    else:
        print("[4] Nenhum dia precisando de reconferência manual neste mês.")

    conn.close()

    print("\n=== RESULTADO ===")
    if problemas:
        print("❌ Problemas encontrados:")
        for p in problemas:
            print(f"   - {p}")
        return 1
    print("✅ Nenhum problema detectado pelas checagens automáticas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
