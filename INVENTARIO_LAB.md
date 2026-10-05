# INVENTARIO_LAB — Fase 0 (Somente Leitura)

> **Gerado em:** 2026-09-30
> **Escopo:** labs `a`, `b`, `z` — pastas de primeiro nível
> **Nada foi criado, movido, renomeado, apagado ou editado nos projetos.**
> Único arquivo escrito: este.

---

## 0. Descoberta dos caminhos dos labs

| Pedido no prompt | Encontrado | Situação |
|---|---|---|
| `/work_out/lab-*` | **não existe** `/work_out` | caminho literal inválido neste host |
| — | `/home/teco/work_out/lab-a` | único candidato |
| — | `/home/teco/work_out/lab-b` | único candidato |
| — | `/home/teco/work_out/lab-z` | único candidato |

- Busca global (`find / -name 'lab-*'`) só achou também `/opt/stacks/lab-master`,
  `/var/log/lab-master`, `/run/lab-master` — **não** são lab-a/b/z, são o
  orquestrador `lab-master`. Foram ignorados como labs.
- **Conclusão:** não há ambiguidade de lab; o único desvio é a raiz
  (`/work_out` → `/home/teco/work_out`). Saída gravada em
  `/home/teco/work_out/INVENTARIO_LAB.md`. **Pergunta 1** para o Paulo.

### Definição de "projeto"

Toda pasta de primeiro nível dentro de cada lab (pastas ocultas descartadas:
`.git`, `.venv`, `.claude`, `.aider*`, `.pytest_cache`). Dentro de `lab-b`
entram também `sessions/` e `target/`, que são **artefatos** (logs e build
Rust) — listados por rigor, marcados como não-projeto. Ver **Pergunta 2**.

**Total: 18 pastas** — lab-a: 2 · lab-b: 13 · lab-z: 3.

---

## 1. Tabela resumo

Legenda: ✅ existe/positivo · ❌ não existe · ⚠️ existe com outro nome ou
com problema · 📦 = artefato, não projeto

| # | Projeto (pasta) | Lab | README | STATUS | git | RAG | Supabase | ObSV | Estado aparente |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `arquivo` | a | ✅ (criado, fora do commit — pasta ignorada) | ✅ (idem) | ❌ (ignorado) | ⚠️ tag `restaurante` (18) | ⚠️ via linha `lab-a` | ❌ | parado |
| 2 | `automacao_padroeira` | a | ✅ (criado, commitado) | ✅ (idem) | ✅ repo `lab-a` | ⚠️ tag `restaurante` (18) | ✅ linha `padroeira` | ✅ `01-Projetos/Padroeira-aut-v1.md` | **ativo** |
| 3 | `API+Doctor` | b | ❌ (fantasma: só STATUS) | ✅ | ❌ | ❌ | ❌ | ❌ | aguardando decisão |
| 4 | `generator` | b | ❌ (fantasma: só STATUS) | ✅ | ❌ | ✅ tag `lab-b/generator` (1) | ⚠️ via linha `lab-b` | ⚠️ só menções | aguardando decisão |
| 5 | `lab-clients` | b | ✅ | ✅ | ✅ repo `lab-b` | ❌ | ⚠️ via linha `lab-b` | ❌ | ativo |
| 6 | `MCP_Bridge` | b | ✅ | ✅ | ❌ | ❌ | ⚠️ via linha `lab-b` | ❌ | ativo (via stack) |
| 7 | `minerador` | b | ✅ (existente; Ficha fora do commit) | ✅ | ✅ repo `lab-b` | ❌ | ⚠️ via linha `lab-b` | ❌ | parado (serviço morto) |
| 8 | `obs` | b | ✅ (existente + Ficha) | ✅ | ✅ repo `lab-b` | ⚠️ tag `obsv` (4) | ✅ linha `obsv` | ✅ `01-Projetos/ObSV-IMPLEMENTATION_PLAN.md` | **ativo** |
| 9 | `ominiroute` | b | ❌ (fantasma: só STATUS) | ✅ | ❌ | ❌ | ⚠️ via linha `lab-b` | ⚠️ `09-Referencias/OmniRoute.md` | aguardando decisão |
| 10 | `promptforge` | b | ✅ (existente + Ficha) | ✅ | ✅ repo `lab-b` | ✅ tag `promptforge` (5) | ⚠️ via linha `lab-b` | ❌ | ativo (sob demanda) |
| 11 | `prompts` 📦 | b | ❌ | ❌ | ❌ (ignorado) | ⚠️ tags `teste-*` (3) | ⚠️ via linha `lab-b` | ❌ | artefato (no README do `lab-b`) |
| 12 | `qwenchat` | b | ✅ (existente + Ficha) | ✅ | ✅ repo `lab-b` | ⚠️ doc taggado `promptforge` | ⚠️ via linha `lab-b` | ❌ | ativo |
| 13 | `sessions` 📦 | b | ❌ | ❌ | ❌ (ignorado) | ❌ | ⚠️ via linha `lab-b` | ❌ | artefato (no README do `lab-b`) |
| 14 | `smartcam` (renomeado de `smartsearck` em 2026-09-30) | b | ✅ (existente + Ficha) | ✅ | ✅ subrepo próprio + gitlink OK | ⚠️ tag `smartcam` (1) | ✅ linha `smartcam` | ✅ `01-Projetos/smartcam/` | **ativo** |
| 15 | `target` 📦 | b | ❌ | ❌ | ❌ (ignorado) | ❌ | ⚠️ via linha `lab-b` | ❌ | artefato (no README do `lab-b`) |
| 16 | `polyglot-swarm` | z | ✅ | ✅ | ✅ repo `lab-z` (`6622aa8`) | ⚠️ só menções | ❌ | ⚠️ só menções | parado |
| 17 | `regente` | z | ✅ (existente + Ficha) | ✅ | ✅ repo `lab-z` | ⚠️ tags `lab-z`, `regente-generator-ai-studio` | ❌ | ✅ `02-Laboratorios/Regente.md` | parado |
| 18 | `revisor` | z | ✅ (existente + Ficha) | ✅ | ✅ repo `lab-z` | ⚠️ tag `lab-z` (4) | ❌ | ⚠️ só menções | concluído → virou infra |

**Nenhum dos 18 tem `STATUS.md`.** O único arquivo de status encontrado é
`lab-a/automacao_padroeira/aut-v1/AUX/status.md` (caminho e nome diferentes).

---

## 2. Detalhamento por projeto

### LAB-A — `/home/teco/work_out/lab-a` (repo próprio, último commit 2026-09-14 `ebd2a59` "feat: tabela de auditoria SQLite, comando /auditar e datas DD/MM/AAAA"; 20 entradas sujas)

#### 2.1 `arquivo`
- **Caminho:** `/home/teco/work_out/lab-a/arquivo`
- **Docs:** ❌ README.md · ❌ STATUS.md · relevantes: `contexto.md`,
  `instrucoes_ptojeto.txt`, `CLAUDE.md`/`CODEX.md`/`OPENCODE.md`
- **Git:** não versionado — `lab-a/.gitignore` contém `arquivo/` → sem histórico
- **Última modificação de arquivo:** 2026-09-10 22:34 (`conversor.py`)
- **Resumo:** pipeline Python de reconciliação fiscal do Restaurante Padroeira
  (`cortex_padroeira.py`, `engine_consolidacao.py`, `motor_balancete.py`,
  `inspetor_celulas.py`, `espiao_links.py`, `transportador_gabarito.py`) com
  `templates/`, `lab_agente_web/` e venv local.
