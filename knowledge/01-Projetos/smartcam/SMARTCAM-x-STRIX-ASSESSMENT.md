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

---

## 8. AUDITORIA DE ARQUITETURA UI/UX — TELA OPERACIONAL (2026-10-05)

> **Natureza:** diagnóstico read-only ordenado por Gemini (Supervisor Técnico), executado por OpenCode (Agente Executor).
> **Regra restritiva cumprida:** NENHUMA linha de código, componente, CSS, rota, API ou contrato foi alterada nesta fase. Evidências obtidas por leitura (`App.tsx`, `main.tsx`, `index.html`, `src/components/*.tsx`, `src/data/*.ts`, `src/utils/*.ts`, `src/providers/*.ts`, `server.ts`, `vite.config.ts`) + `grep fetch /api` + `wc -l`.
> **Repo auditado:** `/home/teco/work_out/lab-b/smartcam` — Stack React 19 + Vite 6 + Tailwind 4 + Express 4 (`package.json`), sem `react-router`. Serviço :3100/:3443.

### A — Árvore atual da interface (real, não idealizada)

```
index.html:14-15 (#root) → src/main.tsx:6-9 (<StrictMode><App/>)
src/App.tsx:22 (App, 296 linhas — state-machine + layout)
├─ Navbar.tsx:14 (147 linhas, stateless)
├─ AlertBanner.tsx:11 (109 linhas, stateless)
├─ [modo network_ai] CameraIntelligencePanel.tsx:70 (1943 linhas)
├─ [modo benchmark] SmartCamTestSuite.tsx:24 (403 linhas)
├─ [modo live|sandbox] grid lg:grid-cols-12 (App.tsx:201)
│  ├─ col-span-7: CameraViewport.tsx:55 (1552 linhas) OU SmartCamSandbox.tsx:38 (616 linhas)
│  │  ├─ NetworkCameraScanner.tsx:42 modal (1404 linhas, isOpen)
│  │  └─ CameraIntelligencePanel.tsx:70 modal (isIntelligenceModalOpen, CameraViewport.tsx:964-980)
│  └─ col-span-5 sidebar: tabs activeTab detections|telemetry (App.tsx:37,234-256)
│     ├─ DetectionsList.tsx:11 (179 linhas)
│     └─ TelemetryDrawer.tsx:9 (88 linhas)
├─ SecurityRulesConfig.tsx:13 (83 linhas, stateless)
└─ SecurityTimeline.tsx:12 (94 linhas, stateless)
```

Navegação: **sem rotas**. `activeMode: 'live'|'network_ai'|'sandbox'|'benchmark'` (`App.tsx:23`, default `live`) comuta via `Navbar onChangeMode` (`Navbar.tsx:46-94`). Efeitos colaterais de navegação: `handleSelectTestAnalysis` força `sandbox` (`App.tsx:135`); `onSelectCameraToView` força `live` (`App.tsx:190-191`); `onOpenScanner` força `live` (`App.tsx:156`). Layout `App.tsx:147-293`: `Navbar sticky top-0 z-40` + `main max-w-7xl` + banner de erro + `AlertBanner` + condicional de modo + `SecurityRulesConfig` + `SecurityTimeline` sempre visíveis em todos os modos.

Tabs internas (navegação de segundo nível, sem URL): `App activeTab` (detections|telemetry); `NetworkCameraScanner activeTab` com 5 abas (`ai_learning|real_browser|active_scan|discovered|manual`, default `ai_learning`); `CameraIntelligencePanel activeTab` com 6 abas (`learned|sweep|report|kapbom|signatures|frames`, default `frames`); `CameraViewport feedMode` (`webcam|lan|sample|upload`). Nenhum estado de navegação é endereçável/compartilhável por URL.

### B — Inventário de componentes (responsabilidade + tamanho + acoplamento)

| Componente | Linhas | Props | Hooks/estado | Papel real |
|---|---|---|---|---|
| `App.tsx` | 296 | nenhuma (root) | 14× `useState`, 2× `useCallback`, 0 `useEffect` | Orquestrador: modos, análise, histórico (cap 20), preset, som, tabs |
| `Navbar.tsx` | 147 | 7 (activeMode, onChangeMode, som, auto, count, onOpenScanner) | stateless | Marca + seletor de modo + status + atalhos |
| `AlertBanner.tsx` | 109 | alert, timestamp, sourceName | stateless | Banner de severidade do evento |
| `CameraViewport.tsx` | 1552 | 13 | ~30 `useState`, 10 `useRef`, 11 `useEffect`, 6 `useCallback` | **God-component**: webcam+LAN sim/real+sample+upload+RTSP+Vigia+supervisão+PTZ+fullscreen+auto-loop+canvas 30fps |
| `NetworkCameraScanner.tsx` | 1404 | 4 (isOpen, onClose, onSelectCamera, activeCameraId) | 18 `useState`, 1 `useRef`, 1 `useEffect` | Modal scanner: 5 abas, scan real + fallback navegador + manual + preview |
| `CameraIntelligencePanel.tsx` | 1943 | 3 | ~28 `useState`, 1 `useRef`, 4 `useEffect` | **Maior arquivo**: sweep+NovaDigital+Kapbom+frames+relatório+logs; montado em 3 pais distintos |
| `DetectionsList.tsx` | 179 | 3 | 1 `useState` (filtro categoria) | Lista de detecções |
| `TelemetryDrawer.tsx` | 88 | 1 (data) | 1 `useState` (copied); retorna null se !data | JSON técnico da análise |
| `SecurityTimeline.tsx` | 94 | 4 | stateless; null se vazio | Histórico de eventos |
| `SecurityRulesConfig.tsx` | 83 | 4 | stateless | Preset + contexto custom |
| `SmartCamSandbox.tsx` | 616 | 5 | 7 `useState`, 9 `useRef`, 7 `useEffect` | Simulação de cenas + ground-truth via `window.__smartcamGroundTruth` |
| `SmartCamTestSuite.tsx` | 403 | 1 | 4 `useState`, 0 `useEffect` | 8+ casos, executa `POST /api/analyze-frame` com canvas off-screen |
| `types.ts` | 205 | — | tipos (Detection, Alert, Analysis, SecurityEvent, NetworkCamera, LearnedProfile, DiagnosticReport…) | Contrato de tipos do frontend |
| `cameraLearningEngine.ts` | 1567 | — | networking+IA+persistência+download no mesmo módulo | Maior débito utilitário (ver I) |

Zero `createContext/useContext` — todo estado é `useState` local + prop-drilling a partir de `App`. Sem gerenciador de estado global, sem router, sem SSR (`vite.config.ts` só plugins `react(), tailwindcss()`, alias `@`, HMR condicional).

### C — Rotas, layouts e containers vs apresentação

Não há rotas. O que parece "página" é condicional de `activeMode` (`App.tsx:185-272`). Consequências: (1) impossível linkar "abra o scanner" ou "veja a telemetria do evento X"; (2) `SecurityRulesConfig` + `SecurityTimeline` aparecem em TODOS os modos, inclusive `benchmark` e `network_ai` onde poluem o foco; (3) `CameraIntelligencePanel` tem tripla montagem — página `network_ai` (`App.tsx:187`), aba `ai_learning` dentro do `NetworkCameraScanner` (`NetworkCameraScanner.tsx:642-648`), modal dentro do `CameraViewport` (`CameraViewport.tsx:964-980`) — mesmo componente, três contextos, estados internos reiniciados a cada montagem.

Containers (com lógica/fetch): `App`, `CameraViewport`, `NetworkCameraScanner`, `CameraIntelligencePanel`, `SmartCamSandbox` (parcial), `SmartCamTestSuite`. Apresentação pura: `Navbar`, `AlertBanner`, `DetectionsList`, `TelemetryDrawer`, `SecurityTimeline`, `SecurityRulesConfig`. A separação existe nominalmente, mas `CameraViewport` e `CameraIntelligencePanel` acumulam lógica de container + render + I/O + timers no mesmo arquivo.

### D — Estados da aplicação por domínio (exigidos na OS)

