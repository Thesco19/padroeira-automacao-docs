---
created: 2026-07-25
updated: 2026-08-18
project: aut-v1
tags: [padroeira, reconciliacao_fiscal, aut-v1, excel, python]
tipo: projeto-especificacao
---

# Projeto: Automação Padroeira (`aut-v1` / `reconciliacao_fiscal_v2`)

**Projeto:** `reconciliacao_fiscal_v2` / `Automação Padroeira (aut-v1)`  
**Status:** Correções 1-3 APLICADAS no código real e validadas em sandbox  
**Responsável Técnico:** [[Kilo]] / [[OpenCode]] / [[Claude]]  

---

## 1. Visão Geral

O projeto **Automação Padroeira (`aut-v1`)** é responsável pelo pipeline de reconciliação fiscal e automação das planilhas de movimento diário (`Movto diario Pad` / `Movto_cx2.xlsx`). Ele processa os fechamentos de caixa do sistema Saurus, injeta linhas de controle (linhas 3, 4 e 5), organiza colunas financeiras e gera o balancete mensal.

---

## 2. Regras de Negócio e Calendário (`fcd26ad3_v2`)

1. **Dias Fechados (Domingos e Feriados):**
   - O restaurante **NÃO abre aos domingos nem feriados**.
   - **Critério Simplificado:** Ausência de registro no caixa Saurus. Se não houver fechamento no Saurus para determinada data, o dia é considerado fechado.
   - O pipeline lê a data/status do caixa Saurus. Quando o dia é considerado fechado, não há registros de faturamento e as colunas permanecem zeradas.

2. **Fonte Única de Verdade do Faturamento:**
   - `Movto_cx2.xlsx` é a fonte única confiável para alinhamento linha a linha do faturamento.

3. **Automação Saurus vs Cache Local:**
   - Em caso de fechamento Saurus faltante, o sistema utiliza o cache local como fallback de preflight, podendo invocar o portal via [[Playwright]] quando necessário.

---

## 3. Diagnóstico de Bugs Encontrados (`aut-v1`)

Durante a execução inicial, foram identificadas três anomalias críticas no processamento das planilhas:
- **Sintoma 1:** Linhas 3, 4 e 5 ficando vazias quando o cache de fechamentos falhava no preflight.
- **Sintoma 2:** Limpeza de colunas do diário apagando acidentalmente o cabeçalho (linha 1).
- **Sintoma 3:** Linhas-fantasma (linhas 29 e 30) em meses de 31 dias e desordem no balancete por desalinhamento do layout do Pad (layout original fixo até linha 30 vs expansão para 31 dias).

---

## 4. Plano de Correção e Implementação (Correções 1 a 3)

### Correção 1: Cache de Fechamentos no Preflight
- **Injeção Idempotente:** Garante a leitura e injeção do cache de fechamentos sempre na etapa de preflight, preenchendo as linhas 3, 4 e 5 de forma idempotente antes do cálculo das colunas.

### Correção 2: Preservação de Cabeçalho na Limpeza
- Ajuste na rotina de limpeza de colunas do diário para iniciar estritamente a partir da linha 2, preservando a linha 1 (cabeçalho) intacta.

### Correção 3: Tratamento Dinâmico de Meses de 31 Dias e Totais
- **Layout de 31 dias:** Inserção dinâmica de linhas quando o mês possui 31 dias, corrigindo a ramificação `insert_rows`.
- **Fórmulas de Totais Dinâmicas:** A linha de totais do Pad passou a utilizar somas dinâmicas (`SUM(B2:B32)`) em TODAS as colunas financeiras (B até P), evitando totais estáticos ou desatualizados.

---

## 5. Validação e Testes Passados

- **Status da Validação:** 4 cenários de teste **PASS** aplicados diretamente nos Pads originais afetados por bugs.
- **Estratégia de Reparo:** Reparo executado in-place preservando os dados históricos e reexecutando o pipeline de forma determinística.

---

## Documentos & Links Relacionados

- [[Agentes-do-Laboratorio]]
- [[LAB-Resumo]]
- [[Supabase]]
