# Plano de Start Controlado e Otimização de Memória (16GB + zram)

**Data:** 2026-08-04
**Host:** teco-Macmini — Intel i7-3615QM @ 2.30GHz (8 threads), 16GB RAM, 2 discos mecânicos

---

## 1. Diagnóstico Completo

### 1.1 Hardware
| Componente | Detalhe |
|------------|---------|
| CPU | Intel Core i7-3615QM (4C/8T, 2.3-3.3 GHz) |
| RAM | 16 GB DDR3 (~16,276,488 kB) |
| OS disk | `/dev/sda` — Apple HDD HTS541010A9E662, 931.5 GB (ROTA=1, mecânico) |
| Storage disk | `/dev/sdb` — Generic 1.8 TB, montado em `/mnt/storage-teco` (43% uso) |
| zram0 | 7.8 GB, algoritmo `lzo-rle`, praticamente **ocioso** (52K de dados) |
| Swap file | `/swapfile` 2 GB, 385 MB em uso |
| Kernel | 5.15.0-174-generic, Ubuntu |
| Uptime | 28 dias |
| Load | 3.60 / 1.91 / 2.90 (moderada para 8 threads) |

### 1.2 Containers Ativos (27) — Consumo de RAM
| Container | Stack | RAM Real | Limite Atual | Observação |
|-----------|-------|----------|--------------|------------|
| **ai_brain (ollama)** | intel-1 | 2.42 GiB | 8 GiB | Maior consumidor — carrega modelos LLM |
| **omniroute-lab** | omniroute | 1.01 GiB | 15.5 GiB | 33% CPU, sem limite real |
| **litellm-proxy** | litellm | 856 MiB | 15.5 GiB | Proxy LLM, sem limite real |
| mcp-lab-universal | mcp-lab | 246 MiB | 15.5 GiB | |
| radarr | gestao-midia | 177 MiB | 768 MiB | OK |
| sonarr | gestao-midia | 167 MiB | 768 MiB | OK |
| bazarr | suporte-midia | 174 MiB | 1 GiB | OK |
| prowlarr | gestao-midia | 152 MiB | 512 MiB | OK |
| seerr | buscador | 171 MiB | 512 MiB | OK |
| dockge | dockge | 144 MiB | 15.5 GiB | Gerenciador — precisa de RAM |
| lidarr | gestao-midia | 130 MiB | 768 MiB | OK |
| playwright-mcp | playwright-mcp | 110 MiB | 15.5 GiB | |
| system_monitor | intel-1 | 95 MiB | 256 MiB | OK |
| mcp-superassistant | proxy | 94 MiB | 15.5 GiB | |
| scrutiny | intel-1 | 56 MiB | 15.5 GiB | |
| transmission | transam | 63 MiB | 15.5 GiB | **11 GB de Block I/O!** |
| litellm-db | litellm | 49 MiB | 15.5 GiB | |
| mcp-bridge | mcp-bridge | 45 MiB | 15.5 GiB | |
| meu-painel | meu-painel | 39 MiB | 15.5 GiB | |
| omniroute-lab-redis | omniroute | 8 MiB | 15.5 GiB | |
| flaresolverr | suporte-midia | 75 MiB | 1 GiB | OK |
| **TOTAL ativos** | | **~6.3 GiB** | | |

### 1.3 Containers Parados (6)
| Container | Stack | Status |
|-----------|-------|--------|
| media_cleaner | limpador | Exited(0) — job único, normal |
| photoprism | fotos-videos | Exited(0) |
| mariadb-midia | fotos-videos | Exited(0) |
| vaultwarden | vaultwarden | Exited(0) |
| n8n_hermes | hermes_core | Exited(0) |
| **langflow** | **langflow** | **Exited(137) — OOM-KILLED** ❌ |

### 1.4 Problemas Identificados

#### 🔴 Pressão de Memória
- **10 GiB/16 GiB usados**, apenas **446 MiB livre**
- **langflow foi OOM-killed** (Exit 137) — confirma exaustão de RAM
- **zram com 7.8 GB alocado mas quase vazio** (52K) — configurado mas não efetivo
- **Swap file de 2 GB** sendo usado em vez de zram (385 MB em uso = 385 MB gravando em disco mecânico)
- **swappiness=10** — muito baixo para zram, faz o kernel preferir manter páginas em RAM física em vez de comprimi-las

