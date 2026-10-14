# intel-1

Classe: stack-terceiros
Local: /opt/stacks
Mapeamento: pasta `intel-1` ↔ serviços `ai_brain`+`system_monitor`+`scrutiny` ↔
LM project=`intel-1`.

## O que é

Ollama local (`ai_brain`, modelos dos agentes) + Glances (`system_monitor`)
+ Scrutiny (saúde de discos), com `ollama_data/`, `scrutiny*` e
`system_monitor` no compose.

## Onde vive

Compose em `/opt/stacks/intel-1/compose.yaml`; **tudo parado, sem container
no ar** (portas declaradas 11434, 8008). Impacto: sem Ollama, o `forge` de
`promptforge`/`qwenchat` não tem backend local (subir o Ollama é decisão
separada — B3).

## Segredos

Só o caminho: `/opt/stacks/intel-1/.env` (nunca commitar).

## Ver também

`STATUS.md` (neste diretório).
