#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot de Reconciliação Padroeira - Ponto Único (bot escuta -> orquestra).

Este é o ELO que faltava no ecossistema: um bot Telegram que ESCUTA o comando
e ORQUESTRA todo o pipeline (Cortex -> Engine -> Balancete) para um ou mais
períodos AAMM, usando a extração SESSÃO ÚNICA do Saurus (reaproveitada do
`extrator_saurus_sessao`, a versão comprovada que produziu 264/0 relatórios).

Comandos:
    /reconciliar [AAMM]   -> roda a reconciliação do período (ex: /reconciliar 2608).
                             Sem AAMM, processa o backlog detectado no Movto_cx2.
    /fechar [AAMM]       -> alias de compatibilidade para /reconciliar.
    /amostra [N] [AAMM]  -> roda apenas N datas pendentes (default 3) — útil p/ teste e2e.

Logs em tempo real: reconciliation.log é zerado a cada start (mode "w") e
espelhado no stdout. Marcadores exatos exigidos pelo teste de produção:
    [TELEGRAM] Comando recebido do usuário.
    [PLAYWRIGHT] Baixando fechamento para a data DD/MM/AAAA...
    [ENGINE] Injetando Kg Equivalente e Sangria (Linha 42) em Movto_diario.AAMM.xlsx...
    [TELEGRAM] Mensagem de resumo enviada ao usuário.
