Espelho de /home/teco/work_out/lab-b/obs/STATUS.md em 2026-09-30; fonte: a pasta

# STATUS — obs

Estado: livre
Situação: ativo
Próximo passo: decidir o destino das 4 modificações não commitadas no repo lab-b (obsv/parsers/canvas_parser.py, obsv/web.py, obsv/webui.py, tests/) e do arquivo não rastreado obs/Mapa-do-Lab.mmd.
Pendências e riscos: trabalho sujo no lab-b (ver acima); nome da pasta (obs) diverge da tag RAG e da linha Supabase (obsv) — unificar na Fase 2.

## Log (mais recente primeiro, só acrescentar)

### 2026-09-30 16:53 — opencode (Fase 1, verificação pré-commit)
- Pretende: decidir se o trabalho do Mapa Mental (5 arquivos sujos) pode ir em commit próprio.
- Fez: rodei os 3 DoctorTests falhos num checkout limpo do HEAD (worktree temporária, sem as mudanças) — falharam lá também (test_config.py:380), logo são pré-existentes e alheios ao Mapa Mental. Worktree removida.
- Conclusão: commit do Mapa Mental liberado neste mesmo commit, com as falhas registradas aqui. Ficam de fora (untracked): obs/Mapa-do-Lab.mmd.

### 2026-09-30 11:12 — opencode (Fase 1, piloto)
- Pretende: criar este STATUS a partir do inventário, sem tocar no README existente.
- Fez: STATUS criado. Situação ativo reverificada agora: unit obsv-bridge.service (systemd --user) em active, servindo o vault em :8777; processo obsv mcp consta no inventário.
- Conclusão: pronto. Daqui: tratar as modificações pendentes e registrar obsv como alias (canônico = obs, sem renomear a pasta).