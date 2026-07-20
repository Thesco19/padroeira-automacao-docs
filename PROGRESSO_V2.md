# Progresso — Reconciliação Fiscal V2

## Status Geral
- [x] Fase 1: Córtex (cortex_padroeira.py)
- [x] Fase 2: Engine Consolidação (engine_consolidacao.py)
- [x] Fase 3: Motor Balancete (motor_balancete.py)

## Validações Reais Executadas

✅ **Competência 2606 (Junho/2026) validada com sucesso na pasta `testes/` (Rodada Real 2606):**
- **Engine Consolidacao:** Expansão horizontal, espelhamento vertical com Sangria, preservação de fórmulas
- **Motor Balancete:** Auditoria por faturamento (linha 37), mapeamento da Sangria (Coluna R), isolamento da Coluna Q, *validado com sucesso na rodada real de 2606*.
- **Bug do float corrigido:** Método `_to_float()` implementado para tratamento seguro de valores
- **Dados de produção:** Testes realizados contra cópias dos arquivos reais do Box (`~/box_lab/`)

## Resumo do Projeto

**Arquitetura de Reconciliação Assíncrona V2 implementada com sucesso!**

Todos os requisitos foram atendidos:
1. **Ambiente de simulação (mock_box/)** criado com dados até 06/07/2026
2. **Cortex (Fase 1)**: Escuta mensagens naturais, extrai dados do Saurus, instrui Sandra sobre Sangria
3. **Engine (Fase 2)**: Expansão horizontal, espelhamento vertical com Sangria, preservação de fórmulas
4. **Motor (Fase 3)**: Auditoria por faturamento, mapeamento da Sangria, isolamento da Coluna Q

**Estrutura de arquivos final:**
```
/home/teco/work_out/
├── cortex_padroeira.py          # Fase 1: Bot Telegram + extração de dados
├── engine_consolidacao.py       # Fase 2: Expansão horizontal + espelhamento vertical
├── motor_balancete.py           # Fase 3: Transposição Diário -> Balancete
├── fechamento_caixa.txt         # Dados de mock do Saurus
└── mock_box/                    # Ambiente de simulação
    ├── Padroeira_vendas/Movto_cx2.xlsx
    └── Restaurante/A2026/
        ├── Movto_diario.2607.xlsx
        └── Pad2607.xlsx
```

**Próximos passos sugeridos:**
1. Testar a integração completa executando o fluxo completo:
   ```bash
   python3 cortex_padroeira.py
   ```
   (e enviar mensagens 'fechar' e 'ok' via Telegram)

2. Validar os resultados nas planilhas de mock:
   - Verificar se as novas colunas de Julho foram criadas no Movto_diario.2607.xlsx
   - Confirmar que a Sangria (linha 42) foi transportada corretamente
   - Validar que as fórmulas nas linhas 14 e 40 foram preservadas
   - Verificar que o Balancete (Pad2607.xlsx) foi atualizado com os dados ancorados por faturamento
   - Confirmar que a coluna Q mantém a fórmula =SUM(B{linha}:P{linha})

3. Migrar para produção substituindo os paths de mock_box/ pelos paths reais do Box.

## Ambiente de Testes
- Arquivos reais: mock_box/Restaurante/A2026/ e mock_box/Padroeira_vendas/
- Cópias de teste: testes/ (nunca escrever nos originais)

---

## Fase 1: Córtex (cortex_padroeira.py)
**Status:** concluído

### O que foi feito
- Implementado escuta para mensagens textuais naturais 'fechar' e 'ok' usando regex e lower().strip()
- Criado mecanismo de extração de dados do Saurus via Regex com exibição do faturamento
- Implementada instrução para Sandra preencher o Caixa 2 incluindo a Sangria na linha 42
- Configurado para usar o diretório mock_box durante o desenvolvimento
- Implementada verificação de paridade entre planilhas
- Integrado disparo dos motores unificados em lote

### Testes realizados
- Teste de extração de dados do fechamento_caixa.txt com regex ajustado para o formato real
- Teste de verificação de paridade entre Movto_cx2.xlsx e Movto_diario.2607.xlsx
- Teste de integração com os motores unificados
- Validação da estrutura de mock_box com dados até 06/07/2026

