# Projeto: Reconciliação Fiscal V2 (Padroeira / Restaurante)

## 🧠 REGRA DE OURO: MEMÓRIA COMPARTILHADA (MCP)
**ESTE PROJETO É OPERADO POR MÚLTIPLOS AGENTES (Claude, Gemini, OpenCode, JCode, Kilo).**
- **Obrigatório:** Antes de qualquer ação, leia `MCP_SHARED_MEMORY_GUIDE.md` e execute `memoria_listar` via MCP server.
- **Persistência:** Toda decisão técnica ou mudança de status deve ser salva via `memoria_salvar` ou `rag_indexar`.
- **Contexto:** Use a pasta `.mcp_context/` para manter a coerência entre as sessões de diferentes agentes.

## Regras invioláveis
- NUNCA escrever nos arquivos de produção do Box (montado em ~/box_lab).
- Testes e desenvolvimento sempre em testes/ ou mock_box/, nunca nos originais.
- Linhas 14 e 40 do Md: nunca valor estático, sempre as fórmulas literais
  (linha 14: =SUM({col}10:{col}13), linha 40: ={col}37-{col}38)
- Coluna Q do Balancete: nunca valor fixo, sempre =SUM(B{linha}:P{linha})

## Estrutura de dados
- Sangria: linha 42, coluna A no Movto_cx2 / Md
- MAPA_DIARIO_PAD: dicionário de mapeamento coluna Balancete -> linha Diário
  - Inclui 'R': 42 (Sangria)
- Faturamento: linha 37 do Md, usado como âncora de varredura (não sequência cega de dias)

## Arquivos principais
- cortex_padroeira.py — bot Telegram, escuta "fechar"/"ok" em texto natural
- engine_consolidacao.py — Fase 1: expansão horizontal + espelhamento vertical
- motor_balancete.py — Fase 2: auditoria por faturamento + sangria + coluna Q

## Ambiente
- Arquivos reais em mock_box/Restaurante/A2026/ e mock_box/Padroeira_vendas/
- Box montado via rclone em ~/box_lab (não sobrevive a reboot — remontar com
  rclone mount box_remoto: ~/box_lab --daemon --vfs-cache-mode writes)
