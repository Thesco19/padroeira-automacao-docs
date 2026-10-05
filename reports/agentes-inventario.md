# Inventário de Agentes, Configs MCP e Diagnóstico de Compatibilidade

> Gerado: 2026-09-18 · Missão: Unificação de Governança Multi-Agente + Saneamento de MCP
> Método: Fase 1 (inventário read-only) + Fase 2 (matriz de compatibilidade e causa raiz Playwright).
> Nenhum arquivo de config/instrução foi modificado nesta etapa.
> Segredos lidos em arquivos de config **não** são reproduzidos aqui.

---

## 1. Hosts

| Host | Tailscale | Estado | Observação |
|---|---|---|---|
| `teco-macmini` | `100.108.74.62` / `teco-macmini.tail9c8d52.ts.net` | **online** (host atual) | Servidor central headless. Funnel habilitado (8443). |
| `teco-vaio` | `100.78.249.102` | **offline** (último visto 10d atrás) | SSH `teco@100.78.249.102` — timeout na tentativa de conexão (2026-09-18). Configs locais do VAIO não estão acessíveis ao vivo; a fonte disponível é o inventário `knowledge/03-Infraestrutura/Inventario-Vaio-teco-vaio.md`. |

**Impacto no escopo:** o saneamento presencial cobre o teco-macmini. Para o teco-vaio será entregue um checklist/indicações no relatório de resultado, para aplicação quando a estação voltar online — sem duplicação de conteúdo.

---

## 2. Inventário por agente (teco-macmini)

### 2.1 Claude Code (v2.1.275)

| Arquivo | Bytes | mtime | Conteúdo (resumo) |
|---|---|---|---|
| `~/.claude.json` | 66.659 | 2026-09-17 20:32 | Estado global: `mcpServers` globais (13) + servers por projeto + permissões aceitas |
| `~/.claude/settings.json` | 1.775 | 2026-09-15 12:40 | Env: proxy `127.0.0.1:10100`, tokens, modelo `policy/free-smart-router`, plugins |
| `~/.claude/CLAUDE.md` | 111 | 2026-08-24 18:57 | Regra global única: responder sempre em pt-BR |
| `~/work_out/CLAUDE.md` | 1.698 | 2026-08-29 21:48 | **Conteúdo do projeto Padroeira/aut-v1** gravado na raiz do lab (fórmulas Excel, estrutura aut-v1) |
| `~/work_out/.claude/mcp.json` | 436 | 2026-08-14 00:39 | MCP por projeto: obsv, mcp-lab-universal (SSE), supabase |
| `~/work_out/.claude/settings.local.json` | 15.976 | 2026-09-05 23:50 | Permissões allow (bash/docker/mcp) + `enabledMcpjsonServers` |
| `~/.claude/agents/*.md` (6) | ~1.3KB cada | 2026-09-18 | Subagentes auto-gerados pelo opencodex (róster `ocx-*`) — não são governança |

**MCP ativos (global):** `duckduckgo-search`, `memory`, `github`, `obsv`, `mcp-lab-universal`, `filesystem`, `sequential-thinking`, `notebooklm`, `fetch`, `docker`, `playwright`, `supabase`. Por projeto (work_out): idem herdado do `.claude/mcp.json`. Projeto `~`: `github`, `hexstrike-ai`, `teco-mcp` (alias SSE 8765).

### 2.2 OpenCode (v1.18.3)

| Arquivo | Bytes | mtime | Conteúdo (resumo) |
|---|---|---|---|
| `~/.config/opencode/opencode.json` | 9.308 | 2026-09-17 22:39 | Providers (groq/cerebras/mistral/…/ollama local) + MCP (14) |
| `~/.config/opencode/opencode.jsonc` | 50 | 2026-09-09 | Apenas `$schema` (vazio) |
| `~/work_out/AGENTS.md` | 742 | 2026-08-17 08:57 | Governança genérica curta (papel/processo/comandos) |
| `~/work_out/OPENCODE.md` | 1.698 | 2026-08-29 21:48 | Idêntico ao CLAUDE.md da raiz (conteúdo Padroeira) |