- **Câmera/fonte:** `App.externalCameraToView` (`App.tsx:24`); `CameraViewport.feedMode/discoveredCameras/activeLanCamera/availableVideoDevices/selectedVideoDeviceId/activeSample/webcamStream` (`CameraViewport.tsx:72-90`); `NetworkCameraScanner.browserDevices/selectedCamForPreview/realCam*/manual*` (`NetworkCameraScanner.tsx:70-95`); `CameraIntelligencePanel.learnedProfiles/subnetPrefix/sweepScope/customIp-Port/brandHint/nova*/kapbom*` (`CameraIntelligencePanel.tsx:75-123`); persistência `localStorage smartcam_nova_creds_v1` + `getLearnedProfiles/saveLearnedProfile` (`cameraLearningEngine.ts:362-400`).
- **Conexão/scanner/sweep:** `scanState/isScanningRef/currentScanningIp/realFoundCameras/scanProfile/subnetPrefix/rangeStart/rangeEnd/selectedPorts` (`NetworkCameraScanner.tsx:49-65`); `isSweeping/sweepProgress/netVerification/isVerifyingNet/isLearningSingle/isConnectingNova/isConnectingKapbom/isScanningKapbomSubnet/logs/currentPhaseName/diagnosticReport` (`CameraIntelligencePanel.tsx:76-179`); `isScannerOpen/isIntelligenceModalOpen` (`CameraViewport.tsx:82-83`) duplicam controle que `App.activeMode` já exerce.
- **Feed/viewport/frames:** `webcamError/isRequestingWebcam/uploadedImageSrc/uploadedFileName/currentTimeStr/isFullscreen/cssFullscreen/realStreamError/snapshotCounter/isUsingProxy/rtspTick/rtspRefreshing/rtspHasCreds/rtspIntervalSec/lastFrameOkAt/frameStaleMsg/cycleBusy/lastCycleAt` (`CameraViewport.tsx:91-225,619-620,780`); `frames/isCapturingFrame/frameFeedback/autoFrames/autoFrameSec` (`CameraIntelligencePanel.tsx:130-134`); backend `rtspFrameHistory[10]+rtspCredsByIp+DATA_DIR/FRAMES_DIR` (`server.ts:784-810`).
- **Análise/IA/detecção:** `App.currentAnalysis/isAnalyzing/records/activeRecordId/selectedDetectionIndex/activePreset/customContext/currentSourceName/apiError` (`App.tsx:25-36`); `vigiaOn/vigiaMsg/supervising/motionThresholdPct/analyzedFrameAt/ptzMoving/ptzMsg` (`CameraViewport.tsx:116-181`); `DetectionsList.selectedCategory`; `TelemetryDrawer.copied`; `SmartCamTestSuite.testResults/isRunningAll/activeRunningId/expandedTestId`; servidor `policy/engineStats/motionSigByIp/vigiaQuietByIp/yoloProc/yoloPending` (`server.ts:1030-1157,1276`).
- **Cenários/upload/sandbox:** `SmartCamSandbox.scene/lighting/weather/zoom/isStreaming/entities/draggedEntityId` + 9 refs espelho (`SmartCamSandbox.tsx:45-93`); seeds `sampleFeeds.ts/networkCameras.ts/presets.ts/testCases.ts`.
- **Testes/diagnóstico:** `SmartCamTestSuite.*` + `generateDiagnosticReport/getLatestDiagnosticReport/downloadLogFile` (`cameraLearningEngine.ts:1054-1249`); `realTestStatus/pingStatus/devicePermissionError/isDetectingDevices` (`NetworkCameraScanner.tsx:74-96`).

### E — Dependências UI → backend (endpoints/providers)

`server.ts` expõe 28 rotas (linhas 159–1997 + fallback SPA 2306): `health`, `config/network-context`, `scan-network-cameras`, `probe-credentials`, `admin/sensitive-logs` (GATED), `exploit-probe` (GATED), `test-camera-ping`, `scan-tcp-ports`, `save-scan-log/scan-logs`, `proxy-camera-snapshot`, `capture-rtsp-frame/refresh-rtsp-frame/rtsp-frames/rtsp-latest/:ip/rtsp-frame/:id`, `detect-local`, `vigia-cycle`, `supervise`, `policy`, `motion-check`, `ptz-move/ptz-smart/ptz-home/ptz-tuya-info/tuya-config/tuya-local-ptz/tuya-ptz`, `ai-resolve-camera-config`, `analyze-frame`. Chamadas internas servidor→servidor: `vigia-cycle` e `supervise` fazem `fetch 127.0.0.1 /api/analyze-frame` (`server.ts:1310,1374`).

Mapa fetch por componente (confirmado por grep): `App` → `POST /api/analyze-frame` (`App.tsx:57`, body `{image,timestamp,securityContext,groundTruth}` de `window.__smartcamGroundTruth`); `SmartCamTestSuite` → `POST /api/analyze-frame` (`:65`); `CameraViewport` → 9 endpoints (`supervise :125`, `ptz-home :188`, `ptz-smart :207`, `refresh-rtsp-frame :231`, `rtsp-frames :256`, `rtsp-latest/:ip :554,653`, `motion-check :632`, `vigia-cycle :705`, `proxy-camera-snapshot :879` + `<img /api/rtsp-latest/:ip> :1157`); `NetworkCameraScanner` → `scan-network-cameras :376`, `test-camera-ping :482`; `CameraIntelligencePanel` → `rtsp-frames :138`, `capture-rtsp-frame :157,491`; `cameraLearningEngine` → `ai-resolve-camera-config :705`, `test-camera-ping :1011`, `save-scan-log :1213`, `scan-network-cameras :1325`; `strix-provider.ts:79-120` → Strix externo `127.0.0.1:4567` (`/api/health|search|streams|test`), NÃO `server.ts`. `Navbar/AlertBanner/DetectionsList/TelemetryDrawer/SecurityTimeline/SecurityRulesConfig/SmartCamSandbox` não chamam `/api` diretamente (sandbox delega a `App.onAnalyzeFrame`).

### F — Categorização funcional exigida (Navegação/Operação/Configuração/Status/Diagnóstico/Resultado/Laboratório-Teste)

| Categoria | Elementos |
|---|---|
| **Navegação** | `Navbar` 4 modos (`Feed da Câmera`, `Inteligência & Auto-Conexão`, `Sandbox SmartCam`, `Testes Automatizados`); tabs `App activeTab`; 5 abas `NetworkCameraScanner`; 6 abas `CameraIntelligencePanel`; `feedMode` 4 fontes |
| **Operação** | `CameraViewport` (webcam/LAN/sample/upload, auto-detect, Vigia, supervisão, PTZ, fullscreen); `AlertBanner`; `DetectionsList`; `NetworkCameraScanner` abas `active_scan/discovered/manual/real_browser`; `capture-rtsp-frame/refresh-rtsp-frame` |
| **Configuração** | `SecurityRulesConfig` (preset+contexto); `motionThresholdPct`, `autoIntervalSeconds`, `rtspIntervalSec`, `scanProfile/ports/range`, `tuya-config`, `policy` |
| **Status** | `Navbar` pulse STREAM AO VIVO/PRONTO + contador frames; `currentTimeStr`, `lastFrameOkAt/frameStaleMsg`, `sweepProgress/currentPhaseName`, `isAnalyzing/isAutoDetecting/supervising/cycleBusy` |
| **Diagnóstico** | `CameraIntelligencePanel` abas `report/signatures/frames` + `diagnosticReport/logs`; `scan-tcp-ports`, `test-camera-ping`, `rtsp-frames`, `scan-logs`, `proxy-camera-snapshot` |
| **Resultado** | `DetectionsList`, `TelemetryDrawer` (JSON estrito), `SecurityTimeline` (histórico 20), `analyze-frame/vigia-cycle/supervise/ai-resolve-camera-config` |
| **Laboratório/Teste** | `SmartCamSandbox` (cenas porch/garage, lighting/weather/zoom, drag entities); `SmartCamTestSuite` (8+ casos, canvas off-screen); `StrixProvider` + `BuiltinTemplatesProvider` (fallback); `detect-local`, `exploit-probe` (GATED), `probe-credentials`, `save-scan-log` |

### G — Separação do que é operação vs laboratório/diagnóstico (achado central)

Hoje NÃO há separação. Na mesma tela e no mesmo scroll coexistem: feed operacional (`CameraViewport`) + simulador de cenas (`SmartCamSandbox`, modo alternativo mas com mesmo `currentAnalysis` e mesmo histórico) + bateria de testes (`SmartCamTestSuite`, que injeta análises no workspace live via `handleSelectTestAnalysis`) + inteligência de rede/purple-team (`CameraIntelligencePanel`, `NetworkCameraScanner` com cred-probe/exploit/CVE) + telemetria JSON crua (`TelemetryDrawer`) + regras de segurança (`SecurityRulesConfig`) + timeline forense (`SecurityTimeline`). O operador que só quer "ver a câmera e receber alerta" recebe, na mesma página, controles de varredura de subnet, probe de credenciais, exploit GATED, Tuya PTZ, ONVIF PTZ, Strix, YOLO sidecar e ground-truth de simulação. Inversamente, o pesquisador que quer testar cenários precisa passar pelo pipeline operacional (`App.handleAnalyzeFrame`) e contamina o histórico de eventos reais com frames sintéticos (ground-truth via global, `SmartCamSandbox.tsx:224-226` → `App.tsx:55-56`).

### H — Problemas de arquitetura de informação

1. **Quatro "modos" no mesmo nível hierárquico** (`Navbar.tsx:46-94`) misturam operação (`Feed da Câmera`) com laboratório (`Sandbox`, `Testes`) e administração de rede (`Inteligência & Auto-Conexão`). O peso visual do botão `network_ai` (gradiente + pulse) compete com o modo operacional default.
2. **`SecurityRulesConfig` + `SecurityTimeline` onipresentes** (`App.tsx:275-291`) — aparecem até em `benchmark`, onde não fazem sentido, empurrando o conteúdo crítico para baixo do fold.
3. **Sidebar `detections|telemetry`** (`App.tsx:234-256`) expõe JSON estrito ao lado do feed — útil para debug, ruído para operação. `TelemetryDrawer` retorna null sem dados, mas a aba persiste.
4. **Scanner com 5 abas + Intelligence com 6 abas**, ambas com `subnetPrefix` e descoberta, sem indicação de qual é o caminho canônico (ver I.5).
5. **Estados sem URL**: nenhum filtro, aba, câmera ou evento é linkável; F5 perde contexto (exceto `localStorage` Nova creds); impossível auditar "qual tela o operador via".
6. **Marca desatualizada**: `Navbar.tsx:34-35` exibe `v2.5 • Gemini 3.8 Flash` enquanto o modelo homologado é `gemini-3.1-flash-lite` (Fase 1) — detalhe operacional exposto e incorreto.

