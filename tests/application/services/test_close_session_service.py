import unittest
from unittest.mock import MagicMock
from app.application.services.close_session_service import CloseSessionService
from app.ports.session_port import SessionManagerPort

class TestCloseSessionService(unittest.TestCase):
    def setUp(self):
        self.mock_session_manager = MagicMock(spec=SessionManagerPort)
        self.service = CloseSessionService(self.mock_session_manager)

    def test_execute(self):
        session_id = "test-session"
        self.service.execute(session_id)
        self.mock_session_manager.close_session.assert_called_once_with(session_id)

if __name__ == '__main__':
    unittest.main()
