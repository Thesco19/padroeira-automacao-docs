# Incidente — Perplexica parou de se conectar às APIs (12/09/2026)

**Status**: ✅ RESOLVIDO (12/09/2026 ~03:10 UTC) — app UP, modelo novo validado, rate limit ativo
**Data**: 2026-09-12 02:47 UTC (11/09 23:47 -03)
**Componente**: `perplexica` (docker_stack, svc `vane`, container `perplexica`, `network_mode: host`, porta 8081)
**Precisão do diagnóstico**: o desligamento (01:51 UTC) foi **consequência**, não causa — o app já falhava a conexão com as APIs antes.

## Causa raiz (verificada em log)

- Provider **"OpenRouter (free)"** configurado com chatModel **`minimax/minimax-m3:free`** (`/opt/stacks/perplexica/data/config.json`).
- O OpenRouter responde **HTTP 404**: *"This model is unavailable for free. The paid version is available now - use this slug instead: minimax/minimax-m3"*.
- O search agent (`chunks/936.js` → `generateObject` → `chat/route.js`) usa esse modelo para gerar resposta/classificação; com 404, **toda busca falha** → app não responde → percepção de "não se conecta às APIs".
- Conexão TCP com `openrouter.ai` **funciona** (resposta estruturada, headers Cloudflare, `cf-ray ... GRU`) — não é problema de rede nem de chave (404 ≠ 401).

## Timeline (12/09 UTC)

| hora | evento |
|---|---|
| 01:19 | `POST /api/resources/perplexica/start` ×2 (API lab-master) |
| 01:20 | stack perplexica UP (vane + 3 sidecars) |
| 01:22 | `config.json` reescrito (provider "OpenRouter (free)" minimax) — mtime 22:22 -03 |
| 01:47–01:48 | buscas falham com **404 minimax/minimax-m3:free** (últimos erros no log) |
| 01:51 | usuário desliga o stack (vane 143, sidecars 0) |
| 01:52–01:53 | shutdown em massa do ecossistema + parada de apps host via API |
| 01:59 | lab-master desligado limpo (exit 0) |
| ~03:00 | remediação: config trocado p/ nemotron free + rate limiter + rebuild |
| ~03:10 | stack religado, UI 200, modelo validado (HTTP 200, custo 0) |

## Evidências

- `docker logs perplexica`: `Search agent error: Error: 404 ... minimax-minimax-m3` em 01:47:30 e 01:48:09 UTC.
- `data/config.json`: `"key": "minimax/minimax-m3:free"` em DOIS providers OpenRouter ("free" e "free 2"), com duas keys distintas (sk-or-v1-...e88a5408 e sk-or-v1-...43ce768).
- Provider **Gemini** (`gemini-provider-001`) continua configurado com key própria e `models/gemini-3.1-flash-lite` — era o provider funcional (nota 06/09).

## Resolução aplicada (12/09/2026)

1. **Modelo trocado** nos dois providers OpenRouter free: `minimax/minimax-m3:free` → **`nvidia/nemotron-3-super-120b-a12b:free`** (262K ctx, structured_outputs; testado 200 OK com ambas as keys).
2. **Gemini** restrito a **`models/gemini-3.1-flash-lite`** (removidos `gemini-2.5-flash` e `gemini-3.1-flash-lite-preview`).
3. **Rate limiter** adicionado ao código (`src/lib/rateLimit.ts`): token bucket por chave, **20 req/min** e **50 req/dia** (janelas alinhadas ao tier free do OpenRouter; `RATE_LIMIT_ENABLED=false` desativa). Aplicado em `generateText`, `streamText`, `generateObject`, `streamObject` de `openaiLLM.ts`. Env no compose: `RATE_LIMIT_PER_MIN`, `RATE_LIMIT_PER_DAY`.
4. **Rebuild** da imagem `vane:local` (Next standalone + patches) e `docker compose up -d` — todos os 4 serviços + flaresolverr UP.

### Validação

- `curl http://localhost:8081/` → **200**; log: `Next.js 16.2.2 ... ✓ Ready`.
- `POST https://openrouter.ai/api/v1/chat/completions` com a key do `config.json` e `nvidia/nemotron-3-super-120b-a12b:free` → **HTTP 200**, `cost: 0`.
- `/api/config` (efetivo): nenhum `minimax`; `nvidia/nemotron-3-super-120b-a12b:free` presente nos 2 providers free; Gemini com lista viva (o merge com `getActiveProviders()` mostra a lista completa do provedor, mas o chatModel configurado é só `gemini-3.1-flash-lite`).
- Rate limiter presente no bundle do container (`.next/server/chunks/743.js`, `485.js`); env `rpm=20 rpd=50`.

## Notas de operação

- `DATA_DIR` não é setado → `configPath = process.cwd()/data/config.json = /home/vane/data/config.json` (mount `./data`). O path `/data/config.json` visto no código é resolvido relativo ao cwd.
- A lista de modelos exibida pela UI vem do merge com `ModelRegistry.getActiveProviders()` (lista ao vivo da API do provedor), não só do `config.json`.
- Rate limits free OpenRouter: 50 req/dia sem créditos, 1.000/dia com ≥US$10 em créditos (docs oficiais). Ajustar `RATE_LIMIT_PER_DAY` se comprar créditos.

## Referência

- Nota relacionada: [[Resolucao Bugs Gemini Flash Lite]] (06/09/2026) — Gemini era o provider funcional.
- `.remember/today-2026-09-11.md` — registro diário com correção de causa raiz e resolução.
