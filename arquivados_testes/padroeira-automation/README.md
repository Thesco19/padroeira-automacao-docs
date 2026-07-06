# Padroeira Automation

Sistema de automação completo para fechamento de caixa do Restaurante Padroeira.

## Estrutura do Projeto

- **core/** → Scripts principais (`cortex_padroeira.py`, `agente_saurus.py`)
- **engines/** → Motores de consolidação de planilhas
- **config/** → Configurações
- **scripts/** → Scripts de execução
- **logs/** → Registros de execução
- **data/** → Arquivos gerados

## Comandos Principais (Aliases)

```bash
pad-enter     # Entrar no projeto (modo edição)
pad-start     # Iniciar sistema completo em tmux
pad-attach    # Entrar na sessão tmux ativa
pad-logs      # Ver últimos logs
