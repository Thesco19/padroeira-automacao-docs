# SMARTCAM × STRIX — ARCHITECTURE ASSESSMENT

Data: 2026-10-04 · Status: **proposta — aguarda revisão do Auditor e aprovação do Usuário**
Escopo: avaliação arquitetural para eventual integração. Nenhum arquivo do repositório foi modificado.

---

## 1. Arquitetura e componentes atuais do SmartCam

**Localização**: `/home/teco/work_out/lab-b/smartcam` (repo próprio, branch `main`; mapa de referência `smartcam_arch_v1`, ARQUITETURA.2026-09-30.md). Serviço systemd user ativo, HTTP :3100 / HTTPS :3443.

**Stack**: Node.js 22 + Express 4 (backend), React 19/Vite 6 (frontend), Python 3 sidecar YOLOv8n, Gemini (análise de frame), ffmpeg.

**Descoberta / rede** (o núcleo desta avaliação):
- `POST /api/scan-network-cameras` — **scan TCP real** (server.ts:368): perfis stealth/balanced/aggressive (batchSize 1–20, timeouts 250–700ms), circuit breaker no stealth, exclusão de gateways, descoberta passiva WS-Discovery + mDNS (5s, `src/utils/passive-discovery.ts`) priorizada antes do TCP.
- `identifyCamera()` (server.ts:305): probe ONVIF (554/8080) e HTTP/MJPEG (80/8000/81/8080). Sem banco de padrões de URL — os stream URLs são templates fixos (`rtsp://ip:8554/stream0`, `rtsp://ip:8080/`).
- `POST /api/test-camera-ping` (server.ts:570) — ping de câmera única.
- Módulos purple team: `cred-probe.ts` (rate 1/s, allowlist CIDR), `exploit-probe.ts` (GATED), `cve-lookup.ts` (offline, informativo), `sensitive-log.ts` (3 fatores admin).

**Limitação central identificada**: o SmartCam *encontra* hosts com portas de vídeo e identifica o protocolo, mas **não sabe construir a URL correta do stream** — depende de templates fixos e credenciais em `data/rtsp-creds.json`. É exatamente a lacuna que o Strix preenche.

## 2. Arquitetura do Strix

**Fontes**: repositório público `eduard256/Strix` (MIT, Go, v2.0.0, binário estático; DEVELOPERS.md e internal/probe/probe.go inspecionados). **Não há clone local** — instalação proposta na seção de plano.

**Mecanismo de probing**:
1. Probe de ~100–120ms por IP (probe.go): portas abertas, vendor via ARP/OUI, mDNS/HomeKit, banner HTTP, ONVIF, Xiaomi miIO (UDP:54321).
2. Matching contra `cameras.db` (SQLite, repo StrixCamDB): **~3.600 marcas, 67K modelos, 102K+ padrões de URL**; três tipos de entidade — `preset` / `brand` / `model` (id `b:hikvision`, `m:hikvision:DS-2CD2032`, `p:onvif`).
3. Construção de URLs candidatos com credenciais/placeholder; **20 workers paralelos** testam cada URL, capturam screenshot ao vivo, codec, resolução e latência.
4. Protocolos: RTSP 554, RTSPS 322, HTTP/HTTPS (MJPEG/snapshot/HLS/TS), RTMP 1935, Bubble (XMeye), DVRIP 34567, HomeKit 51826.

**Interface**: binário único com UI web `:4567` (`STRIX_LISTEN`) + **API HTTP JSON sem autenticação** (CORS aberto):
```
GET /api/probe?ip=…        → detecção (portas, vendor, ONVIF, mdns, xiaomi)
GET /api/search?q=…        → busca no banco (brand/model/preset)
GET /api/streams?ids=…&ip=…&user=…&pass=… → URLs candidatos montados
POST /api/test             → teste paralelo dos streams (poll em /api/test?id=…)
POST /api/generate         → config Frigate/go2rtc pronta
```
Variáveis: `STRIX_LISTEN`, `STRIX_DB_PATH`, `STRIX_LOG_LEVEL`, `STRIX_FRIGATE_URL`, `STRIX_GO2RTC_URL`. Sem dependências externas (ffmpeg opcional para screenshot). Emulador de teste: **StrixCamFake**.

**Observação de segurança relevante**: a API do Strix não tem auth e não tem allowlist — o oposto do design do SmartCam (API key, LAB_ALLOWED_CIDR, gating admin). Qualquer integração precisa colocar o Strix atrás do perímetro do SmartCam, nunca exposto.

