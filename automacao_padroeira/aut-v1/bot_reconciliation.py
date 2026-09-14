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
                             (Cortex -> Engine -> Balancete). Sem MMAA, assume o dia
                             de hoje (AAMM corrente). Se MMAA informado, faz a varredura
                             completa do período. /reconciliar é mantido como alias.
    /amostra [N] [MMAA]  -> roda apenas N datas pendentes (default 3) — útil p/ teste e2e.
    /tabela              -> exibe a tabela de preços vigente (valores do Kg Equivalente).
    /doctor              -> diagnóstico de saúde via IA dos logs recentes.

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
import time
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

# Captura os loggers internos do telebot (polling/409/network) e do urllib3
# para o MESMO arquivo/handler, dando visibilidade a falhas silenciosas de
# getUpdates que o processamento dos comandos não veria.
for _nome_extra in ("telebot", "TeleBot"):
    _lg_extra = logging.getLogger(_nome_extra)
    _lg_extra.setLevel(logging.INFO)
    _lg_extra.handlers = []
    _lg_extra.addHandler(_fh)
    _lg_extra.addHandler(_sh)
_lg_urllib3 = logging.getLogger("urllib3")
_lg_urllib3.setLevel(logging.WARNING)
_lg_urllib3.handlers = []
_lg_urllib3.addHandler(_fh)
_lg_urllib3.addHandler(_sh)


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
backup_mod = _carregar("backup_padroeira", os.path.join(WORK, "backup_padroeira.py"))

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

# --- Auto-healing: webhook órfão bloqueia polling ---
# Se um serviço antigo registrou um webhook neste token e foi desligado, o
# Telegram responde 409 Conflict e o bot não recebe NENHUM comando via
# getUpdates. Ao iniciar, removemos qualquer webhook ativo que não seja
# o nosso (reset seguro: nenhuma instância deste bot registra webhook).
try:
    wh = bot.get_webhook_info()
    wh_url = getattr(wh, "url", "") or ""
    if wh_url:
        logger.warning("Webhook órfão detectado no token (%s) — removendo...", wh_url)
        bot.remove_webhook()
        logger.info("Webhook removido com sucesso. Polling pode prosseguir.")
    else:
        logger.info("Nenhum webhook ativo no token (ok).")
except Exception as e:
    logger.warning("Auto-healing webhook: não foi possível checar/remover: %s", e)


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


def _run_async(coro):
    """
    Executa uma corrotina fora do loop do Telegram (handler síncrono).

    CORREÇÃO P3 (refatorar.md 4c): os handlers do telebot são funções SÍNCRONAS.
    Chamar `asyncio.run` direto levanta `RuntimeError: loop already running` se
    já houver um loop ativo na thread (ex.: execução dentro de um runner async,
    testes ou migração futura). Rodamos a corrotina numa THREAD dedicada com seu
    próprio loop, o que é seguro em qualquer contexto.
    """
    import threading
    resultado = {}
    excecao = {}

    def _wrapper():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            resultado["valor"] = loop.run_until_complete(coro)
        except Exception as e:  # captura para fora da thread
            excecao["erro"] = e
        finally:
            loop.close()

    t = threading.Thread(target=_wrapper, daemon=True)
    t.start()
    t.join()
    if "erro" in excecao:
        raise excecao["erro"]
    return resultado.get("valor")


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


def _parse_data_br(texto: str):
    """
    Tenta extrair uma data no formato DD/MM/AAAA (ou DD/MM/AA) de uma string.

    Ano com 2 dígitos é interpretado como 20XX (ex: 26 -> 2026).
    Retorna (data_iso, data_br, aamm) ou (None, None, None) se não encontrar.
    """
    m = re.search(r"\b(\d{2})/(\d{2})/(\d{4})\b|\b(\d{2})/(\d{2})/(\d{2})\b", texto or "")
    if not m:
        return None, None, None
    dia = m.group(1) or m.group(4)
    mes = m.group(2) or m.group(5)
    ano = m.group(3) or m.group(6)
    ano = "20" + ano if len(ano) == 2 else ano
    try:
        dt = datetime(int(ano), int(mes), int(dia))
    except ValueError:
        return None, None, None
    return dt.strftime("%Y-%m-%d"), dt.strftime("%d/%m/%Y"), dt.strftime("%y%m")


