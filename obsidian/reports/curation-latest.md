# Relatório de Curadoria da Base de Conhecimento

**Data da Curadoria:** 2026-08-18  
**Agente Responsável:** Jcode (Knowledge Curator)  
**Vault:** `/home/teco/work_out/knowledge`  
**Inbox Processada:** `/home/teco/work_out/knowledge/00-Inbox`  

---

## 1. Visão Geral da Operação

Foi realizada a varredura completa da pasta `00-Inbox/` (incluindo o subdiretório `Supabase_Import/` com 75+ exportações relacionais e os documentos de fix mais recentes). O conhecimento foi integrado e sintetizado na estrutura canônica de diretórios do Vault Obsidian, eliminando a duplicação de dados, prescrevendo metadados no padrão YAML frontmatter e inserindo `[[wikilinks]]` bidirecionais entre projetos, agentes, decisões e incidentes.

---

## 2. Documentos Analisados

Total de documentos analisados: **79 arquivos**

1. **Inbox Raiz (2 arquivos):**
   - `mcp_lab_32602_stateless_fix_2026-08-16.md`
   - `omniroute_400_encrypted_fix_2026-08-16.md`
2. **Supabase Import (77 arquivos):**
   - 8 arquivos `agent_context_*.md` (ChatGPT, Claude Code, claude, Codex, Gemini CLI, JCode, Kilo, OpenCode).
   - 19 arquivos referentes à Automação Padroeira `aut-v1` (`artifacts_Correção_1..3`, `artifacts_Diagnóstico_*`, `artifacts_Regra_*`, `decisions_*`, `tasks_*`, `projects_*`, `project_status_*`).
   - 9 arquivos referentes ao `inventario-cli`, Gateways LiteLLM/OmniRoute e Redis (`artifacts_*`, `decisions_*`, `tasks_*`, `project_status_*`).
   - 8 arquivos referentes ao `mcp-lab-universal-admin` (`artifacts_Spec_*`, `tasks_Implementar_*`, `projects_*`, `project_status_*`).
   - 10 arquivos referentes ao Atlas, Governança Supabase e RLS (`artifacts_Índice_Atlas`, `artifacts_Modelo_Orbital`, `artifacts_Diretriz_de_Governança`, `decisions_*`, `tasks_*`).
   - 23 arquivos de mensagens de ponte (`bridge_messages_*`), trocas de contexto (`handoffs_*`), diagnósticos de performance, reversão de deploy e status de laboratórios (`lab-a` a `lab-f`).

---

## 3. Documentos Criados

Foram criados **5 documentos canônicos** altamente estruturados:

1. **`01-Projetos/Padroeira-aut-v1.md`**
   - Consolidação completa do projeto de reconciliação fiscal e automação diária do restaurante.
2. **`01-Projetos/Inventario-CLI-Gateways.md`**
   - Especificação do ecossistema de CLIs de IA, mapeamento de gateways LiteLLM (8000) e OmniRoute (20128), política 100% free-tier e resolução de portas Redis.
3. **`01-Projetos/mcp-lab-universal-admin.md`**
   - Especificação das 6 novas ferramentas de administração FastMCP para gestão do Nó Santuário.
4. **`05-Agentes/Agentes-do-Laboratorio.md`**
   - Catálogo central de todos os agentes de IA operantes no laboratório, seus papéis, modelos e capacidades.
5. **`06-Decisoes/2026-07-27-governanca-atlas-supabase.md`**
   - Registro formal da decisão de definir o Supabase (`lab-g`) como Fonte Única de Verdade e política RLS de segurança.

---

## 4. Documentos Atualizados

Foram atualizados **2 documentos de entrada/índice**:

1. **`02-Laboratorios/LAB-Resumo.md`**
   - Atualizado para refletir todos os módulos (`lab-a` a `lab-z`), componentes globais, governança Supabase e links com os novos projetos canônicos.
2. **`Home.md`**
   - Reestruturado como índice principal do Vault com categorias organizadas de navegação (Índices, Projetos, Governança, Incidentes).

---

## 5. Documentos Movel dos (Incidentes)

Foram movidos e formatados **2 documentos de incidentes recentes**:

