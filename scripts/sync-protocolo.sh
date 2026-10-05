#!/usr/bin/env bash
# sync-protocolo.sh — instala/atualiza o bloco PROTOCOLO_LAB (IDÊNTICO) em
# cada .md de agente (CLAUDE/OPENCODE/CODEX/GEMINI/JCODE).
#
# Uso: scripts/sync-protocolo.sh [--check]
#   --check : só mostra o que mudaria, sem alterar nada e sem backup.
#
# Regras:
# - O bloco canônico sai de PROTOCOLO_LAB.md (entre os marcadores).
# - Nada fora dos marcadores é alterado.
# - Backup antes de modificar: ~/protocolo-bak-<TS>/<caminho-relativo>.
# - Nunca toca em: knowledge/ (vault ObSV), archive/ (backups), node_modules,
#   .git, venv/.venv, .aider*, .remember/.
set -euo pipefail

ROOT="/home/teco/work_out"
STACKS="/opt/stacks"
PROTO="$ROOT/PROTOCOLO_LAB.md"
MARK_IN="<!-- PROTOCOLO_LAB:INICIO -->"
MARK_OUT="<!-- PROTOCOLO_LAB:FIM -->"
TS="$(date +%Y%m%d-%H%M%S)"
BACKUP_BASE="$HOME/protocolo-bak-$TS"
CHECK=0
[ "${1:-}" = "--check" ] && CHECK=1

# 1. Extrai o bloco canônico (entre marcadores, sem as linhas de marcador).
BLOCK_FILE="$(mktemp)"
sed -n "/^${MARK_IN}\$/,/^${MARK_OUT}\$/p" "$PROTO" | sed '1d;$d' > "$BLOCK_FILE"
[ -s "$BLOCK_FILE" ] || { echo "ERRO: bloco vazio em $PROTO"; exit 1; }

# 2. Descobre os arquivos-alvo.
#    knowledge/ e archive/ ficam de fora (find só entra na raiz, lab-a/b/z e stacks).
mapfile -t FILES < <(
  { find "$ROOT" -maxdepth 1 -type f \
      \( -name 'CLAUDE.md' -o -name 'OPENCODE.md' -o -name 'CODEX.md' -o -name 'GEMINI.md' -o -name 'JCODE.md' \) -print
    find "$ROOT/lab-a" "$ROOT/lab-b" "$ROOT/lab-z" \
      \( -path '*/node_modules/*' -o -path '*/.git/*' -o -path '*/venv/*' -o -path '*/.venv/*' -o -path '*/.aider*/*' -o -path '*/.remember/*' \) -prune -o \
      -type f \( -name 'CLAUDE.md' -o -name 'OPENCODE.md' -o -name 'CODEX.md' -o -name 'GEMINI.md' -o -name 'JCODE.md' \) -print
    find "$STACKS" -maxdepth 2 \
      \( -path '*/node_modules/*' -o -path '*/.git/*' \) -prune -o \
      -type f \( -name 'CLAUDE.md' -o -name 'OPENCODE.md' -o -name 'CODEX.md' -o -name 'GEMINI.md' -o -name 'JCODE.md' \) -print
  } | sort -u
)
echo "alvos: ${#FILES[@]}"

# 3. Insere/atualiza via python (splice exato pelos marcadores).
export MARK_IN MARK_OUT BLOCK_FILE CHECK BACKUP_BASE ROOT STACKS HOME
total=0; atualizados=0; inalterados=0; erros=0
for f in "${FILES[@]}"; do
  total=$((total + 1))
  # Caminho relativo para o backup espelhado.
  if [[ "$f" == "$ROOT/"* ]]; then rel="work_out/${f#$ROOT/}"
  elif [[ "$f" == "$STACKS/"* ]]; then rel="stacks/${f#$STACKS/}"
  else rel="outros/$(echo "$f" | tr '/' '_')"; fi
  export F="$f" REL="$rel"
  acao="$(python3 - <<'PYEOF'
import os
f = os.environ['F']
mi = os.environ['MARK_IN']
mo = os.environ['MARK_OUT']
try:
    with open(f, 'r', encoding='utf-8') as fh:
        txt = fh.read()
    with open(os.environ['BLOCK_FILE'], 'r', encoding='utf-8') as fh:
        block = fh.read().strip('\n')
except Exception as e:
    print(f"ERRO:{e}")
    raise SystemExit
if mi in txt and mo in txt:
    pre, resto = txt.split(mi, 1)
    inner, post = resto.split(mo, 1)
    if inner.strip('\n') == block:
        print("SKIP")
    else:
        print("UPDATE")
else:
    print("APPEND")
PYEOF
)"
  case "$acao" in
    SKIP*) inalterados=$((inalterados + 1));;
    APPEND|UPDATE)
      if [ "$CHECK" = "1" ]; then
        echo "mudaria [$acao] $f"
        atualizados=$((atualizados + 1))
      else
        mkdir -p "$BACKUP_BASE/$(dirname "$REL")"
        cp -p "$f" "$BACKUP_BASE/$REL"
        python3 - "$f" <<'PYEOF'
import os, sys
f = sys.argv[1]
mi = os.environ['MARK_IN']
mo = os.environ['MARK_OUT']
with open(os.environ['BLOCK_FILE'], 'r', encoding='utf-8') as fh:
    block = fh.read().strip('\n')
with open(f, 'r', encoding='utf-8') as fh:
    txt = fh.read()
if mi in txt and mo in txt:
    pre, resto = txt.split(mi, 1)
    _, post = resto.split(mo, 1)
    new = pre + mi + "\n" + block + "\n" + mo + post
else:
    if not txt.endswith("\n"):
        txt += "\n"
    new = txt + "\n" + mi + "\n" + block + "\n" + mo + "\n"
with open(f, 'w', encoding='utf-8') as fh:
    fh.write(new)
PYEOF
        echo "[$acao] $f"
        echo "--- diff $f"
        diff -u "$BACKUP_BASE/$REL" "$f" || test $? -eq 1
        atualizados=$((atualizados + 1))
      fi
      ;;
    *) echo "[$acao] $f"; erros=$((erros + 1));;
  esac
done
rm -f "$BLOCK_FILE"
echo "== resumo: total=$total atualizados=$atualizados inalterados=$inalterados erros=$erros"
[ "$CHECK" = "1" ] || echo "backups em: $BACKUP_BASE"
