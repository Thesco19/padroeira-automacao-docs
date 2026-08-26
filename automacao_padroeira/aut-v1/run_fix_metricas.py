#!/usr/bin/env python3
"""
Runner TARGETED de correção das linhas 3/4/5 (peso buffet, peso sobremesa,
clientes) dos Movto_diario.*.xlsx, a partir do cache LOCAL de fechamentos
já corrigidos (./fechamentos/fechamento_caixa_*.txt).

NÃO executa o Motor Balancete nem o Playwright: apenas o EngineConsolidacaoAsync,
cuja ETAPA 2.5 injeta as métricas Saurus de forma IDEMPOTENTE em todas as colunas
do mês-alvo que tenham dado no cache.

Uso:
    python3 run_fix_metricas.py [--aamm 2606] [--aamms 2601,2602]
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cortex_padroeira_async import CortexPadroeiraAsync
from engine_consolidacao_async import EngineConsolidacaoAsync, DATA_MINIMA_PROCESSAMENTO

AAMM_MINIMO = DATA_MINIMA_PROCESSAMENTO.strftime("%y%m")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--aamm", help="Período único (ex: 2606). Padrão: todos.")
    parser.add_argument("--aamms", help="Lista separada por vírgula (ex: 2603,2604)")
    args = parser.parse_args()

    if args.aamms:
        aamms = [a.strip() for a in args.aamms.split(",") if a.strip()]
    elif args.aamm:
        aamms = [args.aamm]
    else:
        aamms = ["2606", "2607", "2608"]

    aamms = [a for a in aamms if a >= AAMM_MINIMO]
    if not aamms:
        print(f"[escopo] Nenhum período >= {AAMM_MINIMO} para processar.")
        return

    # 1. Carrega o cache local de fechamentos (fonte de verdade corrigida)
    cortex = CortexPadroeiraAsync()
    n = cortex.carregar_cache_fechamentos()
    dados_cortex = cortex.dados_por_data
    print(f"[cache] {n} fechamentos carregados | {len(dados_cortex)} datas no mapa")

    # 2. Executa o engine por período (ETAPA 2 + ETAPA 2.5 idempotente)
    for aamm in aamms:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            f"Movto_diario.{aamm}.xlsx")
        if not os.path.exists(path):
            print(f"[skip] {aamm}: arquivo Movto_diario.{aamm}.xlsx não existe")
            continue
        engine = EngineConsolidacaoAsync(aamm=aamm)
        res = engine.executar_motor_unificado(dados_cortex)
        stats = res.get("stats", {})
        status = res.get("status")
        if status == "success":
            print(f"[OK ] {aamm}: new_cols={stats.get('new_columns',0)} "
                  f"cells={stats.get('cells_modified',0)} "
                  f"metricas_saurus={stats.get('metricas_saurus',0)}")
        else:
            print(f"[ERRO] {aamm}: {res.get('error')}")


if __name__ == "__main__":
    main()
