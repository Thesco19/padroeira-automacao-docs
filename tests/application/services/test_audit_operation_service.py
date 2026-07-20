import unittest
from unittest.mock import MagicMock
from app.application.services.audit_operation_service import AuditOperationService
from app.ports.audit_port import AuditPort

class TestAuditOperationService(unittest.TestCase):
    def setUp(self):
        self.mock_audit_port = MagicMock(spec=AuditPort)
        self.service = AuditOperationService(self.mock_audit_port)

    def test_execute(self):
        operation = "test-op"
        details = {"key": "value"}
        self.service.execute(operation, details)
        self.mock_audit_port.audit_operation.assert_called_once_with(operation, details)

if __name__ == '__main__':
    unittest.main()
