#!/usr/bin/env bash
NODES=("10.0.1.1" "10.0.1.200" "10.0.1.31" "10.0.1.227" "10.0.1.213")

echo "=== TESTE DE ESTABILIDADE DOS NÓS MESH / APs ==="
for ip in "${NODES[@]}"; do
    echo -n "Testando $ip: "
    ping -c 5 -i 0.2 -W 1 "$ip" | tail -n 1
done