**MCP ativos:** `obsv`, `lab-universal` (SSE 8765), `ddg-search`, `searxng-local`, `github`, `filesystem`, `playwright`, `sequential-thinking`, `memory`, `notebooklm`, `supabase`, `context7`, `computer-control`, `hexstrike-ai`.

### 2.3 Codex CLI (v0.149.0)

| Arquivo | Bytes | mtime | Conteúdo (resumo) |
|---|---|---|---|
| `~/.codex/config.toml` | 2.912 | 2026-09-18 10:54 | Modelos/proxy 10100 + `mcp_servers` (13) + plugins desabilitados |
| `~/.codex/rules/default.rules` | 513 | 2026-09-03 22:28 | Permissão de curl/docker exec (aprovação) |
| `~/work_out/CODEX.md` | 1.698 | 2026-08-29 21:48 | Idêntico ao CLAUDE.md da raiz (conteúdo Padroeira) |
| `~/.codex/AGENTS.md` | — | — | Não existe |

`codex mcp list` reconhece **todos os 13 servers como enabled**, incluindo `lab-universal` via URL `http://127.0.0.1:8765/mcp` (transporte streamable/remote). Coluna "Auth" = Unsupported (sem OAuth — ok para servers locais).

**MCP ativos:** `github`, `filesystem`, `memory`, `sequential-thinking`, `playwright`, `context7`, `supabase`, `obsv`, `lab-universal` (`/mcp`), `ddg-search`, `notebooklm`, `computer-control`, `docker`.

### 2.4 Gemini CLI (v0.60.0)

| Arquivo | Bytes | mtime | Conteúdo (resumo) |
|---|---|---|---|
| `~/.gemini/config/mcp_config.json` | 131 | 2026-08-14 00:39 | Contém `obsv` stdio — **ver achado 2.4A** |
| `~/.gemini/config/config.json` | 80 | 2026-08-12 | userSettings: remoteControlHostname |
| `~/.gemini/settings.json` | 82 | 2026-08-21 | security.auth: gemini-api-key |
| `~/work_out/GEMINI.md` | 4.049 | 2026-08-04 | Corpo genérico "Consultor Técnico/Revisor" (254 linhas), duplicado de AIDER.md |
| `~/.gemini/mcp_config.json` | — | — | **Não existe** (ver abaixo) |

**Achado 2.4A (config morta):** o comando oficial `gemini mcp list` retorna `No MCP servers configured.` mesmo com `~/.gemini/config/mcp_config.json` presente e contendo o obsv. O Gemini CLI v0.60 lê a config de MCP de `~/.gemini/mcp_config.json` (raiz) e/ou via `gemini mcp add` — **não** de `~/.gemini/config/mcp_config.json`. Ou seja: o MCP do Gemini nunca esteve ativo. Suporte existe (subcomandos `gemini mcp add <name> <commandOrUrl>`, `enable/list/remove`), aceitando **stdio** e **URL remota**.

### 2.5 JCode (v0.84.0)

| Arquivo | Bytes | mtime | Conteúdo (resumo) |
|---|---|---|---|
| `~/.jcode/config.toml` | 5.002 | 2026-09-15 12:41 | `[mcp.servers.obsv]`, provider opencodex (10100), keybindings, websearch |
| `~/.jcode/mcp.json` | 2.014 | 2026-09-15 13:57 | `mcpServers` (8): ddg, github, filesystem, playwright, sequential-thinking, memory, notebooklm, supabase |
| `~/work_out/JCODE.md` | 4.636 | 2026-08-31 | Header (aponta p/ AGENTS.md) + corpo genérico duplicado (263 linhas) |

