import unittest
from unittest.mock import MagicMock
from app.application.services.validate_permission_service import ValidatePermissionService
from app.ports.permission_port import PermissionPort

class TestValidatePermissionService(unittest.TestCase):
    def setUp(self):
        self.mock_permission_port = MagicMock(spec=PermissionPort)
        self.service = ValidatePermissionService(self.mock_permission_port)

    def test_execute(self):
        user_id = "user1"
        operation = "op1"
        self.mock_permission_port.validate_permission.return_value = True
        result = self.service.execute(user_id, operation)
        self.assertTrue(result)
        self.mock_permission_port.validate_permission.assert_called_once_with(user_id, operation)

if __name__ == '__main__':
    unittest.main()