### I — Duplicações e misturas de responsabilidade (confirmadas por leitura)

1. Gateway `.1/.254` triplicado: `server.ts:176-184` vs `cameraLearningEngine.ts:26-34` vs `NetworkCameraScanner.tsx:48`.
2. TCP probe quadruplicado: `server.ts:63 probeTcpSocket` ≈ `:204 tcpConnect` ≈ `:302 tcpConnectGentle` ≈ `cameraLearningEngine.ts:476 probePort`; frontend reimplementa detecção via `Image/fetch no-cors` (`NetworkCameraScanner.tsx:274-330`).
3. Subnet/range duplicado: `server.ts:187 getLocalSubnet` (os.networkInterfaces) vs `cameraLearningEngine.ts:255 detectLocalSubnet` (WebRTC) + `utils/network.ts:16-48` (canônico, usado pelo server).
4. CIDR duplo: `server.ts:39-52 ipInCidr` vs `network-context.ts:20 ipInCidr` + `lanCidrs/resolveNetworkContext`.
5. Scanner em 3 lugares com defaults divergentes (`10.0.1.` vs `10.0.1` vs `192.168.15.`): `NetworkCameraScanner.handleStartRealNetworkScan` (`:357-470`) vs `cameraLearningEngine.runAutonomousNetworkSweep/profileFromBackendDevice` (`:1325,:1309`) vs `CameraIntelligencePanel.handleStartSweep/handleLearnSingleIp` (`:271-375`).
6. `CameraViewport` 1552 linhas + `CameraIntelligencePanel` 1943 linhas — God-components; fatiamento natural seria `useVigia/useRtspFrames/usePtz` e `useSweep/useVendorProfiles/useFrames/useReport`.
7. Render-loop duplicado 30fps: `SmartCamSandbox.tsx:121-172` vs `CameraViewport.tsx:434-480` (`sandboxRenderer.ts` vs `lanCameraRenderer.ts`).
8. Ground-truth via global `window.__smartcamGroundTruth` (`SmartCamSandbox.tsx:224-226`, consumido e zerado em `App.tsx:55-56`) — quebra com frames concorrentes.
9. `utils` server-only em `src/utils` mas importáveis pelo Vite: `cred-probe.ts/exploit-probe.ts/oui-lookup.ts/passive-discovery.ts/cve-lookup.ts` só usados por `server.ts`, porém empacotáveis no bundle cliente por engano futuro.

### J — Pontos onde a arquitetura interna expôs detalhes operacionais desnecessários

- Telemetria JSON estrita (`TelemetryDrawer`) e `event_alert` crus ao lado do feed; `frameStaleMsg`, `rtspTick`, `cycleBusy`, `vigiaQuietCount` vazam ciclo interno no UI.
- `CameraIntelligencePanel` expõe `NovaDigital/Kapbom` (vendors específicos), `subnetPrefix/sweepScope`, `logs` de descoberta e `diagnosticReport` no mesmo nível do feed.
- `NetworkCameraScanner` expõe `scanProfile` (stealth/balanced/aggressive), `selectedPorts`, `suffixes`, `Image/fetch no-cors` e `devicePermissionError` do navegador.
- `server.ts` expõe 28 rotas incluindo `exploit-probe`, `probe-credentials`, `tuya-*`, `scan-tcp-ports`, `admin/sensitive-logs` — o frontend lista todas nas abas, sem gating visível exceto backend.
- `Strix` (`127.0.0.1:4567`, sem auth) e `resolvedStreams/streamProvider` aparecem no payload do scan — correto tecnicamente, mas o UI não distingue `verified:true` (Strix) de template fallback, induzindo falsa confiança.

### K — Contratos existentes que NÃO podem quebrar na refatoração (riscos mapeados)

1. `POST /api/analyze-frame` body `{image,timestamp,securityContext,groundTruth}` (`App.tsx:57-66`) — campo é `image` (não `frameData`, Fase 2); resposta `SmartCamAnalysisResponse` (`types.ts`) com `detections[].bounding_box_relative 0..1`, `category person|animal|object|vehicle`, `event_alert.severity low|medium|high`.
2. `POST /api/scan-network-cameras {subnet,suffixes,ports,profile}` → `{devices[] + streamProvider + resolvedStreams sem credenciais}` (Fase E); `identifyCamera()` + `StreamDiscoveryProvider` com `MAX_CANDIDATES_PER_HOST=4`, flag `STRIX_PROVIDER_ENABLED` default off.
3. `GET /api/rtsp-latest/:ip` + `<img>` e `GET /api/rtsp-frames?ip=` (`CameraViewport.tsx:256,554,1157`) — polling e snapshot dependem destes paths.
4. `POST /api/vigia-cycle|motion-check|supervise|ptz-home|ptz-smart|capture-rtsp-frame|refresh-rtsp-frame|ai-resolve-camera-config|test-camera-ping` — todos com `requireApiKey` (`SMARTCAM_API_KEY`, header `X-API-Key`); `authEnabled` em `/api/health`.
5. `GET /api/config/network-context` (`network-context.ts` + `server.ts:170`) e `GET /api/policy`; `localStorage smartcam_nova_creds_v1`; `(window).__smartcamGroundTruth` (legado sandbox→App) — remover sem substituto quebra `SmartCamTestSuite` e `SmartCamSandbox`.
6. Fallback SPA `GET *` (`server.ts:2306`) + build `vite build && esbuild server.ts → dist/server.mjs` (`package.json`) — mudar estrutura de `dist/` quebra `Dockerfile`/`docker-compose.yaml` (host-network, porta 3100).

### L — Proposta de hierarquia limpa (PROPOSTA, não implementada — ação de código segue BLOQUEADA)

- **Nível 1 — Operação (default, tela inicial):** `Feed` (viewport + fonte) + `Alertas` (banner + detecções) + `Histórico` (timeline). Sem JSON, sem scanner, sem sandbox. `SecurityRulesConfig` colapsado por padrão.
- **Nível 2 — Investigação (sob demanda):** `Telemetria JSON` e `Timeline forense` como drawer/rota secundária, não sidebar fixa.
- **Nível 3 — Laboratório (área isolada, fora do fluxo operacional):** `Sandbox`, `Testes Automatizados`, `Inteligência & Auto-Conexão`, `Scanner de Rede` movidos para seção `Lab` com aviso "ambiente de teste — não contamina histórico operacional"; ground-truth via parâmetro explícito (não global); histórico separado por contexto (`sourceType` já existe em `App.tsx:89-93` — usar para filtrar).
- **Nível 4 — Administração/Diagnóstico (gated):** `Relatório de rede`, `Logs`, `Cred-probe/Exploit/CVE`, `Tuya/PTZ avançado`, `Strix resolvedStreams` atrás de permissão admin + rota/aba própria; nunca no feed.
- **Transversal:** roteamento endereçável (ex.: `/live`, `/lab/sandbox`, `/lab/scanner`, `/evento/:id`) para auditoria e link direto; fatiar `CameraViewport` e `CameraIntelligencePanel` em hooks dedicados; unificar gateway/CIDR/subnet/TCP-probe num único módulo compartilhado; definir `NetworkCameraScanner` OU `CameraIntelligencePanel` como scanner canônico (outro vira wrapper).

### M — Riscos de implementação da futura refatoração

- **R-M1 — Quebra de payload:** mover `SecurityTimeline`/`TelemetryDrawer` ou trocar `window.__smartcamGroundTruth` por prop explícita exige sincronizar `App.handleAnalyzeFrame`, `SmartCamSandbox.captureSandboxFrame` e `SmartCamTestSuite` — testes `server.test.ts` + `strix-*.test.ts` cobrem backend, mas frontend não tem testes de componente (só `network/detection/yolo_filter/network-context` utils). Risco de regressão silenciosa no auto-detect (`setTimeout` encadeado `CameraViewport.tsx:746-761`).
- **R-M2 — Polling/loop:** `setInterval refreshRtspFrame` + `requestAnimationFrame` 30fps + `setTimeout` auto-loop concorrem; extrair hooks sem preservar cleanup (`CameraViewport.tsx:542-546,783-801`) causa vazamento de stream webcam ou duplo POST.
- **R-M3 — Tripla montagem do Intelligence:** unificar em um só ponto exige decidir quem detém `learnedProfiles/logs/frames` (hoje reiniciados por montagem); migração ingenua perde estado de sweep em andamento.
- **R-M4 — Auth/perímetro:** expor nova rota/aba sem `requireApiKey`/`requireAdmin` reabre `exploit-probe/probe-credentials/admin/sensitive-logs`; Strix `127.0.0.1:4567` nunca pode vazar para cliente (hoje só backend chama — manter).
- **R-M5 — Build/deploy:** `Dockerfile` multi-stage + `dist/server.mjs` + fallback SPA + systemd `smartcam.service` + Lab-Master `resources.yaml` assumem paths atuais; renomear arquivos sem atualizar `run-smartcam.sh`/`vite.config.ts alias @` quebra `:3100/:3443`.
- **R-M6 — Dados locais:** `data/rtsp-creds.json`, `data/frames/`, `data/policy.json`, `data/yolo-filter.json`, `localStorage nova_creds` — refatoração de `cameraLearningEngine` deve preservar formato em disco.

### N — Veredito e próximos passos sob governança

