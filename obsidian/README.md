# Obsidian Knowledge Curator

Sistema de curadoria automática da base de conhecimento do laboratório.

O Curator usa um agente JCode para analisar documentos recebidos na Inbox, identificar relações com o conhecimento existente, consolidar informação e atualizar a estrutura do Vault Obsidian.

---

## 1. Por que este sistema existe

Os agentes do laboratório produzem conhecimento em diferentes lugares:

- Supabase
- RAG
- handoffs
- decisões
- artifacts
- diagnósticos
- relatórios
- contextos de agentes
- documentos Markdown

O problema não é armazenar esses documentos.

O problema é **conectar o conhecimento**.

Uma coleção de Markdown sem relações transforma o Obsidian em um depósito de arquivos. O Curator existe para transformar esse depósito em uma base de conhecimento navegável.

O fluxo conceitual é:

```text
Agentes
   │
   ▼
00-Inbox
   │
   ▼
Knowledge Curator
   │
   ├── identifica entidades
   ├── identifica projetos
   ├── identifica decisões
   ├── identifica incidentes
   ├── identifica agentes
   ├── encontra relações
   ├── consolida conhecimento
   └── cria [[wikilinks]]
   │
   ▼
Knowledge Vault
   │
   ├── Projetos
   ├── Laboratórios
   ├── ADR
   ├── Arquitetura
   ├── Agentes
   ├── Decisões
   ├── Runbooks
   ├── Incidentes
   └── Referências
````

---

## 2. Localização

Projeto:

```text
/home/teco/work_out/obsidian
```

Vault:

```text
/home/teco/work_out/knowledge
```

Inbox:

```text
/home/teco/work_out/knowledge/00-Inbox
```

Arquivos já processados:

```text
/home/teco/work_out/knowledge/00-Inbox/_processed
```

Prompts:

```text
/home/teco/work_out/obsidian/prompts
```

Agente:

```text
/home/teco/work_out/obsidian/agents/curator.py
```

Launcher:

```text
/home/teco/work_out/obsidian/run-curator.sh
```

Relatórios:

```text
/home/teco/work_out/obsidian/reports
```

---

## 3. Como usar

Coloque documentos Markdown em:

```text
~/work_out/knowledge/00-Inbox/
```

Depois execute:

```bash
cd ~/work_out/obsidian
./run-curator.sh
```

O Curator:

1. encontra os `.md` da Inbox;
2. lê os documentos;
3. consulta o Vault existente;
4. identifica relações;
5. atualiza ou cria notas canônicas;
6. cria links `[[wikilinks]]`;
7. gera relatório;
8. move documentos processados para `_processed/`.

Arquivos em `_processed/` não devem ser processados novamente.

---

## 4. Princípio fundamental

O Curator **não é um simples organizador de arquivos**.

Ele deve responder:

> "Onde esta informação pertence e com quais informações existentes ela se relaciona?"

Exemplo:

```text
Supabase
   │
   ├── decisão de governança
   │       │
   │       └── Atlas
   │
   ├── projeto Padroeira
   │       │
   │       ├── incidentes
   │       ├── decisões
   │       └── tasks
   │
   └── agentes
           │
           ├── JCode
           ├── Codex
           └── Claude
