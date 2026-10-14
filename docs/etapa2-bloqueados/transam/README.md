# transam

Classe: stack-terceiros
Local: /opt/stacks
Mapeamento: pasta `transam` ↔ serviço `transmission` ↔ LM project=`transam`.

## O que é

Transmission (`lscr.io/linuxserver/transmission:latest`): cliente
torrent, com `config/`.

## Onde vive

Compose em `/opt/stacks/transam/compose.yaml`; container `transmission`
**no ar**, portas 9091 + 51413 (tcp/udp).

## Segredos

Só o caminho: `/opt/stacks/transam/.env` (nunca commitar).

## Ver também

`STATUS.md` (neste diretório).
