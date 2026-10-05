# Protocolo de laboratório (bloco canônico dos agentes)

Fonte de verdade para `scripts/sync-protocolo.sh`. O bloco entre os
marcadores é instalado IDÊNTICO em cada `.md` de agente. Não edite o bloco
sem rodar o sync depois.

<!-- PROTOCOLO_LAB:INICIO -->
## Protocolo de projeto (todos os agentes)
Projeto = pasta de 1º nível em lab-a/b/z ou /opt/stacks. Nome = nome da pasta.
ANTES de mexer: leia README.md e STATUS.md do projeto.
- "Estado: em uso por OUTRO" há menos de 24h: não mexa, avise o Paulo.
- Senão, marque "em uso por <você> desde <data hora>" e registre no Log
  o que PRETENDE fazer.
DURANTE: só altere o projeto declarado. Não crie outra pasta para o mesmo assunto.
AO TERMINAR OU PARAR: preencha Fez e Conclusão (pronto / pela metade /
de onde partir), atualize Situação e Próximo passo, volte Estado para "livre".
Sem STATUS.md: crie pelo template antes de começar.
Nunca escreva segredos em README/STATUS.
Onde buscar contexto: 1) README/STATUS da pasta 2) ObSV 01-Projetos/<nome>
3) RAG com tag=<nome> 4) Supabase lab-g. Em conflito, vale a pasta.
Ao trocar de assunto, prefira sessão nova a --resume/--continue; sessões
longas arrastam contexto antigo.
Ao abrir um projeto, consulte no Supabase lab-g os handoffs com
status=pending para esse projeto; incorpore cada um ao Log do STATUS.md
e marque como accepted. Chats (web/mobile) não escrevem em pasta: eles
registram handoff no Supabase ou entregam o bloco de encerramento ao
usuário. Ao consultar a RAG, SEMPRE filtre por tag=<projeto>.
Se o Supabase não responder, siga sem ele e registre isso no Log.
<!-- PROTOCOLO_LAB:FIM -->