#### 🟡 I/O em Disco Mecânico (thrashing)
- `transmission`: 7.36 GB escritos / 4.14 GB lidos (Block I/O pesado)
- `lidarr`: 1.44 GB escritos
- `radarr`: 4.25 GB escritos
- `dockge`: 2.11 GB lidos
- `sda` (OS): load 1.452 — I/O significativo no disco de boot
- **Todos os 27 containers iniciam simultaneamente no boot** — causam thrashing no disco mecânico

#### 🟡 Falta de Ordem de Startup
- Nenhum `depends_on` com `condition: service_healthy` nos compose files
- Scrutiny (consertado) era sintoma de dependência mal configurada
- Serviços pesados (ollama, litellm, omniroute) competem por I/O e RAM no boot

#### 🟡 Limites de Memória Ausentes
- 14 containers com limite de 15.5 GiB (RAM total do host!) — meaningless
- Não há proteção contra runaway containers consumindo toda RAM

#### 🟢 sysctl.conf
- `vm.dirty_background_ratio=5`, `vm.dirty_ratio=10` — OK (limita write-back no disco mecânico)
- `vm.swappiness=10` — precisa mudar para zram (ver abaixo)

---

## 2. Plano de Implementação

### Fase 1 — zram Otimizado (substitui swap file)

#### Objetivo
Com zram configurado corretamente em 16GB:
- **Compressão zstd: 2:1 a 4:1** → 16GB física = 32-64GB virtuais
- Tudo fica em RAM comprimida (zero I/O em disco mecânico para swap)
- Elimina thrashing de swap em disco

#### Mudanças
1. **Criar serviço systemd `zram0`** com:
   - Tamanho: 16 GB (= RAM total, máxima compressão possível)
   - Algoritmo: `zstd` (melhor ratio que lzo-rle, CPU i7-3615QM suporta bem)
   - Prioridade de swap: 100 (maior que swap file → zram é preferido)
2. **Remover swap file** (`/swapfile`) — zram substitui completamente
3. **Atualizar sysctl.conf:**
   - `vm.swappiness=60` (com zram, queremos comprimir páginas inativas proativamente)
   - Manter `dirty_background_ratio=5` e `dirty_ratio=10` (já bom para HDD)

#### Arquivos
- `/etc/systemd/system/zram0.service` — serviço systemd para zram
- `/etc/sysctl.d/99-zram-tuning.conf` — configuração zram
- Atualizar `/etc/sysctl.conf` — swappiness=60

### Fase 2 — Script de Start Controlado (evita I/O thrashing)

#### Objetivo
Economizar o disco mecânico iniciando containers em **3 fases com delays**, priorizando:
- Fase 0: Infraestrutura (redes, dockge)
- Fase 1: Serviços core (que outros dependem)
- Fase 2: Aplicações principais
- Fase 3: Serviços pesados/optionais

#### Ordem de Startup Proposta

```
FASE 0 — Infraestrutura (0s-15s)
├── gestao-midia (cria media_net)     → aguardar network create
├── dockge (gerenciador)              → aguardar health
└── meu-painel (dashboard visível)    → start

FASE 1 — Core Services (15s-60s) — I/O leve, databases
├── litellm-db (postgres)             → aguardar health
├── omniroute-lab-redis               → aguardar health
├── omniroute-lab                     → aguardar health (depende de redis)
├── litellm-proxy                     → aguardar health (depende de postgres)
└── mcp-lab-universal                 → aguardar health (uvicorn)

FASE 2 — Aplicações (60s-120s)
├── prowlarr                          → aguardar health
├── sonarr                            → depende de prowlarr
├── radarr                            → depende de prowlarr
├── lidarr                            → depende de prowlarr
├── bazarr                            → depende de sonarr/radarr
├── transmission                      → rede media_net
├── seerr                             → aguardar health
├── flaresolverr                      → aguardar health
└── mcp-superassistant-proxy          → start

FASE 3 — Pesados/Opcionais (120s-180s) —大量 RAM + I/O
├── ai_brain (ollama)                 → start (8GB limit)
├── system_monitor (glances)          → start
├── playwright-mcp                    → start
├── mcp-bridge                        → start
├── scrutiny                          → start
└── vaultwarden                       → start
```

