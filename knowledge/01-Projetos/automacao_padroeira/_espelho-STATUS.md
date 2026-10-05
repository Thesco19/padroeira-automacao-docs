Espelho de /home/teco/work_out/lab-a/automacao_padroeira/STATUS.md em 2026-09-30; fonte: a pasta

# STATUS — automacao_padroeira

Estado: livre
Situação: ativo
Próximo passo: PASSO 1 do hardening — implementar allowlist de chat_id em bot_reconciliation.py (Supabase padroeira: current_task, fase hardening_bot_telegram, progresso 97).
Pendências e riscos: token do Telegram exposto precisa ser revogado no BotFather; 4 arquivos modificados e sem commit no repo lab-a (bot_reconciliation.py, async_reconciliation_v2.py, config_precos.py, cortex_padroeira_async.py); conferência manual das planilhas pelo usuário antes de prosseguir (ver log 2026-08-26).

## Log (mais recente primeiro, só acrescentar)

### 2026-09-30 11:12 — opencode (Fase 1, piloto)
- Pretende: criar README.md e este STATUS a partir do inventário.
- Fez: ambos criados. Situação ativo reverificada agora: processo bot_reconciliation.py em execução (pid vivo), recurso important com instância única no lab-master.
- Conclusão: pronto. Daqui: allowlist (PASSO 1), rotação do token (PASSO 2) e conferência manual das planilhas.

### 2026-08-26 — consolidado de aut-v1/AUX/status.md (original preservado)
- Pretende: corrigir planilhas incompletas (faltavam peso de refeição, peso de sobremesa e nº de clientes) e auditar o Kg Equivalente.
- Fez: causa raiz (cache de fechamentos indisponível no preflight) corrigida; parser refeito (findall + soma); limpeza destrutiva removida; token hardcoded do Telegram movido para .env; módulo config_precos.py criado; auditoria do caso 23/07/2026 validada (Refeição 89,25 kg, Sobremesa 10,54 kg); Sangria fixada na linha 42 e Total de Caixa como fórmula na linha 40; pré-produção 2608 executada (4 dias com cache, 12 células confirmadas, Pad2608.xlsx gerado); planilhas excluídas do git via .gitignore próprio.
- Conclusão: ficou pronto o pipeline corrigido e auditado. Ficou pela metade: conferência manual dos meses pelo usuário, revogação do token no BotFather, bugs antigos fora de escopo (colunas fantasma, balancete, credenciais Saurus). De onde partir: AUX/status.md (seções de pendências) + PASSO 1 acima.