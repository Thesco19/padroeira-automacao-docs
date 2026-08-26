from abc import ABC, abstractmethod
from typing import List, Any

class QueryExecutorPort(ABC):
    @abstractmethod
    def execute_query(self, query: str) -> Any:
        pass

    @abstractmethod
    def execute_batch_query(self, queries: List[str]) -> List[Any]:
        pass
