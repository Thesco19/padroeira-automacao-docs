import os
from playwright.sync_api import sync_playwright

print(f"DISPLAY detectado pelo SSH: {os.environ.get('DISPLAY')}")

with sync_playwright() as p:
    # Abre o modo codegen nativo pelo motor do Python
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://ands.retaguarda.app/padroeirarestaurante/sistema")
    
    # Pausa a execução abrindo o Inspector visual na sua tela
    page.pause()

