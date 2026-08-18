# Plano de Implementação — ObSV v2

**Status:** Documento Oficial de Arquitetura e Planejamento  
**Projeto:** ObSV (Vault Obsidian Headless)  
**Contrato Base:** `docs/SPEC.md`

---

## 1. Princípios Invioláveis da Arquitetura

1. **`SPEC.md` é o Contrato**: Nenhuma funcionalidade fora da especificação será adicionada.
2. **`Vault` é a Única Fonte de Verdade**: Todo dado primário reside no sistema de arquivos do vault. Se o SQLite for corrompido ou apagado, o vault permanece 100% intacto e o índice pode ser integralmente reconstruído.
3. **SQLite é Projeção Derivada**: O banco SQLite funciona estritamente como um índice de consulta e busca. Nenhuma mutação no vault é feita através de queries SQL.
4. **Interface Oficial REST v2**: O contrato público canônico da versão 2 é exposto via HTTP/HTTPS sob a raiz `/api/v1`.
5. **Segurança de Rede sem Autenticação Própria**: O ObSV v2 não possui autenticação interna por tokens nem gerenciamento de usuários. A segurança do servidor é provida exclusivamente pela infraestrutura de rede: **HTTPS, Tailnet, ACLs do Tailscale, flag `tailscale_only` e Firewall**.
6. **Biblioteca Padrão do Python (stdlib)**: É proibido introduzir qualquer dependência externa (`pip`). Todo o código de produção utiliza apenas os módulos nativos do Python (>= 3.11).
7. **Framework Oficial de Testes é `unittest`**: Todos os testes automatizados utilizam estritamente o módulo `unittest` da biblioteca padrão. O uso de `pytest` ou outros runners terceiros é proibido no ambiente oficial.
8. **Diagnóstico Inofensivo (`doctor`)**: O comando `doctor` executa apenas leituras e inspeções ambientais. É proibido gerar efeitos colaterais no disco (como criar diretórios `mkdir`) durante o diagnóstico.
9. **Fechamento Obrigatório de Toda Milestone**: Cada milestone deve obrigatoriamente finalizar com a validação completa de quatro pilares:
   - **`unittest`**: Suíte de testes unitários e de integração 100% verde.
   - **`doctor`**: Diagnóstico `obsv doctor` executado sem erros nem alterações no disco.
   - **`verify`**: Execução do comando de verificação `obsv verify`.
   - **`benchmark`**: Medição objetiva e registro de desempenho da funcionalidade entregue na milestone.
10. **Adaptador MCP Diferido**: O protocolo MCP não faz parte do núcleo da v2 e fica reservado para uma milestone futura independente (M14), como consumidor da API REST `/api/v1`.

---

## 2. Ordem de Implementação e Dependências

```text
M01 (Contratos e ADRs)
 └──> M02 (Configuração XDG e Doctor Inofensivo)
       └──> M03 (Fronteira Segura do Vault / Filesystem)
             └──> M03A (Testes de Concorrência, Locking e Integridade)
                   ├──> M04 (Concorrência de Diretórios e Mutações Condicionais)
                   └──> M05 (Base SQLite e Migrações)
                         └──> M06 (Parser Semântico Mínimo)
                               └──> M07 (Indexação, Busca e Reconciliação)
                                     └──> M08 (Interface CLI v2 Local)
                                           └──> M09 (API REST v1 Leitura - Segurança por Perímetro)
                                                 ├──> M10 (API REST v1 Escrita)
                                                 ├──> M11 (Web UI Leitura sem JS)
                                                 │     └──> M12 (Edição Web & Uploads)
                                                 │           └──> M13 (Operação, Resiliência e Release v2)
                                                 └──> M14 (Adaptador MCP Diferido)
```

### Tabela Sintética de Precedência

| Milestone | Título | Dependências Diretas |
| :--- | :--- | :--- |
| **M01** | Decisões de Arquitetura e Contratos Bloqueantes | Nenhum |
| **M02** | Configuração Centralizada XDG e Diagnóstico Inofensivo | M01 |
| **M03** | Fronteira Segura do Vault (Filesystem Confinado) | M01 |
| **M03A** | Testes de Concorrência, Locking e Integridade | M03 |
| **M04** | Mutações Condicionais e Concorrência de Diretórios | M03A, M02 |
| **M05** | Base SQLite, Schema Versionado e Migrações | M02 |
| **M06** | Parser Semântico Mínimo (Markdown, Canvas, Text) | M05 |
| **M07** | Indexação, Busca e Reconciliação Derivada | M04, M05, M06 |
| **M08** | Interface CLI v2 Local | M02, M03, M07 |
| **M09** | API REST v1 de Leitura (Segurança Exclusiva por Perímetro de Rede) | M01, M04, M07, M08 |
| **M10** | API REST v1 de Escrita e Mutações Remotas Condicionais | M09 |
| **M11** | Web UI de Leitura sem JavaScript Obrigatório | M09 |
| **M12** | Edição Web, Upload e Servimento Raw Endurecido | M09, M10, M11 |
| **M13** | Operação, Resiliência e Release v2 Final | M12 |
| **M14** | Adaptador MCP (Diferido / Pós-v2) | M09 (e M10 para escrita) |

