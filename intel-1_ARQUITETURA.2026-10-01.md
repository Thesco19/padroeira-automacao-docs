# Arquitetura — intel-1

> Ollama local (`ai_brain`) + Glances (`system_monitor`) + Scrutiny (saúde de discos).

---

## 1. Visão Geral & Propósito
- **Stack / Linguagem:** Docker (Ollama + Glances + Scrutiny)
- **Localização:** `/opt/stacks/intel-1`
- **Portas & Redes:** 
  - `11434` — Ollama (`ai_brain`, modelos dos agentes)
  - `8008` — Glances (`system_monitor`)
  - Scrutiny (saúde de discos)
- **Status Operacional:** Sob Demanda (Ollama `ai_brain` ligado pontualmente pelo usuário; containers parados por padrão; comportamento ESPERADO e NORMAL)

## 2. Estrutura de Módulos & Arquivos
- `compose.yaml` — Orquestração dos 3 serviços:
  - `ai_brain` — Ollama (modelos: `qwen2.5:1.5b`, `mistral-nemo:12b`, etc.; `OLLAMA_CONTEXT_LENGTH=8192`)
  - `system_monitor` — Glances (porta 8008, UI web)
  - `scrutiny` — Saúde de discos (coleta SMART, UI web)
- `ollama_data/` — Dados persistidos do Ollama (modelos, cache)
- `scrutiny*` — Dados do Scrutiny (config, DB)
- `system_monitor` — Dados do Glances
- `.env` — Variáveis de ambiente (gitignored, permissão 600)
- `.env.example` — Modelo (placeholders)

## 3. Como Rodar / Execução
- **Subir tudo:** `cd /opt/stacks/intel-1 && docker compose up -d`
- **Só Ollama:** `docker compose up -d ai_brain`
- **Parar:** `docker compose down`
- **Logs:** `docker compose logs -f ai_brain` / `system_monitor` / `scrutiny`
- **Portas:** `11434` (Ollama), `8008` (Glances), Scrutiny (porta padrão)
- **Impacto ao parar:** Sem Ollama ativo, o `forge` de `promptforge`/`qwenchat` não tem backend local (comportamento esperado; Ollama sobe sob demanda)

## 4. Variáveis de Ambiente & Configurações (Sem Segredos)
- `.env` (gitignored, permissão 600): Configurações dos serviços
- `.env.example` — Modelo (placeholders)
- `OLLAMA_CONTEXT_LENGTH=8192` (configurado no container `ai_brain`)
- `OLLAMA_HOST=ai_brain:11434` (rede `gestao-midia_media_net`)

## 5. Pontos de Atenção & Mapeamento de Riscos
- **Totalmente parado:** Nenhum container no ar (inventário); decisão de subir Ollama pendente (B3)
- **Impacto crítico:** Sem Ollama (`ai_brain` :11434), o `forge` de `promptforge`/`qwenchat` não tem backend local
- **Sem git:** Só inventários ObSV; sem versionamento
- **Ollama models:** `qwen2.5:1.5b`, `mistral-nemo:12b`, etc. (precisam ser puxados no primeiro up)
- **Scrutiny:** Coleta SMART de discos; UI web própria
- **Glances:** Porta 8008 (System Monitor UI)
- **Rede:** `gestao-midia_media_net` (container `ai_brain` acessível como `ai_brain:11434`)
- **Decisão pendente:** Nenhuma (comportamento sob demanda é o padrão esperado; B3 é opcional para manter Ollama sempre ativo)

---

*Gerado em 2026-10-01 — hash do mapa: intel_1_arquitetura_v1*