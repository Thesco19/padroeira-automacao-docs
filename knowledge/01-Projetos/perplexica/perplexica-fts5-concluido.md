# Perplexica FTS5 — Concluído (Fases 2-4)

**Status:** ✅ CONCLUÍDO
**Data:** 2026-09-14
**Task Supabase (lab-g):** `0af77c01-19d2-4af5-8fb6-231623044362` — status `completed`
**Donos:** opencode (executor) / supervisão Lab

## Escopo executado

Integração read-only do histórico do Perplexica no MCP Lab Universal
(`/opt/stacks/mcp-lab`), Fases 1-4:

1. **Fase 1 — Validação E2E baseline:** 71/71 checks via MCP real (22 tools),
   27 exemplos unitários.
2. **Fase 2 — Índice FTS5:** pipeline `/opt/stacks/mcp-lab/perplexica_fts_build.py`
   instancia `messages_fts` (fts5 porter unicode61) dentro do próprio
   `db.sqlite`, com populate + 4 triggers de sincronização. Tools
   `search_history`/`find_sources` usam `MATCH` com fallback `LIKE`.
   Suíte: **36 exemplos**.
3. **Fase 3 — Automação de rebuild:** cron `5 4 * * *` no host
   (`perplexica_fts_rebuild.sh`) via container (root:root). Runbook DR
   documentado.
4. **Fase 4 — Homologação de Restore (DR):** dry-run real validado:
   restore do backup → hash baseline `c7b739ae…` → rebuild FTS5 → 36 passed →
   MCP E2E ok.

## Artefatos

| Artefato | Local |
|---|---|
| Build FTS5 | `/opt/stacks/mcp-lab/perplexica_fts_build.py` |
| Wrapper/rebuild | `/opt/stacks/mcp-lab/perplexica_fts_rebuild.sh` |
| Docs (runbook) | `/opt/stacks/mcp-lab/PERPLEXICA.md` |
| Backup pré-build | `/opt/stacks/mcp-lab/backups/perplexica_db.sqlite.bak` (`c7b739ae…`) |
| Testes | `/opt/stacks/mcp-lab/test_perplexica.py` (36 passed) |

## Hash baseline (restore)

`c7b739aebf535212839bd3cf676f0b097abbaf81dad78836a1bbd5fb25a84d7a`

## Referências

- Notas históricas em `Projetos/Perplexica/` (pasta legada)
- Estrutura de dados do Perplexica: `/opt/stacks/perplexica/src/lib/agents/search/researcher/actions/historySearch.ts`