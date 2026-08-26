from abc import ABC, abstractmethod

class HealthCheckPort(ABC):
    @abstractmethod
    def health_check(self) -> bool:
        pass
