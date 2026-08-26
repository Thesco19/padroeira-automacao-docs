# Status — Automação Padroeira (aut-v1)

> Última atualização: 2026-08-26 — correções aplicadas (parser, cache, token) e planilhas regeneradas.

## Avanço implementado (2026-08-26)
- **Causa raiz da planilha incompleta:** as saidas pad_prod_test/Movto_diario.2606.xlsx e 2607.xlsx eram stale — geradas (07/ago e 21/ago) antes de o cache fechamentos/ estar disponivel para injecao das linhas 3/4/5 (peso comida, peso sobremesa, nro de clientes). Reproduzindo o pipeline hoje com o codigo corrigido + 179 arquivos no cache, as 26/26 colunas passam a ser preenchidas em ambos os meses.
- **Bug 1 — parser _parsear_fechamento:** re.search para REFEICAO QUILO / SOBREMESA QUILO subcontava dias com 2+ linhas. Trocado por re.findall + soma (helper _somar_kg). Ex.: 2026-06-06 de 2.160 -> 74.211 kg.
- **Bug 2 — limpeza destrutiva:** removido limpar_fechamentos_antigos() de carregar_cache_fechamentos() (apagaria 146/179 arquivos >60d). Nada em fechamentos/ foi deletado (seguem 179 arquivos).
- **Planilhas regeneradas:** Movto_diario.2606.xlsx e 2607.xlsx recriados com 26/26 colunas preenchidas nas linhas 3/4/5.
- **Seguranca:** removido token hardcoded de Telegram de pad_prod_test/cortex_padroeira_async.py -> agora via _ler_env("TELEGRAM_TOKEN", BASE_DIR) com raise RuntimeError se ausente. Revogar token exposto no BotFather.

## Avanço implementado (2026-08-26, parte 2): Kg Equivalente
- **Novo modulo config_precos.py:** tabela de precos isolada e configuravel (REFEICAO_*, REFEICAO_KG_PADRAO=96,90 dias uteis, REFEICAO_KG_SABADOS=104,90 sabado). Funcao valor_kg_dia(data) aplica regra de dia da semana e aceita override por data via OVERRIDE_KG_POR_DATA ou config_precos.json opcional.
- **Parser _parsear_fechamento (cortex + pad_prod_test):** agora extrai qtd A Vontade e To Save (UN), e valores em R$ de PRATOS EXECUTIVOS e DOCES (secao SUBCATEGORIAS VENDIDAS). Calcula kg_eq_ref (linha 3) e kg_eq_sob (linha 4) = soma em R$ / VALOR_KG_DIA.
- **Engine (ambos):** injeta kg_eq_ref na linha 3 e kg_eq_sob na linha 4 (e clientes na 5). Post-flight MAPA_ROWS atualizado para kg_eq_ref/kg_eq_sob. Mantem peso_buf/peso_sob no dict do parser (nao injetados).
- **Bug corrigido no processo:** escape  vazou como caractere de controle no heredoc em ambos os cortex (r_doces). Corrigido para r"DOCES\s+...".
- **Auditoria:** auditar_kg_equivalente.py roda sobre fechamento_caixa_2026-07-23.txt e exibe a memoria de calculo. Caso 23/07/2026 validado: Refeicao 89,25 kg [OK], Sobremesa 10,54 kg [OK]. Planilhas Movto_diario.2606/2607 regeradas com injecao confirmada (post-flight OK; 2026-07-23 -> row3=89,25, row4=10,542, row5=155).
- **Pendente (conferencia manual do usuario):** demais meses (2601-2605,2608) e bugs antigos (colunas fantasma, balancete, credenciais Saurus) seguem sem tocar, por decisao do usuario. Observacao: Movto_diario.2606 foi recriado a partir do template 2607 pelo motor (arquivo nao rastreado no git); conferir se os demais meses precisam do mesmo tratamento.


## Contexto do projeto

Pipeline de reconciliação financeira da Padroeira:

