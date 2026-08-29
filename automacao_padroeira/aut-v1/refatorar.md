# Relatório de Análise de Código - Padroeira Aut-v1

## Arquivos Analisados
- automacao_padroeira/aut-v1/extrator_saurus_sessao.py
- automacao_padroeira/aut-v1/pdv_saurus_extractor.py
- automacao_padroeira/aut-v1/cortex_padroeira_async.py
- automacao_padroeira/aut-v1/bot_reconciliation.py
- automacao_padroeira/aut-v1/async_reconciliation_v2.py
- automacao_padroeira/aut-v1/engine_consolidacao_async.py

## Erros e Pontos de Melhoria (sem alterações de código)

### 1. pdv_saurus_extractor.py
- **Leitura de caminho do Chromium incompleta**: A função `_resolver_executable_path` tenta ler `cfg.get("chromium_path")` retornado por `_carregar_controle_amb()`, porém essa função só carrega `url`, `user` e `pass` do `.env`. Assim, o caminho definido como `PLAYWRIGHT_CHROMIUM_PATH` no `.env` nunca é lido (apenas via env var do sistema). Código morto / comportamento inesperado.

### 2. cortex_padroeira_async.py
- **Nome de arquivo legado com duplo underscore**: `extrair_dados_saurus()` chama `extrair_dados_saurus_por_data("_legado_")`, gerando busca por `fechamento_caixa__legado_.txt` (dois underscores). O arquivo nunca existe e cai no fallback `fechamento_caixa.txt`. Funciona, mas é confuso e sujeito a erro de manutenção.
- **Inconsistência em regex de valores**: `total` usa `([\d.,]+)` e faz `.replace(",", ".")`. Se o relatório usar vírgula decimal (ex: `1.234,56`), vira `1.234.56` e quebra conversão `float` em `_fmt_num` (retorna 0.0). Já `dinheiro/credito/debito` usam `[\d.]+` (sem vírgula). Risco de parsing incorreto.
- **Instância de `bot` Telebot no nível de módulo**: O módulo cria `bot = telebot.TeleBot(...)` e registra handlers `/fechar` e `/ok`. Quando importado por `bot_reconciliation`, esse bot não é o que faz polling (outro é criado), tornando esses handlers "mortos" e duplicando objetos bot com mesmo token.
- **Tratamento de exceção em `_parsear_fechamento`**: Import de `REFEICAO_COM_SOBREMESA` dentro de try/except cria variável local em caso de falha; funciona, mas frágil se o módulo `config_precos` mudar.

### 3. extrator_saurus_sessao.py
- **Fragilidade no tratamento de reconexão**: No `except` de perda de sessão, após tentar reconectar, `iframe` é reatribuído sem checagem de `None`. O `break` salva de crash, mas a lógica não é robusta.
- **Fechamento de recursos**: `browser` e `context` são fechados apenas no final do `try`. Em exceção antes disso, o `async with async_playwright()` deve limpar, mas não há `try/finally` explícito para `browser.close()`.
- **Uso de `content_frame` como propriedade**: Em versões antigas do Playwright era método. Se o ambiente tiver versão incompatível, pode levantar AttributeError.

### 4. bot_reconciliation.py
- **Comando `/fechar` com argumentos desvia para reconciliação**: O handler `cmd_finalizar` captura `/fechar` mas se houver dígitos (ex: `/fechar 2608`), a condição `not re.search(r"\b\d{4}\b", texto)` falha e ele executa o fluxo de `/finalizar` (reconciliação). O help indica que `/fechar` é apenas para o dia corrente.
- **Dois bots Telebot**: Cria seu próprio `bot` e importa `cortex_padroeira_async` que também cria outro. Dois objetos com mesmo token; o segundo não polla, mas é desperdício e confunde.
- **`asyncio.run` dentro de handler síncrono**: `cmd_finalizar` e `cmd_amostra` chamam `asyncio.run(...)`. Em ambiente com loop já ativo (ex: testes async), pode gerar `RuntimeError: loop already running`.
- **`_limpar_processos_orfaos` agressivo**: Mata processos cujo args contenha "node" e "playwright". Em servidor compartilhado, pode matar outras automações legítimas de Playwright.