- **Estado:** **parado** — motivo: sem commits, última edição 10/09, contém
  cópia dos módulos que hoje vivem em `automacao_padroeira/aut-v1` (candidato a
  duplicata, ver §3).
- **Serviços/portas:** nenhum. `segredo em lab-a/arquivo/.env`

#### 2.2 `automacao_padroeira`
- **Caminho:** `/home/teco/work_out/lab-a/automacao_padroeira` (subpastas `aut-v0/`, `aut-v1/`)
- **Docs:** ❌ README.md na raiz (✅ `aut-v1/README.md`) · ❌ STATUS.md
  (⚠️ `aut-v1/AUX/status.md`, atualizado 2026-08-26) · outros: `aut-v1/refatorar.md`,
  `aut-v1/relatorio_auditoria_sombra.md`
- **Git:** ✅ rastreado no repo `lab-a` (exceto `aut-v0/`, que é ignorado).
  Último commit: **2026-09-14** `ebd2a59` "feat: tabela de auditoria SQLite,
  comando /auditar e datas DD/MM/AAAA". 4 arquivos modificados **sem commit**:
  `aut-v1/{bot_reconciliation,async_reconciliation_v2,config_precos,cortex_padroeira_async}.py`
- **Última modificação:** 2026-09-30 09:53 (`aut-v1/logs/reconciliation.log`)
- **Resumo:** automação de reconciliação financeira do restaurante Padroeira;
  `aut-v1` é a versão de produção com bot Telegram orquestrando Cortex → Engine → Motor.
- **Estado:** **ativo** — motivo: processo
  `python3 .../aut-v1/bot_reconciliation.py` em execução (pid 1478667);
  recurso `lab-a/automacao_padroeira/aut-v1` no lab-master é `criticality: important`;
  Supabase `project_status.padroeira` = `active`, progress 97, fase `hardening_bot_telegram`.
- **Serviços:** processo `bot_reconciliation.py` (lab-master, `single_instance: true`);
  `segredo em lab-a/automacao_padroeira/aut-v1/.env`

---

### LAB-B — `/home/teco/work_out/lab-b` (repo próprio, último commit 2026-09-28 `2be21ff` "feat(minerador): pipeline V1.2.2…"; 16 entradas sujas; raiz é um crate Rust `Cargo.toml` + `benchmark_model.sh`)

Pastas rastreadas pelo git: `lab-clients`, `minerador`, `obs`, `promptforge`,
`qwenchat`, `smartsearck` (gitlink). Não rastreadas: `API+Doctor`, `generator`,
`MCP_Bridge`, `ominiroute`, `prompts`, `sessions`, `target`.

#### 2.3 `API+Doctor`
- **Caminho:** `/home/teco/work_out/lab-b/API+Doctor` (subpasta `api_doctor/`)
- **Docs:** ❌ README · ❌ STATUS · ❌ outros `.md` de projeto
  (só `api_doctor/.pytest_cache/README.md`, que é cache do pytest)
- **Git:** ❌ nenhum histórico (todo o conteúdo é cache com `.gitignore` próprio `*`)
- **Última modificação:** 2026-07-20 23:44 (cache do pytest)
- **Resumo:** **indefinido** — a pasta só contém `__pycache__` e `.pytest_cache`;
  não há `.py`, `.toml`, `.json` de código-fonte.
- **Estado:** **indefinido** — motivo: sem código e sem registro em fonte alguma.
- **Serviços:** nenhum.

#### 2.4 `generator`
- **Caminho:** `/home/teco/work_out/lab-b/generator`
- **Docs:** ❌ README · ❌ STATUS · ❌ outros
- **Git:** ❌ não rastreado (só `.env` e diretórios de config de agente)
- **Última modificação:** 2026-09-17 11:15 (`.env`)
- **Resumo:** deveria ser o "AI Generator Universal / Studio" (FastAPI, geração
  de imagem / face swap). A RAG registra a migração de
  `lab-z/regente/generator` → `lab-b/generator` em 2026-09-10, incluindo symlink
  `lab-b/shared -> ../lab-z/regente/shared`.
- **Estado:** **indefinido / aparentemente quebrado** — motivo: a pasta só tem
  `.agents/`, `.codex/`, `.env`, `.opencode/`; **não existe `generator/server.py`**,
  o symlink `lab-b/shared` **não existe**, e o serviço do lab-master
  (`uvicorn --app-dir /home/teco/work_out/lab-b generator.server:app`, porta 8092)
  **está fora do ar**.
- **Serviços:** lab-master declara porta **8092** (hoje sem resposta; 8090 foi
  cedida ao SpiderFoot/OSINT em 15/09). `segredo em lab-b/generator/.env`

#### 2.5 `lab-clients`
- **Caminho:** `/home/teco/work_out/lab-b/lab-clients`
- **Docs:** ❌ README · ❌ STATUS · ❌ outros
- **Git:** ✅ repo `lab-b` · último commit **2026-09-27** `b1b16d5`
  "feat(canvas): /mindmap renderiza .canvas como Mermaid…"
- **Última modificação:** 2026-09-27 22:36 (`src/obsv.rs`)
- **Resumo:** crate Rust compartilhado do lab (trait `LlmProvider`,
  `OllamaProvider`, `OpenAiCompatibleProvider`, clientes ObSV/bridge), usado por
  `qwenchat` e `promptforge`.
- **Estado:** **ativo** — motivo: commit na véspera do inventário; é dependência
  de duas ferramentas em uso.
- **Serviços:** biblioteca, sem porta própria.

#### 2.6 `MCP_Bridge`
- **Caminho:** `/home/teco/work_out/lab-b/MCP_Bridge` (`adapters/mcp_server/`, `sessions/`)
- **Docs:** ❌ README · ❌ STATUS · ❌ outros (`sessions/*.md` são presets de agente)
- **Git:** ❌ não rastreado (`sessions/` ignorado; `adapters/mcp_server/` só tem `__pycache__`)
- **Última modificação:** 2026-08-29 21:49 (preset `sessions/OPENCODE.md`)
- **Resumo:** **indefinido** — o código-fonte do adapter não está na pasta; restam
  só `__pycache__` e presets de sessão.
- **Estado:** **indefinido** — motivo: código local ausente, mas há serviço
  rodando (ver abaixo) ⇒ provável divergência entre o que roda e o que está aqui.
- **Serviços:** container Docker `mcp-bridge` (uvicorn `mcp_server:app`,
  porta **8001**, `project: mcp-bridge` no lab-master).

#### 2.7 `minerador`
- **Caminho:** `/home/teco/work_out/lab-b/minerador`
- **Docs:** ✅ `README.md` · ❌ STATUS.md · ✅ `RESUMO_TECNICO.md`
- **Git:** ✅ repo `lab-b` · último commit **2026-09-28** `2be21ff`
  "feat(minerador): pipeline V1.2.2 com .env, API headless e RAG MCP".
  6 arquivos modificados **sem commit** (`README.md`, `RESUMO_TECNICO.md`,
  `index.html`, `mcp_miner_server.py`, `minerador_api.py`, `test_pipeline.py`);
  não rastreados: `ecossistema_lab.db`, `minerador.log`, `__pycache__/`
