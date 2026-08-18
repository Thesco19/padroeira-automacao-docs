# Regente — Orquestrador Headless de Agentes de IA

> Laboratório: `lab-z` · Projeto: `regente` (`/home/teco/work_out/lab-z/regente`)
> Resumo técnico verificado em **2026-08-04** · Fontes ao vivo (leitura + suíte pytest: **83 passed, 25.32s**)

---

## Objetivo

Orquestrar um **enxame de agentes de IA (polyglot-swarm)** a partir de um
blueprint YAML, de forma **headless** e com **estado**: o orquestrador decide
*quem* executa, *em que ordem*, *com que paralelismo* e *com quais retries* —
usando múltiplas CLIs de IA (claude, gemini, aider, jcode, kilo, pi, codex,
opencode) como ferramentas subjacentes, com um **fallback unificado** para o
gateway local OpenAI-compatível **OmniRoute** quando uma CLI falha.

Ao lado do orquestrador, o projeto abriga um **produto web** desacoplado —
o **AI Generator Universal** (`generator/`) — e uma **camada de ações
destrutivas seguras de arquivo** (PLAN/BUILD em quarentena). O Regente é o
"condutor" do laboratório: dado um objetivo, planeja (architect), executa
(fila com dependências) e sintetiza (Fase 3), persistindo tudo em cache,
checkpoints, memória semântica e diário no Supabase.

---

## Arquitetura

Pipeline em **3 fases** dirigido por um blueprint YAML:

```
blueprint YAML (missão)
        │
        ▼
┌─ FASE 1 · Planejamento ─────────────────────────────────────────┐
│  agent "architect" (se definido) gera plano JSON dinâmico        │
│  fallback → lista estática dos agentes do YAML                   │
└──────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─ FASE 2 · Execução ──────────────────────────────────────────────┐
│  AgentQueue (prioridade + depends_on + max_workers)              │
│    └─ por agente: StateMachine + retries (backoff exponencial)   │
│    └─ run_agent_cli → CLI de IA  → falhou? → fallback OmniRoute  │
│    └─ checkpoint a cada agente concluído (resume possível)       │
└──────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─ FASE 3 · Síntese ───────────────────────────────────────────────┐
│  agente synthesis → resumo final → cache/latest_execution.json   │
└──────────────────────────────────────────────────────────────────┘
```

Princípios estruturais aplicados:

- **Camada de orquestração desacoplada do produto**: `regente.py` (enxame)
  e `generator/` (produto) NÃO importam um do outro — ambos consomem o pacote
  neutro `shared/` (regra `ARCHITECTURAL_DECOUPLING`, decisão P0).
- **Protocolo `(success, content)`**: toda chamada de agente retorna par
  explícito de acerto/erro; sem exceções silenciosas nem retornos ambíguos.
- **Semântica rigorosa de terminal**: `SKIPPED` (não configurado / recusa /
  dependência falha) ≠ `FAILED` (configurado errado / erro real); timeouts
  distinguidos por prefixo `[TIMEOUT]`.
- **Supabase não-bloqueante**: sem `SUPABASE_SERVICE_ROLE`, eventos viram
  log DEBUG e a missão segue.
- **Ações de arquivo nunca destrutivas diretas**: PLAN (scan read-only) →
  BUILD (move para quarentena + manifesto) → RESTORE (devolve).

---

## Componentes

### Núcleo (`regente.py`, 1784 linhas, v2.1.0)
| Componente | Responsabilidade |
|---|---|
| `StateMachine` | Estados por agente (`PENDING→SCHEDULED→RUNNING→SUCCESS/FAILED/…`), transições validadas, histórico, tempo de execução, retries |
| `AgentQueue` | Fila por prioridade (`heapq`), `depends_on`, paralelismo (`max_workers`), detecção de stall/ciclo, aborto via `fail_fast` |
| `SemanticMemory` | Embeddings (`sentence-transformers`) + fallback por palavras-chave; dedup por `content_hash`; persistência `metadata.json`/`vectors.json` 1:1 |
| `CheckpointManager` | Salva/restaura estado (`--resume`), escrita atômica (`.tmp` + `rename`), lista/limpa checkpoints |
| `RegenteOrchestrator` | Orquestra as 3 fases; injeta credenciais no env do subprocess; `on_approval_request` para o fluxo `[S/n]` |
| `run_agent_cli` | `build_cli_command` por tool; timeout prefixado; fallback OmniRoute via `shared/` |
| `record_supabase_event` | Diário `regente_events` (MISSION_START…MISSION_COMPLETE) |

