# 1. Visão Geral

O workspace em /home/teco/work_out está organizado como um repositório Git contendo múltiplos diretórios que parecem representar diferentes projetos, laboratórios e componentes de um sistema maior relacionado à reconciliação fiscal (Projeto: Reconciliação Fiscal V2 - Padroeira / Restaurante). Há também diretórios de apoio como backup, recursos, arquivos de configuração e ambientes virtuais. A estrutura indica um ambiente de desenvolvimento ativo com múltiplas tentativas de implementação e experimentos.

---

# 2. Diretórios da raiz

Diretório: app
Finalidade: Parece ser uma aplicação principal ou um componente do sistema, possivelmente relacionada ao projeto principal.
Status: Ativo (contém arquivos recentes e estrutura de código)
Tecnologias encontradas: Python (arquivos .py), possivelmente um pacote ou módulo.
Confiança: Média
Justificativa: O diretório contém arquivos Python, mas não há um README ou indicativo claro de seu propósito específico no contexto do projeto maior.

Diretório: arquivados_testes
Finalidade: Armazenamento de testes antigos ou arquivos que foram movidos para arquivo.
Status: Legado (nome sugere arquivamento, conteúdo parece ser de testes antigos)
Tecnologias encontradas: Vários arquivos Python e possivelmente configurações antigas.
Confiança: Alta
Justificativa: O nome "arquivados_testes" indica claramente que é um diretório para arquivar testes antigos.

Diretório: backup
Finalidade: Armazenamento de backups de arquivos ou estados anteriores do projeto.
Status: Ativo (contém backups recentes, conforme a data de modificação)
Tecnologias encontradas: Vários tipos de arquivos de backup (possivelmente cópias de código, configurações, etc.)
Confiança: Alta
Justificativa: O nome e a presença de arquivos com timestamps recentes indicam que é usado para backup.

Diretório: .claude
Finalidade: Configurações e dados específicos do Claude Code (assistente de IA).
Status: Ativo (contém configurações recentes)
Tecnologias encontradas: Configurações do Claude Code (agentes, skills, etc.)
Confiança: Alta
Justificativa: Diretório padrão do Claude Code para configurações pessoais do assistente.

Diretório: .git
Finalidade: Repositório Git do projeto.
Status: Ativo (repositório ativo com commits recentes)
Tecnologias encontradas: Git
Confiança: Alta
Justificativa: É o diretório Git do repositório, essencial para versionamento.

Diretório: lab
Finalidade: Laboratório para experimentos e desenvolvimento de funcionalidades relacionadas ao projeto principal.
Status: Ativo (contém arquivos recentes e parece ser usado para desenvolvimento)
Tecnologias encontradas: Python, possivelmente scripts de teste e desenvolvimento.
Confiança: Média
Justificativa: O nome sugere um laboratório de experimentação, e contém arquivos relacionados ao projeto principal.

Diretório: lab_agente_web
Finalidade: Laboratório ou projeto relacionado a um agente web, possivelmente para interface web ou automação web.
Status: Ativo (contém arquivos recentes e estrutura de projeto)
Tecnologias encontradas: Python, possivelmente configurações de litellm, config.yaml
Confiança: Média
Justificativa: O nome sugere um agente web, e há arquivos de configuração relacionados a litellm (LLM integration).

Diretório: lab-b
Finalidade: Segundo laboratório ou ramo de experimentação, possivelmente uma ramo de desenvolvimento alternativo.
Status: Legado ou Indeterminado (contém alguns arquivos, mas menos atividade recente)
Tecnologias encontradas: Vários arquivos Python e possivelmente experimentos antigos.
Confiança: Baixa
Justificativa: O nome é genérico e o conteúdo não é imediatamente claro; pode ser um ramo antigo de experimentação.

Diretório: lab_inventory
Finalidade: Laboratório ou módulo relacionado à gestão de inventário, possivelmente parte do sistema de reconciliação fiscal.
Status: Ativo (contém estrutura de diretórios e arquivos recentes)
Tecnologias encontradas: Python, possivelmente scripts de gestão de inventário.
Confiança: Média
Justificativa: O nome sugere relação com inventário, e há estrutura de diretórios que indica um projeto organizado.