async def _fechar_dia(data_iso: str = None) -> dict:
    """
    PRIMEIRO comando do operador (/fechar):
      1. ENTRA no Saurus (Playwright) e puxa o relatório de fechamento do dia
         informado (ou de HOJE se data_iso for None) em TEMPO REAL. Se o
         relatório do dia já estiver em cache (fechamento_caixa_{data}.txt),
         ele é APAGADO antes da extração, para que o Playwright sempre entre
         no portal e baixe a foto ATUALIZADA do faturamento parcial (e não
         reaproveite uma foto velha do mesmo dia). Se o Playwright estiver
         indisponível, o cache é mantido como fallback.
      2. LÊ o FATURAMENTO (total do fechamento) para a CONFERÊNCIA DE CAIXA.
      3. ENVIA a mensagem de conferência para o Telegram.
      4. SALVA o relatório (cache em ./fechamentos/ e histórico JSON) para ser
         usado pelo comando seguinte (/finalizar), que o transporta para o Diário/PAD.

    Args:
        data_iso: data no formato 'AAAA-MM-DD'. Se None, usa a data de hoje.

    Retorna dict com 'erro' (mensagem) em falha, ou:
        {'erro': None, 'data': 'DD/MM/AAAA', 'aamm': 'AAMM',
         'entrou_saurus': bool, 'do_cache': bool, 'dados': {...}, 'msg': str}
    """
    if data_iso:
        try:
            dt = datetime.strptime(data_iso, "%Y-%m-%d")
        except ValueError:
            return {"erro": f"Data inválida: {data_iso}", "data": data_iso,
                    "aamm": None, "entrou_saurus": False, "do_cache": False,
                    "dados": None, "msg": f"⚠️ Data inválida: {data_iso}"}
    else:
        dt = datetime.now()
    hoje_iso = dt.strftime("%Y-%m-%d")
    hoje_br = dt.strftime("%d/%m/%Y")
    aamm = dt.strftime("%y%m")

    cortex = cortex_mod.CortexPadroeiraAsync(base_dir=WORK)
    pasta = cortex.pasta_fechamentos
    cache = os.path.join(pasta, f"fechamento_caixa_{hoje_iso}.txt")

    entrou_saurus = False
    tinha_cache = os.path.exists(cache)
    do_cache = tinha_cache

    # 1) ESTRATÉGIA DE EXTRAÇÃO:
    #    - DIA CORRENTE (hoje): o /fechar consulta o movimento PARCIAL em tempo
    #      real. Quando o Playwright está disponível, APAGAMOS o cache do dia (se
    #      existir) e baixamos a foto ATUALIZADA — nunca reaproveitar uma foto
    #      velha de consulta anterior no mesmo dia.
    #    - DIAS PASSADOS: o arquivo em cache é o fechamento DEFINITIVO (relatório
    #      completo do Saurus). Reentrar no portal é desnecessário (latência e
    #      risco de apagar um cache bom) — usamos o cache direto. Só entramos no
    #      portal quando NÃO há cache local.
    hoje_real = datetime.now().date()
    eh_hoje = dt.date() == hoje_real
    playwright_ok = cortex._playwright_disponivel()

    if playwright_ok:
        # SEMPRE tentamos reextrair do portal quando o Playwright está disponível
        # (hoje: foto em tempo real; datas antigas: relatório definitivo atualizado,
        # reparseado com as regras vigentes de preço/kg). O cache local existe APENAS
        # como fallback: se a renovação falhar, o relatório antigo continua no lugar.
        try:
            from extrator_saurus_sessao import extrair_lote_saurus
            motivo = "puxar fechamento" if eh_hoje else "atualizar/recalcular"
            logger.info(f"[SAURUS] {motivo} de {hoje_br} no portal...")
            ok, falhas = await extrair_lote_saurus(
                [hoje_iso], pasta, headless=cortex._headless_config(),
                on_progress=lambda i, tot, d, okp: logger.info(
                    f"[PLAYWRIGHT] Baixando fechamento para a data {hoje_br} -> "
                    f"{'OK' if okp else 'FALHA'}"
                ),
            )
            entrou_saurus = ok > 0
            if entrou_saurus:
                do_cache = False
                logger.info(f"[SAURUS] Relatório de {hoje_br} baixado e salvo em {cache}")
            elif not tinha_cache:
                logger.warning(f"[SAURUS] Sem cache de {hoje_br} e sem renovação via portal.")
            else:
                logger.warning(f"[SAURUS] Renovação via portal falhou p/ {hoje_br}; usando cache como fallback.")
        except Exception as e:
            logger.exception(f"[SAURUS] Falha ao entrar no portal Saurus para {hoje_br}")
    else:
        logger.warning("[SAURUS] Playwright indisponível — usando cache local (se houver) como fallback.")

    # 2) Lê o relatório (recém-baixado do portal ou, em fallback, do cache).
    # ITEM 1 (refatorar.md): extrair_dados_saurus_por_data faz I/O de disco
    # (lê o .txt do fechamento) — offload para thread do executor.
    dados = await asyncio.to_thread(cortex.extrair_dados_saurus_por_data, hoje_iso)
    if not dados:
        msg = (f"📊 Faturamento do dia {hoje_br}\n"
               f"⚠️ Não foi possível obter o relatório do Saurus para hoje "
               f"(relatório ausente ou portal indisponível).")
        return {"erro": msg, "data": hoje_br, "aamm": aamm,
                "entrou_saurus": entrou_saurus, "do_cache": do_cache, "dados": None, "msg": msg}

    # Memória de cálculo do Kg Equivalente (auditoria em logs): grava o passo-a-
    # passo usado por _parsear_fechamento (preços por código, pesos/quantidades,
    # valores de executivos/doces e o divisor do dia) para conferência posterior.
    dbg = dados.get("_kg_eq_debug") or {}
    if dbg:
        logger.info(
            f"[KG_EQ] Memória de cálculo {hoje_br}: "
            f"vkg={dbg.get('vkg')} | "
            f"quilo 385={dbg.get('peso_buf_c385')}kg x R${dbg.get('preco_quilo_semana')} | "
            f"386={dbg.get('peso_buf_c386')}kg x R${dbg.get('preco_quilo_fds')} | "
            f"grill 387={dbg.get('peso_grill')}kg | "
            f"a_vontade 383 x {dbg.get('qtd_av_c383')}un | "
            f"c130 x {dbg.get('qtd_av_c130')}un | "
            f"c384 x {dbg.get('qtd_cs_c384')}un | "
            f"c131 x {dbg.get('qtd_av_c131')}un | "
            f"executivos=R${dbg.get('val_exec')} | "
            f"sobremesa 425={dbg.get('peso_sob_c425')}kg x R${dbg.get('preco_c425')} | "
            f"426={dbg.get('peso_sob_c426')}kg x R${dbg.get('preco_c426')} | "
            f"doces=R${dbg.get('val_doces')} | "
            f"fat_ref=R${dbg.get('fat_ref')} -> kg_eq_ref={dados.get('kg_eq_ref')} | "
            f"fat_sob=R${dbg.get('fat_sob')} -> kg_eq_sob={dados.get('kg_eq_sob')}"
        )

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
        if not playwright_ok:
            origem = "cache local (Playwright indisponível)"
        elif eh_hoje:
            origem = "cache local (renovação via portal falhou)"
        else:
            origem = "cache local (fechamento definitivo do dia)"
    else:
        origem = "relatório"
    msg = (
        f"📊 Faturamento do dia {hoje_br}\n"
        f"💰 Faturamento (Total): {_fmt_brl(total)}\n"
        f"💵 Dinheiro: {_fmt_brl(dinheiro)}  |  💳 Crédito: {_fmt_brl(credito)}  |  🏧 Débito: {_fmt_brl(debito)}\n"
        f"🧾 Clientes (Qtd. vendas): {clientes}\n"
        f"📦 Kg Equiv. Refeição: {(kg_ref or '—').replace('.', ',')}  |  Sobremesa: {(kg_sob or '—').replace('.', ',')}\n"
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

    /fechar [DD/MM/AAAA] -> PRIMEIRO comando do operador. Puxa o faturamento do
                          dia informado (ou hoje se sem data), lê para a CONFERÊNCIA
                          DE CAIXA e SALVA NO HISTÓRICO. Aceita data BR como opcional.
    /finalizar [MMAA]  -> CONCLUI o preenchimento e o transporte de dados
                          (Cortex -> Engine -> Balancete Pad). Sem MMAA, assume o
                          dia de hoje; com MMAA, varredura completa do período.
    /reconciliar [MMAA]-> alias de compatibilidade de /finalizar.
    """
    texto = message.text or ""
    chat_id = message.chat.id
    comando = (texto.split()[0].lstrip("/").lower() if texto.split() else "")

    logger.info("[TELEGRAM] Comando recebido do usuário.")

    # /fechar [DD/MM/AAAA] -> entra no Saurus, puxa relatório do dia informado
    # (ou hoje se sem data), lê p/ conferência de caixa, envia e salva no
    # histórico (para o /finalizar transportar depois).
    # Aceita data BR (DD/MM/AAAA) como argumento opcional.
    if comando == "fechar":
        data_iso, data_br, _aamm_fechar = _parse_data_br(texto)
        label_data = data_br if data_br else "hoje"
        try:
            reg = _run_async(_fechar_dia(data_iso=data_iso))
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
        resultado = _run_async(_rodar(aamm=aamm))
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
        resultado = _run_async(_rodar(aamm=aamm, limite=limite))
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


# ----------------------------------------------------------------------
# Auditoria de cálculo (/auditar) — snapshot SQLite com datas DD/MM/AAAA
# ----------------------------------------------------------------------
def _fmt_num_br(v: float, dec: int = 2) -> str:
    """Formata número com separador pt-BR (vírgula decimal e ponto de milhar)."""
    return f"{v:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _parse_data_auditoria(texto: str):
    """
    Converte a entrada de data do /auditar para (data_iso, data_br):
      - vazio            -> (None, None)  [caller usa hoje ou último fechamento]
      - 0409 / 04/09     -> 2026-09-04 / 04/09/2026 (mês direto, ano corrente)
      - 04/09/2026       -> 2026-09-04 / 04/09/2026
      - 04/09/26         -> 2026-09-04 / 04/09/2026
    Retorna (None, None) se não reconhecer um formato válido.
    """
    t = (texto or "").strip()
    if not t:
        return None, None

    m = re.fullmatch(r"(\d{2})/?(\d{2})(?:/(\d{4}))?(?:/(\d{2}))?", t)
    if m:
        dia = int(m.group(1))
        mes = int(m.group(2))
        if m.group(3):
            ano = int(m.group(3))
        elif m.group(4):
            ano = 2000 + int(m.group(4))
        else:
            ano = datetime.now().year
        try:
            dt = datetime(ano, mes, dia)
        except ValueError:
            return None, None
        return dt.strftime("%Y-%m-%d"), dt.strftime("%d/%m/%Y")

    # Fallback: procura DD/MM/AAAA na string (ex.: '/auditar 04/09/2026')
    data_iso, data_br, _aamm = _parse_data_br(texto)
    return data_iso, data_br


def _entrada_display_def(snapshot: dict) -> str:
    """Sempre exibe a data no padrão BR DD/MM/AAAA (nunca ISO)."""
    br = (snapshot.get("detalhamento") or {}).get("data_br") or snapshot.get("data_br")
    if br:
        return br
    try:
        return datetime.strptime(snapshot["data_iso"], "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        return snapshot.get("data_iso", "")


def _formatar_linha_item(item: dict) -> str:
    """Monta uma linha de item de auditoria: Cód X (NOME): QTD UN x R$ P = R$ F."""
    fat = item.get("faturamento")
    preco = item.get("preco_unitario") or 0.0
    qtd = item.get("quantidade") or 0.0
    un = item.get("unidade") or "UN"
    # Quantidade formatada em pt-BR (virgula) — KG com 3 casas, UN inteiro.
    if un.upper() == "KG":
        qtd_s = _fmt_num_br(qtd, 3)
    else:
        qtd_s = str(int(qtd)) if qtd == int(qtd) else _fmt_num_br(qtd, 3)
    if fat is not None:
        return (f"• Cód {item['codigo']} ({item['nome']}): {qtd_s} {un} "
                f"x {_fmt_brl(preco)} = {_fmt_brl(fat)}")
    return (f"• Cód {item['codigo']} ({item['nome']}): {qtd_s} {un} x {_fmt_brl(preco)}")


def _montar_mensagem_auditoria(snapshot: dict, origem: str) -> str:
    """Monta a mensagem do /auditar no padrão amigável, com datas DD/MM/AAAA."""
    det = snapshot.get("detalhamento") or {}
    data_br = _entrada_display_def(snapshot)

    linhas = [f"🔍 AUDITORIA DE CÁLCULO — {data_br}", ""]

    vkg = snapshot.get("preco_kg_divisor")
    fat_ref = snapshot.get("faturamento_refeicao")
    fat_sob = snapshot.get("faturamento_sobremesa")
    kg_ref = snapshot.get("kg_eq_refeicao")
    kg_sob = snapshot.get("kg_eq_sobremesa")
    sub_exec = det.get("subcategoria_exec") or 0.0
    sub_doces = det.get("subcategoria_doces") or 0.0

    # Grupo Refeição (Linha 3)
    linhas.append("📊 GRUPO REFEIÇÃO (Linha 3):")
    itens_ref = det.get("grupo_refeicao") or []
    for item in itens_ref:
        linhas.append(_formatar_linha_item(item))
    if sub_exec:
        linhas.append(f"• Subcategoria PRATOS EXECUTIVOS: {_fmt_brl(sub_exec)}")
    linhas.append("───────────────")
    linhas.append(f"Faturamento Refeição: {_fmt_brl(fat_ref)}")
    linhas.append(f"Divisor do Dia (R$/kg): {_fmt_brl(vkg)}/kg")
    linhas.append(f"➜ Kg Eq Refeição = {_fmt_brl(fat_ref)} / {_fmt_brl(vkg)} = {_fmt_num_br(kg_ref, 3)} KG")
    linhas.append("")

    # Grupo Sobremesa / Doces (Linha 4)
    linhas.append("🍰 GRUPO SOBREMESA / DOCES (Linha 4):")
    itens_sob = det.get("grupo_sobremesa") or []
    for item in itens_sob:
        linhas.append(_formatar_linha_item(item))
    if sub_doces:
        linhas.append(f"• Subcategoria DOCES: {_fmt_brl(sub_doces)}")
    linhas.append("───────────────")
    linhas.append(f"Faturamento Sobremesa: {_fmt_brl(fat_sob)}")
    linhas.append(f"Divisor do Dia (R$/kg): {_fmt_brl(vkg)}/kg")
    linhas.append(f"➜ Kg Eq Sobremesa = {_fmt_brl(fat_sob)} / {_fmt_brl(vkg)} = {_fmt_num_br(kg_sob, 3)} KG")
    linhas.append("")

    linhas.append(f"💾 Origem: {origem}.")
    return "\n".join(linhas)


def _auditar_dia_completo(data_iso: str, data_br: str) -> str:
    """
    Lógica do /auditar para uma data:

      1. Busca snapshot no SQLite via `backup_mod.obter_auditoria_calculo`.
      2. Se não existir no banco, calcula a partir de
         fechamentos/fechamento_caixa_{data_iso}.txt (se existir), salva no
         SQLite e exibe.
      3. Se não houver .txt de fechamento, retorna mensagem de ausência.

    Retorna a mensagem pronta para o Telegram (datas em DD/MM/AAAA).
    """
    snapshot = backup_mod.obter_auditoria_calculo(data_iso)
    if snapshot:
        return _montar_mensagem_auditoria(snapshot, "Snapshot de auditoria do banco SQLite")

    # Sem snapshot: tenta calcular à partir do fechamento real (sem fallback).
    cortex = cortex_mod.CortexPadroeiraAsync(base_dir=WORK)
    dados = cortex.extrair_dados_saurus_por_data(data_iso)
    if not dados:
        caminho = os.path.join(cortex.pasta_fechamentos, f"fechamento_caixa_{data_iso}.txt")
        if not os.path.exists(caminho):
            return (f"⚠️ Não há fechamento salvo para {data_br} e nenhum snapshot no "
                    f"banco. Execute /fechar {data_br} para gerar o relatório do dia.")
        return f"⚠️ Não foi possível calcular a auditoria para {data_br}."

    # Acabou de calcular via _parsear_fechamento -> snapshot foi salvo. Reconsulta.
    snapshot = backup_mod.obter_auditoria_calculo(data_iso)
    if snapshot:
        return _montar_mensagem_auditoria(snapshot, "Fechamento real (./fechamentos) processado agora")
    return f"⚠️ Não foi possível gerar a auditoria para {data_br}."


@bot.message_handler(commands=['auditar'])
def cmd_auditar(message):
    """
    /auditar [data] — exibe a memória de cálculo do Kg Equivalente de um dia.

    A data pode ser omitida (usa hoje ou o último fechamento processado),
    ou informada em formato BR:
      /auditar 0409 | /auditar 04/09 | /auditar 04/09/2026 | /auditar 04/09/26

    Sempre responde com a data no padrão DD/MM/AAAA. Prefere o snapshot no
    SQLite; se ausente, calcula a partir do fechamento real e salva.
    """
    chat_id = message.chat.id
    logger.info("[TELEGRAM] Comando recebido do usuário (/auditar).")

    texto = message.text or ""
    data_iso, data_br = _parse_data_auditoria(texto[texto.find(" ") + 1:] if " " in texto else "")

    # Sem data explícita -> tenta hoje, depois o último fechamento disponível.
    if data_iso is None:
        hoje_iso = datetime.now().strftime("%Y-%m-%d")
        hoje_br = datetime.now().strftime("%d/%m/%Y")
        # 1) snapshot/hoje
        if backup_mod.obter_auditoria_calculo(hoje_iso):
            return bot.send_message(chat_id, _montar_mensagem_auditoria(
                backup_mod.obter_auditoria_calculo(hoje_iso),
                "Snapshot de auditoria do banco SQLite",
            ))
        # 2) fechamento de hoje existe?
        cortex = cortex_mod.CortexPadroeiraAsync(base_dir=WORK)
        caminho_hoje = os.path.join(cortex.pasta_fechamentos, f"fechamento_caixa_{hoje_iso}.txt")
        if os.path.exists(caminho_hoje):
            return bot.send_message(chat_id, _auditar_dia_completo(hoje_iso, hoje_br))
        # 3) último fechamento datado disponível
        import glob as _glob
        arquivos = sorted(_glob.glob(os.path.join(cortex.pasta_fechamentos, "fechamento_caixa_*.txt")))
        if arquivos:
            ultimo = os.path.basename(arquivos[-1]).replace("fechamento_caixa_", "").replace(".txt", "")
            ultimo_br = datetime.strptime(ultimo, "%Y-%m-%d").strftime("%d/%m/%Y")
            return bot.send_message(chat_id, _auditar_dia_completo(ultimo, ultimo_br))
        return bot.send_message(
            chat_id,
            "⚠️ Nenhum fechamento encontrado. Execute /fechar para gerar o relatório do dia.",
        )

    msg = _auditar_dia_completo(data_iso, data_br)
    bot.send_message(chat_id, msg)


@bot.message_handler(commands=['tabela'])
def cmd_tabela(message):
    """Exibe a tabela de preços vigente (valores usados pelo sistema de Kg Equivalente)."""
    from datetime import date as _date
    try:
        import config_precos as cp
    except ImportError:
        bot.reply_to(message, "⚠️ Não foi possível carregar config_precos.py")
        return

    hoje = _date.today()
    eh_sabado = hoje.weekday() == 5
    posicao = "NOVA" if hoje >= cp.DATA_REAJUSTE else "ANTIGA"

    if eh_sabado:
        valor_kg_hoje = cp.valor_kg_dia(hoje)
        label_kg = f"Sábado"
    else:
        valor_kg_hoje = cp.valor_kg_dia(hoje)
        label_kg = f"Dia útil"

    linhas = [
        "📋 *Tabela de Preços — Padroeira*",
        f"📅 Data de hoje: {hoje.strftime('%d/%m/%Y')} ({label_kg})",
        f"📌 Tabela vigente: *{posicao}* (desde {cp.DATA_REAJUSTE.strftime('%d/%m/%Y')})",
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        "🍽️ *Refeição à Quilo (Buffet)*",
        f"  • Seg-Sex (tabela antiga): R$ {cp.REFEICAO_KG_PADRAO_ANTIGO:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        f"  • Sábado  (tabela antiga): R$ {cp.REFEICAO_KG_SABADOS_ANTIGO:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        f"  • Seg-Sex (tabela nova):   R$ {cp.REFEICAO_KG_PADRAO_NOVO:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        f"  • Sábado  (tabela nova):   R$ {cp.REFEICAO_KG_SABADOS_NOVO:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        "",
        "🔥 *Grill*",
        f"  • Preço fixo: R$ {cp.REFEICAO_KG_GRILL:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        "",
        "🍽️ *Coma a Vontade*",
        f"  • Seg-Sex:         R$ {cp.REFEICAO_A_VONTADE:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        f"  • Seg-Sex c/ Doce: R$ {cp.REFEICAO_COM_SOBREMESA:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        f"  • Fim de semana:         R$ {cp.COMA_A_VONTADE_FDS:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        f"  • Fim de semana c/ Doce: R$ {cp.COMA_A_VONTADE_FDS_DOCE:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        "",
        "📦 *Outros*",
        f"  • To Save: R$ {cp.REFEICAO_TO_SAVE:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        f"  • Pavê Pote (seg):    R$ {cp.PAVE_POTE_SEMANA:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        f"  • Pavê Pote (sáb):    R$ {cp.PAVE_POTE_SABADO:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        f"  • Gelatina Colorida:  R$ {cp.GELATINA_COLORIDA:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        f"⚡ *KG do dia (hoje):* R$ {valor_kg_hoje:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        f"🔧 *Reajuste automático em:* {cp.DATA_REAJUSTE.strftime('%d/%m/%Y')}",
    ]

    if cp.OVERRIDE_KG_POR_DATA:
        linhas.append("")
        linhas.append("🔒 *Overrides por data:*")
        for dt, preco in sorted(cp.OVERRIDE_KG_POR_DATA.items()):
            linhas.append(f"  • {dt}: R$ {preco:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    bot.send_message(message.chat.id, "\n".join(linhas), parse_mode="Markdown")


@bot.message_handler(commands=['start', 'help'])
def cmd_help(message):
    bot.reply_to(
        message,
        "Comandos disponíveis:\n"
        "/fechar [DD/MM/AAAA] — consulta o FATURAMENTO do dia em tempo real. "
        "Sem data, usa hoje. Com data BR (ex: /fechar 05/09/2026 ou /fechar 05/09/26), "
        "puxa essa data. "
        "APAGA o cache do dia e ENTRA no Saurus para baixar a foto atualizada, "
        "lê para a conferência de caixa, envia e SALVA o relatório.\n"
        "/finalizar [MMAA] — CONCLUI o preenchimento e o transporte de dados "
        "(Cortex -> Engine -> Balancete) usando os relatórios baixados e, ao final, "
        "LIMPA os processos Playwright/Chromium órfãos. Sem data, processa o DIA DE HOJE.\n"
        "/reconciliar [AAMM] — alias de /finalizar.\n"
        "/amostra [N] [AAMM] — roda N datas pendentes (teste e2e), com cleanup de órfãos ao final.\n"
        "/tabela — exibe a tabela de preços vigente (valores usados pelo sistema de Kg Equivalente).\n"
        "/auditar [data] — exibe a memória de cálculo do Kg Equivalente (US/REFEIÇÃO/SOBREMESA). "
        "Data opcional em BR (0409, 04/09, 04/09/2026). Usa snapshot no SQLite ou o fechamento real.\n"
        "/doctor — lê os logs recentes; se houver erro, consulta a IA (Gemini/OpenAI) e "
        "retorna diagnóstico + prompt de ajuste. Configure GEMINI_API_KEY ou OPENAI_API_KEY no .env.\n"

    )


# ----------------------------------------------------------------------
# Catch-all: registra QUALQUER update que chegue e não case com handlers
# acima. Registrado por último para só disparar quando nada mais casar.
# Diagnóstico: se esta linha imprimir, o update chegou ao processo; se nem
# esta nem um handler específico imprimir, o polling não está entregando.
# ----------------------------------------------------------------------
@bot.message_handler(func=lambda m: True)
def _catch_all_messages(message):
    logger.info(
        "[TELEGRAM] (catch-all) update recebido: text=%r from=%s chat=%s",
        getattr(message, "text", None),
        getattr(getattr(message, "from_user", None), "username", None),
        getattr(getattr(message, "chat", None), "id", None),
    )


# ----------------------------------------------------------------------
# Loop principal — escuta continuamente.
# ----------------------------------------------------------------------
if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("Bot de Reconciliação Padroeira iniciado (modo escuta).")
    logger.info(f"Logs em tempo real: {LOGFILE}")
    logger.info("Comandos: /fechar [DD/MM/AAAA]  |  /finalizar [MMAA]  |  /reconciliar [AAMM]  |  /amostra [N] [AAMM]  |  /tabela  |  /doctor")
    logger.info("=" * 70)
    while True:
        try:
            logger.info("[POLLING] Conectando ao Telegram (infinity_polling)...")
            bot.infinity_polling(timeout=25, long_polling_timeout=25)
            logger.info("[POLLING] infinity_polling retornou (inesperado); reiniciando em 5s...")
        except KeyboardInterrupt:
            logger.info("[POLLING] Interrompido pelo operador.")
            break
        except Exception:
            logger.exception("[POLLING] infinity_polling encerrou com erro; reconectando em 5s...")
            time.sleep(5)
