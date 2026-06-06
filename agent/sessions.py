from collections import defaultdict


def _empty_session():
    return {"messages": [], "intent": None, "pending_journey": None}


_sessions: dict = defaultdict(_empty_session)


def get_history(session_id: str) -> list[dict]:
    return list(_sessions[session_id]["messages"])


def get_intent(session_id: str):
    return _sessions[session_id]["intent"]


def get_pending_journey(session_id: str):
    return _sessions[session_id]["pending_journey"]


def set_intent(session_id: str, intent: str) -> None:
    current = _sessions[session_id]["intent"]
    if current and current != intent:
        _sessions[session_id]["pending_journey"] = current
    if intent == _sessions[session_id]["pending_journey"]:
        _sessions[session_id]["pending_journey"] = None
    _sessions[session_id]["intent"] = intent


def clear_pending_journey(session_id: str) -> None:
    _sessions[session_id]["pending_journey"] = None


def update_history(session_id: str, messages: list[dict]) -> None:
    _sessions[session_id]["messages"] = messages