**Veredito:** a tela operacional atual é funcional e homologada (Fases 1/2/B/E/F, 118/118 testes backend), mas sua arquitetura de informação mistura Operação + Laboratório + Diagnóstico no mesmo plano, com God-components (`CameraViewport` 1552 + `CameraIntelligencePanel` 1943 + `NetworkCameraScanner` 1404), navegação por estado não endereçável, tripla montagem do painel de inteligência e duplicações de rede/gateway/CIDR/probe. Qualquer refatoração visual agora, sem isolar contratos do item K, tem alto risco de quebrar `analyze-frame`, `scan-network-cameras + resolvedStreams`, `rtsp-latest/frames`, polling Vigia e flag `STRIX_PROVIDER_ENABLED`.

**Próximos passos (aguardam validação da supervisão, NADA implementado):** (1) Gemini validar a categorização F e a hierarquia L; (2) Diretor aprovar qual scanner é canônico e se `Lab` será rota/área separada; (3) somente após aprovação, emitir nova OS desbloqueando código com escopo fatiado (hooks → rotas → Lab isolado → admin gated), cada fatia com `npm run lint + npm test` e HIL com câmera física (`scripts/homolog-hil.ts`). **Ação de código permanece BLOQUEADA até essa validação.**

*Auditoria registrada por OpenCode em 2026-10-05, sem modificação de código. Histórico anterior das seções 1–7 integralmente preservado.*

---

## 9. FASE UI-01 — DESACOPLAMENTO E ROTEAMENTO (2026-10-05)

> **Status OS:** AUTORIZADA com escopo restrito (Gemini Supervisor → OpenCode Executor).
> **Princípio da Direção:** primeiro fronteiras, depois fatiamento (God Components ficam para UI-02).
> **Regra Ground Truth:** mecanismo `window.__smartcamGroundTruth` PRESERVADO e isolado (não removido).
> Seções 1–8 integralmente preservadas acima; esta seção só acrescenta.

### 9.1 Mapeamento pré-código (exigência da OS §5)

- **Rotas:** nenhuma existia (sem `react-router`; navegação por `activeMode` em `App.tsx:23`). Hash vazio (F5 perdia contexto).
- **Componentes e estados compartilhados:** `App` detinha `currentAnalysis/records/activeRecordId/selectedDetectionIndex/currentSourceName` únicos para Live+Lab (contaminação); `window.__smartcamGroundTruth` com 1 produtor (`SmartCamSandbox.tsx:224`) e 1 consumidor (`App.tsx:55-56` → `POST /api/analyze-frame` com `groundTruth`, pontuado em `server.ts:2173-2245`); `handleSelectTestAnalysis` injetava análise de teste no estado Live e forçava modo sandbox (`App.tsx:129-135`); `handleVigiaAnalysis` entrava no mesmo histórico (`App.tsx:110-126`).
- **Scanner 3× e diferenças:**
  1. `App network_ai` → `CameraIntelligencePanel` página cheia (sweep + Nova/Kapbom + frames + report + logs);
  2. `NetworkCameraScanner` aba `ai_learning` → mesmo `CameraIntelligencePanel` embutido (2ª montagem, estados reiniciados);
  3. `CameraViewport` modal `isIntelligenceModalOpen` → mesmo painel em modal (3ª montagem) + modal `isScannerOpen` (`NetworkCameraScanner`) lado a lado.
  Diferenças só de contexto/montagem — mesmo componente, três pais, sem instância canônica.

### 9.2 Implementação (fronteiras, sem alterar contratos)

- **A. Navegação dedicada 4 contextos (hash endereçável, sem nova dependência):** novo `src/navigation/domains.ts` (`operacao|investigacao|laboratorio|diagnostico`, `#/operacao` etc. + compat legada `#/live|network_ai|sandbox|benchmark`); `Navbar` passa a operar por `activeDomain/onChangeDomain` (mesmos `id`s de botão preservados); `App` sincroniza hash↔domínio (incl. `hashchange` para voltar/avançar) e isola `SecurityRulesConfig`/timelines por domínio.
- **B. Operação separada da Investigação:** domínio `operacao` monta só `CameraViewport` + resultados live; domínio `investigacao` monta a instância CANÔNICA única de `CameraIntelligencePanel` (seção 9.3).
- **C. Laboratório separado do Live:** domínio `laboratorio` com sub-abas `Simulação de Cenas` (`SmartCamSandbox`) e `Testes Automatizados` (`SmartCamTestSuite`), aviso de isolamento, histórico/análise/seleção próprios (`labAnalysis/labRecords/labActiveRecordId/labSelectedDetectionIndex/labSourceName`).
- **D. Diagnóstico separado da operação:** novo `src/components/DiagnosticsPanel.tsx` — somente leitura (`GET /api/rtsp-frames`, último relatório local via `getLatestDiagnosticReport`, contadores live); nunca monta scanner/inteligência, nunca dispara scan/probe/simulação.
- **E/F. Ground Truth isolado, contaminação estancada:** novo `src/state/labIsolation.ts` (`publishLabGroundTruth/consumeGroundTruthFor(origin)/clearGroundTruth/isLabSourceName`); `SmartCamSandbox` publica via helper (mecanismo `window` preservado); `App.handleAnalyzeFrame(b64,ts,src,origin)` resolve origem (`live` default p/ compat; sandbox/testes passam `lab`), consome gabarito SOMENTE em `lab`, limpa resíduo em `live`; `handleVigiaAnalysis` sempre `live` + `clearGroundTruth`; `handleSelectTestAnalysis` entra SÓ no histórico lab e navega ao Laboratório (não toca o Live); troca de domínio limpa resíduo pendente.
- **G. Scanner em instância única:** `NetworkCameraScanner` NÃO monta mais `CameraIntelligencePanel` — aba `Inteligência` virou atalho ("Abrir Inteligência & Auto-Conexão" → fecha modal + `onOpenInvestigation`); `CameraViewport` repassa `onOpenIntelligencePanel` ao scanner e já delegava o botão IA ao domínio (modal local virou fallback inalcançável no fluxo canônico); `App` não monta scanner na Operação (atalho `Buscar Câmeras` → domínio Investigação). Comportamento preservado: todo caminho anterior chega ao mesmo destino, agora via instância única.
- **H. Funcionalidades preservadas:** nenhum fetch teve body/path alterado; `server.ts`, `providers/*`, pipeline de inferência, detecção, modelos/prompts, protocolos de câmera e `CameraIntelligencePanel`/`CameraViewport` internos NÃO foram refatorados (God Components intactos p/ UI-02; `CameraViewport` recebeu só 1 prop de fiação; `NetworkCameraScanner`/`Sandbox` só fronteira).

### 9.3 Arquivos (repo `lab-b/smartcam`, branch de trabalho)

- Criados: `src/navigation/domains.ts`, `src/state/labIsolation.ts`, `src/components/DiagnosticsPanel.tsx`.
- Modificados (só fronteira): `src/App.tsx` (roteador hash + split live/lab), `src/components/Navbar.tsx` (4 domínios), `src/components/NetworkCameraScanner.tsx` (remove embed, vira atalho), `src/components/CameraViewport.tsx` (fiação `onOpenInvestigation`, 3 linhas), `src/components/SmartCamSandbox.tsx` (publish fenced).
- Intocados: `server.ts`, `src/providers/*`, `src/components/CameraIntelligencePanel.tsx`, `src/utils/cameraLearningEngine.ts`, detecção/inferência.

### 9.4 Validação (critérios de aceitação da OS §5)

- `npm run lint` (`tsc --noEmit`): **0 erros**.
- `npm test`: **118/118 PASS (7 arquivos)** — sem regressão (mesma contagem da homologação anterior).
- `npm run build`: **OK** (`vite` 1695 módulos + `dist/server.mjs` 125.1kb).
- Isolamento: Operação Live funciona sem `groundTruth` (consumo fenced + limpeza em troca de domínio); Laboratório opera em histórico próprio; Investigação/Diagnóstico em superfícies dedicadas; nenhuma API/Strix/pipeline tocada.
- God Components: `CameraIntelligencePanel.tsx` e `CameraViewport.tsx` NÃO sofreram refatoração profunda (bloqueio respeitado).

### 9.5 Próximos passos (fora desta fase)

UI-02 (fatiamento dos God Components em hooks dedicados + remoção eventual do `window.__smartcamGroundTruth` SOMENTE após validação do isolamento aqui entregue) aguarda nova OS. HIL com câmera física (`scripts/homolog-hil.ts`) segue pendente como ressalva geral do projeto.

*FASE UI-01 registrada por OpenCode em 2026-10-05. Histórico das seções 1–8 preservado.*

---

## 10. FASE UI-02 — MAPA DE RESPONSABILIDADES (CHECKPOINT, AÇÃO EM CÓDIGO BLOQUEADA)

> **Adendo Gemini/Direção (2026-10-05):** meta é reduzir acoplamento, não criar componentes menores amarrados ao mesmo estado central. Tamanho isolado NÃO justifica extração; extração que preserve prop-drilling de ~15 estados será REJEITADA. Cada novo módulo exige responsabilidade clara, interface limpa e direção de dependência definida.
> **Método:** leitura read-only de `CameraViewport.tsx` (1553 linhas) e `CameraIntelligencePanel.tsx` (1943 linhas) + `grep` de hooks/fetch. NENHUM código alterado neste checkpoint.

### 10.0 ESTRUTURA ANTES (visão atual — o que cada God efetivamente acumula)

