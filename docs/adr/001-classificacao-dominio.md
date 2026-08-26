# ADR 001: Classificação dos Conceitos de Domínio

## Contexto
O projeto Reconciliação Fiscal V2 precisa de uma estrutura de domínio robusta. Foi decidido focar inicialmente nas entidades fundamentais (`Session`, `Query`, `KnowledgeSource`).

## Decisão
Os seguintes conceitos foram classificados como **Entidades** (possuem identidade persistente, ciclo de vida e estado mutável):

- **Session**: Identificada por um `id` único, rastreia o ciclo de vida do usuário.
- **Query**: Identificada por um `id` único, rastreia o status do processamento.
- **KnowledgeSource**: Identificada por um `id` único, rastreia a conectividade e configuração do recurso.

Conceitos como `SessionParameters`, `QueryCriteria` ou `SourceConfiguration` serão tratados como **Value Objects** (imutáveis, igualdade baseada em valor). 
Conceitos como `QuerySubmitted` ou `KnowledgeSourceConnected` serão **Domain Events** (fatos imutáveis ocorridos no passado).

## Justificativa
Esta classificação respeita o DDD, separando o que precisa de rastreamento de identidade e estado (Entidades) do que é apenas descritivo (Value Objects) ou histórico (Domain Events).
