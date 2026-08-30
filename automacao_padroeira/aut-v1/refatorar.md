# Análise de Código - aut-v1 (Baseada em código completo)

> Análise estática baseada no conteúdo integral dos arquivos do diretório
> `automacao_padroeira/aut-v1/` (sem subdiretórios). Objetivo: registrar erros,
> inconsistências e oportunidades de refatoração. Nenhuma alteração de código foi
> feita, apenas este documento.

## 1. I/O Síncrono bloqueando event loop (Async vs Sync)
As classes com sufixo "Async" (`CortexPadroeiraAsync`, `EngineConsolidacaoAsync`,
`MotorBalanceteAsync`) expõem métodos síncronos (`def`) que realizam leitura/escrita
de arquivos e planilhas (`openpyxl.load_workbook`, `open`, etc.). O orquestrador
`AsyncReconciliationEngine` (em `async_reconciliation_v2.py`) invoca esses métodos
com `await` dentro de funções `async`, mas como os métodos não são `async def`, o
event loop é bloqueado durante o processamento de arquivos. Não causa crash, mas
anula o benefício do asyncio e pode travar outros comandos do bot Telegram.

## 2. Abertura repetida de Movto_cx2.xlsx por dia (Performance)
Em `calendario_padroeira.py`, a função `tem_movimento_cx2` abre e carrega o
`Movto_cx2.xlsx` do zero a cada chamada. `dia_eh_fechado` é chamada para cada dia do
mês em `motor_balancete_async._validar_dias_ausentes` e em
`cortex.verificar_paridade_planilhas`, resultando em dezenas de aberturas do mesmo
arquivo. Deveria abrir uma vez e cachear as datas presentes.

## 3. Leitura de planilha desatualizada em `engine_consolidacao_async.py` (ETAPA 2.6)
`ws_me_lei` é carregado no início da função `executar_motor_unificado` (antes da
injeção). Na ETAPA 2.6, para colunas recém-criadas (pendentes),
`ws_me_lei.cell(row=24, column=col).value` será `None` (pois a injeção ainda não
ocorreu naquele objeto). Assim, a comparação de `total_bruto` cai no fallback ou é
ignorada para dias novos. Não é erro de execução, mas pode mascarar divergências em
dias recém-adicionados.

## 4. Transposição redundante de fórmulas em `motor_balancete_async.py`
Em `injetar_balancete`, a seção (b) escreve `=SUM(...)` para a linha de totais
(cols 2..17) após inserir linhas, e a seção (f) sobrescreve D, Q, R e novamente faz
loop 2..18 com `=SUM(...)`. Código morto, porém inofensivo. Recomenda-se remover a
duplicação para evitar confusão.

## 5. Tratamento de transação em `backup_padroeira.py`
O context manager `_conexao()` faz `conn.commit()` apenas no sucesso e `conn.close()`
no `finally`, sem `conn.rollback()` explícito em caso de exceção. O SQLite faz
rollback ao fechar a conexão, mas à prova de falhas exigiria rollback explícito.

## 6. Import dinâmico e fallback amplo em `cortex_padroeira_async.py`
`_parsear_fechamento` faz `from config_precos import valor_kg_dia, REFEICAO_COM_SOBREMESA`
dentro da função e captura `Exception` genérica para usar defaults. Se o módulo
`config_precos` tiver erro de import, o fallback silencia o problema. Aceitável, mas
frágil para debugging.

## 7. Duplicação de constantes
`DATA_MINIMA_PROCESSAMENTO` é definida em `engine_consolidacao_async.py` e repetida
(embutida) em `cortex_padroeira_async.py`. `async_reconciliation_v2.py` importa de
engine, mas cortex define a sua própria. Risco de divergência silenciosa.

## 8. Fallbacks de offset em `_realinhar_fórmulas_estruturais` (motor)
Se os rótulos estruturais ("Particip.", "Projeção") não forem encontrados após
inserção de linhas, usa fallbacks `base+2`, `base+3`, `base+4`. Caso a planilha
template mude, os offsets podem não bater e as fórmulas apontarem para linhas erradas.

## 9. `extrator_saurus_sessao.py` e `pdv_saurus_extractor.py`
A função `expandir_e_marcar` é `async def` e corretamente aguardada com `await` dentro
do lote. Não há erro de coroutine. Porém, há lógica de navegação duplicada entre os
dois módulos (seletores e fluxo de login), o que pode gerar manutenção divergente.

## Conclusão
Nenhum erro crítico que impeça a execução foi encontrado. Os pontos 1 e 2 merecem
refatoração prioritária para performance e correta arquitetura assíncrona.