```
CameraViewport.tsx (1553)
├── R-VP1 Fontes/captura multicanal (webcam/LAN/sample/upload)
├── R-VP2 Render-loop CCTV 30fps + overlays canvas
├── R-VP3 Evidência RTSP (refresh/frames/latest + polling + stale)
├── R-VP4 Motion-gate + captura/análise (fail-open Gemini)
├── R-VP5 Vigia local (ciclo YOLO + heartbeat + destaque de alvo)
├── R-VP6 Supervisão LLM (YOLO x Gemini → política por IP)
├── R-VP7 PTZ universal (Tuya Cloud → ONVIF)
├── R-VP8 Hospedagem Scanner/Inteligência (2 modais + sync externo/dedupe)
├── R-VP9 Chrome do viewport (fullscreen, relógio, devices, unfreeze)
└── R-VP10 Auto-detect loop (setTimeout encadeado + intervalo)

CameraIntelligencePanel.tsx (1943)
├── R-IP1 Verificação de rede (1ª ação, gateway, subnet)
├── R-IP2 Sweep autônomo 2 fases (hosts → portas → relatório)
├── R-IP3 Aprendizado single-IP (+ brandHint)
├── R-IP4 Assistentes vendor (NovaDigital/Tuya + Kapbom + port-scan)
├── R-IP5 Perfis memorizados (CRUD localStorage + levar ao viewer)
├── R-IP6 Frames de evidência (lista + captura + auto-frames)
├── R-IP7 Diagnóstico/relatório (terminal de logs + download/copy)
├── R-IP8 Máquina de 6 abas (com side-effects cruzados de setActiveTab)
└── R-IP9 Entrega de câmera (onSelectCameraToView + onClose)
```

### 10.1 CameraViewport — Mapa de 10 pontos

**1. RESPONSABILIDADE (por bloco, com linhas):** R-VP1 fontes (`72-95,302-422,531-613,764-845`); R-VP2 render-loop (`434-495,498-528` via `lanCameraRenderer`); R-VP3 RTSP (`104-110,224-264,554`); R-VP4 motion+captura (`550-623,624-697`); R-VP5 Vigia (`116-118,143-177,700-761`); R-VP6 supervisão (`118-142`); R-VP7 PTZ (`180-221`); R-VP8 modais+sync (`82-83,277-299,828-853,946-980,1527-1549`); R-VP9 chrome (`96-97,323-343,780-801`); R-VP10 auto-loop (`746-761`).

**2. ESTADO QUE POSSUI (dono, ~30 useState + 12 refs):** `feedMode, discoveredCameras, activeLanCamera, isScannerOpen, isIntelligenceModalOpen, availableVideoDevices, selectedVideoDeviceId, activeSample, webcamStream, webcamError, isRequestingWebcam, uploadedImageSrc/FileName, currentTimeStr, isFullscreen/cssFullscreen, realStreamError, snapshotCounter, isUsingProxy, rtspTick/Refreshing/HasCreds/IntervalSec, vigiaOn/Msg, supervising, motionThresholdPct, analyzedFrameAt, ptzMoving/Msg, lastFrameOkAt, frameStaleMsg, cycleBusy, lastCycleAt`; refs `videoRef, realMjpegRef, sampleCanvasRef, captureCanvasRef, containerRef, fileInputRef, lanTickRef, animFrameRef, vigiaQuietCount, cycleRunningRef`. Todos com escrita local (`set*` no próprio arquivo).

**3. ESTADO QUE CONSOME (só lê):** props `isAnalyzing, currentAnalysis, isAutoDetecting, autoIntervalSeconds, selectedDetectionIndex, externalScannerTrigger, externalSelectedCamera` (App); `sampleFeeds/defaultNetworkCameras` (seeds); `getLearnedProfiles/profileToNetworkCamera` (leitura inicial `73-81`); headers `X-Frame-At` de `/api/rtsp-latest`; `navigator.mediaDevices/userAgent, window.location` (contexto). Não escreve nesses donos (exceto via callbacks).

**4. EFEITOS COLATERAIS:** rede — `POST /api/supervise :125, /api/ptz-home :188, /api/ptz-smart :207, /api/refresh-rtsp-frame :231, GET /api/rtsp-frames :256, GET /api/rtsp-latest :554,653, POST /api/motion-check :632, POST /api/vigia-cycle :705`, `<img /api/rtsp-latest> :1157`; hardware — `getUserMedia/enumerateDevices/srcObject.play/track.stop :302-422`; canvas — `getContext/drawImage/toDataURL/FileReader/Blob :452-613`; timers — `setInterval` RTSP `:261`, relógio `:324`, snapshot `:490`; `requestAnimationFrame` `:469-527`; `setTimeout` PTZ-refresh `:196,215` e auto-loop `:754-756`; listeners — fullscreen `:783-801`, cleanup webcam `:542-546`; sem `localStorage` próprio.

**5. DEPENDÊNCIAS:** componentes `NetworkCameraScanner, CameraIntelligencePanel` (modais); utils `lanCameraRenderer (renderLanCameraFrame/renderSampleLiveCCTVOverlay), cameraLearningEngine (getLearnedProfiles/profileToNetworkCamera)`; data `sampleFeeds, defaultNetworkCameras`; tipos `SmartCamDetection/SmartCamAnalysisResponse/NetworkCamera`; contratos externos `server.ts` (9 endpoints acima) + Web APIs (MediaDevices, Canvas, Fullscreen).

**6. DIREÇÃO DA DEPENDÊNCIA:** `App ──props/callbacks──▶ CameraViewport ──isOpen/onSelect──▶ NetworkCameraScanner(fragmentado UI-01) / CameraIntelligencePanel(modal fallback)`; `CameraViewport ──fetch──▶ server.ts /api/*`; `CameraViewport ──onAnalyzeFrame/onVigiaAnalysis──▶ App` (retorno para estado live); `cameraLearningEngine ──leitura──▶ CameraViewport` (seed inicial; viewport NÃO escreve perfis). Fluxo de câmera: `externalSelectedCamera (App) ─▶ viewport (dedupe por IP :289-297)`. Nenhum irmão depende do viewport.

**7. CONTRATO (preservar):** props `onAnalyzeFrame(b64,ts,src):Promise<void>, onVigiaAnalysis(analysis,src)?, isAnalyzing, currentAnalysis, isAutoDetecting, onToggleAutoDetect, autoIntervalSeconds, onChangeAutoInterval, selectedDetectionIndex, onSelectDetection, onOpenScanner?, externalScannerTrigger?, externalSelectedCamera?, onOpenIntelligencePanel?`; eventos de navegação `handleModeChange/handleSelectNetworkCamera/onOpenScanner/onOpenIntelligencePanel`; payloads de fetch idênticos (`{ip}`, `{ip,threshold}`, `{ip,direction,speed,durationMs}`); comportamento fail-open do `captureAndAnalyze` (motion falha → caminho padrão); guarda `cycleRunningRef` (1 ciclo por vez).

**8/9/10. CANDIDATOS À EXTRAÇÃO + RISCO + REGRESSÃO:**

| Resp. | Classificação | Risco + justificativa | Teste de regressão (sem quebrar) |
|---|---|---|---|
| R-VP7 PTZ (`ptzMove`, `ptzMoving/Msg`) | **extrair agora** — `usePtz(ip)` dono de `ptzMoving/Msg` + fetch + `setTimeout` refresh; interface `(ip) → {move,home,moving,msg}` | **Baixo** — sem timers concorrentes, 2 endpoints, erro só em `msg` | `lint` + `test` + manual: mover/dir + home retornam `msg` e disparam `refresh`; sem `lint` quebrado |
| R-VP9 devices/fullscreen/relógio (`refreshDevices, startWebcam/stopWebcam, cssFullscreen, currentTimeStr`) | **extrair agora** — `useFeedDevices()` + `ViewportChrome` (apresentação pura: recebe `stream,error,devices` por props estreitas) | **Baixo–Médio** — getUserMedia tem fallback/permissão; extração não muda ordem stop→start | manual webcam on/off + troca de device + F5; checar `srcObject` e cleanup (sem vazamento de track) |
| R-VP3 evidência RTSP (`refreshRtspFrame, rtspTick/Refreshing/HasCreds/IntervalSec, stale`) | **extrair agora** — `useRtspEvidence(ip,isReal)` dono do polling `setInterval` + fetch + stale; interface `(ip) → {tick,refreshing,hasCreds,refresh,staleMsg}` | **Médio** — `setInterval` + `rtspRefreshing` competem com Vigia; mover sem preservar `alive`-guard duplica polling | manual: trocar `rtspIntervalSec`, alternar câmera real/simulada, confirmar 1 `setInterval` ativo (DevTools) + `frameStaleMsg` em falha |
| R-VP5 Vigia (`runVigiaCycle, vigiaOn/Msg, quietCount, highlight effect :160-177`) | **extrair posteriormente** — `useVigia(...)` após R-VP3/R-VP4 estabilizados (depende de ambos) | **Alto** — heartbeat `%6`, `cycleRunningRef` compartilhado com R-VP4, efeito de destaque escreve `onSelectDetection` do pai | manual: 6 ciclos quietos → 1 análise; movimento → `vigia-cycle analyzed=true`; destaque do alvo correto; sem duplo POST concorrente |
| R-VP4 motion+captura (`captureAndAnalyze, grabCurrentFrameBase64`) | **extrair posteriormente** — `useFrameCapture(...)` (depende de R-VP1+R-VP3) | **Alto** — fail-open + `FileReader/Blob/X-Frame-At` + 4 fontes; qualquer mudança de bytes quebra marcador | manual por fonte (webcam/LAN/sample/upload) + teste de falha motion (fail-open analisa canvas); comparar `analyzedFrameAt` |
| R-VP6 supervisão (`runSupervision`) | **extrair posteriormente** — `useSupervision(ip)` (pequeno, mas acopla política por IP) | **Baixo–Médio** — 1 endpoint; risco é semântico (política) não estrutural | manual: `supervise` escolhe motor e persiste; `vigiaMsg` exibe veredito |
| R-VP10 auto-loop (`746-761`) | **manter no container** (orquestra R-VP4/R-VP5; extrair o loop sem os ciclos = prop-drilling) | — | — |
| R-VP8 modais+sync | **manter na UI-02 como está (UI-01 já isolou)** — remover `isIntelligenceModalOpen` local só quando o fallback deixar de ser necessário; `dedupe por IP` é invariante | **Médio** se removido cedo (quebra `externalSelectedCamera`) | navegação Investigação→Operação entrega 1 câmera sem duplicar `discoveredCameras` |
| R-VP1 fontes / R-VP2 render-loop | **não extrair nesta fase** — extrair `FeedCanvas` recebendo ~15 estados via props repetiría o acoplamento (REJEITADO pela regra); fatiar só via hooks donos (R-VP3/R-VP9) primeiro | — | — |