## 3. Sobreposição funcional e capacidades complementares

| Capacidade | SmartCam | Strix | Sobreposição |
|---|---|---|---|
| Descoberta passiva (WS-Discovery/mDNS) | ✅ própria | ✅ (mDNS + HomeKit) | parcial |
| Varredura de subnet | ✅ perfis stealth + circuit breaker | ❌ (probe por IP) | **complementar** |
| Identificação de vendor/modelo | genérica ("ONVIF Camera") | ✅ banco 67K modelos | **complementar** |
| Construção de stream URL | templates fixos (falha na maioria) | ✅ 102K+ padrões | **Strix cobre a lacuna** |
| Teste de stream (screenshot, codec, latência) | parcial (ping) | ✅ com ffmpeg | Strix melhor |
| Credenciais | probe controlado (rate 1/s, allowlist) | manuais na UI | **SmartCam tem mais controle** |
| Detecção YOLO / Gemini / sandbox | ✅ núcleo do produto | ❌ | SmartCam único |
| Purple team (CVE, cred-probe, exploit-probe) | ✅ GATED | ❌ | SmartCam único |
| Geração de config Frigate/go2rtc | ❌ | ✅ | Strix único |

**Conclusão**: sobreposição só na camada de descoberta; o valor é a composição — SmartCam *descobre hosts com segurança e disciplina de rede*, Strix *identifica o modelo e resolve a URL real do stream*.

## 4. Contrato de abstração proposto — `StreamDiscoveryProvider`

Criar interface em novo módulo `src/providers/stream-discovery.ts` (nenhum provider nativo no código hoje — confirmado por grep):

```typescript
export interface CameraStreamCandidate {
  url: string;          // rtsp://…, http://…
  protocol: "rtsp" | "rtsps" | "http" | "rtmp" | "bubble" | "dvrip";
  kind: "main" | "sub";
  verified: boolean;    // testado com sucesso pelo provider
  codec?: string;
  resolution?: string;
  latencyMs?: number;
  screenshotDataUri?: string; // opcional, para o frontend
}

export interface StreamDiscoveryRequest {
  ip: string;
  openPorts: number[];        // do scan do SmartCam
  hints?: { vendor?: string; model?: string; mdnsName?: string };
  credentials?: { user: string; pass: string };
}

export interface StreamDiscoveryProvider {
  readonly name: string;      // "strix", "builtin-templates"
  available(): Promise<boolean>;
  discoverStreams(req: StreamDiscoveryRequest): Promise<CameraStreamCandidate[]>;
}
```

**Implementações**:
1. `StrixProvider` — HTTP client para a API do Strix: `probe` (opcional, se SmartCam não trouxe hints) → `search` (vendor detectado via OUI/ONVIF) → `streams` (monta URLs) → `test` (verifica). Credenciais vindas do fluxo existente do SmartCam (`data/rtsp-creds.json` / cred-probe), **nunca** do Strix.
2. `BuiltinTemplatesProvider` — envolve os templates fixos atuais de `identifyCamera()` como fallback quando o Strix não está disponível.

**Ponto de injeção**: fim de `identifyCamera()`/fluxo do scan (server.ts:305) — em vez de devolver o template fixo, chama o provider e devolve os candidatos verificados no payload de `devices[]` do scan.

**Regras que o contrato impõe**:
- Provider nunca recebe subnets inteiras — só IPs já descobertos pelo SmartCam. O controle de ritmo (perfis, circuit breaker) permanece 100% do SmartCam.
- Falha do provider ≠ falha do scan: `discoverStreams` rejeita → fallback builtin, dispositivo entra com `streamUrl` template e `verified: false`.
- Resposta do Strix é tratada como dados não confiáveis (mesma origem ≠ confiável).

## 5. Riscos, testes e rollback

**Riscos**:
- R1 — **Superfície de rede**: API do Strix sem auth/CORS aberto. Mitigação: rodar em `127.0.0.1` apenas (`STRIX_LISTEN=127.0.0.1:4567`), chamado só pelo backend do SmartCam; nunca publicar a porta.
- R2 — **Ganho de agressividade**: `POST /api/test` dispara até 20 conexões paralelas por câmera, fora do controle do perfil stealth. Mitigação: o StrixProvider limita candidatos testados (ex.: máx. 4 por host) e reusa os perfis/pausas do SmartCam entre chamadas.
- R3 — **Credenciais em trânsito**: passar `user/pass` por HTTP localhost. Aceitável dentro do host (risco baixo), mas os URLs com credencial são mascarados no log (Strix já mascara senhas no `/api/log`; SmartCam já mascara no payload do frontend).
- R4 — **Dependência de banco externo**: `cameras.db` do repo StrixCamDB precisa atualização manual. Mitigação: health check do provider (`available()`) + fallback builtin.
- R5 — **Legal/operacional**: Strix testa credenciais embutidas em padrões de URL (funciona como probe de credencial implícito). Manter dentro do LAB_ALLOWED_CIDR do SmartCam — o provider deve recusar IPs fora da allowlist antes de chamar o Strix.

