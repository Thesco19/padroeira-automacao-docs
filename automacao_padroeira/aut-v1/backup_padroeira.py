#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backup e Divergências - Córtex Padroeira
=========================================

Substitui o backup "em planilha" por um pequeno banco SQLite local
(padroeira_backup.db), guardado ao lado dos scripts.

Responsabilidades:
  1. snapshot_arquivo(): copia binária + hash de um .xlsx antes de
     qualquer escrita (Movto_cx2.xlsx, Movto_diario.{aamm}.xlsx).
  2. registrar_divergencia(): grava, por dia, o valor do caixa
     (Movto_cx2) vs. o valor computado (fechamento.txt/Saurus) e a
     diferença. Se |diferença| > LIMITE_DIVERGENCIA, marca como
     'precisa_reconferencia' e dispara alerta no Telegram (uma única
     vez por dia — idempotente).
  3. limpar_fechamentos_antigos(): apaga fechamento_caixa_*.txt com
     mais de RETENCAO_DIAS dias da pasta de cache local.

Escopo de processamento: nenhuma função aqui decide o corte de data
mínima (jun/2026) — isso é responsabilidade do engine de consolidação,
que já filtra por mês-alvo. Este módulo só cuida de backup e alerta.
"""

import glob
import hashlib
import logging
import os
import shutil
import sqlite3
import time
from contextlib import contextmanager
from datetime import datetime
from typing import Optional

logger = logging.getLogger("BackupPadroeira")

LIMITE_DIVERGENCIA = 30.00   # R$ — acima disso, precisa reconferência manual
RETENCAO_DIAS = 60           # ~2 meses de fechamentos guardados em cache

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "padroeira_backup.db")
SNAPSHOTS_DIR = os.path.join(BASE_DIR, "backups_snapshots")


@contextmanager
def _conexao():
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def inicializar_db() -> None:
    """Cria as tabelas se ainda não existirem. Idempotente."""
    with _conexao() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                arquivo_original TEXT NOT NULL,
                caminho_snapshot TEXT NOT NULL,
                sha256 TEXT NOT NULL,
                aamm TEXT,
                criado_em TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS divergencias (
                data_iso TEXT PRIMARY KEY,
                valor_caixa REAL,
                valor_computado REAL,
                divergencia REAL,
                status TEXT NOT NULL,
                alertado_em TEXT,
                atualizado_em TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS checkup_dias (
                data_iso TEXT PRIMARY KEY,
                categoria TEXT NOT NULL,
                detalhe TEXT,
                atualizado_em TEXT NOT NULL
            )
        """)


def _sha256(caminho: str) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def snapshot_arquivo(caminho: str, aamm: Optional[str] = None) -> Optional[str]:
    """
    Copia `caminho` para backups_snapshots/ com timestamp no nome e
    registra a entrada (com hash) em padroeira_backup.db.
    Deve ser chamado ANTES de qualquer escrita no arquivo original.
    Retorna o caminho do snapshot, ou None se o arquivo original não existir.
    """
    if not os.path.exists(caminho):
        logger.warning(f"[backup] Arquivo não encontrado, nada a copiar: {caminho}")
        return None

    inicializar_db()
    os.makedirs(SNAPSHOTS_DIR, exist_ok=True)

    nome_base = os.path.basename(caminho)
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    nome_snapshot = f"{nome_base}.{timestamp}.bak"
    caminho_snapshot = os.path.join(SNAPSHOTS_DIR, nome_snapshot)

    shutil.copy2(caminho, caminho_snapshot)
    hash_ = _sha256(caminho_snapshot)

    with _conexao() as conn:
        conn.execute(
            "INSERT INTO snapshots (arquivo_original, caminho_snapshot, sha256, aamm, criado_em) "
            "VALUES (?, ?, ?, ?, ?)",
            (nome_base, caminho_snapshot, hash_, aamm, datetime.now().isoformat()),
        )

    logger.info(f"[backup] Snapshot criado: {nome_snapshot} (sha256={hash_[:12]}...)")
    return caminho_snapshot


