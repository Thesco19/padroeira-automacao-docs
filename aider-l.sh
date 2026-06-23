#!/bin/bash
source .venv/bin/activate
export OPENAI_API_BASE="http://127.0.0.1:8000"
export OPENAI_API_KEY="sk-teco-lab"
aider --model openai/groq/llama-3.3-70b-versatile
echo "Arquivo aider-l.sh criado com sucesso!"