#### Arquivo
- `/opt/scripts/docker-controlled-start.sh` — script principal
- `/etc/systemd/system/docker-controlled-start.service` — serviço systemd (roda após docker.service)

### Fase 3 — Limites de Memória Reais (evita OOM)

#### Novos limites por container
| Container | RAM Atual | Novo Limite | Justificativa |
|-----------|-----------|-------------|---------------|
| ai_brain | 2.4 GiB | **6 GiB** | Reduzido de 8G — precisa sobrar para outros |
| omniroute-lab | 1.0 GiB | **1.5 GiB** | Proxy com margem |
| litellm-proxy | 856 MiB | **1.5 GiB** | Proxy com margem |
| mcp-lab | 246 MiB | **512 MiB** | Python server |
| dockge | 144 MiB | **512 MiB** | Gerenciador |
| transmission | 63 MiB | **512 MiB** | Torrent client |
| system_monitor | 95 MiB | **256 MiB** | Já tem limite |
| flaresolverr | 75 MiB | **256 MiB** | Headless browser leve |
| playwright-mcp | 110 MiB | **512 MiB** | Playwright precisa |
| mcp-superassistant | 94 MiB | **256 MiB** | Node.js proxy |
| mcp-bridge | 45 MiB | **256 MiB** | Bridge leve |
| litellm-db | 49 MiB | **512 MiB** | PostgreSQL |
| scrutiny | 56 MiB | **256 MiB** | Web + InfluxDB |
| meu-painel | 39 MiB | **128 MiB** | Dashboard estático |

#### Memória total protegida: ~12 GiB dos 16 GiB
- Reserva para OS + buffers: ~4 GiB
- zram atua como safety net para páginas comprimidas

### Fase 4 — Limpeza de Disco (recupera espaço)

- `docker system prune -a --volumes` — recupera ~50 GB (imagens + build cache)
- Adicionar `noatime` ao mount de `/mnt/storage-teco` (reduz writes no HDD)
- Considerar mover `/var/lib/docker` para `/mnt/storage-teco` (disco maior)

---

## 3. sysctl.conf Atualizado (referência)

```ini
# Rede
net.ipv4.ip_forward=1
net.ipv6.conf.all.forwarding=1

# zram (substitui swap file)
vm.swappiness=60

# Write-back throttling para disco mecânico
vm.dirty_background_ratio=5
vm.dirty_ratio=10
vm.dirty_expire_centisecs=3000
vm.dirty_writeback_centisecs=500
```

---

## 4. Métricas Esperadas Pós-Implementação

| Métrica | Antes | Depois |
|---------|-------|--------|
| RAM livre (média) | 446 MiB | 2-4 GiB |
| Swap em disco | 385 MB / 2 GB | 0 (eliminado) |
| zram uso efetivo | 52 K (ocioso) | 4-8 GiB comprimido |
| OOM kills | langflow morto | 0 |
| Tempo boot I/O | ~3-5 min thrashing | ~60-90s controlado |
| Block I/O pós-boot | Todos ao mesmo tempo | Escalonado em 3 fases |
| Memória total efetiva | 16 GiB (8 usável) | 32-48 GiB (com zram zstd) |

---

## 5. Riscos e Mitigações

| Risco | Mitigação |
|-------|-----------|
| zram consome CPU extra (compressão) | i7-3615QM tem 8 threads — compressão zstd é leve |
| Script de start com delay demora | Fases são configuráveis; dockge pode gerenciar restarts depois |
| Remover swap file pode falhar se zram não subir | Script verifica zram antes de remover swap |
| Limites de RAM muito apertados | Monitoramento via Glances; limites com margem |
| Backup do compose original | Script cria backup antes de modificar qualquer compose |