```

O resultado esperado é uma rede de conhecimento, não uma coleção de resumos independentes.

---

## 5. Estrutura do Vault

A estrutura atualmente utilizada é:

```text
knowledge/
├── 00-Inbox/
│   └── _processed/
├── 01-Projetos/
├── 02-Laboratorios/
├── 03-ADR/
├── 04-Arquitetura/
├── 05-Agentes/
├── 06-Decisoes/
├── 07-Runbooks/
├── 08-Incidentes/
├── 09-Referencias/
├── Home.md
└── README.md
```

O Curator deve preferir a estrutura existente.

Não deve criar novas categorias apenas para acomodar um documento.

---

## 6. Segurança e preservação

O Curator não deve:

* alterar `.obsidian/`;
* alterar configurações do Obsidian;
* alterar código do laboratório;
* alterar arquivos fora do Vault;
* apagar documentos da Inbox;
* apagar conhecimento existente sem justificativa;
* inventar fatos;
* substituir decisões históricas por interpretações;
* criar links para entidades inexistentes sem necessidade.

Documentos processados devem ser movidos para:

```text
00-Inbox/_processed/
```

Nunca usar `rm` para eliminar documentos recebidos.

---

## 7. O agente

Atualmente o executor é:

```text
JCode
```

Versão conhecida no momento da implantação:

```text
jcode v0.67.0
```

Verificar versão:

```bash
jcode --version
```

Ver ajuda:

```bash
jcode run --help
```

O Curator é deliberadamente desacoplado do modelo.

A troca futura de modelo/provider deve ser feita no launcher ou no agente, sem alterar a lógica conceitual da curadoria.

---

## 8. Arquivos importantes

### `agents/curator.py`

Controla:

* descoberta dos documentos;
* exclusão de `_processed`;
* construção da solicitação ao JCode;
* execução do agente.

Não colocar conhecimento permanente neste arquivo.

---

### `prompts/curator.md`

É a especificação operacional do Curator.

Aqui ficam:

* objetivo;
* regras de curadoria;
* estrutura do Vault;
* política de preservação;
* comportamento esperado;
* regras de arquivamento.

**Alterações de comportamento devem preferencialmente ser feitas aqui, e não no Python.**

---

### `run-curator.sh`

É o ponto de entrada operacional.

Deve permanecer simples.

Exemplo de uso:

```bash
./run-curator.sh
```

---

### `reports/curation-latest.md`

Relatório da última execução.

Serve para auditoria rápida:

* documentos processados;
* notas alteradas;
* decisões tomadas;
* problemas encontrados.

---

## 9. Logs

Os logs ficam em:

```text
~/work_out/obsidian/logs/
```

Cada execução pode produzir um arquivo como:

```text
curator-YYYYMMDD-HHMMSS.log
```

Para verificar a última execução:

```bash
ls -t ~/work_out/obsidian/logs/curator-*.log | head -1
```

---

## 10. Teste controlado

Antes de alterar o Curator, testar com um documento isolado.

```bash
mkdir -p ~/work_out/knowledge/00-Inbox/_test
```

Criar um Markdown pequeno:

```text
00-Inbox/_test/test.md
```

Executar:

```bash
cd ~/work_out/obsidian
./run-curator.sh
```

Verificar:

```bash
find ~/work_out/knowledge/00-Inbox -type f
```

O arquivo deve terminar em:

```text
00-Inbox/_processed/
```

Depois verificar:

```bash
cat ~/work_out/obsidian/reports/curation-latest.md
```

---

## 11. Regra para mudanças futuras

Antes de modificar o Curator:

1. criar teste;
2. executar;
3. registrar resultado;
4. alterar uma coisa por vez;
5. executar novamente;
6. verificar o Vault;
7. verificar o relatório;
8. verificar Git.

Não fazer refatorações grandes sem necessidade.

---

## 12. Upgrade do JCode

Antes de atualizar:

```bash
jcode --version
```

Depois da atualização:

```bash
jcode --version
jcode run --help
```

Confirmar especialmente:

* `jcode run`;
* `--tools`;
* `-C/--cwd`;
* providers;
* autenticação;
* comportamento não interativo.

Executar novamente o teste controlado antes de usar a Inbox real.

---

## 13. Troca de agente

O Curator não depende conceitualmente do JCode.

Outro agente pode assumir a função desde que consiga:

* ler Markdown;
* ler o Vault;
* escrever Markdown;
* executar operações de arquivo;
* criar links;
* trabalhar de forma não interativa;
* gerar relatório.

Possíveis candidatos:

```text
JCode
Codex
Claude Code
OpenCode
Gemini CLI
```

A escolha deve considerar principalmente:

1. capacidade de raciocínio sobre múltiplos documentos;
2. capacidade de trabalhar com arquivos;
3. estabilidade em execução headless;
4. custo;
5. contexto disponível;
6. facilidade de manutenção.

---

## 14. Não confundir com RAG

O Curator não substitui o RAG.

RAG responde:

> "Qual informação relevante existe?"

O Curator responde:

> "Como essa informação deve ser integrada ao conhecimento existente?"

São funções diferentes.

Fluxo ideal:

```text
Agentes
   │
   ▼
