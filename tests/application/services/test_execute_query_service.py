import unittest
from unittest.mock import MagicMock
from app.application.services.execute_query_service import ExecuteQueryService
from app.ports.query_port import QueryExecutorPort

class TestExecuteQueryService(unittest.TestCase):
    def setUp(self):
        self.mock_query_port = MagicMock(spec=QueryExecutorPort)
        self.service = ExecuteQueryService(self.mock_query_port)

    def test_execute(self):
        query = "select *"
        self.mock_query_port.execute_query.return_value = "result"
        result = self.service.execute(query)
        self.assertEqual(result, "result")
        self.mock_query_port.execute_query.assert_called_once_with(query)

if __name__ == '__main__':
    unittest.main()
