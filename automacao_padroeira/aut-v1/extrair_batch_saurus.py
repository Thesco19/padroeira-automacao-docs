#!/usr/bin/env python3
"""
Extração em batch de fechamentos do Saurus.
Reutiliza UMA sessão de login para todas as datas, com delay entre consultas
para evitar alarme de segurança do portal.

Uso:
    python3 extrair_batch_saurus.py [--start DATA] [--delay SEGUNDOS] [--headless]
"""
import asyncio
import argparse
import glob
import os
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pdv_saurus_extractor import (
    _carregar_controle_amb,
    SEL_DATA_INICIAL, SEL_DATA_FINAL, SEL_ATUALIZAR,
    SEL_BTN_BDOWN, SEL_BTN_BFOLHA,
    SEL_CHK_PRODUTOS, SEL_CHK_CATEGORIAS,
)
from cortex_padroeira_async import _iterar_cabecalho, CortexPadroeiraAsync
from openpyxl import load_workbook

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAIXA2 = os.path.join(BASE_DIR, "Movto_cx2.xlsx")
PASTA_FECH = os.path.join(BASE_DIR, "fechamentos")


def datas_movto_cx2() -> list[str]:
    """Extrai todas as datas únicas da linha 1 do Movto_cx2.xlsx."""
    wb = load_workbook(CAIXA2, data_only=True)
    ws = wb.active
    datas = set()
    for _, v in _iterar_cabecalho(ws, inicio=2):
        if isinstance(v, datetime):
            datas.add(v.strftime("%Y-%m-%d"))
    wb.close()
    return sorted(datas)


def datas_com_fechamento() -> set[str]:
    """Retorna conjunto de datas que já possuem arquivo de fechamento."""
    existentes = set()
    for f in glob.glob(os.path.join(PASTA_FECH, "fechamento_caixa_*.txt")):
        base = os.path.basename(f).replace("fechamento_caixa_", "").replace(".txt", "")
        if base != "_legado_":
            existentes.add(base)
    return existentes


def datas_com_fechamento_incompleto() -> list[str]:
    """Retorna datas cujo fechamento existe mas NÃO contém a seção PRODUTOS VENDIDOS.

    Esses arquivos foram extraídos corretamente no Saurus mas sem os dados de
    detalhamento de produtos (PRODUTOS VENDIDOS / REFEICAO QUILO / SOBREMESA QUILO),
    o que causa linhas 3/4 do Movto_diario ficarem zeradas.
    """
    incompletas = []
    for f in sorted(glob.glob(os.path.join(PASTA_FECH, "fechamento_caixa_*.txt"))):
        base = os.path.basename(f).replace("fechamento_caixa_", "").replace(".txt", "")
        if base == "_legado_":
            continue
        try:
            with open(f, encoding="utf-8") as fh:
                conteudo = fh.read()
            if "PRODUTOS VENDIDOS" not in conteudo:
                incompletas.append(base)
        except Exception:
            pass
    return incompletas


