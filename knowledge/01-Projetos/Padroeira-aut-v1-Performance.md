---
created: 2026-08-29
updated: 2026-08-29
project: aut-v1
tags: [padroeira, reconciliacao_fiscal, aut-v1, performance, asyncio, openpyxl, cache, python]
tipo: nota-tecnica
---

# Otimização de Performance — aut-v1 (Itens 1 e 2 do refatorar.md)

**Data:** 2026-08-29 · **Commit:** `09199dd` (push origin/main) · **Agente:** [[Claude]]

Baseado nos Itens 1 e 2 do `refatorar.md`. Objetivo: manter a escuta do
Telegram 100% responsiva e eliminar reaberturas repetidas do `Movto_cx2.xlsx`.

## Item 1 — Evitar bloqueio do event loop em I/O

Métodos síncronos do openpyxl / Playwright envolvidos em `asyncio.to_thread(...)`
nos orquestradores:

- **async_reconciliation_v2.py** (`AsyncReconciliationEngine`):
  - `detectar_aamms` (varre ~16k colunas do cabeçalho do Movto_cx2)
  - `verificar_paridade_planilhas` e `_datas_sem_metricas_saurus` (por período, abrem Diário + Caixa2)
  - `extrair_todos_pendentes` (Playwright + disco)
  - `executar_motor_unificado` (Engine) e `injetar_balancete` (Motor Balancete)
- **bot_reconciliation.py** (`_fechar_dia`): `extrair_dados_saurus_por_data` (I/O de disco do .txt).

Handlers síncronos (`cmd_finalizar`, `cmd_amostra`) **mantiveram** sem `await`:
`_limpar_processos_orfaos` e `_salvar_historico_faturamento` — eles rodam dentro
do `_run_async` (thread dedicada com novo event loop, correção P3 4c anterior),
então já estão fora do loop do Telegram.

## Item 2 — Cache da leitura do Movto_cx2.xlsx

`tem_movimento_cx2` (calendario_padroeira.py) refatorado:

- Aceita `workbook=` (injeção de objeto já carregado — evita reabrir o disco).
- Usa `functools.lru_cache` do **cabeçalho de datas** (linha 1), keyed por
  `(caminho, mtime)` → invalida quando o arquivo muda no disco.
- ANTES: cada dia validado do mês reabria o `.xlsx` (dezenas de `load_workbook`).
- AGORA: a linha 1 é lida uma única vez por arquivo/mtime.

**Bugs corrigidos no refactoring:**
1. O openpyxl devolve `datetime.datetime` (não `date`) → normalizado para `.date()`
   no cache, senão a busca `date(ano,mes,dia) in conjunto` nunca batia.
2. `date(ano, mes, dia)` estoura em dia impossível (ex.: 30/02) → protegido com
   `try/except ValueError` retornando `False`.

Assinatura retrocompatível: `(base_dir, aamm, dia, *, workbook=None)` — chamadas
posicionais legadas (ex.: motor_balancete_async.py:255) continuam válidas.

## Verificação

- `python3 -m py_compile *.py` → limpo.
- `auditar_kg_equivalente.py` → Refeição 89.25 kg [OK], Sobremesa 10.54 kg [OK], exit 0.
- Testes de sandbox do Item 2: LRU hit (`cache_info` hits=1), injeção de workbook,
  datas inexistentes (30/02 → False), chamada legada posicional → todos OK.
- Arquivos .xlsx de produção **intocados** (exemplos em /tmp e symlink de fechamento).

## Regras do CLAUDE.md preservadas

Nenhuma alteração em fórmulas: Linhas 14/40 do Diário como fórmulas literais,
Coluna Q do Balancete = `SUM(B:P)`, Sangria na Linha 42 espelhada no Balancete.

---
Relacionado: [[Padroeira-aut-v1]]
