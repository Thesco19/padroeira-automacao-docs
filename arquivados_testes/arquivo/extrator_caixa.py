import re

# ==============================================================================
# CONFIGURAÇÃO DE REGRAS DE NEGÓCIO (Insira aqui os preços praticados no dia)
# ==============================================================================
PRECO_KG_REFEICAO = 69.90   # Preço do KG do buffet salgado / refeição
PRECO_KG_SOBREMESA = 89.90  # Preço do KG da sobremesa quilo / confeitaria
# ==============================================================================

def extrair_dados_relatorio(caminho_arquivo):
    faturamento_total = 0.0
    qtd_clientes = 0
    
    # Valores de quantidade (KG) reais extraídos do relatório
    kg_balanca_real = 0.0
    
    # Valores financeiros extraídos do relatório
    valor_doces_unitarios = 0.0
    valor_pratos_executivos = 0.0

    with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
        linhas = arquivo.readlines()

    for linha in linhas:
        # 1. Captura de dados globais do cabeçalho
        if "Total Vendido" in linha:
            match = re.search(r"Total Vendido\s*:\s*([\d\.,]+)", linha)
            if match:
                faturamento_total = float(match.group(1).replace('.', '').replace(',', '.'))
        
        if "Qtd. Vendas" in linha:
            match = re.search(r"Qtd\. Vendas\s*:\s*(\d+)", linha)
            if match:
                qtd_clientes = int(match.group(1))

        # 2. Captura dinâmica nas tabelas de Subgrupos (*)
        if "*" in linha:
            partes = linha.split()
            
            # Verificação estrutural mínima de colunas
            if len(partes) >= 3:
                # No seu sistema: penúltimo elemento é Qtd/Peso, último é o Valor R$
                qtd_str = partes[-2].replace('.', '').replace(',', '.')
                valor_str = partes[-1].replace('.', '').replace(',', '.')
                
                try:
                    qtd_convertida = float(qtd_str)
                    valor_convertido = float(valor_str)
                    
                    if "BALANÇA" in linha:
                        kg_balanca_real = qtd_convertida
                    elif "DOCES" in linha:
                        valor_doces_unitarios = valor_convertido
                    elif "PRATOS EXECUTIVOS" in linha:
                        valor_pratos_executivos = valor_convertido
                except ValueError:
                    pass

    # ==============================================================================
    # PROCESSAMENTO DAS MÉTRICAS EQUIVALENTES
    # ==============================================================================
    # 1. Sobremesa Equivalente em KG (Faturamento dos Doces Unitários / Preço do KG)
    kg_sobremesa_equivalente = valor_doces_unitarios / PRECO_KG_SOBREMESA
    
    # 2. Refeição Equivalente em KG (Balança Real + (Faturamento Executivos / Preço do KG))
    kg_refeicao_equivalente = kg_balanca_real + (valor_pratos_executivos / PRECO_KG_REFEICAO)

    return {
        "faturamento_total": faturamento_total,
        "qtd_clientes": qtd_clientes,
        "kg_refeicao_total": kg_refeicao_equivalente,
        "kg_sobremesa_total": kg_sobremesa_equivalente
    }

# --- Execução do Teste Local ---
dados = extrair_dados_relatorio("Visualização de Movimentação.txt")

print("==================================================")
print("       RELATÓRIO CONSOLIDADO DE FECHAMENTO        ")
print("==================================================")
print(f"Nº de Clientes Atendidos : {dados['qtd_clientes']}")
print(f"Faturamento Bruto Total  : R$ {dados['faturamento_total']:.2f}")
print(f"Total Refeição Produzida : {dados['kg_refeicao_total']:.3f} KG (Balança + Executivos)")
print(f"Total Doces/Confeitaria  : {dados['kg_sobremesa_total']:.3f} KG (Equivalente)")
print("==================================================")