- **Última modificação:** 2026-09-29 00:28 (`minerador.log`)
- **Resumo:** minerador de repositórios (FastAPI + MCP + RAG) do "Lab Córtex V2":
  mineração, parsing, sanitização, scoring e exposição na RAG.
- **Estado:** **parado** — motivo: unit `minerador.service` (systemd --user)
  está `enabled` mas `inactive (dead)` desde **2026-09-29 00:28**;
  porta 8000 sem resposta.
- **Serviços:** systemd --user `minerador.service` (parado), porta **8000**
  declarada no lab-master. `segredo em lab-b/minerador/.env`

#### 2.8 `obs`
- **Caminho:** `/home/teco/work_out/lab-b/obs`
- **Docs:** ✅ `README.md` · ❌ STATUS.md · ✅ `docs/` com ADRs
  (002/004/005), `IMPLEMENTATION_PLAN.md`, `M10_REPORT.md`, `M13_REPORT.md`
- **Git:** ✅ repo `lab-b` · último commit **2026-09-27** `b1b16d5`.
  4 arquivos modificados **sem commit** (`obsv/parsers/canvas_parser.py`,
  `obsv/web.py`, `obsv/webui.py`, `tests/*`); não rastreado `obs/Mapa-do-Lab.mmd`
- **Última modificação:** 2026-09-28 10:44 (`.remember/logs/…`)
- **Resumo:** **ObSV v2.0** — acesso local ao vault Obsidian via CLI, API REST
  `/api/v1`, Web UI e MCP; o vault no filesystem é a única fonte de verdade.
- **Estado:** **ativo** — motivo: `obsv-bridge.service` (systemd --user)
  rodando desde 2026-09-29 12:30 na porta **8777** (HTTPS/Tailnet, read-only) e
  processo `python3 -m obsv … mcp` em execução.
- **Serviços:** systemd --user `obsv-bridge.service` → :8777;
  processo `obsv mcp`; consumido pelo container `mcp-bridge`.

#### 2.9 `ominiroute`
- **Caminho:** `/home/teco/work_out/lab-b/ominiroute` (subpasta `omniroute/`)
- **Docs:** ❌ README · ❌ STATUS · ❌ outros
- **Git:** ❌ não rastreado
- **Última modificação:** 2026-08-13 22:36 (`.claude/settings.local.json`)
- **Resumo:** **indefinido** — só configs de agentes (`.agents/`, `.codex/`,
  `.claude/`, `.kilo/`) e `omniroute/.env`; nenhum arquivo-fonte.
- **Estado:** **parado / indefinido** — motivo: sem código e sem serviço local.
- **Serviços:** nenhum. `segredo em lab-b/ominiroute/omniroute/.env`
- **Nota:** a documentação do OmniRoute está no ObSV
  (`09-Referencias/OmniRoute.md`), não nesta pasta.

#### 2.10 `promptforge`
- **Caminho:** `/home/teco/work_out/lab-b/promptforge`
- **Docs:** ✅ `README.md` · ❌ STATUS.md · ❌ outros
- **Git:** ✅ repo `lab-b` · último commit **2026-09-21** `5bdfe2a`
  "feat: qwenchat v2 — provedores, /debate, /promote, /model, forge na Mistral"
- **Última modificação:** 2026-09-21 22:19 (`.env.example`)
- **Resumo:** CLI enxuta em Rust que refina prompts via Ollama local
  (`mistral-nemo:12b`, container `ai_brain`), salva versões `.md` em
  `prompts/<projeto>/` e registra a evolução na `bridge_messages` do Supabase.
- **Estado:** **ativo (sob demanda)** — motivo: ferramenta CLI sem daemon,
  último commit 21/09 e consumo documentado pela RAG.
- **Serviços:** nenhuma porta própria; consome o container `ai_brain` (:11434).
  `segredo em lab-b/promptforge/.env` (`.env.example` é só placeholder)

#### 2.11 `prompts` — *artefato/dados*
- **Caminho:** `/home/teco/work_out/lab-b/prompts` (`promptforge/`, `teste-forge/`,
  `teste-forge-mistral/`, `teste-mistral/`)
- **Docs:** ❌ README · ❌ STATUS · só `.md` de prompts gerados (`*-v1.md`, `*-v2.md`)
- **Git:** ❌ conteúdo ignorado (`prompts/*/*-v*.md`, `prompts/*/teste-*.md`)
- **Última modificação:** 2026-09-21 22:33 (`teste-mistral/venda-v2.md`)
- **Resumo:** pasta de **saída** do forge — versões de prompt de vendas geradas
  pelas ferramentas do lab.
- **Estado:** **indefinido (não é projeto de código)** — motivo: só dados gerados,
  tudo gitignorado.
- **Serviços:** nenhum.

#### 2.12 `qwenchat`
- **Caminho:** `/home/teco/work_out/lab-b/qwenchat`
- **Docs:** ✅ `README.md` · ❌ STATUS.md · ❌ outros
- **Git:** ✅ repo `lab-b` · último commit **2026-09-24** `b94bb5a`
  "feat(qwenchat): Fase 1-4 completa - DecisionPolicy, Jev gate, free APIs, mind maps, canvas"
- **Última modificação:** 2026-09-24 22:44 (`src/main.rs`)
- **Resumo:** CLI Rust com modos `explore` (chat sobre a RAG) e `forge` (refino
  de prompts), sobre o crate `lab-clients`; atalhos `qwen-e` / `qwen-f`.
- **Estado:** **ativo** — motivo: recurso `qwenchat` declarado no lab-master
  com `start_command` próprio; último commit 24/09.
- **Serviços:** lab-master recurso `qwenchat` (script `qwenchat-probe.sh`, sem porta fixa).
  `segredo em lab-b/qwenchat/.env`
  ⚠️ o próprio README alerta que chaves de API "foram expostas em terminal —
  **rotacione todas** antes do primeiro uso real".

#### 2.13 `sessions` — *artefato*
- **Caminho:** `/home/teco/work_out/lab-b/sessions`
- **Docs:** ❌ README · ❌ STATUS (só `*_log.txt`)
- **Git:** ❌ ignorado (`sessions/`)
- **Última modificação:** 2026-09-24 22:34
- **Resumo:** logs de sessão do forge/explore (`.txt`), artefato de execução.
- **Estado:** **indefinido (artefato)**.
- **Serviços:** nenhum.

#### 2.14 `smartcam` (nome canônico; pasta renomeada de `smartsearck` em 2026-09-30 — ver §6.1)
- **Caminho:** `/home/teco/work_out/lab-b/smartcam`
- **Docs:** ✅ `README.md` · ❌ STATUS.md · outros: `reviews/`
- **Git:** ✅ **repositório próprio** (`.git` interno, remoto `Thesco19/Smartsearch-`
  **intacto**) **e** gitlink no `lab-b` corrigido nos commits `ba2b45b`
  (repoint `smartsearck`→`smartcam`, SHA `e33f771` = HEAD local) e `e583ae8`
  (remoção do symlink temporário). Sem `.gitmodules` (situação herdada).
  Último commit interno **2026-09-28** `e33f771`. ⚠️ `run-smartcam.sh`
  modificado no worktree interno e **não commitado** (1 linha: `cd …/smartcam`);
  `lab-b` mostra `M smartcam` por isso — commit interno pendente de decisão.
