from app.ports.session_port import SessionManagerPort

class CloseSessionService:
    """Case of use: Close an existing session."""
    def __init__(self, session_manager: SessionManagerPort):
        self._session_manager = session_manager

    def execute(self, session_id: str):
        # Implementation to close session
        return self._session_manager.close_session(session_id)
