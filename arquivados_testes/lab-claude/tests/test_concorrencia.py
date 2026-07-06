#!/usr/bin/env python3
import os
import sys
import time
import threading
import shutil
import logging
from pathlib import Path
import subprocess
from openpyxl import Workbook

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_concorrencia.log'),
        logging.StreamHandler()
    ]
)

# Caminhos dos arquivos mock
MOCK_MOVTO_CX1 = 'mock_movto_cx1.xlsx'
MOCK_PAD_06_2026 = 'mock_Pad_06_2026.xlsx'
SCRIPT_CONSOLIDADOR = '../scripts/consolidador_excel.py'

def criar_arquivos_mock():
    """Cria os arquivos mock necessários para o teste."""
    # Criar arquivo mock_movto_cx1.xlsx
    wb1 = Workbook()
    ws1 = wb1.active
    ws1['A1'] = 'Dados de Movimento'
    wb1.save(MOCK_MOVTO_CX1)

    # Criar arquivo mock_Pad_06_2026.xlsx
    wb2 = Workbook()
    ws2 = wb2.active
    ws2['A1'] = 'Dados Padrão'
    wb2.save(MOCK_PAD_06_2026)

    logging.info(f"Arquivos mock criados: {MOCK_MOVTO_CX1} e {MOCK_PAD_06_2026}")

def bloquear_arquivo():
    """Simula o bloqueio do arquivo por um processo externo."""
    try:
        # Abrir o arquivo em modo de escrita exclusiva
        with open(MOCK_PAD_06_2026, 'wb') as f:
            logging.info(f"Arquivo {MOCK_PAD_06_2026} bloqueado em modo de escrita exclusiva")
            # Manter o arquivo bloqueado por 30 segundos
            time.sleep(30)
    except Exception as e:
        logging.error(f"Erro ao bloquear arquivo: {e}")

def executar_consolidador():
    """Executa o script consolidador_excel.py com os arquivos mock."""
    try:
        # Construir o comando para executar o script consolidador
        cmd = [
            sys.executable,
            SCRIPT_CONSOLIDADOR,
            '--movto_cx1', MOCK_MOVTO_CX1,
            '--pad_06_2026', MOCK_PAD_06_2026
        ]

        # Executar o script consolidador
        logging.info(f"Executando script consolidador: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Verificar a saída do script
        if result.returncode != 0:
            logging.error(f"Script consolidador falhou: {result.stderr}")
        else:
            logging.info(f"Script consolidador executado com sucesso: {result.stdout}")

    except Exception as e:
        logging.error(f"Erro ao executar script consolidador: {e}")

def limpar_arquivos_mock():
    """Remove os arquivos mock após o teste."""
    try:
        if os.path.exists(MOCK_MOVTO_CX1):
            os.remove(MOCK_MOVTO_CX1)
        if os.path.exists(MOCK_PAD_06_2026):
            os.remove(MOCK_PAD_06_2026)
        logging.info("Arquivos mock removidos com sucesso")
    except Exception as e:
        logging.error(f"Erro ao remover arquivos mock: {e}")

def main():
    try:
        # Criar arquivos mock
        criar_arquivos_mock()

        # Iniciar thread para bloquear o arquivo
        thread_bloqueio = threading.Thread(target=bloquear_arquivo)
        thread_bloqueio.start()

        # Executar o script consolidador
        executar_consolidador()

        # Aguardar a thread de bloqueio terminar
        thread_bloqueio.join()

        # Limpar arquivos mock
        limpar_arquivos_mock()

    except Exception as e:
        logging.error(f"Erro durante o teste de concorrência: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
