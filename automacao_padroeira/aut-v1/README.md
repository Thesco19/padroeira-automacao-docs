# Reconciliação Fiscal V2 (Padroeira)

Sistema de automação fiscal para Padroeira e Restaurante.

## Estrutura
- **`bot_reconciliation.py`**: Ponto de entrada (Telegram). Escuta comandos e orquestra todo o pipeline.
- **`async_reconciliation_v2.py`**: Motor central de orquestração.
- **`cortex_padroeira_async.py`**: Extração de dados (Saurus/Playwright).
- **`engine_consolidacao_async.py`**: Consolidação de diário.
- **`motor_balancete_async.py`**: Auditoria e injeção no Balancete.

## Como Usar
O bot roda continuamente em background escutando o Telegram.

### Ativação
Para subir o bot em modo escuta:
```bash
./start_async_reconciliation.sh
```
*O script trava múltiplas instâncias (via `.bot_reconciliation.lock`) e gera logs em `logs/reconciliation.log`.*

### Comandos no Telegram
Envie ao bot:
- `/reconciliar [AAMM]` — roda o pipeline completo para o período (ex: `2608`). Se omitido, processa o backlog do `Movto_cx2.xlsx`.
- `/fechar [AAMM]` — alias de reconciliar.
- `/amostra [N] [AAMM]` — roda um teste e2e com `N` datas pendentes.

## Desativação
Para parar o bot:
1. Encontre o processo: `ps aux | grep bot_reconciliation`
2. Encerre-o: `kill <PID>`
3. Remova o lock se necessário: `rm .bot_reconciliation.lock`
