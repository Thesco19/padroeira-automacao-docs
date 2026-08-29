# Análise de Código e Plano de Refatoração - Ecossistema Padroeira

> Documento gerado a partir da inspeção completa dos fontes em `automacao_padroeira/aut-v1/`.
> Nenhuma alteração de código foi realizada; apenas registro de achados e plano.

## 1. Erros e Inconsistências Identificadas

### Críticos (P1)
1. **Credenciais expostas no código** (`pdv_saurus_extractor.py`)
   - `DEFAULT_USER = "Sandra"` e `DEFAULT_PASS = "270471"` estão hardcoded no nível de módulo.
   - Se o `.env` falhar, o sistema usa silenciosamente essas credenciais reais.

2. **Regex trunca valores decimais brasileiros** (`cortex_padroeira_async.py`)
   - Em `_parsear_fechamento`: padrões `r"DINHEIRO(?:\s+\(\d+\))?\s*:\s*([\d.]+)"` (igual para CRÉDITO/DÉBITO)
     usam classe `[\d.]+` (sem vírgula). Relatórios Saurus com `595,76` são capturados apenas como `595`.
   - Apenas `TOTAL` usa `[\d.,]+`. Inconsistência corrompe dados financeiros injetados.

3. **Mapeamento de linhas divergente entre Engine e Motor** (Risco de falsa reconciliação)
   - `engine_consolidacao_async.py` (ETAPA 2.6) lê `ws_me.cell(row=24, column=col).value` como
     "Total do Cx2" (`caixa_total`).
   - `motor_balancete_async.py` define em `MAPA_DIARIO_PAD`: `'K': 24  # Tickets (Linha de Total dos tickets)`
     e `'Q': 37  # Mov/Dia (Real)`. Ou seja, o Motor entende linha 24 como Tickets, não Total.
   - Causa possível leitura errada na comparação de divergência de caixa.

### Médios (P2)
4. **Recuperação de sessão não refaz data falha** (`extrator_saurus_sessao.py`)
   - No `except` do loop de extração, se a reconexão Playwright for bem-sucedida, não há `continue`
     para reprocessar a data atual; ela é pulada e contabilizada como falha.

5. **Constante de data mínima duplicada**
   - `DATA_MINIMA_PROCESSAMENTO = datetime(2026, 6, 1).date()` existe em `cortex_padroeira_async.py`
     e é importada de `engine_consolidacao_async.py` em `async_reconciliation_v2.py`. Risco de divergência.

6. **Código duplicado de extração Saurus**
   - `pdv_saurus_extractor.extrair_fechamento_saurus` e `extrator_saurus_sessao.extrair_lote_saurus`
     replicam seletores e fluxo de login. O primeiro parece código morto, mas mantém credenciais.

### Menores (P3)
7. **Fallback de import silencioso** (`cortex_padroeira_async.py`)
   - `try: from config_precos import ... except Exception: vkg = 96.90` não loga nada; esconde erros.

8. **Import dentro de função** (`calendario_padroeira.py`)
   - `from openpyxl import load_workbook` dentro de `tem_movimento_cx2` prejudica fail-fast.

9. **Constante não utilizada** (`config_precos.py`)
   - `REFEICAO_KG_GRILL = 144.90` definida mas nunca usada.

10. **Tipagem incompleta**
    - `_iterar_cabecalho(ws, inicio: int = 1)` sem tipo para `ws` e sem retorno; funções async sem anotações.

11. **Fragilidade na limpeza do Motor** (`motor_balancete_async.py`)
    - Passo (d) protege apenas coluna D (4) da âncora; coluna Q (17) é apagada e só reconstruída no passo (f).
      Se passo (f) for pulado, planilha fica sem total.

---

## 2. Plano de Refatoração

### Fase 1 — Correções de Segurança e Integridade (P1)
- [ ] **Segurança**: Remover `DEFAULT_USER`/`DEFAULT_PASS` de `pdv_saurus_extractor.py`; exigir
      `SAURUS_USER`/`SAURUS_PASS` obrigatórios via ambiente/`.env` (erro se ausentes).
- [ ] **Parse correto**: Em `cortex_padroeira_async.py`, alterar regex para `[\d.,]+` e normalizar com
      `.replace(",", ".")` para todas as métricas financeiras (dinheiro, crédito, débito, total).
- [ ] **Mapa único de linhas**: Inspecionar planilha `Movto_diario` real e criar módulo/constante
      compartilhada (ex: `mapa_linhas.py`) com `LINHA_TOTAL=24`, `LINHA_MOV_DIA=37`, etc., usado por
      Engine e Motor para eliminar divergência.

### Fase 2 — Robustez e Manutenção (P2)
- [ ] **Retry de sessão**: Em `extrator_saurus_sessao.py`, após bloco de reconexão bem-sucedida,
      adicionar `continue` para reprocessar a data que falhou no mesmo loop.
- [ ] **Constante centralizada**: Mover `DATA_MINIMA_PROCESSAMENTO` para `calendario_padroeira.py`
      e importar em todos os módulos que a usam.
- [ ] **Unificar Playwright**: Criar `extrator_saurus.py` com funções `extrair_unitario` e `extrair_lote`
      reutilizando mesma sessão; remover `pdv_saurus_extractor.py` ou mantê-lo apenas como wrapper.

### Fase 3 — Qualidade de Código (P3)
- [ ] **Logs em fallbacks**: Adicionar `logger.warning` no `except` de import de `config_precos`.
- [ ] **Imports no topo**: Mover `from openpyxl import load_workbook` para topo de `calendario_padroeira.py`.
- [ ] **Limpar constantes**: Remover `REFEICAO_KG_GRILL` ou integrar ao cálculo de `valor_kg_dia`.
- [ ] **Type hints**: Anotar parâmetros e retornos de todas as funções (foco em `_iterar_cabecalho`, async).
- [ ] **Proteção de âncora**: Em `motor_balancete_async.py`, preservar também coluna Q da linha de totais
      durante a limpeza, reconstruindo-a sempre em seguida.

### Fase 4 — Testes e Validação
- [ ] Teste unitário para `_parsear_fechamento` com texto contendo `DINHEIRO (14): 595,76` e verificar
      que `dinheiro == "595.76"`.
- [ ] Teste de integração com planilha `Movto_diario` sintética validando que Engine e Motor concordam
      no número da linha de Total.
- [ ] Teste de extração em lote simulando queda de sessão para confirmar retry da data.

---
*Prioridade sugerida: Fase 1 imediata (produção), Fase 2 na próxima sprint, Fase 3 contínua.*
