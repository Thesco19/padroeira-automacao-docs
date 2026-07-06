import asyncio
import os
from google import genai

async def rodar_agente():
    # 1. Inicializa o cliente do Gemini usando a nova biblioteca oficial
    # Ela vai buscar automaticamente a variável de ambiente GEMINI_API_KEY
    client = genai.Client()

    print("🤖 Iniciando o motor do navegador isolado...")
    
    # 2. Abre o Playwright e o Chromium em modo VISUAL (headless=False)
    # Graças ao seu túnel SSH -X, a janela vai brotar na tela do MX Linux!
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Alvo de teste: Uma página simples de notícias de tecnologia ou o próprio Google
        url_teste = "https://news.ycombinator.com"
        print(f"🌐 Navegando até: {url_teste}")
        await page.goto(url_teste)
        
        # Espera a página carregar os elementos principais
        await page.wait_for_load_state("networkidle")
        
        print("🕵️‍♂️ Extraindo o conteúdo bruto da página (sem cosméticos)...")
        # Pegamos apenas o texto visível da página, ignorando tags CSS/Imagens pesadas
        conteudo_bruto = await page.locator("body").inner_text()
        
        print("🧠 Enviando dados para o cérebro do Gemini analisar...")
        
        # 3. Prompt para o Gemini atuar como o analista do agente
        prompt = f"""
        Você é o cérebro de um agente autônomo. Analise o conteúdo textual extraído de uma página web
        e faça um resumo executivo dos 3 pontos mais importantes que você encontrou.
        
        Conteúdo da página:
        {conteudo_bruto}
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash', # Modelo rápido e ideal para tarefas agênticas
            contents=prompt,
        )
        
        print("\n📊 === VEREDITO DO GEMINI ===")
        print(response.text)
        print("=============================\n")
        
        print("Aguardando 10 segundos para você ver a janela no MX antes de fechar...")
        await asyncio.sleep(10)
        await browser.close()

# Dispara o loop assíncrono
asyncio.run(rodar_agente())
