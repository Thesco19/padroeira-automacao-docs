# gestao-midia

Classe: stack-terceiros
Local: /opt/stacks
Mapeamento: pasta `gestao-midia` ↔ serviços `prowlarr`+`sonarr`+`radarr`+`lidarr`
↔ LM project=`gestao-midia`.

## O que é

Stack *arr de gestão de mídia (linuxserver.io): Prowlarr, Sonarr, Radarr,
Lidarr, com `config/`.

## Onde vive

Compose em `/opt/stacks/gestao-midia/compose.yaml`; **todos no ar**:
prowlarr :9696, sonarr :8989, radarr :7878, lidarr :8686.

## Segredos

Só o caminho: `/opt/stacks/gestao-midia/.env` (nunca commitar).

## Ver também

`STATUS.md` (neste diretório).
