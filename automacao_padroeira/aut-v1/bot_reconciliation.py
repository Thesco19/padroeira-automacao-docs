#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot de Reconciliação Padroeira - Ponto Único (bot escuta -> orquestra).

Este é o ELO que faltava no ecossistema: um bot Telegram que ESCUTA o comando
e ORQUESTRA todo o pipeline (Cortex -> Engine -> Balancete) para um ou mais
períodos AAMM, usando a extração SESSÃO ÚNICA do Saurus (reaproveitada do
`extrator_saurus_sessao`, a versão comprovada que produziu 264/0 relatórios).

Comandos:
    /fechar              -> PRIMEIRO comando do operador: ENTRA no Saurus (Playwright),
                             puxa o RELATÓRIO DE FECHAMENTO DO DIA, lê o faturamento para
                             a CONFERÊNCIA DE CAIXA, ENVIA ao Telegram e SALVA o relatório
                             (cache ./fechamentos/ + histórico JSON) para o /finalizar usar.
                             Se o relatório do dia já estiver em cache, reaproveita sem
                             reentrar no portal.
    /finalizar [MMAA]    -> CONCLUI o preenchimento e o transporte de dados
                             (Cortex -> Engine -> Balancete Pad). Sem MMAA, assume o dia
                             de hoje (AAMM corrente). Se MMAA informado, faz a varredura
                             completa do período. /reconciliar é mantido como alias.
    /amostra [N] [MMAA]  -> roda apenas N datas pendentes (default 3) — útil p/ teste e2e.

Logs em tempo real: reconciliation.log é zerado a cada start (mode "w") e
espelhado no stdout. Marcadores exatos exigidos pelo teste de produção:
    [TELEGRAM] Comando recebido do usuário.
    [PLAYWRIGHT] Baixando fechamento para a data DD/MM/AAAA...
    [ENGINE] Injetando Kg Equivalente e Sangria (Linha 42) em Movto_diario.AAMM.xlsx...
    [TELEGRAM] Mensagem de resumo enviada ao usuário.
