# Contexto operacional — Codex

> Última análise: 2026-08-09. Esta é uma nota de orientação para atuação no
> laboratório; as fontes normativas são `LAB.md`, `LAB.yaml` e `AGENTS.md` na raiz.

## Escopo do diretório

`/home/teco/work_out` é um laboratório de engenharia do conhecimento com múltiplos
projetos independentes. Não deve ser tratado como uma única aplicação.

| Área | Papel identificado |
| --- | --- |
| `knowledge/` | Vault Obsidian oficial e documentação compartilhada. |
| `app/` e `tests/` | Aplicação Python na raiz, estruturada em domínio, portas e serviços de aplicação. |
| `lab-a/` | Automação. |
| `lab-b/` | Integrações WhatsApp/MCP. |
| `lab-c/` | Projetos de MCP, bridge, autenticação e adaptadores. |
| `lab-d/` | Ferramentas operacionais: Playwright MCP, API Doctor e inventário CLI. |
| `lab-e/` | Homologação de ferramentas de IA; inclui OmniRoute. |
| `lab-g/` | Atlas Bridge/Lab-Central, com banco, migrações e protocolo de coordenação. |
| `lab-obsv/` | Observabilidade. |
| `lab-z/` | Polyglot Swarm e Regente. |
| `backup/` | Material histórico; não alterar sem solicitação explícita. |

## Governança e documentação

- O Vault oficial é `knowledge/`, definido por `knowledge.vault` em `LAB.yaml`.
- Não criar um Vault alternativo e não produzir documentação fora do Vault.
- Organização do Vault: `01-Projetos`, `02-Laboratorios`, `03-ADR`, `04-Prompts`,
  `05-Agentes`, `06-Decisoes`, `07-Runbooks` e `08-Incidentes`.
- `LAB.md` define a governança; `AGENTS.md` define o processo de análise e mudança.
- Antes de atuar em um laboratório, localizar e ler suas instruções, README,
  documentação e arquivos de configuração próprios.

## Procedimento de trabalho

1. Confirmar qual laboratório/projeto é afetado.
2. Ler arquivos relacionados, dependências e testes antes de editar.
3. Identificar causa raiz, impacto e riscos; apresentar a estratégia antes da mudança.
4. Preservar fronteiras arquiteturais e evitar alterações em projetos vizinhos.
5. Executar validações proporcionais: testes unitários para backend e verificação de
   navegador quando houver impacto em interface.
6. Registrar decisões, runbooks ou ADRs no Vault quando a alteração justificar.

## Riscos observados nesta fotografia

- A árvore Git da raiz possui muitas alterações e exclusões pendentes, além de muitos
  itens não rastreados. Essas alterações não devem ser assumidas como pertencentes à
  tarefa corrente.
- Existem repositórios Git aninhados (por exemplo, `lab-a`, `lab-c`, `lab-e` e
  `lab-obsv`); sempre verificar o repositório correto antes de usar Git.
- Há documentação histórica também em `docs/` e dentro dos laboratórios. Ela é útil
  para contexto, mas novas documentações devem ir para `knowledge/`.
- Alguns dados de execução, backups e possíveis segredos/configurações locais podem
  existir em diretórios de laboratório; evitar expô-los em logs, commits ou notas.

## Pontos de entrada úteis

- Visão do laboratório: `knowledge/02-Laboratorios/LAB-Resumo.md`.
- Infraestrutura de coordenação: `lab-g/README.md` e `lab-g/docs/`.
- Arquitetura da aplicação Python da raiz: `docs/plano_arquitetura_hexagonal.md`,
  `app/domain/`, `app/ports/` e `app/application/services/`.
- Ambiente de testes de interface: `lab-d/stacks/playwright-mcp/README.md`.
- Avaliação de roteamento/compatibilidade de clientes: `lab-e/omniroute/`.

## Limites desta nota

Esta nota é um índice operacional, não uma fonte de estado em tempo real. Antes de
qualquer mudança, verificar o estado atual do Git, as instruções locais e a
documentação específica do componente afetado.
