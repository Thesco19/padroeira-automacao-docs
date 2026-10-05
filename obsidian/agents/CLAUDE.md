# Projeto: Automação & Reconciliação Padroeira (aut-v1 Async)

## Ferramentas & CLI Ativas
- Agentes suportados: Claude Code, Codex, OpenCode.
- Módulo Principal: automacao_padroeira/aut-v1/

## Contexto e Premissas do Ecossistema
- Orquestração Assíncrona: Bot Telegram + Playwright (sessão única) + Openpyxl.
- Regra do Restaurante: O restaurante NUNCA abre em dias sem movimento no caixa (calendario_padroeira.py).

## Regras Invioláveis de Código & Excel
- Integridade de Fórmulas no Excel:
  - Linha 14 e Linha 40 do Movimento Diário (Movto_diario.26XX.xlsx): NUNCA gravar valores estáticos, SEMPRE usar fórmulas literais (ex: ={col}37-{col}38 na linha 40).
  - Coluna Q do Balancete (Pad26XX.xlsx): NUNCA valor estático, SEMPRE =SUM(B{linha}:P{linha}).
- Mapeamento de Sangria: Gravada na Linha 42 do Movto_diario e espelhada no Balancete.

## Estrutura Atual de Arquivos (aut-v1)
- bot_reconciliation.py: Bot Telegram principal. Comandos: /fechar (parcial em tempo real), /finalizar (reconciliação + cleanup de processos órfãos) e /doctor (diagnóstico IA de logs).
- async_reconciliation_v2.py: Orquestrador assíncrono central.
- cortex_padroeira_async.py: Parsing dos relatórios (fechamento_caixa_YYYY-MM-DD.txt) e cálculo do Kg Equivalente.
- extrator_saurus_sessao.py: Automação Playwright em sessão única para o portal Saurus.
- engine_consolidacao_async.py: Injeção e auditoria no Movto_diario e Pad.
- calendario_padroeira.py: Regra de dias operacionais vs dias fechados.

## Diretrizes do Ambiente
- Logs: Registrados em logs/reconciliation.log.
- Início do Serviço: ./start_async_reconciliation.sh
- Ambiente: Linux Mint no Mac Mini (teco-Macmini).