Suporte a cliente MCP confirmado (flags `--mcp-tools auto|eager|deferred`, `--mcp-tools-token-threshold`). Não há subcomando `jcode mcp`.

### 2.6 Contexto (não-alvo da missão, mas espelhos do mesmo conteúdo)

| Arquivo | Bytes | mtime | Conteúdo (resumo) |
|---|---|---|---|
| `~/work_out/AIDER.md` | 4.049 | 2026-08-04 | Idêntico ao GEMINI.md (corpo genérico) |
| `~/.config/aider/mcp.json` | 1.980 | 2026-09-13 18:54 | obsv, santuario-memoria, lab-universal, ddg, searxng, github, filesystem |
| `~/work_out/.mcp.json` | — | — | Removido; existe `.mcp.json.bak-20260804_232345` (playwright `http://localhost:3000/mcp` — legado) |
| `~/work_out/.cursorrules` | 909 | 2026-07-17 | Legado: referencia `.mcp_context/` e ferramentas obsoletas (`memoria_listar`, `rag_indexar`) |
| `~/work_out/docs/MCP_SHARED_MEMORY_GUIDE.md` | 23 linhas | jul/2026 | Protocolo obsoleto de `.mcp_context` (endpoint 8765, tools que não existem mais nesse nome) |

---

## 3. Serviços MCP centrais do lab (endpoints reais)

| Serviço | Endpoint verificado | Transporte | Notas |
|---|---|---|---|
| `mcp-lab-universal` (RAG/memória, alias `lab-teco`) | `http://127.0.0.1:8765/mcp` | streamable HTTP | `GET /mcp` → 406 (handshake esperado); **Codex usa este** e é o recomendado p/ clientes novos |
| idem | `http://127.0.0.1:8765/sse` | SSE | `GET /sse` → 200; **trava no cliente rmcp do Codex** (não usar ali) |
| `obsv` (vault) | binário `/home/teco/.local/bin/obsv mcp` | stdio | v2.0.0, funcional nos 8 agentes desde 2026-08-14 |
| Playwright (Docker) | `http://127.0.0.1:3002` (host) / `http://100.108.74.62:3002` (tailscale) | **WebSocket driver** `ws://0.0.0.0:3000/` | Ver seção 4 |
| Supabase `lab-g` | `xwwavfbvdcaypnqmuked` | MCP supabase (stdio) / REST | source of truth de governança |
| mcp-bridge | `https://mcp-bridge-node.tail9c8d52.ts.net/mcp` | streamable HTTP | para claude.ai/destinos externos |

---

## 4. Diagnóstico Playwright (causa raiz)

### 4.1 O que o container é (e o que não é)

- Container: `playwright-mcp` · imagem `mcr.microsoft.com/playwright:v1.61.0-noble` · `user: pwuser` · `ipc: host` · `init: true` · `restart: unless-stopped` · rede `lab_net` · porta `3002→3000`.
- Comando real: `npx -y playwright@1.61.0 run-server --port 3000 --host 0.0.0.0`.
- Log do container: `Listening on ws://0.0.0.0:3000/` e `GET /json → {"wsEndpointPath":"/"}`.
- Browser/binários instalados **no container**: `/ms-playwright` com chromium-1228, chromium_headless_shell-1228, ffmpeg, firefox, webkit.
- Stack: `/opt/stacks/playwright-mcp/docker-compose.yml` (atualizado 2026-09-18 10:37 com `deploy.resources` + `lab_net`).

**Conclusão:** o container expõe o **Playwright Driver Server** (WebSocket/JSON-RPC da API Playwright), **não** um endpoint MCP (`/sse` ou `/mcp`). O cliente correto é o `@playwright/mcp` **conectado a esse driver remoto via env `PLAYWRIGHT_DRIVER_URL`**. É assim que os agentes usam a instância Docker persistente em vez de instanciar browser local.

### 4.2 O que os agentes estão fazendo (cada um)

