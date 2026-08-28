# Reconciliação Fiscal V2 (Padroeira)

Sistema de automação fiscal para Padroeira e Restaurante.

## Estrutura
- **`bot_reconciliation.py`**: Ponto de entrada (Telegram). Escuta comandos e orquestra todo o pipeline.
- **`async_reconciliation_v2.py`**: Orquestrador central (ordena Cortex → Engine → Motor).
- **`cortex_padroeira_async.py`**: Extração de dados (Saurus/Playwright).
- **`engine_consolidacao_async.py`**: Consolidação do Movto_diario (Diário).
- **`motor_balancete_async.py`**: Geração/atualização do Balancete PAD (derivado do Diário).

### Regra do Balancete PAD
O Balancete PAD **nunca é escrito de forma independente**. Ele é sempre **derivado do Movto_diario**:
- No orquestrador, o Engine (que cria/atualiza o Movto_diario) roda **antes** do Motor (que gera/atualiza o PAD).
- `injetar_balancete()` **lê** o `Movto_diario.{AAMM}.xlsx` e **transpõe** os dias/valores para `Pad{AAMM}.xlsx`. Se o Diário não existir, o Motor nem roda.
- Portanto: o PAD é **criado quando o Movto_diario é criado** e **atualizado quando o Movto_diario é atualizado**. `/fechar` (só leitura de faturamento) não toca o PAD.

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
- `/finalizar [MMAA]` — roda o pipeline completo para o período (ex: `2608`). Se omitido, processa o **dia de hoje**.
- `/reconciliar [AAMM]` — alias de `/finalizar` (mantido por compatibilidade).
- `/fechar` — envia o **faturamento do dia** (linha 37 do Diário) sem rodar o pipeline.
- `/amostra [N] [AAMM]` — roda um teste e2e com `N` datas pendentes.

## Desativação
Para parar o bot:
1. Encontre o processo: `ps aux | grep bot_reconciliation`
2. Encerre-o: `kill <PID>`
3. Remova o lock se necessário: `rm .bot_reconciliation.lock`
