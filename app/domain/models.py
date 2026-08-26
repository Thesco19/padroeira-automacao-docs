from dataclasses import dataclass
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

class SessionState(Enum):
    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"

@dataclass
class Session:
    id: UUID
    created_at: datetime
    state: SessionState

    @classmethod
    def create(cls) -> "Session":
        return cls(id=uuid4(), created_at=datetime.utcnow(), state=SessionState.CREATED)

    def activate(self):
        if self.state != SessionState.CREATED:
            raise ValueError(f"Cannot activate session in state {self.state}")
        self.state = SessionState.ACTIVE

    def expire(self):
        self.state = SessionState.EXPIRED

class QueryStatus(Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

@dataclass
class Query:
    id: UUID
    session_id: UUID
    raw_text: str
    status: QueryStatus
    created_at: datetime

    def __post_init__(self):
        if not self.raw_text or not self.raw_text.strip():
            raise ValueError("Query raw_text cannot be empty")
        if self.created_at > datetime.utcnow():
            raise ValueError("Query creation time cannot be in the future")

@dataclass
class KnowledgeSource:
    id: UUID
    name: str
    uri: str
    is_active: bool
    capabilities: list[str]
    priority: int  # Higher is better

    def __post_init__(self):
        if self.priority < 0:
            raise ValueError("Priority cannot be negative")

    def set_health(self, is_healthy: bool):
        self.is_active = is_healthy
