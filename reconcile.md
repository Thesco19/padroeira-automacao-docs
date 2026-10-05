# Tabela de Reconciliação v2 — 2026-09-30 (código apenas)

| Projeto | Último commit de código | Primeiro commit de código | Nº commits código | mtime último arquivo código (arquivo) | Serviço/porta ativo? | Situação no STATUS.md |
|---|---|---|---|---|---|---|
| arquivo | sem commit de código | sem commit de código | 0 | 2026-09-10 22:34 (conversor.py) | parado (duplicata aut-v1?) | parado |
| automacao_padroeira | ebd2a59 2026-09-14 feat: tabela de auditoria SQLite, comando /auditar e datas DD/MM/AAAA | 3eed21d 2026-07-06 Faxina V2: Scripts movidos para lab_agente_web e sub-repositorios removidos | 19 | 2026-09-30 16:14 (logs/reconciliation.log) | ativo (bot_reconciliation.py, pid vivo) | ativo |
| API+Doctor | sem commit de código | sem commit de código | 0 | 2026-07-20 23:44 (.pytest_cache/v/cache/nodeids) | aguardando decisão | aguardando decisão |
| MCP_Bridge | sem commit de código | sem commit de código | 0 | sem arquivo de código | ativo (container :8001) | ativo |
| generator | sem commit de código | sem commit de código | 0 | 2026-09-17 11:15 (.env) | aguardando decisão | aguardando decisão |
| lab-clients | b1b16d5 2026-09-27 feat(canvas): /mindmap renderiza .canvas como Mermaid; parser Rust com fallback de filename | 5709a0d 2026-09-19 feat: crate lab-clients com MCP, Ollama, Supabase e utilitarios de contexto/forge | 16 | 2026-09-27 22:36 (src/obsv.rs) | ativo (biblioteca, sem daemon) | ativo |
| minerador | 2be21ff 2026-09-28 feat(minerador): pipeline V1.2.2 com .env, API headless e RAG MCP | 2be21ff 2026-09-28 feat(minerador): pipeline V1.2.2 com .env, API headless e RAG MCP | 1 | 2026-09-29 00:28 (minerador.log) | parado (systemd dead desde 29/09) | parado |
| obs | adbdad8 2026-09-30 feat(obs): trabalho do Mapa Mental (parser canvas + web UI); 3 DoctorTests ja falhavam no HEAD limpo | 6deb7c3 2026-09-27 feat(config): adiciona max_graph_nodes (default 150) | 8 | 2026-09-28 10:44 (.remember/logs/memory-2026-09-28.log) | ativo (obsv-bridge.service, :8777) | concluído (v2.0) |
| ominiroute | sem commit de código | sem commit de código | 0 | 2026-08-13 22:36 (.claude/settings.local.json) | aguardando decisão | aguardando decisão |
| promptforge | 5bdfe2a 2026-09-21 feat: qwenchat v2 — provedores, /debate, /promote, /model, forge na Mistral | 3e41ca0 2026-09-19 refactor: promptforge consome lab-clients; segredo RLS sai do codigo | 5 | 2026-09-21 22:19 (.env.example) | ativo, degradado (CLI sob demanda, depende intel-1 parado) | ativo (sob demanda — CLI, sem daemon) |
| prompts | sem commit de código | sem commit de código | 0 | sem arquivo de código | desconhecido | sem STATUS.md |
| qwenchat | b94bb5a 2026-09-24 feat(qwenchat): Fase 1-4 completa - DecisionPolicy, Jev gate, free APIs, mind maps, canvas | d50c0d9 2026-09-19 feat: qwenchat modo explore (Qwen + RAG + 5 camadas + resumo de sessao) | 12 | 2026-09-24 22:44 (Cargo.toml) | ativo, degradado (CLI, depende intel-1 parado) | ativo |
| sessions | sem commit de código | sem commit de código | 0 | 2026-09-24 22:34 (test-gate4_explore_log.txt) | desconhecido | sem STATUS.md |
| smartcam | 62f61fb 2026-09-30 fix rename smartcam | a40b35a 2026-09-07 feat: initialize SmartCam project structure | 24 | 2026-09-30 13:33 (.git/objects/41/d6d07155c89971ec5dceb2864de7414ec5f9aa) | ativo (systemd, :3100/:3443) | ativo |
| target | sem commit de código | sem commit de código | 0 | 2026-09-27 22:32 (debug/.fingerprint/lab-clients-582e4e0c90cd83d6/test-lib-lab_clients.json) | desconhecido | sem STATUS.md |
| polyglot-swarm | da3eedf 2026-09-30 chore: commit inicial do lab-z (polyglot-swarm, regente, revisor; sem remoto) | da3eedf 2026-09-30 chore: commit inicial do lab-z (polyglot-swarm, regente, revisor; sem remoto) | 1 | 2026-08-31 22:03 (tasks/demo_review/.pytest_cache/v/cache/nodeids) | parado | parado |
| regente | da3eedf 2026-09-30 chore: commit inicial do lab-z (polyglot-swarm, regente, revisor; sem remoto) | da3eedf 2026-09-30 chore: commit inicial do lab-z (polyglot-swarm, regente, revisor; sem remoto) | 1 | 2026-09-10 22:32 (__pycache__/regente_console.cpython-310.pyc) | parado (sem processo) | parado |
| revisor | da3eedf 2026-09-30 chore: commit inicial do lab-z (polyglot-swarm, regente, revisor; sem remoto) | da3eedf 2026-09-30 chore: commit inicial do lab-z (polyglot-swarm, regente, revisor; sem remoto) | 1 | 2026-09-30 17:23 (.remember/logs/memory-2026-09-30.log) | concluído (hook systemd :8787) | concluído |
| agent-test-lab | sem git (stack) | sem git (stack) | 0 | 2026-09-26 10:40 (results/llm-smoke-gonkarouter.json) | desconhecido | parado |
| atlas-viewer | sem git (stack) | sem git (stack) | 0 | 2026-09-30 13:41 (index.html) | desconhecido | ativo |
| buscador | sem git (stack) | sem git (stack) | 0 | 2026-09-30 21:01 (overseerr-config/logs/.machinelogs-2026-09-30.json) | desconhecido | ativo |
| dockge | sem git (stack) | sem git (stack) | 0 | 2026-09-29 10:49 (data/dockge.db-wal) | desconhecido | ativo |
| flame | sem git (stack) | sem git (stack) | 0 | 2026-09-29 10:55 (data/db.sqlite) | desconhecido | sem STATUS.md |
| fotos-videos | sem git (stack) | sem git (stack) | 0 | 2026-09-24 23:58 (compose.yaml) | desconhecido | parado |
| gestao-midia | sem git (stack) | sem git (stack) | 0 | 2026-09-24 23:58 (compose.yaml) | desconhecido | ativo |
| hermes_core | sem git (stack) | sem git (stack) | 0 | 2026-09-27 16:02 (n8n_data/n8nEventLog.log) | desconhecido | parado |
| intel-1 | sem git (stack) | sem git (stack) | 0 | 2026-09-29 10:53 (scrutiny/config/scrutiny.db) | desconhecido | parado |
| lab-master | sem git (stack) | sem git (stack) | 0 | 2026-09-30 13:42 (config/resources.yaml) | desconhecido | ativo |
| langflow | sem git (stack) | sem git (stack) | 0 | 2026-09-24 23:58 (compose.yaml) | desconhecido | parado |
| limpador | sem git (stack) | sem git (stack) | 0 | 2026-09-24 23:58 (compose.yaml) | desconhecido | parado (por desenho — job run-once, não serviço) |
| mcp-bridge | sem git (stack) | sem git (stack) | 0 | 2026-09-24 23:58 (docker-compose.yaml) | desconhecido | ativo |
| mcp-lab | sem git (stack) | sem git (stack) | 0 | 2026-09-30 20:34 (data/chroma_db/chroma.sqlite3) | desconhecido | ativo |
| mcp-superassistant-proxy | sem git (stack) | sem git (stack) | 0 | 2026-09-24 23:58 (docker-compose.yml) | desconhecido | parado |
| meu-painel | sem git (stack) | sem git (stack) | 0 | 2026-09-24 23:58 (compose.yaml) | desconhecido | ativo |
| n8n | sem git (stack) | sem git (stack) | 0 | 2026-06-08 14:52 (n8n_data/n8nEventLog.log) | desconhecido | sem STATUS.md |
| osint | sem git (stack) | sem git (stack) | 0 | 2026-09-30 14:43 (data/spiderfoot/spiderfoot.db-wal) | desconhecido | ativo (parcial — spiderfoot no ar; theharvester/maigret são CLI) |
| perplexica | sem git (stack) | sem git (stack) | 0 | 2026-09-30 16:53 (.git/logs/refs/heads/lab-docs) | ativo (container :3000) | ativo |
| playwright-mcp | sem git (stack) | sem git (stack) | 0 | 2026-09-24 23:58 (docker-compose.yml) | ativo (container :3002) | ativo |
| plex | sem git (stack) | sem git (stack) | 0 | 2026-09-24 23:58 (compose.yaml) | ativo (container) | ativo |
| suporte-midia | sem git (stack) | sem git (stack) | 0 | 2026-09-30 19:54 (config/bazarr/config/releases.txt) | desconhecido | ativo |
| transam | sem git (stack) | sem git (stack) | 0 | 2026-09-30 19:37 (config/transmission/stats.json) | desconhecido | ativo |
| vaultwarden | sem git (stack) | sem git (stack) | 0 | 2026-09-27 16:00 (vw-data/db.sqlite3-wal) | ativo (container) | parado |

---
*Gerado automaticamente por script (código apenas, exclui .md e commits de 30/09) — o Paulo decide o que fazer com cada linha.*