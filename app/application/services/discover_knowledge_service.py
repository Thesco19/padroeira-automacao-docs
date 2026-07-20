from app.ports.knowledge_port import KnowledgeDiscoveryPort
from typing import Any

class DiscoverKnowledgeService:
    """Case of use: Discover knowledge based on a query."""
    def __init__(self, knowledge_port: KnowledgeDiscoveryPort):
        self._knowledge_port = knowledge_port

    def execute(self, query: str) -> Any:
        return self._knowledge_port.discover_knowledge(query)
