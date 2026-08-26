#!/usr/bin/env python3
"""ETL somente-leitura: Supabase (lab-g) -> vault Obsidian (ObSV v2).

Gera notas Markdown com frontmatter YAML em
knowledge/00-Inbox/Supabase_Import/. NUNCA escreve no Supabase.

Uso:
  python3 supabase_export_obsv.py
"""
import json
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

SUPA_URL = "https://xwwavfbvdcaypnqmuked.supabase.co/rest/v1"
ANON_KEY = ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
            "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh3d2F2ZmJ2ZGNheXBucW11a2VkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODQ3NTkzMDksImV4cCI6MjEwMDMzNTMwOX0."
            "-D97nBCRPqUkDWhbYQI3bFv2eIxTdNeAfRcRGK_BxGs")

VAULT_INBOX = Path.home() / "work_out" / "knowledge" / "00-Inbox" / "Supabase_Import"
HEADERS = {
    "apikey": ANON_KEY,
    "Authorization": f"Bearer {ANON_KEY}",
    "Content-Type": "application/json",
}

# tabela -> (id_col, titulo_col(s), corpo_cols) / None = default (id/titulo/id)
TABELAS = [
    "projects",
    "artifacts",
    "decisions",
    "tasks",
    "handoffs",
    "agent_context",
    "project_status",
    "bridge_messages",
]

TITULO_COLS = {
    "projects": ["display_name", "name"],
    "artifacts": ["title", "id"],
    "decisions": ["decision", "id"],
    "tasks": ["title", "id"],
    "handoffs": ["id"],
    "agent_context": ["agent", "id"],
    "project_status": ["project", "project_id", "id"],
    "bridge_messages": ["id"],
}

CORPO_COLS = {
    "projects": ["name", "display_name", "description", "owner", "active",
                 "documentation_path", "parent_project", "project_type",
                 "repository", "created_at", "updated_at"],
    "artifacts": ["title", "artifact_type", "artifact_format", "author",
                  "source_agent", "project", "related_task", "version",
                  "checksum", "content", "created_at"],
    "decisions": ["decision", "decision_type", "status", "rationale", "impact",
                  "project", "agent", "approved", "approved_by", "review_date",
                  "created_at"],
    "tasks": ["title", "description", "result", "status", "priority", "owner",
              "project", "depends_on", "estimated_effort", "created_at",
              "completed_at", "rollback_reference"],
    "handoffs": ["context", "reason", "task", "from_agent", "to_agent",
                 "status", "accepted", "accepted_at", "project", "created_at"],
    "agent_context": ["agent", "role", "model", "provider", "gateway",
                      "agent_status", "last_seen", "heartbeat", "capabilities",
                      "limitations", "notes", "project", "updated_at"],
    "project_status": ["project", "project_id", "status", "phase", "progress",
                       "summary", "current_task", "next_action", "owner",
                       "updated_at"],
    "bridge_messages": ["payload", "status", "priority", "project_id",
                        "message_type", "conversation_id", "correlation_id",
                        "reply_to", "target", "author", "attempts",
                        "delivery_status", "expires_at", "protocol_version",
                        "agent_session", "created_at"],
}

VALORES_RICH = {"content", "description", "rationale", "impact", "summary",
                "result", "context", "payload", "capabilities", "limitations",
                "notes", "reason"}


def fetch_tabela(tabela):
    rows = []
    offset = 0
    while True:
        url = f"{SUPA_URL}/{tabela}?select=*&offset={offset}&limit=1000"
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=30) as resp:
            batch = json.loads(resp.read().decode("utf-8"))
        rows.extend(batch)
        if len(batch) < 1000:
            break
        offset += 1000
    return rows


def sanitizar(nome):
    nome = re.sub(r'[^\w\-. ]+', "_", nome)
    nome = re.sub(r"\s+", "_", nome).strip("_")
    return nome[:120] or "sem_titulo"


def yaml(v):
    if v is None:
        return '""'
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"'


def fmt_valor(k, v):
    if v is None:
        return ""
    if isinstance(v, (list, dict)):
        return json.dumps(v, ensure_ascii=False, indent=2, default=str)
    s = str(v)
    if k in VALORES_RICH and "\n" in s:
        return "\n```\n" + s + "\n```\n"
    return s


def data_registro(row):
    for k in ("created_at", "updated_at"):
        if row.get(k):
            return str(row[k])[:10]
    return datetime.now().strftime("%Y-%m-%d")


def exportar(tabela, row):
    cols = CORPO_COLS.get(tabela, list(row.keys()))
    titulos = TITULO_COLS.get(tabela, ["id"])
    titulo = next((sanitizar(row[c]) for c in titulos if row.get(c)), sanitizar(row["id"]))
    if tabela == "projects":
        titulo = f"{tabela}_{titulo}"
    projeto = row.get("project") or row.get("project_id") or "lab"
    tags = ["importacao/supabase", "rag"]
    if projeto:
        tags.append(f"projeto/{sanitizar(projeto)}")
    tags_s = " ".join(f"#{t}" for t in tags)
    data = data_registro(row)
    fname = f"{tabela}_{titulo}.md"
    fpath = VAULT_INBOX / fname

    frontmatter = (
        "---\n"
        f"id: {yaml(row.get('id'))}\n"
        f"data: \"{data}\"\n"
        f"fonte: \"{tabela}\"\n"
        f"tags: {tags_s}\n"
        "---\n"
    )
    body = []
    body.append(f"# {titulo}")
    body.append("")
    for c in cols:
        if c in ("id", "created_at", "updated_at"):
            continue
        v = row.get(c)
        if v is None or v == "" or v == [] or v == {}:
            continue
        body.append(f"## {c}")
        body.append("")
        body.append(fmt_valor(c, v))
        body.append("")
    body.append(f"---\n_Fonte: `{tabela}` | ID: `{row.get('id')}` | Importado do Supabase lab-g (read-only)._")
    fpath.write_text(frontmatter + "\n" + "\n".join(body), encoding="utf-8")
    return fpath


def main():
    VAULT_INBOX.mkdir(parents=True, exist_ok=True)
    total = 0
    por_tabela = {}
    erros = []
    for tabela in TABELAS:
        try:
            rows = fetch_tabela(tabela)
        except urllib.error.HTTPError as e:
            erros.append(f"{tabela}: HTTP {e.code}")
            continue
        except Exception as e:  # noqa: BLE001
            erros.append(f"{tabela}: {e}")
            continue
        n = 0
        for row in rows:
            exportar(tabela, row)
            n += 1
        por_tabela[tabela] = n
        total += n
        print(f"{tabela:18s} {n}")
    print("-" * 30)
    print(f"TOTAL: {total} notas -> {VAULT_INBOX}")
    if erros:
        print("ERROS:")
        for e in erros:
            print("  ", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