1. `start_async_reconciliation.sh` → `async_reconciliation_v2.py` (orquestrador)
2. **Cortex** (`cortex_padroeira_async.py`) — extrai fechamentos do portal Saurus + verifica paridade
3. **Engine Consolidação** (`engine_consolidacao_async.py`) — preenche `Movto_diario.{AAMM}.xlsx` a partir de `Movto_cx2.xlsx` e injeta métricas Saurus nas linhas 3/4/5
4. **Motor Balancete** (`motor_balancete_async.py`) — transpõe o diário para `Pad{AAMM}.xlsx`

Fontes:
- `Movto_cx2.xlsx` — caixa 2 (faturamento, preenchido pela Sandra)
- `fechamentos/fechamento_caixa_{data}.txt` — fechamentos do Saurus (peso/clientes/totais), extraídos em batch
- `Movto_diario.{AAMM}.xlsx` e `Pad{AAMM}.xlsx` — gerados

## Diagnóstico — por que os dados não foram preenchidos

### Estado real dos arquivos
- **Faturamento (linhas 6–40):** preenchido corretamente nas colunas do mês-alvo de cada diário (confere com o Caixa 2).
- **Métricas Saurus (linhas 3/4/5 = Peso buffet, Peso sobremesa, Clientes):** vazias em **todos** os meses. Só `2606` tem 15/26 colunas, com valores parciais/duvidosos (1, 2, 3 / 100, 15, 100).
- **Pad2601:** Peso Buf/Peso Sob = 0 em todos os dias; **dias 4 e 31 ausentes**; dias 7/21/28 duplicados fora de ordem (linhas 28–30).

### Causas raiz
1. **Timing:** as reconciliações rodaram em 07/ago (15:02–16:14, `logs/reconciliation.log`), mas os fechamentos do Saurus só foram extraídos em **08/ago** (`batch_extracao.log`, `batch_fix.log`). `dados_por_data` vazio → Engine sem fonte para peso/clientes.
2. **Gatilho de extração não dispara:** em `async_reconciliation_v2.py:127`, a extração só roda `if cortex.pendentes:` (datas ausentes do calendário). Como todas as colunas já existem, `pendentes` fica vazio → `dados_cortex` = `{}` (`async_reconciliation_v2.py:269`) → Engine pula a injeção das linhas 3/4/5 (depende de `dados_dia`, `engine_consolidacao_async.py:255`).
3. **Colunas "fantasma":** sem `template_Movto_diario.xlsx`, cada mês é copiado do mês anterior e `_limpar_colunas_diario` (`engine_consolidacao_async.py:65`) apaga dados mas **preserva a linha 1** (cabeçalhos). Resultado: `2601` carrega 26 colunas de junho vazias, `2602` junho+janeiro, etc. → logs "injeção em N colunas pendentes… 0 células tratadas" (execuções 15:50/16:14).
4. **Balancete com grade fixa herdada:** copia do `Pad2606` (grade de junho); dias extras entram desordenados e, sem espaço até a linha 31, alguns somem (dia 4 e 31 em `Pad2601`).
5. **Parser OK:** as regex de `_parsear_fechamento` funcionam com os fechamentos atuais (ex.: `2026-01-02` → peso 52.168, clientes 97). O dado existe e está correto — só nunca foi injetado.
6. **Segurança (menor):** credenciais hardcoded — `TOKEN_TELEGRAM` (`cortex_padroeira_async.py:35`) e user/senha do Saurus (`pdv_saurus_extractor.py:28-30`).

## Proposta de correção (aprovada para planejar — não implementada)

### Correção 1 — Métricas Saurus (linhas 3/4/5) [causa principal]
- `cortex_padroeira_async.py`: novo método `carregar_cache_fechamentos()` — varre `fechamentos/fechamento_caixa_*.txt`, parseia cada um em `dados_por_data`.
- `async_reconciliation_v2.py:127`: chamar `carregar_cache_fechamentos()` **sempre** no preflight; `extrair_todos_pendentes` só para datas sem arquivo.
- `engine_consolidacao_async.py`: passo separado e idempotente que percorre **todas** as colunas com data em `dados_cortex` e grava linhas 3/4/5; registrar em `alvos_verificacao` (post-flight `:391`).

### Correção 2 — Colunas fantasma
- `engine_consolidacao_async.py:65` `_limpar_colunas_diario`: apagar também o cabeçalho (linha 1) das colunas B..; o engine regenera o calendário do mês-alvo na expansão (`:205-217`).

