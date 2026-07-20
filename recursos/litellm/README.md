# Changelog LiteLLM (2026-07-20)

## Correções e Melhorias
- **Corrigido bug de fallback**: O `model_list` aninhado em `claude-primary`, `claude-fast`, `claude-code`, `claude-code-fast`, `claude-fallback`, e `claude-big` era sintaxe inválida do LiteLLM e nunca funcionou como fallback real. Agora, o fallback é configurado corretamente via `litellm_settings.fallbacks` no `config.yaml`.

- **Troca de primário em `claude-big`**: O primário foi trocado de Groq (banido/403) para NVIDIA.

- **Adicionado provider SambaNova**: Adicionado suporte ao modelo `Meta-Llama-3.1-405B-Instruct` via SambaNova.

- **Migração de API keys**: As API keys foram migradas do `config.yaml` para `os.environ/*`, lidas do `.env` em `/opt/stacks/litellm/.env`.

- **Atualização do `compose.yaml`**: Atualizado com as variáveis de ambiente `GEMINI_API_KEY`, `OPENROUTER_API_KEY`, e `SAMBANOVA_API_KEY`.

## Pendências
- Validar se o container subiu limpo (`docker logs litellm-proxy`).
- Resolver o 404 no endpoint `/mcp` do FastMCP (mcp-lab-universal).

## Em Andamento
- Instalação do plugin `claude-code-setup` via `/plugin marketplace add anthropics/claude-plugins-official`.