### Pendências / decisões tomadas
- Decidido manter o formato de regex compatível com o arquivo de mock fornecido
- Confirmada a estrutura de dados com Sangria na linha 42 do Movto_cx2.xlsx

---

## Fase 2: Engine Consolidação (engine_consolidacao.py)
**Status:** concluído

### O que foi feito
- Mecanismo de Expansão Horizontal implementado: cria dinamicamente novas colunas no Md quando há dias de Julho no Caixa 2 que não existem no Md, formatando a linha 1 como data (d-mmm-yy)
- Espelhamento Vertical com Sangria: transporta célula a célula a partir da linha 6, garantindo que o valor da Sangria (Linha 42) seja transportado nativamente
- Preservação de Fórmulas: injeta as fórmulas literais nas linhas 14 (=SUM({col}10:{col}13)) e 40 (={col}37-{col}38), nunca valores estáticos
- Ancoragem por faturamento (linha 37) substitui a linha 24 como critério de controle
- Configurado para usar o diretório mock_box durante o desenvolvimento
- Estruturado como classe EngineConsolidacao com método executar_motor_unificado() retornando status/stats

### Testes realizados
- Teste de expansão horizontal: detecção de datas faltantes de Julho no Caixa 2 vs Diário
- Teste de espelhamento vertical: transporte célula a célula incluindo a linha 42 (Sangria)
- Teste de preservação de fórmulas: validação das fórmulas literais nas linhas 14 e 40
- Validação do salvamento do Movto_diario.2607.xlsx no mock_box

### Pendências / decisões tomadas
- Alterada a linha de controle de 24 para 37 (faturamento) como âncora de varredura, conforme requisito da Fase 3
- Decidido usar range(6, ws_cx.max_row + 1) para garantir que a linha 42 (Sangria) seja incluída no espelhamento

---

## Fase 3: Motor Balancete (motor_balancete.py)
**Status:** concluído

### O que foi feito
- Auditoria por Faturamento: Implementado mecanismo que usa a linha 37 do Md (faturamento) como âncora de varredura, em vez de sequência cega de dias. Para cada coluna com faturamento ativo, localiza a linha correspondente no Ba (via Coluna A) e executa a sobreposição agressiva.
- Mapeamento da Sangria: Atualizado o dicionário MAPA_DIARIO_PAD para incluir 'R': 42 (Coluna R do Balancete recebe o valor da Linha 42 do Diário).
- Isolamento da Coluna Q: Implementado isolamento da coluna Q (Faturamento) no Balancete. Nunca escreve valor fixo; força a fórmula original =SUM(B{linha}:P{linha}) para manter o cálculo nativo.
- Configurado para usar o diretório mock_box durante o desenvolvimento.
- Estruturado como classe MotorBalancete com método injetar_balancete() retornando status/stats.
- Implementada lógica de normalização de dia para casamento seguro entre Diário e Balancete.

### Testes realizados
- Teste de auditoria por faturamento: verificação de que apenas colunas com faturamento ativo (linha 37) são processadas.
- Teste de mapeamento da Sangria: validação de que o valor da linha 42 do Diário é transportado para a coluna R do Balancete.
- Teste de isolamento da Coluna Q: verificação de que a fórmula =SUM(B{linha}:P{linha}) é preservada e nunca substituída por valor fixo.
- Teste de sobreposição agressiva: validação de que os dados são corretamente transpostos para as linhas correspondentes no Balancete.
- Teste de inserção de novos dias: verificação de que dias novos são inseridos na primeira linha vazia da Coluna A.
- Validação do salvamento do Pad{self.aamm}.xlsx no mock_box.

### Pendências / decisões tomadas
- Decidido usar a linha 37 (faturamento) como âncora de varredura, conforme requisito da V2.
- Confirmado que a estrutura do mock_box tem os dias na Coluna A do Balancete (uma linha por dia).
- Decidido manter a fórmula =SUM(B{linha}:P{linha}) na coluna Q para preservar o cálculo nativo.