### Correção 3 — Balancete
- `motor_balancete_async.py:76` `_limpar_dados_pad`: limpar também a coluna A (números dos dias).
- `motor_balancete_async.py` `injetar_balancete`: dias em ordem crescente a partir da linha 2; garantir espaço p/ 31 dias (inserir linhas se necessário).
- Peso no balancete passa a vir das linhas 3/4 do diário (mapa `B=3, C=4`) após Correção 1.

### Correção 4 — Reparo único dos arquivos atuais
- Rebuild dos 8 `Movto_diario.*` e `Pad{2601..2605,2607,2608}` (Pad2606 é a base estrutural; preserva abas Salarios/Pagamentos/etc.).
- Opção A: modo `--repair` (reconstrói in-place).
- Opção B: apagar arquivos gerados e reexecutar o pipeline.

### Correção 5 (segurança, opcional) — credenciais
- Mover token do Telegram e credenciais do Saurus para `.env`.

## Perguntas em aberto (antes de implementar)
1. Reparo: regenerar os `Movto_diario`/`Pad` atuais ou corrigir in-place?
2. Layout do Pad: zona de dias vai até linha 30/31? Preciso inserir linhas se mês tiver mais dias?
3. `Movto_cx2.xlsx` é a fonte única/confiável do faturamento? (alinhamento linha a linha validado)
4. Fechamento faltante: chamar o portal Saurus (Playwright) automaticamente ou usar só o cache local?

## Arquivos-chave
- `async_reconciliation_v2.py` — orquestrador
- `cortex_padroeira_async.py` — extração Saurus + paridade
- `engine_consolidacao_async.py` — diário mensal
- `motor_balancete_async.py` — balancete (Pad)
- `extrair_batch_saurus.py` / `pdv_saurus_extractor.py` — extração batch do portal
- `logs/reconciliation.log`, `batch_extracao.log`, `batch_fix.log` — histórico de execução

---

## VERIFICAÇÃO FINAL (2026-08-26, turno de consolidação)
Checagem independente do que foi entregue antes da conferência manual do usuário:

- **Auditoria OK**: `python3 auditar_kg_equivalente.py` (caso 23/07/2026, Quinta) retorna:
  - Refeição 89,25 kg [OK]; Sobremesa 10,54 kg [OK]; VALOR_KG_DIA = R$ 96,90.
  - Memória de cálculo conferida: 77,084×96,90 + 14×63,90 + 1×13,90 + 270,40 = 8.648,34 /96,90 = 89,25 kg; 0,175×96,90 + 1.004,60 = 1.021,56 /96,90 = 10,54 kg.
- **Injeção confirmada na planilha real**: `pad_prod_test/Movto_diario.2607.xlsx`, coluna do dia 23/07/2026 →
  linha 3 = 89,25 · linha 4 = 10,542 · linha 5 (clientes) = 155.
- **Token do Telegram seguro**: removido o hardcoded exposto (`8890227531:AAEW...9Ro`). Ambos `cortex_padroeira_async.py` e
  `pad_prod_test/cortex_padroeira_async.py` leem via `_ler_env("TELEGRAM_TOKEN", BASE_DIR)` com `raise RuntimeError` se ausente.
  Nenhuma ocorrência do token exposto resta em .py/.md/.txt/.json/.env. **Ação pendente do usuário: revogar o token no BotFather.**
- **Módulos isolados**: `config_precos.py` (tabela configurável + `valor_kg_dia(data)` com override por data) e
  `auditar_kg_equivalente.py` (script de teste/auditoria) criados e funcionando.
- **Parser corrigido**: uso de `re.findall`+soma para REFEICAO/SOBREMESA QUILO (dias com múltiplas linhas) e regex
  `r"\bDOCES\s+..."` (palavra inteira). Engine injeta kg_eq_ref (linha 3) e kg_eq_sob (linha 4); `MAPA_ROWS` do post-flight atualizado.

### Pendências (decisão do usuário — conferência manual antes de prosseguir)
- Conferência manual dos meses 2606/2607 (e extensão para 2601–2605/2608) pelo usuário.
- `Movto_diario.2606` foi recriado a partir do template 2607 pelo motor (não rastreado no git) — usuário deve conferir.
- Bugs antigos fora de escopo nesta etapa: colunas fantasma, balancete (grade fixa/dias extras), credenciais Saurus no `.env`.

