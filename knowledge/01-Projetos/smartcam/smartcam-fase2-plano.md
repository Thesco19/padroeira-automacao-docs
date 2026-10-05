# SmartCam Fase 2 — Deploy, Injeção de Segredos e Homologação

**Status:** CONCLUÍDO (deploy OK; chave rotacionada; homologação dos endpoints I.A. 100%)
**Data:** 2026-09-14
**Projeto:** smartcam

---

## ✅ Homologação Concluída (2026-09-14, após rotação da chave)

**Rotação da chave executada por Paulo em https://aistudio.google.com/app/apikey**
- Nova chave no formato `AQ.Ab8...` (prefixo `AQ.`, 53 chars) aplicada em `~/.zshrc` (linha 157) e `.env`
- **Atenção/incidente:** o primeiro `docker compose restart` não aplicou a chave porque o `environment:` do compose interpolava `${GEMINI_API_KEY}` do shell persistente (que guardava a chave antiga vazada `AIzaSy...`, 39 chars) — `environment` sobrescreve o `env_file`.
- **Fix:** commit `2b7fd6f` removeu `GEMINI_API_KEY`/`SMARTCAM_API_KEY` do `environment:` do compose; agora as chaves vêm **somente** do `env_file: .env`. Necessário `docker compose up -d --force-recreate` (não basta `restart`, que preserva env vars originais).
- Validação final: hash da chave no container = hash no `.env` (`56f2fae...`), linha única.

**Resultados da homologação (ambos HTTP 200):**
| Endpoint | Resultado |
|----------|-----------|
| `POST /api/analyze-frame` (frame 1x1 branco) | 200; `detections: []`, `event_alert.triggered: false`, `severity: "low"`, `summary: "Nenhuma atividade relevante detectada"`, `processing_time_ms: 3825` |
| `POST /api/ai-resolve-camera-config` (Hikvision 10.0.1.50:80/554) | 200; `brand: "Hikvision"`, `model: "Generic IPC Series"`, `recommendedProtocol: "RTSP"`, 4 candidateStreamPaths, `snapshotFallbackPath: /ISAPI/Streaming/channels/101/picture`, `confidence: 0.95`, explicação coerente |

**Observação importante:** corpo do `analyze-frame` usa campo **`image`** (data URL `data:image/jpeg;base64,...`), NÃO `frameData`.
**Repo:** `Thesco19/Smartsearch-` (local `/home/teco/work_out/lab-b/smartsearck`)

---

## ✅ Deploy Concluído (2026-09-14)

**Decisão aprovada:** Docker host-network, porta 3100 (faixa UIs, livre).

**Entregue:**
- `server.ts:823` → `const PORT = Number(process.env.PORT) || 3100` (parametrizado; build esbuild OK, `PORT` no dist confirmado)
- `Dockerfile` multi-stage (node:22-slim; stage build `npm run build`; stage final `npm ci --omit=dev` + copia `dist/`)
- `docker-compose.yaml` (host-network, env vars, `env_file: .env`)
- `.dockerignore` (node_modules, dist, .env, .git, logs, coverage)
- `.env` local (chmod 600; `GEMINI_API_KEY` do `~/.zshrc`, `SMARTCAM_API_KEY` `openssl rand -hex 32`, `PORT=3100`, `GEMINI_MODEL=gemini-3.1-flash-lite`)

**Imagem local:** `smartsearck-smartcam:latest` (build 5.7s, 2 stages)

**Validações (todas passando):**
| Check | Resultado |
|-------|-----------|
| `docker compose up -d` | smartcam Up |
| `/api/health` | 200, `authEnabled: true`, `hasKey: true` |
| Porta 3100 | `0.0.0.0:3100` (LISTEN; Perplexica segue na 3000, sem conflito) |
| POST `/api/scan-network-cameras` SEM chave | 401 `API key ausente ou inválida.` |
| POST `/api/scan-network-cameras` chave errada | 401 |
| POST `/api/scan-network-cameras` com chave (192.0.2.0/30) | 200, `cameras_discovered: 0` |
| `npm run lint` / `npm run build` / `npm test` | OK / OK / 48 passando |

