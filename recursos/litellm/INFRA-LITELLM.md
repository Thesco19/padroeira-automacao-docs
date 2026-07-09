sudo tee /home/teco/work_out/recursos/litellm/LEIA-ME.md > /dev/null << 'EOF'
# LiteLLM Proxy + Claude Code — Configuração de Referência

## Arquitetura
- `litellm-db`: Postgres 16, guarda estado do LiteLLM
- `litellm-proxy`: proxy que traduz requisições do Claude Code (formato Anthropic)
  para os providers reais (Mistral, NVIDIA NIM, Groq)
- Porta interna do container: 4000
- Porta exposta no host: 8000 (127.0.0.1:8000 -> 4000)
- Motivo de usar 8000: a porta 4000 já é ocupada pelo NoMachine (nxd) no host

## Localização dos arquivos
- Compose: /opt/stacks/litellm/compose.yaml
- Env vars: /opt/stacks/litellm/.env
- Config do LiteLLM: /home/teco/work_out/recursos/litellm/config.yaml
  (montado como bind mount read-only em /app/config.yaml no container)

## Cadeia de fallback (model_name: claude-opus-4-8)
1. Mistral (mistral-large-latest) — tentado primeiro
2. NVIDIA NIM (meta/llama-3.3-70b-instruct) — fallback se Mistral falhar
3. Groq (llama-3.1-8b-instant) — último fallback, rate limit mais folgado

model_name: claude-3-5-sonnet -> Mistral (mistral-large-latest)

## Configurações críticas do litellm_settings
- drop_params: true       -> ignora parâmetros que o provider não suporta
                              (ex: reasoning_effort do Claude Code)
- modify_params: true     -> ajusta valores incompatíveis (ex: max_tokens)
- num_retries: 3          -> tentativas antes de desistir

## Env vars necessárias (devem estar declaradas EXPLICITAMENTE
## na seção `environment:` do compose.yaml, não basta estar no .env)
- GROQ_API_KEY
- MISTRAL_API_KEY
- NVIDIA_API_KEY
- LITELLM_MASTER_KEY (fixo: sk-teco-lab)
- DATABASE_URL (conexão interna com litellm-db)

## Comandos de manutenção
```bash
cd /opt/stacks/litellm

# ver estado
docker compose ps
docker compose logs --tail=50 litellm

# aplicar mudança no config.yaml
docker compose down && docker compose up -d

# confirmar que as env vars chegaram ao container
docker exec litellm-proxy python3 -c "
import os
for k in ['GROQ_API_KEY','MISTRAL_API_KEY','NVIDIA_API_KEY']:
    print(k, 'set:', bool(os.environ.get(k)))
"

# confirmar config carregada de fato
docker exec litellm-proxy cat /app/config.yaml