| Agente | Config atual do Playwright | Comportamento hoje |
|---|---|---|
| Claude Code | stdio `npx @playwright/mcp --executable-path /usr/bin/chromium --headless` | Sobe browser **local no host** a cada sessão; ignora container |
| OpenCode | stdio `npx @playwright/mcp --executable-path /usr/bin/chromium --headless` | idem (processo vivo confirmado: PID 2141036 `npm exec @playwright/mcp` em pts/1 — este próprio agente) |
| Codex | stdio `npx @playwright/mcp --executable-path /usr/bin/chromium --headless` | idem |
| JCode | stdio `npx @playwright/mcp` (sem executable-path) | Browser descoberto ou falha; mais frágil ainda |
| Gemini CLI | não configurado | — |

### 4.3 Evidência ao vivo

- `ps aux | grep playwright` mostra 2 grupos: (a) processos **dentro do container** (driver 3000, ocioso) e (b) `npm exec @playwright/mcp --executable-path /usr/bin/chromium --headless` **no host** (efêmero, instanciado por este agente ao abrir a sessão).
- O `.mcp.json` legado (ago/2026) apontava para `http://localhost:3000/mcp` (SSE) — também incorreto, pois o container não é MCP. O README do stack (`/opt/stacks/playwright-mcp/README.md`) contém essa instrução equivocada (apontar `/sse`), e os `.md` `INSTRUCOES_PLAYWRIGHT_MCP_DOCKGE*.txt` reproduzem o erro.

**Causa raiz (consolidada):** a config MCP de todos os agentes compatíveis aponta para uma instância `@playwright/mcp` **stdio local** (que abre browser próprio no host), em vez de apontar o `@playwright/mcp` para o **driver persistente do container** via `PLAYWRIGHT_DRIVER_URL=http://<host>:3002`. O container fica ocioso, browsers locais sobem/fecham a cada execução e a sessão de browser é perdida. → Correção definitiva na Fase 5 (endpoint fixo, sem auto-launch local).

---

## 5. Matriz de compatibilidade agente × ferramenta MCP

Legenda: `✔` compatível e funcionando · `⚠` compatível, mas configurada de forma errada (efêmera/endpoint errado) · `·` compatível, não configurada hoje · `✘` incompatível/no lab não existe · estado sem símbolo = não configurada (sem evidência).

| Ferramenta MCP | Claude Code | OpenCode | Codex | Gemini CLI | JCode | Observação |
|---|---|---|---|---|---|---|
| **mcp-lab-universal (lab-teco)** | ✔ SSE | ✔ SSE | ✔ `/mcp` (não usar `/sse` — rmcp trava) | · (suporta URL; config morta hoje) | · (suporta desde v0.81.3; config remota `type: remote` p/ `/sse`) | Endpoint correto: `8765`; Codex só via `/mcp` |
| **ObSV** | ✔ stdio | ✔ stdio | ✔ stdio | · (stdio ok; arquivo não é lido — ver 2.4A) | ✔ stdio (`[mcp.servers.obsv]`) | Binário único `obsv mcp` |
| **Playwright** | ⚠ efêmero local | ⚠ efêmero local | ⚠ efêmero local | · (não config.) | ⚠ efêmero local (sem `--executable-path`) | Deve usar driver Docker via `PLAYWRIGHT_DRIVER_URL=http://…:3002` |
| **filesystem** | ✔ | ✔ | ✔ | · | ✔ | stdio npx, raiz `/home/teco/work_out` |
| **github** | ✔ | ✔ | ✔ | · | ✔ | npx stdio + PAT (segredo não reproduzido) |
| **docker** | ✔ (`DOCKER_MCP_LOCAL`) | · (não config.) | ✔ | · | · (não config.) | `docker-mcp` npx stdio |
| **postgres** | ✘ não existe MCP Postgres ativo no lab | ✘ idem | ✘ idem | ✘ idem | ✘ idem | Acesso a banco é via Supabase MCP / RAG; nenhum agente tem server postgres |
| **memory** | ✔ | ✔ | ✔ | · | ✔ | npx stdio |
| **duckduckgo-search** | ✔ (pkg ericthered) | ✔ (`uvx duckduckgo-mcp-server`) | ✔ | · | ✔ | Nomes de pacote divergem entre agentes (não duplicar regra, só catálogo) |
| **fetch** | ✔ (`uvx mcp-server-fetch`) | · | · | · | · | Só Claude Code configurou |
| **supabase** (lab-g) | ✔ | ✔ | ✔ | · | ✔ | npx stdio + token |

