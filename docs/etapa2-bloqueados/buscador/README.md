# buscador

Classe: stack-terceiros
Local: /opt/stacks
Mapeamento: pasta `buscador` ↔ serviço `seerr` ↔ LM project=`buscador`.

## O que é

Seerr (fork do Overseerr): buscador de mídia com config em `overseerr-config/`.

## Onde vive

Compose em `/opt/stacks/buscador/compose.yaml`; container `seerr`
(`ghcr.io/seerr-team/seerr:latest`) **no ar**, porta 5055.

## Segredos

Só o caminho: `/opt/stacks/buscador/.env` (nunca commitar).

## Ver também

`STATUS.md` (neste diretório).
