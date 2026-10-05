Espelho de /home/teco/work_out/lab-b/smartcam/README.md em 2026-09-30; fonte: a pasta

# smartcam
Classe: projeto
Local: lab-b
Nomes em outros sistemas: RAG tag=smartcam | Supabase=smartcam | ObSV=smartcam | LM project=smartcam

## O que é
Sistema de monitoramento por câmeras com IA para detecção de movimento e reconhecimento.

## Como rodar / onde vive
Serviço systemd ativo. Porta HTTP :3100 (health), :3443 (HTTPS). Script: run-smartcam.sh.

## Estrutura
- run-smartcam.sh: script de inicialização
- config/: configurações
- venv/: ambiente virtual Python

## Dependências
Python 3, venv, systemd

## Segredos
Ver .env na pasta do projeto

## Ver também
STATUS.md