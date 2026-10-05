# Arquitetura — osint (teco-osint-stack)

> Stack de OSINT (SpiderFoot, theHarvester, Maigret) orquestrada via Docker Compose.

---

## 1. Visão Geral & Propósito
- **Stack / Linguagem:** Docker (SpiderFoot UI web + theHarvester/Maigret CLI)
- **Localização:** `/opt/stacks/osint`
- **Portas & Redes:** 
  - `5001` / `8090` — SpiderFoot UI web (bind restrito via `.env`)
  - theHarvester / Maigret — CLI sob demanda (sem porta exposta)
- **Status Operacional:** Ativo (parcial — SpiderFoot no ar; theHarvester/Maigret CLI sob demanda)

## 2. Estrutura de Módulos & Arquivos
- `compose.yaml` — Orquestração (SpiderFoot `main` profile, theHarvester/Maigret `cli` profile)
- `.env` / `.env.example` — Variáveis (`OSINT_BIND_IP`, `SPIDERFOOT_PORT`; chaves API opcionais em `config/`)
- `config/` — Exemplos de config (sem credenciais reais)
- `data/spiderfoot/` — Persistência SpiderFoot (config, uploads, DB) — gitignored
- `data/theharvester/` — Resultados theHarvester — gitignored
- `data/maigret/` — Resultados Maigret — gitignored
- `scripts/` — Utilitários de operação
- `docs/` — Documentação de inspiração e notas
- `.gitignore` — `.env`, `data/*`, `logs`, chaves

## 3. Como Rodar / Execução
- **SpiderFoot (UI):** `cd /opt/stacks/osint && cp .env.example .env && docker compose up -d spiderfoot` → `http://{{OSINT_BIND_IP}}:{{SPIDERFOOT_PORT}}` (default `127.0.0.1:8090`)
- **theHarvester (CLI):** `docker compose run --rm theharvester -d example.com -b all` → resultados em `data/theharvester/`
- **Maigret (CLI):** `docker compose run --rm maigret alvo` → resultados em `data/maigret/`
- **Bind IP:** Default `127.0.0.1` (restrito); para tailnet/LAN, ajustar **apenas no `.env` local** — nunca no repositório

## 4. Variáveis de Ambiente & Configurações (Sem Segredos)
- `.env` / `.env.example`: `OSINT_BIND_IP` (default `127.0.0.1`), `SPIDERFOOT_PORT` (default `8090`)
- Chaves API opcionais (Shodan, Censys, VirusTotal, etc.) em `.env` / `config/` — **fora do git**
- Defaults já funcionam sem chaves (fontes públicas desautenticadas)

## 5. Pontos de Atenção & Mapeamento de Riscos
- **Apenas fontes públicas:** Sem chaves API obrigatórias; chaves opcionais fora do repo
- **Bind restrito:** Default `127.0.0.1`; para tailnet/LAN ajustar **só no `.env` local** — nunca no repo
- **Repo público:** Nunca commitar `.env`, IPs internos, hostnames Tailscale, portas reais, credenciais
- **Isolado do Perplexica:** Integração MCP/Perplexica/Supabase/ObSV futura (não implementada)
- **2 arquivos `.bak` não rastreados:** `compose.yaml.bak-20260924_2358`, `compose.yaml.bak-20260925_0258`
- **Integrações futuras:** Perplexica, MCP-Lab, MCP-Bridge, Atlas/Supabase, ObSV — isoladas do Perplexica
- **Repo:** `teco-osint-stack` (último commit 2026-09-25); `data/`, `.env`, logs gitignored
- **SpiderFoot:** UI web :5001/:8090; módulos fontes públicas (whois, DNS, crt.sh…)
- **theHarvester/Maigret:** CLI sob demanda; resultados em `data/`

---

*Gerado em 2026-10-01 — hash do mapa: osint_arquitetura_v1*