#!/bin/bash
# 1. Limpa as chaves conflitantes
unset ANTHROPIC_API_KEY

# 2. Configuração do Proxy (Aponte para o LiteLLM)
export ANTHROPIC_BASE_URL="http://127.0.0.1:8000"
export ANTHROPIC_AUTH_TOKEN="sk-teco-lab" # Bate com o que definimos no Docker
# 1. Bypass Estrito de Permissões (Morgana Core)
export CLAUDE_CODE_SKIP_PERMISSIONS=1
export CI=1 # Opcional: use apenas se o layout do Termius quebrar com a interface gráfica do Claude
# 3. Seletor de Modelos (Descomente o que for usar)
export ANTHROPIC_MODEL="mistral/mistral-large-2512"
# export ANTHROPIC_MODEL="groq/llama-3.3-70b-versatile"
# export ANTHROPIC_MODEL="nvidia-deepseek"
# export ANTHROPIC_MODEL="mistral/mistral-small-2506"
# export ANTHROPIC_MODEL="mistral/ministral-8n-2512"

# 4. Flags de debug e ferramentas
export ENABLE_TOOL_SEARCH="auto"

echo "Iniciando Claude Code com modelo: $ANTHROPIC_MODEL"
claude --debug
