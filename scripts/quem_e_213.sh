#!/usr/bin/env bash
TARGET="10.0.1.213"

echo "=== 1. VERIFICANDO NOME VIA DNS / AVAHI ==="
getent hosts $TARGET
avahi-resolve -a $TARGET 2>/dev/null

echo ""
echo "=== 2. VARRENDO PORTAS ABERTAS (SOCKET BASH) ==="
PORTAS=(80 8080 8123 6668 554 8000 1883 443 1900)
for PORT in "${PORTAS[@]}"; do
  (echo > /dev/tcp/$TARGET/$PORT) >/dev/null 2>&1
  if [ $? -eq 0 ]; then
    echo " -> Porta $PORT ABERTA!"
  fi
done

echo ""
echo "=== 3. CAPTURANDO PACOTES DE ANÚNCIO UDP (SSDP / TUYA / MDNS) ==="
timeout 3 tcpdump -n -i enp1s0f0 host $TARGET 2>/dev/null | head -n 5

