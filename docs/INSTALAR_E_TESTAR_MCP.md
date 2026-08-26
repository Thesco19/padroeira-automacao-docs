================================================================================
GUIA: INSTALAR E TESTAR O MCP "lab-universal" (Memória + RAG)
================================================================================
Servidor: mcp-lab-universal  (FastMCP / SSE)
Endpoint : http://localhost:8765/sse
Ferramentas expostas:
  - status_lab        -> status do nó (sem dependência de rede)
  - search_knowledge  -> busca semântica na base RAG (Chroma)
  - ingest_document   -> ingere documento na base RAG
  - memorizar_fato    -> grava fato na memória persistente (mem0)
  - buscar_memoria    -> pesquisa na memória compartilhada (mem0)

Pré-requisito para TODOS os agentes: o container deve estar rodando.
  docker ps | grep mcp-lab-universal
  # Se não estiver:
  docker start mcp-lab-universal
  # Ou, a partir de /home/teco/work_out (onde está o docker-compose):
  docker compose up -d

Teste rápido de que o endpoint responde (fora do agente):
  curl -N -m 3 http://localhost:8765/sse
  # Deve imprimir uma linha "event: endpoint" / "data: /messages/?session_id=..."

IMPORTANTE — limitação conhecida de rede (vale para todos os agentes):
  O container NÃO consegue alcançar generativelanguage.googleapis.com
  (SSL handshake timeout). Consequentemente:
    - memorizar_fato / buscar_memoria (mem0 -> Gemini) VÃO FALHAR por timeout.
    - search_knowledge / ingest_document (Chroma DefaultEmbeddingFunction)
      também dependem de download/execução do modelo de embedding e podem falhar.
    - status_lab FUNCIONA (não usa rede externa).
  Para deixar memória e RAG 100% funcionais, dê egresso de internet ao container
  para o Google, OU troque LLM/embedder por modelo local (ex.: Ollama em
  http://127.0.0.1:11434, que já roda nesta máquina).

OBSERVAÇÃO sobre concorrência do servidor SSE:
  O FastMCP SSE atende UMA sessão por vez. Se uma sessão anterior não fechar
  limpa, o próximo "GET /sse" trava. Se um agente travar ao conectar:
    docker restart mcp-lab-universal
  e tente novamente.

================================================================================
1) KILO  (já configurado — mantido como referência)
--------------------------------------------------------------------------------
Arquivo: /home/teco/work_out/kilo.jsonc  (config de PROJETO do Kilo)

{
  "$schema": "https://app.kilo.ai/config.json",
  "mcp": {
    "lab-universal": {
      "type": "remote",
      "url": "http://localhost:8765/sse",
      "enabled": true
    }
  },
  "permission": {
    "lab-universal_*": "allow"
  }
}

Testar dentro do Kilo:
  /mcps            -> deve listar "lab-universal" como conectado
  /status          -> confirma MCPs carregados
  Pergunte ao agente: "use a ferramenta status_lab e me diga o resultado."

================================================================================
2) OPENCODE
--------------------------------------------------------------------------------
Arquivo: /home/teco/.config/opencode/opencode.json  (já existe; adicione o bloco "mcp")

ATENÇÃO: a configuração atual do opencode aponta o servidor como "local"
(stdio via `docker exec ... python /app/server_final.py`). Isso NÃO funciona,
pois o container roda uvicorn SSE, não stdio. Substitua por "remote" SSE:

{
  "$schema": "https://opencode.ai/config.json",
  "provider": { ... (manter o existente) ... },
  "model": "litellm/qwen2.5-coder",
  "mcp": {
    "lab-universal": {
      "type": "remote",
      "url": "http://localhost:8765/sse",
      "enabled": true
    }
  }
}

Testar:
  opencode  -> iniciar o TUI
  /mcp      -> lista servidores; "lab-universal" deve aparecer como ok
  Peça: "rode a tool status_lab e mostre a saída."

================================================================================
3) CLAUDE CODE
--------------------------------------------------------------------------------
Config global de MCP fica em ~/.claude.json (chave "mcpServers") ou via comando.
Adicionar (SSE):

  claude mcp add --transport sse lab-universal http://localhost:8765/sse

Ou editar ~/.claude.json manualmente (mesmo formato do Claude Desktop):

{
  "mcpServers": {
    "lab-universal": {
      "type": "sse",
      "url": "http://localhost:8765/sse"
    }
  }
}

Testar:
  claude mcp list            -> deve mostrar lab-universal conectado
  claude mcp get lab-universal -> detalhes e ferramentas
  No chat: "use status_lab e retorne o resultado."

================================================================================
4) GEMINI-CLI
--------------------------------------------------------------------------------
JÁ CONFIGURADO em ~/.gemini/settings.json (bloco "mcpServers"). Conteúdo atual:

{
  "security": { "auth": { "selectedType": "gemini-api-key" } },
  "mcpServers": {
    "local-server": {
      "url": "http://localhost:8765/sse",
      "type": "sse"
    }
  }
}

Se quiser usar o mesmo nome dos outros agentes, renomeie "local-server" para
"lab-universal" (opcional). Nenhuma ação extra necessária.

Testar:
  gemini  -> abrir o CLI
  /mcp    -> listar servidores e ferramentas
  Pergunte: "call the status_lab tool and show the output."

================================================================================
5) JCODE
--------------------------------------------------------------------------------
O jcode NÃO tem suporte a cliente MCP no momento (só existe o subcomando "acp",
voltado a Agent Client Protocol / providers internos). Não há `jcode mcp add`.

Opções:
  a) Usar jcode como cliente ACP de outro servidor que exponha este MCP (avançado).
  b) Aguardar suporte a MCP no jcode, ou usar um dos agentes acima para as
     ferramentas de memória/RAG.
  c) Se o jcode passar a ler .mcp.json, crie na raiz do projeto:

     {
       "mcpServers": {
         "lab-universal": {
           "type": "sse",
           "url": "http://localhost:8765/sse"
         }
       }
     }

  Por ora, NÃO é possível conectar o jcode diretamente a este MCP.

================================================================================
6) TESTE PADRÃO (script independente, fora dos agentes)
--------------------------------------------------------------------------------
Arquivo de exemplo: /home/teco/work_out/test_kilo_mcp.py
Requer o módulo `mcp` (python3 do sistema já o tem: mcp 1.28.0).

  # Garanta o container limpo (uma sessão por vez):
  docker restart mcp-lab-universal
  sleep 3
  cd /home/teco/work_out
  python3 test_kilo_mcp.py

Esperado:
  TOOLS: ['status_lab', 'search_knowledge', 'ingest_document',
          'memorizar_fato', 'buscar_memoria']
  status_lab               -> "Nó Santuário operando normalmente. RAG ativo."
  search_knowledge/ingest_ -> erro de SSL/timeout (rede do container sem Google)
  memorizar_fato/buscar_   -> erro de timeout (mem0 -> Gemini indisponível)

================================================================================
RESUMO DE STATUS (verificado em 2026-07-17)
--------------------------------------------------------------------------------
  [OK] Servidor SSE sobe e lista 5 ferramentas.
  [OK] status_lab funciona em todos os agentes que conectarem.
  [FALHA] memória (mem0/Gemini) e RAG (embedding) por falta de egresso p/ Google.
  [FEITO] Kilo, OpenCode (corrigir p/ remote), Claude Code, Gemini-CLI documentados.
  [N/D]   jcode — sem suporte a MCP cliente hoje.
================================================================================