Diretório: .mcp_context
Finalidade: Contexto compartilhado para o sistema MCP (Multi-Agent Collaboration Protocol) usado no projeto.
Status: Ativo (contém arquivos recentes e é mencionado nas instruções do projeto)
Tecnologias encontradas: Configurações e dados do MCP
Confiança: Alta
Justificativa: É mencionado explicitamente nas instruções do projeto como necessário para coerência entre sessões de diferentes agentes.

Diretório: mock_box
Finalidade: Ambiente de mock que simula o ambiente de produção (Box) usado para testes e desenvolvimento sem afetar os dados reais.
Status: Ativo (contém estrutura de pastas que simula o ambiente de produção)
Tecnologias encontradas: Estrutura de diretórios que simula o Box (pastas como Restaurante/A2026/, Padroeira_vendas/, etc.)
Confiança: Alta
Justificativa: É mencionado nas instruções do projeto como o ambiente de testes e desenvolvimento, montado via rclone.

Diretório: notebook_export
Finalidade: Exportação de Jupyter Notebooks ou análises interativas.
Status: Legado ou Indeterminado (contém poucos arquivos, possivelmente exportações antigas)
Tecnologias encontradas: Possivelmente arquivos de arquivos, mas atividade não clara)
Tecnologias encontradas: Possivelmente arquivos .ipynb ou exports de notebooks.
Confiança: Baixa
Justificativa: O nome sugere exportação de notebooks, mas não há indicação clara de uso recente ou propósito específico no projeto.

Diretório: recursos
Finalidade: Recursos compartilhados utilizados por diferentes partes do projeto, como configurações, modelos, etc.
Status: Ativo (contém subdiretórios como litellm com arquivos de configuração)
Tecnologias encontradas: YAML (config.yaml), markdown, possivelmente configurações de LLMs.
Confiança: Média
Justificativa: O nome sugere recursos compartilhados, e contém configurações para litellm (integração com LLMs).

Diretório: .venv
Finalidade: Ambiente virtual Python para isolamento de dependências do projeto.
Status: Ativo (ambiente virtual padrão do Python)
Tecnologias encontradas: Python virtual environment
Confiança: Alta
Justificativa: É um ambiente virtual Python padrão, usado para gerenciar dependências do projeto.

---

# 3. Arquivos soltos

Arquivo: CLAUDE.md
Finalidade: Instruções e regras do projeto para o Claude Code (agente de IA).
Deveria permanecer na raiz: Sim, pois é específico da configuração do Claude para este projeto.
Projeto: Projeto principal (Reconciliação Fiscal V2)

Arquivo: .cursorrules
Finalidade: Configurações para o Cursor IDE (assistente de código).
Deveria permanecer na raiz: Sim, se o projeto é usado no Cursor IDE.
Projeto: Configuração de IDE, não específico do projeto mas útil para desenvolvimento.

Arquivo: .gitignore
Finalidade: Define quais arquivos e diretórios devem ser ignorados pelo Git.
Deveria permanecer na raiz: Sim, é padrão em repositórios Git.
Projeto: Repositório Git do projeto.

Arquivo: info.md
Finalidade: Informações gerais sobre o projeto, possivelmente visão geral ou instruções iniciais.
Deveria permanecer na raiz: Sim, pois contém informações gerais do projeto.
Projeto: Projeto principal.

Arquivo: INSTALAR_E_TESTAR_MCP.md
Finalidade: Instruções para instalar e testar o MCP (Multi-Agent Collaboration Protocol).
Deveria permanecer na raiz: Sim, pois é específico da configuração do MCP para este projeto.
Projeto: Configuração do MCP no projeto.

Arquivo: .mcp.json
Finalidade: Configuração do MCP (Multi-Agent Collaboration Protocol).
Deveria permanecer na raiz: Sim, é o arquivo de configuração principal do MCP.
Projeto: Configuração do MCP no projeto.

Arquivo: MCP_SHARED_MEMORY_GUIDE.md
Finalidade: Guia para uso da memória compartilhada do MCP.
Deveria permanecer na raiz: Sim, é parte da documentação do MCP para o projeto.
Projeto: Configuração do MCP no projeto.

Arquivo: PROGRESSO_V2.md
Finalidade: Documento de progresso detalhado do Projeto Reconciliação Fiscal V2.
Deveria permanecer na raiz: Sim, pois contém o progresso detalhado do projeto principal.
Projeto: Projeto principal (Reconciliação Fiscal V2).

---

# 4. Projetos identificados