---

## CORREÇÃO — Rótulo da Sangria (Linha 42) e Pré-Produção 2608 (2026-08-26, turno final)

### Contexto e correção
- **O sistema já buscava a Sangria corretamente no Caixa 2 (linha 42) e a copiava para o Diário.** O erro
  anterior meu foi *remapear* a Sangria para a linha 40 (valor + rótulo) e empurrar a fórmula de Total de
  Caixa para a linha 41 — incorreto.
- **Layout correto (confirmado no `Movto_diario.2607.xlsx` base):** a fórmula de Total de Caixa
  `=C37-C38` fica na **Linha 40**; o rótulo "Sangria" e seu valor ficam na **Linha 42** (espelhados do Cx2).
- **Causa do rótulo errado:** em openpyxl, `Worksheet.cell(row, column, value=None)` **NÃO apaga** a célula
  (apenas retorna a existente). Por isso o bloco de limpeza que eu havia escrito não removia resíduos.
- **Correção aplicada em ambos os motores** (`engine_consolidacao_async.py` e
  `pad_prod_test/engine_consolidacao_async.py`): revertido o copy-loop para o comportamento original
  (linha 40 = fórmula `=col37-col38`; Sangria copiada raw da linha 42 do Cx2) e ajustado o bloco de
  rótulos para **garantir "Sangria" na linha 42** e limpar eventuais resíduos nas linhas 40/41 via
  atribuição `ws.cell(...).value = None`.

### Layout do diário após o fix (validado em Movto_diario.2608.xlsx)
- Linha 3: `Peso buffet` (kg_eq_ref)
- Linha 4: `Peso sobremesa` (kg_eq_sob)
- Linha 5: `Clientes`
- Linhas 6–39: Faturamento / módulos do Caixa 2
- **Linha 40: fórmula `=col37-col38` (Total de Caixa)** ✅
- **Linha 42: `Sangria` (etiqueta + valor)** ✅
- Linha 41: vazia ✅

### Pré-produção 2608 (sem Telegram — gatilho desativado por design)
- Executado via `pad_prod_test/pre_producao_2608.py` (carrega só o cache local de fechamentos; `bot=None`).
- Entrada Cx2: `Movto_cx2.xlsx` (agosto/2026). Entrada Saurus: cache `fechamentos/fechamento_caixa_2026-08-*.txt`.
- Métricas injetadas (linhas 3/4/5) e Sangria (linha 42) para os 4 dias com cache em agosto:
  - 2026-08-01 → ref=87,297 · sob=11,225 · clientes=137 · sangria(r42)=150
  - 2026-08-03 → ref=98,655 · sob=8,084 · clientes=202 · sangria(r42)=0
  - 2026-08-07 → ref=73,16 · sob=6,556 · clientes=123 · sangria(r42)=300
  - 2026-08-08 → ref=84,292 · sob=9,47 · clientes=127 · sangria(r42)=400
- Post-flight: 12 células de métricas confirmadas (rows 3/4/5). Balancete `Pad2608.xlsx` gerado (22 dias transpostos).
- Divergências caixa×computado acima de R$30: 4 dias (reconferência manual, esperado — sem Telegram disparado).
- `.env` de `pad_prod_test/` e raiz usam token dummy (`TELEGRAM_TOKEN=1234567890:AAAA_DUMMY_NAO_DISPARA`) — nunca o real.

### Pendências
- **Regra de exclusão de planilhas (26/08/2026):** NENHUMA planilha deve ir para o Git. Criado aut-v1/.gitignore ignorando *.xlsx, *.xls, *.xlsm e travas de lock. Confirmado via git check-ignore: Movto_cx2.xlsx, Movto_diario.2606/2607/2608.xlsx e Pad2608.xlsx estão ignorados. Única planilha ainda rastreada é o template base automacao_padroeira/templates/Movto_diario.2606.xlsx (fora de aut-v1).
- **Git bloqueado neste ambiente:** o .git de /home/teco/work_out/lab-a está montado como somente leitura (fatal: Unable to create '.../.git/index.lock'). Nenhum git add/rm/commit roda daqui. O commit das entregas (engine, config_precos, cortex, status.md) e a remoção do template .xlsx do índice devem ser feitos em ambiente gravável.
- **Não** commitar .env, __pycache__, arquivos deleted antigos. Token real segue exposto e deve ser revogado no BotFather.