---

## 3. Detalhamento das Milestones

---

### M01 — Decisões de Arquitetura e Contratos Bloqueantes

* **Objetivo**: Congelar decisões formais de segurança de rede, contratos `/api/v1` e envelopes padrão antes de qualquer alteração de código.
* **Escopo**:
  * Registrar ADRs sobre: bind de rede restrito, segurança de perímetro (HTTPS, Tailnet, ACLs Tailscale, `tailscale_only`, firewall — sem autenticação por token própria), rejeição integral de symlinks, escrita atômica com precondição e desativação de efeitos colaterais no `doctor`.
  * Congelar contratos JSON para envelopes de sucesso e erro (`code`, `message`, `details`).
  * Definir política de FTS5 no SQLite e limites operacionais (tamanho máximo de payload/upload/busca).
* **Dependências**: Nenhuma.
* **Critérios Objetivos de Conclusão**:
  * Todos os ADRs revisados e assinados na pasta `docs/`.
  * Nenhuma seção em `SPEC.md` marcada como "a definir".
* **Riscos Técnicos**:
  * Ambiguidades residuais em contratos que obriguem refatorações em milestones avançadas.
* **Estratégia de Teste (`unittest`)**:
  * Teste de validação documental de contratos estruturados em arquivos JSON de schema estático.
* **Procedimento de Rollback**:
  * Reversão documental via controle de versão Git.
* **Fechamento Obrigatório da Milestone**:
  - [ ] **unittest**: `python3 -m unittest discover -s tests -p "test_*.py"` (100% verde)
  - [ ] **doctor**: `obsv doctor` (retorno 0 / sem side-effects no disco)
  - [ ] **verify**: `obsv verify`
  - [ ] **benchmark**: Medição do tempo de validação de schemas de contrato (< 10ms).

---

### M02 — Configuração Centralizada XDG e Diagnóstico Inofensivo

* **Objetivo**: Fornecer resolução estrita de configuração XDG e diagnóstico `doctor` 100% livre de efeitos colaterais.
* **Escopo**:
  * Implementar precedência `--vault` > `OBSV_VAULT` > `OBSIDIAN_VAULT` > `config.json`.
  * Validação estrutural de tipos e limites no carregamento de `Config`.
  * Implementar `doctor` puramente de inspeção: checa versão Python (>= 3.11), existência do vault, permissões de leitura/escrita, disponibilidade do SQLite, suporte a FTS5, validação SSL e porta de rede.
  * **Regra Estrita**: `doctor` **NUNCA** executa `mkdir` ou cria arquivos no disco.
* **Dependências**: M01.
* **Critérios Objetivos de Conclusão**:
  * Configuração inválida interrompe a inicialização com `ConfigError` determinístico.
  * `doctor` retorna código de saída `0` (ok), `1` (warning) ou `2` (error) e formato `--json` estável.
  * Nenhuma operação de escrita em disco é realizada durante `obsv doctor`.
* **Riscos Técnicos**:
  * Falha na detecção de permissões em sistemas de arquivos compartilhados/NFS.
* **Estratégia de Teste (`unittest`)**:
  * `tests/test_config.py`: Testar precedência de variáveis de ambiente usando `unittest.mock.patch.dict(os.environ)`.
  * `tests/test_doctor.py`: Validar que `run_checks()` não altera o estado do disco (comparar lista de arquivos antes e depois da execução).
* **Procedimento de Rollback**:
  * Reverter módulo `obsv/config.py` e utilitários de diagnóstico para a versão anterior.
* **Fechamento Obrigatório da Milestone**:
  - [ ] **unittest**: `python3 -m unittest discover -s tests -p "test_*.py"` (100% verde)
  - [ ] **doctor**: `obsv doctor` (retorno 0 / sem side-effects no disco)
  - [ ] **verify**: `obsv verify`
  - [ ] **benchmark**: Medição do tempo de resolução e validação de configuração (< 15ms).

---

### M03 — Fronteira Segura do Vault (Filesystem Confinado)

