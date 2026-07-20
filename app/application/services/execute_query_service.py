from app.ports.query_port import QueryExecutorPort
from typing import Any

class ExecuteQueryService:
    """Case of use: Execute a single query."""
    def __init__(self, query_port: QueryExecutorPort):
        self._query_port = query_port

    def execute(self, query: str) -> Any:
        return self._query_port.execute_query(query)