def registrar_divergencia(
    data_iso: str,
    valor_caixa: Optional[float],
    valor_computado: Optional[float],
    bot=None,
    chat_id: Optional[str] = None,
) -> str:
    """
    Compara caixa (Movto_cx2, soma slips+dinheiro) vs. computado
    (fechamento.txt/Saurus) para `data_iso` (AAAA-MM-DD).
    Grava o resultado em `divergencias` e retorna a categoria:
      "sem_dados", "ok" ou "precisa_reconferencia".
    Dispara alerta Telegram uma única vez por data quando > LIMITE_DIVERGENCIA
    (se `bot` e `chat_id` forem fornecidos).
    """
    inicializar_db()

    if valor_caixa is None or valor_computado is None:
        categoria = "sem_dados"
        diff = None
    else:
        diff = round(valor_computado - valor_caixa, 2)
        categoria = "precisa_reconferencia" if abs(diff) > LIMITE_DIVERGENCIA else "ok"

    agora = datetime.now().isoformat()

    with _conexao() as conn:
        ja_alertado = conn.execute(
            "SELECT alertado_em FROM divergencias WHERE data_iso = ?", (data_iso,)
        ).fetchone()
        alertado_em = ja_alertado[0] if ja_alertado else None

        deve_alertar = (
            categoria == "precisa_reconferencia"
            and alertado_em is None
            and bot is not None
            and chat_id is not None
        )

        if deve_alertar:
            try:
                bot.send_message(
                    chat_id,
                    (
                        f"⚠️ *Divergência acima do limite* — {data_iso}\n"
                        f"• Caixa (Movto_cx2): R$ {valor_caixa:.2f}\n"
                        f"• Computado (Saurus): R$ {valor_computado:.2f}\n"
                        f"• Diferença: R$ {diff:.2f} (limite R$ {LIMITE_DIVERGENCIA:.2f})\n\n"
                        f"Reconferência manual do caixa necessária."
                    ),
                    parse_mode="Markdown",
                )
                alertado_em = agora
                logger.info(f"[divergencia] Alerta Telegram enviado para {data_iso}")
            except Exception as e:
                logger.error(f"[divergencia] Falha ao enviar alerta Telegram p/ {data_iso}: {e}")

        conn.execute(
            """
            INSERT INTO divergencias (data_iso, valor_caixa, valor_computado, divergencia, status, alertado_em, atualizado_em)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(data_iso) DO UPDATE SET
                valor_caixa=excluded.valor_caixa,
                valor_computado=excluded.valor_computado,
                divergencia=excluded.divergencia,
                status=excluded.status,
                alertado_em=COALESCE(divergencias.alertado_em, excluded.alertado_em),
                atualizado_em=excluded.atualizado_em
            """,
            (data_iso, valor_caixa, valor_computado, diff, categoria, alertado_em, agora),
        )

    return categoria


def registrar_checkup_dia(data_iso: str, categoria: str, detalhe: str = "") -> None:
    """
    Grava a categoria do checkup final para um dia sem faturamento preenchido:
    'fechado', 'dado_indisponivel', 'ok', 'precisa_reconferencia' ou 'erro_pipeline'.
    """
    inicializar_db()
    with _conexao() as conn:
        conn.execute(
            """
            INSERT INTO checkup_dias (data_iso, categoria, detalhe, atualizado_em)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(data_iso) DO UPDATE SET
                categoria=excluded.categoria, detalhe=excluded.detalhe, atualizado_em=excluded.atualizado_em
            """,
            (data_iso, categoria, detalhe, datetime.now().isoformat()),
        )


def limpar_fechamentos_antigos(pasta_fechamentos: str, retencao_dias: int = RETENCAO_DIAS) -> int:
    """
    Remove fechamento_caixa_*.txt com mais de `retencao_dias` dias
    (baseado na data no nome do arquivo, não no mtime, pra não depender
    de quando o arquivo foi baixado). Mantém sempre o legado
    fechamento_caixa.txt (sem sufixo de data). Retorna quantos foram removidos.
    """
    padrao = os.path.join(pasta_fechamentos, "fechamento_caixa_*.txt")
    agora = datetime.now().date()
    removidos = 0

    for caminho in glob.glob(padrao):
        nome = os.path.basename(caminho)
        data_str = nome.replace("fechamento_caixa_", "").replace(".txt", "")
        try:
            data_arquivo = datetime.strptime(data_str, "%Y-%m-%d").date()
        except ValueError:
            continue  # nome fora do padrão esperado — não mexe
        if (agora - data_arquivo).days > retencao_dias:
            try:
                os.remove(caminho)
                removidos += 1
                logger.info(f"[retencao] Removido fechamento antigo: {nome} ({data_arquivo})")
            except OSError as e:
                logger.error(f"[retencao] Falha ao remover {nome}: {e}")

    return removidos
