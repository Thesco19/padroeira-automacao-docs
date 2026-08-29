#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrator de Fechamento de Caixa do Portal Saurus - por data (Playwright).

Recupera o relatório de fechamento de caixa de UMA data específica no portal
Saurus e o salva em:
    {pasta_saida}/fechamento_caixa_{AAAA-MM-DD}.txt

Credenciais (opcionais via .env, com fallback):
    SAURUS_URL  - URL do sistema
    SAURUS_USER - usuário
    SAURUS_PASS - senha

Seletores validados contra o portal real em 08/ago/2026.
Os campos de data são inputs HTML5 type='date' (formato ISO YYYY-MM-DD),
localizados no TOPO do formulário de Fechamento de Período.
"""

import asyncio
import os
from datetime import datetime
from typing import Optional

# ----------------------------------------------------------------------
# Configurações sensíveis (lidas de .env, com defaults)
# ----------------------------------------------------------------------
DEFAULT_URL = "https://ands.retaguarda.app/padroeirarestaurante/sistema"
DEFAULT_USER = "Sandra"
DEFAULT_PASS = "270471"

# ----------------------------------------------------------------------
# Seletores REAIS do portal Saurus (descobertos via Playwright 08/ago/2026)
#
# Campos de data: inputs type='date' no topo do formulário.
# Formato aceito: ISO YYYY-MM-DD (ex: "2026-06-24").
#
# Checkboxes de configuração do relatório (popup):
#   chkProdutos   → Detalhar Produtos
#   chkCategorias → Detalhar Categorias
# ----------------------------------------------------------------------
SEL_DATA_INICIAL = "#contentBody_txtDInicial"
SEL_DATA_FINAL   = "#contentBody_txtDFinal"
SEL_ATUALIZAR    = "#contentBody_btnAtualizarMovimento"

# Botões de expansão de opções
SEL_BTN_BDOWN  = ".SaurusControl_ImageButton.btnBDown"
SEL_BTN_BFOLHA = ".SaurusControl_ImageButton.btnBFolha"

# Checkboxes do popup de configuração
SEL_CHK_PRODUTOS   = "#contentBody_cadastro_cookie_fechamento_periodo_chkProdutos"
SEL_CHK_CATEGORIAS = "#contentBody_cadastro_cookie_fechamento_periodo_chkCategorias"


def _resolver_executable_path() -> Optional[str]:
    """Resolve o binário do Chromium a usar.

    Ordem: 1. PLAYWRIGHT_CHROMIUM_PATH (env/.env)  2. /usr/bin/chromium
           3. None (Playwright usa o seu próprio download).

    Fallback gracioso: retorna None se nenhum existir, NÃO quebra o launch.
    (Confirmado em 08/ago/2026: headless do servidor já funciona com o default.)
    """
    cfg = _carregar_controle_amb()
    candidatos = []
    env_path = cfg.get("chromium_path") or os.environ.get("PLAYWRIGHT_CHROMIUM_PATH")
    if env_path:
        candidatos.append(env_path)
    candidatos.append("/usr/bin/chromium")
    for c in candidatos:
        if c and os.path.exists(c):
            return c
    return None


def _carregar_controle_amb() -> dict:
    """Lê .env (leve, sem python-dotenv) do diretório do script."""
    cfg = {
        "url": DEFAULT_URL,
        "user": DEFAULT_USER,
        "pass": DEFAULT_PASS,
    }
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(env_path):
        return cfg
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                if not linha or linha.startswith("#") or "=" not in linha:
                    continue
                chave, _, valor = linha.partition("=")
                chave = chave.strip()
                valor = valor.strip().strip('"').strip("'")
                chave_upp = chave.upper()
                if chave_upp == "SAURUS_URL":
                    cfg["url"] = valor
                elif chave_upp in ("SAURUS_USER", "SAURUS_USERNAME", "SAURUS_USUARIO"):
                    cfg["user"] = valor
                elif chave_upp in ("SAURUS_PASS", "SAURUS_PASSWORD", "SAURUS_SENHA"):
                    cfg["pass"] = valor
    except Exception as e:
        print(f"[pdv_saurus] Aviso ao ler .env: {e}")
    return cfg


async def extrair_fechamento_saurus(
    data_iso: str,
    pasta_saida: str,
    headless: bool = False,
    timeout_ms: int = 45000,
) -> Optional[str]:
    """
    Extrai o relatório de fechamento de caixa do Saurus para a data `data_iso`
    (formato 'AAAA-MM-DD') e grava em `{pasta_saida}/fechamento_caixa_{data_iso}.txt`.

    Fluxo validado contra o portal real:
      1. Login
      2. Abre Fechamento de Período
      3. Seta Data Inicial e Data Final (inputs type='date', formato ISO)
      4. Clica "Atualizar" para recarregar dados do período
      5. Expande opções de detalhamento
      6. Marca checkboxes (Produtos, Categorias)
      7. Gera relatório → captura popup → extrai texto

    Retorna o caminho do arquivo salvo, ou None em caso de falha.
    """
    from playwright.async_api import async_playwright  # import tardio (playwright é opcional)

    cfg = _carregar_controle_amb()
    out_path = os.path.join(pasta_saida, f"fechamento_caixa_{data_iso}.txt")
    os.makedirs(pasta_saida, exist_ok=True)

    # Binário do Chromium: fallback gracioso (None = default do Playwright).
    exe = _resolver_executable_path()
    launch_kwargs = {"headless": headless}
    if exe:
        launch_kwargs["executable_path"] = exe

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(**launch_kwargs)
            context = await browser.new_context()
            page = await context.new_page()

            # 1. Login
            await page.goto(cfg["url"], wait_until="load", timeout=timeout_ms)
            await page.get_by_role("textbox", name="Usuário ou Documento").fill(cfg["user"])
            await page.get_by_role("textbox", name="Senha").fill(cfg["pass"])
            await page.get_by_role("button", name="Fazer Login").click()
            await page.wait_for_load_state("networkidle")

            # 2. Abre Fechamento de Período
            await page.locator("#menu1_lblFavoritoMarcado1006-10").click()
            await page.wait_for_load_state("networkidle")

            iframe = page.locator("#iframeTarefa1006").content_frame
            if iframe is None:
                raise RuntimeError("Iframe de fechamento não localizado")

            # 3. Seta Data Inicial e Data Final (formato ISO: AAAA-MM-DD)
            await iframe.locator(SEL_DATA_INICIAL).fill(data_iso)
            await iframe.locator(SEL_DATA_FINAL).fill(data_iso)

            # 4. Clica "Atualizar" para recarregar dados do período
            await iframe.locator(SEL_ATUALIZAR).click()
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(1.0)

            # 5. Expande opções de detalhamento
            await iframe.locator(SEL_BTN_BDOWN).click()
            await asyncio.sleep(1.0)
            await iframe.locator(SEL_BTN_BFOLHA).click()
            await asyncio.sleep(1.5)

            # 6. Marca checkboxes de forma IDEMPOTENTE
            #    O Saurus usa checkboxes customizados; .check() no input não funciona,
            #    e o estado dos checkboxes PERSISTE entre cliques de Atualizar na mesma
            #    sessão. Se já estiver marcado, clicar no div DESMARCA (toggle).
            #    Por isso: ler o estado do input e só clicar se NÃO estiver marcado.
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

            # 7. Gera relatório e captura o popup
            async with page.expect_popup() as popup_info:
                await iframe.get_by_title("Clique para confirmar as").nth(2).click()
            relatorio = await popup_info.value
            await relatorio.wait_for_load_state("networkidle")

            texto = await relatorio.locator("body").inner_text()

            # 8. Salva o arquivo por data
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(texto)

            await context.close()
            await browser.close()
            return out_path

    except Exception as e:
        print(f"[pdv_saurus] Falha para {data_iso}: {e}")
        if os.path.exists(out_path):
            os.remove(out_path)
        return None


if __name__ == "__main__":
    import sys
    data = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
    pasta = sys.argv[2] if len(sys.argv) > 2 else "fechamentos"
    resultado = asyncio.run(extrair_fechamento_saurus(data, pasta, headless=False))
    print(f"Resultado: {resultado}")
