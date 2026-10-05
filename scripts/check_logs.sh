#!/bin/bash
# check_logs.sh — stacks de mídia (arr + transmission + seerr + plex + bazarr + flaresolverr)
# Corrigido 2026-09-20: `docker logs --tail N` no Docker 29.4.0 retorna vazio
# para driver json-file. Workaround: `docker logs` SEM --tail + `tail -n` do shell.
# Plex não loga em stdout (stdout=0 bytes) — lê log interno via `docker exec`.
#
# Uso:
#   logs              -> snapshot últimas 30 linhas de cada container
#   logs -n 50        -> snapshot últimas 50 linhas
#   logs -f           -> follow (tempo real) de todos
#   logs -f plex      -> follow só do plex
#   logs sonarr plex  -> snapshot só desses

STACKS="prowlarr sonarr radarr lidarr transmission seerr plex bazarr bazarr-auto-translate flaresolverr"
PLEX_LOG_DIR="/config/Library/Application Support/Plex Media Server/Logs"
LINES=30
FOLLOW=0
FILTER=""

usage() {
    echo "Uso: $(basename "$0") [-n LINHAS] [-f] [-h] [container...]"
    echo "  -n LINHAS  nº de linhas no snapshot (padrão 30)"
    echo "  -f         follow (tempo real, Ctrl+C p/ sair)"
    echo "  -h         ajuda"
    exit 0
}

while [ $# -gt 0 ]; do
    case "$1" in
        -n) LINES="$2"; shift 2 ;;
        -f|--follow) FOLLOW=1; shift ;;
        -h|--help) usage ;;
        -*) echo "Opção desconhecida: $1" >&2; usage ;;
        *) FILTER="$FILTER $1"; shift ;;
    esac
done

# containers alvo: filtro do usuário ou todos os STACKS que estiverem rodando
RUNNING=$(docker ps --format "{{.Names}}")
CONTAINERS=""
if [ -n "$FILTER" ]; then
    for c in $FILTER; do
        if echo "$RUNNING" | grep -qx "$c"; then
            CONTAINERS="$CONTAINERS $c"
        else
            echo "⚠️  container '$c' não está rodando (ignorado)." >&2
        fi
    done
else
    for c in $STACKS; do
        if echo "$RUNNING" | grep -qx "$c"; then
            CONTAINERS="$CONTAINERS $c"
        fi
    done
fi

if [ -z "$CONTAINERS" ]; then
  echo "⚠️ Athena: Nenhum container de mídia encontrado."
  echo "   Rodando agora: $(echo $RUNNING | tr '\n' ' ')"
  exit 1
fi

plex_internal_log() {
    # descobre o log principal do Plex (nome varia) e dá tail nele
    local logfile
    logfile=$(docker exec plex sh -c "ls -t '$PLEX_LOG_DIR'/*.log 2>/dev/null | head -n 1")
    if [ -n "$logfile" ]; then
        echo "(via docker exec: $logfile)"
        docker exec plex tail -n "$LINES" "$logfile" 2>&1
    else
        echo "(sem *.log interno; caindo p/ stdout)"
        docker logs "$1" 2>&1 | tail -n "$LINES"
    fi
}

plex_follow_log() {
    local logfile
    logfile=$(docker exec plex sh -c "ls -t '$PLEX_LOG_DIR'/*.log 2>/dev/null | head -n 1")
    if [ -n "$logfile" ]; then
        docker exec plex tail -F -n "$LINES" "$logfile" 2>&1
    else
        docker logs -f --since 60s plex 2>&1
    fi
}

snapshot_one() {
    local c="$1"
    echo ""
    echo "===== $c (últimas $LINES linhas) ====="
    if [ "$c" = "plex" ]; then
        plex_internal_log "$c"
    else
        # SEM --tail do Docker (bug 29.4.0) — tail do shell
        docker logs "$c" 2>&1 | tail -n "$LINES"
    fi
    local rc=${PIPESTATUS[0]:-0}
    if [ "$rc" -ne 0 ]; then
        echo "(docker logs falhou p/ $c, rc=$rc)"
    fi
}

follow_all() {
    echo "🚀 Follow em:$CONTAINERS (Ctrl+C p/ sair)"
    echo "------------------------------------------------"
    # --since funciona (só --tail está quebrado), então limita o histórico antes do follow
    for c in $CONTAINERS; do
        if [ "$c" = "plex" ]; then
            ( echo "--- plex ---"; plex_follow_log ) &
        else
            ( docker logs -f --since 60s "$c" 2>&1 | sed -u "s/^/[$c] /" ) &
        fi
    done
    wait
}

if [ "$FOLLOW" -eq 1 ]; then
    follow_all
    exit 0
fi

echo "🚀 Logs:$CONTAINERS"
echo "------------------------------------------------"
for c in $CONTAINERS; do
    snapshot_one "$c"
done
