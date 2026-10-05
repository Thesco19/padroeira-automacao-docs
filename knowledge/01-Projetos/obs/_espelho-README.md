Espelho de /home/teco/work_out/lab-b/obs/README.md em 2026-09-30; fonte: a pasta

# ObSV — v2.0

Acesso local e seguro a um vault do Obsidian via CLI, API REST /api/v1, Web UI e MCP.

O vault no filesystem é a única fonte de verdade (SPEC §8); o índice SQLite é uma projeção derivada e reconstruível a qualquer momento.

## Características

- Zero dependências externas — 100% biblioteca padrão (Python ≥ 3.9).
- CLI: index, verify, doctor, search, tree, cat, new, backlinks, links, stats, append, mv, mkdir, rm, init, config, serve, mcp e mcp-proxy.
- API REST /api/v1 com envelope M01 ({ok:{...}} / {error:{...}}): leitura (health, stats, tree, file, raw, search, backlinks, links) e escrita (note, mkdir, move, reindex) com precondição de versão (ETag {mtime_ns}:{size}) e 409.
- Web UI sem JavaScript: busca, árvore, visualização renderizada e editor raw com CSP script-src 'none' (SPEC §40).
- HTTPS via certfile/keyfile (ADR-001) e política --tailscale-only (SPEC §34).
- MCP nativo (obsv mcp, obsv serve --mcp): JSON-RPC 2.0 sobre stdio ou HTTP+SSE — ferramentas search_vault, read_note, write_note, get_backlinks, verify_vault.
- MCP proxy (obsv mcp-proxy --server-url): adaptador sidecar (M14) que traduz MCP → REST v1, sem tocar filesystem/SQLite. Encerrar o proxy não afeta o servidor.

## Instalação

pip install .
# ou sem instalar:
PYTHONPATH=. python3 -m obsv --help

## Uso rápido

obsv config --vault /caminho/do/vault
obsv index --full

obsv serve --port 8777                     # HTTP loopback
obsv serve --port 8777 --certfile srv.crt --keyfile srv.key --tailscale-only

obsv doctor
obsv verify

obsv mcp
obsv mcp-proxy --server-url http://127.0.0.1:8777

## Testes

python3 -m unittest discover -s tests -p "test_*.py" -v
python3 -W error::ResourceWarning -m unittest discover -s tests -p "test_*.py"

## Documentação

- docs/SPEC.md — especificação aprovada (contrato congelado).
- docs/IMPLEMENTATION_PLAN.md — milestones M01–M14.
- docs/ADR-*.md — decisões arquiteturais.
- docs/M*_REPORT.md — relatórios de cada milestone.

## Ficha (Fase 1 — só acréscimo, linhas originais intactas)

- Classe: projeto
- Local: lab-b
- Nome canônico: obs; alias: obsv (não renomear a pasta: obsv-bridge.service e o MCP registrado nos agentes dependem dela)
- Nomes em outros sistemas: RAG tag=obsv | Supabase=obsv | ObSV=01-Projetos/ObSV-IMPLEMENTATION_PLAN.md | LM: serviço via systemd (obsv-bridge.service, :8777)
- Segredos: nenhum .env no projeto (verificado no inventário)
- Ver também: STATUS.md