Projeto: Reconciliação Fiscal V2 (Padroeira / Restaurante)
Objetivo: Sistema para reconciliação fiscal de restaurantes, envolvendo processos de fechamento de caixa, conciliação de balancete e integração com sistemas externos (como Saurus).
Linguagem: Python
Docker: Não identificado (não há Dockerfile ou docker-compose.yml visível na raiz ou nos diretórios principais)
Git próprio: Parte do repositório principal (o repositório Git na raiz contém este projeto)
Arquivos principais encontrados:
- cortex_padroeira.py (bot Telegram para escuta de comandos)
- engine_consolidacao.py (fase 1: consolidação de dados)
- motor_balancete.py (fase 2: auditoria por faturamento e sangria)
- PROGRESSO_V2.md (documento detalhando o progresso)
- CLAUDE.md (instruções para o agente Claude)
- Estrutura de mock_box que simula o ambiente de produção
Estado: Ativo (conforme o documento PROGRESSO_V2.md, todas as fases estão marcadas como concluídas, mas o projeto está em desenvolvimento ativo com múltiplos agentes)

Projeto: lab_agente_web
Objetivo: Desenvolvimento de um agente web, possivelmente para interface web ou integração com LLMs (como visto na presença de config.yaml do litellm).
Linguagem: Python
Docker: Não identificado
Git próprio: Parte do repositório principal
Arquivos principais encontrados:
- lab_agente_web/litellm/config.yaml (configuração para litellm)
- lab_agente_web/async_reconciliation_v2.py (possivelmente uma versão assíncrona do motor de reconciliação)
Estado: Ativo (contém arquivos recentes e estrutura de projeto)

Projeto: lab_inventory
Objetivo: Gestão de inventário, possivelmente integrado ao sistema de reconciliação fiscal.
Linguagem: Python
Docker: Não identificado
Git próprio: Parte do repositório principal
Arquivos principais encontrados:
- Estrutura de diretórios com possíveis módulos de gestão de estoque
Estado: Ativo (contém estrutura de diretórios e arquivos recentes)

Projeto: lab
Objetivo: Laboratório geral para experimentos e desenvolvimento de funcionalidades relacionadas ao projeto principal.
Linguagem: Python
Docker: Não identificado
Git próprio: Parte do repositório principal
Arquivos principais encontrados:
- Vários scripts Python que parecem ser experimentos ou testes de funcionalidades
Estado: Ativo (contém arquivos recentes)

Projeto: lab-b
Objetivo: Segundo laboratório ou ramo de experimentação (propósito menos claro).
Linguagem: Python
Docker: Não identificado
Git próprio: Parte do repositório principal
Arquivos principais encontrados:
- Alguns arquivos Python que parecem ser experimentos antigos
Estado: Legado ou abandonado (menos atividade recente, nome genérico)

Projeto: notebook_export
Objetivo: Exportação de Jupyter Notebooks para compartilhamento ou arquivamento.
Linguagem: Possivelmente Jupyter Notebooks (.ipynb)
Docker: Não identificado
Git próprio: Parte do repositório principal
Arquivos principais encontrados:
- Arquivos exportados de notebooks
Estado: Legado ou pouco usado (não há indicação clara de uso recente)

---

# 5. Infraestrutura

Diretório: .claude
Finalidade: Configurações específicas do Claude Code (agente de IA usado no projeto).
Deve permanecer na raiz: Sim, pois é necessário para a configuração do agente de IA que trabalha no projeto.
Justificativa: O projeto usa múltiplos agentes (Claude, Gemini, OpenCode, JCode, Kilo) e o .claude contém configurações específicas para o Claude.

Diretório: .mcp_context
Finalidade: Contexto compartilhado para o sistema MCP (Multi-Agent Collaboration Protocol).
Deve permanecer na raiz: Sim, pois é explicitamente mencionado nas instruções do projeto como necessário para coerência entre sessões de diferentes agentes.
Justificativa: O projeto depende do MCP para compartilhar memória e estado entre agentes.

Diretório: .venv
Finalidade: Ambiente virtual Python para isolamento de dependências.
Deve permanecer na raiz: Sim, pois é padrão em projetos Python para gerenciar dependências e evitar conflitos.
Justificativa: O projeto é em Python e usa dependências específicas que devem ser isoladas.