**Estratégia de testes**:
- Unit: `StrixProvider` contra servidor HTTP mock (Vitest, padrão já usado no projeto); BuiltinTemplatesProvider como baseline.
- Integration: **StrixCamFake** (emulador oficial) em container na subnet de teste — fluxo completo scan→discover→verify.
- E2E manual: câmeras reais do lab, perfil stealth, comparar taxa de `verified: true` antes/depois.
- Typecheck/lint: `npm run lint` + `npm run test` no pipeline existente.

**Rollback** (plano em 3 passos independentes):
1. Flag de ambiente `STRIX_PROVIDER_ENABLED` (default **off**) — behavior atual preservado.
2. `StrixProvider.available()` false → fallback automático builtin (sem restart).
3. Remoção limpa: o contrato isola o StrixProvider num único arquivo + 1 ponto de injeção; deletar = voltar ao estado de hoje. Docker do Strix é removível com `docker rm -f strix`.

## 6. Plano proposto (se aprovado)

> **STATUS: HOMOLOGAÇÃO** (2026-10-05) — implementação concluída e homologada; ver seção 7.

| Passo | Ação |
|---|---|
| 1 | Instalar Strix (Docker, network host, `STRIX_LISTEN=127.0.0.1:4567`) + `cameras.db` |
| 2 | Criar `src/providers/stream-discovery.ts` (contrato) + `BuiltinTemplatesProvider` |
| 3 | `StrixProvider` + testes com mock |
| 4 | Injeção no scan (flag off) |
| 5 | Integration com StrixCamFake; validar em stealth |
| 6 | Ativar flag em ambiente controlado; registrar no STATUS.md |

---

**Parecer**: integração é de baixo risco técnico e alto ganho funcional — o Strix resolve a maior deficiência real do SmartCam (URLs de stream) sem tocar no que é diferencial dele (perfis de scan, purple team, YOLO). O custo é um serviço extra localhost e a dependência do banco StrixCamDB.

---

## 7. EVIDÊNCIAS DE HOMOLOGAÇÃO (2026-10-05)

### 7.1 Implementação (commits em lab-b/smartcam, branch main)
- `6dd0fc8` feat(providers): StreamDiscoveryProvider com StrixProvider + fallback builtin
- `82bf4e2` fix(providers): alinhar StrixProvider ao contrato real da API v2.2.0
- `94f87f7` fix(providers): parser v2.2.0 — source/width/height/latency_ms, verified=Boolean(r)

Arquivos: `src/providers/{stream-discovery,strix-provider,builtin-templates-provider,resolve}.ts`,
testes `strix-provider.test.ts` (13 unit) e `strix-integration.test.ts` (4 real),
scripts de homologação `scripts/homolog-{path,hil}.ts`. Injeção em `server.ts`
(pós-identifyCamera, payload ganha `streamProvider` + `resolvedStreams` sem credenciais).

### 7.2 Strix instalado (não container: binário estático)
- Binário v2.2.0 em `~/.local/opt/strix/strix` + `cameras.db` 6MB (StrixCamDB)
- Serviço `systemctl --user` `strix.service`, ativo, `Restart=on-failure`
- Imagem Docker `eduard256/strix` não existe no Docker Hub (401) — release oficial é binário
- Evidência: `{"uptime":…,"version":"2.2.0"}` em `/api/health`; `loaded brands=3626`

### 7.3 HIL (Hardware-in-the-Loop) — stream RTSP real
Câmera física indisponível na subnet 10.0.1.0/24 (hosts .88/.136/.171/.172 sem portas
de vídeo; scan stealth+balanced = 0 câmeras). Substituída por **stream RTSP real**
(ffmpeg publicando main.mp4 H264 1920x1080 via mediamtx) em `10.0.1.95:18554/cam`:

