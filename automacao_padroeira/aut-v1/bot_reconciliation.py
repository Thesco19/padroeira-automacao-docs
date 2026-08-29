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


def _limpar_processos_orfaos() -> dict:
    """
    Rotina de limpeza de subprocessos Playwright/Chromium residuais e de travas
    temporárias, executada ao final de /finalizar, /reconciliar e /amostra.

    Por que: o Playwright (chromium) pode deixar processos órfãos (especialmente
    em headless, timeouts ou exceções durante a extração), segurando portas e
    travas que atrapalham a próxima execução. Aqui encerramos de forma segura:

      1. SIGTERM primeiro (graceful), depois SIGKILL se ainda estiverem vivos.
      2. Apenas processos cujo nome/linha de comando indicam Chromium/Playwright
         ou o próprio node do Playwright — NUNCA mata processos do usuário.
      3. Remove travas temporárias soltas pelo Chromium em /tmp
         (SingletonLock, SingletonCookie, DevShm) que impedem relançar o browser.

    Retorna um dict de contagem para log/telemetria.
    """
    import signal
    import subprocess

    resumo = {"terminados": 0, "nao_encerrados": 0, "travas_removidas": 0, "erro": None}

    # 1) Descobre processos do Chromium/Playwright via ps (portável em Linux).
    try:
        out = subprocess.run(
            ["ps", "-eo", "pid,comm,args"],
            capture_output=True, text=True, timeout=20,
        ).stdout
    except Exception as e:
        resumo["erro"] = f"falha ao listar processos: {e}"
        logger.warning(f"[CLEANUP] {resumo['erro']}")
        return resumo

    alvos = []
    marcadores = (
        "chromium", "chrome", "headless_shell", "playwright",
        "node",  # o driver do Playwright roda em node
    )
    for linha in out.splitlines():
        campos = linha.split(None, 2)
        if len(campos) < 3:
            continue
        pid_s, comm, args = campos
        args_l = args.lower()
        # Só considera se a linha de comando menciona algo do Chromium/Playwright.
        if not any(m in args_l for m in marcadores):
            continue
        # Evita matar o próprio bot ou processos de usuário legítimos: exige que
        # seja chromium/headless_shell OU node rodando o playwright.
        if "node" in comm.lower() and "playwright" not in args_l:
            continue
        try:
            pid = int(pid_s)
        except ValueError:
            continue
        if pid == os.getpid():
            continue
        alvos.append(pid)

    # 2) Encerra graciosamente (SIGTERM) e, se ainda vivos, SIGKILL.
    for pid in alvos:
        try:
            os.kill(pid, signal.SIGTERM)
            resumo["terminados"] += 1
        except ProcessLookupError:
            pass  # já morreu
        except PermissionError:
            resumo["nao_encerrados"] += 1
        except Exception:
            resumo["nao_encerrados"] += 1

    # Espera um pouco e aplica SIGKILL nos que sobreviveram ao SIGTERM.
    if resumo["terminados"]:
        import time
        time.sleep(2.0)
        for pid in alvos:
            try:
                os.kill(pid, 0)  # ainda existe?
            except ProcessLookupError:
                continue
            except PermissionError:
                # PID de outro usuário: não podemos inspecionar nem matar.
                # Pula (em produção o bot é dono dos processos do Chromium/Playwright).
                resumo["nao_encerrados"] += 1
                continue
            try:
                os.kill(pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass

    # 3) Remove travas temporárias do Chromium em /tmp.
    try:
        for raiz, _, arquivos in os.walk("/tmp"):
            if not any(a in arquivos for a in ("SingletonLock", "SingletonCookie")):
                continue
            for trava in ("SingletonLock", "SingletonCookie", "DevShm"):
                caminho = os.path.join(raiz, trava)
                if os.path.exists(caminho):
                    try:
                        os.remove(caminho)
                        resumo["travas_removidas"] += 1
                    except OSError:
                        pass
    except Exception as e:
        logger.warning(f"[CLEANUP] Falha ao limpar travas em /tmp: {e}")

    logger.info(
        f"[CLEANUP] Processos órfãos: {resumo['terminados']} encerrados, "
        f"{resumo['nao_encerrados']} não encerrados, "
        f"{resumo['travas_removidas']} travas removidas."
    )
    return resumo


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
    """Converte string de valor em float.

    O parser do Córtex já normaliza os valores financeiros para o formato
    ponto-decimal ('595.76', '11469.75'), então NÃO removemos pontos aqui —
    removê-los inflaria o valor ×100 (595.76 -> 59.576). Apenas trocamos
    vírgula por ponto como segurança se algum valor escapar no formato br.
    """
    if s is None:
        return 0.0
    try:
        return float(str(s).replace(",", "."))
    except (ValueError, TypeError):
        return 0.0


async def _fechar_dia() -> dict:
    """
    PRIMEIRO comando do operador (/fechar):
      1. ENTRA no Saurus (Playwright) e puxa o relatório de fechamento do DIA DE HOJE
         em TEMPO REAL. Se o relatório do dia já estiver em cache
         (fechamento_caixa_{data}.txt), ele é APAGADO antes da extração, para que o
         Playwright sempre entre no portal e baixe a foto ATUALIZADA do faturamento
         parcial (e não reaproveite uma foto velha do mesmo dia). Se o Playwright
         estiver indisponível, o cache é mantido como fallback.
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
    tinha_cache = os.path.exists(cache)
    do_cache = tinha_cache

    # 1) ESTRATÉGIA "PARCIAL DO DIA": o /fechar consulta o movimento em tempo
    #    real. Por isso, quando o Playwright está DISPONÍVEL, APAGAMOS o cache do
    #    dia corrente (se existir) ANTES de disparar a extração, para garantir que
    #    o robô ENTRE no portal e baixe a foto ATUALIZADA do faturamento parcial —
    #    e não reaproveite uma foto velha de uma consulta anterior no mesmo dia.
    #    Se o Playwright NÃO estiver disponível, mantemos o cache existente como
    #    fallback (não há como obter foto nova sem o portal).
    if cortex._playwright_disponivel():
        if tinha_cache:
            try:
                os.remove(cache)
                do_cache = False
                logger.info(f"[SAURUS] Cache do dia {hoje_br} removido antes da extração: {cache}")
            except OSError as e:
                logger.warning(f"[SAURUS] Não foi possível remover o cache do dia {hoje_br}: {e}")
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
        logger.warning("[SAURUS] Playwright indisponível — usando cache local (se houver) como fallback.")

    # 2) Lê o relatório (recém-baixado do portal ou, em fallback, do cache).
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

    if entrou_saurus:
        origem = "portal Saurus (foto em tempo real)"
    elif do_cache:
        origem = "cache local (Playwright indisponível)"
    else:
        origem = "relatório"
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
    finally:
        # ETAPA 2: limpa subprocessos Playwright/Chromium órfãos e travas do /tmp
        # ao final de toda execução do pipeline (sucesso ou falha).
        _limpar_processos_orfaos()


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
    finally:
        # ETAPA 2: mesma limpeza de órfãos do /finalizar (o /amostra também roda
        # o pipeline completo, podendo deixar Chromium residuais).
        _limpar_processos_orfaos()


@bot.message_handler(commands=['doctor'])
def cmd_doctor(message):
    """
    /doctor — diagnóstico de saúde em tempo real.

    Lê as últimas 100 linhas de logs/reconciliation.log. Se não houver erro/traceback
    relevante, responde que tudo está operando. Caso contrário, envia o trecho do log
    para a API de IA (Gemini ou OpenAI, conforme a chave presente no .env) e retorna:
      🔍 Diagnóstico do Erro  — explicação em pt-BR do problema.
      🛠️ Prompt para Ajuste    — bloco de código com instruções exatas p/ o agente corrigir.
    """
    chat_id = message.chat.id
    logger.info("[TELEGRAM] Comando recebido do usuário.")

    if not os.path.exists(LOGFILE):
        bot.reply_to(message, "✅ Nenhum log encontrado. Sistemas operando (sem registro de execução ainda).")
        return

    try:
        with open(LOGFILE, "r", encoding="utf-8") as f:
            linhas = f.read().splitlines()
    except Exception as e:
        logger.exception("[DOCTOR] Falha ao ler o log")
        bot.reply_to(message, f"⚠️ Não consegui ler o log: {e}")
        return

    trecho = linhas[-100:]
    texto_log = "\n".join(trecho)

    if not _log_tem_erro_grave(texto_log):
        bot.reply_to(
            message,
            "✅ Todos os sistemas operando normalmente.\n"
            "Nenhum erro encontrado nos logs recentes.",
        )
        return

    bot.reply_to(message, "🔎 Detectei erros nos logs recentes. Consultando a IA para diagnóstico...")
    diag = _diagnosticar_log_com_ia(texto_log)
    bot.send_message(chat_id, diag)


def _log_tem_erro_grave(texto_log: str) -> bool:
    """Detecta erro/traceback/warning relevante no trecho de log."""
    padroes = [
        r"\bERROR\b", r"\bCRITICAL\b", r"\bTraceback\b", r"\bException\b",
        r"\bFalha\b", r"\berro\b", r"FileNotFoundError", r"PermissionError",
        r"TimeoutError", r"ValueError", r"RuntimeError",
    ]
    return any(re.search(p, texto_log) for p in padroes)


def _diagnosticar_log_com_ia(trecho_log: str, max_chars: int = 6000) -> str:
    """
    Envia o trecho de log para a API de IA (Gemini ou OpenAI) e devolve uma
    mensagem formatada para o Telegram com:
      🔍 Diagnóstico do Erro   (explicação em pt-BR)
      🛠️ Prompt para Ajuste     (bloco de código com instruções para o agente corrigir)

    Lê a chave do .env via cortex_mod._ler_env (GEMINI_API_KEY ou OPENAI_API_KEY).
    Se nenhuma chave estiver configurada, devolve o trecho cru para análise manual.
    """
    log_recortado = trecho_log[-max_chars:]
    system = (
        "Você é um engenheiro de software sênior especialista em Python, automação "
        "com Playwright e planilhas (openpyxl). Receberá o trecho final do log de um "
        "bot de reconciliação fiscal. Responda SOMENTE em português do Brasil e no "
        "formato abaixo, sem texto introdutório adicional:\n\n"
        "🔍 Diagnóstico do Erro:\n<explicação curta e direta da causa raiz em 2-4 frases>\n\n"
        "🛠️ Prompt para Ajuste:\n```text\n<instruções exatas e passo a passo que um agente "
        "de IA deve seguir para corrigir a falha no código, citando o arquivo e a função "
        "quando identificável>\n```"
    )
    user = f"Trecho do log de erro:\n\n{log_recortado}"

    # Resolve a chave (GEMINI tem prioridade; cai para OPENAI).
    gemini_key = cortex_mod._ler_env("GEMINI_API_KEY", WORK) or cortex_mod._ler_env("GEMINI_API_KEY", PARENT)
    openai_key = cortex_mod._ler_env("OPENAI_API_KEY", WORK) or cortex_mod._ler_env("OPENAI_API_KEY", PARENT)

    resposta = None
    try:
        if gemini_key:
            resposta = _chamar_gemini(gemini_key, system, user)
        elif openai_key:
            resposta = _chamar_openai(openai_key, system, user)
    except Exception as e:
        logger.exception("[DOCTOR] Falha ao consultar a API de IA")
        resposta = None

    if resposta:
        return resposta

    # Fallback: sem chave de IA ou erro de API — devolve o log para análise manual.
    aviso = (
        "⚠️ Não foi possível consultar a IA (sem GEMINI_API_KEY/OPENAI_API_KEY no .env "
        "ou falha na API). Trecho do log para análise manual:\n\n"
    )
    return aviso + f"```\n{log_recortado[-2500:]}\n```"


def _chamar_gemini(api_key: str, system: str, user: str) -> str:
    """Chama a Gemini REST API (generativelanguage) via requests.

    O modelo 'gemini-1.5-flash' foi DESCONTINUADO (a API passou a retornar 404
    em 29/08/2026). Usamos 'gemini-3.1-flash-lite' — leve e barato, suficiente
    para o diagnóstico curto de log do /doctor. Se um dia este também sair, basta
    trocar aqui; a lista de modelos válidos vem de GET /v1beta/models.
    """
    import requests
    model = "gemini-3.1-flash-lite"
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        f"?key={api_key}"
    )
    payload = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1500},
    }
    try:
        resp = requests.post(url, json=payload, timeout=60)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        # Erro HTTP (ex.: 404 modelo descontinuado, 429 quota, 5xx) — NÃO deve ser
        # um Traceback estourado no log, senão o próprio /doctor se auto-sinaliza
        # como erro grave. Logamos como warning e deixamos o caller cair no fallback.
        logger.warning(f"[DOCTOR] Gemini retornou HTTP error: {e} | body: {resp.text[:300]}")
        raise
    data = resp.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def _chamar_openai(api_key: str, system: str, user: str) -> str:
    """Chama a OpenAI Chat Completions REST API via requests."""
    import requests
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.2,
        "max_tokens": 1500,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


@bot.message_handler(commands=['start', 'help'])
def cmd_help(message):
    bot.reply_to(
        message,
        "Comandos disponíveis:\n"
        "/fechar — consulta o FATURAMENTO PARCIAL DO DIA em tempo real: APAGA o cache do dia e ENTRA no Saurus para baixar a foto atualizada, lê para a conferência de caixa, envia e SALVA o relatório. Use este PRIMEIRO.\n"
        "/finalizar [MMAA] — CONCLUI o preenchimento e o transporte de dados "
        "(Cortex -> Engine -> Balancete) usando os relatórios baixados e, ao final, "
        "LIMPA os processos Playwright/Chromium órfãos. Sem data, processa o DIA DE HOJE.\n"
        "/reconciliar [AAMM] — alias de /finalizar.\n"
        "/amostra [N] [AAMM] — roda N datas pendentes (teste e2e), com cleanup de órfãos ao final.\n"
        "/doctor — lê os logs recentes; se houver erro, consulta a IA (Gemini/OpenAI) e "
        "retorna diagnóstico + prompt de ajuste. Configure GEMINI_API_KEY ou OPENAI_API_KEY no .env.\n"

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
