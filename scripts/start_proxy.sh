#!/bin/bash
export HOST="0.0.0.0"
export PORT=4000
export LITELLM_PORT=4000
export CONFIG_PATH="/home/teco/work_out/recursos/litellm/config.yaml"

echo "⚡ [MORGANA ENGINE] Forçando travamento absoluto na porta $PORT..."

pid=$(lsof -t -i:$PORT)
if [ ! -z "$pid" ]; then
    sudo kill -9 $pid
fi

echo "🚀 Iniciando LiteLLM Proxy..."
exec litellm --config "$CONFIG_PATH" --host $HOST --port $PORT
