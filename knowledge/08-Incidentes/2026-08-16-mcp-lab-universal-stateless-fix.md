---
created: 2026-08-16
project: mcp-lab-universal
tags: [mcp, opencode, debug, fix, stateless, lab-c]
tipo: incidente-fix
---

# Incidente & Correção: MCP lab-universal -32602 no OpenCode

**Data:** 2026-08-16  
**Serviço / Componente:** `mcp-lab-universal` (`lab-c`)  
**Cliente afetado:** [[OpenCode]] (v1.18.3)  
**Status:** Resolvido e validado  

---

## Sintoma

Todas as ferramentas (tools) do MCP `mcp-lab-universal` (inclusive `status_lab`) passaram a falhar no cliente [[OpenCode]] com erro `-32602: Invalid request parameters` após a reinicialização (restart) do container `mcp-lab-universal`.

---

## Causa Raiz

O cliente MCP do [[OpenCode]] 1.18.3 (que inclui o SDK legado `@modelcontextprotocol/sdk@1.29.0` com patch próprio) reconecta o stream SSE após um restart do servidor **sem re-executar o handshake `initialize`** na nova sessão. Ele abre um novo `GET /sse` e envia `tools/call` diretamente.

O servidor Python (SDK MCP 1.28.1) é estritamente aderente à especificação e rejeitava requisições de sessão não inicializada:
- `mcp/server/session.py:205` → `RuntimeError("Received request before initialization was complete")`
- Convertido em `-32602` em `mcp/shared/session.py:383-407`.

### Evidências Coletadas

- **Sessão pré-restart (`7fafa475`):** Handshake completo (`initialize` → `initialized` → `tools/list` → `tools/call`) — Sucesso.
- **Sessão pós-restart (`c546761f`):** Apenas `tools/call` sem `initialize` → `WARNING: Failed to validate request` → Erro `-32602`.
- **SDK TS Oficial 1.30.0 (`/tmp/opencode/ts-sse-test.mjs`):** Conecta, lista e chama `status_lab` com sucesso contra o mesmo servidor.
- **Código do OpenCode (`packages/opencode/src/mcp/index.ts`):** O manipulador `watch()` / `onclose` apenas remove o cliente do estado e publica `ToolsChanged`, sem realizar re-handshake ou reconexão completa.

---

## Solução Aplicada

Ativação do modo `stateless` do SDK Python no ponto de entrada `server_final.py` (montado via bind mount):

```python
import mcp.server.lowlevel.server as _ll
_ll_server_run = _ll.Server.run

async def _ll_run_stateless(self, read_stream, write_stream, initialization_options, **kwargs):
    kwargs.setdefault("stateless", True)
    return await _ll_server_run(self, read_stream, write_stream, initialization_options, **kwargs)

_ll.Server.run = _ll_run_stateless
```

### Impacto da Mudança

- `ServerSession._initialization_state` é inicializado como `Initialized` (`server/session.py:91`), permitindo a aceitação de requisições sem handshake prévio.
- Clientes que realizam o handshake correto (como [[Claude]], [[Codex]], e o SDK TS oficial) continuam operando normalmente sem alterações de comportamento.
- O monkeypatch foi necessário porque o caminho SSE do FastMCP (`handle_sse`) não repassava o parâmetro `stateless` diretamente.

---

## Validação

1. Chamada à tool `status_lab`: Retornou `"Nó Santuário operando normalmente. RAG ativo."`.
2. Logs do servidor: `Processing request of type CallToolRequest` sem avisos de *"before initialization"*.
3. Logs temporários de DEBUG removidos após confirmação.

---

## Links Relacionados

- [[mcp-lab-universal-admin]]
- [[Agentes-do-Laboratorio]]
- [[LAB-Resumo]]
