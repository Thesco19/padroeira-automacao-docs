#!/bin/bash
# ============================================================
# MASTER APPLY — Todas as 4 fases
# Rodar como root: sudo bash /opt/scripts/apply-all.sh
# ============================================================
set -euo pipefail
echo "============================================================"
echo " APLICACAO COMPLETA — Todas as 4 fases"
echo "============================================================"
echo ""
echo "Pressione Ctrl+C nos proximos 5 segundos para cancelar."
sleep 5

echo ">>> FASE 1: zram + sysctl"
bash /opt/scripts/zram/apply.sh
echo ""

echo ">>> FASE 2: Servico systemd start controlado"
cp /opt/scripts/docker-controlled-start.service /etc/systemd/system/
cp /opt/scripts/docker-controlled-start.sh /opt/scripts/
chmod +x /opt/scripts/docker-controlled-start.sh
systemctl daemon-reload
systemctl enable docker-controlled-start.service
echo "  -> docker-controlled-start.service habilitado"
echo ""

echo ">>> FASE 3: Limites de memoria (ja aplicado nos compose files)"
echo "  -> Todos os compose files ja atualizados"
echo "  -> Recriar containers para aplicar novos limites"
echo ""

echo ">>> FASE 4: Limpeza de disco"
bash /opt/scripts/docker-cleanup.sh
echo ""

echo "============================================================"
echo " TODAS AS FASES CONCLUIDAS"
echo "============================================================"
echo ""
echo "Proximos passos:"
echo "  1. REINICIAR para ativar tudo no boot:"
echo "     sudo reboot"
echo ""
echo "  2. OU aplicar sem reiniciar:"
echo "     bash /opt/scripts/zram/apply.sh"
echo "     systemctl start docker-controlled-start"
