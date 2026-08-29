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
1. **`/fechar`** — PRIMEIRO comando do operador. **Consulta o faturamento PARCIAL
   DO DIA em tempo real**: **apaga o cache do dia** (`fechamentos/fechamento_caixa_{data}.txt`)
   e **ENTRA no Saurus** (Playwright) para baixar a foto **atualizada** do
   faturamento parcial, lê para a **conferência de caixa**, **envia** ao Telegram
   e **salva o relatório** (cache + histórico em
   `historico_faturamento/faturamento_diario.json`) para o `/finalizar` usar.
   Se o Playwright estiver indisponível, reaproveita o cache existente como fallback.
2. **`/finalizar [MMAA]`** — CONCLUI o preenchimento e o **transporte de dados**
   (Cortex → Engine → Balancete PAD), consumindo os relatórios baixados pelo
   `/fechar`. Sem MMAA, processa o **dia de hoje**; com MMAA, faz a
   **varredura completa** do período. Ao final, **limpa os processos
   Playwright/Chromium órfãos** e as travas temporárias do `/tmp`.
3. **`/reconciliar [AAMM]`** — alias de `/finalizar` (mantido por compatibilidade).
4. **`/amostra [N] [AAMM]`** — roda um teste e2e com `N` datas pendentes
   (com cleanup de órfãos ao final).
5. **`/doctor`** — comando de **diagnóstico em tempo real**. Lê as últimas 100
   linhas de `logs/reconciliation.log`; se não houver erros, responde que tudo
   opera normalmente. Caso haja erro/traceback, envia o trecho à **API de IA**
   (Gemini ou OpenAI, conforme `GEMINI_API_KEY`/`OPENAI_API_KEY` no `.env`) e
   retorna: 🔍 **Diagnóstico do Erro** + 🛠️ **Prompt para Ajuste** (bloco de
   código com instruções exatas para o agente corrigir a falha). Sem chave de IA
   configurada, devolve o trecho do log para análise manual.

## Desativação
Para parar o bot:
1. Encontre o processo: `ps aux | grep bot_reconciliation`
2. Encerre-o: `kill <PID>`
3. Remova o lock se necessário: `rm .bot_reconciliation.lock`

## Configuração de IA (comando /doctor)
O `/doctor` consulta uma API de IA para gerar o diagnóstico. Adicione **uma** das
chaves ao `.env` local (nunca versionado):

```
GEMINI_API_KEY=...   # prioridade; usa models/gemini-3.1-flash-lite
# ou
OPENAI_API_KEY=...   # usa gpt-4o-mini
```

Se nenhuma chave estiver presente, o `/doctor` ainda detecta erros nos logs e
devolve o trecho cru para análise manual (sem dependência externa).