---

## DECISAO - Exclusao de Planilhas do Git + Status do Teste de Producao 2608 (2026-08-26)

### Regra: planilhas fora do Git
- Criado automacao_padroeira/aut-v1/.gitignore com *.xlsx, *.xls, *.xlsm e travas de lock.
- Validação (git check-ignore -v) confirma que Movto_diario.2608.xlsx, Pad2608.xlsx, Movto_cx2.xlsx e Movto_diario.2606.xlsx (dentro de aut-v1/pad_prod_test) estão ignorados.
- Template base automacao_padroeira/templates/Movto_diario.2606.xlsx permanece no índice (fora de aut-v1); decidir se também removê-lo do Git.

### Teste de produção 2608 (pre-prod) - resposta
- As planilhas de agosto foram criadas e preenchidas corretamente: Movto_diario.2608.xlsx com Peso buffet (r3), Peso sobremesa (r4), Clientes (r5), Sangria na r42 e Total de Caixa (fórmula =col37-col38) na r40; Pad2608.xlsx transpôs 22 dias.
- O robô Playwright NAO rodou neste teste. O pre_producao_2608.py carrega só o cache local (sem Playwright, sem extração de portal). Os dados vieram dos arquivos fechamento_caixa_2026-08-01/03/07/08.txt já existentes. Por isso só 4 dias de agosto têm métricas (cobertura do cache), não os 31.
- O pdv_saurus_extractor.py (Playwright) está instalado e com seletores validados em 08/ago/2026, mas não foi acionado nesta rodada.

---

## PLANO FINAL DE COMMIT / REORGANIZACAO (26/08/2026, aprovado por Paulo)

### Diagnostico real do bloqueio Git (corrige o diagnostico anterior da tarefa)
- NAO e permissao negada nem index.lock orfao: o arquivo .git/index.lock NAO existe.
- O diretorio .git esta com permissoes corretas (drwxrwxr-x teco:teco).
- Causa real: o FS do .git esta montado read-only (ext4 ro, errors=remount-ro em /). touch dentro de .git falha. sudo bloqueado (no new privileges flag).
- Consequencia: qualquer git add/rm/commit falha com Unable to create '.../.git/index.lock': Sistema de arquivos somente para leitura. Os comandos chmod -R u+rwX e rm -f index.lock da tarefa SAO INEFICACES aqui.
- O worktree de aut-v1 (incluindo este status.md) EH gravavel; apenas o .git e read-only. Portanto edito docs/RAG daqui, mas o commit precisa rodar em ambiente com o .git gravavel.

### Decisao aprovada (sim)
1. Remover o template do indice Git (continua no disco, sai do rastreamento):
   git rm --cached automacao_padroeira/templates/Movto_diario.2606.xlsx
2. Adicionar codigo + docs + gitignore (planilhas caem sozinhas pelo .gitignore de aut-v1):
   git add automacao_padroeira/aut-v1/engine_consolidacao_async.py automacao_padroeira/aut-v1/config_precos.py automacao_padroeira/aut-v1/cortex_padroeira_async.py automacao_padroeira/aut-v1/auditar_kg_equivalente.py automacao_padroeira/aut-v1/status.md automacao_padroeira/aut-v1/.gitignore
3. Commit:
   git commit -m "feat: inclui engine no git, fixa sangria na linha 42 e roda pré-produção de 2608"

### Estado de tracking atual (antes do commit)
- Unica planilha ainda no indice: automacao_padroeira/templates/Movto_diario.2606.xlsx (template base, fora de aut-v1).
- engine/config/cortex/auditar/status.md: NAO estao no indice (aut-v1 inteiro aparece como untracked ??).

### Pendencia de execucao
- Rodar os 3 passos acima onde o .git for gravavel (fora deste container / apos remount RW autorizado). Documentado e pronto; nao executavel daqui.
