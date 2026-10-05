#!/usr/bin/env python3
"""
Sincroniza README.md e STATUS.md dos projetos com a RAG via MCP lab-universal.
Idempotente: usa manifesto local (caminho -> hash, doc_id).

Uso:
    python3 scripts/sync-conhecimento.py --dry-run
    python3 scripts/sync-conhecimento.py
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

LABS = ["lab-a", "lab-b", "lab-z"]
STACKS_ROOT = Path("/opt/stacks")
WORK_OUT = Path("/home/teco/work_out")
MANIFEST_PATH = WORK_OUT / "scripts" / "sync-manifest.json"
MCP_URL = "http://127.0.0.1:8765/mcp"

TOKEN_REGEX = re.compile(r"\d{8,10}:[A-Za-z0-9_-]{30,}")


def compute_hash(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


def contains_secret(content: str) -> bool:
    return bool(TOKEN_REGEX.search(content))


def get_projects():
    projects = []
    for lab in LABS:
        lab_path = WORK_OUT / lab
        if not lab_path.exists():
            continue
        for entry in sorted(lab_path.iterdir()):
            if entry.is_dir() and not entry.name.startswith("."):
                projects.append((entry.name, entry))
    if STACKS_ROOT.exists():
        for entry in sorted(STACKS_ROOT.iterdir()):
            if entry.is_dir() and not entry.name.startswith("."):
                projects.append((entry.name, entry))
    return projects


def load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text())
    return {}


def save_manifest(manifest: dict):
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))


def mcp_call(tool_name: str, arguments: dict, max_retries: int = 3, base_delay: float = 1.0) -> dict:
    """Chama ferramenta MCP via HTTP streamable com retry exponencial."""
    import urllib.request
    import time
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments},
    }
    req = urllib.request.Request(
        MCP_URL,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        },
        method="POST",
    )
    last_error = None
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)
    return {"error": str(last_error)}


def sync_project(project_name: str, project_path: Path, manifest: dict, dry_run: bool = False) -> dict:
    results = {"project": project_name, "files": []}
    for fname in ["README.md", "STATUS.md"]:
        fpath = project_path / fname
        if not fpath.exists():
            results["files"].append({"file": fname, "status": "missing"})
            continue

        content = fpath.read_text(encoding="utf-8")
        if contains_secret(content):
            results["files"].append({"file": fname, "status": "skipped_secret", "path": str(fpath)})
            continue

        file_hash = compute_hash(content)
        mirror_header = f"Espelho de {fpath} em {datetime.now().strftime('%Y-%m-%d %H:%M')}; fonte: a pasta\n\n"
        full_content = mirror_header + content

        key = f"{project_name}/{fname}"
        existing = manifest.get(key, {})

        if existing.get("hash") == file_hash:
            results["files"].append({"file": fname, "status": "unchanged"})
            continue

        if dry_run:
            results["files"].append({"file": fname, "status": "would_sync", "hash": file_hash[:8]})
            continue

        old_doc_id = existing.get("doc_id")
        if old_doc_id:
            mcp_call("apagar_documento", {"doc_id": old_doc_id})

        doc_id = f"{project_name}_{fname.replace('.md', '').lower()}_{file_hash[:8]}"
        result = mcp_call("ingest_document", {
            "content": full_content,
            "metadata": {
                "project": project_name,
                "source_file": fname,
                "file_hash": file_hash,
                "synced_at": datetime.now().isoformat(),
            }
        })

        if "error" in result:
            results["files"].append({"file": fname, "status": "error", "error": result["error"]})
        else:
            manifest[key] = {"hash": file_hash, "doc_id": doc_id, "synced_at": datetime.now().isoformat()}
            results["files"].append({"file": fname, "status": "synced", "doc_id": doc_id})

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    projects = get_projects()
    print(f"Projetos encontrados: {len(projects)}")

    manifest = load_manifest()
    all_results = []

    for name, path in projects:
        result = sync_project(name, path, manifest, dry_run=args.dry_run)
        all_results.append(result)
        if not args.dry_run:
            save_manifest(manifest)
            time.sleep(0.5)

    print(json.dumps(all_results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
