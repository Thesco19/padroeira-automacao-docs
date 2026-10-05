# Resolução de Bugs - Perplexica com Gemini 3.1 Flash Lite

**Status**: ✅ FUNCIONAL  
**Data**: 06/09/2026  
**Ambiente**: Mac Mini → Docker (container `perplexica`, imagem `vane:local`, network_mode host)

## Problema Original
Perplexica não respondia queries complexas com busca web usando Gemini 3.1 Flash Lite como LLM.

## Bugs Identificados e Resolvidos

### 1. skipSearch forçado
- **Problema**: Gemini classificava queries como "What is quantum computing?" como `skipSearch: true`
- **Solução**: Forçado `c.classification.skipSearch=false` em `route.js` e `index.ts`
- **Arquivos**: `.next/server/app/api/search/route.js`, `src/lib/agents/search/index.ts`

### 2. generateObject incompatível com Gemini
- **Problema**: `chat.completions.parse()` não suportado pelo Gemini
- **Solução**: Trocado por `chat.completions.create()` com `response_format: {type: "json_object"}`, strip de code fences, wrap com `repairJson`
- **Arquivo**: `.next/server/chunks/136.js`

### 3. Tool schemas rejeitados pelo Gemini
- **Problema**: Gemini rejeita `additionalProperties`, `$schema`, `$ref`, `$defs` nos schemas
- **Solução**: Classe `sanitizeSchemaForGemini` recursivamente limpa os schemas antes de enviar
- **Arquivo**: `.next/server/chunks/136.js`

### 4. streamText/OpenAI SDK incompatível
- **Problema**: OpenAI SDK adiciona `strict:!0` e não suporta `thinking` parameter do Gemini
- **Solução**: `streamText` reescrito com raw `fetch()` para o endpoint Gemini, parser SSE manual
- **Arquivo**: `.next/server/chunks/136.js`

### 5. thought_signature obrigatório (Gemini 3.x)
- **Problema**: Gemini 3.x requer `thought_signature` em function calls, sem ele retorna 400
- **Solução**: Signatures capturadas de `extra_content.google.thought_signature` no stream, re-injetadas via `extra_content` no assistant message
- **Arquivo**: `.next/server/chunks/641.js`

### 6. convertToOpenAIMessages perdia extra_content
- **Problema**: Mapeamento de mensagens descartava `extra_content`
- **Solução**: Patch para preservar `extra_content` em tool_calls do assistant
- **Arquivo**: `.next/server/chunks/136.js`

### 7. SearXNG timeout
- **Problema**: Timeout de 10s insuficiente
- **Solução**: Aumentado para 30s
- **Arquivo**: `.next/server/chunks/641.js`

## Configuração
```json
{
  "chatModel": {"providerId": "gemini-provider-001", "key": "models/gemini-3.1-flash-lite"},
  "embeddingModel": {"providerId": "4a709892-267a-4e98-b719-8a5dab393a3a", "key": "Xenova/all-MiniLM-L6-v2"}
}
```

## Observações
- Patches aplicados no container em runtime (não baked na imagem)
- Para persistir: rebuild da imagem Docker a partir do source atualizado
- Gemini 3.1 Flash Lite: modelo único disponível que funciona
- Endpoints: LLM `https://generativelanguage.googleapis.com/v1beta/openai`, Embedding via transformers.js local