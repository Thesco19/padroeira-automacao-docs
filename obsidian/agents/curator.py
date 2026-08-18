#!/usr/bin/env python3
import subprocess
from pathlib import Path

ROOT = Path("/home/teco/work_out/knowledge")
INBOX = ROOT / "00-Inbox"
PROMPT = Path("/home/teco/work_out/obsidian/prompts/curator.md")

files = sorted(p for p in INBOX.rglob("*.md") if "_processed" not in p.parts)

if not files:
    print("Inbox vazia.")
    raise SystemExit(0)

manifest = "\n".join(str(p) for p in files)

message = f"""
{PROMPT.read_text()}

ARQUIVOS A PROCESSAR:
{manifest}

Execute a curadoria agora. Use as ferramentas disponíveis para ler os arquivos.
"""

subprocess.run(
    [
        "jcode", "run",
        "-C", str(ROOT),
        "--tools", "bash,read,write,apply_patch",
        message,
    ],
    check=True,
)
