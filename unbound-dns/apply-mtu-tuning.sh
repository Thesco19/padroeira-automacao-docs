#!/usr/bin/env bash
# Aplica mitigação PMTU Black Hole no host/gateway Linux.
# Requer sudo com senha (este ambiente MCP não tem tty para sudo, rode no terminal).
set -euo pipefail

echo "== 1. SYSCTL PLPMTUD =="
sudo cp ./99-mtu-tuning.conf /etc/sysctl.d/99-mtu-tuning.conf
sudo sysctl -p /etc/sysctl.d/99-mtu-tuning.conf
sysctl net.ipv4.tcp_mtu_probing net.ipv4.tcp_base_mss net.ipv4.ip_no_pmtu_disc

echo ""
echo "== 2. MSS CLAMPING (FORWARD para roteador + OUTPUT para host) =="
# FORWARD: só faz efeito se este host roteia (gateway). Em host final, o que conta é OUTPUT.
# PPPoE Twibi 1492 / Tailscale 1280 -> clamp automático ao PMTU; fallback explícito 1240/1220
sudo iptables -t mangle -C FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu 2>/dev/null || \
  sudo iptables -t mangle -A FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu

sudo ip6tables -t mangle -C FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu 2>/dev/null || \
  sudo ip6tables -t mangle -A FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu

# Host-originated (este PC/TV Box Linux):
sudo iptables -t mangle -C OUTPUT -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu 2>/dev/null || \
  sudo iptables -t mangle -A OUTPUT -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu

sudo ip6tables -t mangle -C OUTPUT -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu 2>/dev/null || \
  sudo ip6tables -t mangle -A OUTPUT -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu

echo ""
sudo iptables -t mangle -L -n -v | head -n 20
echo "OK. Persistência: instale iptables-persistent (Debian/Ubuntu: sudo apt install iptables-persistent && sudo netfilter-persistent save)"
