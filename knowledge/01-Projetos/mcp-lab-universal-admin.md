---
created: 2026-07-26
updated: 2026-08-18
project: mcp-lab-universal-admin
tags: [mcp, chromadb, mem0, admin, lab-c, python]
tipo: projeto-especificacao
---

# Projeto: Administrador MCP Lab Universal (`mcp-lab-universal-admin`)

**Projeto:** `mcp-lab-universal-admin` (`lab-c`)  
**Status:** Em desenvolvimento / Especificação Aprovada  
**Responsável Técnico:** [[Claude]] / [[OpenCode]]  

---

## 1. Visão Geral

O servidor **`mcp-lab-universal`** ("Nó Santuário", FastMCP + ChromaDB + mem0, porta 8765/27124) fornecia originalmente apenas ferramentas de escrita (`memorizar_fato`, `ingest_document`) e busca (`buscar_memoria`, `search_knowledge`). O projeto **`mcp-lab-universal-admin`** estende o servidor com ferramentas completas de administração e curadoria de dados (listagem, atualização in-place, renomeações e deleção).

---

## 2. Novas Ferramentas de Administração (FastMCP)

1. **`listar_fatos(projeto: str | None = None, limit: int = 50) -> list`**
   - Retorna fatos gravados na memória semântica com seus respectivos IDs.
2. **`apagar_fato(fato_id: str) -> bool`**
   - Remove um fato específico da coleção pelo ID.
3. **`listar_documentos(projeto: str | None = None, limit: int = 50) -> list`**
   - Retorna documentos indexados no ChromaDB com IDs e metadados (`project`, `author`, `date`, `type`).
4. **`apagar_documento(doc_id: str) -> bool`**
   - Remove um documento específico da coleção RAG no Chroma.
5. **`atualizar_documento(doc_id: str, novo_conteudo: str, nova_metadata: dict) -> bool`**
   - Atualiza o conteúdo/metadados de um documento in-place sem duplicar versões desatualizadas.
6. **`renomear_projeto(nome_antigo: str, nome_novo: str) -> dict`**
   - Re-tagging em massa de metadados em documentos e fatos de um projeto.

---

## 3. Tarefas de Implementação e Requisitos

- **Autenticação & Segurança:** Adicionar verificação de token/permissão para operações destrutivas (`apagar_*`, `atualizar_*`).
- **Idempotência:** Garantir que atualizações de documentos preservem os vetores de busca sem corromper a coleção.

---

## Links Relacionados

- [[2026-08-16-mcp-lab-universal-stateless-fix]]
- [[Agentes-do-Laboratorio]]
- [[LAB-Resumo]]
