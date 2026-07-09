import os
import sys
from openai import OpenAI

# Inicializa apontando para o seu LiteLLM local do Docker
client = OpenAI(
    base_url="http://127.0.0.1:8000/v1",
    api_key="sk-teco-lab" # Chave definida no seu docker-compose
)

print("📂 Lendo o contexto dos scripts locais...")
arquivos = ["cortex_padroeira.py", "engine_consolidacao.py", "motor_balancete.py"]
contexto_codigo = ""

for arq in arquivos:
    if os.path.exists(arq):
        with open(arq, "r", encoding="utf-8") as f:
            contexto_codigo += f"\n\n--- ARQUIVO: {arq} ---\n" + f.read()
    else:
        print(f"⚠️ Aviso: {arq} não encontrado no diretório atual.")

prompt_mestre = f"""
Atue como Engenheiro de Software Sênior. Reestruture os 3 scripts abaixo aplicando a Arquitetura de Reconciliação Assíncrona V2 conforme a especificação oficial: https://docs.google.com/document/d/1g6g2D1xkmf_ksKpcgDtWRehbsOTP_U-XBTXO4s8MF9k/edit?usp=drive_web. 

Regras estritas:
1) Crie uma pasta 'mock_box/' local simulando o Caixa 2 preenchido até 06 de Julho de 2026 com a Sangria na linha 42, o Diário atrasado em 28 de Junho e o Balancete parado no dia 20. Altere temporariamente os scripts para testar nesse mock.
2) O bot deve aceitar os inputs textuais livres 'fechar' e 'ok'.
3) O engine deve expandir colunas horizontais no Md se o Caixa 2 estiver mais adiantado, copiando verticalmente a Sangria (Linha 42) e preservando as fórmulas das linhas 14 e 40.
4) O motor deve varrer o Md usando o Faturamento (Linha 37) como âncora para atualizar o Ba (Pad2607.xlsx) de forma retroativa, mapeando a Sangria para a Coluna R e forçando a fórmula de SUM na coluna Q.

Trabalhe por etapas e retorne o código completo reestruturado ou os passos de alteração.

CONTEXTO DOS CODIGOS ATUAIS:
{contexto_codigo}
"""

print("🚀 Enviando payload para o LiteLLM (Groq Llama-3.3)...")
try:
    response = client.chat.completions.create(
        model="claude-3-5-sonnet", # Nome mapeado no seu config.yaml
        messages=[{"role": "user", "content": prompt_mestre}]
    )
    
    print("\n--- RESPOSTA DO AGENTE ---")
    print(response.choices[0].message.content)
    
except Exception as e:
    print(f"❌ Erro na comunicação com o LiteLLM: {e}")
