from __future__ import annotations

from datetime import datetime, timezone

from .models import AuditEvent, Message, Session, TenancyProfile, User


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MemoryStore:
    def __init__(self) -> None:
        self.users: dict[str, User] = {}
        self.tenancies: dict[str, TenancyProfile] = {}
        self.sessions: dict[str, Session] = {}
        self.messages: dict[str, list[Message]] = {}
        self.audit_events: list[AuditEvent] = []

    def seed_default_user(self) -> User:
        user = User(
            id="user_demo",
            email="demo.user@example.com",
            display_name="Demo User",
            role="operator",
        )
        self.users[user.id] = user
        return user

    def add_audit_event(self, event: AuditEvent) -> None:
        self.audit_events.append(event)

    def add_message(self, message: Message) -> None:
        self.messages.setdefault(message.session_id, []).append(message)

    def touch_session(self, session_id: str, current_skill: str | None = None) -> None:
        session = self.sessions[session_id]
        session.updated_at = utc_now()
        if current_skill is not None:
            session.current_skill = current_skill


STORE = MemoryStore()
DEFAULT_USER = STORE.seed_default_user()
