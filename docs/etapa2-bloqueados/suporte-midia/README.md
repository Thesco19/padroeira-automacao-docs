# suporte-midia

Classe: stack-terceiros
Local: /opt/stacks
Mapeamento: pasta `suporte-midia` ↔ serviços `flaresolverr`+`bazarr`+
`bazarr-auto-translate` ↔ LM project=`suporte-midia`.

## O que é

Suporte de mídia: FlareSolverr (bypass Cloudflare, compartilhado com o
Perplexica) + Bazarr (legendas) + auto-translate, com `config/`.

## Onde vive

Compose em `/opt/stacks/suporte-midia/compose.yaml`; **todos no ar**:
flaresolverr :8191, bazarr, auto-translate.

## Segredos

Só o caminho: `/opt/stacks/suporte-midia/.env` (nunca commitar).

## Ver também

`STATUS.md` (neste diretório).