"""

import asyncio
import importlib.util
import json
import logging
import os
import re
import sys
from datetime import datetime

# ----------------------------------------------------------------------
# Logging: FileHandler (zera o arquivo a cada start) + StreamHandler, DEBUG.
# ----------------------------------------------------------------------
WORK = os.path.dirname(os.path.abspath(__file__))            # aut-v1 (raiz do projeto; xlsx de teste ficam aqui)
PARENT = os.path.dirname(WORK)                                # automation_padroeira (pai)

# Histórico de faturamento do dia (lido pelo /fechar, persistido para uso futuro).
HIST_DIR = os.path.join(WORK, "historico_faturamento")
HIST_FILE = os.path.join(HIST_DIR, "faturamento_diario.json")

os.makedirs(os.path.join(WORK, "logs"), exist_ok=True)
os.makedirs(HIST_DIR, exist_ok=True)
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
def _normalizar_aamm(texto_bruto: str) -> str:
    """
    Converte uma entrada de período para AAMM (%y%m).

    Aceita:
      - AAMM (ex: 2608)  -> direto
      - MMAA (ex: 0826)  -> convertido (mês=0826[:2], ano=0826[2:])
      - vazio/None       -> assume o período corrente (datetime.now)

    Retorna sempre no formato %y%m.
    """
    if not texto_bruto:
        return datetime.now().strftime("%y%m")
    t = texto_bruto.strip()
    # Se vier como MMAA (mês primeiro, ex: 0826), transpõe para AAMM.
    # Heurística: se os 2 primeiros dígitos forem > 12, é AAMM; senão MMAA.
    if re.fullmatch(r"\d{4}", t):
        mm, aa = t[:2], t[2:]
        if int(mm) > 12:
            return t  # já estava em AAMM
        return aa + mm  # vira AAMM
    return t


def _parse_aamm(texto: str):
    """
    Extrai o período do texto do comando (aceita AAMM ou MMAA).
    Se não houver número de 4 dígitos, assume o período corrente (hoje).
    """
    m = re.search(r"\b(\d{4})\b", texto or "")
    if m:
        return _normalizar_aamm(m.group(1))
    return _normalizar_aamm("")


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


def _fmt_brl(v: float) -> str:
    """Formata um valor float como R$ com separadores pt-BR (vírgula decimal)."""
    if v is None:
        return "—"
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _fmt_num(s: str) -> float:
    """Converte string de valor Saurus ('1.234,56' / '1234.56') em float."""
    if s is None:
        return 0.0
    try:
        return float(str(s).replace(".", "").replace(",", "."))
    except (ValueError, TypeError):
        return 0.0


async def _fechar_dia() -> dict:
    """
    PRIMEIRO comando do operador (/fechar):
      1. ENTRA no Saurus (Playwright) e puxa o relatório de fechamento do DIA DE HOJE.
         Se o relatório do dia já estiver em cache (fechamento_caixa_{data}.txt),
         reaproveita sem reentrar no portal.
      2. LÊ o FATURAMENTO (total do fechamento) para a CONFERÊNCIA DE CAIXA.
      3. ENVIA a mensagem de conferência para o Telegram.
      4. SALVA o relatório (cache em ./fechamentos/ e histórico JSON) para ser
         usado pelo comando seguinte (/finalizar), que o transporta para o Diário/PAD.

    Retorna dict com 'erro' (mensagem) em falha, ou:
        {'erro': None, 'data': 'DD/MM/AAAA', 'aamm': 'AAMM',
         'entrou_saurus': bool, 'do_cache': bool, 'dados': {...}, 'msg': str}
    """
    hoje = datetime.now()
    hoje_iso = hoje.strftime("%Y-%m-%d")
    hoje_br = hoje.strftime("%d/%m/%Y")
    aamm = hoje.strftime("%y%m")

    cortex = cortex_mod.CortexPadroeiraAsync(base_dir=WORK)
    pasta = cortex.pasta_fechamentos
    cache = os.path.join(pasta, f"fechamento_caixa_{hoje_iso}.txt")

    entrou_saurus = False
    do_cache = os.path.exists(cache)

    # 1) Entra no Saurus se não houver relatório do dia em cache.
    if not do_cache:
        if cortex._playwright_disponivel():
            try:
                from extrator_saurus_sessao import extrair_lote_saurus
                logger.info(f"[SAURUS] Entrando no portal para puxar fechamento de {hoje_br}...")
                ok, falhas = await extrair_lote_saurus(
                    [hoje_iso], pasta, headless=cortex._headless_config(),
                    on_progress=lambda i, tot, d, okp: logger.info(
                        f"[PLAYWRIGHT] Baixando fechamento para a data {hoje_br} -> "
                        f"{'OK' if okp else 'FALHA'}"
                    ),
                )
                entrou_saurus = ok > 0
                if entrou_saurus:
                    logger.info(f"[SAURUS] Relatório de {hoje_br} baixado e salvo em {cache}")
            except Exception as e:
                logger.exception(f"[SAURUS] Falha ao entrar no portal Saurus para {hoje_br}")
        else:
            logger.warning("[SAURUS] Playwright indisponível — não foi possível entrar no Saurus.")

    # 2) Lê o relatório (recém-baixado ou em cache).
    dados = cortex.extrair_dados_saurus_por_data(hoje_iso)
    if not dados:
        msg = (f"📊 Faturamento do dia {hoje_br}\n"
               f"⚠️ Não foi possível obter o relatório do Saurus para hoje "
               f"(relatório ausente ou portal indisponível).")
        return {"erro": msg, "data": hoje_br, "aamm": aamm,
                "entrou_saurus": entrou_saurus, "do_cache": do_cache, "dados": None, "msg": msg}

    # 3) Monta a mensagem de conferência de caixa (do relatório do Saurus).
    total = _fmt_num(dados.get("total"))
    dinheiro = _fmt_num(dados.get("dinheiro"))
    credito = _fmt_num(dados.get("credito"))
    debito = _fmt_num(dados.get("debito"))
    clientes = dados.get("clientes", "0")
    kg_ref = dados.get("kg_eq_ref")
    kg_sob = dados.get("kg_eq_sob")

    origem = "cache local" if do_cache else ("portal Saurus" if entrou_saurus else "relatório")
    msg = (
        f"📊 Faturamento do dia {hoje_br}\n"
        f"💰 Faturamento (Total): {_fmt_brl(total)}\n"
        f"💵 Dinheiro: {_fmt_brl(dinheiro)}  |  💳 Crédito: {_fmt_brl(credito)}  |  🏧 Débito: {_fmt_brl(debito)}\n"
        f"🧾 Clientes (Qtd. vendas): {clientes}\n"
        f"📦 Kg Equiv. Refeição: {kg_ref or '—'}  |  Sobremesa: {kg_sob or '—'}\n"
        f"🔎 Fonte: {origem}"
    )
    return {"erro": None, "data": hoje_br, "aamm": aamm,
            "entrou_saurus": entrou_saurus, "do_cache": do_cache, "dados": dados, "msg": msg}


def _salvar_historico_faturamento(registro: dict) -> bool:
    """
    Persiste o faturamento do dia no histórico (JSON) para uso futuro.

    O registro é indexado pela data (DD/MM/AAAA) e sobrescreve o do mesmo dia.
    Retorna True se salvou com sucesso.
    """
    if registro.get("erro"):
        return False
    try:
        historico = {}
        if os.path.exists(HIST_FILE):
            with open(HIST_FILE, "r", encoding="utf-8") as f:
                historico = json.load(f)
        d = registro.get("dados") or {}
        historico[registro["data"]] = {
            "aamm": registro["aamm"],
            "total": _fmt_num(d.get("total")),
            "dinheiro": _fmt_num(d.get("dinheiro")),
            "credito": _fmt_num(d.get("credito")),
            "debito": _fmt_num(d.get("debito")),
            "clientes": d.get("clientes"),
            "kg_eq_ref": d.get("kg_eq_ref"),
            "kg_eq_sob": d.get("kg_eq_sob"),
            "entrou_saurus": registro.get("entrou_saurus", False),
            "salvo_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        with open(HIST_FILE, "w", encoding="utf-8") as f:
            json.dump(historico, f, ensure_ascii=False, indent=2)
        logger.info(f"[HISTORICO] Faturamento de {registro['data']} salvo em {HIST_FILE}")
        return True
    except Exception:
        logger.exception("[HISTORICO] Falha ao salvar faturamento no histórico")
        return False


# ----------------------------------------------------------------------
# Handlers Telegram
# ----------------------------------------------------------------------
@bot.message_handler(commands=['finalizar', 'reconciliar', 'fechar'])
def cmd_finalizar(message):
    """
    Handler único dos comandos de operação.

    /fechar            -> PRIMEIRO comando do operador. Puxa o faturamento do dia,
                          lê para a CONFERÊNCIA DE CAIXA e SALVA NO HISTÓRICO.
                          Apenas leitura + gravação de histórico (não roda pipeline).
    /finalizar [MMAA]  -> CONCLUI o preenchimento e o transporte de dados
                          (Cortex -> Engine -> Balancete Pad). Sem MMAA, assume o
                          dia de hoje; com MMAA, varredura completa do período.
    /reconciliar [MMAA]-> alias de compatibilidade de /finalizar.
    """
    texto = message.text or ""
    chat_id = message.chat.id
    comando = (texto.split()[0].lstrip("/").lower() if texto.split() else "")

    logger.info("[TELEGRAM] Comando recebido do usuário.")

    # /fechar -> entra no Saurus, puxa relatório do dia, lê p/ conferência de
    # caixa, envia e salva no histórico (para o /finalizar transportar depois).
    if comando == "fechar" and not re.search(r"\b\d{4}\b", texto):
        try:
            reg = asyncio.run(_fechar_dia())
            bot.send_message(chat_id, reg["msg"])
            if reg.get("erro"):
                logger.info("[TELEGRAM] Faturamento do dia enviado ao usuário (com aviso).")
            else:
                salvou = _salvar_historico_faturamento(reg)
                logger.info(
                    f"[TELEGRAM] Faturamento do dia enviado"
                    f"{' (entrou no Saurus)' if reg.get('entrou_saurus') else ' (do cache)'}"
                    f" e {'salvo no histórico' if salvou else 'NÃO salvo (erro de histórico)'}. "
                    f"Relatório disponível para /finalizar."
                )
        except Exception as e:
            logger.exception("[TELEGRAM] Erro ao executar /fechar (Saurus)")
            bot.send_message(chat_id, f"⚠️ Erro ao obter faturamento do Saurus: {e}")
        return

    aamm = _parse_aamm(texto)
    escopo = "dia de hoje (AAMM corrente)" if not re.search(r"\b\d{4}\b", texto) else f"período {aamm} (varredura completa)"

    bot.reply_to(message, "🤖 Processando reconciliação Padroeira...\n"
                          f"Escopo: {escopo}")
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
    """/amostra [N] [AAMM|MMAA] — processa apenas N datas pendentes (teste e2e)."""
    texto = message.text or ""
    logger.info("[TELEGRAM] Comando recebido do usuário.")
    partes = texto.split()
    limite = 3
    aamm = None
    for p in partes[1:]:
        if p.isdigit() and int(p) < 100:
            limite = int(p)
        elif re.fullmatch(r"\d{4}", p):
            aamm = _normalizar_aamm(p)
    chat_id = message.chat.id

    bot.reply_to(message, f"🤖 Amostra de {limite} data(s) pendente(s) "
                          f"(período: {aamm or 'hoje/backlog'})...")
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
        "/fechar — ENTRA no Saurus, puxa o RELATÓRIO DO DIA, lê o faturamento para a "
        "conferência de caixa, envia e SALVA o relatório. Use este PRIMEIRO.\n"
        "/finalizar [MMAA] — CONCLUI o preenchimento e o transporte de dados "
        "(Cortex -> Engine -> Balancete) usando os relatórios baixados. "
        "Sem data, processa o DIA DE HOJE.\n"
        "/reconciliar [AAMM] — alias de /finalizar.\n"
        "/amostra [N] [MMAA] — roda N datas pendentes (teste e2e).\n"
    )


# ----------------------------------------------------------------------
# Loop principal — escuta continuamente.
# ----------------------------------------------------------------------
if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("Bot de Reconciliação Padroeira iniciado (modo escuta).")
    logger.info(f"Logs em tempo real: {LOGFILE}")
    logger.info("Comandos: /fechar (entra no Saurus -> relatorio do dia -> historico)  |  /finalizar [MMAA]  |  /reconciliar [AAMM]  |  /amostra [N] [MMAA]")
    logger.info("=" * 70)
    bot.infinity_polling()
