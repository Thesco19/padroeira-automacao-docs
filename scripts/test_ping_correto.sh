#!/usr/bin/env bash
echo "=== PING MATRIX REVISADA ==="
echo -n "Gateway Giga (.1)  : " && ping -c 5 -i 0.2 10.0.1.1 | tail -n 1
echo -n "Nó Mesh 1 (.31)    : " && ping -c 5 -i 0.2 10.0.1.31 | tail -n 1
echo -n "Nó Mesh 2 (.200)   : " && ping -c 5 -i 0.2 10.0.1.200 | tail -n 1
echo -n "Mi Stick (.171)    : " && ping -c 5 -i 0.2 10.0.1.171 | tail -n 1
echo -n "Host Suspeito (.213): " && ping -c 5 -i 0.2 10.0.1.213 | tail -n 1
