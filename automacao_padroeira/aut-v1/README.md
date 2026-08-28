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
- Portanto: o PAD é **criado quando o Movto_diario é criado** e **atualizado quando o Movto_diario é atualizado**. `/fechar` (só leitura de faturamento + histórico) não toca o PAD.

## Como Usar
O bot roda continuamente em background escutando o Telegram.

### Ativação
Para subir o bot em modo escuta:
```bash
./start_async_reconciliation.sh
```
*O script trava múltiplas instâncias (via `.bot_reconciliation.lock`) e gera logs em `logs/reconciliation.log`.*

### Comandos no Telegram (ordem de uso)
1. **`/fechar`** — PRIMEIRO comando do operador. Puxa o **faturamento do dia** (linha 37 do Diário),
   lê para a **conferência de caixa** (Real / Sistema / Sangria) e **salva no histórico**
   (`historico_faturamento/faturamento_diario.json`) para uso futuro. Apenas leitura + histórico —
   não roda pipeline nem toca o balancete.
2. **`/finalizar [MMAA]`** — CONCLUI o preenchimento e o **transporte de dados**
   (Cortex → Engine → Balancete PAD). Sem MMAA, processa o **dia de hoje**; com MMAA, faz a
   **varredura completa** do período.
3. **`/reconciliar [AAMM]`** — alias de `/finalizar` (mantido por compatibilidade).
4. **`/amostra [N] [AAMM]`** — roda um teste e2e com `N` datas pendentes.

## Desativação
Para parar o bot:
1. Encontre o processo: `ps aux | grep bot_reconciliation`
2. Encerre-o: `kill <PID>`
3. Remova o lock se necessário: `rm .bot_reconciliation.lock`