### 5. async_reconciliation_v2.py
- **Dependência de filtragem no Engine**: `execute_engine_consolidacao` passa `dados_cortex` (todas as datas de todos AAMMs) ao Engine. Assume que o Engine filtra por `aamm`. Se não filtrar, injetará dados de meses errados no Diário. (Confirmado em `engine_consolidacao_async.py` que o filtro é feito via `datas_no_mensal` restrito a `mes_alvo`/`ano_alvo`, ok, mas a passagem de dicionário global é ineficiente).
- **Parada de leitura de cabeçalho**: `detectar_aamms` usa `_iterar_cabecalho(ws, inicio=1)` que para após 2 colunas vazias. Se houver lacunas no meio do cabeçalho do `Movto_cx2.xlsx`, períodos podem ser ignorados.

### 6. engine_consolidacao_async.py
- **Discrepância na linha de total de caixa para divergência**: `LINHA_TOTAL_CAIXA = 37` é usada para ler `valor_caixa` e comparar com `valor_computado` (total Saurus). Porém, o comentário no topo diz que linha 37 é "slips + dinheiro" (somente dinheiro), enquanto o total de caixa calculado está na linha 40 (`=col37-col38`). O total do Saurus inclui crédito/débito, logo comparar linha 37 com total Saurus gerará divergências falsas e permanentes (regra dos R$30 sempre dispara). Deveria comparar com a soma de todas as formas de pagamento ou com a linha que represente o total do fechamento.
- **Bug na detecção de `proxima_coluna_livre`**: No loop em ETAPA 1.1, a variável `proxima_coluna_livre` só é atualizada quando encontra uma célula vazia e `proxima_coluna_livre == 2`. Como ela não é alterada para um valor diferente de 2 após a primeira atualização, se a coluna 2 estiver vazia e depois aparecerem colunas preenchidas e novamente vazias, o valor final será a *última* coluna vazia, não a primeira. Isso causa lacunas na matriz e desalinhamento com o `Movto_cx2.xlsx`.
- **Dupla inserção em `alvos_verificacao`**: Os mesmos dias são adicionados a `alvos_verificacao` tanto no loop de injeção (ETAPA 2) quanto na ETAPA 2.5 (idempotente). Isso faz com que a verificação pós-escrita (`_verificar_pos_escrita`) rode duas vezes para as mesmas células, redundante e pode mascarar falhas.
- **Fórmulas não recalculadas pelo openpyxl**: `wb_me` é salvo com `data_only=False` (preserva fórmulas), mas o openpyxl não recalcula fórmulas. Na próxima execução, `wb_me_lei` com `data_only=True` lerá o valor em cache do XLSX; se o arquivo nunca foi aberto no Excel, virá `None`. Isso afeta a verificação de `v_total` (linha 24) e a leitura de `valor_caixa` (linha 37/40) para divergência, podendo fazer o motor re-injetar dados desnecessariamente.
- **Cópia de linhas do Cx2 para Diário sem validar tipo**: No loop `for linha in range(6, ws_cx.max_row + 1)`, valores são copiados de `ws_cx` (carregado com `data_only=True`) para `ws_me`. Se `ws_cx.max_row` for grande, copia linhas vazias além do necessário, mas não quebra.

### 7. Observações Transversais
- **Condição de corrida potencial**: `/fechar` (escreve cache) e `/finalizar` (lê/processa cache) podem rodar concorrentemente se usuário enviar comandos rápidos, pois o bot é single-threaded mas o Playwright é async. Risco de ler arquivo parcial.
- **Redundância de `BASE_DIR`**: `bot_reconciliation` força `BASE_DIR` nos módulos importados, mas eles já calculam corretamente. Se a estrutura de pastas mudar, pode mascarar erros.
- **Tratamento de `None` em `registrar_divergencia`**: O retorno da função é usado para contar divergências, mas o módulo `backup_padroeira` não foi inspecionado; assumir que retorna string de categoria é arriscado se retornar `None`.

## Conclusão
Nenhum erro crítico que impeça execução no ambiente descrito foi encontrado, mas há vários pontos de fragilidade (leitura de `.env`, duplicação de bots, parsing de números, fechamento de browser, lógica de divergência de caixa e detecção de colunas livres) que devem ser refatorados para maior robustez. O bug de comparação de linha 37 (dinheiro) com total Saurus (todas formas de pagamento) é o mais sério, pois invalida o alerta de divergência.
