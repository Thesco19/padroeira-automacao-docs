# Plano de Implementação: Arquitetura Hexagonal (Fundamentos)

## Justificativa para novas Abstrações (Ports)
Não existem interfaces modeladas anteriormente. Para isolar o domínio da infraestrutura e permitir flexibilidade futura, as seguintes portas são necessárias:

1. `SessionRepository` (Port): Necessária para gerenciar o estado da sessão.
2. `QueryExecutor` (Port): Necessária para abstrair a execução de consultas (dados).
3. `KnowledgeDiscovery` (Port): Necessária para abstrair a descoberta de conhecimento.
4. `AuditLogger` (Port): Necessária para abstrair o registro de operações.
5. `PermissionValidator` (Port): Necessária para abstrair validação de permissões.

## Design Proposto

### Ports (Interfaces)
- `SessionManagerPort` (OpenSession, CloseSession)
- `QueryExecutorPort` (ExecuteQuery, ExecuteBatchQuery)
- `KnowledgeDiscoveryPort` (DiscoverKnowledge)
- `AuditPort` (AuditOperation)
- `PermissionPort` (ValidatePermission)
- `HealthCheckPort` (HealthCheck)

### Application Services (Fundamentais)
- `SessionService`: Implements OpenSession, CloseSession.
- `QueryService`: Implements ExecuteQuery, ExecuteBatchQuery.
- `KnowledgeService`: Implements DiscoverKnowledge.
- `HealthService`: Implements HealthCheck.
- `SecurityService`: Implements ValidatePermission.
- `AuditService`: Implements AuditOperation.

## Próximos Passos
1. Criar estrutura de pastas (`app/domain`, `app/ports`, `app/application`).
2. Implementar interfaces (ports) em `app/ports/`.
3. Implementar Application Services fundamentais em `app/application/`.
4. Realizar revisão arquitetural completa.
