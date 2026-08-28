#!/usr/bin/env bash
#
# start_async_reconciliation.sh — sobe o bot de reconciliação (modo escuta).
#
# O bot escuta comandos Telegram (/reconciliar, /fechar, /amostra) e orquestra
# o pipeline (Cortex -> Engine -> Balancete) sob demanda. Logs em tempo real
# em pad_prod_test/logs/reconciliation.log (zerado a cada start).
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Trava para evitar múltiplas instâncias do bot.
LOCK="$SCRIPT_DIR/.bot_reconciliation.lock"
exec 9>"$LOCK"
if ! flock -n 9; then
    echo "[start] Já existe uma instância do bot rodando (lock: $LOCK)." >&2
    exit 1
fi

mkdir -p "$SCRIPT_DIR/logs"

LOGFILE="$SCRIPT_DIR/logs/reconciliation.log"
echo "[start] $(date '+%Y-%m-%d %H:%M:%S') — iniciando bot_reconciliation.py (modo escuta)"
echo "[start] Logs: $LOGFILE"

# O próprio bot zera o reconciliation.log (FileHandler mode="w"); aqui apenas
# registramos o início do processo antes de redirecionar o stdout.
{
    echo "[start] $(date '+%Y-%m-%d %H:%M:%S') — PID $$ — python3 bot_reconciliation.py"
} >> "$LOGFILE"

python3 "$SCRIPT_DIR/bot_reconciliation.py" 2>&1 | tee -a "$LOGFILE"

echo "[start] $(date '+%Y-%m-%d %H:%M:%S') — bot encerrado." >> "$LOGFILE"
