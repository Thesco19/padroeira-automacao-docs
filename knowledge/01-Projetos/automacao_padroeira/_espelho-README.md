Espelho de /home/teco/work_out/lab-a/automacao_padroeira/README.md em 2026-09-30; fonte: a pasta

# automacao_padroeira

Classe: projeto
Local: lab-a
Nomes em outros sistemas: RAG tag=restaurante | Supabase=padroeira | ObSV=01-Projetos/Padroeira-aut-v1.md + 01-Projetos/Reconciliacao-Fiscal-V2/ | LM project=lab-a/automacao_padroeira/aut-v1

## O que é

Automação da reconciliação financeira do restaurante Padroeira: extração de fechamentos do portal Saurus, consolidação no diário mensal (Movto_diario) e transposição para o balancete (Pad). aut-v1 é a versão de produção (bot Telegram + orquestrador assíncrono); aut-v0 é legado e está fora do git.

## Como rodar / onde vive

O bot roda continuamente em background: processo bot_reconciliation.py (recurso criticality: important, instância única no lab-master). Início do serviço: ./start_async_reconciliation.sh (conforme CLAUDE.md do projeto). Logs em aut-v1/logs/reconciliation.log.

## Estrutura

- aut-v1/ — produção: bot_reconciliation.py, async_reconciliation_v2.py (orquestrador), cortex_padroeira_async.py (extração Saurus + Kg Equivalente), engine_consolidacao_async.py (diário), motor_balancete_async.py (Pad), config_precos.py, calendario_padroeira.py, extrator_saurus_sessao.py (Playwright), logs/, AUX/status.md, .gitignore próprio (planilhas fora do git), README.md próprio.
- aut-v0/ — versão anterior, ignorada pelo git.

## Dependências

Portal Saurus via Playwright (extração de fechamentos); bot Telegram; Supabase lab-g (status e handoffs do projeto padroeira).

## Segredos

Só o caminho: aut-v1/.env (nunca commitar; ver .gitignore). Atenção: o token do Telegram precisa ser rotacionado no BotFather (pendência registrada em aut-v1/AUX/status.md).

## Ver também

STATUS.md (neste diretório), aut-v1/README.md, aut-v1/AUX/status.md.