Supabase / RAG
   │
   ▼
Inbox
   │
   ▼
Curator
   │
   ▼
Knowledge Graph / Markdown
   │
   ▼
RAG futuro
```

---

## 15. Git

O Curator não deve fazer commits automaticamente.

Depois de uma execução:

```bash
cd ~/work_out
git status --short
```

Revisar alterações antes de commit.

Nunca assumir que alterações exibidas por:

```bash
git status
```

foram causadas pelo Curator.

O diretório `~/work_out` contém outros projetos e alterações independentes.

---

## 16. Problemas conhecidos

### Inbox aparece vazia

Verificar:

```bash
find ~/work_out/knowledge/00-Inbox -type f -name "*.md"
```

Lembrar que `_processed/` contém arquivos já processados.

---

### Argument list too long

O primeiro protótipo apresentou:

```text
OSError: [Errno 7] Argument list too long: 'jcode'
```

Causa:

O conteúdo excessivo dos documentos foi colocado diretamente no argumento do processo.

A implementação atual deve enviar ao JCode somente instruções e o manifesto dos arquivos, permitindo que o agente leia os documentos com suas ferramentas.

Se esse erro reaparecer, não aumentar arbitrariamente o tamanho do prompt. Corrigir a interface de entrada.

---

### Curator altera demais

Parar a execução.

Verificar:

```bash
git status --short
```

Inspecionar:

```bash
cat ~/work_out/obsidian/reports/curation-latest.md
```

O Curator deve trabalhar dentro do Vault e não alterar infraestrutura do laboratório.

---

## 17. Filosofia de manutenção

Este projeto deve permanecer pequeno.

Não adicionar:

* banco de dados próprio;
* servidor adicional;
* framework de agentes;
* camada RAG própria;
* sincronização complexa;
* automação desnecessária.

A arquitetura desejada é:

```text
Markdown
   +
Obsidian
   +
JCode
   +
script pequeno
   +
prompt versionado
```

A complexidade deve estar no **raciocínio do agente**, não na infraestrutura.

---

## 18. Objetivo de longo prazo

O objetivo final é transformar:

```text
documentos isolados
```

em:

```text
conhecimento conectado
```

com relações explícitas entre:

```text
Projetos
    ↕
Decisões
    ↕
Agentes
    ↕
Incidentes
    ↕
Arquitetura
    ↕
Runbooks
    ↕
Referências
```

O Obsidian é a representação humana e navegável.

O RAG é a camada de recuperação.

O Supabase continua sendo a fonte oficial dos dados estruturados quando aplicável.

O Curator é a ponte que transforma informação produzida pelos agentes em conhecimento organizado e conectado.

---

## 19. Manutenção rápida

Diagnóstico:

```bash
cd ~/work_out/obsidian
jcode --version
find ~/work_out/knowledge/00-Inbox -type f -name "*.md"
ls -t logs/curator-*.log | head
cat reports/curation-latest.md
```

Execução:

```bash
./run-curator.sh
```

Teste:

```bash
mkdir -p ~/work_out/knowledge/00-Inbox/_test
```

Git:

```bash
cd ~/work_out
git status --short
```

---

**Status:** operacional em 18/08/2026.

**Executor:** JCode 0.67.0.

**Função:** curadoria e conexão semântica da Knowledge Base.

**Princípio:** preservar a informação original, integrar conhecimento e construir conexões.