* **Objetivo**: Isolar toda operação de arquivos na classe `Vault`, garantindo que nenhuma requisição escape da raiz do vault.
* **Escopo**:
  * Métodos de `Vault`: `listdir`, `walk`, `read`, `write`, `mkdir`, `delete`, `move`, `search`.
  * Rejeição total de path traversal (`..`), caminhos absolutos, diretórios reservados (`.git`, `.obsidian`, `.trash`) e links simbólicos (`is_symlink()`).
  * Gravacao atômica com arquivo temporário no mesmo diretório, `fsync()` e `os.replace()`.
  * Corrigir o tratamento de erro em `write` para garantir inicialização limpa de variáveis e cleanup sem `UnboundLocalError`.
* **Dependências**: M01.
* **Critérios Objetivos de Conclusão**:
  * Tentativas de traversal ou acesso a symlinks disparam `VaultError`.
  * Falha simulada durante escrita deixa o arquivo original intacto sem criar resíduos incompletos.
  * Nenhuma API ou CLI acessa `os` ou `pathlib` diretamente sem passar pela classe `Vault`.
* **Riscos Técnicos**:
  * Condições de corrida TOCTOU no sistema de arquivos durante a verificação de links simbólicos.
* **Estratégia de Teste (`unittest`)**:
  * `tests/test_vault.py`: `unittest.TestCase` criando vaults isolados em `tempfile.TemporaryDirectory`.
  * Testar cenários negativos: injeção de symlinks quebrados/válidos, tentativas de escrita fora do vault e caracteres inválidos.
* **Procedimento de Rollback**:
  * O vault permanece intacto no sistema de arquivos. Reverter código Python para a versão anterior.
* **Fechamento Obrigatório da Milestone**:
  - [ ] **unittest**: `python3 -m unittest discover -s tests -p "test_*.py"` (100% verde)
  - [ ] **doctor**: `obsv doctor` (retorno 0 / sem side-effects no disco)
  - [ ] **verify**: `obsv verify`
  - [ ] **benchmark**: Medição de throughput de leitura/escrita simples em disco (> 500 ops/sec).

---

### M03A — Testes de Concorrência, Locking e Integridade

* **Objetivo**: Validar exaustivamente a camada de concorrência e integridade física de mutação antes do desenvolvimento de indexação ou APIs de rede.
* **Escopo**:
  * Validação estrita de **lock por arquivo** (`fcntl.flock`).
  * Validação de **atomic replace** (garantindo ausência de corrupção ou leitura parcial durante substituições simultâneas).
  * Validação de **escrita concorrente** em alta frequência usando múltiplas threads e subprocessos.
  * Validação de **rollback e resiliência** em quedas simuladas do processo no meio de gravações.
  * Validação da **consistência de projeção pré-índice** (garantia de estado `clean` / `dirty`).
* **Dependências**: M03.
* **Critérios Objetivos de Conclusão**:
  * 100 escritas simultâneas no mesmo arquivo resultam em execução estritamente serializada ou rejeição por conflito de lock sem nenhuma nota corrompida.
  * Teste de concorrência confirma que nenhum leitor obtém um arquivo gravado parcialmente durante o `atomic replace`.
  * Falha forçada com `SIGKILL` deixa o arquivo anterior intacto.
* **Riscos Técnicos**:
  * Bloqueios indeterminados (hangs) se os descritores de arquivo não forem fechados em `finally`.
* **Estratégia de Teste (`unittest`)**:
  * `tests/test_concurrency_core.py`: Suíte intensiva de testes multithread e multiprocesso com `concurrent.futures`.
* **Procedimento de Rollback**:
  * Destruir processos de teste e reverter o módulo de locking/escrita.
* **Fechamento Obrigatório da Milestone**:
  - [ ] **unittest**: `python3 -m unittest discover -s tests -p "test_*.py"` (100% verde)
  - [ ] **doctor**: `obsv doctor` (retorno 0 / sem side-effects no disco)
  - [ ] **verify**: `obsv verify`
  - [ ] **benchmark**: Medição de latência de aquisição de lock e atomic replace (< 5ms por operação).

---

### M04 — Mutações Condicionais e Concorrência de Diretórios

* **Objetivo**: Expandir o controle de concorrência para operações estruturais (`move` e `delete` recursivo) e mutações condicionais.
* **Escopo**:
  * Ordenação canônica de aquisição de locks para operações multi-recursos (`move`, `rm -r`).
  * Controle otimista de concorrência com verificação de versão/mtime antes de sobrescrever ou alterar arquivos.
  * Timeouts configuráveis para aquisição de lock com liberação garantida via `contextmanager`.
* **Dependências**: M03A, M02.
* **Critérios Objetivos de Conclusão**:
  * Operações de `move` e `delete` concorrentes não entram em deadlock.
  * Tentativas de alteração com mtime desatualizado disparam erro de conflito determinístico.
