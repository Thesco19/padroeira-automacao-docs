"""
Pre-producao 2608 - sem Telegram (gatilho desativado por design).
Carrega apenas o cache local de fechamentos e roda engine + balancete.
"""
import logging
import os
import sys
import importlib.util

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

WORK = os.path.dirname(os.path.abspath(__file__))          # pad_prod_test
PARENT = os.path.dirname(WORK)                              # aut-v1 (tem backup_padroeira)
sys.path.insert(0, PARENT)

def _carregar(modulo, caminho):
    spec = importlib.util.spec_from_file_location(modulo, caminho)
    m = importlib.util.module_from_spec(spec)
    sys.modules[modulo] = m
    spec.loader.exec_module(m)
    return m

cortex_mod = _carregar("cortex_padroeira_async", os.path.join(WORK, "cortex_padroeira_async.py"))
engine_mod = _carregar("engine_consolidacao_async", os.path.join(WORK, "engine_consolidacao_async.py"))
bal_mod    = _carregar("motor_balancete_async", os.path.join(WORK, "motor_balancete_async.py"))

# forca BASE_DIR do engine para a pasta de trabalho
engine_mod.BASE_DIR = WORK

AAMM = "2608"

cortex = cortex_mod.CortexPadroeiraAsync()
cortex.carregar_cache_fechamentos()
dados_cortex = {d: v for d, v in cortex.dados_por_data.items() if d.startswith("2026-08")}
print(f"[pre-prod] fechamentos AGO no cache: {len(dados_cortex)} -> {sorted(dados_cortex)}")

engine = engine_mod.EngineConsolidacaoAsync(aamm=AAMM)
res_engine = engine.executar_motor_unificado(dados_cortex=dados_cortex, bot=None, chat_id=None)
print(f"[pre-prod] engine status: {res_engine.get('status')}")
if res_engine.get('status') != 'success':
    print("[pre-prod] engine details:", res_engine)
    sys.exit(1)

bal = bal_mod.MotorBalanceteAsync(aamm=AAMM)
res_bal = bal.injetar_balancete()
print(f"[pre-prod] balancete status: {res_bal.get('status')}")

print("[pre-prod] OK - Movto_diario.2608.xlsx e Pad2608.xlsx gerados (sem Telegram).")

