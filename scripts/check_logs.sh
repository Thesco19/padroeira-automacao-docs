#!/bin/bash
# Stacks de mídia monitoradas (arr + transmission + seerr + plex + bazarr + flaresolverr)
STACKS="prowlarr sonarr radarr lidarr transmission seerr plex bazarr bazarr-auto-translate flaresolverr"

CONTAINERS=""
for c in $STACKS; do
    if docker ps --format "{{.Names}}" | grep -qx "$c"; then
        CONTAINERS="$CONTAINERS $c"
    fi
done

if [ -z "$CONTAINERS" ]; then
  echo "⚠️ Athena: Nenhum container de mídia encontrado."
  exit 1
fi

echo "🚀 Monitorando:$CONTAINERS"
echo "------------------------------------------------"


# Como o seu Docker exige 1 argumento por vez, usamos um loop para disparar todos
# O '&' no final faz cada log rodar em background simultaneamente no mesmo terminal
# O 'wait' garante que o script não feche sozinho
for c in $CONTAINERS; do
    docker logs -f --tail 20 "$c" &
done
wait