* **Riscos Técnicos**:
  * Deadlocks em renomeações cruzadas de diretórios (`A -> B` e `B -> A` simultâneos).
* **Estratégia de Teste (`unittest`)**:
  * `tests/test_concurrency_tree.py`: Cenários de movimentação e deleção de árvore sob carga estressada.
* **Procedimento de Rollback**:
  * Encerrar processos em execução para liberar locks efêmeros e reverter para M03A.
* **Fechamento Obrigatório da Milestone**:
  - [ ] **unittest**: `python3 -m unittest discover -s tests -p "test_*.py"` (100% verde)
  - [ ] **doctor**: `obsv doctor` (retorno 0 / sem side-effects no disco)
  - [ ] **verify**: `obsv verify`
  - [ ] **benchmark**: Benchmark de operações estruturais sob concorrência (> 200 ops/sec).

---

### M05 — Base SQLite, Schema Versionado e Migrações

* **Objetivo**: Estruturar a projeção SQLite derivada com suporte a migrações idempotentes e detecção de FTS5.
* **Escopo**:
  * Criação do schema versionado: tabelas `schema_info`, `files`, `notes`, `links`, `tags`, `frontmatter`, `fts_notes`.
  * Suporte a migrações incrementais controladas por PRAGMA `user_version`.
  * Detecção de suporte a FTS5 com degradação graciosa para `LIKE` quando indisponível.
  * Transações curtas com modo WAL habilitado (`PRAGMA journal_mode=WAL`).
* **Dependências**: M02.
* **Critérios Objetivos de Conclusão**:
  * O banco de dados pode ser apagado e recriado do zero sem afetar nenhuma nota do vault.
  * Migrações de schema executam de forma idempotente sem corromper dados existentes.
  * SQLite opera isolado no diretório XDG Data.
* **Riscos Técnicos**:
  * Compilações de Python no ambiente alvo sem o módulo SQLite habilitado com FTS5.
* **Estratégia de Teste (`unittest`)**:
  * `tests/test_db.py`: Validação de conexões em banco `:memory:` e em arquivos temporários. Testes de migração simulando edições de schema.
* **Procedimento de Rollback**:
  * Apagar o arquivo `index.sqlite3`. O sistema reconstruirá o banco a partir do zero na versão anterior.
* **Fechamento Obrigatório da Milestone**:
  - [ ] **unittest**: `python3 -m unittest discover -s tests -p "test_*.py"` (100% verde)
  - [ ] **doctor**: `obsv doctor` (retorno 0 / sem side-effects no disco)
  - [ ] **verify**: `obsv verify`
  - [ ] **benchmark**: Medição de velocidade de escrita de transação no SQLite WAL (> 1000 inserções/sec).

---

### M06 — Parser Semântico Mínimo (Markdown, Canvas, Text)

* **Objetivo**: Extrair metadados das notas usando exclusivamente expressos regulares e parsers nativos stdlib (`json`).
* **Escopo**:
  * Extrator de YAML Frontmatter leve (subconjunto seguro sem dependências externas como `PyYAML`).
  * Extrator de `[[wikilinks]]`, `![[embeds]]`, links Markdown padrão `[texto](link)` e `#tags`.
  * Extrator especializado para arquivos `.canvas` via `json.loads`.
  * Retorno de estrutura imutável de metadados extraídos para indexação.
* **Dependências**: M05.
* **Critérios Objetivos de Conclusão**:
  * Parser extrai links, tags e frontmatter de notas complexas sem falhar.
  * Notas malformadas ou com YAML inválido não interrompem o processo e são registradas com aviso.
  * Nenhuma execução de código ou interpretação de HTML ocorre durante a análise.
* **Riscos Técnicos**:
  * Regexes complexas apresentando comportamento catastrófico de backtracking (ReDoS) em notas grandes.
* **Estratégia de Teste (`unittest`)**:
  * `tests/test_parser.py`: Fixtures contendo notas reais com wikilinks, aliases, tags compostas e frontmatters variados.
* **Procedimento de Rollback**:
  * Reverter módulo de parsing `obsv/parser.py`. O índice derivado precisará ser reconstruído.
* **Fechamento Obrigatório da Milestone**:
  - [ ] **unittest**: `python3 -m unittest discover -s tests -p "test_*.py"` (100% verde)
  - [ ] **doctor**: `obsv doctor` (retorno 0 / sem side-effects no disco)
  - [ ] **verify**: `obsv verify`
  - [ ] **benchmark**: Benchmark de parsing semântico (> 500 KB/sec).

---

### M07 — Indexação, Busca e Reconciliação Derivada

