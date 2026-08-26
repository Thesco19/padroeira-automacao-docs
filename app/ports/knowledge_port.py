from abc import ABC, abstractmethod
from typing import Any

class KnowledgeDiscoveryPort(ABC):
    @abstractmethod
    def discover_knowledge(self, query: str) -> Any:
        pass
