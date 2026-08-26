#!/bin/bash
# ============================================================
# repair-memory.sh — Reparo completo de memória do Mac Mini
# Data: 2026-08-07
# ============================================================
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
ok()   { echo -e "${GREEN}✓${NC} $*"; }
warn() { echo -e "${YELLOW}⚠${NC} $*"; }
fail() { echo -e "${RED}✗${NC} $*"; }

echo "============================================================"
echo " REPARO DE MEMÓRIA — Mac Mini (teco-Macmini)"
echo "============================================================"
echo ""
echo "  Fase1: zram 16G zstd + swappiness 60 + remover swapfile HDD"
echo "  Fase2: start controlado no boot (3 fases com delays)"
echo "  Fase3: limites nos compose (litellm 1.5G, omniroute 4G)"
echo ""
echo "Pressione Ctrl+C nos próximos 5 segundos para cancelar."
sleep 5
echo ""

# ── PRE-CHECK ──────────────────────────────────────────────
echo "=== PRE-CHECK ==="
for f in /opt/scripts/zram/apply.sh /opt/scripts/docker-controlled-start.service /opt/scripts/docker-controlled-start.sh; do
  [ -f "$f" ] && ok "$(basename $f)" || { fail "FALTANDO $f"; exit 1; }
done
for f in /opt/stacks/litellm/compose.yaml /opt/stacks/omniroute/compose.yaml; do
  [ -f "$f" ] && ok "$(basename $(dirname $f))/compose.yaml" || { fail "FALTANDO $f"; exit 1; }
done
echo ""

# ── FASE3 — Limites de memória (não reinicia nada) ─────────
echo "=== FASE3: Limites de memória nos compose files ==="
echo ""

python3 - <<'PYEDIT'
import sys

def edit_file(path, replacements):
    with open(path) as f:
        content = f.read()
    for i, (old, new) in enumerate(replacements):
        count = content.count(old)
        if count != 1:
            print(f"  ✗ ERRO anchor #{i+1}: {count} ocorrências em {path}")
            sys.exit(1)
        content = content.replace(old, new)
    with open(path, 'w') as f:
        f.write(content)

DEPLOY = "\n    # Limite de memória (Fase3) — aplicado em recreate\n    deploy:\n      resources:\n        limits:"

# ── litellm ──
print("  Editando litellm/compose.yaml ...")
edit_file("/opt/stacks/litellm/compose.yaml", [
    ("      retries: 10\n\n  litellm:",
     f"      retries: 10{DEPLOY}\n          memory: 512M\n\n  litellm:"),
    ("      litellm-db:\n        condition: service_healthy",
     f"      litellm-db:\n        condition: service_healthy{DEPLOY}\n          memory: 1.5G"),
    ("      - litellm-probe-data:/data/probe",
     f"      - litellm-probe-data:/data/probe{DEPLOY}\n          memory: 256M"),
])
print("  ✓ litellm: db=512M, proxy=1.5G, health=256M")

# ── omniroute ──
print("  Editando omniroute/compose.yaml ...")
edit_file("/opt/stacks/omniroute/compose.yaml", [
    ("      retries: 3",
     f"      retries: 3{DEPLOY}\n          memory: 1G"),
    ("        condition: service_healthy",
     f"        condition: service_healthy{DEPLOY}\n          memory: 4G"),
])
print("  ✓ omniroute: redis=1G, omniroute=4G")

# ── apply.sh: zram reset ──
print("  Corrigindo apply.sh (zram reset) ...")
with open("/opt/scripts/zram/apply.sh") as f:
    s = f.read()
old = "modprobe zram 2>/dev/null || true\necho zstd > /sys/block/zram0/comp_algorithm"
new = "modprobe zram 2>/dev/null || true\necho 1 > /sys/block/zram0/reset 2>/dev/null || true\necho zstd > /sys/block/zram0/comp_algorithm"
assert s.count(old) == 1, f"apply.sh anchor={s.count(old)}"
s = s.replace(old, new)
with open("/opt/scripts/zram/apply.sh", 'w') as f:
    f.write(s)
print("  ✓ apply.sh: reset antes de disksize")
print()
PYEDIT

# ── VALIDAÇÃO ──────────────────────────────────────────────
echo "=== VALIDAÇÃO ==="
(cd /opt/stacks/litellm && docker compose config -q) && ok "litellm compose válido" || { fail "litellm INVÁLIDO"; exit 1; }
(cd /opt/stacks/omniroute && docker compose config -q) && ok "omniroute compose válido" || { fail "omniroute INVÁLIDO"; exit 1; }
echo ""

# ── FASE1 — zram + sysctl ──────────────────────────────────
echo "=== FASE1: zram 16G zstd ==="
echo ""

cp /opt/scripts/zram/99-zram-tuning.conf /etc/sysctl.d/99-zram-tuning.conf
ok "sysctl instalado (swappiness=60)"

cp /opt/scripts/zram/zram0.service /etc/systemd/system/zram0.service
systemctl daemon-reload
systemctl enable zram0.service
ok "zram0.service habilitado"

swapoff /swapfile 2>/dev/null && ok "swapoff /swapfile" || ok "swapoff já feito"
sed -i "\|/swapfile|s/^/#/" /etc/fstab 2>/dev/null && ok "fstab atualizado" || ok "fstab já atualizado"
rm -f /swapfile && ok "/swapfile removido" || ok "/swapfile já removido"

modprobe zram 2>/dev/null || true
echo 1 > /sys/block/zram0/reset 2>/dev/null || true
echo zstd > /sys/block/zram0/comp_algorithm
echo 16G > /sys/block/zram0/disksize
mkswap /dev/zram0 2>/dev/null
swapon -p 100 /dev/zram0
ok "zram0 ativo: 16G, zstd, prio100"

sysctl --system 2>/dev/null | grep -E "swappiness|dirty"
ok "sysctl aplicado"
echo ""
swapon --show
free -h
echo ""

# ── FASE2 — start controlado ───────────────────────────────
echo "=== FASE2: Start controlado ==="
cp /opt/scripts/docker-controlled-start.service /etc/systemd/system/
cp /opt/scripts/docker-controlled-start.sh /opt/scripts/
chmod +x /opt/scripts/docker-controlled-start.sh
systemctl daemon-reload
systemctl enable docker-controlled-start.service
ok "docker-controlled-start.service habilitado"
echo ""

# ── RESUMO ─────────────────────────────────────────────────
echo "============================================================"
echo " REPARO CONCLUÍDO"
echo "============================================================"
echo ""
echo "Aplicado agora (sem reiniciar containers):"
echo "  ✓ Fase1: zram0 16G zstd, swappiness=60, /swapfile removido"
echo "  ✓ Fase2: start controlado habilitado (ativa no próximo boot)"
echo "  ✓ Fase3: limites adicionados nos compose files"
echo ""
echo "Próximo passo — RECREATE no Dockge:"
echo "  1. Recrear LITELM   (proxy→1.5G, db→512M, health→256M)"
echo "  2. Recrear OMNIROUTE (omniroute→4G, redis→1G)"
echo "     ⚠️ Derruba o proxy brevemente — faça por último"
echo ""
