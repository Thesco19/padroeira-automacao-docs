#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Async Reconciliation Architecture V2 - Cortex Padroeira Integration

Ponto de entrada principal da automação. Coordena os componentes:

1. CortexPadroeiraAsync  – preflight: extração de dados e verificação de paridade.
2. EngineConsolidacaoAsync – consolidação do Diário Mensal (por período AAMM).
3. MotorBalanceteAsync   – injeção do Balancete Pad (por período AAMM).

Todos os imports são locais (mesmo diretório) e todos os caminhos são
resolvidos a partir de BASE_DIR, eliminando dependências de `lab_agente_web`
e de caminhos hardcoded.

Suporte a períodos defasados (AAMM):
  - Por padrão, varre `Movto_cx2.xlsx` e processa TODOS os períodos AAMM
    presentes (backlog).
  - Pode-se restringir a um período via `--aamm 2606`.
"""

import asyncio
import argparse
import logging
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

from openpyxl import load_workbook

from cortex_padroeira_async import CortexPadroeiraAsync, _iterar_cabecalho
from engine_consolidacao_async import EngineConsolidacaoAsync, DATA_MINIMA_PROCESSAMENTO
from motor_balancete_async import MotorBalanceteAsync

# Caminho dinâmico relativo a este script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAIXA2_FILE = os.path.join(BASE_DIR, "Movto_cx2.xlsx")

# AAMM mínimo correspondente a DATA_MINIMA_PROCESSAMENTO (Jun/2026 = "2606")
AAMM_MINIMO = DATA_MINIMA_PROCESSAMENTO.strftime("%y%m")

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AsyncReconciliationV2")


class AsyncReconciliationEngine:
    """
    Engine de Reconciliação Assíncrona V2 para Cortex Padroeira.
    """

    def __init__(self):
        self.status = {
            "cortex_padroeira": {"status": "pending", "result": None, "error": None, "details": None},
            "engine_consolidacao": {"status": "pending", "result": None, "error": None, "details": None, "aamms": []},
            "motor_balancete": {"status": "pending", "result": None, "error": None, "details": None, "aamms": []}
        }
        self.execution_order = [
            "cortex_padroeira",
            "engine_consolidacao",
            "motor_balancete"
        ]

    # ------------------------------------------------------------------
    # Detecção de backlog AAMM a partir do Movto_cx2.xlsx
    # ------------------------------------------------------------------
    def detectar_aamms(self, aamm_especifico: Optional[str] = None) -> List[str]:
        """
        Varre a linha 1 do Movto_cx2.xlsx e retorna todos os períodos AAMM
        presentes (formato %y%m), em ordem crescente. Se `aamm_especifico`
        for informado, retorna apenas ele.
        """
        if aamm_especifico:
            if aamm_especifico < AAMM_MINIMO:
                logger.warning(
                    f"[escopo] Período {aamm_especifico} é anterior a {AAMM_MINIMO} — ignorado."
                )
                return []
            return [aamm_especifico]

        if not os.path.exists(CAIXA2_FILE):
            logger.error(f"Movto_cx2.xlsx não encontrado em {CAIXA2_FILE}")
            return []

        # Parada rápida (2 colunas consecutivas vazias) evita varrer as ~16k
        # colunas finais. Sem read_only para permitir acesso célula a célula.
        aamms = set()
        wb = load_workbook(CAIXA2_FILE, data_only=True)
        try:
            ws = wb.active
            for _, v in _iterar_cabecalho(ws, inicio=1):
                if isinstance(v, datetime):
                    aamms.add(v.strftime("%y%m"))
        finally:
            wb.close()

        aamms_filtrados = [a for a in sorted(aamms) if a >= AAMM_MINIMO]
        if len(aamms_filtrados) < len(aamms):
            ignorados = sorted(aamms - set(aamms_filtrados))
            logger.info(f"[escopo] {len(ignorados)} período(s) anterior a {AAMM_MINIMO} ignorado(s): {ignorados}")
        return aamms_filtrados

    # ------------------------------------------------------------------
    # Componentes
    # ------------------------------------------------------------------
    async def execute_cortex_padroeira(self, aamms: List[str]) -> Dict[str, Any]:
        """
        Executa o preflight Cortex Padroeira (extração + paridade) para TODOS os
        períodos AAMM detectados.

        Fluxo multi-data (por data pendente):
          1. Cache local  ./fechamentos/fechamento_caixa_{dt}.txt
          2. Playwright   pdv_saurus_extractor (se disponível e com seletores)
          3. Fallback     fechamento_caixa.txt estático (com [AVISO])

        A lista `pendentes` é acumulada por período e, ao final, extraída uma
        única vez em `extrair_todos_pendentes()`.
        """
        try:
            logger.info("Iniciando componente Cortex Padroeira Async (preflight multi-data)")

            cortex = CortexPadroeiraAsync()
            dados = cortex.extrair_dados_saurus()  # legado (status / compat)

            # 0. Cache local SEMPRE: popula dados_por_data com todos os fechamentos
            # existentes, independente das datas pendentes do calendário. Isso é o
            # que garante a injeção das linhas 3/4/5 mesmo com colunas já presentes.
            cortex.carregar_cache_fechamentos()

            # 1. Paridade por período; acumula pendentes apenas do AAMM em análise
            todos_pendentes: set = set()
            paridade_ok = True
            for aamm in aamms:
                ok = cortex.verificar_paridade_planilhas(aamm)
                paridade_ok = paridade_ok and ok
                todos_pendentes.update(cortex.pendentes)
            cortex.pendentes = sorted(todos_pendentes)

            # 2. Extração multi-data: roda apenas para datas pendentes SEM arquivo
            # local. Datas já presentes no cache foram carregadas no passo 0.
            pendentes_sem_cache = [
                dt for dt in cortex.pendentes
                if not os.path.exists(
                    os.path.join(cortex.pasta_fechamentos, f"fechamento_caixa_{dt}.txt")
                )
            ]
            extracao: Dict[str, Optional[str]] = {}
            if pendentes_sem_cache:
                logger.info(f"[cortex] Datas pendentes sem cache local a extrair: {len(pendentes_sem_cache)}")
                cortex.pendentes = pendentes_sem_cache
                extracao = await cortex.extrair_todos_pendentes(
                    headless=cortex._headless_config()
                )
                extraidas = [d for d, p in extracao.items() if p]
                logger.info(f"[cortex] Extração concluída: {len(extraidas)}/{len(extracao)} datas")
            else:
                logger.info(
                    f"[cortex] Nenhuma data pendente sem cache local — "
                    f"usando cache ({len(cortex.dados_por_data)} fechamento(s))."
                )

            status = cortex.get_status()
            status["extração_pendentes"] = extracao

            if dados and paridade_ok:
                logger.info("Cortex Padroeira Async concluído com sucesso")
                return {
                    "status": "completed",
                    "result": "Data extraction and verification completed",
                    "error": None,
                    "details": status
                }
            else:
                # Preflight não é fatal: avisa, mas permite que os motores rodem
                # (a ausência de fechamento_caixa.txt, por exemplo, é apenas de entrada).
                aviso = "Dados de fechamento_caixa.txt ausentes ou paridade pendente"
                logger.warning(aviso)
                return {
                    "status": "warning",
                    "result": None,
                    "error": aviso,
                    "details": status
                }

        except Exception as e:
            error_msg = f"Exception in Cortex Padroeira Async: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "status": "warning",
                "result": None,
                "error": error_msg,
                "details": None
            }

    async def execute_engine_consolidacao(self, aamm: str, dados_cortex: Optional[Dict[str, Dict[str, str]]] = None) -> Dict[str, Any]:
        """Executa o Engine de Consolidação para um período AAMM."""
        try:
            logger.info(f"Iniciando Engine Consolidacao Async para {aamm}")
            engine = EngineConsolidacaoAsync(aamm=aamm)
            result = engine.executar_motor_unificado(dados_cortex)

            if result["status"] == "success":
                logger.info(f"Engine Consolidacao Async ({aamm}) concluído com sucesso")
                return {
                    "status": "completed",
                    "result": "Data consolidation completed",
                    "error": None,
                    "details": engine.get_status()
                }
            else:
                error_msg = f"[{aamm}] Engine consolidation failed: {result.get('error')}"
                logger.error(error_msg)
                return {
                    "status": "error",
                    "result": None,
                    "error": error_msg,
                    "details": engine.get_status()
                }

        except Exception as e:
            error_msg = f"[{aamm}] Exception in Engine Consolidacao Async: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "status": "error",
                "result": None,
                "error": error_msg,
                "details": None
            }

    async def execute_motor_balancete(self, aamm: str) -> Dict[str, Any]:
        """Executa o Motor Balancete para um período AAMM."""
        try:
            logger.info(f"Iniciando Motor Balancete Async para {aamm}")
            motor = MotorBalanceteAsync(aamm=aamm)
            result = motor.injetar_balancete()

            if result["status"] == "success":
                logger.info(f"Motor Balancete Async ({aamm}) concluído com sucesso")
                return {
                    "status": "completed",
                    "result": "Balance sheet injection completed",
                    "error": None,
                    "details": motor.get_status()
                }
            else:
                error_msg = f"[{aamm}] Balance sheet injection failed: {result.get('error')}"
                logger.error(error_msg)
                return {
                    "status": "error",
                    "result": None,
                    "error": error_msg,
                    "details": motor.get_status()
                }

        except Exception as e:
            error_msg = f"[{aamm}] Exception in Motor Balancete Async: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "status": "error",
                "result": None,
                "error": error_msg,
                "details": None
            }

    # ------------------------------------------------------------------
    # Orquestração
    # ------------------------------------------------------------------
    async def run_reconciliation(self, aamm: Optional[str] = None) -> Dict[str, Any]:
        """
        Orquestra a execução dos componentes.

        - O Cortex é um preflight não-fatal (avisa, mas não aborta) que agora
          também extrai as datas pendentes (cache -> playwright -> fallback).
        - O Engine e o Motor rodam para cada período AAMM detectado no backlog
          (ou apenas para o período informado em `aamm`).
        """
        logger.info("Iniciando processo de Reconciliação Async V2")

        # 1. Detecta períodos AAMM a processar (backlog multi-período)
        aamms = self.detectar_aamms(aamm)
        if not aamms:
            logger.error("Nenhum período AAMM detectado no Movto_cx2.xlsx")
            return {"status": "error", "details": self.status, "reason": "no_aamms"}

        logger.info(f"Períodos AAMM a processar: {aamms}")

        # 2. Preflight Cortex multi-data (não-fatal) para TODOS os períodos
        self.status["cortex_padroeira"] = await self.execute_cortex_padroeira(aamms)
        logger.info(
            f"Cortex preflight: {self.status['cortex_padroeira']['status']}"
            f" - {self.status['cortex_padroeira'].get('error')}"
        )

        # Dados Saurus por data (peso & clientes) extraídos no preflight, para o engine injetar.
        detalhes_cortex = self.status["cortex_padroeira"].get("details") or {}
        dados_cortex = detalhes_cortex.get("dados_por_data") or {}

        # 3. Engine de Consolidação para cada período
        engine_results = []
        for per in aamms:
            res = await self.execute_engine_consolidacao(per, dados_cortex)
            engine_results.append({"aamm": per, **res})

        self.status["engine_consolidacao"]["aamms"] = aamms
        self.status["engine_consolidacao"]["status"] = (
            "completed" if all(r["status"] == "completed" for r in engine_results)
            else "error"
        )
        self.status["engine_consolidacao"]["result"] = engine_results
        self.status["engine_consolidacao"]["details"] = [r["details"] for r in engine_results]

        # 4. Motor Balancete para cada período
        motor_results = []
        for per in aamms:
            res = await self.execute_motor_balancete(per)
            motor_results.append({"aamm": per, **res})

        self.status["motor_balancete"]["aamms"] = aamms
        self.status["motor_balancete"]["status"] = (
            "completed" if all(r["status"] == "completed" for r in motor_results)
            else "error"
        )
        self.status["motor_balancete"]["result"] = motor_results
        self.status["motor_balancete"]["details"] = [r["details"] for r in motor_results]

        # 5. Verificação final
        all_success = all(
            self.status[comp]["status"] in ("completed", "warning")
            for comp in self.execution_order
        )

        if all_success:
            logger.info("Reconciliação Async V2 concluída com sucesso")
            return {"status": "success", "details": self.status}
        else:
            logger.error("Reconciliação Async V2 concluída com erros")
            return {"status": "error", "details": self.status}

    def get_status_report(self) -> Dict[str, Any]:
        """Gera um relatório resumido do status da reconciliação."""
        overall = "success" if all(
            self.status[comp]["status"] in ("completed", "warning")
            for comp in self.execution_order
        ) else "error"
        return {
            "timestamp": datetime.now().isoformat(),
            "status": self.status,
            "overall_status": overall
        }


async def main() -> Dict[str, Any]:
    """Ponto de entrada assíncrono usado pelo script principal."""
    parser = argparse.ArgumentParser(description="Reconciliação Async V2 - Padroeira")
    parser.add_argument(
        "--aamm",
        help="Período específico (AAMM, ex: 2606). Se omitido, processa todo o backlog do Movto_cx2.",
        default=None,
    )
    parser.add_argument(
        "--all-pending",
        action="store_true",
        help="Processa explicitamente todo o backlog AAMM detectado no Movto_cx2.xlsx (padrão).",
    )
    args = parser.parse_args()

    engine = AsyncReconciliationEngine()
    # --all-pending é explícito; --aamm restringe a um período. Ambos convergem
    # no mesmo comportamento: detectar_aamms(aamm) retorna [aamm] ou todo o backlog.
    result = await engine.run_reconciliation(args.aamm)
    report = engine.get_status_report()

    logger.info("=== Relatório de Reconciliação ===")
    logger.info(f"Overall Status: {report['overall_status']}")
    for comp, details in report["status"].items():
        logger.info(f"{comp}: {details['status']}")
        if details.get("aamms"):
            logger.info(f"  AAMMs: {details['aamms']}")
        if details.get("error"):
            logger.error(f"  Erro: {details['error']}")

    return result


if __name__ == "__main__":
    asyncio.run(main())