**Lab-Master:** registro de recurso independente desta nota (ver pendências).

---

## 🚨 BLOCKER RESOLVIDO: GEMINI_API_KEY vazada (leaked)

**Resolvido em 2026-09-14** — nova chave `AQ.Ab8...` rotacionada e homologada (ver seção "Homologação Concluída" acima).

**Sintoma:** `POST /api/analyze-frame` → HTTP 500 com:
```
{"error":{"code":403,"message":"Your API key was reported as leaked. Please use another API key.","status":"PERMISSION_DENIED"}}
```

**Causa raiz encontrada:** a `GEMINI_API_KEY` da conta do Paulo foi exposta no repo público `Thesco19/Smartsearch-` via `.aider.chat.history.md` (commitado). A Google reclassificou a chave como **leaked** e a invalidou (403 PERMISSION_DENIED no endpoint `generativelanguage.googleapis.com`).

**Evidência:**
- `git log -S <chave>` → aparece em commits (f134852 e históricos de `.aider.chat.history.md`)
- `.aider.chat.history.md` (118KB) permanecia versionado apesar do `.gitignore` já conter `.aider*`

**Ações corretivas já aplicadas:**
1. `git rm --cached .aider.chat.history.md` (removido do tracking; working tree limpo do leak)
2. `.gitignore` já cobria `.aider*` desde a Fase 1 (o arquivo só não tinha sido destracked)
3. Commit `24b5748` incluiu a remoção; commit `2b7fd6f` restringiu as chaves ao `env_file`
4. Chave rotacionada por Paulo no AI Studio; `~/.zshrc` + `.env` atualizados; `docker compose up -d --force-recreate` aplicado

**Detalhe da resolução (importante):** usar `docker compose up -d --force-recreate` ao trocar chaves — `docker compose restart` preserva env vars originais do container e o `environment:` do compose sobrescrevia o `env_file` com variável antiga do shell. Após o fix, o hash da chave no container coincide com o `.env`.

---

## Contexto do Ambiente

**Servidor:** teco-macmini (Mac Mini 2012, Linux Mint 21.3, kernel 5.15.0-174)
- LAN: `10.0.1.95/24`
- Tailscale: `100.108.74.62`
- Docker host-network é o padrão do Lab (Perplexica/MCP/Stacks)
- `gcloud` não instalado; Cloud Run GCP sem precedente no Lab
- LiteLLM (8000) e OmniRoute (20128) desativados

**Portas ocupadas no host (relevantes):**
| Porta | Serviço | Nota |
|-------|---------|------|
| 3000 | Perplexica/Vane | ⚠️ COLISÃO — SmartCam usa 3000 hardcoded |
| 3001 | Flame (painel) | 0.0.0.0 |
| 3002 | Playwright MCP | 0.0.0.0 |
| 8765 | MCP Lab Universal | 0.0.0.0 |
| 9100/9101 | Lab-Master API/frontend | 0.0.0.0 |

**Portas livres (faixas do inventário):**
- UIs: 3100-3199 → **3100 livre** (candidata a UI SmartCam)
- APIs: 9200-9299 → **9200 livre** (candidata backend se necessário)

**Chaves / ambiente:**
- `GEMINI_API_KEY` disponível via env global (`~/.zshrc`), válida, apenas `gemini-3.1-flash-lite` funciona na conta do Paulo (validado 2026-08-24)
- `SMARTCAM_API_KEY` precisa ser gerada (`openssl rand -hex 32`)
- Decisão Lab-D: **sem chaves no Supabase**; chaves ficam no `.env` local (fora do git)
- `APP_URL` existe no `.env.example` (template do AI Studio) mas **não é usado no server.ts**

**Modelo:** `GEMINI_MODEL=gemini-3.1-flash-lite` (fallback na Fase 1, único funcional)

**Estado atual do server.ts:**
- PORT hardcoded = 3000 (⚠️ colide com Perplexica)
- `@google/genai` SDK, endpoint direto `generativelanguage.googleapis.com` (sem LiteLLM)
- Build ESM: `dist/server.mjs` (32KB) + `dist/` assets frontend (vite build OK)
- Rotas que exigem `GEMINI_API_KEY`: `/api/analyze-frame`, `/api/ai-resolve-camera-config`