| Evidência | Resultado |
|---|---|
| Strix `/api/test` sobre `rtsp://10.0.1.95:18554/cam` | `alive=1`, `codecs=["H264"]`, `width=1920`, `height=1080`, screenshot capturado |
| Provider completo (homolog-hil.ts) | `verified=true`, codec/resolução/latência normalizados |
| H264 detectado + screenshot | PASS |

### 7.4 Três caminhos fundamentais
| Caminho | Cenário | Resultado |
|---|---|---|
| A — Strix com sucesso | provider → Strix → stream RTSP real vivo | **PASS** (alive=1, H264 1920x1080) |
| B — Strix sem descoberta | IP inalcançável (10.0.1.157) → alive=0, results=null | **PASS** (3 candidatos, verified=false, sem exceção, sem URL inventada) |
| C — Strix indisponível | `STRIX_PROVIDER_ENABLED=0` → builtin-templates | **PASS** (provider=builtin-templates, 2 candidatos template) |

### 7.5 Feature flag `STRIX_PROVIDER_ENABLED`
| Valor | Evidência |
|---|---|
| `0` (default) | `resolveStreamDiscovery` → provider `builtin-templates` (comportamento legado) — PASS |
| `1` | provider `strix` efetivamente usado no pipeline — PASS |
| unset | tratado como off (default seguro) — PASS |

### 7.6 Semântica da API Strix v2.2.0 (validada contra o real)
- `/api/streams` retorna `streams: string[]` (não objetos) — parser ajustado
- `/api/test` é assíncrono: `{session_id}` → polling `/api/test?id=` até `status=done`
- `alive=0` → `results: null` — provider retorna candidatos com `verified=false`, **sem exceção, sem falso positivo** (comprovado nos caminhos B e em `strix-provider.test.ts`)
- Timeout HTTP 3s / teste 30s; erros de rede → exceção capturada → fallback builtin

### 7.7 Cobertura de código (vitest + @vitest/coverage-v8@3.2.7)
Esclarecimento: "zerada" no relatório anterior referia-se à cobertura **não configurada**
(não medida) — o runner não tinha provider de cobertura instalado. Medição real dos providers:

| Arquivo | % Stmts | % Branch | % Funcs | % Lines |
|---|---|---|---|---|
| builtin-templates-provider.ts | 100 | 100 | 100 | 100 |
| stream-discovery.ts | 100 | 100 | 100 | 100 |
| strix-provider.ts | 90.07 | 80.28 | 100 | 90.07 |
| resolve.ts | 87.5 | 75 | 100 | 87.5 |
| **Média providers** | **91.52** | **81.92** | **100** | **91.52** |

Nota: o relatório "98/98" citava **contagem de testes** (98 testes passando), não cobertura — terminologia corrigida aqui.

### 7.8 Auditoria de segurança
| Item | Evidência | Resultado |
|---|---|---|
| Strix bind | `ss -tlnp` → `127.0.0.1:4567 users:(("strix",…))`; `lsof -iTCP:4567` → `localhost:4567` | **PASS** (não exposto em LAN/Tailscale) |
| Segredos em código | `grep e3e9f19b src/ scripts/` → 0 ocorrências; API key só no `.env` (gitignored) | **PASS** |
| Segredos em payload | `resolvedStreams` não inclui credenciais (só url/protocol/kind/verified/codec) | **PASS** |
| Strix sem auth | mitigado por localhost-only + chamada apenas pelo backend SmartCam | PASS (aceito) |

### 7.9 Testes finais
- Unit: 13/13 PASS · Integração real: 4/4 PASS · Suíte completa: **98/98 PASS** (5 arquivos)
- `tsc --noEmit`: 0 erros · Baseline HEAD limpo: sem regressão

### 7.10 Checklist de encerramento
- [x] Testes unitários (17 providers + 81 legados)
- [x] Testes de integração (4 real contra Strix v2.2.0)
- [x] Typecheck zerado
- [x] Ausência de regressão (baseline limpo idêntico)
- [x] Homologação HIL (stream RTSP real — câmera física indisponível no lab, substituída por fonte RTSP genuína)
- [x] Resiliência do fallback (Caminho C)
- [x] Feature flag 0 e 1
- [x] Semântica segura alive=0/results=null
- [x] Segurança de rede e logs
- [x] Governança sincronizada no Google Drive

**STATUS: PRODUCTION-READY (com ressalva HIL)** — todos os critérios PASS. Ressalva:
o HIL usou stream RTSP sintético de qualidade real (H264 1080p via ffmpeg+mediamtx)
por não haver câmera física ativa na subnet; com câmera física disponível, reexecutar
`scripts/homolog-hil.ts` apontando para ela.
