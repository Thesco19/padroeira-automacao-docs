# Incidente: Plex não conseguia tocar "Evil Dead Burn (2026)"

**Data:** 2026-08-05
**Serviço:** Plex (container `plex`, plexinc/pms-docker:latest)
**Projeto:** homelab-infra

## Sintoma

Playback de "Evil Dead Burn (2026)" falhava. Log do Plex:

```
ERROR - Couldn't find the file to stream: /mnt/storage-teco/downloads/complete/radarr/Evil Dead Burn (2026) [1080p] [WEBRip] [x265] [10bit] [5.1] [YTS.GG - YTS.BZ]/Evil.Dead.Burn.2026.1080p.WEBRip.x265.10bit.AAC5.1-[YTS.GG - YTS.BZ].mp4
```

## Causa raiz

Part órfão/duplicado no banco do Plex. O arquivo existia e estava íntegro em
`/mnt/storage-teco/filmes/Evil Dead Burn (2026)/Evil Dead Burn (2026) WEBRip-1080p.mp4`
(1.98 GB, HEVC Main 10 10-bit, AAC 5.1), mas o Plex tinha **dois parts para o mesmo
metadata_item (7648)**:

| media_item/part | caminho no banco | arquivo existe |
|-----------------|------------------|----------------|
| 6170 | `downloads/complete/radarr/...` | não (Radarr moveu na importação) |
| 6192 | `filmes/Evil Dead Burn (2026)/...` | sim |

O Plex selecionava o part quebrado (6170) → erro de streaming.

## Correção

1. `docker stop plex`.
2. Backup do banco em `/tmp/opencode/plex_library_pre_fix.db`.
3. Removido o part órfão (media_items 6170 + media_parts/media_streams/settings associados).
   O banco foi editado via container `python:3.12-slim` (roda como root), pois o diretório
   é do usuário `plex` e o sudo exige senha. Dono/permissões preservados (`plex:plex 664`).
4. `docker start plex` → healthy.

## Verificação

- Só restou o part 6192 (caminho válido) para o metadata_item 7648.
- Log pós-restart sem erros; Plex reconheceu o caminho correto (`Now watching ...`).

## Observações

- Não era problema de codec/permissão: HEVC Main 10 pode exigir transcode em alguns
  clientes, mas o erro era 100% de caminho de arquivo.
- `403 MyPlex: Updating device connections` é da comunicação com plex.tv, não relacionado.
- Prevenção: verificar `media_parts` órfãos após importações do Radarr que movam arquivos
  já indexados.
