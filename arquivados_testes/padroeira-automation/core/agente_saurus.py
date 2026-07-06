#!/usr/bin/env python
import asyncio
import os
from google import genai
from playwright.async_api import async_playwright

async def extrair_e_analisar_caixa():
    # Inicializa o cliente do Gemini (pega a chave automática do seu .zshrc)
    client = genai.Client()
    
    print("🤖 Iniciando o Chromium tunelado...")
    async with async_playwright() as p:
        # Lança o navegador visível na sua tela do MX
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("🌐 Acessando o painel de retaguarda da Padroeira...")
        await page.goto("https://ands.retaguarda.app/padroeirarestaurante/sistema")
        
        # --- Fluxo de Autenticação Gravado ---
        print("🔐 Efetuando login no sistema...")
        await page.get_by_role("textbox", name="Usuário ou Documento").fill("paulo")
        await page.get_by_role("textbox", name="Senha").fill("270471")
        await page.get_by_role("button", name="Fazer Login").click()
        
        # Aguarda o dashboard carregar
        await page.wait_for_load_state("networkidle")
        
        print("📊 Abrindo a tarefa de Fechamento de Período...")
        await page.locator("#menu1_lblFavoritoMarcado1006-10").click()
        
        # Elemento dentro do iframe principal
        iframe = page.locator("#iframeTarefa1006").content_frame
        
        print("⚙️ Configurando filtros de fechamento...")
        # 1. Clica nos botões de controle para expandir as opções
        await iframe.locator(".SaurusControl_ImageButton.btnBDown").click()
        await iframe.locator(".SaurusControl_ImageButton.btnBFolha").click()
        
        print("⏳ Aguardando a renderização visual dos checkboxes...")
        # Força o script a dar 1.5 segundos para o Saurus abrir o menu na tela
        await asyncio.sleep(1.5)
        
        print("☑️ Selecionando 'Detalhar Produtos' e 'Detalhar Categorias'...")
        # Usamos o seletor exato do container que o gravador usou, garantindo o clique correto
        container_produtos = iframe.locator("#contentBody_cadastro_cookie_fechamento_periodo_chkProdutosDiv")
        await container_produtos.get_by_text("Detalhar Produtos").first.click()
        
        container_categorias = iframe.locator("#contentBody_cadastro_cookie_fechamento_periodo_chkCategoriasDiv")
        await container_categorias.get_by_text("Detalhar Categorias").first.click()
        
        print("⏳ Gerando relatório e aguardando o popup...")
        # Monitora a abertura da nova aba/popup de forma assíncrona
        async with page.expect_popup() as popup_info:
            await iframe.get_by_title("Clique para confirmar as").nth(2).click()
        
        # Captura a nova página gerada
        aba_relatorio = await popup_info.value
        await aba_relatorio.wait_for_load_state("networkidle")
        
        print("🕵️‍♂️ Extraindo os dados financeiros brutos do fechamento...")
        # Captura o texto inteiro do relatório gerado
        dados_caixa_brutos = await aba_relatorio.locator("body").inner_text()
        
        # === SALVANDO EM TEXTO ===
        nome_arquivo_txt = "fechamento_caixa.txt"
        print(f"💾 Salvando os dados extraídos em '{nome_arquivo_txt}'...")
        with open(nome_arquivo_txt, "w", encoding="utf-8") as f:
            f.write(dados_caixa_brutos)
        print("✅ Arquivo de texto gravado com sucesso na pasta do projeto!")
        
        print("🧠 Enviando relatório para análise inteligente do Gemini...")
        
        prompt = f"""
        Você é um analista financeiro sênior especializado em auditoria de restaurantes.
        Analise os dados extraídos do fechamento de período do restaurante 'Padroeira' e gere:
        
        1. Um resumo executivo do faturamento do período (Total vendido, formas de pagamento dominantes).
        2. Alerta de possíveis discrepâncias ou pontos de atenção (se houver dados estranhos).
        3. Destaque das top categorias ou produtos mais vendidos listados.
        
        Dados brutos do sistema:
        {dados_caixa_brutos}
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        print("\n📊 === AUDITORIA DO CAIXA (GEMINI) ===")
        print(response.text)
        print("=======================================\n")
        
        print("Fechando o laboratório em 5 segundos...")
        await asyncio.sleep(5)
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(extrair_e_analisar_caixa())