* **Objetivo**: Sincronizar o estado do vault no filesystem com o índice derivado SQLite.
* **Escopo**:
  * Implementação dos modos `index`, `index --full` e `index --check`.
  * Indexação incremental baseada na comparação de `mtime`, tamanho e hash dos arquivos.
  * Reconciliação de arquivos deletados ou movidos fora do ObSV (removendo registros órfãos).
  * Marcação do estado do índice como `clean` ou `dirty`.
* **Dependências**: M04, M05, M06.
* **Critérios Objetivos de Conclusão**:
  * Operação de reindexação completa reproduz com exatidão o estado de indexações incrementais.
  * Falhas no SQLite durante escritas marcam o índice como `dirty` sem desfazer a alteração no vault.
  * Consultas de busca por FTS5 ou texto retornam em menos de 100ms em vaults de teste.
* **Riscos Técnicos**:
  * Dessincronização entre filesystem e SQLite após quedas abruptas de energia ou interrupções de processo.
* **Estratégia de Teste (`unittest`)**:
  * `tests/test_indexer.py`: Testar ciclo completo: criar arquivo no vault -> indexar -> alterar -> reconciliar -> validar SQLite.
* **Procedimento de Rollback**:
  * Executar `obsv index --full` para reconstruir o índice ou apagar o banco SQLite.
* **Fechamento Obrigatório da Milestone**:
  - [ ] **unittest**: `python3 -m unittest discover -s tests -p "test_*.py"` (100% verde)
  - [ ] **doctor**: `obsv doctor` (retorno 0 / sem side-effects no disco)
  - [ ] **verify**: `obsv verify`
  - [ ] **benchmark**: Medição do tempo de busca FTS5 (< 50ms em base de 1.000 notas).

---

### M08 — Interface CLI v2 Local

* **Objetivo**: Expor todos os casos de uso operacionais do ObSV via linha de comando local.
* **Escopo**:
  * Implementação dos subcomandos: `init`, `doctor`, `verify`, `stats`, `tree`, `cat`, `new`, `append`, `mkdir`, `mv`, `rm`, `search`, `backlinks`, `links`, `index`.
  * Suporte global à flag `--json` com saída estruturada e estável.
  * Mapeamento de códigos de saída: `0` (sucesso), `1` (aviso/erro de negócio), `2` (erro de configuração/uso).
* **Dependências**: M02, M03, M07.
* **Critérios Objetivos de Conclusão**:
  * Todos os comandos funcionam via linha de comando interagindo exclusivamente com as camadas de caso de uso.
  * A saída em formato JSON é válida e respeita o schema de envelope definido em M01.
* **Riscos Técnicos**:
  * Incompatibilidade de codificação de caracteres (UTF-8 vs locale do terminal) na saída de texto.
* **Estratégia de Teste (`unittest`)**:
  * `tests/test_cli.py`: Invocar os comandos CLI através de `subprocess.run` ou chamadas diretas a `main(argv)` capturando `sys.stdout` e `sys.stderr`.
* **Procedimento de Rollback**:
  * Reverter alterações no módulo `obsv/cli.py`.
* **Fechamento Obrigatório da Milestone**:
  - [ ] **unittest**: `python3 -m unittest discover -s tests -p "test_*.py"` (100% verde)
  - [ ] **doctor**: `obsv doctor` (retorno 0 / sem side-effects no disco)
  - [ ] **verify**: `obsv verify`
  - [ ] **benchmark**: Benchmark de tempo de inicialização da CLI (< 30ms).

---

### M09 — API REST v1 de Leitura e Servidor HTTP Seguro (Perímetro de Rede)

* **Objetivo**: Expor os endpoints de leitura da versão 2 sobre HTTP/HTTPS local ou Tailscale com segurança exclusiva por perímetro de rede.
* **Escopo**:
  * Servidor HTTP utilizando `http.server.ThreadingHTTPServer` nativo.
  * Suporte a TLS via módulo `ssl` stdlib (`certfile` e `keyfile`).
  * Restrição de bind (loopback por padrão; liberação remota apenas com HTTPS, Tailnet, ACLs Tailscale, `tailscale_only` e firewall).
  * **Regra de Segurança**: **Sem autenticação própria por tokens**. A segurança é delegada à camada de transporte e rede.
  * Endpoints de leitura: `/api/v1/health`, `/api/v1/stats`, `/api/v1/tree`, `/api/v1/file`, `/api/v1/raw`, `/api/v1/search`, `/api/v1/backlinks`, `/api/v1/links`.
  * Cabeçalhos de segurança obrigatórios: `X-Content-Type-Options: nosniff`, `Cache-Control: no-store`.
* **Dependências**: M01, M04, M07, M08.
* **Critérios Objetivos de Conclusão**:
  * Acesso remoto não-local sem TLS e fora da Tailnet/Firewall é bloqueado pelo bind de rede e política de transporte.
  * Nenhum código de token ou sessão customizado existe na aplicação.
  * Logs de requisições tratam caminhos de forma privada sem vazar metadados sensíveis.