**Extras presentes (fora das 11 colunas):** `sequential-thinking` (Claude/OpenCode/Codex/JCode ✔), `notebooklm` (Claude/OpenCode/Codex/JCode ✔), `context7` (OpenCode/Codex ✔), `computer-control` (OpenCode/Codex/Claude-project — Xvfb `:99` vivo ✔), `searxng-local` (OpenCode ✔, via SearXNG 8081 do Perplexica), `hexstrike-ai` (OpenCode + Claude project-home → host `100.67.175.95` **offline** — indisponível no momento), `teco-mcp` (Claude project `~` → alias SSE 8765, **duplicado** do mcp-lab-universal).

### 5.1 Leitura da matriz (importante)

1. **Não há incompatibilidade de transporte generalizada**: quase todas as tools do lab são MCP stdio e funcionam em qualquer CLI que suporte MCP (todos os 5 suportam). A única restrição de transporte real é **Codex + SSE** (usar `/mcp`), já respeitada na config atual.
2. **Ferramentas "incompatíveis" no sentido da missão = configs mortas/erradas**, não a tool em si. Os dois casos concretos: (a) Playwright efêmero em 4 agentes (corrigir p/ driver Docker); (b) Gemini CLI com config de MCP num arquivo que o CLI não lê (config nunca ativa).
3. **Docker no OpenCode** não está configurado hoje — historicamente funcional (memória 2026-08-01), ausente no `opencode.json` atual. Caso de decisão: readicionar ou não (ver desenho da Fase 3).
4. **postgres**: não existe MCP Postgres no lab; a coluna é atendida por Supabase MCP. Nenhuma entrada a remover (nenhum agente tem), nenhuma a adicionar (evitar duplicação com Supabase).
5. Verificação dinâmica da matriz será feita na Fase 6 (recarregar cada CLI e conferir tools ativas).

---

## 6. Contradições e redundâncias entre instruções atuais

### 6.1 Contradições

| # | Contradição | Onde |
|---|---|---|
| C1 | `CLAUDE.md`/`CODEX.md`/`OPENCODE.md` da raiz do lab dizem que "agentes suportados: Claude Code, Codex, OpenCode" e descrevem **o projeto Padroeira** — mas estes arquivos são carregados como instrução **global do work_out**, portando regras de um projeto específico para qualquer tarefa do lab inteiro | `~/work_out/{CLAUDE,CODEX,OPENCODE}.md` |
| C2 | `AGENTS.md` (raiz) diz "usar MCP servers quando disponíveis (filesystem, memory, github)" vs catálogo real (tem mcp-lab-universal/obsv/supabase que são os canônicos) | `~/work_out/AGENTS.md` |
| C3 | `.cursorrules` + `docs/MCP_SHARED_MEMORY_GUIDE.md` mandam ler `.mcp_context/` e usar `memoria_listar`/`rag_indexar` — ferramentas **que não existem** nesse nome no servidor atual (8765 expõe `buscar_memoria`/`ingest_document`). Endpoint correto do lab hoje é via MCP, não resposta de `curl localhost:8765` | `.cursorrules`, `docs/MCP_SHARED_MEMORY_GUIDE.md` |
| C4 | `GEMINI.md` (raiz) lista "playwright, browser, docker, terminal, rag, memory, supabase" como ferramentas esperadas — mas o Gemini CLI hoje não tem MCP ativo (config morta) | `~/work_out/GEMINI.md` |
| C5 | `AGENTS.md` canônico do vault (2026-08-31) diz que JCode "pode não chamar MCP — verificar"; JCode v0.84.0 **já suporta** (`--mcp-tools`). Instrução desatualizada. | `knowledge/AGENTS.md` §4 |
| C6 | `JCODE.md` contém o corpo genérico (persona/processo) apesar de já apontar para o AGENTS.md — duplicação parcial com o canônico | `~/work_out/JCODE.md` |

