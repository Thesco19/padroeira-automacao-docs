#!/bin/bash
set -euo pipefail
echo "=== FASE 4: Limpeza de disco Docker ==="
echo ""
echo "Espaco ANTES:"
docker system df
echo ""

echo "[1/4] Build cache (~28GB recuperaveis)..."
docker builder prune -f 2>&1 | tail -1

echo "[2/4] Containers parados (6 exited)..."
docker container prune -f 2>&1 | tail -1

echo "[3/4] Imagens dangling..."
docker image prune -f 2>&1 | tail -1

echo "[4/4] Volumes nao utilizados..."
docker volume prune -f 2>&1 | tail -1

echo ""
echo "Espaco DEPOIS:"
docker system df
echo ""
echo "=== FASE 4 CONCLUIDA ==="
echo ""
echo "Para limpeza MISTERIOSA adicional (~50GB+), rode manualmente:"
echo "  docker system prune -a --volumes"
echo "  (ATENCAO: remove todas imagens nao usadas e containers parados)"
