#!/usr/bin/env python3
"""
Aplica limites de memória (deploy.resources.limits.memory) nos compose files.
Executar como root: python3 apply-memory-limits.py
Cria backup de cada arquivo antes de modificar.
"""
import yaml, sys, os, shutil
from pathlib import Path

LIMITS = {
    # /opt/stacks/intel-1/compose.yaml
    "/opt/stacks/intel-1/compose.yaml": {
        "ai_brain":       "6G",      # era 8G → libera 2G
        "scrutiny":       "256M",    # novo
        "system_monitor": "256M",    # ja existe, manter
    },
    # /opt/stacks/litellm/compose.yaml
    "/opt/stacks/litellm/compose.yaml": {
        "litellm":    "1536M",  # proxy + API calls
        "litellm-db": "512M",   # postgres
    },
    # /opt/stacks/mcp-lab/docker-compose.yaml
    "/opt/stacks/mcp-lab/docker-compose.yaml": {
        "mcp-lab-universal": "512M",
    },
    # /opt/stacks/mcp-bridge/docker-compose.yaml
    "/opt/stacks/mcp-bridge/docker-compose.yaml": {
        "mcp-bridge": "256M",
    },
    # /opt/stacks/mcp-superassistant-proxy/docker-compose.yml
    "/opt/stacks/mcp-superassistant-proxy/docker-compose.yml": {
        "mcp-superassistant-proxy": "256M",
    },
    # /opt/stacks/transam/compose.yaml
    "/opt/stacks/transam/compose.yaml": {
        "transmission": "512M",
    },
    # /opt/stacks/meu-painel/compose.yaml
    "/opt/stacks/meu-painel/compose.yaml": {
        "flame": "128M",
    },
    # /opt/stacks/playwright-mcp/docker-compose.yml
    "/opt/stacks/playwright-mcp/docker-compose.yml": {
        "playwright-mcp": "512M",
    },
    # /opt/stacks/vaultwarden/compose.yaml
    "/opt/stacks/vaultwarden/compose.yaml": {
        "vaultwarden": "256M",
    },
    # /opt/stacks/langflow/compose.yaml
    "/opt/stacks/langflow/compose.yaml": {
        "langflow": "2G",  # previne OOM kill
    },
}

def ensure_deploy_limit(services, svc_name, mem_limit):
    """Adiciona ou atualiza deploy.resources.limits.memory para um servico."""
    if svc_name not in services:
        print(f"  [WARN] servico '{svc_name}' nao encontrado, skip")
        return False

    svc = services[svc_name]
    if not isinstance(svc, dict):
        print(f"  [WARN] servico '{svc_name}' nao e dict, skip")
        return False

    deploy = svc.setdefault("deploy", {})
    resources = deploy.setdefault("resources", {})
    limits = resources.setdefault("limits", {})
    old = limits.get("memory")
    limits["memory"] = mem_limit
    if old and old != mem_limit:
        print(f"  {svc_name}: memory {old} -> {mem_limit}")
    elif not old:
        print(f"  {svc_name}: memory = {mem_limit} (novo)")
    else:
        print(f"  {svc_name}: memory = {mem_limit} (inalterado)")
    return True


def process_file(filepath, targets):
    path = Path(filepath)
    if not path.exists():
        print(f"[SKIP] {filepath} nao existe")
        return

    # Backup
    backup = path.with_suffix(path.suffix + ".bak")
    shutil.copy2(path, backup)

    with open(path, "r") as f:
        data = yaml.safe_load(f)

    services = data.get("services", {})
    print(f"[{filepath}] {len(services)} servicos encontrados")

    all_ok = True
    for svc_name, mem_limit in targets.items():
        if not ensure_deploy_limit(services, svc_name, mem_limit):
            all_ok = False

    with open(path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    if all_ok:
        print(f"  -> salvo (backup: {backup.name})")
    else:
        print(f"  -> salvo com WARNINGS (backup: {backup.name})")


if __name__ == "__main__":
    print("=" * 60)
    print("Aplicando limites de memoria nos compose files")
    print("=" * 60)
    for fpath, targets in LIMITS.items():
        process_file(fpath, targets)
        print()
    print("CONCLUIDO")
