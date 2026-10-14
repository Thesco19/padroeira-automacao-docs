# meu-painel

Classe: stack-terceiros
Local: /opt/stacks
Mapeamento: pasta `meu-painel` ↔ serviço `flame` ↔ LM project=`meu-painel`.

## O que é

Flame (`pawelmalak/flame:latest`): painel inicial do lab. Nota (B1):
`/opt/stacks/flame/` é só o diretório de dados (volume `data/`, montado em
`/app/data`) — não é projeto e não recebe docs próprios.

## Onde vive

Compose em `/opt/stacks/meu-painel/compose.yaml`; container `meu-painel`
**no ar**, porta 3001→5005.

## Segredos

Só caminhos (nunca valores): `/opt/stacks/meu-painel/.env` e senha padrão
no corpo de `/opt/stacks/meu-painel/compose.yaml` (trocar).

## Ver também

`STATUS.md` (neste diretório).
