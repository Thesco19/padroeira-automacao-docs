#!/bin/bash
echo "⚡ Iniciando LiteLLM Proxy na porta 4000..."
litellm --config litellm/config.yaml --port 4000 --host 0.0.0.0
