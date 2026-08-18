---
created: 2026-07-27
updated: 2026-08-18
tags: [governanca, supabase, atlas, rls, fonte-de-verdade]
tipo: decisao-arquitetura
---

# Decisão de Arquitetura & Governança: Supabase como Fonte Única de Verdade (Atlas v2)

**Data:** 2026-07-27  
**Status:** Aprovado / Em Vigor  
**Projeto:** `atlas` / `lab-g`  
**Decisores:** [[ChatGPT]] (Idealizador), [[Claude]] (Auditor), [[JCode]], [[OpenCode]]  

---

## Contexto e Problema

Anteriormente, o estado do laboratório ficava disperso em memórias temporárias (`.mcp_context`), arquivos soltos no Google Drive e no índice Chroma/mem0 do `mcp-lab-universal`. Isso gerava inconsistências, duplicação de projetos e perda de contexto em trocas de sessão.

---

## Decisões Formais

1. **Supabase (`lab-g`) como Fonte Única de Verdade (Single Source of Truth):**
   - O banco de dados Supabase em `lab-g` é a única fonte normativa oficial do estado do laboratório (`projects`, `artifacts`, `decisions`, `tasks`, `handoffs`, `agent_context`, `project_status`).
   - O `mcp-lab-universal` ("Nó Santuário", porta 8765) atua como índice semântico e memória auxiliar de busca, não como fonte de verdade primária.

2. **Centralização de Governança e Aprovação de Infraestrutura:**
   - Toda e qualquer alteração de infraestrutura deve obrigatoriamente registrar uma proposta na tabela `public.decisions` com status `pending` antes da execução.
   - Eliminação total de pontes via Google Drive.

3. **Políticas de Segurança Row Level Security (RLS):**
   - RLS habilitado em todas as 8 tabelas do `lab-g`.
   - **Leitura (`SELECT`):** Aberta para perfis `anon` e `authenticated`.
   - **Escrita (`INSERT`, `UPDATE`, `DELETE`):** Restrita estritamente a requisições com a chave de serviço ou políticas de perfil autorizados.

4. **Modelo Orbital do Atlas:**
   - O ecossistema opera em modelo orbital centralizado em torno da base de conhecimento compartilhada (`knowledge/` Obsidian Vault) e do banco Supabase (`lab-g`), com os agentes operando em órbitas especializadas (planejamento, código, auditoria, orquestração).

---

## Links Relacionados

- [[Agentes-do-Laboratorio]]
- [[LAB-Resumo]]
- [[Supabase]]
