#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smoke Test - Córtex Padroeira
==============================

Roda o pipeline completo (cache de fechamentos -> paridade -> consolidação
-> divergência) contra um mês JÁ CONHECIDO, sem disparar Telegram, e imprime
um resumo pra comparar com o que uma conferência manual já sabe ser verdade.

⚠️ IMPORTANTE: rode isto contra uma CÓPIA da pasta de dados, nunca contra a
pasta de produção. O engine de consolidação escreve de verdade no
Movto_diario.{aamm}.xlsx (mesmo sem bot, ele salva o arquivo). O snapshot de
backup protege contra desastre, mas o objetivo do smoke test é validar a
lógica sem arriscar o mês real.

Uso:
    python3 smoke_test_padroeira.py --base-dir /caminho/para/copia --aamm 2607

Se --base-dir não apontar para uma pasta com "sandbox", "teste" ou "copia"
no nome, o script pede confirmação explícita antes de continuar.
"""

import argparse
import os
import sqlite3
import sys

# Garante que os módulos do projeto (cortex_padroeira_async, engine_consolidacao_async,
# backup_padroeira, calendario_padroeira) sejam encontrados a partir do --base-dir.
def _preparar_sys_path(base_dir: str) -> None:
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)


def _confirmar_pasta_segura(base_dir: str) -> bool:
    nome = os.path.basename(os.path.normpath(base_dir)).lower()
    palavras_seguras = ("sandbox", "teste", "test", "copia", "cópia", "smoke")
    if any(p in nome for p in palavras_seguras):
        return True
    resposta = input(
        f"⚠️  '{base_dir}' não parece ser uma pasta de teste (não tem "
        f"sandbox/teste/copia no nome). Tem certeza que NÃO é a pasta de "
        f"produção? Digite 'confirmo' para continuar: "
    )
    return resposta.strip().lower() == "confirmo"


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test do Córtex Padroeira")
    parser.add_argument("--base-dir", required=True, help="Pasta com os arquivos (deve ser uma CÓPIA de teste)")
    parser.add_argument("--aamm", required=True, help="Mês-alvo no formato AAMM, ex: 2607 para julho/2026")
    args = parser.parse_args()

    base_dir = os.path.abspath(args.base_dir)

    if not os.path.isdir(base_dir):
        print(f"❌ Pasta não encontrada: {base_dir}")
        return 1

    if not _confirmar_pasta_segura(base_dir):
        print("Abortado pelo usuário.")
        return 1

    _preparar_sys_path(base_dir)

    # Import tardio: só depois de ajustar o sys.path pro base_dir correto.
    from cortex_padroeira_async import CortexPadroeiraAsync
    from engine_consolidacao_async import EngineConsolidacaoAsync
    from backup_padroeira import DB_PATH

    print(f"\n=== SMOKE TEST — {args.aamm} — {base_dir} ===\n")

    # 1) Carrega cache de fechamentos locais (sem chamar Playwright/portal).
    cortex = CortexPadroeiraAsync(base_dir=base_dir)
    carregados = cortex.carregar_cache_fechamentos()
    print(f"[1/4] Fechamentos carregados do cache: {carregados}")

    # 2) Verifica paridade / datas pendentes pro mês-alvo.
    ok_paridade = cortex.verificar_paridade_planilhas(args.aamm)
    print(f"[2/4] Verificação de paridade: {'OK' if ok_paridade else 'FALHOU'}")
    print(f"       Pendentes detectados: {len(cortex.pendentes)} -> {cortex.pendentes}")

    # 3) Roda o engine de consolidação SEM bot (não dispara Telegram),
    #    mas ainda grava snapshot + divergências no SQLite.
    engine = EngineConsolidacaoAsync(aamm=args.aamm)
    resultado = engine.executar_motor_unificado(
        dados_cortex=cortex.dados_por_data, bot=None, chat_id=None
    )
    print(f"[3/4] Consolidação: {resultado['status']}")
    if resultado["status"] != "success":
        print(f"       Erro: {resultado.get('error')}")
        return 1
    print(f"       Stats: {resultado['stats']}")

    # 4) Resumo lido direto do padroeira_backup.db.
    print(f"[4/4] Resumo de divergências ({os.path.basename(DB_PATH)}):")
    conn = sqlite3.connect(DB_PATH)
    try:
        linhas = conn.execute(
            """
            SELECT status, COUNT(*) FROM divergencias
            WHERE data_iso LIKE ?
            GROUP BY status
            """,
            (f"20{args.aamm[:2]}-{args.aamm[2:]}-%",),
        ).fetchall()
        if not linhas:
            print("       Nenhuma divergência registrada para este mês.")
        for status, qtd in linhas:
            print(f"       {status}: {qtd} dia(s)")

        precisa_reconf = conn.execute(
            """
            SELECT data_iso, valor_caixa, valor_computado, divergencia FROM divergencias
            WHERE status = 'precisa_reconferencia' AND data_iso LIKE ?
            ORDER BY data_iso
            """,
            (f"20{args.aamm[:2]}-{args.aamm[2:]}-%",),
        ).fetchall()
        if precisa_reconf:
            print("\n       Dias que precisariam de alerta Telegram em produção:")
            for data_iso, caixa, computado, diff in precisa_reconf:
                print(f"         {data_iso}: caixa={caixa} computado={computado} diff={diff}")
    finally:
        conn.close()

    print(
        "\n=== FIM DO SMOKE TEST ===\n"
        "Compare os números acima com a conferência manual desse mês antes de "
        "rodar contra dados de produção.\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
