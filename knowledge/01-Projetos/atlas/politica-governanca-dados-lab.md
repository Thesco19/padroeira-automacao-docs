---
title: "Política de Governança de Dados do Laboratório v1.0"
date: 2026-08-30
version: "1.0"
tags:
  - governanca
  - atlas
  - politica
  - laboratorio
  - supabase
  - obsv
  - rag
---

# Política de Governança de Dados do Laboratório v1.0

**Data:** 2026-08-30
**Status:** Vigente
**Autor:** Claude (chat) — consolidado a partir de decisões acumuladas do laboratório

---

## 1. Escopo e Objetivo

Esta política define as regras de governança de dados do laboratório de IA multi-agente, estabelecendo:

- O papel de cada sistema de armazenamento (Supabase, ObSV, RAG/mcp-lab-universal)
- A divisão formal de responsabilidade entre eles
- A regra de dono único por conteúdo
- A convenção de nomenclatura de projeto
- A linha de base de segurança

---

## 2. Definição de Sistemas

### 2.1 Supabase (lab-g) — Fonte Oficial de Estado

- **Função:** Fonte oficial de estado e protocolo entre agentes
- **Tabelas:** projects, artifacts, decisions, tasks, handoffs, agent_context, project_status, bridge_messages
- **Conteúdo:** Status de projetos, tarefas, decisões formais, handoffs entre agentes, mensagens de ponte, contexto de sessão
- **Regra:** Se é estado ou protocolo → Supabase é a fonte de verdade

### 2.2 ObSV (Vault Obsidian) — Fonte Oficial de Documentação Viva

- **Função:** Fonte oficial de documentação viva/narrativa
- **Conteúdo:** Specs, progresso, regras de projeto, ADRs, runbooks, documentação técnica, decisões narrativas
- **Regra:** Se é explicação ou "como funciona" → ObSV é a fonte de verdade

### 2.3 RAG/mcp-lab-universal (Chroma + mem0) — Camada de Busca Semântica

- **Função:** Camada de busca semântica e recall
- **Conteúdo:** Resumos de documentos, fatos soltos,索引 semântica
- **Regra:** Não é fonte primária — fatos soltos em mem0 são transitórios e devem ser promovidos a documentação (ObSV) ou estado formal (Supabase) quando amadurecem
- **Hierarquia:** Se é fato solto útil → RAG temporário; se amadureceu → promover a ObSV ou Supabase

---

## 3. Regra Central: Dono Único

**Todo conteúdo tem um dono único, nunca duplicar integralmente entre sistemas.**

- Usar referência curta em vez de cópia completa
- Quando um documento precisa ser acessível em múltiplos sistemas, criar apenas uma referência (link/ID) no sistema secundário apontando para o dono original
- Exceção: resumos e índices no RAG são aceitáveis, mas devem conter referência ao documento original

---

## 4. Convenção de Nomenclatura de Projeto

- Usar o **mesmo identificador de projeto** nos três sistemas (Supabase, ObSV, RAG)
- Projetos guarda-chuva com subprojetos quando aplicável
- Formato: lowercase, sem underscores para projetos novos (usar hífens)
- Exemplos validados: `atlas`, `restaurante`, `lab-z`, `obsv`, `work_out`

---

## 5. Linha de Base de Segurança

### 5.1 Supabase (lab-g)
- RLS (Row Level Security) habilitado nas 8 tabelas
- Leitura aberta (para agentes autenticados)
- Escrita exige header `x-lab-secret`
- **Nota de correção (2026-08-30):** O limite de 2 projetos é do plano free do Supabase por organização (confirmado: lab-g e lab-z-regente), NÃO do RAG — o RAG (Chroma) não tem esse limite e já tem 10+ tags de projeto

### 5.2 ObSV (Vault)
- Gate `tailscale_only` ativo
- Acesso restrito à rede Tailscale

### 5.3 RAG/mcp-lab-universal
- Hoje depende apenas do perímetro de rede (Tailscale)
- **Identificado como o elo mais fraco** em termos de segurança

### 5.4 Regra Universal
- **Proibido gravar segredos crus** (tokens, senhas, chaves) em qualquer um dos três sistemas

---

## 6. Árvore de Decisão para Agente em Dúvida

```
┌─────────────────────────────────┐
│  Agente tem uma informação?     │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│  É estado ou protocolo?         │──SIM──▶ Supabase
└──────────┬──────────────────────┘
           │ NÃO
           ▼
┌─────────────────────────────────┐
│  É explicação / como funciona?  │──SIM──▶ ObSV
└──────────┬──────────────────────┘
           │ NÃO
           ▼
┌─────────────────────────────────┐
│  É fato solto útil?             │──SIM──▶ RAG temporário
└──────────┬──────────────────────┘         │
           │ NÃO                            │ amadureceu?
           ▼                                ▼
┌─────────────────────────────────┐  Promover a ObSV
│  Dúvida persistente?            │  ou Supabase
│  → registrar como fato e        │
│    sinalizar Paulo              │
└─────────────────────────────────┘
```

---

## 7. Processos Operacionais

### 7.1 Criação de Conteúdo
1. Identificar o dono correto (Supabase/ObSV/RAG)
2. Criar no sistema dono
3. Se necessário em outro sistema, criar apenas referência

### 7.2 Atualização de Conteúdo
1. Atualizar sempre no sistema dono
2. Atualizar referências em outros sistemas se o ID/caminho mudar

### 7.3 Migração entre Sistemas
1. Quando um conteúdo amadurece (ex: fato solto → decisão formal)
2. Promover do RAG para ObSV ou Supabase
3. Manter referência no sistema antigo por 30 dias

---

## 8. Auditoria e Conformidade

- Revisão trimestral da política
- Verificação de que todos os projetos seguem a convenção de nomenclatura
- Limpeza periódica de fatos obsoletos no RAG
- Validação de que nenhum segredo foi gravado em texto plano

---

## 9. Histórico de Alterações

| Data | Versão | Alteração | Autor |
|------|--------|-----------|-------|
| 2026-08-30 | 1.0 | Versão inicial | Claude (chat) |

---

## Referências

- Supabase lab-g: project_status, artifacts, decisions (tabelas oficiais)
- ObSV vault: `/home/teco/work_out/knowledge/`
- RAG: mcp-lab-universal (Chroma + mem0), porta 8765
- Documento original: `/mnt/user-data/outputs/politica-governanca-dados-lab.md` (Claude chat)
- Índice Atlas: `doc_f0bdb6c4f64413620231ed8d52a2f97f15edcd89` (RAG)