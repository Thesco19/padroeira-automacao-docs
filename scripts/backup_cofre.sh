#!/bin/bash

# ==============================================================================
# OPERAÇÃO: Backup Blindado do Vaultwarden (Zero-Trust via Rclone)
# ==============================================================================

DATA_ATUAL=$(date +"%Y-%m-%d_%H-%M")
DIRETORIO_ALVO="/opt/stacks/vaultwarden/vw-data"
ARQUIVO_TMP="/tmp/vaultwarden_bkp_$DATA_ATUAL.tar.gz"

# 1. Empacota o cofre inteiro (Banco de dados, chaves RSA e anexos)
# Usamos o sudo para garantir leitura em todos os arquivos criados pelo Docker
sudo tar -czf "$ARQUIVO_TMP" -C "$DIRETORIO_ALVO" .

# 2. Exfiltra o pacote pelo túnel criptografado do Rclone para o Box
rclone copy "$ARQUIVO_TMP" box_cripto:

# 3. Queima de arquivo: apaga o pacote temporário do Mac Mini
sudo rm "$ARQUIVO_TMP"

# 4. Rotação de Segurança: apaga backups com mais de 30 dias no Box 
# (Impede que o armazenamento ocioso lote com o tempo)
rclone delete box_cripto: --min-age 30d

# Emite um sinal no log do sistema
logger "Vaultwarden: Backup criptografado enviado para o Box com sucesso."
