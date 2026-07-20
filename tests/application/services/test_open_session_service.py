import unittest
from unittest.mock import MagicMock
from app.application.services.open_session_service import OpenSessionService
from app.ports.session_port import SessionManagerPort

class TestOpenSessionService(unittest.TestCase):
    def setUp(self):
        self.mock_session_manager = MagicMock(spec=SessionManagerPort)
        self.service = OpenSessionService(self.mock_session_manager)

    def test_execute(self):
        session_id = "test-session"
        self.service.execute(session_id)
        self.mock_session_manager.open_session.assert_called_once_with(session_id)

if __name__ == '__main__':
    unittest.main()
