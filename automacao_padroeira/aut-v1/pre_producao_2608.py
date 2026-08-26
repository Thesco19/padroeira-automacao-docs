"""
Pré-produção 2608 — sem Telegram (gatilho desativado por design).
Carrega apenas o cache local de fechamentos e roda engine + balancete.
"""
import logging
import os
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from cortex_padroeira_async import CortexPadroeiraAsync
from engine_consolidacao_async import EngineConsolidacaoAsync
from motor_balancete_async import MotorBalanceteAsync

AAMM = "2608"

# 1. Cache Saurus local (sem Playwright, sem extração de portal)
cortex = CortexPadroeiraAsync()
cortex.carregar_cache_fechamentos()
dados_cortex = {
    d: v for d, v in cortex.dados_por_data.items()
    if d.startswith("2026-08")
}
print(f"[pre-prod] fechamentos AGO no cache: {len(dados_cortex)} -> {sorted(dados_cortex)}")

# 2. Engine (bot=None -> Telegram desativado)
engine = EngineConsolidacaoAsync(aamm=AAMM)
res_engine = engine.executar_motor_unificado(dados_cortex=dados_cortex, bot=None, chat_id=None)
print(f"[pre-prod] engine status: {res_engine.get('status')}")
if res_engine.get('status') != 'success':
    print("[pre-prod] engine details:", res_engine)
    sys.exit(1)

# 3. Balancete
bal = MotorBalanceteAsync(aamm=AAMM)
res_bal = bal.injetar_balancete()
print(f"[pre-prod] balancete status: {res_bal.get('status')}")

print("[pre-prod] OK — Movto_diario.2608.xlsx e Pad2608.xlsx gerados (sem Telegram).")
