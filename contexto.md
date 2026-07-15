# CONTEXTO: Automação Ecossistema Padroeira

## Objetivo Principal
Automatizar a consolidação do faturamento do Restaurante Padroeira através de um pipeline Python que sincroniza dados brutos do Caixa 2 para o Diário Mensal e transpõe os totais consolidados para o Balancete Geral, preservando a integridade das fórmulas nativas.

## Estado Atual
* **Higienização de Base Concluída:** Dados históricos (2015-2025) removidos do Caixa 2, reduzindo a complexidade da matriz.
* **Fase 1.1 (Expansão Horizontal) [CONCLUÍDA]:** O script mapeia datas pendentes no Caixa 2 e cria dinamicamente novas colunas no Diário Mensal.
* **Fase 1.2 (Sincronia Vertical Espelhada) [CONCLUÍDA]:** Cópia de dados linha a linha (a partir da Linha 6), com injeção automática de fórmulas estruturais no LibreOffice nas linhas 14 e 40.
* **Fase 2 (Transposição Balancete) [EM DESENVOLVIMENTO]:** Motor de sobreposição agressiva construído para inverter a matriz (Dias em colunas para Dias em linhas).

## Arquivos Críticos
* `/home/teco/Nuvens/Box/Padroeira/Padroeira vendas/Movto_cx2.xlsx`: Base de origem primária (Lançamentos manuais, higienizado a partir de 2026).
* `/home/teco/Nuvens/Box/Padroeira/Restaurante/A2026/Movto_diario.AAMM.xlsx`: Diário consolidado (Matriz: Dias = Colunas / Categorias = Linhas).
* `/home/teco/Nuvens/Box/Padroeira/Restaurante/A2026/PadAAMM.xlsx`: Balancete Geral (Matriz invertida: Dias = Linhas / Categorias = Colunas).
* `/home/teco/Nuvens/Box/work_out/lab/automacao_padroeira/engine_consolidacao.py`: Motor da Fase 1 (Expansão e Espelhamento Vertical).
* `/home/teco/Nuvens/Box/work_out/lab/automacao_padroeira/motor_balancete.py`: Motor da Fase 2 (Transposição Diário ➔ Balancete).

## Gargalos/Pendências
1. **Bloqueio Atual:** O script `motor_balancete.py` reportou `PathNotFound` ao tentar carregar os arquivos da Fase 2. Necessário rodar `ls -la` no diretório alvo e depurar o nome exato do arquivo `Pad2606.xlsx` vs `Movto_diario.2606.xlsx`.
2. **Fase 3 (Backlog):** Automação de virada de mês (Cópia de template de planilhas vazias para o novo mês).
3. **Fase 4 (Backlog):** Automação de virada de ano (Criação de nova estrutura de pastas).

## Configurações/Variáveis
* **Caminho Raiz:** `/home/teco/Nuvens/Box/Padroeira`
* **Mês Lógico de Homologação:** `AAMM = "2606"`
* **Diretriz de Execução (Fase 2):** Sobreposição Agressiva (Tratoramento de dados da coluna para garantir a verdade absoluta do dia).
* **Parâmetros de Exceção (Fase 1):** * `Linha 14`: Recebe a fórmula `=SUM({coluna}10:{coluna}13)`
  * `Linha 40`: Recebe a fórmula `={coluna}37-{coluna}38`
* **Dicionário de Transposição (Fase 2 - MAPA_DIARIO_PAD):**
  * Coluna Destino Balancete : Linha Origem Diário (Ex: 'B': 3, 'E': 6, 'F': 10, 'K': 24, 'Q': 37).