Diretório: recursos
Finalidade: Recursos compartilhados como configurações de LLMs (litellm), possivelmente outros recursos comuns.
Deve permanecer na raiz: Sim, pois contém configurações que são usadas por múltiplos componentes do projeto (como lab_agente_web).
Justificativa: Os recursos são compartilhados entre diferentes partes do projeto, tornando-o necessário na raiz.

Diretório: .git
Finalidade: Repositório Git para versionamento do código.
Deve permanecer na raiz: Sim, é essencial para o versionamento do projeto.
Justificativa: Sem o .git, não há versionamento, o que é crítico para desenvolvimento colaborativo.

Diretório: backup
Finalidade: Backups de arquivos e estados anteriores do projeto.
Deve permanecer na raiz: Sim, pois é uma prática comum manter backups no mesmo repositório para fácil acesso e segurança.
Justificativa: Embora os backups possam ser movidos para armazenamento externo, mantê-los no repositório facilita a restauração rápida durante o desenvolvimento.

Diretório: mock_box
Finalidade: Ambiente de mock que simula o ambiente de produção (Box) para testes e desenvolvimento.
Deve permanecer na raiz: Sim, pois é usado para testes sem afetar dados reais, e é mencionado nas instruções do projeto.
Justificativa: O projeto depende deste ambiente para desenvolvimento e teste seguro.

---

# 6. Problemas encontrados

- Diretórios duplicados: Não foram identificados diretórios duplicados com o mesmo nome exatamente, mas há múltiplos laboratórios (lab, lab_agente_web, lab-b, lab_inventory) que podem ter sobreposição de funcionalidade.
- Projetos parcialmente misturados: Os diretórios lab, lab_agente_web, lab-b e lab_inventory parecem ser laboratórios ou experimentos que podem estar misturando funcionalidades do projeto principal sem clara separação.
- Documentação espalhada: Há vários arquivos de documentação na raiz (info.md, PROGRESSO_V2.md, MCP_SHARED_MEMORY_GUIDE.md, INSTALAR_E_TESTAR_MCP.md) além do CLAUDE.md, o que pode causar confusão sobre onde encontrar informações específicas.
- Possíveis arquivos órfãos: Arquivos como .cursorrules, .mcp.json e outros arquivos de configuração estão na raiz, o que é apropriado, mas alguns arquivos em diretórios como arquivados_testes podem ser órfãos (não utilizados mais).
- Possíveis testes antigos: O diretório arquivados_testes contém claramente testes antigos, mas há possibilidade de testes antigos também em outros diretórios como lab ou lab-b.
- Possíveis backups esquecidos: O diretório backup está ativo, mas há possibilidade de backups antigos em outros locais (como em arquivados_testes ou até mesmo na raiz com extensões de backup).

---

# 7. Dúvidas

- Qual é o propósito exato do diretório 'app' e como ele se relaciona com os outros componentes do projeto?
- O diretório lab-b está ativamente sendo usado ou é um ramo abandonado de experimentação?
- Qual é a relação entre lab_inventory e o projeto principal de reconciliação fiscal?
- O notebook_export está sendo usado ativamente ou é um legado de análises anteriores?
- Há planos para consolidar os diversos laboratórios (lab, lab_agente_web, lab-b, lab_inventory) em uma estrutura mais clara?
- O diretório 'recursos' contém apenas configurações do litellm ou há outros recursos que deveriam ser organizados de forma diferente?
- Por que existem múltiplos arquivos de configuração para MCP (.mcp.json, MCP_SHARED_MEMORY_GUIDE.md, INSTALAR_E_TESTAR_MCP.md) e eles não estão consolidados em um local de documentação mais claro?

---

# 8. Resumo

O workspace está organizado em torno do projeto principal de Reconciliação Fiscal V2, que parece estar em estado avançado de desenvolvimento (com todas as fases marcadas como concluídas no PROGRESSO_V2.md). No entanto, há múltiplos diretórios de laboratório e experimentos que podem estar criando confusão sobre a estrutura do projeto. A infraestrutura necessária (como .git, .venv, .claude, .mcp_context, recursos, mock_box e backup) está apropriadamente posicionada na raiz. A documentação está um pouco dispersa, mas cobre os aspectos principais do projeto. A próxima etapa deveria envolver uma investigação mais profunda em cada diretório de laboratório para entender seu propósito e determinar se há sobreposição ou funcionalidade que deveria ser integrada ao projeto principal ou arquivada.