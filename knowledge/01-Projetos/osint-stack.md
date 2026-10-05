---
created: 2026-09-12
updated: 2026-09-12
project: osint
tags: [osint, spiderfoot, theharvester, maigret, docker-compose, teco-lab, lab-master, perplexica]
tipo: projeto-especificacao
---

# Projeto: Stack OSINT do Teco Lab (`osint`)

**Projeto:** `osint`  \
**Status:** FASE 6 concluída (SpiderFoot persistente); Fases 7-8 pendentes (theHarvester/Maigret sob demanda)  \
**Repositório:** https://github.com/Thesco19/teco-osint-stack (público)  \
**Fonte de estado:** Supabase lab-g (`projects`/`project_status`/`decisions` — tag `osint`)  \

---

## 1. Objetivo

Stack de **OSINT (Open Source Intelligence)** do Teco Lab, orquestrada via Docker Compose, operando **apenas sobre fontes públicas** e **sem credenciais obrigatórias**. Repositório público com placeholders — nunca IPs internos, hostnames Tailscale, portas do Lab ou segredos.

## 2. Ferramentas

| Ferramenta | Profile | Função |
|---|---|---|
| **SpiderFoot** | (sem profile!) | Automação de OSINT (UI web), módulos sobre fontes públicas. |
| **theHarvester** | `cli` | Reconhecimento passivo — e-mails, subdomínios, hosts. |
| **Maigret** | `cli` | Busca de contas por username em redes sociais. |

> IMPORTANTE: o serviço `spiderfoot` NÃO usa `profiles` (ver §6). CLIs usam `profiles: ["cli"]`.

## 3. Estrutura do repositório

- `compose.yaml` — orquestração (placeholders via `.env`).
- `.env.example` — modelo público; `.env` real fora do git.
- `README.md` / `CLAUDE.md` — documentação e convenções.
- `docker/spiderfoot/Dockerfile` — build local (pinned ao master `0f815a2`; branch `fix-install-error` rejeitado por bug de persistência do DB).
- `data/` — persistência (fora do git, apenas `.gitkeep`).

## 4. FASE 6 — SpiderFoot persistente (concluída)

- **Bind Tailscale-only**: `network_mode: host` + `command: ["-l", "<bind_ip>:<porta>"]` (o próprio SF injeta socket_host/port no CherryPy). Escuta SOMENTE no IP Tailscale — nunca `0.0.0.0`; não responde na LAN.
- **Sem imagem oficial publicada** (GHCR privada; Docker Hub inexistente) → Dockerfile próprio + build local (`teco-osint-stack-spiderfoot`).
- **PIN no master** (`0f815a2`): o branch `fix-install-error` (dez/2024) grava o DB em caminho errado (`dataPath()+"spiderfoot.db"` sem barra) → fora do bind mount. Master grava dentro de `/var/lib/spiderfoot` (mount `./data/spiderfoot`) — persistência OK.
- **Scan de exemplo aprovado**: UI start/stop, export JSON/CSV, scanlist; um scan passive completo (`FINISHED`, 228 eventos, 40 tipos de evento).
- **Fontes externas mortas** (débito, não bloqueiam): `api.bgpview.io` (NXDOMAIN), `www.threatcrowd.org` (NameResolutionError), módulo `sfp_stevenblack_hosts` (IndexError).
- Débito de segurança: autenticação da UI desabilitada (sem `passwd`); mitigado pelo bind Tailscale.

## 5. Integração com lab-master (NOVA — 2026-09-12)

- Recurso `osint-stack` registrado no `/opt/stacks/lab-master/config/resources.yaml` como `docker_compose` (compose_file `/opt/stacks/osint/compose.yaml`, container `osint-spiderfoot`, porta 8090).
- É **CORRELATO DIRECIONAL do Perplexica**: `perplexica.correlates = [flaresolverr, osint-stack]`. Ao acionar/desligar o Perplexica pelo lab-master, a stack OSINT sobre/desce junto (validado via API `/api/resources/perplexica/{start,stop}`).
- Detalhe de compat: `docker compose start|stop` do lab-master NÃO passa `--profile`; por isso o spiderfoot não usa profiles.

## 6. Estado futuro (pendente)

- Fase 7: validar theHarvester (`docker compose run --rm theharvester -d <domínio> -b all`).
- Fase 8: validar Maigret (`docker compose run --rm maigret <username>`).
- Fase 9: exemplo de persistência/reinício.
- Fase 10-11: governança (Supabase/RAG/ObSV) e relatório final.

## Links Relacionados

- [[politica-governanca-dados-lab]] — governança dos três sistemas (Supabase/ObSV/RAG)