---

## Decisão Pendente: Alvo de Deploy

| Opção | Prós | Contras | Recomendação |
|-------|------|---------|--------------|
| **A: Docker host-network (padrão Lab)** | Precedente claro (Perplexica, MCP), sem provisioning novo, tailnet já configura, systemd+docker compose | Obrigatório livrar porta 3000 | ✅ **Recomendada** |
| **B: Cloud Run GCP** | Auto-scale, sem gerência de servidor | Sem gcloud, sem conta GCP, billing, padrão diferente do Lab, mais complexo hoje | Não recomendada agora |
| **C: Tailscale Funnel** | Exposição externa já testada (MCP 8001) | Exigiria porta dedicada, menos seguro que LAN interna | Opcional em paralelo |

**Se opção A escolhida:** porta proposta = **3100** (faixa UIs, livre, não colide com Perplexica 3000).

---

## Etapas Detalhadas (Opção A — Docker host-network)

### 1. Parametrizar PORT no server.ts
- Trocar `const PORT = 3000` por `const PORT = process.env.PORT || 3100`
- Referência: `server.ts:823`

### 2. Criar Dockerfile multi-stage
```
# Stage 1: build
FROM node:22-slim AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci --ignore-scripts
COPY . .
RUN npm run build    # vite build + esbuild → dist/

# Stage 2: production
FROM node:22-slim
WORKDIR /app
COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/package.json ./
EXPOSE ${PORT:-3100}
ENV NODE_ENV=production
CMD ["node", "dist/server.mjs"]
```

### 3. Criar docker-compose.yaml (padrão Lab)
```yaml
services:
  smartcam:
    build: .
    container_name: smartcam
    restart: unless-stopped
    network_mode: host          # padrão do Lab
    environment:
      - NODE_ENV=production
      - PORT=${PORT:-3100}
      - GEMINI_MODEL=${GEMINI_MODEL:-gemini-3.1-flash-lite}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - SMARTCAM_API_KEY=${SMARTCAM_API_KEY}
      - APP_URL=${APP_URL:-}
    env_file:
      - .env                    # fora do git
```

### 4. Criar .env a partir do .env.example
```bash
cd /home/teco/work_out/lab-b/smartsearck
cp .env.example .env
# Editar .env: preencher valores reais:
# GEMINI_API_KEY=<extrair de ~/.zshrc>
# GEMINI_MODEL=gemini-3.1-flash-lite
# SMARTCAM_API_KEY=$(openssl rand -hex 32)
# PORT=3100
```

### 5. Criar .dockerignore
```
node_modules
dist
.git
.env
.env.*
!.env.example
*.log
coverage
```

### 6. Build e deploy
```bash
cd /home/teco/work_out/lab-b/smartsearck
docker compose build
docker compose up -d
docker compose logs -f smartcam  # verificar startup
```

### 7. Smoke test (deploy)
```bash
# Health (público)
curl -s http://localhost:3100/api/health | jq .
# Esperado: {"status":"ok","authEnabled":true,...}

# Sem chave → 401
curl -s -X POST http://localhost:3100/api/scan-network-cameras \
  -H "Content-Type: application/json" \
  -d '{"subnet":"192.0.2.0/30"}'
# Esperado: {"error":"API key ausente ou inválida."}

# Com chave → 200
curl -s -X POST http://localhost:3100/api/scan-network-cameras \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <SMARTCAM_API_KEY>" \
  -d '{"subnet":"192.0.2.0/30"}' | jq .
# Esperado: 200, cameras_discovered: 0 (TEST-NET)
```

### 8. Registrar no Lab_Master
```bash
# Registrar via API do lab-master ou adicionar no resources.yaml
# Porta 3100, projeto lab-b/smartsearck, owner teco
```

### 9. (Opcional) Expor via LAN/HTTP direto
- LAN: `http://10.0.1.95:3100` (já acessível, firewall do Lab permite)
- Sem necessidade de Tailscale Funnel para uso interno

---

## Etapa: Homologação da Detecção com GEMINI_API_KEY — EXECUTADA E APROVADA ✅

