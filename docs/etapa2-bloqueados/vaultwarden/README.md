# vaultwarden

Classe: stack-terceiros
Local: /opt/stacks
Mapeamento: pasta `vaultwarden` ↔ serviço `vaultwarden` ↔
LM project=`vaultwarden`.

## O que é

Vaultwarden (`vaultwarden/server:latest`): gerenciador de senhas
auto-hospedado, com `vw-data/`.

## Onde vive

Compose em `/opt/stacks/vaultwarden/compose.yaml`; **sem container no ar**
(parado), porta declarada 8222.

## Segredos

Só o caminho: `/opt/stacks/vaultwarden/.env` (nunca commitar).

## Ver também

`STATUS.md` (neste diretório).
