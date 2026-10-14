# limpador

Classe: stack-terceiros
Local: /opt/stacks
Mapeamento: pasta `limpador` ↔ serviço `cleaner` ↔ LM project=`limpador`.

## O que é

Faxina de logs (`alpine`, `restart: no`): apaga logs rotacionados de
radarr/lidarr/seerr/bazarr/plex e zera o buffer stdout/stderr de todos os
containers do host. Roda uma vez por invocação, não é daemon.

## Onde vive

Compose em `/opt/stacks/limpador/compose.yaml`; parado por desenho
(sem container permanente, sem porta).

## Segredos

Só o caminho: `/opt/stacks/limpador/.env` (nunca commitar).

## Ver também

`STATUS.md` (neste diretório).
