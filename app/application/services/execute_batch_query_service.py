from app.ports.query_port import QueryExecutorPort
from typing import List, Any

class ExecuteBatchQueryService:
    """Case of use: Execute a batch of queries."""
    def __init__(self, query_port: QueryExecutorPort):
        self._query_port = query_port

    def execute(self, queries: List[str]) -> List[Any]:
        return self._query_port.execute_batch_query(queries)
