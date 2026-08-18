# Runbook: Ajustar intervalo de RSS Sync do stack *Arr

**Data:** 2026-08-06
**Projeto:** gestao-midia (Prowlarr 2.5.2 + Sonarr 4.0.19 + Radarr 4.0.19)
**Status:** aplicado

## Objetivo

Eliminar o aviso `rss sync didn't cover the period` reduzindo o intervalo de RSS Sync.

## Contexto / Descoberta importante

O aviso **não é do Prowlarr**. É emitido pelo **Sonarr/Radarr** (apps conectados) para
indexadores servidos via Prowlarr — ex. `Torznab: Indexer The Pirate Bay (Prowlarr) rss
sync didn't cover the period between ...`.

- **Prowlarr v2 não tem intervalo de RSS Sync ajustável.** Não está em `config.xml`, nem no
  banco `prowlarr.db` (`AppSyncProfiles`, `Applications`, `Indexers`, `Config`), nem na API
  (`/api/v1/config/indexer` e `/api/v1/appsyncprofile` → 404).
- **Sonarr/Radarr v4: o intervalo é GLOBAL** (Settings → Indexers), não por-indexador.
  `GET /api/v3/indexer/{id}` não expõe `rssSyncInterval` (PUT nele é ignorado silenciosamente,
  responde 202 sem aplicar). O valor vive em `config/indexer` → `rssSyncInterval`.

Causa do gap: o TPB (via Prowlarr) devolve poucos releases por sync (paginação limitada) e não
cobre a janela de 60 min entre syncs. Reduzir o intervalo encolhe a janela que precisa ser coberta.

## Procedimento

Via API dos apps (não do Prowlarr). Para cada app (Sonarr 8989, Radarr 7878):

```bash
# 1. Ler o objeto global atual
curl -s -H "X-Api-Key: $KEY" http://localhost:8989/api/v3/config/indexer

# 2. Alterar "rssSyncInterval": 60 → 30 e enviar PUT
#    (resposta 202 = assíncrona; confirmar com GET fresco)
curl -s -X PUT -H "X-Api-Key: $KEY" -H "Content-Type: application/json" \
  --data @payload.json http://localhost:8989/api/v3/config/indexer
```

Chaves de API: Sonarr `cfa5...` / Radarr `79e0...` (ver `config/*/config.xml`).

## Verificação

```bash
curl -s -H "X-Api-Key: $KEY" http://localhost:8989/api/v3/config/indexer
# → rssSyncInterval: 30
```

Aplicado e confirmado em Sonarr e Radarr (60 → 30).

## Rollback

`rssSyncInterval` de volta para `60` via mesmo endpoint (PUT).

## Observações

- O intervalo é global: a mudança afeta **todos** os indexadores com RSS ativo, não apenas os que
  emitiam o aviso.
- Dobrar a frequência do RSS sync aumenta requisições aos indexadores (rate-limit).
- Se o aviso do TPB persistir mesmo a 30 min (TPB às vezes devolve só ~15 min): reduzir para
  **15 min** ou aumentar o limite de resultados do Prowlarr.