### 6.2 Redundâncias (mesmo conteúdo, palavras diferentes)

| Bloco duplicado | Arquivos |
|---|---|
| Persona/processo "Consultor Técnico, Revisor, Arquiteto… explicar plano antes de editar… critério de sucesso… Obsidian vault" (254–267 linhas) | `GEMINI.md`, `AIDER.md`, `JCODE.md` (corpo), `knowledge/05-Agentes/Persona-Padrao.md`, `knowledge/05-Agentes/Diretrizes-Gerais.md` |
| Governança genérica curta (papel/processo/comandos test-lint-build) | `AGENTS.md` (raiz), `knowledge/05-Agentes/Diretrizes-Gerais.md` (§ "Origem: 00-Inbox/work_out/AGENTS.md") |
| "Leia o AGENTS.md primeiro" (pointer) | `knowledge/{CLAUDE,CODEX,OPENCODE}.md` + todos os `CLAUDE.md`/`CODEX.md`/`OPENCODE.md` nas subpastas do vault |
| Regras/instruções do Padroeira | `~/work_out/CLAUDE.md` = `CODEX.md` = `OPENCODE.md` = `docs/CLAUDE.md` = `docs/CODEX.md` = `docs/OPENCODE.md` (byte a byte) |

**Nota:** existem **dezenas** de `CLAUDE.md`/`CODEX.md`/`OPENCODE.md` espelhados em subpastas do work_out e do vault (todos pointers de 270 bytes). Não são alvo de reescrita — já estão corretos como pointers. A duplicação relevante está nos 5 arquivos de agente da raiz.

---

## 7. Estado da fonte única hoje

- `knowledge/AGENTS.md` (7.050 bytes, 2026-08-31) já se auto-intitula **"Referência Canônica do Laboratório"** e é apontado por todos os `CLAUDE.md`/`CODEX.md`/`OPENCODE.md` do vault. Cobre: papel/processo, catálogo de ferramentas reais (mcp-lab-universal, ObSV, Supabase), árvore de decisão "onde gravar o quê", problemas conhecidos, auditoria `revisor_code`.
- **Lacunas vs. missão:** não define papel individual dos 5 agentes; não tem convenções de host (hostnames Tailscale) nem mapas de stacks Docker; não tem catálogo MCP por ferramenta com "quando usar / quando NÃO usar / como invocar"; **não tem a regra explícita do Playwright Docker**; não formaliza o registro de auditoria no Supabase `lab-g` como obrigatório.
- Convenção de gestão de sessão existente para servir de modelo (citada na missão): `etapa.md` do mcp-bridge (`/opt/stacks/mcp-bridge/etapa.md` — estado, endpoint, autenticação, causa-raiz, próximos passos).

---

## 8. Anexos

- Anexo A — Lista completa de arquivos de instrução espalhados (ver seção 6.2 e o `find` executado em 2026-09-18; ~130 entries).
- Anexo B — Inventário de MCP do VAIO (do vault, seção 2.3 do inventário VAIO): MCP servers listados no VAIO incluem `github, filesystem, memory, sequential-thinking, playwright, context7, supabase, obsv, lab-universal, ddg-search, notebooklm, computer-control, hexstrike-ai, fetch, wazuh, docker, GitKraken` — a validar quando a estação voltar ao ar.