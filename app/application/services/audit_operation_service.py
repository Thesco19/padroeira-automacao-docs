from app.ports.audit_port import AuditPort
from typing import Any

class AuditOperationService:
    """Case of use: Log an audit operation."""
    def __init__(self, audit_logger: AuditPort):
        self._audit_logger = audit_logger

    def execute(self, operation: str, details: Any):
        return self._audit_logger.audit_operation(operation, details)
