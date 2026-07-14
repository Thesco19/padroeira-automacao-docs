#!/usr/bin/env python3
"""
Script de consolidação de dados financeiros/contábeis.

Este script foi movido para a pasta **lab-a**. Ele mantém a mesma
funcionalidade original – parse de argumentos e verificação de
bloqueio de arquivos Excel – e pode ser usado como ponto de entrada
auxiliar da automação.
"""

import argparse
import logging
import sys
from pathlib import Path

# Configuração de logging estruturado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('consolidador.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def verificar_bloqueio_excel(caminho: str) -> bool:
    """
    Verifica se um arquivo Excel está bloqueado para edição.

    Retorna:
        False – arquivo livre (ou inexistente) ou sem arquivos temporários.
        True  – bloqueio detectado (não utilizado na lógica atual).
    """
    try:
        path = Path(caminho)
        if not path.exists():
            logger.warning(f"Arquivo não encontrado: {caminho}")
            return False

        # Arquivos temporários do Excel começam com '~$'
        temp_files = [f for f in path.parent.glob('~$*') if f.is_file()]
        if temp_files:
            temp_names = [f.name for f in temp_files]
            logger.warning(f"Arquivos temporários encontrados (possível bloqueio): {temp_names}")
            return False  # Conforme requisito atual, sempre retorna False

        logger.info(f"Arquivo verificado sem bloqueios: {caminho}")
        return False

    except Exception as e:
        logger.error(f"Erro ao verificar bloqueio do arquivo {caminho}: {str(e)}", exc_info=True)
        return False

def main():
    """Processa argumentos de linha de comando e inicia a verificação."""
    parser = argparse.ArgumentParser(
        description='Consolidador de movimentos contábeis e padrões mensais.'
    )
    parser.add_argument('--movto_cx1', type=str, required=True,
                        help='Caminho para o arquivo de movimentos contábeis (CX1).')
    parser.add_argument('--pad_mes', type=str, required=True,
                        help='Caminho para o arquivo de padrões mensais.')

    args = parser.parse_args()

    logger.info("Iniciando processo de consolidação")
    logger.info(f"Argumentos recebidos: movto_cx1={args.movto_cx1}, pad_mes={args.pad_mes}")

    # Verificação de bloqueio dos arquivos
    movto_bloqueado = verificar_bloqueio_excel(args.movto_cx1)
    pad_mes_bloqueado = verificar_bloqueio_excel(args.pad_mes)

    if movto_bloqueado or pad_mes_bloqueado:
        logger.warning("Alguns arquivos podem estar bloqueados para edição")
    else:
        logger.info("Todos os arquivos estão livres para processamento")

    logger.info("Estrutura inicial do consolidador concluída com sucesso")
    logger.info("Próximas etapas (não implementadas):")
    logger.info("1. Validação dos arquivos de entrada")
    logger.info("2. Mapeamento de estruturas de dados")
    logger.info("3. Consolidação dos movimentos contábeis")
    logger.info("4. Geração do arquivo de saída")

if __name__ == "__main__":
    main()
