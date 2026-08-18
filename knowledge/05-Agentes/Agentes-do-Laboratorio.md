---
created: 2026-08-18
updated: 2026-08-18
tags: [agentes, catalog, laboratorio, atlas]
tipo: catalogo-agentes
---

# Catálogo de Agentes do Laboratório

Este documento centraliza o catálogo de agentes de IA registrados no ecossistema do laboratório [[Atlas]], suas funções, provedores, modelos e capacidades operacionais.

---

## Estrutura de Agentes Registrados

| Agente | Papel (Role) | Provedor / Gateway | Modelo | Capacidades | Status | Projeto Base |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **[[Claude]]** | Supervisor / Auditor | Anthropic / claude.ai | `claude-sonnet-5` | `supabase_audit`, `rag_ingest`, `security_review` | Online | `inventario-cli` / `lab-central` |
| **[[Claude Code]]** | Coder | Anthropic | `claude-3-opus` | `code`, `analysis`, `documentation` | Registered | `lab-central` |
| **[[Codex]]** | Coder | OpenAI | `codex` / `auto/best-coding` | `code`, `generation` | Registered | `lab-central` |
| **[[JCode]]** | Coder | Multi-provider / Local | Multi-model | `code`, `debug`, pair programming | Registered | `lab-central` |
| **[[OpenCode]]** | Coder / Multi-tool | OpenCode / Gateways | `big-pickle` | `sql`, `files`, `mcp`, `supabase` | Registered | `lab-central` |
| **[[Gemini CLI]]** | Coder / Search | Google | `gemini-pro` / `flash` | `code`, `search` | Registered | `lab-central` |
| **[[ChatGPT]]** | Planner / Assistant | OpenAI | `gpt-4` | `conversation`, `analysis`, `code` | Registered | `lab-central` |
| **[[Kilo]]** | Analyst / Assistant | Multi-provider | Multi-model | `analysis`, `research` | Registered | `lab-central` |

---

## Papéis e Governança Inter-Agentes

1. **Supervisão & Auditoria:**
   - **[[Claude]]**: Responsável pela auditoria de segurança (RLS no Supabase), ingestão RAG e integração nativa com MCP e Supabase.
   - **[[ChatGPT]]**: Atua no planejamento conceitual e arquitetura de auto-organização (idealizador do modelo orbital Atlas).

2. **Execução & Desenvolvimento de Código:**
   - **[[JCode]]**, **[[OpenCode]]**, **[[Claude Code]]**, **[[Codex]]**, **[[Gemini CLI]]**: Agentes executores para tarefas de refatoração, automação, infraestrutura e desenvolvimento.

3. **Coordenação Headless:**
   - Orquestrados pelo enxame [[Regente]] (`lab-z`), que gerencia a fila de prioridades, dependências e fallback unificado para o gateway [[OmniRoute]].

---

## Documentos Relacionados

- [[Codex-Contexto-Operacional]]
- [[Regente]]
- [[LAB-Resumo]]
- [[Inventario-CLI-Gateways]]
