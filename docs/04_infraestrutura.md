# Infraestrutura

## Objetivo
Documentar a infraestrutura técnica e os componentes de suporte que sustentam o Projeto Atlas, permitindo a reprodutibilidade e a manutenção do ambiente de desenvolvimento e execução.

## Ambiente de Desenvolvimento
- **Isolamento:** Utiliza ambientes virtuais Python localizados em `/.venv/`.
- **Configuração de IDE:** Regras de comportamento e estilo de desenvolvimento centralizadas em `/.cursorrules`.
- **Assistência de IA:** Configurações de agentes e ferramentas de automação presentes em `/.claude/`.

## Orquestração e Contêineres
- **Orquestração:** O projeto faz uso de infraestrutura baseada em Docker.
- **Evidências:** 
    - `/opt/stacks/litellm/compose.yaml`
    - `/opt/stacks/litellm/config.yaml`
- **Limitação:** NÃO FOI POSSÍVEL DETERMINAR a existência de uma estratégia de orquestração completa para todos os módulos.

## Configurações de Integração
- **Protocolo MCP:** Utiliza o sistema de colaboração entre agentes, estruturado através de:
    - `/.mcp_context/`
    - `/.mcp.json`
    - `MCP_SHARED_MEMORY_GUIDE.md`
- **Recursos Compartilhados:** A infraestrutura de recursos é centralizada em `/recursos/`, contendo definições de proxy de LLM (litellm).

## Simulação e Testes
- **Ambiente de Simulação:** Utiliza o diretório `/mock_box/` para simular o sistema de arquivos de produção, com estruturas de dados predefinidas em formato XLSX.
- **Armazenamento de Testes:** Scripts e dados de testes legados ou arquivados estão localizados em `/arquivados_testes/`.

## Gestão de Versionamento e Backups
- **Versionamento:** O projeto é versionado via Git, com o repositório principal na raiz (`/.git/`).
- **Backup:** Existe uma estrutura dedicada para backups em `/backup/`, contendo arquivos com extensões `.bak`, logs e históricos de chat.

## Limitações Conhecidas
- NÃO FOI POSSÍVEL DETERMINAR a política de retenção dos logs e backups.
- NÃO FOI POSSÍVEL DETERMINAR o processo automatizado de remontagem do ambiente Box fora do ambiente de desenvolvimento.
- NÃO FOI POSSÍVEL DETERMINAR a estratégia de deploy para produção.

## Referências
- `.git/`
- `.venv/`
- `/opt/stacks/litellm/`
- `.mcp.json`
- `.claude/`