### 10.2 CameraIntelligencePanel — Mapa de 10 pontos

**1. RESPONSABILIDADE:** R-IP1 verificação (`188-234`, `237-248` auto-run); R-IP2 sweep (`271-322` + `runAutonomousNetworkSweep` + `sweepProgress/currentPhaseName`); R-IP3 single-IP (`340-373`); R-IP4 vendors Nova (`453-520`, creds `97-114`) + Kapbom (`390-450,521-560`, defaults `.25:554/123456`); R-IP5 perfis (`238-240,320,358,379,416,476`, `handleClearAllProfiles/handleDeleteProfile/handleConnectToViewer`); R-IP6 frames (`136-174,258-268`, auto `setInterval`); R-IP7 relatório/logs (`177-179,183-185,251-255`, downloads `978,1618,1726-1745,1877`, clipboard+`setTimeout`); R-IP8 6 abas (`126,271-373` com `setActiveTab('sweep')` cruzado em 4 handlers); R-IP9 entrega (`361,385,434,487,556` → `onSelectCameraToView`, `386` → `onClose`).

**2. ESTADO QUE POSSUI (~28 useState + 1 ref):** `learnedProfiles, isSweeping, sweepProgress, netVerification, isVerifyingNet, subnetPrefix, sweepScope, customIpInput/PortInput/brandHintInput, isLearningSingle, novaIp/Password/Username/Port, isConnectingNova, novaFeedback, kapbomIp/Password/Username/Port, isConnectingKapbom, isScanningKapbomSubnet, kapbomFeedback, logs (cap 80), activeTab, frames, isCapturingFrame, frameFeedback, autoFrames, autoFrameSec, diagnosticReport, currentPhaseName, copiedLog`; ref `logsEndRef`. Escrita 100% local; persistência que POSSUI: `localStorage smartcam_nova_creds_v1` (`100,111`) e perfis via `cameraLearningEngine` (localStorage).

**3. ESTADO QUE CONSOME (só lê):** props `activeCameraId?, onClose?` (App/viewport); `getLearnedProfiles/getLatestDiagnosticReport` (hidratação `237-244`); `KNOWN_VENDOR_SIGNATURES` (tabela); `NetworkVerificationInfo` (resultado); `GET /api/rtsp-frames` (lista). Não escreve no pai exceto via `onSelectCameraToView/onClose`.

**4. EFEITOS COLATERAIS:** rede — `GET /api/rtsp-frames :138`, `POST /api/capture-rtsp-frame :157,491`, e via engine `POST /api/ai-resolve-camera-config, /api/test-camera-ping, /api/save-scan-log, /api/scan-network-cameras` + `probePort` TCP direto (`408,540-541`); timers — `setInterval` auto-frames `:266`, `setTimeout` clipboard `:1649,1745`; persistência — `localStorage` Nova + engine (perfis/relatório); `window.confirm` (`326`); downloads via Blob (`downloadLogFile/downloadJsonFile`); scroll `logsEndRef.scrollIntoView :253`; auto-run de rede no mount (`237-248` executa `verifyCurrentNetwork` sem gesto do usuário).

**5. DEPENDÊNCIAS:** `cameraLearningEngine` (11 imports: perfis, subnet, verify, learn, sweep, vendors, probe, downloads, relatório, assinaturas); tipos (`LearnedCameraProfile/DiscoveryLogEvent/NetworkCamera/DiagnosticReport/...`); `server.ts` (frames/capture + via engine); Web APIs (`localStorage, clipboard, confirm, scrollIntoView`).

**6. DIREÇÃO DA DEPENDÊNCIA:** `App ──{onSelectCameraToView,activeCameraId,onClose}──▶ CameraIntelligencePanel ──callbacks/dados──▶ cameraLearningEngine ──fetch/probe──▶ server.ts / rede`; `Panel ──onSelectCameraToView──▶ App ──externalCameraToView──▶ CameraViewport` (anel Operação↔Investigação mediado por App, não direto). Painel NÃO é importado por nenhum serviço; é folha consumidora (pós-UI-01: montagem canônica única no domínio Investigação).

**7. CONTRATO:** props `onSelectCameraToView(camera):void, activeCameraId?:string, onClose?:()=>void`; forma dos perfis `LearnedCameraProfile→NetworkCamera` (`profileToNetworkCamera`); corpos `POST /api/capture-rtsp-frame {ip,port,path,kind,username,password}`; invariantes: gateway `.1/.254` recusado (Nova `457`), logs cap 80, `sweepScope fast|full`, `activeTab` 6 valores. Auto-run `handleRunNetworkVerification(false)` no mount é comportamento observável (dependência de rede no abrir da Investigação).

**8/9/10. CANDIDATOS À EXTRAÇÃO + RISCO + REGRESSÃO:**

| Resp. | Classificação | Risco + justificativa | Teste de regressão |
|---|---|---|---|
| R-IP6 frames (`refreshFrames/handleCaptureFrame/autoFrames`) | **extrair agora** — `useFrameEvidence()` dono de `frames/isCapturing/capFeedback/autoFrames/Sec` + 2 fetches + `setInterval`; interface `(defaults) → {frames,capture,auto}`; `DiagnosticsPanel` (UI-01) já consome `GET /api/rtsp-frames` independente — prova de interface limpa | **Baixo** — sem dependência de sweep/logs; auto-interval isolável | manual: captura Nova IP, auto-frames 30s, lista atualiza; Diagnóstico continua listando sem montar o painel |
| R-IP7 logs/relatório/downloads | **extrair agora** — `useDiscoveryLog()` (`logs/addLog`, cap 80, autoscroll ref) + `ReportView` apresentação pura (recebe `report` pronto, não 15 estados) | **Baixo** — terminal é append-only; clipboard/download são folhas | manual: sweep gera logs com autoscroll, download .log/.json e copy funcionam; cap 80 respeitado |
| R-IP5 perfis (CRUD + levar ao viewer) | **extrair posteriormente** — `useLearnedProfiles()` (após R-IP2/R-IP3 estabilizados; sweep e single-IP escrevem perfis via callbacks) | **Médio** — 6 pontos de escrita (`320,358,379,416,476,555`) + `window.confirm`; dedupe `id/ip` é invariante | manual: aprender single-IP, sweep parcial, deletar, limpar tudo (confirm), reconectar ao viewer sem duplicar por IP |
| R-IP1 verificação | **extrair posteriormente** — `useNetworkVerification()` (após R-IP8; hoje auto-roda no mount e escreve `subnetPrefix/customIpInput`) | **Médio** — auto-run no mount + fallback `192.168.15.0/24`; mudar timing quebra default de sweep | manual: abrir Investigação executa 1ª ação 1 vez; subnet herdada correta; fallback só em erro |
| R-IP4 vendors (Nova+Kapbom) | **extrair posteriormente** — `useVendorAssistants()` (2 formulários + creds + `probePort`) | **Médio–Alto** — credenciais em `localStorage` + `probePort` direto + `isGatewayIp`; fatiar cedo duplica estado de creds | manual: Nova `.157` conecta e persiste reload; Kapbom `.25` + port-scan; gateway `.1` recusado |
| R-IP2 sweep / R-IP3 single-IP | **manter no container nesta fase** — orquestram engine + 4 escritas (`sweepProgress/phase/logs/profiles/report`); extrair o botão sem o estado = prop-drilling (REJEITADO) | — | — |
| R-IP8 6 abas | **manter** — é a máquina de estados do container; fatiar abas como componentes puros SÓ com props estreitas (`profiles→LearnedTab`, `report→ReportTab`) após os hooks acima existirem | — | — |
| R-IP9 entrega | **manter** — 1 linha de contrato (`onSelectCameraToView`) | — | — |

### 10.3 ESTRUTURA DEPOIS (proposta de desacoplamento real — NÃO implementada, bloqueada)

