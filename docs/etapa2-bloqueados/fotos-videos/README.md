# fotos-videos

Classe: stack-terceiros
Local: /opt/stacks
Mapeamento: pasta `fotos-videos` ↔ serviços `photoprism`+`mariadb-midia` ↔
LM project=`fotos-videos`.

## O que é

Photoprism (fotos/vídeos) + MariaDB de apoio.

## Onde vive

Compose em `/opt/stacks/fotos-videos/compose.yaml`; **sem container no ar**
(parado), porta declarada 2342.

## Segredos

Só o caminho: `/opt/stacks/fotos-videos/.env` (nunca commitar).

## Ver também

`STATUS.md` (neste diretório).
