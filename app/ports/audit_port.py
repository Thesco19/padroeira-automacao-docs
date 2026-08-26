from abc import ABC, abstractmethod
from typing import Any

class AuditPort(ABC):
    @abstractmethod
    def audit_operation(self, operation: str, details: Any):
        pass
