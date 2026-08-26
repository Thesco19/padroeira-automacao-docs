from typing import Protocol, Optional
from uuid import UUID
from app.domain.models import Session, Query, KnowledgeSource

class SessionPort(Protocol):
    """Gerencia o ciclo de vida e persistência de Sessões."""
    
    def get_by_id(self, session_id: UUID) -> Optional[Session]:
        """Retorna sessão por ID ou None se não encontrada."""
        ...
        
    def save(self, session: Session) -> None:
        """Persiste uma sessão."""
        ...

class QueryExecutorPort(Protocol):
    """Executa consultas no contexto de domínio."""
    
    def execute(self, query: Query) -> None:
        """Executa a consulta definida."""
        ...

class KnowledgeDiscoveryPort(Protocol):
    """Descobre e consulta fontes de conhecimento."""
    
    def find_by_capability(self, capability: str) -> list[KnowledgeSource]:
        """Retorna fontes que suportam a capacidade."""
        ...

class PermissionPort(Protocol):
    """Valida permissões de acesso no domínio."""
    
    def can_access(self, session_id: UUID, resource: str) -> bool:
        """Verifica se a sessão tem acesso ao recurso."""
        ...

class AuditPort(Protocol):
    """Registra eventos de auditoria do sistema."""
    
    def log(self, event_type: str, data: dict) -> None:
        """Registra um evento de auditoria."""
        ...

class HealthCheckPort(Protocol):
    """Verifica a saúde de componentes do sistema."""
    
    def check_health(self, component_id: UUID) -> bool:
        """Retorna se o componente está saudável."""
        ...
