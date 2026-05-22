from collections import defaultdict


def _empty_session():
    return {"messages": [], "intent": None}


_sessions: dict = defaultdict(_empty_session)


def get_history(session_id: str) -> list[dict]:
    return list(_sessions[session_id]["messages"])


def get_intent(session_id: str):
    return _sessions[session_id]["intent"]


def set_intent(session_id: str, intent: str) -> None:
    _sessions[session_id]["intent"] = intent


def update_history(session_id: str, messages: list[dict]) -> None:
    _sessions[session_id]["messages"] = messages
