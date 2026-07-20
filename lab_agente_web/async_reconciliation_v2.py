#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Async Reconciliation Architecture V2 - Cortex Padroeira Integration

Este script foi movido para a pasta **lab-a** e agora serve como o
principal ponto de entrada da automação. Ele coordena a execução
assíncrona dos componentes:

1. CortexPadroeiraAsync – extração de dados e verificação de planilhas.
2. EngineConsolidacaoAsync – consolidação dos dados.
3. MotorBalanceteAsync – injeção do balancete.

Os imports foram atualizados para usar caminhos absolutos, permitindo
que o módulo seja executado a partir da nova estrutura de diretórios.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

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
            "engine_consolidacao": {"status": "pending", "result": None, "error": None, "details": None},
            "motor_balancete": {"status": "pending", "result": None, "error": None, "details": None}
        }
        self.execution_order = [
            "cortex_padroeira",
            "engine_consolidacao",
            "motor_balancete"
        ]

    async def execute_cortex_padroeira(self) -> Dict[str, Any]:
        """Executa o componente Cortex Padroeira (versão assíncrona)."""
        try:
            logger.info("Iniciando componente Cortex Padroeira Async")

            # Importação absoluta dos módulos que permanecem em `lab_agente_web`
            from lab_agente_web.cortex_padroeira_async import CortexPadroeiraAsync

            cortex = CortexPadroeiraAsync()
            dados = cortex.extrair_dados_saurus()
            paridade_ok = cortex.verificar_paridade_planilhas()
            status = cortex.get_status()

            if dados and paridade_ok:
                logger.info("Cortex Padroeira Async concluído com sucesso")
                return {
                    "status": "completed",
                    "result": "Data extraction and verification completed",
                    "error": None,
                    "details": status
                }
            else:
                error_msg = "Data extraction or verification failed"
                logger.error(error_msg)
                return {
                    "status": "error",
                    "result": None,
                    "error": error_msg,
                    "details": status
                }

        except Exception as e:
            error_msg = f"Exception in Cortex Padroeira Async: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "status": "error",
                "result": None,
                "error": error_msg,
                "details": None
            }

    async def execute_engine_consolidacao(self) -> Dict[str, Any]:
        """Executa o componente Engine de Consolidação (versão assíncrona)."""
        try:
            logger.info("Iniciando componente Engine Consolidacao Async")

            from lab_agente_web.engine_consolidacao_async import EngineConsolidacaoAsync

            engine = EngineConsolidacaoAsync()
            result = engine.executar_motor_unificado()

            if result["status"] == "success":
                logger.info("Engine Consolidacao Async concluído com sucesso")
                return {
                    "status": "completed",
                    "result": "Data consolidation completed",
                    "error": None,
                    "details": engine.get_status()
                }
            else:
                error_msg = f"Engine consolidation failed: {result['error']}"
                logger.error(error_msg)
                return {
                    "status": "error",
                    "result": None,
                    "error": error_msg,
                    "details": engine.get_status()
                }

        except Exception as e:
            error_msg = f"Exception in Engine Consolidacao Async: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "status": "error",
                "result": None,
                "error": error_msg,
                "details": None
            }

    async def execute_motor_balancete(self) -> Dict[str, Any]:
        """Executa o componente Motor Balancete (versão assíncrona)."""
        try:
            logger.info("Iniciando componente Motor Balancete Async")

            from lab_agente_web.motor_balancete_async import MotorBalanceteAsync

            motor = MotorBalanceteAsync()
            result = motor.injetar_balancete()

            if result["status"] == "success":
                logger.info("Motor Balancete Async concluído com sucesso")
                return {
                    "status": "completed",
                    "result": "Balance sheet injection completed",
                    "error": None,
                    "details": motor.get_status()
                }
            else:
                error_msg = f"Balance sheet injection failed: {result['error']}"
                logger.error(error_msg)
                return {
                    "status": "error",
                    "result": None,
                    "error": error_msg,
                    "details": motor.get_status()
                }

        except Exception as e:
            error_msg = f"Exception in Motor Balancete Async: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "status": "error",
                "result": None,
                "error": error_msg,
                "details": None
            }

    async def run_reconciliation(self) -> Dict[str, Any]:
        """Orquestra a execução dos três componentes em ordem."""
        logger.info("Iniciando processo de Reconciliação Async V2")

        # 1. Cortex Padroeira
        self.status["cortex_padroeira"] = await self.execute_cortex_padroeira()
        if self.status["cortex_padroeira"]["status"] == "error":
            logger.error("Abortando reconciliação devido a erro no Cortex Padroeira")
            return {"status": "error", "details": self.status}

        # 2. Engine de Consolidação
        self.status["engine_consolidacao"] = await self.execute_engine_consolidacao()
        if self.status["engine_consolidacao"]["status"] == "error":
            logger.error("Abortando reconciliação devido a erro na Engine de Consolidação")
            return {"status": "error", "details": self.status}

        # 3. Motor Balancete
        self.status["motor_balancete"] = await self.execute_motor_balancete()

        # Verificação final
        all_success = all(
            self.status[comp]["status"] == "completed"
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
            self.status[comp]["status"] == "completed"
            for comp in self.execution_order
        ) else "error"
        return {
            "timestamp": datetime.now().isoformat(),
            "status": self.status,
            "overall_status": overall
        }

async def main() -> Dict[str, Any]:
    """Ponto de entrada assíncrono usado pelo script principal."""
    engine = AsyncReconciliationEngine()
    result = await engine.run_reconciliation()
    report = engine.get_status_report()

    logger.info("=== Relatório de Reconciliação ===")
    logger.info(f"Overall Status: {report['overall_status']}")
    for comp, details in report["status"].items():
        logger.info(f"{comp}: {details['status']}")
        if details["error"]:
            logger.error(f"  Erro: {details['error']}")
        if details["details"]:
            logger.info(f"  Detalhes: {details['details']}")

    return result

if __name__ == "__main__":
    asyncio.run(main())
