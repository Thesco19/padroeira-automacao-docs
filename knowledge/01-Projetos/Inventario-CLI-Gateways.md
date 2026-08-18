---
created: 2026-07-25
updated: 2026-08-18
project: inventario-cli
tags: [inventario, cli, gateways, litellm, omniroute, redis, free-tier]
tipo: projeto-especificacao
---

# Projeto: Inventário CLI & Gateways de IA (LiteLLM & OmniRoute)

**Projeto:** `inventario-cli`  
**Status:** Ativo / Auditoria Concluída (100% Free-Tier Preservado)  
**Responsável Técnico:** [[OpenCode]] / [[Claude]]  

---

## 1. Visão Geral

O projeto **Inventário CLI & Gateways** unifica o mapeamento de todas as ferramentas de linha de comando de IA (Aider, OpenCode, Claude Code, JCode, Kilo, Kimi, Gemini CLI) e os gateways de roteamento local [[LiteLLM]] e [[OmniRoute]].

---

## 2. Diretriz de Governança: 100% Free-Tier

- **Política Estrita:** Toda a infraestrutura de modelos e gateways opera 100% dentro do **free-tier** (provedores gratuitos como Groq, Cerebras, SambaNova, HuggingFace, Gemini Free e NVIDIA NIM).
- **Aliases `claude-*` no LiteLLM:** Os nomes de aliases `claude-code`, `claude-code-fast`, `claude-opus-4-8-20251001` mantêm essa nomenclatura no LiteLLM por exigência dos clientes CLI, mas são roteados para endpoints compatíveis/gratuitos via OpenRouter / LiteLLM proxy.

---

## 3. Mapeamento de Gateways

| Gateway | Porta | Protocolo | Tipo / Função |
| :--- | :--- | :--- | :--- |
| **[[LiteLLM]]** | `8000` | OpenAI-compatible / Anthropic `/v1/messages` | Proxy com aliases fake → modelos reais |
| **[[OmniRoute]]** | `20128` | OpenAI-compatible / Smart Routing | Routing com múltiplos provedores e fallback inteligente |

---

## 4. Tabela de Conversão: CLI → Alias → Gateway / Provedor Real

| Ferramenta CLI | Modelo Solicitado | Gateway / Porta | Alias Interno | Provedor / Endpoint Real |
| :--- | :--- | :--- | :--- | :--- |
| **[[OpenCode]]** | `auto/best-coding` | OmniRoute (20128) | `auto/best-coding` | Smart Routing (Groq/Cerebras/Together) |
| **[[OpenCode]]** | `big-pickle` | OmniRoute (20128) | `oc/big-pickle` | Provedor dinâmico |
| **[[Claude Code]]** | `claude-sonnet-4.6` | LiteLLM (8000) / OmniRoute | `claude-code` | OpenRouter / Anthropic |
| **[[JCode]]** | `mistral-medium` | LiteLLM (8000) | `mistral-medium` | Mistral AI (`api.mistral.ai`) |
| **[[Gemini CLI]]** | `gemini-3.1-flash-lite` | LiteLLM (8000) | `gemini-3.1-flash-lite` | Google AI Studio |
| **Aider** | `cerebras/gpt-oss-120b` | Direto / LiteLLM | `cerebras-gpt-oss-120b` | Cerebras AI (`api.cerebras.ai`) |
| **Kimi** | `moonshot-v1-128k` | Direto | N/A | Moonshot AI |

---

## 5. Resolução de Conflitos e Receita de Correção

1. **Conflito de Porta Redis (OmniRoute vs LiteLLM):**
   - Resolução: Isolar instâncias Redis e garantir que a porta padrão do OmniRoute não colida com o cache do LiteLLM.
2. **Reordenação de Fallback no Alias `claude-code`:**
   - LiteLLM reordenado para priorizar rotas gratuitas com tempo de resposta mais baixo (Groq / Cerebras) com fallback para OpenRouter.
3. **Provedores no Dashboard OmniRoute:**
   - Configurados provedores real-time com verificação de chaves e tratamento de cota.

---

## Links Relacionados

- [[2026-08-16-omniroute-400-encrypted-fix]]
- [[Agentes-do-Laboratorio]]
- [[LAB-Resumo]]
