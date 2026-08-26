# Padrões de Desenvolvimento

## Objetivo
Documentar as diretrizes e padrões de desenvolvimento observados no Projeto Atlas, visando a consistência do código e a eficiência dos processos operacionais.

## Estilo de Código (Python)
- **Estruturação:** O código é estruturado predominantemente em classes (ex: `EngineConsolidacao`, `MotorBalancete`) com métodos executáveis principais.
- **Tipagem:** O uso de type hints não é consistente em todos os arquivos analisados.
- **Imports:** Importações seguem o padrão de colocar bibliotecas de terceiros seguidas de módulos locais.
- **Regex:** O uso intensivo de `re` para extração de dados é um padrão observado na extração de informações de texto bruto.
- **Tratamento de Dados:** Presença de métodos auxiliares para tratamento seguro de tipos (ex: `_to_float()`).

## Versionamento (Git)
- **Uso de Git:** O diretório raiz contém uma estrutura de repositório Git ativa (`.git/`).
- **Padrões de Commit:** Evidenciado por histórico de commits indicando features e revisões (ex: `feat:`, `claude code review`).

## Testes e Automação
- **Ambiente de Testes:** Utilização de um diretório dedicado (`mock_box/`) para simular o ambiente de produção, separando dados reais de testes.
- **Automação:** Os testes são integrados no fluxo de trabalho (ex: `test_conversor.py`), indicando uma prática de validar componentes isoladamente.
- **Validação de Paridade:** Observada a implementação de scripts específicos para verificar a paridade entre planilhas (`teste_paridade.py`).

## Gerenciamento de Configuração
- **Configuração de Agentes:** Utiliza arquivos JSON/YAML centralizados para configuração de serviços e proxys de LLM (ex: `/opt/stacks/litellm/config.yaml`).
- **Variáveis de Ambiente:** Uso de placeholders no formato `os.environ/` para configurações sensíveis.

## Interação com Agentes de IA
- **Diretrizes de Agente:** A configuração da IA é gerenciada pelo arquivo `.claude/` e regras de comportamento no `.cursorrules`.
- **Protocolo de Memória:** O projeto utiliza um sistema de memória compartilhada (MCP) para troca de contexto entre agentes, documentado em `MCP_SHARED_MEMORY_GUIDE.md` e configurado via `.mcp.json`.

## Limitações Observadas
- NÃO FOI POSSÍVEL DETERMINAR a existência de um guia de estilo de código formal (ex: PEP8 estrito).
- NÃO FOI POSSÍVEL DETERMINAR a cobertura de testes automatizados completa do sistema.
- NÃO FOI POSSÍVEL DETERMINAR a estratégia de branching utilizada para novas funcionalidades.

## Referências
- `lab/conversor.py`
- `lab_agente_web/cortex_padroeira.py`
- `.cursorrules`
- `.mcp.json`
- `/opt/stacks/litellm/config.yaml`