- **Última modificação:** 2026-09-29 23:47 (`data/frames/index.json`)
- **Resumo:** **SmartCam** — scanner purple team de câmeras IP para lab fechado
  (TypeScript/Express + React/Vite, ffmpeg/YOLO para evidências).
- **Estado:** **ativo** — motivo: processo node em **3100/3443**;
  recurso `criticality: important` no lab-master
  (`start_command: bash …/run-smartcam.sh`); Supabase `smartcam` = `active`, 35%.
- **Serviços:** portas **3100** (API) e **3443** (HTTPS); `Dockerfile` e
  `docker-compose.yaml` presentes.
  `segredo em lab-b/smartsearck/.env` · `segredo em lab-b/smartsearck/data/key.pem`

#### 2.15 `target` — *artefato*
- **Caminho:** `/home/teco/work_out/lab-b/target`
- **Docs:** ❌ README · ❌ STATUS
- **Git:** ❌ ignorado (`**/target/`)
- **Última modificação:** 2026-09-27 22:32 (fingerprint de build `lab-clients`)
- **Resumo:** diretório de build do Cargo (`debug/`, `release/`).
- **Estado:** **indefinido (artefato)**.
- **Serviços:** nenhum.

---

### LAB-Z — `/home/teco/work_out/lab-z` (**sem repositório git algum** — `git ls-files -- lab-z` = 0 no repo `work_out`)

#### 2.16 `polyglot-swarm`
- **Caminho:** `/home/teco/work_out/lab-z/polyglot-swarm`
- **Docs:** ❌ README · ❌ STATUS · relevantes: `CLAUDE.md`/`CODEX.md`/`OPENCODE.md`
- **Git:** ❌ nenhum
- **Última modificação:** 2026-08-31 22:03 (`tasks/demo_review/reviews/…/review.md`)
- **Resumo:** blueprint e runner do enxame `polyglot-swarm`
  (`run_swarm.py` + `swarm_blueprint.yaml`), declarando gateways `litellm_proxy`
  (:8000) e `omniroute` (:4000) e papéis de agente (architect/coder/reviewer/research…).
- **Estado:** **parado / indefinido** — motivo: nenhum processo, sem
  representação em Supabase, e o orquestrador vivo hoje é `regente`
  (`run_swarm.py` também existe lá, com hash diferente — dois arquivos homônimos).
- **Serviços:** nenhum.

#### 2.17 `regente`
- **Caminho:** `/home/teco/work_out/lab-z/regente`
- **Docs:** ✅ `README.md` · ❌ STATUS.md · ✅ `RESUMO.md`, `AVALIACAO.md`,
  `obsidian.md`, `plans/`
- **Git:** ❌ nenhum
- **Última modificação:** 2026-09-10 22:32 (`__pycache__/regente_console.cpython-310.pyc`)
  — fontes `regente.py`/`regente_console.py` param em 2026-09-08/09
- **Resumo:** orquestrador headless de agentes que executa um blueprint YAML em
  3 fases (planejamento → execução com fila/paralelismo → síntese), com
  checkpoints, memória semântica e eventos no Supabase.
- **Estado:** **parado** — motivo: recurso `lab-z/regente` no lab-master é
  `criticality: optional` com `process_pattern: regente_console` e **nenhum
  processo correspondente está rodando**.
- **Serviços:** lab-master recurso `regente` via script
  `/home/teco/work_out/lab-z/regente/bin/regente` (sem porta).
  Observação: `lab-z/regente/shared/` existe, mas o symlink `lab-b/shared`
  que deveria apontar para ele **não existe**.

#### 2.18 `revisor`
- **Caminho:** `/home/teco/work_out/lab-z/revisor`
- **Docs:** ✅ `README.md` · ❌ STATUS.md · outros: `run_evidence/review_aider.md`,
  `.remember/*`, `reviews/`
- **Git:** ❌ nenhum
- **Última modificação:** 2026-09-03 00:02 (`.remember/tmp/…`)
- **Resumo:** PoC de revisão entre agentes (OpenCode executor → Aider revisor
  read-only → decisão), com `run_review.py`, `revisor_tool.py`, `revisor_hook.py`.
- **Estado:** **concluído → virou infraestrutura** — motivo: a PoC foi promovida
  à tool `revisor_code` do MCP `mcp-lab-universal`; o hook roda via systemd
  socket activation e **está ativo hoje**.
- **Serviços:** systemd --user `revisor-hook.socket` + `revisor-hook.service`
  (enabled), porta **127.0.0.1:8787** respondendo.

---

## 3. Lacunas e inconsistências

### 3.1 Nomes divergentes (pasta × RAG × Supabase × ObSV)

| Pasta | RAG (tag) | Supabase (`projects`) | ObSV (caminho) |
|---|---|---|---|
| `lab-b/smartsearck` | `smartcam` | `smartcam` | `01-Projetos/smartcam/` |
| `lab-b/obs` | `obsv` | `obsv` | `01-Projetos/ObSV-IMPLEMENTATION_PLAN.md` |
| `lab-a/arquivo` e `lab-a/automacao_padroeira` | `restaurante` | `padroeira` | `01-Projetos/Padroeira-aut-v1.md`, `01-Projetos/Reconciliacao-Fiscal-V2/` |
| `lab-b/ominiroute` | — | — | `09-Referencias/OmniRoute.md` |
| `lab-z/revisor`, `lab-z/regente`, `lab-z/polyglot-swarm` | `lab-z` (agregador) e `regente-generator-ai-studio` | **sem linha** | `02-Laboratorios/Regente.md` |
| `lab-b/qwenchat` | doc taggado **`promptforge`** | — | — |

Regra do AGENTS.md ("use sempre o mesmo identificador nos três sistemas") está
violada em **6 casos**; o caso mais grave é `smartsearck` (nome com typo) vs `smartcam`.

### 3.2 Projetos duplicados / candidatos a duplicata
1. **`lab-a/arquivo` ↔ `lab-a/automacao_padroeira/aut-v1`** — mesmos módulos
   (`cortex_padroeira.py`, `engine_consolidacao.py`, `motor_balancete.py`);
   `arquivo/` está gitignorado e parado desde 10/09, `aut-v1` está ativo.
2. **`lab-z/polyglot-swarm/run_swarm.py` ↔ `lab-z/regente/run_swarm.py`** —
   homônimos com hashes diferentes (11.069 B vs 17.085 B), sem git para medir a linhagem.
3. **`lab-b/prompts/promptforge/` ↔ `lab-b/promptforge/`** — mesma palavra,
   naturezas distintas (pastas de saída × código).
4. **`lab-b/generator`** — declarado como migrado para cá, mas o código não está
   em lugar nenhum de `lab-b` (backup antigo em `archive/backup/generator_prototipo_2026-07-30/`).

### 3.3 Docs órfãos / mal taggados (RAG)
- `doc_1290cc…` — README do **qwenchat** taggado como projeto **`promptforge`**.
- `doc_5154a455…` — "Verificação Final — Kg Equivalente (aut-v1)" com
  `project = (sem projeto)` (o texto cita `restaurante`).
- `doc_74c757b5…` e `doc_93586dbd…` — Perplexica com `project = (sem projeto)`.
- `listar_projetos` reporta **4** documentos sem projeto, mas o filtro devolve
  **3** ⇒ 1 documento sem tag não foi localizado (ver Pergunta 6).
- `doc_1`, `doc_4`, `doc_8` (tag `infraestrutura`) estão marcados como
  "[REVISAR - placeholder legado, conflita com Inventario-Portas-Servidor.md]".