### Console TUI (`regente_console.py`, 767 linhas)
- 1 processo Python, 3 painéis `rich` (CHAT / MCPs / STATUS).
- Reutiliza 100% a camada de orquestração (não duplica).
- Missões de chat viram blueprints (`architect` = `opencode-plan`; `synthesis` = `opencode-review`), fila FIFO.
- `[S/n]` roteado via metadata estruturada (`on_approval_request`), sem regex em stdout.
- Healthchecks de MCP configuráveis (campo `healthcheck` → `~/.config/regente/mcp-healthchecks.json` → defaults → inferência por tipo).

### Ações de arquivo (`planner.py`, 578 linhas) — Fase 6
- `--scan-fs` / `--scan-fast` (duplicatas por sha256 ou via report `fdupes`; candidatos a inútil por categoria).
- `--build-from-plan`: move **apenas** itens `approved:true` para `quarantine/<plan_id>__<ts>/` + `manifest.json`; nunca `os.remove`.
- `--restore-plan`: desfaz o build mais recente.

### Produto desacoplado (`generator/`, v1.0.0) — AI Generator Universal
- FastAPI standalone (porta 8090): geração de capas rap/gangster, img2img, face swap (InsightFace CPU), presets, galeria.
- Providers registrados via `@register_provider` (Civitai, HuggingFace, OpenRouter, Gemini, Pollinations) com **verificação real de chave** antes de ativar; fallback em cadeia → rota livre do Pollinations.
- Fluxo único: `ImagePipeline` → tradução de prompt → geração com fallback → pós-processamento → `~/Pictures/StudioUniversal/`.
- **Status real 2026-08-04**: Civitai `400 insufficientBuzz`, HF `402` sem créditos, Gemini `429` quota free=0, OpenRouter sem chave → **na prática só o Pollinations (rota livre) gera**.

### Infraestrutura neutra (`shared/`, 132 linhas)
- `omniroute_client.py`: cliente único e canônico do fallback OmniRoute (SSE streaming real, `data:` com/sem espaço, erro SSE propagado, deadline absoluto, `tool_model` p/ roteamento por tool). Propriedade de nenhum dos lados.

### V1 legado
- `run_swarm.py` (425 linhas): versão 1, sem estados/fila/memória/checkpoint; semântica documentada preservada no V2.

---

## Tecnologias

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.10+ (stdlib: `argparse`, `threading`, `heapq`, `hashlib`) |
| CLI de agentes | claude, gemini, aider, jcode, kilo, pi, codex, **opencode** (1.18.x, `--format json --pure`) |
| Gateway LLM | **OmniRoute** local (`127.0.0.1:20129`, OpenAI-compat, SSE); LiteLLM Proxy (porta 8000) como rota legada |
| Memória semântica | `sentence-transformers` (`all-MiniLM-L6-v2`), fallback palavras-chave; numpy opcional |
| Persistência | JSON local (cache/checkpoints/memória) + **Supabase** (`regente_events`, `regente_projects`, `regente_steps`) |
| UI | `rich` (TUI); FastAPI + Uvicorn + Web UI estática (produto `generator/`) |
| IA de imagem | Civitai, HuggingFace, OpenRouter, Gemini, Pollinations |
| Testes | pytest (**83 passed, 25.32s**), unittest (`generator/`), runners injetáveis |
| Obsidian | Vault oficial do lab em `/home/teco/work_out/knowledge` (REST API/MCP em `127.0.0.1:27123`/`27124`) |

---

## Riscos

**Críticos / P0**
1. **Fallback OmniRoute sem healthcheck prévio** — assume `127.0.0.1:20129` acessível; erro de conexão é tratado como `False` sem retry dedicado. Se o gateway cair, todo agente "falha" com latência de timeout.
2. **Modelo default `auto/coding` sem fallback de modelo em runtime** — se o OmniRoute passar a recusá-lo, a cadeia inteira de fallback falha (risco já anotado no RESUMO).
3. **Dependência de ambiente local/não-portável** — `~/work_out/lab-z/regente` hardcoded como default (embora configurável por env); `ANTHROPIC_BASE_URL` default `127.0.0.1:8000`; execução em outras máquinas/containers exige env explícito.

**Segurança / dados**
4. **Supabase: RLS permissiva** (`USING true` nas tabelas `regente_*`) e `SUPABASE_SERVICE_ROLE` no orquestrador — aceitável para uso local único, **inaceitável antes de qualquer exposição**.
5. **`--auto-approve` sem trava adicional** (timestamp/lock file) — pendência documentada; um `-y` em contexto errado executa agentes sem confirmação.
6. **Chaves de API em `.env`** (`generator/.env`) e em `~/.claude/settings.json` / LiteLLM config — fora do git, mas sensíveis ao backup/vazamento.
7. **`run_agent_cli` injeta credenciais no env do subprocess** — qualquer CLI de agente lê `ANTHROPIC_*`/`OPENAI_*`; é a intenção, mas amplia a superfície de exposição das chaves.