1. `00-Inbox/mcp_lab_32602_stateless_fix_2026-08-16.md` → **`08-Incidentes/2026-08-16-mcp-lab-universal-stateless-fix.md`**
2. `00-Inbox/omniroute_400_encrypted_fix_2026-08-16.md` → **`08-Incidentes/2026-08-16-omniroute-400-encrypted-fix.md`**

---

## 6. Documentos Mesclados

Foram mesclados **67 arquivos fragmentados** provenientes da Inbox/Supabase nas 5 notas canônicas:

- **Mesclados em `Padroeira-aut-v1.md` (19 arquivos):** `artifacts_Correção_1...3`, `artifacts_Diagnóstico_aut-v1`, `artifacts_Regra_*`, `decisions_Correção_3`, `decisions_Em_aberto_*`, `tasks_Implementar_Correções_1-3`, `project_status_padroeira`, `projects_projects_Automação_Padroeira__aut-v1`.
- **Mesclados em `Inventario-CLI-Gateways.md` (9 arquivos):** `artifacts_Inventario_CLI_Completo`, `artifacts_Mapeamento_de_Conversões`, `artifacts_Receita_de_Correção`, `tasks_Corrigir_alias_*`, `tasks_Configurar_provedores_*`, `tasks_Resolver_conflito_*`, `decisions_Manter_toda_a_stack_*`, `projects_projects_Inventario_CLI`, `project_status_inventario-cli`.
- **Mesclados em `mcp-lab-universal-admin.md` (8 arquivos):** `artifacts_Spec_de_Ferramentas_*`, `tasks_Implementar_autenticação`, `tasks_Implementar_atualizar_documento`, `tasks_Implementar_listar_*`, `tasks_Implementar_renomear_*`, `projects_*`, `project_status_mcp-lab-universal-admin`.
- **Mesclados em `Agentes-do-Laboratorio.md` (8 arquivos):** `agent_context_ChatGPT`, `agent_context_Claude_Code`, `agent_context_claude`, `agent_context_Codex`, `agent_context_Gemini_CLI`, `agent_context_JCode`, `agent_context_Kilo`, `agent_context_OpenCode`.
- **Mesclados em `2026-07-27-governanca-atlas-supabase.md` & `LAB-Resumo.md` (23 arquivos):** `artifacts_Índice_Atlas`, `artifacts_Modelo_Orbital`, `artifacts_Diretriz_de_Governança`, `decisions_Centralizar_*`, `decisions_RLS_*`, `decisions_Título_*`, `project_status_lab-a..f`, `bridge_messages_*`, `handoffs_*`.

---

## 7. Conflitos Encontrados & Resoluções

1. **Conflito de Porta Redis (OmniRoute vs LiteLLM):**
   - *Resolução:* Isolamento das instâncias Redis configurado e documentado em [[Inventario-CLI-Gateways]].
2. **Desalinhamento de Linhas no Pad (29/30/31 dias):**
   - *Resolução:* Padronização de expansão dinâmica de linhas e fórmulas `SUM()` universais registrada em [[Padroeira-aut-v1]].
3. **Múltiplos Nomes de Projetos Similares (`lab-d` vs `inventario-cli`, `lab-c` vs `mcp-bridge`):**
   - *Resolução:* Mapeamento correto dos diretórios em relação às funcionalidades no [[LAB-Resumo]].
4. **Arquivos nulos (0-byte) na raiz do Vault (`00.md` e `01.md`):**
   - *Resolução:* Removidos com segurança para evitar poluição da raiz.

---

## 8. Recomendações Futuras

1. **Manutenção do Fluxo Inbox:**
   - Garantir que novos resumos ou relatórios gerados por agentes passem pelo processo de curadoria antes de permanecerem na Inbox.
2. **Registro Formal de ADRs:**
   - Formalizar ADRs pendentes sobre a arquitetura do [[Regente]] e decoupling `shared/` na pasta `03-ADR/`.
3. **Sincronização de Tags:**
   - Manter as tags padronizadas (`#projeto/*`, `#incidente-fix`, `#governanca`) para otimizar pesquisas semânticas via Obsidian e RAG.
