---
created: 2026-08-16
project: omniroute
tags: [omniroute, debug, fix, gemini, codex, schema, lab-e]
tipo: incidente-fix
---

# Incidente & Correção: OmniRoute HTTP 400 "Unknown name encrypted" (Gemini via Codex)

**Data:** 2026-08-16  
**Serviço / Componente:** [[OmniRoute]] (`lab-e`, container `omniroute-lab`, API `http://127.0.0.1:20128`)  
**Agente afetado:** [[Codex]] (`auto/best-coding`)  
**Status:** Resolvido e persistido via overlay image  

---

## Sintoma

O agente [[Codex]] utilizando o modelo `auto/best-coding` via gateway [[OmniRoute]] entrava em ciclo de *"Reconnecting..."* apresentando o seguinte erro HTTP 400 retornado pelo provedor Gemini:

```text
HTTP 400 Unknown name "encrypted" at 'tools[0].function_declarations[3/6/7].parameters.properties[0].value': Cannot find field.
```

---

## Causa Raiz

- O [[Codex]] envia ferramentas de colaboração (`collaboration__followup_task`, `collaboration__send_message`, `collaboration__spawn_agent`) cujo JSON Schema da propriedade `message` contém a flag customizada `"encrypted": true` (convenção client-side do Codex).
- O sanitizador do tradutor Gemini (`GEMINI_UNSUPPORTED_SCHEMA_KEYS` localizado em `open-sse/translator/helpers/geminiHelper.ts`) não incluía a chave `"encrypted"`. Assim, a chave não era filtrada antes de enviar para a API da Google Gemini, disparando o erro HTTP 400.

---

## Correção Aplicada & Persistência

### 1. Correção em Runtime (Fonte e Chunks)
1. **Source:** Em `/app/open-sse/translator/helpers/geminiHelper.ts`, a chave `"encrypted"` foi adicionada ao conjunto `GEMINI_UNSUPPORTED_SCHEMA_KEYS`.
2. **Chunks Compilados:** Nos 9 arquivos de chunk Next.js (`/app/.build/next/server/chunks/open-sse_*.js`), substituiu-se `,"cornerRadius"` por `,"encrypted","cornerRadius"`.

### 2. Persistência via Imagem Overlay Reproduzível
Para garantir a permanência da correção pós-reboot/recreate de containers:
- **Artefatos no Host (`/opt/stacks/omniroute`):**
  - `patches/encrypted-schema-fix/geminiHelper.ts` (código fonte patcheado).
  - `patches/encrypted-schema-fix/chunks/open-sse_*.js` (9 chunks patcheados).
  - `Dockerfile` (overlay `FROM diegosouzapw/omniroute:3.8.49` + `COPY` dos arquivos).
  - `compose.yaml` (imagem atualizada para `omniroute-lab:3.8.49-encrypted-fix`).

---

## Validação

- Teste de execução do Codex: `codex exec --json --skip-git-repo-check "Reply with exactly: OK"`
- **Resultado:** `agent_message: "OK"`, `turn.completed`, zero ocorrências de erro HTTP 400 no schema.
- **Nota upstream:** O fix já foi mesclado na branch `release/v3.8.50` do repositório upstream `diegosouzapw/OmniRoute`. Quando a versão 3.8.50+ for oficialmente lançada no Docker Hub, a imagem overlay poderá ser substituída pela oficial.

---

## Links Relacionados

- [[Inventario-CLI-Gateways]]
- [[Agentes-do-Laboratorio]]
- [[LAB-Resumo]]
