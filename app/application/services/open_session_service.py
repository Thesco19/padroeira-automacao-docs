from app.ports.session_port import SessionManagerPort

class OpenSessionService:
    """Case of use: Open a new session."""
    def __init__(self, session_manager: SessionManagerPort):
        self._session_manager = session_manager

    def execute(self, session_id: str):
        # Implementation to open session
        return self._session_manager.open_session(session_id)
