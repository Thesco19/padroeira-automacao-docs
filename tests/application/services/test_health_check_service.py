import unittest
from unittest.mock import MagicMock
from app.application.services.health_check_service import HealthCheckService
from app.ports.health_port import HealthCheckPort

class TestHealthCheckService(unittest.TestCase):
    def setUp(self):
        self.mock_health_port = MagicMock(spec=HealthCheckPort)
        self.service = HealthCheckService(self.mock_health_port)

    def test_execute(self):
        self.mock_health_port.health_check.return_value = True
        result = self.service.execute()
        self.assertTrue(result)
        self.mock_health_port.health_check.assert_called_once()

if __name__ == '__main__':
    unittest.main()