async def extrair_todas(
    datas: list[str],
    delay: float = 4.0,
    headless: bool = True,
    timeout_ms: int = 45000,
):
    """
    Extrai fechamentos para lista de datas reutilizando UMA sessão.
    Delay entre cada consulta para não disparar alarme.
    """
    from playwright.async_api import async_playwright

    cfg = _carregar_controle_amb()
    os.makedirs(PASTA_FECH, exist_ok=True)

    ok = 0
    falhas = 0
    total = len(datas)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context()
        page = await context.new_page()

        # Login único
        print(f"[login] Conectando ao Saurus...")
        await page.goto(cfg["url"], wait_until="load", timeout=timeout_ms)
        await page.get_by_role("textbox", name="Usuário ou Documento").fill(cfg["user"])
        await page.get_by_role("textbox", name="Senha").fill(cfg["pass"])
        await page.get_by_role("button", name="Fazer Login").click()
        await page.wait_for_load_state("networkidle")
        print("[login] OK")

        # Abre Fechamento de Período uma vez
        await page.locator("#menu1_lblFavoritoMarcado1006-10").click()
        await page.wait_for_load_state("networkidle")

        iframe = page.locator("#iframeTarefa1006").content_frame
        if iframe is None:
            print("ERRO: iframe não encontrado")
            await browser.close()
            return

        async def expandir_e_marcar():
            """Expande opções e marca checkboxes IDEMPOTENTEMENTE.

            O estado dos checkboxes PERSISTE entre iterações na mesma sessão.
            O 'Atualizar' NÃO reseta os checkboxes. Se já estiverem marcados,
            clicar no div DESMARCA (toggle). Por isso, lemos o estado do input
            e só clicamos se NÃO estiver marcado (garante estado ON).
            """
            from pdv_saurus_extractor import SEL_CHK_PRODUTOS, SEL_CHK_CATEGORIAS

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
            out_path = os.path.join(PASTA_FECH, f"fechamento_caixa_{data_iso}.txt")

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

                # Salva
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(texto)

                ok += 1
                # Log compacto a cada 10
                if ok % 10 == 0 or i == total:
                    print(f"  [{i}/{total}] {ok} OK, {falhas} falhas — último: {data_iso}")
                else:
                    print(f"  [{i}/{total}] OK {data_iso}")

            except Exception as e:
                falhas += 1
                print(f"  [{i}/{total}] FALHA {data_iso}: {e}")
                # Se perdeu a sessão, tenta reconectar
                if "Target page" in str(e) or "closed" in str(e).lower():
                    print("  [reconectando sessão...]")
                    try:
                        await page.goto(cfg["url"], wait_until="load", timeout=timeout_ms)
                        await page.get_by_role("textbox", name="Usuário ou Documento").fill(cfg["user"])
                        await page.get_by_role("textbox", name="Senha").fill(cfg["pass"])
                        await page.get_by_role("button", name="Fazer Login").click()
                        await page.wait_for_load_state("networkidle")
                        await page.locator("#menu1_lblFavoritoMarcado1006-10").click()
                        await page.wait_for_load_state("networkidle")
                        iframe = page.locator("#iframeTarefa1006").content_frame
                        print("  [sessão reconectada]")
                    except Exception as re:
                        print(f"  [reconexão falhou: {re}] — parando")
                        break

            # Delay entre consultas
            if i < total:
                await asyncio.sleep(delay)

        await context.close()
        await browser.close()

    print(f"\n=== RESUMO ===")
    print(f"Total: {total} | OK: {ok} | Falhas: {falhas}")
    return ok, falhas


async def main():
    parser = argparse.ArgumentParser(description="Extração batch de fechamentos Saurus")
    parser.add_argument("--start", help="Data inicial AAAA-MM-DD (padrão: todas as pendentes)")
    parser.add_argument("--delay", type=float, default=4.0, help="Delay entre consultas (segundos, padrão=4)")
    parser.add_argument("--headless", action="store_true", default=True, help="Rodar sem display (padrão)")
    parser.add_argument("--no-headless", dest="headless", action="store_false", help="Rodar com display")
    parser.add_argument("--fix-incomplete", action="store_true",
                        help="Reprocessa apenas fechamentos existentes que estão incompletos "
                             "(sem PRODUTOS VENDIDOS). Útil após correção de extração.")
    args = parser.parse_args()

    todas = datas_movto_cx2()

    # --- Modo correção: reprocessa apenas os incompletos (toggle idempotente) ---
    if args.fix_incomplete:
        pendentes = datas_com_fechamento_incompleto()
        print(f"MODO FIX: reprocessando {len(pendentes)} fechamentos incompletos")
        print(f"Delay entre consultas: {args.delay}s")
        print(f"Tempo estimado:        ~{len(pendentes) * (args.delay + 5) / 60:.0f} min")
        print()
        if not pendentes:
            print("Nenhum fechamento incompleto!")
            return
        await extrair_todas(pendentes, delay=args.delay, headless=args.headless)
        return

    # --- Modo normal: pendentes (completo) ---
    existentes = datas_com_fechamento()
    pendentes = [d for d in todas if d not in existentes]

    if args.start:
        pendentes = [d for d in pendentes if d >= args.start]

    print(f"Datas no Movto_cx2:    {len(todas)}")
    print(f"Fechamentos existentes:{len(existentes)}")
    print(f"Pendentes:             {len(pendentes)}")
    print(f"Delay entre consultas: {args.delay}s")
    print(f"Tempo estimado:        ~{len(pendentes) * (args.delay + 5) / 60:.0f} min")
    print()

    if not pendentes:
        print("Nenhuma data pendente!")
        return

    await extrair_todas(pendentes, delay=args.delay, headless=args.headless)


if __name__ == "__main__":
    asyncio.run(main())