- Tags de projeto na RAG que **não correspondem a nenhuma pasta** dos labs:
  `arr-stack-diagnostico`, `gestao-midia`, `lab-e`, `opencodex`,
  `opencodex-config-cleanup`, `osint`, `perplexica`, `redes-docker-mtu-regra`,
  `teste-forge`, `teste-forge-mistral`, `teste-mistral`, `work_out`.
- Tags de pasta **sem nenhum documento**: `API+Doctor`, `lab-clients`,
  `MCP_Bridge`, `minerador`, `ominiroute`, `sessions`, `target`, `polyglot-swarm`.

### 3.4 Supabase (lab-g)
- **Consulta ao vivo falhou:** não há MCP `supabase` nesta sessão e a REST API
  respondeu **HTTP 401** com a anon key embutida em `scripts/supabase_export_obsv.py`.
  Fonte usada: **snapshot local** `knowledge/00-Inbox/Supabase_Import/`
  exportado em **2026-09-18 22:48** (ver Pergunta 4).
- `projects` tem linhas para `lab-a`, `lab-b` (labs), mas **não para `lab-z`**.
- `project_status` de `lab-a` e `lab-b`: `status=active`, `phase=unknown`,
  `progress=0`, summary "status a ser preenchido" → **lab sem status real**.
- Linhas de projeto que casam com pasta: `padroeira` (active/97),
  `smartcam` (active/35), `obsv`. Nenhuma pasta tem linha própria com o nome da pasta.
- `handoffs` (5 no snapshot): `lab-a` (1), `padroeira` (2, ambas `pending`),
  `inventario-cli` (1), `smartcam` (1).

### 3.5 Git
- **lab-z inteiro não é versionado.**
- `lab-a`: `arquivo/` e `automacao_padroeira/aut-v0/` no `.gitignore` ⇒ histórico perdido.
- `lab-b`: 4 pastas de primeiro nível sem nenhum arquivo rastreado
  (`API+Doctor`, `generator`, `MCP_Bridge`, `ominiroute`) — e sem estar no
  `.gitignore`, ou seja, **"fantasmas"**: não são rastreadas nem declaradas como ignoradas.
- `smartsearck`: gitlink sem `.gitmodules` ⇒ submódulo quebrado e ` M smartsearck` permanente.
- Trabalho sujo não commitado: lab-a 20 entradas · lab-b 16 entradas
  (inclui 6 arquivos do `minerador` e 4 do `obs`).

### 3.6 Serviços fora do esperado
| Serviço | Esperado | Real |
|---|---|---|
| `lab-b/generator` :8092 | lab-master `important/optional` | **fora do ar** (código ausente) |
| `minerador` :8000 | systemd `enabled` | **dead** desde 2026-09-29 00:28 |
| `MCP_Bridge` :8001 | — | **no ar** (container), mas código local ausente |
| `lab-z/regente` | lab-master recurso | nenhum processo `regente_console` |
| `revisor-hook` :8787 | socket activation | **no ar** |
| `obsv` :8777 | systemd user | **no ar** |

### 3.7 Segredos expostos (apenas caminhos, sem valores)
- `segredo em lab-a/arquivo/.env`
- `segredo em lab-a/automacao_padroeira/aut-v1/.env`
- `segredo em lab-b/generator/.env`
- `segredo em lab-b/minerador/.env`
- `segredo em lab-b/ominiroute/omniroute/.env`
- `segredo em lab-b/promptforge/.env`
- `segredo em lab-b/qwenchat/.env` (+ README documenta exposição anterior de chaves em terminal)
- `segredo em lab-b/smartsearck/.env`
- `segredo em lab-b/smartsearck/data/key.pem` (chave TLS; **não** está no git)
- `segredo em lab-a/.aider.chat.history.md` e `segredo em lab-b/smartsearck/.aider.chat.history.md` (histórico de chat)
- Fora dos labs, mas relevante: `segredo em scripts/supabase_export_obsv.py` (credencial embutida no código),
  `segredo em .claude/settings.local.json`, `segredo em knowledge/.obsidian/plugins/obsidian-local-rest-api/data.json`
- **Não está no git:** apenas `promptforge/.env.example` (placeholder) está versionado.
  Nenhum `.env` foi encontrado no index de `lab-a` ou `lab-b`.

---

## 4. Perguntas para o Paulo

1. **Caminho de saída.** O prompt manda gravar em `/work_out/INVENTARIO_LAB.md`,
   mas `/work_out` não existe; a raiz real é `/home/teco/work_out`. Gravar aqui
   está correto, ou quer um symlink `/work_out`?
2. **O que conta como "projeto"?** `lab-b/sessions` e `lab-b/target` são artefatos
   (logs e build) e `lab-b/prompts` é pasta de dados gerados. Incluo os três na
   Fase 1 (README/STATUS) ou excluo?
3. **O que houve com `API+Doctor`, `generator`, `MCP_Bridge` e `ominiroute`?**
   As quatro pastas não têm código-fonte (só caches/configs), não estão no
   `.gitignore` e não têm registro em RAG/Supabase/ObSV. São restos de migração,
   devem ser apagadas, ou o código está em outro lugar que eu não encontrei?
   Especialmente `generator`: RAG e lab-master dizem que ele vive em
   `lab-b/generator` com porta 8092, mas o módulo `generator.server` não existe.
4. **Supabase ao vivo.** Não havia MCP `supabase` nesta sessão e a REST retornou 401.
   Usei o snapshot local de 2026-09-18. Posso confiar nele como fonte para a Fase 1,
   ou você quer me passar um acesso (MCP/credencial) para consultar `projects`,
   `project_status` e `handoffs` em tempo real?
5. **Nome canônico de `smartsearck`.** A pasta tem typo (`smartsearck`), mas RAG,
   Supabase, ObSV e o repositório remoto usam `smartcam`/`Smartsearch-`. O README/STATUS
   da Fase 1 deve usar o nome da pasta (regra do prompt) ou o nome canônico das fontes?
6. **Documento sem tag não identificado.** `listar_projetos` diz 4 documentos sem
   projeto; o filtro devolve 3. Quer que eu caçe o quarto antes da Fase 1?
7. **lab-z sem git.** Nenhum dos 3 projetos do lab-z está versionado. Criar um repo
   para `lab-z` é escopo da Fase 1 ou fica para depois?
8. **Submódulo quebrado do `smartsearck`.** `lab-b` registra o gitlink mas não tem
   `.gitmodules`, e o ponteiro está desatualizado. Posso tratar como "git ✅ com aviso"
   no STATUS, ou isso é um item de correção separado?
9. **Escopo de "serviços".** Mapeei serviços via `lab-master/config/resources.yaml`,
   `systemctl --user`, `docker ps` e portas. Algo fora disso que deva constar no STATUS?

---

*Fim da Fase 0 (texto original preservado; continua em §5–§6).*

---

## 5. Fase 0b — STACKS (`/opt/stacks`, somente leitura, 2026-09-30)

24 pastas de primeiro nível (+ 1 tarball de backup do lab-master e 1
`.pytest_cache`). Nenhuma escrita foi feita aqui. Classes:
**(a)** projeto próprio (código do lab) · **(b)** stack de terceiros
(só compose/config) · **(c)** infra do lab · **(dados)** diretório de
dados/volume, não projeto.

