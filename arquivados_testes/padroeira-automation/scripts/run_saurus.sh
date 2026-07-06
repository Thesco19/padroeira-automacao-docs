#!/bin/bash
# ================================================
# run_saurus.sh - Script Principal Padroeira
# ================================================

echo "🚀 Iniciando Padroeira Automation - $(date)"
echo "============================================"

# Diretórios
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

LOG_FILE="logs/saurus_$(date +%Y%m%d).log"
mkdir -p logs

echo "[$(date)] Iniciando agente_saurus.py" | tee -a "$LOG_FILE"

# Ativa venv
source .venv/bin/activate

# Executa o agente
python core/agente_saurus.py 2>&1 | tee -a "$LOG_FILE"

echo "[$(date)] Execução finalizada." | tee -a "$LOG_FILE"
echo "============================================"
