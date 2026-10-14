#!/usr/bin/env bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}=== 1. GATEWAY E INTERFACES DA REDE ===${NC}"
GATEWAY=$(ip route | grep default | awk '{print $3}' | head -n 1)
IFACE=$(ip route | grep default | awk '{print $5}' | head -n 1)

echo "Interface principal: $IFACE"
echo "IP do Gateway (Roteador): $GATEWAY"
echo ""

echo -e "${YELLOW}=== 2. TESTE DE CONECTIVIDADE LOCAL E EXTERNA ===${NC}"
if [ -n "$GATEWAY" ]; then
    ping -c 3 -W 2 "$GATEWAY" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "Ping Gateway ($GATEWAY): ${GREEN}OK${NC}"
    else
        echo -e "Ping Gateway ($GATEWAY): ${RED}FALHOU (Possível perda de link físico/LAN)${NC}"
    fi
else
    echo -e "${RED}Gateway padrão não encontrado! Check o DHCP/Configuração de IP.${NC}"
fi

ping -c 3 -W 2 1.1.1.1 > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "Ping IP Externo (1.1.1.1): ${GREEN}OK${NC}"
else
    echo -e "Ping IP Externo (1.1.1.1): ${RED}FALHOU (Link WAN fora do ar)${NC}"
fi

host google.com > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "Resolução DNS (google.com): ${GREEN}OK${NC}"
else
    echo -e "Resolução DNS (google.com): ${RED}FALHOU (Problema no Servidor DNS)${NC}"
fi
echo ""

echo -e "${YELLOW}=== 3. DISPOSITIVOS CONECTADOS E TABELA ARP ===${NC}"
echo "Total de IPs ativos/descobertos na tabela ARP local:"
ip neighbor | grep -v FAILED | wc -l
echo "Últimas entradas da tabela ARP:"
ip neighbor show | head -n 10
echo ""

echo -e "${YELLOW}=== 4. VERIFICAÇÃO DE INTERFACES WI-FI NO HOST ===${NC}"
if command -v iwconfig > /dev/null 2>&1; then
    iwconfig 2>&1 | grep -v "no wireless extensions"
elif command -v nmcli > /dev/null 2>&1; then
    nmcli device status | grep wifi
else
    echo "Nenhuma ferramenta de gerência sem fio (iwconfig/nmcli) encontrada ou sem rádio local."
fi
echo ""

echo -e "${YELLOW}=== 5. PERDA DE PACOTES E LATÊNCIA NO ROUTER (30 seg) ===${NC}"
if [ -n "$GATEWAY" ]; then
    echo "Métricas de estabilidade para $GATEWAY:"
    ping -c 20 -i 0.2 "$GATEWAY" | tail -n 2
fi

