import unittest
from unittest.mock import MagicMock
from app.application.services.discover_knowledge_service import DiscoverKnowledgeService
from app.ports.knowledge_port import KnowledgeDiscoveryPort

class TestDiscoverKnowledgeService(unittest.TestCase):
    def setUp(self):
        self.mock_knowledge_port = MagicMock(spec=KnowledgeDiscoveryPort)
        self.service = DiscoverKnowledgeService(self.mock_knowledge_port)

    def test_execute(self):
        query = "test-query"
        self.mock_knowledge_port.discover_knowledge.return_value = "some knowledge"
        result = self.service.execute(query)
        self.assertEqual(result, "some knowledge")
        self.mock_knowledge_port.discover_knowledge.assert_called_once_with(query)

if __name__ == '__main__':
    unittest.main()