* **Riscos Técnicos**:
  * Exposição acidental da porta em interfaces públicas se o bind não for estritamente configurado.
* **Estratégia de Teste (`unittest`)**:
  * `tests/test_api_read.py`: Iniciar o servidor HTTP em porta efêmera (`localhost:0`) dentro de um `setUpClass` do `unittest` e realizar requisições via `urllib.request`.
* **Procedimento de Rollback**:
  * Interromper o servidor HTTP e reverter o binário.
* **Fechamento Obrigatório da Milestone**:
  - [ ] **unittest**: `python3 -m unittest discover -s tests -p "test_*.py"` (100% verde)
  - [ ] **doctor**: `obsv doctor` (retorno 0 / sem side-effects no disco)
  - [ ] **verify**: `obsv verify`
  - [ ] **benchmark**: Benchmark de throughput de requisições HTTP GET de leitura (> 300 req/sec).

---

### M10 — API REST v1 de Escrita e Mutações Remotas Condicionais

* **Objetivo**: Habilitar a alteração do vault via requisições HTTP seguras sobre a Tailnet/HTTPS.
* **Escopo**:
  * Endpoints de escrita: `/api/v1/save`, `/api/v1/new`, `/api/v1/append`, `/api/v1/mkdir`, `/api/v1/move`, `/api/v1/delete`, `/api/v1/reindex`.
  * Validação obrigatória de precondição de versão (`If-Match` / hash / mtime) para evitar substituições acidentais.
  * Retorno de HTTP `409 Conflict` quando houver divergência de versão.
  * Separação estrita entre exceções de protocolo HTTP (ex: JSON inválido -> HTTP 400) e erros de domínio do Vault.
* **Dependências**: M09.
* **Critérios Objetivos de Conclusão**:
  * Mutações remotas funcionam com proteção otimista de versão (`409 Conflict` em colisões).
  * Falhas de validação de corpo da requisição retornam erros HTTP de transporte sem gerar `VaultError`.
* **Riscos Técnicos**:
  * Mutações indesejadas caso o firewall ou a ACL Tailscale estejam desconfigurados na máquina hospedeira.
* **Estratégia de Teste (`unittest`)**:
  * `tests/test_api_write.py`: Testar mutações via HTTP usando `urllib.request`, validando respostas `200`, `400`, `404`, `409` e `413`.
* **Procedimento de Rollback**:
  * Desativar a flag de escrita (`--read-only`) ou reverter para a versão M09.
* **Fechamento Obrigatório da Milestone**:
  - [ ] **unittest**: `python3 -m unittest discover -s tests -p "test_*.py"` (100% verde)
  - [ ] **doctor**: `obsv doctor` (retorno 0 / sem side-effects no disco)
  - [ ] **verify**: `obsv verify`
  - [ ] **benchmark**: Benchmark de latência de escrita via API REST (< 20ms por POST/PUT).

---

### M11 — Web UI de Leitura sem JavaScript Obrigatório

* **Objetivo**: Disponibilizar uma interface gráfica no navegador para navegação e visualização de notas sem dependência de JavaScript.
* **Escopo**:
  * Renderização de páginas HTML via templates Python nativos com escapamento rigoroso (`html.escape`).
  * Visualização da árvore de arquivos, leitura de notas traduzidas de Markdown para HTML básico e busca.
  * Política de Segurança do Conteúdo (CSP) restritiva (`script-src 'none'`).
  * Proibição total de renderização de HTML bruto inserido em notas Markdown.
* **Dependências**: M09.
* **Critérios Objetivos de Conclusão**:
  * A navegação, leitura e busca funcionam perfeitamente no navegador com JavaScript totalmente desativado.
  * Nenhuma injeção de script (XSS) é possível através de conteúdo Markdown ou metadados de arquivos.
* **Riscos Técnicos**:
  * Injeção de XSS via atributos de tags HTML permitidas ou URLs `javascript:`.
* **Estratégia de Teste (`unittest`)**:
  * `tests/test_web_ui.py`: Efetuar requisições GET para a interface web e inspecionar a string HTML retornada confirmando escapamento e cabeçalhos CSP.
* **Procedimento de Rollback**:
  * Desativar as rotas da Web UI ou retornar a resposta apenas para endpoints `/api/v1`.
* **Fechamento Obrigatório da Milestone**:
  - [ ] **unittest**: `python3 -m unittest discover -s tests -p "test_*.py"` (100% verde)
  - [ ] **doctor**: `obsv doctor` (retorno 0 / sem side-effects no disco)
  - [ ] **verify**: `obsv verify`
  - [ ] **benchmark**: Benchmark de renderização HTML de notas (> 400 págs/sec).