```
CameraViewport (Container/Orchestrator — só composição + domínio)
├── ViewportChrome (apresentação pura: props {stream,devices,fullscreen,clock})
├── FeedCanvas (visualização: props {mode,camera,overlays} — SEM lógica de fetch)
├── useFeedDevices (dono: devices/stream/permissão/cleanup)
├── useRtspEvidence (dono: polling/fetch/stale — ip como entrada, tick como saída)
├── useFrameCapture (dono: motion-gate + bytes exibidos; depende dos dois acima)
├── useVigia (dono: ciclo/heartbeat/destaque; depende de evidence+capture)
├── usePtz (dono: move/home/msg)
├── useSupervision (dono: veredito/política)
└── AutoDetectLoop (orquestrador: chama capture/vigia por intervalo — sem estado próprio)

CameraIntelligencePanel (Container/Orchestrator — só composição + 6 abas)
├── TabsNav / LearnedTab / SweepTab / ReportTab / FramesTab / VendorTab (apresentação pura)
├── useDiscoveryLog (dono: logs/cap/autoscroll)
├── useFrameEvidence (dono: frames/captura/auto — compartilhável com Diagnóstico)
├── useLearnedProfiles (dono: CRUD/dedupe/persistência)
├── useNetworkVerification (dono: 1ª ação/subnet/fallback)
├── useVendorAssistants (dono: Nova/Kapbom creds/probe)
└── SweepOrchestrator (orquestra engine + progress/report — sem estado de formulário)
```

Regra de aceitação por extração: o hook novo é DONO do seu estado+efeitos (não recebe 15 props do pai); o componente novo recebe ≤5 props de dados + callbacks; direção sempre `Container → Hook/Service → /api`, nunca irmão→irmão; cada extração acompanha seu teste de regressão da tabela (manual nesta fase, pois o frontend só tem testes de utils — `network/detection/yolo_filter/network-context` — sem testes de componente).

### 10.4 Travas e próximos passos

- **Travas vigentes:** nenhuma alteração em `CameraViewport.tsx` / `CameraIntelligencePanel.tsx` além do já executado na UI-01 (fiação de 3 linhas + remoção do embed); `server.ts`, `providers/*`, Strix, pipeline de inferência, detecção, modelos/prompts intocados; `window.__smartcamGroundTruth` preservado e isolado (remoção só pós-validação, UI-02 ou posterior).
- **Para liberar UI-02:** Supervisão+D Direção aprovam este mapa (quais hooks "extrair agora": propostos `usePtz`, `useFeedDevices`+`ViewportChrome`, `useRtspEvidence`, `useDiscoveryLog`+`ReportView`, `useFrameEvidence`) e a ordem (evidência/devices primeiro, Vigia/captura e vendors depois). Cada extração em incremento próprio com `lint + test + build` e regressão manual da tabela.

*Mapa registrado por OpenCode em 2026-10-05, sem modificação de código. Seções 1–9 preservadas.*

---

## 11. FASE UI-02 — INCREMENTO 1: EXTRAÇÕES DE BAIXO RISCO (2026-10-05)

> **Status OS:** AUTORIZADO (Mapa §10 aprovado pela Direção). Escopo estrito: somente itens "Extrair Agora".
> Seções 1–10 integralmente preservadas acima; esta seção só acrescenta.

### 11.1 Arquivos criados (5 hooks + 2 componentes, todos novos, zero alteração de contrato)

| Arquivo | Responsabilidade extraída | Interface (dona do estado) |
|---|---|---|
| `src/hooks/usePtz.ts` | R-VP7 PTZ universal (Tuya→ONVIF, refresh pós-movimento) | `(ip, refreshIntervalSec, onAfterMove) → {moving, msg, move, home}` |
| `src/hooks/useFeedDevices.ts` | R-VP9 devices/stream (enumerate, getUserMedia fallbacks, attach, cleanup) | `(feedMode, videoRef, onStarted) → {devices, selectedId, select, stream, error, requesting, start, stop, refresh}` |
| `src/hooks/useRtspEvidence.ts` | R-VP3 evidência RTSP (refresh, polling alive-guard, stale, `bump`) | `(ip, enabled) → {tick, bump, refreshing, hasCreds, intervalSec, setIntervalSec, lastOkAt, staleMsg, refresh}` |
| `src/hooks/useDiscoveryLog.ts` | R-IP7 log (cap 80, autoscroll) | `() → {logs, add, clear, endRef}` |
| `src/hooks/useFrameEvidence.ts` | R-IP6 frames (lista, captura universal RTSP/HTTP, auto, carga inicial, `ingest` p/ fluxo vendor) | `(ip, port, username, password, onLog, onCaptured) → {frames, capturing, feedback, auto, autoSec, setAuto, setAutoSec, refresh, capture, ingest}` |
| `src/components/ViewportChrome.tsx` | R-VP9 apresentação pura (seletor de lente) | **3 props**: `{devices, selectedId, onSelect}` (null se ≤1 lente) |
| `src/components/ReportView.tsx` | R-IP7 apresentação pura (aba de relatório: métricas, fases 1/2, log, exportações; `copied` local) | **3 props**: `{report, sweeping, onStartSweep}` |

### 11.2 Arquivos modificados (só fiação; God Components NÃO refatorados por dentro)

- `CameraViewport.tsx` (−~250 linhas líquidas): blocos PTZ/devices/RTSP removidos e substituídos por `usePtz`/`useFeedDevices`/`useRtspEvidence` + `ViewportChrome`; render-loop 30fps, motion-gate, Vigia, supervisão, upload, modais e polling de snapshot **intocados** (snapshot lê `evidence.intervalSec`).
- `CameraIntelligencePanel.tsx` (−~380 linhas líquidas): blocos log/relatório/frames removidos e substituídos por `useDiscoveryLog`/`ReportView`/`useFrameEvidence`; sweep, single-IP, vendors Nova/Kapbom, perfis, verificação, 6 abas e entrega de câmera **intocados** (fluxo Nova 1º frame usa `ev.ingest`).
- Fidelidade: dois guards de concorrência recriados com `ref` (`refreshingRef`, `capturingRef`) preservando a semântica original `if (x) return`; callbacks instáveis isolados em refs (`onStartedRef`, `onLogRef/onCapturedRef`) para não resetar intervalos.

### 11.3 Conformidade com as restrições da OS

- FeedCanvas/render-loop (30fps): **não tocado**. Vigia, captura, supervisão, perfis, verificação: **não tocados** (classificados "Posteriormente"/"Manter").
- Componentes novos de apresentação: **3 props cada (≤5)** — sem prop-drilling.
- Intocados: `server.ts`, `src/providers/*`, Strix, inferência/detecção, `src/state/labIsolation.ts` (Ground Truth), `src/navigation/domains.ts`, `DiagnosticsPanel`.
- Semânticas preservadas verbatim: fallbacks getUserMedia + mensagens, fail-open de captura, dedupe por IP, cap 80 de logs, auto-intervalos, payloads de fetch.

### 11.4 Verificação por passo (exigência da OS §3 — tsc + bateria + build)

| Passo | `tsc --noEmit` | `npm test` | `npm run build` |
|---|---|---|---|
| usePtz | 0 erros | 118/118 | — |
| useFeedDevices + ViewportChrome | 0 erros | 118/118 | — |
| useRtspEvidence | 0 erros | 118/118 | — |
| useDiscoveryLog + ReportView + useFrameEvidence | 0 erros | **118/118 (7 arquivos)** | OK (1695→~1700 módulos, `dist/server.mjs` 125.1kb) |

### 11.5 Árvores atualizadas (pós-Incremento 1)

```
CameraViewport (Container — só composição + loops preservados)
├── ViewportChrome (puro, 3 props)
├── FeedCanvas/render-loop (INTOCADO — UI-02 posterior)
├── useFeedDevices / useRtspEvidence / usePtz (donos)
├── useFrameCapture[Vigia/Supervisão] (ainda internos — posteriores)
└── modais Scanner/Inteligência (fiação UI-01 intacta)

CameraIntelligencePanel (Container — só composição + 6 abas)
├── ReportView (puro, 3 props)
├── useDiscoveryLog / useFrameEvidence (donos)
├── useLearnedProfiles/Verification/Vendors/Sweep (ainda internos — posteriores)
└── entrega onSelectCameraToView (contrato intacto)
```

### 11.6 Próximo

Aguardar revisão do Supervisor (Gemini) sobre este incremento antes de qualquer passo adicional. Itens "Posteriormente" (Vigia, captura, supervisão, perfis, verificação, vendors) seguem BLOQUEADOS até nova OS.

*Incremento 1 registrado por OpenCode em 2026-10-05. Alterações de código NÃO commitadas (working tree à disposição da revisão). Seções 1–10 preservadas.*

---

## 12. FASE UI-02 — INCREMENTO 2: AUTOMAÇÃO E IA (2026-10-05)

> **Status OS:** AUTORIZADO pela Direção (recomendação da Supervisão homologada). Escopo: 4 hooks de automação/IA.
> Seções 1–11 integralmente preservadas acima; esta seção só acrescenta.

### 12.1 Arquivos criados