### 5.1 Tabela resumo

| # | Pasta | Classe | README | git | Serviço / portas | Estado | Projeto de lab ligado |
|---|---|---|---|---|---|---|---|
| S01 | `agent-test-lab` | (a) | ❌ (tem `results/FASE5_RELATORIO.md`) | ❌ | compose `deepseek-harness`+`verifier` (python:3.11-slim), sem container | parado | Atlas (conceitual) |
| S02 | `atlas-viewer` | (a) | ✅ | ❌ | `atlas-viewer` (nginx:alpine) **:8080 UP** | ativo | raiz `work_out` (`atlas-viewer-README.md`, `docker-compose-viewer.yml`, `nginx.conf` — config duplicada, ver §5.3) |
| S03 | `buscador` | (b) | ❌ | ❌ | `seerr` **:5055 UP** | ativo | — |
| S04 | `dockge` | (b) | ❌ | ❌ | `dockge` **:5001 UP** | ativo | — (gestão) |
| S05 | `flame` | (dados) | ❌ | ❌ | só `data/` = volume do serviço `flame` (ver S16) | n/a | — |
| S06 | `fotos-videos` | (b) | ❌ | ❌ | photoprism :2342 + mariadb, sem container | parado | — |
| S07 | `gestao-midia` | (b) | ❌ | ❌ | prowlarr :9696, sonarr :8989, radarr :7878, lidarr :8686 — **todos UP** | ativo | — |
| S08 | `hermes_core` | (b) | ❌ | ❌ | n8n custom (docker-in-docker) :5678, sem container | parado | — |
| S09 | `intel-1` | (b) | ❌ | ❌ | `ai_brain` (ollama) :11434, glances, scrutiny :8008 — **tudo parado** | **parado (impacta promptforge/qwenchat)** | `lab-b/promptforge`, `lab-b/qwenchat`, `lab-b/lab-clients` (consomem Ollama) |
| S10 | `lab-master` | (c) | ✅ | ⚠️ repo vazio (sem commits) | API :9100 + container **UP** | ativo | todos (é o gerente: `config/resources.yaml`) |
| S11 | `langflow` | (b) | ❌ | ❌ | langflow :7860, sem container | parado | — |
| S12 | `limpador` | (b) | ❌ | ❌ | `cleaner` (alpine, `restart: no`, limpa logs' arr/bazarr/plex/docker) | parado por desenho | mídia/stacks |
| S13 | `mcp-bridge` | (a) | ✅ + `docs/` | ❌ | código real (`mcp_server.py` etc.) + container **UP :8001**, OAuth PKCE | ativo | **é o código ausente de `lab-b/MCP_Bridge`** (resolve fantasma §3.5) |
| S14 | `mcp-lab` | (a) | ❌ (tem `PERPLEXICA.md`) | ❌ | `server_final.py` + container **UP :8765** = mcp-lab-universal (RAG+mem0) | ativo | todos (é o backend de RAG/memória) |
| S15 | `mcp-superassistant-proxy` | (b) | ❌ | ❌ | proxy node :3007, sem container | parado | — |
| S16 | `meu-painel` | (b) | ❌ | ❌ | `flame` **:3001 UP** | ativo | — |
| S17 | `n8n` | (dados) | ❌ | ❌ | só `n8n_data/` legado (`hermes_core` usa o próprio) | n/a | — |
| S18 | `osint` | (a) | ✅ | ✅ `Thesco19/teco-osint-stack` (2026-09-25) | spiderfoot **UP** (+ theharvester/maigret cli) e backend `@lab/atlas` (`osint_query` + 29 tools) | ativo | Supabase `Stack_OSINT` |
| S19 | `perplexica` | (a/b) | ✅ (upstream) | ✅ (2026-09-26; remote = upstream `ItzCrazyKns/Perplexica`) | `vane` + maths + serpapi-search **UP** (:8081) | ativo | ObSV `01-Projetos/perplexica/` |
| S20 | `playwright-mcp` | (b) | ✅ | ❌ | container **UP :3002→3000** | ativo | — (automação) |
| S21 | `plex` | (b) | ❌ | ❌ | container **UP :32400** | ativo | — |
| S22 | `suporte-midia` | (b) | ❌ | ❌ | flaresolverr **:8191 UP** + bazarr + auto-translate UP | ativo | — |
| S23 | `transam` | (b) | ❌ | ❌ | transmission **:9091 UP** | ativo | — |
| S24 | `vaultwarden` | (b) | ❌ | ❌ | :8222, sem container | parado | — |

Sem README: 17 de 24 (têm: `atlas-viewer`, `lab-master`, `mcp-bridge`,
`osint`, `perplexica`, `playwright-mcp`, + relatório em `agent-test-lab`).
Com git: 3 (`lab-master` vazio; `osint`; `perplexica`).
Com container no ar: 14 pastas. Parados: 8. Só-dados: 2.

### 5.2 Cruzamento STACKS × RAG / Supabase / ObSV (somente leitura)

| Stack | RAG | Supabase (snapshot 18/09) | ObSV |
|---|---|---|---|
| `agent-test-lab` | — | — | — |
| `atlas-viewer` | ⚠️ tag `atlas` (conceitual) | ⚠️ linha `Atlas` | — |
| `buscador`, `dockge`, `fotos-videos`, `meu-painel`, `plex`, `transam`, `vaultwarden`, `langflow`, `hermes_core`, `limpador`, `mcp-superassistant-proxy`, `playwright-mcp` | — | — | inventários `03-Infraestrutura/` |
| `gestao-midia` | ✅ tag `gestao-midia` (1) | — | inventários |
| `intel-1` (ai_brain/ollama, glances, scrutiny) | — | — | inventários + `VAIO_AUDITORIA_001` |
| `lab-master` | ⚠️ doc `lab-b/generator` cita `resources.yaml` | — | inventários |
| `mcp-bridge` | — | — | inventários |
| `mcp-lab` | — (é o servidor, não conteúdo) | ✅ linha `mcp-lab-universal-admin` | ✅ `01-Projetos/mcp-lab-universal-admin.md` + inventários |
| `osint` | ✅ tag `osint` (2) | ✅ `Stack_OSINT` + status `osint` | ✅ `01-Projetos/osint-stack.md` |
| `perplexica` | ✅ tag `perplexica` (1) + 2 sem tag | — | ✅ `01-Projetos/perplexica/perplexica-fts5-concluido.md` + inventários |

### 5.3 Lacunas e duplicidades das stacks

1. **Fantasma resolvido:** `lab-b/MCP_Bridge` (sem código) ↔
   `/opt/stacks/mcp-bridge` (código real + container UP). O deploy vive na stack.
2. **Config duplicada:** `atlas-viewer` tem compose/nginx na stack **e**
   arquivos correlatos na raiz do `work_out`
   (`atlas-viewer-README.md`, `docker-compose-viewer.yml`, `nginx.conf`, `atlas.ts`).
3. **`intel-1` parado:** sem Ollama (`ai_brain`), o `forge` de `promptforge`/`qwenchat`
   (modelos `mistral-nemo:12b`/`qwen`) não tem backend local.
4. **Recursos do LM sem pasta em `/opt/stacks`:** `tradutor` (:5000/:9001,
   sem container), `opencodex` (npm global + systemd, sem pasta), `ai_brain`/
   `system_monitor`/`scrutiny` (serviços dentro de `intel-1`), `n8n`
   (serviço em `hermes_core` + pasta legada `n8n/`).
5. **`lab-master/.git` vazio** (branch sem commits) — infra crítica sem versionamento.
6. **`perplexica` é fork funcional do upstream** (`ItzCrazyKns/Perplexica`) com
   commits locais (roteamento autônomo 2026-09-26) — divergência futura do upstream.
7. **Segredos (só caminhos):** `segredo em /opt/stacks/<buscador,fotos-videos,
   gestao-midia,hermes_core,intel-1,langflow,limpador,mcp-bridge,mcp-lab,
   meu-painel,osint,perplexica,suporte-midia,transam,vaultwarden>/.env`
   (15 arquivos) + `segredo em /opt/stacks/meu-painel/compose.yaml`
   (senha padrão no corpo do compose).
8. **Timers/cron (pergunta 9):** nenhum timer user, nenhum cron do teco;
   timers de sistema: só `lab-master-ensure-helper.timer` (a cada minuto) é do lab.

### 5.4 Perguntas novas (Fase 0b)

- **B1.** `flame/` e `n8n/` são só dados — mantê-los como "pastas de stack" no
  inventário ou documentar como volumes e ignorar na Fase 1?
- **B2.** Qual nome canônico para as stacks sem README (17/24)? Vale o nome da
  pasta ou o `project:` do LM (ex.: `buscador`↔seerr, `meu-painel`↔flame,
  `transam`↔transmission)?
- **B3.** `intel-1` (Ollama) deve voltar ao ar antes da Fase 1, ou o forge passa
  a usar outro backend?
- **B4.** `tradutor` (LM, sem pasta/container) é recurso morto ou vive em outro lugar?

---

## 6. Atualizações pós-Fase 0 (2026-09-30)

### 6.1 Rename `smartsearck` → `smartcam` (executado)

- **Pré-checagem (só leitura):** referências encontradas — `resources.yaml:329`
  do LM (`start_command`), `run-smartcam.sh` (`cd …/smartsearck`), gitlink do
  `lab-b`, docs do ObSV (`smartcam-fase*.md`) e da RAG (doc do resumo técnico).
  Nada ambíguo. Systemd, cron, timers, docker e `.env`/`dist` **não** referenciavam
  o caminho. Sem venv python (só `node_modules`, caminhos relativos).
- **Backup:** `/tmp/opencode/backups/smartcam-pre-rename-20260930.tar.gz`
  (56 MB, 11.383 arquivos).
- **Serviço:** parado antes (tsx + `yolo_sidecar.py` + esbuild; health `:3100`
  ok no baseline) e subido depois pelo launcher atualizado.
- **Mudanças:** `mv` + symlink temporário (removido após validação);
  `resources.yaml:329` → `…/lab-b/smartcam/run-smartcam.sh`;
  `run-smartcam.sh` → `cd …/lab-b/smartcam`; gitlink corrigido em `lab-b`
  (`ba2b45b`: `smartcam`→`e33f771` = HEAD local; `e583ae8`: remoção do symlink).
  Remoto `Smartsearch-` **intacto** (nenhum fetch/push).
- **Validação:** processo `tsx server.ts` rodando **do caminho novo**,
  health `:3100` ok (igual ao baseline, com chave/auth), `:3443` → 200,
  LM `/api/status` → `smartcam` state **ON**, `ports_open` [3100, 3443].
  `yolo_sidecar.py` é lazy (`yoloEnsure()` em `server.ts`) — ausência
  pós-restart é normal.
- **Sobrou:** `run-smartcam.sh` modificado e **não commitado** no repo interno
  (`M smartcam` no `lab-b`); `.bak` do LM, docs RAG/ObSV e remoto, **intocados**
  de propósito. → **Perguntas 5 e 8 do §4, resolvidas.**

### 6.2 Deliberações do Paulo sobre as perguntas do §4

- **P1 (caminho):** manter `/home/teco/work_out`, sem symlink `/work_out`. *(aplicado)*
- **P2 (o que é projeto):** `sessions`, `target` e `prompts` **não** são projetos:
  sem STATUS; entram numa seção "artefatos" do README do `lab-b` (Fase 1);
  `target` e `sessions` já estão no `.gitignore` (verificado). *(nada a fazer agora)*
- **P3 (fantasmas):** não apagar. `MCP_Bridge` confirmado como deploy
  (`/opt/stacks/mcp-bridge`, §5.3 item 1). `generator`/`ominiroute`/`API+Doctor`
  seguem "aguardando decisão" para a Fase 1.
- **P4 (Supabase):** snapshot de 18/09 vale para **leitura** na Fase 1, não para
  escrita de estado (Fase 1 roda com agente que tenha o MCP do Supabase).
  Item separado: remover a credencial embutida de `scripts/supabase_export_obsv.py`.
- **P6 (doc sem tag):** caçar o 4º documento dentro da Fase 1, na etapa de retag.
- **P7 (git no lab-z):** repo criado **sem** o primeiro commit — bloqueado pelo
  gate, ver §6.3.
- **P9 (serviços):** escopo mantido + timers/cron (levantados no §5.3 item 8).

### 6.3 Git do lab-z: repo inicializado, commit BLOQUEADO pelo gate

- `.gitignore` criado com o conteúdo especificado
  (`.env`, `**/.env`, `venv/`, `.venv/`, `*.pem`, `.aider*`); `lab-z/` já é
  ignorado no repo `work_out` (`.gitignore:57`), então nada vaza para cima.
- `git init` executado; `git status` lista 7 entradas (3 pastas + 3 `.md` + `.gitignore`).
- **Gate FALHOU — nenhum commit foi feito:**
  1. `regente/quarantine/` (2,3 GB — cópias forenses de perfil de navegador,
     fotos de família `.avi`, `manifest.json` de 50 MB+) entraria no commit;
  2. rechecagem binária confirmou **padrões fortes de segredo em 3 arquivos** do
     `quarantine/` (2× `private_key`, 1× `bearer_jwt` em LevelDB do Opera);
  3. ruído pesado também entraria: `regente/.opencode/node_modules` (63 MB),
     `__pycache__`/`.pytest_cache` vários.
- Estado atual totalmente reversível (repo sem HEAD + `.gitignore` untracked).
- **Para liberar:** dizer se `quarantine/` sai do repo (recomendado: mover para
  fora de `lab-z` ou adicionar ao `.gitignore`) e se entram também
  `__pycache__/`, `.pytest_cache/`, `.opencode/node_modules` no ignore.

---

*Inventário atualizado em 2026-09-30: rename smartcam executado e validado,
Fase 0b (/opt/stacks) anexada, repo lab-z inicializado sem commit.
Fase 1 NÃO iniciada (aguarda template do Paulo).*

### 6.4 Gate do lab-z liberado + piloto da Fase 1 (2026-09-30 11:12)

- **Gate:** `regente/quarantine/` (2,3 GB) movido para
  `/home/teco/quarantine-regente/` (fora do repo, **não apagado**; proibido
  entrar na RAG e no ObSV). `.gitignore` ampliado (`quarantine/`,
  `__pycache__/`, `.pytest_cache/`, `.opencode/node_modules/`).
  Re-checagem binária da árvore restante: **zero padrões fortes de segredo**.
  Primeiro commit feito: `da3eedf` ("commit inicial do lab-z"), **sem remoto**.
- **B1–B4 aplicadas:** `flame/` e `n8n/` são volumes (README da stack dona na
  Fase 1); nome de pasta vale como canônico (+ linha de mapeamento no README);
  `intel-1` parado sem bloquear; `tradutor` = "aguardando decisão" (só leitura).
- **Piloto Fase 1 (sem commits, aguarda revisão):**
  `lab-b/smartcam/STATUS.md`, `lab-b/obs/STATUS.md`,
  `lab-a/automacao_padroeira/README.md` e `STATUS.md` criados.
  READMEs existentes (`smartcam`, `obs`) preservados. Estados reverificados
  na hora: bot `padroeira` rodando, smartcam health ok, `obsv-bridge` active.

### 6.5 Etapa 2 executada (2026-09-30, piloto aprovado)

- **Ajustes do piloto aplicados:** `obs/STATUS.md` com Pretende/Fez/Conclusão
  separados; linha em branco antes de `## Log` em todos; Ficha acrescentada
  (só acréscimo) a 12 READMEs: `smartcam`, `obs`, `minerador`, `promptforge`,
  `qwenchat`, `regente`, `revisor`, `osint`, `lab-master`, `mcp-bridge`,
  `atlas-viewer`, `playwright-mcp`. `perplexica` (upstream) intocado.
- **Arquivos novos:** README+STATUS de `arquivo`, `lab-clients`, `MCP_Bridge`,
  `polyglot-swarm`; STATUS de `minerador`, `promptforge`, `qwenchat`,
  `regente`, `revisor`, `API+Doctor`, `generator`, `ominiroute`;
  `lab-b/README.md` (com seção Artefatos); `lab-z/STATUS.md` (item
  `lab-z/CLAUDE.md` = aguardando decisão); README+STATUS de 12 stacks com
  escrita (`agent-test-lab`, `mcp-lab`, `hermes_core`, `langflow`,
  `mcp-superassistant-proxy`, `plex`) + STATUS de `atlas-viewer`,
  `lab-master`, `mcp-bridge`, `osint`, `perplexica`, `playwright-mcp`.
- **Bloqueados sem escrita (pastas root, sem sudo):** `buscador`, `dockge`,
  `fotos-videos`, `gestao-midia`, `intel-1`, `limpador`, `meu-painel`,
  `suporte-midia`, `transam`, `vaultwarden` — conteúdos prontos em
  `/tmp/opencode/etapa2-bloqueados/<stack>/README.md|STATUS.md` para aplicar.
- **Commits (sem push):** smartcam `62f61fb` (fix rename) + `41d6d07` (docs);
  `lab-b` `5012adb` (gitlink) + `b731f48` (docs, 15 arquivos);
  `lab-a` `d08d0fe` (automacao; `arquivo/` ignorado, fora do commit);
  `lab-z` `6622aa8` (gate re-rodado, limpo); `osint` `8dbafa8`;
  `perplexica` `e304ebf` (**detached HEAD** — repo já estava detached).
  Não commitado de propósito: `minerador/README.md` (Ficha somada a
  modificações alheias), 4 arquivos do `obs` (testes falharam, ver abaixo).
- **Testes `obs`:** 559 passed, **3 failed** (`test_config.py::DoctorTests` —
  `test_healthy_config_returns_exit_ok`, `test_json_output_is_valid_json`,
  `CLIDoctorTests::test_doctor_with_valid_vault`). Código do Mapa Mental
  NÃO commitado, conforme regra.
- **`tradutor` (só leitura):** recurso **removido** do `resources.yaml` hoje
  (13:30; entraram `atlas-viewer` e `minerador`); portas 5000/9001 fechadas;
  sem unit systemd; sem pasta. Nada mexido. Estado sugerido: aguardando
  decisão (provável recurso morto — confirmar).
- Tabela §1 atualizada (README/STATUS pós–Etapa 2).

### 6.7 Descontaminação fiscal dos .md de agentes (2026-09-30)

- Diagnóstico (só leitura): 14 arquivos idênticos (template Padroeira,
  n=17) em `lab-a/`, `lab-z/`, `arquivo/`, `automacao_padroeira/`, `obs/`,
  `regente/`, `polyglot-swarm/` + 1 variante (`polyglot-swarm/CLAUDE.md`
  com seção própria `revisor_code`, escopo só do projeto). Topo (`/`,
  `~`, `/opt`), raiz `work_out`, `lab-b/` e stacks: limpos.
- Correção (mover, nunca apagar; backup em `~/md-bak-20260930/`, 90 arquivos;
  md5 confirma `lab-a/` idêntico a `automacao_padroeira/`): stub
  ("Contexto deste projeto…") em 90 arquivos de `lab-a/`, `lab-z/`,
  `arquivo/`, `obs/`, `regente/`, `polyglot-swarm/` (seção `revisor_code`
  preservada); `automacao_padroeira/` intocado; sync re-rodado (90 updates).
- Verificação: 141 arquivos fora de `automacao_padroeira/` todos em n=3
  residual (só as palavras do próprio stub) e **zero** com conteúdo
  substantivo (`reconcilia|sangria|NFe|Kg Eq|Telegram|restaurante`).
- Commits (sem push): `lab-a` `3d62bf3`, `lab-b` `7512eae` (33 arquivos;
  `obs/Mapa-do-Lab.mmd` untracked excluído do commit), `lab-z` `410438b`.

### 6.6 Pós–Etapa 2: pendências resolvidas + Fase 2A (2026-09-30)

- **P1 (stacks root):** conteúdos copiados para `~/etapa2-bloqueados/` (o
  `/tmp` é volátil). **Sem sudo nesta sessão** (`sudo -n` pede senha) → o
  loop `cp -n` + `chown` **não** foi executado; precisa do Paulo ou root.
- **P2 (obs):** os 3 `DoctorTests` **falham também no HEAD limpo**
  (worktree temporária, removida depois) → pré-existentes e alheios ao Mapa
  Mental → commit `adbdad8` feito, com as falhas anotadas no STATUS.
- **P3 (minerador):** Ficha isolada via patch e commitada limpa (`fff7830`,
  9 ins); uma varredura acidental da linha alheia foi desfeita e verificada
  (0 ocorrências no commit).
- **P4:** branch `lab-docs` → `e304ebf` criada no perplexica (sem push).
- **P5:** diff completo `.bak`×live confirma só +`atlas-viewer`,
  +`minerador`, −`tradutor` (+ linha `smartcam` da Fase 1 e 1 cosmética).
  `tradutor` registrado no STATUS do LM como **removido em 30/09**.
- **2A-0 (só leitura):** vault ObSV **limpo** (sem token/fragmento; só o nome
  do script em `01-Projetos/Padroeira-aut-v1-Performance.md`); RAG tem o
  token exposto em `doc_04e04789…` (tag `restaurante`) → **limpar antes da 2B**.
- **2A (protocolo):** `PROTOCOLO_LAB.md` criado + `scripts/sync-protocolo.sh`
  (idempotente, `--check`, backup espelhado em `~/protocolo-bak-<TS>/`,
  nunca toca em knowledge/archive/caches/venvs). Executado: **150 alvos,
  149 atualizados + 1 já sincronizado, 0 erros**; bloco md5-idêntico em
  todos; zero linhas removidas fora dos marcadores. Achado e corrigido um
  bug no script (`pipefail` + `head`). Sem commits; sem escrita em
  RAG/Supabase/ObSV.
