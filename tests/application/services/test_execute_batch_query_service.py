import unittest
from unittest.mock import MagicMock
from app.application.services.execute_batch_query_service import ExecuteBatchQueryService
from app.ports.query_port import QueryExecutorPort

class TestExecuteBatchQueryService(unittest.TestCase):
    def setUp(self):
        self.mock_query_port = MagicMock(spec=QueryExecutorPort)
        self.service = ExecuteBatchQueryService(self.mock_query_port)

    def test_execute(self):
        queries = ["q1", "q2"]
        self.mock_query_port.execute_batch_query.return_value = ["r1", "r2"]
        result = self.service.execute(queries)
        self.assertEqual(result, ["r1", "r2"])
        self.mock_query_port.execute_batch_query.assert_called_once_with(queries)

if __name__ == '__main__':
    unittest.main()