---

### M12 — Edição Web, Upload e Servimento Raw Endurecido

* **Objetivo**: Adicionar capacidades de escrita via navegador e download seguro de arquivos anexos.
* **Escopo**:
  * Formulários HTML de criação e edição com precondição de versão.
  * Upload de arquivos anexos com validação de extensão, tamanho máximo e restrição de nome.
  * Servimento de arquivos raw com cabeçalho `Content-Disposition: attachment` por padrão para prevenir execução inline no navegador.
  * Tratamento especial para arquivos SVG (forçando o download para evitar execução de Scripts).
* **Dependências**: M09, M10, M11.
* **Critérios Objetivos de Conclusão**:
  * Upload de arquivos executáveis ou fora dos limites é recusado.
  * Download de anexos força a caixa de download do navegador sem executar scripts no contexto da origem.
* **Riscos Técnicos**:
  * Spoofing de Content-Type durante upload de arquivos maliciosos.
* **Estratégia de Teste (`unittest`)**:
  * `tests/test_web_upload.py`: Envio de requisições `multipart/form-encoded` via HTTP e validação dos arquivos gravados no vault.
* **Procedimento de Rollback**:
  * Desativar os formulários de escrita da Web UI mantendo a interface apenas em modo de leitura.
* **Fechamento Obrigatório da Milestone**:
  - [ ] **unittest**: `python3 -m unittest discover -s tests -p "test_*.py"` (100% verde)
  - [ ] **doctor**: `obsv doctor` (retorno 0 / sem side-effects no disco)
  - [ ] **verify**: `obsv verify`
  - [ ] **benchmark**: Benchmark de upload de anexos (> 10 MB/sec).

---

### M13 — Operação, Resiliência e Release v2 Final

* **Objetivo**: Homologar a aplicação para execução de longo prazo como serviço de sistema (`systemd`) e integrar validações operacionais.
* **Escopo**:
  * Arquivo de unidade `systemd` com sandbox de segurança (`ProtectSystem=full`, `PrivateTmp=true`, `NoNewPrivileges=true`).
  * Testes de resiliência e recuperação pós-falha (encerramentos abruptos com `SIGKILL`).
  * Validação final da suíte operacional sob o ambiente de produção Linux.
* **Dependências**: M12.
* **Critérios Objetivos de Conclusão**:
  * O serviço inicia, reinicia e executa sob `systemd` sem privilégios de `root`.
  * Suíte de testes `unittest` passa 100% sem alertas ou vazamentos de recursos.
  * Documentação operacional e manual de implantação finalizados.
* **Riscos Técnicos**:
  * Exaustão de descritores de arquivo (`ulimit -n`) sob uso prolongado do servidor.
* **Estratégia de Teste (`unittest`)**:
  * Execução da suíte completa de integração em ambiente Linux de produção.
* **Procedimento de Rollback**:
  * Parar o serviço `systemd` e restaurar a versão do pacote anterior.
* **Fechamento Obrigatório da Milestone**:
  - [ ] **unittest**: `python3 -m unittest discover -s tests -p "test_*.py"` (100% verde)
  - [ ] **doctor**: `obsv doctor` (retorno 0 / sem side-effects no disco)
  - [ ] **verify**: `obsv verify`
  - [ ] **benchmark**: Benchmark global do sistema (latência de busca < 100ms com 10.000 notas sintéticas).

---

### M14 — Adaptador MCP (Diferido / Pós-v2)

* **Objetivo**: Fornecer integração com o protocolo Model Context Protocol (MCP) sem poluir a arquitetura do núcleo.
* **Escopo**:
  * Processo independente (sidecar CLI) que traduz comandos do protocolo MCP para requisições na API REST `/api/v1`.
  * NENHUM acesso direto ao sistema de arquivos ou ao SQLite a partir do adaptador MCP.
* **Dependências**: M09 (e M10 para capacidades de escrita).
* **Critérios Objetivos de Conclusão**:
  * O adaptador executa em processo separado e interage com o ObSV exclusivamente via HTTP REST.
  * A desativação ou remoção do adaptador MCP não afeta o funcionamento do ObSV.
* **Riscos Técnicos**:
  * Latência adicional introduzida pela camada de tradução MCP -> REST HTTP.
* **Estratégia de Teste (`unittest`)**:
  * `tests/test_mcp_adapter.py`: Mock do servidor REST e validação da tradução de chamadas MCP JSON-RPC.
* **Procedimento de Rollback**:
  * Encerrar o processo do adaptador MCP. O servidor ObSV continuará operando normalmente.