**Confiabilidade / manutenção**
8. **`regente.py` monolítico (1784 linhas)** — `StateMachine`, `AgentQueue`, `SemanticMemory`, `CheckpointManager`, orquestrador e CLI no mesmo arquivo; acoplamento interno dificulta teste isolado e evolução.
9. **`_resume_from_checkpoint` muta `self.config`** (`agents.pop`) e reconstrói terminal de `results` — retomar com blueprint diferente pode levar a estado inconsistente; idempotência do resume não é totalmente coberta.
10. **`datetime.utcnow()`** (deprecado em Python 3.12+) usado em `StateMachine` e orquestrador — risco de deprecation em versões futuras.
11. **Fase 1 `architect` não valida `tool`** contra `SUPPORTED_TOOLS` antes de rodar; falha vira fallback silencioso para plano estático (comportamento documentado, rastreabilidade limitada).
12. **Tools `kilo`/`pi`/`codex` com flags não validadas** — fallback mínimo `[tool, prompt]`; idempotência/retry não confirmados empiricamente.

**Produto / operacional**
13. **Provedores de imagem majoritariamente inoperantes na prática** (Civitai sem Buzz, HF sem créditos, Gemini quota 0, OpenRouter sem chave) — geração real depende de serviço gratuito de terceiro (Pollinations); qualquer mudança na rota livre quebra o produto.
14. **Quarentena da Fase 6**: 90.343 itens (1,88 GiB) já movidos aguardando revisão/apagamento para liberar espaço; `instalador_baixado` ainda não decidido.
15. **Sem CI/CD**: suíte só roda manualmente; sem lint/type-check automatizado.

---

## Melhorias sugeridas

**Arquitetura / qualidade**
1. **Fatiar `regente.py` em módulos** (`core/state.py`, `core/queue.py`, `core/memory.py`, `core/checkpoint.py`, `runners/`, `cli.py`), seguindo o padrão limpo já usado em `generator/` — reduz acoplamento e viabiliza testes unitários finos.
2. **Healthcheck + retry dedicado do OmniRoute** antes de marcar FAILED; **fallback de modelo** configurável (`auto/coding` → alternativa) quando o gateway recusar o primário.
3. **Migrar `datetime.utcnow()` → `datetime.now(timezone.utc)`** (Python 3.12+).
4. **Validação de schema do blueprint** (`pydantic` ou `jsonschema`) — hoje a validação é mínima (YAML vazio já é tratado, mas campos errados falham no meio da execução).
5. **Checkpoint versionado + schema + não mutar `self.config`** — resume determinístico e auditável.

**Segurança / governança**
6. **RLS no Supabase com políticas por executor/projeto** e uso de chave com privilégio mínimo no orquestrador; rotacionar `SUPABASE_SERVICE_ROLE`.
7. **Trava mínima no `--auto-approve`** (lock file ou janela de timestamp) — item já em pendências.
8. **Inventário de segredos** (`.env` do generator, settings.json, LiteLLM config) com rotação periódica.

**Observabilidade / operação**
9. **CI/CD**: pipeline com `pytest` + `ruff` + `mypy`; evento `TEST_SUITE_RESULT` já é o padrão de evidência — automatizar para cada push.
10. **Métricas estruturadas** (Prometheus/OpenTelemetry) por agente/fase; hoje só há resumo em log + eventos Supabase.
11. **Registrar ADRs no Vault** para as decisões P0 já tomadas (decoupling `shared/`, OmniRoute como fallback definitivo, quarentena PLAN/BUILD, nome do produto) — `knowledge/03-ADR`.
12. **Produto generator**: decidir destino do `instalador_baixado`, apagar quarentena validada, e documentar a limitação real de provedores (ou configurar billing) para o produto não depender de um único serviço gratuito.

**Testes**
13. **Smoke E2E automatizado do fallback OmniRoute** contra o serviço real (o `~/.local/bin/claude-check` já faz a verificação básica — elevar a testes de integração do orquestrador).
14. **Cobertura do `--resume`** com múltiplos cenários (blueprint alterado, agente mid-flight, checkpoint corrompido).

---

## Estado verificado (2026-08-04)

- Suíte `regente`: **83 passed, 0 failed, 0 skipped** (25.32s) — inclui `test_regente`, `test_console`, `test_planner`.
- `regente.py` **v2.1.0** (1784 linhas) · console 767 · planner 578 · `shared/` 132 · V1 `run_swarm.py` 425.
- Quarentena Fase 6: **90.343 itens movidos, 1,88 GiB liberados** (`manifest.json` do plano `c42b498e`).
- `generator/` **v1.0.0** "AI Generator Universal".
- Nó Santuário (mcp-lab-universal) operando; RAG ativo.
- Diretório do projeto não versionado em repo próprio — o repo raiz `/home/teco/work_out` contém apenas ruído de deleções pré-existentes.
