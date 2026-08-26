from abc import ABC, abstractmethod

class SessionManagerPort(ABC):
    @abstractmethod
    def open_session(self, session_id: str):
        pass

    @abstractmethod
    def close_session(self, session_id: str):
        pass
