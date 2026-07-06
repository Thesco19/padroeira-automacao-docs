import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://ands.retaguarda.app/padroeirarestaurante/expirou/c2lzdGVtYQ==")
    page.get_by_role("textbox", name="Usuário ou Documento").click()
    page.get_by_role("textbox", name="Usuário ou Documento").fill("papp")
    page.get_by_role("textbox", name="Usuário ou Documento").click()
    page.get_by_role("textbox", name="Usuário ou Documento").fill("paulo")
    page.get_by_role("textbox", name="Senha").click()
    page.get_by_role("textbox", name="Senha").click()
    page.get_by_role("textbox", name="Senha").fill("270471")
    page.get_by_role("button", name="Fazer Login").click()
    page.locator("#menu1_lblFavoritoMarcado1006-10").click()
    page.locator("#iframeTarefa1006").content_frame.locator(".SaurusControl_ImageButton.btnBDown").click()
    page.locator("#iframeTarefa1006").content_frame.locator(".SaurusControl_ImageButton.btnBFolha").click()
    page.locator("#iframeTarefa1006").content_frame.locator("#contentBody_cadastro_cookie_fechamento_periodo_chkProdutosDiv").get_by_text("Detalhar Produtos").click()
    page.locator("#iframeTarefa1006").content_frame.locator("#contentBody_cadastro_cookie_fechamento_periodo_chkProdutosDiv").get_by_text("Detalhar Produtos").click()
    page.locator("#iframeTarefa1006").content_frame.locator("#contentBody_cadastro_cookie_fechamento_periodo_chkProdutosDiv").get_by_text("Detalhar Produtos").click()
    page.locator("#iframeTarefa1006").content_frame.locator("#contentBody_cadastro_cookie_fechamento_periodo_chkCategoriasDiv").get_by_text("Detalhar Categorias").click()
    page.locator("#iframeTarefa1006").content_frame.locator("#contentBody_cadastro_cookie_fechamento_periodo_chkCategoriasDiv").get_by_text("Detalhar Categorias").click()
    page.locator("#iframeTarefa1006").content_frame.locator("#contentBody_cadastro_cookie_fechamento_periodo_chkCategoriasDiv").get_by_text("Detalhar Categorias").click()
    with page.expect_popup() as page1_info:
        page.locator("#iframeTarefa1006").content_frame.get_by_title("Clique para confirmar as").nth(2).click()
    page1 = page1_info.value
    page.close()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
