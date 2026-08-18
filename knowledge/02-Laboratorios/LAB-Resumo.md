---
created: 2026-08-04
updated: 2026-08-18
tags: [laboratorio, atlas, estrutura, resumo]
tipo: laboratorio-resumo
---

# Laboratório Atlas — Visão Geral & Arquitetura

## Objetivo

Construir um laboratório de Engenharia do Conhecimento orientado a IA, com memória compartilhada, governança federada via [[Supabase]], documentação centralizada no Obsidian Vault (`knowledge/`) e orquestração de enxame de agentes com o [[Regente]].

---

## Infraestrutura Física & Hardware

- **Servidor Principal (Headless):** Mac Mini (Intel Core i7-3615QM, 16GB RAM, Linux Mint / Ubuntu x86_64).
- **Clientes de Operação:** Vaio Ubuntu, MX Linux.
- **Cliente de Consulta:** iPad (visualização e consulta do Vault).
- **Diretório Raiz de Trabalho:** `/home/teco/work_out`

---

## Divisão Estrutural por Módulos (`lab-*`)

| Módulo | Nome / Foco | Componentes & Projetos Principais |
| :--- | :--- | :--- |
| **`knowledge/`** | Knowledge Base | Vault oficial Obsidian (Fonte normativa de documentação human-agent) |
| **`lab-a/`** | Automação | [[Padroeira-aut-v1]] (Reconciliação Fiscal `reconciliacao_fiscal_v2`, planilhas Saurus) |
| **`lab-b/`** | Integrações | Adaptações e pontes WhatsApp / MCP |
| **`lab-c/`** | MCP & Memória | [[mcp-lab-universal-admin]], ChromaDB, mem0, Tailscale Funnel / Bridge |
| **`lab-d/`** | Ferramentas Operacionais | API Doctor (fase gamma), Playwright MCP, [[Inventario-CLI-Gateways]] |
| **`lab-e/`** | Homologação & Gateways | [[OmniRoute]] (Smart router 20128), [[LiteLLM]] (Proxy 8000) |
| **`lab-f/`** | Laboratório F | Experimentos secundários e integrações auxiliares |
| **`lab-g/`** | Governança & Atlas | [[2026-07-27-governanca-atlas-supabase]], Banco Supabase (`lab-g`), Atlas Bridge |
| **`lab-obsv/`** | Observabilidade | [[ObSV-IMPLEMENTATION_PLAN]] (Vault Headless REST/CLI server, ObSV v2) |
| **`lab-z/`** | Orquestração Enxame | [[Regente]] (Orquestrador Headless multi-agente, Polyglot Swarm) |

---

## Componentes Técnicos Globais

- **[[Agentes-do-Laboratorio]]:** [[Claude]], [[Claude Code]], [[Codex]], [[JCode]], [[OpenCode]], [[Gemini CLI]], [[ChatGPT]], [[Kilo]].
- **Gateways LLM:** [[OmniRoute]] (Smart routing local), [[LiteLLM]] Proxy.
- **Armazenamento & Memória:** Supabase (`lab-g`), ChromaDB / mem0 (`mcp-lab-universal`), SQLite local, Vault Markdown (`knowledge/`).
- **Containers & Runtime:** Docker, Python 3.10+, FastAPI, `rich` TUI.

---

## Governança Normativa

- `LAB.md`: Regras gerais do laboratório e conduta de agentes.
- `LAB.yaml`: Configuração de serviços, portas e caminhos do laboratório.
- `AGENTS.md`: Protocolo de análise, escopo e limites de alteração por agente.
- [[2026-07-27-governanca-atlas-supabase]]: Decisão formal do Supabase como Fonte Única de Verdade (Single Source of Truth).

---

## Links Relacionados

- [[Agentes-do-Laboratorio]]
- [[Regente]]
- [[Padroeira-aut-v1]]
- [[Inventario-CLI-Gateways]]
- [[mcp-lab-universal-admin]]
- [[ObSV-IMPLEMENTATION_PLAN]]
- [[2026-07-27-governanca-atlas-supabase]]
