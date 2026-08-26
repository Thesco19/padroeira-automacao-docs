#!/bin/bash
# Start script for Async Reconciliation Architecture V2
# - Resolve o diretório do script (portável, sem hardcode).
# - Trava de execução via flock (impede execuções simultâneas).
# - Redireciona logs para ./logs/reconciliation.log.

set -euo pipefail

# Diretório do próprio script (portável)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Trava de execução (flock) — trava o fd 200 no arquivo /tmp
exec 200>"/tmp/aut_v1_reconciliation.lock"
flock -n 200 || {
    echo "Execução em andamento (lock: /tmp/aut_v1_reconciliation.lock). Abortando."
    exit 1
}

# Garante diretório de logs
mkdir -p "$SCRIPT_DIR/logs"
LOGFILE="$SCRIPT_DIR/logs/reconciliation.log"

# Executa e grava no log + stdout
{
    echo "================================================================"
    echo "$(date '+%Y-%m-%d %H:%M:%S') | Início da Execução"
    echo "================================================================"
    python3 "$SCRIPT_DIR/async_reconciliation_v2.py" "$@"
    exit_status=$?
    echo "----------------------------------------------------------------"
    if [ "$exit_status" -eq 0 ]; then
        echo "✔  Async Reconciliation V2 concluído com sucesso"
    else
        echo "✘  Async Reconciliation V2 falhou (exit status $exit_status)"
    fi
    echo "$(date '+%Y-%m-%d %H:%M:%S') | Fim da Execução"
    echo "================================================================"
} 2>&1 | tee -a "$LOGFILE"