"""

import asyncio
import importlib.util
import logging
import os
import re
import sys

# ----------------------------------------------------------------------
# Logging: FileHandler (zera o arquivo a cada start) + StreamHandler, DEBUG.
# ----------------------------------------------------------------------
WORK = os.path.dirname(os.path.abspath(__file__))            # aut-v1 (raiz do projeto; xlsx de teste ficam aqui)
PARENT = os.path.dirname(WORK)                                # automation_padroeira (pai)

os.makedirs(os.path.join(WORK, "logs"), exist_ok=True)
LOGFILE = os.path.join(WORK, "logs", "reconciliation.log")

logger = logging.getLogger("BotReconciliation")
logger.setLevel(logging.DEBUG)

_fh = logging.FileHandler(LOGFILE, mode="w", encoding="utf-8")
_fh.setLevel(logging.DEBUG)
_sh = logging.StreamHandler(sys.stdout)
_sh.setLevel(logging.DEBUG)

_fmt = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
_fh.setFormatter(_fmt)
_sh.setFormatter(_fmt)
logger.addHandler(_fh)
logger.addHandler(_sh)


# ----------------------------------------------------------------------
# Carga de módulos via importlib (mesmo padrão de pre_producao_2608.py).
# ----------------------------------------------------------------------
def _carregar(modulo: str, caminho: str):
    spec = importlib.util.spec_from_file_location(modulo, caminho)
    m = importlib.util.module_from_spec(spec)
    sys.modules[modulo] = m
    spec.loader.exec_module(m)
    return m


sys.path.insert(0, PARENT)

cortex_mod = _carregar("cortex_padroeira_async", os.path.join(WORK, "cortex_padroeira_async.py"))
engine_mod = _carregar("engine_consolidacao_async", os.path.join(WORK, "engine_consolidacao_async.py"))
bal_mod = _carregar("motor_balancete_async", os.path.join(WORK, "motor_balancete_async.py"))
async_recon_mod = _carregar("async_reconciliation_v2", os.path.join(WORK, "async_reconciliation_v2.py"))

# Força o BASE_DIR do engine para a pasta de trabalho (onde estão os xlsx de teste).
engine_mod.BASE_DIR = WORK
cortex_mod.BASE_DIR = WORK

# Token: vem do ambiente (ou .env local). .env mantém DUMMY propositalmente.
TOKEN_TELEGRAM = cortex_mod._ler_env("TELEGRAM_TOKEN", WORK) or cortex_mod._ler_env("TELEGRAM_TOKEN", PARENT)
CHAT_ID_ALERTAS = cortex_mod._ler_env("TELEGRAM_CHAT_ID", WORK) or cortex_mod._ler_env("TELEGRAM_CHAT_ID", PARENT)

if not TOKEN_TELEGRAM:
    raise RuntimeError(
        "TELEGRAM_TOKEN não encontrado no ambiente nem no .env. "
        "Configure-o antes de iniciar o bot (nunca deixe o token hardcoded)."
    )

import telebot

bot = telebot.TeleBot(TOKEN_TELEGRAM)


# ----------------------------------------------------------------------
# Orquestração
# ----------------------------------------------------------------------
def _parse_aamm(texto: str):
    """Extrai um AAMM (YYMM) do texto do comando, se houver."""
    m = re.search(r"\b(\d{4})\b", texto)
    if m:
        return m.group(1)
    return None


async def _rodar(aamm: str = None, limite: int = None) -> dict:
    """Executa a reconcilação assíncrona (cortex -> engine -> balancete)."""
    engine = async_recon_mod.AsyncReconciliationEngine()
    resultado = await engine.run_reconciliation(aamm=aamm, limite=limite)
    return resultado


def _resumo(resultado: dict) -> str:
    """Monta a mensagem de resumo para o Telegram."""
    det = (resultado or {}).get("details") or {}
    cortex = det.get("cortex_padroeira", {})
    eng = det.get("engine_consolidacao", {})
    bal = det.get("motor_balancete", {})

    aamms_eng = (eng.get("aamms") or []) + (bal.get("aamms") or [])
    aamms_unicos = sorted(set(aamms_eng))

    linhas = []
    linhas.append("🤖 Reconciliação Padroeira — Resumo")
    if aamms_unicos:
        linhas.append(f"📅 Período(s): {', '.join(aamms_unicos)}")
    linhas.append(f"• Córtex (preflight): {cortex.get('status', '?')}"
                  + (f" — {cortex.get('error')}" if cortex.get("error") else ""))
    linhas.append(f"• Engine (Diário): {eng.get('status', '?')}")
    linhas.append(f"• Balancete (Pad): {bal.get('status', '?')}")

    extr = (cortex.get("details") or {}).get("extração_pendentes") or {}
    if extr:
        ok = sum(1 for v in extr.values() if v)
        linhas.append(f"• Fechamentos Saurus extraídos: {ok}/{len(extr)}")

    overall = (resultado or {}).get("status", "error")
    linhas.append(f"✅ Status geral: {overall}")
    return "\n".join(linhas)


# ----------------------------------------------------------------------
# Handlers Telegram
# ----------------------------------------------------------------------
@bot.message_handler(commands=['reconciliar', 'fechar'])
def cmd_reconciliar(message):
    texto = message.text or ""
    logger.info("[TELEGRAM] Comando recebido do usuário.")
    aamm = _parse_aamm(texto)
    chat_id = message.chat.id

    bot.reply_to(message, "🤖 Processando reconciliação Padroeira...\n"
                          f"Período: {aamm or 'backlog do Movto_cx2'}")
    try:
        resultado = asyncio.run(_rodar(aamm=aamm))
        resumo = _resumo(resultado)
        bot.send_message(chat_id, resumo)
        logger.info("[TELEGRAM] Mensagem de resumo enviada ao usuário.")
    except Exception as e:
        logger.exception("[TELEGRAM] Erro ao executar reconciliação")
        try:
            bot.send_message(chat_id, f"⚠️ Erro na reconciliação: {e}")
        except Exception:
            pass


@bot.message_handler(commands=['amostra'])
def cmd_amostra(message):
    """/amostra [N] [AAMM] — processa apenas N datas pendentes (teste e2e)."""
    texto = message.text or ""
    logger.info("[TELEGRAM] Comando recebido do usuário.")
    partes = texto.split()
    limite = 3
    aamm = None
    for p in partes[1:]:
        if p.isdigit() and limite is None and int(p) < 100:
            limite = int(p)
        elif re.fullmatch(r"\d{4}", p):
            aamm = p
    chat_id = message.chat.id

    bot.reply_to(message, f"🤖 Amostra de {limite} data(s) pendente(s) "
                          f"(período: {aamm or 'backlog'})...")
    try:
        resultado = asyncio.run(_rodar(aamm=aamm, limite=limite))
        resumo = _resumo(resultado)
        bot.send_message(chat_id, resumo)
        logger.info("[TELEGRAM] Mensagem de resumo enviada ao usuário.")
    except Exception as e:
        logger.exception("[TELEGRAM] Erro ao executar amostra")
        try:
            bot.send_message(chat_id, f"⚠️ Erro na amostra: {e}")
        except Exception:
            pass


@bot.message_handler(commands=['start', 'help'])
def cmd_help(message):
    bot.reply_to(
        message,
        "Comandos disponíveis:\n"
        "/reconciliar [AAMM] — roda a reconciliação (ex: /reconciliar 2608)\n"
        "/fechar [AAMM] — alias de /reconciliar\n"
        "/amostra [N] [AAMM] — roda N datas pendentes (teste e2e)\n"
    )


# ----------------------------------------------------------------------
# Loop principal — escuta continuamente.
# ----------------------------------------------------------------------
if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("Bot de Reconciliação Padroeira iniciado (modo escuta).")
    logger.info(f"Logs em tempo real: {LOGFILE}")
    logger.info("Comandos: /reconciliar [AAMM]  |  /fechar [AAMM]  |  /amostra [N] [AAMM]")
    logger.info("=" * 70)
    bot.infinity_polling()
