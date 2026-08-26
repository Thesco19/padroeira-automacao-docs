from abc import ABC, abstractmethod

class PermissionPort(ABC):
    @abstractmethod
    def validate_permission(self, user_id: str, operation: str) -> bool:
        pass