* **Fechamento Obrigatório da Milestone**:
  - [ ] **unittest**: `python3 -m unittest discover -s tests -p "test_*.py"` (100% verde)
  - [ ] **doctor**: `obsv doctor` (retorno 0 / sem side-effects no disco)
  - [ ] **verify**: `obsv verify`
  - [ ] **benchmark**: Benchmark da ponte MCP -> REST HTTP (< 10ms de overhead por comando).

---

## 4. Estratégia de Testes Usando Apenas `unittest`

### 4.1. Regras de Execução de Testes
1. É **estritamente proibido** utilizar `pytest`, `nose` ou qualquer outro test runner de terceiros.
2. A suíte completa deve ser executada exclusivamente pelo comando padrão do Python:
   ```bash
   python3 -m unittest discover -s tests -p "test_*.py" -v
   ```
3. Nenhum teste pode depender do estado da máquina host ou acessar o diretório de usuário real (`~/.config` ou `~/.local`).
4. Todo teste de escrita ou banco de dados deve utilizar diretórios temporários via `tempfile.TemporaryDirectory` ou banco SQLite em memória (`:memory:`).

---

## 5. Estratégia de Integração Contínua (CI)

A integração contínua utiliza exclusivamente scripts compatíveis com a biblioteca padrão do Python e utilitários nativos do POSIX/Linux.

### Pipeline de CI (Passos Obrigatórios)
1. **Verificação de Compilação e Sintaxe**:
   ```bash
   python3 -m py_compile obsv/*.py
   ```
2. **Execução da Suíte Oficial de Testes**:
   ```bash
   python3 -m unittest discover -s tests -p "test_*.py" -v
   ```
3. **Execução do Diagnóstico Inofensivo**:
   ```bash
   python3 -m obsv doctor --json
   ```
4. **Execução da Verificação de Integridade**:
   ```bash
   python3 -m obsv verify
   ```
5. **Auditoria de Código e Ausência de Dependências**:
   Garantir que nenhum arquivo importe bibliotecas fora da stdlib:
   ```bash
   python3 -c "import sys, obsv; print('Módulos carregados OK')"
   ```
6. **Verificação da Integridade da Documentação**:
   Confirmar que `SPEC.md` permanece inalterado durante o processo de CI.

---

## 6. Estratégia Geral de Rollback entre Milestones

Em caso de falha crítica durante ou após a implantação de uma milestone:

1. **O Vault Permanece Intacto**: Dado que o `Vault` no sistema de arquivos é a única fonte de verdade e todas as escritas são atômicas (`fsync` + `rename`), o sistema de arquivos nunca fica em estado parcialmente gravado.
2. **Reversão do Código**: Reverter os binários/código Python para a tag Git da milestone anterior estável.
3. **Recuperação do Índice SQLite**:
   * Se a alteração envolvia mudança de schema SQLite (M05/M07), apague o arquivo `index.sqlite3`.
   * Execute o comando de indexação total na versão anterior para recompor a projeção derivada:
     ```bash
     obsv index --full
     ```
4. **Revisão de Mutações Remotas**: Se a falha ocorreu em mutações remotas (M10/M12), desative temporariamente os endpoints de escrita através do parâmetro de inicialização `--read-only`.

---

## 7. Critérios para Revisão Arquitetural antes da Próxima Milestone

Antes de declarar uma milestone concluída e iniciar a próxima, o revisor arquitetural deve validar o seguinte **Checklist de Homologação**:

- [ ] **Zero Dependências Externas**: O arquivo `pyproject.toml` ou módulo não inclui nenhuma dependência de terceiros.
- [ ] **Suíte `unittest` Aprovada**: O comando `python3 -m unittest discover -s tests -p "test_*.py"` executa com 100% de sucesso.
- [ ] **Diagnóstico `doctor` Limpo**: O comando `obsv doctor` executa sem erros e sem criar/modificar arquivos no disco.
- [ ] **Comando `verify` Aprovado**: O comando `obsv verify` é executado com êxito.
- [ ] **Benchmark Executado**: O indicador de desempenho da milestone foi medido e registrado.
- [ ] **Contrato `SPEC.md` Respeitado**: Nenhuma nova funcionalidade ou alteração de contrato foi introduzida além do especificado.
- [ ] **Sem Autenticação por Token Própria**: A camada HTTP confia estritamente na segurança de perímetro (HTTPS, Tailnet, ACLs, Firewall).
- [ ] **Isolamento de Componentes**: A camada de apresentação (CLI/HTTP) não realiza operações diretas no sistema de arquivos sem passar pelo `Vault`.
- [ ] **Projeção SQLite Desacoplada**: A exclusão do banco de dados SQLite não afeta a leitura básica do vault nem os testes da camada de arquivos.
