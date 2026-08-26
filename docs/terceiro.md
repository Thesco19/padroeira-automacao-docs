# Relatório terceiro.md

## PARTE 1 - DEPENDÊNCIAS REAIS

Análise de referências entre diretórios (imports, configurações, scripts).

| Origem | Destino | Tipo | Arquivo | Trecho |
| :--- | :--- | :--- | :--- | :--- |
| /opt/stacks/litellm/config.yaml | Sistema (Ambiente) | Referência (Variável) | /opt/stacks/litellm/config.yaml | database_url: "os.environ/DATABASE_URL" |

*Nota: A maioria dos imports encontrados (via `grep`) refere-se a bibliotecas padrão do Python (ex: `os`, `argparse`) ou bibliotecas externas instaladas (`playwright`, `openpyxl`, `google-genai`). Não foram encontradas evidências de imports cruzados entre os projetos listados (ex: import de `lab_inventory` dentro de `lab_agente_web`).*

---

## PARTE 2 - DIRETÓRIOS INDEPENDENTES

| Diretório | Pode ser movido? | Justificativa |
| :--- | :--- | :--- |
| app/ | NÃO FOI POSSÍVEL DETERMINAR | Evidência insuficiente sobre a utilização deste diretório. |
| arquivados_testes/ | SIM | Parece ser apenas um repositório de arquivos antigos sem referências ativas. |
| backup/ | SIM | Estrutura de backup independente. |
| .claude/ | NÃO | Diretório de infraestrutura de configuração do agente. |
| .git/ | NÃO | Repositório principal do sistema. |
| lab/ | NÃO FOI POSSÍVEL DETERMINAR | Alta complexidade e arquivos heterogêneos. |
| lab_agente_web/ | NÃO FOI POSSÍVEL DETERMINAR | Possíveis dependências não mapeadas pelo `grep`. |
| lab-b/ | SIM | Poucos arquivos, parece um experimento isolado. |
| lab_inventory/ | NÃO FOI POSSÍVEL DETERMINAR | Estrutura de projeto com dependências internas. |
| .mcp_context/ | NÃO | Infraestrutura crítica de colaboração entre agentes. |
| mock_box/ | NÃO FOI POSSÍVEL DETERMINAR | Possível referenciado em scripts (não confirmados). |
| notebook_export/ | SIM | Apenas exportações de documentos. |
| recursos/ | NÃO | Contém configurações essenciais para outros módulos. |
| .venv/ | NÃO | Ambiente virtual de execução. |

---

## PARTE 3 - DEPENDÊNCIAS DA RAIZ

Arquivos que obrigatoriamente devem permanecer na raiz (devem estar no local de execução/vcs):

- **.git/**: Repositório principal.
- **.claude/**: Configurações dos agentes.
- **.mcp_context/**: Contexto MCP.
- **CLAUDE.md**: Instruções de operação.
- **.gitignore**: Regras do VCS.
- **.mcp.json**: Configuração MCP.
- **.venv/**: Ambiente de execução.

---

## PARTE 4 - PROJETOS

| Projeto | Autonomia | Dependências Externas | Pode virar independente? | Pode ser movido para: |
| :--- | :--- | :--- | :--- | :--- |
| lab_agente_web/ | NÃO FOI POSSÍVEL DETERMINAR | Provável (Litellm/Rede) | NÃO FOI POSSÍVEL DETERMINAR | NÃO FOI POSSÍVEL DETERMINAR |
| lab_inventory/ | NÃO FOI POSSÍVEL DETERMINAR | Provável (Dados) | NÃO FOI POSSÍVEL DETERMINAR | NÃO FOI POSSÍVEL DETERMINAR |

---

## PARTE 5 - RISCO

| Diretório | Risco | Motivo |
| :--- | :--- | :--- |
| .git/ | Alto | Quebra o controle de versão do workspace. |
| .venv/ | Alto | Quebra o ambiente de execução Python. |
| recursos/ | Médio | Pode quebrar configurações de serviços (ex: Litellm). |
| .claude/ | Médio | Pode quebrar a funcionalidade dos agentes. |
| lab/ | Médio | Alta complexidade e incerteza de uso. |
| arquivados_testes/ | Baixo | Apenas arquivos legados. |
| notebook_export/ | Baixo | Apenas documentação. |