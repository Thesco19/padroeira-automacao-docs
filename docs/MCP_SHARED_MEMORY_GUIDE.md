# 🧠 Protocolo de Memória Compartilhada (MCP Context)

Este projeto utiliza um servidor MCP rodando em Docker (`http://localhost:8765`) para manter a persistência de contexto entre diferentes agentes (Claude, Gemini, OpenCode, JCode, Kilo).

## 📂 Localização dos Dados
A memória **NÃO** é global. Cada projeto possui seu próprio contexto isolado na pasta:
`./.mcp_context/`

- **`memory.json`**: Armazena chaves-valor para fatos, configurações e decisões rápidas.
- **`rag_store/`**: Armazena documentos e históricos de conversa para busca semântica.

## 🛠️ Regras para Agentes
1. **Consulta Inicial**: Ao iniciar qualquer tarefa, o agente DEVE chamar `memoria_listar` e `rag_buscar` com a consulta "resumo do projeto" para recuperar o estado atual.
2. **Gravação de Decisões**: Sempre que uma decisão arquitetural ou técnica for tomada, utilize `memoria_salvar` para registrar a chave e o valor correspondente.
3. **Histórico de Conversa**: Ao encerrar a sessão ou concluir um marco importante, utilize `rag_indexar` para salvar um resumo do que foi feito e o que ficou pendente.
4. **Isolamento**: Não tente ler memórias de outros projetos; utilize apenas a pasta `.mcp_context` do diretório de trabalho atual.

## 🚀 Ferramentas Disponíveis
- `memoria_salvar(chave, valor)`
- `memoria_recuperar(chave)`
- `memoria_listar()`
- `rag_indexar(doc_id, texto)`
- `rag_buscar(consulta)`