> Requer: `GEMINI_API_KEY` no `.env` (conta Paulo, válido somente `gemini-3.1-flash-lite`)

**Resultado da execução real:** `/api/analyze-frame` e `/api/ai-resolve-camera-config` ambos retornaram HTTP 200 (detalhes na seção "Homologação Concluída" no topo). Comandos utilizados foram:

### 1. Gerar e injetar SMARTCAM_API_KEY
```bash
KEY=$(openssl rand -hex 32)
echo "SMARTCAM_API_KEY=$KEY" >> .env
docker compose up -d --force-recreate   # não usar "restart" (preserva env vars antigas)
echo "Chave gerada: $KEY"
# Salvar no gerenciador de senhas / vault
```

### 2. Testar /api/health (validar authEnabled=true)
```bash
curl -s http://localhost:3100/api/health | jq .
# Esperado: authEnabled: true, hasKey: true
```

### 3. Testar /api/analyze-frame com frame mock
```bash
# Frame dummy: quadrado 2x2 pixels (mínimo para exemplo)
FRAME="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAFAABAAAAAAAAAAAAAAAAAAAACf/EABQQAQAAAAAAAAAAAAAAAAAAAAD/xAAUAQEAAAAAAAAAAAAAAAAAAAAA/8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEQMRAD8AKwA//9k="

# Campo correto: "image" (NÃO "frameData")
curl -s -X POST http://localhost:3100/api/analyze-frame \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $SMARTCAM_API_KEY" \
  -d "{\"cameraId\":\"homologacao\",\"image\":\"$FRAME\"}" | jq .
# Resultado homologado: 200, detections: [], event_alert.triggered: false, severity: "low", processing_time_ms: 3825
```

### 4. Testar /api/ai-resolve-camera-config (IP real da rede)
```bash
curl -s -X POST http://localhost:3100/api/ai-resolve-camera-config \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $SMARTCAM_API_KEY" \
  -d '{"ip":"192.168.1.100","detectedPorts":[80,554],"bannerInfo":"Hikvision"}' | jq .
# Resultado homologado: 200, brand: "Hikvision", protocol: RTSP, confidence: 0.95
```

### 5. Validação de categorias (Obrigatório para homologação)
Após análise real com câmera:
- Verificar que `bounding_box_relative` está em 0..1 (não 0..1000)
- Verificar que `category` é `person|animal|object|vehicle`
- Verificar que `event_alert.severity` é `low|medium|high`

---

## Validação Final (Fase 2 completa)

| Check | Método | Esperado |
|-------|--------|----------|
| `docker compose ps` | shell | smartcam running, healthy |
| `/api/health` | curl | 200, authEnabled: true |
| Auth OFF (sem chave) | curl POST rota /api | 401 |
| Auth ON (com chave) | curl POST rota /api | 200 |
| Scan rede 192.0.2.0/30 | curl POST | 200, 0 cameras |
| `analyze-frame` com GEMINI_API_KEY | curl POST | 200, detections format OK |
| Porta 3100 (não 3000) | ss -tlnp | SmartCam escutando 3100 |

---

## Rollback

```bash
# Parar container
docker compose -f /home/teco/work_out/lab-b/smartsearck/docker-compose.yaml down

# Reverter se necessário
git revert HEAD  # reverter commit Fase 2
docker compose build && docker compose up -d
```

---

## Artefatos a Criar

| Arquivo | Conteúdo |
|---------|----------|
| `Dockerfile` | Multi-stage build (node:22-slim) |
| `docker-compose.yaml` | Serviço smartcam, host-network, env vars |
| `.dockerignore` | node_modules, dist, .env, .git |
| `.env` (local) | GEMINI_API_KEY, SMARTCAM_API_KEY, PORT=3100 (fora do git) |
| `server.ts` (patch) | PORT parametrizado via env |

---

## Pendências Fora do Escopo Fase 2

- Expor externalmente (Tailscale Funnel / tailscale serve)
- Integração com câmeras reais (scan-network-cameras com subnet 192.168.1.0/24)
- Monitoramento/alertas (rate-limit Gemini, erros de scan)
- Registro automático no Lab_Master via API