# Análise de Erros e Correções - aut-v1

> Exame dos arquivos do diretório `automacao_padroeira/aut-v1` (sem subdiretórios).
> Objetivo: registrar erros e inconsistências de código, e documentar as correções
> efetivamente aplicadas (ver seção "Status de Correção" ao final).

## 1. Erro Arquitetural Assíncrono (Bloqueio de Event Loop)
As classes `CortexPadroeiraAsync`, `EngineConsolidacaoAsync` e `MotorBalanceteAsync` possuem métodos síncronos (`def`) que executam I/O de arquivos (ex: `openpyxl.load_workbook`). O orquestrador `AsyncReconciliationEngine` aguarda esses métodos com `await` dentro de funções `async`, o que não é válido para funções síncronas e bloqueia o event loop, anulando o modelo assíncrono e podendo travar o bot.

## 2. Erro de Lógica em Leitura de Planilha (ETAPA 2.6)
Em `engine_consolidacao_async.py`, `ws_me_lei` é carregado antes da injeção de dados. Na ETAPA 2.6, ao verificar colunas recém-criadas, `ws_me_lei.cell(...).value` retorna `None`, fazendo com que a comparação de `total_bruto` use fallback ou seja ignorada, mascarando divergências.

## 3. Falta de Rollback Explícito em Transação
Em `backup_padroeira.py`, o context manager `_conexao()` não chama `conn.rollback()` em caso de exceção, confiando no fechamento da conexão. Isso é frágil e pode deixar transações parciais em caso de falhas inesperadas.

## 4. Captura de Exceção Ampla e Silenciosa
Em `cortex_padroeira_async.py`, `_parsear_fechamento` importa `config_precos` dentro da função e captura `Exception` genérica para usar defaults. Erros de import reais são silenciados, dificultando o debug.

## 5. Offsets de Fórmulas Frágeis (Risco de Erro em Runtime)
Em `motor_balancete_async.py`, `_realinhar_fórmulas_estruturais` utiliza fallbacks `base+2`, `base+3` se rótulos não forem achados. Mudanças no template da planilha farão as fórmulas apontarem para linhas erradas sem erro explícito.

## 6. Duplicação de Constantes (Risco de Divergência)
`DATA_MINIMA_PROCESSAMENTO` está definida em `engine_consolidacao_async.py` e embutida em `cortex_padroeira_async.py`. Divergências silenciosas podem ocorrer.

## 7. Abertura Repetida de Arquivo (Lock e Performance)
`tem_movimento_cx2` em `calendario_padroeira.py` abre `Movto_cx2.xlsx` do zero a cada dia do mês, causando dezenas de aberturas e risco de lock de arquivo.

## 8. Código Morto / Fórmulas Redundantes
Em `motor_balancete_async.py` (`injetar_balancete`), há sobrescrita redundante de `=SUM(...)` (seções b e f), confundindo a manutenção.

## 9. Duplicação de Lógica de Navegação
`extrator_saurus_sessao.py` e `pdv_saurus_extractor.py` possuem seletores e fluxo de login duplicados, gerando risco de manutenção divergente.

## Conclusão da Análise Original
Não há erros de sintaxe que impeçam a execução, mas os pontos 1 e 2 são erros lógicos/arquiteturais que afetam a correta execução assíncrona e a validação de dados.

## Status de Correção (sessão de refatoração — CÓDIGO ALTERADO)
- **Item 1**: Resolvido em `async_reconciliation_v2.py` (uso de `asyncio.to_thread` para métodos síncronos).
- **Item 2**: Resolvido em `engine_consolidacao_async.py` (leitura do total do Caixa 2 via `mapa_cx_datas` em vez de `ws_me_lei` obsoleto).
- **Item 3**: Resolvido em `backup_padroeira.py` (adição de `conn.rollback()` no context manager `_conexao()`).
- **Item 4**: Resolvido em `cortex_padroeira_async.py` (captura específica de `ImportError` e log de erro explícito).
- **Item 5**: Resolvido em `motor_balancete_async.py` (varredura completa da coluna A e `RuntimeError` explícito em vez de offsets `base+2/3/4`).
- **Item 6**: Resolvido em `cortex_padroeira_async.py` (importação de `DATA_MINIMA_PROCESSAMENTO` do engine, eliminando duplicação).
- **Item 7**: Resolvido em `calendario_padroeira.py` (cache LRU do cabeçalho do `Movto_cx2.xlsx`).
- **Item 8**: Resolvido em `motor_balancete_async.py` (remoção de sobrescrita redundante de `SUM` na seção (f)).
- **Item 9**: Mitigado via `extrator_saurus_sessao.py` reutilizando seletores e funções de `pdv_saurus_extractor.py` (imports explícitos).

> Documento atualizado após aplicação das correções em todos os arquivos citados.
> Nenhuma alteração pendente conhecida para os itens levantados.
