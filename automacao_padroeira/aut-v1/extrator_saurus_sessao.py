#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrator de Fechamentos do Saurus - SESSÃO ÚNICA (reaproveitada).

Versão comprovadamente funcional no ambiente (264 relatórios, 0 falhas,
headless em 08/ago/2026). Diferente de `pdv_saurus_extractor.extrair_fechamento_saurus`
(que faz login + launch + close POR DATA), esta função reutiliza UMA única
sessão de login para todas as datas, com delay entre consultas para não
disparar alarme de segurança do portal.

O elo "bot escuta -> orquestra" (cortex/async/engine/balancete) usa ESTA função
para extrair múltiplas pendentes de forma robusta.

Uso:
    from extrator_saurus_sessao import extrair_lote_saurus
    ok, falhas = await extrair_lote_saurus(
        datas=["2026-08-04","2026-08-05","2026-08-06"],
        pasta_saida="fechamentos", headless=True, delay=4.0
    )
"""

import asyncio
import os
from datetime import datetime
from typing import List, Optional, Tuple

# Reaproveita credenciais e seletores já validados do extrator unitário.
from pdv_saurus_extractor import (
    _carregar_controle_amb,
    _resolver_executable_path,
    SEL_DATA_INICIAL, SEL_DATA_FINAL, SEL_ATUALIZAR,
    SEL_BTN_BDOWN, SEL_BTN_BFOLHA,
    SEL_CHK_PRODUTOS, SEL_CHK_CATEGORIAS,
)

DEFAULT_DELAY = 4.0
DEFAULT_TIMEOUT_MS = 45000


async def extrair_lote_saurus(
    datas: List[str],
    pasta_saida: str,
    headless: bool = True,
    delay: float = DEFAULT_DELAY,
    timeout_ms: int = DEFAULT_TIMEOUT_MS,
    executable_path: Optional[str] = None,
    on_progress=None,
) -> Tuple[int, int]:
    """
    Extrai fechamentos para a lista de datas reutilizando UMA sessão de browser.

    Args:
        datas: lista de datas ISO (AAAA-MM-DD) a extrair.
        pasta_saida: diretório onde salvar fechamento_caixa_{data}.txt.
        headless: roda sem display (padrão True em servidor).
        delay: segundos entre consultas (evita alarme de segurança).
        timeout_ms: timeout de navegação.
        executable_path: binário do Chromium (fallback gracioso; None = default Playwright).
        on_progress: callback(i, total, data_iso, ok) opcional p/ log/live updates.

    Retorna (ok, falhas).
    """
    from playwright.async_api import async_playwright

    cfg = _carregar_controle_amb()
    os.makedirs(pasta_saida, exist_ok=True)

    # Resolve o binário do Chromium (gracioso: None mantém o default do Playwright).
    exe = executable_path or _resolver_executable_path()
    launch_kwargs = {"headless": headless}
    if exe:
        launch_kwargs["executable_path"] = exe

    ok = 0
    falhas = 0
    total = len(datas)

    async with async_playwright() as p:
        browser = await p.chromium.launch(**launch_kwargs)
        context = await browser.new_context()
        page = await context.new_page()

        # Login único
        await page.goto(cfg["url"], wait_until="load", timeout=timeout_ms)
        await page.get_by_role("textbox", name="Usuário ou Documento").fill(cfg["user"])
        await page.get_by_role("textbox", name="Senha").fill(cfg["pass"])
        await page.get_by_role("button", name="Fazer Login").click()
        await page.wait_for_load_state("networkidle")

        # Abre Fechamento de Período uma vez
        await page.locator("#menu1_lblFavoritoMarcado1006-10").click()
        await page.wait_for_load_state("networkidle")

        iframe = page.locator("#iframeTarefa1006").content_frame
        if iframe is None:
            await browser.close()
            raise RuntimeError("Iframe de fechamento não localizado no portal Saurus")

        async def expandir_e_marcar():
            """Expande opções e marca checkboxes IDEMPOTENTEMENTE (estado persiste na sessão)."""
            await iframe.locator(SEL_BTN_BDOWN).click()
            await asyncio.sleep(1.0)
            await iframe.locator(SEL_BTN_BFOLHA).click()
            await asyncio.sleep(1.5)
            for sel_input, sel_div, texto in (
                (SEL_CHK_PRODUTOS,
                 "#contentBody_cadastro_cookie_fechamento_periodo_chkProdutosDiv", "Detalhar Produtos"),
                (SEL_CHK_CATEGORIAS,
                 "#contentBody_cadastro_cookie_fechamento_periodo_chkCategoriasDiv", "Detalhar Categorias"),
            ):
                try:
                    if not await iframe.locator(sel_input).is_checked():
                        await iframe.locator(sel_div).get_by_text(texto).first.click()
                except Exception:
                    pass
            await asyncio.sleep(0.5)

        for i, data_iso in enumerate(datas, 1):
            out_path = os.path.join(pasta_saida, f"fechamento_caixa_{data_iso}.txt")
            sucesso = False
            try:
                # Seta datas
                await iframe.locator(SEL_DATA_INICIAL).fill(data_iso)
                await iframe.locator(SEL_DATA_FINAL).fill(data_iso)

                # Atualiza (recarrega dados do período)
                await iframe.locator(SEL_ATUALIZAR).click()
                await page.wait_for_load_state("networkidle")
                await asyncio.sleep(1.0)

                # Expande opções + marca checkboxes (o Atualizar resetou o estado)
                await expandir_e_marcar()

                # Gera relatório
                async with page.expect_popup() as popup_info:
                    await iframe.get_by_title("Clique para confirmar as").nth(2).click()
                relatorio = await popup_info.value
                await relatorio.wait_for_load_state("networkidle")

                texto = await relatorio.locator("body").inner_text()
                await relatorio.close()

                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(texto)

                ok += 1
                sucesso = True

            except Exception as e:
                falhas += 1
                # Se perdeu a sessão, tenta reconectar uma vez antes de desistir.
                if "Target page" in str(e) or "closed" in str(e).lower():
                    try:
                        await page.goto(cfg["url"], wait_until="load", timeout=timeout_ms)
                        await page.get_by_role("textbox", name="Usuário ou Documento").fill(cfg["user"])
                        await page.get_by_role("textbox", name="Senha").fill(cfg["pass"])
                        await page.get_by_role("button", name="Fazer Login").click()
                        await page.wait_for_load_state("networkidle")
                        await page.locator("#menu1_lblFavoritoMarcado1006-10").click()
                        await page.wait_for_load_state("networkidle")
                        iframe = page.locator("#iframeTarefa1006").content_frame
                    except Exception:
                        break

            if on_progress:
                try:
                    on_progress(i, total, data_iso, sucesso)
                except Exception:
                    pass

            # Delay entre consultas
            if i < total:
                await asyncio.sleep(delay)

        await context.close()
        await browser.close()

    return ok, falhas


if __name__ == "__main__":
    import sys
    import glob as _glob

    alvo = sys.argv[1] if len(sys.argv) > 1 else "fechamentos"
    pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), alvo)
    # Usa todas as datas pendentes do Movto_cx2 se nenhum arg de datas for dado.
    from cortex_padroeira_async import _iterar_cabecalho, CortexPadroeiraAsync
    from openpyxl import load_workbook

    c = CortexPadroeiraAsync()
    pend = c.pendentes or []
    if not pend:
        cx2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Movto_cx2.xlsx")
        wb = load_workbook(cx2, data_only=True)
        ws = wb.active
        datas = set()
        for _, v in _iterar_cabecalho(ws, inicio=2):
            if isinstance(v, datetime):
                datas.add(v.strftime("%Y-%m-%d"))
        pend = sorted(datas)
    print(f"Extraindo {len(pend)} datas em sessão única...")
    res = asyncio.run(extrair_lote_saurus(pend, pasta, headless=True))
    print(f"Resultado: {res}")