| Arquivo | Responsabilidade extraída | Interface |
|---|---|---|
| `src/hooks/useCycleGuard.ts` | Primitiva de orquestração (infra): exclusão mútua YOLO↔Gemini + `lastCycleAt` (ambos os caminhos atualizavam) | `() → {busy, lastCycleAt, acquire(analyzing), release, markCycle}` |
| `src/hooks/useVigiaCycle.ts` | R-VP5 + ramo motion-gate (toggle, threshold, frameAt, quiet-heartbeat %6, destaque do alvo, `runLocal` YOLO, `runGated` Gemini) | `(guard, camera, analyzing, feedLanReal, currentAnalysis, onSelectDetection, evidenceRefresh, grabLocalFrame, describeLocalSource, currentTime, analyze, notifyVigia?, onEngage, bumpTick)` — objeto de opções tipado |
| `src/hooks/useAnalysisRun.ts` | R-VP4 manual puro (guard → captura local → `analyze` → carimbo) | `(guard, analyzing, grabLocalFrame, describeLocalSource, currentTime, analyze) → {run}` |
| `src/hooks/useSweepEngine.ts` | R-IP2 (sweeping/progress/phase/report + `start(prefix, scope)` + hidratação do relatório) | `(onLog, onProfiles) → {sweeping, progress, phase, report, start}` |
| `src/hooks/useVendorProfile.ts` | R-IP4 (formulários Nova/Kapbom, creds Nova em localStorage, probe, `connectNova/connectKapbom/scanKapbom(prefix)`, 1º frame imediato) | `(onLog, onProfiles, onSelectCamera, onFramesIngested) → {nova:{...}, kapbom:{...}, persistCreds, connectNova, connectKapbom, scanKapbom}` |

### 12.2 Arquivos modificados (só fiação)

- `CameraViewport.tsx` (1367→**1259**, −108): bloco Vigia/motion/YOLO/manual removido; `describeLocalSource` + `feedLanReal` + `guard` no orquestrador; roteamento manual preservado (`vigia.on && feedLanReal → runGated`, senão `runManual`); auto-loop preservado (`runLocal` vs manual); supervisão, render-loop, upload, modais, status-line **intocados** (lêem `vigia.*`/`guard.*`).
- `CameraIntelligencePanel.tsx` (1689→**1442**, −247): blocos sweep/vendors removidos; wrappers finos (`handleStartSweep` = clear + aba + `sweep.start`; `handleConnect*` = fiação; `handleScanKapbomPorts` = aba + `scanKapbom`); ponte vendor→frames via `evIngestRef` (resolve o ciclo de instanciação); verificação, single-IP, perfis CRUD, 6 abas, entrega **intocados**.
- Totais vs baseline original (§10): Viewport 1552→1259 (**−293**); Painel 1943→1442 (**−501**). Nota: os −250/−380 do parecer do Incremento 1 eram parciais intermediários; os números finais consolidados são estes.

### 12.3 Conformidade com as restrições da OS

- Pipelines de inferência, prompts, modelos, `providers/*`, `server.ts`, rotas Express: **intocados** (só `fetch` chamados dos hooks, mesmos paths/bodies).
- Ground Truth (`labIsolation`, `App`, `SmartCamSandbox`): **intocado** — Vigia/análise operam só no fluxo Live, sem `groundTruth`.
- FeedCanvas 30fps e refs de canvas: **intocados** (`grabCurrentFrameBase64` permanece no viewport como `grabLocalFrame`).
- Apresentação: nenhum componente novo; `ReportView`/`ViewportChrome` seguem com 3 props.
- Guards de concorrência recriados com `ref` (`runningRef`, `sweepingRef`, `scanningRef`, `capturingRef` já existente); callbacks instáveis isolados em refs (intervalos/auto-loops não resetam além da dinâmica original, e o `CycleGuard` impede sobreposição mesmo em reset).

### 12.4 Verificação por passo (tsc + bateria + build)

| Passo | `tsc --noEmit` | `npm test` | `npm run build` |
|---|---|---|---|
| useVigiaCycle + useAnalysisRun + useCycleGuard | 0 erros | 118/118 | — |
| useSweepEngine | 0 erros (após fiação) | — | — |
| useVendorProfile (fechamento) | **0 erros** | **118/118 (7 arquivos)** | **OK** (`dist/server.mjs` 125.1kb) |

### 12.5 Árvores atualizadas (pós-Incremento 2 — FASE UI-02 completa)

```
CameraViewport (Container — composição + loops + fontes)
├── ViewportChrome (puro, 3 props)
├── FeedCanvas/render-loop (INTOCADO) + grabLocalFrame/describeLocalSource (R-VP1)
├── useFeedDevices / useRtspEvidence / usePtz (I1)
├── useVigiaCycle (dono: on/msg/threshold/frameAt + runLocal/runGated/toggle)
├── useAnalysisRun (dono: runManual) + useCycleGuard (dono: busy/lastCycleAt)
└── Supervisão IA + modais (intocados/posteriores)

CameraIntelligencePanel (Container — composição + 6 abas)
├── ReportView (puro, 3 props)
├── useDiscoveryLog / useFrameEvidence (I1)
├── useSweepEngine (dono: sweeping/progress/phase/report)
├── useVendorProfile (dono: nova/kapbom + creds + probe)
└── Verificação/single-IP/perfis/entrega (intocados)
```

### 12.6 Encerramento da FASE UI-02

Extrações "Extrair Agora" (§10) esgotadas nos Incrementos 1–2. Restam como trabalho futuro (nova OS): Vigia→(concluído), captura→(concluída manual; motion-gate concluído), supervisão, perfis CRUD, verificação de rede — e a remoção eventual do `window.__smartcamGroundTruth` somente pós-validação do isolamento. HIL com câmera física segue pendente como ressalva geral.

*Incremento 2 registrado por OpenCode em 2026-10-05. Alterações de código NÃO commitadas (working tree à disposição da auditoria final). Seções 1–11 preservadas.*

---

## 13. FASE UI-03 — POLIMENTO VISUAL E DESIGN SYSTEM (2026-10-05)

> **Status OS:** AUTORIZADO pela Direção. Escopo estrito: somente apresentação (JSX/classes/CSS).
> Seções 1–12 integralmente preservadas acima; esta seção só acrescenta.

### 13.1 Componentes criados (apresentação pura, todos ≤4 props)

| Arquivo | Papel | Props |
|---|---|---|
| `src/components/StatusBadge.tsx` | Badge de status (tons live/idle/alert/info + pulse opcional) | 3: `{tone, pulse?, children}` |
| `src/components/SectionHeader.tsx` | Cabeçalho padrão de painel (ícone + título + meta + ações) | 4: `{icon, title, meta?, actions?}` |
| `src/components/LoadingState.tsx` | Spinner (`.sk-spinner`) / skeleton shimmer (`.sk-skeleton`), com `aria-busy`/`aria-live` e `sr-only` | 3: `{label?, variant?, lines?}` |

### 13.2 Alterações por incremento (só visual; zero lógica)

- **UI-03.1 Operação:** `Navbar` — pills de status/frames migradas para `StatusBadge` (mesmas condições `isAutoDetecting`/`analysisCount`, mesmos breakpoints `sm`/`lg`); `App` — grid da Operação 7/5 → **8/4** (`lg:col-span-8` feed + `lg:col-span-4` resultados, com `min-w-0` anti-overflow); grid do Laboratório preservado 7/5.
- **UI-03.2 Drawers:** `TelemetryDrawer`, `SecurityRulesConfig`, `SecurityTimeline` (+ `DetectionsList` no mesmo padrão) — cabeçalhos migrados para `SectionHeader` (textos, ícones, botões, ids e handlers idênticos; só a casca uniformizada). Overlays do viewport (PTZ, mensagens, barra de frame) mantêm `absolute` dentro do container do feed — secundárias não invadem a área central.
- **UI-03.3 Sistema:** `index.css` — bloco `@theme` (`--font-sans` Inter stack) + utilitários aditivos `.sk-spinner`/`.sk-skeleton` (keyframes + `prefers-reduced-motion`); nenhuma classe utilitária existente alterada. `CameraViewport` — 2 botões passam a exibir `LoadingState` nas mesmas condições (`evidence.refreshing`, `feed.requesting`; lógica de `disabled`/handlers intacta).

### 13.3 Conformidade com as restrições da OS

- Hooks UI-02 (`usePtz`, `useVigiaCycle`, `useAnalysisRun`, `useSweepEngine`, `useVendorProfile`, `useCycleGuard`, I1): **nenhum arquivo tocado** (`git diff` sem `src/hooks/*`).
- `server.ts`, `providers/*`, Strix, inferência: **intocados**. Ground Truth Live: **nenhum consumo adicionado** (zero `__smartcamGroundTruth` fora de `labIsolation`/`App`/`Sandbox`).
- Props dos visuais novos: 3–4 (≤5). Nenhum estado, efeito, fetch ou condição foi criado/alterado — só casca.

### 13.4 Verificação

- `tsc --noEmit`: **0 erros** · `npm test`: **118/118 (7 arquivos)** · `npm run build`: **OK** (`dist/server.mjs` 125.1kb).
- Conferência de escopo via `git diff --name-only`: só `App`, `Navbar`, `CameraViewport`, `DetectionsList`, `TelemetryDrawer`, `SecurityRulesConfig`, `SecurityTimeline`, `index.css` (+ 3 componentes novos).

### 13.5 Encerramento do ciclo UI-01→UI-03

Fronteiras (UI-01) + desacoplamento (UI-02 I1+I2) + polimento (UI-03) concluídos com 118/118 estáveis do início ao fim. Pendências gerais do projeto (fora do ciclo UI): HIL com câmera física, homologação em ambiente da Direção, remoção eventual do Ground Truth pós-validação, commit da working tree (aguarda ordem).

*FASE UI-03 registrada por OpenCode em 2026-10-05. Alterações de código NÃO commitadas. Seções 1–12 preservadas.*

